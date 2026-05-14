"""Spacing distribution of dropping-zeta zeros: GUE vs GOE vs Poisson?

We use the K=30 zeros and compute normalized nearest-neighbor spacings.

With only ~14 conjugate pairs the statistics are weak — this is a
qualitative check, not a Kolmogorov-Smirnov-strong test.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    data_path = Path(__file__).resolve().parents[1] / "data" / "dropping_zeta_zeros.npz"
    out_dir = Path(__file__).resolve().parents[1] / "data"
    data = np.load(data_path)
    s = data["roots_s"]

    # Drop the trivial root (closest to s=1, real)
    abs_z = np.abs(np.exp(-s * np.log(2)))
    triv_idx = int(np.argmin(np.abs(abs_z - 0.5)))
    mask = np.ones(len(s), dtype=bool); mask[triv_idx] = False
    s_nt = s[mask]

    # Use upper half-plane only (Im(s) > 0), the conjugate symmetric pair
    upper = s_nt[s_nt.imag > 0]
    upper = upper[np.argsort(upper.imag)]  # sort by Im(s)
    print(f"Non-trivial zeros in upper half-plane (sorted by Im(s)): {len(upper)}")
    print(f"{'Im(s)':>10} {'Re(s)':>10}")
    for z in upper:
        print(f"{z.imag:>10.4f} {z.real:>10.4f}")

    # Compute consecutive Im(s) spacings
    Im = upper.imag
    spacings = np.diff(Im)
    mean_spacing = spacings.mean()
    s_norm = spacings / mean_spacing
    print(f"\nMean Im-spacing: {mean_spacing:.4f}")
    print(f"Normalized spacings:")
    for i, sn in enumerate(s_norm):
        print(f"  {Im[i]:>6.3f} -> {Im[i+1]:>6.3f} : s = {sn:.4f}")

    # Reference distributions
    s_grid = np.linspace(0, 3, 200)
    pi = np.pi
    # Wigner surmise GOE: P(s) = (pi/2) s exp(-pi s^2 / 4)
    p_goe = (pi / 2) * s_grid * np.exp(-pi * s_grid**2 / 4)
    # Wigner surmise GUE: P(s) = (32/pi^2) s^2 exp(-4 s^2 / pi)
    p_gue = (32 / pi**2) * s_grid**2 * np.exp(-4 * s_grid**2 / pi)
    # Poisson: P(s) = exp(-s)
    p_poi = np.exp(-s_grid)

    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    ax.hist(s_norm, bins=np.linspace(0, 3, 10), density=True,
            alpha=0.6, color="C0", label=f"empirical (n={len(s_norm)})")
    ax.plot(s_grid, p_poi, "C1--", label="Poisson")
    ax.plot(s_grid, p_goe, "C2-", label="Wigner-Dyson GOE")
    ax.plot(s_grid, p_gue, "C3-", label="Wigner-Dyson GUE")
    ax.set_xlabel("normalized spacing s / <s>")
    ax.set_ylabel("density")
    ax.set_title(f"Im(s) nearest-neighbor spacings\n(K=30 dropping zeta, n={len(s_norm)})")
    ax.legend()
    ax.grid(alpha=0.3)
    out_png = out_dir / "spacing_distribution.png"
    fig.savefig(out_png, dpi=120)
    print(f"\nSaved {out_png}")

    # Quantitative: compare to predictions
    # Mean ratio: ratio test (Atas et al. 2013)
    # r_n = min(s_n, s_{n+1}) / max(s_n, s_{n+1})
    if len(s_norm) >= 2:
        s_arr = np.array(s_norm)
        r = np.minimum(s_arr[:-1], s_arr[1:]) / np.maximum(s_arr[:-1], s_arr[1:])
        print(f"\nMean ratio <r> = {r.mean():.4f}")
        print(f"  Poisson prediction:   <r> ≈ 0.386 (= 2 ln 2 − 1)")
        print(f"  GOE prediction:       <r> ≈ 0.5359")
        print(f"  GUE prediction:       <r> ≈ 0.6027")


if __name__ == "__main__":
    main()
