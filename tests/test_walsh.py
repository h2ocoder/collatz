"""Tests for collatz.walsh — orthonormal Walsh-Hadamard transform."""

import numpy as np
import pytest

from collatz.walsh import (
    shannon_entropy,
    walsh_forward,
    weight_energies,
)


def test_walsh_parseval():
    """sum |F[m]|^2 == sum |f[n]|^2."""
    rng = np.random.default_rng(31)
    for K in (2, 5, 8):
        N = 1 << K
        f = rng.standard_normal(N)
        F = walsh_forward(f)
        assert F.shape == (N,)
        assert abs(float(F @ F) - float(f @ f)) / float(f @ f) < 1e-12


def test_walsh_self_inverse():
    """Orthonormal Walsh transform is its own inverse."""
    rng = np.random.default_rng(32)
    K = 6
    N = 1 << K
    f = rng.standard_normal(N)
    g = walsh_forward(walsh_forward(f))
    np.testing.assert_allclose(g, f, atol=1e-12)


def test_walsh_of_constant():
    """f ≡ c → F[0] = c * sqrt(N), F[m] = 0 for m > 0."""
    K = 5
    N = 1 << K
    f = np.full(N, 3.5)
    F = walsh_forward(f)
    assert abs(F[0] - 3.5 * np.sqrt(N)) < 1e-12
    np.testing.assert_allclose(F[1:], np.zeros(N - 1), atol=1e-12)


def test_walsh_of_delta_uniform_magnitude():
    """f = e_n → all |F[m]| == 1/sqrt(N) with signs (-1)^{<m,n>}."""
    K = 4
    N = 1 << K
    n = 5  # 0b0101
    f = np.zeros(N)
    f[n] = 1.0
    F = walsh_forward(f)
    expected_mag = 1.0 / np.sqrt(N)
    np.testing.assert_allclose(np.abs(F), np.full(N, expected_mag), atol=1e-12)
    for m in range(N):
        sign = -1.0 if bin(m & n).count("1") % 2 else 1.0
        assert abs(F[m] - sign * expected_mag) < 1e-12, f"sign wrong at m={m}"


def test_walsh_constant_mode_matches_haar():
    """F[0] (walsh) == c0 (haar) for the same input."""
    from collatz.wavelets import haar_forward

    rng = np.random.default_rng(33)
    K = 5
    f = rng.standard_normal(1 << K)
    F = walsh_forward(f)
    c0, _ = haar_forward(f)
    assert abs(F[0] - c0) < 1e-12


def test_weight_energies_covers_parseval():
    """F[0]^2 + sum_w W_w == ||f||^2."""
    rng = np.random.default_rng(34)
    K = 7
    N = 1 << K
    f = rng.standard_normal(N)
    F = walsh_forward(f)
    W = weight_energies(F, K)
    assert W.shape == (K + 1,)
    total = F[0] ** 2 + float(W.sum())
    # weight_energies includes w=0 (which is F[0]^2 alone in this bucket).
    # So actually total == ||f||^2 OR W.sum() == ||f||^2; verify the spec'd convention.
    # Per spec: W_w = sum_{popcount(m) = w} |F[m]|^2, so w=0 includes only F[0].
    # Then sum_w W_w = sum_m |F[m]|^2 = ||f||^2 by Parseval. Both should equal ||f||^2.
    assert abs(float(W.sum()) - float(f @ f)) / float(f @ f) < 1e-12


def test_weight_energies_walsh_character():
    """Walsh character with popcount(m0)=w0 has all its energy at weight w0."""
    K = 5
    N = 1 << K
    m0 = 0b10110  # popcount = 3
    # Build w_{m0}(n) = (1/sqrt(N)) * (-1)^{<m0,n>}
    signs = np.array(
        [(-1.0) ** (bin(m0 & n).count("1")) for n in range(N)]
    )
    f = signs / np.sqrt(N)
    F = walsh_forward(f)
    W = weight_energies(F, K)
    expected = np.zeros(K + 1)
    expected[bin(m0).count("1")] = 1.0
    np.testing.assert_allclose(W, expected, atol=1e-12)


def test_shannon_entropy_known_values():
    """Entropy is 0 on a delta, log2(n) on uniform."""
    assert abs(shannon_entropy(np.array([1.0, 0.0, 0.0, 0.0]))) < 1e-12
    h = shannon_entropy(np.full(8, 1 / 8))
    assert abs(h - 3.0) < 1e-12  # log2(8) = 3


def test_shannon_entropy_handles_zero_safely():
    """Zero entries contribute zero, not NaN."""
    p = np.array([0.5, 0.0, 0.5, 0.0])
    h = shannon_entropy(p)
    assert abs(h - 1.0) < 1e-12


def test_walsh_rejects_non_power_of_two():
    with pytest.raises(ValueError):
        walsh_forward(np.zeros(7))
