"""Q1.5  The Pythagorean interval 3^s / 2^k of a cycle.

Convention: shortcut map T_c(n) = n/2 (even), (3n+c)/2 (odd) on Z.  A cycle with k
shortcut steps, s of them odd, lives in cell (k, s); its "interval" is 3^s/2^k,
measured in cents as 1200*(s*log2(3) - k)  (positive = ascending, i.e. 3^s > 2^k,
which is the NEGATIVE-integer side; negative cents = descending = positive integers).
Output: q15_intervals.log, q15_intervals.json
"""
import json
import os
from fractions import Fraction
from math import gcd, log, log2

import mpmath

from hc_common import (T, Tee, fmt_factor, n_primitive_necklaces, orbit)

HERE = os.path.dirname(os.path.abspath(__file__))
out = Tee(os.path.join(HERE, "q15_intervals.log"))
J = {}
THETA = log2(3)


def cents(k, s):
    return 1200.0 * (s * THETA - k)


UP = {1: "perfect fifth", 2: "major whole tone", 3: "Pyth. major sixth", 4: "ditone (Pyth. major third)",
      5: "Pyth. major seventh", 6: "Pyth. tritone (aug. fourth)", 7: "apotome (chromatic semitone)",
      8: "Pyth. augmented fifth", 9: "Pyth. augmented second", 10: "Pyth. augmented sixth",
      11: "Pyth. augmented third", 12: "Pythagorean comma"}
DOWN = {0: "octave", 1: "perfect fourth", 2: "Pyth. minor seventh", 3: "Pyth. minor third",
        4: "Pyth. minor sixth", 5: "limma (diatonic semitone)", 6: "Pyth. diminished fifth",
        7: "Pyth. diminished octave", 8: "Pyth. diminished fourth", 9: "Pyth. diminished seventh",
        10: "Pyth. diminished third", 11: "Pyth. diminished sixth", 12: "Pyth. diminished ninth"}


def interval_name(k, s):
    """Name of 3^s/2^k when it lies within an octave of the unison and s <= 12."""
    if (k, s) == (84, 53):
        return "Mercator's comma 3^53/2^84 (asc.)"
    if s > 12:
        return ""
    if 2 ** k < 3 ** s < 2 ** (k + 1):
        return f"{UP[s]} {3**s}/{2**k} (asc.)"
    if 3 ** s < 2 ** k < 2 * 3 ** s or (s == 0 and k == 1):
        return f"{DOWN[s]} {2**k}/{3**s} (desc.)"
    return "(compound: more than an octave)"


# ---------------------------------------------------------------- A
out("=" * 78)
out("A. Continued fraction of log2(3) and the 'record cells'")
out("=" * 78)
mpmath.mp.dps = 400
theta = mpmath.log(3) / mpmath.log(2)
cf = []
x = theta
for _ in range(40):
    a = int(mpmath.floor(x))
    cf.append(a)
    x = 1 / (x - a)
out(f"log2(3) = [{cf[0]}; {', '.join(map(str, cf[1:26]))}, ...]")
# convergents p/q (p = k, q = s) and intermediate fractions
conv = [(1, 0), (cf[0], 1)]          # p_{-1}/q_{-1} = 1/0, p_0/q_0
for a in cf[1:]:
    conv.append((a * conv[-1][0] + conv[-2][0], a * conv[-1][1] + conv[-2][1]))
cf_type = {}
for i, (p, q) in enumerate(conv):
    cf_type[(p, q)] = "convergent"
for i in range(1, len(conv) - 1):
    a_next = cf[i]                    # conv[i+1] = a_next*conv[i] + conv[i-1]
    for j in range(1, a_next):
        p = conv[i - 1][0] + j * conv[i][0]
        q = conv[i - 1][1] + j * conv[i][1]
        cf_type.setdefault((p, q), "semiconvergent")

# exact record cells: on each side, 3^s/2^k closer to 1 than for every smaller s
SMAX = 700
rec = {}
best = {+1: None, -1: None}
for s in range(0, SMAX + 1):
    t = 3 ** s
    for side, k in ((+1, t.bit_length()), (-1, t.bit_length() - 1)):
        if k < 1 or k < s:
            continue
        # distance from unison as a ratio > 1
        r = Fraction(2 ** k, t) if side == 1 else Fraction(t, 2 ** k)
        if best[side] is None or r < best[side]:
            best[side] = r
            rec[(k, s)] = side
