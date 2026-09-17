"""L11 analysis: match a trained RNN's reachable hidden states to the 5 states of the minimal
Terras Mealy machine by behavioural signature, and report how much of the reachable set is
exactly one of the five (vs. 'glitch' states with some deviating continuation).

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/rnn_state_match.py <checkpoint stem> [<stem> ...]
  e.g. ternary_rnn_fp2_H16_s0  ternary_rnn_H64_H64_s0
"""
import random
import sys
from collections import Counter
from pathlib import Path

import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ternary_rnn import TRNN, TernaryLinear, make_batch, DEV, RESULTS  # noqa: E402

HORIZON = 8


def ideal_signatures():
    """Signature (outputs on all 2^H continuations) of each state of the ideal transducer."""
    def step(state, x):
        p, prev, c = state
        g = p & prev
        tot = x + g + c
        return tot % 2, (p, x, int(tot >= 2))
    # reachable non-start states
    states = set()
    for x0 in (0, 1):  # after the start token
        p = x0
        tot = x0 + x0
        states.add((p, x0, int(tot >= 2)))
    frontier = list(states)
    while frontier:
        s = frontier.pop()
        for x in (0, 1):
            _, ns = step(s, x)
            if ns not in states:
                states.add(ns)
                frontier.append(ns)
    sigs = {}
    for s in states:
        out = []
        for c in range(1 << HORIZON):
            st = s
            for j in range(HORIZON):
                y, st = step(st, (c >> j) & 1)
                out.append(y)
        sigs.setdefault(tuple(out), []).append(s)
    return sigs  # signature -> list of (p, prev, carry) states sharing it (merged = same minimal state)


def rnn_signatures(model, N=400, L=32, seed=5):
    rng = random.Random(seed)
    u, _, _ = make_batch(rng, N, L)
    with torch.no_grad():
        _, hs = model(u, return_h=True)
        H = torch.unique(torch.round(hs.reshape(-1, hs.shape[-1]) * 1e4) / 1e4, dim=0)
        conts = torch.tensor([[(c >> j) & 1 for j in range(HORIZON)] for c in range(1 << HORIZON)], dtype=torch.float32, device=DEV)
        C = conts.shape[0]
        sigs = []
        for i in range(0, H.shape[0], 256):
            h0 = H[i:i + 256]
            B = h0.shape[0]
            h = h0.repeat_interleave(C, 0)
            x = conts.repeat(B, 1)
            outs = []
            for t in range(HORIZON):
                ut = torch.stack([torch.zeros_like(x[:, t]), x[:, t]], 1)
                h = F.relu(model.inp(ut) + model.rec(h))
                outs.append((model.out(h).squeeze(-1) > 0).int())
            sigs.append(torch.stack(outs, 1).view(B, C * HORIZON).cpu())
    return [tuple(r.tolist()) for r in torch.cat(sigs)]


if __name__ == "__main__":
    ideal = ideal_signatures()
    print(f"ideal machine: {len(ideal)} distinct behavioural states (minimal Mealy machine)")
    for stem in sys.argv[1:]:
        fp = "fp" in stem
        TernaryLinear.full_precision = fp
        H = int(stem.split("_H")[-1].split("_")[0])
        model = TRNN(H).to(DEV)
        model.load_state_dict(torch.load(RESULTS / "checkpoints" / f"{stem}.pt", map_location=DEV))
        model.eval()
        sigs = rnn_signatures(model)
        cnt = Counter(sigs)
        exact_states = {s: c for s, c in cnt.items() if s in ideal}
        n_exact = sum(exact_states.values())
        print(f"\n{stem} ({'full precision' if fp else 'ternary'}, H={H}): {len(sigs)} reachable hidden states, {len(cnt)} behavioural classes")
        # the minimal Mealy machine has 5 states; one is the start state, never revisited, so
        # reachable hidden states after the first input can only realise the other 4
        print(f"  hidden states whose horizon-{HORIZON} behaviour equals one of the {len(ideal)} ideal non-start states: {n_exact}/{len(sigs)} = {n_exact/len(sigs):.4f}")
        print(f"  ideal non-start states realised: {len(exact_states)}/{len(ideal)}; glitch classes: {len(cnt) - len(exact_states)} covering {len(sigs) - n_exact} states")
        # how far are glitch classes from the nearest ideal signature (Hamming distance over 2048 outputs)?
        far = []
        for s, c in cnt.items():
            if s not in ideal:
                d = min(sum(a != b for a, b in zip(s, t)) for t in ideal)
                far.append((d, c))
        if far:
            far.sort()
            print(f"  glitch classes: nearest-ideal Hamming distances (of {(1 << HORIZON) * HORIZON} outputs) and sizes: {far[:8]}")
