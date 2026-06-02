"""Tests for collatz.utils helpers."""

import math

import numpy as np

from collatz.utils import (
    beatty_to_o,
    bits_to_2d,
    sturmian_sign,
)


LOG2_3 = math.log2(3.0)


def test_beatty_to_o_first_rungs():
    """Beatty rung k_o = o + floor(o * log2 3) + 1; verify first few values."""
    m = beatty_to_o()
    # o=1: k = 1 + 1 + 1 = 3
    # o=2: k = 2 + 3 + 1 = 6
    # o=3: k = 3 + 4 + 1 = 8
    # o=4: k = 4 + 6 + 1 = 11
    assert m[3] == 1
    assert m[6] == 2
    assert m[8] == 3
    assert m[11] == 4


def test_sturmian_sign_threshold():
    """epsilon_o = +1 if (o-1)*log2(3) mod 1 >= 2 - log2(3), else -1."""
    threshold = 2.0 - LOG2_3
    for o in range(1, 30):
        frac = ((o - 1) * LOG2_3) % 1.0
        expected = 1 if frac >= threshold else -1
        assert sturmian_sign(o) == expected, f"mismatch at o={o}"


def test_bits_to_2d_split():
    """Splitting K bits of n into (high, low) returns the expected coordinates."""
    K = 6
    # n = 0b101_010 = 42; high half (top 3 bits) = 0b101 = 5; low half = 0b010 = 2
    hi, lo = bits_to_2d(42, K)
    assert hi == 5
    assert lo == 2
    # n = 0 -> (0, 0)
    assert bits_to_2d(0, K) == (0, 0)
    # n = 2^K - 1 -> (max, max)
    assert bits_to_2d((1 << K) - 1, K) == ((1 << (K - K // 2)) - 1, (1 << (K // 2)) - 1)


def test_helpers_are_pure():
    """Helpers should not mutate global state; calling twice returns equal results."""
    a = beatty_to_o()
    b = beatty_to_o()
    assert a == b
    assert sturmian_sign(5) == sturmian_sign(5)
