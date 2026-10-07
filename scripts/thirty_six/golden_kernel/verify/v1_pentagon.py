"""Skeptic check 1: Theorem A (folded pentagon), its corollary on integers, the trace / word-count
identities, uniqueness of the lumping, and the mirror / cousin tests.

Independent of gk_common.py: branches are found by brute-force search on residues, the integer statements
are checked with the integer map T itself and with integer word constants C(w), not with residues mod 5.

CONVENTION: shortcut map T(n) = n/2 (n even), (3n+1)/2 (n odd).  Mirror: (3n-1)/2.  Cousin: (5n+1)/2.
Run:  python -X utf8 v1_pentagon.py      (writes v1_pentagon.log)
"""
from __future__ import annotations

import itertools
import sys
from fractions import Fraction
from math import gcd
from pathlib import Path

import sympy as sp

LOG: list[str] = []
FAIL: list[str] = []


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def check(name: str, cond: bool) -> None:
    say(f"   [{'ok' if cond else 'FAIL'}] {name}")
    if not cond:
        FAIL.append(name)


def branches(N: int, q: int = 3, c: int = 1, d: int = 2):
    """e[x], o[x] on Z/N found by search: d*e(x) = x, d*o(x) = q x + c (mod N)."""
    e, o = [None] * N, [None] * N
    for x in range(N):
        for y in range(N):
            if (d * y - x) % N == 0:
                assert e[x] is None
                e[x] = y
            if (d * y - (q * x + c)) % N == 0:
                assert o[x] is None
                o[x] = y
    assert None not in e and None not in o
    return e, o


def push_matrix(N, e, o):
    """P[y][x] = number of branches sending x to y  (acts on measures as column vectors)."""
    P = [[0] * N for _ in range(N)]
    for x in range(N):
        P[e[x]][x] += 1
        P[o[x]][x] += 1
    return sp.Matrix(P)


x = sp.symbols("x")

# ------------------------------------------------------------------ 1. Theorem A
say("=== 1. Theorem A on Z/5 (3x+1) ===")
e, o = branches(5)
say(f"   e = {e}, o = {o}")
P5 = push_matrix(5, e, o)
cells = [[1], [2, 3], [0, 4]]                   # Y, Z, X


def ind(S, N=5):
    return sp.Matrix([1 if t in S else 0 for t in range(N)])


iY, iZ, iX = (ind(c_) for c_ in cells)
check("push(1_Y) = 1_Z", P5 * iY == iZ)
check("push(1_Z) = 2*1_Y + 1_X", P5 * iZ == 2 * iY + iX)
check("push(1_X) = 1_X + 1_Z", P5 * iX == iX + iZ)
cp = sp.factor(P5.charpoly(x).as_expr())
say(f"   charpoly(2K_5) = {cp}")
check("charpoly(2K_5) = x(x-1)(x-2)(x^2+x-1)", sp.expand(cp - x * (x - 1) * (x - 2) * (x ** 2 + x - 1)) == 0)

# the 5-state chain itself is NOT a pentagon walk
C5 = sp.zeros(5, 5)
for i in range(5):
    C5[i, (i + 1) % 5] = C5[(i + 1) % 5, i] = 1
say(f"   charpoly(pentagon adjacency) = {sp.factor(C5.charpoly(x).as_expr())}")
check("the 5-state residue chain is NOT isomorphic to the pentagon walk (different characteristic polynomials: "
      "2K_5 has the extra eigenvalues 1 and 0, the pentagon has the golden pair twice)",
      sp.expand(C5.charpoly(x).as_expr() - P5.charpoly(x).as_expr()) != 0)
isos = [p for p in itertools.permutations(range(5))
        if all(P5[p[i], p[j]] == C5[i, j] for i in range(5) for j in range(5))]
check("no relabelling of residues turns 2K_5 into the pentagon adjacency matrix", len(isos) == 0)
check("2K_5 is not symmetric (the chain is not reversible w.r.t. uniform measure)", P5 != P5.T)

# strong lumpability fails: residue 2 goes to Y with both branches, residue 3 to X with both
to_cell = {1: "Y", 2: "Z", 3: "Z", 0: "X", 4: "X"}
say(f"   images of 2: {to_cell[e[2]]},{to_cell[o[2]]};  images of 3: {to_cell[e[3]]},{to_cell[o[3]]}")
check("NOT strongly lumpable: the two points of Z have different cell-transition laws", {to_cell[e[2]], to_cell[o[2]]} != {to_cell[e[3]], to_cell[o[3]]})

# which starting residues give the pentagon law?  only the apex residue 1
def law(start, k):
    v = sp.zeros(5, 1)
    v[start] = 1
    for _ in range(k):
        v = P5 * v
    return [Fraction(int(v[i]), 2 ** k) for i in range(5)]


def pent_law(k):
    w = [Fraction(0)] * 5
    w[0] = Fraction(1)
    for _ in range(k):
        w = [(w[(i - 1) % 5] + w[(i + 1) % 5]) / 2 for i in range(5)]
    return w


