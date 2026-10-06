"""Q5.1 / Q5.2   F(n) = sum_{d|n} tau(d) = tau_3(n) = prod T_(a_i+1)  as a dynamical system.

F is OEIS A007425 (d_3, the number of ordered factorisations n = r*s*t); it is also the
number of pairs e | d | n, i.e. the number of intervals of the divisor lattice of n.

What this script does
  [A] exact, finite enumeration of E_k = {n : tau_k(n) >= n} for k = 2..8 by a pruned
      depth-first search whose pruning bound is proved in README.md (Lemma 1).  From E_k
      it reads off ALL fixed points and ALL cycles of n -> tau_k(n).  k = 3 is F.
  [B] sieve of F up to N = 10^7 (independent check of [A] for k = 3), attractor of every
      n <= N, basin sizes at 10^3..10^7, transient-length ("total stopping time")
      distribution, record holders, max F(n)/n.
  [C] least n of each transient length among ALL n < 10^40, using the fact that the
      orbit of n depends only on its prime signature (so the least n with a given
      transient is a least-of-signature number, OEIS A025487).

CONVENTION: "transient length" t(n) = least t >= 0 with F^t(n) periodic.  The Collatz-style
"dropping time" (first t with F^t(n) < n) is 1 for every n outside the ten-element set E_3.

Run:  python -X utf8 q51_q52_tau3_dynamics.py      (about 5.5 minutes, single process; 5 of them are k = 8 in [A])
Output: q51_q52_tau3_dynamics.log / .json
"""
import json
import os
import sys
import time
from fractions import Fraction
from math import comb

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "q51_q52_tau3_dynamics.log"), "w", encoding="utf-8")


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


def small_primes(n):
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i in range(n + 1) if sieve[i]]


PR = small_primes(100000)


def factor_small(n):
    f = {}
    for p in PR:
        if p * p > n:
            break
        while n % p == 0:
            f[p] = f.get(p, 0) + 1
            n //= p
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def tau_k(n, k):
    r = 1
    for a in factor_small(n).values():
        r *= comb(a + k - 1, k - 1)
    return r


# ------------------------------------------------------------------ [A]
def g(k, p, a):
    return Fraction(comb(a + k - 1, k - 1), p ** a)


def M(k, p):
    """max over a >= 0 of g(k,p,a); the ratio g(a+1)/g(a) = (a+k)/((a+1)p) is decreasing in a."""
    best = Fraction(1)
    a = 0
    while True:
        a += 1
        v = g(k, p, a)
        if v > best:
            best = v
        if Fraction(a + k, (a + 1) * p) < 1 and v < 1:
            # from here on g decreases and is already below 1 -> cannot matter
            break
        if a > 10 * k + 50:
            break
    return best


def enumerate_E(k):
    """All n with tau_k(n) >= n.  DFS over primes in increasing order.

    State: (n, R = tau_k(n)/n, index of next prime).  Prune when R * B < 1 where
    B = product over all later primes of max(1, M(k,p)); this is a finite product because M(k,p) = 1 for p >= k (README, Lemma 1).
    """
    # tail bound: product of M(k,p) over primes p >= PR[i]   (M(k,p) = 1 for p >= k when k >= 2:
    # g(k,p,1) = k/p <= 1 and the ratio (a+k)/((a+1)p) <= (k+1)/(2p) < 1)
    Ms = []
    i = 0
    while PR[i] < k:
        Ms.append(M(k, PR[i]))
        i += 1
    nsmall = len(Ms)
    tail = [Fraction(1)] * (nsmall + 1)
    for j in range(nsmall - 1, -1, -1):
        tail[j] = tail[j + 1] * max(Fraction(1), Ms[j])
    res = []

    def dfs(n, R, idx):
        # n uses only primes with index < idx
        if R >= 1:
            res.append(n)
        j = idx
        while True:
            p = PR[j]
            B = tail[j] if j < nsmall else Fraction(1)
            if R * B < 1:
                # no extension using primes >= p can reach ratio >= 1
                # (for j >= nsmall every further factor is <= 1 and R < 1 already)
                break
            # is any exponent of p viable?
            a = 1
            any_viable = False
            pa = p
            while True:
                Rn = R * g(k, p, a)
                Bn = tail[j + 1] if j + 1 <= nsmall else Fraction(1)
                if Rn * Bn >= 1:
                    any_viable = True
                    dfs(n * pa, Rn, j + 1)
                # stop when g is decreasing and already too small
                if Fraction(a + k, (a + 1) * p) < 1 and Rn * Bn < 1:
                    break
                a += 1
                pa *= p
            if j >= nsmall and not any_viable:
                # for primes p >= k, g(k,p,1) = k/p decreases with p: larger primes fail too
                break
            j += 1

    dfs(1, Fraction(1), 0)
    return sorted(res)


