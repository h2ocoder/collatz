"""Skeptic check 5: transient records (Q5.2-e), numerology controls, Q5.3 (null + the cell (2,2)
identity), Q5.5, and a conditional statement about unbounded transients.

Independent code paths:
  [A] least n of each transient length below 10^40 -- signatures handled as exponent tuples,
      F evaluated on tuples through a factor table of the triangular numbers (no trial
      division of n), transient memoised per signature.
  [B] control: which n <= 300 are a fixed point of SOME tau_k (k >= 2)?
  [C] Q5.3-d: T_(k+1) T_(s+1) = C(k+s,k)^2 -- proof of 'only (0,0),(2,2)' for ALL k <= s, plus search.
      Q5.3-b: independent re-run of the cube/square search on rows, antidiagonals, windows.
  [D] Q5.5: pi_3(2^K) by brute force vs the Beatty sum; how special is the value 36?
  [E] conditional: transient length unbounded if squarefree triangular numbers with exactly j
      prime factors exist for every j (OEIS A127637); checks of the reduction.

Run: python -X utf8 v5_controls.py     (about 1-2 min)
"""
import os
import sys
import time
from math import comb, isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v5_controls.log"), "w", encoding="utf-8")
T0 = time.time()
sys.setrecursionlimit(100000)


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


PR = primes_upto(100000)


def factor(n):
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


def T(m):
    return m * (m + 1) // 2


PERIODIC = {1, 3, 6, 9, 18, 36}
TFAC = {}


def tfac(m):
    if m not in TFAC:
        TFAC[m] = factor(T(m))
    return TFAC[m]


SIGMEMO = {}


def t_sig(sig):
    """transient of a NON-periodic integer with exponent tuple sig (sorted, non-increasing)."""
    if sig in SIGMEMO:
        return SIGMEMO[sig]
    val = 1
    ex = {}
    for a in sig:
        val *= T(a + 1)
        for p, e in tfac(a + 1).items():
            ex[p] = ex.get(p, 0) + e
    if val in PERIODIC:
        r = 1
    else:
        r = 1 + t_sig(tuple(sorted(ex.values(), reverse=True)))
    SIGMEMO[sig] = r
    return r


def t_int(n):
    if n in PERIODIC:
        return 0
    return t_sig(tuple(sorted(factor(n).values(), reverse=True)))


# ------------------------------------------------------------------ [A]
def part_A(LIMIT=10 ** 40):
    out(f"[A] least n of each transient length among least-of-signature numbers below {LIMIT:.0e}")
    best = {}
    count = 0
    stack = [(1, 0, 10 ** 9, ())]      # (n, prime index, max exponent, exps)
    while stack:
        n, i, mx, exps = stack.pop()
        count += 1
        t = 0 if n in PERIODIC else t_sig(exps)
        if t not in best or n < best[t][0]:
            best[t] = (n, exps)
        p = PR[i]
        m = n
        a = 0
        while a < mx:
            m *= p
            a += 1
            if m >= LIMIT:
                break
            stack.append((m, i + 1, a, exps + (a,)))
    out(f"    least-of-signature numbers below limit: {count}  (researcher: 5754126)   ({time.time()-T0:.0f}s)")
    for t in sorted(best):
        out(f"    t = {t:>2}: least n = {best[t][0]}  signature {best[t][1]}")
    expect = [1, 2, 8, 30, 24, 60, 72, 180, 360, 1800, 37800, 49896000, 105700299921216000]
    out("    agrees with the README list for t = 0..12 and no t >= 13:",
        [best[t][0] for t in sorted(best)] == expect)
    # the two signatures whose least member is periodic (6 and 36): their other members have t = 1
    out("    t(10), t(100) (non-periodic members of the signatures of 6 and 36):", t_int(10), t_int(100))
    # a preimage of the t = 12 record
    rec = 105700299921216000
    prod = 136 * 171 * 91 ** 2 * 55 ** 2 * 28 * 10 * 6 ** 3 * 3
    idx = [16, 18, 13, 13, 10, 10, 7, 4, 3, 3, 3, 2]
    out("    136*171*91^2*55^2*28*10*6^3*3 == record:", prod == rec, "; all factors triangular:",
        all(T(m) in (136, 171, 91, 55, 28, 10, 6, 3) for m in idx))
    sig13 = tuple(sorted((m - 1 for m in idx), reverse=True))
    n13 = 1
    for a, p in zip(sig13, PR):
        n13 *= p ** a
    out(f"    hence signature {sig13} has t = {t_sig(sig13)}; its least member is ~10^{len(str(n13))-1}")


