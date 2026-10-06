"""Skeptic check of Q4.5-a/b/c.  Independent code: the STANDARD map (n/2 | q n + c), not the
researcher's shortcut arrays; classes built by brute force over residues, not by splitting.

CONVENTION.  dest(n) = first value < n on the orbit of n >= 2 (same for standard and shortcut map).
sigma(n) = number of standard steps to get there, k(n) = number of halvings, s(n) = odd steps.
M(d) = #{n >= 2 : dest(n) = d}.

Checks
  1. bounds n/2 <= dest < n, M >= 1, M = 1 on multiples of 3, M >= 2 on d = 1 mod 3 (d > 1),
     distribution, least d for each multiplicity -- for d <= 10^7 (twice the researcher's range).
  2. N(s) by an independent word count; mean M = sum N(s)/3^s (exact Fractions) and the observed mean.
  3. class formula: #{n : dest(n) = d, k(n) <= K} = #{classes (r,k,s), k <= K, d = d_r mod 3^s, t >= tmin}
     EXACTLY, for d <= 2*10^5, K = 16; exact 3-adic densities of {M_K = 1} for K = 4, 8, 12.
  4. coalescing pairs (k, d).
  5. mirror 3x-1 and cousin 5x+1, with the same code.
  6. NEW (skeptic): the martingale identity  sum_{dropped by j} N 3^s/4^k + sum_{alive at j} W(j,s) 3^s/4^j = 1
     for every j, and the consequence  mean of dest(n)/n = sum_s N(s) 3^s / 4^k(s) = 1 - p.

Run:  python -X utf8 v3_destination.py     (about 2 minutes)
"""
from __future__ import annotations

import math
import os
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v3_destination.log"), "w", encoding="utf-8")


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")


def drop_standard(N, q=3, c=1, max_steps=6000, cap=1 << 61):
    """dest, k (halvings), s (odd steps) for 2 <= n <= N under n -> n/2 | q n + c.  k = -1: no drop."""
    dest = np.zeros(N + 1, dtype=np.int64)
    kk = np.full(N + 1, -1, dtype=np.int32)
    ss = np.zeros(N + 1, dtype=np.int32)
    idx = np.arange(2, N + 1, dtype=np.int64)
    cur = idx.copy()
    kh = np.zeros(idx.size, dtype=np.int32)
    so = np.zeros(idx.size, dtype=np.int32)
    for _ in range(max_steps):
        if idx.size == 0:
            break
        odd = (cur & 1) == 1
        cur = np.where(odd, q * cur + c, cur >> 1)
        so += odd
        kh += ~odd
        done = cur < idx
        if done.any():
            dest[idx[done]] = cur[done]
            kk[idx[done]] = kh[done]
            ss[idx[done]] = so[done]
        keep = ~done & (cur < cap)
        idx, cur, kh, so = idx[keep], cur[keep], kh[keep], so[keep]
    return dest, kk, ss


def word_counts(smax):
    """N(s): number of parity words (shortcut letters) whose first prefix with 3^ones < 2^length
    is the whole word and has s ones.  Also returns alive[j] = {s: count} of not-yet-dropped words."""
    N = {}
    alive = [{0: 1}]
    j = 0
    while True:
        nxt = {}
        for s, w in alive[-1].items():
            # letter 1 (odd step): ones s+1, length j+1; 3^(s+1) > 2^(j+1) always when 3^s > 2^j
            nxt[s + 1] = nxt.get(s + 1, 0) + w
            # letter 0 (even step): ones s, length j+1
            if 3 ** s > 2 ** (j + 1):
                nxt[s] = nxt.get(s, 0) + w
            else:
                N[s] = N.get(s, 0) + w
        j += 1
        nxt = {s: w for s, w in nxt.items() if s <= smax}
        alive.append(nxt)
        if not nxt:
            break
    return N, alive