starts_ok = []
for s in range(5):
    ok_any = False
    for perm in itertools.permutations(range(5)):      # any labelling residue -> pentagon vertex
        if all([law(s, k)[r] for r in range(5)] == [pent_law(k)[perm[r]] for r in range(5)] for k in range(0, 9)):
            ok_any = True
            break
    starts_ok.append(ok_any)
say(f"   starting residue r: is the law of the chain after k = 0..8 steps a pentagon-walk law under SOME labelling? {dict(enumerate(starts_ok))}")
check("only the start n = 1 (mod 5) gives a pentagon-walk law", starts_ok == [False, True, False, False, False])

# ------------------------------------------------------------------ 2. all exactly lumpable partitions (control)
say("\n=== 2. control: ALL partitions of Z/N whose cell-uniform measures are preserved (exact lumpability) ===")


def set_partitions(items):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for part in set_partitions(rest):
        yield [[first]] + part
        for i in range(len(part)):
            yield part[:i] + [[first] + part[i]] + part[i + 1:]


def exact_lumpings(N, e, o):
    out = []
    for part in set_partitions(list(range(N))):
        if len(part) in (1, N):
            continue
        ok = True
        for C in part:
            img = [0] * N
            for t in C:
                img[e[t]] += 1
                img[o[t]] += 1
            if any(len({img[t] for t in D}) != 1 for D in part):
                ok = False
                break
        if ok:
            out.append(sorted(sorted(c_) for c_ in part))
    return out


L5 = exact_lumpings(5, e, o)
say(f"   N = 5 (3x+1): non-trivial exactly lumpable partitions: {L5}")
check("(Y, Z, X) = {1},{2,3},{0,4} is among them", [[0, 4], [1], [2, 3]] in L5)
for N in (7, 11):
    eN, oN = branches(N)
    LN = exact_lumpings(N, eN, oN)
    say(f"   N = {N} (3x+1): non-trivial exactly lumpable partitions: {len(LN)}  {LN[:6]}")

# ------------------------------------------------------------------ 3. corollary on integers
say("\n=== 3. corollary on integers (the map T itself; window of 5*2^k consecutive integers containing negatives) ===")


def T(n, q=3, c=1):
    return n // 2 if n % 2 == 0 else (q * n + c) // 2


def lucas(k):
    a, b = 2, 1
    for _ in range(k):
        a, b = b, a + b
    return a


