"""Skeptic check 5: Q1.5 (intervals, record cells, forcing, control family).

Independent code path:
 * record cells from exact integer comparisons of |2^k - 3^s| * 2^(-k) style cross-products,
   continued fraction of log2(3) from exact integer arithmetic (no mpmath, no floats);
 * cycles of 3x+c by path-following with one global visited set (their code keeps a per-start
   dictionary plus a resolved set) and primitivity tested on the gcd of the WHOLE cycle;
 * extra controls the researcher did not run: a size-matched control and a small-cell control.

Convention: shortcut map T_c(n) = n/2 (even), (3n+c)/2 (odd) on Z; cell (k, s); interval 3^s/2^k.
Output: v5_intervals.log
"""
import os
from fractions import Fraction
from math import gcd, comb

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v5_intervals.log"), "w", encoding="utf-8")


def out(*a):
    line = " ".join(str(x) for x in a)
    print(line)
    LOG.write(line + "\n")
    LOG.flush()


# ------------------------------------------------------------------ 1
out("=" * 78)
out("1. Continued fraction of log2(3) by exact integer arithmetic, and record cells, s <= 3000")
out("=" * 78)


def cf_log2_3(nterms):
    """CF of log(3)/log(2) by the classical 'Euclid on logarithms' algorithm with exact rationals:
    keep a > b > 1 as exact fractions; a_i = floor(log_b a), then (a, b) <- (b, a / b^a_i)."""
    a, b = Fraction(3), Fraction(2)
    terms = []
    for _ in range(nterms):
        n = 0
        x = a
        while x >= b:
            x /= b
            n += 1
        terms.append(n)
        if x == 1:
            break
        a, b = b, x
    return terms


cf = cf_log2_3(14)
out("log2(3) = [" + "; ".join([str(cf[0]), ", ".join(map(str, cf[1:]))]) + ", ...]")
assert cf[:10] == [1, 1, 1, 2, 2, 3, 1, 5, 2, 23]
conv = [(1, 0), (cf[0], 1)]
for a in cf[1:]:
    conv.append((a * conv[-1][0] + conv[-2][0], a * conv[-1][1] + conv[-2][1]))
kind = {c: "convergent" for c in conv}
for i in range(1, len(conv) - 1):
    for j in range(1, cf[i]):
        kind.setdefault((conv[i - 1][0] + j * conv[i][0], conv[i - 1][1] + j * conv[i][1]), "semiconvergent")

SMAX = min(3000, conv[-1][1] - 1)
rec = {}
best_pos = best_neg = None        # store (num, den) of the ratio > 1
p3 = 1
for s in range(0, SMAX + 1):
    L = p3.bit_length()
    # positive side: smallest 2^k > 3^s
    k = L
    if k >= 1 and k >= s:
        num, den = 1 << k, p3
        if best_pos is None or num * best_pos[1] < best_pos[0] * den:
            best_pos = (num, den)
            rec[(k, s)] = +1
    k = L - 1
    if k >= 1 and k >= s and (1 << k) < p3:
        num, den = p3, 1 << k
        if best_neg is None or num * best_neg[1] < best_neg[0] * den:
            best_neg = (num, den)
            rec[(k, s)] = -1
    p3 *= 3
rec_list = sorted(rec)
cf_list = sorted(c for c in kind if c[1] <= SMAX and c[0] >= 1)
out(f"record cells with s <= {SMAX}: {len(rec_list)};  (semi)convergents with s <= {SMAX}: {len(cf_list)};"
    f"  equal: {rec_list == cf_list}")
assert rec_list == cf_list
out("first twelve:", [(c, kind[c][0]) for c in rec_list[:12]])
assert rec_list[:12] == [(1, 0), (1, 1), (2, 1), (3, 2), (5, 3), (8, 5), (11, 7), (19, 12), (27, 17),
                         (46, 29), (65, 41), (84, 53)]

