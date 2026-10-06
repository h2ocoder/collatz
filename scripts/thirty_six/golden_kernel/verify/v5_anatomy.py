"""Skeptic check 5: exact anatomy at p = 37, 41, 31, 11, 13, 23 with sympy only (no gk_common), Proposition D by
exact interpolation, the 'node' at 37, the eigenvalue-0 anomaly at N = 275, and two numerology controls.

CONVENTION: shortcut map; A = 2K_N = R_e + R_o on functions on Z/N, (A f)(x) = f(x/2) + f((3x+1)/2); A^- = R_e - R_o.
Run:  python -X utf8 v5_anatomy.py
"""
from __future__ import annotations

import time
from fractions import Fraction
from pathlib import Path

import sympy as sp

T0 = time.time()
LOG: list[str] = []
FAIL: list[str] = []
x, th = sp.symbols("x theta")


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def check(name: str, cond: bool) -> None:
    say(f"   [{'ok' if cond else 'FAIL'}] {name}")
    if not cond:
        FAIL.append(name)


def perms(N: int):
    i2 = pow(2, -1, N)
    Re, Ro = sp.zeros(N, N), sp.zeros(N, N)
    for t in range(N):
        Re[t, t * i2 % N] = 1
        Ro[t, (3 * t + 1) * i2 % N] = 1
    return Re, Ro


def min_support(vecs: list[sp.Matrix]) -> int:
    """exact minimal support over a space of dimension 1 or 2 (pencil argument)."""
    if len(vecs) == 1:
        return sum(1 for t in vecs[0] if t != 0)
    w1, w2 = vecs
    n = len(w1)
    both0 = sum(1 for i in range(n) if w1[i] == 0 and w2[i] == 0)
    best = n - sum(1 for t in w2 if t == 0)                       # w2 itself
    ratios: dict = {}
    for i in range(n):
        if w2[i] != 0:
            ratios[-w1[i] / w2[i]] = ratios.get(-w1[i] / w2[i], 0) + 1
    for cnt in ratios.values():                                    # w1 + t w2
        best = min(best, n - cnt - both0)
    return best


# ------------------------------------------------------------------ p = 37
say("=== 1. p = 37 ===")
Re, Ro = perms(37)
A = Re + Ro
cp = sp.factor_list(A.charpoly(x).as_expr())[1]
say("   charpoly(2K_37) factors: " + ", ".join(f"({sp.Poly(f, x).degree()}: {f if sp.Poly(f, x).degree() <= 2 else 'deg ' + str(sp.Poly(f, x).degree())})^{m_}" for f, m_ in cp))
fd = {str(f): m_ for f, m_ in cp}
check("(x-2) x^2 (x^2+1) (x-1)^2 (x+1)^2 times one irreducible factor of degree 28",
      fd.get("x - 2") == 1 and fd.get("x") == 2 and fd.get("x**2 + 1") == 1 and fd.get("x - 1") == 2 and fd.get("x + 1") == 2
      and sorted(sp.Poly(f, x).degree() for f, _ in cp)[-1] == 28 and len(cp) == 6)
big = [f for f, _ in cp if sp.Poly(f, x).degree() == 28][0]
G = sp.Poly(big, x)
check("the degree-28 factor is G(x^2) with G = y^14 + y^13 + 2y^12 - 7y^11 - 6y^10 - 15y^9 + 11y^8 + 3y^7 + 18y^6 - 13y^5 - 33y^4 - 26y^3 - 11y^2 + 26y + 9",
      G.all_coeffs()[::2] == [1, 1, 2, -7, -6, -15, 11, 3, 18, -13, -33, -26, -11, 26, 9] and not any(G.all_coeffs()[1::2]))
roots = sorted((abs(complex(r)) / 2 for r in G.nroots(n=20)), reverse=True)
say(f"   largest |lambda| of K_37 below 1: {roots[0]:.6f}")
check("|lambda_2(K_37)| = 0.673523", abs(roots[0] - 0.673523) < 1e-6)
I37 = sp.eye(37)
for v in (1, -1):
    Rn = (A - v * I37).nullspace()
    Ln = (A.T - v * I37).nullspace()
    pair = sp.Matrix(2, 2, lambda i, j: (Ln[i].T * Rn[j])[0]) if len(Rn) == 2 else None
    say(f"   eigenvalue {v:+d}: dim {len(Rn)}; minimal support of an eigenfunction {min_support(Rn)}, of an eigenfunctional {min_support(Ln)}; det of left-right pairing {pair.det() if pair is not None else None}")
    check(f"eigenvalue {v:+d} of 2K_37 has geometric multiplicity 2 and is semisimple", len(Rn) == 2 and pair.det() != 0)
    # first-order splitting under R_e + (1+eps) R_o: eigenvalues of pair^-1 * (L^T R_o R)
    C = pair.inv() * sp.Matrix(2, 2, lambda i, j: (Ln[i].T * Ro * Rn[j])[0])
    pol = sp.Poly(sp.primitive(sp.together(C.charpoly(x).as_expr()).as_numer_denom()[0])[1], x)
    disc = sp.discriminant(pol.as_expr(), x)
    say(f"      compression of R_o to the eigenspace: charpoly {pol.as_expr()}, discriminant {disc} = {sp.factorint(disc)}")