beta = {1: 0, 2: 1, 3: 4, 0: 2, 4: 3}
all_ok = True
for k in range(0, 17):
    period = 5 * 2 ** k
    lo = -(period // 3)                      # an arbitrary window, not [0, period)
    counts = [0] * 5
    for n in range(lo, lo + period):
        if n % 5 != 1:
            continue
        m = n
        for _ in range(k):
            m = T(m)
        counts[m % 5] += 1
    w = pent_law(k)
    pred = [int(w[beta[r]] * 2 ** k) for r in range(5)]
    ret = Fraction(2 ** k + 2 * (-1) ** k * lucas(k), 5 * 2 ** k)
    ok = counts == pred and Fraction(counts[1], 2 ** k) == ret and sum(counts) == 2 ** k
    all_ok &= ok
    if k in (0, 1, 2, 8, 16):
        say(f"   k = {k:>2}: counts by residue {counts}; pentagon law x 2^k {pred}; return prob {ret}")
check("k = 0..16: law of T^k(n) mod 5 over n = 1 (mod 5) in a window of length 5*2^k = pentagon-walk law; return prob (2^k + 2(-1)^k L_k)/(5 2^k)", all_ok)

# starting from n = 2 (mod 5) the law is not a pentagon-walk law (k = 1: everything lands on residue 1)
cnt = [0] * 5
for n in range(2, 5 * 2, 5):
    cnt[T(n) % 5] += 1
say(f"   start n = 2 (mod 5), k = 1: counts {cnt}  (a pentagon walk from a neighbour would split 1/2, 1/2)")

# ------------------------------------------------------------------ 4. trace identity and word counts with integer constants
say("\n=== 4. tr(A_5^n) = 2^n + 1 + (-1)^n L_n and the word count, with integer word constants ===")
A = P5.T
M = sp.eye(5)
ok = True
for n in range(1, 41):
    M = M * A
    ok &= M.trace() == 2 ** n + 1 + (-1) ** n * lucas(n)
check("tr((2K_5)^n) = 2^n + 1 + (-1)^n L_n, n = 1..40 (n = 0 fails: tr = 5, formula gives 4, because of the eigenvalue 0)", ok)
ok = True
seq_B, seq_A = [], []
for n in range(1, 17):
    An = Bn = 0
    for w in itertools.product((0, 1), repeat=n):
        # T^n(x) = (3^s x + C)/2^n along the parity word w (first letter applied first)
        s, C, pw = 0, 0, 1          # after j steps: value = (3^s x + C)/2^j ; keep numerator pieces as integers
        for bit in w:
            if bit:
                C = 3 * C + pw       # (3 y + 1)/2 with y = (3^s x + C)/pw
                s += 1
            pw *= 2
        if (2 ** n - 3 ** s) % 5 == 0:
            An += 1
            if C % 5 == 0:
                Bn += 1
    ok &= 5 * Bn == An + 1 + (-1) ** n * lucas(n)
    # closed form of A_n: sum of C(n, s) over s = -n (mod 4)
    ok &= An == sum(sp.binomial(n, s) for s in range(n + 1) if (s + n) % 4 == 0)
    seq_A.append(An)
    seq_B.append(Bn)
check("#{w of length n: 5 | 2^n - 3^s and 5 | C(w)} = (A_n + 1 + (-1)^n L_n)/5 with integer C(w), n = 1..16;  A_n = sum_{s = -n mod 4} C(n, s)", ok)
say(f"   A_n, n = 1..16: {seq_A}")
say(f"   B_n, n = 1..16: {seq_B}")

# ------------------------------------------------------------------ 5. mirror and cousins
say("\n=== 5. mirror (3x-1) and cousins (3x+c, 5x+1, 7x+1) ===")
em, om = branches(5, 3, -1)
Pm = push_matrix(5, em, om)
neg = lambda S: sorted((-t) % 5 for t in S)  # noqa: E731
cm = [neg(c_) for c_ in cells]
check(f"3x-1 mod 5: the SAME folded pentagon with cells negated {cm}: the statement is sign-blind",
      Pm * ind(cm[0]) == ind(cm[1]) and Pm * ind(cm[1]) == 2 * ind(cm[0]) + ind(cm[2]) and Pm * ind(cm[2]) == ind(cm[2]) + ind(cm[1]))
check("3x-1 and 3x+1 mod 5 have the same characteristic polynomial", Pm.charpoly(x) == P5.charpoly(x))
# integers: T_-(n) = (3n-1)/2; start n = -1 = 4 (mod 5)
okm = True
for k in range(0, 13):
    counts = [0] * 5
    for n in range(4, 5 * 2 ** k, 5):
        m = n
        for _ in range(k):
            m = T(m, 3, -1)
        counts[m % 5] += 1
    w = pent_law(k)
    okm &= counts == [int(w[beta[(-r) % 5]] * 2 ** k) for r in range(5)]
check("3x-1 on integers: T_-^k(n) mod 5 for n = 4 (mod 5) has the same pentagon law (k = 0..12)", okm)
for c in (1, 2, 3, 4, 5, 7, 10):
    try:
        ec, oc = branches(5, 3, c)
    except AssertionError:
        say(f"   3x+{c} mod 5: branches not bijective")
        continue
    cpc = sp.factor(push_matrix(5, ec, oc).charpoly(x).as_expr())
    say(f"   3x+{c} mod 5: charpoly(2K) = {cpc}   (same as 3x+1: {sp.expand(cpc - cp) == 0})")
say("   so 'the same chain for every 3x+c' needs c prime to the modulus: for 5 | c both branches fix 0 and the kernel is different.")
for q in (5, 7):
    hits = []
    for N in range(3, 62):
        if gcd(N, 2 * q) != 1:
            continue
        eq, oq = branches(N, q, 1)
        fac = sp.factor_list(push_matrix(N, eq, oq).charpoly(x).as_expr())[1]
        for f, mult in fac:
            pf = sp.Poly(f, x)
            if pf.degree() >= 2:
                rts = pf.nroots(n=30, maxsteps=200)
                if all(abs(sp.im(r)) < 1e-20 and abs(sp.re(r)) <= 2 + 1e-20 for r in rts):
                    hits.append((N, str(f)))
    say(f"   {q}x+1, N <= 61 prime to {2 * q}: irreducible factors of degree >= 2 with all roots real in [-2, 2] (= irrational cosines by Kronecker): {hits}")
e7, o7 = branches(7, 5, 1)
say(f"   5x+1 mod 7: odd branch o = {o7} is an involution: {all(o7[o7[t]] == t for t in range(7))};  charpoly(2K) = {sp.factor(push_matrix(7, e7, o7).charpoly(x).as_expr())}")
e3, o3 = branches(3, 5, 1)
say(f"   5x+1 mod 3: e = {e3} (reflection), o = {o3} (translation);  charpoly(2K) = {sp.factor(push_matrix(3, e3, o3).charpoly(x).as_expr())}")

# ------------------------------------------------------------------ 6. geometry
say("\n=== 6. the geometric constants ===")
check("cos 36 = phi/2 = apothem of the pentagon of circumradius 1; diagonal/side = phi = 2cos 36",
      sp.simplify(sp.cos(sp.pi / 5) - (1 + sp.sqrt(5)) / 4) == 0
      and sp.simplify(sp.sin(2 * sp.pi / 5) / sp.sin(sp.pi / 5) - (1 + sp.sqrt(5)) / 2) == 0)

say(f"\n{len(FAIL)} failures" + (": " + "; ".join(FAIL) if FAIL else ""))
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
sys.exit(1 if FAIL else 0)
