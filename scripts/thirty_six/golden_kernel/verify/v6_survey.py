"""Skeptic check 6: the (q, d, N) survey (Q3.3-b), the family G_N (Q3.3-c), mechanisms A and B, and the
Theorem-B ingredients for 3x+1 and for the cousins 5x+1, 7x+1.

Independent code path (power sums + Newton + CRT; Psi_j from cyclotomic polynomials); nothing imported from
gk_common.py.  Triple set as in the researcher's log: 2 <= q, d <= 12, q != d, 2 <= N <= 60, gcd(N, q d) = 1.

CONVENTION: e(x) = x/d, o(x) = (q x + 1)/d on Z/N; A = R_e + R_o; level N = characters of exact order N.
Run:  python -X utf8 v6_survey.py
"""
from __future__ import annotations

import time
from math import gcd
from pathlib import Path

import numpy as np
import sympy as sp

T0 = time.time()
LOG: list[str] = []
FAIL: list[str] = []


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def check(name: str, cond: bool) -> None:
    say(f"   [{'ok' if cond else 'FAIL'}] {name}")
    if not cond:
        FAIL.append(name)


BIG = []
_r = 2 ** 62
while len(BIG) < 10:
    _r = sp.prevprime(_r)
    BIG.append(int(_r))


def charpoly(N: int, q: int, d: int) -> list[int]:
    di = pow(d, -1, N)
    e = [(t * di) % N for t in range(N)]
    o = [((q * t + 1) * di) % N for t in range(N)]
    einv = np.zeros(N, dtype=np.int64)
    oinv = np.zeros(N, dtype=np.int64)
    for t in range(N):
        einv[e[t]] = t
        oinv[o[t]] = t
    need = 2 * 3 ** N + 1
    mods, res, prod = [], [], 1
    for r in BIG:
        M = np.eye(N, dtype=np.int64)
        tr = [0] * (N + 1)
        for k in range(1, N + 1):
            M = M[:, einv] + M[:, oinv]
            M -= r * (M >= r)
            tr[k] = sum(int(v) for v in M.diagonal()) % r
        el = [1] + [0] * N
        for k in range(1, N + 1):
            s = 0
            for i in range(1, k + 1):
                term = el[k - i] * tr[i]
                s += term if i % 2 else -term
            el[k] = s % r * pow(k, -1, r) % r
        res.append([(el[N - k] if (N - k) % 2 == 0 else -el[N - k]) % r for k in range(N + 1)])
        mods.append(r)
        prod *= r
        if prod > need:
            break
    out = [0] * (N + 1)
    Mm = 1
    for rr, m in zip(res, mods):
        inv = pow(Mm % m, -1, m)
        for i in range(N + 1):
            out[i] += Mm * (((rr[i] - out[i]) * inv) % m)
        Mm *= m
    return [c - Mm if c > Mm // 2 else c for c in out]


def pdivmod(a, b):
    a = list(a)
    db = len(b) - 1
    if len(a) - 1 < db:
        return [0], a
    qq = [0] * (len(a) - db)
    for i in range(len(a) - 1, db - 1, -1):
        c = a[i]
        if c:
            qq[i - db] = c
            for j in range(db + 1):
                a[i - db + j] -= c * b[j]
    return qq, (a[:db] if db else [0])


_x = sp.symbols("x")
_psi: dict[int, list[int]] = {}


def Psi(j: int) -> list[int]:
    if j not in _psi:
        if j == 1:
            _psi[j] = [-2, 1]
        elif j == 2:
            _psi[j] = [2, 1]
        else:
            f = [int(c) for c in sp.Poly(sp.cyclotomic_poly(j, _x), _x).all_coeffs()[::-1]]
            h = (len(f) - 1) // 2
            Cp, Cc = [2], [0, 1]
            r = [f[h]] + [0] * h
            for k in range(1, h + 1):
                for i, c in enumerate(Cc):
                    r[i] += f[h + k] * c
                nx = [0] + Cc
                for i, c in enumerate(Cp):
                    nx[i] -= c
                Cp, Cc = Cc, nx
            _psi[j] = r
    return _psi[j]


_ph = np.arange(800001, dtype=np.int64)
for _i in range(2, 800001):
    if _ph[_i] == _i:
        _ph[_i::_i] -= _ph[_i::_i] // _i
PHI = [int(v) for v in _ph]
_root: dict[int, tuple[int, int]] = {}


def root_data(j: int) -> tuple[int, int]:
    if j not in _root:
        r = (2 ** 24 // j + 1) * j + 1
        while not sp.isprime(r):
            r += j
        pf = [int(t) for t in sp.factorint(j)]
        h = 2
        while True:
            z = pow(h, (r - 1) // j, r)
            if all(pow(z, j // t, r) != 1 for t in pf) and (j > 1 or z == 1):
                break
            h += 1
        _root[j] = (r, z)
    return _root[j]


def horner(a, pt, r):
    v = 0
    for c in reversed(a):
        v = (v * pt + c) % r
    return v


CAND = [j for j in range(1, len(PHI)) if j != 4 and PHI[j] <= 2 * 304]      # every j with deg Psi_j <= 304


def cos_factors(prim: list[int]) -> dict[int, int]:
    """all j (j != 4) with Psi_j | prim, with multiplicities (exact division; every j with deg Psi_j <= deg prim)."""
    deg = len(prim) - 1
    found = {}
    rest = prim
    cap = 2 * (2 * deg) ** 2 + 16                 # phi(j) >= sqrt(j/2)
    assert cap < len(PHI)
    for j in CAND:
        if j > cap:
            break
        dj = 1 if j <= 2 else PHI[j] // 2
        if dj > len(rest) - 1:
            continue
        r_, z_ = root_data(j)                      # prefilter: prim must vanish at a root of Psi_j modulo r_ = 1 (mod j)
        if horner(rest, (z_ + pow(z_, -1, r_)) % r_, r_) != 0:
            continue
        pj = Psi(j)
        k = 0
        while len(rest) - 1 >= dj:
            qq, rem = pdivmod(rest, pj)
            if any(rem):
                break
            rest, k = qq, k + 1
        if k:
            found[j] = k
    return found


def all_real(prim: list[int]) -> bool:
    """every root real?  The roots are algebraic integers of modulus <= 2, so by Kronecker they are all real iff
    prim = x^a * prod Psi_j^k.  (A Sturm sequence at degree 300 is far too slow.)"""
    a = 0
    while prim[a] == 0:
        a += 1
    rest = prim[a:]
    cf = cos_factors(rest)
    return sum(k * (1 if j <= 2 else PHI[j] // 2) for j, k in cf.items()) == len(rest) - 1


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


# ------------------------------------------------------------------ the survey
say("=== 1. survey 2 <= q, d <= 12, q != d, 2 <= N <= 60, gcd(N, q d) = 1 ===")
triples = 0
hits = []
classA = classB = 0
realA = realB = 0
for d in range(2, 13):
    for q in range(2, 13):
        if q == d:
            continue
        prim: dict[int, list[int]] = {1: [-2, 1]}
        for N in range(2, 61):
            if gcd(N, q * d) != 1:
                continue
            triples += 1
            p_ = charpoly(N, q, d)
            for dd in divisors(N):
                if dd < N:
                    p_, rem = pdivmod(p_, prim[dd])
                    assert not any(rem), (q, d, N, dd)
            prim[N] = p_
            cf = {j: k for j, k in cos_factors(p_).items() if j not in (1, 2, 3, 6)}
            if cf:
                hits.append((q, d, N, cf))
            a, b = pow(d, -1, N), q * pow(d, -1, N) % N
            isA = N > 2 and (a * a) % N == 1 and (b + 1) % N == 0      # N = 2 is degenerate (-1 = 1): 20 triples, counted in neither class
            isB = N > 2 and (a + 1) % N == 0 and b % N == 1
            if isA or isB:
                ar = all_real(p_)
                classA += isA
                classB += isB
                realA += isA and ar
                realB += isB and ar
    say(f"   d = {d} done ({time.time() - T0:.0f} s, {triples} triples)")
say(f"   triples: {triples};  with an irrational cosine at level N: {len(hits)}")
check("2574 triples, 124 with an irrational cosine", triples == 2574 and len(hits) == 124)
byj: dict[int, int] = {}
for q, d, N, cf in hits:
    for j in cf:
        byj[j] = byj.get(j, 0) + 1
say(f"   number of triples by j: {dict(sorted(byj.items()))}")
check("counts by j: 5 -> 50, 10 -> 24, 8 -> 43, 12 -> 8, 7 -> 3, 9 -> 1, 11 -> 1", (byj.get(5), byj.get(10), byj.get(8), byj.get(12), byj.get(7), byj.get(9), byj.get(11)) == (50, 24, 43, 8, 3, 1, 1))
d2 = [(q, d, N) for q, d, N, cf in hits if d == 2]
check(f"with d = 2 the only hits are (3,2,5) and (8,2,5): {d2}", d2 == [(3, 2, 5), (8, 2, 5)])
check(f"mechanism A (a^2 = 1, b = -1): {realA} of {classA} all real;  mechanism B (a = -1, b = 1): {realB} of {classB} all real",
      (classA, realA, classB, realB) == (70, 70, 22, 22))
p437 = charpoly(7, 4, 3)
p437, rem = pdivmod(p437, [-2, 1])
say(f"   (4,3,7): prim = {sp.factor(sp.Poly(p437[::-1], _x).as_expr())}")
check("(4,3,7): prim = (x^2 - 2)(x^4 - x^2 + 2)", sp.expand(sp.Poly(p437[::-1], _x).as_expr() - (_x ** 2 - 2) * (_x ** 4 - _x ** 2 + 2)) == 0)
say("   q = 5, 7, 9, 11 with d = 2: hits " + str([(q, d, N) for q, d, N, cf in hits if d == 2 and q in (5, 7, 9, 11)]) + " (none: 5x+1, 7x+1, 9x+1, 11x+1 have no irrational cosine for N <= 60)")

# ------------------------------------------------------------------ G_N
say("\n=== 2. family G_N = (1/2)(x -> -2x) + (1/2)(x -> -x-2), N odd, 5 <= N <= 301 ===")
prim = {1: [-2, 1]}
gold, octa, other, real_levels = [], [], [], []
for N in range(3, 302, 2):
    dd_ = (N - 1) // 2
    p_ = charpoly(N, dd_ + 1, dd_)
    for t in divisors(N):
        if t < N:
            p_, rem = pdivmod(p_, prim[t])
            assert not any(rem)
    prim[N] = p_
    if N < 5:
        continue
    cf = {j: k for j, k in cos_factors(p_).items() if j not in (1, 2, 3, 6)}
    if 5 in cf or 10 in cf:
        gold.append(N)
    if 8 in cf:
        octa.append(N)
    if set(cf) - {5, 8, 10}:
        other.append((N, cf))
    if all_real(p_):
        real_levels.append(N)
say(f"   golden (j = 5 or 10): {gold};  octagon (j = 8): {octa};  other: {other};  all-real levels: {real_levels}")
check("golden at 5, 11, 15, 19, 33, 57; octagon at 7, 21, 23, 69; nothing else; all real only at 5 and 15",
      gold == [5, 11, 15, 19, 33, 57] and octa == [7, 21, 23, 69] and not other and real_levels == [5, 15])

# ------------------------------------------------------------------ Theorem B ingredients, mirror and cousins
say("\n=== 3. tr(A_N) and tr(A_N^2) by direct fixed-point counts, N <= 5000 ===")
for q, c in ((3, 1), (3, -1), (5, 1), (7, 1)):
    bad1, bad2, special = [], [], set()
    for N in range(3, 5001):
        if gcd(N, 2 * q) != 1:
            continue
        i2 = pow(2, -1, N)
        xs = np.arange(N, dtype=np.int64)
        e = (xs * i2) % N
        o = ((q * xs + c) * i2) % N
        t1 = int(np.count_nonzero(e == xs) + np.count_nonzero(o == xs))
        t2 = int(np.count_nonzero(e[e] == xs) + np.count_nonzero(e[o] == xs) + np.count_nonzero(o[e] == xs) + np.count_nonzero(o[o] == xs))
        # predicted: gcd(1 - mult, N)-type counts; for 3x+-1 and N prime to 6: tr = 2, tr2 = 3 + gcd(5, N)
        if q == 3:
            if t1 != 2:
                bad1.append(N)
            if t2 != 3 + gcd(5, N):
                bad2.append(N)
        else:
            if t2 != 4:
                special.add(N)
    if q == 3:
        say(f"   {q}x{c:+d}: tr(A) != 2 at {bad1};  tr(A^2) != 3 + gcd(5, N) at {bad2}   (N prime to 6, N <= 5000)")
        check(f"{q}x{c:+d}: Theorem B ingredients hold for all N <= 5000 (sign-blind: identical for 3x+1 and 3x-1)", not bad1 and not bad2)
    else:
        mults = sorted(special)[:12]
        say(f"   {q}x+1: tr(A^2) != 4 exactly at the multiples of {mults[:3]}... (first: {mults})")
say("   so tr(A^2) deviates from 4 only at multiples of 3 or 7 for 5x+1 (21 = 5^2 - 2^2) and of 3 or 5 for 7x+1 (45 = 7^2 - 2^2): the role 5 = 3^2 - 2^2 plays for 3x+1.")

say(f"\n{len(FAIL)} failures;  total time {time.time() - T0:.0f} s")
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
