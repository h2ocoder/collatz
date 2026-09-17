"""Q4: the cost of one prime.  Minimal ternary threshold circuit that tracks T(n) mod 3 from the
Terras circuit's output bit stream, and the combined Terras + mod-3 machine.

Tracker: reads the output bits y_t (LSB first) of T(n) and maintains R = sum y_i 2^i (mod 3).
Since 2^i = (-1)^i (mod 3), the update is R' = R + y*(1 if phase even else -1) (mod 3), with a
phase bit toggling every step.  State (phase, R): 6 states, encoded as lines (ph, r1, r0) with R
in {0,1,2} as (r1 r0) in {00, 01, 10}.  Outputs per step: ph', r1', r0'.  Rows: 12 reachable
(ph, R, y).  Exhaustive search for the minimal number of ternary threshold units, as in
minimal_circuit.py.  Then the combined machine: is the minimum for (Terras + tracker) equal to
5 + tracker, or can units be shared?  (Searched with the same DFS on the product rows.)

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/mod3_tracker_circuit.py
"""
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from minimal_circuit import threshold_functions, mask, NR as _NR  # noqa: E402,F401

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"


def dfs_generic(R, targets, target_names, K):
    """Generic exhaustive search: R rows x lines, targets list of 0/1 columns."""
    nr = R.shape[0]

    def m(col):
        return int("".join(str(int(v)) for v in col), 2)

    tmasks = [m(t) for t in targets]

    def rec(cols, names, funcs, depth_left):
        have = {m(c) for c in cols}
        missing = [j for j in range(len(targets)) if tmasks[j] not in have]
        if not missing:
            return list(zip(names, [funcs[m(c)] for c in cols]))
        if depth_left < len(missing):
            return None
        inputs = np.concatenate([R] + [c[:, None] for c in cols], axis=1) if cols else R
        tf = tfuncs(inputs, nr)
        cands = [tmasks[j] for j in missing if tmasks[j] in tf]
        if depth_left > len(missing):
            cands += [mk for mk in tf if mk not in have and mk not in tmasks]
        for mk in cands:
            col = np.array([int(b) for b in format(mk, f"0{nr}b")], dtype=np.int8)
            nm = target_names[tmasks.index(mk)] if mk in tmasks else f"h{len(cols)+1}"
            f2 = dict(funcs)
            f2[mk] = tf[mk]
            res = rec(cols + [col], names + [nm], f2, depth_left - 1)
            if res:
                return res
        return None

    return rec([], [], {}, K)


def tfuncs(inputs, nr):
    mcols = inputs.shape[1]
    W = np.array(list(itertools.product((-1, 0, 1), repeat=mcols)), dtype=np.int8)
    S = W @ inputs.T.astype(np.int8)
    out = {}
    pw = (1 << np.arange(nr - 1, -1, -1)).astype(np.int64)
    for theta in range(-mcols, mcols + 2):
        masks = ((S >= theta).astype(np.int64)) @ pw
        for i, mk in enumerate(masks):
            if mk not in out:
                out[int(mk)] = (W[i].tolist(), theta)
    return out


def tracker_rows():
    rows, outs = [], []
    for ph in (0, 1):
        for Rv in (0, 1, 2):
            for y in (0, 1):
                r1, r0 = Rv >> 1, Rv & 1
                Rn = (Rv + (y if ph == 0 else -y)) % 3
                rows.append((ph, r1, r0, y))
                outs.append((1 - ph, Rn >> 1, Rn & 1))
    return np.array(rows, dtype=np.int8), np.array(outs, dtype=np.int8)


if __name__ == "__main__":
    t0 = time.time()
    R, O = tracker_rows()
    targets = [O[:, j] for j in range(3)]
    names = ["ph'", "r1'", "r0'"]
    print("mod-3 tracker: 12 rows over lines (ph, r1, r0, y); targets ph', r1', r0'")
    best = None
    for K in range(3, 8):
        res = dfs_generic(R, targets, names, K)
        if res:
            best = (K, res)
            break
        print(f"  K={K}: none ({time.time()-t0:.0f}s)")
    K, circ = best
    print(f"MINIMUM tracker: {K} units")
    lines = ["ph", "r1", "r0", "y"]
    allw = []
    for i, (nm, (w, th)) in enumerate(circ):
        ins = lines + [c[0] for c in circ[:i]]
        print(f"  {nm:4s} = [ " + " ".join(f"{'+' if wj > 0 else '-'}{n}" for wj, n in zip(w, ins) if wj) + f" >= {th} ]")
        allw += w
    print(f"  zero density {allw.count(0)/len(allw):.3f}")

    # combined machine: Terras (5 units incl. y) feeding the tracker.  Lower bound: tracker alone
    # needs K units even given y; Terras needs 5 to produce y, p', carry'.  Can they share?  Search the
    # product: lines (start, x, p, prev, carry, ph, r1, r0), targets y, p', carry', ph', r1', r0'.
    from minimal_circuit import R as RT, T as TT, targets_of  # noqa: E402
    prod_rows, prod_out = [], []
    for i, row in enumerate(RT):
        y, pn, cn = TT[i]
        for ph in (0, 1):
            for Rv in (0, 1, 2):
                Rn = (Rv + (y if ph == 0 else -y)) % 3
                prod_rows.append(tuple(row) + (ph, Rv >> 1, Rv & 1))
                prod_out.append((y, pn, cn, 1 - ph, Rn >> 1, Rn & 1))
    PR, PO = np.array(prod_rows, dtype=np.int8), np.array(prod_out, dtype=np.int8)
    print(f"\ncombined Terras + mod-3 tracker: {PR.shape[0]} rows over 8 lines, 6 targets; searching K <= 8 (lower bound 5 + {K} if no sharing)")
    ptargets = [PO[:, j] for j in range(6)]
    pnames = ["y", "p'", "carry'", "ph'", "r1'", "r0'"]
    found = None
    for Kc in range(6, 9):
        res = dfs_generic(PR, ptargets, pnames, Kc)
        print(f"  K={Kc}: {'found' if res else 'none'} ({time.time()-t0:.0f}s)", flush=True)
        if res:
            found = (Kc, res)
            break
    result = dict(tracker_units=K, tracker_circuit=[(nm, w, th) for nm, (w, th) in circ],
                  combined_units=found[0] if found else None, combined_searched_to=8)
    if found:
        print(f"COMBINED MINIMUM: {found[0]} units (vs 5 + {K} = {5+K} without sharing)")
        for i, (nm, (w, th)) in enumerate(found[1]):
            ins = ["start", "x", "p", "prev", "carry", "ph", "r1", "r0"] + [c[0] for c in found[1][:i]]
            print(f"  {nm:6s} = [ " + " ".join(f"{'+' if wj > 0 else '-'}{n}" for wj, n in zip(w, ins) if wj) + f" >= {th} ]")
        result["combined_circuit"] = [(nm, w, th) for nm, (w, th) in found[1]]
    else:
        print(f"no combined circuit with <= 8 units found; the sum 5 + {K} = {5+K} stands as the best known")
    json.dump(result, open(RESULTS / "mod3_tracker_circuit.json", "w"), indent=1)
    print(f"elapsed {time.time()-t0:.0f}s")
