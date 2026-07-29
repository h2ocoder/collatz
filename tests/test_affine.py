"""Tests for the exact affine dropping-orbit machinery."""
from fractions import Fraction

import pytest

from collatz.affine import (
    affine_destination_coefficients,
    affine_orbit_profile,
    orbit_max,
    orbit_sum,
    orbit_sum_coefficients,
    profile_from_alphas,
    subgroup_summary,
)
from collatz.core import alpha_sequence, stopping_destination, stopping_time
from collatz.dropping import dropping_orbit
from collatz.lfunctions.lattice_paths import enumerate_subgroups, k_of


@pytest.mark.parametrize("n", [2, 3, 5, 7, 11, 27, 97, 703, 871])
def test_profile_reproduces_orbit_exactly(n):
    profile = affine_orbit_profile(n)
    orbit = dropping_orbit(n)
    assert len(profile) == len(orbit) == stopping_time(n)
    for (a, b), x in zip(profile, orbit):
        assert a * n + b == x


@pytest.mark.parametrize("n", [2, 3, 5, 7, 27, 97])
def test_orbit_sum_and_max_match_orbit(n):
    orbit = dropping_orbit(n)
    assert orbit_sum(n) == sum(orbit)
    assert orbit_max(n) == max(orbit)


@pytest.mark.parametrize("n", [3, 7, 11, 27, 31, 97])
def test_orbit_sum_coefficients_exact_and_subgroup_invariant(n):
    k = stopping_time(n)
    s = sum(1 for x in dropping_orbit(n) if x % 2 == 1)
    modulus = 1 << (k - s)
    A, B = orbit_sum_coefficients(n)
    for m in (n, n + modulus, n + 2 * modulus):
        assert A * m + B == orbit_sum(m)
        assert orbit_sum_coefficients(m) == (A, B)


def test_destination_coefficients_match_known_table():
    # dest = (3/4) n + 1/4 on n ≡ 1 (mod 4)  [k=3]
    assert affine_destination_coefficients(5) == (Fraction(3, 4), Fraction(1, 4))
    # dest = (9/16) n + 5/16 on the k=6 class (n ≡ 3 mod 16)
    assert affine_destination_coefficients(3) == (Fraction(9, 16), Fraction(5, 16))
    # even class: dest = n/2
    assert affine_destination_coefficients(8) == (Fraction(1, 2), Fraction(0))


@pytest.mark.parametrize("n", [5, 11, 27, 97])
def test_destination_coefficients_predict_destination(n):
    lam, C = affine_destination_coefficients(n)
    assert lam * n + C == stopping_destination(n)


@pytest.mark.parametrize("s", [1, 2, 3, 4, 5])
def test_profile_from_alphas_matches_member_profile(s):
    for alphas in enumerate_subgroups(s):
        profile = profile_from_alphas(alphas)
        k = s + sum(alphas)
        assert k == k_of(s)
        assert len(profile) == k
        # find a member of this subgroup and compare
        member = next(
            n for n in range(3, 1 << (k + 4), 2)
            if stopping_time(n) == k and tuple(alpha_sequence(n)[:s]) == alphas
        )
        assert profile == affine_orbit_profile(member)


@pytest.mark.parametrize("s", [1, 2, 3, 4])
def test_subgroup_summary_consistency(s):
    for alphas in enumerate_subgroups(s):
        info = subgroup_summary(alphas)
        assert info["s"] == s
        assert info["k"] == k_of(s)
        profile = profile_from_alphas(alphas)
        assert info["A"] == sum(a for a, _ in profile)
        # destination slope is the universal contraction ratio 3^s / 2^(k-s)
        assert info["lam"] == Fraction(3**s, 2 ** (info["k"] - s))
