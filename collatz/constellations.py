# collatz/constellations.py
"""Prime constellation dropping signatures (exploratory).

A constellation of gap g is a pair (p, p+g) with both members prime.  This
module enumerates such pairs (`prime_pairs`), attaches each pair its joint
Collatz dropping signature (`pair_signature`, `joint_signature_counts`),
builds an admissible-integer **coupling null** for that joint distribution
(`coupling_null_counts`), and tabulates the gap-forced residue coupling
(`forced_coupling_table`).

Reuses `collatz.residues.prime_sieve` and `collatz.dropping.dropping_set`;
the 3-adic odd-step count s is `collatz.dropping.orbital_oddity`.
"""
from __future__ import annotations

from collections import Counter

import numpy as np

from .dropping import dropping_set
from .residues import prime_sieve

K_CAP = 15  # dropping sets at or beyond this fold into a single k>=K_CAP bin


def prime_pairs(n_max: int, gap: int) -> np.ndarray:
    """Primes p <= n_max such that p + gap is also prime, as an int64 array.

    Example: prime_pairs(30, 2) -> array([ 3,  5, 11, 17, 29])
    """
    if gap <= 0 or gap % 2 != 0:
        raise ValueError("gap must be a positive even integer")
    primes = prime_sieve(n_max + gap)
    is_prime = np.zeros(n_max + gap + 1, dtype=bool)
    is_prime[primes] = True
    base = primes[primes <= n_max]
    keep = is_prime[base + gap]
    return base[keep].astype(np.int64)
