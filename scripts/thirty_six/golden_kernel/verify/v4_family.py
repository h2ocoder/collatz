"""Skeptic check 4: the family (d+1, d) on Z/p.  Proposition F (F1, F2), the base rate of sporadic +-1,
and a NEW exact symmetry found while checking: the eigenvalue -1 is shared by d and 1/d.

Independent code: explicit eigenvector checks for F1 / F2 (no rank computation), my own elimination modulo
r = 2^31 - 1 for the nullities, and the predicted multiplicity obtained by enumerating the characters of F_p^x
directly (chi_j(g^a) = exp(2 pi i j a/(p-1))) instead of the (m, t, idx) formula.

CONVENTION: e(x) = x/d, o(x) = ((d+1) x + 1)/d on Z/p;  A = R_e + R_o on functions, (A f)(x) = f(e x) + f(o x);
A^- = R_e - R_o.  d = 2 is the Terras (3x+1) kernel.  K = A/2.
Run:  python -X utf8 v4_family.py [P_MAX=151]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import sympy as sp

P_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 151
R = 2 ** 31 - 1
T0 = time.time()
LOG: list[str] = []
FAIL: list[str] = []


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def check(name: str, cond: bool) -> None:
    say(f"   [{'ok' if cond else 'FAIL'}] {name}")
    if not cond:
        FAIL.append(name)


def maps(p: int, d: int):
    di = pow(d, -1, p)
    xs = np.arange(p, dtype=np.int64)
    return (xs * di) % p, (((d + 1) * xs + 1) * di) % p


def matrix(p: int, d: int, sign: int = 1) -> np.ndarray:
    e, o = maps(p, d)
    A = np.zeros((p, p), dtype=np.int64)
    A[np.arange(p), e] += 1
    A[np.arange(p), o] += sign
    return A


def nullity(M: np.ndarray) -> int:
    """nullity modulo R (>= nullity over Q)."""
    M = M % R
    n = M.shape[0]
    rank = 0
    for c in range(n):
        nz = np.flatnonzero(M[rank:, c])
        if nz.size == 0:
            continue
        i = rank + int(nz[0])
        if i != rank:
            M[[rank, i]] = M[[i, rank]]
        M[rank] = (M[rank] * pow(int(M[rank, c]), -1, R)) % R
        rows = np.flatnonzero(M[:, c])
        rows = rows[rows != rank]
        if rows.size:
            fac = M[rows, c].copy()
            hi, lo = fac >> 16, fac & 0xFFFF                      # keep products below 2^63
            M[rows] = (M[rows] - ((hi[:, None] * M[rank][None, :]) % R << 16) - lo[:, None] * M[rank][None, :]) % R
        rank += 1
        if rank == n:
            break
    return n - rank


# ------------------------------------------------------------------ F1, F2 by explicit eigenvectors, wide range
say("=== 1. Proposition F by explicit eigenvectors, all primes 5 <= p <= 2000 ===")
n1 = n2 = 0
ok1 = ok2 = True
conv1 = conv2 = True
for p in sp.primerange(5, 2001):
    p = int(p)
    for d in range(2, p - 1):
        f1 = (d * d + d - 1) % p == 0
        f2 = (d * d + 3 * d + 1) % p == 0
        if not (f1 or f2 or p <= 61):
            continue
        e, o = maps(p, d)
        # F1: f = delta_{-1} - delta_0, A f = f ?
        f = np.zeros(p, dtype=np.int64)
        f[p - 1], f[0] = 1, -1
        is1 = np.array_equal(f[e] + f[o], f)
        if f1:
            n1 += 1
            ok1 &= is1
        elif is1:
            conv1 = False
        # F2: f = delta_{x1} - delta_{x0}, x0 = 1/(d^2 - d - 1), x1 = d x0, A f = -f ?
        den = (d * d - d - 1) % p
        if den:
            x0 = pow(den, -1, p)
            x1 = d * x0 % p
            f = np.zeros(p, dtype=np.int64)
            f[x1], f[x0] = 1, -1
            is2 = np.array_equal(f[e] + f[o], -f)
            if f2:
                n2 += 1
                ok2 &= is2
            elif is2 and d != 1:
                conv2 = False
        elif f2:
            ok2 = False
check(f"F1: delta_-1 - delta_0 is an eigenfunction with A-eigenvalue +1 at all {n1} roots of d^2+d-1 (p <= 2000)", ok1 and n1 > 0)
check(f"F2: delta_x1 - delta_x0 is an eigenfunction with A-eigenvalue -1 at all {n2} roots of d^2+3d+1 (p <= 2000)", ok2 and n2 > 0)
check("converse (all d, p <= 61): these two vectors are eigenvectors ONLY at roots of F1 resp. F2", conv1 and conv2)
say(f"   d = 2: F1(2) = {2 * 2 + 2 - 1}, F2(2) = {2 * 2 + 3 * 2 + 1};  the 2-cycle at p = 11: x0 = {pow((4 - 2 - 1) % 11, -1, 11)}, x1 = {2 * pow(1, -1, 11) % 11}")

# ------------------------------------------------------------------ base rate
say(f"\n=== 2. base rate of sporadic +-1 in the family, primes 5 <= p <= {P_MAX} ===")
tot = spor_tot = expl = 0
spor: dict[int, dict[int, dict[int, int]]] = {}
nul: dict[tuple[int, int, int], int] = {}
for p in sp.primerange(5, P_MAX + 1):
    p = int(p)
    g = int(sp.primitive_root(p))
    lg = {pow(g, a, p): a for a in range(p - 1)}
    I = np.eye(p, dtype=np.int64)
    spor[p] = {}
    for d in range(2, p - 1):
        tot += 1
        A = matrix(p, d)
        ld, lq = lg[d], lg[(d + 1) % p]
        for v in (1, -1):
            # predicted: characters chi_j with chi(q) = -1 and -chi(d) = v
            target = 0 if v == -1 else (p - 1) // 2
            pred = sum(1 for j in range(p - 1) if (j * lq - (p - 1) // 2) % (p - 1) == 0 and (j * ld - target) % (p - 1) == 0)
            nl = nullity(A - v * I)
            nul[(p, d, v)] = nl
            assert nl >= pred, (p, d, v, nl, pred)
            if nl > pred:
                spor[p].setdefault(d, {})[v] = nl - pred
    for d in spor[p]:
        spor_tot += 1
        if (d * d + d - 1) % p == 0 or (d * d + 3 * d + 1) % p == 0:
            expl += 1
say(f"   kernels: {tot};  with a sporadic +-1: {spor_tot};  roots of F1 or F2 among them: {expl};  not: {spor_tot - expl}")
say(f"   Collatz column d = 2: sporadic at {[(p, spor[p][2]) for p in spor if 2 in spor[p]]}")
say(f"   p = 37: sporadic d: { {d: v for d, v in sorted(spor[37].items())} }" if 37 in spor else "")
for lo, hi in ((5, 41), (43, 79), (83, 113), (127, 151)):
    ps = [p for p in spor if lo <= p <= hi]
    if ps:
        un = sum(1 for p in ps for d in spor[p] if (d * d + d - 1) % p and (d * d + 3 * d + 1) % p)
        say(f"   {lo:>3} <= p <= {hi:>3}: {len(ps)} primes, unexplained sporadic d per prime {un / len(ps):.2f} = {100 * un / sum(p - 3 for p in ps):.1f} % of the kernels")
frac_small = [(p, len(spor[p]), p - 3) for p in spor if p <= 47]
say(f"   (p, sporadic d, kernels) for p <= 47: {frac_small}")

# ------------------------------------------------------------------ NEW: d <-> 1/d
say("\n=== 3. NEW (skeptic): the eigenvalue -1 of A is shared by d and 1/d, with equal geometric multiplicity ===")
say("   proof: rho(1 + e + o) is singular iff rho(e^-1 (1 + e + o)) = rho(1 + e^-1 + e^-1 o) is; e^-1 and e^-1 o are affine maps with")
say("   multipliers d and d + 1 and distinct fixed points, so they are conjugate in AGL(1,p) to the pair (e', o') of the parameter 1/d.")
bad = [(p, d) for (p, d, v), nl in nul.items() if v == -1 and nul[(p, pow(d, -1, p), -1)] != nl]
check(f"nullity(A_d + 1) = nullity(A_(1/d) + 1) for all {tot} kernels, p <= {P_MAX}", not bad)
badp = [(p, d) for (p, d, v), nl in nul.items() if v == 1 and nul[(p, pow(d, -1, p), 1)] != nl]
say(f"   the eigenvalue +1 is NOT shared in general: {len(badp)} of {tot} kernels have nullity(A_d - 1) != nullity(A_(1/d) - 1), e.g. {badp[:6]}")
# +1 of A_d  <->  +1 of A^-_{1/d}  (multiply -1 + e + o by e^-1)
bad2 = []
for p in sp.primerange(5, min(P_MAX, 101) + 1):
    p = int(p)
    I = np.eye(p, dtype=np.int64)
    for d in range(2, p - 1):
        if nullity(matrix(p, pow(d, -1, p), -1) - I) != nul[(p, d, 1)]:
            bad2.append((p, d))
check(f"nullity(A_d - 1) = nullity(A^-_(1/d) - 1) for all kernels with p <= {min(P_MAX, 101)}  (same argument with -1 + e + o)", not bad2)
for p in (31, 37, 41, 43):
    if p in spor:
        orb = sorted({2, pow(2, -1, p), (-3) % p, pow(-3, -1, p), (-1 - pow(2, -1, p)) % p, pow((-1 - pow(2, -1, p)) % p, -1, p)})
        say(f"   p = {p}: orbit of d = 2 under d -> 1/d, d -> -1-d: {orb};  (d, nullity of A+1, nullity of A-1): {[(d, nul[(p, d, -1)], nul[(p, d, 1)]) for d in orb]}")
say("   reading: the pairs {d, 1/d} carry the same -1 by the symmetry above, so 'all six sporadic at 37' is three independent facts, not six.")
say("   For Collatz: -1/2 is an eigenvalue of K_p (Terras) iff it is one of the kernel (1/2) f(2x) + (1/2) f(3x+1) of the semigroup <2x, 3x+1>.")

say(f"\n{len(FAIL)} failures;  total time {time.time() - T0:.0f} s")
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
