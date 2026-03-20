"""Tests for collatz.orbits module."""

from collatz.orbits import class_members, aligned_orbits
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
