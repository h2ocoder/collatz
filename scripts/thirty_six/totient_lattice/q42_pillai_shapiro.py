"""Q4.2 (first half)  The totient descent is trapped between log_3 and log_2.

Verifies, for every n <= 10^7 and in exact integer arithmetic:

  (P)  Pillai 1929:   2^(H-1) < n <= 2*3^(H-1)   for n >= 2,  H = H(n)
       i.e.  log_3(n/2) + 1 <= H(n) < log_2(n) + 1;  extremes 2*3^k (largest in its class);
       powers of 2 give H(2^k) = k = log_2 n.
  (S)  Shapiro 1943:  C = H - 1 satisfies C(mn) = C(m) + C(n) + [m and n both even];
       equivalently F (A064415) is COMPLETELY additive with F(2) = 1, F(p) = F(p-1).
  (F)  the clean two-sided form:  2^F(n) <= n <= 3^F(n) for all n >= 1,
       equality on the left iff n = 2^a, on the right iff n = 3^b.
  (L)  on the 3-smooth lattice:  F(2^a 3^b) = a + b  (the L1 norm), H(2^a 3^b) = a + b for a >= 1,
       and the totient chain of 2^a 3^b is the L-shaped monotone path
       (a,b) -> (a,b-1) -> ... -> (a,0) -> (a-1,0) -> ... -> (0,0).
  (I)  the Collatz-facing invariant:  F(T(n) + 1) = F(n + 1) for every odd n, T(n) = (3n+1)/2,
       because T(n) + 1 = 3(n+1)/2 and F(3) = F(2).  Mirror map 3x-1: same with n - 1.
       5x+1: (5n+1)/2 is v -> 5v/2 in v = 3n + 1 and F rises by exactly F(5) - F(2) = 1.

Run:  python -X utf8 q42_pillai_shapiro.py     (about 1 minute)
"""
from __future__ import annotations

import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import shapiro_F, spf_sieve, totient_height, totient_sieve  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "q42_pillai_shapiro.log"), "w", encoding="utf-8")


def out(*args):
    s = " ".join(str(a) for a in args)
    print(s, flush=True)
    LOG.write(s + "\n")


