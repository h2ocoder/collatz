"""Experiment 4: scaling and anatomy of dropping-residue hyperuniformity.

Extends Experiment 3 (collatz_residue_rigidity.py) to s = 16 (108,950
subgroups) and dissects the mechanism:

  Q1. Does the low-harmonic suppression persist as N grows, and how does the
      star discrepancy scale (digital-net polylog vs random sqrt(N))?
  Q2. Where does the cancellation live?  Group subgroups by trailing alpha
      (which controls the top bits of the residue): measure within-group
      phase sums |sum e(2 pi i phi)| / sqrt(n_g) against the Rayleigh
      expectation ~0.89 for random phases.
  Q3. What are the anomalous levels doing?  Per-harmonic fingerprints S(h)
      for h = 1..8 at every level.

Figures -> data/collatz_hyperuniformity_scaling.png
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from collatz.affine import residue_from_alphas, subgroup_summary
from collatz.lfunctions.lattice_paths import enumerate_subgroups, k_of

DATA = Path(__file__).resolve().parents[1] / "data"
S_RANGE = range(8, 17)

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "0.9", "grid.linewidth": 0.6,
    "font.size": 10,
})


def level_phases(s: int) -> tuple[np.ndarray, np.ndarray]:
    """(phases, trailing alphas) for every subgroup of oddity s."""
    k = k_of(s)
    m = 2.0 ** (k - s)
    lam = 3.0**s / 2.0 ** (k - s)
    shift = lam / (1 + lam * lam)
    phi, alast = [], []
    for a in enumerate_subgroups(s):
        r0 = residue_from_alphas(a)
        c = float(subgroup_summary(a)["C"])
        phi.append(((r0 + shift * c) / m) % 1.0)
        alast.append(a[-1])
    return np.array(phi), np.array(alast)


def main() -> None:
    DATA.mkdir(exist_ok=True)
    rows = []
    for s in S_RANGE:
        phi, alast = level_phases(s)
        n = phi.size
        h = np.arange(1, 65)
        F = np.exp(2j * math.pi * np.outer(h, phi)).sum(axis=1)
        S = np.abs(F) ** 2 / n
        ps = np.sort(phi)
        i = np.arange(1, n + 1)
        dstar = max(np.max(i / n - ps), np.max(ps - (i - 1) / n))
        # within-group Rayleigh ratio for the largest trailing-alpha group
        big = alast == alast.min()
        g = np.exp(2j * math.pi * phi[big])
        ray = np.abs(g.sum()) / math.sqrt(big.sum())
        rows.append({"s": s, "n": n, "S14": S[:4].mean(), "S8": S[:8],
                     "ndstar": n * dstar, "ray_big": ray,
                     "frac": (s * math.log2(3)) % 1.0})
        print(f"s={s:2d} N={n:6d}  S(1-4)={S[:4].mean():6.3f}  "
              f"N*D*={n * dstar:7.1f} (rand {math.sqrt(n):6.1f})  "
              f"biggest-group |sum|/sqrt(n)={ray:5.2f} (rand 0.89)  "
              f"frac(s log2 3)={rows[-1]['frac']:.3f}")

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2))
    s_vals = np.array([r["s"] for r in rows])
    n_vals = np.array([r["n"] for r in rows])

    ax = axes[0]
    ax.semilogy(s_vals, [r["S14"] for r in rows], "o-", color=BLUE, lw=1.6, ms=5)
    ax.axhline(1.0, color="0.55", lw=1.2, ls="--")
    for r in rows:
        if r["S14"] > 1:
            ax.annotate(f"s={r['s']}", (r["s"], r["S14"]), textcoords="offset points",
                        xytext=(0, 6), ha="center", fontsize=9, color=ORANGE)
    ax.set_xlabel("orbital oddity s")
    ax.set_ylabel("S(h) averaged over h = 1..4")
    ax.set_title("Low-harmonic structure factor (1 = Poisson)", fontsize=11)

    ax = axes[1]
    ax.loglog(n_vals, [r["ndstar"] for r in rows], "o-", color=BLUE, lw=1.6, ms=5)
    ax.loglog(n_vals, np.sqrt(n_vals), "--", color="0.55", lw=1.2)
    ax.loglog(n_vals, np.log(n_vals), ":", color="0.55", lw=1.2)
    ax.text(n_vals[-1], math.sqrt(n_vals[-1]), r"  $\sqrt{N}$ (random)",
            fontsize=9, color="0.45", va="center")
    ax.text(n_vals[-1], math.log(n_vals[-1]), r"  $\log N$ (digital net)",
            fontsize=9, color="0.45", va="center")
    ax.set_xlabel("N (subgroups per level)")
    ax.set_ylabel(r"$N \cdot D^*_N$")
    ax.set_title("Star discrepancy: sub-random, not polylog", fontsize=11)

    ax = axes[2]
    im_data = np.array([r["S8"] for r in rows]).T
    im = ax.imshow(np.log10(np.maximum(im_data, 1e-3)), aspect="auto", origin="lower",
                   cmap="RdBu_r", vmin=-2, vmax=2,
                   extent=(s_vals[0] - 0.5, s_vals[-1] + 0.5, 0.5, 8.5))
    ax.set_xlabel("orbital oddity s")
    ax.set_ylabel("harmonic h")
    ax.set_title("log10 S(h): anomalies are isolated modes", fontsize=11)
    fig.colorbar(im, ax=ax, shrink=0.9)
    fig.tight_layout()
    fig.savefig(DATA / "collatz_hyperuniformity_scaling.png", dpi=160)
    plt.close(fig)
    print("figure written to data/collatz_hyperuniformity_scaling.png")


if __name__ == "__main__":
    main()
