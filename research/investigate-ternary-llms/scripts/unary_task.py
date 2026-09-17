"""L15: unary as the worst base.  Learn n -> T(n) (Terras step) from n written in UNARY (a^n),
versus from n in binary, with held-out n so that memorisation cannot pass.

Input : 'a' * n  (unary, length n <= NMAX)  or  bits of n LSB-first (binary);  then SEP.
Output: T(n) in binary, LSB first (fixed 11 digits), then EOS.
Split : 80% of n in [1, NMAX] for training, 20% held out (the rule must generalise across n).
Stratified by parity of n (the only decision T makes) and by n size.

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/unary_task.py [--nmax 1024] [--steps 6000]
Writes results/unary_task.json
"""
import argparse
import json
import math
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
DEV = "cuda" if torch.cuda.is_available() else "cpu"


def terras(n):
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


class Block(nn.Module):
    def __init__(self, d, h):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.attn = nn.MultiheadAttention(d, h, batch_first=True)
        self.mlp = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))

    def forward(self, x, mask):
        a = self.ln1(x)
        x = x + self.attn(a, a, a, attn_mask=mask, need_weights=False)[0]
        return x + self.mlp(self.ln2(x))


class TF(nn.Module):
    def __init__(self, V, T, d=128, h=4, L=4):
        super().__init__()
        self.tok, self.pos = nn.Embedding(V, d), nn.Embedding(T, d)
        self.blocks = nn.ModuleList(Block(d, h) for _ in range(L))
        self.ln, self.head = nn.LayerNorm(d), nn.Linear(d, V)
        self.register_buffer("mask", torch.triu(torch.full((T, T), float("-inf")), 1))

    def forward(self, x):
        T = x.shape[1]
        hcur = self.tok(x) + self.pos(torch.arange(T, device=x.device))
        for b in self.blocks:
            hcur = b(hcur, self.mask[:T, :T])
        return self.head(self.ln(hcur))


class Enc:
    """Tokens: 0='a'/bit0, 1=bit1, 2=SEP, 3=EOS, 4=PAD.  Unary uses token 0 repeated n times."""

    def __init__(self, mode, nmax, out_bits=11):
        self.mode, self.nmax, self.ob = mode, nmax, out_bits
        self.Lin = nmax if mode == "unary" else nmax.bit_length()
        self.T = self.Lin + 1 + out_bits + 1
        self.V = 5

    def encode(self, n):
        if self.mode == "unary":
            inp = [0] * n + [4] * (self.Lin - n)  # right-pad with PAD so SEP is at a fixed position
        else:
            inp = [(n >> i) & 1 for i in range(self.Lin)]
        t = terras(n)
        return inp + [2] + [(t >> i) & 1 for i in range(self.ob)] + [3]

    def batch(self, ns):
        return torch.tensor([self.encode(int(n)) for n in ns], device=DEV)


@torch.no_grad()
def exact(model, enc, ns, bs=64):
    ok = []
    for i in range(0, len(ns), bs):
        toks = enc.batch(ns[i:i + bs])
        Lp = enc.Lin + 1
        seq = toks[:, :Lp].clone()
        for _ in range(enc.ob + 1):
            seq = torch.cat([seq, model(seq)[:, -1].argmax(-1, keepdim=True)], 1)
        ok += (seq[:, Lp:] == toks[:, Lp:]).all(1).cpu().tolist()
    return np.array(ok)


def run(mode, nmax, steps, seed=0):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    enc = Enc(mode, nmax)
    all_n = np.arange(1, nmax + 1)
    rng.shuffle(all_n)
    ntest = len(all_n) // 5
    test_n, train_n = all_n[:ntest], all_n[ntest:]
    model = TF(enc.V, enc.T).to(DEV)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=3e-4, total_steps=steps, pct_start=0.05)
    Lp = enc.Lin + 1
    bs = 16 if mode == "unary" else 128
    t0 = time.time()
    for step in range(1, steps + 1):
        toks = enc.batch(rng.choice(train_n, bs))
        logits = model(toks[:, :-1])
        loss = F.cross_entropy(logits[:, Lp - 1:].reshape(-1, enc.V), toks[:, Lp:].reshape(-1))
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        if step % 2000 == 0 or step == steps:
            print(f"    {mode} step {step} loss {loss:.4f} ({time.time()-t0:.0f}s)", flush=True)
    ok_tr = exact(model, enc, train_n[:512])
    ok_te = exact(model, enc, test_n)
    by = defaultdict(lambda: [0, 0])
    for n, o in zip(test_n, ok_te):
        by[("odd" if n % 2 else "even", "n<=256" if n <= 256 else "n>256")][0] += int(o)
        by[("odd" if n % 2 else "even", "n<=256" if n <= 256 else "n>256")][1] += 1
    strat = {f"{p},{s}": dict(acc=v[0] / v[1], n=v[1]) for (p, s), v in sorted(by.items())}
    return dict(mode=mode, nmax=nmax, train_acc=float(ok_tr.mean()), test_acc=float(ok_te.mean()), strat=strat, seconds=time.time() - t0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=1024)
    ap.add_argument("--steps", type=int, default=6000)
    a = ap.parse_args()
    out = []
    for mode in ("binary", "unary"):
        print(f"== {mode} input, n <= {a.nmax}, held-out 20% of n")
        r = run(mode, a.nmax, a.steps)
        out.append(r)
        print(f"  train exact {r['train_acc']:.3f}   held-out exact {r['test_acc']:.3f}   by parity/size: "
              + ", ".join(f"{k}: {v['acc']:.2f}[n={v['n']}]" for k, v in r["strat"].items()))
        json.dump(out, open(RESULTS / "unary_task.json", "w"), indent=1)
