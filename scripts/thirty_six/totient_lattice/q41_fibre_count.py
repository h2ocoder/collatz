"""Q4.1  A(a,b) = #{x : phi(x) = 2^a 3^b} as a restricted two-dimensional partition count.

GENERATING FUNCTION (proved in README, section Q4.1)

    sum_{a,b>=0} A(a,b) X^a Y^b
        = (1 + 1/(1-X)) * (1 + X/(1-Y)) * prod_{(i,j) in P} (1 + X^i Y^j)

    P = {(i,j) : i>=1, j>=0, (i,j) != (1,0), 2^i 3^j + 1 prime}   (Pierpont primes > 3)

    factor 1 + 1/(1-X)   : the power of 2 in x.  2^alpha contributes (alpha-1, 0), alpha>=1.
    factor 1 + X/(1-Y)   : the power of 3 in x.  3^beta  contributes (1, beta-1),  beta>=1.
    factor 1 + X^i Y^j   : the Pierpont prime 2^i 3^j + 1, used at most once (squarefree part).

So with D(c,d) = number of sets of distinct Pierpont points summing to (c,d) and
R(u,v) = number of 3-smooth x with phi(x) = 2^u 3^v,

    A(a,b) = sum_{c<=a, d<=b} D(c,d) R(a-c, b-d),
    R(0,0)=2, R(0,v>0)=0, R(1,0)=3, R(u>=2,0)=2, R(1,v>=1)=2, R(u>=2,v>=1)=1.

This script
  1. builds P with proved primality (Lucas certificates, see pierpont.py),
  2. computes D and A exactly (Python ints) for a,b <= 40 and prints a,b <= 30,
  3. lists the eight lattice decompositions at (2,2),
  4. verifies A against a brute-force totient sieve (every 3-smooth m <= 10^6),
  5. recomputes A014197 / A007374 from the sieve: 36 is the least m (over ALL m) with
     exactly eight solutions, and says which first-k-fold values are 3-smooth.

Run:  python -X utf8 q41_fibre_count.py   (about 15 s)
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pierpont import pierpont_points  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "q41_fibre_count.log"), "w", encoding="utf-8")


def out(*args):
    s = " ".join(str(a) for a in args)
    print(s)
    LOG.write(s + "\n")


def subset_counts(points, amax, bmax):
    """D[c][d] = number of subsets of `points` with coordinate sum (c,d); exact ints."""
    D = np.zeros((amax + 1, bmax + 1), dtype=object)
    D[:, :] = 0
    D[0, 0] = 1
    for i, j in points:
        if i > amax or j > bmax:
            continue
        # 0/1 knapsack: the right-hand side is evaluated from the old D before assignment
        D[i:, j:] = D[i:, j:] + D[: amax + 1 - i, : bmax + 1 - j]
    return D


def absorb(D):
    """A = D convolved with R, i.e. multiply by (1 + 1/(1-X)) (1 + X/(1-Y))."""
    amax, bmax = D.shape[0] - 1, D.shape[1] - 1
    # E = D * (2 + X + X^2 + ...) = D + cumulative sum of D along a
    E = D.copy()
    run = np.zeros(bmax + 1, dtype=object)
    run[:] = 0
    for a in range(amax + 1):
        run = run + D[a, :]
        E[a, :] = D[a, :] + run - D[a, :] + D[a, :]  # = D[a] + sum_{c<=a} D[c]
    # A = E * (1 + X (1 + Y + Y^2 + ...)) = E(a,b) + sum_{d<=b} E(a-1,d)
    A = E.copy()
    for a in range(1, amax + 1):
        cs = 0
        for b in range(bmax + 1):
            cs = cs + E[a - 1, b]
            A[a, b] = E[a, b] + cs
    return A


def R(u, v):
    if u < 0 or v < 0:
        return 0
    if u == 0:
        return 2 if v == 0 else 0
    if v == 0:
        return 3 if u == 1 else 2
    return 2 if u == 1 else 1


def smooth_solutions(u, v):
    """3-smooth x = 2^alpha 3^beta with phi(x) = 2^u 3^v, as (alpha, beta) pairs."""
    sols = []
    for beta in range(0, v + 2):
        for alpha in range(0, u + 2):
            uu = (alpha - 1 if alpha >= 1 else 0) + (1 if beta >= 1 else 0)
            vv = beta - 1 if beta >= 1 else 0
            if (uu, vv) == (u, v):
                sols.append((alpha, beta))
    return sols


def enumerate_solutions(a, b, points):
    """All x with phi(x) = 2^a 3^b, each with its lattice decomposition."""
    pts = sorted(p for p in points if p[0] <= a and p[1] <= b)
    res = []

    def rec(k, c, d, chosen):
        if k == len(pts):
            for alpha, beta in smooth_solutions(a - c, b - d):
                x = (1 << alpha) * 3 ** beta
                for i, j in chosen:
                    x *= (1 << i) * 3 ** j + 1
                res.append((x, alpha, beta, tuple(chosen)))
            return
        rec(k + 1, c, d, chosen)
        i, j = pts[k]
        if c + i <= a and d + j <= b:
            rec(k + 1, c + i, d + j, chosen + [(i, j)])

    rec(0, 0, 0, [])
    return sorted(res)


def totient_sieve(n):
    phi = np.arange(n + 1, dtype=np.int64)
    is_comp = np.zeros(n + 1, dtype=bool)
    for p in range(2, n + 1):
        if not is_comp[p]:
            is_comp[p * p::p] = True if p * p <= n else False
            phi[p::p] -= phi[p::p] // p
    return phi


def preimage_bound(M):
    """Rigorous B with: phi(x) <= M  =>  x <= B * phi(x).

    If x has w distinct primes then phi(x) >= prod_{first w primes}(p-1), and
    x/phi(x) = prod_{p|x} p/(p-1) <= prod_{first w primes} p/(p-1).
    """
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    prod, B = 1, 1.0
    for p in primes:
        if prod * (p - 1) > M:
            break
        prod *= p - 1
        B *= p / (p - 1)
    return B


def main():
    t0 = time.time()
    AMAX = BMAX = 40
    P = pierpont_points(AMAX, BMAX)
    out(f"Pierpont points (i,j), 1<=i<={AMAX}, 0<=j<={BMAX}, primality proved by Lucas certificate: {len(P)}")
    out("  with i+j <= 8:", sorted([p for p in P if p[0] + p[1] <= 8], key=lambda t: (t[0] + t[1], t[0])))
    out("  as primes     :", sorted((1 << i) * 3 ** j + 1 for i, j in P if i + j <= 8))

    D = subset_counts(P, AMAX, BMAX)
    A = absorb(D)

    # --- cross-check `absorb` against the explicit R-convolution on a small box
    for a in range(0, 13):
        for b in range(0, 13):
            s = sum(D[c, d] * R(a - c, b - d) for c in range(a + 1) for d in range(b + 1))
            assert s == A[a, b], (a, b, s, A[a, b])
    out("absorb() agrees with the explicit sum over R on 0<=a,b<=12")

    out("\nTABLE 1.  A(a,b) = #{x : phi(x) = 2^a 3^b}.  rows a = 0..30 (power of 2), columns b = 0..12 (power of 3)")
    out("      b=" + "".join(f"{b:>9d}" for b in range(13)))
    for a in range(31):
        out(f"a={a:>2d}   " + "".join(f"{int(A[a, b]):>9d}" for b in range(13)))
    out("\n(the full exact table for 0<=a,b<=40 is in q41_table.json)")

    out("\nTABLE 1b.  D(c,d) = number of sets of distinct Pierpont points summing to (c,d), c = 0..12, d = 0..8")
    out("      d=" + "".join(f"{d:>7d}" for d in range(9)))
    for c in range(13):
        out(f"c={c:>2d}   " + "".join(f"{int(D[c, d]):>7d}" for d in range(9)))

    out("\nRow b = 0 (phi(x) = 2^a):", [int(A[a, 0]) for a in range(41)])
    out("  -> a+2 for a <= 31 and 32 for a >= 32 (five Fermat primes 3,5,17,257,65537; exponents 1,2,4,8,16 sum to 31)")
    out("Column a = 0 (phi(x) = 3^b):", [int(A[0, b]) for b in range(8)], " (phi is even beyond 1)")
    out("Column a = 1 (phi(x) = 2*3^b):", [int(A[1, b]) for b in range(41)])
    out("  -> 3 at b = 0; otherwise 4 when 2*3^b + 1 is prime and 2 when it is not")
    out("Diagonal A(a,a) (phi(x) = 6^a):", [int(A[a, a]) for a in range(26)])

    # --- the eight decompositions at (2,2)
    out("\nTHE EIGHT SOLUTIONS OF phi(x) = 36 = 2^2 3^2 AS LATTICE DECOMPOSITIONS OF (2,2)")
    out("  x     = 2^alpha * 3^beta * (Pierpont primes)        (2,2) = [from 2^alpha] + [from 3^beta] + Pierpont points")
    sols = enumerate_solutions(2, 2, P)
    for x, alpha, beta, chosen in sols:
        c2 = (alpha - 1, 0) if alpha >= 1 else (0, 0)
        c3 = (1, beta - 1) if beta >= 1 else (0, 0)
        primes = [(1 << i) * 3 ** j + 1 for i, j in chosen]
        out(f"  {x:>4d} = 2^{alpha} * 3^{beta} * {str(primes) if primes else '1':<6}   "
            f"(2,2) = {c2} + {c3} + {list(chosen)}")
    assert [s[0] for s in sols] == [37, 57, 63, 74, 76, 108, 114, 126]
    out("  grouped by Pierpont part:  D(2,2)R(0,0) + D(1,2)R(1,0) + D(1,1)R(1,1) + D(0,0)R(2,2)"
        f" = {D[2,2]}*{R(0,0)} + {D[1,2]}*{R(1,0)} + {D[1,1]}*{R(1,1)} + {D[0,0]}*{R(2,2)} = "
        f"{D[2,2]*R(0,0) + D[1,2]*R(1,0) + D[1,1]*R(1,1) + D[0,0]*R(2,2)}")
    out("  the other Pierpont points below (2,2) are (2,0) [5] and (2,1) [13]; their remainders are (0,2) and (0,1),")
    out("  and R(0,v) = 0 for v > 0 (a power of 3 always brings a factor 2), so 5 and 13 divide no solution.")

    # --- closed form of the column a = 2 (derived in the README from the generating function)
    Pset = set(P)
    bad = 0
    for b in range(1, BMAX + 1):
        pairs = sum(1 for d1 in range(1, b) for d2 in range(d1 + 1, b) if d1 + d2 == b
                    and (1, d1) in Pset and (1, d2) in Pset)
        f = (1 + 2 * sum(1 for d in range(1, b) if (1, d) in Pset) + 3 * ((1, b) in Pset)
             + 2 * ((2, b) in Pset) + 2 * pairs)
        bad += f != A[2, b]
    out("\nCOLUMN a = 2.  A(2,b) = 1 + 2 #{1<=d<b : 2*3^d+1 prime} + 3 [2*3^b+1 prime] + 2 [4*3^b+1 prime]")
    out(f"              + 2 #{{d1<d2, d1+d2=b : 2*3^d1+1 and 2*3^d2+1 prime}}   for b >= 1: mismatches for b <= {BMAX}: {bad}")
    assert bad == 0
    out("  at b = 2:  A(2,2) = 1 + 2 [7 prime] + 3 [19 prime] + 2 [37 prime] = 8, the largest value the formula allows.")

    # --- brute force
    N = 10 ** 7
    M = 10 ** 6
    B = preimage_bound(M)
    assert B * M < N
    out(f"\nBRUTE FORCE.  totient sieve to N = {N}; phi(x) <= {M} implies x <= {B:.4f} * phi(x) < N,")
    out("  so the sieve sees every solution of phi(x) = m for every m <= 10^6.")
    phi = totient_sieve(N)
    cnt = np.bincount(phi[1:], minlength=N + 1)
    checked = mism = 0
    a = 0
    while (1 << a) <= M:
        b = 0
        while (1 << a) * 3 ** b <= M:
            m = (1 << a) * 3 ** b
            if a <= AMAX and b <= BMAX:
                checked += 1
                if int(cnt[m]) != int(A[a, b]):
                    mism += 1
                    out("  MISMATCH", a, b, m, int(cnt[m]), int(A[a, b]))
            b += 1
        a += 1
    out(f"  3-smooth m <= 10^6 checked: {checked}, mismatches between sieve count and formula: {mism}")
    assert mism == 0
    out("  phi^-1(36) from the sieve:", np.nonzero(phi[: 400] == 36)[0].tolist())

    # --- A014197 / A007374
    out("\nA014197(m) for m = 1..40 (number of x with phi(x) = m):")
    out("  ", [int(cnt[m]) for m in range(1, 41)])
    first = {}
    for m in range(1, M + 1):
        k = int(cnt[m])
        if k >= 2 and k not in first:
            first[k] = m
    oeis_A007374 = [1, 2, 4, 8, 12, 32, 36, 40, 24, 48, 160, 396, 2268, 704, 312, 72, 336, 216, 936, 144,
                    624, 1056, 1760, 360, 2560, 384, 288, 1320, 3696, 240]
    mine = [first.get(k) for k in range(2, 32)]
    out("A007374 recomputed (least m with exactly k solutions, k = 2..31):")
    out("  ", mine)
    out("  agrees with the OEIS data for k = 2..31:", mine == oeis_A007374)
    assert first[8] == 36

    def smooth3(m):
        while m % 2 == 0:
            m //= 2
        while m % 3 == 0:
            m //= 3
        return m == 1

    def exps(m):
        a = b = 0
        while m % 2 == 0:
            m //= 2
            a += 1
        while m % 3 == 0:
            m //= 3
            b += 1
        return a, b

    out("  k : least m : 3-smooth? : lattice point")
    for k in range(2, 32):
        m = first[k]
        out(f"  {k:>2d} : {m:>5d} : {'yes' if smooth3(m) else 'no ':<3} : {exps(m) if smooth3(m) else '-'}")
    out("  multiplicities below 36:", {m: int(cnt[m]) for m in range(1, 36) if cnt[m] > 0})
    out("  -> the values 2,3,4,5,6,7 are first reached at 1,2,4,8,12,32; 24 = 2^3*3 jumps to 10, so 8 is first reached at 36.")

    # --- how sparse are 3-smooth totient values, and how heavy are their fibres?
    tot_vals = int(np.count_nonzero(cnt[1: M + 1]))
    sm = [m for m in range(1, M + 1) if smooth3(m)]
    out(f"\n3-smooth m <= 10^6: {len(sm)}; of these totient values: {sum(1 for m in sm if cnt[m] > 0)};"
        f" all totient values <= 10^6: {tot_vals}")
    mean_all = float(cnt[1: M + 1][cnt[1: M + 1] > 0].mean())
    mean_sm = float(np.mean([cnt[m] for m in sm if cnt[m] > 0]))
    out(f"  mean fibre size over totient values <= 10^6: all {mean_all:.3f}, 3-smooth {mean_sm:.3f}")

    table = {"amax": AMAX, "bmax": BMAX,
             "A": [[int(A[a, b]) for b in range(BMAX + 1)] for a in range(AMAX + 1)],
             "D": [[int(D[a, b]) for b in range(BMAX + 1)] for a in range(AMAX + 1)],
             "pierpont_points": [list(p) for p in P]}
    with open(os.path.join(HERE, "q41_table.json"), "w", encoding="utf-8") as f:
        json.dump(table, f)
    out(f"\nwrote q41_table.json   ({time.time() - t0:.1f} s)")


if __name__ == "__main__":
    main()
    LOG.close()
