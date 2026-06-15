# scripts/prime_constellation_signatures.py
"""Prime constellation dropping signatures: observed pairs vs nulls.

For gaps g in {2, 4, 6} (twins, cousins, sexy primes) and primes p <= N:
classify each pair (p, p+g) by its joint Collatz dropping signature, and
compare to (a) the generic single-prime marginal and (b) the admissible-
integer coupling null.  Render five figures and print a per-gap summary.

Outputs (data/):
    collatz_constellation_coupling.png   forced-coupling skeleton (all gaps)
    collatz_constellation_joint.png      joint k_p x k_{p+g} heatmaps
    collatz_constellation_marginal.png   headline: marginal bars + joint ratio
    collatz_constellation_genus.png      3-adic odd-step (s) refinement
    collatz_constellation_phase.png      optional internal-space phase scatter
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from collatz.constellations import (  # noqa: E402
    K_CAP,
    coupling_null_counts,
    forced_coupling_table,
    joint_signature_counts,
    prime_pairs,
)
from collatz.dropping import orbital_oddity  # noqa: E402
from collatz.residues import prime_sieve  # noqa: E402

# ----- Configuration ---------------------------------------------------
N = 10_000_000
GAPS = (2, 4, 6)
NULL_STRIDE = 5  # systematic subsample of odd integers for the null
OUT_DIR = Path(__file__).resolve().parent.parent / "data"
GAP_NAME = {2: "twins", 4: "cousins", 6: "sexy"}


# ----- Data pipeline ---------------------------------------------------
def slow_member_marginal(joint: dict) -> dict:
    """Marginal over the SLOW member (the coordinate that is not dropping set 3).

    Falls back to the larger coordinate when neither is exactly 3 (cousins).
    """
    counts = Counter()
    for (kp, kq), c in joint.items():
        slow = kq if kp == 3 else (kp if kq == 3 else max(kp, kq))
        counts[slow] += c
    return dict(counts)


def odd_step_joint(pairs: np.ndarray, gap: int, coprime3: bool) -> dict:
    """Joint (s_p, s_{p+g}) histogram via orbital_oddity (the 3-adic layer)."""
    counts = Counter()
    for p in pairs.tolist():
        if coprime3 and (p % 3 == 0 or (p + gap) % 3 == 0):
            continue
        counts[(orbital_oddity(p), orbital_oddity(p + gap))] += 1
    return dict(counts)


def odd_step_null(n_max: int, gap: int, stride: int, coprime3: bool) -> dict:
    """Coupling null for the (s_p, s_{p+g}) odd-step histogram."""
    counts = Counter()
    step = 2 * stride
    n = 3
    while n <= n_max - gap:
        if not (coprime3 and (n % 3 == 0 or (n + gap) % 3 == 0)):
            counts[(orbital_oddity(n), orbital_oddity(n + gap))] += 1
        n += step
    return dict(counts)


def chi_squared(obs: dict, exp_density: dict, total_obs: int) -> float:
    """Chi-squared of observed marginal vs an expected density (normalized)."""
    chi = 0.0
    for k, d in exp_density.items():
        expected = d * total_obs
        if expected > 0:
            chi += (obs.get(k, 0) - expected) ** 2 / expected
    return chi


def total_variation(obs: dict, null: dict) -> float:
    """Total-variation distance between two histograms (normalized to densities)."""
    so, sn = sum(obs.values()) or 1, sum(null.values()) or 1
    keys = set(obs) | set(null)
    return 0.5 * sum(abs(obs.get(k, 0) / so - null.get(k, 0) / sn) for k in keys)


def density(hist: dict) -> dict:
    total = sum(hist.values()) or 1
    return {k: v / total for k, v in hist.items()}


def print_summary(gap, pairs, joint, null):
    name = GAP_NAME[gap]
    slow_obs = slow_member_marginal(joint)
    slow_null = slow_member_marginal(null)
    chi = chi_squared(slow_obs, density(slow_null), sum(slow_obs.values()))
    tv = total_variation(joint, null)
    print(f"\n=== g={gap} ({name}) — {len(pairs)} pairs ===")
    print(f"  chi^2 (slow marginal vs coupling-null slow): {chi:.1f}")
    print(f"  total-variation (joint vs coupling null): {tv:.4f}")
    obs_d, null_d = density(joint), density(null)
    devs = sorted(
        ((obs_d.get(k, 0) - null_d.get(k, 0), k) for k in set(obs_d) | set(null_d)),
        key=lambda t: abs(t[0]),
        reverse=True,
    )[:5]
    print("  top deviating joint cells (obs_density - null_density):")
    for d, k in devs:
        print(f"    {k}: {d:+.5f}")


def compute(gap):
    """All histograms for one gap. Returns a dict bundle."""
    pairs = prime_pairs(N, gap)
    joint = joint_signature_counts(pairs, gap)
    null = coupling_null_counts(N, gap, stride=NULL_STRIDE)
    coprime3 = gap % 3 == 0  # the g=6 3-adic cross-check
    return {
        "gap": gap,
        "pairs": pairs,
        "joint": joint,
        "null": null,
        "s_joint": odd_step_joint(pairs, gap, coprime3),
        "s_null": odd_step_null(N, gap, NULL_STRIDE, coprime3),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Sieving primes up to {N}...")
    primes = prime_sieve(N)
    print(f"pi({N}) = {primes.size}")

    bundles = []
    for gap in GAPS:
        print(f"Computing g={gap} ({GAP_NAME[gap]})...")
        b = compute(gap)
        bundles.append(b)
        print_summary(gap, b["pairs"], b["joint"], b["null"])

    render_all(bundles)


def _joint_grid(hist, k_cap=K_CAP):
    """Dense (k_cap+1) x (k_cap+1) array from a sparse joint histogram."""
    g = np.zeros((k_cap + 1, k_cap + 1), dtype=float)
    for (kp, kq), c in hist.items():
        g[min(kp, k_cap), min(kq, k_cap)] = c
    return g


def fig_coupling(out_path):
    """Forced-coupling skeleton: mod-8 residue map per gap, fast/slow tagged."""
    fig, axes = plt.subplots(1, len(GAPS), figsize=(15, 4))
    for ax, gap in zip(axes, GAPS):
        rows = forced_coupling_table(gap, 8)
        grid = np.zeros((len(rows), 2))
        labels = []
        for i, (a, b, fa, fb) in enumerate(rows):
            grid[i] = [1.0 if fa else 0.2, 1.0 if fb else 0.2]
            labels.append(f"{a}|{b}")
        ax.imshow(grid, aspect="auto", cmap="coolwarm", vmin=0, vmax=1)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["p", f"p+{gap}"])
        ax.set_title(f"g={gap} ({GAP_NAME[gap]})\nred=fast (D3), blue=slow")
        ax.set_ylabel("odd residue a | (a+g) mod 8")
    fig.suptitle("Gap-forced 2-adic coupling (theorem, not data)")
    plt.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def fig_joint(bundles, out_path):
    """Observed joint k_p x k_{p+g} heatmap per gap (log counts)."""
    fig, axes = plt.subplots(1, len(bundles), figsize=(16, 5))
    for ax, b in zip(axes, bundles):
        grid = _joint_grid(b["joint"])
        im = ax.imshow(
            np.log10(grid + 1), origin="lower", cmap="viridis", aspect="auto"
        )
        ax.set_xlabel("$k_{p+g}$")
        ax.set_ylabel("$k_p$")
        ax.set_title(f"g={b['gap']} ({GAP_NAME[b['gap']]}) — log10(count+1)")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle("Observed joint dropping signatures of prime pairs")
    plt.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def fig_marginal(bundles, out_path):
    """Headline: slow-member marginal (observed vs coupling-null slow) + joint ratio."""
    fig, axes = plt.subplots(2, len(bundles), figsize=(16, 9))
    for j, b in enumerate(bundles):
        slow_obs = density(slow_member_marginal(b["joint"]))
        slow_null = density(slow_member_marginal(b["null"]))
        ks = sorted(set(slow_obs) | set(slow_null))
        ax = axes[0, j]
        x = np.arange(len(ks))
        w = 0.4
        ax.bar(x - w / 2, [slow_null.get(k, 0) for k in ks], w,
               label="coupling null (HL)", color="0.7")
        ax.bar(x + w / 2, [slow_obs.get(k, 0) for k in ks], w,
               label="observed slow", color="mediumseagreen")
        ax.set_xticks(x)
        ax.set_xticklabels(ks, fontsize=7)
        ax.set_xlabel("dropping set k (slow member)")
        ax.set_title(f"g={b['gap']} ({GAP_NAME[b['gap']]}) — slow marginal vs null")
        ax.legend(fontsize=8)

        obs_d = _joint_grid(density(b["joint"]))
        null_d = _joint_grid(density(b["null"]))
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(null_d > 0, obs_d / null_d, np.nan)
        ax2 = axes[1, j]
        im = ax2.imshow(ratio, origin="lower", cmap="RdBu_r", vmin=0, vmax=2,
                        aspect="auto")
        ax2.set_xlabel("$k_{p+g}$")
        ax2.set_ylabel("$k_p$")
        ax2.set_title("observed / coupling-null (joint)")
        fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    fig.suptitle("Constellation signatures: slow marginal HL test (top) + joint correlation (bottom)")
    plt.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def fig_genus(bundles, out_path):
    """3-adic odd-step (s) refinement: observed/null ratio per gap, g=6 cross-check."""
    fig, axes = plt.subplots(1, len(bundles), figsize=(16, 5))
    smax = 0
    for b in bundles:
        for (sp, sq) in list(b["s_joint"]) + list(b["s_null"]):
            smax = max(smax, sp, sq)
    smax = min(smax, 20)
    for ax, b in zip(axes, bundles):
        obs = np.zeros((smax + 1, smax + 1))
        nul = np.zeros((smax + 1, smax + 1))
        for (sp, sq), c in b["s_joint"].items():
            if sp <= smax and sq <= smax:
                obs[sp, sq] = c
        for (sp, sq), c in b["s_null"].items():
            if sp <= smax and sq <= smax:
                nul[sp, sq] = c
        od, nd = obs / (obs.sum() or 1), nul / (nul.sum() or 1)
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(nd > 0, od / nd, np.nan)
        im = ax.imshow(ratio, origin="lower", cmap="PuOr_r", vmin=0, vmax=2,
                       aspect="auto")
        tag = " (3-adic coupled)" if b["gap"] % 3 == 0 else ""
        ax.set_xlabel("$s_{p+g}$ (odd steps)")
        ax.set_ylabel("$s_p$")
        ax.set_title(f"g={b['gap']} ({GAP_NAME[b['gap']]}){tag}")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle("Odd-step (3-adic) signature: observed / null — watch g=6 vs g=2,4")
    plt.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def render_all(bundles):
    fig_coupling(OUT_DIR / "collatz_constellation_coupling.png")
    fig_joint(bundles, OUT_DIR / "collatz_constellation_joint.png")
    fig_marginal(bundles, OUT_DIR / "collatz_constellation_marginal.png")
    fig_genus(bundles, OUT_DIR / "collatz_constellation_genus.png")
    print("Figures written to", OUT_DIR)


if __name__ == "__main__":
    main()
