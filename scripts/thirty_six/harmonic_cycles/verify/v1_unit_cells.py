"""Skeptic check 1: Q1.1 (unit cells, transposition lemma, one-even-step theorem).

Independent code path: nothing is imported from hc_common.  Word constants are obtained by
COMPOSING affine maps with Fractions (not from the closed formula), fixed points are solved
from the composed map, and every integer fixed point is confirmed by plain iteration.
Maps tested: 3x+1, 3x-1 (mirror), 5x+1, 5x-1, 7x+1 (cousins).

Convention: shortcut map T_{q,c}(n) = n/2 (n even), (q n + c)/2 (n odd), on all of Z.
A word w has k = len(w) shortcut steps, s = number of odd steps.  D = 2^k - q^s.
Output: v1_unit_cells.log
"""
import os
import sys
from fractions import Fraction
from itertools import combinations, product
from math import gcd, isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v1_unit_cells.log"), "w", encoding="utf-8")


def out(*a):
    line = " ".join(str(x) for x in a)
    print(line)
    LOG.write(line + "\n")


def step(n, q=3, c=1):
    return n // 2 if n % 2 == 0 else (q * n + c) // 2


def affine_of_word(w, q=3, c=1):
    """Return (A, B) with T_w(x) = A x + B, by composing the two branches as Fractions."""
    A, B = Fraction(1), Fraction(0)
    for b in w:
        if b:
            A, B = A * q / 2, (B * q + c) / 2
        else:
            A, B = A / 2, B / 2
    return A, B


def fixed_point(w, q=3, c=1):
    A, B = affine_of_word(w, q, c)
    return B / (1 - A)


def all_words(k, s):
    for pos in combinations(range(k), s):
        w = [0] * k
        for p in pos:
            w[p] = 1
        yield tuple(w)


# ------------------------------------------------------------------ 1
out("=" * 78)
out("1. Theorem 1 over a wider range: |2^k - 3^s| = 1, k <= 20000 (their range: k <= 3000)")
out("=" * 78)
sol = []
p3 = 1
s = 0
for k in range(0, 20001):
    two = 1 << k
    # advance s so that 3^s is the largest power of 3 <= 2*two
    while p3 * 3 <= 2 * two:
        p3 *= 3
        s += 1
    t, ss = p3, s
    # test the (at most three) powers of 3 nearest to 2^k
    for _ in range(3):
        if abs(two - t) == 1:
            sol.append((k, ss, two - t))
        if ss == 0:
            break
        t //= 3
        ss -= 1
sol = sorted(set(sol))
out("solutions (k, s, D) with k >= 0:", sol)
assert [x for x in sol if x[0] >= 1] == [(1, 0, 1), (1, 1, -1), (2, 1, 1), (3, 2, -1)]
out("  note k = 0: 2^0 - 3^0 = 0, no solution; all four solutions have s <= k.")

# 3-smooth triangular numbers by direct factoring (does NOT use the coprime-pair argument)
out("")


def smooth3(m):
    if m <= 0:
        return False
    while m % 2 == 0:
        m //= 2
    while m % 3 == 0:
        m //= 3
    return m == 1


