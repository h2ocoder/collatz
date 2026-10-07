"""Skeptic check 2: polygonal trichotomy, CRS criterion from k = 1, reflections, cubic figurate families.

Independent of common.py / q22: every statement is tested by explicit enumeration of fibres with
Python integers (no numpy bincount), including s <= 2, negative s and k = 1, 2 which q22 skipped.

Run: C:/repos/collatz/.venv/Scripts/python.exe -X utf8 v2_polygonal_and_cubic.py
"""
import json
import os
import random
import time
from fractions import Fraction
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v2_polygonal_and_cubic.log"), "w", encoding="utf-8")
RES = {}
T0 = time.time()


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


def v2(n):
    n = abs(n)
    assert n
    return (n & -n).bit_length() - 1


def P(s, n):
    return ((s - 2) * n * n - (s - 4) * n) // 2


A023105 = [1, 2, 2, 3, 4, 7, 12, 23, 44, 87, 172, 343, 684, 1367, 2732, 5463, 10924]

# ---------------------------------------------------------------------------------------------
out("=" * 100)
out("1. Polygonal trichotomy by v2(s-2), s = -7 .. 40 (s = 2 is the identity), k = 1 .. 11")
out("=" * 100)
bad = []
first_fail = {}
for s in range(-7, 41):
    a = s - 2
    typ = "isometry" if a == 0 or v2(a) >= 2 else ("free fold" if v2(a) == 0 else "ramified fold")
    for k in range(1, 12):
        M, M2 = 1 << k, 1 << (k + 1)
        if typ == "free fold":
            c = (s - 4) * pow(a, -1, M2) % M2
            fib = {}
            for n in range(M2):
                fib.setdefault(P(s, n) % M, []).append(n)
            ok = len(fib) == M and all(len(v) == 2 and (v[0] + v[1]) % M2 == c and (v[0] - v[1]) % 2 == 1
                                       for v in fib.values())
            crs = len({P(s, n) % M for n in range(M)}) == M
            if not crs and s not in first_fail:
                first_fail[s] = k
            ok &= crs == ((s - 3) % M == 0)
        elif typ == "ramified fold":
            b = a // 2
            cc = ((1 - b) // 2) * pow(b, -1, M) % M
            vals = [P(s, n) % M for n in range(M)]
            ok = all(vals[n] == (b * (n + cc) ** 2 - b * cc * cc) % M for n in range(M))
            ok &= len(set(vals)) == A023105[k]
            ok &= all(vals[n] % 4 == 1 for n in range(1, M, 2)) if k >= 2 else True
            ok &= all(vals[n] % 2 == 0 for n in range(0, M, 2))
        else:
            vals = [P(s, n) % M for n in range(M)]
            ok = len(set(vals)) == M
            if k <= 8:
                ok &= all(v2(P(s, x) - P(s, y)) == v2(x - y) for x in range(M) for y in range(x))
        if not ok:
            bad.append((s, k, typ))
out("  every (s, k) agrees with: s odd -> free fold with fibres {x, (s-4)/(s-2) - x};")
out("  s = 0 mod 4 -> b(n+c)^2 - bc^2, #values = A023105(k), odd values 1 mod 4;  s = 2 mod 4 -> isometry:", not bad)
if bad:
    out("  FAILURES:", bad[:20])
RES["trichotomy_ok"] = not bad

out("")
out("  CRS criterion for odd s (first 2^k terms a CRS mod 2^k  <=>  s = 3 mod 2^k), tested from k = 1.")
out("  First failing k should be v2(s-3) + 1:")
okff = True
for s in sorted(first_fail):
    pred = v2(s - 3) + 1
    okff &= first_fail[s] == pred
line = ", ".join(f"s={s}: k={first_fail[s]}" for s in (5, 7, 9, 11, 13, 19, 27, 35) if s in first_fail)
out("    ", line, "   all equal v2(s-3)+1:", okff)
out("     pentagonal numbers 0, 1, 5, 12 mod 4 =", [P(5, n) % 4 for n in range(4)],
    " -> s = 5 already fails at k = 2 (the README said k = 3; q22 only started at k = 3)")
RES["crs_first_fail"] = {str(s): k for s, k in first_fail.items()}
RES["crs_first_fail_formula_ok"] = okff

# ---------------------------------------------------------------------------------------------
out("")
out("=" * 100)
out("2. Rules q x + d (q, d odd, gcd = 1) whose centre reflection x -> -2d/(q-1) - x is integral: (q-1) | 2d")
out("   The README said this is 'where triangular is tied to the multiplier 3'.  Counter-examples with q != 3:")
out("=" * 100)
hits = []
for q in range(3, 40, 2):
    for d in range(-15, 16, 2):
        if gcd(q, abs(d)) != 1:
            continue
        if (2 * d) % (q - 1) == 0:
            c = -2 * d // (q - 1)
            comm = all(c - (q * x + d) == q * (c - x) + d for x in range(-200, 200))
            hits.append((q, d, c, comm))
nonq3 = [(q, d, c) for q, d, c, comm in hits if q != 3]
out("  all (q, d) found with q <= 39, |d| <= 15:  q = 3 with every odd d not divisible by 3, and:", nonq3)
out("  every one of them commutes with its reflection (checked |x| < 200):", all(h[3] for h in hits))
out("  7x+3: centre -3/6 = -1/2, so NOT(x) = -1-x commutes with x -> 7x+3 exactly as with x -> 3x+1:",
    all(-1 - (7 * x + 3) == 7 * (-1 - x) + 3 for x in range(-1000, 1000)))
out("  general solution: q = 2d' + 1 with d' | d (so q = 3 mod 4);  for |d| = 1 this forces q = 3.")
RES["integral_reflection_rules_q_ne_3"] = nonq3

# ---------------------------------------------------------------------------------------------
out("")
out("=" * 100)
out("3. Cubic figurate families (the README had these as 'computed, no proofs').  Proof sketches in README;")
out("   here: exhaustive fibre structure mod 2^k, k = 2 .. 13, period 2^(k+1)")
out("=" * 100)


def pyr(n):
    return n * (n + 1) * (2 * n + 1) // 6


def tet(n):
    return n * (n + 1) * (n + 2) // 6


def octa(n):
    return n * (2 * n * n + 1) // 3


def stella(n):
    return n * (2 * n * n - 1)


ok_pyr = ok_tet = ok_oct = ok_st = True
for k in range(2, 14):
    M, M2 = 1 << k, 1 << (k + 1)
    ev = sorted(pyr(n) % M for n in range(0, M2, 2))
    od = sorted(pyr(n) % M for n in range(1, M2, 2))
    ok_pyr &= ev == list(range(M)) and od == list(range(M))
    todd = sorted(tet(n) % M for n in range(1, M2, 2))
    t0 = sorted(tet(n) % M for n in range(0, M2, 4))
    t2 = sorted(tet(n) % M for n in range(2, M2, 4))
    four = sorted(list(range(0, M, 4)) * 2)
    ok_tet &= todd == list(range(M)) and t0 == four and t2 == four
    ok_oct &= sorted(octa(n) % M for n in range(M)) == list(range(M))
    ok_st &= sorted(stella(n) % M for n in range(M)) == list(range(M))
out("  square pyramidal: every residue mod 2^k has exactly one even and one odd preimage mod 2^(k+1):", ok_pyr)
out("  tetrahedral: odd n -> every residue once; n = 0 mod 4 and n = 2 mod 4 -> each residue = 0 mod 4 twice")
out("               (so multiplicity 5 on 4Z, 1 elsewhere):", ok_tet)
out("  octahedral, stella octangula: permutations of Z/2^k:", ok_oct, ok_st)
random.seed(20261006)
law = dict(pyr_same=True, tet_odd=True, tet_even_mod4=True, oct=True, stella=True, pyr_odd_symmetry=True)
for _ in range(200000):
    x = random.getrandbits(70) - (1 << 69)
    y = random.getrandbits(70) - (1 << 69)
    if x == y:
        continue
    if (x - y) % 2 == 0:
        law["pyr_same"] &= v2(pyr(x) - pyr(y)) == v2(x - y) - 1
    xo, yo = x | 1, y | 1
    if xo != yo:
        law["tet_odd"] &= v2(tet(xo) - tet(yo)) == v2(xo - yo) - 1
    xe, ye = (x >> 2 << 2), (y >> 2 << 2)
    if xe != ye:
        law["tet_even_mod4"] &= v2(tet(xe) - tet(ye)) == v2(xe - ye) and v2(tet(xe + 2) - tet(ye + 2)) == v2(xe - ye)
        law["tet_even_mod4"] &= tet(xe) % 4 == 0 and tet(xe + 2) % 4 == 0
    law["oct"] &= v2(octa(x) - octa(y)) == v2(x - y)
    law["stella"] &= v2(stella(x) - stella(y)) == v2(x - y)
    law["pyr_odd_symmetry"] &= pyr(-1 - x) == -pyr(x)
out("  valuation laws on 200000 random signed 70-bit pairs:")
out("     pyramidal, x = y mod 2:        v2(f(x)-f(y)) = v2(x-y) - 1 :", law["pyr_same"])
out("     tetrahedral, x, y odd:         v2(f(x)-f(y)) = v2(x-y) - 1 :", law["tet_odd"])
out("     tetrahedral, x = y mod 4 even: v2(f(x)-f(y)) = v2(x-y), value in 4Z :", law["tet_even_mod4"])
out("     octahedral, stella octangula:  v2(f(x)-f(y)) = v2(x-y) :", law["oct"], law["stella"])
out("     pyramidal is ODD under NOT:    f(-1-n) = -f(n)  (no fold along NOT) :", law["pyr_odd_symmetry"])
RES["cubic"] = dict(pyr=ok_pyr, tet=ok_tet, oct=ok_oct, stella=ok_st, laws=law)

# ---------------------------------------------------------------------------------------------
out("")
out("=" * 100)
out("4. The 'matched' families F_q(n) = n((q-2)n+1)/2 of the first-run law: 2-adic type")
out("=" * 100)
ok_f = True
for q in (3, 5, 7, 9, 11, 13):
    a = q - 2
    for k in range(1, 11):
        M, M2 = 1 << k, 1 << (k + 1)
        c = (-pow(a, -1, M2)) % M2
        fib = {}
        for n in range(M2):
            fib.setdefault(n * (a * n + 1) // 2 % M, []).append(n)
        ok_f &= len(fib) == M and all(len(v) == 2 and (v[0] + v[1]) % M2 == c for v in fib.values())
out("  for q = 3, 5, ..., 13 and k = 1..10: F_q is a free 2-to-1 fold with fibres {x, -1/(q-2) - x}:", ok_f)
out("  (F_q(x) - F_q(y) = (x-y)((q-2)(x+y)+1)/2; same proof as Theorem 3 case 1.  Polygonal only for q = 3, 5.)")
RES["matched_families_fold"] = ok_f

out("")
out(f"done in {time.time() - T0:.1f} s")
with open(os.path.join(HERE, "v2_polygonal_and_cubic.json"), "w", encoding="utf-8") as fh:
    json.dump(RES, fh, indent=1, default=str)
LOG.close()
