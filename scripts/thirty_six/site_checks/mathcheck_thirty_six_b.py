"""Reviewer check (lens: mathematics) of site/explore/thirty-six.md, part B (the slower counts).

Independent code; nothing imported from site_figures/.

  1. control family 3x + c, 5 <= c <= 199: number of primitive cycles meeting [-20000, 20000],
     share in record cells, size-matched share; the five 5x+1 cycles
  2. "actual dropping times in every class modulo 2^24 or less": all classes of level <= 24,
     least residue, actual stopping time
  3. destination multiplicity M(d): finite, = 1 when 3 | d, mean 1.69; same for 3x-1
  4. sum N(s)/3^s to 700 terms
  5. "it holds for every rule": triangular numbers under 5x+1 and 3x-1 at integer level

Run: C:/repos/collatz/.venv/Scripts/python.exe -X utf8 mathcheck_thirty_six_b.py
"""
from __future__ import annotations

import sys
from fractions import Fraction
from math import gcd
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


# ------------------------------------------------------------------ 1. control family
say("== 1. cycles of 3x + c and record cells")


def record_cells(q: int, s_max: int) -> set:
    """(k, s) such that q^s / 2^k is closer to 1 than for every smaller s on the same side of 1.
    Compared exactly: below 1 a ratio a/2^k beats b/2^l iff a*2^l > b*2^k."""
    rec = set()
    best_lo = None            # (num, k): largest ratio < 1 so far
    best_hi = None            # smallest ratio > 1 so far
    for s in range(0, s_max + 1):
        p = q ** s
        k_hi = p.bit_length() - 1          # 2^k_hi <= p  -> ratio >= 1
        k_lo = k_hi + 1                    # 2^k_lo > p   -> ratio < 1
        if best_lo is None or p * (1 << best_lo[1]) > best_lo[0] * (1 << k_lo):
            best_lo = (p, k_lo)
            rec.add((k_lo, s))
        if s >= 1 and p != 1 << k_hi:
            if best_hi is None or p * (1 << best_hi[1]) < best_hi[0] * (1 << k_hi):
                best_hi = (p, k_hi)
                rec.add((k_hi, s))
    return rec


R3 = record_cells(3, 700)
first = sorted(R3, key=lambda c: (c[1], c[0]))[:9]
say(f"      record cells of log2 3, s <= 700: {len(R3)}; first {first}")
ok(first[:8] == [(1, 0), (1, 1), (2, 1), (3, 2), (5, 3), (8, 5), (11, 7), (19, 12)] and len(R3) == 19,
   "record ladder (1,0), (1,1), (2,1), (3,2), (5,3), (8,5), (11,7), (19,12), ...; 19 cells with s <= 700")
known = {(1, 0), (1, 1), (2, 1), (3, 2), (11, 7)}
ok(known <= R3, "the cells of the five known cycles of T are all record cells")

W = 20000
cycles = []                                   # (c, element of least |.|, k, s)
for c in range(5, 200, 2):
    state = {}                                # value -> index of the walk that first saw it
    for start in range(-W, W + 1):
        if start in state:
            continue
        walk, x = [], start
        local = {}
        while x not in state and x not in local:
            local[x] = len(walk)
            walk.append(x)
            x = x >> 1 if x % 2 == 0 else (3 * x + c) >> 1
        if x in local:                        # a new cycle
            cyc = walk[local[x]:]
            if any(-W <= y <= W for y in cyc):
                m = min(cyc, key=abs)
                if m != 0 and gcd(abs(m), c) == 1:
                    cycles.append((c, m, len(cyc), sum(y & 1 for y in cyc)))
        for y in walk:
            state[y] = True
n_all = len(cycles)
in_rec = [t for t in cycles if (t[2], t[3]) in R3]
big = [t for t in cycles if abs(t[1]) >= 5 * t[0]]
big_rec = [t for t in big if (t[2], t[3]) in R3]
small = [t for t in cycles if abs(t[1]) <= 3 * t[0]]
say(f"      primitive cycles of 3x+c, c odd, 5 <= c <= 199, meeting [-{W}, {W}]: {n_all}")
say(f"      in record cells: {len(in_rec)} = {100 * len(in_rec) / n_all:.1f} %")
say(f"      |min| >= 5c: {len(big_rec)} of {len(big)} = {100 * len(big_rec) / len(big):.1f} %;  |min| <= 3c: "
    f"{sum(1 for t in small if (t[2], t[3]) in R3)} of {len(small)}")
