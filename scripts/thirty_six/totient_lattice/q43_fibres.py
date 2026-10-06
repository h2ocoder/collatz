"""Q4.3  Totient fibres against dropping classes.

For every totient value m <= 10^5 the fibre phi^-1(m) is complete inside [1, 10^6]:
  phi(x) <= 10^5 forces x to have at most 7 distinct primes (1*2*4*6*10*12*16 = 92160,
  times 18 exceeds 10^5), hence x/phi(x) <= 2/1*3/2*5/4*7/6*11/10*13/12*17/16 = 5.539.

CONVENTION.  sigma(x) = dropping time in the REPO convention: number of standard steps
x -> x/2 | 3x+1 until the first value < x (collatz.dropping.dropping_time).  k = number of
shortcut steps (= halvings), s = number of odd steps, sigma = k + s.  dest = first value < x.

What is tested
  1. structure forced by phi alone: x odd => 2x in the same fibre; y coprime to 6 =>
     {3y, 4y, 6y} in one fibre.  Even members have sigma = 1, so only odd members matter.
  2. do the odd members of one fibre have more similar dropping times than chance?
     statistic: probability that two distinct odd members of the same fibre have the same
     sigma (pairs pooled over all fibres); control: sigma shuffled among all odd members
     within strata x mod 2^k.  Also eta^2 (share of the variance of sigma between fibres).
  3. Collatz arrows inside fibres: phi(T(x)) = phi(x), phi(dest(x)) = phi(x), beyond 2x -> x.
  4. the full Collatz data of the eight solutions of phi(x) = 36.

Run:  python -X utf8 q43_fibres.py      (about 1 minute)
"""
from __future__ import annotations

import os
import sys
import time

import numpy as np
import sympy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
from common import (dropping_arrays, shapiro_F, total_stopping_times,  # noqa: E402
                    totient_height, totient_sieve)

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "q43_fibres.log"), "w", encoding="utf-8")


def out(*args):
    s = " ".join(str(a) for a in args)
    print(s, flush=True)
    LOG.write(s + "\n")


