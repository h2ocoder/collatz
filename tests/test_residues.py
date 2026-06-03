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


from collatz.residues import dropping_set_residues
from collatz.dropping import dropping_set


def test_R_1_is_evens_only():
    """Dropping Set 1 = all even numbers, so R_1 = {0} mod 2."""
    assert dropping_set_residues(1) == frozenset({0})


def test_R_3_matches_1_mod_4():
    """Dropping Set 3 = {n : n ≡ 1 mod 4, n > 1}, so R_3 = {1, 5} mod 8."""
    assert dropping_set_residues(3) == frozenset({1, 5})


def test_R_2_is_empty():
    """Set 2 requires n odd AND (3n+1)/2 < n, which is impossible for positive n."""
    assert dropping_set_residues(2) == frozenset()


def test_partition_up_to_4096():
    """For every n in [2, 4096], n mod 2^k must lie in R_k where k = dropping_set(n)."""
    for n in range(2, 4097):
        k = dropping_set(n)
        r = n % (1 << k)
        assert r in dropping_set_residues(k), (
            f"n={n}, k={k}, r={r} not in R_{k}={sorted(dropping_set_residues(k))}"
        )


def test_residue_density_consistent():
    """Empirical Set_k density up to N matches |R_k| / 2^k within tolerance for small k."""
    N = 4096
    empirical = {k: 0 for k in range(1, 12)}
    for n in range(2, N + 1):
        k = dropping_set(n)
        if k < 12:
            empirical[k] += 1
    for k in range(1, 12):
        R_k = dropping_set_residues(k)
        if not R_k:
            assert empirical[k] == 0
            continue
        predicted_density = len(R_k) / (1 << k)
        observed_density = empirical[k] / (N - 1)
        # Loose: density tracks within 30% at N = 4096 (small-N regime)
        if predicted_density > 0.01:
            assert abs(observed_density - predicted_density) / predicted_density < 0.30, (
                f"k={k}: predicted {predicted_density:.4f}, observed {observed_density:.4f}"
            )


from collatz.residues import (
    coprime_residues,
    dirichlet_prediction,
    dropping_set_residue_table,
)


def test_residue_table_covers_range():
    """Table returns frozensets for k in 1..k_max."""
    table = dropping_set_residue_table(8)
    assert set(table.keys()) == set(range(1, 9))
    for k, R in table.items():
        assert isinstance(R, frozenset)
        assert R == dropping_set_residues(k)


def test_coprime_residues_filters_odds():
    """coprime_residues(k) = R_k intersect odd residues mod 2^k."""
    # R_3 = {1, 5}; both odd, so coprime = R_3.
    assert coprime_residues(3) == frozenset({1, 5})
    # R_1 = {0}; 0 is even, so coprime = empty.
    assert coprime_residues(1) == frozenset()


def test_dirichlet_prediction_zero_when_no_coprime_residues():
    """A set with no odd residues asymptotically contains no primes."""
    # k=1: only even residue, so prediction = 0 regardless of pi(N).
    assert dirichlet_prediction(1, prime_count=10_000) == 0.0


def test_dirichlet_prediction_matches_formula():
    """Prediction = |R_k ∩ odd| / 2^(k-1) * pi(N)."""
    # k=3: 2 coprime residues out of 4 odd residues mod 8 -> ratio = 0.5
    pi_N = 78_498  # pi(1e6)
    expected = 2 / 4 * pi_N
    assert dirichlet_prediction(3, prime_count=pi_N) == pytest.approx(expected)
