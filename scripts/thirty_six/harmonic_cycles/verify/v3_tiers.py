"""Skeptic check 3: Q1.3 (tiers, circuits, census, tripled cells) and the new v-lattice remark.

Independent code path: primitive necklaces are generated as Lyndon words by Duval's algorithm
(their census uses numpy over all 2^k bit patterns); word constants are Python ints; cycles of
3x+c are identified from gcd(C, D) and a sample is confirmed by plain iteration.

Convention: shortcut map T_c(n) = n/2 (even), (3n+c)/2 (odd) on Z.  Word of length k with s ones
lives in cell (k, s); D = 2^k - 3^s; fixed point c*C(w)/D.
Output: v3_tiers.log
"""
import json
import os
import sys
from collections import defaultdict
from math import gcd, isqrt, comb

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v3_tiers.log"), "w", encoding="utf-8")


def out(*a):
    line = " ".join(str(x) for x in a)
    print(line)
    LOG.write(line + "\n")
    LOG.flush()


# ------------------------------------------------------------------ 1
out("=" * 78)
out("1. Repeated values of D and of |D| among cells 1 <= s < k <= 400 (their range: k <= 60)")
out("=" * 78)
seen = defaultdict(list)
for k in range(2, 401):
    two = 1 << k
    t = 3
    for s in range(1, k):
        seen[two - t].append((k, s))
        t *= 3
rep_signed = {D: v for D, v in seen.items() if len(v) > 1}
absd = defaultdict(list)
for D, v in seen.items():
    absd[abs(D)] += [(k, s, 1 if D > 0 else -1) for k, s in v]
rep_abs = {a: v for a, v in absd.items() if len(v) > 1}
out("signed D attained twice:", dict(sorted(rep_signed.items())))
out("|D| attained twice     :", dict(sorted(rep_abs.items())))
assert sorted(rep_signed) == [5, 13] and sorted(rep_abs) == [1, 5, 13]
out("  -> signed: D = 5, 13.  In absolute value ALSO |D| = 1 ((2,1) with D = +1 and (3,2) with D = -1).")
out("")
out("  Pillai / Stroeker-Tijdeman is a statement about the SIGNED equation 3^x - 2^y = c.  With")
out("  absolute values and no restriction x < y it is false for c > 13:")
small = defaultdict(list)
for x in range(0, 40):
    for y in range(0, 64):
        c = 3 ** x - 2 ** y
        if 0 < abs(c) <= 100:
            small[abs(c)].append((x, y, c))
multi = {c: v for c, v in small.items() if len(v) > 1}
for c in sorted(multi):
    out(f"     |3^x - 2^y| = {c}: (x, y, signed value) = {multi[c]}")
assert 23 in multi
out("  e.g. 3^3 - 2^2 = 23 = 2^5 - 3^2.  Inside Collatz cells (s < k) the second sign never occurs for")
out("  c > 1, which is why the researcher's table is right although the citation was mis-stated.")

# ------------------------------------------------------------------ 2
out("")
out("=" * 78)
out("2. Circuits 1^a 0^b: (2^(a+b) - 3^a) | (2^b - 1), a, b >= 1.  Wider range: a <= 12000, every b")
out("   that passes the necessary size test |D| <= 2^b - 1 (their range: a + b <= 700)")
out("=" * 78)
sols = []
p3 = 3
n_tests = 0
for a in range(1, 12001):
    # D > 0 needs 2^(a+b) > 3^a and 2^b (2^a - 1) <= 3^a - 1;  D < 0 needs 3^a + 1 <= 2^b (2^a + 1)
    L = p3.bit_length() - a          # 2^(a+L) > 3^a >= 2^(a+L-1)
    for b in range(max(1, L - 3), L + 4):
        D = (1 << (a + b)) - p3
        num = (1 << b) - 1
        if abs(D) <= num:
            n_tests += 1
            if num % D == 0:
                m = num // D
                sols.append((a, b, D, m * (1 << a) - 1))
    p3 *= 3