def main():
    t0 = time.time()
    N = 10 ** 7
    phi = totient_sieve(N)
    H = totient_height(phi)
    F = shapiro_F(H)
    n = np.arange(N + 1, dtype=np.int64)
    out(f"N = {N}.  H = A003434 (iterations of phi to reach 1), F = A064415.   [{time.time() - t0:.0f} s]")
    out("H(1..40) =", H[1:41].tolist())
    out("F(1..40) =", F[1:41].tolist())
    assert H[1:41].tolist() == [0, 1, 2, 2, 3, 2, 3, 3, 3, 3, 4, 3, 4, 3, 4, 4, 5, 3, 4, 4, 4, 4, 5, 4, 5, 4, 4,
                                4, 5, 4, 5, 5, 5, 5, 5, 4, 5, 4, 5, 5]
    assert F[1:41].tolist() == [0, 1, 1, 2, 2, 2, 2, 3, 2, 3, 3, 3, 3, 3, 3, 4, 4, 3, 3, 4, 3, 4, 4, 4, 4, 4, 3,
                                4, 4, 4, 4, 5, 4, 5, 4, 4, 4, 4, 4, 5]
    out("  both agree with the OEIS data for n = 1..40")

    # ---------------------------------------------------------------- (P) Pillai / Shapiro class bounds
    out("\n(P) CLASS BOUNDS.  class h = {n : H(n) = h}.  Claim: 2^(h-1) < n <= 2*3^(h-1).")
    out("   h    min n        max n <= N     2^(h-1)     2*3^(h-1)    min>2^(h-1)   max = 2*3^(h-1)?")
    a007755 = [1, 2, 3, 5, 11, 17, 41, 83, 137, 257, 641, 1097, 2329, 4369, 10537, 17477, 35209, 65537,
               140417, 281929, 557057, 1114129, 2384897, 4227137, 8978569]
    hmax = int(H[1:].max())
    order = np.argsort(H[1:], kind="stable") + 1
    Hs = H[order]
    bounds = np.searchsorted(Hs, np.arange(hmax + 2))
    mins = []
    ok_all = True
    for h in range(1, hmax + 1):
        members = order[bounds[h]:bounds[h + 1]]
        lo, hi = int(members.min()), int(members.max())
        mins.append(lo)
        top = 2 * 3 ** (h - 1)
        ok_lo = lo > 2 ** (h - 1)
        ok_hi = hi <= top
        ok_all &= ok_lo and ok_hi
        eq = "yes" if hi == top else ("(2*3^(h-1) > N)" if top > N else "NO")
        out(f"  {h:>2d}  {lo:>9d}  {hi:>12d}  {2 ** (h - 1):>10d}  {top:>12d}      {ok_lo}        {eq}")
    out("  all classes inside (2^(h-1), 2*3^(h-1)]:", ok_all)
    assert ok_all
    out("  least element of each class:", [1] + mins)
    out("  OEIS A007755                :", a007755[: len(mins) + 1])
    assert [1] + mins == a007755[: len(mins) + 1]
    # exact pointwise check
    p2 = np.left_shift(np.int64(1), (H[2:] - 1).astype(np.int64))
    p3 = 2 * np.power(np.int64(3), (H[2:] - 1).astype(np.int64))
    viol = int(np.sum(~((p2 < n[2:]) & (n[2:] <= p3))))
    out(f"  pointwise 2^(H-1) < n <= 2*3^(H-1), 2 <= n <= N: violations = {viol}")
    assert viol == 0

    # ---------------------------------------------------------------- (S) additivity
    out("\n(S) ADDITIVITY.")
    spf = spf_sieve(N)
    idx = np.arange(2, N + 1)
    lhs = F[idx]
    rhs = F[spf[idx]] + F[idx // spf[idx]]
    bad = int(np.sum(lhs != rhs))
    out(f"  F(n) = F(p) + F(n/p), p = least prime factor, all 2 <= n <= N: failures = {bad}")
    assert bad == 0
    primes = idx[spf[idx] == idx]
    oddp = primes[primes > 2]
    badp = int(np.sum(F[oddp] != F[oddp - 1]))
    out(f"  F(p) = F(p-1) for all {oddp.size} odd primes p <= N: failures = {badp}")
    assert badp == 0
    out("  => F is completely additive on [1, N] (induction on the number of prime factors).")
    rng = np.random.default_rng(4)
    m = rng.integers(2, 3162, size=2_000_000)
    k = rng.integers(2, 3162, size=2_000_000)
    C = H.astype(np.int64) - 1
    both_even = ((m % 2 == 0) & (k % 2 == 0)).astype(np.int64)
    bad2 = int(np.sum(C[m * k] != C[m] + C[k] + both_even))
    out(f"  Shapiro's form C(mk) = C(m) + C(k) + [m, k both even], 2*10^6 random pairs, mk < 10^7: failures = {bad2}")
    assert bad2 == 0

    # ---------------------------------------------------------------- (F) sandwich for F
    out("\n(F) SANDWICH  2^F(n) <= n <= 3^F(n).")
    Fi = F[1:].astype(np.int64)
    two, three = np.left_shift(np.int64(1), Fi), np.power(np.int64(3), Fi)
    v1 = int(np.sum(two > n[1:]))
    v2 = int(np.sum(three < n[1:]))
    out(f"  violations of 2^F <= n: {v1};  violations of n <= 3^F: {v2}   (1 <= n <= N)")
    assert v1 == 0 and v2 == 0
    eqL = n[1:][two == n[1:]]
    eqR = n[1:][three == n[1:]]
    out("  equality 2^F = n exactly for n =", eqL.tolist())
    out("  equality 3^F = n exactly for n =", eqR.tolist())
    assert all((x & (x - 1)) == 0 for x in eqL.tolist())
    ratio = Fi[1:] / np.log(n[2:])
    out(f"  F(n)/ln n over 2 <= n <= N: min {ratio.min():.4f} (1/ln 3 = {1 / math.log(3):.4f}), "
        f"max {ratio.max():.4f} (1/ln 2 = {1 / math.log(2):.4f}), mean {ratio.mean():.4f}")
    for lo, hi in ((10 ** 3, 10 ** 4), (10 ** 4, 10 ** 5), (10 ** 5, 10 ** 6), (10 ** 6, 10 ** 7)):
        r = F[lo:hi].astype(float) / np.log(np.arange(lo, hi))
        out(f"    mean F(n)/ln n on [{lo}, {hi}): {r.mean():.4f}   sd {r.std():.4f}")
    out("  (Erdos-Granville-Pomerance-Spiro 1990 conjecture H(n) ~ alpha ln n for almost all n;")
    out("   the mean ratio drifts slowly and sits strictly between 1/ln 3 and 1/ln 2.)")

    # ---------------------------------------------------------------- (L) the 3-smooth lattice
    out("\n(L) ON THE 3-SMOOTH LATTICE.")
    cnt = bad = 0
    a = 0
    while 2 ** a <= N:
        b = 0
        while 2 ** a * 3 ** b <= N:
            x = 2 ** a * 3 ** b
            cnt += 1
            if F[x] != a + b:
                bad += 1
            if x > 1:
                want_H = a + b if a >= 1 else b + 1
                if H[x] != want_H:
                    bad += 1
                if a >= 1 and b >= 1 and phi[x] != 2 ** a * 3 ** (b - 1):
                    bad += 1
                if a >= 1 and b == 0 and phi[x] != 2 ** (a - 1):
                    bad += 1
                if a == 0 and b >= 1 and phi[x] != 2 * 3 ** (b - 1):
                    bad += 1
            b += 1
        a += 1
    out(f"  3-smooth x <= N: {cnt}; failures of F = a+b, H = a+b (a>=1) / b+1 (a=0), and of the chain shape: {bad}")
    assert bad == 0
    chain, x = [], 36
    while x > 1:
        chain.append(x)
        x = int(phi[x])
    chain.append(1)
    out("  totient chain of 36 = 2^2 3^2:", " -> ".join(map(str, chain)),
        "  i.e. (2,2) -> (2,1) -> (2,0) -> (1,0) -> (0,0);  H(36) = 4 = 2 + 2")
    out("  sandwich on the lattice:  a log_3(2) + b = log_3 m  <=  a + b  <=  a + b log_2(3) = log_2 m.")

    # the dictionary entry: a Collatz dropping word with k halvings and s triplings takes
    # sigma = k + s standard steps, and that is the totient height of the lattice point 2^k 3^s
    def H_big(m):
        h = 0
        while m > 1:
            a2 = (m & -m).bit_length() - 1
            odd = m >> a2
            b3 = 0
            while odd % 3 == 0:
                odd //= 3
                b3 += 1
            assert odd == 1
            m = (2 ** a2 * 3 ** (b3 - 1)) if (a2 >= 1 and b3 >= 1) else (2 ** (a2 - 1) if b3 == 0 else 2 * 3 ** (b3 - 1))
            h += 1
        return h
    bad = 0
    spectrum = set()
    for x in range(2, 20001):
        y, kk, ss = x, 0, 0
        while True:
            if y % 2:
                y, ss = 3 * y + 1, ss + 1
            else:
                y, kk = y // 2, kk + 1
            if y < x:
                break
        spectrum.add(kk + ss)
        if H_big(2 ** kk * 3 ** ss) != kk + ss:
            bad += 1
    out(f"  dictionary: sigma(n) = k + s = H(2^k 3^s) for 2 <= n <= 20000 (sigma = standard steps to drop,")
    out(f"    repo convention; H by explicit totient chain of the 3-smooth number): failures = {bad}")
    out(f"    dropping times that occur below 20000: {sorted(spectrum)[:14]} ...  (= L1 norms of the staircase")
    out("    points (floor(s log2 3) + 1, s); OEIS A122437 gives this spectrum)")
    assert bad == 0

    # ---------------------------------------------------------------- (I) Collatz-facing invariant
    out("\n(I) INVARIANCE UNDER THE ODD COLLATZ STEP.  v = n + 1,  T(n) + 1 = 3 v / 2  (n odd).")
    odd = np.arange(1, (2 * N - 3) // 3 + 1, 2, dtype=np.int64)
    Tn = (3 * odd + 1) // 2
    Tn_ok = Tn + 1 <= N
    odd, Tn = odd[Tn_ok], Tn[Tn_ok]
    badI = int(np.sum(F[Tn + 1] != F[odd + 1]))
    out(f"  3x+1:  F(T(n)+1) = F(n+1) for all {odd.size} odd n with T(n)+1 <= N: failures = {badI}")
    assert badI == 0
    oddm = np.arange(3, (2 * N + 3) // 3, 2, dtype=np.int64)
    Tm = (3 * oddm - 1) // 2
    okm = Tm - 1 <= N
    oddm, Tm = oddm[okm], Tm[okm]
    badM = int(np.sum(F[Tm - 1] != F[oddm - 1]))
    out(f"  3x-1:  F(T'(n)-1) = F(n-1), T'(n) = (3n-1)/2, all {oddm.size} odd n >= 3 in range: failures = {badM}")
    assert badM == 0
    odd5 = np.arange(1, (2 * N) // 15, 2, dtype=np.int64)
    T5 = (5 * odd5 + 1) // 2
    ok5 = 3 * T5 + 1 <= N
    odd5, T5 = odd5[ok5], T5[ok5]
    d5 = F[3 * T5 + 1].astype(np.int64) - F[3 * odd5 + 1]
    out(f"  5x+1:  F(3 T5(n) + 1) - F(3n + 1), T5(n) = (5n+1)/2, {odd5.size} odd n: values = {np.unique(d5).tolist()}"
        "   (always +1 = F(5) - F(2))")
    assert np.unique(d5).tolist() == [1]
    out("  odd primes q with F(q) = F(2) = 1:", [int(q) for q in oddp[:2000] if F[q] == 1],
        " (F(q) = F(q-1) = 1 forces q - 1 = 2)")
    out("  n with F(n) = 1 below N:", n[1:][Fi == 1].tolist())
    out("  example n = 35: v = 36 = 2^2 3^2 -> 54 = 2 3^3 -> 81 = 3^4 (n: 35 -> 53 -> 80); F(v) = 4 throughout.")
    assert F[36] == F[54] == F[81] == 4

    # what F(n+1) does at even steps
    ev = np.arange(2, N - 1, 2, dtype=np.int64)
    dF = F[ev // 2 + 1].astype(np.int64) - F[ev + 1]
    vals, counts = np.unique(dF, return_counts=True)
    out("\n  at an EVEN step n -> n/2 the coordinate moves v -> (v+1)/2 and F is not conserved:")
    out("    F(n/2 + 1) - F(n + 1) over even n < N:  mean %.4f, sd %.4f, range [%d, %d]"
        % (dF.mean(), dF.std(), dF.min(), dF.max()))
    out("    distribution:", {int(v): int(c) for v, c in zip(vals, counts)})
    out(f"\ndone in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
    LOG.close()
