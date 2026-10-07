"""Skeptic check 3: the square-triangular Pell orbit (Q2.3), independently of q23_pell.py.

Different code path: the sequences are generated from the Pell numbers P_n (0, 1, 2, 5, 12, ...) and the
half-companion numbers H_n (1, 1, 3, 7, 17, ...):  m_j = P_(2j)/2,  u_j = H_(2j);  minimal periods are found
without assuming they are powers of two (k <= 11); isometry is checked on ALL pairs, including negative j;
the dropping classes along the orbit are computed for 3x+1, 3x-1 and 5x+1 (the researcher only ran 3x+1
and asserted the others).

Run: C:/repos/collatz/.venv/Scripts/python.exe -X utf8 v3_pell.py
"""
import json
import os
import random
import statistics
import time
from math import isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v3_pell.log"), "w", encoding="utf-8")
RES = {}
T0 = time.time()


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


def v2(n):
    n = abs(n)
    assert n
    return (n & -n).bit_length() - 1


J = 5000
Pn, Hn = [0, 1], [1, 1]
for i in range(2, 2 * J + 3):
    Pn.append(2 * Pn[-1] + Pn[-2])
    Hn.append(2 * Hn[-1] + Hn[-2])
m = [Pn[2 * j] // 2 for j in range(J + 1)]
u = [Hn[2 * j] for j in range(J + 1)]
n = [(x - 1) // 2 for x in u]
N = [x * x for x in m]


def mj(j):          # extension to negative indices: eps^(-j) = u_j - m_j sqrt 8
    return m[j] if j >= 0 else -m[-j]


def uj(j):
    return u[abs(j)]


out("=" * 100)
out("A. Generation and identities (j <= 5000 where cheap)")
out("=" * 100)
ok = all(u[j] ** 2 - 8 * m[j] ** 2 == 1 and n[j] * (n[j] + 1) // 2 == N[j] for j in range(0, J + 1, 7))
out("  first terms m:", m[:6], " u:", u[:6], " n:", n[:6], " N:", N[:5])
out("  u^2 - 8m^2 = 1 and T_(n_j) = m_j^2 (every 7th j <= 5000):", ok)
ok_rec = all(m[j + 1] == 6 * m[j] - m[j - 1] and u[j + 1] == 3 * u[j] + 8 * m[j] for j in range(1, 2000))
out("  m_(j+1) = 6m_j - m_(j-1), u_(j+1) = 3u_j + 8m_j (j < 2000):", ok_rec)
R = 700
iso = True
prod = True
for a in range(-R, R + 1):
    for b in range(a + 1, R + 1):
        d = mj(b) - mj(a)
        iso &= v2(d) == v2(b - a)
        if (b - a) % 2 == 0:
            prod &= d == 2 * mj((b - a) // 2) * uj((a + b) // 2)
out(f"  v2(m_i - m_j) = v2(i - j) for ALL pairs -{R} <= i < j <= {R} (negative indices included):", iso)
out("  m_i - m_j = 2 m_((i-j)/2) u_((i+j)/2) on all those pairs with i = j mod 2:", prod)
out("  Bumby / Webb-Long criterion for uniform distribution mod 2^h of w_(j+1) = a w_j + b w_(j-1):")
out("     a = 2 mod 4, b = 3 mod 4, w_0 != w_1 mod 2.   Here a = 6, b = -1, (w_0, w_1) = (0, 1):",
    6 % 4 == 2 and (-1) % 4 == 3)
RES["A"] = dict(iso=iso, prod=prod)

out("")
out("=" * 100)
out("B. Minimal periods mod 2^k, brute force over EVERY candidate period (k <= 11), then powers of two (k <= 20)")
out("=" * 100)


def pred(kind, k):
    if kind == "m":
        return 1 << k
    if kind == "N":
        return 2 if k == 1 else 1 << (k - 1)
    if kind == "u":
        return 1 if k == 1 else (2 if k <= 4 else 1 << (k - 3))
    return 2 if k <= 3 else 1 << (k - 2)


def seqs_mod(k, L):
    M = 1 << (k + 1)                # u is needed mod 2^(k+1) to get n mod 2^k
    a, b = 1, 0
    U, Mm = [], []
    for _ in range(L):
        U.append(a)
        Mm.append(b)
        a, b = (3 * a + 8 * b) % M, (a + 3 * b) % M
    mod = 1 << k
    return ([x % mod for x in Mm], [x * x % mod for x in Mm], [x % mod for x in U],
            [((x - 1) // 2) % mod for x in U])


def min_period_any(x, maxP):
    L = len(x)
    for Pd in range(1, maxP + 1):
        if x[:L - Pd] == x[Pd:]:
            return Pd
    return None


okB = True
rows = []
for k in range(1, 21):
    if k <= 11:
        L = 4 << k
        s = seqs_mod(k, L)
        got = tuple(min_period_any(x, 2 << k) for x in s)
    else:
        L = 3 << k
        s = seqs_mod(k, L)
        got = []
        for x in s:
            Pd = 1
            while x[:L - Pd] != x[Pd:]:
                Pd *= 2
            got.append(Pd)
        got = tuple(got)
    want = (pred("m", k), pred("N", k), pred("u", k), pred("n", k))
    okB &= got == want
    rows.append((k,) + got)
out("   k: (per m, per N, per u, per n)")
out("  ", rows[:8])
out("  ", rows[8:14])
out("   all k = 1..20 as the README predicts:", okB)
RES["B_periods_ok"] = okB

out("")
out("=" * 100)
out("C. Closures: residues of n_j and u_j;  the README's '0 or 1 mod 8' sharpened")
out("=" * 100)
okC = True
for k in range(3, 17):
    mod = 1 << k
    mm, NN, UU, nn = seqs_mod(k, 1 << k)
    okC &= sorted(mm) == list(range(mod))
    okC &= sorted(NN) == sorted(x * x % mod for x in range(mod))
    half = mod // 2
    sq = {x * x % half for x in range(half)}
    full = {r for r in range(mod) if (r * (r + 1) // 2) % half in sq}
    got = set(nn)
    okC &= got == {r for r in full if r % 8 in (0, 1)}
    okC &= got | {(mod - 1 - r) for r in got} == full and not (got & {(mod - 1 - r) for r in got})
out("  k = 3..16: m_j permutation; N_j = multiset of squares; n_j residues = {0,1 mod 8 with T square};")
out("             union with NOT-image = all of {T_r square}, disjoint:", okC)
res_n = sorted({(n[j] % 16, j % 2) for j in range(0, 400)})
res_u = sorted({(u[j] % 32, j % 2) for j in range(0, 400)})
out("  (n_j mod 16, j mod 2) for j < 400:", res_n, "  -> n_j = 0 mod 8 (j even) or 1 mod 16 (j odd)")
out("  (u_j mod 32, j mod 2) for j < 400:", res_u, "  -> u_j = 1 mod 16 (j even) or 3 mod 32 (j odd)")
out("  the full 2-adic solution set of 'T_n is a square' lies in n = 0, 7 mod 8 and n = 1, 14 mod 16:",
    sorted({r % 16 for r in range(1 << 12) if (r * (r + 1) // 2) % (1 << 11) in {x * x % (1 << 11) for x in range(1 << 11)}}))
RES["C_ok"] = okC

out("")
out("=" * 100)
out("D. Dropping classes along the orbit, actual integers 2 <= j <= 600, for THREE rules")
out("   entry: number of distinct Terras stopping times seen for j even / j odd")
out("=" * 100)


def stop(x0, q, d, cap=200000):
    x, k = x0, 0
    while k < cap:
        x = (q * x + d) >> 1 if x & 1 else x >> 1
        k += 1
        if x < x0:
            return k
    return None


RES["D"] = {}
for (q, d) in ((3, 1), (3, -1), (5, 1)):
    for name, seq in (("N_j", N), ("n_j", n), ("u_j", u)):
        ev, od = {}, {}
        for j in range(2, 601):
            k = stop(seq[j], q, d)
            dd = ev if j % 2 == 0 else od
            dd[k] = dd.get(k, 0) + 1
        fmt = lambda h: dict(sorted(h.items(), key=lambda t: (t[0] is None, t[0]))) if len(h) <= 3 else \
            f"{len(h)} distinct values, top {sorted(h.items(), key=lambda t: -t[1])[:4]}"
        out(f"  {q}x{d:+d}  {name}:  j even: {fmt(ev)}   |  j odd: {fmt(od)}")
        RES["D"][f"{q}x{d:+d} {name}"] = dict(even=len(ev), odd=len(od))
out("  -> the two-class concentration (README Q2.3-d) is a 3x+1 statement.  For 3x-1 and 5x+1 the odd-index")
out("     terms (odd squares, 1 mod 8) and the u_j spread over many classes: 'still two' was not computed and is false.")

out("")
out("=" * 100)
out("E. What singles out 36")
out("=" * 100)
tri_j = [j for j in range(J + 1) if isqrt(8 * m[j] + 1) ** 2 == 8 * m[j] + 1]


def smooth3(x):
    while x % 2 == 0:
        x //= 2
    while x % 3 == 0:
        x //= 3
    return x == 1


sm_j = [j for j in range(1, J + 1) if smooth3(m[j])]
out(f"  j <= {J} with m_j triangular (Ljunggren): {tri_j};   with N_j 3-smooth: {sm_j}")
out("  The 3-smooth statement needs no search: N = T_n is 3-smooth iff n and n+1 are both 3-smooth, and")
out("  consecutive 3-smooth numbers are (1,2), (2,3), (3,4), (8,9) (Levi ben Gerson), so T_n in {1, 3, 6, 36};")
out("  the squares among these are 1 and 36.  Status: proved, not 'computed j <= 3000'.")
sm_tri = [t * (t + 1) // 2 for t in range(1, 2 * 10 ** 6) if smooth3(t) and smooth3(t + 1)]
out("  3-smooth triangular numbers with index < 2*10^6:", sm_tri)
# rank of apparition: 3 | m_j iff 2 | j ; 5 | m_j iff 3 | j ; so j >= 3 forces another prime
out("  3 | m_j <=> 2 | j:", all((m[j] % 3 == 0) == (j % 2 == 0) for j in range(1, 2000)),
    ";  v2(m_j) = v2(j):", all(v2(m[j]) == v2(j) for j in range(1, 2000)))
RES["E"] = dict(tri_j=tri_j, smooth_j=sm_j)

out("")
out("=" * 100)
out("F. Pythagorean-lift discriminants 4^k + 9^s: perfect squares, and never 2*square")
out("=" * 100)
sq_cells = [(k, s) for k in range(1, 300) for s in range(1, 200) if isqrt(4 ** k + 9 ** s) ** 2 == 4 ** k + 9 ** s]
out("  (k, s) with 1 <= k < 300, 1 <= s < 200 and 4^k + 9^s a perfect square:", sq_cells)
out("  proof: primitive triple (2^k, 3^s, y) => 2^k = 2ab, 3^s = a^2 - b^2 with b = 1, a = 2^(k-1);")
out("         (2^(k-1) - 1)(2^(k-1) + 1) = 3^s forces 2^(k-1) - 1 = 1.  So (2, 1) is the only cell, for all k, s.")
out("  4^8 + 9^5 =", 4 ** 8 + 9 ** 5, "(= D of Set_13 in scripts/pythagorean_lifts/README.md)")
RES["F_square_cells"] = sq_cells

out("")
out("=" * 100)
out("G. Null test re-run with a different seed, 30 controls per term (the researcher used 10), 5 <= j <= 160")
out("   controls: random integers with the same bit length and the same residue mod 16")
out("=" * 100)


def tst(x):
    c = 0
    while x != 1:
        x = (3 * x + 1) >> 1 if x & 1 else x >> 1
        c += 1
    return c


random.seed(8128)
RES["G"] = {}
for name, seq in (("u_j", u), ("n_j", n), ("m_j", m), ("N_j", N)):
    zs = []
    for j in range(5, 161):
        x = seq[j]
        bl = x.bit_length()
        ctr = []
        for _ in range(30):
            y = random.getrandbits(bl - 1) | (1 << (bl - 1))
            y = (y >> 4 << 4) | (x & 15)
            ctr.append(tst(y))
        mu, sd = statistics.mean(ctr), statistics.stdev(ctr)
        zs.append((tst(x) - mu) / sd)
    mz, sz = statistics.mean(zs), statistics.stdev(zs)
    out(f"  {name}: mean z = {mz:+.3f}, sd z = {sz:.3f}, standard error {sz / len(zs) ** 0.5:.3f}, "
        f"|mean| / se = {abs(mz) / (sz / len(zs) ** 0.5):.2f}")
    RES["G"][name] = dict(mean_z=mz, sd_z=sz)

out("")
out(f"done in {time.time() - T0:.1f} s")
with open(os.path.join(HERE, "v3_pell.json"), "w", encoding="utf-8") as fh:
    json.dump(RES, fh, indent=1, default=str)
LOG.close()
