"""Kozyrev/Haar wavelet transform on Z_2 / 2^K Z_2.

The Kozyrev wavelet basis on Z_p (Kozyrev, 2002) consists of eigenfunctions
of the Vladimirov p-adic Laplacian. For p = 2 they coincide with the
discrete dyadic Haar wavelets on the integers [0, 2^K).

Basis convention:
    - phi(n) = 1 / sqrt(N)                            (one constant mode)
    - psi_{j, a}(n), j in [0, K), a in [0, 2^j)       (N - 1 wavelets)
      supp(psi_{j, a}) = [a * 2^{K-j}, (a+1) * 2^{K-j})
      values: +1/sqrt(2^{K-j}) on the first half of the support,
              -1/sqrt(2^{K-j}) on the second half.

Shell j = 0 is coarsest; j = K-1 is finest. Flat index: 2^j - 1 + a.

Parseval: ||f||^2 = c0^2 + sum_{j,a} c_{j,a}^2.
"""
from __future__ import annotations

import numpy as np


def idx(j: int, a: int) -> int:
    """Heap-style flat index for wavelet (j, a).

    Example: idx(0, 0) == 0, idx(1, 0) == 1, idx(2, 3) == 6.
    """
    return (1 << j) - 1 + a


def kozyrev_basis_vector(j: int, a: int, K: int) -> np.ndarray:
    """Build psi_{j, a} explicitly as a length-2^K array.

    Used for tests and illustration; not called by the fast transform.

    Example: kozyrev_basis_vector(1, 0, 2) == [1/sqrt(2), -1/sqrt(2), 0, 0].
    """
    if not (0 <= j < K):
        raise ValueError(f"shell j={j} out of range [0, {K})")
    if not (0 <= a < (1 << j)):
        raise ValueError(f"offset a={a} out of range [0, {1 << j})")
    N = 1 << K
    support_size = 1 << (K - j)
    half = support_size // 2
    start = a * support_size
    scale = 1.0 / np.sqrt(support_size)
    vec = np.zeros(N, dtype=np.float64)
    vec[start : start + half] = scale
    vec[start + half : start + support_size] = -scale
    return vec


def haar_forward(f: np.ndarray) -> tuple[float, np.ndarray]:
    """Fast orthonormal Haar/Kozyrev transform.

    Args:
        f: length-N array, N a power of 2.

    Returns:
        (c0, coeffs) where
            c0      = <f, phi>  with phi(n) = 1/sqrt(N)
            coeffs  = length-(N-1) array; coeffs[idx(j, a)] = <f, psi_{j, a}>

    Implementation: standard in-place dyadic cascade, O(N log N).
    The finest details (shell j = K - 1) are computed first; the coarsest
    (shell j = 0) last.

    Example: haar_forward(np.array([1., 2., 3., 4.])) -> (5.0, [-2.0, -1/sqrt(2), -1/sqrt(2)]).
    """
    f = np.asarray(f, dtype=np.float64)
    N = f.size
    if N == 0 or (N & (N - 1)) != 0:
        raise ValueError(f"length {N} is not a positive power of 2")
    K = int(round(np.log2(N)))

    s = f.copy()
    coeffs = np.empty(N - 1, dtype=np.float64)
    inv_sqrt2 = 1.0 / np.sqrt(2.0)
    # Cascade from finest (j = K-1) down to coarsest (j = 0).
    for j in range(K - 1, -1, -1):
        # s has length 2^(j+1) at this point.
        new_s = (s[0::2] + s[1::2]) * inv_sqrt2
        new_d = (s[0::2] - s[1::2]) * inv_sqrt2
        coeffs[(1 << j) - 1 : (1 << (j + 1)) - 1] = new_d
        s = new_s
    c0 = float(s[0])
    return c0, coeffs