def stats(label, q, c, N, report_first=False):
    t0 = time.time()
    dest, k, s = drop_standard(N, q, c)
    n = np.arange(N + 1, dtype=np.int64)
    ok = k >= 0
    ok[:2] = False
    D = N // 2
    nd = int((~ok[2:]).sum())
    out(f"\n  {label}: 2 <= n <= {N}; n that never drop within the caps: {nd} ({nd / (N - 1):.4%})"
        f"  first: {n[2:][~ok[2:]][:10].tolist()}   [{time.time() - t0:.0f} s]")
    assert np.all((2 * dest[ok] >= n[ok]) & (dest[ok] < n[ok]))
    M = np.bincount(dest[ok], minlength=N + 1)[: D + 1]
    d = np.arange(D + 1)
    Md = M[1:]
    dd = d[1:]
    out(f"    n/2 <= dest(n) < n for every n that drops: True;  M(d) >= 1 for all 1 <= d <= {D}: {bool(Md.min() >= 1)}")
    mult = dd % q == 0
    out(f"    multiples of {q}: {int(mult.sum())}, of which M = 1: {int((Md[mult] == 1).sum())}")
    assert np.all(Md[mult] == 1)
    vals, cnts = np.unique(Md, return_counts=True)
    out(f"    mean M = {Md.mean():.6f}; max M = {int(Md.max())}")
    out("    m: frequency: least d  ->  " + ";  ".join(
        f"{int(v)}: {cn / D:.6f}: {int(dd[np.argmax(Md == v)])}" for v, cn in zip(vals, cnts)))
    for r in range(q):
        sel = dd % q == r
        out(f"    d = {r} mod {q}: mean M {Md[sel].mean():.4f}, Pr[M = 1] {np.mean(Md[sel] == 1):.4f}, min M {int(Md[sel].min())}")
    return dest, k, s, M


