"""Census of primitive cycles of T_k(x) = x/2 | (3x+k)/2 for k coprime to 6, and the divergence side.

For each cycle (word v of length b with s odd steps, minimum x_min):
    x_min * (2^b - 3^s) = k * r(v)          (cycle equation; r(v) = parity-vector intercept)
    2^b / 3^s = prod_{odd i} (1 + k/(3 x_i))  <=  (1 + k/(3 x_min))^s
  =>  x_min <= k s / (3 w ln 2),   w = b - s log2 3   ("the slack inequality")
Both are checked on every cycle found.  Cycles are found by iterating from every odd start
below START_MAX (with gcd(start, k) = 1) and detecting returns; elements are capped at CAP.

Divergence: expected log2 growth per Terras step for px+k is (1/2) log2 p - 1: negative for
p = 3 (contract), positive for p >= 5.  We measure for 3x+k (k <= 600) that every start below
START_MAX reaches a cycle, and for 5x+1 / 7x+1 the fraction of starts that exceed 10^40.

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/cycles_3xk_census.py
"""
import json
import math
from collections import defaultdict
from fractions import Fraction
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
KMAX, START_MAX, CAP = 600, 20000, 10**9
L3 = math.log2(3)


def T(x, k, p=3):
    return x // 2 if x % 2 == 0 else (p * x + k) // 2


def cycle_from(x0, k, p=3, maxsteps=100000):
    """Iterate; return the cycle (as list starting at its min) if one is reached below CAP, else None."""
    x, seen = x0, {}
    path = []
    for t in range(maxsteps):
        if x in seen:
            cyc = path[seen[x]:]
            m = min(cyc)
            i = cyc.index(m)
            return cyc[i:] + cyc[:i]
        if x > CAP:
            return None
        seen[x] = t
        path.append(x)
        x = T(x, k, p)
    return None


def r_of(v):
    r, pow3 = 0, 1
    for i in range(len(v) - 1, -1, -1):
        if v[i]:
            r += pow3 << i
            pow3 *= 3
    return r


if __name__ == "__main__":
    out = {}
    per_k = {}
    viol_eq = viol_slack = 0
    all_cycles = []
    diverged = defaultdict(int)
    for k in range(1, KMAX + 1, 2):
        if k % 3 == 0:
            continue
        cycles = {}
        for x0 in range(1, START_MAX, 2):
            if gcd(x0, k) != 1:
                continue
            cyc = cycle_from(x0, k)
            if cyc is None:
                diverged[k] += 1
                continue
            if gcd(cyc[0], k) != 1:
                continue  # non-primitive (a lifted cycle of a divisor of k)
            cycles[cyc[0]] = cyc
        for m, cyc in cycles.items():
            b, s = len(cyc), sum(x % 2 for x in cyc)
            v = [x % 2 for x in cyc]
            rv = r_of(v)
            k_eff = (1 << b) - 3**s
            if m * k_eff != k * rv:
                viol_eq += 1
            w = b - s * L3
            slack = k * s / (3 * w * math.log(2))
            if m > slack + 1e-9:
                viol_slack += 1
            all_cycles.append(dict(k=k, min=m, b=b, s=s, w=w, slack=slack, r=rv))
        per_k[k] = sorted(cycles)
    print(f"k coprime to 6, k <= {KMAX}, starts < {START_MAX}, cap {CAP:.0e}: {len(all_cycles)} primitive cycles over {len(per_k)} values of k")
    print(f"  cycle equation x_min (2^b - 3^s) = k r(v): violations {viol_eq}")
    print(f"  slack inequality x_min <= k s / (3 w ln 2): violations {viol_slack}")
    print(f"  starts that did not reach a cycle below cap (any k): {sum(diverged.values())}")
    # distribution of the number of cycles per k
    nc = defaultdict(int)
    for k, c in per_k.items():
        nc[len(c)] += 1
    print("  number of primitive cycles per k -> how many k:", dict(sorted(nc.items())))
    print("  k with the most cycles:", sorted(per_k, key=lambda k: -len(per_k[k]))[:10], [len(per_k[k]) for k in sorted(per_k, key=lambda k: -len(per_k[k]))[:10]])
    print("  k = 1:", per_k[1], "  k = 5:", per_k[5], "  k = 7:", per_k[7], "  k = 13:", per_k[13], "  k = 47:", per_k[47][:8])
    # (b, s) of cycles: how close is b/s to log2 3?  compare k=1 vs others
    ws = [c["w"] for c in all_cycles]
    print(f"  waste w = b - s log2 3 over all cycles: min {min(ws):.4f}, median {sorted(ws)[len(ws)//2]:.3f}, max {max(ws):.3f}")
    # the slack ratio x_min / (k s / (3 w ln2)) : how tight is the inequality?
    ratios = sorted(c["min"] / c["slack"] for c in all_cycles)
    print(f"  tightness x_min / slack bound: median {ratios[len(ratios)//2]:.3f}, max {ratios[-1]:.3f}")
    # which (b,s) shapes occur and for which k: is k always a multiple of (2^b-3^s)/gcd(2^b-3^s, r)?
    need_ok = all((c["k"] * c["r"]) % ((1 << c["b"]) - 3**c["s"]) == 0 for c in all_cycles)
    print(f"  (2^b - 3^s) | k r(v) for every cycle: {need_ok}")
    shapes = defaultdict(set)
    for c in all_cycles:
        shapes[(c["b"], c["s"])].add(c["k"])
    print("  most common (b, s) shapes and how many k realise them:",
          sorted(((len(v), bs) for bs, v in shapes.items()), reverse=True)[:12])
    out["census"] = dict(n_cycles=len(all_cycles), viol_eq=viol_eq, viol_slack=viol_slack, per_k_counts={k: len(v) for k, v in per_k.items()},
                         diverged=dict(diverged))

    # ---------- divergence side
    print("\nDrift per Terras step, E[log2(T(x)/x)] = (1/2) log2 p - 1:")
    for p in (3, 5, 7):
        print(f"   p={p}: {0.5*math.log2(p) - 1:+.4f} bits/step")
    for p in (5, 7):
        big = 0
        cyc = 0
        for x0 in range(1, 2001, 2):
            x = x0
            seen = set()
            for _ in range(20000):
                if x in seen:
                    cyc += 1
                    break
                seen.add(x)
                x = T(x, 1, p)
                if x > 10**40:
                    big += 1
                    break
        print(f"   {p}x+1: of 1000 odd starts < 2000, {big} exceeded 10^40 within 20000 steps, {cyc} entered a cycle")
        out[f"{p}x+1"] = dict(exceeded_1e40=big, cycled=cyc)
    json.dump(out, open(RESULTS / "cycles_3xk_census.json", "w"), indent=1)
