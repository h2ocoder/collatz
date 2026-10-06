r"""Skeptic check of Q4.4-a/b/c, and a CORRECTION to Q4.4-a item 3.

README (before this pass) said: 'each cubic step needs the auxiliary sqrt(-p/3), which in general
lies outside the cyclotomic field ... a construction uses exactly two trisections and more than
one square root'.  That is not forced.

PROPOSITION (classical; Kummer theory over K(omega), or Conner-Perlis: the trace form of an
odd-degree Galois extension is the unit form).  Let K < K' be real fields with K'/K cyclic of
degree 3, Gal = <tau>.  For y in K' \ K put
        R  = y + w tau(y) + w^2 tau^2(y),   R~ = y + w^2 tau(y) + w tau^2(y)     (w = e^(2 pi i/3)),
        N  = R R~  (in K, > 0),             x  = (R^2 + R~^2)/N.
Then x lies in K', generates K' over K, and x^3 - 3x - c = 0 with c = (R^6 + R~^6)/N^3 in K,
|c| < 2.  So x = 2 cos(psi/3) with 2 cos(psi) = c IN K:  every cubic step is the trisection of
an angle whose cosine already lies in the field below.  No auxiliary square root is needed to
reach the NUMBER cos(2 pi/n); Gleason's sqrt(7) for the heptagon disappears when the doubled
angle is trisected (cos psi = 13/14 instead of 1/(2 sqrt 7)).
(Proof: tau R = w^2 R, tau R~ = w R~, so N, R^6 + R~^6 are tau-invariant and real; alpha = R/R~
has |alpha| = 1, tau(alpha) = w alpha, x = alpha + 1/alpha, x^3 - 3x = alpha^3 + alpha^-3.
x in K would force alpha^3 = +-1, i.e. R^3 in K or sqrt(-3) K, impossible for a Kummer
generator of the abelian extension K'(w)/K.)

Consequence for phi(n) = 2^a 3^b:  Q(cos 2pi/n) is reached from Q by exactly a - 1 square
roots and b such trisections; for phi(n) = 36: ONE square root and TWO trisections, as the
seed sentence said.

This script
  1. recomputes (Z/n)* and (Z/n)*/{+-1} for the eight n by counting square and cube roots of 1,
  2. checks the primary-decomposition rule for all n <= 30000 with 3-smooth phi(n) (different
     invariants than the researcher's), and which group types of order 36 occur,
  3. verifies the proposition EXACTLY (integer arithmetic in Z[zeta_p]) for the cubic subfields
     of Q(zeta_p), p = 7, 13, 19, 37, 73, 97, 109: c = +-(L^2 - 27 M^2)/(2p) with 4p = L^2 + 27 M^2,
  4. verifies it numerically (50 digits) for the NESTED second cubic step of p = 19, 37 and n = 27,
  5. assembles 'one square root + two trisections' for each of the eight polygons numerically,
  6. recomputes A100982 by brute force over residues and compares with A(a,b).

Run:  python -X utf8 v4_polygons.py
"""
from __future__ import annotations

import json
import os
import time
from fractions import Fraction
from math import gcd, isqrt

import mpmath as mp
from sympy import factorint, primitive_root, totient

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
LOG = open(os.path.join(HERE, "v4_polygons.log"), "w", encoding="utf-8")
mp.mp.dps = 50


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")


# ----------------------------------------------------------------------------- groups
def roots_of_unity_counts(n, real=False):
    """#{g in (Z/n)* : g^e = 1} for e = 2,4,8,..., and 3,9,27,... (mod +-1 if real)."""
    units = [g for g in range(1, n) if gcd(g, n) == 1]
    if real:
        units = [g for g in units if g <= n - g]
    res = {}
    for p in (2, 3):
        e, lst = p, []
        while True:
            if real:
                c = sum(1 for g in units if pow(g, e, n) in (1, n - 1))
            else:
                c = sum(1 for g in units if pow(g, e, n) == 1)
            if lst and c == lst[-1]:
                break
            lst.append(c)
            e *= p
        res[p] = lst
    return res


