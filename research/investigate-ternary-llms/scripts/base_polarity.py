"""L7: does the input base matter for transformers learning Collatz steps, and is base 6 special?

Two tasks on odd n (random, n < 2^24):
  one  : Syracuse step   S(n) = (3n+1) / 2^v2(3n+1)
  long : Charton-Narayanan long step  kappa(n) = ((3/2)^k (n+1) - 1) / 2^k',  k = v2(n+1)
Bases 2, 3, 6, 16, 24.  Digits least-significant first.  Decoder-only causal
transformer trained on next-token loss over the output digits; exact-match accuracy
with greedy decoding on 4096 held-out n; long-step accuracy also stratified by (k, k').

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/base_polarity.py [--steps N] [--bases 2,3,6,16,24] [--tasks one,long]
Writes results/base_polarity.json and results/checkpoints/<task>_b<base>.pt (gitignored).
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
CKPT = RESULTS / "checkpoints"
CKPT.mkdir(parents=True, exist_ok=True)
DEV = "cuda" if torch.cuda.is_available() else "cpu"
NBITS = 24


# ---------------------------------------------------------------- arithmetic
def v2(x):
    return (x & -x).bit_length() - 1


def one_step(n):
    m = 3 * n + 1
    return m >> v2(m)


def long_step(n):
    k = v2(n + 1)
    x = n
    for _ in range(k):
        x = (3 * x + 1) // 2
    kp = v2(x)
    return x >> kp, k, kp


def digits(x, base, L):
    out = []
    for _ in range(L):
        out.append(x % base)
        x //= base
    assert x == 0
    return out


def n_digits(max_val, base):
    return int(math.ceil(math.log(max_val + 1, base))) + 1


# ---------------------------------------------------------------- data
class Task:
    def __init__(self, task, base):
        self.task, self.base = task, base
        self.Lin = n_digits(1 << NBITS, base)
        # one step: S(n) < 2n.  long step: kappa < (3/2)^k (n+1) <= 3^k 2^(NBITS-k) <= 3^NBITS
        maxout = (1 << NBITS) * 2 if task == "one" else 3 ** NBITS
        self.Lout = n_digits(maxout, base) + 1
        # vocab: digits 0..base-1, SEP, EOS, PAD
        self.SEP, self.EOS, self.PAD = base, base + 1, base + 2
        self.V = base + 3
        self.T = self.Lin + 1 + self.Lout + 1

    def encode(self, n):
        if self.task == "one":
            y, k, kp = one_step(n), None, None
        else:
            y, k, kp = long_step(n)
        assert y < self.base ** self.Lout
        toks = digits(n, self.base, self.Lin) + [self.SEP] + digits(y, self.base, self.Lout) + [self.EOS]
        return toks, (k, kp)

    def batch(self, ns):
        rows, meta = [], []
        for n in ns:
            t, m = self.encode(int(n))
            rows.append(t)
            meta.append(m)
        return torch.tensor(rows, device=DEV), meta


def sample_odd(rng, size):
    return rng.integers(0, 1 << (NBITS - 1), size=size) * 2 + 1


# ---------------------------------------------------------------- model
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
    def __init__(self, V, T, d=256, h=4, L=4):
        super().__init__()
        self.tok, self.pos = nn.Embedding(V, d), nn.Embedding(T, d)
        self.blocks = nn.ModuleList(Block(d, h) for _ in range(L))
        self.ln, self.head = nn.LayerNorm(d), nn.Linear(d, V)
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


# ---------------------------------------------------------------- train / eval
@torch.no_grad()
def exact_match(model, task, toks):
    """Greedy decode the output digits; compare to the target."""
    B = toks.shape[0]
    Lp = task.Lin + 1  # prompt length incl. SEP
    seq = toks[:, :Lp].clone()
    for _ in range(task.Lout + 1):
        logits = model(seq)[:, -1]
        seq = torch.cat([seq, logits.argmax(-1, keepdim=True)], 1)
    return (seq[:, Lp:] == toks[:, Lp:]).all(1)


def run(task_name, base, steps, seed=0, d=256, L=4):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    task = Task(task_name, base)
    test_ns = sample_odd(np.random.default_rng(12345), 4096)
    test_toks, test_meta = task.batch(test_ns)
    model = TF(task.V, task.T, d=d, L=L).to(DEV)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=3e-4, total_steps=steps, pct_start=0.05)
    Lp = task.Lin + 1
    t0 = time.time()
    curve = []
    for step in range(1, steps + 1):
        toks, _ = task.batch(sample_odd(rng, 256))
        logits = model(toks[:, :-1])
        loss = F.cross_entropy(logits[:, Lp - 1:].reshape(-1, task.V), toks[:, Lp:].reshape(-1))
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        if step % 1000 == 0 or step == steps:
            acc = float(exact_match(model, task, test_toks).float().mean())
            curve.append((step, float(loss), acc))
            print(f"    {task_name} base {base:2d} step {step:5d} loss {loss:.4f} test exact-match {acc:.4f} ({time.time()-t0:.0f}s)", flush=True)
    ok = exact_match(model, task, test_toks).cpu().numpy()
    acc = float(ok.mean())
    strat = None
    if task_name == "long":
        by = defaultdict(lambda: [0, 0])
        for good, (k, kp) in zip(ok, test_meta):
            key = f"{k},{kp}"
            by[key][0] += int(good)
            by[key][1] += 1
        strat = {key: dict(acc=v[0] / v[1], n=v[1]) for key, v in sorted(by.items(), key=lambda kv: -kv[1][1])}
    torch.save(dict(state=model.state_dict(), task=task_name, base=base, d=d, L=L), CKPT / f"{task_name}_b{base}.pt")
    return dict(task=task_name, base=base, acc=acc, curve=curve, strat=strat, Lin=task.Lin, Lout=task.Lout,
                seconds=time.time() - t0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=8000)
    ap.add_argument("--bases", default="2,3,6,16,24")
    ap.add_argument("--tasks", default="one,long")
    a = ap.parse_args()
    bases = [int(b) for b in a.bases.split(",")]
    tasks = a.tasks.split(",")
    print(f"device={DEV}; steps={a.steps}; bases={bases}; tasks={tasks}")
    out = []
    for task in tasks:
        for base in bases:
            print(f"== task {task}, base {base}")
            out.append(run(task, base, a.steps))
            json.dump(out, open(RESULTS / "base_polarity.json", "w"), indent=1)
    print("\nSUMMARY exact-match on 4096 held-out odd n < 2^24")
    print("  base   one-step   long-step")
    for base in bases:
        o = next((r["acc"] for r in out if r["task"] == "one" and r["base"] == base), None)
        l = next((r["acc"] for r in out if r["task"] == "long" and r["base"] == base), None)
        fo = "   -    " if o is None else f"{o:8.4f}"
        fl = "    -    " if l is None else f"{l:9.4f}"
        print(f"  {base:4d}   {fo}   {fl}")
    for r in out:
        if r["strat"]:
            top = list(r["strat"].items())[:8]
            print(f"  long base {r['base']} by (k,k'): " + ", ".join(f"({k}) {v['acc']:.2f}[n={v['n']}]" for k, v in top))
