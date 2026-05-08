"""Tests for Eisenstein integer arithmetic."""

import math

import pytest

from collatz.lfunctions.eisenstein import (
    EisensteinInt,
    conjugate,
    divides,
    find_split_prime,
    is_associate,
    is_unit,
    norm,
    pi,
    pi_bar,
    quotient,
    reduce_mod,
    split_or_inert,
    units,
)


def test_omega_cube_root():
    omega = EisensteinInt(0, 1)
    one = EisensteinInt(1, 0)
    assert omega * omega * omega == one


def test_omega_squared():
    omega = EisensteinInt(0, 1)
    # omega^2 = -1 - omega
    assert omega * omega == EisensteinInt(-1, -1)


def test_pi_pi_bar_equals_three():
    # pi * pi_bar = (1 - omega)(1 - omega^2) = 3
    assert pi * pi_bar == EisensteinInt(3, 0)


def test_pi_norm():
    assert norm(pi) == 3
    assert norm(pi_bar) == 3


def test_pi_argument():
    # arg(pi) = -30 deg = -pi/6
    assert math.isclose(pi.arg(), -math.pi / 6, abs_tol=1e-12)
    assert math.isclose(pi_bar.arg(), math.pi / 6, abs_tol=1e-12)


def test_norm_multiplicative_random():
    pairs = [
        (EisensteinInt(2, 3), EisensteinInt(5, -1)),
        (EisensteinInt(7, 2), EisensteinInt(-3, 4)),
        (EisensteinInt(1, 1), EisensteinInt(1, -1)),
        (EisensteinInt(11, -5), EisensteinInt(2, 8)),
    ]
    for x, y in pairs:
        assert norm(x * y) == norm(x) * norm(y)


def test_conjugation_norm_invariant():
    for alpha in [EisensteinInt(2, 3), EisensteinInt(7, -2), pi]:
        assert norm(alpha.conjugate()) == norm(alpha)


def test_units_have_norm_one():
    for u in units():
        assert norm(u) == 1
        assert is_unit(u)


def test_units_form_group_under_multiplication():
    us = units()
    # Closed under multiplication
    for u in us:
        for v in us:
            assert is_unit(u * v)


def test_pi_squared_equals_minus_three_omega():
    # pi^2 = (1-omega)^2 = 1 - 2*omega + omega^2 = -3*omega
    assert pi * pi == EisensteinInt(0, -3)


def test_split_or_inert_classification():
    assert split_or_inert(3) == "ramified"
    # Split: p == 1 mod 3
    for p in [7, 13, 19, 31, 37]:
        assert split_or_inert(p) == "split"
    # Inert: p == 2 mod 3
    for p in [2, 5, 11, 17, 23]:
        assert split_or_inert(p) == "inert"


def test_find_split_prime_norm():
    for p in [7, 13, 19, 31, 37]:
        alpha = find_split_prime(p)
        assert norm(alpha) == p


def test_pi_divides_three():
    three = EisensteinInt(3, 0)
    assert divides(pi, three)


def test_quotient_three_by_pi():
    three = EisensteinInt(3, 0)
    q = quotient(three, pi)
    assert q * pi == three
    # 3 / pi = pi_bar (up to a unit), since pi * pi_bar = 3
    # Actually q should be exactly pi_bar / unit; either way q * pi = 3.
    # Stronger: 3 = pi * pi_bar, so 3/pi = pi_bar. Verify directly.
    assert q == pi_bar


def test_reduce_mod_pi_squared():
    # Reduction modulo pi^2 = -3*omega = (3) as ideals.
    pi2 = pi * pi
    assert pi2.norm() == 9

    # Every Eisenstein integer reduces to one of 9 residue classes mod (3).
    representatives = set()
    for a in range(-10, 11):
        for b in range(-10, 11):
            alpha = EisensteinInt(a, b)
            r = reduce_mod(alpha, pi2)
            # canonical form: take representatives in 0..2 for each coord modulo 3
            representatives.add((r.a % 3, r.b % 3))
    assert len(representatives) == 9


def test_is_associate():
    one = EisensteinInt(1, 0)
    omega = EisensteinInt(0, 1)
    minus_omega = EisensteinInt(0, -1)
    assert is_associate(one, omega)
    assert is_associate(omega, minus_omega)
    assert not is_associate(EisensteinInt(2, 0), one)


def test_pi_squared_equals_three_unit():
    # pi^2 = -3*omega, so pi^2 is associated to 3 via the unit -omega^{-1} = -omega^2
    pi2 = pi * pi
    three = EisensteinInt(3, 0)
    assert is_associate(pi2, three)
