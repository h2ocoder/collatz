"""Tests for collatz.embeddings.progression — progression-edit-distance embedding.

Sequence-based companion to trajectory.py (set-based) and the lens-bundle Phi.
Distance via Levenshtein edit distance; tempo-flexible (insertions/deletions
handle different orbit lengths) but progression-strict (substitutions cost).
"""

import pytest

from collatz.embeddings.concept import Concept
from collatz.embeddings.iteration import _syr_step
from collatz.embeddings.progression import (
    concept_progression_distance,
    edit_distance,
    joint_progression,
    nearest_progression,
    normalized_edit_distance,
    progression_analogy,
    progression_distance,
    sector_progression,
)


# ---- sector_progression --------------------------------------------------


def test_sector_progression_3():
    """alpha_sequence(3) = [1, 4], so 2 Syracuse hops; sectors L..0 = (2, 1, 0)."""
    assert sector_progression(3) == (2, 1, 0)


def test_sector_progression_5():
    """alpha_sequence(5) = [4], so 1 Syracuse hop; sectors (1, 0)."""
    assert sector_progression(5) == (1, 0)


def test_sector_progression_7():
    """alpha_sequence(7) has length 5; sectors (5, 4, 3, 2, 1, 0)."""
    assert sector_progression(7) == (5, 4, 3, 2, 1, 0)


def test_sector_progression_n_one():
    assert sector_progression(1) == (0,)


def test_sector_progression_lifts_evens():
    """Even n is lifted to its odd part first."""
    assert sector_progression(6) == sector_progression(3)
    assert sector_progression(40) == sector_progression(5)


def test_sector_progression_decrements_by_one():
    """Walking the orbit, each consecutive sector value differs by -1 (mod 12)."""
    for n in [3, 7, 11, 17, 27, 41]:
        prog = sector_progression(n)
        for i in range(1, len(prog)):
            assert prog[i] == (prog[i - 1] - 1) % 12, f"n={n}, step {i}: {prog}"


def test_sector_progression_first_element_matches_sector_lens():
    """First element of progression equals the sector lens output."""
    from collatz.embeddings.lenses import sector

    for n in [3, 5, 7, 11, 17, 27]:
        assert sector_progression(n)[0] == sector(n)


# ---- joint_progression ---------------------------------------------------


def test_joint_progression_3():
    """3 -> 5 -> 1: sectors (2,1,0), mod3 (0,2,1)."""
    assert joint_progression(3) == ((2, 0), (1, 2), (0, 1))


def test_joint_progression_n_one():
    """n=1: single element with sector 0 and mod3 1."""
    assert joint_progression(1) == ((0, 1),)


def test_joint_progression_length_matches_sector_progression():
    for n in [3, 5, 7, 11, 17, 27, 41]:
        assert len(joint_progression(n)) == len(sector_progression(n))


def test_joint_progression_sector_axis_matches_sector_progression():
    for n in [3, 5, 7, 11, 17, 27]:
        sec_only = tuple(s for s, _ in joint_progression(n))
        assert sec_only == sector_progression(n)


# ---- edit_distance --------------------------------------------------------


def test_edit_distance_identical():
    assert edit_distance("abc", "abc") == 0
    assert edit_distance((), ()) == 0
    assert edit_distance((1, 2, 3), (1, 2, 3)) == 0


def test_edit_distance_substitution():
    assert edit_distance("abc", "abd") == 1


def test_edit_distance_insertion():
    assert edit_distance("abc", "abcd") == 1
    assert edit_distance("abcd", "abc") == 1


def test_edit_distance_full_delete():
    assert edit_distance("abc", "") == 3
    assert edit_distance("", "abc") == 3


def test_edit_distance_works_on_tuples():
    assert edit_distance((1, 2, 3), (1, 2, 4)) == 1
    assert edit_distance((1, 2, 3), (1, 2)) == 1


def test_edit_distance_classical_kitten_sitting():
    """Classic textbook example: Levenshtein distance is 3."""
    assert edit_distance("kitten", "sitting") == 3


# ---- normalized_edit_distance --------------------------------------------


def test_normalized_in_unit_interval():
    for s1, s2 in [("abc", "abc"), ("abc", ""), ("abc", "xyz"), ("kitten", "sitting")]:
        d = normalized_edit_distance(s1, s2)
        assert 0.0 <= d <= 1.0


