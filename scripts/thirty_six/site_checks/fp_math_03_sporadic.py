"""Reviewer check 3 for site/explore/folded-pentagon.md: the section 'The other golden prime'.

Exact (sympy over Z, integer vectors).  Independent of the thread's code.

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 fp_math_03_sporadic.py
"""
from __future__ import annotations

import math
import sys

import sympy as sp
from sympy import n_order, primerange

FAIL = 0
x = sp.symbols("x")


def check(ok: bool, label: str) -> None:
    global FAIL
    if not ok:
        FAIL += 1
    print(f"   [{'ok' if ok else 'FAIL'}] {label}")
    sys.stdout.flush()


def branches(p: int, d: int = 2, q: int | None = None):
    q = d + 1 if q is None else q
    inv = pow(d, -1, p)
    return [v * inv % p for v in range(p)], [(q * v + 1) * inv % p for v in range(p)]


def charpoly(p: int, d: int = 2) -> sp.Poly:
    e, o = branches(p, d)
    A = sp.zeros(p, p)
    for v in range(p):
        A[v, e[v]] += 1
        A[v, o[v]] += 1
    return A.charpoly(x)


def mult(poly: sp.Poly, root: int) -> int:
    m = 0
    f = sp.Poly(x - root, x)
    while True:
        qo, r = sp.div(poly, f)
        if not r.is_zero:
            return m
        poly, m = qo, m + 1


def forced(p: int, d: int = 2):
    """Theorem C for the pair (d+1, d): (m, t, idx) with d^m = (d+1)^t, or None when ord(d+1) is odd."""
    q = (d + 1) % p
    oq = n_order(q, p)
    if oq % 2:
        return None
    powers = {pow(q, i, p): i for i in range(oq)}
    m = next(i for i in range(1, p) if pow(d, i, p) in powers)
    t = powers[pow(d, m, p)]
    return m, t, (p - 1) // (oq * m)


def forced_mult(p: int, d: int, c: int) -> int:
    f = forced(p, d)
    if f is None:
        return 0
    m, t, idx = f
    return idx if c**m == (-1) ** (m + t) else 0


# ---------------------------------------------------------------- 1. the listed primes, exactly
print("=== 1. exact characteristic polynomials of A_p = 2K_p at 5, 11, 31, 37, 41 (and 7, 13 as plain cases) ===")
CP = {}
for p in (5, 7, 11, 13, 31, 37, 41):
    CP[p] = charpoly(p)
    f = forced(p, 2)
    fac = sp.factor_list(CP[p].as_expr())[1]
    small = " * ".join(f"({sp.sstr(g)})^{k}" if k > 1 else f"({sp.sstr(g)})" for g, k in fac if sp.degree(g, x) <= 5)
    print(f"   p = {p:2d}: ord 3 = {n_order(3, p)}, Theorem C (m, t, idx) = {f}; factors of degree <= 5: {small}; other degrees: {[sp.degree(g, x) for g, k in fac if sp.degree(g, x) > 5]}")
    print(f"           multiplicity of +1 / -1: {mult(CP[p], 1)} / {mult(CP[p], -1)}   forced by Theorem C: {forced_mult(p, 2, 1)} / {forced_mult(p, 2, -1)}")
