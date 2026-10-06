"""Reviewer check (lens: mathematics) of site/explore/thirty-six.md, part A.

Independent of scripts/thirty_six/site_figures/check_thirty_six_page.py: nothing is imported
from it.  Dropping times here follow the SITE definition (site/foundations/definitions.md):
standard map f(n) = n/2 or 3n+1, dropping time = least j >= 1 with f^j(n) < n, Dset_j = the
n > 1 with dropping time j.

Covers: pairs / unit cells / cycles / one-even-element theorem / why 3 / intervals;
figurate families against Dset (and the figure JSON); Theorem 2' at class level and at integer
level; totient; the map F; tau_k; N(s), Bizley, Winkler; Ljunggren; small wording checks.

Run: C:/repos/collatz/.venv/Scripts/python.exe -X utf8 mathcheck_thirty_six_a.py
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from math import comb, gcd, isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT: list[str] = []
BAD: list[str] = []


def say(s: str = "") -> None:
    print(s, flush=True)
    OUT.append(s)


def ok(cond: bool, msg: str) -> None:
    say(("ok    " if cond else "WRONG ") + msg)
    if not cond:
        BAD.append(msg)


def T(n: int) -> int:  # shortcut map
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def tri(n: int) -> int:
    return n * (n + 1) // 2


def site_drop(n: int, sign: int = 1, cap: int = 10 ** 6):
    """Site dropping time: standard steps (n/2, 3n+sign) until the first value < n."""
    x, j = n, 0
    while j < cap:
        x = x // 2 if x % 2 == 0 else 3 * x + sign
        j += 1
        if x < n:
            return j
    return None


# ------------------------------------------------------------------ 1. pairs, cells, cycles
say("== 1. pairs, unit cells, cycles")
smooth = sorted({2 ** a * 3 ** b for a in range(700) for b in range(450) if 2 ** a * 3 ** b < 10 ** 200})
pairs = [(x, y) for x, y in zip(smooth, smooth[1:]) if y == x + 1]
ok(pairs == [(1, 2), (2, 3), (3, 4), (8, 9)], f"consecutive 3-smooth pairs below 10^200: {pairs}")
tri_smooth = []
for n in range(1, 10 ** 6):
    t = tri(n)
    while t % 2 == 0:
        t //= 2
    while t % 3 == 0:
        t //= 3
    if t == 1:
        tri_smooth.append(tri(n))
ok(tri_smooth == [1, 3, 6, 36], f"3-smooth triangular numbers T_n, n < 10^6: {tri_smooth}")

rows = [((1, 2), 1, (1, 0), [0]), ((2, 3), 3, (1, 1), [-1]), ((3, 4), 6, (2, 1), [1, 2]),
        ((8, 9), 36, (3, 2), [-5, -7, -10])]
for (lo, hi), tnum, (k, s), cyc in rows:
    orb = [cyc[0]]
    while T(orb[-1]) != cyc[0]:
        orb.append(T(orb[-1]))
    good = (orb == cyc and len(orb) == k and sum(x % 2 for x in orb) == s
            and {2 ** k, 3 ** s} == {lo, hi} and tri(lo) == tnum and abs(2 ** k - 3 ** s) == 1)
    ok(good, f"table row pair {(lo, hi)}: T_{lo} = {tnum}, cell {(k, s)}, 2^k-3^s = {2**k - 3**s}, cycle {orb}")

# all integer cycles met from |n| <= 10^5: exactly five
mins = set()
for start in range(-3000, 3001):
    path, pos, x = [], {}, start
    while x not in pos:
        pos[x] = len(path)
        path.append(x)
        x = T(x)
    cyc = path[pos[x]:]
    mins.add(min(cyc, key=abs))
ok(mins == {0, -1, 1, -5, -17}, f"cycles of T reached from |n| <= 3000 (by least |element|): {sorted(mins)}")
c17 = [-17]
while T(c17[-1]) != -17:
    c17.append(T(c17[-1]))
ok((len(c17), sum(x % 2 for x in c17)) == (11, 7) and 2 ** 11 - 3 ** 7 == -139,
   f"-17 cycle: cell ({len(c17)},{sum(x % 2 for x in c17)}), 2^11 - 3^7 = {2**11 - 3**7}, 3^7/2^11 = {Fraction(3**7, 2**11)}")

# one-even-element theorem, all three equivalent conditions, a <= 300
closing, consec, triang = [], [], []
for a in range(0, 301):
    D = 2 ** (a + 1) - 3 ** a
    # fixed point of the word 1^a 0: solve by composing the affine maps exactly
    num, den = Fraction(1), Fraction(0)          # x -> num*x + den
    for _ in range(a):
        num, den = num * Fraction(3, 2), den * Fraction(3, 2) + Fraction(1, 2)
    num, den = num / 2, den / 2
    x = den / (1 - num)
    if x.denominator == 1:
        xi = int(x)
        orb = [xi]
        for _ in range(a):
            orb.append(T(orb[-1]))
        assert T(orb[-1]) == xi and [y % 2 for y in orb] == [1] * a + [0]
        closing.append((a, orb))
    if abs(D) == 1:
        consec.append(a)
    if isqrt(8 * 6 ** a + 1) ** 2 == 8 * 6 ** a + 1:
        triang.append(a)
ok([a for a, _ in closing] == consec == triang == [0, 1, 2],
   f"1^a 0 closes on an integer / 2^(a+1),3^a consecutive / 6^a triangular, a <= 300: {closing}")
v = [n + 1 for n in (-5, -7, -10)]
ok(v == [-4, -6, -9] and v[0] * v[2] == v[1] ** 2 == 36 == tri(8) and (v[2] + 1) // 2 == v[0]
   and all(Fraction(3, 2) * p == q for p, q in zip(v, v[1:])),
   "v = n+1: -4 -> -6 -> -9 by x3/2, (v+1)/2 sends -9 to -4, (-4)(-9) = (-6)^2 = 36 = T_8")
m3 = lambda n: n // 2 if n % 2 == 0 else (3 * n - 1) // 2
ok([m3(5), m3(7), m3(10)] == [7, 10, 5], "3x-1: 5 -> 7 -> 10 -> 5, v = n-1 = 4, 6, 9")

# why 3
cells = {}
for q in range(3, 4001, 2):
    found = []
    for s in range(0, 40):
        for val in (q ** s - 1, q ** s + 1):
            if val >= 2 and val & (val - 1) == 0:
                found.append((val.bit_length() - 1, s))
    cells[q] = sorted(set(found))
four = [q for q, c in cells.items() if len(c) == 4]
two = [q for q, c in cells.items() if len(c) == 2]
one = [q for q, c in cells.items() if len(c) == 1]
big_s = [(q, c) for q, cs in cells.items() for c in cs if c[1] >= 2]
ok(four == [3] and cells[3] == [(1, 0), (1, 1), (2, 1), (3, 2)] and big_s == [(3, (3, 2))]
   and all((q + 1) & q == 0 or (q - 1) & (q - 2) == 0 for q in two) and len(four) + len(two) + len(one) == len(cells),
   f"|2^k - q^s| = 1, odd q <= 4001: four cells only q=3; two cells for {two[:6]}.. ({len(two)}); s>=2 only {big_s}")

# ------------------------------------------------------------------ 2. figurate families vs Dset
say()
say("== 2. figurate families against the site's dropping sets (K = 16, actual orbits)")
K = 16
M = 1 << K


def shares_site(values, sign):
    cnt: dict = {}
    for val in values:
        j = site_drop(val, sign, cap=5000) if val >= 2 else None
        cnt[j] = cnt.get(j, 0) + 1
    return cnt


# natural law from residues: coefficient class of r mod 2^K, expressed as site index k+s
def coeff_class(r: int, Kbits: int, q: int = 3, d: int = 1):
    x, s = r, 0
    for j in range(1, Kbits + 1):
        if x % 2:
            x = (q * x + d) // 2
            s += 1
        else:
            x //= 2
        if q ** s < 2 ** j:
            return j, s
    return None


nat: dict = {}
for r in range(M):
    c = coeff_class(r, K)
    key = c[0] + c[1] if c else None
    nat[key] = nat.get(key, 0) + 1
say("      natural class sizes mod 2^16 by site index: "
    + ", ".join(f"{k}:{nat[k]}" for k in sorted(k for k in nat if k is not None)) + f", undetermined:{nat[None]}")
exp_first = {1: M // 2, 3: M // 4, 6: M // 16, 8: M // 16}
ok(all(nat[k] == v for k, v in exp_first.items()), "natural shares: 1/2 in Dset_1, 1/4 in Dset_3, 1/16 in Dset_6, 1/16 in Dset_8")
ok(sorted(k for k in nat if k is not None) == [1, 3, 6, 8, 11, 13, 16, 19, 21, 24, 26],
   "site indices reachable at level <= 16: 1, 3, 6, 8, 11, 13, 16, 19, 21, 24, 26")

fams = {"triangular": [tri(n) for n in range(M)], "cubes": [n ** 3 for n in range(M)],
        "squares": [n * n for n in range(M)]}
res = {}
for name, vals in fams.items():
    res[name] = shares_site(vals, +1)
res["squares_3x-1"] = shares_site(fams["squares"], -1)

for name in ("triangular", "cubes"):
    c = res[name]
    diffs = {k: c.get(k, 0) - nat[k] for k in nat if k is not None and c.get(k, 0) != nat[k]}
    say(f"      {name}: actual-minus-natural by set (non-zero only): {diffs}; values 0/1 not filed: {c.get(None, 0)}")
    # the only discrepancies must be the two values 0 and 1 (which never drop)
    ok(diffs == {1: -1, 3: -1} and c.get(None, 0) == 2,
       f"{name}: exactly natural in every set of index <= 26, except that the values 0 and 1 do not drop")
c = res["squares"]
ok({k: v for k, v in c.items() if k is not None} == {1: M // 2 - 1, 3: M // 2 - 1} and c[None] == 2,
   f"squares under 3x+1: {c}")
c = res["squares_3x-1"]
say("      squares under 3x-1, first sets: " + ", ".join(f"{k}:{c.get(k, 0)}" for k in [1, 3, 6, 8, 11, 13, 16, 19, 21, 24, 26]))
ok(c.get(1) == M // 2 - 1 and c.get(3, 0) == 0 and c.get(6, 0) == 0 and all(c.get(k, 0) > 0 for k in [8, 11, 13, 16, 19, 21, 24, 26]),
   "squares under 3x-1: half in Dset_1, none in Dset_3 or Dset_6, something in every later set shown")

# compare with the figure's JSON
jf = HERE.parent / "site_figures" / "fig_thirty_six_figurate.json"
if jf.exists():
    J = json.loads(jf.read_text(encoding="utf-8"))
    idx = [1, 3, 6, 8, 11, 13, 16, 19, 21, 24, 26]
    def mine(c, zero_one_by_residue, sign):
        out = [c.get(k, 0) for k in idx]
        rest = sum(v for k, v in c.items() if k is not None and k not in idx)
        nd = c.get(None, 0)
        if zero_one_by_residue and sign == 1:
            out[0] += 1; out[1] += 1          # 0 -> evens, 1 -> 1 mod 4 (the figure's filing)
        elif zero_one_by_residue:
            out[0] += 1; rest += 1            # 0 -> evens, 1 -> last bucket (3x-1)
        return [Fraction(x, M) for x in out] + [Fraction(rest + (0 if zero_one_by_residue else nd), M)]
    for key, name, sign in (("triangular_3x+1", "triangular", 1), ("cubes_3x+1", "cubes", 1),
                            ("squares_3x+1", "squares", 1), ("squares_3x-1", "squares_3x-1", -1)):
        figv = [Fraction(x) for x in J["exact"][key]]
        ok(figv == mine(res[name], True, sign), f"figure JSON '{key}' = my recount (with 0 and 1 filed by residue, as the script says)")
    natv = [Fraction(x) for x in J["exact"]["natural"]]
    ok(natv[:11] == [Fraction(nat[k], M) for k in idx] and natv[11] == Fraction(nat[None], M),
       "figure JSON 'natural' = my residue count")
    say(f"      last bucket (29+): natural {float(natv[11]):.4f}, squares under 3x-1 {float(Fraction(J['exact']['squares_3x-1'][11])):.4f}")

# 103 distinct dropping times, site convention AND Terras convention
site_m, site_p, terras_m = set(), set(), set()
for n in range(2, 200001):
    sq = n * n
    site_p.add(site_drop(sq, +1))
    x, k = sq, 0
    j = 0
    while True:
        if x % 2:
            x = 3 * x - 1
            j += 1
            x //= 2
            j += 1
        else:
            x //= 2
            j += 1
        k += 1
        if x < sq:
            break
    terras_m.add(k)
    site_m.add(site_drop(sq, -1))
ok(site_p == {1, 3}, f"squares of 2..200000 under 3x+1: site dropping times {sorted(site_p)}")
ok(len(terras_m) == 103, f"squares of 2..200000 under 3x-1: {len(terras_m)} distinct Terras stopping times")
say(f"      ... and {len(site_m)} distinct SITE dropping times (un-shortcut steps)")
ok(len(site_m) == 103, "the page's '103 different dropping times' also holds in the site's step convention")
cub_p, cub_m = set(), set()
for n in range(2, 20001):
    sc = tri(n) ** 2
    cub_p.add(site_drop(sc, +1))
    cub_m.add(site_drop(sc, -1))
ok(cub_p == {1, 3} and len(cub_m) > 20, f"sums of cubes T_n^2, n = 2..20000: {sorted(cub_p)} under 3x+1, {len(cub_m)} distinct under 3x-1")

# squares: a sixth
for k in (10, 16, 20):
    nsq = len({(x * x) % (1 << k) for x in range(1 << (k - 1) + 1)}) if k <= 16 else None
    formula = (2 ** (k - 1) + (4 if k % 2 == 0 else 5)) // 3
    if nsq is not None:
        ok(nsq == formula, f"squares mod 2^{k}: {nsq} residues = {nsq / 2**k:.5f} of all (limit 1/6 = 0.16667)")
ok(all(pow(x, 2, 8) == 1 for x in range(1, 100, 2)), "odd squares are 1 mod 8")
ok(sorted(pow(x, 3, 1 << 14) for x in range(1, 1 << 14, 2)) == list(range(1, 1 << 14, 2)), "cubing permutes the odd residues mod 2^14")
iso = all(((a ** 3 - b ** 3) & -(a ** 3 - b ** 3)) == ((a - b) & -(a - b))
          for a in range(1, 400, 2) for b in range(a + 2, 400, 2))
ok(iso, "v_2(a^3 - b^3) = v_2(a - b) for odd a != b below 400 (isometry)")
ok(all(sorted(tri(n) % (1 << k) for n in range(1 << k)) == list(range(1 << k)) for k in range(1, 17)),
   "T_0..T_(2^k-1) is a complete residue system mod 2^k, k = 1..16")
ok(all(tri(n) == tri(-1 - n) for n in range(-200, 200)), "T_n = T_(-1-n)")
# first 2^K counted from T_1 instead of T_0
alt = sorted(tri(n) % 8 for n in range(1, 9))
say(f"      T_1..T_8 mod 8 = {alt} (not a complete system; counting must start at T_0, but class counts are unaffected: 0 and 4 are both even)")

# polygonal trichotomy
good = True
for sides in range(3, 41):
    a = sides - 2
    P = lambda n, a=a: n + a * n * (n - 1) // 2
    v2 = (a & -a).bit_length() - 1
    k = 9
    if v2 == 0:
        from collections import Counter
        img = Counter(P(n) % (1 << k) for n in range(1 << (k + 1)))
        good &= len(img) == 1 << k and set(img.values()) == {2}
    elif v2 == 1:
        good &= len({P(n) % (1 << k) for n in range(1 << (k + 1))}) == len({(n * n) % (1 << k) for n in range(1 << k)})
    else:
        good &= len({P(n) % (1 << k) for n in range(1 << k)}) == 1 << k
ok(good, "polygonal numbers, sides 3..40, mod 2^9: fold / collapse / permutation according to v_2(sides - 2) = 0 / 1 / >= 2")

# NOT conjugacy
okc = True
for m in range(-500, 500):
    lhs = -1 - T(-1 - m)
    x = m + 1
    rhs = (x // 2 if x % 2 == 0 else (3 * x - 1) // 2) - 1
    okc &= lhs == rhs
ok(okc, "NOT o T o NOT is the 3x-1 shortcut map in the coordinate m+1 (|m| < 500)")

# ------------------------------------------------------------------ 3. Theorem 2'
say()
say("== 3. Theorem 2' (which rules give the squares two classes)")
Kc = 12
mism = []
for q in range(3, 33, 2):
    for d in range(-31, 33, 2):
        levels = set()
        for r in range(1, 1 << Kc, 8):                       # residues 1 mod 8 = closure of odd squares
            c = coeff_class(r, Kc, q, d)
            levels.add(c[0] if c else None)
        single = len(levels) == 1 and None not in levels
        crit = (q == 3 and d % 4 == 1) or (q in (5, 7) and (q + d) % 8 == 0)
        if single != crit:
            mism.append((q, d))
ok(not mism, f"class level: odd squares in ONE class iff q=3, d=1 mod 4 or q in {{5,7}}, q+d=0 mod 8 (480 rules, level 12); mismatches: {mism}")


def site_drop_rule(n: int, q: int, d: int, cap: int = 20000):
    x, j = n, 0
    while j < cap:
        x = x // 2 if x % 2 == 0 else q * x + d
        j += 1
        if x < n:
            return j
    return None


for (q, d) in ((3, 1), (3, 5), (3, 37), (3, 101), (7, 1), (5, 3), (3, -3)):
    sets = {}
    for n in range(2, 3001):
        j = site_drop_rule(n * n, q, d)
        sets.setdefault(j, []).append(n * n)
    desc = ", ".join(f"Dset_{j}: {len(vv)}" + (f" {vv}" if len(vv) <= 6 else "") for j, vv in sorted(sets.items(), key=lambda t: (t[0] is None, t[0])))
    say(f"      rule ({q}x{d:+d})/2, squares of 2..3000 by ACTUAL dropping time: {desc}")
sets37 = {site_drop_rule(n * n, 3, 37) for n in range(2, 3001)}
ok(len(sets37) > 2, f"INTEGER level: under 3x+37 (q = 3, d = 1 mod 4) the squares > 1 meet {len(sets37)} dropping sets, not two "
                   "(9 and 25 lie below the threshold 37): the page's general 'iff' is a statement about classes, not about sets")

# ------------------------------------------------------------------ 4. totient
say()
say("== 4. phi(x) = 36")
X = 3000
phi = list(range(X + 1))
for p in range(2, X + 1):
    if phi[p] == p:
        for m in range(p, X + 1, p):
            phi[m] = phi[m] // p * (p - 1)
sols = [x for x in range(1, X + 1) if phi[x] == 36]
ok(sols == [37, 57, 63, 74, 76, 108, 114, 126], f"solutions of phi(x) = 36 (x <= 3000; phi(x) >= sqrt(x/2) rules out more): {sols}")
mult = {}
for x in range(1, X + 1):
    mult[phi[x]] = mult.get(phi[x], 0) + 1
ok(mult[36] == 8 and all(mult.get(m, 0) != 8 for m in range(1, 36)), "36 is the least n with exactly eight solutions")
# generating function coefficient at X^2 Y^2
def isprime(n):
    return n > 1 and all(n % p for p in range(2, isqrt(n) + 1))
pts = [(i, j) for i in range(1, 3) for j in range(0, 3) if (i, j) != (1, 0) and isprime(2 ** i * 3 ** j + 1)]
say(f"      Pierpont points with i, j <= 2: {[(p, 2**p[0]*3**p[1]+1) for p in pts]}")
def coeff(a, b):
    # (1 + 1/(1-X)) : coefficient 2 at X^0, 1 at X^u (u>=1);  (1 + X/(1-Y)): 1 at 1, 1 at X Y^v (v>=0)
    total = 0
    from itertools import combinations
    for r in range(len(pts) + 1):
        for S in combinations(pts, r):
            ci, cj = sum(p[0] for p in S), sum(p[1] for p in S)
            ra, rb = a - ci, b - cj
            if ra < 0 or rb < 0:
                continue
            # ways from the 2-part and the 3-part to make (ra, rb)
            ways = 0
            for use3 in (False, True):
                if not use3:
                    if rb == 0:
                        ways += 2 if ra == 0 else 1
                else:
                    u = ra - 1                      # 3-part contributes (1, v), v = rb
                    if u >= 0:
                        ways += 2 if u == 0 else 1
            total += ways
    return total
ok(coeff(2, 2) == 8, f"coefficient of X^2 Y^2 in the generating function = {coeff(2, 2)}")
parts = {108: [(1, 0), (1, 2)], 63: [(1, 1), (1, 1)], 126: [(0, 0), (1, 1), (1, 1)], 57: [(1, 0), (1, 2)],
         76: [(1, 0), (1, 2)], 114: [(0, 0), (1, 0), (1, 2)], 37: [(2, 2)], 74: [(0, 0), (2, 2)]}
ok(all((sum(p[0] for p in v), sum(p[1] for p in v)) == (2, 2) for v in parts.values())
   and 108 == 2 ** 2 * 3 ** 3 and 63 == 9 * 7 and 57 == 3 * 19 and 76 == 4 * 19 and 114 == 6 * 19,
   "table of the eight solutions: factorisations and lattice parts add up to (2,2); counts 1 + 2 + 3 + 2")
ok(all(phi[n] // 2 == 2 * 9 for n in sols) and phi[10] == 4,
   "deg Q(cos 2pi/n) = phi(n)/2 = 2^1 3^2 for the eight n (one square root, two cubic steps); phi(10) = 2^2")

# ------------------------------------------------------------------ 5. F and tau_k
say()
say("== 5. F(n) = sum_{d|n} tau(d)")
L = 10 ** 6
spf = list(range(L + 1))
for p in range(2, isqrt(L) + 1):
    if spf[p] == p:
        for m in range(p * p, L + 1, p):
            if spf[m] == m:
                spf[m] = p
Fv = [0, 1] + [0] * (L - 1)
for n in range(2, L + 1):
    m, out = n, 1
    while m > 1:
        p, e = spf[m], 0
        while m % p == 0:
            m //= p
            e += 1
        out *= (e + 1) * (e + 2) // 2
    Fv[n] = out
# definition check on a small range
ok(all(Fv[n] == sum(sum(1 for e in range(1, d + 1) if d % e == 0) for d in range(1, n + 1) if n % d == 0) for n in range(1, 400)),
   "product formula F(p^a) = T_(a+1) agrees with the definition for n < 400")
orb = [72]
for _ in range(9):
    orb.append(Fv[orb[-1]])
ok(orb == [72, 60, 54, 30, 27, 10, 9, 6, 9, 6], "72 -> 60 -> 54 -> 30 -> 27 -> 10 -> 9 -> 6 -> 9 -> 6")
ok([n for n in range(1, L + 1) if Fv[n] == n] == [1, 3, 18, 36], "fixed points of F up to 10^6: 1, 3, 18, 36")
ok([n for n in range(1, L + 1) if Fv[n] > n] == [2, 4, 6, 8, 12, 24], "F(n) > n exactly at 2, 4, 6, 8, 12, 24 (n <= 10^6): six integers")
ok([n for n in range(1, L + 1) if 2 * Fv[n] == 3 * n] == [2, 4, 6, 12], "F(n) = 3n/2 exactly at 2, 4, 6, 12 (n <= 10^6): four integers")
ends = set()
for n in range(1, L + 1):
    x = n
    while x not in (1, 3, 18, 36, 6, 9):
        x = Fv[x]
    ends.add(x)
ok(ends == {1, 3, 18, 36, 6, 9}, "every orbit from n <= 10^6 ends in 1, 3, 18, 36 or {6, 9}")
sig36 = sum(d ** 0 for d in range(1, 37) if 36 % d == 0)
lhs = sum(sum(1 for e in range(1, d + 1) if d % e == 0) ** 3 for d in range(1, 37) if 36 % d == 0)
ok(lhs == 36 ** 2 == Fv[36] ** 2, f"Liouville at 36: sum tau(d)^3 = {lhs} = 36^2")


def tau_k_of(n: int, k: int) -> int:
    out, p = 1, 2
    while p * p <= n:
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        out *= comb(e + k - 1, e)
        p += 1
    return out * (k if n > 1 else 1)


ok(all(tau_k_of(p * p * q * q, k) == tri(k) ** 2 == sum(i ** 3 for i in range(1, k + 1))
       for (p, q) in ((2, 3), (2, 5), (3, 7), (11, 13)) for k in range(1, 60)), "tau_k(p^2 q^2) = T_k^2 = 1^3+..+k^3")
fam = [k for k in range(1, 61) if tau_k_of(tri(k) ** 2, k) == tri(k) ** 2]
say(f"      k <= 60 with tau_k(T_k^2) = T_k^2: {fam}")
ok(fam[1:7] == [3, 4, 5, 6, 10, 13] and [tri(k) ** 2 for k in fam[1:5]] == [36, 100, 225, 441],
   "k = 3, 4, 5, 6, 10, 13, ... giving 36, 100, 225, 441")
ok(fam[0] == 1, "EDGE: k = 1 also satisfies tau_1(T_1^2) = T_1^2 (tau_1 = 1) although T_1 = 1 is not a product of two primes: "
                "the README's Theorem 3 says k >= 2, the page drops it")

# ------------------------------------------------------------------ 6. N(s)
say()
say("== 6. dropping-word counts N(s)")
def N_beatty(s: int) -> int:
    if s == 1:
        return 1
    m = [None] + [(3 ** i).bit_length() - 1 for i in range(1, s)]       # floor(i log2 3)
    f = {t: 1 for t in range(1, m[1] + 1)}
    for i in range(2, s):
        g, run = {}, 0
        for t in range(1, m[i] + 1):
            run += f.get(t - 1, 0)
            if run:
                g[t] = run
        f = g
    return sum(f.values())
Ns = [None] + [N_beatty(s) for s in range(1, 61)]
ok(Ns[1:14] == [1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045], f"N(1..13) = {Ns[1:14]} (A100982)")
ok(Ns[10] == 476 and Ns[36] == 38088111350198, f"N(10) = {Ns[10]}, N(36) = {Ns[36]}")
F8 = lambda j: Fraction(comb(8 * j, 3 * j), 8 * j)
F19 = lambda j: Fraction(comb(19 * j, 7 * j), 19 * j)
ok(F8(2) - F8(1) ** 2 / 2 == 476 and F19(3) + F19(1) * F19(2) + F19(1) ** 3 / 6 == Ns[36],
   f"Bizley closed forms: N(10) = F2 - F1^2/2 = {F8(2)} - {F8(1)**2/2};  N(36) = F3 + F1 F2 + F1^3/6 with F1 = {F19(1)}")
lo_eq, up_eq, viol = [], [], 0
for s in range(1, 61):
    m = (3 ** s).bit_length() - 1
    lo, up = Fraction(comb(m - 1, s - 1), s), Fraction(comb(m, s - 1), s)
    viol += not (lo <= Ns[s] <= up)
    if Ns[s] == lo:
        lo_eq.append(s)
    if Ns[s] == up:
        up_eq.append(s)
ok(viol == 0 and lo_eq == [1, 2, 7, 12, 53] and up_eq == [1, 3, 5, 17, 29, 41],
   f"Winkler sandwich holds for s <= 60; equality orders lower {lo_eq}, upper {up_eq}")
ok(all(Fraction(comb(2 * m + 1, 2), 2 * m + 1) == m for m in range(1, 500)),
   "REMARK: every positive integer m is the rational Catalan number Cat(2, 2m-1) = C(2m+1,2)/(2m+1); e.g. N(4) = 3 = Cat(2,5). "
   "So 'N(s) is a rational Catalan number exactly at ...' is not literally an 'exactly'; the exact statement is about meeting the bounds")
mean = sum(Fraction(Ns[s], 3 ** s) for s in range(1, 61)) + 1
say(f"      1 + sum_(s<=60) N(s)/3^s = {float(mean):.8f}")
ok(1.6899 < float(mean) < 1.6903606, "partial sum to 60 terms is 1.6899 (terms decay like 0.946^s; part B sums 700 terms)")

# ------------------------------------------------------------------ 7. Ljunggren and wording
say()
say("== 7. Ljunggren; 'triangular sum of cubes'")
tt = [tri(n) for n in range(0, 10 ** 6) if isqrt(8 * tri(n) ** 2 + 1) ** 2 == 8 * tri(n) ** 2 + 1]
ok(tt == [0, 1, 6], f"triangular numbers T_n (n < 10^6) whose square is triangular: {tt}")
tris = {tri(n) for n in range(1, 200)}
two_cubes = sorted({a ** 3 + b ** 3 for a in range(1, 20) for b in range(a + 1, 20)} & tris)
say(f"      triangular numbers that are a sum of two distinct positive cubes: {two_cubes[:6]} (28 = 1^3 + 3^3 = T_7, 91 = 3^3 + 4^3 = T_13)")
ok(28 in two_cubes and 91 in two_cubes, "so 'the only triangular sum of cubes' needs 'of the FIRST n cubes, n > 1'")
ok(1 == 1 ** 3 == tri(1), "and 1 = 1^3 = T_1 is a triangular sum of the first n = 1 cubes (README: 'n > 1')")

say()
say(f"{len(BAD)} wrong")
(HERE / "mathcheck_thirty_six_a.log").write_text("\n".join(OUT) + "\n", encoding="utf-8")
sys.exit(1 if BAD else 0)
