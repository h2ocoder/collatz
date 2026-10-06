"""Q4.5  The Collatz analogue of totient fibre multiplicity: how many n share a dropping destination?

CONVENTION.  dest(n) = first value < n on the orbit of n >= 2 (the same number for the standard
map and for the shortcut map T).  k(n) = number of shortcut steps to get there (= halvings),
s(n) = number of odd steps.  M(d) = #{n >= 2 : dest(n) = d},  d >= 1.

Statements checked here (proofs in the README)
  (a) n/2 <= dest(n) < n, so the fibre of d lies in (d, 2d]; it always contains 2d: M(d) >= 1.
  (b) 3 | d  =>  M(d) = 1.   So multiplicity ONE has density >= 1/3: the opposite of Carmichael.
  (c) Terras: on a dropping class n = r + 2^k t the destination is d = d_r + 3^s t.  Hence
          M(d) = #{dropping classes (r, k, s) : d = d_r mod 3^s and t >= t_min},
      a function of d that is locally constant in the 3-ADIC topology (up to the finitely many
      small d excluded by t >= t_min) -- dual to the dropping time, which is 2-adically
      locally constant in n.
  (d) mean multiplicity = sum_s N(s)/3^s with N(s) = OEIS A100982 (and N(0) = 1), equivalently
      the mean of 2^k/3^s over n.
  (e) which multiplicities occur (Ford-type question), by brute force.
  (f) multiplicity of the pair (k, d).
  (g) mirror maps: 3x-1 and 5x+1.

Run:  python -X utf8 q45_destination_multiplicity.py      (about 2 minutes)
"""
from __future__ import annotations

import math
import os
import sys
import time
from fractions import Fraction

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import dropping_arrays  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "q45_destination_multiplicity.log"), "w", encoding="utf-8")


def out(*args):
    s = " ".join(str(a) for a in args)
    print(s, flush=True)
    LOG.write(s + "\n")


def dropping_classes(K):
    """All dropping classes with k <= K for the 3x+1 shortcut map.

    Returns arrays r, k, s, d_r: every n = r (mod 2^k) has parity word of the class, and
    T^k(r + 2^k t) = d_r + 3^s t.  The class drops at step k: 3^s < 2^k and 3^s_i > 2^i before.
    Also returns the number of surviving (not yet dropped) classes at each level.
    """
    r = np.array([0], dtype=np.int64)
    val = np.array([0], dtype=np.int64)
    s = np.array([0], dtype=np.int64)
    rec_r, rec_k, rec_s, rec_d, surv = [], [], [], [], []
    pow3 = [3 ** i for i in range(40)]   # s <= K log_3(2) + 1 < 40 for K <= 60
    for j in range(0, K):
        # split each class mod 2^j into two classes mod 2^(j+1)
        p3 = np.array(pow3, dtype=np.int64)[s]
        r = np.concatenate([r, r + (1 << j)])
        val = np.concatenate([val, val + p3])
        s = np.concatenate([s, s])
        odd = (val & 1).astype(bool)
        # odd step: continue (3^(s+1) > 2^(j+1) automatically)
        r_o, v_o, s_o = r[odd], (3 * val[odd] + 1) >> 1, s[odd] + 1
        # even step: continue only if still 3^s > 2^(j+1)
        ev = ~odd
        r_e, v_e, s_e = r[ev], val[ev] >> 1, s[ev]
        above = np.array([pow3[x] > (1 << (j + 1)) for x in range(40)])[s_e]
        rec_r.append(r_e[~above])
        rec_k.append(np.full(int((~above).sum()), j + 1, dtype=np.int64))
        rec_s.append(s_e[~above])
        rec_d.append(v_e[~above])
        r = np.concatenate([r_o, r_e[above]])
        val = np.concatenate([v_o, v_e[above]])
        s = np.concatenate([s_o, s_e[above]])
        surv.append(r.size)
    return (np.concatenate(rec_r), np.concatenate(rec_k), np.concatenate(rec_s), np.concatenate(rec_d), surv)


