"""Walsh-Hadamard transform = 2-adic Fourier transform on Z / 2^K Z.

The Walsh characters W_m(n) = (-1)^{<m, n>_2} (bitwise dot product) are
exactly the additive characters of (Z / 2^K Z, +); they form an
orthonormal basis dual to the position basis. This is the "wave-like"
basis that pairs with the Kozyrev wavelets ("particle-like") under the
discrete 2-adic uncertainty principle.

Normalization: F[m] = (1/sqrt(N)) sum_n f[n] (-1)^{<m,n>_2}.
The transform is its own inverse: walsh_forward(walsh_forward(f)) == f.
Parseval: sum_m |F[m]|^2 = sum_n |f[n]|^2.
"""
from __future__ import annotations

import numpy as np


def walsh_forward(f: np.ndarray) -> np.ndarray:
    """Fast orthonormal Walsh-Hadamard transform (natural Hadamard order).

    Args:
        f: length-N array, N a power of 2.

    Returns:
        F of length N, F[m] = (1/sqrt(N)) sum_n f[n] (-1)^{<m,n>_2}.

    Implementation: in-place butterfly, O(N log N).
    """
    f = np.asarray(f, dtype=np.float64).copy()
    N = f.size
    if N == 0 or (N & (N - 1)) != 0:
        raise ValueError(f"length {N} is not a positive power of 2")
    h = 1
    while h < N:
        # Standard Hadamard butterfly on stride 2h.
        for i in range(0, N, h * 2):
            block = f[i : i + 2 * h]
            x = block[:h].copy()
            y = block[h:].copy()
            block[:h] = x + y
            block[h:] = x - y
        h *= 2
    return f / np.sqrt(N)


def weight_energies(F: np.ndarray, K: int) -> np.ndarray:
    """Bucket squared Walsh coefficients by Hamming weight of m.

    Returns shape (K+1,) where out[w] = sum_{popcount(m) = w} |F[m]|^2.
    The w = 0 entry is F[0]^2 (constant mode).
    """
    F = np.asarray(F, dtype=np.float64)
    N = F.size
    if N != (1 << K):
        raise ValueError(f"F.size={N} != 2^K={1 << K}")
    weights = np.array(
        [bin(m).count("1") for m in range(N)], dtype=np.int64
    )
    sq = F * F
    out = np.zeros(K + 1, dtype=np.float64)
    for w in range(K + 1):
        out[w] = sq[weights == w].sum()
    return out


def shannon_entropy(p: np.ndarray) -> float:
    """Shannon entropy in bits.

    Treats zero probabilities as contributing zero (0 * log 0 := 0).
    Does NOT normalize p; pass a probability vector.

    Example: shannon_entropy([0.5, 0.5]) == 1.0; shannon_entropy([1.0, 0.0]) == 0.0.
    """
    p = np.asarray(p, dtype=np.float64)
    mask = p > 0
    if not np.any(mask):
        return 0.0
    return float(-np.sum(p[mask] * np.log2(p[mask])))