N = 3_000_000
hits = [(n, n * (n + 1) // 2) for n in range(-N, N + 1) if smooth3(n * (n + 1) // 2)]
out(f"n in [-{N}, {N}] with T_n = n(n+1)/2 3-smooth (direct factoring):")
out("  ", hits)
assert [h for h in hits if h[0] >= 1] == [(1, 1), (2, 3), (3, 6), (8, 36)]
out("  edge cases: T_0 = T_(-1) = 0 is not 3-smooth; T_(-n-1) = T_n, so the negative list mirrors")
out("  the positive one (n = -2, -3, -4, -9).  36 = T_8 = T_(-9).")

# ------------------------------------------------------------------ 2
out("")
out("=" * 78)
out("2. Lemma 3 (adjacent transposition) and Theorem 4, exhaustive k <= 15, for")
out("   3x+1, 3x-1, 5x+1, 5x-1, 7x+1.  Also the CYCLIC transposition (positions k-1, 0),")
out("   which the README's lemma does not cover.")
out("=" * 78)
for (q, c) in ((3, 1), (3, -1), (5, 1), (5, -1), (7, 1)):
    KMAX = 15 if q == 3 else 13
    n_swaps = 0
    bad_lemma = 0
    adj_int_outside = 0
    cyc_int_outside = 0
    all_int_cells = []
    prim_cycles = {}
    for k in range(1, KMAX + 1):
        for s in range(0, k + 1):
            D = 2 ** k - q ** s
            if D == 0:
                continue
            n_w = n_int = 0
            ints = set()
            consts = {}
            for w in all_words(k, s):
                A, B = affine_of_word(w, q, c)
                # T_w(x) = (q^s x + c*C)/2^k  ->  c*C = B * 2^k
                cC = B * 2 ** k
                assert cC.denominator == 1 and A == Fraction(q ** s, 2 ** k)
                consts[w] = int(cC)
                n_w += 1
                if int(cC) % D == 0:
                    n_int += 1
                    ints.add(w)
                    x = int(cC) // D
                    # confirm by plain iteration that x is periodic with parity word w
                    y = x
                    for b in w:
                        assert (y % 2) == b, (q, c, w, x)
                        y = step(y, q, c)
                    assert y == x
                    if all(w[i:] + w[:i] != w for i in range(1, k)):
                        orb = []
                        y = x
                        for _ in range(k):
                            orb.append(y)
                            y = step(y, q, c)
                        prim_cycles[frozenset(orb)] = (k, s, D, min(orb, key=abs))
            if n_int == n_w:
                all_int_cells.append((k, s, D, n_w))
            # transpositions
            for w, Cw in consts.items():
                for j in range(k - 1):
                    if w[j] == 1 and w[j + 1] == 0:
                        w2 = list(w)
                        w2[j], w2[j + 1] = 0, 1
                        w2 = tuple(w2)
                        t = sum(w[j + 2:])
                        n_swaps += 1
                        if consts[w2] - Cw != c * q ** t * 2 ** j:
                            bad_lemma += 1
                        if abs(D) != 1 and w in ints and w2 in ints:
                            adj_int_outside += 1
                if k >= 2 and w[k - 1] != w[0]:
                    w2 = list(w)
                    w2[0], w2[k - 1] = w[k - 1], w[0]
                    if abs(D) != 1 and w in ints and tuple(w2) in ints:
                        cyc_int_outside += 1
    nontriv = [c_ for c_ in all_int_cells if c_[3] > 1 or c_[0] == 1]
    out(f" map {q}x{c:+d}, k <= {KMAX}: {n_swaps} adjacent swaps, lemma failures {bad_lemma};")
    out(f"    adjacent integer pairs outside unit cells: {adj_int_outside}; cyclic-swap integer pairs "
        f"outside unit cells: {cyc_int_outside}")
    out(f"    all-integer cells with >1 word or k = 1 (k,s,D,#words): {nontriv}")
    out(f"    primitive integer cycles (k,s,D,min|n|): {sorted(prim_cycles.values())}")
    assert bad_lemma == 0 and adj_int_outside == 0
    assert all(abs(c_[2]) == 1 for c_ in nontriv)

# ------------------------------------------------------------------ 3
out("")
out("=" * 78)
out("3. Theorem 5 (word 1^a 0): wider range and a direct search that uses no word algebra")
out("=" * 78)
ok_a = []
p3 = 1
for a in range(0, 6001):
    D = (1 << (a + 1)) - p3
    C = p3 - (1 << a)
    if C % D == 0:
        ok_a.append((a, D, C // D))
    p3 *= 3
out("a <= 6000 with (2^(a+1) - 3^a) | (3^a - 2^a):  (a, D, x) =", ok_a)
assert [t[0] for t in ok_a] == [0, 1, 2]


def is_tri(Nn):
    r = isqrt(8 * Nn + 1)
    return r * r == 8 * Nn + 1


tri6 = [a for a in range(0, 3001) if is_tri(6 ** a)]
out("a <= 3000 with 6^a triangular:", tri6)
assert tri6 == [0, 1, 2]

out("")
out("direct search: every cycle with EXACTLY ONE EVEN ELEMENT meeting |n| <= 200000")
for (q, c) in ((3, 1), (3, -1), (5, 1), (5, -1), (7, 1), (7, -1), (9, 1)):
    found = set()
    B = 200000
    for n0 in range(-B, B + 1, 2):       # the even element
        n = step(n0, q, c)
        steps = 1
        while n % 2 and abs(n) < 10 ** 30 and steps < 400:
            n = step(n, q, c)
            steps += 1
        if n == n0:
            found.add((n0, steps))
    desc = []
    for n0, k in sorted(found, key=lambda t: abs(t[0])):
        orb = [n0]
        for _ in range(k - 1):
            orb.append(step(orb[-1], q, c))
        desc.append(orb)
    out(f"  {q}x{c:+d}: {desc}")
out("  -> 3x+1: {0}, {2,1}, {-10,-5,-7};  3x-1: mirror images;  5x+1: {0}, {-2,-1};  7x+1, 9x+1: only {0}.")
out("  The statement is sign-symmetric (3x-1 gives the negated cycles) and separates q = 3 from q >= 5")
out("  only by the arithmetic of |2^(a+1) - q^a| = 1.")

# v-coordinates, including the general identity v*v' = T_v at EVERY even step
out("")
out("v = n + 1:  an even step sends v -> v' = (v+1)/2, so v*v' = T_v at every even step of every")
out("orbit (not only in cycles).  Check on 10^5 random even n, both signs:")
import random
random.seed(36)
for _ in range(100000):
    n = 2 * random.randint(-10 ** 12, 10 ** 12)
    v, v2 = n + 1, n // 2 + 1
    assert v * v2 == v * (v + 1) // 2
out("  OK.  So 'v_bot * v_top = T_(v_top)' is automatic; the content of Theorem 5 is v_top = (3/2)^a v_bot")
out("  with v_bot = +-2^a.")
for cyc in ([0], [1, 2], [-5, -7, -10], [-17, -25, -37, -55, -82, -41, -61, -91, -136, -68, -34]):
    vs = [n + 1 for n in cyc]
    ev = [(vs[i], vs[(i + 1) % len(vs)]) for i in range(len(cyc)) if cyc[i] % 2 == 0]
    out(f"  cycle {cyc}")
    out(f"     v = {vs};  even steps (v, v', v*v' = T_v): "
        f"{[(a, b, a * b) for a, b in ev]}")

LOG.close()