def coefficient_stopping_time(N):
    """tau(n) = least j with 3^(s_j) < 2^j, s_j = number of odd steps among the first j (Terras)."""
    smax = [0] * 2100          # smax[j] = largest s with 3^s < 2^j
    s3 = 0
    for j in range(1, 2100):
        while 3 ** (s3 + 1) < 2 ** j:
            s3 += 1
        smax[j] = s3
    smax = np.array(smax, dtype=np.int32)
    tau = np.zeros(N + 1, dtype=np.int32)
    idx = np.arange(2, N + 1, dtype=np.int64)
    cur = idx.copy()
    ss = np.zeros(idx.size, dtype=np.int32)
    j = 0
    while idx.size:
        odd = (cur & 1).astype(bool)
        cur = np.where(odd, (3 * cur + 1) >> 1, cur >> 1)
        ss += odd
        j += 1
        done = ss <= smax[j]
        tau[idx[done]] = j
        keep = ~done
        idx, cur, ss = idx[keep], cur[keep], ss[keep]
    return tau


def word_counts(smax):
    """N(s), s = 0..smax: number of dropping classes with s odd steps (exact ints)."""
    N = {0: 1}
    cur = {0: 1}  # s -> number of not-yet-dropped words of the current length j
    j = 0
    while min(cur) <= smax if cur else False:
        nxt = {}
        for s, w in cur.items():
            nxt[s + 1] = nxt.get(s + 1, 0) + w
            if 3 ** s > 2 ** (j + 1):
                nxt[s] = nxt.get(s, 0) + w
            elif s >= 1:
                N[s] = N.get(s, 0) + w
        cur = {s: w for s, w in nxt.items() if s <= smax + 1}
        j += 1
        if j > 2 * smax + 10:
            break
    return [N.get(s, 0) for s in range(smax + 1)]


def multiplicity_stats(label, mult, add, N, q):
    k, s, dest = dropping_arrays(N, mult=mult, add=add, max_steps=3000, cap=1 << 60)
    nn = np.arange(2, N + 1)
    ok = k[2:] > 0
    D = N // 2
    M = np.bincount(dest[2:][ok], minlength=N + 1)[: D + 1]
    never = nn[~ok]
    out(f"\n  {label}:  n in [2, {N}]; n that do not drop (cycle minima, or orbit above 2^60 / 3000 steps): {never.size}"
        f"  ({never.size / nn.size:.4%});  first few: {never[:12].tolist()}")
    d = np.arange(1, D + 1)
    Md = M[1:]
    vals, cnts = np.unique(Md, return_counts=True)
    out(f"    d in [1, {D}]: mean M = {Md.mean():.5f};  max M = {int(Md.max())};  distribution: "
        + ", ".join(f"{int(v)}: {c / D:.4f}" for v, c in zip(vals, cnts) if c / D >= 5e-5))
    out(f"    M(d) = 0 for {int((Md == 0).sum())} values of d;  among multiples of {q}: M = 1 for "
        f"{int(((Md == 1) & (d % q == 0)).sum())} of {int((d % q == 0).sum())}, other values: "
        f"{sorted(set(Md[d % q == 0].tolist()) - {1})}")
    return k, s, dest, M


