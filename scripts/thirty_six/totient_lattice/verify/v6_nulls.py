"""Skeptic check of the statistical nulls Q4.2-d, Q4.3-a, Q4.3-c and of the table Q4.3-b.

Independent design (no shared code, different range, different statistics):

 A. F against Collatz times on a range DISJOINT from the researcher's: odd n in (10^7, 4*10^7].
    Residue and size are controlled by DIFFERENCING within pairs (n, n + 2^k) with the same residue
    mod 2^k and almost the same size (n'/n < 1.007 for k = 16), instead of regression on bins.
    Statistic: Pearson correlation of the differences, standard error 1/sqrt(#pairs).  A real partial
    correlation of -0.0009 (the researcher's unexplained residual, 1.3-1.9 s.e. on 2.5 million n)
    would show here at about 2.5 s.e.
    CAVEAT: a pair controls n mod 2^k but its two members differ in bit k, so this statistic still sees
    dependence carried by bit k (i.e. by n mod 2^(k+1)).  A pooled 3 x 3 sign-table chi-square was tried
    first and DROPPED: pooled over residue classes whose marginal distributions differ it is not a valid
    test of within-class independence (it gave chi2 = 59 at k = 16 from class heterogeneity alone).
 B. the same within-stratum shuffle test of mutual information, re-implemented, on (10^7, 2*10^7].
 C. fibres phi^-1(m), m <= 10^5: pair agreement of dropping times against shuffles within x mod 2^k,
    plus the MECHANISM of the residue excess (fibre-mates are p*y and q*y with phi(p) = phi(q)).
 D. Collatz arrows inside fibres against a null that respects T(x) = 2 mod 3.
 E. Collatz data of the eight solutions of phi(x) = 36 from the repo functions.

CONVENTION.  sigma = number of STANDARD steps (n/2 | 3n+1) to the first value < n (the repo's
collatz.dropping.dropping_time); sig_inf = standard steps to reach 1 (collatz.core.total_stopping_time).

Run:  python -X utf8 v6_nulls.py      (about 5 minutes; ~1 GB of memory)
"""
from __future__ import annotations

import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..")))
LOG = open(os.path.join(HERE, "v6_nulls.log"), "w", encoding="utf-8")


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")


def build_F(N):
    """Shapiro's F from its additive definition; also returns phi (int32) if N <= 4*10^6."""
    spf = np.zeros(N + 1, dtype=np.int32)
    for p in range(2, int(N ** 0.5) + 2):
        if spf[p] == 0:
            seg = spf[p * p:: p]
            seg[seg == 0] = p
    idx = np.arange(N + 1, dtype=np.int32)
    pr = spf == 0
    pr[:2] = False
    spf[pr] = idx[pr]
    del idx, pr
    F = np.zeros(N + 1, dtype=np.int16)
    F[2] = 1
    want_phi = N <= 4 * 10 ** 6
    phi = np.zeros(N + 1, dtype=np.int32) if want_phi else None
    if want_phi:
        phi[1] = 1
        phi[2] = 1
    lo = 3
    while lo <= N:
        hi = min(N, 2 * lo - 2)
        n = np.arange(lo, hi + 1, dtype=np.int64)
        p = spf[lo: hi + 1].astype(np.int64)
        m = n // p
        isp = m == 1
        comp = ~isp
        F[n[comp]] = F[p[comp]] + F[m[comp]]
        if want_phi:
            mm, pp = m[comp], p[comp]
            phi[n[comp]] = np.where(mm % pp == 0, phi[mm].astype(np.int64) * pp, phi[mm].astype(np.int64) * (pp - 1))
            phi[n[isp]] = n[isp] - 1
        F[n[isp]] = F[n[isp] - 1]
        lo = hi + 1
    return F, phi


