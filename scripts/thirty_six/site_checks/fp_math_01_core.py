"""Reviewer check 1 for site/explore/folded-pentagon.md (lens: mathematical check).

Independent recomputation of every statement in the sections 'Two branches modulo 5', 'The fold',
'On actual integers', 'What it is not', 'Why 5' and the sign-blind remarks.  Nothing is imported
from the thread; exact arithmetic (int / Fraction / sympy) except where a float is announced.

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 fp_math_01_core.py
"""
from __future__ import annotations

import itertools
import math
from fractions import Fraction as Fr

import sympy as sp

FAIL = 0


def check(ok: bool, label: str) -> None:
    global FAIL
    if not ok:
        FAIL += 1
    print(f"   [{'ok' if ok else 'FAIL'}] {label}")


PHI = (1 + math.sqrt(5)) / 2

# ---------------------------------------------------------------- 0. constants
print("=== 0. constants ===")
check(abs(math.cos(math.radians(36)) - PHI / 2) < 1e-15, f"cos 36 = phi/2 = {PHI/2:.6f} (page: 0.809)")
check(abs(math.cos(math.radians(72)) - 1 / (2 * PHI)) < 1e-15, f"cos 72 = 1/(2 phi) = {1/(2*PHI):.6f}")
check(abs(math.cos(math.radians(144)) + PHI / 2) < 1e-15, "cos 144 = -cos 36 = -phi/2")
# apothem of the pentagon of circumradius 1, and midpoint of the two neighbours of a vertex
V = [complex(math.cos(math.pi / 2 + 2 * math.pi * i / 5), math.sin(math.pi / 2 + 2 * math.pi * i / 5)) for i in range(5)]
check(abs(abs((V[2] + V[3]) / 2) - PHI / 2) < 1e-15, "apothem (midpoint of the opposite side) = cos 36")
check(abs((V[1] + V[4]) / 2 - math.cos(math.radians(72)) * V[0]) < 1e-15, "midpoint of the two neighbours = cos 72 x vertex")
check(abs((V[2] + V[3]) / 2 + math.cos(math.radians(36)) * V[0]) < 1e-15, "midpoint of the opposite side = -cos 36 x vertex (across the centre)")

# ---------------------------------------------------------------- 1. two branches mod 5
print("=== 1. two branches modulo 5 ===")
N = 5
inv2 = pow(2, -1, N)
e = [x * inv2 % N for x in range(N)]
o = [(3 * x + 1) * inv2 % N for x in range(N)]
print(f"   e = {e}   o = {o}")
check(inv2 == 3 and e == [3 * x % 5 for x in range(5)], "x/2 = 3x mod 5")
check(o == [(3 - x) % 5 for x in range(5)], "(3x+1)/2 = 3 - x mod 5")
check([x for x in range(5) if e[x] == x] == [0], "even branch fixes 0 only")
check(sp.n_order(3, 5) == 4, "the multiplier 3 has order 4")
check(all(o[o[x]] == x for x in range(5)) and [x for x in range(5) if o[x] == x] == [4], "odd branch is an involution fixing 4 = -1 only")
check(e[2] == 1 and o[2] == 1, "both branches send 2 to 1 (the apex)")
check({e[3], o[3]} == {0, 4}, "both branches send 3 into the far pair {0, 4}")

# ---------------------------------------------------------------- 2. Theorem A
print("=== 2. Theorem A: push-forward of cell-uniform mass ===")


def push(mass: list) -> list:
    out = [0] * 5
    for x in range(5):
        out[e[x]] += mass[x]
        out[o[x]] += mass[x]
    return out


def ind(cell):
    return [1 if x in cell else 0 for x in range(5)]


