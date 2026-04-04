"""Tests for collatz.orbits module."""

from fractions import Fraction
from collatz.orbits import class_members, aligned_orbits, pairwise_ratios, pairwise_differences, modular_equivalences
import pandas as pd


def test_class_members_set3_mod0():
    """Dropping set 3, modulus 0 should include 5, 9, 13, 17, ..."""
    members = class_members(3, 0, 50)
    from collatz.dropping import dropping_time
    for m in members:
        assert dropping_time(m) == 3, f"{m} has dropping time {dropping_time(m)}, expected 3"
    assert 5 in members
    assert 9 in members
    assert 13 in members


def test_class_members_returns_sorted():
    members = class_members(3, 0, 100)
    assert members == sorted(members)


def test_class_members_respects_limit():
    members = class_members(3, 0, 20)
    assert all(m < 20 for m in members)


def test_aligned_orbits_shape():
    """All orbits in same (set, modulus) should have equal length."""
    members = class_members(3, 0, 50)
    df = aligned_orbits(members)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == len(members)
    # All rows should have the same number of columns (no NaN)
    assert df.isna().sum().sum() == 0


def test_aligned_orbits_first_column_is_members():
    """Column 0 should be the members themselves."""
    members = class_members(3, 0, 30)
    df = aligned_orbits(members)
    assert list(df[0]) == members


def test_aligned_orbits_known_orbit():
    """dropping_orbit(5) = [5, 16, 8], so row for n=5 should be [5, 16, 8]."""
    df = aligned_orbits([5])
    assert list(df.iloc[0]) == [5, 16, 8]


def test_pairwise_ratios_shape():
    """Ratios DataFrame should have same shape as orbits."""
    members = class_members(3, 0, 50)
    df = aligned_orbits(members)
    ratios = pairwise_ratios(df)
    assert ratios.shape == df.shape


def test_pairwise_ratios_first_row_is_one():
    """First row (reference) should be all 1s."""
    members = class_members(3, 0, 30)
    df = aligned_orbits(members)
    ratios = pairwise_ratios(df)
    assert all(r == Fraction(1) for r in ratios.iloc[0])


def test_pairwise_ratios_are_fractions():
    """All ratio values should be Fraction instances."""
    members = class_members(3, 0, 30)
    df = aligned_orbits(members)
    ratios = pairwise_ratios(df)
    for col in ratios.columns:
        for val in ratios[col]:
            assert isinstance(val, Fraction), f"Expected Fraction, got {type(val)}"


def test_pairwise_differences_first_row_zero():
    """First row should be all zeros (reference minus itself)."""
    members = class_members(3, 0, 30)
    df = aligned_orbits(members)
    diffs = pairwise_differences(df)
    assert all(d == 0 for d in diffs.iloc[0])


def test_pairwise_differences_known():
    """Check difference between n=5 and n=9 orbits.

    dropping_orbit(5) = [5, 16, 8]
    dropping_orbit(9) = [9, 28, 14]
    diffs = [4, 12, 6]
    """
    df = aligned_orbits([5, 9])
    diffs = pairwise_differences(df)
    assert list(diffs.iloc[1]) == [4, 12, 6]


def test_modular_equivalences_returns_series():
    members = class_members(3, 0, 50)
    df = aligned_orbits(members)
    mods = modular_equivalences(df)
    assert isinstance(mods, pd.Series)
    assert len(mods) == len(df.columns)


def test_modular_equivalences_positive():
    """All moduli should be >= 1."""
    members = class_members(3, 0, 100)
    df = aligned_orbits(members)
    mods = modular_equivalences(df)
    assert all(m >= 1 for m in mods)


def test_modular_equivalences_valid():
    """All values in a column should be congruent mod the returned modulus."""
    members = class_members(3, 0, 100)
    df = aligned_orbits(members)
    mods = modular_equivalences(df)
    for col in df.columns:
        m = mods[col]
        residues = set(int(v) % m for v in df[col])
        assert len(residues) == 1, f"Column {col}: expected 1 residue mod {m}, got {residues}"
