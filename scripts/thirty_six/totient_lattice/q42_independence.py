"""Q4.2 (second half)  Is the totient height related to Collatz times once residues are controlled?

Variables, for odd n (even n are excluded: their dropping time is 1):

  F(n)      Shapiro's additive totient height (A064415); for odd n, H(n) = F(n) + 1
  G(n)      = F(n+1), the height in the coordinate v = n+1 in which the odd shortcut
            step is v -> 3v/2 and F is conserved (see q42_pillai_shapiro.py)
  sigma     dropping time, REPO CONVENTION: standard steps n -> n/2 | 3n+1 until < n
  sig_inf   total stopping time: standard steps until 1

Sample.  Raw correlations: all odd n in [3, 10^7].  Controlled tests: the top octave, odd n in
[5*10^6, 10^7] (2.5 million numbers), so that size varies by a factor 2 only, and size is
controlled by equal bins of ln n inside the octave (256 bins in Table A; 8 to 2048 in Table B).
(A first version of this script stratified by floor(log2 n) only; that leaves a spurious
0.02-bit 'dependence' between F and sig_inf, because both grow with ln n inside an octave.
Table B therefore scans the bin width.  Recorded here as a trap.)

Tests
  A. Pearson and Spearman correlation after removing, additively, the means over the size
     bins, over the classes n mod 2^k, and over the classes n mod 3^j.
  B. Mutual information I(X; Y) in bits (plug-in estimator), against a control in which X is
     shuffled WITHIN strata (size bin, n mod 2^k, n mod 3^j).  The control keeps every
     dependence mediated by size and by the residue classes, and destroys the rest.
     excess = I(observed) - mean I(shuffled);  z = excess / sd(shuffled).
  C. A positive control: a synthetic dependence of known size injected into sig_inf.

Run:  python -X utf8 q42_independence.py      (about 3 minutes)
"""
from __future__ import annotations

import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
from common import (dropping_arrays, shapiro_F, total_stopping_times,  # noqa: E402
                    totient_height, totient_sieve)

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "q42_independence.log"), "w", encoding="utf-8")


def out(*args):
    s = " ".join(str(a) for a in args)
    print(s, flush=True)
    LOG.write(s + "\n")


def mi_bits(x, y, nx, ny):
    joint = np.bincount(x.astype(np.int64) * ny + y, minlength=nx * ny).reshape(nx, ny).astype(float)
    n = joint.sum()
    px, py = joint.sum(1, keepdims=True), joint.sum(0, keepdims=True)
    nz = joint > 0
    return float(np.sum(joint[nz] / n * np.log2(joint[nz] * n / (px @ py)[nz])))


def rank(a):
    order = np.argsort(a, kind="stable")
    sa = a[order]
    starts = np.flatnonzero(np.r_[True, sa[1:] != sa[:-1]])
    ends = np.r_[starts[1:], a.size]
    r = np.empty(a.size)
    r[order] = np.repeat((starts + ends - 1) / 2.0, ends - starts)
    return r


def demean(r, classes, ncls):
    sums = np.bincount(classes, weights=r, minlength=ncls)
    cnts = np.bincount(classes, minlength=ncls)
    return r - (sums / np.maximum(cnts, 1))[classes]


def residualise(x, factors):
    """additive removal of class means for several factors (three backfitting sweeps)."""
    r = x.astype(float) - x.mean()
    for _ in range(3):
        for cls, ncls in factors:
            r = demean(r, cls, ncls)
    return r


def corr(a, b):
    a = a - a.mean()
    b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else float("nan")