def build_collatz(N, chunk=4 * 10 ** 6):
    """sigma (standard steps to drop, int16), dest (int32), sig_inf (int32) for 2 <= n <= N."""
    sigma = np.zeros(N + 1, dtype=np.int16)
    dest = np.zeros(N + 1, dtype=np.int32)
    for lo in range(2, N + 1, chunk):
        hi = min(N, lo + chunk - 1)
        idx = np.arange(lo, hi + 1, dtype=np.int64)
        cur = idx.copy()
        st = np.zeros(idx.size, dtype=np.int16)
        while idx.size:
            odd = (cur & 1) == 1
            cur = np.where(odd, 3 * cur + 1, cur >> 1)
            st += 1
            done = cur < idx
            if done.any():
                sigma[idx[done]] = st[done]
                dest[idx[done]] = cur[done]
                keep = ~done
                idx, cur, st = idx[keep], cur[keep], st[keep]
    tinf = np.zeros(N + 1, dtype=np.int32)
    known = np.zeros(N + 1, dtype=bool)
    known[1] = True
    lo = 2
    while lo <= N:
        hi = min(N, 2 * lo - 1)
        n = np.arange(lo, hi + 1, dtype=np.int64)
        d = dest[lo: hi + 1].astype(np.int64)
        pend = np.ones(n.size, dtype=bool)
        while pend.any():
            ready = pend & known[d]
            tinf[n[ready]] = tinf[d[ready]] + sigma[n[ready]]
            known[n[ready]] = True
            pend &= ~ready
        lo = hi + 1
    return sigma, dest, tinf


def corr(a, b):
    a = a - a.mean()
    b = b - b.mean()
    return float((a * b).sum() / math.sqrt((a * a).sum() * (b * b).sum()))


def sign_chi2(x, y):
    sx, sy = np.sign(x).astype(np.int64) + 1, np.sign(y).astype(np.int64) + 1
    tab = np.bincount(sx * 3 + sy, minlength=9).reshape(3, 3).astype(float)
    exp = tab.sum(1, keepdims=True) @ tab.sum(0, keepdims=True) / tab.sum()
    ok = exp > 0
    return float(((tab - exp) ** 2 / np.where(ok, exp, 1))[ok].sum())


def mi_bits(x, y, nx, ny):
    joint = np.bincount(x * ny + y, minlength=nx * ny).reshape(nx, ny).astype(float)
    n = joint.sum()
    px, py = joint.sum(1, keepdims=True), joint.sum(0, keepdims=True)
    nz = joint > 0
    return float(np.sum(joint[nz] / n * np.log2(joint[nz] * n / (px @ py)[nz])))


