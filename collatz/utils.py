"""Shared helpers: caching, batch computation, Sturmian/Beatty utilities."""

import math
from functools import lru_cache

import numpy as np


@lru_cache(maxsize=None)
def _collatz_step_cached(n):
    """Cached single Collatz step."""
    return n // 2 if n % 2 == 0 else 3 * n + 1


def batch_apply(func, start, end):
    """Apply a classification function to a range of integers.

    Returns a list of (n, result) tuples for n in [start, end).
    """
    return [(n, func(n)) for n in range(start, end)]


def members_of_class(class_func, class_value, limit):
    """Find all integers n in [2, limit) belonging to a given class.

    Args:
        class_func: function that maps n -> class value (e.g., dropping_set)
        class_value: the target class value
        limit: upper bound (exclusive)

    Returns:
        Sorted list of integers belonging to that class.
    """
    return [n for n in range(2, limit) if class_func(n) == class_value]


LOG2_3 = math.log2(3.0)


def beatty_to_o(max_o: int = 100) -> dict[int, int]:
    """Map standard Beatty rung k_o = o + floor(o * log2 3) + 1 back to o.

    Returns a dict {k: o} covering o in [1, max_o). Used to identify which
    odd-stopping-time class a given Collatz drop time belongs to.

    Example: beatty_to_o()[3] == 1; beatty_to_o()[6] == 2.
    """
    m: dict[int, int] = {}
    for o in range(1, max_o):
        k = o + int(math.floor(o * LOG2_3)) + 1
        m[k] = o
    return m


def sturmian_sign(o: int) -> int:
    """Sturmian sign epsilon_o for o >= 1: +1 if gap_o = 3, -1 if gap_o = 2.

    The threshold is 2 - log2(3); compared against fractional part of
    (o - 1) * log2(3).

    Example: sturmian_sign(1) == -1; sturmian_sign(2) == 1.
    """
    threshold = 2.0 - LOG2_3
    frac = ((o - 1) * LOG2_3) % 1.0
    return 1 if frac >= threshold else -1


def bits_to_2d(n: int, K: int) -> tuple[int, int]:
    """Split n's K bits into (high half, low half) for 2D bit-split imaging.

    Returns (row, col) where row indexes the top (K - K//2) bits and col
    indexes the low K//2 bits. Used by 2-adic visualizations so that
    2-adically close integers land in nearby pixels.

    Example: bits_to_2d(42, 6) == (5, 2).
    """
    half = K // 2
    low = n & ((1 << half) - 1)
    high = n >> half
    return high, low


def trailing_zeros_vec(arr: np.ndarray) -> np.ndarray:
    """v_2 (2-adic valuation) of each element of arr; arr must be > 0.

    Vectorized via the bit trick `low = a & -a`.
    """
    a = arr.astype(np.int64)
    low = a & -a
    return np.round(np.log2(low.astype(np.float64))).astype(np.int64)