def part_A(results):
    out("=" * 78)
    out("[A] E_k = {n : tau_k(n) >= n}, fixed points and cycles of n -> tau_k(n), k = 2..8")
    out("=" * 78)
    fam = {}
    for k in range(2, 9):
        t0 = time.time()
        E = enumerate_E(k)
        fixed = [n for n in E if tau_k(n, k) == n]
        asc = [n for n in E if tau_k(n, k) > n]
        # every cycle of length >= 2 contains an ascent; follow each ascent's orbit
        cycles = set()
        maxratio = max(Fraction(tau_k(n, k), n) for n in E)
        argmax = [n for n in E if Fraction(tau_k(n, k), n) == maxratio]
        for n in asc:
            seen = []
            x = n
            while x not in seen:
                seen.append(x)
                x = tau_k(x, k)
            cyc = seen[seen.index(x):]
            if len(cyc) > 1:
                m = cyc.index(min(cyc))
                cycles.add(tuple(cyc[m:] + cyc[:m]))
        cycles = sorted(cycles)
        fam[k] = {"size_E": len(E), "max_E": E[-1], "fixed": fixed, "cycles": [list(c) for c in cycles],
                  "n_ascents": len(asc), "max_ratio": str(maxratio), "argmax": argmax[:10]}
        out(f"\n k = {k}:  |E_k| = {len(E)}, max E_k = {E[-1]}, #ascents = {len(asc)}   ({time.time()-t0:.1f}s)")
        out(f"   fixed points : {fixed}")
        out(f"   cycles (len>=2): {[list(c) for c in cycles]}")
        out(f"   max tau_k(n)/n = {maxratio} at n = {argmax[:10]}")
        if k == 3:
            out(f"   E_3 = {E}")
            out(f"   ascents (F(n) > n): {[(n, tau_k(n,3)) for n in asc]}")
            out(f"   F(n) = 3n/2 exactly at n = {[n for n in E if 2*tau_k(n,3) == 3*n]}")
            assert E == [1, 2, 3, 4, 6, 8, 12, 18, 24, 36]
            assert fixed == [1, 3, 18, 36]
            assert [list(c) for c in cycles] == [[6, 9]]
    results["tau_k_family"] = fam
    # brute-force cross-check of E_k for small k against direct search
    for k, lim in ((2, 10 ** 5), (3, 10 ** 5), (4, 3 * 10 ** 5)):
        direct = [n for n in range(1, lim + 1) if tau_k(n, k) >= n]
        E = enumerate_E(k)
        okk = direct == [n for n in E if n <= lim] and (E[-1] <= lim)
        out(f" cross-check k={k}: direct search n <= {lim} reproduces E_k: {okk}")
        results[f"E{k}_crosscheck"] = okk