check(sp.expand(CP[5].as_expr() - x * (x - 1) * (x - 2) * (x**2 + x - 1)) == 0, "p = 5: x(x-1)(x-2)(x^2+x-1); the +1/2 at 5 is Theorem C's, the golden pair is the extra")
check((mult(CP[11], 1), mult(CP[11], -1)) == (1, 1) and forced(11) is None, "p = 11: +1/2 and -1/2 once each, none forced (ord_11(3) = 5 is odd)")
check((mult(CP[31], 1) - forced_mult(31, 2, 1), mult(CP[31], -1) - forced_mult(31, 2, -1)) == (1, 0), "p = 31: exactly one extra +1/2, no extra -1/2")
check((mult(CP[37], 1), mult(CP[37], -1)) == (2, 2) and forced_mult(37, 2, 1) == forced_mult(37, 2, -1) == 0, "p = 37: +1/2 twice and -1/2 twice, none forced (Theorem C gives +-i/2)")
check(sp.rem(CP[37], sp.Poly(x**2 + 1, x)).is_zero, "p = 37: x^2 + 1 divides (Theorem C's +-i/2)")
check(sp.rem(CP[41], sp.Poly(x**5 + 3, x)).is_zero, "p = 41: x^5 + 3 divides, i.e. five eigenvalues with (2 lambda)^5 = -3")
check(abs(3 ** 0.2 / 2 - 0.6229) < 5e-5, f"|lambda| at 41 is 3^(1/5)/2 = {3**0.2/2:.4f}, not 1/2: 'a stranger of another kind'")
check((mult(CP[41], 1) - forced_mult(41, 2, 1), mult(CP[41], -1) - forced_mult(41, 2, -1)) == (0, 0), "p = 41: no extra +-1/2")
check(all(mult(CP[p], c) == forced_mult(p, 2, c) for p in (7, 13) for c in (1, -1)), "p = 7, 13: no +-1/2 beyond Theorem C")

# ---------------------------------------------------------------- 2. Proposition F in the family (d+1, d)
print("=== 2. the two golden conditions, explicit eigenfunctions, every prime 5 <= p <= 400 and every d ===")


def apply_A(p, d, f):
    """(A f)(v) = f(e v) + f(o v)."""
    e, o = branches(p, d)
    return [f[e[v]] + f[o[v]] for v in range(p)]


n_f1 = n_f2 = 0
ok1 = ok2 = True
for p in primerange(5, 401):
    for d in range(2, p - 1):                 # d != 0, 1, -1
        f1 = [0] * p
        f1[p - 1], f1[0] = 1, -1             # delta_{-1} - delta_0
        is1 = apply_A(p, d, f1) == f1
        root1 = (d * d + d - 1) % p == 0
        ok1 &= is1 == root1
        n_f1 += root1
        den = (d * d - d - 1) % p
        root2 = (d * d + 3 * d + 1) % p == 0
        if den:
            x0 = pow(den, -1, p)
            x1 = d * x0 % p
            f2 = [0] * p
            f2[x1] += 1
            f2[x0] -= 1
            is2 = x0 != x1 and apply_A(p, d, f2) == [-v for v in f2]
            ok2 &= is2 == root2
        else:
            ok2 &= not root2
        n_f2 += root2
check(ok1, f"delta_-1 - delta_0 is an eigenfunction for +1 (K: +1/2) exactly when p | d^2 + d - 1 ({n_f1} roots)")
check(ok2, f"delta_x1 - delta_x0 on the 2-cycle is an eigenfunction for -1 (K: -1/2) exactly when p | d^2 + 3d + 1 ({n_f2} roots)")
check(sp.discriminant(x**2 + x - 1, x) == 5 and sp.discriminant(x**2 + 3 * x + 1, x) == 5, "both quadratics have discriminant 5")
check((2 * 2 + 2 - 1, 2 * 2 + 3 * 2 + 1) == (5, 11), "at d = 2 they are 5 and 11")
# Collatz at 5 and 11 in detail
e5, o5 = branches(5)
check([v for v in range(5) if e5[v] == v] == [0] and [v for v in range(5) if o5[v] == v] == [4], "p = 5: the eigenfunction sits on the fixed points 0 and -1")
e11, o11 = branches(11)
check(o11[1] == 2 and e11[2] == 1, "p = 11: 1 -> 2 -> 1 is the trivial cycle (odd step then even step)")
pre = lambda br, y: [v for v in range(11) if br[v] == y]
print(f"   p = 11: preimages of 2: e^-1 = {pre(e11, 2)}, o^-1 = {pre(o11, 2)};  preimages of 1: e^-1 = {pre(e11, 1)}, o^-1 = {pre(o11, 1)}")
check(pre(e11, 2) == [4] and pre(o11, 1) == [pow(3, -1, 11)] == [4], "p = 11: the two outside preimages, 4 (of 2) and 1/3 (of 1), coincide: 1/3 = 4 mod 11")
check([p for p in primerange(5, 2000) if (4 * 3 - 1) % p == 0] == [11], "4 = 1/3 mod p only for p = 11")
f2 = [0] * 11
f2[2], f2[1] = 1, -1
check(apply_A(11, 2, f2) == [-v for v in f2], "p = 11: delta_2 - delta_1 is an eigenfunction for -1")
# symmetry lambda -> -lambda at 11 (m = 2)
lvl11, rem11 = sp.div(CP[11], sp.Poly(x - 2, x))
print(f"   p = 11: level-11 polynomial = {sp.factor(lvl11.as_expr())}")
check(rem11.is_zero and all(mono[0] % 2 == 0 for mono in lvl11.monoms()),
      "p = 11: the level-11 characteristic polynomial is even (spectrum symmetric under lambda -> -lambda), so -1/2 gives +1/2")
