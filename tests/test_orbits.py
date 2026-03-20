"""Tests for collatz.orbits module."""

from collatz.orbits import class_members


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