Y, Z, X = {1}, {2, 3}, {0, 4}
check(push(ind(Y)) == ind(Z), "2K: 1_Y -> 1_Z")
check(push(ind(Z)) == [2 * a + b for a, b in zip(ind(Y), ind(X))], "2K: 1_Z -> 2*1_Y + 1_X")
check(push(ind(X)) == [a + b for a, b in zip(ind(X), ind(Z))], "2K: 1_X -> 1_X + 1_Z")
# the page's wording, in probabilities: unit mass spread evenly over each cell
uY = [Fr(v, 1) for v in ind(Y)]
uZ = [Fr(v, 2) for v in ind(Z)]
uX = [Fr(v, 2) for v in ind(X)]
half = lambda m: [v / 2 for v in push(m)]
check(half(uY) == uZ, "all the mass on Y goes to Z, evenly")
check(half(uZ) == [a / 2 + b / 2 for a, b in zip(uY, uX)], "half the mass on Z goes to Y, half to X, evenly")
check(half(uX) == [a / 2 + b / 2 for a, b in zip(uZ, uX)], "half the mass on X goes to Z, half stays on X, evenly")
# folded pentagon: adjacency of C5 on indicator vectors of {v0}, {v1,v4}, {v2,v3}
C5 = sp.zeros(5, 5)
for v in range(5):
    C5[v, (v + 1) % 5] = 1
    C5[v, (v - 1) % 5] = 1
fold = {}
for name, cell in (("Y", [0]), ("Z", [1, 4]), ("X", [2, 3])):
    vec = sp.Matrix([1 if v in cell else 0 for v in range(5)])
    fold[name] = list(C5 * vec)
check(fold["Y"] == [0, 1, 0, 0, 1] and fold["Z"] == [2, 0, 1, 1, 0] and fold["X"] == [0, 1, 1, 1, 1], "pentagon: vertex -> nbrs; nbrs -> 2 vertex + far; far -> nbrs + far (same three rules)")
M3 = sp.Matrix([[0, 2, 0], [1, 0, 1], [0, 1, 1]])   # columns: images of 1_Y, 1_Z, 1_X in the basis (1_Y, 1_Z, 1_X)
xs = sp.symbols("x")
cp3 = sp.factor(M3.charpoly(xs).as_expr())
print(f"   charpoly of 2K on span(1_Y,1_Z,1_X): {cp3}")
check(sp.expand(cp3 - (xs - 2) * (xs**2 + xs - 1)) == 0, "= (x-2)(x^2+x-1): eigenvalues of K are 1, cos 72, cos 144")
r = sorted(float(v) / 2 for v in sp.Poly(xs**2 + xs - 1).nroots())
check(abs(r[0] + PHI / 2) < 1e-12 and abs(r[1] - 1 / (2 * PHI)) < 1e-12, f"roots of x^2+x-1 halved: {r[0]:.6f}, {r[1]:.6f}")

# ---------------------------------------------------------------- 3. the proof's fractions
print("=== 3. the three lines of the proof, over Q ===")
E = lambda x: Fr(x) / 2
O = lambda x: (3 * Fr(x) + 1) / 2
h, q, e8 = Fr(1, 2), Fr(1, 4), Fr(1, 8)
check(E(0) == 0 and O(0) == h and E(-1) == -h and O(-1) == -1, "e(0)=0, o(0)=1/2, e(-1)=-1/2, o(-1)=-1")
check(E(h) == q and E(-h) == -q and O(-h) == -q and O(h) == Fr(5, 4), "e(+-1/2)=+-1/4, o(-1/2)=-1/4, o(1/2)=5/4")
check(E(-q) == -e8 and O(-q) == e8, "e(-1/4)=-1/8, o(-1/4)=1/8")
m5 = lambda fr: fr.numerator * pow(fr.denominator, -1, 5) % 5
check(m5(q) == 4 and m5(Fr(5, 4)) == 0, "mod 5: 1/4 = -1, 5/4 = 0")
check(m5(e8) == 2 and m5(-e8) == 3 and m5(-h) == 2 and m5(h) == 3, "mod 5: 1/8 = 2 = -1/2 and -1/8 = 3 = 1/2")
check(m5(-q) == 1 and {m5(h), m5(-h)} == {2, 3} and {m5(Fr(0)), m5(Fr(-1))} == {0, 4}, "rational names: Y={-1/4}={1}, Z={+-1/2}={2,3}, X={0,-1}={0,4}")

