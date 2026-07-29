"""Experiment 3: where does the Collatz circle rigidity come from?

The circle-count error E(r) decomposes exactly into per-class sawtooths:
class (residue r0, modulus m = 2^(k-s), slope lambda, intercept C) contributes
count = floor((X(r) - r0)/m) + 1 with X(r) = (-lam*C + sqrt((1+lam^2)r^2 - C^2))
/(1+lam^2).  The class's phase on its own sawtooth wheel is

    phi = frac( (r0 + lam*C/(1+lam^2)) / m ).

Experiment: (a) verify the sawtooth model reproduces the sieved E(r) trace;
(b) shuffle the phases (uniform random r0) and show the fluctuation returns
to the independent null — isolating phase structure as the cause of the
rigidity; (c) measure per-level pair-correlation energy via the form factor

    V_s / (N_s/12),   V_s = sum_h |F_s(h)|^2 / (2 pi^2 h^2),
    F_s(h) = sum_i e(h phi_i),

which is the asymptotic (dense-regime) variance ratio vs independent phases.

Figures -> data/collatz_residue_rigidity.png,
           data/collatz_residue_form_factor.png
"""
from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from collatz.affine import residue_from_alphas, sieve_dropping, subgroup_summary
from collatz.lfunctions.lattice_paths import enumerate_subgroups, k_of

DATA = Path(__file__).resolve().parents[1] / "data"
N_MAX = 10_000_000
S_MAX = 14
N_SHUFFLE = 6
GRID_PER_WINDOW = 512
H_MAX = 4096

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "0.9", "grid.linewidth": 0.6,
    "font.size": 10,
})


def build_levels() -> list[dict]:
    """Per level: modulus m, slope lam, arrays of residues r0 and intercepts C."""
    levels = [{"s": 0, "k": 1, "m": 2.0, "lam": 0.5,
               "r0": np.array([0.0]), "C": np.array([0.0])}]
    for s in range(1, S_MAX + 1):
        k = k_of(s)
        m = 2.0 ** (k - s)
        lam = 3.0**s / 2.0 ** (k - s)
        r0, C = [], []
        for alphas in enumerate_subgroups(s):
            r0.append(float(residue_from_alphas(alphas)))
            C.append(float(subgroup_summary(alphas)["C"]))
        levels.append({"s": s, "k": k, "m": m, "lam": lam,
                       "r0": np.array(r0), "C": np.array(C)})
    return levels


def model_counts(levels: list[dict], r_grid: np.ndarray,
                 rng: np.random.Generator | None = None) -> np.ndarray:
    """Exact fan count at each grid radius; rng != None shuffles class phases."""
    total = np.zeros(r_grid.size)
    for lev in levels:
        m, lam = lev["m"], lev["lam"]
        r0 = lev["r0"] if rng is None else rng.uniform(0, m, lev["r0"].size)
        C = lev["C"]
        one = 1.0 + lam * lam
        # X per class per grid point (chunk classes to bound memory)
        for lo in range(0, r0.size, 4096):
            r0c, Cc = r0[lo:lo + 4096, None], C[lo:lo + 4096, None]
            disc = one * r_grid[None, :] ** 2 - Cc**2
            X = (-lam * Cc + np.sqrt(np.maximum(disc, 0.0))) / one
            cnt = np.floor((X - r0c) / m) + 1.0
            # progression starts at n = r0 (n >= 2 handled below for r0 <= 1)
            np.maximum(cnt, 0.0, out=cnt)
            if rng is None:
                # drop n = 0 (even class) and n = 1 (class r0 = 1)
                drop = (r0c <= 1.0) & (X >= r0c)
                cnt -= drop
            total += cnt.sum(axis=0)
    return total


def windowed_std(r: np.ndarray, e: np.ndarray, edges: np.ndarray):
    mid, std = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        msk = (r >= lo) & (r < hi)
        if msk.sum() < 32:
            continue
        mid.append(math.sqrt(lo * hi))
        std.append((e[msk] - e[msk].mean()).std())
    return np.array(mid), np.array(std)


def form_factor_ratio(lev: dict) -> tuple[float, np.ndarray]:
    """(V_s/(N_s/12), |F(h)|^2/N_s for h=1..H_MAX) from the class phases."""
    m, lam = lev["m"], lev["lam"]
    phi = np.mod((lev["r0"] + lam * lev["C"] / (1 + lam * lam)) / m, 1.0)
    h = np.arange(1, H_MAX + 1)
    F2 = np.abs(np.exp(2j * math.pi * np.outer(h, phi)).sum(axis=1)) ** 2
    V = (F2 / (2 * math.pi**2 * h**2)).sum()
    n = phi.size
    # tail h > H_MAX at the null level N/(2 pi^2 h^2)
    V += n / (2 * math.pi**2) * (1.0 / H_MAX)
    return V / (n / 12.0), F2 / n