def main():
    t0 = time.time()
    N = 2 * 10 ** 7
    out("1. 3x+1, d <= 10^7")
    dest, k, s, M = stats("3x+1", 3, 1, N)
    D = N // 2
    Md = M[1:]
    dd = np.arange(1, D + 1)
    one = (dd % 3 == 1) & (dd > 1)
    out(f"    d = 1 mod 3, d > 1: min M = {int(Md[one].min())} (claim: >= 2);  M(1) = {int(Md[0])}")
    assert Md[one].min() >= 2
    out("    M(1..40) =", Md[:40].tolist())
    for X in (10 ** 2, 10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6, 5 * 10 ** 6, 10 ** 7):
        out(f"    max M(d), d <= {X}: {int(Md[:X].max())} at d = {int(np.argmax(Md[:X])) + 1}")
    out("    multiplicities missing between 1 and max:", sorted(set(range(1, int(Md.max()) + 1)) - set(Md.tolist())))

    # 2. mean multiplicity
    SM = 600
    Ns, alive = word_counts(SM)
    a100982 = [1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, 17637, 51033, 108950, 312455, 663535,
               1900470, 5936673, 13472296, 39993895, 87986917, 257978502, 820236724]
    assert [Ns[x] for x in range(1, 26)] == a100982 and Ns[0] == 1
    out("\n2. N(s) by independent word count: N(0) = 1, N(1..25) = A100982: True")
    ks = {x: (1 if x == 0 else int(math.floor(x * math.log2(3))) + 1) for x in range(SM + 1)}
    for x in range(1, SM + 1):
        assert 2 ** ks[x] > 3 ** x > 2 ** (ks[x] - 1)
    for smax in (25, 100, 200, 400, 550):
        mean = sum(Fraction(Ns[x], 3 ** x) for x in range(smax + 1))
        dens = sum(Fraction(Ns[x], 2 ** ks[x]) for x in range(smax + 1))
        low = sum(Fraction(Ns[x] * 3 ** x, 4 ** ks[x]) for x in range(smax + 1))
        out(f"    s <= {smax:>3d}: sum N/2^k = {float(dens):.12f}   sum N/3^s = {float(mean):.12f}   sum N 3^s/4^k = {float(low):.12f}")
    nn = np.arange(2, N + 1, dtype=np.int64)
    out(f"    observed: mean M(d), d <= {D}: {Md.mean():.6f};  mean n/dest(n): {np.mean(nn / dest[2:]):.6f};"
        f"  mean dest(n)/n: {np.mean(dest[2:] / nn):.6f}")

    # 3. class formula by brute force over residues
    K = 16
    cls = {}   # (k, s) -> list of (r, d_r)
    for r in range(1 << K):
        x, a3, j, sj = r, 1, 0, 0
        while j < K:
            if x & 1:
                x = (3 * x + 1) >> 1
                a3 *= 3
                sj += 1
            else:
                x >>= 1
            j += 1
            if a3 < (1 << j):
                rr = r & ((1 << j) - 1)
                if rr == r:                       # count each class once (its least representative)
                    cls.setdefault((j, sj), []).append((r, x))
                break
    ncls = sum(len(v) for v in cls.values())
    out(f"\n3. classes with k <= {K} by brute force over residues: {ncls}; by s: "
        f"{[sum(len(v) for (kk, sv), v in cls.items() if sv == t) for t in range(0, 11)]}")
    D0 = 200000
    model = np.zeros(D0 + 1, dtype=np.int64)
    for (kk, sv), lst in cls.items():
        mod = 3 ** sv
        for r, dr in lst:
            start = dr + (mod if r < 2 else 0)        # n = r + 2^k t >= 2 forces t >= 1 for r in {0, 1}
            if start <= D0:
                model[start::mod] += 1
    sel = (k[: 2 * D0 + 1] >= 0) & (k[: 2 * D0 + 1] <= K)
    sel[:2] = False
    brute = np.bincount(dest[: 2 * D0 + 1][sel], minlength=2 * D0 + 1)[: D0 + 1]
    out(f"    #{{n : dest(n) = d, k(n) <= {K}}} == class count, for every 1 <= d <= {D0}: "
        f"{bool(np.array_equal(brute[1:], model[1:]))}")
    assert np.array_equal(brute[1:], model[1:])
    full = M[: D0 + 1]
    out(f"    M(d) == class count (k <= {K}) for {np.mean(full[1:] == model[1:]):.4%} of d <= {D0}; never smaller: "
        f"{bool((full[1:] >= model[1:]).all())}")
    for KK in (4, 8, 12):
        S = max(sv for (kk, sv) in cls if kk <= KK)
        tot = np.zeros(3 ** S, dtype=np.int64)
        for (kk, sv), lst in cls.items():
            if kk <= KK:
                for r, dr in lst:
                    tot[dr % 3 ** sv:: 3 ** sv] += 1
        pr1 = Fraction(int((tot == 1).sum()), 3 ** S)
        out(f"    K = {KK:>2d}: exact 3-adic density of {{M_K = 1}} = {pr1} = {float(pr1):.6f};  mean M_K = {tot.mean():.6f}")
    tail = sum(Fraction(Ns[x], 3 ** x) for x in range(SM + 1)) - sum(
        Fraction(Ns[x], 3 ** x) for x in range(0, 16))
    out(f"    density of d met by some class with s > 15 (k > 24) is at most {float(tail):.4f}; so the natural density of")
    out("    {M = 1} exists (decreasing limit) and lies in [0.5330 - %.4f, 0.5330]; observed %.6f" % (float(tail), np.mean(Md == 1)))

    # 4. coalescing pairs
    key = dest[2:] * 4096 + k[2:]
    order = np.argsort(key, kind="stable")
    ks_ = key[order]
    dup = np.nonzero(ks_[1:] == ks_[:-1])[0]
    out(f"\n4. pairs n != n' <= {N} with the same (k, dest): {dup.size}: "
        f"{[(int(order[i]) + 2, int(order[i + 1]) + 2, int(k[order[i] + 2]), int(dest[order[i] + 2])) for i in dup[:8]]}")

    # 5. mirror and cousin
    out("\n5. MIRROR 3x-1 AND COUSIN 5x+1 (same code, n <= 4*10^6)")
    stats("3x+1 (reference)", 3, 1, 4 * 10 ** 6)
    stats("3x-1", 3, -1, 4 * 10 ** 6)
    stats("5x+1", 5, 1, 4 * 10 ** 6)

    # 6. martingale identity
    out("\n6. MARTINGALE IDENTITY (new).  X_j = 3^(s_j)/2^j is a martingale under fair parity bits (E = (3/2 + 1/2)/2 = 1).")
    Ns2, alive2 = word_counts(40)   # exact while s <= 40 is not truncated: j <= 40
    for j in (1, 2, 5, 10, 20, 40):
        dropped = sum(Fraction(Ns_ * 3 ** x, 4 ** ks[x]) for x, Ns_ in Ns2.items() if ks[x] <= j)
        al = sum(Fraction(w * 3 ** x, 4 ** j) for x, w in alive2[j].items())
        out(f"    j = {j:>2d}: dropped part {float(dropped):.10f} + alive part {float(al):.10f} = {dropped + al}")
        assert dropped + al == 1
    low = sum(Fraction(Ns[x] * 3 ** x, 4 ** ks[x]) for x in range(SM + 1))
    out(f"    limit: mean of dest(n)/n = sum_s N(s) 3^s/4^k(s) = {float(low):.10f} = 1 - p,  p = {1 - float(low):.10f}")
    out("    p = probability that a walk with odd-step probability 3/4 (the size-biased walk) never drops.")
    out(f"    observed mean dest(n)/n over n <= {N}: {np.mean(dest[2:] / nn):.6f}")
    out(f"\ndone in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
