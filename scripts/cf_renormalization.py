"""Test CF-renormalization hypothesis for (P_o, A_o).

Conjecture: at o = q_k (CF denominators of log_2 3), the values
(P_{q_k}, A_{q_k}) satisfy a recurrence in k determined by the CF
coefficients a_k. If so, the L-probe is computable in O(log o)
instead of O(o).
"""
from __future__ import annotations

import math
import time
from fractions import Fraction
from pathlib import Path

import numpy as np


# ---------------- CF expansion of log_2(3) ----------------

def cf_expansion(x: float, depth: int) -> list[int]:
    """Continued fraction coefficients [a_0; a_1, ..., a_{depth-1}]."""
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
    """Return list of (h_k, k_k) convergents."""
    h = [1, coefs[0]]
    k = [0, 1]
    for n in range(1, len(coefs)):
        a = coefs[n]
        h.append(a * h[-1] + h[-2])
        k.append(a * k[-1] + k[-2])
    return list(zip(h[1:], k[1:]))


# ---------------- Beatty boundary + DP ----------------

def B(j: int) -> int:
    if j == 0:
        return 0
    return int(math.floor(j * math.log2(3.0)))


def gap(o: int) -> int:
    return (o + B(o) + 1) - ((o - 1) + B(o - 1) + 1)


def compute_PA(o_minus_1: int) -> tuple[int, int]:
    """Return (P_o, A_o) for the given o = o_minus_1 + 1."""
    if o_minus_1 == 0:
        return 1, 1
    T_max = B(o_minus_1)
    f = [[0] * (T_max + 1) for _ in range(o_minus_1 + 1)]
    f[0][0] = 1
    for j in range(1, o_minus_1 + 1):
        Bj = B(j)
        for s in range(j, min(Bj, T_max) + 1):
            for alpha in range(1, s - (j - 1) + 1):
                prev = s - alpha
                if prev < j - 1 or prev > B(j - 1):
                    continue
                f[j][s] += f[j - 1][prev]
    B_om1 = B(o_minus_1)
    P = sum(f[o_minus_1][T] for T in range(o_minus_1, T_max + 1) if f[o_minus_1][T] > 0)
    A = sum((-1) ** (B_om1 - T) * f[o_minus_1][T] for T in range(o_minus_1, T_max + 1))
    return P, A


def main():
    log2_3 = math.log2(3.0)
    coefs = cf_expansion(log2_3, 12)
    convergents = cf_convergents(coefs)

    print(f"log_2(3) = [{coefs[0]}; {', '.join(map(str, coefs[1:]))}, ...]")
    print(f"Convergents (h_k / q_k):")
    for k, (h, q) in enumerate(convergents):
        print(f"  k={k}: {h}/{q} ≈ {h/q:.10f}  (error {abs(h/q - log2_3):.2e})")

    # Compute (P_o, A_o) at every o up to first o > 53
    o_max = 53
    print(f"\nComputing (P_o, A_o) for o = 1..{o_max}...")
    t0 = time.time()
    data = {}
    for o in range(1, o_max + 1):
        data[o] = compute_PA(o - 1)
    print(f"Done in {time.time() - t0:.1f}s\n")

    # Tabulate at CF denominators
    print("Values at CF denominators o = q_k:\n")
    print(f"{'k':>3} {'a_k':>5} {'q_k':>5} {'P_{q_k}':>16} {'A_{q_k}':>16} "
          f"{'P_{q_k}/P_{q_{k-1}}':>22} {'A_{q_k}/A_{q_{k-1}}':>22}")
    prev_P = prev_A = None
    for k, (h, q) in enumerate(convergents):
        if q > o_max:
            break
        P, A = data[q]
        a = coefs[k]
        if prev_P is None:
            r_P = r_A = "—"
        else:
            r_P = f"{Fraction(P, prev_P)}" if prev_P > 0 else "—"
            r_A = f"{Fraction(A, prev_A)}" if prev_A > 0 else "—"
        print(f"{k:>3d} {a:>5d} {q:>5d} {P:>16d} {A:>16d} {r_P:>22} {r_A:>22}")
        prev_P = P
        prev_A = A

    # Also try at semi-convergent / off-CF values to compare
    print("\nValues at all o for context (last 10):")
    for o in range(max(1, o_max - 10), o_max + 1):
        P, A = data[o]
        print(f"  o={o:>3d}: P={P:>14d}  A={A:>14d}  gap={gap(o)}  is_CF={o in [q for _, q in convergents]}")

    # Save
    out_dir = Path(__file__).resolve().parents[1] / "data"
    np.savez(out_dir / "cf_PA.npz",
             os=np.array(list(data.keys())),
             Ps=np.array([data[o][0] for o in data]),
             As=np.array([data[o][1] for o in data]),
             cf_coefs=np.array(coefs[:8]),
             cf_qs=np.array([q for _, q in convergents[:8]]))
    print(f"\nSaved {out_dir / 'cf_PA.npz'}")


if __name__ == "__main__":
    main()