def main() -> None:
    DATA.mkdir(exist_ok=True)
    print("building class table (residues + intercepts) ...")
    levels = build_levels()
    n_classes = sum(lev["r0"].size for lev in levels)
    print(f"  {n_classes} classes across levels s = 0..{S_MAX}")

    # ---- data trace ----------------------------------------------------------
    print(f"sieving to N = {N_MAX:,} ...")
    ktime, dest, _ = sieve_dropping(N_MAX)
    n = np.arange(N_MAX + 1, dtype=np.int64)
    k_levels = [lev["k"] for lev in levels]
    keep = np.isin(ktime, k_levels) & (n >= 2)
    radius = np.sqrt(n[keep].astype(float) ** 2 + dest[keep].astype(float) ** 2)
    radius.sort()
    radius = radius[radius <= N_MAX]

    edges = 2.0 ** np.arange(8, math.floor(math.log2(N_MAX)) + 1)
    r_grid = np.concatenate([
        np.linspace(lo, hi, GRID_PER_WINDOW, endpoint=False)
        for lo, hi in zip(edges[:-1], edges[1:])])

    kappa = np.searchsorted(radius, N_MAX * 0.99) / (N_MAX * 0.99)
    data_cnt = np.searchsorted(radius, r_grid, side="right")
    e_data = data_cnt - kappa * r_grid
    e_data -= e_data.mean()

    # ---- model trace + shuffled nulls ---------------------------------------
    print("evaluating exact sawtooth model on the grid ...")
    model_cnt = model_counts(levels, r_grid)
    e_model = model_cnt - kappa * r_grid
    e_model -= e_model.mean()
    resid = data_cnt - model_cnt
    print(f"  model vs data count: max |diff| = {np.abs(resid).max():.0f}, "
          f"final diff = {resid[-1]:.0f}  (small-n class deviations)")

    mid_d, std_d = windowed_std(r_grid, e_data, edges)
    mid_m, std_m = windowed_std(r_grid, e_model, edges)
    shuf = []
    for i in range(N_SHUFFLE):
        rng = np.random.default_rng(100 + i)
        e_s = model_counts(levels, r_grid, rng=rng) - kappa * r_grid
        e_s -= e_s.mean()
        shuf.append(windowed_std(r_grid, e_s, edges)[1])
        print(f"  shuffle {i + 1}/{N_SHUFFLE} done")
    shuf = np.array(shuf)

    # ---- per-level pair-correlation energy -----------------------------------
    print("\nper-level dense-regime rigidity ratio V_s/(N_s/12):")
    ratios, ffs = {}, {}
    for lev in levels[1:]:
        ratio, ff = form_factor_ratio(lev)
        ratios[lev["s"]], ffs[lev["s"]] = ratio, ff
        print(f"  s={lev['s']:2d}  N={lev['r0'].size:6d}  ratio={ratio:7.3f}")

    # ---- figures -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    ax = axes[0]
    lo_band = shuf.min(axis=0)
    hi_band = shuf.max(axis=0)
    ax.fill_between(mid_m, lo_band, hi_band, color=AQUA, alpha=0.25, lw=0)
    ax.loglog(mid_m, shuf.mean(axis=0), "-", color=AQUA, lw=1.6)
    ax.loglog(mid_d, std_d, "o-", color=BLUE, lw=1.6, ms=4)
    ax.loglog(mid_m, std_m, "s--", color=ORANGE, lw=1.2, ms=4, alpha=0.85)
    ax.text(mid_m[-1], shuf.mean(axis=0)[-1], "  phase-shuffled fan", color=AQUA,
            fontsize=9, va="center")
    ax.text(mid_d[-1], std_d[-1], "  data", color=BLUE, fontsize=9, va="center")
    ax.text(mid_m[-1], std_m[-1] * 0.8, "  sawtooth model", color=ORANGE,
            fontsize=9, va="top")
    ax.set_xlabel("r (dyadic window midpoint)")
    ax.set_ylabel("windowed std of E(r)")
    ax.set_title("Rigidity is in the phases: shuffling them restores the null",
                 fontsize=11)

    ax = axes[1]
    s_vals = sorted(ratios)
    ax.axhline(1.0, color="0.55", lw=1.2, ls="--")
    ax.plot(s_vals, [ratios[s] for s in s_vals], "o-", color=BLUE, lw=1.6, ms=5)
    ax.text(s_vals[-1], 1.02, "independent phases", color="0.45", fontsize=8,
            ha="right", va="bottom")
    ax.set_xlabel("orbital oddity s")
    ax.set_ylabel(r"$V_s / (N_s/12)$")
    ax.set_title("Pair-correlation energy of dropping residues per level",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(DATA / "collatz_residue_rigidity.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    for s, color in [(10, AQUA), (12, BLUE), (14, ORANGE)]:
        ax.semilogy(np.arange(1, H_MAX + 1), ffs[s], "-", color=color, lw=0.7,
                    alpha=0.8, label=f"s = {s}  (N = {levels[s]['r0'].size})")
    ax.axhline(1.0, color="0.55", lw=1.2, ls="--")
    ax.legend(frameon=False, fontsize=9)
    ax.set_xlabel("harmonic h")
    ax.set_ylabel(r"$|F_s(h)|^2 / N_s$")
    ax.set_title("Form factor of subgroup phases (1 = Poissonian)", fontsize=11)
    fig.tight_layout()
    fig.savefig(DATA / "collatz_residue_form_factor.png", dpi=160)
    plt.close(fig)
    print("figures written to data/")


if __name__ == "__main__":
    main()