# ------------------------------------------------------------------ [B]
def part_B():
    out("\n[B] control: n <= 300 that are fixed by tau_k for some k >= 2")
    hits = {}
    for n in range(1, 301):
        f = factor(n)
        for k in range(2, n + 2):
            v = 1
            for e in f.values():
                v *= comb(e + k - 1, e)
            if v == n:
                hits.setdefault(n, []).append(k)
            if v > n and n > 1:
                break
    comp = {n: ks for n, ks in hits.items() if n > 1 and len(factor(n)) + sum(factor(n).values()) > 2}
    out("    composite n <= 300 fixed by some tau_k:", comp)
    out("    primes p <= 300 fixed by tau_p (trivially, tau_k(p) = k): all of them:",
        all(hits.get(p) == [p] for p in PR if p <= 300))
    out("    so in 30..42 the fixed points of some tau_k are:", {n: hits[n] for n in range(30, 43) if n in hits})


# ------------------------------------------------------------------ [C]
def part_C():
    out("\n[C] Q5.3-d  T_(k+1) T_(s+1) = C(k+s,k)^2")
    hits = [(k, s) for k in range(0, 1500) for s in range(k, 1500) if (k <= 2 or s < 40) and
            T(k + 1) * T(s + 1) == comb(k + s, k) ** 2]
    out("    solutions with k <= 2, s < 1500 or 3 <= k <= s < 40:", hits)
    # proof for k >= 3: C(k+s,k) >= C(s+3,3) and T_(k+1)T_(s+1) <= T_(s+1)^2 for k <= s, and
    # C(s+3,3)^2 / T_(s+1)^2 = ((s+3)/3)^2 >= 4 > 1 for s >= 3.
    ok = all(comb(k + s, k) >= comb(s + 3, 3) and T(k + 1) <= T(s + 1) and
             9 * comb(s + 3, 3) ** 2 == (s + 3) ** 2 * T(s + 1) ** 2
             for k in range(3, 120) for s in range(k, 120))
    out("    inequalities used in the proof for 3 <= k <= s (checked s < 120):", ok)
    out("    k = 2: C(s+2,2) = T_(s+1), so the equation reads T_3 T_(s+1) = T_(s+1)^2, i.e. T_(s+1) = 6, s = 2")
    out("    k = 1: 3 T_(s+1) = (s+1)^2 has no solution; k = 0: T_(s+1) = 1 gives s = 0")

    out("    Q5.3-b  independent re-run of the search sum x^3 = (sum x)^2")
    SM = 420
    b = [(3 ** s).bit_length() - 1 - s for s in range(SM + 1)]     # floor(s log2(3/2))
    A = [[1]]
    for s in range(1, SM + 1):
        prev = A[-1]
        row = []
        for e in range(b[s] + 1):
            row.append((prev[e] if e < len(prev) else 0) + (row[e - 1] if e else 0))
        A.append(row)
    N = [None] + [A[s][b[s]] for s in range(1, SM + 1)]
    assert N[1:11] == [1, 1, 2, 3, 7, 12, 30, 85, 173, 476]
    JM = 400
    S = [sum(A[s][j - s] for s in range(0, j + 1) if 0 <= j - s < len(A[s])) for j in range(JM + 1)]
    assert S[:12] == [1, 1, 1, 2, 3, 4, 8, 13, 19, 38, 64, 128]

    def cs(X):
        return sum(x ** 3 for x in X) == sum(X) ** 2

    tested = 0
    found = []

    def windows(seq, lo, name):
        nonlocal tested
        for a in range(lo, len(seq)):
            s1 = s3 = 0
            for bb in range(a, len(seq)):
                s1 += seq[bb]
                s3 += seq[bb] ** 3
                tested += 1
                if s3 == s1 * s1:
                    found.append((name, a, bb, seq[a:bb + 1] if bb - a < 8 else "long"))
    windows(N, 1, "A100982 window")
    windows(S, 0, "A076227 window")
    for s in range(SM + 1):
        tested += 1
        if cs(A[s]):
            found.append(("row", s, s, A[s]))
    for j in range(JM + 1):
        d = [A[s][j - s] for s in range(0, j + 1) if 0 <= j - s < len(A[s])]
        tested += 1
        if cs(d):
            found.append(("antidiagonal", j, j, d))
    # weighted variants: partial sums and first differences of A100982, and N(s)/gcd structure
    PS = [sum(N[1:i + 1]) for i in range(1, 200)]
    DF = [N[i + 1] - N[i] for i in range(1, 200)]
    windows(PS, 0, "partial sums of A100982")
    windows([x for x in DF if x > 0], 0, "first differences of A100982")
    nontriv = [h for h in found if h[3] == "long" or sorted(h[3]) != list(range(1, len(h[3]) + 1))]
    out(f"      multisets tested: {tested}; hits: {len(found)}; hits that are not literally {{1..m}}: {nontriv}")
    out("      largest m among the hits:", max(len(h[3]) for h in found if h[3] != "long"))


