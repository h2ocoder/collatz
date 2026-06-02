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
