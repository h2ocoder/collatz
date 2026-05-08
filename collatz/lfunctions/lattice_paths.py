"""Lattice-path enumeration for Dropping-Set subgroups.

For Dset_k with oddity s, each subgroup corresponds to a tuple
(alpha_1, ..., alpha_{s-1}, alpha_s) of "extra halving" lengths satisfying:

  - alpha_1 = 1 for s >= 2 (forced by 3n+1 being even but not divisible by 4
    when n ≡ 3 mod 4).
  - alpha_i >= 1 for all i.
  - sum_{j<=i} alpha_j < i * log_2(3) for i = 1..s-1
    (path stays strictly below the line, orbit doesn't drop early).
  - sum_{j<=s} alpha_j = k - s = ceil(s * log_2 3)
    (path crosses the line at step s, orbit drops).

The trailing alpha alpha_s = (k - s) - sum_{i<s} alpha_i determines the
affine constant C mod 3 within the subgroup, because:

  - C is reset to 1 after each odd step.
  - Each subsequent halving multiplies C by 2 mod 3 (since 2^{-1} = 2 mod 3).

So C mod 3 at the end = 2^{alpha_s} mod 3, equivalently:

  dest mod 3 = { 1 if alpha_s is even, 2 if alpha_s is odd }.

This module enumerates the subgroups and counts by parity of alpha_s,
giving access to N_1(s) - N_2(s) = (subgroups with dest ≡ 1) - (subgroups
with dest ≡ 2).
"""

from __future__ import annotations

import math
from functools import lru_cache


def k_of(s: int) -> int:
    """Stopping time of Dset with oddity s: k = ceil(s * log_2 6)."""
    return s + math.ceil(s * math.log2(3))


def density_per_subgroup(s: int) -> float:
    """Asymptotic density of one subgroup of Dset_k(s) among all odd integers.

    For s = 1 (Set_3): single subgroup, density = 1/2.
    For s >= 2: density per subgroup = 1/2^{k-s-1} where k = k_of(s).
    """
    if s <= 0:
        raise ValueError("s must be >= 1")
    if s == 1:
        return 0.5
    return 2.0 ** -(k_of(s) - s - 1)


def enumerate_subgroups(s: int) -> list[tuple[int, ...]]:
    """Enumerate alpha-tuples (alpha_1, ..., alpha_s) for Dset_k with oddity s.

    Returns the list of tuples; the last element is the trailing alpha.
    """
    if s == 1:
        return [(2,)]
    if s == 0:
        return []
    k = k_of(s)
    target = k - s
    log23 = math.log2(3)
    paths: list[tuple[int, ...]] = []

    def recurse(prefix: list[int], cur_sum: int, idx: int) -> None:
        if idx == s - 1:
            a_s = target - cur_sum
            if a_s >= 1:
                paths.append(tuple(prefix) + (a_s,))
            return
        for a in range(1, target - cur_sum + 1):
            new_sum = cur_sum + a
            if new_sum >= (idx + 1) * log23:
                break
            recurse(prefix + [a], new_sum, idx + 1)

    recurse([1], 1, 1)
    return paths


def count_by_dest_residue(s: int) -> tuple[int, int]:
    """Return (N_1(s), N_2(s)) for Dset_k with oddity s.

    N_b(s) = number of subgroups with dest ≡ b (mod 3).
    For small s uses brute enumeration; for s >= 8 uses DP.
    """
    if s <= 7:
        paths = enumerate_subgroups(s)
        n1 = sum(1 for p in paths if p[-1] % 2 == 0)
        n2 = len(paths) - n1
        return n1, n2
    return count_by_dest_residue_dp(s)


def count_by_dest_residue_dp(s: int) -> tuple[int, int]:
    """DP version: count prefixes by sum, then partition by trailing-alpha parity.

    State: dp[i][t] = number of valid alpha-prefixes of length i with sum = t,
    satisfying sum_j < j * log_2(3) for all j = 1..i.

    Transitions: dp[i][t] = sum_{a >= 1} dp[i-1][t - a], filtered by feasibility.
    """
    if s <= 0:
        return (0, 0)
    if s == 1:
        return (1, 0)  # alpha_1 = 2, even -> N_1
    log23 = math.log2(3)
    target = math.ceil(s * log23)  # = k - s

    # dp[i][t] over i in 1..s-1, t in 1..target.
    # We only need dp_prev (length i-1) when computing dp_cur (length i).
    # Sums for valid prefix at step i: t < i * log_2(3), so t <= floor(i * log_2 3).

    # Initialize dp at i=1: only a_1=1 is valid (since 1 < log_2 3 ~ 1.585).
    dp_prev: dict[int, int] = {1: 1}

    for i in range(2, s):  # build dp[i] for i = 2 .. s-1
        max_t = int(i * log23)  # strict < i*log_2 3 -> t <= floor when not integer; log_2 3 irrational so safe
        dp_cur: dict[int, int] = {}
        for t_prev, count in dp_prev.items():
            # extend by a >= 1: new t = t_prev + a, with new t <= max_t.
            for new_t in range(t_prev + 1, max_t + 1):
                dp_cur[new_t] = dp_cur.get(new_t, 0) + count
        dp_prev = dp_cur

    # Now dp_prev = dp[s-1][t] for t < (s-1) log_2 3.
    # Final: alpha_s = target - t >= 1, so t <= target - 1.
    n1 = 0  # alpha_s even -> dest ≡ 1 mod 3
    n2 = 0
    for t, count in dp_prev.items():
        a_s = target - t
        if a_s < 1:
            continue
        if a_s % 2 == 0:
            n1 += count
        else:
            n2 += count
    return n1, n2


def b_imbalance_term(s: int) -> float:
    """Contribution of Dset_k(s) to rho_1 - rho_2:
        D(s) = (N_1(s) - N_2(s)) * density_per_subgroup(s).
    """
    n1, n2 = count_by_dest_residue(s)
    return (n1 - n2) * density_per_subgroup(s)


def rho_diff_partial(s_max: int) -> float:
    """Partial sum sum_{s=1..s_max} D(s).

    The full sum rho_1 - rho_2 is the limit as s_max -> infinity.
    """
    return sum(b_imbalance_term(s) for s in range(1, s_max + 1))