out(f"candidates passing the size test: {n_tests};  solutions (a, b, D, n_min): {sols}")
assert sols == [(1, 1, 1, 1), (2, 1, -1, -5)]
# make sure the window max(1, L-3) .. L+3 really contains every b with |D| <= 2^b - 1
p3 = 3
for a in range(1, 400):
    L = p3.bit_length() - a
    for b in range(1, 3 * a + 10):
        D = (1 << (a + b)) - p3
        if abs(D) <= (1 << b) - 1:
            assert max(1, L - 3) <= b <= L + 3, (a, b)
    p3 *= 3
out("  (window check a < 400: every admissible b lies in the tested window.)")
out("  mirror: the divisibility is unchanged for 3x-1 (the circuits are n = -1 and n = +5); the")
out("  statement is sign-symmetric.  Cousins 5x+1, 7x+1: see the direct search in check 1.")

# ------------------------------------------------------------------ 3
out("")
out("=" * 78)
out("3. Independent census of primitive necklaces (Lyndon words, Duval), k <= 24")
out("=" * 78)
KMAX = 24


def lyndon_words(n):
    """All binary Lyndon words of length <= n (Duval 1988), as lists."""
    w = [-1]
    while w:
        w[-1] += 1
        yield w
        m = len(w)
        while len(w) < n:
            w.append(w[len(w) - m])
        while w and w[-1] == 1:
            w.pop()


