"""Prime distribution across Collatz Dropping Sets: observed vs Dirichlet null.

For primes p <= N (default 1e7), classify each by its Dropping Set k and
its residue p mod 2^k.  Compare counts to the Dirichlet null model
(equidistribution of primes across odd residues mod 2^k).  Render:

  1. Arithmetic-form table: which residues r mod 2^k populate D_k.
  2. Observed vs Dirichlet bar chart per D_k, with chi-squared annotation.
  3. Per-residue heatmap inside D_k for k in {3, 6, 8, 11, 13}.

Outputs:
    data/collatz_prime_dropping_residues_form.png
    data/collatz_prime_dropping_observed_vs_dirichlet.png
    data/collatz_prime_dropping_residue_heatmap.png
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np

from collatz.dropping import dropping_set
from collatz.residues import (
    coprime_residues,
    dirichlet_prediction,
    dropping_set_residue_table,
    dropping_set_residues,
    prime_sieve,
)


# ----- Configuration ---------------------------------------------------

N = 10_000_000  # prime ceiling
K_MAX = 15  # maximum dropping set considered
HEATMAP_KS = (3, 6, 8, 11, 13)  # populated dropping sets within K_MAX
OUT_DIR = Path(__file__).resolve().parent.parent / "data"


# ----- Step 1: sieve and classify --------------------------------------


def sieve_and_classify(n_max: int):
    """Sieve primes <= n_max, classify into (k, r) buckets.

    Returns:
      primes: 1-D int64 array of primes <= n_max
      counts_by_k: dict k -> int  (number of primes with dropping_set = k)
      counts_by_k_r: dict k -> Counter mapping residue r -> count
      small_primes: list of primes p with p < 2**k(p), tracked separately
    """
    primes = prime_sieve(n_max)
    counts_by_k = Counter()
    counts_by_k_r = defaultdict(Counter)
    small_primes = []
    for p in primes.tolist():
        k = dropping_set(p)
        counts_by_k[k] += 1
        r = p % (1 << k)
        counts_by_k_r[k][r] += 1
        if p < (1 << k):
            small_primes.append(p)
    return primes, counts_by_k, counts_by_k_r, small_primes


# ----- Step 2: arithmetic-form figure ----------------------------------


def plot_residue_form(residue_table, out_path):
    """Heatmap: rows = k (1..K_max), columns = r (0..1023 for visibility).

    Cells light up when r in R_k.  Side annotations: |R_k|, |R_k ∩ odd|.
    """
    k_max = max(residue_table.keys())
    n_cols = min(1024, 1 << k_max)
    grid = np.zeros((k_max, n_cols), dtype=float)
    for k, R in residue_table.items():
        M = 1 << k
        for r in R:
            # Project to first n_cols columns by folding mod n_cols
            if r < n_cols:
                grid[k - 1, r] = 1.0
            else:
                grid[k - 1, r % n_cols] = max(grid[k - 1, r % n_cols], 0.5)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.imshow(grid, aspect="auto", cmap="viridis", interpolation="nearest")
    ax.set_xlabel(f"Residue r (mod $2^{{{k_max}}}$, folded to first {n_cols} columns)")
    ax.set_ylabel("Dropping Set k")
    ax.set_yticks(range(k_max))
    ax.set_yticklabels(range(1, k_max + 1))
    ax.set_title(f"Arithmetic Form of Dropping Sets: residues r mod $2^k$ that populate $D_k$")

    # Side-text with sizes
    for i, k in enumerate(range(1, k_max + 1)):
        R = residue_table[k]
        coprime = coprime_residues(k)
        ax.text(
            n_cols + 5,
            i,
            f"|R|={len(R)}, |odd|={len(coprime)}",
            fontsize=8,
            va="center",
        )
    plt.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


# ----- Step 3: observed-vs-Dirichlet figure ----------------------------


def chi_squared(observed: float, expected: float) -> float:
    """One-cell chi-squared contribution; returns 0 when expected is 0."""
    if expected == 0:
        return 0.0
    return (observed - expected) ** 2 / expected


def plot_observed_vs_dirichlet(counts_by_k, prime_count, k_max, out_path):
    """Grouped bars: predicted (gray) vs observed (color) per k.

    Annotate each bar pair with log10(observed / predicted).
    """
    ks = list(range(1, k_max + 1))
    predicted = [dirichlet_prediction(k, prime_count) for k in ks]
    observed = [counts_by_k.get(k, 0) for k in ks]

    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(ks))
    width = 0.4
    ax.bar(x - width / 2, predicted, width, label="Dirichlet null", color="0.7")
    ax.bar(x + width / 2, observed, width, label="Observed", color="mediumseagreen")
    ax.set_yscale("symlog", linthresh=1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(ks)
    ax.set_xlabel("Dropping Set k")
    ax.set_ylabel("Prime count (symlog)")
    ax.set_title(
        f"Primes per Dropping Set vs Dirichlet null (N = {prime_count} = pi({N}))"
    )

    # Annotate log-ratio above each observed bar
    for xi, p, o in zip(x, predicted, observed):
        if p > 0 and o > 0:
            ratio = np.log10(o / p)
            ax.text(
                xi + width / 2,
                o * 1.15 + 1,
                f"{ratio:+.2f}",
                ha="center",
                fontsize=8,
            )

    # Chi-squared total in the legend area
    chi2_total = sum(chi_squared(o, p) for o, p in zip(observed, predicted))
    ax.text(
        0.02,
        0.95,
        f"$\\chi^2$ total = {chi2_total:.1f}",
        transform=ax.transAxes,
        fontsize=10,
        va="top",
    )
    ax.legend(loc="upper right")
    plt.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


# ----- Step 4: per-residue heatmap -------------------------------------


def plot_residue_heatmap(counts_by_k_r, prime_count, ks, out_path):
    """One row per k in `ks`; cells = one per odd residue in R_k, colored by count.

    Color scale: counts normalized by (predicted per residue) so a value of
    1.0 means "matches Dirichlet exactly".  Values > 1 are over-represented;
    < 1 under-represented.
    """
    fig, axes = plt.subplots(len(ks), 1, figsize=(14, 2 * len(ks)))
    if len(ks) == 1:
        axes = [axes]

    for ax, k in zip(axes, ks):
        R_odd = sorted(coprime_residues(k))
        if not R_odd:
            ax.text(0.5, 0.5, f"R_{k} ∩ odd is empty", transform=ax.transAxes, ha="center")
            ax.set_axis_off()
            continue
        expected_per = dirichlet_prediction(k, prime_count) / len(R_odd) if R_odd else 0.0
        observed = np.array([counts_by_k_r.get(k, {}).get(r, 0) for r in R_odd])
        ratio = observed / expected_per if expected_per > 0 else observed.astype(float)

        im = ax.imshow(
            ratio.reshape(1, -1),
            aspect="auto",
            cmap="RdBu_r",
            vmin=0.0,
            vmax=2.0,
            interpolation="nearest",
        )
        ax.set_yticks([])
        ax.set_xticks(np.linspace(0, len(R_odd) - 1, min(8, len(R_odd))).astype(int))
        ax.set_xticklabels(
            [str(R_odd[i]) for i in np.linspace(0, len(R_odd) - 1, min(8, len(R_odd))).astype(int)],
            fontsize=8,
        )
        ax.set_xlabel(f"odd residue r mod $2^{{{k}}}$ (in $R_{{{k}}}$, |·|={len(R_odd)})")
        ax.set_title(f"k = {k} — observed / Dirichlet per residue")
        fig.colorbar(im, ax=ax, fraction=0.02, pad=0.01)

    fig.suptitle(
        "Per-residue prime counts inside each Dropping Set, normalized by Dirichlet null"
    )
    plt.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


# ----- Step 5: summary printer -----------------------------------------


def print_summary(counts_by_k, prime_count, k_max, small_primes):
    print(f"\nTotal primes <= {N}: {prime_count}")
    print(f"Small primes (p < 2**k(p)): {len(small_primes)}\n")
    print(f"{'k':>3} {'|R_k|':>6} {'|odd|':>6} {'predicted':>12} {'observed':>10} {'log10 obs/pred':>15} {'chi2':>10}")
    for k in range(1, k_max + 1):
        predicted = dirichlet_prediction(k, prime_count)
        observed = counts_by_k.get(k, 0)
        R = dropping_set_residues(k)
        odd = coprime_residues(k)
        ratio = np.log10(observed / predicted) if (predicted > 0 and observed > 0) else float("nan")
        chi2 = chi_squared(observed, predicted)
        print(f"{k:>3} {len(R):>6} {len(odd):>6} {predicted:>12.1f} {observed:>10d} {ratio:>15.3f} {chi2:>10.1f}")


# ----- Main ------------------------------------------------------------


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Building residue table for k=1..{K_MAX}...")
    residue_table = dropping_set_residue_table(K_MAX)
    print(f"Sieving primes up to {N}...")
    primes, counts_by_k, counts_by_k_r, small_primes = sieve_and_classify(N)
    prime_count = int(primes.size)

    print(f"Rendering arithmetic-form figure...")
    plot_residue_form(
        residue_table, OUT_DIR / "collatz_prime_dropping_residues_form.png"
    )
    print(f"Rendering observed-vs-Dirichlet figure...")
    plot_observed_vs_dirichlet(
        counts_by_k,
        prime_count,
        K_MAX,
        OUT_DIR / "collatz_prime_dropping_observed_vs_dirichlet.png",
    )
    print(f"Rendering per-residue heatmap...")
    plot_residue_heatmap(
        counts_by_k_r,
        prime_count,
        HEATMAP_KS,
        OUT_DIR / "collatz_prime_dropping_residue_heatmap.png",
    )

    print_summary(counts_by_k, prime_count, k_max=K_MAX, small_primes=small_primes)


if __name__ == "__main__":
    main()
