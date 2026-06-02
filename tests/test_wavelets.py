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
