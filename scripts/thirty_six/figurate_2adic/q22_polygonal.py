"""Q2.2  Polygonal families P_s(n) = ((s-2) n^2 - (s-4) n)/2 as maps on the 2-adic integers.

Claim tested (theorem 3 of the README): the type is decided by v2(s-2).
    v2(s-2) = 0  (s odd)        free 2-to-1 fold, Haar -> Haar          (triangular, pentagonal, ...)
    v2(s-2) = 1  (s = 0 mod 4)  ramified fold = affine image of squaring (square, octagonal, ...)
    v2(s-2) >= 2 (s = 2 mod 4)  isometric bijection of Z_2 (Rivest)      (hexagonal, decagonal, ...)

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 q22_polygonal.py
Writes q22_polygonal.log / .json.  Conventions: common.py (Terras stopping time k of the VALUE).
"""
import json
import os
import random
import sys
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import Tee, class_table, polygonal, stop, v2

out = Tee(os.path.join(HERE, "q22_polygonal.log"))
res = {}
t0 = time.time()

NAMES = {3: "triangular", 4: "square", 5: "pentagonal", 6: "hexagonal", 7: "heptagonal",
         8: "octagonal", 9: "nonagonal", 10: "decagonal", 11: "hendecagonal", 12: "dodecagonal"}


def n_squares(k):
    return ((1 << (k - 1)) + (4 if k % 2 == 0 else 5)) // 3


def predicted_type(s):
    v = v2(s - 2)
    return {0: "free fold"}.get(v, "ramified fold" if v == 1 else "isometry")


def rivest(s):
    """Rivest (2001): a0 + a1 x + ... + ad x^d is a permutation polynomial mod 2^w (all w >= 2)
    iff a1 odd, a2+a4+... even, a3+a5+... even.  Only applicable when the coefficients are
    integers, i.e. s even:  P_s(n) = b n^2 + (1-b) n with b = (s-2)/2."""
    if s % 2:
        return None
    b = (s - 2) // 2
    a1, a2 = 1 - b, b
    return (a1 % 2 == 1) and (a2 % 2 == 0)


def inv_mod(a, M):
    return pow(a, -1, M)