# ---------------------------------------------------------------- 4. corollary on integers
print("=== 4. corollary: T^k(n) mod 5 over n = 1 (mod 5) in ANY window of 5*2^k consecutive integers ===")


def T(n: int, c: int = 1) -> int:
    return n // 2 if n % 2 == 0 else (3 * n + c) // 2


def law_on_integers(k: int, start: int, window_start: int, c: int = 1) -> list[int]:
    counts = [0] * 5
    for n0 in range(window_start, window_start + 5 * 2**k):
        if n0 % 5 != start:
            continue
        n = n0
        for _ in range(k):
            n = T(n, c)
        counts[n % 5] += 1
    return counts


def walk(k: int, frm: int) -> list[int]:
    w = [0] * 5
    w[frm] = 1
    for _ in range(k):
        w = [w[(v - 1) % 5] + w[(v + 1) % 5] for v in range(5)]
    return w


def lucas(k: int) -> int:
    a, b = 2, 1
    for _ in range(k):
        a, b = b, a + b
    return a


ORDER = [1, 2, 4, 0, 3]          # residue sitting on vertex v of the pentagon 1-2-4-0-3


def walk_by_residue(k: int, start: int, order=ORDER) -> list[int]:
    w = walk(k, order.index(start))
    out = [0] * 5
    for v, r in enumerate(order):
        out[r] = w[v]
    return out


