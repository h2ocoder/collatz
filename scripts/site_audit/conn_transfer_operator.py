"""Audit check for site/connections/hilbert-polya.md.

Builds the operator exactly as the page defines it:

    L[g](y) = sum_{f(x) = y} g(x) / |f'(x)|      on Z/MZ

    even branch x -> x/2      weight 2
    odd  branch x -> n x + 1  weight 1/n

and reports: non-zero eigenvalues, rank, lambda^n, asymmetry.

Two readings of "x/2 on Z/MZ" are tried:
  (A) preimage of y under halving is the single class 2y mod M        (weight 2)
  (B) forward map x -> x/2 taken on representatives 0..M-1 (so x/2 in 0..M/2-1)
"""
import sys
import numpy as np


def build(M, n, reading="A", w_even=2.0, w_odd=None, c=1):
    if w_odd is None:
        w_odd = 1.0 / n
    L = np.zeros((M, M))
    if reading == "A":
        # L[y, x] : mass / function value transported from x to y
        for y in range(M):
            x = (2 * y) % M
            L[y, x] += w_even
        for x in range(1, M, 2):
            y = (n * x + c) % M
            L[y, x] += w_odd
    else:
        for x in range(M):
            if x % 2 == 0:
                L[(x // 2) % M, x] += w_even
            else:
                L[(n * x + c) % M, x] += w_odd
    return L


def report(M, n, reading):
    L = build(M, n, reading)
    ev = np.linalg.eigvals(L)
    nz = [e for e in ev if abs(e) > 1e-6]
    nz.sort(key=lambda z: (-abs(z), np.angle(z)))
    rank = np.linalg.matrix_rank(L)
    asym = np.linalg.norm(L - L.T) / np.linalg.norm(L)
    print(f"M={M:4d} n={n:2d} reading {reading}: rank={rank:3d}  #nonzero eig={len(nz):3d}  "
          f"asym |L-L^T|/|L|={asym:.3f}")
    for e in nz[:12]:
        print(f"      {e.real:+.6f}{e.imag:+.6f}i  |.|={abs(e):.6f}  |.|^{n}={abs(e)**n:.6f}  "
              f"lam^{n}={(e**n).real:+.5f}{(e**n).imag:+.5f}i")
    if len(nz) > 12:
        print(f"      ... {len(nz) - 12} more")


if __name__ == "__main__":
    print("target radius n=3:", (4 / 3) ** (1 / 3), " n=5:", (4 / 5) ** (1 / 5), " n=7:", (4 / 7) ** (1 / 7))
    for reading in ("A", "B"):
        print("=" * 30, "reading", reading)
        for M in (6, 12, 24, 48, 96):
            report(M, 3, reading)
        for M in (10, 20, 30, 40, 24):
            report(M, 5, reading)
        for M in (14, 28, 42, 24):
            report(M, 7, reading)
