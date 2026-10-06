"""Q2.1  Triangular numbers, squares, cubes and sums of cubes as maps on Z/2^k,
and the exact number of them in each dropping class.

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 q21_figurate_residues.py
Writes q21_figurate_residues.log and q21_figurate_residues.json next to this file.

Conventions: see common.py.  Classes are indexed by the Terras stopping time k
(shortcut map); the repo's Dropping Set index is k + s.
"""
import json
import os
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..")))

from common import (A020914, A100982, Tee, class_table, cst, primitive_counts,
                    stop, tri, v2)

out = Tee(os.path.join(HERE, "q21_figurate_residues.log"))
res = {}
t0 = time.time()

# ---------------------------------------------------------------- A. CRS property
out("=" * 78)
out("A. T_0 .. T_(2^k - 1) is a complete residue system mod 2^k   (theorem 1)")
out("   B. over a full period n mod 2^(k+1) every residue mod 2^k is hit exactly twice,")
out("      and the two preimages are n and NOT(n) = 2^(k+1) - 1 - n            (fold)")
out("=" * 78)
crs_ok = []
for k in range(1, 23):
    M = 1 << k
    n = np.arange(M, dtype=np.int64)
    t = (n * (n + 1) // 2) % M
    is_crs = len(np.unique(t)) == M
    n2 = np.arange(2 * M, dtype=np.int64)
    t2 = (n2 * (n2 + 1) // 2) % M
    mult = np.bincount(t2, minlength=M)
    twice = bool((mult == 2).all())
    fold = bool((t2 == t2[::-1]).all())          # T_n == T_(2M-1-n) mod M
    crs_ok.append((k, is_crs, twice, fold))
    if k <= 6 or k % 4 == 0 or k == 22:
        out(f"  k={k:2d}  CRS on [0,2^k): {is_crs}   every residue twice on [0,2^(k+1)): {twice}"
            f"   T_n = T_NOT(n): {fold}")
res["A_crs_all_true_k_1_22"] = all(a and b and c for _, a, b, c in crs_ok)
out("  all k = 1..22:", res["A_crs_all_true_k_1_22"])

# ---------------------------------------------------------------- C. squares
out("")
out("=" * 78)
out("C. Squares: collapse.  #squares mod 2^k (OEIS A023105) and the odd squares")
out("=" * 78)


def n_squares_formula(k):
    # closed form for the number of squares mod 2^k (k>=1): see README, theorem 2
    # even k: (2^(k-1) + 4)/3 ;  odd k: (2^(k-1) + 5)/3
    return ((1 << (k - 1)) + (4 if k % 2 == 0 else 5)) // 3


sq_rows = []
for k in range(1, 23):
    M = 1 << k
    n = np.arange(M, dtype=np.int64)
    sq = (n * n) % M
    nsq = len(np.unique(sq))
    odd = sq[1::2]
    odd_vals, odd_mult = np.unique(odd, return_counts=True)
    all_1mod8 = bool((odd_vals % 8 == 1).all()) if k >= 3 else None
    expected_odd = M // 8 if k >= 3 else None
    four_to_one = bool((odd_mult == 4).all()) if k >= 3 else None
    sq_rows.append((k, nsq, n_squares_formula(k), all_1mod8, len(odd_vals), expected_odd, four_to_one))
    if k <= 8 or k % 4 == 0 or k == 22:
        out(f"  k={k:2d}  #squares={nsq:8d}  formula={n_squares_formula(k):8d}  ratio={nsq / M:.6f}"
            f"   odd squares all = 1 mod 8: {all_1mod8}, #={len(odd_vals)} (2^k/8={expected_odd}),"
            f" each hit 4x by odd n: {four_to_one}")
res["C_squares_formula_ok"] = all(r[1] == r[2] for r in sq_rows)
res["C_odd_squares_ok"] = all(r[3] and r[4] == r[5] and r[6] for r in sq_rows if r[0] >= 3)
out("  formula matches for k=1..22:", res["C_squares_formula_ok"],
    "   odd-square statement k=3..22:", res["C_odd_squares_ok"], "   limit ratio 1/6 =", 1 / 6)

# ---------------------------------------------------------------- D. cubes
out("")
out("=" * 78)
out("D. Cubes: x -> x^3 permutes the odd residues mod 2^k and is a 2-adic isometry on units")
out("=" * 78)
cube_ok = True
for k in range(1, 21):
    M = 1 << k
    odd = list(range(1, M, 2))
    img = {pow(x, 3, M) for x in odd}
    ok = (len(img) == len(odd)) and all(y & 1 for y in img)
    cube_ok &= ok
    if k <= 5 or k % 5 == 0:
        out(f"  k={k:2d}  odd cubes distinct mod 2^k: {ok}  ({len(img)} of {len(odd)})")
random.seed(36)
iso_ok = True
for _ in range(200000):
    a = random.getrandbits(80) | 1
    b = random.getrandbits(80) | 1
    if a == b:
        continue
    iso_ok &= v2(a ** 3 - b ** 3) == v2(a - b)
out("  permutation for k=1..20:", cube_ok, "   v2(a^3-b^3) = v2(a-b) on 200000 random odd 80-bit pairs:", iso_ok)
res["D_cube_perm_ok"] = cube_ok
res["D_cube_isometry_ok"] = iso_ok
# even cubes: v2(n^3) = 3 v2(n)
res["D_even_cube_val"] = all(v2(n ** 3) == 3 * v2(n) for n in range(2, 5000, 2))

# ---------------------------------------------------------------- E. class counts vs A100982
out("")
out("=" * 78)
out("E. Dropping classes as residue classes: N(k) = #{r mod 2^k : cst(r) = k}")
out("   Terras stopping time k (shortcut map).  s = number of odd steps.  repo Set index = k+s")
out("=" * 78)
K = 20
lab, counts = class_table(K)
N = {k: counts[k] >> (K - k) for k in sorted(counts) if k}
ks = sorted(N)
out("   s   k=A020914(s)  k+s(repo)   N(k)   A100982(s)   density N(k)/2^k")
match = True
for i, k in enumerate(ks):
    s = i  # s = 0 for k = 1
    oe = 1 if s == 0 else A100982[s - 1]
    match &= (N[k] == oe) and (k == A020914[s])
    out(f"  {s:2d}   {k:3d}          {k + s:3d}      {N[k]:6d}   {oe:6d}       {N[k] / 2 ** k:.8f}")
und = counts.get(0, 0)
out(f"  residues mod 2^{K} with cst > {K} (undetermined at this level): {und}  = {und / 2 ** K:.6f}")
out("  N(k) equals A100982 (with the s=0 class 'even' prepended) and k = A020914(s):", match)
res["E_N"] = {str(k): N[k] for k in ks}
res["E_matches_A100982"] = match
res["E_undetermined_mod_2^20"] = und

# ---------------------------------------------------------------- F. exact counts along the families
out("")
out("=" * 78)
out("F. Exact class counts among the first 2^K terms (residue level, cst of value mod 2^K)")
out("   families: T_n, n^2, n^3, T_n^2 = 1^3+...+n^3 (Nicomachus), for n = 0 .. 2^K - 1")
out("=" * 78)


def family_counts(K, lab, f):
    M = 1 << K
    c = {}
    for n in range(M):
        k = lab[f(n) % M]
        c[k] = c.get(k, 0) + 1
    return c


fams = {
    "T_n": tri,
    "n^2": lambda n: n * n,
    "n^3": lambda n: n * n * n,
    "T_n^2": lambda n: tri(n) ** 2,
}
res["F"] = {}
for Kf in (8, 12, 16, 20):
    if Kf == K:
        labf, cf = lab, counts
    else:
        labf, cf = class_table(Kf)
    out(f"  --- K = {Kf}:  natural count N(k)*2^(K-k) versus count of family values in class k (k=0: cst > K)")
    fc = {name: family_counts(Kf, labf, f) for name, f in fams.items()}
    allk = sorted(cf)
    out("     k    natural " + "".join(f"{name:>10s}" for name in fams))
    for k in allk:
        out(f"   {k:3d} {cf[k]:10d} " + "".join(f"{fc[name].get(k, 0):10d}" for name in fams))
    eq_T = fc["T_n"] == cf
    eq_cube = fc["n^3"] == cf
    sq_two = set(fc["n^2"]) == {1, 2} and fc["n^2"][1] == fc["n^2"][2] == (1 << (Kf - 1))
    sc_two = set(fc["T_n^2"]) == {1, 2} and fc["T_n^2"][1] == fc["T_n^2"][2] == (1 << (Kf - 1))
    out(f"     T_n exactly natural: {eq_T}   n^3 exactly natural: {eq_cube}   "
        f"n^2 half/half on k=1,2: {sq_two}   T_n^2 half/half on k=1,2: {sc_two}")
    res["F"][str(Kf)] = dict(T_exact=eq_T, cube_exact=eq_cube, square_two_classes=sq_two,
                             sumcubes_two_classes=sc_two)

# ---------------------------------------------------------------- G. actual integers up to 2^20 (> 10^6)
out("")
out("=" * 78)
out("G. Actual stopping times of the integers T_n, n^2, n^3, T_n^2 for 2 <= n < 2^20 = 1048576")
out("   (Terras stopping time k of the VALUE; column 'natural' = all integers m in [2, 2^20))")
out("   also the same for 2 <= n <= 10^6 in the json file")
out("=" * 78)
L = 1 << 20


def hist(values):
    h = {}
    bad = 0
    for x in values:
        r = stop(x)
        if r is None:
            bad += 1
            continue
        h[r[0]] = h.get(r[0], 0) + 1
    return h, bad


res["G"] = {}
H = {}
H["natural"], bad_nat = hist(range(2, L))
for name, f in fams.items():
    H[name], b = hist(f(n) for n in range(2, L))
    res["G"][name + "_no_drop"] = b
allk = sorted(set().union(*[set(h) for h in H.values()]))
out("     k   k+s   density      natural        T_n        n^2        n^3      T_n^2    exact N(k)2^(20-k)")
for k in allk:
    s = ks.index(k) if k in ks else None
    dens = N[k] / 2 ** k if k in N else float("nan")
    exact = (N[k] << (20 - k)) if (k in N and k <= 20) else ""
    out(f"   {k:3d}  {'' if s is None else k + s:>4}  {dens:.7f} "
        + "".join(f"{H[c].get(k, 0):11d}" for c in ("natural", "T_n", "n^2", "n^3", "T_n^2"))
        + f"    {exact}")
tot = {c: sum(H[c].values()) for c in H}
out("   totals:", tot)
# exactness check for triangular numbers: for k <= 20 the count over n in [0, 2^20) is exactly N(k) 2^(20-k);
# n = 0, 1 give T = 0, 1 (residue classes k=1 and k=2) which never drop, so subtract them.
exact_T = True
for k in allk:
    if k <= 20:
        want = (N[k] << (20 - k)) - (1 if k in (1, 2) else 0)
        exact_T &= H["T_n"].get(k, 0) == want
out("   T_n counts equal N(k)*2^(20-k) for every k <= 20 (minus the two non-dropping values T_0=0, T_1=1):", exact_T)
# the same exactness for the natural column and for cubes
exact_nat = all(H["natural"].get(k, 0) == (N[k] << (20 - k)) - (1 if k in (1, 2) else 0)
                for k in allk if k <= 20)
exact_cube = all(H["n^3"].get(k, 0) == (N[k] << (20 - k)) - (1 if k in (1, 2) else 0)
                 for k in allk if k <= 20)
out("   natural column exact in the same sense:", exact_nat, "   n^3 column exact in the same sense:", exact_cube)
res["G"]["T_exact_k_le_20"] = exact_T
res["G"]["natural_exact_k_le_20"] = exact_nat
res["G"]["cube_exact_k_le_20"] = exact_cube
res["G"]["hist_2^20"] = {c: {str(k): v for k, v in sorted(h.items())} for c, h in H.items()}

# n <= 10^6 version (the range named in the task)
H6 = {}
H6["natural"], _ = hist(range(2, 10 ** 6 + 1))
for name, f in fams.items():
    H6[name], _ = hist(f(n) for n in range(2, 10 ** 6 + 1))
res["G"]["hist_10^6"] = {c: {str(k): v for k, v in sorted(h.items())} for c, h in H6.items()}
out("   n <= 10^6: max |freq(T_n) - density| over k <= 16:",
    max(abs(H6["T_n"].get(k, 0) / (10 ** 6 - 1) - N[k] / 2 ** k) for k in ks if k <= 16))
out("   n <= 10^6: max |freq(n^3) - density| over k <= 16:",
    max(abs(H6["n^3"].get(k, 0) / (10 ** 6 - 1) - N[k] / 2 ** k) for k in ks if k <= 16))
out("   n <= 10^6: squares  k=1:", H6["n^2"].get(1), " k=2:", H6["n^2"].get(2),
    " other:", sum(v for k, v in H6["n^2"].items() if k > 2))
out("   n <= 10^6: T_n^2    k=1:", H6["T_n^2"].get(1), " k=2:", H6["T_n^2"].get(2),
    " other:", sum(v for k, v in H6["T_n^2"].items() if k > 2))

# ---------------------------------------------------------------- H. repo functions, modulus 2^16
out("")
out("=" * 78)
out("H. Check with the repo's own functions (collatz.dropping.dropping_time), modulus 2^16")
out("   repo dropping time = k + s (un-shortcut steps).  T_n for 2 <= n < 2^16.")
out("=" * 78)
from collatz.dropping import dropping_time, dropping_destination  # noqa: E402

K16 = 16
lab16, c16 = class_table(K16)
repo_hist = {}
mism = 0
for n in range(2, 1 << K16):
    t = tri(n)
    dt = dropping_time(t)
    k, s = stop(t)
    if dt != k + s:
        mism += 1
    repo_hist[dt] = repo_hist.get(dt, 0) + 1
nat_hist = {}
for m in range(2, 1 << K16):
    dt = dropping_time(m)
    nat_hist[dt] = nat_hist.get(dt, 0) + 1
out("   repo dropping_time(T_n) == k+s from common.stop for all n:", mism == 0)
out("   Set index j=k+s   #T_n (2<=n<2^16)   #integers m (2<=m<2^16)   N(k)*2^(16-k)")
N16 = {k: c16[k] >> (K16 - k) for k in c16 if k}
k_of_j = {k + i: k for i, k in enumerate(sorted(N16))}
same_for_resolved = True
for j in sorted(set(repo_hist) | set(nat_hist)):
    k = k_of_j.get(j)
    exact = (N16[k] << (K16 - k)) if k else ""
    if k:
        want = exact - (1 if k in (1, 2) else 0)
        same_for_resolved &= repo_hist.get(j, 0) == want == nat_hist.get(j, 0)
    if j <= 40:
        out(f"       {j:3d}          {repo_hist.get(j, 0):8d}            {nat_hist.get(j, 0):8d}            {exact}")
out("   for every class of modulus <= 2^16 the two repo counts agree with N(k)*2^(16-k) (minus T=0,1):",
    same_for_resolved)
res["H_repo_matches"] = bool(mism == 0 and same_for_resolved)

# ---------------------------------------------------------------- I. mirror test
out("")
out("=" * 78)
out("I. Mirror test: the same count for the rules 3x-1 and 5x+1 (K = 16)")
out("   If T_n is 'natural' for every rule, the statement cannot see the rule at all.")
out("=" * 78)
res["I"] = {}
for (q, d) in ((3, 1), (3, -1), (5, 1), (5, -1), (7, 1)):
    labq, cq = class_table(16, q, d)
    fT = {}
    fC = {}
    for n in range(1 << 16):
        a = labq[tri(n) % (1 << 16)]
        fT[a] = fT.get(a, 0) + 1
        b = labq[pow(n, 3, 1 << 16)]
        fC[b] = fC.get(b, 0) + 1
    Nq = {k: cq[k] >> (16 - k) for k in sorted(cq) if k}
    out(f"   rule {q}x{d:+d}: classes k = {list(Nq)[:8]}..., N(k) = {list(Nq.values())[:8]}...,"
        f" undetermined {cq.get(0, 0)};  T_n natural: {fT == cq};  n^3 natural: {fC == cq}")
    res["I"][f"{q}x{d:+d}"] = dict(T_natural=fT == cq, cube_natural=fC == cq,
                                   N={str(k): v for k, v in Nq.items()})

out("")
out(f"done in {time.time() - t0:.1f} s")
with open(os.path.join(HERE, "q21_figurate_residues.json"), "w", encoding="utf-8") as fh:
    json.dump(res, fh, indent=1)
out.close()