def predicted_counts(n):
    """the same counts from the standard structure theorem applied to the factorisation of n."""
    cyc = []                      # orders of cyclic factors
    for p, e in factorint(n).items():
        if p == 2:
            if e == 2:
                cyc.append(2)
            elif e >= 3:
                cyc += [2, 2 ** (e - 2)]
        else:
            cyc.append(p ** (e - 1) * (p - 1))
    res = {}
    for p in (2, 3):
        e, lst = p, []
        while True:
            c = 1
            for m in cyc:
                c *= gcd(m, e)
            if lst and c == lst[-1]:
                break
            lst.append(c)
            e *= p
        res[p] = lst
    return res, cyc


def smooth3(m):
    while m % 2 == 0:
        m //= 2
    while m % 3 == 0:
        m //= 3
    return m == 1


# ----------------------------------------------------------------------------- exact Z[zeta_p]
def cmul(u, v, p):
    w = [0] * p
    for i, a in enumerate(u):
        if a:
            for j, b in enumerate(v):
                if b:
                    w[(i + j) % p] += a * b
    return w


def cnorm(u):
    """canonical form modulo 1 + zeta + ... + zeta^(p-1) = 0: subtract the coefficient of zeta^0."""
    return [a - u[0] for a in u]


def is_rational(u):
    # u = c * 1 modulo the relation  <=>  coefficients (c + t, t, t, ..., t)
    return all(a == u[1] for a in u[1:])


def rational_value(u):
    """if u = c * 1 (mod the relation): coefficients (c + t, t, t, ..., t) -> c."""
    assert is_rational(u)
    return u[0] - u[1]


