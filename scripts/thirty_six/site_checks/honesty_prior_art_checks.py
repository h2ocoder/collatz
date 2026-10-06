"""Reviewer checks (lens: honesty and prior art) for site/explore/thirty-six.md and folded-pentagon.md.

Each block tests one sentence of a page against a direct computation.  Read-only with respect to
the site; prints its results and writes nothing else.

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 honesty_prior_art_checks.py
"""
from __future__ import annotations

from fractions import Fraction
from math import comb, isqrt

import numpy as np


def tri(n: int) -> int:
    return n * (n + 1) // 2


def is_tri(m: int) -> bool:
    r = isqrt(8 * m + 1)
    return r * r == 8 * m + 1


# ---------------------------------------------------------------------------------------------
print("== 1. thirty-six.md: 'squares of 2..200,000 show 103 different dropping times under 3x-1'")
print("   The README counts Terras (shortcut) stopping times k; the site's dropping time is k + s.")
ks, kps, pairs = set(), set(), set()
for n in range(2, 200001):
    v = n * n
    x, k, s = v, 0, 0
    while True:
        if x & 1:
            x = (3 * x - 1) >> 1
            s += 1
        else:
            x >>= 1
        k += 1
        if x < v:
            break
    ks.add(k)
    kps.add(k + s)
    pairs.add((k, s))
print(f"   distinct shortcut times k: {len(ks)};  distinct un-shortcut times k+s: {len(kps)};  distinct (k,s): {len(pairs)}")

# ---------------------------------------------------------------------------------------------
print("== 2. thirty-six.md: 'the only triangular sum of cubes'")
hits = [(a, b, a ** 3 + b ** 3) for a in range(1, 40) for b in range(a + 1, 40) if is_tri(a ** 3 + b ** 3)]
print("   sums of two distinct cubes that are triangular (a, b < 40):", hits[:6])
first = [(n, tri(n) ** 2) for n in range(0, 2000) if is_tri(tri(n) ** 2)]
print("   sums of the FIRST n cubes that are triangular, n < 2000:", first)

# ---------------------------------------------------------------------------------------------
print("== 3. folded-pentagon.md lead: 'the rate at which the Collatz map forgets a starting residue modulo 5'")
A = np.zeros((5, 5))
for x in range(5):
    A[x, (3 * x) % 5] += 1          # e(x) = x/2 = 3x
    A[x, (3 - x) % 5] += 1          # o(x) = (3x+1)/2 = 3 - x
K = A / 2
for start in range(5):
    p = np.zeros(5)
    p[start] = 1
    tv = []
    for k in range(1, 61):
        p = p @ K
        tv.append(0.5 * np.abs(p - 0.2).sum())
    print(f"   start {start}: TV(k=60)/TV(k=59) = {tv[-1] / tv[-2]:.6f}   TV(60)/cos36^60 = {tv[-1] / np.cos(np.pi / 5) ** 60:.4f}")
print(f"   cos 36 deg = {np.cos(np.pi / 5):.6f}")

# ---------------------------------------------------------------------------------------------
print("== 4. thirty-six.md: '5 is the only modulus prime to 6 at which every eigenvalue ... is real'")
real_mods = []
for N in range(5, 200):
    if N % 2 == 0 or N % 3 == 0:
        continue
    inv2 = pow(2, -1, N)
    M = np.zeros((N, N))
    for x in range(N):
        M[x, (x * inv2) % N] += 1
        M[x, ((3 * x + 1) * inv2) % N] += 1
    ev = np.linalg.eigvals(M)
    if np.max(np.abs(ev.imag)) < 1e-6:
        real_mods.append(N)
print("   moduli N < 200 prime to 6 with all eigenvalues real (float test):", real_mods)
print("   but the golden eigenvalue is present at every multiple of 5 (level 5 is a summand):")
for N in (25, 35, 55):
    inv2 = pow(2, -1, N)
    M = np.zeros((N, N))
    for x in range(N):
        M[x, (x * inv2) % N] += 1
        M[x, ((3 * x + 1) * inv2) % N] += 1
    ev = np.linalg.eigvals(M) / 2
    print(f"   N = {N}: min |lambda + cos36| = {np.min(np.abs(ev + np.cos(np.pi / 5))):.2e}")

# ---------------------------------------------------------------------------------------------
print("== 5. thirty-six.md: 'fixed point of tau_k exactly when T_k is a product of two distinct primes' (README: k >= 2)")


def tau_k_of_prime_powers(k: int, exps) -> int:
    out = 1
    for e in exps:
        out *= comb(e + k - 1, e)
    return out


print("   k = 1: T_1^2 = 1, tau_1(1) =", tau_k_of_prime_powers(1, []), "-> fixed, though T_1 = 1 is not a product of two primes")

# ---------------------------------------------------------------------------------------------
print("== 6. thirty-six.md: 'N(10) = 476 ... whether the values are new is unknown'")
print("   A100982 (offset 1) data line on oeis.org: 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, ... -> a(10) = 476 is a listed term")
F85 = lambda j: Fraction(comb(8 * j, 3 * j), 8 * j)
print("   Bizley form F_2 - F_1^2/2 with F_j = C(8j,3j)/(8j):", F85(2) - F85(1) ** 2 / 2)
