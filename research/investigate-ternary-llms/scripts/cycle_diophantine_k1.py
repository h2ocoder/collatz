"""Why 3x+1 is special, made quantitative.

A cycle of T_k with s odd steps, length b, waste w = b - s log2 3 > 0 and minimum x_min obeys
    2^b / 3^s = prod_{odd} (1 + k/(3 x_i)) <= (1 + k/(3 x_min))^s
so  x_min <= k s / (3 w ln 2)        (slack inequality; exact for k = 1 with the +1 replaced by k).
For k = 1: every n < X0 = 2^71 is verified to reach 1 (Barina), so a nontrivial cycle needs
x_min >= X0, hence w <= s / (3 X0 ln 2): the pair (s, b) must approximate log2 3 from above to
within ~ s / (2 * 10^21).  Such pairs are the upper semiconvergents (record trit packings) of
log2 3 with enormous s.  This script lists the record packings, the maximal x_min each permits
for k = 1, and the first record whose bound exceeds X0 -- i.e. the minimal length of a
nontrivial 3x+1 cycle.  For k = 2^b - 3^s the same inequality gives x_min <= s 3^s (2^w-1)/(3 w ln2)
~ s 3^s / 3: no constraint at all -- the cycles are unconstrained and all necklaces occur.

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/cycle_diophantine_k1.py
"""
import json
import math
from pathlib import Path

import mpmath as mp

mp.mp.dps = 80
HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
L3 = mp.log(3, 2)
X0 = mp.mpf(2) ** 71  # verified convergence bound (Barina)


def record_packings(smax):
    """Upper semiconvergents s of log2 3 up to smax: records of w(s) = ceil(s L3) - s L3."""
    best = mp.mpf(2)
    recs = []
    # walk convergents via continued fraction to reach large s cheaply
    cf = mp.identify  # unused; do a direct scan with the CF-generated candidates
    # generate continued fraction of log2 3
    a = []
    x = L3
    for _ in range(40):
        ai = int(mp.floor(x))
        a.append(ai)
        x = 1 / (x - ai)
    # convergents p/q and intermediate fractions (p_{n-1} + t p_n)/(q_{n-1} + t q_n)
    p0, q0, p1, q1 = 1, 0, a[0], 1
    cands = {1}
    for ai in a[1:]:
        for t in range(1, ai + 1):
            q = q0 + t * q1
            if q <= smax:
                cands.add(q)
        p0, q0, p1, q1 = p1, q1, p1 * ai + p0, q1 * ai + q0
        if q1 > smax:
            break
    for s in sorted(cands):
        w = mp.ceil(s * L3) - s * L3
        if w < best:
            best = w
            recs.append((s, int(mp.ceil(s * L3)), w))
    return recs


if __name__ == "__main__":
    recs = record_packings(10**13)
    print("record trit packings s (upper semiconvergents of log2 3), waste w, and the LARGEST minimum a 3x+1 cycle with s odd steps could have:")
    print("        s              b            w(s)         x_min <= s/(3 w ln2)      vs verified 2^71 = 2.36e21")
    first = None
    rows = []
    for s, b, w in recs:
        bound = mp.mpf(s) / (3 * w * mp.log(2))
        ok = bound >= X0
        if ok and first is None:
            first = (s, b)
        rows.append((s, b, float(w), float(bound), bool(ok)))
        if s < 400 or ok or s in (971, 15601):
            print(f"  {s:13d}  {b:13d}   {mp.nstr(w, 6):>10}   {mp.nstr(bound, 5):>16}     {'possible' if ok else 'impossible'}")
    print(f"\nFirst record packing whose bound clears the verified range: s = {first[0]}, b = {first[1]}  ->")
    print(f"  any nontrivial 3x+1 cycle has at least {first[0]} odd steps and length at least {first[1]} (Eliahou-style bound from x_min > 2^71).")
    # the same inequality for k = 2^b - 3^s at a small record packing: vacuous
    for s, b, w in recs[:6]:
        k = (1 << b) - 3**s
        bound_k = mp.mpf(k) * s / (3 * w * mp.log(2))
        print(f"  k = 2^{b} - 3^{s} = {k}: slack bound x_min <= {mp.nstr(bound_k, 5)}  vs natural cycle scale 3^s = {3**s}  -> unconstrained")
    json.dump(dict(first_possible=dict(s=first[0], b=first[1]), records=[dict(s=s, b=b, w=w, bound=bd, possible=ok) for s, b, w, bd, ok in rows]),
              open(RESULTS / "cycle_diophantine_k1.json", "w"), indent=1)
