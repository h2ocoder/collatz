"""L9: ternary-weight transformer on the long Collatz step, stratified by (k, k') and probed at SEP.

Same architecture as base_polarity.py (decoder-only, LSB-first digits) but every linear map
(attention q/k/v/o, MLP, head) is a BitNet b1.58 TernaryLinear (absmean quantizer + STE).
Embeddings and LayerNorms stay full precision, as in BitNet.

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/ternary_transformer.py [--base 16] [--d 256,512] [--steps 20000]
Writes results/ternary_transformer.json and checkpoints/long_b{base}_ternary_d{d}.pt
"""
import argparse
import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base_polarity as bp  # noqa: E402
from probe_kkp import KCAP, cap, fit_probe  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
DEV = "cuda" if torch.cuda.is_available() else "cpu"
bp.DEV = DEV


class TernaryLinear(nn.Module):
    def __init__(self, i, o, bias=True):
        super().__init__()
        self.w = nn.Parameter(torch.randn(o, i) / math.sqrt(i))
        self.b = nn.Parameter(torch.zeros(o)) if bias else None

    def quant(self):
        gamma = self.w.abs().mean().clamp(min=1e-8)
        return torch.round(self.w / gamma).clamp(-1, 1), gamma

    def forward(self, x):
        wq, gamma = self.quant()
        return F.linear(x, self.w + (wq * gamma - self.w).detach(), self.b)


class TAttn(nn.Module):
    def __init__(self, d, h):
        super().__init__()
        self.h, self.dh = h, d // h
        self.qkv, self.o = TernaryLinear(d, 3 * d), TernaryLinear(d, d)

    def forward(self, x, mask):
        B, T, D = x.shape
        q, k, v = self.qkv(x).view(B, T, 3, self.h, self.dh).permute(2, 0, 3, 1, 4)
        att = (q @ k.transpose(-1, -2)) / math.sqrt(self.dh) + mask
        y = (att.softmax(-1) @ v).transpose(1, 2).reshape(B, T, D)
        return self.o(y)


class TBlock(nn.Module):
    def __init__(self, d, h):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.attn = TAttn(d, h)
        self.mlp = nn.Sequential(TernaryLinear(d, 4 * d), nn.GELU(), TernaryLinear(4 * d, d))

    def forward(self, x, mask):
        x = x + self.attn(self.ln1(x), mask)
        return x + self.mlp(self.ln2(x))


class TTF(nn.Module):
    def __init__(self, V, T, d=256, h=4, L=4):
        super().__init__()
        self.tok, self.pos = nn.Embedding(V, d), nn.Embedding(T, d)
        self.blocks = nn.ModuleList(TBlock(d, h) for _ in range(L))
        self.ln, self.head = nn.LayerNorm(d), TernaryLinear(d, V)
        self.register_buffer("mask", torch.triu(torch.full((T, T), float("-inf")), 1))

    def forward(self, x, return_hidden=False):
        T = x.shape[1]
        hcur = self.tok(x) + self.pos(torch.arange(T, device=x.device))
        hs = [hcur]
        for b in self.blocks:
            hcur = b(hcur, self.mask[:T, :T])
            hs.append(hcur)
        out = self.head(self.ln(hcur))
        return (out, hs) if return_hidden else out

    def zero_density(self):
        z, n = 0, 0
        for m in self.modules():
            if isinstance(m, TernaryLinear):
                wq, _ = m.quant()
                z += int((wq == 0).sum())
                n += wq.numel()
        return z / n


def train_eval(base, d, steps, seed=0):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    task = bp.Task("long", base)
    test_ns = bp.sample_odd(np.random.default_rng(12345), 4096)
    test_toks, test_meta = task.batch(test_ns)
    model = TTF(task.V, task.T, d=d).to(DEV)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=3e-4, total_steps=steps, pct_start=0.05)
    Lp = task.Lin + 1
    t0 = time.time()
    for step in range(1, steps + 1):
        toks, _ = task.batch(bp.sample_odd(rng, 256))
        logits = model(toks[:, :-1])
        loss = F.cross_entropy(logits[:, Lp - 1:].reshape(-1, task.V), toks[:, Lp:].reshape(-1))
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        if step % 5000 == 0 or step == steps:
            acc = float(bp.exact_match(model, task, test_toks).float().mean())
            print(f"    ternary d={d} base {base} step {step:5d} loss {loss:.4f} exact-match {acc:.4f} ({time.time()-t0:.0f}s)", flush=True)
    ok = bp.exact_match(model, task, test_toks).cpu().numpy()
    by = defaultdict(lambda: [0, 0])
    for good, (k, kp) in zip(ok, test_meta):
        by[f"{k},{kp}"][0] += int(good)
        by[f"{k},{kp}"][1] += 1
    strat = {key: dict(acc=v[0] / v[1], n=v[1]) for key, v in sorted(by.items(), key=lambda kv: -kv[1][1])}
    # probe (k,k') at SEP, last layer
    from probe_kkp import hidden_at_sep
    Htr, mtr = hidden_at_sep(model, task, bp.sample_odd(np.random.default_rng(7), 16384))
    Hte, mte = hidden_at_sep(model, task, test_ns)
    fn = lambda m: (cap(m[0]) - 1) * KCAP + cap(m[1]) - 1  # noqa: E731
    probe = [fit_probe(Htr[l], [fn(m) for m in mtr], Hte[l], [fn(m) for m in mte], KCAP * KCAP) for l in range(len(Htr))]
    torch.save(dict(state=model.state_dict(), d=d, L=4, base=base), RESULTS / "checkpoints" / f"long_b{base}_ternary_d{d}.pt")
    return dict(base=base, d=d, acc=float(ok.mean()), strat=strat, probe_joint_by_layer=probe,
                zero_density=model.zero_density(), seconds=time.time() - t0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=int, default=16)
    ap.add_argument("--d", default="256,512")
    ap.add_argument("--steps", type=int, default=20000)
    a = ap.parse_args()
    out = []
    for d in [int(x) for x in a.d.split(",")]:
        print(f"== ternary long step, base {a.base}, d={d}")
        r = train_eval(a.base, d, a.steps)
        out.append(r)
        json.dump(out, open(RESULTS / "ternary_transformer.json", "w"), indent=1)
        top = list(r["strat"].items())[:8]
        print(f"  overall {r['acc']:.4f}; zero density {r['zero_density']:.3f}; (k,k') probe by layer {['%.3f' % p for p in r['probe_joint_by_layer']]}")
        print("  by (k,k'): " + ", ".join(f"({k}) {v['acc']:.2f}[n={v['n']}]" for k, v in top))
