"""Skeptic check 8: (a) exhaustive search for eigenvectors / eigenfunctionals of support <= 2 of R_e + eps R_o,
all primes 5 <= p < 300 (the researcher: p < 200), by exact coefficient bookkeeping (no linear algebra);
(b) irreducibility of the generic factor of g_N for small levels, certified by factor-degree patterns modulo
primes (a different algorithm from the factorisation over Z used by the researcher).

CONVENTION: e(x) = x/2, o(x) = (3x+1)/2 on Z/p;  (A_eps f)(x) = f(e x) + eps f(o x).
  right vector (function)  f = delta_a + c delta_b:   A delta_a = delta_{2a} + eps delta_{(2a-1)/3}
  left vector (functional) mu = delta_a + c delta_b:  delta_a A = delta_{a/2} + eps delta_{(3a+1)/2}
Run:  python -X utf8 v8_twopoint_irreducible.py
"""
from __future__ import annotations

import time
from fractions import Fraction
from pathlib import Path

import sympy as sp

T0 = time.time()
LOG: list[str] = []


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def name(v: int, p: int) -> str:
    """a small rational name for the residue v mod p, if there is one."""
    for den in (1, 2, 3, 4, 8):
        for num in sorted(range(-5, 6), key=abs):
            if (v * den - num) % p == 0:
                return str(Fraction(num, den))
    return str(v)


say("=== (a) support <= 2, primes 5 <= p < 300, eps = +1 (K) and -1 (K^-), both sides ===")
found: dict[tuple, list[int]] = {}
for p in sp.primerange(5, 300):
    p = int(p)
    i2, i3 = pow(2, -1, p), pow(3, -1, p)
    for eps in (1, -1):
        for side in ("right", "left"):
            if side == "right":
                img = [((2 * a) % p, ((2 * a - 1) * i3) % p) for a in range(p)]
            else:
                img = [((a * i2) % p, ((3 * a + 1) * i2) % p) for a in range(p)]
            # support 1
            for a in range(p):
                P1, P2 = img[a]
                tot: dict[int, int] = {}
                tot[P1] = tot.get(P1, 0) + 1
                tot[P2] = tot.get(P2, 0) + eps
                if all(v == 0 for pt, v in tot.items() if pt != a):
                    lam = tot.get(a, 0)
                    found.setdefault((eps, side, (name(a, p),), ("1",), lam), []).append(p)
            # support 2: delta_a + c delta_b, a < b
            for a in range(p):
                P1, P2 = img[a]
                for b in range(a + 1, p):
                    P3, P4 = img[b]
                    co: dict[int, list[int]] = {}           # point -> [constant, coefficient of c]
                    for pt, k0, k1 in ((P1, 1, 0), (P2, eps, 0), (P3, 0, 1), (P4, 0, eps)):
                        t = co.setdefault(pt, [0, 0])
                        t[0] += k0
                        t[1] += k1
                    c = None
                    ok = True
                    for pt, (k0, k1) in co.items():
                        if pt in (a, b):
                            continue
                        if k1 == 0:
                            if k0 != 0:
                                ok = False
                                break
                        else:
                            cc = Fraction(-k0, k1)
                            if c is None:
                                c = cc
                            elif c != cc:
                                ok = False
                                break
                    if not ok or c == 0:
                        continue
                    ka, kb = co.get(a, [0, 0]), co.get(b, [0, 0])
                    # (A f)(a) = lam, (A f)(b) = lam c
                    cands = [c] if c is not None else None
                    if cands is None:
                        # c free: (ka0 + ka1 c) c = kb0 + kb1 c   ->  quadratic in c with rational roots only
                        A2, B2, C2 = ka[1], ka[0] - kb[1], -kb[0]
                        cands = []
                        if A2 == 0:
                            if B2 != 0:
                                cands = [Fraction(-C2, B2)]
                        else:
                            disc = B2 * B2 - 4 * A2 * C2
                            if disc >= 0 and int(disc ** 0.5) ** 2 == disc:
                                r_ = int(disc ** 0.5)
                                cands = [Fraction(-B2 + r_, 2 * A2), Fraction(-B2 - r_, 2 * A2)]
                    for c_ in cands:
                        if c_ == 0:
                            continue
                        lam = ka[0] + ka[1] * c_
                        if kb[0] + kb[1] * c_ == lam * c_:
                            found.setdefault((eps, side, (name(a, p), name(b, p)), ("1", str(c_)), lam), []).append(p)