K_MAX = 16
ok_all, ok_formula, returns = True, True, []
for k in range(K_MAX + 1):
    target = walk_by_residue(k, 1)
    wins = [1, -(5 * 2**k) // 2 - 7, -5 * 2**k - 3, 123456789] if k <= 13 else [1, -(5 * 2**k) // 2 - 7]
    for w0 in wins:
        c = law_on_integers(k, 1, w0)
        ok_all &= c == target and sum(c) == 2**k
    returns.append(target[1])
    ok_formula &= 5 * target[1] == 2**k + 2 * (-1) ** k * lucas(k)
    if k in (0, 1, 2, 8, 16):
        print(f"   k = {k:2d}: counts on residues 0..4 = {law_on_integers(k, 1, 1)}   pentagon walk = {target}")
check(ok_all, f"k = 0..{K_MAX}: integer counts = pentagon-walk counts (windows starting at 1, negative, straddling 0, large)")
check(law_on_integers(8, 1, 1) == [57, 70, 36, 36, 57], "k = 8: 256 integers land 57, 70, 36, 36, 57 on residues 0, 1, 2, 3, 4")
check(ok_formula, f"return count = (2^k + 2(-1)^k L_k)/5 for k = 0..{K_MAX}")
print(f"   returns k = 0..{K_MAX}: {returns}")
check(returns[:9] == [1, 0, 2, 0, 6, 2, 20, 14, 70], "first return counts 1, 0, 2, 0, 6, 2, 20, 14, 70 (A054877 as quoted)")
check([lucas(k) for k in range(7)] == [2, 1, 3, 4, 7, 11, 18], "Lucas numbers 2, 1, 3, 4, 7, 11, 18")
# the second labelling 1-2-0-4-3 gives the same law from the apex (the fold cannot tell them apart)
check(all(walk_by_residue(k, 1, [1, 2, 0, 4, 3]) == walk_by_residue(k, 1) for k in range(K_MAX + 1)), "labelling 1-2-0-4-3 gives the same apex law as 1-2-4-0-3")

# ---------------------------------------------------------------- 5. decay rate
print("=== 5. distance from uniform (total variation) against (phi/2)^k ===")


def chain_law(k: int, start: int, c: int = 1) -> list[Fr]:
    inv = pow(2, -1, 5)
    ee = [x * inv % 5 for x in range(5)]
    oo = [(3 * x + c) * inv % 5 for x in range(5)]
    m = [Fr(0)] * 5
    m[start] = Fr(1)
    for _ in range(k):
        nxt = [Fr(0)] * 5
        for x in range(5):
            nxt[ee[x]] += m[x] / 2
            nxt[oo[x]] += m[x] / 2
        m = nxt
    return m


def tv(m) -> float:
    return float(sum(abs(v - Fr(1, 5)) for v in m) / 2)


for s in range(5):
    ratios = [tv(chain_law(k, s)) / (PHI / 2) ** k for k in (8, 16, 40, 41, 80)]
    print(f"   start {s}: TV/(phi/2)^k at k = 8, 16, 40, 41, 80: " + ", ".join(f"{x:.5f}" for x in ratios))
lim = [tv(chain_law(80, s)) / (PHI / 2) ** 80 for s in range(5)]
lim79 = [tv(chain_law(79, s)) / (PHI / 2) ** 79 for s in range(5)]
check(all(x > 0.05 and abs(x - y) < 1e-9 for x, y in zip(lim, lim79)),
      "from EVERY start residue the distance decays at rate exactly phi/2 (ratio settles on a non-zero constant: "
      + ", ".join(f"{x:.5f}" for x in lim) + ")")
check(abs(lim[1] - 2 * PHI / 5) < 1e-9, f"apex start: ratio tends to 2 phi/5 = {2*PHI/5:.6f}")
check(all(chain_law(k, 1) == [Fr(v, 2**k) for v in walk_by_residue(k, 1)] for k in range(40)), "chain law from 1 = pentagon law for k = 0..39 (exact fractions)")

# ---------------------------------------------------------------- 6. what it is not
print("=== 6. what it is not ===")
A = sp.zeros(5, 5)
for x in range(5):
    A[x, e[x]] += 1
    A[x, o[x]] += 1
cpA = sp.factor(A.charpoly(xs).as_expr())
cpC = sp.factor(C5.charpoly(xs).as_expr())
print(f"   charpoly(2K_5) = {cpA}\n   charpoly(pentagon) = {cpC}")
check(sp.expand(cpA - xs * (xs - 1) * (xs - 2) * (xs**2 + xs - 1)) == 0, "charpoly(2K_5) = x(x-1)(x-2)(x^2+x-1)")
check(sp.expand(cpC - (xs - 2) * (xs**2 + xs - 1) ** 2) == 0, "charpoly(pentagon) = (x-2)(x^2+x-1)^2")
relabel = 0
for p in itertools.permutations(range(5)):
    P = sp.zeros(5, 5)
    for i, j in enumerate(p):
        P[i, j] = 1
    if P * A * P.T == C5:
        relabel += 1
check(relabel == 0, "none of the 120 relabellings turns 2K_5 into the pentagon adjacency matrix")
check(law_on_integers(1, 2, 1) == [0, 2, 0, 0, 0], "from n = 2 (mod 5) every integer lands on residue 1 after one step")
for s in (0, 2, 3, 4):
    laws = [[v * 2**k for v in chain_law(k, s)] for k in range(K_MAX + 1)]
    hit = [p for p in itertools.permutations(range(5)) if all(laws[k] == [walk(k, p[s])[p[r]] for r in range(5)] for k in range(K_MAX + 1))]
    hit1 = [p for p in itertools.permutations(range(5)) if laws[1] == [walk(1, p[s])[p[r]] for r in range(5)]]
    check(not hit, f"start {s}: none of the 120 labellings gives a pentagon law (k = 0..{K_MAX}); already none at k = 1: {not hit1}")
hit = [p for p in itertools.permutations(range(5)) if all([v * 2**k for v in chain_law(k, 1)] == [walk(k, p[1])[p[r]] for r in range(5)] for k in range(K_MAX + 1))]
print(f"   labellings (residue -> vertex) that DO work from start 1: {len(hit)} of 120; cyclic orders: " + ", ".join(sorted({'-'.join(str(p.index(v)) for v in range(5)) for p in hit if p[1] == 0})))
edges = lambda cyc: {frozenset((cyc[i], cyc[(i + 1) % 5])) for i in range(5)}
affine = [[(a * i + b) % 5 for i in range(5)] for a in range(1, 5) for b in range(5)]
check(all(edges(ORDER) != edges(c) for c in affine), "1-2-4-0-3 is not an affine image of 0-1-2-3-4 (neither the additive pentagon nor its pentagram)")
check(edges([e[x] for x in range(5)]) == edges([0, 2, 4, 1, 3]), "halving maps the additive pentagon 0-1-2-3-4 onto its pentagram (sides -> diagonals)")

# ---------------------------------------------------------------- 7. why 5, only 5 (A')
print("=== 7. why 5 ===")
a, b = pow(2, -1, 5), 3 * pow(2, -1, 5) % 5
check((a, b) == (3, 4) and b == (a + 1) % 5 and b == a * a % 5 and b == 4, "mod 5: a = 1/2 = 3, b = 3/2 = 4 = a + 1 = a^2 = -1")
check(sp.expand((xs - 3) ** 2 - (xs**2 - xs - 1)).as_poly(xs).trunc(5).is_zero, "x^2 - x - 1 = (x - 3)^2 mod 5")
inv_e, inv_o, closes = [], [], []
for n in range(5, 3000):
    if math.gcd(n, 6) != 1:
        continue
    i2 = pow(2, -1, n)
    if all((x * i2 * i2 - x) % n == 0 for x in range(n)):
        inv_e.append(n)
    if all((((3 * ((3 * x + 1) * i2 % n) + 1) * i2) - x) % n == 0 for x in range(n)):
        inv_o.append(n)
    f = lambda num, den: num * pow(den, -1, n) % n
    if {f(1, 4), f(5, 4)} == {f(-1, 1), 0} and {f(1, 8), f(-1, 8)} == {f(1, 2), f(-1, 2)}:
        closes.append(n)
check(inv_o == [5] and inv_e == [], f"moduli prime to 6 below 3000 with an involutive branch: odd {inv_o}, even {inv_e}")
check(closes == [5], f"moduli prime to 6 below 3000 at which lines 2 and 3 of the proof close up: {closes}")
check(5 == 3 + 2 == 3**2 - 2**2, "5 = 3 + 2 = 3^2 - 2^2")

# ---------------------------------------------------------------- 8. sign-blindness
print("=== 8. 3x-1 and 3x+c ===")
em = [x * 3 % 5 for x in range(5)]
om = [(3 * x - 1) * 3 % 5 for x in range(5)]


def push_m(mass):
    out = [0] * 5
    for x in range(5):
        out[em[x]] += mass[x]
        out[om[x]] += mass[x]
    return out


Ym, Zm, Xm = {4}, {2, 3}, {0, 1}
check(push_m(ind(Ym)) == ind(Zm) and push_m(ind(Zm)) == [2 * a_ + b_ for a_, b_ in zip(ind(Ym), ind(Xm))]
      and push_m(ind(Xm)) == [a_ + b_ for a_, b_ in zip(ind(Xm), ind(Zm))], "3x-1: Theorem A with apex 4, near pair {2,3}, far pair {0,1}")
ORDER_M = [(5 - r) % 5 for r in ORDER]
ok = True
for k in range(K_MAX + 1):
    c = law_on_integers(k, 4, -(5 * 2**k) // 2 - 7, c=-1)
    ok &= c == walk_by_residue(k, 4, ORDER_M) and c == [walk_by_residue(k, 1)[(5 - r) % 5] for r in range(5)]
check(ok, f"3x-1 on integers, n = 4 (mod 5), k = 0..{K_MAX}: pentagon law = the 3x+1 law with residues negated")
ok = True
for n in (5, 7, 11, 13, 25, 35, 49, 55, 77, 91):
    i2 = pow(2, -1, n)
    for c in range(1, n):
        if math.gcd(c, n) != 1:
            continue
        for x in range(n):
            ok &= (c * x) * i2 % n == c * (x * i2) % n and (3 * c * x + c) * i2 % n == c * ((3 * x + 1) * i2) % n
check(ok, "3x+c mod N is the 3x+1 chain relabelled by x -> cx for every c prime to N (ten moduli)")
cyc = [5]
for _ in range(3):
    cyc.append(T(cyc[-1], -1))
check(cyc == [5, 7, 10, 5], f"3x-1 shortcut cycle: {' -> '.join(map(str, cyc))}")

print(f"\n{FAIL} failures")
