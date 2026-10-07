"""Skeptic check of X-a and X-b, and a PROOF OF COMPLETENESS for X-a.

Equation (E):  2^k = 1 + 3^s + 2^i 3^j,   k >= 1, s, i, j >= 0.

THEOREM.  (E) has exactly nine solutions (k,s,i,j):
   (2,0,1,0) (3,0,1,1) (3,1,2,0) (4,1,2,1) (4,2,1,1) (5,3,2,0) (6,2,1,3) (6,3,2,2) (8,5,2,1).

PROOF (each numbered step is checked below).
 1. i >= 1 (parity) and i < k.  3^s + 1 = 2^i (2^(k-i) - 3^j) with the bracket odd, so
    i = v_2(3^s + 1):  i = 1 if s is even, i = 2 if s is odd.
 2. s = 0:  2^(k-1) = 1 + 3^j, so (k-1, j) = (1,0), (2,1)   [Levi ben Gerson].
 3. s >= 1, j = 0:  s even gives 2^k = 3^s + 3, impossible; s odd gives 2^k - 3^s = 5.
 4. s >= 1, j >= 1:  2^k = 1 mod 3, so k = 2K and v_3(2^k - 1) = 1 + v_3(K)  [lifting the exponent].
      j > s:  v_3(2^k - 1) = s, so 3^s <= 3K and 0 < 2^(k-i) - 3^j = (1 + 3^s)/2^i <= (1 + 3k/2)/2.
      j < s:  v_3(2^k - 1) = j, so 3^j <= 3K and 0 < 2^k - 3^s = 1 + 2^i 3^j <= 1 + 6k.
      j = s:  2^k - 1 = 3^s (1 + 2^i); i = 1 gives 2^k - 3^(s+1) = 1, so s = 0 (excluded);
              i = 2 gives 4^K - 1 = 5 * 3^s with 3^(s-1) | K, only K = 2, s = 1.
 5. So in every remaining case 0 < 2^x - 3^y <= 6x + 13 with y >= 1 and x in {k, k-1, k-2}.
    Ellison (1971, Theorem 3): |2^x - 3^y| > 2^x e^(-x/10) for all positive integers x, y with
    x not in {1,...,11,13,14,16,19,27}.  For x >= 28 the right side exceeds 10^7 > 6x + 13.
    Hence x <= 27, k <= 29, and the exhaustive search below finishes the proof.          QED

The same statement is a special case of Alex & Foster, On the Diophantine equation
1 + x + y = z, Rocky Mountain J. Math. 22 (1992) 11-62 (all solutions with xyz = 2^r 3^s 5^t).

This script
  a. enumerates (E) by a different loop than the researcher's (over i, j, s; test power of 2),
  b. checks steps 1 and 4 on every solution and step 5 numerically (exact integers) for
     x <= 6000, independently of Ellison's theorem in that range,
  c. runs the mirror / cousin equations (numerology control),
  d. checks the cuban statement X-b, including cuban primes of the SECOND kind,
  e. shows that 37 = 2^6 - 3^3 and 37 = 4^3 - 3^3 are the same identity.

Run:  python -X utf8 v5_sunit.py
"""
from __future__ import annotations

import math
import os
import time

from sympy import isprime

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v5_sunit.log"), "w", encoding="utf-8")


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")


def smooth_exps(m, q):
    """(i, j) with m = 2^i q^j, or None."""
    if m <= 0:
        return None
    i = (m & -m).bit_length() - 1
    m >>= i
    j = 0
    while m % q == 0:
        m //= q
        j += 1
    return (i, j) if m == 1 else None


def solve(q, sign, kmax):
    """all (k,s,i,j,D) with sign*(2^k - q^s) = D = 2^i q^j + 1, 1 <= k <= kmax, q^s < 2^(kmax+1)."""
    sols = []
    smax = int((kmax + 1) * math.log(2) / math.log(q)) + 1
    pw = [q ** s for s in range(smax + 1)]
    for k in range(1, kmax + 1):
        p2 = 1 << k
        for s in range(smax + 1):
            D = sign * (p2 - pw[s])
            if D <= 1:
                continue
            e = smooth_exps(D - 1, q)
            if e is not None:
                sols.append((k, s, e[0], e[1], D))
    return sols