def main():
    t0 = time.time()
    N = 4 * 10 ** 7
    F, _ = build_F(N + 2)
    out(f"N = {N}: F built [{time.time() - t0:.0f} s]")
    sigma, dest, tinf = build_collatz(N)
    out(f"sigma, dest, sig_inf built [{time.time() - t0:.0f} s];  max sigma {int(sigma.max())}, max sig_inf {int(tinf.max())}")
    from collatz import core, dropping
    for x in list(range(2, 1500)) + [27, 63, 703, 871, 6171, 77031, 837799, 8400511]:
        assert dropping.dropping_time(x) == sigma[x] and dropping.dropping_destination(x) == dest[x]
        assert core.total_stopping_time(x) == tinf[x]
    out("agree with collatz.dropping.dropping_time / dropping_destination / core.total_stopping_time on 1500 values")

    # ------------------------------------------------------------------ A. paired differences
    out("\nA. PAIRED DIFFERENCES.  pairs (n, n + 2^k), n odd, bit k of n equal to 0, both in (10^7, 4*10^7].")
    out("   corr = Pearson correlation of (X(n') - X(n), Y(n') - Y(n));  s.e. = 1/sqrt(pairs)")
    out("     k      pairs      s.e.    | F(n),sigma      z | F(n),sig_inf    z | F(n+1),sigma    z | F(n+1),sig_inf  z")
    LOW = 10 ** 7
    for k in (2, 4, 8, 12, 16, 20):
        step = 1 << k
        n = np.arange(LOW + 1, N - step + 1, 2, dtype=np.int64)
        n = n[((n >> k) & 1) == 0]
        m = n + step
        dF = (F[m] - F[n]).astype(np.float64)
        dG = (F[m + 1] - F[n + 1]).astype(np.float64)
        dS = (sigma[m] - sigma[n]).astype(np.float64)
        dT = (tinf[m] - tinf[n]).astype(np.float64)
        se = 1 / math.sqrt(n.size)
        row = []
        for a, b in ((dF, dS), (dF, dT), (dG, dS), (dG, dT)):
            r = corr(a, b)
            row.append(f"{r:+.5f} {r / se:+6.1f}")
        out(f"    {k:>2d}  {n.size:>9d}  {se:.5f}  | " + " | ".join(row))
        if k == 16:
            out(f"         (k = 16: fraction of pairs with different sigma: {np.mean(dS != 0):.4f}; with different sig_inf: {np.mean(dT != 0):.4f})")
    # disjoint sub-ranges for the F(n), sig_inf pair at k = 16 (is a small residual stable in sign?)
    step = 1 << 16
    for lo, hi in ((10 ** 7, 2 * 10 ** 7), (2 * 10 ** 7, 3 * 10 ** 7), (3 * 10 ** 7, 4 * 10 ** 7)):
        n = np.arange(lo + 1, hi - step + 1, 2, dtype=np.int64)
        n = n[((n >> 16) & 1) == 0]
        m = n + step
        dF = (F[m] - F[n]).astype(np.float64)
        r1 = corr(dF, (sigma[m] - sigma[n]).astype(np.float64))
        r2 = corr(dF, (tinf[m] - tinf[n]).astype(np.float64))
        out(f"   k = 16, n in ({lo}, {hi}]: {n.size} pairs, s.e. {1 / math.sqrt(n.size):.5f};  F,sigma {r1:+.5f};  F,sig_inf {r2:+.5f}")
    # positive control for this statistic: sig_inf + round(0.5 * (F - 19))
    n = np.arange(LOW + 1, N - step + 1, 2, dtype=np.int64)
    n = n[((n >> 16) & 1) == 0]
    m = n + step
    rng = np.random.default_rng(5)
    bump_n = (rng.random(n.size) < 0.02) * (F[n] - 19)
    bump_m = (rng.random(n.size) < 0.02) * (F[m] - 19)
    r = corr((F[m] - F[n]).astype(np.float64), (tinf[m] + bump_m - tinf[n] - bump_n).astype(np.float64))
    out(f"   positive control (sig_inf + (F - 19) on a random 2% of n): corr {r:+.5f}, z = {r * math.sqrt(n.size):+.1f}")

    # ------------------------------------------------------------------ B. mutual information, re-implemented
    out("\nB. MUTUAL INFORMATION against within-stratum shuffles, odd n in (10^7, 2*10^7]  (strata: 256 size bins x n mod 2^k)")
    n = np.arange(10 ** 7 + 1, 2 * 10 ** 7 + 1, 2, dtype=np.int64)
    X = F[n].astype(np.int64)
    G = F[n + 1].astype(np.int64)
    S = np.minimum(sigma[n].astype(np.int64), 200)
    T = tinf[n].astype(np.int64)
    sb = np.minimum(255, ((np.log(n) - math.log(10 ** 7)) / math.log(2) * 256).astype(np.int64))
    nX, nS, nT = int(max(X.max(), G.max())) + 1, int(S.max()) + 1, int(T.max()) + 1
    rng = np.random.default_rng(99)
    out("     k    pair             I observed    shuffled mean    sd         excess        z")
    for k in (4, 8, 12):
        strata = sb * (1 << k) + (n & ((1 << k) - 1))
        order = np.argsort(strata, kind="stable")
        st_sorted = strata[order]
        res = {"F,sigma": [], "F,sig_inf": [], "F(n+1),sigma": [], "F(n+1),sig_inf": []}
        for _ in range(10):
            # random permutation inside each stratum: sort by (stratum, random key)
            perm = order[np.lexsort((rng.random(n.size), st_sorted))]
            Xs = np.empty_like(X)
            Xs[order] = X[perm]
            Gs = np.empty_like(G)
            Gs[order] = G[perm]
            res["F,sigma"].append(mi_bits(Xs, S, nX, nS))
            res["F,sig_inf"].append(mi_bits(Xs, T, nX, nT))
            res["F(n+1),sigma"].append(mi_bits(Gs, S, nX, nS))
            res["F(n+1),sig_inf"].append(mi_bits(Gs, T, nX, nT))
        obs = {"F,sigma": mi_bits(X, S, nX, nS), "F,sig_inf": mi_bits(X, T, nX, nT),
               "F(n+1),sigma": mi_bits(G, S, nX, nS), "F(n+1),sig_inf": mi_bits(G, T, nX, nT)}
        for key in obs:
            a = np.array(res[key])
            out(f"    {k:>2d}    {key:<15s}  {obs[key]:.6f}      {a.mean():.6f}      {a.std(ddof=1):.1e}   {obs[key] - a.mean():+.2e}   {(obs[key] - a.mean()) / a.std(ddof=1):+6.2f}")
        out(f"         [{time.time() - t0:.0f} s]")
    del X, G, S, T, sb, n

    # ------------------------------------------------------------------ C. fibres
    out("\nC. FIBRES phi^-1(m), m <= 10^5 (complete below 10^6 since x <= 5.539 phi(x))")
    M, NN = 10 ** 5, 10 ** 6
    _, phi = build_F(3 * NN + 2)
    x = np.arange(1, NN + 1, dtype=np.int64)
    ph = phi[1: NN + 1].astype(np.int64)
    inr = ph <= M
    out(f"   totient values <= {M}: {np.unique(ph[inr]).size};  preimages: {int(inr.sum())};  phi^-1(36) = {x[ph == 36].tolist()}")
    sel = inr & (x % 2 == 1) & (x >= 3)
    xo, mo = x[sel], ph[sel]
    c3 = np.bincount(mo, minlength=M + 1)
    keep = c3[mo] >= 2
    xo, mo = xo[keep], mo[keep]
    so = sigma[xo].astype(np.int64)
    order = np.argsort(mo, kind="stable")
    xo, mo, so = xo[order], mo[order], so[order]
    starts = np.flatnonzero(np.r_[True, mo[1:] != mo[:-1]])
    sizes = np.diff(np.r_[starts, mo.size])
    npairs = int(np.sum(sizes * (sizes - 1) // 2))
    out(f"   odd members x >= 3 in fibres with at least two: {xo.size} in {starts.size} fibres, {npairs} pairs")

    def agree(vals):
        key = mo * 100003 + vals
        _, c = np.unique(key, return_counts=True)
        return float(np.sum(c * (c - 1) // 2)) / npairs
    p_obs = agree(so)
    out(f"   Pr[sigma(x) = sigma(x')] over pairs of fibre-mates: {p_obs:.5f}")
    rng = np.random.default_rng(2026)
    out("     shuffle of sigma within x mod 2^k:    k    mean      sd       z of observed")
    for k in (1, 2, 3, 4, 8, 12):
        strata = xo & ((1 << k) - 1)
        o2 = np.argsort(strata, kind="stable")
        ss = strata[o2]
        vals = []
        for _ in range(150):
            perm = o2[np.lexsort((rng.random(xo.size), ss))]
            sh = np.empty_like(so)
            sh[o2] = so[perm]
            vals.append(agree(sh))
        vals = np.array(vals)
        out(f"                                          {k:>2d}   {vals.mean():.5f}  {vals.std(ddof=1):.5f}  {(p_obs - vals.mean()) / vals.std(ddof=1):+6.2f}")
    # mechanism: 2-adic distance between fibre-mates
    out("   MECHANISM.  v_2(x - x') for pairs of odd fibre-mates (independent odd numbers: 1/2, 1/4, 1/8, 1/16, 1/16):")
    v2c = np.zeros(6, dtype=np.int64)
    ratio = {}
    for st, sz in zip(starts.tolist(), sizes.tolist()):
        if sz < 2:
            continue
        xs = xo[st: st + sz]
        dif = (xs[:, None] - xs[None, :])[np.triu_indices(sz, 1)]
        dif = np.abs(dif)
        v = np.zeros(dif.size, dtype=np.int64)
        d2 = dif.copy()
        for _ in range(5):
            ev = d2 % 2 == 0
            v += ev
            d2 = np.where(ev, d2 // 2, d2)
            if not ev.any():
                break
        v2c += np.bincount(np.minimum(v, 5), minlength=6)
        if sz <= 12:
            for i in range(sz):
                for j in range(i + 1, sz):
                    g = math.gcd(int(xs[i]), int(xs[j]))
                    r = (int(xs[i]) // g, int(xs[j]) // g)
                    ratio[r] = ratio.get(r, 0) + 1
    out("     v_2 = 1, 2, 3, 4, >= 5: " + ", ".join(f"{c / v2c[1:].sum():.4f}" for c in v2c[1:]))
    top = sorted(ratio.items(), key=lambda kv: -kv[1])[:12]
    out("     most frequent reduced ratios x : x' among fibre-mates (fibres with <= 12 odd members): "
        + ", ".join(f"{a}:{b} ({c})" for (a, b), c in top))
    out("     => fibre-mates are p*y and q*y with phi(p) = phi(q) (7:9, 13:21, 19:27, 35:39:45, ...); x - x' = (q - p) y has a")
    out("        forced 2-adic valuation (9 - 7 = 2, 21 - 13 = 8, 27 - 19 = 8, 39 - 35 = 4), which is the whole residue effect.")

    # ------------------------------------------------------------------ D. arrows
    out("\nD. COLLATZ ARROWS INSIDE FIBRES.  odd x <= 10^6 with phi(T(x)) = phi(x), T(x) = (3x+1)/2")
    xodd = np.arange(1, NN + 1, 2, dtype=np.int64)
    Tx = (3 * xodd + 1) // 2
    hits = int(np.sum(phi[Tx] == phi[xodd]))
    out(f"   count: {hits}   (note T(x) = 2 mod 3 always; a fair null must keep y = 2 mod 3 and the parity of T(x))")
    null = []
    for t in list(range(-25, 0)) + list(range(1, 26)):
        y = Tx + 6 * t
        ok = (y >= 1) & (y <= 3 * NN + 1)
        null.append(int(np.sum(phi[y[ok]] == phi[xodd[ok]])))
    null = np.array(null)
    out(f"   null y = T(x) + 6t, t = -25..25, t != 0: mean {null.mean():.1f}, sd {null.std(ddof=1):.1f}, min {null.min()}, max {null.max()};"
        f"  z of the real count: {(hits - null.mean()) / null.std(ddof=1):+.2f}")
    null2 = []
    for t in list(range(-25, 0)) + list(range(1, 26)):
        y = Tx + t
        ok = (y >= 1) & (y <= 3 * NN + 1)
        null2.append(int(np.sum(phi[y[ok]] == phi[xodd[ok]])))
    null2 = np.array(null2)
    out(f"   cruder null y = T(x) + t (any residue): mean {null2.mean():.1f}, sd {null2.std(ddof=1):.1f}")

    # ------------------------------------------------------------------ E. the fibre of 36
    out("\nE. THE FIBRE OF 36, from the repo functions (sigma = standard steps; k = halvings; s = odd steps)")
    out("      x   sigma   k   s   dest   sig_inf   orbit max")
    for v in (37, 57, 63, 74, 76, 108, 114, 126):
        orb = core.orbit(v)
        sg = dropping.dropping_time(v)
        pre = orb[: sg + 1]
        s_odd = sum(1 for y in pre[:-1] if y % 2)
        out(f"   {v:>4d}  {sg:>5d} {sg - s_odd:>3d} {s_odd:>3d}  {dropping.dropping_destination(v):>5d}  {core.total_stopping_time(v):>7d}  {max(orb):>9d}")
    out(f"\ndone in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
