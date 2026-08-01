"""Experiment 1: affine orbit-sum spectra — what it means to live in a dropping set.

Every subgroup alpha = (alpha_1..alpha_s) of Dropping Set D_k carries exact
affine invariants (collatz/affine.py):

    orbit sum  = A_alpha * n + B_alpha
    peak coeff P_alpha = max_j a_j        (orbit max ~ P_alpha * n)

log2 a_j traced along the orbit is the deficiency of the subgroup's lattice
path below the Beatty line y = x*log2(3).  Questions:

  Q1. How do log2 P and log2 A scale across the N(s) subgroups as s grows —
      like sqrt(s) (constrained-bridge fluctuation) or like s (bandwidth)?
  Q2. Is the relative wobble B/A (the +1's shift of the affine line) bounded?
  Q3. Does the aggregate mass M(N) = sum_{n<=N} orbitsum(n) converge to the
      lattice-predicted (kappa_M/2) * N^2?

Figures -> data/collatz_affine_slope_spectrum.png,
           data/collatz_affine_orbit_profiles.png,
           data/collatz_affine_mass_scaling.png
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from collatz.affine import profile_from_alphas, sieve_dropping, subgroup_summary
from collatz.lfunctions.lattice_paths import enumerate_subgroups, k_of

DATA = Path(__file__).resolve().parents[1] / "data"
S_MAX = 14
N_MAX = 10_000_000
LOG23 = math.log2(3)

# dataviz palette (light mode)
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
GRID = dict(color="0.88", linewidth=0.6)
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "0.9", "grid.linewidth": 0.6,
    "font.size": 10,
})


def collect_spectra(s_max: int) -> dict[int, dict]:
    """Per-s arrays of log2(A), log2(P), and B/A across all subgroups."""
    out = {}
    for s in range(1, s_max + 1):
        rows = [subgroup_summary(a) for a in enumerate_subgroups(s)]
        out[s] = {
            "log2A": np.array([math.log2(r["A"]) for r in rows]),
            "log2P": np.array([math.log2(r["P"]) for r in rows]),
            "wobble": np.array([float(r["B"] / r["A"]) for r in rows]),
            "A": [r["A"] for r in rows],
            "k": k_of(s),
        }
        print(f"  s={s:2d}  k={out[s]['k']:2d}  N(s)={len(rows):6d}  "
              f"mean log2P={out[s]['log2P'].mean():6.3f}  max={out[s]['log2P'].max():6.3f}  "
              f"max|B/A|={np.abs(out[s]['wobble']).max():8.3f}")
    return out


def fit_power(s_vals: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Fit y = c * s^gamma; returns (c, gamma)."""
    gamma, logc = np.polyfit(np.log(s_vals), np.log(y), 1)
    return math.exp(logc), gamma


def figure_slope_spectrum(spec: dict[int, dict]) -> None:
    s_vals = np.array(sorted(spec))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharex=True)
    for ax, key, label in [(axes[0], "log2P", r"$\log_2 P_\alpha$ (peak coefficient)"),
                           (axes[1], "log2A", r"$\log_2 A_\alpha$ (orbit-sum slope)")]:
        means = np.array([spec[s][key].mean() for s in s_vals])
        maxes = np.array([spec[s][key].max() for s in s_vals])
        for s in s_vals:
            y = spec[s][key]
            x = np.full_like(y, s) + np.random.default_rng(s).uniform(-0.22, 0.22, y.size)
            ax.plot(x, y, ".", color=BLUE, ms=2, alpha=0.12, rasterized=True)
        ax.plot(s_vals, means, "-", color=BLUE, lw=2)
        ax.plot(s_vals, maxes, "-", color=ORANGE, lw=2)
        ax.plot(s_vals, (LOG23 - 1) * s_vals + 1, "--", color="0.55", lw=1.2)
        c, gamma = fit_power(s_vals[2:], means[2:])
        ax.plot(s_vals, c * s_vals**gamma, ":", color=AQUA, lw=1.6)
        ax.text(s_vals[-1], maxes[-1], "  max (all-ones path)", color=ORANGE,
                va="center", fontsize=9)
        ax.text(s_vals[-1], means[-1], f"  mean ~ {c:.2f}·s^{gamma:.2f}", color=AQUA,
                va="top", fontsize=9)
        ax.text(s_vals[-1], (LOG23 - 1) * s_vals[-1] + 1.35, "bandwidth 0.585s+1",
                color="0.45", ha="right", fontsize=8)
        ax.set_xlabel("orbital oddity s")
        ax.set_title(label, fontsize=11)
    fig.suptitle("Slope spectra across the N(s) subgroups of each dropping set",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(DATA / "collatz_affine_slope_spectrum.png", dpi=160)
    plt.close(fig)


def figure_orbit_profiles(s_show: tuple[int, int] = (8, 12)) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=False)
    for ax, s in zip(axes, s_show):
        subs = enumerate_subgroups(s)
        for alphas in subs:
            prof = profile_from_alphas(alphas)
            y = [math.log2(a) for a, _ in prof]
            ax.plot(range(len(y)), y, "-", color=BLUE, lw=0.7,
                    alpha=min(1.0, 30 / len(subs)), rasterized=True)
        # the all-ones extremal path in orange
        kmax = k_of(s)
        ones = tuple([1] * (s - 1) + [kmax - s - (s - 1)]) if s > 1 else (2,)
        prof = profile_from_alphas(ones)
        ax.plot(range(len(prof)), [math.log2(a) for a, _ in prof], "-",
                color=ORANGE, lw=1.8)
        ax.axhline(0.0, color="0.55", lw=1.0, ls="--")
        ax.set_xlabel("step j")
        ax.set_title(f"s = {s}:  all {len(subs)} subgroup profiles", fontsize=11)
    axes[0].set_ylabel(r"$\log_2 a_j$  (orbit altitude relative to n)")
    fig.suptitle("Dropping-orbit profiles are subgroup invariants "
                 "(sawtooths below the Beatty line)", fontsize=12)
    fig.tight_layout()
    fig.savefig(DATA / "collatz_affine_orbit_profiles.png", dpi=160)
    plt.close(fig)


