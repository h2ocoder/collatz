"""Reviewer check 2 for site/explore/folded-pentagon.md: Theorem B, the census and the 5x+1 control.

Part 1 is exact (direct fixed-point counts).  Parts 2-5 are floating-point reproductions (numpy
eigenvalues, tolerances printed): they are an independent sanity check of computed claims that the
thread established exactly, not a replacement for them.

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 fp_math_02_theorem_b.py
"""
from __future__ import annotations

import math
import sys

import numpy as np
from sympy import divisors, factorint, isprime, mobius, n_order, primerange, totient

FAIL = 0


def check(ok: bool, label: str) -> None:
    global FAIL
    if not ok:
        FAIL += 1
    print(f"   [{'ok' if ok else 'FAIL'}] {label}")
    sys.stdout.flush()


PHI = (1 + math.sqrt(5)) / 2

# ---------------------------------------------------------------- 1. traces, exact, N <= 5000
print("=== 1. tr A_N = 2 and tr A_N^2 = 3 + gcd(5, N) by direct fixed-point count, every N <= 5000 prime to 6 ===")
bad1, bad2, n_mod, words_fix = [], [], 0, {}
for sign in (1, -1):
    for N in range(5, 5001):
        if math.gcd(N, 6) != 1:
            continue
        n_mod += sign == 1
        x = np.arange(N, dtype=np.int64)
        i2 = pow(2, -1, N)
        e = x * i2 % N
        o = (3 * x + sign) % N * i2 % N
        t1 = int((e == x).sum() + (o == x).sum())
        fx = {"ee": int((e[e] == x).sum()), "eo": int((o[e] == x).sum()), "oe": int((e[o] == x).sum()), "oo": int((o[o] == x).sum())}
        if t1 != 2:
            bad1.append((sign, N))
        if sum(fx.values()) != 3 + math.gcd(5, N) or fx["ee"] != 1 or fx["eo"] != 1 or fx["oe"] != 1 or fx["oo"] != math.gcd(5, N):
            bad2.append((sign, N))
        if sign == 1 and N in (5, 7, 25, 35):
            words_fix[N] = fx