for key in sorted(found, key=lambda k: (-k[0], k[1], len(k[2]), -len(found[k]))):
    eps, side, sup, coef, lam = key
    ps = found[key]
    say(f"   eps = {eps:+d} {side:>5} support {sup} coefficients {coef} eigenvalue {lam}: p in {ps if len(ps) <= 8 else str(ps[:4])[:-1] + ', ..., ' + str(ps[-1]) + '] (' + str(len(ps)) + ' primes)'}")
kplus = sorted({(k[1], k[2], k[4], tuple(found[k])) for k in found if k[0] == 1})
say(f"   K (eps = +1) complete list: {kplus}")
say("   (rational names are chosen per prime, so one configuration can appear under several names at small p)")

say("\n=== (b) irreducibility of the generic factor of g_N by degree patterns modulo primes, levels N <= 79 ===")
x, y = sp.symbols("x y")


def Amat(N: int) -> sp.Matrix:
    i2 = pow(2, -1, N)
    M = sp.zeros(N, N)
    for t in range(N):
        M[t, t * i2 % N] += 1
        M[t, (3 * t + 1) * i2 % N] += 1
    return M


prim: dict[int, sp.Poly] = {1: sp.Poly(x - 2, x)}
res = []
for N in range(5, 80):
    if sp.gcd(N, 6) != 1:
        continue
    cp = sp.Poly(Amat(N).charpoly(x).as_expr(), x)
    for d in sp.divisors(N):
        if d < N:
            cp, rem = sp.div(cp, prim[d])
            assert rem.is_zero
    prim[N] = cp
    # strip x, and all linear factors of g in y = x^m (found as integer roots)
    o3 = sp.n_order(3, N)
    H = {pow(3, t, N) for t in range(o3)}
    m, z = 1, 2 % N
    while z not in H:
        z = z * 2 % N
        m += 1
    co = cp.all_coeffs()[::-1]
    r0 = cp.degree() % m
    assert all(c == 0 for i, c in enumerate(co) if (i - r0) % m)
    g = sp.Poly(co[r0::m][::-1], y)
    lin = 0
    for c0 in range(-40, 41):
        while g.degree() > 0 and g.eval(c0) == 0:
            g = sp.div(g, sp.Poly(y - c0, y))[0]
            lin += 1
    n = g.degree()
    if n <= 1:
        res.append((N, n, "trivial"))
        continue
    possible = set(range(n + 1))
    used = []
    for ell in sp.primerange(5, 400):
        ell = int(ell)
        if N % ell == 0:
            continue
        gl = sp.Poly(g.as_expr(), y, modulus=ell)
        if sp.gcd(gl, gl.diff()).degree() > 0:
            continue                                    # not squarefree modulo ell
        degs = [f.degree() for f, e_ in gl.factor_list()[1] for _ in range(e_)]
        sums = {0}
        for dg in degs:
            sums |= {s + dg for s in sums}
        possible &= sums
        used.append(ell)
        if possible == {0, n}:
            break
    res.append((N, n, "irreducible (certified)" if possible == {0, n} else f"NOT certified: possible factor degrees {sorted(possible)[:8]}"))
    say(f"   N = {N:>2}: m = {m}, linear factors of g removed: {lin}, generic degree {n}: {res[-1][2]} using primes {used[:6]}{'...' if len(used) > 6 else ''}")
bad = [r for r in res if not r[2].startswith(("irreducible", "trivial"))]
say(f"   levels checked: {len(res)};  not certified irreducible: {bad}")
say(f"\ntotal time {time.time() - T0:.0f} s")
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
