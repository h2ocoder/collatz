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
from collatz.dropping import dropping_set, orbital_oddity  # noqa: E402
from collatz.residues import prime_sieve  # noqa: E402

# ----- Configuration ---------------------------------------------------
N = 10_000_000
GAPS = (2, 4, 6)
NULL_STRIDE = 5  # systematic subsample of odd integers for the null
OUT_DIR = Path(__file__).resolve().parent.parent / "data"
GAP_NAME = {2: "twins", 4: "cousins", 6: "sexy"}


# ----- Data pipeline ---------------------------------------------------
def generic_prime_marginal(primes: np.ndarray, k_cap: int = K_CAP) -> dict:
    """Dropping-set distribution over all single primes (the HL marginal)."""
    counts = Counter()
    for p in primes.tolist():
        counts[min(dropping_set(p), k_cap)] += 1
    return dict(counts)


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


def print_summary(gap, pairs, joint, null, generic):
    name = GAP_NAME[gap]
    slow = slow_member_marginal(joint)
    gen_density = density(generic)
    chi = chi_squared(slow, gen_density, sum(slow.values()))
    tv = total_variation(joint, null)
    print(f"\n=== g={gap} ({name}) — {len(pairs)} pairs ===")
    print(f"  chi^2 (slow marginal vs generic primes): {chi:.1f}")
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
    generic = generic_prime_marginal(primes)
    print(f"pi({N}) = {primes.size}")

    bundles = []
    for gap in GAPS:
        print(f"Computing g={gap} ({GAP_NAME[gap]})...")
        b = compute(gap)
        bundles.append(b)
        print_summary(gap, b["pairs"], b["joint"], b["null"], generic)

    # Figures (defined in Task 6)
    render_all(bundles, generic)


def render_all(bundles, generic):  # noqa: F811  (replaced in Task 6)
    print("[render_all stub — figures added in Task 6]")


if __name__ == "__main__":
    main()
