"""Skeptic check of Q4.1-a/b/c/d.  Independent code path: NO generating-function DP from the
researcher, NO shared helpers.

  1. Pierpont points by sympy.isprime (BPSW; the researcher used Lucas certificates).
  2. A(a,b) by explicit enumeration of triples (alpha, beta, S) with dict polynomials.
  3. A(a,b) by an inverse-totient algorithm that knows nothing about Pierpont primes
     (recursion over all primes p with (p-1) | m), for every 3-smooth m = 2^a 3^b, a,b <= 22.
  4. A014197(m) for every m <= 6000 by the same inverse-totient algorithm (no sieve), and
     A007374 from it; 36 against its neighbours.
  5. corollaries (row b = 0, column a = 1, column a = 2) and edge cases.

Run:  python -X utf8 v1_fibre_count.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from functools import lru_cache

from sympy import divisors, isprime

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
LOG = open(os.path.join(HERE, "v1_fibre_count.log"), "w", encoding="utf-8")


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")


def invphi_count(m: int) -> int:
    """#{x >= 1 : phi(x) = m}, by recursion over the primes p with (p-1) | m."""
    if m < 1:
        return 0
    P = sorted((d + 1 for d in divisors(m) if isprime(d + 1)), reverse=True)

    @lru_cache(maxsize=None)
    def cnt(mm: int, idx: int) -> int:
        tot = 1 if mm == 1 else 0
        for t in range(idx, len(P)):
            p = P[t]
            if mm % (p - 1):
                continue
            q = mm // (p - 1)
            while True:
                tot += cnt(q, t + 1)
                if q % p:
                    break
                q //= p
        return tot

    return cnt(m, 0)


def invphi_list(m: int):
    P = sorted((d + 1 for d in divisors(m) if isprime(d + 1)), reverse=True)
    res = []

    def rec(mm, idx, x):
        if mm == 1:
            res.append(x)
        for t in range(idx, len(P)):
            p = P[t]
            if mm % (p - 1):
                continue
            q = mm // (p - 1)
            y = x * p
            while True:
                rec(q, t + 1, y)
                if q % p:
                    break
                q //= p
                y *= p

    rec(m, 0, 1)
    return sorted(res)


