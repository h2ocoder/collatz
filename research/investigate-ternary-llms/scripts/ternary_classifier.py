"""L5/L6: a BitNet-style ternary-weight MLP that predicts the dropping set of odd n
from its low bits.

Input : bits 1..B of odd n (bit 0 is always 1), encoded as +-1.
Target: dropping set k in {3, 6, 8, 11, 13, 16, 19} or ">=21"  (8 classes).
        Class k with s Syracuse steps is decided by n mod 2^b(s), b = k - s:
        3->2, 6->4, 8->5, 11->7, 13->8, 16->10, 19->12 bits.  With bits 0..11
        (B = 11 informative bits) every class is exactly decidable.
Model : Linear(B, H) -> ReLU -> Linear(H, 8), both layers with absmean ternary
        weights {-1,0,+1} * gamma and a straight-through estimator (BitNet b1.58).
        Biases are real.  A hidden unit with quantized weights +-1 on bits 1..j,
        0 elsewhere, and bias about -(j - 1/2) is exactly the residue test
        n = r (mod 2^(j+1)) with r read off the signs.

Experiments
  (i)   accuracy vs number of bits shown B = 1..15, against the exact Bayes ceiling
  (ii)  readability of the learned hidden units as residue tests
  (iii) zero density of the ternary weights
  (L6)  per-class accuracy over training steps (learning order)

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/ternary_classifier.py
"""
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from collatz.core import stopping_time  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
RESULTS.mkdir(exist_ok=True)
DEV = "cuda" if torch.cuda.is_available() else "cpu"
CLASSES = [3, 6, 8, 11, 13, 16, 19, 21]  # 21 means ">= 21"
CLASS_BITS = {3: 2, 6: 4, 8: 5, 11: 7, 13: 8, 16: 10, 19: 12, 21: 12}
NMAX_BITS = 16  # odd n < 2^16 -> 32768 samples, 15 informative bits


# ---------------------------------------------------------------- data
def make_data():
    ns = np.arange(1, 1 << NMAX_BITS, 2)
    ks = np.array([stopping_time(int(n)) if n > 1 else 3 for n in ns])  # n=1 has no stopping time; treat as class 3 (1 mod 4)
    ks = np.where(ks >= 21, 21, ks)
    y = np.array([CLASSES.index(int(k)) for k in ks])
    return ns, y


def bits_pm1(ns, B):
    """bits 1..B of n as +-1 (shape [N, B])."""
    x = ((ns[:, None] >> np.arange(1, B + 1)[None, :]) & 1).astype(np.float32)
    return 2 * x - 1


def bayes_ceiling(ns, y, B):
    """Best possible accuracy from bits 0..B (majority class per residue mod 2^(B+1))."""
    res = ns % (1 << (B + 1))
    tab = defaultdict(Counter)
    for r, c in zip(res, y):
        tab[r][c] += 1
    return sum(max(cnt.values()) for cnt in tab.values()) / len(ns)


# ---------------------------------------------------------------- model
class TernaryLinear(nn.Module):
    """BitNet b1.58 absmean quantizer with straight-through estimator."""

    def __init__(self, i, o):
        super().__init__()
        self.w = nn.Parameter(torch.randn(o, i) * 0.5)
        self.b = nn.Parameter(torch.zeros(o))

    def quant(self):
        gamma = self.w.abs().mean().clamp(min=1e-8)
        return torch.round(self.w / gamma).clamp(-1, 1), gamma

    def forward(self, x):
        wq, gamma = self.quant()
        w_eff = self.w + (wq * gamma - self.w).detach()  # STE
        return F.linear(x, w_eff, self.b)


class Net(nn.Module):
    def __init__(self, B, H):
        super().__init__()
        self.l1, self.l2 = TernaryLinear(B, H), TernaryLinear(H, len(CLASSES))

    def forward(self, x):
        return self.l2(F.relu(self.l1(x)))


def train(B, H=64, steps=3000, lr=2e-2, seed=0, log_every=0, ns=None, y=None, split=0.2):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    X = torch.tensor(bits_pm1(ns, B), device=DEV)
    Y = torch.tensor(y, device=DEV)
    idx = rng.permutation(len(ns))
    ntest = int(split * len(ns))
    te, tr = idx[:ntest], idx[ntest:]
    net = Net(B, H).to(DEV)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps)
    curve = []
    for t in range(1, steps + 1):
        opt.zero_grad()
        loss = F.cross_entropy(net(X[tr]), Y[tr])
        loss.backward()
        opt.step()
        sched.step()
        if log_every and (t % log_every == 0 or t == 1):
            with torch.no_grad():
                pred = net(X[te]).argmax(1)
                per = [float((pred[Y[te] == c] == c).float().mean()) if (Y[te] == c).any() else None for c in range(len(CLASSES))]
                curve.append((t, float((pred == Y[te]).float().mean()), per))
    with torch.no_grad():
        acc_te = float((net(X[te]).argmax(1) == Y[te]).float().mean())
        acc_tr = float((net(X[tr]).argmax(1) == Y[tr]).float().mean())
    return net, acc_tr, acc_te, curve


