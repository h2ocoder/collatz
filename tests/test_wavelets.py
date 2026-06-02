"""Tests for collatz.wavelets — Kozyrev/Haar transform."""

import numpy as np
import pytest

from collatz.wavelets import idx, kozyrev_basis_vector


def test_idx_layout():
    """Heap-style flat index: idx(j, a) = 2^j - 1 + a."""
    # Shell 0 has 1 wavelet at index 0
    assert idx(0, 0) == 0
    # Shell 1 has 2 wavelets at indices 1, 2
    assert idx(1, 0) == 1
    assert idx(1, 1) == 2
    # Shell 2 has 4 wavelets at indices 3..6
    assert idx(2, 0) == 3
    assert idx(2, 3) == 6


def test_kozyrev_basis_vector_K2():
    """For K = 2 (N = 4), verify the three explicit basis vectors."""
    psi_00 = kozyrev_basis_vector(0, 0, 2)
    psi_10 = kozyrev_basis_vector(1, 0, 2)
    psi_11 = kozyrev_basis_vector(1, 1, 2)

    np.testing.assert_allclose(psi_00, [0.5, 0.5, -0.5, -0.5])
    np.testing.assert_allclose(psi_10, [1 / np.sqrt(2), -1 / np.sqrt(2), 0, 0])
    np.testing.assert_allclose(psi_11, [0, 0, 1 / np.sqrt(2), -1 / np.sqrt(2)])


def test_kozyrev_orthonormal_K5():
    """All N-1 basis vectors at K=5 should be pairwise orthonormal."""
    K = 5
    N = 1 << K
    vectors = []
    for j in range(K):
        for a in range(1 << j):
            vectors.append(kozyrev_basis_vector(j, a, K))
    M = np.stack(vectors)  # shape (N-1, N)
    gram = M @ M.T
    np.testing.assert_allclose(gram, np.eye(N - 1), atol=1e-12)


def test_kozyrev_basis_orthogonal_to_constant():
    """Every wavelet should be orthogonal to the constant function."""
    K = 5
    N = 1 << K
    phi = np.ones(N) / np.sqrt(N)
    for j in range(K):
        for a in range(1 << j):
            psi = kozyrev_basis_vector(j, a, K)
            assert abs(phi @ psi) < 1e-12, f"non-orthogonal at j={j}, a={a}"


from collatz.wavelets import haar_forward


def test_haar_forward_K2_known_values():
    """For K=2, transform of [a, b, c, d] matches hand calculation."""
    f = np.array([1.0, 2.0, 3.0, 4.0])
    c0, coeffs = haar_forward(f)
    # c0 = (1+2+3+4)/2 = 5.0
    assert abs(c0 - 5.0) < 1e-12
    # coeffs[0] (shell 0) = (1+2-3-4)/2 = -2.0
    # coeffs[1] (shell 1, a=0) = (1-2)/sqrt(2) = -1/sqrt(2)
    # coeffs[2] (shell 1, a=1) = (3-4)/sqrt(2) = -1/sqrt(2)
    np.testing.assert_allclose(coeffs, [-2.0, -1 / np.sqrt(2), -1 / np.sqrt(2)])


def test_haar_forward_basis_vector_is_one_hot():
    """The forward transform of a basis vector psi_{j,a} should be a one-hot at idx(j,a)."""
    K = 4
    N = 1 << K
    for j in range(K):
        for a in range(1 << j):
            psi = kozyrev_basis_vector(j, a, K)
            c0, coeffs = haar_forward(psi)
            assert abs(c0) < 1e-12, f"c0 nonzero for psi_{j},{a}"
            expected = np.zeros(N - 1)
            expected[idx(j, a)] = 1.0
            np.testing.assert_allclose(coeffs, expected, atol=1e-12)


def test_haar_forward_constant_function():
    """For f ≡ c, all wavelet coefficients should be zero; c0 = c * sqrt(N)."""
    K = 6
    N = 1 << K
    f = np.full(N, 3.5)
    c0, coeffs = haar_forward(f)
    np.testing.assert_allclose(coeffs, np.zeros(N - 1), atol=1e-12)
    assert abs(c0 - 3.5 * np.sqrt(N)) < 1e-10


def test_haar_forward_parseval():
    """||f||^2 == c0^2 + sum |c_{j,a}|^2 for random f."""
    rng = np.random.default_rng(42)
    K = 8
    N = 1 << K
    f = rng.standard_normal(N)
    c0, coeffs = haar_forward(f)
    lhs = float(f @ f)
    rhs = c0 * c0 + float(coeffs @ coeffs)
    assert abs(lhs - rhs) / lhs < 1e-12


def test_haar_forward_rejects_non_power_of_two():
    with pytest.raises(ValueError):
        haar_forward(np.zeros(7))


from collatz.wavelets import haar_inverse


def test_haar_inverse_round_trip_random():
    """haar_inverse(*haar_forward(f)) ≈ f to float64 precision."""
    rng = np.random.default_rng(7)
    for K in (2, 4, 6, 9):
        N = 1 << K
        f = rng.standard_normal(N)
        c0, coeffs = haar_forward(f)
        g = haar_inverse(c0, coeffs)
        np.testing.assert_allclose(g, f, atol=1e-12, rtol=1e-12)


def test_haar_inverse_full_reconstruction_equals_input():
    """With depth_cutoff = K (default), full reconstruction is exact."""
    f = np.array([1.0, 2.0, 3.0, 4.0, -1.0, 0.5, 7.0, -2.0])
    c0, coeffs = haar_forward(f)
    g = haar_inverse(c0, coeffs, depth_cutoff=None)
    np.testing.assert_allclose(g, f, atol=1e-12)


def test_haar_inverse_partial_reconstruction_monotone():
    """||f - f_J||^2 is non-increasing as J increases (Parseval projection)."""
    rng = np.random.default_rng(11)
    K = 8
    N = 1 << K
    f = rng.standard_normal(N)
    c0, coeffs = haar_forward(f)
    prev_err = np.inf
    for J in range(K + 1):
        f_J = haar_inverse(c0, coeffs, depth_cutoff=J)
        err = float(np.sum((f - f_J) ** 2))
        assert err <= prev_err + 1e-12, f"reconstruction error grew at J={J}"
        prev_err = err
    # At J = K, error must be ~0
    assert prev_err < 1e-20


def test_haar_inverse_J0_returns_mean():
    """With depth_cutoff = 0, reconstruction is f's mean projected onto phi."""
    f = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    c0, coeffs = haar_forward(f)
    f_0 = haar_inverse(c0, coeffs, depth_cutoff=0)
    expected = np.full_like(f, f.mean())
    np.testing.assert_allclose(f_0, expected, atol=1e-12)


def test_haar_inverse_ball_indicator_concentrates_at_coarse_shells():
    """Indicator of a 2-adic ball at level j0 has zero coefficients at shells j > j0."""
    K = 5
    N = 1 << K
    j0 = 2  # ball of support size N / 2^j0 = 8
    a0 = 1  # ball at indices [8, 16)
    support = 1 << (K - j0)
    f = np.zeros(N)
    f[a0 * support : (a0 + 1) * support] = 1.0
    c0, coeffs = haar_forward(f)
    # All wavelet coefficients at shells j > j0 must be zero
    for j in range(j0 + 1, K):
        for a in range(1 << j):
            assert abs(coeffs[idx(j, a)]) < 1e-12, f"nonzero at j={j}, a={a}"