# ------------------------------------------------------------------ [B]
def part_B(results, N=10 ** 7):
    out("\n" + "=" * 78)
    out(f"[B] sieve of F = tau_3 up to N = {N}")
    out("=" * 78)
    t0 = time.time()
    sieve = np.ones(N + 1, dtype=bool)
    sieve[:2] = False
    for i in range(2, int(N ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = False
    primes = np.nonzero(sieve)[0]
    F = np.ones(N + 1, dtype=np.int64)
    for p in primes.tolist():
        pk = p
        a = 1
        while pk <= N:
            # multiples of p^a currently carry the factor T_a; replace it by T_(a+1)
            Ta = a * (a + 1) // 2
            Ta1 = (a + 1) * (a + 2) // 2
            view = F[pk::pk]
            if Ta == 1:
                view *= Ta1
            else:
                view //= Ta
                view *= Ta1
            pk *= p
            a += 1
    F[0] = 0
    out(f"   sieve done in {time.time()-t0:.1f}s;  pi(N) = {len(primes)}")
    # spot check against direct factorisation
    rng = np.random.default_rng(36)
    for n in rng.integers(1, N + 1, size=2000).tolist() + list(range(1, 200)):
        assert int(F[n]) == tau_k(n, 3), n
    out("   spot check vs direct factorisation: 2199 values OK")

    idx = np.arange(N + 1)
    ge = np.nonzero(F[1:] >= idx[1:])[0] + 1
    out(f"   n <= N with F(n) >= n : {ge.tolist()}")
    out(f"   n <= N with F(n) =  n : {[n for n in ge.tolist() if F[n] == n]}")
    out(f"   n <= N with F(n) >  n : {[n for n in ge.tolist() if F[n] > n]}")
    ratio = F[1:] / idx[1:]
    out(f"   max F(n)/n = {ratio.max()} at n = {(np.nonzero(ratio == ratio.max())[0] + 1).tolist()}")
    results["B_F_ge_n"] = ge.tolist()

    maxF = int(F.max())
    out(f"   max F(n) for n <= N: {maxF} at n = {int(np.argmax(F))}")
    periodic = {1: 1, 3: 3, 18: 18, 36: 36, 6: 6, 9: 6}   # value -> attractor label (6 = the 2-cycle {6,9})
    lab = np.zeros(maxF + 1, dtype=np.int64)
    tr = np.zeros(maxF + 1, dtype=np.int64)
    for m in range(1, maxF + 1):
        x, t = m, 0
        while x not in periodic:
            x = int(F[x])
            t += 1
        lab[m] = periodic[x]
        tr[m] = t
    label = lab[F]            # attractor of F(n) == attractor of n
    trans = tr[F] + 1
    for m in periodic:
        trans[m] = 0
    label[0] = 0
    trans[0] = 0

    names = {1: "fixed 1", 3: "fixed 3", 18: "fixed 18", 36: "fixed 36", 6: "cycle {6,9}"}
    out("\n   basin sizes  #{n <= X : orbit ends in attractor}")
    out(f"   {'X':>10} " + " ".join(f"{names[a]:>14}" for a in (1, 3, 18, 36, 6)))
    basins = {}
    X = 10
    while X <= N:
        row = {a: int(np.count_nonzero(label[1:X + 1] == a)) for a in (1, 3, 18, 36, 6)}
        basins[X] = row
        out(f"   {X:>10} " + " ".join(f"{row[a]:>14}" for a in (1, 3, 18, 36, 6)))
        X *= 10
    out("   as fractions of X:")
    for X, row in basins.items():
        out(f"   {X:>10} " + " ".join(f"{row[a]/X:>14.6f}" for a in (1, 3, 18, 36, 6)))
    results["basins"] = {str(k): v for k, v in basins.items()}
    out(f"   basin of 3 == set of primes: {basins[N][3] == len(primes)}  "
        f"(and every prime maps to 3: {bool(np.all(F[primes] == 3))})")
    results["basin3_is_primes"] = bool(basins[N][3] == len(primes))

    out("\n   transient length t(n) (iterations until a periodic point), n <= N")
    tmax = int(trans.max())
    dist = {t: int(np.count_nonzero(trans[1:] == t)) for t in range(tmax + 1)}
    first = {t: int(np.argmax(trans == t)) for t in range(1, tmax + 1)}
    first[0] = 1
    for t in range(tmax + 1):
        n0 = first[t]
        orb = [n0]
        while orb[-1] not in periodic:
            orb.append(int(F[orb[-1]]))
        out(f"     t = {t}: count {dist[t]:>9}  first n = {n0:>8}  orbit {orb}")
    out(f"     mean transient length over n <= N: {float(trans[1:].mean()):.6f}")
    results["transient_dist"] = dist
    results["transient_first"] = first

    # transient by attractor
    out("\n   distribution of t(n) inside each basin (n <= N):")
    for a in (3, 18, 36, 6):
        sel = trans[1:][label[1:] == a]
        out(f"     {names[a]:>12}: " + ", ".join(f"t={t}:{int(np.count_nonzero(sel == t))}" for t in range(tmax + 1)))

    # preimages of 36 below N: p^7 and p^2 q^2
    pre36 = np.nonzero(F == 36)[0]
    kinds = {}
    for n in pre36.tolist():
        sig = tuple(sorted(factor_small(n).values(), reverse=True))
        kinds[sig] = kinds.get(sig, 0) + 1
    out(f"\n   F(n) = 36 for {len(pre36)} values n <= N; prime signatures: {kinds}")
    out("     (36 = T_8 gives p^7; 36 = T_3 * T_3 gives p^2 q^2; no other product of triangular numbers > 1 is 36)")
    results["pre36_signatures"] = {str(k): v for k, v in kinds.items()}
    return F


# ------------------------------------------------------------------ [C]
def part_C(results, LIMIT=10 ** 40):
    out("\n" + "=" * 78)
    out(f"[C] least n of each transient length among all n < {LIMIT:.0e} (via prime signatures, A025487)")
    out("=" * 78)
    periodic = {1, 3, 18, 36, 6, 9}
    memo = {}

    def Fval(n):
        r = 1
        for a in factor_small(n).values():
            r *= (a + 1) * (a + 2) // 2
        return r

    def trans(n):
        if n in periodic:
            return 0
        if n in memo:
            return memo[n]
        v = 1 + trans(Fval(n))
        memo[n] = v
        return v

    best = {}
    cnt = 0
    primes = PR[:60]

    def dfs(i, n, maxexp, exps):
        nonlocal cnt
        cnt += 1
        # n is a least-of-signature number with exponents exps
        f = 1
        for a in exps:
            f *= (a + 1) * (a + 2) // 2
        t = 0 if n in periodic else 1 + trans(f)
        if t not in best or n < best[t][0]:
            best[t] = (n, tuple(exps))
        p = primes[i]
        m = n
        for a in range(1, maxexp + 1):
            m *= p
            if m >= LIMIT:
                break
            dfs(i + 1, m, a, exps + [a])

    t0 = time.time()
    dfs(0, 1, 200, [])
    out(f"   least-of-signature numbers below limit: {cnt}   ({time.time()-t0:.1f}s)")
    rec = {}
    for t in sorted(best):
        n, exps = best[t]
        orb = [n]
        while orb[-1] not in periodic:
            orb.append(Fval(orb[-1]))
        out(f"     t = {t}: least n = {n}  signature {exps}")
        out(f"            orbit: {orb}")
        rec[t] = str(n)
    results["least_n_by_transient"] = rec
    out("   (t is unbounded? not settled here; see README, open questions)")


def main():
    results = {}
    part_A(results)
    part_B(results)
    part_C(results)
    json.dump(results, open(os.path.join(HERE, "q51_q52_tau3_dynamics.json"), "w"), indent=1)
    out("\nwrote q51_q52_tau3_dynamics.json")


if __name__ == "__main__":
    main()
    LOG.close()
