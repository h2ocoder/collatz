"""Q2.3  Square-triangular numbers as a Pell orbit, seen 2-adically and through dropping classes.

    u^2 - 8 m^2 = 1,   u = 2n+1,   N = m^2 = T_n,   u_j + m_j sqrt(8) = (3 + sqrt 8)^j
    j :  0  1   2    3      4
    u :  1  3  17   99    577     (OEIS A001541)
    m :  0  1   6   35    204     (OEIS A001109)
    n :  0  1   8   49    288     (OEIS A001108)
    N :  0  1  36 1225  41616     (OEIS A001110)

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 q23_pell.py
Writes q23_pell.log / .json.  Conventions: common.py (Terras stopping time k, s odd steps,
repo Dropping Set index = k + s).
"""
import json
import os
import random
import statistics
import sys
import time
from math import isqrt

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import Tee, class_table, stop, tri, v2

out = Tee(os.path.join(HERE, "q23_pell.log"))
res = {}
t0 = time.time()

J = 400
u = [1, 3]
m = [0, 1]
for j in range(2, J + 1):
    u.append(6 * u[-1] - u[-2])
    m.append(6 * m[-1] - m[-2])
n = [(x - 1) // 2 for x in u]
N = [x * x for x in m]

# ------------------------------------------------------------------ A. identities
out("=" * 96)
out("A. Exact identities, checked for all 0 <= j <= 400 with Python integers")
out("=" * 96)
chk = {}
chk["pell u^2-8m^2=1"] = all(u[j] ** 2 - 8 * m[j] ** 2 == 1 for j in range(J + 1))
chk["N_j = T_(n_j) = m_j^2"] = all(tri(n[j]) == N[j] for j in range(J + 1))
chk["u_(j+1) = 3u_j + 8m_j"] = all(u[j + 1] == 3 * u[j] + 8 * m[j] for j in range(J))
chk["n_(j+1) = (3n_j+1) + 4m_j"] = all(n[j + 1] == 3 * n[j] + 1 + 4 * m[j] for j in range(J))
chk["n_(j-1) = (3n_j+1) - 4m_j"] = all(n[j - 1] == 3 * n[j] + 1 - 4 * m[j] for j in range(1, J + 1))
chk["n_(j+1)+n_(j-1) = 2(3n_j+1)"] = all(n[j + 1] + n[j - 1] == 2 * (3 * n[j] + 1) for j in range(1, J))
chk["n_(2i) = 8 m_i^2 and n_(2i)+1 = u_i^2"] = all(
    n[2 * i] == 8 * m[i] ** 2 and n[2 * i] + 1 == u[i] ** 2 for i in range(J // 2 + 1))
chk["n_(2i+1) = (u_i+4m_i)^2 and n_(2i+1)+1 = 2(u_i+2m_i)^2"] = all(
    n[2 * i + 1] == (u[i] + 4 * m[i]) ** 2 and n[2 * i + 1] + 1 == 2 * (u[i] + 2 * m[i]) ** 2
    for i in range(J // 2))
chk["v2(m_j) = v2(j)"] = all(v2(m[j]) == v2(j) for j in range(1, J + 1))
random.seed(1225)
pairs = [(random.randrange(J + 1), random.randrange(J + 1)) for _ in range(20000)]
chk["v2(m_i - m_j) = v2(i - j)   (isometry in j)"] = all(
    v2(m[a] - m[b]) == v2(a - b) for a, b in pairs if a != b)
chk["m_i - m_j = 2 m_((i-j)/2) u_((i+j)/2)  (i-j even)"] = all(
    m[a] - m[b] == 2 * m[(a - b) // 2] * u[(a + b) // 2] for a, b in pairs if a >= b and (a - b) % 2 == 0)
chk["u_(j+P) - u_j = 16 m_(P/2) m_(j+P/2)  (P even)"] = all(
    u[j + P] - u[j] == 16 * m[P // 2] * m[j + P // 2]
    for P in (2, 4, 6, 8, 16, 32, 64) for j in range(0, J - P))
chk["N_(j+P) - N_j = m_P m_(2j+P)"] = all(
    N[j + P] - N[j] == m[P] * m[2 * j + P] for P in (1, 2, 3, 4, 8, 16) for j in range(0, (J - P) // 2))
chk["u_j = 3^j mod 8"] = all((u[j] - 3 ** j) % 8 == 0 for j in range(J + 1))
for name, ok in chk.items():
    out(f"  {ok!s:5s}  {name}")
res["A_identities"] = chk

# ------------------------------------------------------------------ B. periods mod 2^k
out("")
out("=" * 96)
out("B. Minimal periods of the Pell sequences mod 2^k   (k = 1 .. 18)")
out("   predicted: m: 2^k ;  N=m^2: 2 (k=1), 2^(k-1) (k>=2) ;  u: 1,2,2,2 then 2^(k-3) (k>=5) ;")
out("              n=(u-1)/2: 2,2,2 then 2^(k-2) (k>=4)")
out("=" * 96)
KMAX = 18
BIG = 1 << (KMAX + 2)
L = (1 << (KMAX + 1)) + (1 << KMAX)          # > one state period mod 2^(KMAX+1) plus the largest shift
uu = np.empty(L, dtype=np.int64)
mm = np.empty(L, dtype=np.int64)
a, b = 1, 0
for j in range(L):
    uu[j] = a
    mm[j] = b
    a, b = (3 * a + 8 * b) % BIG, (a + 3 * b) % BIG
nn = ((uu - 1) // 2)          # valid mod 2^(KMAX+1)
NN = (mm * mm) % BIG


def min_period(x, mod):
    y = x % mod
    P = 1
    while P < len(y) // 2:
        if (y[:-P] == y[P:]).all():
            return P
        P *= 2
    return None


def pred(kind, k):
    if kind == "m":
        return 1 << k
    if kind == "N":
        return 2 if k == 1 else 1 << (k - 1)
    if kind == "u":
        return 1 if k == 1 else (2 if k <= 4 else 1 << (k - 3))
    if kind == "n":
        return 2 if k <= 3 else 1 << (k - 2)


per = {}
okper = True
out("    k    per(m)   per(N)   per(u)   per(n)   state(u,m)   all as predicted")
for k in range(1, KMAX + 1):
    M = 1 << k
    pm, pN, pu, pn = (min_period(mm, M), min_period(NN, M), min_period(uu, M), min_period(nn, M))
    st = 1
    while not (((uu[:-st] % M) == (uu[st:] % M)).all() and ((mm[:-st] % M) == (mm[st:] % M)).all()):
        st *= 2
    ok = (pm, pN, pu, pn) == (pred("m", k), pred("N", k), pred("u", k), pred("n", k))
    okper &= ok
    per[k] = dict(m=pm, N=pN, u=pu, n=pn, state=st)
    out(f"   {k:2d} {pm:8d} {pN:8d} {pu:8d} {pn:8d} {st:10d}        {ok}")
res["B_periods"] = {str(k): v for k, v in per.items()}
res["B_periods_as_predicted"] = okper

# ------------------------------------------------------------------ C. closures
out("")
out("=" * 96)
out("C. 2-adic closure of the orbit: which residues mod 2^k are hit?")
out("   m_j : predicted every residue exactly once per period 2^k (j -> m_j is an isometry of Z_2)")
out("   N_j : predicted the same multiset as { x^2 mod 2^k : 0 <= x < 2^k }")
out("   n_j : predicted set  { r : r = 0,1 mod 8  and  T_r mod 2^(k-1) is a square mod 2^(k-1) }")
out("         (= half of the 2-adic solution set {T_n is a square}; the other half is NOT(n_j))")
out("=" * 96)
out("    k   m perm  N=squares   #n_j res   predicted   equal    #/2^k     (1/12 = 0.083333)")
clo = {}
ok_clo = True
for k in range(3, KMAX + 1):
    M = 1 << k
    mk = mm[:M] % M
    m_perm = len(np.unique(mk)) == M
    Nk = np.sort(NN[:M] % M)
    x = np.arange(M, dtype=np.int64)
    sq = np.sort((x * x) % M)
    N_like_sq = bool((Nk == sq).all())
    nset = np.unique(nn[: per[k]["n"] * 2] % M)
    # predicted set
    half = M // 2
    xs = np.arange(half, dtype=np.int64)
    sqset = np.zeros(half, dtype=bool)
    sqset[(xs * xs) % half] = True
    r = np.arange(M, dtype=np.int64)
    tr = (r * (r + 1) // 2) % half
    predset = r[((r % 8 == 0) | (r % 8 == 1)) & sqset[tr]]
    eq = (len(predset) == len(nset)) and bool((predset == nset).all())
    # mirror half: NOT(n_j) residues
    notset = np.unique((M - 1 - nset) % M)
    full = r[sqset[tr]]
    union_ok = bool((np.union1d(nset, notset) == full).all()) and len(np.intersect1d(nset, notset)) == 0
    ok_clo &= m_perm and N_like_sq and eq and union_ok
    clo[k] = dict(m_perm=m_perm, N_like_squares=N_like_sq, n_residues=int(len(nset)),
                  predicted=int(len(predset)), equal=eq, union_with_NOT_is_full_solution_set=union_ok,
                  full=int(len(full)))
    out(f"   {k:2d}   {m_perm!s:5s}   {N_like_sq!s:5s}   {len(nset):9d}   {len(predset):9d}   {eq!s:5s}"
        f"   {len(nset) / M:.6f}   n_j u NOT(n_j) = all of {{T_r square}} ({len(full)}): {union_ok}")
res["C_closure"] = {str(k): v for k, v in clo.items()}
res["C_all_ok"] = ok_clo
out("  all predictions hold for k = 3..18:", ok_clo)

# multiplicity law for n_j over one period (how non-uniform is the orbit on its support?)
k = 14
M = 1 << k
vals = nn[: per[k]["n"]] % M
_, mult = np.unique(vals, return_counts=True)
mh = dict(zip(*[x.tolist() for x in np.unique(mult, return_counts=True)]))
out(f"  multiplicities of n_j mod 2^{k} over one period ({per[k]['n']} terms): {mh}  (not uniform: j -> n_j is even in j)")
res["C_n_multiplicities_k14"] = {str(a): b for a, b in mh.items()}

# ------------------------------------------------------------------ D. dropping classes of the actual integers
out("")
out("=" * 96)
out("D. Dropping classes along the Pell orbit, actual integers, 2 <= j <= 400")
out("   entry = (Terras k, odd steps s); repo Dropping Set index = k+s")
out("=" * 96)


def classes(seq, j0=2):
    even, odd = {}, {}
    for j in range(j0, J + 1):
        r = stop(seq[j])
        d = even if j % 2 == 0 else odd
        d[r] = d.get(r, 0) + 1
    return even, odd


res["D"] = {}
for name, seq in (("u_j", u), ("n_j", n), ("N_j = m_j^2", N)):
    ev, od = classes(seq)
    out(f"  {name:12s} j even: {ev}    j odd: {od}")
    res["D"][name] = dict(even={str(a): b for a, b in ev.items()}, odd={str(a): b for a, b in od.items()})
# the roots m_j: exactly natural over j mod 2^K
K = 16
lab, cnat = class_table(K)
lab_np = np.array(lab)
cm = np.bincount(lab_np[mm[: 1 << K] % (1 << K)], minlength=K + 1)
nat = np.array([cnat.get(i, 0) for i in range(K + 1)])
out(f"  roots m_j, j in [0, 2^{K}): class counts equal the natural counts N(k) 2^(K-k) exactly:",
    bool((cm == nat).all()))
res["D"]["m_j_natural_K16"] = bool((cm == nat).all())
hm = {}
for j in range(2, J + 1):
    r = stop(m[j])
    hm[r[0]] = hm.get(r[0], 0) + 1
out(f"  roots m_j actual stopping times, j = 2..{J}: {dict(sorted(hm.items()))}")
out("     natural expectation for 399 numbers: k=1: 199.5, k=2: 99.8, k=4: 24.9, k=5: 24.9, k=7: 9.4, k=8: 10.9")
res["D"]["m_j_actual_hist"] = {str(a): b for a, b in sorted(hm.items())}

# ------------------------------------------------------------------ E. total stopping times vs controls
out("")
out("=" * 96)
out("E. Null test: total stopping time (T-steps to reach 1) along the Pell orbit, 5 <= j <= 200,")
out("   against 10 random integers with the same bit length and the same residue mod 16.")
out("   z = (tst - mean_control)/sd_control ; report mean z and sd of z (null: mean 0, sd 1)")
out("=" * 96)


def tst(x):
    c = 0
    while x != 1:
        x = (3 * x + 1) >> 1 if x & 1 else x >> 1
        c += 1
    return c


random.seed(41616)
res["E"] = {}
for name, seq in (("u_j", u), ("n_j", n), ("m_j", m), ("N_j", N)):
    zs = []
    ratio = []
    for j in range(5, 201):
        x = seq[j]
        bl = x.bit_length()
        ctr = []
        for _ in range(10):
            y = random.getrandbits(bl - 1) | (1 << (bl - 1))
            y = (y >> 4 << 4) | (x & 15)
            ctr.append(tst(y))
        mu, sd = statistics.mean(ctr), statistics.pstdev(ctr)
        t = tst(x)
        ratio.append(t / bl)
        if sd > 0:
            zs.append((t - mu) / sd)
    mz, sz = statistics.mean(zs), statistics.pstdev(zs)
    out(f"  {name:5s}  mean z = {mz:+.3f}   sd z = {sz:.3f}   (se of mean ~ {sz / len(zs) ** 0.5:.3f})"
        f"   mean T-steps per bit = {statistics.mean(ratio):.4f}   (heuristic 1/(1 - log2(3)/2) = 4.8187)")
    res["E"][name] = dict(mean_z=mz, sd_z=sz, steps_per_bit=statistics.mean(ratio))

# ------------------------------------------------------------------ F. what singles out 36
out("")
out("=" * 96)
out("F. What singles out j = 2 (N = 36)?")
out("=" * 96)
JJ = 3000
uu2, mm2 = [1, 3], [0, 1]
for j in range(2, JJ + 1):
    uu2.append(6 * uu2[-1] - uu2[-2])
    mm2.append(6 * mm2[-1] - mm2[-2])


def is_tri(x):
    r = isqrt(8 * x + 1)
    return r * r == 8 * x + 1


def smooth3(x):
    for p in (2, 3):
        while x % p == 0:
            x //= p
    return x == 1


tri_roots = [j for j in range(JJ + 1) if is_tri(mm2[j])]
out(f"  (Ljunggren 1946) j <= {JJ} with m_j triangular, i.e. N_j = (triangular)^2 = sum of cubes: {tri_roots}"
    f"  -> m = {[mm2[j] for j in tri_roots]}, N = {[mm2[j] ** 2 for j in tri_roots]}")
sm = [j for j in range(1, JJ + 1) if smooth3(mm2[j])]
out(f"  j <= {JJ} with N_j 3-smooth: {sm}  -> N = {[mm2[j] ** 2 for j in sm]}")
out("  n_2 = 8 = 8*m_1^2, n_2 + 1 = 9 = u_1^2 : the pair (8, 9) IS the fundamental solution 3^2 - 8*1^2 = 1")
res["F_m_triangular_j"] = tri_roots
res["F_N_3smooth_j"] = sm

# ------------------------------------------------------------------ G. Pythagorean-lift Pell problems live elsewhere
out("")
out("=" * 96)
out("G. Relation to the repo's Pythagorean lifts (scripts/pythagorean_lifts): none beyond 'both are conics'")
out("   lift discriminant of the cell (k, s) is D = 4^k + 9^s (n^2 + ((3^s n + c)/2^k)^2 = y^2);")
out("   square-triangular numbers live in Q(sqrt 2).  4^k + 9^s is odd, so never 2*square.")
out("=" * 96)
cells = []
k_of_s = lambda s: len(bin(3 ** s)) - 2          # A020914
for s in range(1, 9):
    k = k_of_s(s)
    D = 4 ** k + 9 ** s
    r = isqrt(D)
    cells.append((k, s, k + s, D, r * r == D))
    out(f"   cell k={k:2d} s={s}  (repo Set_{k + s})   D = 4^k + 9^s = {D}   perfect square: {r * r == D}")
res["G_lift_discriminants"] = cells
out("   only Set_3 (k=2, s=1) is degenerate: 4^2 + 3^2 = 5^2, the (3,4,5) triple.")

# ------------------------------------------------------------------ H. is the midpoint identity special to 3?
out("")
out("=" * 96)
out("H. Mirror / control for the identity  n_(j+1) + n_(j-1) = 2 (3 n_j + 1)")
out("   For any odd q the unit q + sqrt(q^2-1) has trace 2q, so with u = (q-1) n + 1 (centre -1/(q-1),")
out("   where n -> q n + 1 is u -> q u) the same identity holds with q n + 1.  q = 3 is not singled out.")
out("=" * 96)
ctrl = {}
for q in (3, 5, 7, 9):
    D = q * q - 1
    uq, yq = [1, q], [0, 1]
    for j in range(2, 40):
        uq.append(2 * q * uq[-1] - uq[-2])
        yq.append(2 * q * yq[-1] - yq[-2])
    pell = all(a * a - D * b * b == 1 for a, b in zip(uq, yq))
    integral = all((a - 1) % (q - 1) == 0 for a in uq)
    nq = [(a - 1) // (q - 1) for a in uq] if integral else None
    mid = integral and all(nq[j + 1] + nq[j - 1] == 2 * (q * nq[j] + 1) for j in range(1, 38))
    ctrl[q] = dict(pell=pell, integral=integral, midpoint=bool(mid), first_n=nq[:6] if nq else None)
    out(f"   q={q}: u^2 - {D} y^2 = 1, unit {q}+sqrt({D});  n = (u-1)/{q - 1} integral for all j: {integral};"
        f"  n_j = {nq[:6] if nq else None};  n_(j+1)+n_(j-1) = 2({q}n_j+1): {mid}")
out("   mirror (3x-1): with n' = n + 1 (so N = T_(n'-1)) the identity reads n'_(j+1) + n'_(j-1) = 2(3n'_j - 1):",
    all((n[j + 1] + 1) + (n[j - 1] + 1) == 2 * (3 * (n[j] + 1) - 1) for j in range(1, J)))
res["H_control"] = ctrl

out("")
out(f"done in {time.time() - t0:.1f} s")
with open(os.path.join(HERE, "q23_pell.json"), "w", encoding="utf-8") as fh:
    json.dump(res, fh, indent=1, default=str)
out.close()
