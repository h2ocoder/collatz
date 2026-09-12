"""Density exponents for #{n <= x : n -> 1} via Krasikov-Lagarias difference inequalities.

Two inequality systems are computed, both as monotone, positively homogeneous maps
M_lambda on vectors indexed by residue classes mod 3^k.  The best exponent gamma
= log2(lambda*) is the lambda at which the nonlinear Perron root of M_lambda equals 1
(power iteration + bisection).

System KL (Krasikov-Lagarias 2003, Acta Arith. 109, system L_k^{NT}):
    principal classes m ≡ 2 (mod 3).  With alpha = log2(3), d_{k-1}[m'] = min over the
    three lifts of m' to level k:
      m ≡ 2 (9):  c[m] <= λ^-2 c[4m] + λ^(α-2) d[(4m-2)/3]
      m ≡ 5 (9):  c[m] <= λ^-2 c[4m]
      m ≡ 8 (9):  c[m] <= λ^-2 c[4m] + λ^(α-1) d[(2m-1)/3]
    Published: γ_2=0.436588, γ_5=0.733579, γ_9=0.816830, γ_11=0.841756.

System DROP (this repo): the same backward tree expanded along *dropping words*
(first-return parity words of the T-map).  For a target class m (m ≢ 0 mod 3) and
each dropping T-word w with s ones, length L, constant C_w, the preimage
    n_w(a) = (2^L a - C_w) / 3^s      exists iff a ≡ ρ_w (mod 3^s)
has normalized height y - (L - s α) (always retarded), and its class is known only
mod 3^(k-s), so it enters through d_{k-s} = min over 3^s lifts:
      c[m] <= λ^-1 c[2m] + Σ_w [m ≡ ρ_w (3^s)] λ^-(L - sα) d_{k-s}[n_w(m)]

Usage: python scripts/density_exponent_kl.py [kmax] [smax]
"""
from __future__ import annotations

import math
import sys
import time

import numpy as np

ALPHA = math.log2(3)


# ----------------------------------------------------------------------
# dropping words
# ----------------------------------------------------------------------

def dropping_words(s_max: int):
    """All T-words (first symbol 1) that first satisfy 2^L > 3^s at their last symbol,
    with at most s_max ones.  Returns list of (L, s, C) with T^L(n) = (3^s n + C)/2^L."""
    out = []

    def rec(L, s, a, c, is_dropped):
        # state after L steps: value = (a n + c)/2^L, a = 3^s
        if is_dropped:
            out.append((L, s, c))
            return
        if s >= s_max and True:
            # can still append zeros until it drops
            pass
        # step 1 (odd): allowed only if s < s_max
        if s < s_max:
            a1, c1 = 3 * a, 3 * c + (1 << L)
            rec(L + 1, s + 1, a1, c1, (1 << (L + 1)) > a1)
        # step 0 (even)
        if L > 0:
            rec(L + 1, s, a, c, (1 << (L + 1)) > a)

    # first symbol must be 1 (n odd)
    rec(1, 1, 3, 1, False)  # after one odd step: (3n+1)/2, never dropped
    return out


# ----------------------------------------------------------------------
# generic Perron-root machinery
# ----------------------------------------------------------------------

def perron_root(apply, n, iters=400, tol=1e-10, seed_vec=None):
    """Growth rate of the monotone homogeneous map `apply` by power iteration."""
    c = np.ones(n) if seed_vec is None else seed_vec.copy()
    c[c < 0] = 0
    r = 1.0
    for it in range(iters):
        Mc = apply(c)
        nrm = Mc.max()
        if nrm <= 0:
            return 0.0, c
        r_new = nrm / c.max()
        c = Mc / nrm
        if it > 20 and abs(r_new - r) < tol:
            r = r_new
            break
        r = r_new
    return r, c


