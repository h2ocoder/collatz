"""Verification before contacting M.C. Siegel (arXiv 2007.15936).

Checks the three claims connecting Siegel's (p,q)-adic numen chi_q to the
log-6 wobble (docs/Explorations/Log-6 Rotation Duality.md):

  1. Branch conventions.  Siegel's shortened map uses H0(x) = x/2 and
     H1(x) = (qx+1)/2.  Under log_6|.|, H0 rotates by -log_6 2 = alpha
     (mod 1) but H1 rotates by 2*alpha - 1 != alpha: the uniform-rotation
     property of the wobble analysis is special to the FULL map
     (x/2 and 3x+1 as separate steps); the cocycle and the wobble
     increment are identical in both presentations.

  2. One accumulation series, two completions.  The parity vector gives
     the exact integer identity 2^E x_N = 3^O x_0 + C, and the wobble is
     its archimedean shadow: W_total = log_6(1 + C/(3^O x_0)).  Siegel's
     chi_3 is the 3-adic limit of the same parity-vector data.

  3. The numen functional equations chi(2z) = chi(z)/2 and
     chi(2z+1) = (q chi(z)+1)/2, solved on periodic bit blocks with exact
     rational arithmetic, reproduce the known cycles (Correspondence
     Principle): q=3 -> {1,2} and the fixed point -1; q=5 -> {1,3,8,4,2}
     and {13,33,83,208,104,52,26}.
"""

from __future__ import annotations

import math
from fractions import Fraction

from collatz.core import orbit

LOG6 = math.log(6)
ALPHA = math.log(3) / LOG6


def check_rotations() -> None:
    full_even = (-math.log(2) / LOG6) % 1
    short_odd = (math.log(1.5) / LOG6) % 1
    assert abs(full_even - ALPHA) < 1e-12
    assert abs(short_odd - (2 * ALPHA - 1)) < 1e-12
    print(f"1. full map: every step rotates by alpha = {ALPHA:.6f}; "
          f"shortened map odd branch rotates by 2*alpha-1 = {short_odd:.6f}")


def check_accumulation(seeds=(27, 703, 670617279)) -> None:
    for n in seeds:
        seq = orbit(n)
        c = o = e = 0
        for x in seq[:-1]:
            if x % 2 == 1:
                c, o = 3 * c + 2 ** e, o + 1
            else:
                e += 1
        assert seq[-1] * 2 ** e == 3 ** o * n + c
        w_from_c = math.log1p(c / (3 ** o * n)) / LOG6
        w_direct = sum(math.log1p(1 / (3 * x)) / LOG6
                       for x in seq[:-1] if x % 2 == 1)
        assert abs(w_from_c - w_direct) < 1e-12
    print(f"2. 2^E x_N = 3^O n + C exact, and W_total = log_6(1 + C/(3^O n)),"
          f" for n in {seeds}")


def chi_periodic(bits: list[int], q: int) -> Fraction:
    """chi_q at the 2-adic rational whose bits repeat `bits` (LSB-first)."""
    a, b = Fraction(1), Fraction(0)
    for bit in reversed(bits):
        if bit == 0:
            a, b = a / 2, b / 2
        else:
            a, b = Fraction(q) * a / 2, (Fraction(q) * b + 1) / 2
    return b / (1 - a)


def shortened_parities(x: int, q: int, steps: int) -> list[int]:
    bits = []
    for _ in range(steps):
        if x % 2 == 1:
            bits.append(1)
            x = (q * x + 1) // 2
        else:
            bits.append(0)
            x //= 2
    return bits


def check_numen() -> None:
    rot = lambda b, i: b[i:] + b[:i]
    b3 = shortened_parities(1, 3, 2)
    assert {chi_periodic(rot(b3, i), 3) for i in range(2)} == {1, 2}
    assert chi_periodic([1], 3) == -1
    b5a = shortened_parities(1, 5, 5)
    assert ({chi_periodic(rot(b5a, i), 5) for i in range(5)}
            == {1, 2, 3, 4, 8})
    b5b = shortened_parities(13, 5, 7)
    assert ({chi_periodic(rot(b5b, i), 5) for i in range(7)}
            == {13, 26, 33, 52, 83, 104, 208})
    print("3. numen functional equations reproduce all tested cycles: "
          "q=3 {1,2} and -1; q=5 {1,3,8,4,2} and {13,...,208}")


if __name__ == "__main__":
    check_rotations()
    check_accumulation()
    check_numen()
    print("all checks pass")
