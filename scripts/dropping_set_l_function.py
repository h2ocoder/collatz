"""Phase 1.5: split D_chi_6(N) by dropping time T(n).

For odd n in [3, N], aggregate chi_6(orbit_pair(n)) into bins indexed
by the dropping time T(n). For each bin, report:

  count_k     = number of n contributing
  sum_k       = sum of chi(orbit_pair(n))
  |sum_k|     = magnitude
  ratio_k     = |sum_k| / sqrt(count_k)   (GRH-trivial baseline = O(log N))

If the ratio is roughly constant across k, chi_6 does not see the
2-adic stratification — the dropping-set split is "invisible" to it
(consistent with Multiplication Symmetry). If the ratio depends on k,
the L-function probe is correlated with the dropping structure.

Also computes the aggregate sum to confirm consistency with prior
phase-1 work.

Run at multiple N values (passed on the command line) to extract
growth rates per bin.
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from collatz.core import stopping_time  # noqa: E402
from collatz.lfunctions import SexticResidueCharacter  # noqa: E402
from collatz.lfunctions.orbit_lift import orbit_pair  # noqa: E402


def compute_bins(N: int):
    """Return dict {k: (sum_k_complex, count_k)} for odd n in [3, N]."""
    chi = SexticResidueCharacter()
    bins: dict[int, list] = {}
    total = 0.0 + 0j
    t0 = time.time()
    for n in range(3, N + 1, 2):
        T = stopping_time(n)
        alpha = orbit_pair(n)
        v = chi.evaluate(alpha)
        # Note: v can be 0 (when alpha divisible by pi; chi_6 has conductor (pi^2))
        if T not in bins:
            bins[T] = [0.0 + 0j, 0, 0]  # [sum, count, count_nonzero]
        bins[T][0] += v
        bins[T][1] += 1
        if v != 0:
            bins[T][2] += 1
        total += v
    t1 = time.time()
    return bins, total, t1 - t0


def report(N: int, bins: dict, total: complex, elapsed: float):
    print(f"\n=== N = {N}  (elapsed {elapsed:.2f}s) ===")
    print(f"Aggregate sum: {total:.4f}  |sum|={abs(total):.4f}  "
          f"sqrt(N)={math.sqrt(N):.3f}  |sum|/sqrt(N)={abs(total)/math.sqrt(N):.4f}")
    print(f"\n{'k':>4} {'count':>10} {'cnt_nz':>8} {'|sum_k|':>12} "
          f"{'arg(sum)deg':>12} {'|sum|/sqrt(cnt)':>16} {'|sum|/sqrt(nz)':>16}")
    rows = []
    for k in sorted(bins.keys()):
        s, cnt, nz = bins[k]
        if cnt == 0:
            continue
        abs_s = abs(s)
        ratio_all = abs_s / math.sqrt(cnt) if cnt > 0 else 0.0
        ratio_nz = abs_s / math.sqrt(nz) if nz > 0 else 0.0
        arg = math.degrees(math.atan2(s.imag, s.real)) if abs_s > 0 else 0.0
        print(f"{k:>4d} {cnt:>10d} {nz:>8d} {abs_s:>12.4f} "
              f"{arg:>12.2f} {ratio_all:>16.4f} {ratio_nz:>16.4f}")
        rows.append((k, cnt, nz, s, abs_s, ratio_all, ratio_nz))
    return rows


def main():
    Ns = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else [10_000, 100_000]
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(exist_ok=True)

    all_results: dict[int, list] = {}
    for N in Ns:
        bins, total, elapsed = compute_bins(N)
        rows = report(N, bins, total, elapsed)
        all_results[N] = rows

    # Save raw data for plotting
    np.savez(
        out_dir / "dropping_set_l_function.npz",
        Ns=np.array(Ns),
        # Flatten: per-N dict -> we'll save per-N via separate keys
        **{f"N{N}_k": np.array([r[0] for r in all_results[N]]) for N in Ns},
        **{f"N{N}_count": np.array([r[1] for r in all_results[N]]) for N in Ns},
        **{f"N{N}_count_nz": np.array([r[2] for r in all_results[N]]) for N in Ns},
        **{f"N{N}_sum_re": np.array([r[3].real for r in all_results[N]]) for N in Ns},
        **{f"N{N}_sum_im": np.array([r[3].imag for r in all_results[N]]) for N in Ns},
    )
    print(f"\nSaved {out_dir / 'dropping_set_l_function.npz'}")


if __name__ == "__main__":
    main()