def best_lambda(make_apply, n, lo=1.0, hi=2.0, iters_bisect=40, **kw):
    """Largest λ with Perron root >= 1, by bisection.  Returns (λ, γ, eigenvector)."""
    c = None
    for _ in range(iters_bisect):
        mid = 0.5 * (lo + hi)
        r, c = perron_root(make_apply(mid), n, seed_vec=c, **kw)
        if r >= 1:
            lo = mid
        else:
            hi = mid
    return lo, math.log2(lo), c


# ----------------------------------------------------------------------
# System KL
# ----------------------------------------------------------------------

def kl_system(k: int):
    N = 3 ** k
    r = np.arange(N, dtype=np.int64)
    principal = (r % 3 == 2)
    idx4 = (4 * r) % N
    m2 = principal & (r % 9 == 2)
    m8 = principal & (r % 9 == 8)
    # targets at level k-1 (residue mod 3^(k-1))
    t2 = ((4 * r - 2) % N) // 3          # for m ≡ 2 mod 9, ≡ 2 mod 3
    t8 = ((2 * r - 1) % N) // 3          # for m ≡ 8 mod 9, ≡ 2 mod 3
    Nk1 = 3 ** (k - 1)

    def make(lam):
        a4 = lam ** -2.0
        a2 = lam ** (ALPHA - 2)
        a8 = lam ** (ALPHA - 1)

        def apply(c):
            d = c.reshape(3, Nk1).min(axis=0)     # min over the 3 lifts
            out = np.zeros_like(c)
            out[principal] = a4 * c[idx4[principal]]
            out[m2] += a2 * d[t2[m2]]
            out[m8] += a8 * d[t8[m8]]
            return out
        return apply

    return make, N


# ----------------------------------------------------------------------
# System DROP
# ----------------------------------------------------------------------

