"""Arithmetic form of Collatz Dropping Sets and Dirichlet null model.

Each Dropping Set D_k is a finite union of residue classes mod 2^k.  This
module exposes that decomposition (`dropping_set_residues`,
`dropping_set_residue_table`), the subset of those residues coprime to 2^k
(`coprime_residues`), and a Dirichlet-equidistribution null model for how
primes distribute across D_k (`dirichlet_prediction`).  A fast Sieve of
Eratosthenes (`prime_sieve`) is included for convenience.
"""
from __future__ import annotations

import numpy as np


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
