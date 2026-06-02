"""2-adic Newton potential of the Collatz dropping classification.

For each n in [1, N], compute the standard stopping time T(n) and several
"potential" functions V(n) that put a Newton-style 1/distance^p kernel
on the 2-adic distance |n - m|_2 = 2^{-v_2(|n-m|)}, where v_2 is the
2-adic valuation.

Two structural visualizations:

  1. Stopping-time fractal — T(n) reshaped as a 2D image, with axes
     being the high-half and low-half bits of n. Nearby pixels are
     2-adically close integers. The image should show a self-similar
     fractal: residue classes mod 2^k organized into nested rectangles,
     each row/column band echoing a Beatty rung.

  2. Sturmian-signed Newton potential V_χ(n) — for each n, compute
                V_χ(n) = Σ_{m ≠ n} χ(m) · 4^{v_2(|n-m|)} / 4^K
     where χ(m) is the proved Sturmian sign of the dropping class
     containing m (from Part 5 of the Dropping Zeta Spectrum thread).
     The 4^{v_2} weight is the inverse-square law of 2-adic Newton.
     The result is a signed scalar field on the integers that
     visualizes how the Sturmian phase pattern propagates through
     2-adic neighborhoods.

The 2D-image rendering of V_χ should expose any non-trivial geometric
structure that the inverse-square law extracts from the dropping
classification — analogous to how Newton's potential lets you "see"
gravitational mass distributions in 3-space.

Outputs:
    data/collatz_2adic_potential.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from collatz.stopping import stopping_time
from collatz.utils import (
    LOG2_3,
    beatty_to_o,
    bits_to_2d,
    sturmian_sign,
    trailing_zeros_vec,
)


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(exist_ok=True)

    K = 11  # N = 2^K = 2048
    N = 1 << K
    half = K // 2
    rows = 1 << (K - half)  # high-half bit count → rows = 64
    cols = 1 << half        # low-half bit count → cols = 32
    print(f"K = {K}, N = {N}, image = {rows} × {cols}")

    # ---------- Stopping times ----------
    print("Computing T(n) for n = 1..N ...")
    T = np.zeros(N + 1, dtype=np.int64)
    for n in range(2, N + 1):  # n=1 stays 0 (no drop below 1; core requires n > 1)
        T[n] = stopping_time(n)

    # ---------- Sturmian sign χ(n) ----------
    print("Building Sturmian sign χ(n)...")
    k_to_o = beatty_to_o()
    chi = np.zeros(N + 1, dtype=np.float64)
    on_beatty = 0
    off_beatty = 0
    even_count = 0
    for n in range(1, N + 1):
        t = int(T[n])
        if t == 1:
            # Even n: drops in one step. Treat k_0 case as +1 (convention).
            chi[n] = +1
            even_count += 1
        elif t in k_to_o:
            chi[n] = float(sturmian_sign(k_to_o[t]))
            on_beatty += 1
        else:
            # Off-Beatty drops (affine-correction tail) — give χ = 0
            chi[n] = 0
            off_beatty += 1
    print(f"  even (k_0): {even_count}, on-Beatty odd: {on_beatty}, "
          f"off-Beatty: {off_beatty}")

    # ---------- Newton-like potentials ----------
    print("Computing 2-adic potentials V(n)...")
    ns = np.arange(1, N + 1, dtype=np.int64)
    chi_vec = chi[1:N + 1]
    V_chi = np.zeros(N + 1, dtype=np.float64)
    V_uniform = np.zeros(N + 1, dtype=np.float64)
    V_T = np.zeros(N + 1, dtype=np.float64)
    norm = 4.0 ** K

    # Weight by inverse-square 2-adic distance
    T_vec = T[1:N + 1].astype(np.float64)
    for n in range(1, N + 1):
        d = np.abs(ns - n)
        d[d == 0] = 1 << 50  # placeholder for self — weight ≈ 0
        tz = trailing_zeros_vec(d)
        tz = np.clip(tz, 0, K)
        w = (4.0 ** tz) / norm
        # Self exclusion
        w[ns == n] = 0
        V_chi[n] = float(np.sum(chi_vec * w))
        V_uniform[n] = float(np.sum(w))
        V_T[n] = float(np.sum(T_vec * w))

    # ---------- Reshape to 2D ----------
    img_T = np.full((rows, cols), np.nan)
    img_chi = np.full((rows, cols), np.nan)
    img_V = np.full((rows, cols), np.nan)
    for n in range(1, N + 1):
        hi, lo = bits_to_2d(n, K)
        if hi < rows and lo < cols:
            img_T[hi, lo] = T[n]
            img_chi[hi, lo] = chi[n]
            img_V[hi, lo] = V_chi[n]

    # ---------- Plot ----------
    fig = plt.figure(figsize=(16, 11))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1], hspace=0.32, wspace=0.28)

    # Top-left: T(n) strip
    ax = fig.add_subplot(gs[0, 0])
    sc = ax.scatter(np.arange(1, N + 1), T[1:N + 1], c=T[1:N + 1],
                    cmap='viridis', s=2.5, edgecolor='none')
    ax.set_xlabel('n')
    ax.set_ylabel('T(n)')
    ax.set_title(f'Standard stopping time T(n), n = 1..{N}')
    fig.colorbar(sc, ax=ax, label='T(n)', shrink=0.85)
    ax.grid(alpha=0.3)

    # Top-middle: V_uniform
    ax = fig.add_subplot(gs[0, 1])
    ax.plot(np.arange(1, N + 1), V_uniform[1:N + 1], lw=0.6, color='#7f8c8d')
    ax.set_xlabel('n')
    ax.set_ylabel(r'$V_0(n)$')
    ax.set_title(r'Unsigned 2-adic potential $V_0(n) = \sum_m 4^{v_2|n-m|}/4^K$'
                 '\n(uniform charge — baseline ≈ constant)')
    ax.grid(alpha=0.3)

    # Top-right: V_chi
    ax = fig.add_subplot(gs[0, 2])
    Vchi_slice = V_chi[1:N + 1]
    colors = np.where(Vchi_slice >= 0, '#3498db', '#e74c3c')
    ax.bar(np.arange(1, N + 1), Vchi_slice, color=colors, width=1.0,
           edgecolor='none')
    ax.axhline(0, color='black', lw=0.6)
    ax.set_xlabel('n')
    ax.set_ylabel(r'$V_\chi(n)$')
    ax.set_title(r'Sturmian-signed Newton potential'
                 '\n' r'$V_\chi(n) = \sum_m \chi(m) \cdot 4^{v_2|n-m|}/4^K$')
    ax.grid(alpha=0.3)

    # Bottom-left: T(n) as 2D fractal
    ax = fig.add_subplot(gs[1, 0])
    im = ax.imshow(img_T, cmap='viridis', aspect='auto',
                   interpolation='nearest', origin='lower')
    ax.set_xlabel(f'low {half} bits of n')
    ax.set_ylabel(f'high {K - half} bits of n')
    ax.set_title('T(n) as 2D image — 2-adic fractal structure of dropping classes')
    fig.colorbar(im, ax=ax, label='T(n)', shrink=0.85)

    # Bottom-middle: χ(n) as 2D
    ax = fig.add_subplot(gs[1, 1])
    im = ax.imshow(img_chi, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1,
                   interpolation='nearest', origin='lower')
    ax.set_xlabel(f'low {half} bits of n')
    ax.set_ylabel(f'high {K - half} bits of n')
    ax.set_title('χ(n) = Sturmian sign of n\'s dropping class\n'
                 '(red = −1 / blue = +1 / white = off-Beatty)')
    fig.colorbar(im, ax=ax, label='χ(n)', shrink=0.85)

    # Bottom-right: V_chi as 2D fractal — this is the headline
    ax = fig.add_subplot(gs[1, 2])
    vmax = float(np.nanmax(np.abs(img_V)))
    im = ax.imshow(img_V, cmap='RdBu_r', aspect='auto',
                   vmin=-vmax, vmax=vmax,
                   interpolation='nearest', origin='lower')
    ax.set_xlabel(f'low {half} bits of n')
    ax.set_ylabel(f'high {K - half} bits of n')
    ax.set_title(r'$V_\chi(n)$ as 2D image — Sturmian phase made geometric'
                 '\n(the inverse-square-twisted dropping field)')
    fig.colorbar(im, ax=ax, label=r'$V_\chi$', shrink=0.85)

    fig.suptitle(
        "2-adic Newton potential of the Collatz dropping classification\n"
        "(stopping time → 2-adic fractal; Sturmian sign rule → "
        "inverse-square geometric field)",
        fontsize=13, y=0.995,
    )

    out_png = out_dir / "collatz_2adic_potential.png"
    fig.savefig(out_png, dpi=120, facecolor='white', bbox_inches='tight')
    print(f"Saved {out_png}")


if __name__ == "__main__":
    main()
