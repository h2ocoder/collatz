"""Skeptic check 2 (Q5.2-g, Lemma 1).  INDEPENDENT enumeration of E_k = {n : tau_k(n) >= n}
and of all fixed points / cycles of n -> tau_k(n), k = 2..8.

Different code path from q51_q52_tau3_dynamics.py:
  * pure integer arithmetic (num, den) instead of Fractions;
  * two-stage search: (i) exponent vectors on the primes p < k, pruned with the product of
    the per-prime maxima; (ii) extension by primes p >= k, where every factor is <= 1
    (g_k(p,1) = k/p <= 1 and g_k(p,a+1)/g_k(p,a) = (a+k)/((a+1)p) < 1), so the ratio only
    falls and the search stops as soon as it drops below 1;
  * cross-check by BRUTE FORCE from the definition: tau_k = 1 * tau_(k-1) (additive divisor
    sieve) for all n <= 3*10^6 and k = 2..8.

Run: python -X utf8 v2_tauk_attractors.py      (a few minutes; k = 8 dominates)
"""
import os
import sys
import time
from math import comb

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v2_tauk_attractors.log"), "w", encoding="utf-8")
sys.setrecursionlimit(10000)


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")
    LOG.flush()


def primes_upto(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]


PR = primes_upto(200000)


def tau_k_of(n, k, memo={}):
    """tau_k(n) by trial division (n must factor over PR)."""
    key = (n, k)
    if key in memo:
        return memo[key]
    m, r = n, 1
    for p in PR:
        if p * p > m:
            break
        if m % p == 0:
            a = 0
            while m % p == 0:
                m //= p
                a += 1
            r *= comb(a + k - 1, a)
    if m > 1:
        assert m < PR[-1] ** 2
        r *= k
    memo[key] = r
    return r


def enumerate_E(k):
    small = [p for p in PR if p < k]
    large = [p for p in PR if p >= k]
    # per-prime exponent tables on the small primes: (num = C(a+k-1,a), den = p^a)
    tables = []
    maxima = []          # (num, den) of the maximal g_k(p, a)
    for p in small:
        best = (1, 1)
        a = 0
        tab = [(1, 1, 0)]
        while True:
            a += 1
            nu, de = comb(a + k - 1, a), p ** a
            tab.append((nu, de, a))
            if nu * best[1] > best[0] * de:
                best = (nu, de)
            # stop when decreasing ((a+k) < (a+1)p) and g < 1 / (product of ALL maxima) is
            # certain; we do not know the other maxima yet, so use a crude safe bound: g < 10^-40
            if (a + k) < (a + 1) * p and nu * 10 ** 40 < de:
                break
        tables.append(tab)
        maxima.append(best)
    # tail products of maxima
    tailn = [1] * (len(small) + 1)
    taild = [1] * (len(small) + 1)
    for i in range(len(small) - 1, -1, -1):
        tailn[i] = tailn[i + 1] * maxima[i][0]
        taild[i] = taild[i + 1] * maxima[i][1]
    res = []          # (n, tau_k(n))

    def ext(num, den, n, li):
        # here num >= den (tau >= n); record, then try primes >= k from index li
        res.append((n, num))
        i = li
        while True:
            p = large[i]
            if num * k < den * p:
                break
            pa = 1
            a = 0
            while True:
                a += 1
                pa *= p
                nu = num * comb(a + k - 1, a)
                de = den * pa
                if nu < de:
                    break
                ext(nu, de, n * pa, i + 1)
            i += 1

    def rec(i, num, den, n):
        if i == len(small):
            if num >= den:
                ext(num, den, n, 0)
            return
        for nu, de, a in tables[i]:
            nn, dd = num * nu, den * de
            if nn * tailn[i + 1] >= dd * taild[i + 1]:
                rec(i + 1, nn, dd, n * small[i] ** a)

    rec(0, 1, 1, 1)
    res.sort()
    return res


