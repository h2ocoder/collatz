"""Compute |R_k| (sizes of dropping-residue sets) and the zeros of the
dropping zeta function.

The dropping zeta is g(z) = sum_k |R_k| z^k where |R_k| counts residues
r mod 2^k whose Collatz orbit first drops below the starting value at
exactly step k. Terras: sum_k |R_k|/2^k = 1.

The "Collatz zeros" are the roots of 1 - g(z) = 0. We hunt for them and
check whether they lie on a critical line (Re(s) constant) after s = -log_2(z).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collatz.core import collatz_step  # noqa: E402


def compute_Rk(K_max: int, lift: int = 10**6) -> list[int]:
    """Return list R[k] for k = 0..K_max, R[0] = 0 by convention.

    Maintains survivors S_k = set of residues mod 2^k that have NOT yet
    dropped by step k. Represented as a list of (n_0, n_k) tuples where
    n_0 is a representative integer and n_k is its value after k steps.
    """
    R = [0]
    # S_0: one "residue" (the trivial mod-1 residue, representing every integer)
    # represented by n_0 = lift (must be big enough that intermediates stay positive)
    survivors = [(lift, lift)]
    for k in range(1, K_max + 1):
        new_survivors = []
        dropped = 0
        for n_0, _ in survivors:
            for n_0_child in (n_0, n_0 + 2 ** (k - 1)):
                # Re-simulate k steps from n_0_child
                n = n_0_child
                for _ in range(k):
                    n = collatz_step(n)
                if n < n_0_child:
                    dropped += 1
                else:
                    new_survivors.append((n_0_child, n))
        R.append(dropped)
        survivors = new_survivors
    return R


def main() -> None:
    K_max = 30
    print(f"Computing |R_k| for k = 1..{K_max} ...")
    t0 = time.time()
    R = compute_Rk(K_max)
    t1 = time.time()
    print(f"Done in {t1 - t0:.1f}s\n")

    total = 0.0
    print(f"{'k':>3} {'|R_k|':>10} {'density':>14} {'cum sum':>10}")
    for k in range(1, K_max + 1):
        density = R[k] / 2**k
        total += density
        print(f"{k:>3d} {R[k]:>10d} {density:>14.6e} {total:>10.6f}")

    print(f"\nTotal mass captured up to k={K_max}: {total:.6f}")
    print(f"Remaining (not yet dropped): {1 - total:.6f}\n")

    # Build polynomial p(z) = -1 + sum_{k>=1} R[k] z^k = g(z) - 1
    # Roots of p(z) are the "Collatz zeros"
    coeffs = np.array([-1.0] + [float(R[k]) for k in range(1, K_max + 1)])
    # numpy.roots expects highest degree first
    poly = coeffs[::-1]
    roots = np.roots(poly)
    print(f"Polynomial degree = {len(coeffs) - 1}, found {len(roots)} roots\n")

    # Sort by modulus (smallest first); z = 1/2 should be among them
    roots = roots[np.argsort(np.abs(roots))]

    # Convert each root z to s-plane via s = -log_2(z) = -log(z)/log(2)
    log2 = np.log(2.0)
    s_values = -np.log(roots) / log2  # complex log; principal branch

    print(f"{'|z|':>10} {'arg(z) deg':>12} {'Re(s)':>10} {'Im(s)':>10}")
    for z, s in zip(roots[:40], s_values[:40]):
        print(f"{abs(z):>10.6f} {np.degrees(np.angle(z)):>12.4f} {s.real:>10.6f} {s.imag:>10.6f}")

    # Save for plotting
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(exist_ok=True)
    np.savez(
        out_dir / "dropping_zeta_zeros.npz",
        R=np.array(R),
        roots_z=roots,
        roots_s=s_values,
        K_max=K_max,
    )
    print(f"\nSaved to {out_dir / 'dropping_zeta_zeros.npz'}")


if __name__ == "__main__":
    main()
