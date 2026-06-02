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
    # Note on asymmetry: H_K is over K shell-energies (constant mode excluded
    # via Kozyrev's c0 split), while H_W is over K+1 weight-energy buckets
    # (w=0 bucket included = F[0]^2 = c0^2). For DC-heavy fields (e.g.
    # dropping-set indicators) this inflates H_W relative to H_K and biases
    # the duality scatter toward the "Kozyrev-localized" half-plane. The
    # asymmetry is a deliberate spec choice (the constant mode lives in the
    # same array as Walsh wavelet coefficients but is split out in the Haar
    # representation); read the scatter accordingly.
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
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(exist_ok=True)

    K = 11
    N = 1 << K
    target_dropping_classes = [1, 3, 6, 8, 11, 13, 16]
    partial_recon_depths = [2, 4, 6, 8, K]

    print(f"K = {K}, N = {N}")
    print("Building input fields...")
    chi = build_chi(N)
    T = build_stopping_time_field(N)
    indicators = {
        k: build_dropping_indicator(N, k) for k in target_dropping_classes
    }
    nonempty = [k for k, v in indicators.items() if v.sum() > 0]
    if len(nonempty) < len(target_dropping_classes):
        skipped = sorted(set(target_dropping_classes) - set(nonempty))
        print(f"  skipping empty dropping classes: {skipped}")
    target_dropping_classes = nonempty

    print("Running Haar (Kozyrev) transforms...")
    c0_chi, coeffs_chi = haar_forward(chi)
    c0_T, coeffs_T = haar_forward(T)
    coeffs_Dk = {k: haar_forward(indicators[k])[1] for k in target_dropping_classes}

    E_chi = shell_energies(coeffs_chi, K)
    E_T = shell_energies(coeffs_T, K)
    E_Dk = {k: shell_energies(coeffs_Dk[k], K) for k in target_dropping_classes}

    print("Running Walsh-Hadamard transforms...")
    F_chi = walsh_forward(chi)
    F_T = walsh_forward(T)
    F_Dk = {k: walsh_forward(indicators[k]) for k in target_dropping_classes}

    W_chi = weight_energies(F_chi, K)
    W_T = weight_energies(F_T, K)
    W_Dk = {k: weight_energies(F_Dk[k], K) for k in target_dropping_classes}

    print("Estimating Kozyrev and Walsh shuffle null bands (100 shuffles each)...")
    null_mean_K, null_std_K = shuffle_null_band(chi, K, n_shuffles=100, seed=0)
    null_mean_W, null_std_W = walsh_shuffle_null_band(chi, K, n_shuffles=100, seed=1)

    print("Computing duality entropies (H_K, H_W)...")
    duality_points: list[tuple[str, float, float, str, str]] = []
    H_K_chi, H_W_chi = duality_entropies(coeffs_chi, F_chi, K)
    duality_points.append((r"$\chi$", H_K_chi, H_W_chi, "#2c3e50", "o"))
    H_K_T, H_W_T = duality_entropies(coeffs_T, F_T, K)
    duality_points.append(("T", H_K_T, H_W_T, "#c0392b", "s"))
    cmap = plt.colormaps["viridis"]
    for i, k in enumerate(target_dropping_classes):
        color = cmap(i / max(1, len(target_dropping_classes) - 1))
        H_K_k, H_W_k = duality_entropies(coeffs_Dk[k], F_Dk[k], K)
        duality_points.append((rf"$D_{{{k}}}$", H_K_k, H_W_k, color, "^"))
    # Shuffled-chi control point
    rng = np.random.default_rng(99)
    shuf = chi[rng.permutation(N)]
    _, coeffs_shuf = haar_forward(shuf)
    F_shuf = walsh_forward(shuf)
    H_K_shuf, H_W_shuf = duality_entropies(coeffs_shuf, F_shuf, K)
    duality_points.append(("shuf(χ)", H_K_shuf, H_W_shuf, "#95a5a6", "x"))

    print("Building partial reconstructions of chi...")
    chi_reconstructions = {
        J: haar_inverse(c0_chi, coeffs_chi, depth_cutoff=J)
        for J in partial_recon_depths
    }

    # ---------- Figure ----------
    fig = plt.figure(figsize=(16, 17))
    gs = fig.add_gridspec(4, 3, hspace=0.55, wspace=0.32)

    # Row 0: Kozyrev shell-energy curves
    js = np.arange(K)
    ax = fig.add_subplot(gs[0, 0])
    ax.plot(js, E_chi, marker="o", color="#2c3e50", label=r"$E_j(\chi)$")
    ax.fill_between(
        js,
        null_mean_K - 2 * null_std_K,
        null_mean_K + 2 * null_std_K,
        color="#bdc3c7",
        alpha=0.6,
        label=r"shuffle null $\pm 2\sigma$",
    )
    ax.plot(js, null_mean_K, color="#7f8c8d", lw=0.8, linestyle="--", label="null mean")
    ax.set_xlabel("Kozyrev shell j")
    ax.set_ylabel(r"$E_j$")
    ax.set_title(r"Kozyrev: $\chi$ shell energies vs null")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    ax = fig.add_subplot(gs[0, 1])
    for i, k in enumerate(target_dropping_classes):
        color = cmap(i / max(1, len(target_dropping_classes) - 1))
        norm = E_Dk[k].sum()
        if norm > 0:
            ax.plot(js, E_Dk[k] / norm, marker="o", color=color, label=f"$D_{k}$")
    ax.set_xlabel("Kozyrev shell j")
    ax.set_ylabel(r"$\hat E_j$")
    ax.set_title("Kozyrev: dropping-class fingerprints")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    ax = fig.add_subplot(gs[0, 2])
    ax.plot(js, E_T, marker="o", color="#c0392b", label=r"$E_j(T)$")
    ax.set_xlabel("Kozyrev shell j")
    ax.set_ylabel(r"$E_j$")
    ax.set_title("Kozyrev: stopping time T(n)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Row 1: Walsh weight-energy curves (dual to Row 0)
    ws = np.arange(K + 1)
    ax = fig.add_subplot(gs[1, 0])
    ax.plot(ws, W_chi, marker="o", color="#2c3e50", label=r"$W_w(\chi)$")
    ax.fill_between(
        ws,
        null_mean_W - 2 * null_std_W,
        null_mean_W + 2 * null_std_W,
        color="#bdc3c7",
        alpha=0.6,
        label=r"shuffle null $\pm 2\sigma$",
    )
    ax.plot(ws, null_mean_W, color="#7f8c8d", lw=0.8, linestyle="--", label="null mean")
    ax.set_xlabel("Walsh weight w")
    ax.set_ylabel(r"$W_w$")
    ax.set_title(r"Walsh: $\chi$ weight energies vs null")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    ax = fig.add_subplot(gs[1, 1])
    for i, k in enumerate(target_dropping_classes):
        color = cmap(i / max(1, len(target_dropping_classes) - 1))
        norm = W_Dk[k].sum()
        if norm > 0:
            ax.plot(ws, W_Dk[k] / norm, marker="o", color=color, label=f"$D_{k}$")
    ax.set_xlabel("Walsh weight w")
    ax.set_ylabel(r"$\hat W_w$")
    ax.set_title("Walsh: dropping-class fingerprints")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    ax = fig.add_subplot(gs[1, 2])
    ax.plot(ws, W_T, marker="o", color="#c0392b", label=r"$W_w(T)$")
    ax.set_xlabel("Walsh weight w")
    ax.set_ylabel(r"$W_w$")
    ax.set_title("Walsh: stopping time T(n)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Row 2: bit-split images of partial reconstructions of chi
    selected_recon = [
        partial_recon_depths[0],
        partial_recon_depths[len(partial_recon_depths) // 2],
        partial_recon_depths[-1],
    ]
    titles = [rf"$\chi_{{J={J}}}$" for J in selected_recon]
    for col, (J, title) in enumerate(zip(selected_recon, titles)):
        img = field_to_2d(chi_reconstructions[J], K)
        ax = fig.add_subplot(gs[2, col])
        vmax = float(np.nanmax(np.abs(img))) or 1.0
        ax.imshow(
            img,
            cmap="RdBu_r",
            aspect="auto",
            vmin=-vmax,
            vmax=vmax,
            interpolation="nearest",
            origin="lower",
        )
        ax.set_xlabel(f"low {K // 2} bits of n")
        ax.set_ylabel(f"high {K - K // 2} bits of n")
        ax.set_title(title)

    # Row 3 col 0: duality scatter (H_K vs H_W)
    ax = fig.add_subplot(gs[3, 0])
    H_K_max = float(np.log2(K))
    H_W_max = float(np.log2(K + 1))
    # Reference: max-entropy corner and diagonal lower bound proxy
    ax.axhline(H_W_max, color="#bdc3c7", lw=0.6, linestyle=":")
    ax.axvline(H_K_max, color="#bdc3c7", lw=0.6, linestyle=":")
    for label, H_K_v, H_W_v, color, marker in duality_points:
        ax.scatter([H_K_v], [H_W_v], s=80, c=[color], marker=marker,
                   edgecolor="black", linewidth=0.5, label=label)
    ax.set_xlim(-0.1, H_K_max + 0.2)
    ax.set_ylim(-0.1, H_W_max + 0.2)
    ax.set_xlabel(r"$H_K$ (Kozyrev shell entropy, bits)")
    ax.set_ylabel(r"$H_W$ (Walsh weight entropy, bits)")
    ax.set_title("Duality scatter: H_K vs H_W")
    ax.legend(fontsize=7, loc="lower left", ncol=2)
    ax.grid(alpha=0.3)

    # Row 3 cols 1, 2: dyadic spectrograms of chi and T
    for col, (label, c) in enumerate([(r"$\chi$", coeffs_chi), ("T(n)", coeffs_T)]):
        grid = coefficient_grid(c, K)
        ax = fig.add_subplot(gs[3, col + 1])
        ax.imshow(
            np.log1p(grid),
            cmap="viridis",
            aspect="auto",
            origin="lower",
            interpolation="nearest",
        )
        ax.set_xlabel("offset a")
        ax.set_ylabel("shell j")
        ax.set_title(f"dyadic spectrogram: {label} (log)")

    fig.suptitle(
        "Kozyrev orbital spectrum of Collatz dropping classification\n"
        rf"$N = 2^{{{K}}} = {N}$ — Kozyrev (particle basis), Walsh (wave basis), duality scatter",
        fontsize=13,
        y=0.995,
    )

    out_png = out_dir / "collatz_kozyrev_spectrum.png"
    fig.savefig(out_png, dpi=120, facecolor="white", bbox_inches="tight")
    print(f"Saved {out_png}")


if __name__ == "__main__":
    main()
