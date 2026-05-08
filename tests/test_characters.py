"""Tests for Hecke characters chi_3 and chi_6 on Z[omega]."""

import cmath
import math

import pytest

from collatz.lfunctions.characters import (
    CubicResidueCharacter,
    SexticResidueCharacter,
    TrivialCharacter,
    divisible_by_pi,
    unit_class_of,
)
from collatz.lfunctions.eisenstein import EisensteinInt, pi, pi_bar, units


def test_trivial_character_one_on_units():
    chi = TrivialCharacter()
    for u in units():
        assert chi.evaluate(u) == 1.0 + 0j


def test_trivial_character_zero_on_zero():
    chi = TrivialCharacter()
    assert chi.evaluate(EisensteinInt(0, 0)) == 0.0 + 0j


def test_pi_divisibility():
    # pi | pi
    assert divisible_by_pi(pi)
    # pi | 3
    assert divisible_by_pi(EisensteinInt(3, 0))
    # pi does not divide 1
    assert not divisible_by_pi(EisensteinInt(1, 0))
    # pi divides pi^2
    assert divisible_by_pi(pi * pi)


def test_chi_six_zero_on_pi_multiples():
    chi6 = SexticResidueCharacter()
    assert chi6.evaluate(pi) == 0.0 + 0j
    assert chi6.evaluate(EisensteinInt(3, 0)) == 0.0 + 0j
    assert chi6.evaluate(pi * pi) == 0.0 + 0j


def test_chi_six_unit_values_lie_in_mu6():
    """chi_6 must take values in mu_6 = {zeta_6^k : k=0..5}."""
    chi6 = SexticResidueCharacter()
    expected = {cmath.exp(1j * math.pi * k / 3) for k in range(6)}
    seen = []
    for a in range(-4, 5):
        for b in range(-4, 5):
            alpha = EisensteinInt(a, b)
            if divisible_by_pi(alpha):
                continue
            v = chi6.evaluate(alpha)
            # Identify which 6th root we got
            for k in range(6):
                if abs(v - cmath.exp(1j * math.pi * k / 3)) < 1e-9:
                    seen.append(k)
                    break
            else:
                pytest.fail(f"chi_6({alpha}) = {v} is not a 6th root of unity")
    # All six values should be hit
    assert set(seen) == {0, 1, 2, 3, 4, 5}


def test_chi_six_multiplicative_on_coprime_pairs():
    """chi_6(alpha * beta) = chi_6(alpha) * chi_6(beta)."""
    chi6 = SexticResidueCharacter()
    pairs = [
        (EisensteinInt(2, 0), EisensteinInt(5, 0)),
        (EisensteinInt(1, 1), EisensteinInt(2, 0)),  # both not pi-divisible
        (EisensteinInt(2, 1), EisensteinInt(5, -2)),
        (EisensteinInt(7, 2), EisensteinInt(11, 0)),
    ]
    for alpha, beta in pairs:
        if divisible_by_pi(alpha) or divisible_by_pi(beta):
            continue
        v_alpha = chi6.evaluate(alpha)
        v_beta = chi6.evaluate(beta)
        v_prod = chi6.evaluate(alpha * beta)
        assert abs(v_prod - v_alpha * v_beta) < 1e-9, (
            f"chi6({alpha}) = {v_alpha}, chi6({beta}) = {v_beta}, "
            f"chi6({alpha * beta}) = {v_prod}"
        )


def test_chi_six_order_six():
    """chi_6 has order 6: 6th power is principal (when nonzero)."""
    chi6 = SexticResidueCharacter()
    for a in range(-3, 4):
        for b in range(-3, 4):
            alpha = EisensteinInt(a, b)
            if divisible_by_pi(alpha) or (a == 0 and b == 0):
                continue
            v = chi6.evaluate(alpha)
            assert abs(v ** 6 - 1) < 1e-9


def test_chi_three_squared_equals_chi_six_squared():
    """chi_3 = chi_6^2 (both have order 3 with same kernel)."""
    chi3 = CubicResidueCharacter()
    chi6 = SexticResidueCharacter()
    for a in range(-3, 4):
        for b in range(-3, 4):
            alpha = EisensteinInt(a, b)
            if divisible_by_pi(alpha) or (a == 0 and b == 0):
                continue
            v3 = chi3.evaluate(alpha)
            v6_sq = chi6.evaluate(alpha) ** 2
            assert abs(v3 - v6_sq) < 1e-9


def test_chi_six_value_at_two():
    """chi_6(2) is some 6th root of unity."""
    chi6 = SexticResidueCharacter()
    v = chi6.evaluate(EisensteinInt(2, 0))
    # 2 has unit class index found via discrete log
    k = unit_class_of(EisensteinInt(2, 0))
    assert k is not None
    expected = cmath.exp(1j * math.pi * k / 3)
    assert abs(v - expected) < 1e-9


def test_chi_six_constant_on_associates():
    """chi_6(u * alpha) = chi_6(alpha) only if chi_6(u) = 1.

    For finite-order Hecke characters, chi must be trivial on units. In our
    setup chi_6 is defined on residue classes mod (3); let us verify:
    multiplying alpha by a unit u that is itself a unit mod (3) acts as
    multiplication in the unit class group.
    """
    chi6 = SexticResidueCharacter()
    alpha = EisensteinInt(2, 0)
    v = chi6.evaluate(alpha)
    for u in units():
        v_u_alpha = chi6.evaluate(u * alpha)
        v_u = chi6.evaluate(u)
        # multiplicative
        assert abs(v_u_alpha - v_u * v) < 1e-9


def test_chi_six_units_sum_to_zero():
    """sum_{u in units} chi_6(u) = 0 because chi_6 is nontrivial on units."""
    chi6 = SexticResidueCharacter()
    s = sum(chi6.evaluate(u) for u in units())
    assert abs(s) < 1e-9