def main():
    t0 = time.time()
    AM = BM = 40
    with open(os.path.join(PARENT, "q41_table.json"), encoding="utf-8") as f:
        theirs = json.load(f)

    # 1. Pierpont points, independent primality test
    mine_pts = sorted((i, j) for i in range(1, AM + 1) for j in range(0, BM + 1)
                      if (i, j) != (1, 0) and isprime((1 << i) * 3 ** j + 1))
    their_pts = sorted(tuple(p) for p in theirs["pierpont_points"])
    out(f"1. Pierpont points i,j <= 40: mine (sympy BPSW) {len(mine_pts)}, theirs {len(their_pts)}, equal: {mine_pts == their_pts}")
    assert mine_pts == their_pts

    # 2. explicit enumeration with dict polynomials (subset polynomial, then alpha and beta by hand)
    D = {(0, 0): 1}
    for (i, j) in mine_pts:
        add = {}
        for (c, d), v in D.items():
            c2, d2 = c + i, d + j
            if c2 <= AM and d2 <= BM:
                add[(c2, d2)] = add.get((c2, d2), 0) + v
        for key, v in add.items():
            D[key] = D.get(key, 0) + v
    A = {}
    for (c, d), v in D.items():
        for alpha in range(0, AM + 2):
            u2 = (alpha - 1, 0) if alpha >= 1 else (0, 0)
            for beta in range(0, BM + 2):
                u3 = (1, beta - 1) if beta >= 1 else (0, 0)
                a, b = c + u2[0] + u3[0], d + u2[1] + u3[1]
                if a <= AM and b <= BM:
                    A[(a, b)] = A.get((a, b), 0) + v
    badA = sum(1 for a in range(AM + 1) for b in range(BM + 1) if A.get((a, b), 0) != theirs["A"][a][b])
    badD = sum(1 for a in range(AM + 1) for b in range(BM + 1) if D.get((a, b), 0) != theirs["D"][a][b])
    out(f"2. explicit (alpha, beta, S) enumeration vs q41_table.json on 0<=a,b<=40: mismatches A {badA}, D {badD}")
    assert badA == 0 and badD == 0
    out("   A(2,2) =", A[(2, 2)], "  A(0,0) =", A[(0, 0)], "  A(0,b>0) all zero:",
        all(A.get((0, b), 0) == 0 for b in range(1, BM + 1)))

    # 3. inverse totient, knows nothing about Pierpont primes
    R = 22
    bad = 0
    for a in range(0, R + 1):
        for b in range(0, R + 1):
            m = (1 << a) * 3 ** b
            c = invphi_count(m)
            if c != A.get((a, b), 0):
                bad += 1
                out("   MISMATCH", a, b, c, A.get((a, b), 0))
    out(f"3. inverse-totient count vs formula for all {(R + 1) ** 2} lattice points a,b <= {R} "
        f"(m up to 2^{R} 3^{R} = {(1 << R) * 3 ** R:.3e}): mismatches {bad}   [{time.time() - t0:.0f} s]")
    assert bad == 0
    fib = invphi_list(36)
    out("   phi^-1(36) by inverse totient:", fib)
    assert fib == [37, 57, 63, 74, 76, 108, 114, 126]
    # every member of a 3-smooth fibre has the claimed shape (checked on a,b <= 6)
    def shape_ok(x):
        while x % 2 == 0:
            x //= 2
        while x % 3 == 0:
            x //= 3
        p = 5
        while x > 1:
            if x % p == 0:
                x //= p
                if x % p == 0:
                    return False
                q = p - 1
                while q % 2 == 0:
                    q //= 2
                while q % 3 == 0:
                    q //= 3
                if q != 1:
                    return False
            else:
                p += 2
        return True
    okshape = all(shape_ok(x) for a in range(7) for b in range(7) for x in invphi_list((1 << a) * 3 ** b))
    out("   every x with phi(x) = 2^a 3^b (a,b <= 6) is 2^alpha 3^beta * distinct Pierpont primes > 3:", okshape)
    assert okshape

    # 4. A014197 for all m <= 6000 and A007374
    MM = 6000
    cnt = [0] * (MM + 1)
    for m in range(1, MM + 1):
        cnt[m] = invphi_count(m) if (m == 1 or m % 2 == 0) else 0
    out("4. A014197(1..40) =", cnt[1:41])
    first = {}
    for m in range(1, MM + 1):
        if cnt[m] >= 2 and cnt[m] not in first:
            first[cnt[m]] = m
    mine = [first.get(k) for k in range(2, 32)]
    out("   least m <= 6000 with exactly k solutions, k = 2..31:", mine)
    out("   (this is only an upper bound for A007374(k) unless the least m is <= 6000; all 30 found)")
    out("   m < 36 with exactly 8 solutions:", [m for m in range(1, 36) if cnt[m] == 8], "; A014197(36) =", cnt[36])
    assert cnt[36] == 8 and all(cnt[m] != 8 for m in range(1, 36))
    out("   neighbours (numerology control): A014197 at 24, 30, 32, 35, 36, 37, 40, 48, 64, 72 =",
        [cnt[m] for m in (24, 30, 32, 35, 36, 37, 40, 48, 64, 72)])
    out("   other m <= 6000 with exactly 8 solutions:", [m for m in range(1, MM + 1) if cnt[m] == 8][:25])
    out("   lattice points a,b <= 40 with A(a,b) = 8:", sorted(k for k, v in A.items() if v == 8))
    # which k have a 3-smooth champion
    def smooth(m):
        while m % 2 == 0:
            m //= 2
        while m % 3 == 0:
            m //= 3
        return m == 1
    out("   k (2..31) whose least m is 3-smooth:", [k for k in range(2, 32) if smooth(first[k])])

    # 5. corollaries and their edge cases
    row0 = [A[(a, 0)] for a in range(41)]
    out("5. row b = 0:", row0)
    assert row0 == [a + 2 for a in range(32)] + [32] * 9
    col1_ok = all(A[(1, b)] == 2 + 2 * isprime(2 * 3 ** b + 1) for b in range(1, 41)) and A[(1, 0)] == 3
    out("   column a = 1: A(1,b) = 2 + 2[2*3^b+1 prime] for 1 <= b <= 40 and A(1,0) = 3:", col1_ok)
    assert col1_ok
    S = {b for b in range(1, 41) if isprime(2 * 3 ** b + 1)}
    bad2 = 0
    for b in range(1, 41):
        f = (1 + 2 * sum(1 for d in range(1, b) if d in S) + 3 * (b in S) + 2 * isprime(4 * 3 ** b + 1)
             + 2 * sum(1 for d1 in S for d2 in S if d1 < d2 and d1 + d2 == b))
        bad2 += f != A[(2, b)]
    out("   column a = 2 closed form, 1 <= b <= 40: mismatches", bad2, "; at b = 0 the formula gives",
        1 + 3 * 0 + 2 * isprime(5), "but A(2,0) =", A[(2, 0)], "(formula is for b >= 1 only, as stated)")
    assert bad2 == 0
    out("   diagonal A(a,a), a = 0..15:", [A[(a, a)] for a in range(16)])
    out("   row b = 1, A(a,1), a = 0..15:", [A.get((a, 1), 0) for a in range(16)])
    out("   column a = 2, A(2,b), b = 0..15:", [A[(2, b)] for b in range(16)])
    out("   column a = 1, A(1,b), b = 0..20:", [A[(1, b)] for b in range(21)])
    out(f"done in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
