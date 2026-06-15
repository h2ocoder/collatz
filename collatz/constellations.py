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

    gap must be a positive even integer.  For p > 2, an odd gap would force
    one of p, p+gap to be even (hence composite), so only the degenerate pair
    (2, 2+gap) could ever occur; even gaps enumerate the non-trivial
    constellations: twins (g=2), cousins (g=4), sexy primes (g=6), etc.

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


def _capped_set(n: int, k_cap: int) -> int:
    """dropping_set(n) clipped to k_cap."""
    return min(dropping_set(n), k_cap)


def pair_signature(p: int, gap: int, k_cap: int = K_CAP) -> tuple[int, int]:
    """Joint dropping signature (k_p, k_{p+gap}), each capped at k_cap.

    Example: pair_signature(3, 2) == (6, 3)
    """
    return (_capped_set(p, k_cap), _capped_set(p + gap, k_cap))


def joint_signature_counts(pairs, gap: int, k_cap: int = K_CAP) -> dict:
    """Counter over capped (k_p, k_{p+gap}) for every p in `pairs`.

    `pairs` is any iterable of ints (e.g. the output of prime_pairs).
    Returns a plain dict keyed by (int, int).
    """
    counts = Counter()
    for p in np.asarray(pairs).tolist():
        counts[pair_signature(p, gap, k_cap)] += 1
    return dict(counts)


def coupling_null_counts(
    n_max: int, gap: int, k_cap: int = K_CAP, stride: int = 1
) -> dict:
    """Joint dropping-signature histogram over admissible integers (the null).

    Iterates odd n in [3, n_max - gap], taking every `stride`-th odd value,
    and counts the capped signature (dropping_set(n), dropping_set(n+gap)).
    Because every odd n with even gap has n+gap odd, these are exactly the
    integers admissible for the constellation at the prime 2 -- so by
    Hardy-Littlewood the prime pairs inherit this 2-adic distribution, and
    any deviation of observed pairs from it is genuine correlation.

    Deterministic: no randomness, fixed systematic stride.

    Example: sum(coupling_null_counts(31, 2, stride=1).values()) == 14
             (odd n = 3,5,...,29; n+2 <= 31)
    """
    if gap <= 0 or gap % 2 != 0:
        raise ValueError("gap must be a positive even integer")
    if stride < 1:
        raise ValueError("stride must be >= 1")
    counts = Counter()
    step = 2 * stride  # stay on odd integers
    n = 3
    upper = n_max - gap
    while n <= upper:
        sig = (_capped_set(n, k_cap), _capped_set(n + gap, k_cap))
        counts[sig] += 1
        n += step
    return dict(counts)


def forced_coupling_table(gap: int, modulus: int) -> list[tuple[int, int, bool, bool]]:
    """The gap-forced residue coupling, one row per odd residue mod `modulus`.

    Each row is (a, (a+gap) mod modulus, fast_a, fast_b) where `fast_x` marks
    a member in dropping set 3 (equivalently x ≡ 1 mod 4, the fast dropper).
    This is a pure-arithmetic theorem -- no primes involved -- and anchors the
    empirical figures.

    Example: forced_coupling_table(2, 8)[0] == (1, 3, True, False)
    """
    if gap <= 0 or gap % 2 != 0:
        raise ValueError("gap must be a positive even integer")
    rows = []
    for a in range(1, modulus, 2):
        b = (a + gap) % modulus
        rows.append((a, b, a % 4 == 1, b % 4 == 1))
    return rows