print(f"   {n_mod} moduli; fixed points of the two-letter words at N = 5, 7, 25, 35: {words_fix}")
check(not bad1, "tr A_N = 2 (fixed points 0 and -1) for 3x+1 and for 3x-1")
check(not bad2, "three two-letter words have exactly one fixed point, 'oo' has gcd(5, N): tr A_N^2 = 3 + gcd(5, N), for 3x+1 and 3x-1")
# 'oo' is x -> (9x+5)/4
ok = all((9 * x + 5) * pow(4, -1, N) % N == ((3 * ((3 * x + 1) * pow(2, -1, N) % N) + 1) * pow(2, -1, N)) % N for N in (5, 7, 11, 35) for x in range(N))
check(ok, "odd then odd is x -> (9x+5)/4")
# level sums by Moebius inversion
S2 = {N: sum(mobius(N // d) * (3 + math.gcd(5, d) if d > 1 else 4) for d in divisors(N)) for N in range(5, 5001) if math.gcd(N, 6) == 1}
check(S2[5] == 4 and all(v == 0 for N, v in S2.items() if N != 5), "level sums of squares: 4 at level 5, 0 at every other level 5 < N <= 5000")
check(abs(1 + 0 + PHI**-2 + PHI**2 - 4) < 1e-12, "at level 5: 1 + 0 + 1/phi^2 + phi^2 = 4")


# ---------------------------------------------------------------- level matrices in the Fourier basis
def level_eigs(N: int, q: int = 3) -> np.ndarray:
    """eigenvalues of A = R_e + R_o on the additive characters of exact order N (map x/2, (qx+1)/2)."""
    units = [s for s in range(1, N) if math.gcd(s, N) == 1]
    idx = {s: i for i, s in enumerate(units)}
    i2 = pow(2, -1, N)
    M = np.zeros((len(units), len(units)), dtype=complex)
    for s in units:
        M[idx[s * i2 % N], idx[s]] += 1.0
        M[idx[q * s * i2 % N], idx[s]] += np.exp(2j * np.pi * (s * i2 % N) / N)
    return np.linalg.eigvals(M)


def full_eigs(N: int, q: int = 3) -> np.ndarray:
    i2 = pow(2, -1, N)
    A = np.zeros((N, N))
    for x in range(N):
        A[x, x * i2 % N] += 1
        A[x, (q * x + 1) * i2 % N] += 1
    return np.linalg.eigvals(A)


def multiset_close(a: np.ndarray, b: np.ndarray, tol: float) -> bool:
    a, b = list(a), list(b)
    if len(a) != len(b):
        return False
    for v in a:
        j = min(range(len(b)), key=lambda t: abs(b[t] - v))
        if abs(b[j] - v) > tol:
            return False
        b.pop(j)
    return True


print("=== 2. the level decomposition used here agrees with the full matrix (float) ===")
for N in (5, 25, 35, 55, 77):
    lv = np.concatenate([level_eigs(d) if d > 1 else np.array([2.0 + 0j]) for d in divisors(N)])
    check(multiset_close(lv, full_eigs(N).astype(complex), 2e-4), f"N = {N}: eigenvalues of A_N = union of the levels d | N")
ev5 = np.sort(level_eigs(5).real)
print(f"   level 5, eigenvalues of K: {np.round(ev5 / 2, 6)}")
check(np.allclose(ev5 / 2, sorted([0.5, 0.0, math.cos(math.radians(72)), -math.cos(math.radians(36))]), atol=1e-9) and np.abs(level_eigs(5).imag).max() < 1e-9,
      "level 5: eigenvalues of K are 1/2, 0, cos 72, -cos 36, all real")

# ---------------------------------------------------------------- 3. Theorem B + census numerically, N <= 400
print("=== 3. every level 5 <= N <= 400 prime to 6 (float, tolerance 1e-6 on eigenvalues of A) ===")
TOL = 1e-6
J_MAX = 16000        # every j with phi(j)/2 <= 1300 is below this (phi(j) >= sqrt(j/2))... checked below
J_ALL = np.arange(1, J_MAX + 1)
DEG_J = np.array([1 if j <= 2 else int(totient(j)) // 2 for j in J_ALL])
FIRST_J = 2 * np.cos(2 * np.pi / J_ALL)
CONJ = {}


def conjugates(j: int) -> np.ndarray:
    if j not in CONJ:
        CONJ[j] = np.array(sorted({round(2 * math.cos(2 * math.pi * i / j), 13) for i in range(1, j + 1) if math.gcd(i, j) == 1}))
    return CONJ[j]


def nearest(sorted_real: np.ndarray, values: np.ndarray) -> np.ndarray:
    """distance from each value to the nearest entry of sorted_real."""
    if len(sorted_real) == 0:
        return np.full(len(values), 9.0)
    pos = np.clip(np.searchsorted(sorted_real, values), 1, len(sorted_real) - 1) if len(sorted_real) > 1 else np.zeros(len(values), dtype=int)
    lo = np.abs(values - sorted_real[np.maximum(pos - 1, 0)])
    hi = np.abs(values - sorted_real[pos])
    return np.minimum(lo, hi)


def cosine_orders(ev: np.ndarray, dim: int) -> list[int]:
    """orders j such that EVERY conjugate of 2cos(2 pi/j) is within TOL of a (numerically real) eigenvalue.
    This is necessary for Psi_j to divide the characteristic polynomial; all j with deg Psi_j <= dim are tried."""
    real = np.sort(ev[np.abs(ev.imag) < 1e-5].real)
    cand = J_ALL[(DEG_J <= dim) & (nearest(real, FIRST_J) < TOL)]
    return [int(j) for j in cand if (nearest(real, conjugates(int(j))) < TOL).all()]


# every j whose Psi_j could fit (degree <= 1300, i.e. phi(j) <= 2600) is below J_MAX, by the Rosser-Schoenfeld bound
# phi(j) > j / (e^gamma lnln j + 3/lnln j), whose right side is increasing for j >= 16000
_ll = math.log(math.log(J_MAX))
_rs = J_MAX / (math.exp(0.5772156649015329) * _ll + 3 / _ll)
check(_rs > 2600, f"J_MAX = {J_MAX} covers every j with deg Psi_j <= 1300: phi(j) > {_rs:.0f} for j >= {J_MAX}")


levels = [N for N in range(5, 401) if math.gcd(N, 6) == 1]
check(len(levels) == 132 and sum(isprime(N) for N in levels) == 76, f"{len(levels)} moduli prime to 6 from 5 to 400, of which 76 primes")
tally, all_real, sums_bad, irrational, zero_spec, no_cos = {}, [], [], {}, [], 0
for N in levels:
    ev = level_eigs(N)
    s1, s2 = ev.sum(), (ev**2).sum()
    want2 = 4 if N == 5 else 0
    if abs(s1) > 1e-6 or abs(s2 - want2) > 1e-5:
        sums_bad.append(N)
    if np.abs(ev.imag).max() < 1e-4:
        all_real.append(N)
    if np.abs(ev).max() < 1e-3:
        zero_spec.append(N)
    js = cosine_orders(ev, len(ev))
    no_cos += not js
    for j in js:
        tally[j] = tally.get(j, 0) + 1
        if j not in (1, 2, 3, 4, 6):
            irrational.setdefault(N, []).append(j)
print(f"   cosine orders j -> number of levels: {dict(sorted(tally.items()))}   (thread: j=4: 102, j=6: 68, j=3: 65, j=5: 1)")
check(not sums_bad, "sum of eigenvalues = 0 at every level; sum of squares = 0 at every level but 5 (= 4 there)")
check(all_real == [5], f"levels whose eigenvalues are all real: {all_real}")
check(not zero_spec, "no level has all eigenvalues zero")
check(irrational == {5: [5]}, f"irrational cosines (orders j other than 1, 2, 3, 4, 6): {irrational}")
check(set(tally) <= {3, 4, 5, 6}, "the only cosines at levels > 1 are 0 (j=4), +1/2 (j=6), -1/2 (j=3) and the golden pair (j=5)")
check((tally.get(4), tally.get(6), tally.get(3), tally.get(5)) == (102, 68, 65, 1), "level counts 102 / 68 / 65 / 1 as in the thread's census table")
print(f"   levels with no cosine eigenvalue: {no_cos}  (thread: 29)")
for N in (25, 125, 55, 35):
    ev = level_eigs(N)
    d = min(np.abs(ev + PHI).min(), np.abs(ev - 1 / PHI).min())
    check(d > 1e-3, f"level {N}: no golden eigenvalue (nearest eigenvalue of A to -phi or 1/phi is {d:.4f} away)")

# ---------------------------------------------------------------- 4. primes up to P_MAX numerically
P_MAX = 1300
print(f"=== 4. every prime 5 <= p <= {P_MAX} (float): irrational cosines, and eigenvalues of modulus exactly 1/2 ===")
irr_p, unit_excess, golden_at = {}, {}, {}
for p in primerange(5, P_MAX + 1):
    ev = full_eigs(p).astype(complex)
    ev = np.delete(ev, np.argmin(np.abs(ev - 2)))          # drop level 1
    js = [j for j in cosine_orders(ev, p - 1) if j not in (1, 2, 3, 4, 6)]
    if js:
        irr_p[p] = js
    if p in (11, 13, 29, 89, 199):
        golden_at[p] = float(min(np.abs(ev + PHI).min(), np.abs(ev - 1 / PHI).min()))
    # eigenvalues of A of modulus 1 (K: modulus 1/2), against the number Theorem C forces
    on_circle = int((np.abs(np.abs(ev) - 1) < 1e-6).sum())
    o3 = n_order(3, p)
    if o3 % 2 == 0:
        H3 = {pow(3, i, p) for i in range(o3)}
        m = next(i for i in range(1, p) if pow(2, i, p) in H3)
        size_H = o3 * m                      # |<2,3>| = ord(3) * m
        forced = (p - 1) // size_H * m       # idx * m roots of x^m = +-1, each with multiplicity idx
    else:
        forced = 0
    if on_circle != forced:
        unit_excess[p] = on_circle - forced
print(f"   irrational cosines at prime levels: {irr_p}")
check(irr_p == {5: [5]}, f"the golden pair at 5 is the only irrational cosine at a prime level up to {P_MAX}")
print(f"   distance from the golden pair to the spectrum of A_p at the Fibonacci/Lucas primes: { {p: round(v, 4) for p, v in golden_at.items()} }")
check(all(v > 1e-3 for v in golden_at.values()), "no golden eigenvalue at 11, 13, 29, 89, 199")
print(f"   primes where the number of eigenvalues with |lambda| = 1/2 differs from Theorem C's count: {unit_excess}")
check(unit_excess == {11: 2, 31: 1, 37: 4}, f"eigenvalues of modulus exactly 1/2 beyond Theorem C: only at 11 (+-1/2), 31 (one), 37 (four), p <= {P_MAX}; "
      "this float test would also see eigenvalues on the circle that are NOT half a root of unity, and finds none")

# ---------------------------------------------------------------- 5. the 5x+1 control
print("=== 5. control 5x+1, levels 3 <= N <= 200 prime to 10 (float) ===")
lev5 = [N for N in range(3, 201) if math.gcd(N, 10) == 1]
real5, irr5, tally5 = [], {}, {}
for N in lev5:
    ev = level_eigs(N, q=5)
    if np.abs(ev.imag).max() < 1e-4:
        real5.append(N)
    for j in cosine_orders(ev, len(ev)):
        tally5[j] = tally5.get(j, 0) + 1
        if j not in (1, 2, 3, 4, 6):
            irr5.setdefault(N, []).append(j)
print(f"   {len(lev5)} levels; cosine orders j -> levels: {dict(sorted(tally5.items()))}; level 3 eigenvalues of A: {np.round(level_eigs(3, q=5), 6)}")
check(irr5 == {}, f"5x+1: no irrational cosine at any level up to 200 ({irr5})")
check(real5 == [3], f"5x+1: the only all-real level up to 200 is {real5}")

print(f"\n{FAIL} failures")