rec_list = sorted(rec)
cf_list = sorted(c for c in cf_type if c[1] <= SMAX and c[0] >= 1)
out(f"record cells with s <= {SMAX} (exact integer comparison): {len(rec_list)}")
out(f"convergents + semiconvergents of log2(3) with s <= {SMAX}: {len(cf_list)}")
out(f"the two lists coincide: {rec_list == cf_list}")
assert rec_list == cf_list
J["cf_log2_3"] = cf[:26]
J["record_cells_s_le_700"] = [(k, s, cf_type[(k, s)]) for k, s in rec_list]

out("")
out("The ladder of record cells (k <= 110).  mediant = sum of two earlier record cells.")
out("  (k,s)     type            side   D = 2^k - 3^s          cents     necklaces N   N/|D|        name")
ladder = []
for (k, s) in rec_list:
    if k > 110:
        break
    D = 2 ** k - 3 ** s
    N = n_primitive_necklaces(k, s)
    med = ""
    for (k1, s1) in rec_list:
        if (k - k1, s - s1) in rec and (k1, s1) <= (k - k1, s - s1):
            med = f"= ({k1},{s1}) + ({k-k1},{s-s1})"
    Dstr = str(D) if abs(D) < 10 ** 12 else f"{D:.4e}"
    out(f"  ({k},{s})".ljust(11) + f"{cf_type[(k, s)]:15s} {'+' if D > 0 else '-'}     {Dstr:22s}"
        f"{cents(k, s):9.3f}  {N:<13.6g} {N/abs(D):<12.4g} {interval_name(k, s)}  {med}")
    ladder.append({"k": k, "s": s, "type": cf_type[(k, s)], "D": D, "cents": cents(k, s),
                   "necklaces": N, "expected": N / abs(D), "name": interval_name(k, s), "mediant": med})
J["ladder"] = ladder

# ---------------------------------------------------------------- B
out("")
out("=" * 78)
out("B. The five known cycles of 3x+1 on Z")
out("=" * 78)


def cycle_from(n, c=1):
    orb = [n]
    m = T(n, 3, c)
    while m != n:
        orb.append(m)
        m = T(m, 3, c)
    return orb


def superparticular(orb):
    """3^s/2^k = prod over circuits of (1 + 1/x_top) / (1 + 1/x_bot), x_bot = first odd of a
    run of odd elements, x_top = the even element that ends the run."""
    k = len(orb)
    if all(z % 2 for z in orb) or all(z % 2 == 0 for z in orb):
        return None
    # rotate to start at an odd element preceded by an even one
    i0 = next(i for i in range(k) if orb[i] % 2 and orb[i - 1] % 2 == 0)
    orb = orb[i0:] + orb[:i0]
    facs = []
    i = 0
    while i < k:
        xb = orb[i]
        while orb[i % k] % 2:
            i += 1
        xt = orb[i % k]
        while i < k and orb[i] % 2 == 0:
            i += 1
        facs.append((Fraction(xt + 1, xt), Fraction(xb, xb + 1)))
    return facs


rows = []
out(" min   (k,s)    D     3^s/2^k        cents     CF type          odd elements; harmonic check; name")
for n0 in (0, -1, 1, -5, -17):
    orb = cycle_from(n0)
    k, s = len(orb), sum(1 for z in orb if z % 2)
    D = 2 ** k - 3 ** s
    odd = [z for z in orb if z % 2]
    prod = Fraction(1)
    for z in odd:
        prod *= Fraction(3 * z + 1, 3 * z)
    assert prod == Fraction(2 ** k, 3 ** s) or s == 0
    facs = superparticular(orb)
    fac_str = ""
    if facs:
        tot = Fraction(1)
        for a, b in facs:
            tot *= a * b
        assert tot == Fraction(3 ** s, 2 ** k)
        fac_str = " * ".join(f"({a.numerator}/{a.denominator})({b.numerator}/{b.denominator})" for a, b in facs)
    out(f" {n0:4d}  ({k},{s})".ljust(15) + f"{D:5d}  {3**s}/{2**k}".ljust(22)
        + f"{cents(k, s):9.3f}  {cf_type.get((k, s), 'neither'):15s}  odd = {odd}")
    out(f"        name: {interval_name(k, s)}")
    out(f"        2^k/3^s = prod(1 + 1/(3x)) over odd x: {prod == Fraction(2**k, 3**s) or s == 0}")
    if fac_str:
        out(f"        superparticular form 3^s/2^k = {fac_str}")
    rows.append({"min": n0, "k": k, "s": s, "D": D, "ratio": f"{3**s}/{2**k}", "cents": cents(k, s),
                 "cf_type": cf_type.get((k, s), "neither"), "name": interval_name(k, s),
                 "superparticular": fac_str, "cycle": orb})
J["known_cycles"] = rows