def drop_system(k: int, s_max: int):
    N = 3 ** k
    r = np.arange(N, dtype=np.int64)
    principal = (r % 3 != 0)
    idx2 = (2 * r) % N
    words = [w for w in dropping_words(min(s_max, k - 1))]
    # group words by s; for each word: mask of classes m ≡ ρ_w (3^s), target index at level k-s
    by_s = {}
    for (L, s, C) in words:
        mod_s = 3 ** s
        inv2L = pow(pow(2, L, mod_s), -1, mod_s)
        rho = (C * inv2L) % mod_s
        mask = principal & (r % mod_s == rho)
        # n = (2^L m - C)/3^s  mod 3^(k-s); compute with Python ints to avoid overflow
        mm = r[mask]
        t = ((pow(2, L) % N) * mm - (C % N)) % N
        assert np.all(t % mod_s == 0)
        tgt = (t // mod_s) % (3 ** (k - s))
        beta = L - s * ALPHA
        by_s.setdefault(s, []).append((mask, tgt, beta))

    def make(lam):
        a2 = lam ** -1.0
        pre = {s: [(mask, tgt, lam ** (-beta)) for (mask, tgt, beta) in lst] for s, lst in by_s.items()}

        def apply(c):
            out = np.zeros_like(c)
            out[principal] = a2 * c[idx2[principal]]
            for s, lst in pre.items():
                d = c.reshape(3 ** s, 3 ** (k - s)).min(axis=0)   # min over 3^s lifts
                for mask, tgt, coef in lst:
                    out[mask] += coef * d[tgt]
            return out
        return apply

    return make, N, len(words)


# ----------------------------------------------------------------------
# Exact certificate for the KL system
# ----------------------------------------------------------------------

def certify_kl_exact(k: int, lam_p: float, c: np.ndarray, scale_bits: int = 30) -> bool:
    """Verify, in exact integer arithmetic, that the positive vector C = floor(c·2^S)
    satisfies C[m] ≤ A4·C[4m] + A2·D[t2] (m ≡ 2 mod 9), C[m] ≤ A4·C[4m] (m ≡ 5 mod 9),
    C[m] ≤ A4·C[4m] + A8·D[t8] (m ≡ 8 mod 9), where A4 ≤ λ'^-2·2^S, A2 ≤ λ'^(α-2)·2^S,
    A8 ≤ λ'^(α-1)·2^S are integer LOWER bounds of the true coefficients and D is the
    coordinatewise min over the three lifts.  Because the map is monotone in its
    coefficients, success proves c/2^S ≤ M_{λ'}(c/2^S), i.e. the Krasikov–Lagarias
    system L_k(λ') is feasible, giving the exponent log2(λ')."""
    import mpmath as mp
    mp.mp.dps = 60
    S = 1 << scale_bits
    lp = mp.mpf(lam_p)
    al = mp.log(3) / mp.log(2)
    A4 = int(mp.floor(lp ** -2 * S))
    A2 = int(mp.floor(lp ** (al - 2) * S))
    A8 = int(mp.floor(lp ** (al - 1) * S))
    N = 3 ** k
    r = np.arange(N, dtype=np.int64)
    principal = (r % 3 == 2)
    C = np.floor(c / c.max() * S).astype(np.int64)
    if not np.all(C[principal] > 0):
        return False
    D = C.reshape(3, 3 ** (k - 1)).min(axis=0)
    idx4 = (4 * r) % N
    t2 = ((4 * r - 2) % N) // 3
    t8 = ((2 * r - 1) % N) // 3
    rhs = np.zeros(N, dtype=np.int64)
    rhs[principal] = A4 * C[idx4[principal]]
    m2 = principal & (r % 9 == 2)
    m8 = principal & (r % 9 == 8)
    rhs[m2] += A2 * D[t2[m2]]
    rhs[m8] += A8 * D[t8[m8]]
    lhs = C * S
    assert lhs.max() < (1 << 62) and rhs.max() < (1 << 62)
    return bool(np.all(lhs[principal] <= rhs[principal]))


def certify_cli(k: int, lam: float, slack: float = 1e-4):
    import os
    make, N = kl_system(k)
    path = f"data/kl_eigvec_k{k}.npy"
    lam_p = lam - slack
    if os.path.exists(path):
        c = np.load(path)
    else:
        _, c = perron_root(make(lam_p), N, iters=2000, tol=1e-13)
    _, c = perron_root(make(lam_p), N, iters=3000, tol=1e-14, seed_vec=c)
    ok = certify_kl_exact(k, lam_p, c)
    print(f"k={k}: λ'={lam_p:.7f} γ'={math.log2(lam_p):.6f} exact certificate: {ok}")
    return ok


# ----------------------------------------------------------------------

def compare_cli(kmax, smax):
    published = {2: 0.436588, 5: 0.733579, 9: 0.816830, 11: 0.841756}
    print(f"dropping words with s<= {smax}: " + str({s: sum(1 for w in dropping_words(smax) if w[1] == s) for s in range(1, smax + 1)}))
    print("\n| k | KL γ_k | KL λ_k | published γ_k | DROP γ_k (s≤min(smax,k-1)) | #words | time s |")
    print("|---|---|---|---|---|---|---|")
    for k in range(2, kmax + 1):
        t0 = time.time()
        make, N = kl_system(k)
        lam, gam, _ = best_lambda(make, N)
        make_d, N, nw = drop_system(k, smax)
        lam_d, gam_d, _ = best_lambda(make_d, N)
        print(f"| {k} | {gam:.6f} | {lam:.6f} | {published.get(k, '')} | {gam_d:.6f} | {nw} | {time.time()-t0:.1f} |", flush=True)




if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "certify":
        certify_cli(int(sys.argv[2]), float(sys.argv[3]))
    else:
        compare_cli(int(sys.argv[1]) if len(sys.argv) > 1 else 9,
                    int(sys.argv[2]) if len(sys.argv) > 2 else 8)


# ----------------------------------------------------------------------
# Memory-lean KL system (int32 indices on principal subset, float32 vectors) for k >= 17
# ----------------------------------------------------------------------

def kl_system_lean(k: int):
    N = 3 ** k
    Nk1 = N // 3
    P = np.arange(2, N, 3, dtype=np.int64)              # principal residues m ≡ 2 mod 3
    idx4 = ((4 * P) % N).astype(np.int32)
    is2 = (P % 9 == 2); is8 = (P % 9 == 8)
    P2 = P[is2]; P8 = P[is8]
    t2 = (((4 * P2 - 2) % N) // 3).astype(np.int32)
    t8 = (((2 * P8 - 1) % N) // 3).astype(np.int32)
    pos2 = np.nonzero(is2)[0].astype(np.int32); pos8 = np.nonzero(is8)[0].astype(np.int32)
    Pi = P.astype(np.int32)
    del P, P2, P8, is2, is8

    def make(lam):
        a4 = np.float32(lam ** -2.0); a2 = np.float32(lam ** (ALPHA - 2)); a8 = np.float32(lam ** (ALPHA - 1))

        def apply(c):
            d = c.reshape(3, Nk1).min(axis=0)
            out = np.zeros(N, dtype=np.float32)
            vals = a4 * c[idx4]
            vals[pos2] += a2 * d[t2]
            vals[pos8] += a8 * d[t8]
            out[Pi] = vals
            return out
        return apply

    return make, N


def lean_cli(k: int, lo: float, hi: float = 2.0, nbis: int = 20):
    import time
    t0 = time.time()
    make, N = kl_system_lean(k)
    c = np.ones(N, dtype=np.float32)
    for _ in range(nbis):
        mid = 0.5 * (lo + hi)
        r, c = perron_root(make(mid), N, iters=600, tol=1e-7, seed_vec=c)
        if r >= 1: lo = mid
        else: hi = mid
    lam = lo; lamp = lam - 1e-4
    r, c = perron_root(make(lamp), N, iters=1500, tol=1e-8, seed_vec=c)
    Mc = make(lamp)(c)
    princ = np.arange(2, N, 3)
    ok = bool(np.all(Mc[princ] >= c[princ]) and np.all(c[princ] > 0))
    np.save(f"data/kl_eigvec_k{k}.npy", c)
    print(f"| {k} | γ={math.log2(lam):.6f} | λ={lam:.6f} | N={N} | float-cert γ'={math.log2(lamp):.6f}: {ok} | {time.time()-t0:.0f}s |", flush=True)


def certify_kl_exact_lean(k: int, lam_p: float, c: np.ndarray, scale_bits: int = 30, chunk: int = 4_000_000) -> bool:
    """Same certificate as certify_kl_exact, computed in chunks over the principal classes
    with int32 indices, so k=17 (129M classes) fits in ~3 GB."""
    import mpmath as mp
    mp.mp.dps = 60
    S = 1 << scale_bits
    lp = mp.mpf(lam_p); al = mp.log(3) / mp.log(2)
    A4 = int(mp.floor(lp ** -2 * S)); A2 = int(mp.floor(lp ** (al - 2) * S)); A8 = int(mp.floor(lp ** (al - 1) * S))
    N = 3 ** k; Nk1 = N // 3
    C = np.floor(c.astype(np.float64) / float(c.max()) * S).astype(np.int64)
    D = C.reshape(3, Nk1).min(axis=0)
    ok = True
    for start in range(2, N, 3 * chunk):
        P = np.arange(start, min(N, start + 3 * chunk), 3, dtype=np.int64)
        if not np.all(C[P] > 0):
            return False
        rhs = A4 * C[(4 * P) % N]
        m2 = (P % 9 == 2); m8 = (P % 9 == 8)
        rhs[m2] += A2 * D[((4 * P[m2] - 2) % N) // 3]
        rhs[m8] += A8 * D[((2 * P[m8] - 1) % N) // 3]
        if not np.all(C[P] * S <= rhs):
            ok = False; break
    return ok