def kappa_mass_partial(spec: dict[int, dict]) -> list[tuple[int, float]]:
    """Partial sums of kappa_M = 1/2 + sum_s 2^-(k-s) * sum_alpha A_alpha."""
    total = 0.5  # even class: A = 1, modulus 2
    out = []
    for s in sorted(spec):
        k = spec[s]["k"]
        total += float(sum(spec[s]["A"])) * 2.0 ** -(k - s)
        out.append((s, total))
    return out


def figure_mass_scaling(spec: dict[int, dict]) -> None:
    print(f"sieving orbit sums to N = {N_MAX:,} ...")
    t0 = time.time()
    ktime, dest, osum = sieve_dropping(N_MAX)
    print(f"  sieve done in {time.time() - t0:.1f}s; max dropping time = {ktime.max()}")

    n_grid = np.unique(np.logspace(2, math.log10(N_MAX), 400).astype(np.int64))
    csum = np.cumsum(osum, dtype=np.float64)
    ratio = 2.0 * csum[n_grid] / n_grid.astype(np.float64) ** 2

    partials = kappa_mass_partial(spec)
    kappa_last = partials[-1][1]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    ax = axes[0]
    ax.semilogx(n_grid, ratio, "-", color=BLUE, lw=1.6)
    for s, val in partials[-4:]:
        ax.axhline(val, color=ORANGE, lw=0.9, alpha=0.5)
    ax.axhline(kappa_last, color=ORANGE, lw=1.4)
    ax.text(n_grid[2], kappa_last, f"lattice prediction κ_M (s≤{partials[-1][0]}) "
            f"= {kappa_last:.4f}", color=ORANGE, va="bottom", fontsize=9)
    ax.set_xlabel("N")
    ax.set_ylabel(r"$2\,M(N)/N^2$")
    ax.set_title("Aggregate orbit mass vs lattice prediction", fontsize=11)

    ax = axes[1]
    s_vals = np.array(sorted(spec))
    wmax = [np.abs(spec[s]["wobble"]).max() for s in s_vals]
    wmean = [np.abs(spec[s]["wobble"]).mean() for s in s_vals]
    ax.plot(s_vals, wmax, "-o", color=ORANGE, lw=1.6, ms=4)
    ax.plot(s_vals, wmean, "-o", color=BLUE, lw=1.6, ms=4)
    ax.text(s_vals[-1], wmax[-1], "  max |B/A|", color=ORANGE, va="center", fontsize=9)
    ax.text(s_vals[-1], wmean[-1], "  mean |B/A|", color=BLUE, va="center", fontsize=9)
    ax.set_xlabel("orbital oddity s")
    ax.set_ylabel("relative wobble |B/A|")
    ax.set_title("The +1 shifts the orbit-sum line by a bounded offset?", fontsize=11)
    fig.tight_layout()
    fig.savefig(DATA / "collatz_affine_mass_scaling.png", dpi=160)
    plt.close(fig)

    print("\nkappa_M partial sums:")
    for s, val in partials:
        print(f"  s<={s:2d}: {val:.6f}")
    print(f"empirical 2 M(N)/N^2 at N={N_MAX:,}: {ratio[-1]:.6f}")


def main() -> None:
    DATA.mkdir(exist_ok=True)
    print("enumerating subgroup spectra ...")
    spec = collect_spectra(S_MAX)

    s_vals = np.array(sorted(spec))
    for key in ("log2P", "log2A"):
        means = np.array([spec[s][key].mean() for s in s_vals])
        c, gamma = fit_power(s_vals[2:], means[2:])
        print(f"mean {key} ~ {c:.3f} * s^{gamma:.3f}")

    figure_slope_spectrum(spec)
    figure_orbit_profiles()
    figure_mass_scaling(spec)
    print("figures written to data/")


if __name__ == "__main__":
    main()
