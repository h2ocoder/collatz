"""Skeptic check of the remaining numerical statements of Q4.1-c/f/g.

  1. totient sieve to 5.6*10^6 (complete for m <= 10^6 since x <= 5.5394 phi(x)): number of
     totient values <= 10^6, mean fibre size overall and over 3-smooth values; A014197 against
     the inverse-totient counts of v1 for m <= 6000 is NOT repeated here.
  2. level sets a + b = n: where is A(a, n - a) largest?  (uses the exact table of v1b, rebuilt
     here in float64 from the Pierpont points file.)
  3. the 'equal multiplier' saddle prediction of the ridge, points-only form:
     theta(s) = sum_p i ln2 w_p / sum_p ln(p-1) w_p,  w_p = 1/(1 + (p-1)^s).
  4. numerology control for Q4.1-b: for every 3-smooth m = 2^a 3^b <= 10^4, the three numbers
     m/6 + 1, m/2 + 1, m + 1 -- how often are all three prime?  (36 is not alone.)

Run:  python -X utf8 v7_misc.py
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np
from sympy import isprime

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
LOG = open(os.path.join(HERE, "v7_misc.log"), "w", encoding="utf-8")
LN2, LN3 = math.log(2), math.log(3)


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")


def phi_sieve(N):
    spf = np.zeros(N + 1, dtype=np.int32)
    for p in range(2, int(N ** 0.5) + 2):
        if spf[p] == 0:
            seg = spf[p * p:: p]
            seg[seg == 0] = p
    idx = np.arange(N + 1, dtype=np.int32)
    pr = spf == 0
    pr[:2] = False
    spf[pr] = idx[pr]
    phi = np.zeros(N + 1, dtype=np.int64)
    phi[1] = 1
    phi[2] = 1
    lo = 3
    while lo <= N:
        hi = min(N, 2 * lo - 2)
        n = np.arange(lo, hi + 1, dtype=np.int64)
        p = spf[lo: hi + 1].astype(np.int64)
        m = n // p
        phi[lo: hi + 1] = np.where(m == 1, n - 1, np.where(m % p == 0, phi[m] * p, phi[m] * (p - 1)))
        lo = hi + 1
    return phi


def main():
    t0 = time.time()
    M = 10 ** 6
    N = 5_600_000
    assert 2 * 1.5 * 1.25 * 7 / 6 * 1.1 * 13 / 12 * 17 / 16 * M < N and 1 * 2 * 4 * 6 * 10 * 12 * 16 * 18 > M
    phi = phi_sieve(N)
    cnt = np.bincount(phi[1:][phi[1:] <= M], minlength=M + 1)
    vals = int(np.count_nonzero(cnt[1:]))
    out(f"1. totient values <= 10^6: {vals}  (researcher / Ford's table: 180184);  preimages: {int(cnt[1:].sum())};"
        f"  mean fibre size {cnt[1:].sum() / vals:.3f}   [{time.time() - t0:.0f} s]")
    sm = []
    a = 0
    while 2 ** a <= M:
        b = 0
        while 2 ** a * 3 ** b <= M:
            sm.append((2 ** a * 3 ** b, a, b))
            b += 1
        a += 1
    tv = [m for m, a, b in sm if cnt[m] > 0]
    out(f"   3-smooth m <= 10^6: {len(sm)};  totient values among them: {len(tv)};  mean fibre size over those: {np.mean([cnt[m] for m in tv]):.3f}")
    with open(os.path.join(PARENT, "q41_table.json"), encoding="utf-8") as f:
        A = json.load(f)["A"]
    bad = sum(1 for m, a, b in sm if int(cnt[m]) != A[a][b])
    out(f"   sieve count equals the table A(a,b) for all {len(sm)} of them: mismatches {bad}")
    assert bad == 0 and vals == 180184
    first = {}
    for m in range(1, M + 1):
        k = int(cnt[m])
        if k >= 2 and k not in first:
            first[k] = m
    out("   least m with exactly k solutions, k = 2..36 (sieve):", [first.get(k) for k in range(2, 37)])
    oeis = [1, 2, 4, 8, 12, 32, 36, 40, 24, 48, 160, 396, 2268, 704, 312, 72, 336, 216, 936, 144, 624, 1056, 1760,
            360, 2560, 384, 288, 1320, 3696, 240, 768, 9000, 432, 7128, 4200]
    out("   equals the 35 terms of OEIS A007374 fetched today:", [first.get(k) for k in range(2, 37)] == oeis)
    assert [first.get(k) for k in range(2, 37)] == oeis

    # 2. level sets a + b = n
    with open(os.path.join(PARENT, "q41_pierpont_points_480x300.json"), encoding="utf-8") as f:
        P = [tuple(p) for p in json.load(f)]
    AM, BM = 480, 300
    D = np.zeros((AM + 1, BM + 1))
    D[0, 0] = 1
    for i, j in P:
        D[i:, j:] += D[: AM + 1 - i, : BM + 1 - j].copy()
    E = D + np.cumsum(D, axis=0)
    At = E.copy()
    At[1:, :] += np.cumsum(E[:-1, :], axis=1)
    out("\n2. level sets a + b = n: argmax of A(a, n - a)")
    for n in (40, 80, 120, 160, 200, 240, 280):
        a = max(range(1, n), key=lambda a_: At[a_, n - a_] if n - a_ <= BM else -1)
        out(f"   n = {n:>3d}: a* = {a}, b* = {n - a}, b*/a* = {(n - a) / a:.3f}")

    # 3. saddle, points only
    out("\n3. equal-multiplier saddle, Pierpont part only: theta(s) = sum i ln2 w / sum ln(p-1) w, w = 1/(1 + (p-1)^s)")
    size = np.array([i * LN2 + j * LN3 for i, j in P])
    X = np.array([i * LN2 for i, j in P])
    for L, s in ((60, 0.2214), (100, 0.1719), (140, 0.1455), (180, 0.1284), (220, 0.1163), (260, 0.1071), (300, 0.0998), (320, 0.0966)):
        w = 1 / (1 + np.exp(np.minimum(s * size, 700)))
        out(f"   L = {L:>3d} (s = {s}): theta = {float((X * w).sum() / (size * w).sum()):.3f};  sum ln(p-1) w = {float((size * w).sum()):.1f}"
            f"  (should be close to L minus the absorption part)")

    # 4. numerology control
    out("\n4. CONTROL for 'phi(x) = 36 has eight solutions because 7, 19, 37 are all prime':")
    out("   3-smooth m = 2^a 3^b with a, b >= 1, m <= 10^6, for which m/6 + 1, m/2 + 1 and m + 1 are all prime:")
    hits = [(m, a, b) for m, a, b in sorted(sm) if a >= 1 and b >= 1 and isprime(m // 6 + 1) and isprime(m // 2 + 1) and isprime(m + 1)]
    out("    ", [(m, (a, b), (m // 6 + 1, m // 2 + 1, m + 1)) for m, a, b in hits])
    out("   (the triple of primes is a statement at every lattice point; it decides the count 8 only at (2,2),")
    out("    because only there are (a-1,b-1), (a-1,b), (a,b) the ONLY usable Pierpont points.)")
    out("   A(a,b) at these points:", [(m, A[a][b]) for m, a, b in hits if a <= 40 and b <= 40])
    out(f"\ndone in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