def main():
    t0 = time.time()
    # ------------------------------------------------------------------ a. enumeration, other loop order
    KMAX = 2000
    found = set()
    for i in (1, 2, 3, 4, 5, 6, 7, 8):          # the proof says only i = 1, 2 can occur; test more anyway
        for s in range(0, 1300):
            base = 1 + 3 ** s
            pj = 1
            for j in range(0, 1300):
                N = base + (pj << i)
                if N & (N - 1) == 0:
                    found.add((N.bit_length() - 1, s, i, j))
                pj *= 3
    out(f"a. solutions of 2^k = 1 + 3^s + 2^i 3^j with 1 <= i <= 8, s, j < 1300 (k up to ~{int(1300 * 1.585) + 8}):")
    for sol in sorted(found):
        k, s, i, j = sol
        D = 2 ** k - 3 ** s
        out(f"     k={k} s={s} i={i} j={j}   D = 2^k - 3^s = {D}   prime: {isprime(D)}   m = D - 1 = {D - 1}")
    assert sorted(found) == [(2, 0, 1, 0), (3, 0, 1, 1), (3, 1, 2, 0), (4, 1, 2, 1), (4, 2, 1, 1),
                             (5, 3, 2, 0), (6, 2, 1, 3), (6, 3, 2, 2), (8, 5, 2, 1)]
    full = solve(3, +1, KMAX)
    out(f"   full search over (k, s) with k <= {KMAX} (any i): {len(full)} solutions, same set:",
        sorted((k, s, i, j) for k, s, i, j, D in full) == sorted(found), f"  [{time.time() - t0:.0f} s]")
    assert sorted((k, s, i, j) for k, s, i, j, D in full) == sorted(found)

    # ------------------------------------------------------------------ b. the steps of the proof
    ok1 = all(i == (1 if s % 2 == 0 else 2) for k, s, i, j in found)
    out("b. step 1 (i = 1 for s even, 2 for s odd) on every solution:", ok1)
    assert ok1
    # v_2(3^s + 1) in {1, 2} and v_3(4^K - 1) = 1 + v_3(K)
    def v(n, p):
        c = 0
        while n % p == 0:
            n //= p
            c += 1
        return c
    assert all(v(3 ** s + 1, 2) == (1 if s % 2 == 0 else 2) for s in range(0, 400))
    assert all(v(4 ** K - 1, 3) == 1 + v(K, 3) for K in range(1, 400))
    out("   v_2(3^s + 1) = 1 (s even), 2 (s odd) for s < 400;  v_3(4^K - 1) = 1 + v_3(K) for K < 400: verified")
    # step 5 without Ellison, for x <= XMAX: all (x, y >= 1) with 0 < 2^x - 3^y <= 6x + 13
    XMAX = 6000
    small = []
    y, p3 = 0, 1
    for x in range(1, XMAX + 1):
        p2 = 1 << x
        while p3 * 3 < p2:
            p3 *= 3
            y += 1
        # p3 = largest power of 3 below 2^x  (y may be 0)
        if y >= 1 and 0 < p2 - p3 <= 6 * x + 13:
            small.append((x, y, p2 - p3))
    out(f"   step 5: all (x, y >= 1) with 0 < 2^x - 3^y <= 6x + 13, x <= {XMAX}: {small}")
    assert max(x for x, _, _ in small) <= 27
    worst = min(((1 << x) - 3 ** int(x * math.log(2) / math.log(3))) / (2 ** x * math.exp(-x / 10))
                for x in range(28, 400))
    out(f"   Ellison's bound holds with room on 28 <= x < 400: min (2^x - 3^y)/(2^x e^(-x/10)) = {worst:.3f}")
    out("   => with Ellison's Theorem 3 every solution has k <= 29; the list above is complete.")

    # ------------------------------------------------------------------ c. mirror and cousins
    out("\nc. MIRROR AND COUSINS (how many comparable coincidences are available?)")
    neg = solve(3, -1, 400)
    out(f"   3x-1 side, 3^s - 2^k = 2^i 3^j + 1, k <= 400: {len(neg)} solutions")
    for k, s, i, j, D in neg:
        out(f"     3^{s} - 2^{k} = {D} = 2^{i} 3^{j} + 1   prime: {isprime(D)}")
    for q in (5, 7):
        pos = solve(q, +1, 300)
        ng = solve(q, -1, 300)
        out(f"   q = {q}:  2^k - {q}^s = 2^i {q}^j + 1: {[(k, s, D) for k, s, i, j, D in pos]}")
        out(f"            {q}^s - 2^k = 2^i {q}^j + 1: {[(k, s, D) for k, s, i, j, D in ng]}")
    ms = sorted({D - 1 for k, s, i, j, D in full if s >= 1})
    out(f"   3-smooth m with m + 1 = 2^k - 3^s, s >= 1: {ms}  (m + 1 prime for {[m for m in ms if isprime(m + 1)]})")
    reps = {}
    for k, s, i, j, D in full:
        if s >= 1:
            reps.setdefault(D, []).append((k, s))
    out("   representations 2^k - 3^s of each denominator:", reps)
    out("   -> 5 and 13 are cycle denominators TWICE each, 7 and 37 once; 36 is one of five values of m")
    out("      and is singled out only by the superlative 'largest with m + 1 prime'.")

    # ------------------------------------------------------------------ d. cuban numbers
    out("\nd. CUBAN NUMBERS")
    first = [n for n in range(1, 10 ** 5) if smooth_exps(3 * n * (n + 1), 3) is not None]
    out("   first kind c_n = (n+1)^3 - n^3 = 3n(n+1) + 1 of Pierpont form, n < 10^5:",
        [(n, 3 * n * (n + 1) + 1, isprime(3 * n * (n + 1) + 1)) for n in first])
    out("   (n(n+1) is 3-smooth iff {n, n+1} = {2^a, 3^b}: Levi ben Gerson, so this list is complete: PROVED)")
    second = []
    for n in range(0, 10 ** 5):
        c = 3 * (n + 1) ** 2 + 1          # ((n+2)^3 - n^3)/2 = 3(n+1)^2 + 1
        if smooth_exps(c - 1, 3) is not None and isprime(c):
            second.append((n, c, smooth_exps(c - 1, 3)))
    out(f"   second kind ((n+2)^3 - n^3)/2 = 3(n+1)^2 + 1 that are Pierpont PRIMES, n < 10^5: {len(second)} of them:")
    out("     ", [(c, e) for n, c, e in second[:14]], "...")
    out("   -> 'the Pierpont cuban primes are exactly 7, 19, 37' is true only for cuban primes of the FIRST kind.")
    out("      13 = 2^2 3 + 1 (which divides no solution of phi(x) = 36) is a Pierpont cuban prime of the second kind.")

    # ------------------------------------------------------------------ e. one identity, not two
    out("\ne. X-a AND X-b ARE THE SAME IDENTITY")
    out("   (n+1)^3 - n^3 = 3 n (n+1) + 1.  For the consecutive 3-smooth pair (n, n+1) = (3, 4):")
    out(f"     4^3 - 3^3 = 2^6 - 3^3 = {4 ** 3 - 3 ** 3} = 3*3*4 + 1 = 2^2 3^2 + 1.")
    out("   so 'cycle denominator of cell (6,3)' and 'cuban prime' are one fact about the pair (3,4).")
    for (n, m) in ((1, 2), (2, 3), (3, 4), (8, 9)):
        for e in (2, 3):
            d = m ** e - n ** e
            out(f"     {m}^{e} - {n}^{e} = {d};  d - 1 = {d - 1} 3-smooth: {smooth_exps(d - 1, 3)}")
    out("   (squares: (n+1)^2 - n^2 = 2n + 1 gives 2^2 - 1 = 3, 2^4 - 3^2 = 7; cubes give 2^3 - 1 = 7, 2^6 - 3^3 = 37:")
    out("    four of the nine solutions come from powers of Gersonides pairs.)")
    out(f"\ndone in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
