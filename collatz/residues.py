"""Arithmetic form of Collatz Dropping Sets and Dirichlet null model.

Each Dropping Set D_k is a finite union of residue classes mod 2^k.  This
module exposes that decomposition (`dropping_set_residues`,
`dropping_set_residue_table`), the subset of those residues coprime to 2^k
(`coprime_residues`), and a Dirichlet-equidistribution null model for how
primes distribute across D_k (`dirichlet_prediction`).  A fast Sieve of
Eratosthenes (`prime_sieve`) is included for convenience.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from .dropping import dropping_set


def prime_sieve(n: int) -> np.ndarray:
    """All primes p with 2 <= p <= n, as a 1-D int64 NumPy array.

    Plain Sieve of Eratosthenes on a boolean array of length n+1.
    Returns an empty array when n < 2.

    Example: prime_sieve(10) -> array([2, 3, 5, 7])
    """
    if n < 2:
        return np.empty(0, dtype=np.int64)
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[:2] = False
    for p in range(2, int(n**0.5) + 1):
        if is_prime[p]:
            is_prime[p * p :: p] = False
    return np.nonzero(is_prime)[0].astype(np.int64)


@lru_cache(maxsize=None)
def dropping_set_residues(k: int) -> frozenset[int]:
    """Residues r mod 2^k such that every large n ≡ r (mod 2^k) has dropping_set(n) = k.

    Computed by checking three large representatives (r+2^k, r+2·2^k, r+3·2^k)
    and accepting r only if all three classify to k.  This guards against
    residues where the orbit accidentally drops at step k for small n but not
    asymptotically.

    Returns frozenset() when no residue class satisfies the property
    (e.g. k=2 has no qualifying residue: 3x+1 dynamics cannot drop in
    exactly 2 steps).

    Example: dropping_set_residues(1) == frozenset({0})
    Example: dropping_set_residues(3) == frozenset({1, 5})
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    M = 1 << k
    R = set()
    for r in range(M):
        base = r if r >= 2 else r + M
        reps = (base, base + M, base + 2 * M)
        if all(dropping_set(n) == k for n in reps):
            R.add(r)
    return frozenset(R)


def dropping_set_residue_table(k_max: int) -> dict[int, frozenset[int]]:
    """Map {k: R_k} for k in 1..k_max.

    Each R_k is the output of `dropping_set_residues(k)`.

    Example: dropping_set_residue_table(3) ==
             {1: frozenset({0}), 2: frozenset(), 3: frozenset({1, 5})}
    """
    if k_max < 1:
        raise ValueError("k_max must be >= 1")
    return {k: dropping_set_residues(k) for k in range(1, k_max + 1)}


@lru_cache(maxsize=None)
def coprime_residues(k: int) -> frozenset[int]:
    """Residues in R_k that are coprime to 2^k (equivalently, odd).

    Primes p > 2 with dropping_set(p) = k must have p mod 2^k in this set.

    Example: coprime_residues(3) == frozenset({1, 5})
    """
    return frozenset(r for r in dropping_set_residues(k) if r % 2 == 1)


def dirichlet_prediction(k: int, prime_count: int) -> float:
    """Expected number of primes <= N falling in Dropping Set k, under Dirichlet.

    Formula: |R_k ∩ odd| / 2^(k-1) * pi(N), with pi(N) supplied as `prime_count`.

    Example: dirichlet_prediction(3, prime_count=78498) == 39249.0
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    coprime_count = len(coprime_residues(k))
    odd_residues_total = 1 << (k - 1)
    return coprime_count / odd_residues_total * prime_count
