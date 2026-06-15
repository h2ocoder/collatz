# tests/test_constellations.py
"""Tests for collatz.constellations — prime constellation dropping signatures."""

import numpy as np
import pytest

from collatz.constellations import prime_pairs


def _brute_pairs(n_max, gap):
    from collatz.residues import prime_sieve
    primes = set(prime_sieve(n_max + gap).tolist())
    return [p for p in sorted(primes) if p <= n_max and (p + gap) in primes]


def test_prime_pairs_twins_small():
    """Twins (g=2) up to 30: (3,5),(5,7),(11,13),(17,19),(29,31)."""
    ps = prime_pairs(30, 2)
    assert list(ps) == [3, 5, 11, 17, 29]


def test_prime_pairs_cousins_small():
    """Cousins (g=4) up to 20: (3,7),(7,11),(13,17),(19,23) — p<=n_max, p+g prime."""
    ps = prime_pairs(20, 4)
    assert list(ps) == [3, 7, 13, 19]


def test_prime_pairs_sexy_small():
    """Sexy (g=6) up to 20: (5,11),(7,13),(11,17),(13,19),(17,23)."""
    ps = prime_pairs(20, 6)
    assert list(ps) == [5, 7, 11, 13, 17]


def test_prime_pairs_matches_brute_force():
    """Agree with a set-membership brute force up to 10**4 for all three gaps."""
    for gap in (2, 4, 6):
        assert list(prime_pairs(10_000, gap)) == _brute_pairs(10_000, gap)


def test_prime_pairs_returns_int_array():
    ps = prime_pairs(30, 2)
    assert isinstance(ps, np.ndarray)
    assert ps.dtype.kind == "i"


def test_prime_pairs_rejects_bad_gap():
    """gap=0, gap=1, and gap=-2 must all raise ValueError."""
    for bad_gap in (0, 1, -2):
        with pytest.raises(ValueError):
            prime_pairs(30, bad_gap)