def pair_agreement(fid, val):
    """Pr[val equal] over unordered pairs of distinct members within the same fibre id."""
    key = fid.astype(np.int64) * 4096 + val
    _, c = np.unique(key, return_counts=True)
    same = float(np.sum(c * (c - 1) // 2))
    _, cf = np.unique(fid, return_counts=True)
    tot = float(np.sum(cf * (cf - 1) // 2))
    return same / tot, int(tot)


def eta2(fid, val):
    val = val.astype(float)
    grand = val.mean()
    inv = np.unique(fid, return_inverse=True)[1]
    sums = np.bincount(inv, weights=val)
    cnts = np.bincount(inv)
    between = float(np.sum(cnts * (sums / cnts - grand) ** 2))
    return between / float(np.sum((val - grand) ** 2))


def parity_word(x):
    """shortcut parity word of x up to and including the dropping step."""
    w, y = [], x
    while True:
        if y % 2:
            w.append("1")
            y = (3 * y + 1) // 2
        else:
            w.append("0")
            y //= 2
        if y < x:
            return "".join(w)


def main():
    t0 = time.time()
    M, N = 10 ** 5, 10 ** 6
    B = 2 / 1 * 3 / 2 * 5 / 4 * 7 / 6 * 11 / 10 * 13 / 12 * 17 / 16
    assert 1 * 2 * 4 * 6 * 10 * 12 * 16 <= M < 1 * 2 * 4 * 6 * 10 * 12 * 16 * 18 and B * M < N
    phi = totient_sieve(3 * N + 2)
    k, s, dest = dropping_arrays(N)
    sigma = (k + s).astype(np.int64)
    tst = total_stopping_times(k, s, dest)
    out(f"phi^-1(m) complete for all m <= {M}: x <= {B:.3f} m < {N}.   [{time.time() - t0:.0f} s]")

    x = np.arange(1, N + 1, dtype=np.int64)
    inrange = phi[1:N + 1] <= M
    xs, ms = x[inrange], phi[1:N + 1][inrange]
    cnt = np.bincount(ms, minlength=M + 1)
    out(f"totient values m <= {M}: {int(np.count_nonzero(cnt))};  preimages in total: {xs.size};"
        f"  largest fibre: m = {int(np.argmax(cnt))} with {int(cnt.max())} solutions")
    assert cnt[36] == 8

    # ---------------------------------------------------------------- 1. forced structure
    odd = xs % 2 == 1
    out("\n1. STRUCTURE FORCED BY phi ALONE")
    out(f"   odd members: {int(odd.sum())};  members 2*odd: {int(((xs % 4) == 2).sum())};  members divisible by 4: {int(((xs % 4) == 0).sum())}")
    xo = xs[odd]
    assert np.all(phi[2 * xo] == phi[xo])
    out("   x odd  =>  phi(2x) = phi(x): verified for every odd member (so #odd = #(2*odd) exactly:",
        int(odd.sum()) == int(((xs % 4) == 2).sum()), ")")
    y = np.arange(1, N // 6 + 1, dtype=np.int64)
    y = y[(y % 2 == 1) & (y % 3 != 0)]
    assert np.all((phi[3 * y] == phi[4 * y]) & (phi[4 * y] == phi[6 * y]) & (phi[3 * y] == 2 * phi[y]))
    out(f"   y coprime to 6  =>  phi(3y) = phi(4y) = phi(6y) = 2 phi(y): verified for {y.size} values of y")
    out("   in the fibre of 36: {37, 74} and {63, 126} are doubling pairs; {57, 76, 114} = {3, 4, 6} * 19;")
    out("   108 = 4 * 27 stands alone.  Collatz reads these as halvings: 74 -> 37, 126 -> 63, 114 -> 57,")
    out("   76 -> 38 -> 19, 108 -> 54 -> 27.  Every even x has sigma = 1.")
    nf_odd = np.bincount(ms[odd], minlength=M + 1)
    out(f"   fibres with no odd member: {int(np.sum((cnt > 0) & (nf_odd == 0)))};  with exactly one: {int(np.sum(nf_odd == 1))};"
        f"  with two or more: {int(np.sum(nf_odd >= 2))}")

    # ---------------------------------------------------------------- 2. dropping times inside fibres
    sel = odd & (xs >= 3)
    xo, mo = xs[sel], ms[sel]
    # keep the fibres that contain at least two odd members x >= 3
    c3 = np.bincount(mo, minlength=M + 1)
    keep = c3[mo] >= 2
    xo, mo = xo[keep], mo[keep]
    so = sigma[xo]
    p_obs, npairs = pair_agreement(mo, so)
    e_obs = eta2(mo, so)
    out("\n2. DROPPING TIMES OF THE ODD MEMBERS OF A FIBRE   (sigma = standard steps, repo convention)")
    out(f"   odd members x >= 3 lying in fibres with at least two of them: {xo.size}, in {np.unique(mo).size} fibres, {npairs} pairs")
    out(f"   observed:  Pr[sigma(x) = sigma(x')] = {p_obs:.5f};   eta^2 (between-fibre share of Var sigma) = {e_obs:.5f}")
    out("   control: sigma shuffled among these x within strata x mod 2^k (k = 1 is a global shuffle)")
    lso = np.log(so.astype(float))
    e_log = eta2(mo, lso)
    out(f"   robust variant: eta^2 of ln(sigma) = {e_log:.5f}")
    out("     k    Pr same: mean of 200   sd       z     | eta^2(sigma): mean    sd      z    frac<=obs | eta^2(ln sigma): mean   sd      z")
    rng = np.random.default_rng(36)
    for kk in (1, 2, 3, 4, 6, 8, 10, 12):
        strata = xo & ((1 << kk) - 1)
        base = np.argsort(strata, kind="stable")
        ps, es, ls = [], [], []
        for _ in range(200):
            perm = np.lexsort((rng.random(xo.size), strata))
            sh = np.empty_like(so)
            sh[base] = so[perm]
            ps.append(pair_agreement(mo, sh)[0])
            es.append(eta2(mo, sh))
            ls.append(eta2(mo, np.log(sh.astype(float))))
        ps, es, ls = np.array(ps), np.array(es), np.array(ls)
        zp = (p_obs - ps.mean()) / ps.std(ddof=1)
        ze = (e_obs - es.mean()) / es.std(ddof=1)
        zl = (e_log - ls.mean()) / ls.std(ddof=1)
        out(f"    {kk:>2d}      {ps.mean():.5f}        {ps.std(ddof=1):.5f}  {zp:+6.2f}   |      {es.mean():.5f}   {es.std(ddof=1):.5f}  {ze:+6.2f}    {np.mean(es <= e_obs):.3f}   |"
            f"       {ls.mean():.5f}   {ls.std(ddof=1):.5f}  {zl:+6.2f}")
    out("   residue content of fibres (why small k shows an excess):")
    for mod in (4, 8):
        key = mo * mod + (xo % mod)
        _, c = np.unique(key, return_counts=True)
        same = float(np.sum(c * (c - 1) // 2)) / npairs
        base_p = sum((np.mean(xo % mod == r)) ** 2 for r in range(1, mod, 2))
        out(f"     Pr[x = x' mod {mod}] for two odd members of one fibre: {same:.4f}   (if independent: {base_p:.4f})")

    # ---------------------------------------------------------------- 3. Collatz arrows inside fibres
    out("\n3. COLLATZ ARROWS INSIDE A FIBRE (beyond the forced 2x -> x)")
    xodd = np.arange(1, N + 1, 2, dtype=np.int64)
    T = (3 * xodd + 1) // 2
    hit = xodd[phi[T] == phi[xodd]]
    out(f"   odd x <= {N} with phi((3x+1)/2) = phi(x): {hit.size}:  {hit[:40].tolist()}")
    def smooth3(m):
        while m % 2 == 0:
            m //= 2
        while m % 3 == 0:
            m //= 3
        return m == 1
    sm = [(int(v), int(phi[v]), int((3 * v + 1) // 2)) for v in hit.tolist() if smooth3(int(phi[v]))]
    out(f"     of these, with 3-smooth phi(x) (x, phi, T(x)): {sm}")
    out("     e.g. the whole fibre phi^-1(6) = {7, 9, 14, 18} is one shortcut path 18 -> 9 -> 14 -> 7, and")
    out("     1729 = 7*13*19 -> 2594 = 2*1297 -> 1297 stays in phi^-1(1296) = phi^-1(6^4) (1297 = 6^4 + 1 is prime).")
    hit2 = xodd[phi[3 * xodd + 1] == phi[xodd]]
    out(f"   odd x <= {N} with phi(3x+1) = phi(x): {hit2.size}:  {hit2[:40].tolist()}")
    xx = np.arange(3, N + 1, 2, dtype=np.int64)
    hit3 = xx[phi[dest[xx]] == phi[xx]]
    out(f"   odd x in [3, {N}] with phi(dest(x)) = phi(x): {hit3.size}:  {hit3[:40].tolist()}")
    # chance level: how often is phi(y) = phi(x) for y a random integer of the size of T(x)?
    rr = np.random.default_rng(1)
    chance = []
    for _ in range(20):
        yy = np.minimum(3 * N + 1, np.maximum(1, (T * rr.uniform(0.9, 1.1, size=T.size)).astype(np.int64)))
        chance.append(int(np.sum(phi[yy] == phi[xodd])))
    out(f"   chance level for the first count (y uniform within 10% of (3x+1)/2, 20 draws): mean {np.mean(chance):.1f}, sd {np.std(chance, ddof=1):.1f}")

    # ---------------------------------------------------------------- 4. the fibre of 36
    H = totient_height(phi[: N + 2])
    F = shapiro_F(H)
    out("\n4. THE FIBRE OF 36.   sigma = standard steps to drop (repo convention), k = shortcut steps = halvings,")
    out("   s = odd steps, sigma = k + s; word = shortcut parity word up to the drop; sig_inf = standard steps to 1.")
    out("     x   factorisation      (Z/x)* lattice parts          x mod 16  sigma  k  s  dest  word        sig_inf  max of orbit   x+1 = v        F(v)")
    parts = {37: "(2,2)", 57: "(1,0)+(1,2)", 63: "(1,1)+(1,1)", 74: "(2,2)", 76: "(1,0)+(1,2)",
             108: "(1,0)+(1,2)", 114: "(1,0)+(1,2)", 126: "(1,1)+(1,1)"}
    fibre = xs[ms == 36].tolist()
    assert fibre == [37, 57, 63, 74, 76, 108, 114, 126]
    for v in fibre:
        fac = " * ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sympy.factorint(v).items())
        orb, yv = [v], v
        while yv != 1:
            yv = yv // 2 if yv % 2 == 0 else 3 * yv + 1
            orb.append(yv)
        vfac = " * ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sympy.factorint(v + 1).items())
        out(f"   {v:>4d}  {fac:<16s}  {parts[v]:<28s}  {v % 16:>5d}   {int(sigma[v]):>5d} {int(k[v]):>2d} {int(s[v]):>2d}  {int(dest[v]):>4d}  "
            f"{parity_word(v):<10s}  {int(tst[v]):>6d}  {max(orb):>10d}     {v + 1:>4d} = {vfac:<10s} {int(F[v + 1]):>3d}")
        assert len(orb) - 1 == tst[v]
    out("   dropping-time multiset of the fibre: ", sorted(int(sigma[v]) for v in fibre),
        " odd members only:", sorted(int(sigma[v]) for v in fibre if v % 2))
    out("   37 = 5 mod 8 drops in 3 steps (class n = 1 mod 4); 57 = 9 mod 16 likewise; 63 = 2^6 - 1 climbs six")
    out("   odd steps first (v = 64 -> 729 = 3^6) and has sig_inf = 107.")
    out(f"\ndone in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
