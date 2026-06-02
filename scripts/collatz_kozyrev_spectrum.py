# scripts/collatz_kozyrev_spectrum.py
"""Kozyrev orbital spectrum of Collatz dropping sets.

Decomposes three fields on Z / 2^K Z in the orthonormal Kozyrev (= dyadic
Haar) wavelet basis:

  - chi(n)        the proved Sturmian sign of n's dropping class,
                  zero on off-Beatty values
  - 1_{D_k}(n)    indicator of dropping set k (selected k values)
  - T(n)          standard stopping time

For each field we compute the Kozyrev shell-energy spectrum E_j and the
dual Walsh-Hadamard weight-energy spectrum W_w, partial reconstructions
f_J at increasing J, shuffle-based null bands for both bases, and the
duality scatter (H_K vs H_W).

Output: data/collatz_kozyrev_spectrum.png
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from collatz.dropping import dropping_set
from collatz.stopping import stopping_time
from collatz.utils import beatty_to_o, bits_to_2d, sturmian_sign
from collatz.walsh import shannon_entropy, walsh_forward, weight_energies
from collatz.wavelets import (
    coefficient_grid,
    haar_forward,
    haar_inverse,
    shell_energies,
)


# ---------- Input field constructors ----------


def build_chi(N: int) -> np.ndarray:
    """Sturmian sign field chi(n) for n in [0, N).

    chi[0] := 0 (no class). For n >= 2:
      - if stopping_time(n) == 1: chi[n] = +1 (k_0 convention)
      - if stopping_time(n) maps back to a Beatty rung o: chi[n] = sturmian_sign(o)
      - else (off-Beatty tail): chi[n] = 0
    chi[1] := 0 (stopping_time is undefined for n=1).
    """
    k_to_o = beatty_to_o()
    chi = np.zeros(N, dtype=np.float64)
    for n in range(2, N):
        t = stopping_time(n)
        if t == 1:
            chi[n] = 1.0
        elif t in k_to_o:
            chi[n] = float(sturmian_sign(k_to_o[t]))
        else:
            chi[n] = 0.0
    return chi


def build_dropping_indicator(N: int, k: int) -> np.ndarray:
    """Indicator vector 1_{D_k}(n) for n in [0, N): 1 if dropping_set(n) == k."""
    out = np.zeros(N, dtype=np.float64)
    for n in range(2, N):
        if dropping_set(n) == k:
            out[n] = 1.0
    return out


def build_stopping_time_field(N: int) -> np.ndarray:
    """Stopping-time field T(n) as float for n in [0, N); T(0) = T(1) = 0."""
    out = np.zeros(N, dtype=np.float64)
    for n in range(2, N):
        out[n] = float(stopping_time(n))
    return out


# ---------- Wavelet analysis helpers ----------


def shuffle_null_band(
    f: np.ndarray, K: int, n_shuffles: int = 100, seed: int = 0
) -> tuple[np.ndarray, np.ndarray]:
    """Estimate per-Kozyrev-shell null mean and std under random permutations of f.

    Returns (mean[K], std[K]) of shell energies over `n_shuffles` random
    permutations.
    """
    rng = np.random.default_rng(seed)
    samples = np.empty((n_shuffles, K), dtype=np.float64)
    for i in range(n_shuffles):
        idx = rng.permutation(f.size)
        _, c = haar_forward(f[idx])
        samples[i] = shell_energies(c, K)
    return samples.mean(axis=0), samples.std(axis=0)


def walsh_shuffle_null_band(
    f: np.ndarray, K: int, n_shuffles: int = 100, seed: int = 1
) -> tuple[np.ndarray, np.ndarray]:
    """Estimate per-Walsh-weight null mean and std under random permutations of f.

    Returns (mean[K+1], std[K+1]) of weight energies over `n_shuffles` random
    permutations. The w = 0 entry is the constant-mode energy F[0]^2.
    """
    rng = np.random.default_rng(seed)
    samples = np.empty((n_shuffles, K + 1), dtype=np.float64)
    for i in range(n_shuffles):
        idx = rng.permutation(f.size)
        F = walsh_forward(f[idx])
        samples[i] = weight_energies(F, K)
    return samples.mean(axis=0), samples.std(axis=0)


def duality_entropies(
    coeffs_kozyrev: np.ndarray, F_walsh: np.ndarray, K: int
) -> tuple[float, float]:
    """Return (H_K, H_W) = Shannon entropies of normalized Kozyrev and Walsh spectra.

    Kozyrev: distribution over K shells (constant mode excluded).
    Walsh:   distribution over (K+1) Hamming-weight buckets, INCLUDING w=0.
    Conventions match the spec's H4 sub-claims.
    """
    E = shell_energies(coeffs_kozyrev, K)
    W = weight_energies(F_walsh, K)
    E_total = E.sum()
    W_total = W.sum()
    H_K = shannon_entropy(E / E_total) if E_total > 0 else 0.0
    H_W = shannon_entropy(W / W_total) if W_total > 0 else 0.0
    return H_K, H_W


def field_to_2d(field: np.ndarray, K: int) -> np.ndarray:
    """Lay out a length-2^K field as a 2D bit-split image (high bits row, low bits col)."""
    half = K // 2
    rows = 1 << (K - half)
    cols = 1 << half
    img = np.full((rows, cols), np.nan, dtype=np.float64)
    for n in range(1, field.size):
        hi, lo = bits_to_2d(n, K)
        if hi < rows and lo < cols:
            img[hi, lo] = field[n]
    return img


def main() -> None:
    raise SystemExit("Pipeline not yet implemented; see Task 9.")


if __name__ == "__main__":
    main()