def main():
    t0 = time.time()
    out("1. THE EIGHT n WITH phi(n) = 36: square and cube roots of 1")
    out("     n   #{g^2=1} #{g^3=1} #{g^9=1}   (Z/n)*               #{g^2=+-1} #{g^3=+-1} #{g^9=+-1}  (Z/n)*/{+-1}")
    for n in (37, 57, 63, 74, 76, 108, 114, 126):
        assert totient(n) == 36
        c = roots_of_unity_counts(n)
        r = roots_of_unity_counts(n, real=True)
        sq, cu, cu9 = c[2][0], c[3][0], c[3][-1]
        two = "C4" if sq == 2 else "C2 x C2"
        three = "C9" if cu == 3 else "C3 x C3"
        rsq, rcu, rcu9 = r[2][0], r[3][0], r[3][-1]
        rthree = "C9" if rcu == 3 else "C3 x C3"
        out(f"   {n:>4d}      {sq}        {cu}        {cu9}       {two + ' x ' + three:<20s}     {rsq}          {rcu}          {rcu9}       C2 x {rthree}")
        pc, cyc = predicted_counts(n)
        assert pc == c, (n, pc, c)
    out("   C4 x C3 x C3 would need 2 square roots of 1 and 9 cube roots: none of the eight has that.")

    out("\n2. STRUCTURE RULE for every n <= 30000 with 3-smooth phi(n) (counts of 2-power and 3-power roots of 1)")
    cnt = 0
    for n in range(3, 30001):
        if smooth3(int(totient(n))):
            pc, _ = predicted_counts(n)
            assert pc == roots_of_unity_counts(n), n
            cnt += 1
    out(f"   n checked: {cnt}; mismatches 0   [{time.time() - t0:.0f} s]")

    out("\n3. CUBIC SUBFIELD OF Q(zeta_p): generator x with x^3 - 3x - c = 0, c RATIONAL (exact arithmetic)")
    out("     p    (a,b): a^2-ab+b^2=p     c = N(x)        (L, M): 4p = L^2 + 27M^2   c = +-(L^2-27M^2)/(2p)   3(4-c^2) square   cos(psi) = c/2")
    for p in (7, 13, 19, 37, 73, 97, 109):
        g = int(primitive_root(p))
        # cubic periods eta_i = sum_{t} zeta^(g^(3t+i))
        eta = []
        for i in range(3):
            v = [0] * p
            for t in range((p - 1) // 3):
                v[pow(g, 3 * t + i, p)] += 1
            eta.append(v)
        U = [[3 * a for a in e] for e in eta]
        for e in U:
            e[0] += 1                     # U_i = 3 eta_i + 1 = 3 (eta_i + 1/3): trace zero
        LM = next((L, M) for M in range(1, 40) for L in range(1, 400) if L * L + 27 * M * M == 4 * p)
        L, M = LM
        target = Fraction(L * L - 27 * M * M, 2 * p)
        # all lattice vectors a U_0 + b U_1 of norm a^2 - ab + b^2 = p give Tr(x^2) = 6; they fall into two
        # classes (beta and its conjugate in Z[omega]) with c = +-target and c = +-(target^2 - 2) (the doubled angle)
        cvals = {}
        for a in range(-25, 26):
            for b in range(-25, 26):
                if a * a - a * b + b * b != p:
                    continue
                X = [a * U[0][t] + b * U[1][t] for t in range(p)]         # x = X / p
                X3 = cmul(cmul(X, X, p), X, p)
                rest = [X3[t] - 3 * p * p * X[t] for t in range(p)]       # X^3 - 3 p^2 X = c p^3
                assert is_rational(rest), p
                cc = Fraction(rational_value(rest), p ** 3)
                cvals.setdefault(abs(cc), (a, b, X, cc))
        assert abs(target) in cvals, (p, sorted(cvals))
        assert set(cvals) == {abs(target), abs(target * target - 2)}, (p, sorted(cvals))
        a, b, X, c = cvals[abs(target)]
        ab = (a, b)
        sq = 3 * (4 - c * c)
        is_sq = isqrt(sq.numerator) ** 2 == sq.numerator and isqrt(sq.denominator) ** 2 == sq.denominator
        out(f"   {p:>4d}    {str(ab):<10s}             {str(c):<10s}      {str(LM):<10s}                 {str(abs(c) == abs(target)):<5s}"
            f"                   {str(is_sq):<5s}           {c / 2}")
        assert abs(c) == abs(target) and is_sq and abs(c) < 2
        # numeric sanity: X/p is a real number equal to 2 cos((psi + 2 pi m)/3)
        z = mp.e ** (2j * mp.pi / p)
        xnum = sum(X[t] * z ** t for t in range(p)).real / p
        psi = mp.acos(mp.mpf(c.numerator) / c.denominator / 2)
        assert min(abs(xnum - 2 * mp.cos((psi + 2 * mp.pi * m) / 3)) for m in range(3)) < mp.mpf(10) ** -40
    out("   heptagon: 2 cos(psi) = +-13/7, i.e. the cubic field of the 7-gon is Q(cos(psi/3)) with cos(psi) = 13/14 (sign: x -> -x):")
    out("   a trisection of an angle with RATIONAL cosine; no sqrt(7).  (Gleason: cos(psi) = 1/(2 sqrt 7); 2 psi_G = psi.)")
    psi7 = mp.acos(mp.mpf(13) / 14)
    x0, x1 = 2 * mp.cos(psi7 / 3), 2 * mp.cos((psi7 + 2 * mp.pi) / 3)
    err = abs(2 * mp.cos(2 * mp.pi / 7) - (-mp.mpf(1) / 3 + x0 + x1 / 3))
    out(f"   explicit: 2cos(2pi/7) = -1/3 + x0 + x1/3, x_m = 2cos((psi + 2 pi m)/3), cos(psi) = 13/14;  error {mp.nstr(err, 3)}")
    assert err < mp.mpf(10) ** -40
    err10 = abs(mp.cos(mp.pi / 5) - (1 + mp.sqrt(5)) / 4)
    t36 = 2 * mp.cos(mp.pi / 18)
    err36 = abs(t36 ** 3 - 3 * t36 - mp.sqrt(3))
    out(f"   small cases: decagon (2,0): cos 36 deg = (1 + sqrt 5)/4 = golden ratio / 2, error {mp.nstr(err10, 3)};"
        f"  36-gon (2,1): (2cos 10 deg)^3 - 3(2cos 10 deg) = sqrt 3, error {mp.nstr(err36, 3)}")
    assert err10 < mp.mpf(10) ** -40 and err36 < mp.mpf(10) ** -40

    out("\n4. NESTED SECOND CUBIC STEP K3 < K9 (the 'cyclic of order 9' case), 50-digit numerics")
    w = mp.e ** (2j * mp.pi / 3)

    def nested(n_mod, period_exps, sigma_mult, label):
        """y = sum zeta^e over period_exps; sigma: zeta -> zeta^sigma_mult has order 9 on K9; tau = sigma^3."""
        z = mp.e ** (2j * mp.pi / n_mod)
        def conj(k):
            mlt = pow(sigma_mult, k, n_mod)
            return sum(z ** (e * mlt % n_mod) for e in period_exps).real
        ys = [conj(k) for k in range(9)]           # sigma^k(y)
        def xc(k):                                 # x and c built from sigma^k(y) (i.e. sigma^k applied)
            y0, y1, y2 = ys[k % 9], ys[(k + 3) % 9], ys[(k + 6) % 9]
            R = y0 + w * y1 + w * w * y2
            Rb = y0 + w * w * y1 + w * y2
            Nn = (R * Rb).real
            x = ((R * R + Rb * Rb) / Nn).real
            c = ((R ** 6 + Rb ** 6) / Nn ** 3).real
            return x, c
        x0, c0 = xc(0)
        x3, c3 = xc(3)
        x6, c6 = xc(6)
        assert abs(c0 - c3) < mp.mpf(10) ** -40 and abs(c0 - c6) < mp.mpf(10) ** -40     # c fixed by tau: c in K3
        assert abs(x0 ** 3 - 3 * x0 - c0) < mp.mpf(10) ** -40
        assert abs(x0 - x3) > mp.mpf(10) ** -5                                           # x not in K3
        cs = [xc(k)[1] for k in range(3)]          # the three Q-conjugates of c (sigma permutes them)
        psi = mp.acos(c0 / 2)
        ok = min(abs(x0 - 2 * mp.cos((psi + 2 * mp.pi * m) / 3)) for m in range(3)) < mp.mpf(10) ** -40
        # minimal polynomial of c over Q: (t - c)(t - sigma c)(t - sigma^2 c)
        e1, e2, e3 = cs[0] + cs[1] + cs[2], cs[0] * cs[1] + cs[0] * cs[2] + cs[1] * cs[2], cs[0] * cs[1] * cs[2]
        out(f"   {label}: c = {mp.nstr(c0, 15)} (|c| < 2: {abs(c0) < 2}), tau-invariant: True, x = 2cos(psi/3 + 2 pi m/3): {ok}")
        out(f"       c is cubic over Q: t^3 - ({mp.nstr(e1, 12)}) t^2 + ({mp.nstr(e2, 12)}) t - ({mp.nstr(e3, 12)});"
            f"  e1, e2, e3 rational: {mp.identify(e1)}, {mp.identify(e2)}, {mp.identify(e3)}")
        return c0

    # p = 19: K9 = Q(zeta_19)^+, y = zeta + zeta^-1, sigma = multiplication by a primitive root
    nested(19, [1, 18], int(primitive_root(19)), "p = 19 (19-gon, also the 57-, 76-, 114-gon)")
    # p = 37: K9 = subfield of degree 9: period over the subgroup of order 4 = {g^(9t)}
    g = int(primitive_root(37))
    nested(37, [pow(g, 9 * t, 37) for t in range(4)], g, "p = 37 (37-gon, 74-gon)")
    # n = 27: K9 = Q(zeta_27)^+, y = zeta + zeta^-1, sigma = multiplication by 2 (order 18 mod 27, order 9 on K9)
    c27 = nested(27, [1, 26], 2, "n = 27 (27-gon inside the 108-gon)")
    out(f"       for n = 27 the direct choice is x = 2cos(2 pi/27), c = 2cos(2 pi/9) = {mp.nstr(2 * mp.cos(2 * mp.pi / 9), 15)} in K3 (triple-angle formula)")

    out("\n5. ONE SQUARE ROOT + TWO TRISECTIONS for each polygon with phi(n) = 36")
    out("   Q(cos 2pi/n) has degree 18 = 2 * 3^2; its tower is one quadratic and two cubic steps, each cubic step")
    out("   K(2cos(psi/3)) with 2cos(psi) in K (sections 3 and 4):")
    rows = [(37, "sqrt(37)", "c1 = 47/37 (rational);  c2 in K3 (nested, section 4)"),
            (74, "sqrt(37)", "same field as the 37-gon"),
            (57, "sqrt(57)", "c1 = 11/19 (rational);  c2 in K3 of the 19-gon (nested)"),
            (76, "sqrt(19)", "as the 19-gon"),
            (114, "sqrt(57)", "same field as the 57-gon"),
            (108, "sqrt(3)", "c1 = -1 (psi = 120 deg, the 9-gon);  c2 = 2cos(2pi/9) (nested, the 27-gon)"),
            (63, "sqrt(21)", "c1 = -13/7 (7-gon) and c2 = -1 (9-gon): two INDEPENDENT trisections of rational-cosine angles"),
            (126, "sqrt(21)", "same field as the 63-gon")]
    for n, sq, txt in rows:
        out(f"   {n:>4d}-gon:  {sq:<9s}  {txt}")
    # verify the quadratic subfields numerically: sqrt(D) is in Q(zeta_n)^+  <=>  D = conductor discriminant dividing n
    for n, D in ((37, 37), (57, 57), (76, 19), (108, 3), (63, 21)):
        # sqrt(D) in Q(zeta_m) real iff the quadratic field Q(sqrt D) has conductor dividing n (disc D or 4D)
        disc = D if D % 4 == 1 else 4 * D
        assert n % disc == 0, (n, D)
    out("   quadratic subfields: conductor of Q(sqrt D) divides n in each case (37 | 37, 57 | 57, 76 | 76, 12 | 108, 21 | 63).")

    out("\n6. A(a,b) AGAINST A100982 (brute force over residues mod 2^22, not a path count)")
    K = 22
    by_s = {}
    for r in range(1 << K):
        x, a3, sj = r, 1, 0
        for j in range(1, K + 1):
            if x & 1:
                x = (3 * x + 1) >> 1
                a3 *= 3
                sj += 1
            else:
                x >>= 1
            if a3 < (1 << j):
                if r < (1 << j):
                    by_s[sj] = by_s.get(sj, 0) + 1
                break
    mine = [by_s[s] for s in range(1, 14)]      # k(13) = 21 <= 22
    out("   dropping classes by s = 1..13:", mine)
    assert mine == [1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045]
    with open(os.path.join(PARENT, "q41_table.json"), encoding="utf-8") as f:
        A = json.load(f)["A"]
    import math
    seqs = {"diagonal": [A[a][a] for a in range(26)], "row b=1": [A[a][1] for a in range(26)],
            "column a=2": [A[2][b] for b in range(26)],
            "antidiag sums": [sum(A[a][n - a] for a in range(n + 1)) for n in range(26)],
            "staircase": [A[int(math.floor(s * math.log2(3))) + 1][s] for s in range(1, 21)]}
    tgt = [1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652]
    hits = []
    for nm, sq in seqs.items():
        variants = {"": sq, "diff": [sq[i + 1] - sq[i] for i in range(len(sq) - 1)],
                    "psum": [sum(sq[: i + 1]) for i in range(len(sq))],
                    "ratio": [sq[i + 1] // sq[i] if sq[i] else 0 for i in range(len(sq) - 1)]}
        for vn, tr in variants.items():
            for sh in range(0, 12):
                for st in range(0, 7):
                    if tr[sh: sh + 5] == tgt[st: st + 5]:
                        hits.append((nm, vn, sh, st))
    out("   any run of 5 consecutive terms of A100982 (starting at term 1..7) inside the sequences / differences /")
    out("   partial sums / integer ratios, shifts 0..11:", hits if hits else "none")
    out(f"\ndone in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