# ---------------------------------------------------------------- interpretability
def residue_tests(net, B, ns, y):
    """For each hidden unit: quantized weights, support, whether the support is a
    prefix of bits 1..j, the residue it encodes, and how well its firing pattern
    matches the exact test n = r (mod 2^(j+1))."""
    wq, gamma = net.l1.quant()
    wq = wq.detach().cpu().numpy().astype(int)
    b = net.l1.b.detach().cpu().numpy()
    X = bits_pm1(ns, B)
    pre = X @ (wq.T * float(gamma)) + b
    fires = pre > 0
    rows = []
    for u in range(wq.shape[0]):
        supp = np.nonzero(wq[u])[0] + 1  # bit indices
        if len(supp) == 0:
            rows.append(dict(unit=u, support=[], prefix=False, nnz=0))
            continue
        j = int(supp.max())
        prefix = list(supp) == list(range(1, j + 1))
        # residue implied by the signs on the support: bit i = 1 if w=+1 else 0; bit 0 = 1
        r = 1 + sum((1 << i) for i in supp if wq[u][i - 1] == 1)
        mod = 1 << (j + 1)
        exact = (ns % mod) == r if prefix else None
        match = float((fires[:, u] == exact).mean()) if prefix else None
        # is that residue class "pure" (single dropping set)?
        if prefix:
            cls = Counter(y[exact]) if exact.any() else Counter()
            purity = max(cls.values()) / max(1, sum(cls.values())) if cls else 0.0
            top = CLASSES[cls.most_common(1)[0][0]] if cls else None
        else:
            purity, top = None, None
        rows.append(dict(unit=u, support=[int(s) for s in supp], nnz=int(len(supp)), prefix=bool(prefix),
                         residue=int(r) if prefix else None, mod=int(mod) if prefix else None,
                         fires_frac=float(fires[:, u].mean()), match_exact_test=match,
                         class_purity=purity, class_top=top, bias=float(b[u]), gamma_bias_ratio=float(b[u] / gamma)))
    return rows


if __name__ == "__main__":
    t0 = time.time()
    ns, y = make_data()
    print(f"device={DEV}; {len(ns)} odd n < 2^{NMAX_BITS}; class counts:",
          {CLASSES[c]: int((y == c).sum()) for c in range(len(CLASSES))})

    # (i) accuracy vs bits shown
    print("\n(i) accuracy vs bits shown (H=64, 3000 steps, 20% held-out)")
    print("  B   Bayes ceiling   train acc   test acc   (test - ceiling)")
    sweep = []
    for B in range(1, 16):
        ceil = bayes_ceiling(ns, y, B)
        _, atr, ate, _ = train(B, ns=ns, y=y)
        sweep.append((B, ceil, atr, ate))
        print(f" {B:2d}   {ceil:.4f}         {atr:.4f}      {ate:.4f}     {ate - ceil:+.4f}")

    # main run: B = 11 (exactly decidable) with learning curve, 3 seeds
    print("\n(ii)/(iii)/(L6) main runs at B=11, H=64")
    mains = []
    for seed in range(3):
        net, atr, ate, curve = train(11, seed=seed, log_every=50, ns=ns, y=y)
        rows = residue_tests(net, 11, ns, y)
        wq1, _ = net.l1.quant()
        wq2, _ = net.l2.quant()
        z1 = float((wq1 == 0).float().mean())
        z2 = float((wq2 == 0).float().mean())
        prefix_units = [r for r in rows if r.get("prefix")]
        exact_units = [r for r in prefix_units if r["match_exact_test"] is not None and r["match_exact_test"] > 0.999]
        pure_units = [r for r in exact_units if r["class_purity"] is not None and r["class_purity"] > 0.999]
        dead = [r for r in rows if r["nnz"] == 0 or r["fires_frac"] < 1e-4]
        print(f"  seed {seed}: train {atr:.4f} test {ate:.4f}; zero density L1 {z1:.3f} L2 {z2:.3f}; "
              f"units: {len(rows)} total, {len(dead)} dead, {len(prefix_units)} prefix-support, "
              f"{len(exact_units)} fire exactly as a residue test, {len(pure_units)} of those test a pure class")
        mains.append(dict(seed=seed, acc_train=atr, acc_test=ate, zero_density_l1=z1, zero_density_l2=z2,
                          n_units=len(rows), n_dead=len(dead), n_prefix=len(prefix_units), n_exact=len(exact_units),
                          n_pure=len(pure_units), units=rows, curve=curve))
        if seed == 0:
            print("    sample of prefix-support units (support, residue mod 2^(j+1), match, top class, purity):")
            for r in sorted(prefix_units, key=lambda r: r["mod"])[:12]:
                print(f"      bits 1..{max(r['support'])}: n = {r['residue']} mod {r['mod']}  match={r['match_exact_test']:.3f}  "
                      f"class {r['class_top']} purity={r['class_purity']:.3f}  bias/gamma={r['gamma_bias_ratio']:.2f}")
            supp_hist = Counter(r["nnz"] for r in rows)
            print("    support-size histogram:", dict(sorted(supp_hist.items())))

    # (L6) learning order from seed 0: first step at which each class's test accuracy exceeds 0.9
    curve = mains[0]["curve"]
    order = {}
    for c in range(len(CLASSES)):
        hit = next((t for t, _, per in curve if per[c] is not None and per[c] >= 0.9), None)
        order[CLASSES[c]] = hit
    print("\n(L6) first training step with per-class test accuracy >= 0.9 (seed 0):")
    for k in CLASSES:
        print(f"   class {k:>2} (needs {CLASS_BITS[k]:2d} bits): step {order[k]}")

    json.dump(dict(device=DEV, sweep=sweep, mains=mains, learning_order=order, classes=CLASSES,
                   elapsed_s=time.time() - t0),
              open(RESULTS / "ternary_classifier.json", "w"), indent=1)
    print(f"\nelapsed {time.time() - t0:.0f}s; wrote {RESULTS / 'ternary_classifier.json'}")