# ------------------------------------------------------------------ 2
out("")
out("=" * 78)
out("2. The five known cycles: cell, interval, product formulas (exact)")
out("=" * 78)


def T(n, c=1, q=3):
    return n // 2 if n % 2 == 0 else (q * n + c) // 2


def cycle_of(n0, c=1, q=3):
    orb = [n0]
    y = T(n0, c, q)
    while y != n0:
        orb.append(y)
        y = T(y, c, q)
    return orb


for n0 in (0, -1, 1, -5, -17):
    orb = cycle_of(n0)
    k, s = len(orb), sum(z % 2 for z in orb)
    D = 2 ** k - 3 ** s
    odd = [z for z in orb if z % 2]
    prod = Fraction(1)
    for z in odd:
        prod *= 1 + Fraction(1, 3 * z)
    if n0 == 0:
        # T(x)/x is undefined at x = 0: the product formula does NOT hold for the cycle {0}
        assert prod == 1 and Fraction(2 ** k, 3 ** s) == 2
    else:
        assert prod == Fraction(2 ** k, 3 ** s)
    # circuits
    facs = Fraction(1)
    desc = []
    if 0 < s < k:
        i0 = next(i for i in range(k) if orb[i] % 2 and orb[i - 1] % 2 == 0)
        r = orb[i0:] + orb[:i0]
        i = 0
        while i < k:
            xb = r[i]
            while r[i % k] % 2:
                i += 1
            xt = r[i % k]
            while i < k and r[i] % 2 == 0:
                i += 1
            f = (1 + Fraction(1, xt)) / (1 + Fraction(1, xb))
            facs *= f
            desc.append((xb, xt))
        assert facs == Fraction(3 ** s, 2 ** k)
    out(f"  min {n0:4d}: cell ({k},{s}), D = {D:5d}, 3^s/2^k = {Fraction(3**s, 2**k)}, "
        f"record cell: {(k, s) in rec}, circuits (bottom, top): {desc}")
out("  NOTE: Proposition 8 fails for the cycle {0} (empty product 1, but 2^k/3^s = 2); it needs")
out("  'a cycle not containing 0'.")
out("  mirror: for 3x-1 the cycles are negated and every factor (1 + 1/(3x)) becomes (1 - 1/(3x));")
out("  the cells and intervals are IDENTICAL.  The interval of a cycle does not see the sign of the")
out("  map; only 'ascending <=> D < 0' does, and that is sign(D).")
for n0 in (1, 5, 17):
    orb = cycle_of(n0, c=-1)
    k, s = len(orb), sum(z % 2 for z in orb)
    out(f"     3x-1, min {n0}: cell ({k},{s}), interval {Fraction(3**s, 2**k)}")
out("  cousin 5x+1 (intervals 5^s/2^k):")
for n0 in (-1, 1, 13, 17):
    orb = cycle_of(n0, 1, 5)
    k, s = len(orb), sum(z % 2 for z in orb)
    out(f"     5x+1, min {n0}: cell ({k},{s}), D = {2**k - 5**s}, 5^s/2^k = {Fraction(5**s, 2**k)}"
        f"  ({'5-limit named: 5/4 major third' if (k, s) == (2, 1) else '25/32, 125/128 (diesis) etc.'})")

# ------------------------------------------------------------------ 3
out("")
out("=" * 78)
out("3. Forcing: negative cycle other than {-1} => odd elements <= -5 => 1 < 3^s/2^k <= (15/14)^s")
out("=" * 78)
# -3 is not on a cycle:
y = -3
seq = [y]
for _ in range(4):
    y = T(y)
    seq.append(y)
out("  trajectory of -3:", seq, "(falls into -1, so no cycle contains -3)")
for s in range(1, 21):
    neg = [k for k in range(s, 2 * s + 2) if 2 ** k < 3 ** s
           and Fraction(3 ** s, 2 ** k) <= Fraction(15, 14) ** s]
    if s in (2, 7, 12):
        out(f"  s = {s}: admissible negative cells {[(k, s) for k in neg]}")
    if s == 7:
        assert neg == [11]
