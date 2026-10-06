"""Q3.1  WHY cos 36 degrees?  The Terras kernel mod 5 as a folded pentagon walk.  All checks exact.

Conventions: see gk_common.py.  Shortcut map; branches on Z/5:  e(x) = x/2 = 3x,  o(x) = (3x+1)/2 = 3 - x.
A = 2K_5 = R_e + R_o acts on functions, (A f)(x) = f(e x) + f(o x); A^T pushes measures forward.

Run:  python -X utf8 q31_pentagon.py     (writes q31_pentagon.log and q31_pentagon.json)
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gk_common import branches, charpoly_int, pstr, two_K  # noqa: E402

LOG: list[str] = []
RES: dict = {}


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def check(name: str, cond: bool) -> None:
    RES.setdefault("checks", {})[name] = bool(cond)
    say(f"   [{'ok' if cond else 'FAIL'}] {name}")


N = 5
e, o = branches(N)
A = sp.Matrix(two_K(N).tolist())
x = sp.symbols("x")
phi = (1 + sp.sqrt(5)) / 2

say("=== 1. the two branches on Z/5 ===")
say(f"   e = x/2      : {e}   (x -> 3x)")
say(f"   o = (3x+1)/2 : {o}   (x -> 3 - x)")
check("e(x) = 3x mod 5 (order 4, fixes 0)", e == [3 * t % 5 for t in range(5)])
check("o(x) = 3 - x mod 5 (a reflection of the additive pentagon, fixes -1 = 4)", o == [(3 - t) % 5 for t in range(5)])
check("e sends additive pentagon edges {i,i+1} to pentagram edges {i,i+2}",
      all((e[(i + 1) % 5] - e[i]) % 5 in (2, 3) for i in range(5)))
check("e sends pentagram edges {i,i+2} to pentagon edges", all((e[(i + 2) % 5] - e[i]) % 5 in (1, 4) for i in range(5)))
check("o preserves pentagon edges", all((o[(i + 1) % 5] - o[i]) % 5 in (1, 4) for i in range(5)))
# group generated
gens = [tuple(e), tuple(o)]
G = {tuple(range(5))}
frontier = list(G)
while frontier:
    nxt = []
    for g in frontier:
        for h in gens:
            c = tuple(h[g[i]] for i in range(5))
            if c not in G:
                G.add(c)
                nxt.append(c)
    frontier = nxt
check("<e, o> = AGL(1,5), order 20", len(G) == 20 and all((g[1] - g[0]) % 5 != 0 and all((g[i] - g[0]) % 5 == (g[1] - g[0]) * i % 5 for i in range(5)) for g in G))
e2 = tuple(e[e[i]] for i in range(5))
D5 = {tuple(range(5))}
frontier = list(D5)
while frontier:
    nxt = []
    for g in frontier:
        for h in (e2, tuple(o)):
            c = tuple(h[g[i]] for i in range(5))
            if c not in D5:
                D5.add(c)
                nxt.append(c)
    frontier = nxt
check("<e^2, o> = D_5 (order 10): e^2 = (x -> -x) and o are two mirrors of the additive pentagon", len(D5) == 10)

say("\n=== 2. spectrum and eigenvectors of A = 2K_5 (exact) ===")
cp = charpoly_int(two_K(5))
say("   charpoly(2K_5) = " + pstr(cp) + " = " + str(sp.factor(sp.Poly(cp[::-1], x).as_expr())))
check("charpoly(2K_5) = x (x-1) (x-2) (x^2+x-1)", sp.expand(sp.Poly(cp[::-1], x).as_expr() - x * (x - 1) * (x - 2) * (x ** 2 + x - 1)) == 0)
say("   eigenvalues of K_5: 1, 1/2, 0, (sqrt5-1)/4 = cos 72 = 1/(2 phi), -(sqrt5+1)/4 = -cos 36 = -phi/2")
check("cos(72 deg) = 1/(2 phi) and cos(36 deg) = phi/2 (sympy exact)",
      sp.simplify(sp.cos(2 * sp.pi / 5) - 1 / (2 * phi)) == 0 and sp.simplify(sp.cos(sp.pi / 5) - phi / 2) == 0)
right = {
    "2": sp.Matrix([1, 1, 1, 1, 1]),
    "1": sp.Matrix([-1, 0, 0, 0, 1]),              # delta_{-1} - delta_0
    "0": sp.Matrix([1, 0, 1, -1, -1]),             # delta_0 + delta_2 - delta_3 - delta_4
}
left = {
    "2": sp.Matrix([[1, 1, 1, 1, 1]]),
    "1": sp.Matrix([[-2, 2, 1, 0, -1]]),
    "0": sp.Matrix([[1, -1, 0, -1, 1]]),
}
for lam, v in right.items():
    check(f"right eigenvector for 2K-eigenvalue {lam}: {list(v)}", A * v == int(lam) * v)
for lam, v in left.items():
    check(f"left eigenvector (measure) for 2K-eigenvalue {lam}: {list(v)}", v * A == int(lam) * v)
# golden right eigenvector (phi^4, 1, 2phi, -phi^2, -2phi^3)
fg = sp.Matrix([phi ** 4, 1, 2 * phi, -phi ** 2, -2 * phi ** 3])
check("right golden eigenvector f = (phi^4, 1, 2phi, -phi^2, -2phi^3):  2K f = f/phi", sp.simplify(A * fg - fg / phi) == sp.zeros(5, 1))
a = sp.Matrix([2, 1, 0, -1, -2])     # a(x) = 2 - x = minus the centred residue of x + 1/2
b = sp.Matrix([3, 0, 2, -1, -4])
check("f = a + phi*b with a = (2,1,0,-1,-2) (sawtooth = -centred residue of x + 1/2), b = (3,0,2,-1,-4)",
      sp.simplify(fg - a - phi * b) == sp.zeros(5, 1))
check("on the golden lattice W = Za + Zb:  2K a = b - a,  2K b = a   (matrix [[-1,1],[1,0]] = inverse Fibonacci matrix up to GL2(Z))",
      A * a == b - a and A * b == a)
check("(2K)^2 a + 2K a - a = 0  (the sawtooth is a cyclic vector of the golden block)", A * A * a + A * a - a == sp.zeros(5, 1))
check("W mod 5 = the affine-linear functions F_5 -> F_5 (a = 2 - x, b = 2x + 3 mod 5)",
      all((a[t] - (2 - t)) % 5 == 0 and (b[t] - (2 * t + 3)) % 5 == 0 for t in range(5)))

say("\n=== 3. the folding: cells  Y = {-1/4} = {1},  Z = {+-1/2} = {2,3},  X = {0,-1} = {0,4} ===")
inv = lambda r: pow(r, -1, 5)  # noqa: E731
Y = {(-inv(4)) % 5}
Z = {inv(2) % 5, (-inv(2)) % 5}
X = {0, 4}
check("Y, Z, X partition Z/5", Y | Z | X == set(range(5)) and len(Y) + len(Z) + len(X) == 5)


def push(mu: dict[int, Fraction]) -> dict[int, Fraction]:
    out: dict[int, Fraction] = {}
    for pt, w in mu.items():
        for img in (e[pt], o[pt]):
            out[img] = out.get(img, 0) + w
    return out


ind = lambda S: {s: Fraction(1) for s in S}  # noqa: E731
pY, pZ, pX = push(ind(Y)), push(ind(Z)), push(ind(X))
say(f"   push-forward of 1_Y: {dict(pY)}   1_Z: {dict(pZ)}   1_X: {dict(pX)}")
check("push(1_Y) = 1_Z", pY == ind(Z))
check("push(1_Z) = 2*1_Y + 1_X", pZ == {**{s: Fraction(2) for s in Y}, **ind(X)})
check("push(1_X) = 1_X + 1_Z", pX == {**ind(X), **ind(Z)})
cellsYZX = [sorted(Y), sorted(Z), sorted(X)]
Q = sp.zeros(3, 3)                                  # columns = images of (1_Y, 1_Z, 1_X) in that basis
for j, img in enumerate((pY, pZ, pX)):
    for i, ci in enumerate(cellsYZX):
        assert len({img.get(t, 0) for t in ci}) == 1
        Q[i, j] = img.get(ci[0], 0)
say("   matrix of 2K^T on span(1_Y, 1_Z, 1_X) (columns = images): " + str(Q.tolist()))
check("its charpoly is (x-2)(x^2+x-1)", sp.expand(Q.charpoly(x).as_expr() - (x - 2) * (x ** 2 + x - 1)) == 0)
# pentagon folded along the mirror through a vertex: cells apex / near pair / far pair
C5 = sp.zeros(5, 5)
for i in range(5):
    C5[i, (i + 1) % 5] = 1
    C5[i, (i - 1) % 5] = 1
cells5 = [[0], [1, 4], [2, 3]]
Qpent = sp.zeros(3, 3)
for j, cj in enumerate(cells5):
    v = sp.zeros(5, 1)
    for t in cj:
        v[t] = 1
    img = C5.T * v
    for i, ci in enumerate(cells5):
        assert len({img[t] for t in ci}) == 1
        Qpent[i, j] = img[ci[0]]
check("the same 3x3 matrix is the pentagon adjacency restricted to mirror-symmetric functions (cells apex / near / far)", Qpent == Q)
# explicit pentagons on the residues
P = A.T
for cyc in ((1, 2, 0, 4, 3), (1, 2, 4, 0, 3)):
    Cp = sp.zeros(5, 5)
    for i in range(5):
        u, w = cyc[i], cyc[(i + 1) % 5]
        Cp[u, w] = 1
        Cp[w, u] = 1
    okU = all(P * sp.Matrix([1 if t in S else 0 for t in range(5)]) == Cp * sp.Matrix([1 if t in S else 0 for t in range(5)]) for S in (Y, Z, X))
    diffs = [(cyc[(i + 1) % 5] - cyc[i]) % 5 for i in range(5)]
    affine = len({d if d <= 2 else 5 - d for d in diffs}) == 1
    check(f"2K^T = adjacency of the 5-cycle {cyc} on span(1_Y,1_Z,1_X); steps {diffs}; is an affine image of the additive pentagon: {affine}", okU and not affine)
RES["quotient_matrix"] = Q.tolist()

say("\n=== 4. the same statement on integers: T^k(n) mod 5 for n = 1 (mod 5) is a pentagon random walk ===")


def T(n: int) -> int:
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def lucas(k: int) -> int:
    a_, b_ = 2, 1
    for _ in range(k):
        a_, b_ = b_, a_ + b_
    return a_


beta = {1: 0, 2: 1, 3: 4, 0: 2, 4: 3}          # residue -> pentagon vertex (apex 0; near 1,4; far 2,3)
walk = [Fraction(0)] * 5
walk[0] = Fraction(1)
all_ok = True
rows = []
for k in range(0, 15):
    counts = [0] * 5
    for n in range(1, 5 * 2 ** k, 5):          # n = 1 mod 5, one full period 5 * 2^k
        m = n
        for _ in range(k):
            m = T(m)
        counts[m % 5] += 1
    emp = [Fraction(c, 2 ** k) for c in counts]
    pred = [walk[beta[r]] for r in range(5)]
    ret_formula = Fraction(2 ** k + 2 * (-1) ** k * lucas(k), 5 * 2 ** k)
    same = emp == pred and emp[1] == ret_formula
    all_ok &= same
    rows.append({"k": k, "counts_by_residue_0..4": counts, "walk_law_times_2^k": [int(w * 2 ** k) for w in pred]})
    if k <= 8:
        say(f"   k = {k:>2}: counts of T^k(n) mod 5 = {counts}  (2^k x pentagon-walk law in residue order: {[int(w * 2 ** k) for w in pred]})  return prob {emp[1]} = (2^k + 2(-1)^k L_k)/(5 2^k)")
    walk = [(walk[(i - 1) % 5] + walk[(i + 1) % 5]) / 2 for i in range(5)]
check("for k = 0..14: law of T^k(n) mod 5 given n = 1 mod 5 (all 2^k residues mod 5*2^k) = law of the simple random walk on a pentagon after k steps", all_ok)
RES["integer_walk_check"] = rows
# total variation from uniform, exact closed form
wk = [Fraction(0)] * 5
wk[0] = Fraction(1)
tv_ok = True
for k in range(0, 40):
    tv = sum(abs(w - Fraction(1, 5)) for w in wk) / 2
    # closed form: the walk law is 1/5 + (2/5)(c1^k cos(72 j) + c2^k cos(144 j)), c1 = cos72, c2 = cos144
    if k >= 1:
        num = sp.nsimplify(tv)
    wk = [(wk[(i - 1) % 5] + wk[(i + 1) % 5]) / 2 for i in range(5)]
c1, c2 = sp.cos(2 * sp.pi / 5), sp.cos(4 * sp.pi / 5)
k_ = 12
law = [sp.Rational(1, 5) + sp.Rational(2, 5) * (c1 ** k_ * sp.cos(2 * sp.pi * j / 5) + c2 ** k_ * sp.cos(4 * sp.pi * j / 5)) for j in range(5)]
w12 = [Fraction(0)] * 5
w12[0] = Fraction(1)
for _ in range(k_):
    w12 = [(w12[(i - 1) % 5] + w12[(i + 1) % 5]) / 2 for i in range(5)]
check("spectral formula for the walk law at k = 12: 1/5 + (2/5)(cos^k72 cos(72j) + cos^k144 cos(144j))",
      all(sp.simplify(law[j] - sp.Rational(w12[j].numerator, w12[j].denominator)) == 0 for j in range(5)))

say("\n=== 5. Lucas numbers count the closed walks:  tr(A^n) = 2^n + 1 + (-1)^n L_n ===")
An = sp.eye(5)
tr_ok = True
hc = []
for n in range(1, 21):
    An = An * A
    tr_ok &= An.trace() == 2 ** n + 1 + (-1) ** n * lucas(n)
check("tr((2K_5)^n) = 2^n + 1 + (-1)^n L_n for n = 1..20", tr_ok)
# word-level meaning: words w in {e,o}^n act by x -> alpha x + beta; count words with alpha = 1 (5 | 2^n - 3^s) and beta = 0 (5 | C(w))
wl_ok = True
for n in range(1, 15):
    An_cnt = Bn_cnt = fix_total = 0
    for w in itertools.product((0, 1), repeat=n):
        al, be = 1, 0
        for bit in w:                          # apply branches left to right
            if bit == 0:
                al, be = al * 3 % 5, be * 3 % 5            # x -> 3x
            else:
                al, be = (-al) % 5, (3 - be) % 5           # x -> 3 - x
        if al == 1:
            An_cnt += 1
            if be == 0:
                Bn_cnt += 1
                fix_total += 5
        else:
            fix_total += 1
    wl_ok &= fix_total == 2 ** n + 1 + (-1) ** n * lucas(n)
    wl_ok &= 5 * Bn_cnt == An_cnt + 1 + (-1) ** n * lucas(n)
    hc.append({"n": n, "words_with_5|2^n-3^s": An_cnt, "of_which_5|C(w)": Bn_cnt, "L_n": lucas(n)})
check("word count: #{w in {e,o}^n : 5 | 2^n - 3^s and 5 | C(w)} = (A_n + 1 + (-1)^n L_n)/5 with A_n = #{w : 5 | 2^n - 3^s}, n = 1..14", wl_ok)
say("   n, A_n, B_n: " + ", ".join(f"({r['n']},{r['words_with_5|2^n-3^s']},{r['of_which_5|C(w)']})" for r in hc))
RES["hidden_colour_5"] = hc

say("\n=== 6. what is NOT the mechanism (tests of the additive-pentagon story) ===")
t = sp.zeros(5, 5)
for i in range(5):
    t[i, (i + 1) % 5] = 1           # (t f)(x) = f(x+1)
c1m, c2m = t + t.T, t ** 2 + (t ** 2).T
Re = sp.zeros(5, 5)
Ro = sp.zeros(5, 5)
for i in range(5):
    Re[i, e[i]] = 1
    Ro[i, o[i]] = 1
check("additive pentagon c1 = t + t^-1 and pentagram c2 = t^2 + t^-2:  c1 c2 = c1 + c2 and c1 + c2 = J - I  (so c^2 + c - 1 = 0 off constants)",
      c1m * c2m == c1m + c2m and c1m + c2m == sp.ones(5, 5) - sp.eye(5))
check("R_e c1 = c2 R_e (e swaps pentagon and pentagram), R_o commutes with c1", Re * c1m == c2m * Re and Ro * c1m == c1m * Ro)
check("but 2K does NOT commute with c1", A * c1m != c1m * A)
Wb = sp.Matrix.hstack(a, b)
check("the golden plane W is NOT invariant under the additive pentagon c1", sp.Matrix.hstack(Wb, c1m * a).rank() == 3)
# projections of the golden eigenvector on V1 (72-degree rep) and V2 (144-degree rep)
P1 = sp.Matrix(5, 5, lambda i, j: sp.Rational(2, 5) * sp.cos(2 * sp.pi * (i - j) / 5))
P2 = sp.Matrix(5, 5, lambda i, j: sp.Rational(2, 5) * sp.cos(4 * sp.pi * (i - j) / 5))
n1 = sp.simplify((P1 * fg).dot(P1 * fg))
n2 = sp.simplify((P2 * fg).dot(P2 * fg))
say(f"   golden eigenvector f: |proj on V1|^2 = {sp.nsimplify(n1)} = {float(n1):.6f},  |proj on V2|^2 = {sp.nsimplify(n2)} = {float(n2):.6f}  (both non-zero: f lies in neither D5-isotypic plane)")
check("golden eigenvector lies in neither V1 nor V2", n1 != 0 and n2 != 0)
check("2K_5 is not normal (A A^T != A^T A) although its spectrum is real", A * A.T != A.T * A)
sv = sorted((sp.sqrt(v) for v, mlt in (A.T * A).eigenvals().items() for _ in range(mlt)), key=float)
say("   singular values of 2K_5: " + ", ".join(str(s) for s in sv) + "  (no golden ratio: phi is in the eigenvalues, not the singular values)")
# digraph automorphisms / anti-automorphisms
auts = [p for p in itertools.permutations(range(5)) if all(A[p[i], p[j]] == A[i, j] for i in range(5) for j in range(5))]
anti = [p for p in itertools.permutations(range(5)) if all(A[p[i], p[j]] == A[j, i] for i in range(5) for j in range(5))]
say(f"   automorphisms of the branch digraph: {len(auts)} (identity only); anti-automorphisms (reversals): {len(anti)}")
RES["digraph_automorphisms"] = len(auts)
RES["digraph_antiautomorphisms"] = [list(p) for p in anti]
# Latimer-MacDuffee: conjugacy has no content
#   M S = S F^-1 with F^-1 = [[0,1],[1,-1]]  <=>  S = [v, M v];  det S = a21 p^2 + (a22-a11) p r - a12 r^2  (v = (p, r)),
#   a binary quadratic form of discriminant 5; class number h(5) = 1 means it always represents +-1.
cnt = 0
tot = 0
for a11 in range(-12, 13):
    a22 = -1 - a11
    for a12 in range(-200, 201):
        if a12 == 0:
            continue
        num = a11 * a22 + 1          # a12 a21 = a11 a22 - det, det = -1
        if num % a12:
            continue
        a21 = num // a12
        tot += 1
        found = any(a21 * p_ * p_ + (a22 - a11) * p_ * r_ - a12 * r_ * r_ in (1, -1) for p_ in range(-60, 61) for r_ in range(-60, 61))
        cnt += found
say(f"   Latimer-MacDuffee sanity: of {tot} integer 2x2 matrices with charpoly x^2+x-1 (|a11| <= 12, |a12| <= 200), {cnt} are GL2(Z)-conjugate to the")
say("   pentagon/A_4 block [[0,1],[1,-1]] (conjugator [v, Mv] with |v| <= 60).  So 'conjugate to the pentagon block' says nothing beyond the characteristic polynomial.")
RES["latimer_macduffee_sample"] = {"matrices": tot, "conjugate_found": cnt}

say("\n=== 7. over Q: when does the folded pentagon close? ===")
say("   push-forward of point masses at rational points (valid mod every N prime to 6):")
say("     delta_0 + delta_{-1}       ->  (delta_0 + delta_{-1}) + (delta_{1/2} + delta_{-1/2})        [always]")
say("     delta_{1/2} + delta_{-1/2} ->  2 delta_{-1/4} + delta_{1/4} + delta_{5/4}")
say("     delta_{-1/4}               ->  delta_{-1/8} + delta_{1/8}")
closes = []
for Nn in range(5, 2000):
    if Nn % 2 == 0 or Nn % 3 == 0:
        continue
    i2, i4, i8 = pow(2, -1, Nn), pow(4, -1, Nn), pow(8, -1, Nn)
    if {i4 % Nn, 5 * i4 % Nn} == {0, Nn - 1} and {i8 % Nn, (-i8) % Nn} == {i2 % Nn, (-i2) % Nn}:
        closes.append(Nn)
check("the configuration {-1/4; +-1/2; 0,-1} closes ({1/4,5/4} = {-1,0} and {+-1/8} = {+-1/2}) only for N = 5 among N < 2000 prime to 6", closes == [5])
RES["closing_moduli"] = closes

bad = [k_ for k_, v in RES["checks"].items() if not v]
say(f"\n{len(RES['checks'])} checks, {len(bad)} failed" + ("" if not bad else ": " + "; ".join(bad)))
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
Path(__file__).with_suffix(".json").write_text(json.dumps(RES, indent=1, default=str), encoding="utf-8")
