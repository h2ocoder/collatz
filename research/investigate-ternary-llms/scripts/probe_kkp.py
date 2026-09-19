"""L8: linear probes for (k, k') in the long-step transformers' residual streams.

For the long step kappa(n) = ((3/2)^k (n+1) - 1) / 2^k', k = v2(n+1) (trailing 1-bits of n),
k' = halvings afterwards.  Within each (k,k') class the map is affine with intercept
C = (3^k - 2^k) / 2^(k+k'), so "the model represents (k,k')" == "it represents the affine map".
We read the residual stream after each layer at the SEP position (all input digits seen, no
output produced) and fit multinomial logistic regression for k, for k', and for the joint class.
Baselines: majority class, and a probe on a shuffled label (chance).

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/probe_kkp.py [bases]
Writes results/probe_kkp.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base_polarity as bp  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
DEV = "cuda" if torch.cuda.is_available() else "cpu"
bp.DEV = DEV
KCAP = 6  # classes 1..KCAP-1, and ">=KCAP"


def cap(x):
    return min(x, KCAP)


def hidden_at_sep(model, task, ns, bs=512):
    """Residual stream after each layer (and the embedding) at the SEP position."""
    hs_all = None
    metas = []
    with torch.no_grad():
        for i in range(0, len(ns), bs):
            toks, meta = task.batch(ns[i:i + bs])
            metas += meta
            _, hs = model(toks[:, :task.Lin + 1], return_hidden=True)  # up to and including SEP
            cur = [h[:, -1].float().cpu() for h in hs]  # position of SEP
            hs_all = cur if hs_all is None else [torch.cat([a, b]) for a, b in zip(hs_all, cur)]
    return hs_all, metas


def fit_probe(Xtr, ytr, Xte, yte, ncls, steps=600):
    """Multinomial logistic regression, full-batch L-BFGS on standardized features."""
    mu, sd = Xtr.mean(0, keepdim=True), Xtr.std(0, keepdim=True) + 1e-6
    Xtr, Xte = ((Xtr - mu) / sd).to(DEV), ((Xte - mu) / sd).to(DEV)
    ytr, yte = torch.tensor(ytr, device=DEV), torch.tensor(yte, device=DEV)
    W = torch.zeros(Xtr.shape[1], ncls, device=DEV, requires_grad=True)
    b = torch.zeros(ncls, device=DEV, requires_grad=True)
    opt = torch.optim.LBFGS([W, b], max_iter=steps, line_search_fn="strong_wolfe")

    def closure():
        opt.zero_grad()
        loss = F.cross_entropy(Xtr @ W + b, ytr) + 1e-3 * (W ** 2).sum()
        loss.backward()
        return loss

    opt.step(closure)
    with torch.no_grad():
        return float(((Xte @ W + b).argmax(1) == yte).float().mean())


def probe_base(spec):
    """spec: base, or 'base@checkpoint_stem' to probe a specific checkpoint file."""
    base, stem = (int(spec.split("@")[0]), spec.split("@")[1]) if "@" in str(spec) else (int(spec), f"long_b{spec}")
    ck = torch.load(RESULTS / "checkpoints" / f"{stem}.pt", map_location=DEV)
    task = bp.Task("long", base)
    model = bp.TF(task.V, task.T, d=ck["d"], L=ck["L"]).to(DEV)
    model.load_state_dict(ck["state"])
    model.eval()
    rng = np.random.default_rng(7)
    ns_tr, ns_te = bp.sample_odd(rng, 16384), bp.sample_odd(np.random.default_rng(12345), 4096)
    Htr, mtr = hidden_at_sep(model, task, ns_tr)
    Hte, mte = hidden_at_sep(model, task, ns_te)
    labels = {
        "k": (lambda m: cap(m[0]) - 1, KCAP),
        "k'": (lambda m: cap(m[1]) - 1, KCAP),
        "(k,k')": (lambda m: (cap(m[0]) - 1) * KCAP + cap(m[1]) - 1, KCAP * KCAP),
    }
    out = {"base": base, "checkpoint": stem, "layers": ck["L"], "probe": {}, "majority": {}, "shuffled": {}}
    print(f"\nbase {base} ({ck['L']} layers, {stem}), probes at SEP; test n = 4096")
    for name, (fn, ncls) in labels.items():
        ytr = [fn(m) for m in mtr]
        yte = [fn(m) for m in mte]
        maj = Counter(yte).most_common(1)[0][1] / len(yte)
        out["majority"][name] = maj
        accs = [fit_probe(Htr[l], ytr, Hte[l], yte, ncls) for l in range(len(Htr))]
        out["probe"][name] = accs
        ysh = list(np.random.default_rng(1).permutation(ytr))
        out["shuffled"][name] = fit_probe(Htr[-1], ysh, Hte[-1], yte, ncls)
        print(f"  {name:7s} majority {maj:.3f} | by layer (emb, L1..L{ck['L']}): " + " ".join(f"{a:.3f}" for a in accs)
              + f" | shuffled-label control {out['shuffled'][name]:.3f}")
    return out


if __name__ == "__main__":
    bases = sys.argv[1].split(",") if len(sys.argv) > 1 else ["16", "2", "6@long_b6_L8_layers", "6@long_b6_L2_layers"]
    res = [probe_base(b) for b in bases]
    json.dump(res, open(RESULTS / "probe_kkp.json", "w"), indent=1)
    print(f"\nwrote {RESULTS / 'probe_kkp.json'}")
