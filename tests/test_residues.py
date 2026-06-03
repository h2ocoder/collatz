"""Tests for collatz.residues — arithmetic form of dropping sets and Dirichlet null."""

import numpy as np
import pytest

from collatz.residues import prime_sieve


def test_prime_sieve_small():
    """Sieve returns primes up to N inclusive, as a NumPy int array."""
    primes = prime_sieve(20)
    assert isinstance(primes, np.ndarray)
    assert primes.dtype.kind == "i"
    assert list(primes) == [2, 3, 5, 7, 11, 13, 17, 19]


def test_prime_sieve_excludes_one():
    """1 is not prime; 2 is."""
    primes = prime_sieve(2)
    assert list(primes) == [2]


def test_prime_sieve_count_at_1e5():
    """Pi(1e5) = 9592 (well-known)."""
    primes = prime_sieve(100_000)
    assert primes.size == 9592
    assert primes[0] == 2
    assert primes[-1] == 99991


def test_prime_sieve_rejects_small_n():
    """N < 2 returns an empty array (no primes exist)."""
    assert prime_sieve(1).size == 0
    assert prime_sieve(0).size == 0
