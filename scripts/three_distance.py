"""Three Distance Theorem analysis for the L-probe.

For each N, the points T_o := {(o-1) log_2 3} for o = 1..N partition
[0, 1) into N arcs with at most 3 distinct lengths. At N = q_k (CF
denominators), the lengths simplify to exactly 2.

We:
  1. Verify the TDT prediction at each q_k.
  2. Locate the threshold τ = 2 - log_2 3 ≈ 0.4150 (sign-rule cutoff)
     within the arc partition and identify which arcs it crosses.
  3. Compute A_o/P_o at CF denominators and look at convergence.
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def cf_expansion(x: float, depth: int) -> list[int]:
    coefs = []
    for _ in range(depth):
        a = int(math.floor(x))
        coefs.append(a)
        frac = x - a
        if frac < 1e-15:
            break
        x = 1.0 / frac
    return coefs


def cf_convergents(coefs: list[int]) -> list[tuple[int, int]]:
    h = [1, coefs[0]]
    k = [0, 1]
    for n in range(1, len(coefs)):
        a = coefs[n]
        h.append(a * h[-1] + h[-2])
        k.append(a * k[-1] + k[-2])
    return list(zip(h[1:], k[1:]))


def three_distance_lengths(alpha: float, N: int) -> dict[float, int]:
    """Compute the multiset of arc lengths formed by {α}, {2α}, ..., {Nα}."""
    points = sorted(((i * alpha) % 1.0 for i in range(1, N + 1)))
    arcs = []
    for i in range(len(points)):
        if i + 1 < len(points):
            arcs.append(points[i + 1] - points[i])
        else:
            arcs.append(1.0 + points[0] - points[i])
    # Bucket into distinct lengths (tolerance for FP error)
    buckets: list[tuple[float, int]] = []
    for a in arcs:
        placed = False
        for k, (val, cnt) in enumerate(buckets):
            if abs(a - val) < 1e-9:
                buckets[k] = (val, cnt + 1)
                placed = True
                break
        if not placed:
            buckets.append((a, 1))
    return {val: cnt for val, cnt in sorted(buckets, key=lambda x: x[0])}


def main():
    log2_3 = math.log2(3.0)
    coefs = cf_expansion(log2_3, 10)
    convergents = cf_convergents(coefs)

    print("Three Distance arc partition at CF denominators:\n")
    print(f"{'k':>3} {'q_k':>5} {'# arcs':>8} {'arc lengths -> counts':>50} "
          f"{'τ = 0.4150 falls in':>22}")
    print("-" * 100)
    threshold = 2 - log2_3
    for k, (h, q) in enumerate(convergents):
        if q > 5000:
            break
        lengths = three_distance_lengths(log2_3, q)
        n_distinct = len(lengths)
        # Find which arc τ is in
        points = sorted(((i * log2_3) % 1.0 for i in range(1, q + 1)))
        idx_below = sum(1 for p in points if p < threshold)
        idx_above = q - idx_below
        # Format lengths
        len_str = "  ".join(f"{v:.5f}×{c}" for v, c in lengths.items())
        print(f"{k:>3d} {q:>5d} {n_distinct:>8d} {len_str:>50} "
              f"{f'{idx_below} below + {idx_above} above':>22}")


if __name__ == "__main__":
    main()