out("  s = 7 forces (11,7).  Note what this is: for s <= 10, (15/14)^s < 2, so there is AT MOST ONE")
out("  admissible k for each s; 'the cell is forced by s' holds for every small s, not just 7.")
single = [s for s in range(1, 11) if len([k for k in range(s, 2 * s + 2) if 2 ** k < 3 ** s and
                                          Fraction(3 ** s, 2 ** k) <= Fraction(15, 14) ** s]) == 1]
out(f"  s <= 10 with exactly one admissible negative cell: {single}; of these, record cells at "
    f"s = {[s for s in single if any((k, s) in rec for k in range(s, 2*s+2))]}")


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


def necklaces(k, s):
    g = gcd(k, s)
    return sum(mobius(d) * comb(k // d, s // d) for d in range(1, g + 1) if g % d == 0) // k


tot = recw = 0
for s in range(1, 13):
    for k in range(s, 2 * s + 2):
        if 2 ** k < 3 ** s and Fraction(3 ** s, 2 ** k) <= Fraction(15, 14) ** s:
            D = 3 ** s - 2 ** k
            if D == 1:
                continue
            w = Fraction(necklaces(k, s), D)
            tot += w
            if (k, s) in rec:
                recw += w
out(f"  heuristic weight (necklaces/|D|) of admissible non-unit negative cells, s <= 12: "
    f"total {float(tot):.4f}, on record cells {float(recw):.4f} ({100*float(recw/tot):.1f}%)")

# ------------------------------------------------------------------ 4
out("")
out("=" * 78)
out("4. Control family: primitive cycles of 3x+c, 5 <= c <= 199, gcd(c,6) = 1, meeting")
out("   [-20000, 20000]  (own path-following search; primitivity = gcd of the whole cycle with c is 1)")
out("=" * 78)


rows = []
B = 20000
for c in range(5, 200):
    if gcd(c, 6) != 1:
        continue
    known = {}          # element -> cycle id
    cyc_list = []
    # every cycle meeting [-B, B] contains an element in [-B, B]; from each start follow until
    # an already-classified value or a cycle is found
    state = {}
    for n0 in range(-B, B + 1):
        if n0 in state:
            continue
        path = []
        y = n0
        seen_local = {}
        while y not in state and y not in seen_local:
            seen_local[y] = len(path)
            path.append(y)
            y = T(y, c)
        if y in seen_local:
            cy = path[seen_local[y]:]
            cyc_list.append(cy)
        for z in path:
            state[z] = 1
    for cy in cyc_list:
        if cy == [0]:
            continue
        if not any(abs(z) <= B for z in cy):
            continue
        g = 0
        for z in cy:
            g = gcd(g, abs(z))
        if gcd(g, c) != 1:
            continue                    # multiple of a cycle of 3x + c/g
        k, s = len(cy), sum(z % 2 for z in cy)
        D = 2 ** k - 3 ** s
        m = min(abs(z) for z in cy)
        rows.append({"c": c, "k": k, "s": s, "D": D, "min": m, "rec": (k, s) in rec,
                     "side": 1 if D > 0 else -1})


def pct(sel):
    n = len(sel)
    r = sum(x["rec"] for x in sel)
    return f"{r}/{n} = {100*r/n:.1f}%" if n else "0/0"


out(f"  cycles: {len(rows)}   in record cells: {pct(rows)}")
out(f"  positive side: {pct([x for x in rows if x['side'] == 1])};  negative side: "
    f"{pct([x for x in rows if x['side'] == -1])}")
out(f"  |min| > 3c: {pct([x for x in rows if x['min'] > 3 * x['c']])};  |min| <= 3c: "
    f"{pct([x for x in rows if x['min'] <= 3 * x['c']])}")
assert len(rows) == 257 and sum(x["rec"] for x in rows) == 55
cells = {(x["k"], x["s"]) for x in rows}
out(f"  distinct cells occupied: {len(cells)}, record cells among them: {sum(c_ in rec for c_ in cells)}")

out("")
out("  Extra control A (size-matched).  For c = 1 the non-trivial cycles have |min|/c = 5 and 17.")
out("  Cycles of 3x+c with |min| >= 5c:")
big = [x for x in rows if x["min"] >= 5 * x["c"]]
out(f"     {pct(big)}  (positive {pct([x for x in big if x['side'] == 1])}, "
    f"negative {pct([x for x in big if x['side'] == -1])})")
out("  Extra control B (small cells).  Among ALL cells 1 <= s < k <= 11 how many are record cells?")
small = [(k, s) for k in range(2, 12) for s in range(1, k)]
out(f"     {sum(c_ in rec for c_ in small)} of {len(small)}; among the octave-reduced ones "
    f"(2^(k-1) < 3^s < 2^(k+1)): "
    f"{sum(c_ in rec for c_ in small if 2**(c_[0]-1) < 3**c_[1] < 2**(c_[0]+1))} of "
    f"{sum(1 for c_ in small if 2**(c_[0]-1) < 3**c_[1] < 2**(c_[0]+1))}")
out("     cells with k <= 3 (1 <= s < k): (2,1), (3,1), (3,2): two of three are record cells, and")
out("     (1,0), (1,1) are record cells by definition (first on each side).")
out("  Verdict: the 21.4% headline is diluted by cycles with |min| <= 3c, for which the interval is")
out("  far from unison by the product formula; the size-matched figure is about one half.  'Cycles")
out("  sit at record cells' is still not a law, but it is a strong tendency for cycles that are")
out("  large relative to c, which is the classical Crandall/Eliahou mechanism.")


# ------------------------------------------------------------------ 5
out("")
out("=" * 78)
out("5. Cousin test: do the known cycles of 5x+1 also sit at record cells (of log2 5)?")
out("=" * 78)


def record_cells(q, smax):
    rc = {}
    bp = bn = None
    pq = 1
    for s_ in range(0, smax + 1):
        L = pq.bit_length()
        k_ = L
        if k_ >= 1 and k_ >= s_:
            num, den = 1 << k_, pq
            if bp is None or num * bp[1] < bp[0] * den:
                bp = (num, den)
                rc[(k_, s_)] = +1
        k_ = L - 1
        if k_ >= 1 and k_ >= s_ and (1 << k_) < pq:
            num, den = pq, 1 << k_
            if bn is None or num * bn[1] < bn[0] * den:
                bn = (num, den)
                rc[(k_, s_)] = -1
        pq *= q
    return rc


assert sorted(record_cells(3, 60)) == [c_ for c_ in rec_list if c_[1] <= 60]
rec5 = record_cells(5, 40)
out("  record cells of 5^s/2^k, s <= 40:", sorted(rec5))
for n0 in (0, -1, 1, 13, 17):
    orb = cycle_of(n0, 1, 5)
    k, s = len(orb), sum(z % 2 for z in orb)
    out(f"     5x+1 cycle through {n0}: cell ({k},{s}), D = {2**k - 5**s}, record cell: {(k, s) in rec5}")
    assert (k, s) in rec5
out("  -> all five known cycles of 5x+1 on Z sit at record cells too (5/4 is the unit cell, 25/32 and")
out("     125/128 are 'accidents' with D = 7 and D = 3).  'Known cycles sit at record cells' does not")
out("     distinguish the multiplier 3 from 5, nor 3x+1 from 3x-1: it is the size constraint")
out("     2^k/q^s = prod(1 + 1/(q x)) at work, plus the fact that tiny cells are record cells.")

LOG.close()
