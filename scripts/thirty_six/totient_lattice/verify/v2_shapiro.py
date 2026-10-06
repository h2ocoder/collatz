"""Skeptic check of Q4.2-a/b/c.  Independent code path.

The researcher computed H by iterating a totient sieve and DEFINED F from H (F = H or H - 1).
Here F is built from its ADDITIVE definition (F(2) = 1, F(p) = F(p-1), F(mn) = F(m) + F(n))
with a smallest-prime-factor sieve, phi is built multiplicatively from the same sieve, H by
dynamic programming H(n) = 1 + H(phi(n)); then the claimed relations are tested, to N = 3*10^7
(three times the researcher's range, so the class h = 16 maximum 2*3^15 = 28697814 is inside).

Edge cases: n = 1, m = 1 in Shapiro's formula, the primes 2 and 3, 0 and negative arguments in
the Collatz-facing invariant, and general odd multipliers q (q x + c maps).

Run:  python -X utf8 v2_shapiro.py     (about 1.5 minutes)
"""
from __future__ import annotations

import math
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v2_shapiro.log"), "w", encoding="utf-8")


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")


def main():
    t0 = time.time()
    N = 3 * 10 ** 7
    # smallest prime factor
    spf = np.zeros(N + 1, dtype=np.int32)
    lim = int(N ** 0.5) + 1
    for p in range(2, lim + 1):
        if spf[p] == 0:
            seg = spf[p * p:: p]
            seg[seg == 0] = p
    idx = np.arange(N + 1, dtype=np.int32)
    prime = spf == 0
    prime[:2] = False
    spf[prime] = idx[prime]
    out(f"N = {N}; spf sieve done, {int(prime.sum())} primes   [{time.time() - t0:.0f} s]")

    # F and phi, in increasing n, vectorised by 'generation': n = p * m with m < n.
    # process n in blocks so that cofactors m = n / spf(n) <= n/2 are already known.
    F = np.zeros(N + 1, dtype=np.int16)
    phi = np.zeros(N + 1, dtype=np.int32)
    phi[1] = 1
    F[2] = 1
    phi[2] = 1
    lo = 3
    while lo <= N:
        hi = min(N, 2 * lo - 2)          # for n in [lo, hi]: n-1 < n and n/spf <= hi/2 < lo, all known...
        n = np.arange(lo, hi + 1, dtype=np.int64)
        p = spf[lo: hi + 1].astype(np.int64)
        m = n // p
        isp = m == 1
        comp = ~isp
        # composites first: need F[p], phi[p] for primes p in the same block?  p <= sqrt(n) < lo for n >= 9.
        # (for lo = 3: block [3,4]; 4 = 2*2 fine.  lo = 5: [5,8]: 6 = 2*3, 8 = 2*4 fine.)
        Fc = F[p[comp]] + F[m[comp]]
        mm = m[comp]
        pp = p[comp]
        ph = np.where(mm % pp == 0, phi[mm].astype(np.int64) * pp, phi[mm].astype(np.int64) * (pp - 1))
        F[n[comp]] = Fc
        phi[n[comp]] = ph
        # primes: F(p) = F(p-1); p-1 may lie in the same block (it is composite or 2), now filled.
        F[n[isp]] = F[n[isp] - 1]
        phi[n[isp]] = n[isp] - 1
        lo = hi + 1
    out(f"F (additive definition) and phi (multiplicative) built   [{time.time() - t0:.0f} s]")
    assert F[1:41].tolist() == [0, 1, 1, 2, 2, 2, 2, 3, 2, 3, 3, 3, 3, 3, 3, 4, 4, 3, 3, 4, 3, 4, 4, 4, 4, 4, 3,
                                4, 4, 4, 4, 5, 4, 5, 4, 4, 4, 4, 4, 5]
    # spot-check phi against sympy
    from sympy import totient
    rng = np.random.default_rng(7)
    for x in rng.integers(1, N, size=300).tolist() + [1, 2, 3, 4, 36, 37, 108, 126, N]:
        assert int(phi[x]) == int(totient(x)), x
    out("phi agrees with sympy.totient on 300 random n and the fibre of 36;  F(1..40) = A064415")

    # H by DP
    H = np.zeros(N + 1, dtype=np.int16)
    lo = 2
    while lo <= N:
        hi = min(N, 2 * lo - 1)          # phi(n) < n; need H[phi(n)] known: phi(n) <= n - 1, may be in the block
        # iterate inside the block until stable (phi(n) < lo for most n; the rest resolve in a few passes)
        n = np.arange(lo, hi + 1, dtype=np.int64)
        ph = phi[lo: hi + 1].astype(np.int64)
        pending = np.ones(n.size, dtype=bool)
        known = np.zeros(N + 1, dtype=bool) if lo == 2 else known
        known[1] = True
        while pending.any():
            ready = pending & known[ph]
            H[n[ready]] = H[ph[ready]] + 1
            known[n[ready]] = True
            pending &= ~ready
        lo = hi + 1
    assert H[1:41].tolist() == [0, 1, 2, 2, 3, 2, 3, 3, 3, 3, 4, 3, 4, 3, 4, 4, 5, 3, 4, 4, 4, 4, 5, 4, 5, 4, 4,
                                4, 5, 4, 5, 5, 5, 5, 5, 4, 5, 4, 5, 5]
    out(f"H by DP built; H(1..40) = A003434   [{time.time() - t0:.0f} s]")

    n = np.arange(N + 1, dtype=np.int64)
    odd = (n % 2 == 1)
    # Lemma 1
    bad = int(np.sum(H[2:] != F[2:] + odd[2:]))
    out(f"\nQ4.2-a.  H(n) = F(n) + [n odd] for 2 <= n <= N: failures {bad};  H(1) = {int(H[1])}, F(1) = {int(F[1])} (n = 1 is the exception: odd, H = F)")
    assert bad == 0
    Fi = F.astype(np.int64)
    two = np.left_shift(np.int64(1), Fi[1:])
    three = np.power(np.int64(3), Fi[1:])
    v1 = int(np.sum(two > n[1:]))
    v2 = int(np.sum(three < n[1:]))
    out(f"  2^F(n) <= n <= 3^F(n), 1 <= n <= N: violations {v1}, {v2}   (max F = {int(Fi.max())}, 3^maxF fits int64: {3 ** int(Fi.max()) < 2 ** 63})")
    assert v1 == 0 and v2 == 0
    eqL = n[1:][two == n[1:]].tolist()
    eqR = n[1:][three == n[1:]].tolist()
    out(f"  equality 2^F = n: {len(eqL)} values, all powers of 2: {all(x & (x - 1) == 0 for x in eqL)};"
        f" every power of 2 <= N present: {len(eqL) == N.bit_length()}")

    def pow3(x):
        while x % 3 == 0:
            x //= 3
        return x == 1
    out(f"  equality 3^F = n: {len(eqR)} values, all powers of 3: {all(pow3(x) for x in eqR)};"
        f" every power of 3 <= N present: {len(eqR) == int(math.log(N, 3)) + 1}")
    ev = n[2::2]
    v3 = int(np.sum(ev > 2 * np.power(np.int64(3), Fi[2::2] - 1)))
    out(f"  Lemma 3, even case n <= 2*3^(F-1): violations {v3}")
    Hi = H.astype(np.int64)
    pl = int(np.sum(~((np.left_shift(np.int64(1), Hi[2:] - 1) < n[2:]) & (n[2:] <= 2 * np.power(np.int64(3), Hi[2:] - 1)))))
    out(f"  Pillai: 2^(H-1) < n <= 2*3^(H-1), 2 <= n <= N: violations {pl}")
    assert v3 == 0 and pl == 0
    hmax = int(H.max())
    mx = np.zeros(hmax + 1, dtype=np.int64)
    np.maximum.at(mx, H[1:], n[1:])
    mn = np.full(hmax + 1, N + 1, dtype=np.int64)
    np.minimum.at(mn, H[1:], n[1:])
    okmax = [h for h in range(1, hmax + 1) if 2 * 3 ** (h - 1) <= N]
    out(f"  largest n with H = h equals 2*3^(h-1) for every h with 2*3^(h-1) <= N (h = 1..{max(okmax)}): "
        f"{all(int(mx[h]) == 2 * 3 ** (h - 1) for h in okmax)}")
    assert all(int(mx[h]) == 2 * 3 ** (h - 1) for h in okmax)
    out("  least n of each class h = 0..%d: %s" % (hmax, mn.tolist()))
    a007755 = [1, 2, 3, 5, 11, 17, 41, 83, 137, 257, 641, 1097, 2329, 4369, 10537, 17477, 35209, 65537,
               140417, 281929, 557057, 1114129, 2384897, 4227137, 8978569, 16843009]
    out("  equals OEIS A007755 (26 terms):", mn.tolist()[: len(a007755)] == a007755[: hmax + 1])
    # Shapiro's class function, including the m = 1 edge
    C = Hi - 1
    rngp = np.random.default_rng(11)
    a = rngp.integers(2, 5400, size=3_000_000)
    b = rngp.integers(2, 5400, size=3_000_000)
    both = ((a % 2 == 0) & (b % 2 == 0)).astype(np.int64)
    bad = int(np.sum(C[a * b] != C[a] + C[b] + both))
    out(f"  Shapiro C(mn) = C(m) + C(n) + [both even], C = H - 1, 3*10^6 random pairs m, n >= 2: failures {bad}")
    assert bad == 0
    out(f"  EDGE m = 1: C(1) = H(1) - 1 = {int(C[1])};  C(1*n) = C(n) but C(1) + C(n) = C(n) - 1: the formula FAILS at m = 1")
    out("       unless C(1) := 0 (Shapiro's own convention C(1) = C(2) = 0).  README must say m, n >= 2 or C(1) = 0.")
    r = Fi[10 ** 6: 10 ** 7] / np.log(n[10 ** 6: 10 ** 7])
    out(f"  mean F(n)/ln n on [10^6, 10^7): {r.mean():.4f};  on [10^7, 3*10^7): {(Fi[10 ** 7:] / np.log(n[10 ** 7:])).mean():.4f}")

    # Q4.2-b
    cnt = bad = 0
    aa = 0
    while 2 ** aa <= N:
        bb = 0
        while 2 ** aa * 3 ** bb <= N:
            x = 2 ** aa * 3 ** bb
            cnt += 1
            bad += int(F[x]) != aa + bb
            if x > 1:
                bad += int(H[x]) != (aa + bb if aa >= 1 else bb + 1)
            bb += 1
        aa += 1
    out(f"\nQ4.2-b.  F(2^a 3^b) = a + b and H = a + b (a >= 1), b + 1 (a = 0, b >= 1) on {cnt} 3-smooth x <= N: failures {bad}")
    assert bad == 0
    out("  note H(3^b) = b + 1 != 0 + b: 'H is the L1 norm' fails on the axis a = 0; F is the L1 norm everywhere.")
    out("  with 5 in place of 3: F(5) =", int(F[5]), " F(2^a 5^b) = a + 2b (not the L1 norm);  F(7) =", int(F[7]))
    chain, x = [], 36
    while x > 1:
        chain.append(x)
        x = int(phi[x])
    out("  totient chain of 36:", chain + [1])

    # Q4.2-c, general q x + c
    out("\nQ4.2-c.  odd step n -> (q n + c)/2 in the coordinate v = (q - 2) n + c:  v -> q v / 2 exactly.")
    for q, c in ((3, 1), (3, -1), (5, 1), (5, -1), (7, 1), (9, 1), (3, 5), (3, 7)):
        nmax = (2 * N - 2 * abs(c) - 2) // (q * max(1, q - 2)) - 2
        o = np.arange(3, nmax, 2, dtype=np.int64)
        T = (q * o + c) // 2
        v0 = (q - 2) * o + c
        v1 = (q - 2) * T + c
        okv = (v0 > 0) & (v1 > 0) & (v1 <= N)
        assert np.all(2 * v1[okv] == q * v0[okv])
        dF = Fi[v1[okv]] - Fi[v0[okv]]
        out(f"  {q}x{c:+d}: F(v') - F(v) over {int(okv.sum())} odd n: values {np.unique(dF).tolist()}"
            f"   (F({q}) - F(2) = {int(F[q]) - 1})")
    out("  => conserved iff F(q) = 1 iff q = 3; the SIGN c and even the value of c (3x+5, 3x+7) are irrelevant.")
    out("  n with F(n) = 1, n <= N:", n[1:][Fi[1:] == 1].tolist())
    # negative integers under 3x+1 (the true mirror): v = n + 1 <= 0; use F(|v|), v = 0 at the fixed point n = -1
    bad = 0
    for x in range(-3, -200001, -2):
        T = (3 * x + 1) // 2
        v, w = abs(x + 1), abs(T + 1)
        if w <= N and int(F[w]) != int(F[v]):
            bad += 1
    out(f"  negative odd n in [-200001, -3] under 3x+1, with F(|n + 1|): failures {bad}   (n = -1 gives v = 0, F undefined)")
    out("  F(n+1) therefore cannot tell 3x+1 from 3x-1, nor positive from negative n.")
    # any completely additive f with f(2) = f(3) works: Omega restricted? e.g. f = (number of prime factors 2 or 3)
    o = np.arange(1, 10 ** 6, 2, dtype=np.int64)
    def v_p(arr, p):
        res = np.zeros(arr.size, dtype=np.int64)
        a_ = arr.copy()
        while True:
            dv = a_ % p == 0
            if not dv.any():
                break
            res += dv
            a_ = np.where(dv, a_ // p, a_)
        return res
    g0 = v_p(o + 1, 2) + v_p(o + 1, 3)
    g1 = v_p((3 * o + 1) // 2 + 1, 2) + v_p((3 * o + 1) // 2 + 1, 3)
    out(f"  control: g(v) = v_2(v) + v_3(v) is conserved by the odd step too: failures {int(np.sum(g0 != g1))}"
        " -- the invariant does not need the totient.")
    # even-step statistics
    e = np.arange(2, 10 ** 7 - 1, 2, dtype=np.int64)
    dF = Fi[e // 2 + 1] - Fi[e + 1]
    out(f"  even step, F(n/2 + 1) - F(n + 1), even n < 10^7: mean {dF.mean():.4f}, sd {dF.std():.4f}")
    out(f"\ndone in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
