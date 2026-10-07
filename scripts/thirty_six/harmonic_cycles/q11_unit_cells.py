"""Q1.1  3-smooth triangular numbers  <->  unit cells  <->  integer cycles.

Convention: shortcut map T(n) = n/2 (even), (3n+1)/2 (odd) on Z; a word of
length k with s ones lives in cell (k, s); D = 2^k - 3^s; x(w) = C(w)/D.
Output: q11_unit_cells.log, q11_unit_cells.json
"""
import json
import os
from fractions import Fraction
from math import comb, isqrt

from hc_common import (T, Tee, cell_denominator, fixed_point, is_primitive,
                       n_primitive_necklaces, necklace_rep, orbit, parity_word,
                       word_constant, words)

HERE = os.path.dirname(os.path.abspath(__file__))
out = Tee(os.path.join(HERE, "q11_unit_cells.log"))
J = {}

# ---------------------------------------------------------------- A
out("=" * 78)
out("A. 3-smooth triangular numbers  T_n = n(n+1)/2")
out("=" * 78)
# T_n 3-smooth  <=>  n and n+1 both 3-smooth.  Enumerate ALL 3-smooth numbers
# below 10^300 and look for consecutive pairs.
LIMIT = 10 ** 300
smooth = []
p2 = 1
while p2 <= LIMIT:
    v = p2
    while v <= LIMIT:
        smooth.append(v)
        v *= 3
    p2 *= 2