# ------------------------------------------------------------------ [D]
def part_D():
    out("\n[D] Q5.5 lattice-point counts")
    def pi3(x):
        c = 0
        p3 = 1
        while p3 <= x:
            v = p3
            while v <= x:
                c += 1
                v *= 2
            p3 *= 3
        return c
    okB = True
    vals = []
    for K in range(0, 300):
        beatty = 0
        bq = 0
        while 3 ** bq <= 2 ** K:
            ce = (3 ** bq - 1).bit_length() if bq else 0       # ceil(b log2 3) = bit_length(3^b - 1) for b >= 1
            beatty += K + 1 - ce
            bq += 1
        v = pi3(2 ** K)
        okB &= v == beatty
        vals.append(v)
    out("    pi_3(2^K) == sum_b (K+1-ceil(b log2 3)) for K < 300:", okB)
    out("    first terms:", vals[:12], " (OEIS A022331: 1, 2, 4, 6, 9, 13, 17, 22, 28, 34, 41, 48):",
        vals[:12] == [1, 2, 4, 6, 9, 13, 17, 22, 28, 34, 41, 48])
    out("    pi_3(36) =", pi3(36))
    L = [(3 ** s).bit_length() for s in range(1, 40)]            # dropping-word lengths A020914(s)
    G = [sum(L[:S]) for S in range(0, 40)]        # #{(j,s): 1<=s<=S, j>=0, 2^j < 3^s} = sum of word lengths
    out("    word lengths L(1..6) =", L[:6], "; G(6) = their sum =", G[6])
    # H(S) = number of admissible cells (e, s'), s' <= S, e <= floor(s' log2(3/2))  (q55's H)
    H = [sum((3 ** s).bit_length() - s for s in range(0, S + 1)) for S in range(0, 40)]
    seqs = {"pi3(2^K)": vals[:60], "pi3(3^S)": [pi3(3 ** s) for s in range(40)], "G(S)": G, "H(S)": H}
    for nm, sq in seqs.items():
        out(f"    {nm}: values in 25..45: {[v for v in sq if 25 <= v <= 45]}")
    allv = sorted({v for sq in seqs.values() for v in sq if 25 <= v <= 45})
    out(f"    {len(allv)} of the 21 integers 25..45 occur in at least one of these four sequences: {allv}")


# ------------------------------------------------------------------ [E]
def part_E():
    out("\n[E] conditional unboundedness of the transient")
    ok = True
    for j in range(3, 60):
        ok &= t_sig((1,) * j) == 2 + t_int(T(j + 1))
    out("    t(squarefree n with j prime factors) = 2 + t(T_(j+1)) for 3 <= j < 60:", ok,
        " (n -> 3^j -> T_(j+1))")
    a127637 = [3, 6, 66, 210, 3570, 207690, 930930, 56812470, 1803571770, 32395433070, 265257422430]
    okA = True
    for j, v in enumerate(a127637, start=1):
        m = (isqrt(8 * v + 1) - 1) // 2
        f = factor(v)
        okA &= T(m) == v and len(f) == j and all(e == 1 for e in f.values())
    out("    first 11 terms of OEIS A127637 are squarefree triangular with exactly j prime factors:", okA)
    out("    chain: j0 = 3 (t = 3);  T_11 = 66 is squarefree with 3 primes -> squarefree n with 10 primes has t =",
        t_sig((1,) * 10), "; A127637(10) = T_m with m =", (isqrt(8 * a127637[9] + 1) - 1) // 2,
        "-> squarefree n with m-1 primes has t =", 2 + t_int(a127637[9]))
    out(f"\ntotal {time.time()-T0:.0f}s")


if __name__ == "__main__":
    part_A()
    part_B()
    part_C()
    part_D()
    part_E()
    LOG.close()