def test_normalized_zero_for_identical():
    assert normalized_edit_distance("abc", "abc") == 0.0


def test_normalized_one_for_disjoint_same_length():
    assert normalized_edit_distance("abc", "xyz") == 1.0


def test_normalized_two_empties_is_zero():
    """Empty vs empty: define as 0 (no edits required)."""
    assert normalized_edit_distance("", "") == 0.0


# ---- progression_distance -----------------------------------------------


def test_progression_distance_self_zero():
    for n in [3, 7, 11, 27]:
        assert progression_distance(n, n) == 0.0
        assert progression_distance(n, n, joint=True) == 0.0


def test_progression_distance_in_unit_interval():
    for a, b in [(3, 7), (5, 27), (11, 41)]:
        d = progression_distance(a, b)
        dj = progression_distance(a, b, joint=True)
        assert 0.0 <= d <= 1.0
        assert 0.0 <= dj <= 1.0


def test_progression_distance_syracuse_shift_small():
    """progression_distance(c, T_syr(c)) is small but non-zero — one step removed.

    For odd n with orbit length L, T_syr(n) has orbit length L-1 and a shifted
    sector progression. Edit distance: prefix differs by exactly one element
    (the leading sector), then everything else aligns.
    """
    for n in [7, 11, 17, 27]:
        c = n
        c_shifted = _syr_step(n)
        d = progression_distance(c, c_shifted)
        # one step removed: edit distance = 1 (delete the leading sector)
        # normalized by max length (which is len(prog(c))).
        assert 0.0 < d < 1.0, f"n={n}: dist={d}"


# ---- concept_progression_distance ---------------------------------------


def test_concept_progression_distance_self_zero():
    c = Concept("x", (3, 5, 7))
    assert concept_progression_distance(c, c) == 0.0
    assert concept_progression_distance(c, c, joint=True) == 0.0


def test_concept_progression_distance_mismatched_length_raises():
    a = Concept("a", (3, 5))
    b = Concept("b", (3, 5, 7))
    with pytest.raises(ValueError):
        concept_progression_distance(a, b)
    with pytest.raises(ValueError):
        concept_progression_distance(a, b, joint=True)


def test_concept_progression_distance_is_mean_pairwise():
    """Manually compute the mean and verify."""
    c1 = Concept("c1", (3, 5))
    c2 = Concept("c2", (7, 11))
    expected = (progression_distance(3, 7) + progression_distance(5, 11)) / 2
    assert concept_progression_distance(c1, c2) == pytest.approx(expected)


# ---- progression_analogy -------------------------------------------------


def test_progression_analogy_returns_ranked_list():
    a = Concept("a", (3, 5, 7))
    b = Concept("b", (5, 7, 11))
    c = Concept("c", (11, 13, 17))
    cands = [Concept(f"d{i}", (i, i + 2, i + 4)) for i in range(13, 25, 2)]
    ranked = progression_analogy(a, b, c, cands)
    assert len(ranked) == len(cands)
    scores = [s for _, s in ranked]
    # ascending order — best first
    assert scores == sorted(scores)


def test_progression_analogy_self_consistency():
    """If a == b (zero relationship distance), best d should be the candidate
    closest to c (zero distance, i.e., c itself if available)."""
    a = Concept("a", (3, 5, 7))
    c = Concept("c", (11, 13, 17))
    far = Concept("far", (101, 103, 105))
    cands = [c, far]
    ranked = progression_analogy(a, a, c, cands)
    assert ranked[0][0] is c


def test_progression_analogy_joint_and_sector_both_run():
    """Both flag values should produce sensible rankings."""
    a = Concept("a", (3, 5, 7))
    b = Concept("b", (5, 7, 11))
    c = Concept("c", (11, 13, 17))
    cands = [Concept(f"d{i}", (i, i + 2, i + 4)) for i in range(13, 25, 2)]
    r_sec = progression_analogy(a, b, c, cands, joint=False)
    r_joint = progression_analogy(a, b, c, cands, joint=True)
    assert len(r_sec) == len(r_joint) == len(cands)


# ---- nearest_progression -------------------------------------------------


def test_nearest_progression_target_is_top_when_present():
    target = Concept("t", (3, 5, 7))
    others = [Concept(f"o{i}", (i, i + 2, i + 4)) for i in range(13, 25, 2)]
    ranked = nearest_progression(target, [target] + others)
    assert ranked[0][0] is target
    assert ranked[0][1] == 0.0
