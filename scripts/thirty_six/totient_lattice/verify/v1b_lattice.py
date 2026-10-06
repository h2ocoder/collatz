"""Skeptic check of Q4.1-d (large table), Q4.1-e/f (growth, ridge, critical slope), Q4.1-g (Pierpont
points).  Independent code path:

  * primality of every 2^i 3^j + 1 in the 480 x 300 box by sympy.isprime (BPSW) after my own trial
    division -- the researcher used Lucas certificates;
  * the table A(a,b), a <= 480, b <= 300, EXACTLY (Python integers packed row-wise with 128-bit
    limbs; the researcher's large table is float64);
  * ridge by a different estimator (integer a, linear interpolation in b only, local quadratic);
  * random controls with another seed and another DP;
  * sensitivity of the 'fitted sqrt(L) coefficient' to the form of the fit.

Run:  python -X utf8 v1b_lattice.py      (about 3-4 minutes)
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np
from sympy import isprime, primerange

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
LOG = open(os.path.join(HERE, "v1b_lattice.log"), "w", encoding="utf-8")
LN2, LN3 = math.log(2), math.log(3)
AM, BM = 480, 300
LIMB = 128
MASK = (1 << (LIMB * (BM + 1))) - 1


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")


def exact_table(points):
    """A[a][b] exact, via packed rows."""
    rows = [0] * (AM + 1)
    rows[0] = 1
    for i, j in points:
        sh = LIMB * j
        for a in range(AM, i - 1, -1):
            r = rows[a - i]
            if r:
                rows[a] += (r << sh) & MASK
    # E = D + cumulative sum over a   (factor 1 + 1/(1-X))
    E = []
    run = 0
    for a in range(AM + 1):
        run += rows[a]
        E.append(rows[a] + run)
    lm = (1 << LIMB) - 1

    def unpack(x):
        return [(x >> (LIMB * b)) & lm for b in range(BM + 1)]
    Eu = [unpack(e) for e in E]
    A = [Eu[0][:]]
    for a in range(1, AM + 1):
        cs, row = 0, []
        for b in range(BM + 1):
            cs += Eu[a - 1][b]                 # factor 1 + X/(1-Y)
            row.append(Eu[a][b] + cs)
        A.append(row)
    D = [unpack(r) for r in rows]
    return D, A


def float_table(points):
    D = np.zeros((AM + 1, BM + 1))
    D[0, 0] = 1.0
    for i, j in points:
        D[i:, j:] += D[: AM + 1 - i, : BM + 1 - j].copy()
    E = D + np.cumsum(D, axis=0)
    A = E.copy()
    A[1:, :] += np.cumsum(E[:-1, :], axis=1)
    return A


def ridge_1d(lnA, L):
    """argmax over theta of ln A on X + Y = L: integer a, linear interpolation in b; local quadratic fit."""
    th, val = [], []
    for a in range(1, AM):
        b = (L - a * LN2) / LN3
        if not (1 <= b < BM - 1):
            continue
        j = int(math.floor(b))
        f = b - j
        v = (1 - f) * lnA[a][j] + f * lnA[a][j + 1]
        th.append(a * LN2 / L)
        val.append(v)
    th, val = np.array(th), np.array(val)
    k = int(np.argmax(val))
    sel = np.abs(th - th[k]) <= 0.12
    co = np.polyfit(th[sel], val[sel], 2)
    return float(-co[1] / (2 * co[0])), float(np.polyval(co, -co[1] / (2 * co[0])))


def main():
    t0 = time.time()
    with open(os.path.join(PARENT, "q41_pierpont_points_480x300.json"), encoding="utf-8") as f:
        theirs = sorted(tuple(p) for p in json.load(f))
    out(f"researcher's Pierpont points in the box 1 <= i <= {AM}, 0 <= j <= {BM}: {len(theirs)}")

    # ------------------------------------------------------------------ independent primality
    small = list(primerange(5, 2000))
    mine = []
    tested = 0
    for i in range(1, AM + 1):
        p2 = 1 << i
        p3 = 1
        for j in range(0, BM + 1):
            if (i, j) != (1, 0):
                N = p2 * p3 + 1
                if N < 4_000_000:
                    if isprime(N):
                        mine.append((i, j))
                elif all(N % q for q in small):
                    tested += 1
                    if isprime(N):
                        mine.append((i, j))
            p3 *= 3
    mine.sort()
    out(f"independent test (trial division by primes < 2000, then sympy BPSW on {tested} survivors): {len(mine)} primes;"
        f" same set: {mine == theirs}   [{time.time() - t0:.0f} s]")
    assert mine == theirs

    # counts against the literature (Wikipedia 'Pierpont prime': 42, 65, 157, 795 below 10^6, 10^9, 10^20, 10^100;
    # these counts include the primes 2 and 3)
    def count_below(X):
        return 2 + sum(1 for i, j in mine if (1 << i) * 3 ** j + 1 < X)
    cs = [count_below(10 ** e) for e in (6, 9, 20, 100)]
    out(f"Pierpont primes below 10^6, 10^9, 10^20, 10^100 (with 2 and 3): {cs}   (literature: [42, 65, 157, 795])")
    assert cs == [42, 65, 157, 795]
    out(f"  per decade up to 10^100: {cs[3] / 100:.2f};  Gleason's heuristic 9 per decade = 3 ln 10/(ln 2 ln 3) = {3 * math.log(10) / (LN2 * LN3):.2f}")
    out("  => 'about 8 per decade, below Gleason's 9' is already visible in the published counts (not new).")
    Lcap = min(AM * LN2, BM * LN3)
    inside = [(i, j) for i, j in mine if i * LN2 + j * LN3 <= Lcap]
    sx = sum(i * LN2 for i, j in inside)
    sy = sum(j * LN3 for i, j in inside)
    sd = math.sqrt(sum((i * LN2 + j * LN3) ** 2 for i, j in inside) / 12) / (sx + sy)
    out(f"points with ln(p-1) <= {Lcap:.2f}: {len(inside)};  sum i ln2 = {sx:.1f}, sum j ln3 = {sy:.1f}, theta_cm = {sx / (sx + sy):.4f} +- {sd:.4f}")
    out("  theta_cm for cutoffs U = 20, 30, ..., 320 (it wanders by several sd-of-the-final-value; 0.4996 is one draw):")
    out("   ", [round(sum(i * LN2 for i, j in inside if i * LN2 + j * LN3 <= U) /
                      sum(i * LN2 + j * LN3 for i, j in inside if i * LN2 + j * LN3 <= U), 3) for U in range(20, 330, 30)])
    kappa = len(inside) / Lcap
    out(f"  kappa = {kappa:.4f}")

    # ------------------------------------------------------------------ exact table
    D, A = exact_table(mine)
    out(f"\nexact table A(a,b), a <= {AM}, b <= {BM} built   [{time.time() - t0:.0f} s];  largest entry has {A[AM][BM].bit_length()} bits (< {LIMB})")
    assert max(max(r) for r in A).bit_length() < LIMB - 1
    with open(os.path.join(PARENT, "q41_table.json"), encoding="utf-8") as f:
        ex = json.load(f)
    bad = sum(1 for a in range(41) for b in range(41) if A[a][b] != ex["A"][a][b] or D[a][b] != ex["D"][a][b])
    out(f"  agreement with the researcher's exact 41 x 41 table (A and D): mismatches {bad}")
    assert bad == 0
    lnA = [[math.log(v) if v > 0 else float("-inf") for v in row] for row in A]
    out("  values quoted in q41_rays.log:  ln A(480,300) = %.2f (76.75);  ln A(480,240) = %.3f (72.361);  ln A(476,300) = %.3f (76.554);"
        % (lnA[480][300], lnA[480][240], lnA[476][300]))
    out("                                  ln A(300,300) = %.3f (65.997);  ln A(160,101) = %.3f (40.906);  ln A(120,300) = %.3f (47.171)"
        % (lnA[300][300], lnA[160][101], lnA[120][300]))
    Af = float_table(mine)
    rel = max(abs(Af[a, b] - A[a][b]) / A[a][b] for a in range(1, AM + 1, 7) for b in range(0, BM + 1, 5))
    out(f"  float64 DP against the exact table on a sub-grid: max relative error {rel:.2e}")
    out("  diagonal A(a,a), a = 0..12:", [A[a][a] for a in range(13)])
    out("  A(40,40) =", A[40][40], "  A(100,100) =", A[100][100])

    # ------------------------------------------------------------------ growth: how model-dependent is the fit?
    out("\nGROWTH ALONG THE CRITICAL RAY b = round(a ln2/ln3): fitted coefficient of sqrt(L) under different fit forms")
    pts = [(a * LN2 + round(a * LN2 / LN3) * LN3, lnA[a][round(a * LN2 / LN3)]) for a in range(4, 476)]
    Ls = np.array([p[0] for p in pts])
    ys = np.array([p[1] for p in pts])
    c_emp = kappa * math.pi ** 2 / 12
    out(f"  heuristic h(1/2) = 2 sqrt(kappa pi^2/12) = {2 * math.sqrt(c_emp):.3f}")
    for lo in (40, 100, 200, 400):
        s = Ls >= lo
        M3 = np.vstack([np.sqrt(Ls[s]), np.log(Ls[s]), np.ones(s.sum())]).T
        a3 = np.linalg.lstsq(M3, ys[s], rcond=None)[0]
        M2 = np.vstack([np.sqrt(Ls[s]), np.ones(s.sum())]).T
        a2 = np.linalg.lstsq(M2, ys[s], rcond=None)[0]
        M4 = np.vstack([np.sqrt(Ls[s]), np.log(Ls[s]), np.ones(s.sum()), 1 / np.sqrt(Ls[s])]).T
        a4 = np.linalg.lstsq(M4, ys[s], rcond=None)[0]
        out(f"  L >= {lo:>3d}:  a sqrt(L) + b ln L + c -> a = {a3[0]:.3f} (b = {a3[1]:+.2f});   a sqrt(L) + c -> a = {a2[0]:.3f};"
            f"   with an extra d/sqrt(L) -> a = {a4[0]:.3f} (b = {a4[1]:+.2f})")
    out("  local slope d(ln A)/d(sqrt L) at L = 150, 300, 600: " + ", ".join(
        f"{(np.interp(L + 20, Ls, ys) - np.interp(L - 20, Ls, ys)) / (math.sqrt(L + 20) - math.sqrt(L - 20)):.3f}" for L in (150, 300, 600)))
    out("  ratio ln A / (2 sqrt(c L)) at L = 100, 300, 600: " + ", ".join(
        f"{np.interp(L, Ls, ys) / (2 * math.sqrt(c_emp * L)):.3f}" for L in (100, 300, 600)))
    out("  => the '2 to 6 per cent high' agreement is a property of one three-parameter fit; the data fix the")
    out("     exponent 1/2 and the shape in theta, not the constant.")

    # ------------------------------------------------------------------ ridge
    LEVELS = (60, 100, 140, 180, 220, 260, 300, 320)
    theirs_ridge = (0.522, 0.523, 0.528, 0.531, 0.534, 0.535, 0.536, 0.536)
    out("\nRIDGE of ln A on size level sets (my estimator) against the researcher's:")
    mine_ridge = []
    for L, tr in zip(LEVELS, theirs_ridge):
        th, v = ridge_1d(lnA, L)
        mine_ridge.append(th)
        out(f"  L = {L:>3d}: theta* = {th:.3f}  (researcher {tr:.3f});  slope b/a = {(1 - th) / th * LN2 / LN3:.3f};  critical slope {LN2 / LN3:.3f}")
    # smoothness through theta = 1/2: ln A along the level set L = 300, residual from a global quartic
    L = 300
    th, val = [], []
    for a in range(1, AM):
        b = (L - a * LN2) / LN3
        if 1 <= b < BM - 1:
            j = int(b)
            th.append(a * LN2 / L)
            val.append((1 - (b - j)) * lnA[a][j] + (b - j) * lnA[a][j + 1])
    th, val = np.array(th), np.array(val)
    s = (th > 0.3) & (th < 0.7)
    res = val[s] - np.polyval(np.polyfit(th[s], val[s], 4), th[s])
    near = np.abs(th[s] - 0.5) < 0.03
    out(f"  L = 300, 0.3 < theta < 0.7: residual from a quartic: rms {res.std():.4f} overall, {res[near].std():.4f} within 0.03 of theta = 1/2,"
        f" max |res| {np.abs(res).max():.4f}  (no kink at the critical line)")

    # ------------------------------------------------------------------ random controls
    NT = 120
    rng = np.random.default_rng(20261006)
    ii, jj = np.meshgrid(np.arange(1, AM + 1), np.arange(1, BM + 1), indexing="ij")
    prob = np.minimum(1.0, kappa * LN2 * LN3 / (ii * LN2 + jj * LN3))
    fermat = [p for p in mine if p[1] == 0]
    ctrl = {L: [] for L in LEVELS}
    for _ in range(NT):
        mask = rng.random(prob.shape) < prob
        pts_r = fermat + list(zip(ii[mask].tolist(), jj[mask].tolist()))
        Ar = float_table(pts_r)
        with np.errstate(divide="ignore"):
            lr = np.log(Ar).tolist()
        for L in LEVELS:
            ctrl[L].append(ridge_1d(lr, L)[0])
    out(f"\nCONTROL: {NT} random point sets (same density law, seed 20261006), same estimator   [{time.time() - t0:.0f} s]")
    for L, th in zip(LEVELS, mine_ridge):
        c = np.array(ctrl[L])
        out(f"  L = {L:>3d}: real {th:.3f};  control {c.mean():.3f} +- {c.std(ddof=1):.3f};  z = {(th - c.mean()) / c.std(ddof=1):+.2f};"
            f"  fraction of controls >= real: {np.mean(c >= th):.3f};  |control - 1/2| > |real - 1/2|: {np.mean(np.abs(c - 0.5) > abs(th - 0.5)):.3f}")
    out(f"\ndone in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
