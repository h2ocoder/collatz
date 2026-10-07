"""Q3.4  The prime 37 = 36 + 1 and the other sporadic primes: exact anatomy.

Conventions: gk_common.py.  A = 2K_p = R_e + R_o on functions on Z/p (e(x) = x/2, o(x) = (3x+1)/2);
signed kernel A^- = R_e - R_o;  theta-family A_theta = R_e + theta R_o.

Parts
  1. exact spectrum of K_37 (factorisation, symmetry, the theorem's eigenvalues, the extras).
  2. the two-variable characteristic polynomial P_p(x, theta) = det(x - R_e - theta R_o) / (x - 1 - theta) is
     supported on the relation lattice {(k, s) : p | 2^k - 3^s}  (monomial x^(p-1-k) theta^s)  -- checked exactly.
  3. classification of eigenvectors / eigenfunctionals of support <= 2 (brute force, all primes < 200, both signs).
  4. anatomy of every sporadic rational eigenvalue found (5, 11, 23^-, 31, 37, 41): exact eigenspaces, minimal
     supports, rational labels of small supports and the congruences that close them.
  5. the characteristic-p shadow: kappa_n = 2^-n (1 + 3^n) and the polygon that lives in characteristic p.
  6. (moved to q34c_family_base_rate.py)
  7. the double eigenvalue at 37 is one Q-rational node of the curve P_37(x, theta) = 0.

Run:  python -X utf8 q34_anatomy_37.py     (writes q34_anatomy_37.log / .json)
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction
from math import comb
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gk_common import (branches, charpoly_int, euler_phi, is_prime, multiplicity, order, pdivmod, primes_upto,  # noqa: E402
                       pstr, two_K)

T0 = time.time()
LOG: list[str] = []
RES: dict = {}
x, y, th = sp.symbols("x y theta")
BIG = (16777213, 16777199)
assert all(is_prime(b) for b in BIG)


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def rank_mod(M: np.ndarray, m: int) -> int:
    A = (M % m).astype(np.int64)
    n_rows, n_cols = A.shape
    r = 0
    for c in range(n_cols):
        piv = np.nonzero(A[r:, c])[0]
        if len(piv) == 0:
            continue
        i = r + int(piv[0])
        if i != r:
            A[[r, i]] = A[[i, r]]
        A[r] = (A[r] * pow(int(A[r, c]), -1, m)) % m
        col = A[:, c].copy()
        col[r] = 0
        nz = np.nonzero(col)[0]
        if len(nz):
            A[nz] = (A[nz] - np.outer(col[nz], A[r])) % m
        r += 1
        if r == n_rows:
            break
    return r


def corank(M: np.ndarray) -> int:
    """corank over Q (rank over F_r never exceeds the rank over Q; take the max over two 24-bit primes)."""
    return M.shape[0] - max(rank_mod(M, b) for b in BIG)


def prim_vec(v) -> list[int]:
    den = sp.ilcm(*[sp.Rational(c).q for c in v])
    w = [int(c * den) for c in v]
    g = sp.igcd(*w)
    return [c // g for c in w]


def rat_label(r: int, p: int, hmax: int = 9) -> str:
    """smallest-height rational a/b (b a power of 2 times a power of 3 preferred) congruent to r mod p."""
    best = None
    for b in (1, 2, 4, 8, 16, 3, 9, 6, 12, 5, 7):
        a = r * b % p
        if a > p // 2:
            a -= p
        h = max(abs(a), b)
        if h <= hmax and (best is None or h < best[0]):
            best = (h, a, b)
    if best is None:
        return str(r)
    return f"{best[1]}/{best[2]}" if best[2] != 1 else f"{best[1]}"


def min_support(vs: list[list[int]]) -> tuple[int, list[int], bool]:
    """minimal support of a non-zero vector in span(vs); exact for dim <= 2, greedy upper bound otherwise."""
    if len(vs) == 1:
        return sum(1 for c in vs[0] if c), vs[0], True
    if len(vs) == 2:
        v1, v2 = vs
        cands = [v1, v2]
        for i in range(len(v1)):
            if v1[i] or v2[i]:
                w = [v1[j] * v2[i] - v2[j] * v1[i] for j in range(len(v1))]
                if any(w):
                    cands.append(prim_vec(w))
        best = min(cands, key=lambda w: sum(1 for c in w if c))
        return sum(1 for c in best if c), best, True
    B = sp.Matrix(vs).T
    k = B.shape[1]
    best = None
    rng = np.random.default_rng(0)
    for _ in range(400):
        S = sorted(rng.choice(B.shape[0], size=k - 1, replace=False).tolist())
        ns = B.extract(S, list(range(k))).nullspace()
        if len(ns) != 1:
            continue
        w = prim_vec(B * ns[0])
        s = sum(1 for c in w if c)
        if s and (best is None or s < best[0]):
            best = (s, w)
    return best[0], best[1], False


# =============================================================================== 1. spectrum of K_37
say("=== 1. exact spectrum of K_37 ===")
p = 37
cp = charpoly_int(two_K(p))
prim37, r_ = pdivmod(cp, [-2, 1])
assert r_ == [0]
say(f"   ord_37(2) = {order(2, 37)} (2 is a primitive root), ord_37(3) = {order(3, 37)}, 3 = 2^26, 37 = 2^6 - 3^3, 2^2 3^2 = 36 = -1 (mod 37), ord(6) = {order(6, 37)}, ord(3/4) = {order(3 * pow(4, -1, 37) % 37, 37)}")
fl = sp.Poly(prim37[::-1], x).factor_list()[1]
say("   charpoly(2K_37) = (x - 2) * " + " * ".join(f"({f.as_expr()})^{e}" if e > 1 else f"({f.as_expr()})" for f, e in sorted(fl, key=lambda t: t[0].degree())))
g37 = prim37[0::2]
assert all(c == 0 for c in prim37[1::2])
say("   in y = x^2 (the spectrum is invariant under x -> -x because 2 has order m = 2 modulo <3>):")
say("   g_37(y) = " + str(sp.factor(sp.Poly(g37[::-1], y).as_expr())))
RES["g37"] = pstr(g37, "y")
ev = []
for f, e in fl:
    rts = np.roots([float(c) for c in f.all_coeffs()])
    name = str(f.as_expr()) if f.degree() <= 2 else f"generic degree-{f.degree()} factor"
    for z in rts:
        for _ in range(e):
            ev.append((complex(z) / 2, name))
ev.sort(key=lambda t: (-round(abs(t[0]), 9), round(np.angle(t[0]) % (2 * np.pi), 9)))
say("   eigenvalues of K_37 other than 1, by modulus then argument (lambda | modulus | arg/pi | factor):")
for z, name in ev:
    say(f"      {z.real:+.6f}{z.imag:+.6f}i | {abs(z):.6f} | {np.angle(z) / np.pi:+.4f} | {name}")
RES["K37_eigenvalues"] = [{"re": z.real, "im": z.imag, "abs": abs(z), "factor": name} for z, name in ev]
say(f"   second-largest modulus |lambda_2(K_37)| = {max(abs(z) for z, _ in ev):.6f}")
say("   on the circle |lambda| = 1/2:  +-i/2 (THEOREM: characters of order 4 have chi(3) = -1, chi(2) = +-i; lattice form: m = 2, 2^2 = 3^7, x^2 = (-1)^(2+7) = -1)")
say("                                  +1/2 twice and -1/2 twice (NOT predicted: sporadic)")
say("   eigenvalue 0 twice = number of characters with chi(3) = -1 = (p-1)/ord(3) = 2  (kernel of 1 + M_3 in the coordinate y = 4x + 1)")

# =============================================================================== 2. two-variable polynomial
say("\n=== 2. P_p(x, theta) = det(x - R_e - theta R_o) / (x - 1 - theta): support on the relation lattice ===")


def two_var_poly(p: int) -> dict[tuple[int, int], int]:
    """coefficients c[(i, s)] of x^i theta^s in P_p(x, theta), by exact interpolation in theta at 0..p-1."""
    e, o = branches(p)
    n = p - 1
    vals = []          # vals[theta] = coefficient list in x
    for t in range(n + 1):
        A = np.zeros((p, p), dtype=np.int64)
        for u in range(p):
            A[u, e[u]] += 1
            A[u, o[u]] += t
        full = charpoly_int(A, radius=1 + t)
        q_, rr = pdivmod(full, [-(1 + t), 1])
        assert rr == [0]
        vals.append(q_ + [0] * (n + 1 - len(q_)))
    out: dict[tuple[int, int], int] = {}
    # Newton forward differences at nodes 0..n, then expand binomial(theta, j) into monomials
    fall = [[Fraction(1)]]                      # falling factorial theta^(j) as coefficient list
    for j in range(1, n + 1):
        prev = fall[-1]
        nxt = [Fraction(0)] * (len(prev) + 1)
        for k, c in enumerate(prev):
            nxt[k + 1] += c
            nxt[k] -= (j - 1) * c
        fall.append(nxt)
    fact = [1]
    for j in range(1, n + 1):
        fact.append(fact[-1] * j)
    for i in range(n + 1):
        col = [vals[t][i] for t in range(n + 1)]
        diffs = []
        cur = col[:]
        for j in range(n + 1):
            diffs.append(cur[0])
            cur = [cur[k + 1] - cur[k] for k in range(len(cur) - 1)]
        mono = [Fraction(0)] * (n + 1)
        for j, dj in enumerate(diffs):
            if dj:
                for k, c in enumerate(fall[j]):
                    mono[k] += Fraction(dj, fact[j]) * c
        for s, c in enumerate(mono):
            if c:
                assert c.denominator == 1
                out[(i, s)] = int(c)
    return out


two_var = {}
for pp in (5, 7, 11, 13, 37):
    c2 = two_var_poly(pp)
    n = pp - 1
    off = [(n - i, s) for (i, s) in c2 if (pow(2, n - i, pp) - pow(3, s, pp)) % pp != 0 or s > n - i]
    lattice_cells = [(k, s) for k in range(n + 1) for s in range(k + 1) if (pow(2, k, pp) - pow(3, s, pp)) % pp == 0]
    used = sorted((n - i, s) for (i, s) in c2)
    say(f"   p = {pp}: {len(c2)} monomials; cells (k, s) off the lattice p | 2^k - 3^s: {off} (must be []); lattice cells in the triangle: {len(lattice_cells)}, with zero coefficient: {sorted(set(lattice_cells) - set(used))}")
    two_var[pp] = {f"{n - i},{s}": v for (i, s), v in sorted(c2.items(), key=lambda t: (n - t[0][0], t[0][1]))}
    if pp <= 11:
        expr = sum(v * x ** i * th ** s for (i, s), v in c2.items())
        say(f"      P_{pp}(x, theta) = {sp.Poly(expr, x).as_expr()}")
    if pp == 5:
        assert sp.expand(expr - ((x ** 2 - th ** 2) ** 2 + th * x - 1)) == 0
        say("      = (x^2 - theta^2)^2 + theta x - 1;   theta = 1: x (x-1)(x^2+x-1);   theta = -1: x (x+1)(x^2-x-1)")
    if pp == 37:
        say("      cells (k, s): coefficient of x^(36-k) theta^s:  " + ", ".join(f"({k_s}): {v}" for k_s, v in two_var[pp].items()))
        # value and gradient at (1,1) and at (-1,-1)
        expr = sum(v * x ** i * th ** s for (i, s), v in c2.items())
        for pt in ((1, 1), (-1, 1), (-1, -1), (sp.I, 1)):
            val = [sp.simplify(e_.subs({x: pt[0], th: pt[1]})) for e_ in (expr, sp.diff(expr, x), sp.diff(expr, th))]
            say(f"      at (x, theta) = {pt}:  P = {val[0]},  dP/dx = {val[1]},  dP/dtheta = {val[2]}")
        hess = [sp.diff(expr, x, 2), sp.diff(expr, x, th), sp.diff(expr, th, 2)]
        hv = [int(h.subs({x: 1, th: 1})) for h in hess]
        disc = hv[1] ** 2 - hv[0] * hv[2]
        say(f"      Hessian at (1,1): P_xx = {hv[0]}, P_x,theta = {hv[1]}, P_theta,theta = {hv[2]};  P_x,theta^2 - P_xx P_theta,theta = {disc} = {sp.factorint(disc)}"
            f"  ({'> 0: a node with two real branches' if disc > 0 else 'not a real node'}; sqrt = {sp.sqrt(disc)})")
        RES["node_37"] = {"hessian": hv, "disc": disc}
RES["two_variable_polynomials"] = two_var

# =============================================================================== 3. two-point classification
say("\n=== 3. eigenvectors / eigenfunctionals of support <= 2, all primes 5 <= p < 200, both signs (brute force) ===")
found = []
for p in [q for q in primes_upto(199) if q >= 5]:
    e, o = branches(p)
    for sign in (1, -1):
        for side in ("right", "left"):
            # column a of the operator applied to delta_a
            def image(a: int) -> dict[int, int]:
                out: dict[int, int] = {}
                if side == "left":            # push-forward: delta_a -> delta_{e a} + sign delta_{o a}
                    pts = ((e[a], 1), (o[a], sign))
                else:                         # (A delta_a)(x) = delta_a(e x) + sign delta_a(o x): support e^-1 a, o^-1 a
                    pts = ((2 * a % p, 1), ((2 * a - 1) * pow(3, -1, p) % p, sign))
                for pt, w in pts:
                    out[pt] = out.get(pt, 0) + w
                return {k: v for k, v in out.items() if v}
            imgs = [image(a) for a in range(p)]
            for a in range(p):
                ia = imgs[a]
                if set(ia) <= {a}:            # support 1
                    found.append((p, sign, side, (a,), (1,), Fraction(ia.get(a, 0))))
                for b in range(a + 1, p):
                    ib = imgs[b]
                    # find c with A(delta_a + c delta_b) = lam (delta_a + c delta_b)
                    outside = (set(ia) | set(ib)) - {a, b}
                    c = None
                    ok = True
                    for pt in outside:
                        va, vb = ia.get(pt, 0), ib.get(pt, 0)
                        if vb == 0:
                            ok = False
                            break
                        cc = Fraction(-va, vb)
                        if c is None:
                            c = cc
                        elif c != cc:
                            ok = False
                            break
                    if not ok:
                        continue
                    if c is None:
                        # span(delta_a, delta_b) is invariant: eigenvectors of the 2x2 block with both entries non-zero
                        M2 = sp.Matrix([[ia.get(a, 0), ib.get(a, 0)], [ia.get(b, 0), ib.get(b, 0)]])
                        for lam2, _, vecs in M2.eigenvects():
                            for vv in vecs:
                                if vv[0] != 0 and vv[1] != 0:
                                    found.append((p, sign, side, (a, b), (1, sp.nsimplify(vv[1] / vv[0])), sp.nsimplify(lam2)))
                        continue
                    if c == 0:
                        continue
                    ra = ia.get(a, 0) + c * ib.get(a, 0)
                    rb = ia.get(b, 0) + c * ib.get(b, 0)
                    lam = ra
                    if rb == lam * c:
                        found.append((p, sign, side, (a, b), (1, c), lam))
say("   (p, sign of the o-branch, side, support, coefficients, eigenvalue of R_e + sign R_o):")
by_kind: dict[str, list] = {}
for p, sign, side, supp, coef, lam in found:
    lab = tuple(rat_label(s, p) for s in supp)
    kind = f"sign {sign:+d} {side:>5} support {lab} coef {tuple(str(c) for c in coef)} eigenvalue {lam}"
    by_kind.setdefault(kind, []).append(p)
for kind, ps in sorted(by_kind.items(), key=lambda t: (-len(t[1]), t[0])):
    say(f"      {kind}:  " + (f"all {len(ps)} primes" if len(ps) == 44 else f"p in {ps}"))
RES["two_point"] = [{"p": p, "sign": sign, "side": side, "support": list(supp), "coef": [str(c) for c in coef], "eigenvalue": str(lam)} for p, sign, side, supp, coef, lam in found if len({pp for pp, s2, sd, *_ in found}) and p <= 41]

# =============================================================================== 4. anatomy of the sporadic eigenvalues
say("\n=== 4. anatomy of the sporadic rational eigenvalues ===")
sporadic = [  # (p, sign, m, c): (2K^sign)^m has the eigenvalue c, not explained by the theorem
    (5, 1, 1, None), (11, 1, 1, 1), (11, 1, 1, -1), (23, -1, 1, 1), (31, 1, 1, 1), (37, 1, 1, 1), (37, 1, 1, -1), (41, 1, 5, -3),
]
anat = []
for p, sign, m, c in sporadic:
    if c is None:
        continue
    A = sp.Matrix(two_K(p, sign=sign).tolist())
    M = A ** m - c * sp.eye(p)
    R = [prim_vec(v) for v in M.nullspace()]
    L = [prim_vec(v) for v in M.T.nullspace()]
    sr, vr, exr = min_support(R)
    sl, vl, exl = min_support(L)
    rec = {"p": p, "sign": sign, "m": m, "c": c, "dim": len(R), "min_support_right": sr, "min_support_left": sl,
           "exact_right": exr, "exact_left": exl}
    say(f"   p = {p}, kernel {'K' if sign == 1 else 'K^-'}: (2K)^{m} = {c} on a {len(R)}-dimensional space; minimal support of an eigenfunction: {sr}{'' if exr else ' (upper bound)'} of {p}; of an eigenfunctional: {sl}{'' if exl else ' (upper bound)'} of {p}")
    for nm, s_, v_ in (("eigenfunction", sr, vr), ("eigenfunctional", sl, vl)):
        if s_ <= 12:
            lab = {rat_label(i, p): v_[i] for i in range(p) if v_[i]}
            say(f"      sparsest {nm}: {lab}   (residues {[i for i in range(p) if v_[i]]})")
            rec[f"sparsest_{nm}"] = {str(k): v for k, v in lab.items()}
    anat.append(rec)
RES["anatomy"] = anat
# the two small closed configurations, as congruence conditions over Q
say("   p = 11, eigenfunction delta_1 - delta_2 of 2K with eigenvalue -1:  (2K delta_a)(x) is supported on {2a, (2a-1)/3};")
say("      2K(delta_1 - delta_2) = delta_2 + delta_{1/3} - delta_4 - delta_1,  equal to -(delta_1 - delta_2) iff 1/3 = 4, i.e. iff p | 11.")
say("   p = 11, eigen-measure mu = 3 d_{-1} + d_{-1/2} + 2 d_{-1/4} - 2 d_0 - 2 d_{1/4} - 2 d_{1/2} with eigenvalue +1: over Q the push-forward is")
say("      mu + 2 d_{-1/2} + 2 d_{-1/8} - 2 d_{7/8} - 2 d_{5/4};  the defect vanishes iff {-1/2, -1/8} = {7/8, 5/4}, i.e. iff p | 11.")
for Nn in range(5, 3000):
    if Nn % 2 and Nn % 3:
        i2, i4, i8 = pow(2, -1, Nn), pow(4, -1, Nn), pow(8, -1, Nn)
        if {(-i2) % Nn, (-i8) % Nn} == {7 * i8 % Nn, 5 * i4 % Nn}:
            say(f"      (the defect vanishes for N = {Nn})")

# =============================================================================== 5. characteristic-p shadow
say("\n=== 5. the characteristic-p shadow: charpoly(2K_p) = prod_n (x - kappa_n) mod p, kappa_n = 2^-n (1 + 3^n) ===")
for p, sign, m, c in sporadic:
    if c is None:
        continue
    kap = [(pow(2, -n, p) * (1 + sign * pow(3, n, p))) % p for n in range(p)]
    ns_ = [n for n in range(p) if pow(kap[n], m, p) == c % p]
    say(f"   p = {p} ({'K' if sign == 1 else 'K^-'}), c = {c}: degrees n with kappa_n^{m} = c (mod p): {ns_}   (upper bound for the multiplicity of the eigenvalue family)")
for p in (5, 7, 11, 13, 31, 37, 41, 73):
    k = order(3 * pow(4, -1, p) % p, p)
    r = order(pow(2, k, p), p)
    say(f"   p = {p}: ord(3/4) = {k}; on the degrees n = {k} j the two branches act (on leading coefficients) by 2^-n = eta^-j and (3/2)^n = eta^j, eta = 2^{k} of order r = {r}: "
        f"kappa_{{{k}j}} = eta^j + eta^-j = '2cos(2 pi j/{r})' in F_{p}")
say("   p = 37: r = 12, a dodecagon in characteristic 37 (37 = 2^6 - 3^3 makes 3/4 of order 3).  Its residues 2cos(2 pi j/12) mod 37, j = 0..12:")
eta = pow(2, 3, 37)
say("      " + ", ".join(str((pow(eta, j, 37) + pow(eta, -j, 37)) % 37) for j in range(13)) + "   (sqrt3 = +-15 mod 37)")
say("      characteristic 0 keeps 2, 1 (twice), 0 (twice), -1 (twice) of these; -2 and +-sqrt3 are NOT eigenvalues of 2K_37.")
say("   p = 7: r = 3 (triangle: 2, -1, -1 in F_7) but characteristic 0 has -1 only once: polygon residues do not lift in general.")

say("")
say("=== 6. base rate across the family (d+1, d): see q34c_family_base_rate.py ===")

# =============================================================================== 7. the node at 37
say("\n=== 7. the double eigenvalue at 37 ===")
p = 37
e, o = branches(p)
Re = sp.zeros(p, p)
Ro = sp.zeros(p, p)
for t in range(p):
    Re[t, e[t]] = 1
    Ro[t, o[t]] = 1
A = Re + Ro
for lam in (1, -1):
    R = sp.Matrix.hstack(*(A - lam * sp.eye(p)).nullspace())
    L = sp.Matrix.hstack(*(A.T - lam * sp.eye(p)).nullspace())
    G = L.T * R
    Co = G.inv() * (L.T * Ro * R)
    cpo_int = sp.Poly(Co.charpoly(x).as_expr(), x).clear_denoms()[1]
    dsc = int(cpo_int.discriminant())
    say(f"   eigenvalue {lam:+d} of 2K_37: eigenspace of dimension {R.shape[1]} (semisimple: det of the left-right pairing = {G.det()} != 0);")
    say(f"      first-order splitting under R_e + (1 + eps) R_o: slopes d(2 lambda)/d(eps) are the roots of {cpo_int.as_expr()} (discriminant {dsc} = {sp.factorint(dsc)})")
say("   so the two branches through (x, theta) = (1, 1) are conjugate over Q(sqrt(641)): one Q-rational node, not two independent rational coincidences.")

say(f"\ntotal time {time.time() - T0:.0f} s")
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
Path(__file__).with_suffix(".json").write_text(json.dumps(RES, indent=0, default=str), encoding="utf-8")