H3 = {pow(3, i, 11) for i in range(n_order(3, 11))}
check(next(i for i in range(1, 11) if pow(2, i, 11) in H3) == 2, "p = 11: m = 2 (least m with 2^m in <3>)")
# golden ratio of the field
for p, want in ((5, "-phi"), (11, "-phi^2")):
    roots = [r for r in range(p) if (r * r - r - 1) % p == 0]
    desc = []
    for r in roots:
        for name, val in (("-phi", -r), ("-phi^2", -r * r), ("-1/phi", -pow(r, -1, p)), ("-1/phi^2", -pow(r * r, -1, p))):
            if val % p == 2:
                desc.append(f"phi = {r}: 2 = {name}")
    print(f"   F_{p}: roots of x^2 - x - 1 are {roots}; " + "; ".join(desc))
    check(any(s.endswith("2 = " + want) for s in desc), f"2 = {want} (mod {p}) for a root phi of x^2 - x - 1")

# ---------------------------------------------------------------- 3. base rate at 37
print("=== 3. base rate at p = 37: kernels (d+1, d), d = 2..35, with +-1/2 beyond Theorem C ===")
def nullity(p: int, d: int, c: int) -> int:
    """geometric multiplicity of the eigenvalue c of A, exactly over Q."""
    e, o = branches(p, d)
    A = sp.zeros(p, p)
    for v in range(p):
        A[v, e[v]] += 1
        A[v, o[v]] += 1
    return p - (A - c * sp.eye(p)).rank()


spor_alg, spor_geo = {}, {}
for d in range(2, 36):
    cp = charpoly(37, d)
    alg = {c: mult(cp, c) - forced_mult(37, d, c) for c in (1, -1)}
    geo = {c: (nullity(37, d, c) if mult(cp, c) else 0) - forced_mult(37, d, c) for c in (1, -1)}
    assert all(v >= 0 for v in geo.values()), (d, geo)
    if any(alg.values()):
        spor_alg[d] = {c: v for c, v in alg.items() if v}
    if any(geo.values()):
        spor_geo[d] = {c: v for c, v in geo.items() if v}
print(f"   geometric multiplicity above Theorem C (the thread's definition): {spor_geo}")
print(f"   algebraic multiplicity above Theorem C:                          {spor_alg}")
THREAD = {2: {1: 2, -1: 2}, 4: {1: 1}, 12: {-1: 1}, 17: {-1: 1}, 19: {-1: 2}, 22: {1: 1}, 24: {1: 1, -1: 1}, 28: {1: 1}, 34: {-1: 1}}
check(len(range(2, 36)) == 34 and spor_geo == THREAD, f"{len(spor_geo)} of 34 kernels at p = 37 carry a sporadic +-1/2 (extra eigenvectors), Collatz (d = 2) among them: the thread's list")
print(f"   NOTE by algebraic multiplicity the count is {len(spor_alg)} of 34; kernels that differ: "
      f"{ {d: (spor_alg.get(d), spor_geo.get(d)) for d in sorted(set(spor_alg) | set(spor_geo)) if spor_alg.get(d) != spor_geo.get(d)} } (Jordan blocks at +-1)")
check(not any((d * d + d - 1) % 37 == 0 or (d * d + 3 * d + 1) % 37 == 0 for d in range(37)), "neither golden condition has a root mod 37 (5 is not a square mod 37)")

print(f"\n{FAIL} failures")