ok(n_all == 257, "257 primitive cycles (c odd, 5..199, window +-20000)")
ok(round(100 * len(in_rec) / n_all) == 21, "21 % in record cells")
ok((len(big_rec), len(big)) == (53, 89), "size-matched: 53 of 89 = 59.6 % ('about 60 %')")
n_c = len({t[0] for t in cycles})
say(f"      (these 257 cycles belong to {n_c} of the 98 maps; '257 cycles of the maps 3x+c' = primitive ones met in the window)")

R5 = record_cells(5, 300)
five = []
for start in (0, -1, 1, 13, 17):
    orb, x = [start], None
    x = start // 2 if start % 2 == 0 else (5 * start + 1) // 2
    while x != start:
        orb.append(x)
        x = x // 2 if x % 2 == 0 else (5 * x + 1) // 2
    five.append((len(orb), sum(y & 1 for y in orb)))
ok(all(c in R5 for c in five), f"5x+1: cycles through 0, -1, 1, 13, 17 sit in cells {five}, all record cells of log2 5 (not of log2 3)")

# ------------------------------------------------------------------ 2. classes of level <= 24
say()
say("== 2. every coefficient class of level <= 24: does the least residue (hence every member) drop on time?")
LV = 24
count_by_level: dict = {}
exceptions = []
# node: (least residue r mod 2^j, j, s, image x = T^j(r)); members r + 2^j t have image x + 3^s t
stack = [(0, 0, 0, 0)]
pow3 = [3 ** i for i in range(LV + 2)]
n_nodes = 0
while stack:
    r, j, s, x = stack.pop()
    n_nodes += 1
    for t in (0, 1):
        r2 = r + (t << j)
        y = x + t * pow3[s]
        if y & 1:
            y2, s2 = (3 * y + 1) >> 1, s + 1
        else:
            y2, s2 = y >> 1, s
        j2 = j + 1
        if (1 << j2) > pow3[s2]:              # coefficient stopping time reached: a class of level j2
            count_by_level[j2] = count_by_level.get(j2, 0) + 1
            if not y2 < r2:
                exceptions.append((r2, j2, s2, y2))
        elif j2 < LV:
            stack.append((r2, j2, s2, y2))
total = sum(count_by_level.values())
say(f"      classes by level: {dict(sorted(count_by_level.items()))}")
say(f"      total classes of level <= {LV}: {total}; nodes visited: {n_nodes}")
say(f"      least residues that do NOT satisfy T^k(r) < r: {exceptions}")
ok(total == 81119, "81,119 classes of level <= 24 (README figure)")
ok(sorted(e[0] for e in exceptions) == [0, 1], "the only least residues that fail to drop at their class level are 0 and 1")
ok(sorted(count_by_level) == [1, 2, 4, 5, 7, 8, 10, 12, 13, 15, 16, 18, 20, 21, 23, 24],
   "levels 1, 2, 4, 5, 7, 8, 10, 12, 13, 15, 16, 18, 20, 21, 23, 24")

# ------------------------------------------------------------------ 3. destination multiplicity
say()
say("== 3. how many integers drop onto d")


def dest_table(limit_n: int, sign: int):
    """dest(n) for 2 <= n <= limit_n under 3x+sign (standard map); None if no drop within cap."""
    M: dict = {}
    nodrop = []
    for n in range(2, limit_n + 1):
        x, steps = n, 0
        while x >= n and steps < 5000:
            x = x >> 1 if x % 2 == 0 else 3 * x + sign
            steps += 1
        if x < n:
            M[x] = M.get(x, 0) + 1
        else:
            nodrop.append(n)
    return M, nodrop


