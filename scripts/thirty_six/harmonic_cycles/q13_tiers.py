"""Q1.3  The next tier: cells ordered by |D| = |2^k - 3^s|.

Convention: shortcut map T_c(n) = n/2 (even), (3n+c)/2 (odd) on Z; cell (k, s) =
words of length k with s ones; D = 2^k - 3^s; fixed point of w under T_c is
c*C(w)/D.  Every primitive word w is therefore a primitive cycle of exactly one
map 3x + c0, namely c0 = |D| / gcd(C(w), D), on the side sign(D) (D > 0: positive
integers, D < 0: negative integers).  [Lagarias 1990.]

Part C is a COMPLETE census of all primitive words of length k <= 24, i.e. of
every primitive cycle of length <= 24 of every map 3x + c (c >= 1, gcd(c,6)=1) on Z.
Output: q13_tiers.log, q13_tiers.json
"""
import json
import os
from collections import defaultdict
from math import comb, gcd

import numpy as np

from hc_common import (T, Tee, fmt_factor, n_primitive_necklaces, orbit, parity_word)

HERE = os.path.dirname(os.path.abspath(__file__))
out = Tee(os.path.join(HERE, "q13_tiers.log"))
J = {}
KCELL = 60
KCENSUS = 24

# ---------------------------------------------------------------- A
out("=" * 78)
out(f"A. Cells (k, s), 1 <= s <= k-1, k <= {KCELL}, ordered by |D| = |2^k - 3^s|")
out("   (s = 0 and s = k are omitted: their only word is 0^k resp. 1^k, the fixed points 0, -1)")
out("=" * 78)
cells = []
for k in range(2, KCELL + 1):
    for s in range(1, k):
        D = 2 ** k - 3 ** s
        cells.append((abs(D), k, s, D))
cells.sort()
out(" |D|   sign  (k,s)    factor(|D|)        n=min(2^k,3^s)   2^(k-1)*3^s = n(n+|D|)/2   prim.necklaces")
tier_rows = []
for absD, k, s, D in cells[:45]:
    n = min(2 ** k, 3 ** s)
    val = 2 ** (k - 1) * 3 ** s
    assert 2 * val == n * (n + absD)
    nn = n_primitive_necklaces(k, s)
    out(f" {absD:5d}  {'+' if D > 0 else '-'}   ({k},{s})".ljust(22)
        + f"{fmt_factor(absD):18s} {n:<16d} {val:<26d} {nn}")
    tier_rows.append({"absD": absD, "D": D, "k": k, "s": s, "n": n,
                      "half_product": val, "primitive_necklaces": nn})
J["cells_by_absD"] = tier_rows

# repeated values of D (Pillai's equation 2^k - 3^s = D), sign included
byD = defaultdict(list)
for absD, k, s, D in cells:
    byD[D].append((k, s))
rep = {D: v for D, v in byD.items() if len(v) > 1}
out("")
out(f"values of D = 2^k - 3^s attained by more than one cell (1 <= s < k <= {KCELL}): "
    f"{dict(sorted(rep.items()))}")
byA = defaultdict(list)
for absD, k, s, D in cells:
    byA[absD].append((k, s, D))
repA = {a: v for a, v in byA.items() if len(v) > 1}
out(f"values of |D| attained by more than one cell: {dict(sorted(repA.items()))}")
J["repeated_D"] = {str(D): v for D, v in sorted(rep.items())}
J["repeated_absD"] = {str(a): v for a, v in sorted(repA.items())}

# ---------------------------------------------------------------- B
out("")
out("=" * 78)
out("B. Circuits 1^a 0^b (Steiner's 1-cycles): integer iff (2^(a+b) - 3^a) | (2^b - 1)")
out("   exhaustive for 0 <= a, b, 1 <= a + b <= 700 (exact integer arithmetic)")
out("=" * 78)
circ = []
p3 = 1
for a in range(0, 701):
    for b in range(0, 701 - a):
        if a + b == 0:
            continue
        D = (1 << (a + b)) - p3
        num = (1 << b) - 1
        if num % D == 0:
            m = num // D
            circ.append((a, b, D, m, m * (1 << a) - 1))
    p3 *= 3
prim = [c for c in circ if (c[0] >= 1 and c[1] >= 1) or c[0] + c[1] == 1]
out(f"solutions (a, b, D, m, n_min = m*2^a - 1): total {len(circ)}")
out(f"   a = 0 (word 0^b, n = 0): {sum(1 for c in circ if c[0] == 0)} solutions (all b)")
out(f"   b = 0 (word 1^a, n = -1): {sum(1 for c in circ if c[1] == 0)} solutions (all a)")
out(f"   a, b >= 1: {[c for c in circ if c[0] >= 1 and c[1] >= 1]}")
J["circuits_a_b_le_700"] = [c for c in circ if c[0] >= 1 and c[1] >= 1]
assert [c[:2] for c in circ if c[0] >= 1 and c[1] >= 1] == [(1, 1), (2, 1)]

