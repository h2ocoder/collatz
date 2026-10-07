"""Side question (beyond the seed list): when is a Collatz cycle denominator a Pierpont prime?

37 = 2^2 3^2 + 1 is the Pierpont prime at the lattice point (2,2), and also 37 = 2^6 - 3^3 is
the denominator of the cycle equation in the Collatz cell (k,s) = (6,3).  How often do the two
lattices meet like this?  Solve

        2^k - 3^s = 2^i 3^j + 1        (k >= 1, s >= 0, i >= 0, j >= 0)

i.e. the four-term S-unit equation 1 + 3^s + 2^i 3^j = 2^k over S = {2, 3}.  Such equations
have finitely many non-degenerate solutions (Evertse; van der Poorten-Schlickewei); this
script searches k <= KMAX exhaustively.  The search bound is a computation, not a proof of
completeness.

Also: the cuban numbers (n+1)^3 - n^3 = 3n(n+1) + 1 = 6 T_n + 1 that are Pierpont numbers.

Run:  python -X utf8 x_pierpont_cycle_cells.py      (about 1 minute)
"""
from __future__ import annotations

import os
import sys
import time

import sympy

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "x_pierpont_cycle_cells.log"), "w", encoding="utf-8")


def out(*args):
    s = " ".join(str(a) for a in args)
    print(s, flush=True)
    LOG.write(s + "\n")


def smooth_exponents(m):
    """(i, j) if m = 2^i 3^j, else None."""
    if m <= 0:
        return None
    i = (m & -m).bit_length() - 1
    m >>= i
    j = 0
    while m % 3 == 0:
        m //= 3
        j += 1
    return (i, j) if m == 1 else None


def main():
    t0 = time.time()
    KMAX = 1500
    sols = []
    for k in range(1, KMAX + 1):
        p2 = 1 << k
        p3 = 1
        while p3 < p2:
            # quick filter: 2^k - 3^s - 1 must be 3-smooth; if s >= 1 and it is divisible by 3
            # then 2^k = 1 mod 3; cheap tests first
            m = p2 - p3 - 1
            if m > 0:
                e = smooth_exponents(m)
                if e is not None:
                    s = 0
                    q = p3
                    while q > 1:
                        q //= 3
                        s += 1
                    sols.append((k, s, e[0], e[1], p2 - p3))
            p3 *= 3
    out(f"all solutions of 2^k - 3^s = 2^i 3^j + 1 with k <= {KMAX}   [{time.time() - t0:.0f} s]")
    out("    k   s   i   j   D = 2^k - 3^s   prime?   remark")
    for k, s, i, j, D in sols:
        rem = ""
        if s == 0:
            rem = "s = 0: D = 2^k - 1, no tripling (not a Collatz cell)"
        elif D == 37:
            rem = "<-- 37 = 36 + 1: cell (6,3), Pierpont point (2,2)"
        out(f"  {k:>3d} {s:>3d} {i:>3d} {j:>3d}   {D:>10d}      {'yes' if sympy.isprime(D) else 'no '}     {rem}")
    with_trip = [x for x in sols if x[1] >= 1]
    out(f"  solutions with s >= 1: {len(with_trip)};  largest D among them: {max(x[4] for x in with_trip)}"
        f"  at (k,s) = {max(with_trip, key=lambda x: x[4])[:2]}")
    out(f"  largest k occurring: {max(x[0] for x in sols)}  (search went to k = {KMAX})")

    out("\ncuban numbers c_n = (n+1)^3 - n^3 = 3 n (n+1) + 1 = 6 T_n + 1 that are of Pierpont form 2^i 3^j + 1:")
    out("  c_n - 1 = 3 n (n+1) is 3-smooth iff n and n+1 are both 3-smooth iff n in {1, 2, 3, 8}")
    out("  (consecutive 3-smooth numbers: Levi ben Gerson 1343; checked here for n < 10^6).")
    hits = [n for n in range(1, 10 ** 6) if smooth_exponents(3 * n * (n + 1)) is not None]
    out("  n with 3n(n+1) 3-smooth, n < 10^6:", hits)
    for n in hits:
        c = 3 * n * (n + 1) + 1
        out(f"    n = {n}: 6 T_n = {c - 1} = 2^{smooth_exponents(c - 1)[0]} 3^{smooth_exponents(c - 1)[1]},  c_n = {c}"
            f" = {sympy.factorint(c)}   {'PRIME' if sympy.isprime(c) else 'composite'}")
    out("  so the cuban primes that are Pierpont primes are exactly 7, 19, 37 -- and")
    out("  A(2,2) = 1 + 2 [7 prime] + 3 [19 prime] + 2 [37 prime] = 8  (see q41_fibre_count.log).")
    out("  7 + 19 + 37 = 4^3 - 1 = 63 and 1 + 7 + 19 + 37 = 64 (telescoping); 36 = T_3^2 = 6 T_3 because T_3 = 6.")
    out(f"\ndone in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
