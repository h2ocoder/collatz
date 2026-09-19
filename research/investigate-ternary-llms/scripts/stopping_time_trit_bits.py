"""Verify: odd stopping time T(n) = s + bitlen(3^s) = s + (minimum bits to store s trits).

For odd n > 1 with s odd (3x+1) steps in its stopping orbit, the repo's
Odd Stopping Time Spectrum theorem says T = ceil(s * log2 6) = s + ceil(s * log2 3).
Since 3^s is never a power of 2, ceil(s * log2 3) = (3^s).bit_length() exactly,
which is also the minimum number of bits b with 3^s <= 2^b, i.e. the minimum
storage for s trits. This script checks the integer form (no floating point)
and also checks the stronger "halving budget" reading: the number of halvings
in the stopping orbit is exactly bitlen(3^s), never more.

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/stopping_time_trit_bits.py
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from collatz.core import stopping_time  # noqa: E402


def odd_and_even_steps(n):
    """Count (odd steps, halvings) along the stopping orbit of n."""
    start, odd, even = n, 0, 0
    while True:
        if n % 2:
            n = 3 * n + 1
            odd += 1
        else:
            n //= 2
            even += 1
            if n < start:
                return odd, even


def min_bits_for_trits(t):
    """Smallest b with 3^t <= 2^b (exact integer arithmetic)."""
    b = (3**t).bit_length()
    # bit_length gives 2^(b-1) <= 3^t < 2^b; 3^t is never a power of two
    assert 3**t <= 2**b and (b == 0 or 3**t > 2 ** (b - 1))
    return b


def check(ns):
    violations = 0
    spectrum = {}
    for n in ns:
        s, halvings = odd_and_even_steps(n)
        t = stopping_time(n)
        predicted = s + min_bits_for_trits(s)
        if t != s + halvings or halvings != min_bits_for_trits(s) or t != predicted:
            violations += 1
            if violations <= 5:
                print(f"  VIOLATION n={n}: T={t}, s={s}, halvings={halvings}, predicted={predicted}")
        spectrum[s] = t
    return violations, spectrum


if __name__ == "__main__":
    N = 1_000_000
    v, spec = check(range(3, N, 2))
    print(f"odd n in [3, {N}): violations = {v}, distinct s = {len(spec)}, max s = {max(spec)}")

    rng = random.Random(28)
    big = [rng.getrandbits(128) | 1 for _ in range(20_000)]
    big = [n for n in big if n > 1]
    v2, spec2 = check(big)
    print(f"20,000 random odd 128-bit n: violations = {v2}, max s = {max(spec2)}")

    print("\n s | trits->bits b=bitlen(3^s) | T = s+b | waste b - s*log2(3)")
    import math
    for s in range(1, 13):
        b = min_bits_for_trits(s)
        print(f"{s:2d} | {b:26d} | {s + b:7d} | {b - s * math.log2(3):.4f}")