D = 10 ** 6
for sign in (+1, -1):
    Mult, nodrop = dest_table(2 * D, sign)
    vals = [Mult.get(d, 0) for d in range(1, D + 1)]
    mean = sum(vals) / D
    three = {Mult.get(d, 0) for d in range(3, D + 1, 3)}
    mn = min(vals)
    say(f"      3x{sign:+d}: d <= 10^6 (all n <= 2*10^6): mean M = {mean:.5f}, min M = {mn}, max M = {max(vals)}, "
        f"M on multiples of 3: {sorted(three)}, never dropping n: {nodrop[:6]}")
    ok(three == {1}, f"3x{sign:+d}: M(d) = 1 for every multiple of 3 up to 10^6")
    ok(abs(mean - 1.6904) < 2e-3, f"3x{sign:+d}: mean of M(d) over d <= 10^6 is {mean:.4f} (the page's 1.69)")
    if sign == 1:
        ok(mn >= 1, "3x+1: every d >= 1 is a destination (2d drops onto d)")

# ------------------------------------------------------------------ 4. the series
say()
say("== 4. sum N(s)/3^s")
S_MAX = 700
N = [0] * (S_MAX + 1)
alive = {0: 1}
j = 0
while alive:
    j += 1
    nxt = {}
    for t, c in alive.items():
        # letter 0
        if (1 << j) > 3 ** t:
            N[t] += c
        else:
            nxt[t] = nxt.get(t, 0) + c
        # letter 1 (never a drop)
        if t + 1 <= S_MAX:
            assert (1 << j) < 3 ** (t + 1)
            nxt[t + 1] = nxt.get(t + 1, 0) + c
    alive = nxt
tot = sum(Fraction(N[s], 3 ** s) for s in range(S_MAX + 1))
say(f"      N(0..12) = {N[:13]};  sum_(s<=700) N(s)/3^s = {float(tot):.10f}")
ok(N[10] == 476 and N[36] == 38088111350198 and abs(float(tot) - 1.6903605922) < 1e-9, "N(10), N(36) and the mean 1.6903605922")
ok(abs(float(sum(Fraction(N[s], 1 << (3 ** s).bit_length()) for s in range(S_MAX + 1))) - 1) < 1e-9,
   "sum N(s)/2^level(s) = 1: the classes partition the integers (density)")

# ------------------------------------------------------------------ 5. 'for every rule'
say()
say("== 5. triangular numbers under other rules, integer level, K = 14")
K = 14
M2 = 1 << K


def coeff_level(r, q, d, Kbits):
    x, s = r, 0
    for jj in range(1, Kbits + 1):
        if x & 1:
            x = (q * x + d) >> 1
            s += 1
        else:
            x >>= 1
        if q ** s < 1 << jj:
            return jj
    return None


def actual_level(n, q, d, cap=3000):
    x = n
    for jj in range(1, cap + 1):
        x = (q * x + d) >> 1 if x & 1 else x >> 1
        if x < n:
            return jj
    return None


for (q, d) in ((3, 1), (3, -1), (5, 1)):
    nat: dict = {}
    for r in range(M2):
        lv = coeff_level(r, q, d, K)
        nat[lv] = nat.get(lv, 0) + 1
    res: dict = {}
    by_res: dict = {}
    for n in range(M2):
        v = n * (n + 1) // 2
        lv = coeff_level(v % M2, q, d, K)
        by_res[lv] = by_res.get(lv, 0) + 1
        a = actual_level(v, q, d) if v >= 2 else None
        res[a] = res.get(a, 0) + 1
    same_res = by_res == nat
    levels = sorted(k for k in nat if k is not None)
    dev = {k: res.get(k, 0) - nat[k] for k in levels if res.get(k, 0) != nat[k]}
    say(f"      rule ({q}x{d:+d})/2: natural shares of the first classes "
        + ", ".join(f"L{k}: {Fraction(nat[k], M2)}" for k in levels[:4])
        + f"; residue law exact: {same_res}; actual-minus-natural: {dev}; never drop within cap: {res.get(None, 0)}")
    ok(same_res, f"({q}x{d:+d})/2: at RESIDUE level the first 2^{K} triangular numbers carry the rule's natural law exactly")
say("      (for 5x+1 the shares are 1/2, 1/8, ... : 'the same shares as all integers' is rule by rule, not '1/2, 1/4, 1/16, 1/16')")

say()
say(f"{len(BAD)} wrong")
(HERE / "mathcheck_thirty_six_b.log").write_text("\n".join(OUT) + "\n", encoding="utf-8")
sys.exit(1 if BAD else 0)
