"""Reduce the sign rule to a clean combinatorial claim on alpha-sequences.

REDUCTION CHAIN
================

Step 1 (already done in Part 3 of the doc):
    sgn(c_2^{(k_o)} - c_1^{(k_o)}) = sgn(C_2 - C_1)
where C_d counts parity-classes of R_{k_o} (each class has 2^o residues).

Step 2 (new):
    In Syracuse alpha-coordinates, a parity class is a sequence
    (α_1, ..., α_o) with each α_i ≥ 1, Σ α_i = e_o := k_o - o, and
    partial sums S_j := Σ_{i ≤ j} α_i satisfying S_j ≤ B_j := ⌊j log_2 3⌋
    for j < o (the "no-earlier-drop" condition), with S_o = B_o + 1 (the
    final-drop condition).

    j* (Collatz position of last odd step) = k_o − 1 − α_o, so
    j* + k_o is even ⟺ α_o is odd ⟺ class contributes to C_2.

    So C_2 − C_1 = #{paths : α_o odd} − #{paths : α_o even}.

Step 3 (key reduction):
    Let N(o−1, T) = # valid paths of length o−1 ending at S_{o−1} = T.
    Then α_o = e_o − T, so

        C_2 − C_1 = Σ_T N(o−1, T) · (−1)^{α_o + 1}
                  = Σ_T N(o−1, T) · (−1)^{e_o − T + 1}
                  = (−1)^{e_o + 1} Σ_T (−1)^{-T} N(o−1, T)
                  = (−1)^{B_o} Σ_T (−1)^T N(o−1, T)        (since e_o = B_o + 1)
                  = (−1)^{B_o} · D_o

    where D_o := Σ_T (−1)^T N(o−1, T).

Step 4 (alternating-sum reformulation):
    Letting u = B_{o−1} − T (distance from boundary), and noting
    Σ T ranges over [o−1, B_{o−1}]:

        AltSum(o) := Σ_d (−1)^d N(o−1, B_{o−1} − d) = (−1)^{B_{o−1}} D_o

    The sign of C_2 − C_1 is then

        sgn(C_2 − C_1) = sgn((−1)^{B_o − B_{o−1}} · AltSum(o))
                       = sgn((−1)^{gap_o − 1} · AltSum(o))

    which equals +1 if gap_o = 3 (odd-1 = even, +1) and AltSum > 0,
    or if gap_o = 2 (odd, −1) and AltSum < 0. Empirically we'll see
    AltSum > 0 always, giving the Sturmian sign rule.

STRUCTURAL CLAIM
================

    For all o ≥ 1 with o ≠ 3:  AltSum(o) > 0.

This is the remaining piece to prove. The script verifies it
empirically up to o ≤ O_max.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def B(j: int) -> int:
    """Beatty boundary B_j = floor(j log_2 3)."""
    if j == 0:
        return 0
    return int(math.floor(j * math.log2(3.0)))


def count_valid_paths(o_minus_1: int, T: int, max_step: int = None) -> int:
    """Number of (α_1, ..., α_{o-1}) with each ≥ 1, Σ = T, S_j ≤ B_j.

    Uses DP: f[j][s] = # paths of length j with S_j = s and S_i ≤ B_i for i ≤ j.
    """
    j_target = o_minus_1
    if max_step is None:
        max_step = T  # generous upper bound
    # f[j][s] = count
    f = [[0] * (T + 1) for _ in range(j_target + 1)]
    f[0][0] = 1
    for j in range(1, j_target + 1):
        for s in range(j, min(B(j), T) + 1):  # need s ≥ j (each step ≥ 1), s ≤ B_j
            for alpha in range(1, s - (j - 1) + 1):  # need S_{j-1} = s - alpha ≥ j - 1
                prev = s - alpha
                if prev < j - 1 or prev > B(j - 1):
                    continue
                f[j][s] += f[j - 1][prev]
    return f[j_target][T]


def all_N(o_minus_1: int) -> dict[int, int]:
    """Return dict {T: N(o-1, T)} for all valid T."""
    if o_minus_1 == 0:
        return {0: 1}
    j_target = o_minus_1
    T_max = B(j_target)
    f = [[0] * (T_max + 1) for _ in range(j_target + 1)]
    f[0][0] = 1
    for j in range(1, j_target + 1):
        Bj = B(j)
        for s in range(j, min(Bj, T_max) + 1):
            for alpha in range(1, s - (j - 1) + 1):
                prev = s - alpha
                if prev < j - 1 or prev > B(j - 1):
                    continue
                f[j][s] += f[j - 1][prev]
    return {T: f[j_target][T] for T in range(j_target, T_max + 1) if f[j_target][T] > 0}


def main():
    print(f"{'o':>3} {'k_o':>4} {'gap':>4} {'B_{o-1}':>8} {'N(o-1, T) by T':>40} "
          f"{'AltSum':>8} {'sign rule OK?':>14}")
    print("-" * 110)

    O_max = 18
    log2_3 = math.log2(3.0)

    for o in range(1, O_max + 1):
        B_o = B(o)
        B_om1 = B(o - 1)
        k_o = o + B_o + 1
        gap = k_o - (o - 1 + B_om1 + 1) if o > 1 else (o + B_o + 1 - 1)  # k_o - k_{o-1}

        N_dict = all_N(o - 1)
        N_str = " ".join(f"N({T})={cnt}" for T, cnt in sorted(N_dict.items()))

        # AltSum(o) = sum_T (-1)^{B_{o-1} - T} N(o-1, T)
        alt_sum = sum((-1) ** (B_om1 - T) * cnt for T, cnt in N_dict.items())

        # Predicted sign from Sturmian rule
        pred_sign = +1 if gap == 3 else -1
        # Computed sign = (-1)^{gap - 1} * sign(AltSum)
        if alt_sum != 0:
            computed_sign = ((-1) ** (gap - 1)) * (1 if alt_sum > 0 else -1)
        else:
            computed_sign = 0
        match = "✓" if computed_sign == pred_sign else ("Δ=0" if alt_sum == 0 else "✗")

        print(f"{o:>3d} {k_o:>4d} {gap:>4d} {B_om1:>8d} {N_str:>40} "
              f"{alt_sum:>+8d} {match:>14}")


if __name__ == "__main__":
    main()