smooth.sort()
pairs = [(a, b) for a, b in zip(smooth, smooth[1:]) if b - a == 1]
out(f"number of 3-smooth integers below 10^300: {len(smooth)}")
out(f"consecutive pairs among them: {pairs}")
tri = [(a, a * (a + 1) // 2) for a, _ in pairs]
out(f"(n, T_n) with T_n 3-smooth, n < 10^300: {tri}")
J["consecutive_3smooth_pairs_below_1e300"] = pairs
J["smooth_triangular"] = tri
assert pairs == [(1, 2), (2, 3), (3, 4), (8, 9)]

# ---------------------------------------------------------------- B
out("")
out("=" * 78)
out("B. Unit cells: (k, s), k >= 1, 0 <= s <= k, with |2^k - 3^s| = 1   (k <= 3000)")
out("=" * 78)
unit = []
pow3 = [1]
for k in range(1, 3001):
    two = 1 << k
    while pow3[-1] < 2 * two:
        pow3.append(pow3[-1] * 3)
    for s, t in enumerate(pow3):
        if s > k:
            break
        if abs(two - t) == 1:
            unit.append((k, s, two - t))
out("unit cells (k, s, D):", unit)
J["unit_cells_k_le_3000"] = unit
assert [(k, s) for k, s, _ in unit] == [(1, 0), (1, 1), (2, 1), (3, 2)]

out("")
out(" n | pair      | cell (k,s) |  D | T_n = 2^(k-1)*3^s | words C(k,s) | prim. necklaces")
cell_of_pair = {frozenset((2 ** k, 3 ** s)): (k, s) for k, s, _ in unit}
for (a, b) in pairs:
    k, s = cell_of_pair[frozenset((a, b))]
    D = 2 ** k - 3 ** s
    assert a * b // 2 == 2 ** (k - 1) * 3 ** s
    out(f" {a} | ({a},{b})     | ({k},{s})      | {D:+d} | {a*b//2:3d} = 2^{k-1}*3^{s}      "
        f"| {comb(k, s)}            | {n_primitive_necklaces(k, s)}")

# ---------------------------------------------------------------- C
out("")
out("=" * 78)
out("C. Exhaustive word census, k <= 18: which cells have ALL words integer?")
out("=" * 78)
KMAX = 18
all_integer_cells = []
integer_cycles = {}       # frozenset(orbit) -> (k, s, word)
n_words_total = 0
for k in range(1, KMAX + 1):
    for s in range(0, k + 1):
        D = cell_denominator(k, s)
        n_int = 0
        n_w = 0
        for w in words(k, s):
            n_w += 1
            C = word_constant(w)
            if C % D == 0:
                n_int += 1
                if is_primitive(w):
                    x = C // D
                    orb = orbit(x, k)
                    # verify it really is a cycle with this parity word
                    pw, back = parity_word(x, k)
                    assert pw == w and back == x, (w, x)
                    key = frozenset(orb)
                    if key not in integer_cycles:
                        integer_cycles[key] = (k, s, necklace_rep(w), min(orb, key=abs))
        n_words_total += n_w
        if n_int == n_w:
            all_integer_cells.append((k, s, D, n_w))
out(f"words examined: {n_words_total}")
out("cells in which every word has an integer fixed point (k, s, D, #words):")
for c in all_integer_cells:
    k, s, D, n_w = c
    tag = "UNIT" if abs(D) == 1 else ("trivial: only word 0^k, x = 0" if s == 0
                                      else "trivial: only word 1^k, x = -1")
    out(f"   {c}   {tag}")
out("")
out("distinct primitive integer cycles of T found in ALL cells k <= %d:" % KMAX)
cyc_rows = []
for key, (k, s, w, m) in sorted(integer_cycles.items(), key=lambda kv: kv[1][0]):
    D = cell_denominator(k, s)
    x0 = Fraction(word_constant(w), D)
    orb = orbit(int(x0), k)
    out(f"   cell ({k},{s})  D = {D:+d}  word {''.join(map(str, w))}  cycle {orb}")
    cyc_rows.append({"k": k, "s": s, "D": D, "word": "".join(map(str, w)), "cycle": orb})
J["all_integer_cells_k_le_18"] = all_integer_cells
J["primitive_integer_cycles_k_le_18"] = cyc_rows
assert len(cyc_rows) == 5

# ---------------------------------------------------------------- D
out("")
out("=" * 78)
out("D. Transposition lemma: swapping an adjacent '10' -> '01' at positions j, j+1")
out("   changes C(w) by exactly 3^t * 2^j  (t = number of ones after position j+1).")
out("=" * 78)
checked = 0
both_integer_outside_unit = 0
for k in range(2, 15):
    for s in range(1, k):
        D = cell_denominator(k, s)
        for w in words(k, s):
            C = word_constant(w)
            for j in range(k - 1):
                if w[j] == 1 and w[j + 1] == 0:
                    w2 = list(w)
                    w2[j], w2[j + 1] = 0, 1
                    t = sum(w[j + 2:])
                    C2 = word_constant(w2)
                    assert C2 - C == 3 ** t * 2 ** j
                    checked += 1
                    if C % D == 0 and C2 % D == 0 and abs(D) != 1:
                        both_integer_outside_unit += 1
out(f"adjacent transpositions checked (2 <= k <= 14): {checked}; identity holds in all")
out(f"adjacent pairs with BOTH fixed points integer outside unit cells: {both_integer_outside_unit}")
J["transposition_pairs_checked"] = checked
J["adjacent_integer_pairs_outside_unit_cells"] = both_integer_outside_unit
assert both_integer_outside_unit == 0

# ---------------------------------------------------------------- E
out("")
out("=" * 78)
out("E. The unit-cell cycles in the coordinate v = n + 1 (odd step: v -> 3v/2;")
out("   even step: v -> (v+1)/2, so T_v = v(v+1)/2 = v * v')")
out("=" * 78)
rows = []
for (k, s, D) in unit:
    w = tuple([1] * s + [0] * (k - s))
    x = fixed_point(w)
    assert x.denominator == 1
    orb = orbit(int(x), k)
    vs = [n + 1 for n in orb]
    n_min = min(2 ** k, 3 ** s)
    tri_n = n_min * (n_min + 1) // 2
    # v before / after the run of s odd steps (each multiplies v by exactly 3/2)
    v_bot = vs[0]
    v_top = v_bot * 3 ** s // 2 ** s
    assert v_top * 2 ** s == v_bot * 3 ** s
    out(f"cell ({k},{s}) D={D:+d}  word {''.join(map(str, w))}  n-orbit {orb}  v-orbit {vs}")
    out(f"     v_bot = {v_bot}, v_top = {v_top}, v_bot*v_top = {v_bot*v_top}, "
        f"T_(v_top) = {v_top*(v_top+1)//2}, 2^(k-1)*3^s = {2**(k-1)*3**s} = T_{n_min}")
    rows.append({"cell": [k, s], "D": D, "n_orbit": orb, "v_orbit": vs,
                 "v_bot_times_v_top": v_bot * v_top, "T_n": tri_n, "n": n_min,
                 "halvings_b": k - s})
J["unit_cell_cycles_v_coordinates"] = rows

# ---------------------------------------------------------------- F
out("")
out("=" * 78)
out("F. One-halving circuits 1^a 0:  closes on an integer iff m*(2^(a+1) - 3^a) = 1")
out("   (v_bot = m*2^a, v_top = m*3^a).  Equivalently 6^a is triangular.")
out("=" * 78)


def is_triangular(N):
    r = isqrt(8 * N + 1)
    return r * r == 8 * N + 1


tri6 = [a for a in range(0, 2001) if is_triangular(6 ** a)]
unit_a = [a for a in range(0, 2001) if abs(2 ** (a + 1) - 3 ** a) == 1]
out(f"a <= 2000 with 6^a triangular: {tri6}  -> 6^a = {[6**a for a in tri6]}")
out(f"a <= 2000 with |2^(a+1) - 3^a| = 1: {unit_a}")
assert tri6 == unit_a == [0, 1, 2]
J["a_with_6^a_triangular_le_2000"] = tri6

# The same closure condition for the (qx+1)/2 family (coordinate u = (q-2)n + 1):
# the circuit 1^a 0 closes on an integer iff |2^(a+1) - q^a| = 1.
hits = [(q, a, 2 ** (a + 1) - q ** a) for q in range(3, 2000, 2)
        for a in range(1, 61) if abs(2 ** (a + 1) - q ** a) == 1]
out(f"(q odd in [3,1999], 1 <= a <= 60) with |2^(a+1) - q^a| = 1: {hits}")
J["one_halving_circuits_q_a_D"] = hits
assert hits == [(3, 1, 1), (3, 2, -1), (5, 1, -1)]
out("  -> one-halving cycles: q=3,a=1 (cycle 1,2), q=3,a=2 (cycle -5,-7,-10), q=5,a=1 (cycle -1,-2).")
out("  The only one with a >= 2 odd steps is (q, a) = (3, 2); its u-product is (2*3)^2 = 36 = T_8.")
# CAUTION (checked, to avoid over-claiming): '(2q)^a is triangular' is equivalent to
# the closure condition only when q is a prime power.  For composite q the factors can
# split between n and n+1, e.g. (2*3465)^2 = 48024900 = T_9800 with 9800 = 8*35^2,
# 9801 = 99^2: a square triangular number that is NOT a consecutive pair {2^(a+1), q^a}.
tri_2q = [(q, a, (2 * q) ** a) for q in range(3, 4000, 2) for a in range(2, 13)
          if is_triangular((2 * q) ** a)]
out(f"(q odd < 4000, 2 <= a <= 12) with (2q)^a triangular: {tri_2q}")
J["(2q)^a_triangular_a_ge_2"] = tri_2q

# square triangular numbers that are 3-smooth
sq = [N for _, N in tri if isqrt(N) ** 2 == N]
out(f"3-smooth triangular numbers that are also squares: {sq}")
J["smooth_square_triangular"] = sq

with open(os.path.join(HERE, "q11_unit_cells.json"), "w", encoding="utf-8") as f:
    json.dump(J, f, indent=1, default=str)
out("")
out("wrote q11_unit_cells.json")
out.close()
