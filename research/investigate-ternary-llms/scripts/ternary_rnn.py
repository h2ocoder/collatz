"""L11: does a trained ternary-weight RNN rediscover the Terras transducer?

Task: bit-serial, LSB first.  Input at time t: (start_t, x_t) with x_t = bit t of n.
Target at time t: bit (t-1) of T(n)  (one-step delay = the division by 2; target 0 at t=0).
Model: Elman RNN h_t = relu(W_in u_t + W_hh h_{t-1} + b), y_t = sigmoid(w_out h_t + c),
       every weight matrix a BitNet TernaryLinear (absmean + STE).  Hidden size H.
After training: (1) exact-match on T(n) for random 40-bit n; (2) extract the machine the RNN
implements by binarising h_t (> 0) over many sequences, counting distinct states and checking
whether transitions are deterministic; (3) minimise the extracted Mealy machine and compare
its state count with the minimal Terras transducer (computed here from the reachable
(p, prev, carry) states of the circuit).

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/ternary_rnn.py [--H 16] [--steps 20000]
Writes results/ternary_rnn.json
"""
import argparse
import json
import math
import random
import sys
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


class TernaryLinear(nn.Module):
    def __init__(self, i, o, bias=True):
        super().__init__()
        self.w = nn.Parameter(torch.randn(o, i) / math.sqrt(i))
        self.b = nn.Parameter(torch.zeros(o)) if bias else None

    def quant(self):
        g = self.w.abs().mean().clamp(min=1e-8)
        return torch.round(self.w / g).clamp(-1, 1), g

    def forward(self, x):
        wq, g = self.quant()
        return F.linear(x, self.w + (wq * g - self.w).detach(), self.b)


class TRNN(nn.Module):
    def __init__(self, H):
        super().__init__()
        self.inp, self.rec, self.out = TernaryLinear(2, H), TernaryLinear(H, H, bias=False), TernaryLinear(H, 1)
        self.H = H

    def forward(self, u, return_h=False):  # u: [B, T, 2]
        B, T, _ = u.shape
        h = torch.zeros(B, self.H, device=u.device)
        ys, hs = [], []
        for t in range(T):
            h = F.relu(self.inp(u[:, t]) + self.rec(h))
            ys.append(self.out(h).squeeze(-1))
            hs.append(h)
        y = torch.stack(ys, 1)
        return (y, torch.stack(hs, 1)) if return_h else y


def terras(n):
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def make_batch(rng, B, L):
    ns = [rng.getrandbits(L - 4) for _ in range(B)]
    u = torch.zeros(B, L, 2)
    y = torch.zeros(B, L)
    for i, n in enumerate(ns):
        t = terras(n)
        for j in range(L):
            u[i, j, 0] = float(j == 0)
            u[i, j, 1] = (n >> j) & 1
            y[i, j] = ((t >> (j - 1)) & 1) if j >= 1 else 0.0
    return u.to(DEV), y.to(DEV), ns


def minimal_terras_machine():
    """Minimal Mealy machine of the Terras transducer, from the (p, prev, carry) state space."""
    # states: 'S' (start) then (p, prev, carry); input x; output y (delayed sum bit), next state
    def step(state, x):
        if state == "S":
            p = x
            g = x  # +1 injection equals x at t=0 (prev=0)
            tot = x + g
            return tot % 2, (p, x, int(tot >= 2))
        p, prev, c = state
        g = p & prev
        tot = x + g + c
        return tot % 2, (p, x, int(tot >= 2))

    # reachable states
    states, frontier = {"S"}, ["S"]
    while frontier:
        s = frontier.pop()
        for x in (0, 1):
            _, ns = step(s, x)
            if ns not in states:
                states.add(ns)
                frontier.append(ns)
    return minimise({s: {x: step(s, x) for x in (0, 1)} for s in states})


def minimise(table):
    """Moore-style partition refinement on a Mealy machine {state: {x: (y, next)}}."""
    states = list(table)
    part = {s: tuple(table[s][x][0] for x in (0, 1)) for s in states}
    while True:
        sig = {s: (part[s], tuple(part[table[s][x][1]] for x in (0, 1))) for s in states}
        ids = {v: i for i, v in enumerate(sorted(set(sig.values())))}
        new = {s: ids[sig[s]] for s in states}
        if len(set(new.values())) == len(set(part.values())):
            return len(set(new.values()))
        part = new


