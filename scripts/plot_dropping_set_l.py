"""Visualize D_chi_6(N) split by dropping set: α_k = |sum_k|/count_nz_k."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    data_path = Path(__file__).resolve().parents[1] / "data" / "dropping_set_l_function.npz"
    out_dir = Path(__file__).resolve().parents[1] / "data"
    data = np.load(data_path)

    N = 300_000
    ks = data[f"N{N}_k"]
    cnt = data[f"N{N}_count"]
    cnt_nz = data[f"N{N}_count_nz"]
    re = data[f"N{N}_sum_re"]
    im = data[f"N{N}_sum_im"]

    mag = np.hypot(re, im)
    alpha = np.where(cnt_nz > 0, mag / np.maximum(cnt_nz, 1), 0)
    arg = np.degrees(np.arctan2(im, re))
    signed_alpha = alpha * np.sign(im)  # +1 if upper half, -1 if lower

    # Show only k with at least 50 contributing n's (statistically meaningful)
    keep = cnt_nz >= 50
    ks_p = ks[keep]; alpha_p = alpha[keep]; signed_p = signed_alpha[keep]
    cnt_p = cnt[keep]

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    ax = axes[0]
    ax.axhline(np.sqrt(3) / 2, color="r", ls="--", lw=0.7, label="√3/2 ≈ 0.866 (saturation)")
    ax.axhline(np.sqrt(3) / 6, color="g", ls="--", lw=0.7, label="√3/6 ≈ 0.289")
    ax.axhline(1 / 8, color="purple", ls="--", lw=0.7, label="1/8 = 0.125")
    ax.scatter(ks_p, alpha_p, c=cnt_p, cmap="viridis", s=80, edgecolor="black", linewidth=0.5)
    cbar = plt.colorbar(ax.collections[0], ax=ax)
    cbar.set_label("count_k (n's in Dset_k)")
    ax.set_ylabel(r"$\alpha_k = |\mathrm{sum}_k| / \mathrm{count\_nz}_k$")
    ax.set_title(rf"Per-n coherent character on Dset$_k$ ($\chi_6$, $N={N:,}$)")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_ylim(-0.05, 1.0)

    ax = axes[1]
    ax.axhline(0, color="black", lw=0.5)
    ax.axhline(+np.sqrt(3)/2, color="r", ls="--", lw=0.5)
    ax.axhline(-np.sqrt(3)/2, color="r", ls="--", lw=0.5)
    ax.scatter(ks_p, signed_p, c=cnt_p, cmap="viridis", s=80, edgecolor="black", linewidth=0.5)
    ax.set_xlabel("Dropping time k")
    ax.set_ylabel(r"$\alpha_k \cdot \mathrm{sign}(\mathrm{Im}\,\mathrm{sum}_k)$")
    ax.set_title("Same, signed by phase (≈ ±90° throughout)")
    ax.grid(alpha=0.3)
    ax.set_ylim(-1.0, 1.0)

    fig.tight_layout()
    out_png = out_dir / "dropping_set_l_function.png"
    fig.savefig(out_png, dpi=120)
    print(f"Saved {out_png}")

    # Print summary table for the writeup
    print(f"\nSummary table (N = {N:,}):")
    print(f"{'k':>4} {'count':>8} {'cnt_nz':>8} {'α_k':>10} {'phase':>10}")
    for k_val in sorted(set(ks_p.tolist())):
        i = int(np.where(ks == k_val)[0][0])
        a = arg[i]
        print(f"{int(ks[i]):>4d} {int(cnt[i]):>8d} {int(cnt_nz[i]):>8d} "
              f"{alpha[i]:>10.4f} {a:>+10.2f}")


if __name__ == "__main__":
    main()
