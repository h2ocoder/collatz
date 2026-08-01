"""Experiment 2: the Collatz circle problem.

Count lattice points (n, dest(n)) inside the disk of radius r:

    C(r) = #{ n >= 2 : n^2 + dest(n)^2 <= r^2 }.

By the Affine Orbit Structure theorem the point set is a fan of lines
dest = lambda_s * n + C_c, one arithmetic progression (modulus 2^(k-s)) per
subgroup, so restricting to oddities s <= S:

    C_S(r) = kappa_S * r + beta_S + E_S(r),

    kappa_S = (1/2)(1 + 1/4)^(-1/2)
              + sum_s N(s) * 2^-(k-s) * (1 + lambda_s^2)^(-1/2),

with kappa_S exactly computable from the Lattice Path Formula.  E_S(r) is a
sum of centered sawtooths over the active progressions — the analog of the
Gauss circle error term.  We measure its growth exponent theta
(windowed max and std vs r on log-log axes) and compare against
theta = 1/2 (square-root cancellation, the Gauss-conjecture analog).

Figures -> data/collatz_gauss_circle_fan.png,
           data/collatz_gauss_circle_error.png
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from collatz.affine import sieve_dropping
from collatz.lfunctions.lattice_paths import enumerate_subgroups, k_of

DATA = Path(__file__).resolve().parents[1] / "data"
N_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000_000
S_MAX = 14  # levels k(s), s = 1..14, plus the even class k = 1

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "0.9", "grid.linewidth": 0.6,
    "font.size": 10,
})


def kappa_exact(s_max: int) -> tuple[float, float, list[tuple[int, float]]]:
    """(kappa_S, covered density, per-level [(k, contribution)])."""
    kappa = 0.5 / math.sqrt(1.25)  # even class: lambda = 1/2, density 1/2
    density = 0.5
    levels = [(1, kappa)]
    for s in range(1, s_max + 1):
        k = k_of(s)
        lam = 3.0**s / 2.0 ** (k - s)
        rho = len(enumerate_subgroups(s)) * 2.0 ** -(k - s)
        contrib = rho / math.sqrt(1.0 + lam * lam)
        kappa += contrib
        density += rho
        levels.append((k, contrib))
    return kappa, density, levels


def null_sawtooth_std(r: float, s_max: int) -> float:
    """Independent-phase sawtooth null for E(r).

    Each residue class (modulus m, slope lambda) contributes a centered
    sawtooth of variance 1/12 once its progression is dense below radius r
    (mu = expected points >= 1), and Bernoulli variance mu(1-mu) while sparse.
    """
    var = 0.0
    lam0 = 0.5
    mu = r / (2.0 * math.sqrt(1 + lam0 * lam0))
    var += 1.0 / 12.0 if mu >= 1 else mu * (1 - mu)
    for s in range(1, s_max + 1):
        k = k_of(s)
        m = 2.0 ** (k - s)
        lam = 3.0**s / 2.0 ** (k - s)
        mu = r / (m * math.sqrt(1 + lam * lam))
        per_class = 1.0 / 12.0 if mu >= 1 else mu * (1 - mu)
        var += len(enumerate_subgroups(s)) * per_class
    return math.sqrt(var)


def main() -> None:
    DATA.mkdir(exist_ok=True)
    kappa, density, levels = kappa_exact(S_MAX)
    k_levels = {k for k, _ in levels}
    print(f"exact kappa_S (s<={S_MAX}) = {kappa:.8f}, covered density = {density:.6f}")

    print(f"sieving to N = {N_MAX:,} ...")
    ktime, dest, _ = sieve_dropping(N_MAX)
    n = np.arange(N_MAX + 1, dtype=np.int64)
    keep = np.isin(ktime, list(k_levels)) & (n >= 2)
    npts, dpts = n[keep], dest[keep]
    radius = np.sqrt(npts.astype(np.float64) ** 2 + dpts.astype(np.float64) ** 2)
    order = np.argsort(radius)
    radius = radius[order]
    print(f"kept {radius.size:,} of {N_MAX - 1:,} points "
          f"({radius.size / (N_MAX - 1):.4f}, predicted {density:.4f})")

    # C(radius_i) = i + 1 exactly at the sorted radii; valid for r <= N_MAX
    valid = radius <= N_MAX
    radius = radius[valid]
    count = np.arange(1, radius.size + 1, dtype=np.float64)

    # empirical slope check + intercept fit on the upper half
    half = radius > radius[-1] / 2
    slope_fit = np.polyfit(radius[half], count[half], 1)
    beta = np.mean(count - kappa * radius)
    err = count - kappa * radius - beta
    print(f"fitted slope = {slope_fit[0]:.8f}  (exact kappa = {kappa:.8f}, "
          f"rel diff = {slope_fit[0] / kappa - 1:.2e})")
    print(f"fitted beta = {beta:.3f}")

    # windowed error statistics on dyadic windows
    edges = 2.0 ** np.arange(8, math.floor(math.log2(N_MAX)) + 1)
    win_mid, win_max, win_std = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (radius >= lo) & (radius < hi)
        if m.sum() < 100:
            continue
        e = err[m] - err[m].mean()  # local detrend: kill slow drift, keep sawtooth
        win_mid.append(math.sqrt(lo * hi))
        win_max.append(np.abs(e).max())
        win_std.append(e.std())
    win_mid, win_max, win_std = map(np.array, (win_mid, win_max, win_std))
    th_max = np.polyfit(np.log(win_mid), np.log(win_max), 1)[0]
    th_std = np.polyfit(np.log(win_mid), np.log(win_std), 1)[0]
    print(f"error growth exponents: theta(max) = {th_max:.3f}, "
          f"theta(std) = {th_std:.3f}   [Gauss-conjecture analog: 0.5]")

    null_std = np.array([null_sawtooth_std(r, S_MAX) for r in win_mid])
    rigidity = null_std / win_std
    print(f"independent-sawtooth null std at top window: {null_std[-1]:.1f} "
          f"vs observed {win_std[-1]:.1f}  (rigidity factor {rigidity[-1]:.2f})")

    # ---- figure 1: the fan ---------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    sub = np.random.default_rng(1).choice(npts.size, size=60_000, replace=False)
    ax.plot(npts[sub], dpts[sub], ".", ms=1.0, color=BLUE, alpha=0.25,
            rasterized=True)
    r_arc = 0.9 * npts[sub].max()
    th = np.linspace(0, math.pi / 4, 200)
    ax.plot(r_arc * np.cos(th), r_arc * np.sin(th), "-", color=ORANGE, lw=1.8)
    ax.plot([0, npts[sub].max()], [0, npts[sub].max() / 2], "--", color="0.6", lw=1)
    ax.plot([0, npts[sub].max()], [0, npts[sub].max()], "--", color="0.6", lw=1)
    ax.text(0.62 * r_arc, 0.62 * r_arc, "d = n", color="0.45", fontsize=9,
            rotation=45, rotation_mode="anchor")
    ax.text(0.86 * npts[sub].max(), 0.45 * npts[sub].max(), "d = n/2",
            color="0.45", fontsize=9)
    ax.text(r_arc * 0.72, r_arc * 0.28, "C(r): points inside the arc",
            color=ORANGE, fontsize=9)
    ax.set_xlabel("n (orbit start)")
    ax.set_ylabel("dest(n) (orbit end)")
    ax.set_title("The Collatz fan: (n, dest) lies on affine lines between "
                 "d = n/2 and d = n", fontsize=11)
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(DATA / "collatz_gauss_circle_fan.png", dpi=160)
    plt.close(fig)

    # ---- figure 2: error term ------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    ax = axes[0]
    step = max(1, radius.size // 400_000)
    ax.plot(radius[::step], err[::step], "-", color=BLUE, lw=0.5, alpha=0.8,
            rasterized=True)
    ax.axhline(0, color="0.55", lw=1)
    ax.set_xlabel("r")
    ax.set_ylabel(r"$E(r) = C_S(r) - \kappa_S r - \beta$")
    ax.set_title(f"Collatz circle error term  (exact κ_S = {kappa:.6f})",
                 fontsize=11)

    ax = axes[1]
    ax.loglog(win_mid, win_max, "o-", color=ORANGE, lw=1.4, ms=4)
    ax.loglog(win_mid, win_std, "o-", color=BLUE, lw=1.4, ms=4)
    ax.loglog(win_mid, null_std, "-", color=AQUA, lw=1.6)
    ref = win_std[len(win_std) // 2] * (win_mid / win_mid[len(win_std) // 2]) ** 0.5
    ax.loglog(win_mid, ref, "--", color="0.55", lw=1.2)
    ax.text(win_mid[-1], win_max[-1], f"  max, θ={th_max:.2f}", color=ORANGE,
            fontsize=9, va="center")
    ax.text(win_mid[-1], win_std[-1], f"  std, θ={th_std:.2f}", color=BLUE,
            fontsize=9, va="center")
    ax.text(win_mid[-1], null_std[-1], "  independent-sawtooth null", color=AQUA,
            fontsize=9, va="center")
    ax.text(win_mid[-1], ref[-1], r"  $r^{1/2}$", color="0.45", fontsize=9,
            va="center")
    ax.set_xlabel("r (dyadic window midpoint)")
    ax.set_ylabel("windowed |E|")
    ax.set_title("Error growth vs the square-root-cancellation line",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(DATA / "collatz_gauss_circle_error.png", dpi=160)
    plt.close(fig)

    print("figures written to data/")


if __name__ == "__main__":
    main()
