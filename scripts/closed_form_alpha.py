"""Closed-form prediction for α_k = |D_chi_6^(k)| / count_nz_k.

Theory: within each Dset_k, the joint (n mod 3, dest mod 3) distribution
determines the orbit-pair sum exactly. Specifically:
  - For each residue r in R_k (mod 2^k), dest mod 3 is a constant d_r.
  - As n varies over its residue class, n mod 3 equidistributes over {0, 1, 2}.
  - The orbit-pair lift's character value is chi_6(n + dest*omega) which
    only depends on (n mod 3, dest mod 3).
  - Therefore D_chi^(k)(N) is exactly determined by the distribution of d_r
    across R_k.

This script:
  1. Enumerates R_k for k in target list.
  2. For each r in R_k, computes d_r = dest(r) mod 3 (via Collatz simulation
     with the standard large-lift representative).
  3. Predicts |sum_k| and alpha_k.
  4. Compares to the empirical Phase 1.5 results.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from collatz.core import collatz_step  # noqa: E402
from collatz.lfunctions import SexticResidueCharacter  # noqa: E402
from collatz.lfunctions.eisenstein import EisensteinInt  # noqa: E402


def chi6_table() -> dict[tuple[int, int], complex]:
    """χ_6 on Z[ω]/3 indexed by (i mod 3, j mod 3) for i + j·ω."""
    chi = SexticResidueCharacter()
    table = {}
    for i in range(3):
        for j in range(3):
            table[(i, j)] = chi.evaluate(EisensteinInt(i, j))
    return table


def compute_Rk_with_dest_residue(K_max: int, lift: int = 10**6):
    """For each k in 1..K_max, return list of (r mod 2^k, dest mod 3) for r ∈ R_k.

    Reuses the survivor-tracking algorithm.
    """
    R_data: dict[int, list[tuple[int, int]]] = {}
    survivors = [(lift, lift)]  # (n_0, n_current)
    R_data[0] = []
    for k in range(1, K_max + 1):
        new_survivors = []
        dropped: list[tuple[int, int]] = []
        for n_0, _ in survivors:
            for n_0_child in (n_0, n_0 + 2 ** (k - 1)):
                n_iter = n_0_child
                for _ in range(k):
                    n_iter = collatz_step(n_iter)
                if n_iter < n_0_child:
                    # n_0_child has residue r = n_0_child mod 2^k (offset by lift mod 2^k)
                    # dest = n_iter; record (r, dest mod 3)
                    r = n_0_child % (2 ** k)
                    dropped.append((r, n_iter % 3))
                else:
                    new_survivors.append((n_0_child, n_iter))
        R_data[k] = dropped
        survivors = new_survivors
    return R_data


def main():
    K_max = 30  # tier 1/2/3 range
    print("Enumerating R_k with dest-mod-3 fingerprints up to k =", K_max)
    R_data = compute_Rk_with_dest_residue(K_max)

    table = chi6_table()

    # For each k with |R_k| > 0, compute dest-mod-3 distribution
    print(f"\n{'k':>3} {'|R_k|':>6} {'d=0':>5} {'d=1':>5} {'d=2':>5} "
          f"{'pred α_k':>12} {'pred phase':>12}")
    for k in sorted(R_data.keys()):
        if k == 0:
            continue
        rs = R_data[k]
        if not rs:
            continue
        # Count dest residues
        counts = [0, 0, 0]
        for _, d in rs:
            counts[d] += 1
        # Predict sum (per unit count of n in Dset_k):
        # For each residue r with d_r = d, n mod 3 equidistributes over {0,1,2},
        # contributing (1/3) * [chi(0,d) + chi(1,d) + chi(2,d)] per n.
        # Aggregated across the |R_k| residues, the per-n contribution
        # (averaged over residue choice) is:
        #   (1/|R_k|) * Σ_r (1/3) [χ(0,d_r) + χ(1,d_r) + χ(2,d_r)]
        # But n mod 3 also varies within a residue class. Easier: the total
        # contribution per Dset_k member n is determined by (n mod 3, d_{r(n)})
        # uniformly distributed in [counts of d_r across R_k] × [3 values of n mod 3].
        # |R_k| · 3 cells total; each with one n.
        per_n_sum = 0j
        for d, cnt in enumerate(counts):
            for i in range(3):
                per_n_sum += cnt * table[(i, d)]
        # per_n_sum: total over all (n mod 3, residue choice) cells, with each cell weight 1.
        # Number of cells = |R_k| · 3. Number nonzero cells = |R_k| · 2 (since one (i, d) pair has chi=0
        # per d value; specifically (i, d) with i + d ≡ 0 mod 3).
        nz_cells = sum(2 * cnt for cnt in counts)  # 2 of 3 n-residues are nonzero per d
        if nz_cells == 0:
            continue
        alpha_pred = abs(per_n_sum) / nz_cells if nz_cells > 0 else 0.0
        phase_pred = math.degrees(math.atan2(per_n_sum.imag, per_n_sum.real)) if abs(per_n_sum) > 1e-9 else float('nan')
        print(f"{k:>3d} {len(rs):>6d} {counts[0]:>5d} {counts[1]:>5d} {counts[2]:>5d} "
              f"{alpha_pred:>12.4f} {phase_pred:>+12.2f}°")

    # Now compare to empirical from dropping_set_l_function.npz at N=300000
    print("\n\n=== Match against empirical α_k (N=300,000) ===")
    data = np.load(Path(__file__).resolve().parents[1] / "data" / "dropping_set_l_function.npz")
    N = 300_000
    ks = data[f"N{N}_k"]
    cnt_nz = data[f"N{N}_count_nz"]
    re = data[f"N{N}_sum_re"]
    im = data[f"N{N}_sum_im"]
    emp = {}
    for i in range(len(ks)):
        k = int(ks[i])
        if cnt_nz[i] > 0:
            mag = math.hypot(re[i], im[i])
            arg = math.degrees(math.atan2(im[i], re[i]))
            emp[k] = (mag / cnt_nz[i], arg)

    print(f"{'k':>3} {'emp α_k':>10} {'pred α_k':>10} {'emp phase':>11} {'pred phase':>11} {'match?':>8}")
    for k in sorted(R_data.keys()):
        if k == 0 or not R_data[k]:
            continue
        if k not in emp:
            continue
        # Predicted
        counts = [0, 0, 0]
        for _, d in R_data[k]:
            counts[d] += 1
        per_n_sum = sum(cnt * table[(i, d)] for d, cnt in enumerate(counts) for i in range(3))
        nz_cells = sum(2 * cnt for cnt in counts)
        if nz_cells == 0:
            continue
        a_pred = abs(per_n_sum) / nz_cells
        p_pred = math.degrees(math.atan2(per_n_sum.imag, per_n_sum.real)) if abs(per_n_sum) > 1e-9 else 0.0
        a_emp, p_emp = emp[k]
        match = "✓" if abs(a_pred - a_emp) < 0.02 and (abs(p_pred - p_emp) < 5 or abs(abs(p_pred - p_emp) - 360) < 5) else "✗"
        print(f"{k:>3d} {a_emp:>10.4f} {a_pred:>10.4f} {p_emp:>+11.2f} {p_pred:>+11.2f} {match:>8}")


if __name__ == "__main__":
    main()
