"""Tests for collatz.embeddings.keys (coset-quotient embedding)."""

import math

import pytest

from collatz.embeddings.concept import Concept
from collatz.embeddings.keys import (
    concept_coset_distance,
    coset_distance,
    key_signature,
    keys_analogy,
    subgroup_id,
)


# ---- subgroup_id ---------------------------------------------------------


def test_subgroup_id_sentinel_for_one():
    assert subgroup_id(1) == (0, 0, 1)


def test_subgroup_id_set3_period4_same_subgroup():
    """Set_3 has s=1, period 4, residue 1 mod 4: 5, 9, 13, 17, 21, 25 all share."""
    target = subgroup_id(5)
    assert target == (3, 1, 1)
    for n in [9, 13, 17, 21, 25, 29, 33, 37]:
        assert subgroup_id(n) == target, f"n={n} should be in same subgroup as 5"


def test_subgroup_id_set6_residue3_mod16_same_subgroup():
    """Set_6 with s=2, period 16, residue 3 mod 16: 3, 19, 35, 51, 67, 83, 99."""
    target = subgroup_id(3)
    assert target == (6, 2, 3)
    for n in [19, 35, 51, 67, 83, 99]:
        assert subgroup_id(n) == target, f"n={n} should be in same subgroup as 3"


def test_subgroup_id_distinguishes_sets():
    """5 (Set_3) and 3 (Set_6) must have different subgroup ids."""
    assert subgroup_id(5) != subgroup_id(3)


def test_subgroup_id_known_values():
    # 11: k=8, s=3, period 32, residue 11
    assert subgroup_id(11) == (8, 3, 11)
    # 7: k=11, s=4, period 128, residue 7
    assert subgroup_id(7) == (11, 4, 7)
    # 27: k=96, s=37 (from MEMORY); residue 27
    k, s, r = subgroup_id(27)
    assert k == 96
    assert s == 37
    assert r == 27 % (2 ** (96 - 37))


def test_subgroup_id_rejects_zero_or_negative():
    with pytest.raises(ValueError):
        subgroup_id(0)
    with pytest.raises(ValueError):
        subgroup_id(-3)


# ---- key_signature -------------------------------------------------------


def test_key_signature_sentinel_for_one():
    assert key_signature(1) == (0.0, 0, 0)


def test_key_signature_consistency_within_subgroup():
    """All Set_3 s=1 members share key_signature."""
    sig5 = key_signature(5)
    for n in [9, 13, 17, 21, 25, 29]:
        assert key_signature(n) == sig5


def test_key_signature_log2_alpha_formula():
    """slope_log == s*log2(3) - (k - s) for n=3 (s=2, k=6)."""
    sig, k, s = key_signature(3)
    assert k == 6
    assert s == 2
    expected = 2 * math.log2(3) - (6 - 2)
    assert math.isclose(sig, expected, rel_tol=1e-12)


def test_key_signature_distinguishes_set_families():
    """Different (k, s) -> different key_signature."""
    assert key_signature(3) != key_signature(5)  # Set_6 vs Set_3
    assert key_signature(7) != key_signature(11)  # Set_11 vs Set_8


# ---- coset_distance ------------------------------------------------------


def test_coset_distance_identical_is_zero():
    assert coset_distance(7, 7) == 0.0


def test_coset_distance_same_subgroup_is_zero():
    """5 and 9 (and 13, 17) are in the same subgroup of Set_3."""
    assert coset_distance(5, 9) == 0.0
    assert coset_distance(5, 13) == 0.0
    assert coset_distance(5, 17) == 0.0
    assert coset_distance(3, 19) == 0.0  # same subgroup of Set_6
    assert coset_distance(3, 35) == 0.0


def test_coset_distance_different_set_is_one():
    """5 (Set_3) vs 3 (Set_6) -> 1.0."""
    assert coset_distance(5, 3) == 1.0
    assert coset_distance(5, 7) == 1.0  # Set_3 vs Set_11


def test_coset_distance_one_is_sentinel():
    assert coset_distance(1, 5) == 1.0
    assert coset_distance(5, 1) == 1.0
    assert coset_distance(1, 1) == 0.0


def test_coset_distance_in_unit_interval():
    for n1 in [3, 5, 7, 11, 17, 27]:
        for n2 in [3, 5, 7, 11, 17, 27]:
            d = coset_distance(n1, n2)
            assert 0.0 <= d <= 1.0


def test_coset_distance_rejects_invalid():
    with pytest.raises(ValueError):
        coset_distance(0, 5)
    with pytest.raises(ValueError):
        coset_distance(5, -3)


# ---- concept_coset_distance ---------------------------------------------


def test_concept_coset_distance_identical_is_zero():
    c = Concept("x", (5, 9, 13))  # all same Set_3 subgroup
    assert concept_coset_distance(c, c) == 0.0


def test_concept_coset_distance_same_subgroup_components_zero():
    a = Concept("a", (5, 9, 13))
    b = Concept("b", (17, 21, 25))
    assert concept_coset_distance(a, b) == 0.0


def test_concept_coset_distance_mismatched_length_raises():
    a = Concept("a", (5, 9))
    b = Concept("b", (5, 9, 13))
    with pytest.raises(ValueError):
        concept_coset_distance(a, b)


def test_concept_coset_distance_returns_mean():
    """Per-component: 5 vs 9 = 0, 5 vs 3 = 1.0 -> mean over 2 = 0.5."""
    a = Concept("a", (5, 5))
    b = Concept("b", (9, 3))
    assert concept_coset_distance(a, b) == 0.5


# ---- keys_analogy --------------------------------------------------------


def test_keys_analogy_returns_ranked_list_of_expected_length():
    a = Concept("a", (5, 9, 13))
    b = Concept("b", (17, 21, 25))
    c = Concept("c", (3, 19, 35))
    cands = [
        Concept("d0", (51, 67, 83)),  # same subgroup as c -> distance 0
        Concept("d1", (5, 9, 13)),    # different Set_k entirely -> distance 1
        Concept("d2", (7, 11, 27)),   # mixed -> distance 1
        Concept("d3", (99, 51, 19)),  # same subgroup as c -> distance 0
    ]
    ranked = keys_analogy(a, b, c, cands)
    assert len(ranked) == len(cands)
    # Scores must be sorted ascending.
    scores = [s for _, s in ranked]
    assert scores == sorted(scores)


def test_keys_analogy_self_consistency():
    """If a == b (target distance 0), expected d should be one closest to c (also 0)."""
    a = Concept("a", (5, 9, 13))
    c = Concept("c", (3, 19, 35))
    near = Concept("near", (51, 67, 83))  # same subgroup as c -> 0
    far = Concept("far", (5, 7, 11))      # all different sets from c -> 1
    ranked = keys_analogy(a, a, c, [far, near])
    assert ranked[0][0] is near