# ---------------------------------------------------------------- C
out("")
out("=" * 78)
out("C. Which cells can hold a cycle of 3x+1 at all?  (archimedean constraint)")
out("   negative cycle other than {-1}: odd elements <= -5, so 1 < 3^s/2^k <= (15/14)^s")
out("   positive cycle other than {1,2}: odd elements >= 3,  so 1 < 2^k/3^s <= (10/9)^s")
out("=" * 78)
allowed = []
out("  s   negative side: allowed k (cents) [record?]        positive side: allowed k (cents) [record?]")
for s in range(1, 21):
    neg = [k for k in range(s, 2 * s + 2) if 2 ** k < 3 ** s
           and Fraction(3 ** s, 2 ** k) <= Fraction(15, 14) ** s]
    pos = [k for k in range(s, 3 * s + 2) if 2 ** k > 3 ** s
           and Fraction(2 ** k, 3 ** s) <= Fraction(10, 9) ** s]
    f = lambda ks: ", ".join(f"({k},{s}) {cents(k, s):+.1f}c{' [R]' if (k, s) in rec else ''}" for k in ks) or "none"
    out(f"  {s:2d}  {f(neg):48s}  {f(pos)}")
    allowed.append({"s": s, "neg": neg, "pos": pos})
J["allowed_cells_3x+1"] = allowed
# Heuristic weight of each allowed non-unit cell: (primitive necklaces)/|D|.  HEURISTIC ONLY
# (each necklace hits 0 mod D with 'probability' 1/|D|); it is known not to be calibrated on the
# positive side, where it predicts cycles that archimedean bounds exclude.
out("")
out("  heuristic weight N/|D| of the allowed NON-unit cells with s <= 12, and the share on record cells")
heur = {}
for side, key in ((-1, "neg"), (+1, "pos")):
    tot = recw = 0.0
    parts = []
    for row in allowed:
        if row["s"] > 12:
            continue
        for k in row[key]:
            s_ = row["s"]
            D = 2 ** k - 3 ** s_
            if abs(D) == 1:
                continue
            wgt = n_primitive_necklaces(k, s_) / abs(D)
            tot += wgt
            if (k, s_) in rec:
                recw += wgt
            parts.append(f"({k},{s_}){'[R]' if (k, s_) in rec else ''} {wgt:.4f}")
    out(f"   {'negative' if side < 0 else 'positive'} side: " + ", ".join(parts))
    out(f"      total {tot:.4f}, on record cells {recw:.4f} ({100*recw/tot:.1f}%)")
    heur[key] = {"total": tot, "on_record_cells": recw}
J["heuristic_weights_s_le_12"] = heur

# ---------------------------------------------------------------- D
out("")
out("=" * 78)
out("D. Control family: all primitive cycles of 3x+c meeting [-20000, 20000],")
out("   c coprime to 6, c <= 199.  Is the cell a record cell (= (semi)convergent)?")
out("=" * 78)


def find_cycles_c(c, B=20000, max_steps=200000):
    cycles = {}
    resolved = set()
    for n0 in range(-B, B + 1):
        path = []
        seen = {}
        n = n0
        hit = None
        for i in range(max_steps):
            if n in resolved:
                break
            if n in seen:
                hit = seen[n]
                break
            seen[n] = i
            path.append(n)
            n = n // 2 if n % 2 == 0 else (3 * n + c) // 2
        if hit is not None:
            cyc = path[hit:]
            m = min(cyc, key=lambda z: (abs(z), z))
            i0 = cyc.index(m)
            cyc = cyc[i0:] + cyc[:i0]
            cycles[frozenset(cyc)] = cyc
        resolved.update(path)
    return list(cycles.values())