pow3 = [3 ** i for i in range(KMAX + 2)]
cell_n = defaultdict(int)
by_c = defaultdict(lambda: defaultdict(int))      # c0 -> (k,s) -> count
int_cycles = []
total = 0
for w in lyndon_words(KMAX):
    k = len(w)
    s = 0
    C = 0
    for j in range(k):
        if w[j]:
            C = 3 * C + (1 << j)
            s += 1
    total += 1
    cell_n[(k, s)] += 1
    D = (1 << k) - pow3[s]
    g = gcd(C, abs(D))
    c0 = abs(D) // g
    if c0 <= 199:
        by_c[c0][(k, s)] += 1
    if c0 == 1:
        int_cycles.append((k, s, D, C // D))
out(f"Lyndon words of length <= {KMAX}: {total}")
assert total == 1465020
# necklace counts per cell against the Moebius formula


def mobius(n):
    res, p = 1, 2
    while p * p <= n:
        if n % p == 0:
            n //= p
            if n % p == 0:
                return 0
            res = -res
        p += 1
    return -res if n > 1 else res


for (k, s), n in cell_n.items():
    g = gcd(k, s)
    want = sum(mobius(d) * comb(k // d, s // d) for d in range(1, g + 1) if g % d == 0) // k
    assert n == want, (k, s, n, want)
out("necklace count of every cell agrees with the Moebius formula.")
out("integer cycles of 3x+1 (k, s, D, x of the Lyndon rotation):")
for r in sorted(int_cycles):
    k, s, D, x = r
    orb = [x]
    for _ in range(k - 1):
        y = orb[-1]
        orb.append(y // 2 if y % 2 == 0 else (3 * y + 1) // 2)
    y = orb[-1]
    assert (y // 2 if y % 2 == 0 else (3 * y + 1) // 2) == x and len(set(orb)) == k
    out(f"   {r}  min|n| = {min(orb, key=abs)}")
assert len(int_cycles) == 5

their_path = os.path.join(HERE, "..", "q13_tiers.json")
with open(their_path, encoding="utf-8") as f:
    their = json.load(f)["cycles_by_c_le_199_k_le_24"]
mism = 0
n_cmp = 0
for c in sorted(set(list(map(int, their)) + list(by_c))):
    mine = dict(by_c.get(c, {}))
    th = {(k, s): n for k, s, D, n in their.get(str(c), [])}
    n_cmp += sum(mine.values())
    if mine != th:
        mism += 1
        out(f"   MISMATCH c = {c}: mine {sorted(mine.items())}  theirs {sorted(th.items())}")
out(f"comparison with q13_tiers.json for every c <= 199: {n_cmp} cycles, {mism} values of c disagree")
assert mism == 0

out("")
out("mirror / cousin: integer cycles with k <= 20 of 3x-1 and 5x+1 from the same Lyndon enumeration")
for (q, c) in ((3, -1), (5, 1), (5, -1), (7, 1)):
    found = []
    for w in lyndon_words(20):
        k = len(w)
        s = 0
        C = 0
        for j in range(k):
            if w[j]:
                C = q * C + (1 << j)
                s += 1
        D = (1 << k) - q ** s
        if D != 0 and (c * C) % D == 0:
            x = c * C // D
            orb = [x]
            for _ in range(k - 1):
                y = orb[-1]
                orb.append(y // 2 if y % 2 == 0 else (q * y + c) // 2)
            found.append((k, s, D, min(orb, key=abs)))
    out(f"   {q}x{c:+d}: {sorted(found)}")
out("   -> 3x-1: the negated 3x+1 list (same cells, same D).  5x+1: unit cells (1,0), (2,1) only;")
out("      its other cycles (1; 13; 17) are 'accidents' with D = 7, 3, 3.")

# ------------------------------------------------------------------ 4
out("")
out("=" * 78)
out("4. Is '3x+5 and 3x+13 are cycle-rich BECAUSE 5 and 13 are the repeated denominators' right?")
out("   Free cycles of 3x+c (cells with |D| = c, gcd(C, D) = 1), k <= 24, by c:")
out("=" * 78)
free = {}
for c in by_c:
    cells = {cell: n for cell, n in by_c[c].items() if abs((1 << cell[0]) - 3 ** cell[1]) == c}
    if cells and c > 1:
        free[c] = cells
rows = sorted(free.items(), key=lambda kv: -sum(kv[1].values()))
for c, cells in rows[:14]:
    out(f"   c = {c:4d}: {sum(cells.values()):3d} free cycles in cells {dict(sorted(cells.items()))}")
out("   -> 3x+13 owes 7 of its 8 free cycles to the single cell (8,5); 3x+5 owes 2 of 3 to (5,3).")
out("      3x+37 has 3 and 3x+47 has 5 free cycles from ONE cell each; 3x+139 has 29.  The number of")
out("      free cycles is the necklace count of the cell(s), which is large when |D| is small for the")
out("      size of the cell (record cells).  The repetition of D adds exactly one cycle (the cells")
out("      (3,1) and (4,1) have one necklace).  So the README's causal sentence is an overstatement.")

# ------------------------------------------------------------------ 5
out("")
out("=" * 78)
out("5. Multiples of unit cells.  Doubled: D(2k,2s)^2 = 8 T_n + 1.  Tripled: |D(3k,3s)| = 6 T_n + 1")
out("   (centered hexagonal number), where T_n = 2^(k-1) 3^s is the cell's triangular number.")
out("=" * 78)
for (k, s) in ((1, 0), (1, 1), (2, 1), (3, 2)):
    x, y = 2 ** k, 3 ** s
    n = min(x, y)
    Tn = n * (n + 1) // 2
    D2 = 2 ** (2 * k) - 3 ** (2 * s)
    D3 = 2 ** (3 * k) - 3 ** (3 * s)
    assert D2 * D2 == 8 * Tn + 1 and abs(D3) == 6 * Tn + 1
    out(f"   cell ({k},{s}): T_{n} = {Tn};  D(2k,2s) = {D2}, D^2 = {D2*D2} = 8*{Tn}+1;  "
        f"D(3k,3s) = {D3}, |D| = 6*{Tn}+1")
out("   -> 37 = 2^6 - 3^3 = 6*T_3 + 1 comes from the cell (2,1), whose triangular number is 6;")
out("      the '36' in 37 = 36 + 1 is 6*T_3, not T_8.  The cell (3,2) that owns 36 = T_8 gives")
out("      17 = sqrt(8*36 + 1) and 217 = 6*36 + 1 instead.  That 6*T_3 = T_8 is the coincidence")
out("      6 * 6 = 36; no further mechanism was found.  Control: the same recipe gives 7 = 6*1+1")
out("      and 19 = 6*3+1 for the other two unit cells.")

# ------------------------------------------------------------------ 6
out("")
out("=" * 78)
out("6. Family 1^a 0 for 3x + c, c = |2^(a+1) - 3^a| (Q1.3-e), a <= 60, by plain iteration")
out("=" * 78)
for a in range(0, 61):
    Da = 2 ** (a + 1) - 3 ** a
    c = abs(Da)
    m = 1 if Da > 0 else -1
    x0 = m * 2 ** a - c
    y = x0
    vs = []
    for i in range(a + 1):
        vs.append(y + c)
        assert (y % 2 == 1) == (i < a)
        y = y // 2 if y % 2 == 0 else (3 * y + c) // 2
    assert y == x0 and vs[0] * vs[-1] == 6 ** a and gcd(abs(x0), c) == 1
    r = isqrt(8 * 6 ** a + 1)
    assert (r * r == 8 * 6 ** a + 1) == (a <= 2)
out("   OK for a <= 60: cycle closes, v_bot*v_top = 6^a, primitive (gcd(x, c) = 1), 6^a triangular iff a <= 2.")

# ------------------------------------------------------------------ 7
out("")
out("=" * 78)
out("7. NEW (skeptic): the lattice point (2,2) itself lies on the -17 cycle.")
out("   v = n + 1; a run of odd steps starting at v = lam*2^a is lam*2^a, lam*2^(a-1)*3, ..., lam*3^a.")
out("=" * 78)


def cyc(n0, c=1):
    orb = [n0]
    y = n0 // 2 if n0 % 2 == 0 else (3 * n0 + c) // 2
    while y != n0:
        orb.append(y)
        y = y // 2 if y % 2 == 0 else (3 * y + c) // 2
    return orb


def smooth_part(v):
    a = b = 0
    v = abs(v)
    while v % 2 == 0:
        v //= 2
        a += 1
    while v % 3 == 0:
        v //= 3
        b += 1
    return a, b, v


for n0 in (1, -5, -17):
    orb = cyc(n0)
    out(f"   cycle of {n0}: n = {orb}")
    out(f"        v = n+1 = {[n + 1 for n in orb]}")
    out(f"        |v| = lam * 2^a * 3^b, (a, b, lam): {[smooth_part(n + 1) for n in orb]}")
orb17 = cyc(-17)
assert -37 in orb17 and [n + 1 for n in orb17[:5]] == [-16, -24, -36, -54, -81]
out("   -> first circuit of the -17 cycle: v = -(2^4, 2^3*3, 2^2*3^2, 2*3^3, 3^4): the whole")
out("      anti-diagonal a + b = 4 with lam = -1, passing through -(2^2 * 3^2) = -36 at n = -37.")
out("      The three non-trivial known cycles contain unit-lam runs of height 1 ({1,2}), 2 (-5)")
out("      and 4 (-17), because their minima are 2 - 1, -(2^2 + 1), -(2^4 + 1).")
out("      Exits of those runs are consecutive pairs (v_top, 2v'): (3,4), (8,9), (80,81).")
out("   Control (is this special to 36?): which v-values of small cycles of 3x+c are 3-smooth with")
out("   lam = +-1 and a = b?  (v = n + c for 3x+c.)")
cnt = defaultdict(list)
for c in range(1, 200):
    if gcd(c, 6) != 1:
        continue
    seen_c = set()
    for n0 in range(-3000, 3001):
        y = n0
        path = []
        pos = {}
        while y not in pos and y not in seen_c and len(path) < 5000:
            pos[y] = len(path)
            path.append(y)
            y = y // 2 if y % 2 == 0 else (3 * y + c) // 2
        if y in pos:
            cy = path[pos[y]:]
            if gcd(abs(cy[0]), c) == 1 or cy == [0]:
                for z in cy:
                    a, b, lam = smooth_part(z + c) if z + c != 0 else (0, 0, 0)
                    if lam == 1 and a == b and a >= 1 and z % 2:
                        cnt[c].append((z, z + c, a))
        seen_c.update(path)
out(f"   odd cycle elements n with |n + c| = 6^a, a >= 1, c <= 199: "
    f"{ {c: v for c, v in sorted(cnt.items())} }")
out("   (for c = 1: n = -7 (v = -6) in the -5 cycle and n = -37 (v = -36) in the -17 cycle.)")

LOG.close()