def main():
    t0 = time.time()
    N = 10 ** 7
    D = N // 2
    k, s, dest = dropping_arrays(N)
    assert (k[2:] > 0).all()
    n = np.arange(2, N + 1, dtype=np.int64)
    out(f"3x+1.  n in [2, {N}], so M(d) is complete for d <= {D}.   [{time.time() - t0:.0f} s]")

    # (a)
    assert np.all((2 * dest[2:] >= n) & (dest[2:] < n))
    out("(a) n/2 <= dest(n) < n for all n: verified.")
    M = np.bincount(dest[2:], minlength=N + 1)[: D + 1]
    d = np.arange(1, D + 1)
    Md = M[1:]
    assert Md.min() >= 1
    out(f"    M(d) >= 1 for all d <= {D} (n = 2d): verified.   M(1..40) = {Md[:40].tolist()}")

    # (b)
    assert np.all(Md[d % 3 == 0] == 1)
    out(f"(b) M(d) = 1 for every d divisible by 3 ({int((d % 3 == 0).sum())} values): verified.")
    vals, cnts = np.unique(Md, return_counts=True)
    out("    distribution of M(d), d <= %d:" % D)
    out("      m        count      frequency     least d with M(d) = m")
    first = {}
    for m in vals.tolist():
        first[m] = int(d[np.argmax(Md == m)])
    for v, c in zip(vals.tolist(), cnts.tolist()):
        out(f"     {v:>2d}   {c:>10d}     {c / D:.6f}      {first[v]}")
    out("    by residue of d mod 3:  " + ";  ".join(
        f"d = {r} mod 3: mean M {Md[d % 3 == r].mean():.4f}, Pr[M = 1] {np.mean(Md[d % 3 == r] == 1):.4f}" for r in range(3)))
    for X in (10 ** 2, 10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6, D):
        out(f"    max M(d) for d <= {X:>8d}: {int(Md[:X].max())}  (first at d = {int(np.argmax(Md[:X])) + 1})")
    dmax = int(np.argmax(Md)) + 1
    fib = (np.nonzero(dest[2:] == dmax)[0] + 2).tolist()
    out(f"    the fibre of d = {dmax}: n = {fib}  with shortcut dropping times k = {[int(k[x]) for x in fib]}")

    # (c) classes and the 3-adic model
    tau = coefficient_stopping_time(N)
    assert np.array_equal(tau[2:], k[2:])
    del tau
    out(f"\n    Terras' coefficient stopping time (least j with 3^(s_j) < 2^j) equals the dropping time k(n)")
    out(f"    for every 2 <= n <= {N}: verified.  (Known far beyond this range; open in general.)")
    K = 24
    cr, ck, cs, cd, surv = dropping_classes(K)
    out(f"\n(c) dropping classes with k <= {K}: {cr.size};  not yet dropped at level {K}: {surv[-1]} classes"
        f" (density {surv[-1] / 2 ** K:.5f})")
    by_s = np.bincount(cs)
    out("    classes by s:", by_s.tolist(), " (s >= 1: OEIS A100982 as long as k(s) <= K)")
    # sanity: destination formula on actual integers
    rng = np.random.default_rng(36)
    pick = rng.integers(0, cr.size, size=200000)
    t = rng.integers(1, 5, size=200000)
    nn = cr[pick] + (t << ck[pick])
    okr = nn <= N
    assert np.all(dest[nn[okr]] == cd[pick][okr] + 3 ** cs[pick][okr] * t[okr])
    assert np.all(k[nn[okr]] == ck[pick][okr])
    out(f"    dest(r + 2^k t) = d_r + 3^s t and k(n) = k: verified on {int(okr.sum())} random members with n <= N.")
    # model multiplicity for integer d: classes with k <= K, t >= t_min (t_min = 1 iff r < 2)
    D0 = 300000
    model = np.zeros(D0 + 1, dtype=np.int64)
    for smax in range(0, int(cs.max()) + 1):
        sel = cs == smax
        mod = 3 ** smax
        tmin = (cr[sel] < 2).astype(np.int64)
        start = cd[sel] + mod * tmin
        for st in start.tolist():
            if st <= D0:
                model[st::mod] += 1
    diff = Md[:D0] - model[1:]
    out(f"    for d <= {D0}:  M(d) - (number of classes with k <= {K} through d) is >= 0 everywhere: {bool((diff >= 0).all())};"
        f" nonzero for {int((diff > 0).sum())} values of d ({(diff > 0).mean():.4%}) -- classes with k > {K}")
    # 3-adic densities of the truncated function
    out("    exact densities of {d : M_K(d) = m}, M_K = number of classes with k <= K through the 3-adic")
    out("    residue of d  (computed on Z / 3^S, S = largest s with k(s) <= K):")
    out("      K     S    Pr[M_K=1]   Pr[=2]    Pr[=3]    Pr[=4]    Pr[=5]   Pr[>=6]   mean M_K")
    for KK in (4, 8, 12, 16, 20, 24):
        sel = ck <= KK
        S = int(cs[sel].max())
        tot = np.zeros(3 ** S, dtype=np.int16)
        for ss in range(0, S + 1):
            m2 = sel & (cs == ss)
            c = np.bincount(cd[m2] % 3 ** ss, minlength=3 ** ss).astype(np.int16)
            tot += np.tile(c, 3 ** (S - ss))
        pr = np.bincount(tot, minlength=8) / 3 ** S
        out(f"     {KK:>2d}    {S:>2d}    {pr[1]:.6f}  {pr[2]:.6f}  {pr[3]:.6f}  {pr[4]:.6f}  {pr[5]:.6f}  {pr[6:].sum():.6f}   {tot.mean():.6f}")
    out("    Pr[M_K = 1] decreases to the natural density of {M = 1}; observed frequency for d <= %d: %.6f" % (D, np.mean(Md == 1)))

    # (d) mean multiplicity
    Ns = word_counts(400)
    assert Ns[1:26] == [1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, 17637, 51033, 108950, 312455, 663535,
                        1900470, 5936673, 13472296, 39993895, 87986917, 257978502, 820236724]
    ks = [0 if x == 0 else int(math.floor(x * math.log2(3))) + 1 for x in range(401)]
    ks[0] = 1
    for x in range(1, 401):
        assert 2 ** ks[x] > 3 ** x > 2 ** (ks[x] - 1)
    out("\n(d) mean multiplicity.  N(s) from the word count (N(1..25) = A100982 checked).")
    out("      smax    sum N(s)/2^k(s)  (density dropped)      sum N(s)/3^s  (mean multiplicity so far)")
    for smax in (10, 25, 50, 100, 200, 400):
        dens = sum(Fraction(Ns[x], 2 ** ks[x]) for x in range(smax + 1))
        mean = sum(Fraction(Ns[x], 3 ** x) for x in range(smax + 1))
        out(f"      {smax:>4d}       {float(dens):.10f}                        {float(mean):.10f}")
    out(f"    observed mean of M(d), d <= {D}: {Md.mean():.6f};   mean of 2^k/3^s over 2 <= n <= N: "
        f"{np.mean(np.exp(k[2:] * math.log(2) - s[2:] * math.log(3))):.6f};   mean of n/dest(n): {np.mean(n / dest[2:]):.6f}")

    # (f) pairs (k, d)
    key = dest[2:] * 1024 + k[2:]
    uk, uc = np.unique(key, return_counts=True)
    out(f"\n(f) pairs (k, d): {uk.size} distinct pairs for {n.size} values of n; largest multiplicity of a pair: {int(uc.max())}")
    if uc.max() > 1:
        idx = np.nonzero(uc > 1)[0]
        out(f"    pairs with multiplicity >= 2: {idx.size}; multiplicity counts: "
            + str({int(v): int(c) for v, c in zip(*np.unique(uc, return_counts=True))}))
        for i in idx[:6].tolist():
            dd, kk = int(uk[i] // 1024), int(uk[i] % 1024)
            members = (np.nonzero((dest[2:] == dd) & (k[2:] == kk))[0] + 2).tolist()
            out(f"      d = {dd}, k = {kk}: n = {members}")
    else:
        out("    every (k, d) determines n uniquely in this range.")

    # (g) mirror maps
    out("\n(g) MIRROR MAPS, shortcut form x -> x/2 or (q x + c)/2, same definitions.")
    multiplicity_stats("3x+1 (reference)", 3, 1, 2 * 10 ** 6, 3)
    multiplicity_stats("3x-1", 3, -1, 2 * 10 ** 6, 3)
    multiplicity_stats("5x+1", 5, 1, 2 * 10 ** 6, 5)
    out(f"\ndone in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