allc = []
per_c = {}
for c in range(1, 200):
    if gcd(c, 6) != 1:
        continue
    recs = []
    for cyc in find_cycles_c(c):
        if cyc == [0]:
            continue
        if gcd(abs(cyc[0]), c) != 1:
            continue                         # a multiple of a cycle of 3x + c/g
        k = len(cyc)
        s = sum(1 for z in cyc if z % 2)
        D = 2 ** k - 3 ** s
        odd = [z for z in cyc if z % 2]
        h = sum(log(1 + c / (3 * z)) for z in odd)
        assert abs(h - (k * log(2) - s * log(3))) < 1e-9
        within = (2 ** (k - 1) < 3 ** s < 2 ** (k + 1))
        recs.append({"c": c, "min": cyc[0], "k": k, "s": s, "D": D, "side": 1 if D > 0 else -1,
                     "record": (k, s) in rec, "within_octave": within, "cents": cents(k, s),
                     "g": abs(D) // c})
    per_c[c] = recs
    allc += recs
J["cycles_3x+c"] = allc
# cross-check against the complete word census of q13_tiers.py (all cycles of length <= 24)
census_path = os.path.join(HERE, "q13_tiers.json")
if os.path.exists(census_path):
    with open(census_path, encoding="utf-8") as f:
        census = json.load(f).get("cycles_by_c_le_199_k_le_24", {})
    mism = 0
    n_cmp = 0
    for c in per_c:
        mine = {}
        for r in per_c[c]:
            if r["k"] <= 24:
                mine[(r["k"], r["s"])] = mine.get((r["k"], r["s"]), 0) + 1
        if c == 1:
            mine[(1, 0)] = 1                 # the cycle {0}, which part D leaves out
        theirs = {(k, s): n for k, s, D, n in census.get(str(c), [])}
        n_cmp += sum(theirs.values())
        if mine != theirs:
            mism += 1
            out(f"  MISMATCH c = {c}: brute force {sorted(mine.items())} vs census {sorted(theirs.items())}")
    out(f"  cross-check with the q13 census (every primitive cycle of length <= 24, c <= 199): "
        f"{n_cmp} cycles compared, {mism} values of c disagree")
    J["census_crosscheck"] = {"cycles_compared": n_cmp, "c_values_disagreeing": mism}
out("  c   #prim.cycles  cells (k,s)[*=record cell]{count}")
for c in sorted(per_c):
    if c > 49:
        continue
    cellcount = {}
    for r in per_c[c]:
        key = (r["k"], r["s"], r["record"])
        cellcount[key] = cellcount.get(key, 0) + 1
    desc = "  ".join(f"({k},{s}){'*' if R else ''}{{{n}}}" for (k, s, R), n in sorted(cellcount.items()))
    out(f"  {c:3d}  {len(per_c[c]):3d}   {desc}")


def summary(sel, label):
    n = len(sel)
    if n == 0:
        out(f"  {label}: 0 cycles")
        return None
    r = sum(1 for x in sel if x["record"])
    w = sum(1 for x in sel if x["within_octave"])
    out(f"  {label}: {n} cycles; in record cells {r} ({100*r/n:.1f}%); "
        f"interval within an octave of unison {w} ({100*w/n:.1f}%)")
    return {"n": n, "record": r, "within_octave": w}


out("")
S = {}
S["c=1"] = summary([x for x in allc if x["c"] == 1], "c = 1 (non-zero cycles)")
S["c>1"] = summary([x for x in allc if x["c"] > 1], "5 <= c <= 199, all")
S["c>1 pos"] = summary([x for x in allc if x["c"] > 1 and x["side"] == 1], "5 <= c <= 199, positive side")
S["c>1 neg"] = summary([x for x in allc if x["c"] > 1 and x["side"] == -1], "5 <= c <= 199, negative side")
S["free"] = summary([x for x in allc if x["c"] > 1 and x["g"] == 1], "5 <= c <= 199, 'free' cycles (|D| = c)")
S["accident"] = summary([x for x in allc if x["c"] > 1 and x["g"] > 1], "5 <= c <= 199, 'accident' cycles (|D| = c*g, g > 1)")
S["big"] = summary([x for x in allc if x["c"] > 1 and abs(x["min"]) > 3 * x["c"]],
                   "5 <= c <= 199, cycles with |min| > 3c")
S["small"] = summary([x for x in allc if x["c"] > 1 and abs(x["min"]) <= 3 * x["c"]],
                     "5 <= c <= 199, cycles with |min| <= 3c")
J["summary"] = S
# how many distinct cells are occupied, and how many of them are record cells
cells_occ = {(x["k"], x["s"]) for x in allc if x["c"] > 1}
out(f"  distinct cells occupied by 3x+c cycles (c > 1): {len(cells_occ)}, of which record cells: "
    f"{sum(1 for c_ in cells_occ if c_ in rec)}")
top = {}
for x in allc:
    if x["c"] > 1:
        top[(x["k"], x["s"])] = top.get((x["k"], x["s"]), 0) + 1
out("  ten most populated cells (cell, #cycles, record?, name):")
for (k, s), n in sorted(top.items(), key=lambda kv: -kv[1])[:10]:
    out(f"      ({k},{s})  {n:4d}  {'record' if (k, s) in rec else 'no    '}  {interval_name(k, s)}")
J["top_cells"] = [[k, s, n, (k, s) in rec] for (k, s), n in sorted(top.items(), key=lambda kv: -kv[1])[:20]]

with open(os.path.join(HERE, "q15_intervals.json"), "w", encoding="utf-8") as f:
    json.dump(J, f, indent=1, default=str)
out("")
out("wrote q15_intervals.json")
out.close()