def extract_machine(model, L=40, N=3000, seed=1):
    rng = random.Random(seed)
    u, y, ns = make_batch(rng, N, L)
    with torch.no_grad():
        yp, hs = model(u, return_h=True)
    pat = (hs > 0).cpu().numpy().astype(np.uint8)
    yb = (yp > 0).cpu().numpy().astype(int)
    ub = u[:, :, 1].cpu().numpy().astype(int)
    st = {}
    trans = defaultdict(set)
    n_states = 0
    for i in range(N):
        prev = "INIT"
        for t in range(L):
            key = pat[i, t].tobytes()
            if key not in st:
                st[key] = n_states
                n_states += 1
            trans[(prev, int(ub[i, t]), int(u[i, t, 0].item()))].add((int(yb[i, t]), st[key]))
            prev = st[key]
    deterministic = all(len(v) == 1 for v in trans.values())
    return n_states, deterministic, trans, st


def minimise_extracted(trans):
    """Minimise the extracted machine if deterministic; inputs are (x, start)."""
    tab = defaultdict(dict)
    for (s, x, start), outs in trans.items():
        (y, ns), = outs
        tab[s][(x, start)] = (y, ns)
    states = list(tab)
    inputs = sorted({k for s in states for k in tab[s]})
    part = {s: tuple(tab[s].get(k, (None, None))[0] for k in inputs) for s in states}
    while True:
        sig = {s: (part[s], tuple(part.get(tab[s].get(k, (None, None))[1]) for k in inputs)) for s in states}
        ids = {v: i for i, v in enumerate(sorted(set(sig.values()), key=str))}
        new = {s: ids[sig[s]] for s in states}
        if len(set(new.values())) == len(set(part.values())):
            return len(set(new.values()))
        part = new


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--H", type=int, default=16)
    ap.add_argument("--steps", type=int, default=20000)
    ap.add_argument("--seeds", type=int, default=3)
    a = ap.parse_args()
    m0 = minimal_terras_machine()
    print(f"minimal Terras Mealy machine: {m0} states (from the circuit's reachable (p,prev,carry) states)")
    out = dict(H=a.H, minimal_terras_states=m0, runs=[])
    for seed in range(a.seeds):
        torch.manual_seed(seed)
        rng = random.Random(seed)
        model = TRNN(a.H).to(DEV)
        opt = torch.optim.Adam(model.parameters(), lr=3e-3)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.steps)
        t0 = time.time()
        for step in range(1, a.steps + 1):
            L = rng.choice([12, 16, 24, 32])
            u, y, _ = make_batch(rng, 256, L)
            loss = F.binary_cross_entropy_with_logits(model(u), y)
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            sched.step()
            if step % 5000 == 0:
                print(f"  seed {seed} step {step} loss {loss:.4f} ({time.time()-t0:.0f}s)", flush=True)
        # exact match on 40-bit sequences (longer than training)
        u, y, ns = make_batch(random.Random(99), 2000, 40)
        with torch.no_grad():
            yp = (model(u) > 0).float()
        exact = float((yp == y).all(1).float().mean())
        bitacc = float((yp == y).float().mean())
        n_states, det, trans, _ = extract_machine(model)
        mini = minimise_extracted(trans) if det else None
        zs = []
        for m in model.modules():
            if isinstance(m, TernaryLinear):
                wq, _ = m.quant()
                zs.append(float((wq == 0).float().mean()))
        print(f"seed {seed}: exact-match on 40-bit n = {exact:.4f} (bit acc {bitacc:.4f}); binarised hidden states visited = {n_states}, "
              f"deterministic = {det}, minimised = {mini}; zero density per matrix = {[round(z, 2) for z in zs]}")
        out["runs"].append(dict(seed=seed, exact=exact, bitacc=bitacc, states=n_states, deterministic=det, minimised=mini, zero_density=zs))
    json.dump(out, open(RESULTS / "ternary_rnn.json", "w"), indent=1)
