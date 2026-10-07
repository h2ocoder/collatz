"""Skeptic check 9: Jordan blocks of 2K_N at the eigenvalue 0 as a pairing of two families of alternating functions.

In the coordinate y = 4x + 1 the kernel is (A f)(y) = F(h(y)), F(u) = f(u) + f(3u), h(y) = (y+1)/2.  Hence
   ker A = V_0     = { f : f(3u) = -f(u) }                (alternating on the even cycles of u -> 3u, centre 0),
   im  A = R_h(V_0^perp),
   R_h F in V_0  <=>  F in V_half = { F : F(3u - 1) = -F(u) }   (the same for u -> 3u - 1, centre 1/2).
So  dim(ker A  intersect  im A) = dim ker A^2 - dim ker A = corank of the pairing  V_half x V_0 -> Q,  <F, f> = sum_u F(u) f(u).
This script checks that identity exactly (integer pairing matrix, rank by sympy) against the nullities of A and A^2.

Run:  python -X utf8 v9_zero_jordan.py
"""
from __future__ import annotations

from math import gcd
from pathlib import Path

import numpy as np
import sympy as sp

LOG: list[str] = []
RR = 2 ** 31 - 1


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def nullity_mod(M: np.ndarray) -> int:
    M = M % RR
    n = M.shape[0]
    rank = 0
    for c in range(n):
        nz = np.flatnonzero(M[rank:, c])
        if nz.size == 0:
            continue
        i = rank + int(nz[0])
        if i != rank:
            M[[rank, i]] = M[[i, rank]]
        M[rank] = (M[rank] * pow(int(M[rank, c]), -1, RR)) % RR
        rows = np.flatnonzero(M[:, c])
        rows = rows[rows != rank]
        if rows.size:
            fac = M[rows, c].copy()
            hi, lo = fac >> 16, fac & 0xFFFF
            M[rows] = (M[rows] - ((hi[:, None] * M[rank][None, :]) % RR << 16) - lo[:, None] * M[rank][None, :]) % RR
        rank += 1
        if rank == n:
            break
    return n - rank


def alternating_basis(N: int, step) -> list[dict[int, int]]:
    """one alternating function per even cycle of the permutation `step` of Z/N."""
    seen = set()
    out = []
    for s in range(N):
        if s in seen:
            continue
        cyc, u = [], s
        while u not in seen:
            seen.add(u)
            cyc.append(u)
            u = step(u)
        if len(cyc) % 2 == 0:
            out.append({pt: (-1) ** i for i, pt in enumerate(cyc)})
    return out


ok_all = True
for N in [n for n in range(5, 400) if gcd(n, 6) == 1 and (n in (5, 7, 17, 19, 35, 37, 41, 55, 61, 65, 73, 85, 91) or any(n % (q * q) == 0 for q in (5, 7, 11, 13, 17, 19)))]:
    i2 = pow(2, -1, N)
    V0 = alternating_basis(N, lambda u: 3 * u % N)
    Vh = alternating_basis(N, lambda u: (3 * u - 1) % N)
    if not V0:
        continue
    G = sp.Matrix(len(Vh), len(V0), lambda i, j: sum(v * V0[j].get(pt, 0) for pt, v in Vh[i].items()))
    corank = len(V0) - G.rank()
    # A in the coordinate y: (A f)(y) = f(h y) + f(3 h y)
    A = np.zeros((N, N), dtype=np.int64)
    for yv in range(N):
        hy = (yv + 1) * i2 % N
        A[yv, hy] += 1
        A[yv, 3 * hy % N] += 1
    k1 = nullity_mod(A.copy())
    k2 = nullity_mod((A @ A) % RR)
    good = (k1 == len(V0)) and (k2 - k1 == corank)
    ok_all &= good
    say(f"   N = {N:>3}: dim V_0 = dim ker A = {len(V0)} ({k1}), dim V_half = {len(Vh)}, corank of the pairing = {corank}, dim ker A^2 - dim ker A = {k2 - k1}  {'ok' if good else 'MISMATCH'}")
say(f"identity holds at every level tested: {ok_all}")

say("")
say("=== primes: the pairing is non-degenerate (THEOREM: for prime p it is, up to invertible diagonal factors, the matrix of Jacobi sums")
say("    J(chi, chi'), chi(3) = chi'(3) = -1, whose determinant is a non-zero multiple of the product of the Gaussian periods")
say("    sum_{h in <3>} zeta_p^(c h); these are sums of distinct members of the basis zeta, ..., zeta^(p-1) of Q(zeta_p), hence non-zero) ===")
def pairing_corank(N: int) -> tuple[int, int]:
    """(dim V_0, corank modulo 2^31 - 1 of the pairing V_half x V_0).  The corank over Q is at most this, so 0 is a proof."""
    V0 = alternating_basis(N, lambda u: 3 * u % N)
    if not V0:
        return 0, 0
    where = {}
    for j, f in enumerate(V0):
        for pt, sgn in f.items():
            where[pt] = (j, sgn)
    Vh = alternating_basis(N, lambda u: (3 * u - 1) % N)
    G = np.zeros((len(Vh), len(V0)), dtype=np.int64)
    for i, F in enumerate(Vh):
        for pt, sgn in F.items():
            if pt in where:
                j, s0 = where[pt]
                G[i, j] += sgn * s0
    if G.shape[0] != G.shape[1]:
        return len(V0), -1
    return len(V0), nullity_mod(G)


bad = []
cnt = 0
for q in sp.primerange(5, 3000):
    q = int(q)
    z, cork = pairing_corank(q)
    if z == 0:
        continue
    cnt += 1
    if cork != 0:
        bad.append(q)
say(f"   primes 5 <= p < 3000 with ord_p(3) even: {cnt};  degenerate pairing (Jordan block at 0) at: {bad}")

say("")
say("=== composite test of the period rule: at N = p^2 q the periods of <3> vanish iff p does not divide ord_q(3) ===")
rule_ok = True
for N, pp, qq in ((175, 5, 7), (325, 5, 13), (425, 5, 17), (275, 5, 11), (775, 5, 31), (1525, 5, 61), (245, 7, 5), (539, 7, 11), (1421, 7, 29), (2107, 7, 43)):
    z, corank = pairing_corank(N)
    oq = sp.n_order(3, qq)
    oN = sp.n_order(3, N)
    zN = int(sp.totient(N)) // oN if oN % 2 == 0 else 0
    blocks_pp = pairing_corank(pp * pp)[1]
    pred = blocks_pp + (zN if oq % pp else 0)     # level p^2 contributes its own block(s); level N contributes zN or 0
    rule_ok &= corank == pred
    say(f"   N = {N:>4} = {pp}^2 * {qq}: ord_{qq}(3) = {oq} ({'not ' if oq % pp else ''}divisible by {pp}); zeros at level N: {zN}; "
        f"Jordan blocks on Z/N: {corank}; predicted by the rule: {pred}  {'ok' if corank == pred else 'MISMATCH'}")
say(f"   rule holds on these ten levels: {rule_ok}")
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
