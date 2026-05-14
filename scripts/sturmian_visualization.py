"""Visualize the Sturmian structure of the sign pattern.

Overlays:
  (1) the empirical sgn(c_2 - c_1) at each dropping time k_o
  (2) the Sturmian gap sequence for slope log_2(3)
  (3) the "carry" condition {(o-1) log_2 3} ≥ 2 - log_2 3 ≈ 0.415

These all coincide, showing the sign pattern is the cutting sequence
of the line y = x log_2(3).
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    out_dir = Path(__file__).resolve().parents[1] / "data"
    log2_3 = math.log2(3.0)

    O_max = 30
    # Compute k_o and gaps
    k_list, gaps, signs_pred, frac_parts = [], [], [], []
    k_prev = 1
    for o in range(1, O_max + 1):
        k_o = o + math.floor(o * log2_3) + 1
        gap = k_o - k_prev
        k_list.append(k_o)
        gaps.append(gap)
        signs_pred.append(+1 if gap == 3 else -1)
        frac_parts.append((o * log2_3) % 1)  # the "phase" of the Beatty sequence at o
        k_prev = k_o
    k_arr = np.array(k_list)
    gap_arr = np.array(gaps)
    sign_arr = np.array(signs_pred)
    frac_arr = np.array(frac_parts)

    # Empirical signs from data (for k in our computed range)
    empirical = {
        3: -1, 6: +1, 8: 0, 11: +1, 13: -1, 16: +1, 19: +1,
        21: -1, 24: +1, 26: -1, 29: +1, 32: +1, 34: -1, 37: +1,
        39: -1, 42: +1, 44: -1, 47: +1, 50: +1, 52: -1, 55: +1,
        57: -1, 60: +1
    }

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    # Plot 1: predicted + empirical sign pattern
    ax = axes[0]
    ax.axhline(0, color="black", lw=0.5)
    # Predicted (filled circles)
    for k, s, g in zip(k_arr, sign_arr, gap_arr):
        color = "C2" if g == 3 else "C3"
        ax.scatter([k], [s], c=color, s=120, edgecolor="black", linewidth=0.5, zorder=2)
    # Empirical (open circles overlaid)
    for k, e in empirical.items():
        ax.scatter([k], [e], s=200, facecolor="none", edgecolor="black", linewidth=1.5, zorder=3)
    # Legend
    ax.scatter([], [], c="C2", s=120, edgecolor="black", linewidth=0.5, label="predicted +1 (gap=3)")
    ax.scatter([], [], c="C3", s=120, edgecolor="black", linewidth=0.5, label="predicted −1 (gap=2)")
    ax.scatter([], [], s=200, facecolor="none", edgecolor="black", linewidth=1.5, label="empirical")
    ax.set_ylabel("sgn(c_2 − c_1)")
    ax.set_title("Sturmian sign rule: empirical sgn(Δ) matches gap parity at k_o")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    ax.set_ylim(-1.7, 1.7)

    # Plot 2: gap sequence
    ax = axes[1]
    for o, (k, g) in enumerate(zip(k_arr, gap_arr), start=1):
        color = "C2" if g == 3 else "C3"
        ax.scatter([k], [g], c=color, s=80, edgecolor="black", linewidth=0.5)
    ax.set_ylabel("gap_o = k_o − k_{o−1}")
    ax.set_yticks([2, 3])
    ax.set_title("Gap sequence (Sturmian / Beatty cutting sequence of slope log₂3)")
    ax.grid(alpha=0.3)
    ax.set_ylim(1.5, 3.5)

    # Plot 3: fractional parts {(o-1) · log_2(3)} — the right quantity to threshold against
    ax = axes[2]
    threshold = 2 - log2_3  # ≈ 0.415
    frac_prev = [(o - 1) * log2_3 % 1 for o in range(1, O_max + 1)]
    for o, (k, f, g) in enumerate(zip(k_arr, frac_prev, gap_arr), start=1):
        color = "C2" if g == 3 else "C3"
        ax.scatter([k], [f], c=color, s=80, edgecolor="black", linewidth=0.5)
    ax.axhline(threshold, color="red", ls="--", lw=1,
               label=f"threshold = 2 − log₂3 ≈ {threshold:.3f}")
    ax.set_ylabel(r"$\{(o-1) \cdot \log_2 3\}$")
    ax.set_xlabel("k_o (dropping time)")
    ax.set_title(r"Beatty fractional part — green (gap=3, sign=+) above threshold; red (gap=2, sign=−) below")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_ylim(0, 1)

    fig.tight_layout()
    out_png = out_dir / "sturmian_sign_pattern.png"
    fig.savefig(out_png, dpi=120)
    print(f"Saved {out_png}")

    # Also print the predicted sequence for o up to 30
    print(f"\nPredicted (o, k_o, gap_o, sign):")
    for o, (k, g, s) in enumerate(zip(k_arr, gap_arr, sign_arr), start=1):
        emp = empirical.get(int(k), "?")
        match = "✓" if int(s) == emp else "(Δ=0)" if emp == 0 else "?" if emp == "?" else "✗"
        print(f"  o={o:>2d}  k={k:>3d}  gap={g}  predicted={int(s):+d}  empirical={emp}  {match}")


if __name__ == "__main__":
    main()
