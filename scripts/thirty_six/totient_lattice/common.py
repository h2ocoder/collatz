"""Shared helpers for the totient_lattice thread (thread 4 of scripts/thirty_six).

CONVENTIONS (stated here once, repeated on every table that uses them)

  standard map   f(n) = n/2 (n even), 3n+1 (n odd)            -- the repo's collatz.core
  shortcut map   T(n) = n/2 (n even), (3n+1)/2 (n odd)        -- Terras

  dropping time, repo convention (collatz.dropping.dropping_time = core.stopping_time):
      sigma(n) = number of STANDARD steps until the first value < n,  n >= 2.
  shortcut dropping time k(n) = number of SHORTCUT steps until the first value < n
      = number of halvings; s(n) = number of odd steps;  sigma(n) = k(n) + s(n).
  dropping destination dest(n) = that first value < n.  It is the same number in both
      conventions, because the value 3n+1 skipped by the shortcut is > n.
  total stopping time sigma_inf(n) = number of STANDARD steps to reach 1 (core.total_stopping_time).

  H(n)  = number of iterations of Euler's phi needed to reach 1   (OEIS A003434), H(1) = 0.
  C(n)  = H(n) - 1 = iterations to reach 2 (Shapiro's class), n >= 2.
  F(n)  = H(n) for n even, H(n) - 1 for n odd > 1, F(1) = 0   (OEIS A064415): Shapiro's
          completely additive height, F(2) = 1, F(p) = F(p-1) for odd primes p.
"""
from __future__ import annotations

import numpy as np


def totient_sieve(n: int) -> np.ndarray:
    """phi[0..n] as int64."""
    phi = np.arange(n + 1, dtype=np.int64)
    comp = np.zeros(n + 1, dtype=bool)
    for p in range(2, n + 1):
        if not comp[p]:
            if p * p <= n:
                comp[p * p::p] = True
            phi[p::p] -= phi[p::p] // p
    return phi


def spf_sieve(n: int) -> np.ndarray:
    """smallest prime factor, spf[0] = spf[1] = 0."""
    spf = np.zeros(n + 1, dtype=np.int64)
    for p in range(2, n + 1):
        if spf[p] == 0:
            seg = spf[p::p]
            seg[seg == 0] = p
    return spf


def totient_height(phi: np.ndarray) -> np.ndarray:
    """H[n] = iterations of phi to reach 1 (H[0] is meaningless and set to 0)."""
    n = len(phi) - 1
    H = np.zeros(n + 1, dtype=np.int16)
    cur = np.arange(n + 1, dtype=np.int64)
    idx = np.nonzero(cur > 1)[0]
    while idx.size:
        H[idx] += 1
        cur[idx] = phi[cur[idx]]
        idx = idx[cur[idx] > 1]
    return H


def shapiro_F(H: np.ndarray) -> np.ndarray:
    n = len(H) - 1
    F = H.astype(np.int16).copy()
    odd = np.arange(n + 1) % 2 == 1
    F[odd] -= 1
    F[1] = 0
    F[0] = 0
    return F


def dropping_arrays(n: int, mult: int = 3, add: int = 1, max_steps: int = 2000,
                    cap: int = 1 << 61):
    """Vectorised dropping data for the shortcut map T(x) = x/2 or (mult*x + add)/2, 2 <= x <= n.

    Returns k (halvings = shortcut steps), s (odd steps), dest, each indexed 0..n.
    Entries with k == -1 did not drop within max_steps or exceeded `cap` (never happens for
    3x+1 below 10^8; does happen for 3x-1 cycles and for 5x+1).
    """
    k = np.zeros(n + 1, dtype=np.int32)
    s = np.zeros(n + 1, dtype=np.int32)
    dest = np.zeros(n + 1, dtype=np.int64)
    idx = np.arange(2, n + 1, dtype=np.int64)
    cur = idx.copy()
    kk = np.zeros(idx.size, dtype=np.int32)
    ss = np.zeros(idx.size, dtype=np.int32)
    step = 0
    while idx.size and step < max_steps:
        odd = (cur & 1).astype(bool)
        cur = np.where(odd, (mult * cur + add) >> 1, cur >> 1)
        kk += 1
        ss += odd
        step += 1
        done = cur < idx
        if done.any():
            di = idx[done]
            k[di] = kk[done]
            s[di] = ss[done]
            dest[di] = cur[done]
        blown = cur > cap
        if blown.any():
            k[idx[blown]] = -1
        keep = ~(done | blown)
        idx, cur, kk, ss = idx[keep], cur[keep], kk[keep], ss[keep]
    if idx.size:
        k[idx] = -1
    return k, s, dest


def total_stopping_times(k: np.ndarray, s: np.ndarray, dest: np.ndarray) -> np.ndarray:
    """Standard-step total stopping time via sigma_inf(n) = sigma(n) + sigma_inf(dest(n))."""
    n = len(k) - 1
    sig = (k.astype(np.int64) + s).tolist()
    d = dest.tolist()
    t = [0] * (n + 1)
    for x in range(2, n + 1):
        t[x] = sig[x] + t[d[x]]
    return np.array(t, dtype=np.int32)


def smooth_part_solutions(u: int, v: int):
    """3-smooth x = 2^alpha 3^beta with phi(x) = 2^u 3^v, as (alpha, beta) pairs.

    2^alpha contributes (alpha-1, 0) for alpha >= 1; 3^beta contributes (1, beta-1) for beta >= 1.
    """
    sols = []
    for beta in range(0, v + 2):
        for alpha in range(0, u + 2):
            uu = (alpha - 1 if alpha >= 1 else 0) + (1 if beta >= 1 else 0)
            vv = beta - 1 if beta >= 1 else 0
            if (uu, vv) == (u, v):
                sols.append((alpha, beta))
    return sols


def fibre_decompositions(a: int, b: int, points):
    """All x with phi(x) = 2^a 3^b as (x, alpha, beta, tuple of Pierpont points)."""
    pts = sorted(p for p in points if p[0] <= a and p[1] <= b)
    res = []

    def rec(k, c, d, chosen):
        if k == len(pts):
            for alpha, beta in smooth_part_solutions(a - c, b - d):
                x = (1 << alpha) * 3 ** beta
                for i, j in chosen:
                    x *= (1 << i) * 3 ** j + 1
                res.append((x, alpha, beta, tuple(chosen)))
            return
        rec(k + 1, c, d, chosen)
        i, j = pts[k]
        if c + i <= a and d + j <= b:
            rec(k + 1, c + i, d + j, chosen + [(i, j)])

    rec(0, 0, 0, [])
    return sorted(res)