check("support claims at 37: (+1) 24 and 26, (-1) 24 and 31",
      (min_support((A - I37).nullspace()), min_support((A.T - I37).nullspace()), min_support((A + I37).nullspace()), min_support((A.T + I37).nullspace())) == (24, 26, 24, 31))
say("   NOTE: 'P, dP/dx, dP/dtheta vanish at (1,1)' is automatic for ANY eigenvalue of geometric multiplicity 2 (the adjugate of a")
say("   corank-2 matrix is 0), and the branch slopes are the eigenvalues of the 2x2 compression above.  The 'node' adds nothing beyond")
say("   'multiplicity 2, compression of R_o irreducible over Q'.")

# ------------------------------------------------------------------ Proposition D at 37 by interpolation in theta
say("\n=== 2. Proposition D: support of det(x - R_e - theta R_o) on the relation lattice, exact interpolation ===")
for p in (5, 7, 11, 13, 37):
    Re_, Ro_ = perms(p)
    # coefficients of x^i are polynomials in theta of degree <= p: interpolate at theta = 0..p
    vals = []
    for tv in range(p + 1):
        vals.append([int(c) for c in (Re_ + tv * Ro_).charpoly(x).all_coeffs()[::-1]])      # ascending in x
    coef: dict[tuple[int, int], Fraction] = {}
    nodes = list(range(p + 1))
    # Lagrange basis polynomials (ascending coefficient lists in theta)
    basis = []
    for a_ in nodes:
        num = [Fraction(1)]
        den = Fraction(1)
        for b_ in nodes:
            if b_ != a_:
                num = [Fraction(0)] + num
                for i in range(len(num) - 1):
                    num[i] -= b_ * num[i + 1]
                den *= (a_ - b_)
        basis.append([c / den for c in num])
    for i in range(p + 1):
        pol = [Fraction(0)] * (p + 1)
        for a_ in nodes:
            v_ = vals[a_][i]
            if v_:
                for s in range(p + 1):
                    pol[s] += v_ * basis[a_][s]
        for s in range(p + 1):
            if pol[s] != 0:
                coef[(i, s)] = pol[s]
    # full determinant = (x - 1 - theta) * P_p.  Monomial x^i theta^s of the FULL determinant has total degree <= p;
    # lattice statement for P_p: x^(p-1-k) theta^s with p | 2^k - 3^s.  Divide by (x - 1 - theta) exactly.
    full = sum(c * x ** i * th ** s for (i, s), c in coef.items())
    quo, rem_ = sp.Poly(full, x, domain=sp.ZZ[th]).div(sp.Poly(x - 1 - th, x, domain=sp.ZZ[th]))
    assert rem_.is_zero, "x - 1 - theta must divide the determinant (constants)"
    Pp = sp.Poly(quo.as_expr(), x, th)
    off = [(p - 1 - i, s) for (i, s), c in Pp.terms() if (pow(2, p - 1 - i, p) - pow(3, s, p)) % p]
    cells = [(k, s) for k in range(p) for s in range(k + 1) if (pow(2, k, p) - pow(3, s, p)) % p == 0]
    present = {(p - 1 - i, s) for (i, s), c in Pp.terms()}
    say(f"   p = {p}: monomials of P_p: {len(Pp.terms())}; off the lattice: {off}; lattice cells with 0 <= s <= k <= p-1: {len(cells)}; missing: {sorted(set(cells) - present)}")
    check(f"p = {p}: P_p is supported on the lattice p | 2^k - 3^s", not off and all(c.denominator == 1 for c in coef.values()))
    if p == 5:
        check("P_5 = (x^2 - theta^2)^2 + theta x - 1", sp.expand(Pp.as_expr() - ((x ** 2 - th ** 2) ** 2 + th * x - 1)) == 0)