def main():
    t0 = time.time()
    N = 10 ** 7
    phi = totient_sieve(N + 1)
    H = totient_height(phi)
    F = shapiro_F(H)
    k, s, dest = dropping_arrays(N)
    assert int((k[2:] < 0).sum()) == 0
    sigma = (k + s).astype(np.int64)
    tst = total_stopping_times(k, s, dest)
    out(f"N = {N}; arrays built in {time.time() - t0:.0f} s")

    from collatz import core, dropping
    for x in range(2, 3000):
        assert dropping.dropping_time(x) == sigma[x]
        assert dropping.dropping_destination(x) == dest[x]
        assert core.total_stopping_time(x) == tst[x]
    out("sigma, dest, sig_inf agree with collatz.dropping.dropping_time / dropping_destination /")
    out("  collatz.core.total_stopping_time for 2 <= n < 3000  (standard-map step counts)")
    out(f"mean sigma over 2 <= n <= N: {sigma[2:].mean():.4f} standard steps;  mean shortcut k: {k[2:].mean():.4f};"
        f"  max sigma: {int(sigma.max())}")

    # ---------------------------------------------------------------- raw, full range
    nall = np.arange(3, N + 1, 2, dtype=np.int64)
    out(f"\nRAW CORRELATIONS, all odd n in [3, {N}] ({nall.size} numbers), nothing controlled:")
    for name, x, y in (("F(n)  , sigma  ", F[nall], sigma[nall]), ("F(n)  , sig_inf", F[nall], tst[nall]),
                       ("F(n+1), sigma  ", F[nall + 1], sigma[nall]), ("F(n+1), sig_inf", F[nall + 1], tst[nall])):
        out(f"  {name}   Pearson {corr(x.astype(float), y.astype(float)):+.5f}   Spearman {corr(rank(x), rank(y)):+.5f}")
    out("  (F(n) and sig_inf both grow like ln n: the +0.13 is the size confound.)")

    # ---------------------------------------------------------------- top octave
    n = np.arange(N // 2 + 1, N + 1, 2, dtype=np.int64)
    lnn = np.log(n)
    NB = 2048   # finest size resolution; coarser bins are obtained by integer division
    sb = np.minimum(NB - 1, ((lnn - np.log(N / 2)) / np.log(2) * NB).astype(np.int64))
    NBA = 256   # size bins used in Table A
    sbA = sb * NBA // NB
    Fo = F[n].astype(np.int64)
    Go = F[n + 1].astype(np.int64)
    so = sigma[n]
    to = tst[n].astype(np.int64)
    out(f"\nCONTROLLED SAMPLE: odd n in ({N // 2}, {N}], {n.size} numbers; size bins: equal bins of ln n in the octave")

    out("\nMEANS BY RESIDUE (why residue-mediated dependence must exist):")
    for mod in (4, 8):
        row = []
        for r in range(1, mod, 2):
            sel = (n % mod) == r
            row.append(f"{r}: F {Fo[sel].mean():.3f}, sigma {so[sel].mean():.2f}, sig_inf {to[sel].mean():.2f}")
        out(f"  n mod {mod} ->  " + "   |   ".join(row))
    for mod in (3, 9):
        row = []
        for r in range(mod):
            sel = (n % mod) == r
            row.append(f"{r}: F {Fo[sel].mean():.3f}, sig_inf {to[sel].mean():.2f}")
        out(f"  n mod {mod} ->  " + "   |   ".join(row))

    # ---------------------------------------------------------------- A. correlations
    out(f"\nTABLE A.  PARTIAL CORRELATIONS, top octave.  Removed additively: means over {NBA} size bins, class means of")
    out("  n mod 2^k, class means of n mod 3^j.   (k, j) = (0, 0): size only.")
    se = 1 / np.sqrt(n.size)
    pairs = [("F(n)  , sigma  ", Fo, so), ("F(n)  , sig_inf", Fo, to),
             ("F(n+1), sigma  ", Go, so), ("F(n+1), sig_inf", Go, to)]
    out("  pair               k   j     Pearson     Spearman")
    for name, x, y in pairs:
        rx_, ry_ = rank(x), rank(y)
        for kk, jj in ((0, 0), (2, 0), (4, 0), (8, 0), (12, 0), (16, 0), (0, 2), (8, 2), (16, 3)):
            fac = [(sbA, NBA)]
            if kk:
                fac.append((n & ((1 << kk) - 1), 1 << kk))
            if jj:
                fac.append((n % 3 ** jj, 3 ** jj))
            p = corr(residualise(x, fac), residualise(y, fac))
            sp = corr(residualise(rx_, fac), residualise(ry_, fac))
            out(f"  {name}   {kk:>2d}  {jj:>2d}    {p:+.5f}    {sp:+.5f}")
    out(f"  standard error of a correlation of independent variables at this sample size: {se:.5f}")

    # ---------------------------------------------------------------- B. mutual information
    NSHUF = 12
    rng = np.random.default_rng(36)
    nF = int(max(Fo.max(), Go.max())) + 1
    ns, nt = int(so.max()) + 1, int(to.max()) + 1
    out("\nTABLE B.  MUTUAL INFORMATION in bits (plug-in), top octave, against a shuffle of X within strata")
    out(f"  (size bin, n mod 2^k, n mod 3^j); {NSHUF} shuffles per row.  excess = observed - mean(shuffled).")
    out("  'bins' = number of size bins in the strata.  The first five rows scan the bin width at k = 1: an")
    out("  excess that shrinks with the bin width is a size confound (F and sig_inf both grow with ln n), not")
    out("  a dependence.  sigma has no size trend, so its rows do not move.")
    obs = {("F", "sigma"): mi_bits(Fo, so, nF, ns), ("F", "sig_inf"): mi_bits(Fo, to, nF, nt),
           ("F(n+1)", "sigma"): mi_bits(Go, so, nF, ns), ("F(n+1)", "sig_inf"): mi_bits(Go, to, nF, nt)}
    inj = to + ((rng.random(n.size) < 0.02) & (Fo % 2 == 0)).astype(np.int64)
    obs[("F", "sig_inf+inj")] = mi_bits(Fo, inj, nF, nt + 1)
    out("  X       Y            k  j  bins   I observed   mean shuffled   sd shuffled     excess         z")
    configs = ((1, 0, 8), (1, 0, 32), (1, 0, 128), (1, 0, 512), (1, 0, 2048),
               (2, 0, 128), (4, 0, 128), (8, 0, 128), (12, 0, 32), (1, 2, 128), (8, 1, 128))
    for kk, jj, nb in configs:
        sbin = sb * nb // NB
        strata = (sbin * (1 << kk) + (n & ((1 << kk) - 1))) * 3 ** jj + n % 3 ** jj
        base = np.argsort(strata, kind="stable")
        acc = {key: [] for key in obs}
        for _ in range(NSHUF):
            perm = np.lexsort((rng.random(n.size), strata))
            Fs = np.empty_like(Fo)
            Fs[base] = Fo[perm]
            Gs = np.empty_like(Go)
            Gs[base] = Go[perm]
            acc[("F", "sigma")].append(mi_bits(Fs, so, nF, ns))
            acc[("F", "sig_inf")].append(mi_bits(Fs, to, nF, nt))
            acc[("F(n+1)", "sigma")].append(mi_bits(Gs, so, nF, ns))
            acc[("F(n+1)", "sig_inf")].append(mi_bits(Gs, to, nF, nt))
            acc[("F", "sig_inf+inj")].append(mi_bits(Fs, inj, nF, nt + 1))
        for key in obs:
            a = np.array(acc[key])
            ex = obs[key] - a.mean()
            out(f"  {key[0]:<7s} {key[1]:<11s} {kk:>2d} {jj:>2d}  {nb:>3d}    {obs[key]:.6f}     {a.mean():.6f}      "
                f"{a.std(ddof=1):.2e}    {ex:+.2e}   {ex / a.std(ddof=1):+7.2f}")
        out(f"     [k = {kk}, j = {jj}: {np.unique(strata).size} strata; {time.time() - t0:.0f} s]")

    ent = [-np.sum(p[p > 0] * np.log2(p[p > 0])) for p in
           (np.bincount(Fo) / n.size, np.bincount(so) / n.size, np.bincount(to) / n.size)]
    out("\nSCALE.  H(F) = %.3f bits, H(sigma) = %.3f bits, H(sig_inf) = %.3f bits." % tuple(ent))
    out("  positive control: 'sig_inf+inj' adds 1 to sig_inf for a random 2% of the n with F even.")
    out("  Its excess over the plain 'F, sig_inf' row is what a real dependence of that size looks like.")
    out(f"\ndone in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