out("=" * 100)
out("1. Residue-level classification, s = 3 .. 34, k = 3 .. 14")
out("   mult(2^(k+1)) = set of multiplicities of residues mod 2^k hit by P_s(n), n in [0, 2^(k+1))")
out("   CRS[0,2^k) = are the first 2^k terms a complete residue system mod 2^k (all k tested)")
out("   image = #distinct residues mod 2^14 / 2^14;  axis = fixed point (s-4)/(2(s-2)) of the reflection")
out("=" * 100)
out("   s  v2(s-2) predicted      Rivest  mult@2^(k+1)   CRS[0,2^k)  image@k=14  #sq(14)/2^14  axis        fold check")
rows = []
for s in range(3, 35):
    a = s - 2
    typ = predicted_type(s)
    mults = set()
    crs_all = True
    crs_fail_first = None
    fold_ok = None
    for k in range(3, 15):
        M = 1 << k
        n = np.arange(2 * M, dtype=np.int64)
        p = ((a * n * n - (s - 4) * n) // 2) % M
        mult = np.bincount(p, minlength=M)
        mults |= set(int(x) for x in np.unique(mult))
        first = p[:M]
        is_crs = len(np.unique(first)) == M
        if not is_crs and crs_fail_first is None:
            crs_fail_first = k
        crs_all &= is_crs
        if s % 2 == 1:
            # reflection iota(x) = (s-4)/(s-2) - x, computed mod 2^(k+1)
            c = ((s - 4) * inv_mod(a, 2 * M)) % (2 * M)
            idx = (c - n) % (2 * M)
            ok = bool((p == p[idx]).all()) and bool(((idx - n) % 2 == 1).all())
            fold_ok = ok if fold_ok is None else (fold_ok and ok)
    image = len(np.unique(p)) / M
    axis = Fraction(s - 4, 2 * (s - 2))
    rows.append(dict(s=s, v2=v2(a), predicted=typ, rivest=rivest(s), mults=sorted(mults),
                     crs_initial=crs_all, crs_fail_first_k=crs_fail_first, image14=image,
                     axis=str(axis), fold_ok=fold_ok))
    out(f"  {s:2d}    {v2(a)}     {typ:14s} {str(rivest(s)):6s}  {str(sorted(mults))[:14]:14s} {str(crs_all):5s}"
        f"{'' if crs_all else '(k=' + str(crs_fail_first) + ')':7s} {image:.6f}    {n_squares(14) / 2 ** 14:.6f}"
        f"     {str(axis):10s}  {fold_ok}")
res["classification"] = rows

# verify predictions row by row
ok_all = True
for r in rows:
    if r["predicted"] == "free fold":
        ok = r["mults"] == [2] and r["fold_ok"] and abs(r["image14"] - 1) < 1e-12
        ok &= (r["crs_initial"] == (r["s"] == 3))
    elif r["predicted"] == "isometry":
        ok = r["mults"] == [2] and r["crs_initial"] and r["rivest"] is True
    else:
        ok = (not r["crs_initial"]) and r["rivest"] is False and abs(r["image14"] - n_squares(14) / 2 ** 14) < 1e-12
    ok_all &= ok
out("  every row agrees with the v2(s-2) trichotomy:", ok_all)
out("  (isometries show multiplicity [2] on [0,2^(k+1)) only because that window is two periods)")
res["trichotomy_verified_s_3_34"] = ok_all

out("")
out("=" * 100)
out("2. Metric behaviour: v2(P(x)-P(y)) - v2(x-y) on 50000 random 64-bit pairs (min, max)")
out("   free fold: +(-1) when x-y even ... precisely v2(x-y) - 1 + v2(2 + (s-2)(x+y-1));")
out("   isometry: always 0;  ramified fold: >= 1 when x = y mod 2, 0 otherwise")
out("=" * 100)
random.seed(8)
met = {}
for s in range(3, 15):
    lo, hi = 10 ** 9, -10 ** 9
    lo_same, hi_same = 10 ** 9, -10 ** 9
    for _ in range(50000):
        x = random.getrandbits(64)
        y = random.getrandbits(64)
        if x == y:
            continue
        dv = v2(polygonal(s, x) - polygonal(s, y)) - v2(x - y) if polygonal(s, x) != polygonal(s, y) else 999
        if (x - y) % 2 == 0:
            lo_same, hi_same = min(lo_same, dv), max(hi_same, dv)
        else:
            lo, hi = min(lo, dv), max(hi, dv)
    met[s] = dict(same_parity=(lo_same, hi_same), opposite_parity=(lo, hi))
    out(f"  s={s:2d} {NAMES.get(s, ''):13s} {predicted_type(s):14s}  x=y mod 2: [{lo_same},{hi_same}]"
        f"   x!=y mod 2: [{lo},{hi}]")
res["metric"] = {str(k): v for k, v in met.items()}

out("")
out("=" * 100)
out("3. Dropping classes along each family, residue level, K = 16, n over one full period [0, 2^17)")
out("   count of n with cst(P_s(n) mod 2^16) = k, divided by 2 (two periods of the modulus).")
out("   'natural' = N(k) 2^(16-k).   Terras stopping time k of the VALUE; repo Set index = k+s.")
out("=" * 100)
K = 16
lab, cnat = class_table(K)
lab_np = np.array(lab, dtype=np.int64)
ks = sorted(cnat)
hdr = "     k   natural " + "".join(f"  s={s:<5d}" for s in range(3, 15))
out(hdr)
fam_counts = {}
M = 1 << K
n = np.arange(2 * M, dtype=np.int64)
for s in range(3, 15):
    a = s - 2
    p = ((a * n * n - (s - 4) * n) // 2) % M
    c = np.bincount(lab_np[p], minlength=K + 1)
    fam_counts[s] = c
for k in ks:
    out(f"   {k:3d} {cnat[k]:9d} " + "".join(f"{fam_counts[s][k] / 2:9.0f}" for s in range(3, 15)))
nat_vec = np.array([cnat.get(k, 0) for k in range(K + 1)])
exact = {}
for s in range(3, 15):
    typ = predicted_type(s)
    if typ in ("free fold", "isometry"):
        exact[s] = bool((fam_counts[s] == 2 * nat_vec).all())
    else:
        exact[s] = bool(fam_counts[s][1] == M and fam_counts[s][2] == M and fam_counts[s].sum() == 2 * M)
    out(f"   s={s:2d} {NAMES.get(s, ''):13s} {typ:14s} prediction "
        f"{'= natural, exactly' if typ != 'ramified fold' else '= half in k=1, half in k=2, nothing else'}: {exact[s]}")
res["residue_level_exact_K16"] = {str(s): v for s, v in exact.items()}

out("")
out("=" * 100)
out("4. Actual integers: Terras stopping time of P_s(n), 2 <= n <= 10^6  (frequency per class)")
out("   density row = N(k)/2^k.  Values that never drop (only P_s(1) = 1 is excluded by n >= 2).")
out("=" * 100)
dens = {k: (cnat[k] >> (K - k)) / 2 ** k for k in ks if k}
show = [1, 2, 4, 5, 7, 8, 10, 12]
out("   s  type            " + "".join(f"   k={k:<6d}" for k in show) + "   k>12")
out("      natural density " + "".join(f" {dens[k]:9.6f}" for k in show) + f" {1 - sum(dens[k] for k in show):9.6f}")
act = {}
NMAX = 10 ** 6
for s in range(3, 15):
    h = {}
    nod = 0
    for m in range(2, NMAX + 1):
        r = stop(polygonal(s, m))
        if r is None:
            nod += 1
            continue
        h[r[0]] = h.get(r[0], 0) + 1
    tot = sum(h.values())
    act[s] = dict(hist={str(k): v for k, v in sorted(h.items())}, no_drop=nod)
    rest = sum(v for k, v in h.items() if k > 12) / tot
    out(f"  {s:2d}  {predicted_type(s):14s}  " + "".join(f" {h.get(k, 0) / tot:9.6f}" for k in show)
        + f" {rest:9.6f}")
res["actual_10^6"] = act

out("")
out("=" * 100)
out("5. Which reflections preserve Z?  iota_s(x) = (s-4)/(s-2) - x maps Z to Z iff (s-2) | 2")
out("=" * 100)
for s in range(3, 13):
    c = Fraction(s - 4, s - 2)
    out(f"  s={s:2d}  iota(x) = {c} - x   centre {Fraction(s - 4, 2 * (s - 2))}   integral: {c.denominator == 1}"
        f"   centre in Z_2: {Fraction(s - 4, 2 * (s - 2)).denominator % 2 == 1}"
        f"   iota preserves Z_2: {c.denominator % 2 == 1}")
out("  centres: s=3 -> -1/2 = fixed point of x -> 3x+1 ;  s=4 -> 0 = fixed point of x -> 3x")
out("  rule q x + d has centre -d/(q-1); its reflection x -> -2d/(q-1) - x preserves Z iff (q-1) | 2d:")
for (q, d) in ((3, 1), (3, -1), (5, 1), (5, -1), (7, 1), (5, 3), (9, 1)):
    c = Fraction(-2 * d, q - 1)
    out(f"     {q}x{d:+d}: reflection x -> {c} - x   integral: {c.denominator == 1}")

out("")
out("=" * 100)
out("6. Beyond polygons (computed only): other figurate families mod 2^14 over one full period")
out("   image = fraction of residues hit;  mults = multiplicities that occur (per period)")
out("=" * 100)
others = {
    "pronic n(n+1)": (lambda m: m * (m + 1), 1),
    "centred square 2n(n+1)+1": (lambda m: 2 * m * (m + 1) + 1, 1),
    "centred hexagonal 3n(n+1)+1": (lambda m: 3 * m * (m + 1) + 1, 1),
    "tetrahedral C(n+2,3)": (lambda m: m * (m + 1) * (m + 2) // 6, 2),
    "square pyramidal n(n+1)(2n+1)/6": (lambda m: m * (m + 1) * (2 * m + 1) // 6, 2),
    "octahedral n(2n^2+1)/3": (lambda m: m * (2 * m * m + 1) // 3, 1),
    "stella octangula n(2n^2-1)": (lambda m: m * (2 * m * m - 1), 1),
    "cube n^3": (lambda m: m ** 3, 1),
    "centred cube n^3+(n+1)^3": (lambda m: m ** 3 + (m + 1) ** 3, 1),
    "sum of cubes T_n^2": (lambda m: (m * (m + 1) // 2) ** 2, 2),
    "fourth power n^4": (lambda m: m ** 4, 1),
    "fifth power n^5": (lambda m: m ** 5, 1),
}
k = 14
M = 1 << k
oth = {}
for name, (f, per) in others.items():
    vals = [f(m) % M for m in range(per * M)]
    mult = np.bincount(np.array(vals), minlength=M)
    image = int((mult > 0).sum()) / M
    ms = sorted(set(int(x) // per if False else int(x) for x in np.unique(mult)))
    labs = np.bincount(lab_np[np.array([f(m) % (1 << K) for m in range(per * (1 << K))])], minlength=K + 1)
    natural = bool((labs == per * nat_vec).all())
    oth[name] = dict(image=image, mults=ms[:8], class_counts_natural=natural)
    out(f"  {name:34s} period 2^{k + per - 1}: image {image:.6f}  mults {str(ms[:6]):22s}"
        f"  dropping-class counts natural (K=16): {natural}")
res["other_families"] = oth

out("")
out(f"done in {time.time() - t0:.1f} s")
with open(os.path.join(HERE, "q22_polygonal.json"), "w", encoding="utf-8") as fh:
    json.dump(res, fh, indent=1)
out.close()