def analyse(k):
    t0 = time.time()
    E = enumerate_E(k)
    ns = [n for n, _ in E]
    assert len(set(ns)) == len(ns)
    fixed = [n for n, t in E if t == n]
    asc = [(n, t) for n, t in E if t > n]
    # maximal ratio
    bn, bd = 1, 1
    for n, t in E:
        if t * bd > bn * n:
            bn, bd = t, n
    from math import gcd
    g = gcd(bn, bd)
    arg = [n for n, t in E if t * bd == bn * n]
    # cycles: follow every ascent
    cyc_of = {}
    cycles = set()
    for n, t in asc:
        path = [n]
        x = t
        seen = {n: 0}
        while x not in seen and x not in cyc_of:
            seen[x] = len(path)
            path.append(x)
            x = tau_k_of(x, k)
        if x in cyc_of:
            c = cyc_of[x]
        else:
            cyc = path[seen[x]:]
            m = cyc.index(min(cyc))
            c = tuple(cyc[m:] + cyc[:m])
            cycles.add(c)
        for y in path:
            cyc_of[y] = c
    proper = sorted(c for c in cycles if len(c) > 1)
    out(f"\n k = {k}: |E_k| = {len(E)}, max E_k = {ns[-1]}, #ascents = {len(asc)}  ({time.time()-t0:.1f}s)")
    out(f"   fixed points: {fixed}")
    out(f"   cycles (len >= 2): lengths {[len(c) for c in proper]}")
    for c in proper:
        out(f"      {list(c)}")
        assert all(tau_k_of(c[i], k) == c[(i + 1) % len(c)] for i in range(len(c)))
    out(f"   max tau_k(n)/n = {bn//g}/{bd//g} at n = {arg[:10]}")
    return ns, fixed, proper


def main():
    expect_size = {2: 2, 3: 10, 4: 100, 5: 1011, 6: 12309, 7: 159565, 8: 2208054}
    expect_fixed = {2: [1, 2], 3: [1, 3, 18, 36], 4: [1, 100, 200, 224, 560, 1344, 1920], 5: [1, 5, 75, 225],
                    6: [1, 441, 19559232], 7: [1, 7, 72030, 133111440, 399334320, 1944810000],
                    8: [1, 11859210000, 311203233792]}
    expect_cyc_len = {2: [], 3: [2], 4: [2, 2], 5: [2], 6: [11], 7: [2, 2, 3, 2, 2, 3, 2], 8: [2, 2, 2, 5, 14, 2]}
    kmax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    Es = {}
    allok = True
    for k in range(2, kmax + 1):
        ns, fixed, proper = analyse(k)
        Es[k] = ns
        ok = (len(ns) == expect_size[k] and fixed == expect_fixed[k]
              and sorted(len(c) for c in proper) == sorted(expect_cyc_len[k]))
        out(f"   agrees with the researcher's table (|E_k|, fixed points, cycle lengths): {ok}")
        allok &= ok
    out("\nALL k agree with README table 3.5:", allok)

    # brute force from the definition, n <= 3*10^6
    N = 3 * 10 ** 6
    t0 = time.time()
    cur = np.ones(N + 1, dtype=np.int64)      # tau_1 = 1
    cur[0] = 0
    idx = np.arange(N + 1, dtype=np.int64)
    out(f"\nbrute force tau_k = 1 * tau_(k-1) by additive divisor sieve, n <= {N}")
    for k in range(2, kmax + 1):
        nxt = np.zeros(N + 1, dtype=np.int64)
        cl = cur.tolist()
        for d in range(1, N + 1):
            nxt[d::d] += cl[d]
        cur = nxt
        ge = (np.nonzero(cur[1:] >= idx[1:])[0] + 1).tolist()
        mine = [n for n in Es[k] if n <= N]
        out(f"   k = {k}: #{{n <= N : tau_k(n) >= n}} = {len(ge)}; equals DFS list restricted to n <= N: {ge == mine}"
            f"   ({time.time()-t0:.0f}s)")
        fx = [n for n in ge if cur[n] == n]
        out(f"          fixed points <= N by brute force: {fx}")
    LOG.close()


if __name__ == "__main__":
    main()