# ------------------------------------------------------------------ 41, 31, 11, 13, 23
say("\n=== 3. p = 41, 31, 11 (K) and 13, 23 (K^-) ===")
Re, Ro = perms(41)
A41 = Re + Ro
c41 = sp.Poly(A41.charpoly(x).as_expr(), x)
q, r = sp.div(c41, sp.Poly(x ** 5 + 3, x))
check("x^5 + 3 divides charpoly(2K_41) exactly", r.is_zero)
q2, r2 = sp.div(q, sp.Poly(x ** 5 + 3, x))
check("... with multiplicity exactly 1", not r2.is_zero)
say("   factor degrees of charpoly(2K_41): " + str(sorted((sp.Poly(f, x).degree(), m_) for f, m_ in sp.factor_list(c41.as_expr())[1])))
say(f"   |lambda| = 3^(1/5)/2 = {float(3 ** 0.2 / 2):.4f};  41 = 2^5 + 3^2, ord_41(2) = {sp.n_order(2, 41)}, ord_41(3) = {sp.n_order(3, 41)}")
Re, Ro = perms(31)
A31 = Re + Ro
R31, L31 = (A31 - sp.eye(31)).nullspace(), (A31.T - sp.eye(31)).nullspace()
check("p = 31: eigenvalue +1 of 2K is simple; supports 19 (function) and 29 (functional)", len(R31) == 1 and (min_support(R31), min_support(L31)) == (19, 29))
say("   factor degrees of charpoly(2K_31): " + str(sorted((sp.Poly(f, x).degree(), m_) for f, m_ in sp.factor_list(A31.charpoly(x).as_expr())[1])))
Re, Ro = perms(11)
f = sp.zeros(11, 1)
f[1], f[2] = 1, -1
check("p = 11: (2K)(delta_1 - delta_2) = -(delta_1 - delta_2)   [the trivial cycle {1, 2}]", (Re + Ro) * f == -f)
say("   charpoly(2K_11) = " + str(sp.factor(A.charpoly(x).as_expr()) if False else sp.factor((Re + Ro).charpoly(x).as_expr())))
Re, Ro = perms(13)
say("   charpoly(2K^-_13) = " + str(sp.factor((Re - Ro).charpoly(x).as_expr())))
Re, Ro = perms(23)
say("   charpoly(2K^-_23) = " + str(sp.factor((Re - Ro).charpoly(x).as_expr())))
check("p = 23: eigenvalue +1 of 2K^- has geometric multiplicity 2", len((Re - Ro - sp.eye(23)).nullspace()) == 2)

# ------------------------------------------------------------------ N = 275
say("\n=== 4. eigenvalue 0 at the non-squarefree level 275 = 5^2 * 11 ===")
import numpy as np  # noqa: E402

RR = 2 ** 31 - 1


def nullity_mod(M: "np.ndarray") -> int:
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


def A_np(N: int) -> "np.ndarray":
    i2 = pow(2, -1, N)
    M = np.zeros((N, N), dtype=np.int64)
    for t in range(N):
        M[t, t * i2 % N] += 1
        M[t, (3 * t + 1) * i2 % N] += 1
    return M


say("   (nullities modulo 2^31 - 1; the exact algebraic multiplicities per level are in v2_census.log)")
for N in (25, 49, 175, 245, 275, 325):
    M = A_np(N)
    M2 = (M @ M) % RR
    M3 = (M2 @ M) % RR
    say(f"   Z/{N}: dim ker A = {nullity_mod(M.copy())}, dim ker A^2 = {nullity_mod(M2)}, dim ker A^3 = {nullity_mod(M3)}")
say("   level 275 alone (census): algebraic multiplicity of 0 is 10 = number of even cycles of y -> 3y + 1/2: no doubling, although 275 is not squarefree.")

# ------------------------------------------------------------------ numerology controls
say("\n=== 5. control: how often does the characteristic-p shadow 'predict' +-1, and how often is it there? ===")
tot = shadow_p1 = shadow_m1 = 0
for p in sp.primerange(5, 3001):
    p = int(p)
    kap = {(pow(2, -n, p) * (1 + pow(3, n, p))) % p for n in range(1, p - 1)}       # n = p-1 gives 2 (constants' twin)
    tot += 1
    shadow_p1 += 1 in kap
    shadow_m1 += (p - 1) in kap
say(f"   primes 5 <= p <= 3000: {tot};  some degree n in [1, p-2] has kappa_n = +1 (mod p): {shadow_p1};  kappa_n = -1: {shadow_m1}")
say("   actual eigenvalue +1 of 2K_p beyond Theorem C in that range: p = 11, 31, 37 only;  -1: p = 11, 37 only  (v3_krylov_scan)")
say("   so a residue kappa_n = +-1 exists at about two primes in three and lifts at three primes: the 'dodecagon in characteristic 37'")
say("   locates residues, it is not a mechanism.")
small = []
for p in sp.primerange(5, 3001):
    p = int(p)
    k = sp.n_order(3 * pow(4, -1, p) % p, p)
    if k <= 12:
        eta = pow(2, k, p)
        r_ = sp.n_order(eta, p)
        ent = sorted({(pow(eta, j, p) + pow(eta, -j, p)) % p for j in range(1, r_)})
        small.append((p, k, r_, 1 in ent, (p - 1) in ent))
say(f"   primes <= 3000 with ord_p(3/4) = k <= 12, as (p, k, r = ord(2^k), +1 among the polygon residues, -1 among them): {small}")

say(f"\n{len(FAIL)} failures;  total time {time.time() - T0:.0f} s")
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
