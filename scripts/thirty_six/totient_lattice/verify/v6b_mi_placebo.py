"""Skeptic follow-up to v6_nulls.py section B.

v6 found, on (10^7, 2*10^7] with 256 size bins, a mutual-information excess between F(n+1) and
sig_inf(n) that does NOT vanish at k = 8 or k = 12 (+1.7e-4 bits, z = 3.4 and 4.7), where the
researcher reported 'gone by k = 12' (and -2e-6 at k = 8).  Is that a real arithmetic dependence,
a dependence carried by higher residue bits, or an artefact of the estimator?

PLACEBO TEST.  Replace the number n + 1 by a DIFFERENT number with the same residue mod 2^17:
        P(n) = F(n + 1 + 2^17),          Q(n) = F(n + 2^17)   (placebo for F(n)).
P shares with F(n+1) everything that is a function of (n + 1) mod 2^17 (in particular v_2(n+1) when
it is below 17) and of the size, and nothing else.  If P shows the same excess as F(n+1), the
excess is residue/size-mediated or an artefact; if only F(n+1) shows it, it is arithmetic.

Also scans the size-bin width (256, 1024, 4096 bins per octave) and the estimator: sig_inf is used
raw and also coarsened to 32 quantile classes (which removes most of the plug-in bias).

Run:  python -X utf8 v6b_mi_placebo.py      (about 4 minutes)
"""
from __future__ import annotations

import math
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v6b_mi_placebo.log"), "w", encoding="utf-8")


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")


def build_F(N):
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
    lo = 3
    while lo <= N:
        hi = min(N, 2 * lo - 2)
        n = np.arange(lo, hi + 1, dtype=np.int64)
        p = spf[lo: hi + 1].astype(np.int64)
        m = n // p
        isp = m == 1
        comp = ~isp
        F[n[comp]] = F[p[comp]] + F[m[comp]]
        F[n[isp]] = F[n[isp] - 1]
        lo = hi + 1
    return F


def build_tinf(N, chunk=4 * 10 ** 6):
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
    return sigma, tinf


def mi_bits(x, y, nx, ny):
    joint = np.bincount(x * ny + y, minlength=nx * ny).reshape(nx, ny).astype(float)
    n = joint.sum()
    px, py = joint.sum(1, keepdims=True), joint.sum(0, keepdims=True)
    nz = joint > 0
    return float(np.sum(joint[nz] / n * np.log2(joint[nz] * n / (px @ py)[nz])))


def main():
    t0 = time.time()
    LO, HI = 10 ** 7, 2 * 10 ** 7
    SH = 1 << 17
    F = build_F(HI + SH + 4)
    sigma, tinf = build_tinf(HI)
    out(f"arrays built [{time.time() - t0:.0f} s]")
    n = np.arange(LO + 1, HI + 1, 2, dtype=np.int64)
    Y = tinf[n].astype(np.int64)
    # coarse version of sig_inf: 32 quantile classes
    qs = np.quantile(Y, np.linspace(0, 1, 33)[1:-1])
    Yq = np.searchsorted(qs, Y).astype(np.int64)
    S = np.minimum(sigma[n].astype(np.int64), 200)
    V = {"F(n)": F[n].astype(np.int64), "placebo F(n+2^17)": F[n + SH].astype(np.int64),
         "F(n+1)": F[n + 1].astype(np.int64), "placebo F(n+1+2^17)": F[n + 1 + SH].astype(np.int64)}
    nX = int(max(v.max() for v in V.values())) + 1
    nY, nQ, nS = int(Y.max()) + 1, 32, int(S.max()) + 1
    lnn = np.log(n)
    rng = np.random.default_rng(424242)
    NSH = 12
    out(f"odd n in ({LO}, {HI}]: {n.size} numbers; {NSH} shuffles per configuration")
    out("  bins = size bins per octave;  strata = (size bin, n mod 2^k);  excess in bits, z in brackets")
    out("  bins    k   variable               vs sig_inf (raw)        vs sig_inf (32 quantiles)   vs sigma")
    for nb, k in ((256, 8), (1024, 8), (4096, 8), (256, 12), (1024, 12), (1024, 4)):
        sb = np.minimum(nb - 1, ((lnn - math.log(LO)) / math.log(2) * nb).astype(np.int64))
        strata = sb * (1 << k) + (n & ((1 << k) - 1))
        order = np.argsort(strata, kind="stable")
        ss = strata[order]
        acc = {name: ([], [], []) for name in V}
        for _ in range(NSH):
            perm = order[np.lexsort((rng.random(n.size), ss))]
            for name, x in V.items():
                xs = np.empty_like(x)
                xs[order] = x[perm]
                acc[name][0].append(mi_bits(xs, Y, nX, nY))
                acc[name][1].append(mi_bits(xs, Yq, nX, nQ))
                acc[name][2].append(mi_bits(xs, S, nX, nS))
        for name, x in V.items():
            cells = []
            for t, (yy, ny) in enumerate(((Y, nY), (Yq, nQ), (S, nS))):
                a = np.array(acc[name][t])
                ob = mi_bits(x, yy, nX, ny)
                cells.append(f"{ob - a.mean():+.2e} ({(ob - a.mean()) / a.std(ddof=1):+5.1f})")
            out(f"  {nb:>4d}   {k:>2d}   {name:<20s}   {cells[0]:<22s}  {cells[1]:<22s}      {cells[2]}")
        out(f"       [{np.unique(strata).size} strata, mean size {n.size / np.unique(strata).size:.1f}; {time.time() - t0:.0f} s]")
    out(f"\ndone in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
