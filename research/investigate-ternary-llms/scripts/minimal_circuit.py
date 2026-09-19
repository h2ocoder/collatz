"""L10: minimal ternary-weight threshold circuit for the Terras transducer.

The Terras layer of ternary_syracuse_circuit.py processes one bit per step with
state (p, prev_x, carry) and inputs (start, x).  Per step it must produce
    y      = (x + g + carry) mod 2,        g = (p AND prev_x) OR (start AND x)
    p'     = p OR (start AND x)
    carry' = majority(x, g, carry)
(prev_x' = x is a free copy; the one-step delay of y is the division by 2.)
The hand-built circuit uses 8 threshold units (plus 3 for the comparator).

Reachable input rows: start=1 => p=prev=carry=0 (2 rows); start=0, p=0 => carry=0
(4 rows); start=0, p=1 => 8 rows.  14 rows total.  A unit is [sum_j w_j in_j >= theta]
with w in {-1,0,+1} over the 5 lines plus any earlier unit in the same step.

Search: exhaustive for K <= 4 total units (targets included, any dependency order),
then a bounded search for K = 5..7 that only allows helpers drawn from single-unit
functions.  Reports the minimum found and the zero density of the dense weight
matrix of each optimal circuit.

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/minimal_circuit.py
"""
import itertools
import json
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
LINES = ["start", "x", "p", "prev", "carry"]

# ---------------------------------------------------------------- rows and targets
rows = []
for x in (0, 1):
    rows.append((1, x, 0, 0, 0))
for prev in (0, 1):
    for x in (0, 1):
        rows.append((0, x, 0, prev, 0))
for prev in (0, 1):
    for c in (0, 1):
        for x in (0, 1):
            rows.append((0, x, 1, prev, c))
R = np.array(rows, dtype=np.int8)  # 14 x 5
NR = len(rows)


def targets_of(row):
    s, x, p, prev, c = row
    g = (p and prev) or (s and x)
    tot = x + g + c
    return tot % 2, int(p or (s and x)), int(tot >= 2)


T = np.array([targets_of(r) for r in rows], dtype=np.int8)  # 14 x 3  (y, p', carry')
TARGET_NAMES = ["y", "p'", "carry'"]


def mask(col):
    return int("".join(str(int(v)) for v in col), 2)


TARGET_MASKS = [mask(T[:, j]) for j in range(3)]


def threshold_functions(inputs):
    """All Boolean functions over the 14 rows realizable as a ternary threshold unit
    of the given input columns (14 x m).  Returns {mask: (weights, theta)} (first found)."""
    m = inputs.shape[1]
    W = np.array(list(itertools.product((-1, 0, 1), repeat=m)), dtype=np.int8)  # 3^m x m
    S = W @ inputs.T.astype(np.int8)  # 3^m x 14
    out = {}
    for theta in range(-m, m + 2):
        F_ = (S >= theta).astype(np.int8)
        pw = (1 << np.arange(NR - 1, -1, -1)).astype(np.int64)
        masks = F_ @ pw
        for i, mk in enumerate(masks):
            if mk not in out:
                out[int(mk)] = (W[i].tolist(), theta)
    return out


def dfs(cols, names, funcs, K, found, depth_left):
    """cols: list of 14-vectors computed so far (beyond the 5 lines); names: their labels.
    funcs: dict mask->(w,theta) for each computed unit.  Return a circuit if all targets
    are among the computed units within depth_left more units."""
    have = {mask(c) for c in cols}
    missing = [j for j in range(3) if TARGET_MASKS[j] not in have]
    if not missing:
        return list(zip(names, [funcs[mask(c)] for c in cols]))
    if depth_left < len(missing):
        return None
    inputs = np.concatenate([R] + [c[:, None] for c in cols], axis=1) if cols else R
    tf = threshold_functions(inputs)
    # candidates: if depth_left == len(missing) we must add a target now
    cands = [TARGET_MASKS[j] for j in missing if TARGET_MASKS[j] in tf]
    if depth_left > len(missing):
        cands += [mk for mk in tf if mk not in have and mk not in TARGET_MASKS]
    for mk in cands:
        col = np.array([int(b) for b in format(mk, f"0{NR}b")], dtype=np.int8)
        nm = TARGET_NAMES[TARGET_MASKS.index(mk)] if mk in TARGET_MASKS else f"h{len(cols)+1}"
        funcs2 = dict(funcs)
        funcs2[mk] = tf[mk]
        res = dfs(cols + [col], names + [nm], funcs2, K, found, depth_left - 1)
        if res:
            return res
    return None


if __name__ == "__main__":
    t0 = time.time()
    f1 = threshold_functions(R)
    print(f"{len(f1)} distinct single-unit ternary threshold functions of the 5 lines over {NR} reachable rows")
    print("targets realizable by a single unit:", [TARGET_NAMES[j] for j in range(3) if TARGET_MASKS[j] in f1])

    best = None
    for K in range(3, 8):
        print(f"searching K = {K} units ... ({time.time()-t0:.0f}s)", flush=True)
        res = dfs([], [], {}, K, None, K)
        if res:
            best = (K, res)
            break
    if best is None:
        print("no circuit with <= 7 units found by this search (the hand-built one has 8)")
    else:
        K, circ = best
        print(f"\nMINIMUM FOUND: {K} units")
        allw = []
        for i, (nm, (w, th)) in enumerate(circ):
            ins = LINES + [c[0] for c in circ[:i]]
            terms = " ".join(f"{'+' if wj > 0 else '-'}{n}" for wj, n in zip(w, ins) if wj)
            print(f"  {nm:7s} = [ {terms} >= {th} ]")
            allw += w
        z = allw.count(0) / len(allw)
        print(f"dense zero density of the optimal circuit's weight matrix: {z:.3f} ({allw.count(0)}/{len(allw)})")
        json.dump(dict(K=K, circuit=[(nm, w, th) for nm, (w, th) in circ], zero_density=z,
                       n_single_unit_functions=len(f1), seconds=time.time() - t0),
                  open(RESULTS / "minimal_circuit.json", "w"), indent=1)
    print(f"elapsed {time.time()-t0:.0f}s")