# ---------------------------------------------------------------- B2
out("")
out("=" * 78)
out("B2. What persists of '36' beyond D = 1: the one-halving circuit 1^a 0 of the map")
out("    3x + c, c = |2^(a+1) - 3^a|.  In v = n + c the odd run is m*2^a -> ... -> m*3^a")
out("    (m = sign of 2^(a+1) - 3^a), and v_bot * v_top = 6^a = n(n + c)/2, n = min(2^(a+1), 3^a).")
out("=" * 78)
out("  a   c = |2^(a+1)-3^a|   cycle of 3x+c (n)                         v = n + c            6^a      triangular?")
b2 = []
for a in range(0, 9):
    Da = 2 ** (a + 1) - 3 ** a
    c = abs(Da)
    m = 1 if Da > 0 else -1
    x0 = m * 2 ** a - c
    orb = [x0]
    for _ in range(a):
        assert orb[-1] % 2 != 0 or a == 0
        orb.append((3 * orb[-1] + c) // 2)
    assert orb[-1] % 2 == 0 and orb[-1] // 2 == x0          # the single halving closes the cycle
    vs = [z + c for z in orb]
    assert vs[0] * vs[-1] == 6 ** a
    nmin = min(2 ** (a + 1), 3 ** a)
    assert nmin * (nmin + c) == 2 * 6 ** a
    r = int((8 * 6 ** a + 1) ** 0.5)
    tri = any((r + d) ** 2 == 8 * 6 ** a + 1 for d in (-1, 0, 1))
    out(f"  {a}   {c:<18d} {str(orb):42s} {str(vs):20s} {6**a:<8d} {tri}")
    b2.append({"a": a, "c": c, "cycle": orb, "v": vs, "six_pow_a": 6 ** a, "triangular": tri})
J["one_halving_family"] = b2

# ---------------------------------------------------------------- C
out("")
out("=" * 78)
out(f"C. Complete census of primitive words, k <= {KCENSUS}")
out("=" * 78)
CMAX = 400                      # record cycles of 3x+c0 for c0 <= CMAX
cell_stats = {}                 # (k,s) -> dict
cyc_by_c = defaultdict(list)    # c0 -> list of (k, s, D, n_cycles)
int_cycles = []                 # c0 == 1
total_necklaces = 0
CH = 20                         # chunk bits
for k in range(1, KCENSUS + 1):
    hi_bits = max(0, k - CH)
    lo = min(k, CH)
    acc_c0 = defaultdict(lambda: defaultdict(int))   # s -> c0 -> word count
    acc_n = defaultdict(int)                         # s -> primitive word count
    acc_g1 = defaultdict(int)                        # s -> words with gcd(C,D) = 1
    divs = [d for d in range(1, k) if k % d == 0]
    mask = (1 << k) - 1
    Dk = {s: 2 ** k - 3 ** s for s in range(k + 1)}
    for hi in range(1 << hi_bits):
        idx = np.arange(1 << lo, dtype=np.int64) | (np.int64(hi) << np.int64(lo))
        C = np.zeros(idx.shape, dtype=np.int64)
        pop = np.zeros(idx.shape, dtype=np.int64)
        for j in range(k):
            bit = (idx >> j) & 1
            C = np.where(bit == 1, 3 * C + (1 << j), C)
            pop += bit
        primitive = np.ones(idx.shape, dtype=bool)
        for d in divs:
            rot = ((idx >> d) | (idx << (k - d))) & mask
            primitive &= rot != idx
        for s in range(0, k + 1):
            sel = primitive & (pop == s)
            if not sel.any():
                continue
            Cs = C[sel]
            D = Dk[s]
            g = np.gcd(Cs, abs(D))
            c0 = abs(D) // g
            acc_n[s] += int(sel.sum())
            acc_g1[s] += int((g == 1).sum())
            small = c0 <= CMAX
            if small.any():
                vals, cnts = np.unique(c0[small], return_counts=True)
                for v, cn in zip(vals.tolist(), cnts.tolist()):
                    acc_c0[s][v] += cn
                one = c0 == 1
                if one.any():
                    widx = idx[sel][one]
                    for wv, cv in zip(widx.tolist(), Cs[one].tolist()):
                        int_cycles.append((k, s, wv, cv // D))
    for s in sorted(acc_n):
        D = Dk[s]
        nn = acc_n[s] // k
        assert acc_n[s] % k == 0 and nn == n_primitive_necklaces(k, s)
        total_necklaces += nn
        cell_stats[(k, s)] = {"D": D, "necklaces": nn, "gcd1": acc_g1[s] // k,
                              "c0_small": {c: n // k for c, n in sorted(acc_c0[s].items())}}
        for c, n in acc_c0[s].items():
            assert n % k == 0
            cyc_by_c[c].append((k, s, D, n // k))
out(f"primitive necklaces (= primitive rational cycles) examined: {total_necklaces}")

# integer cycles of 3x+1
seen = {}
for k, s, wv, x in int_cycles:
    orb = orbit(x, k)
    w, back = parity_word(x, k)
    assert back == x
    seen[frozenset(orb)] = (k, s, 2 ** k - 3 ** s, min(orb, key=abs))
out(f"primitive integer cycles of 3x+1 with length k <= {KCENSUS}: (k, s, D, element of least |n|)")
for v in sorted(seen.values()):
    out(f"    {v}")
J["integer_cycles_3x+1_k_le_24"] = sorted(seen.values())
assert len(seen) == 5

out("")
out("Tier table with census data (cells with |D| <= 300 and k <= 24):")
out(" |D| sign (k,s)   necklaces  gcd(C,D)=1   other c0 = |D|/gcd present (c0: #cycles)")
tier2 = []
for absD, k, s, D in cells:
    if absD > 300 or k > KCENSUS:
        continue
    st = cell_stats[(k, s)]
    other = {c: n for c, n in st["c0_small"].items() if c != absD}
    out(f" {absD:4d}  {'+' if D > 0 else '-'}  ({k},{s})".ljust(18)
        + f"{st['necklaces']:<10d} {st['gcd1']:<12d} {other}")
    tier2.append({"absD": absD, "D": D, "k": k, "s": s, **st})
J["tier_table_census"] = tier2

out("")
out(f"Cycles of 3x+c with length <= {KCENSUS}, by c (c <= 49):  'free' = cell with |D| = c,")
out("   'accident' = cell with |D| = c*g, g > 1 and g | C(w).   +: positive side, -: negative side")
freeacc = {}
for c in sorted(cyc_by_c):
    if c > 49:
        continue
    free = [(k, s, D, n) for k, s, D, n in sorted(cyc_by_c[c]) if abs(D) == c]
    acc = [(k, s, D, n) for k, s, D, n in sorted(cyc_by_c[c]) if abs(D) != c]
    nf = sum(n for *_, n in free)
    na = sum(n for *_, n in acc)
    freeacc[c] = {"free": free, "accident": acc}
    out(f"  c = {c:3d}: free cycles {nf:3d} in cells {[(k, s, '+' if D > 0 else '-', n) for k, s, D, n in free]}")
    out(f"           accident cycles {na:3d} in cells "
        f"{[(k, s, '+' if D > 0 else '-', abs(D)//c, n) for k, s, D, n in acc]}   [(k,s,side,g,#)]")
J["free_vs_accident_c_le_49"] = {str(c): v for c, v in freeacc.items()}
# complete list, used by q15_intervals.py as an independent cross-check of its brute force
J["cycles_by_c_le_199_k_le_24"] = {str(c): sorted([k, s, D, n] for k, s, D, n in cyc_by_c[c])
                                   for c in sorted(cyc_by_c) if c <= 199}

# expected vs actual for the 3x+1 column
out("")
out("3x+1 only: cells k <= 24 on the two 'octave-reduced' diagonals, heuristic expectation")
out("  necklaces/|D| against the actual number of integer cycles")
out("  (k,s)   D        necklaces   necklaces/|D|   actual")
rows = []
for k in range(2, KCENSUS + 1):
    for s in range(1, k):
        D = 2 ** k - 3 ** s
        if not (2 ** (k - 1) < 3 ** s < 2 ** (k + 1)):
            continue
        st = cell_stats[(k, s)]
        actual = st["c0_small"].get(1, 0)
        rows.append({"k": k, "s": s, "D": D, "necklaces": st["necklaces"],
                     "expected": st["necklaces"] / abs(D), "actual": actual})
        out(f"  ({k},{s})".ljust(10) + f"{D:<9d}{st['necklaces']:<12d}{st['necklaces']/abs(D):<16.4f}{actual}")
J["3x+1_expected_vs_actual"] = rows

with open(os.path.join(HERE, "q13_tiers.json"), "w", encoding="utf-8") as f:
    json.dump(J, f, indent=1, default=str)
out("")
out("wrote q13_tiers.json")
out.close()
