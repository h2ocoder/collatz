"""Tests for collatz.embeddings.style — orbit style fingerprint embedding."""

import math

import pytest

from collatz.embeddings.concept import Concept
from collatz.embeddings.style import (
    alpha_histogram,
    concept_style_distance,
    mod3_transition_histogram,
    nearest_style,
    style_analogy,
    style_distance,
    style_fingerprint,
)


# ---- alpha_histogram ----------------------------------------------------


def test_alpha_histogram_length():
    """Default max_alpha=8 -> length 9."""
    assert len(alpha_histogram(7)) == 9
    assert len(alpha_histogram(7, max_alpha=4)) == 5


def test_alpha_histogram_is_pmf_for_normal_n():
    for n in [3, 5, 7, 11, 27, 41, 1023]:
        h = alpha_histogram(n)
        assert all(x >= 0 for x in h), f"negative bin for n={n}"
        assert math.isclose(sum(h), 1.0, abs_tol=1e-12), f"PMF doesn't sum to 1 for n={n}"


def test_alpha_histogram_n3():
    """alpha_sequence(3) = [1, 4]; bin 1 -> 0.5, bin 4 -> 0.5."""
    h = alpha_histogram(3)
    assert h[1] == 0.5
    assert h[4] == 0.5
    assert sum(h[i] for i in [0, 2, 3, 5, 6, 7, 8]) == 0.0


def test_alpha_histogram_n7():
    """alpha_sequence(7) = [1, 1, 2, 3, 4]; bins 1->2/5, 2->1/5, 3->1/5, 4->1/5."""
    h = alpha_histogram(7)
    assert math.isclose(h[1], 2 / 5)
    assert math.isclose(h[2], 1 / 5)
    assert math.isclose(h[3], 1 / 5)
    assert math.isclose(h[4], 1 / 5)


def test_alpha_histogram_clamps_high_alphas():
    """Alphas >= max_alpha should clamp into the last bin."""
    # For n=3 alpha_sequence is [1, 4]; max_alpha=2 forces 4 into bin 2.
    h = alpha_histogram(3, max_alpha=2)
    assert len(h) == 3
    # Bin 1 -> 0.5 (alpha=1), bin 2 -> 0.5 (alpha=4 clamped).
    assert h[1] == 0.5
    assert h[2] == 0.5


def test_alpha_histogram_n1_sentinel_zero():
    """For n=1 (no Syracuse steps) we return all zeros as sentinel."""
    h = alpha_histogram(1)
    assert all(x == 0.0 for x in h)


def test_alpha_histogram_even_lifts_to_odd():
    """alpha_histogram is the same on n and on _odd_part(n)."""
    assert alpha_histogram(6) == alpha_histogram(3)
    assert alpha_histogram(40) == alpha_histogram(5)


def test_alpha_histogram_rejects_nonpositive():
    with pytest.raises(ValueError):
        alpha_histogram(0)
    with pytest.raises(ValueError):
        alpha_histogram(-3)


# ---- mod3_transition_histogram ------------------------------------------


def test_mod3_transition_length_4():
    h = mod3_transition_histogram(7)
    assert len(h) == 4


def test_mod3_transition_is_pmf_when_defined():
    """For orbits with >= 2 in-{1,2} odd values, returns a PMF summing to 1."""
    for n in [7, 9, 11, 15, 27, 41, 137]:
        h = mod3_transition_histogram(n)
        assert all(x >= 0 for x in h), f"negative bin for n={n}"
        assert math.isclose(sum(h), 1.0, abs_tol=1e-12), f"not PMF for n={n}"


def test_mod3_transition_n7():
    """orbit(7) = (7, 11, 17, 13, 5, 1); residues post-{0,1} filter = [1, 2, 2, 1, 2].

    Transitions: (1,2), (2,2), (2,1), (1,2). Counts: (1,1)=0, (1,2)=2, (2,1)=1, (2,2)=1.
    """
    h = mod3_transition_histogram(7)
    assert h == (0.0, 0.5, 0.25, 0.25)


def test_mod3_transition_n15():
    """orbit(15) = (15, 23, 35, 53, 5, 1); residues = [2, 2, 2, 2] (15 dropped, 1 dropped).

    All transitions are (2, 2): PMF (0, 0, 0, 1).
    """
    h = mod3_transition_histogram(15)
    assert h == (0.0, 0.0, 0.0, 1.0)


def test_mod3_transition_n1_sentinel_zero():
    h = mod3_transition_histogram(1)
    assert h == (0.0, 0.0, 0.0, 0.0)


def test_mod3_transition_short_orbit_sentinel():
    """n=3 has orbit (3, 5, 1); residues post-filter = [2]; <2 entries -> sentinel."""
    h = mod3_transition_histogram(3)
    assert h == (0.0, 0.0, 0.0, 0.0)


def test_mod3_transition_rejects_nonpositive():
    with pytest.raises(ValueError):
        mod3_transition_histogram(0)


# ---- style_fingerprint --------------------------------------------------


def test_style_fingerprint_length_default():
    """Default max_alpha=8 -> 9 + 4 = 13."""
    assert len(style_fingerprint(7)) == 13


def test_style_fingerprint_length_custom():
    assert len(style_fingerprint(7, max_alpha=4)) == 5 + 4


def test_style_fingerprint_sum_is_2_for_normal_orbit():
    """Both pieces sum to 1 for a normal orbit -> total sums to 2."""
    for n in [7, 9, 11, 13, 15, 27]:
        assert math.isclose(sum(style_fingerprint(n)), 2.0, abs_tol=1e-12)


# ---- style_distance -----------------------------------------------------


def test_style_distance_self_zero():
    for n in [3, 7, 11, 27, 41]:
        assert style_distance(n, n) == 0.0


def test_style_distance_nonneg_and_bounded():
    pairs = [(3, 5), (7, 11), (3, 27), (5, 9), (15, 27), (41, 137)]
    for n1, n2 in pairs:
        d = style_distance(n1, n2)
        assert d >= 0.0, f"negative distance for {n1},{n2}"
        assert d <= 1.0, f"distance > 1 for {n1},{n2}"


def test_style_distance_symmetric():
    for n1, n2 in [(3, 5), (7, 27), (15, 41)]:
        assert math.isclose(style_distance(n1, n2), style_distance(n2, n1))


def test_style_distance_similar_orbits_close():
    """Two integers in the same Set_3 subgroup (n=1 mod 4) should share dynamics
    in their first few alphas, leading to small style_distance.

    5, 21, 85 are all in Set_3 (alpha_seq starts with [a, ...] where the orbit
    drops within 3 Syracuse steps). Their fingerprints should be relatively
    similar to each other compared to e.g. fingerprint(27).
    """
    # Compare 7 vs 11: both Set_11 with similar dynamics.
    d_close = style_distance(7, 11)
    # Compare 7 vs 27: very different orbit lengths and alpha distributions.
    d_far = style_distance(7, 27)
    assert d_close < d_far, f"expected 7~11 closer than 7~27, got {d_close} vs {d_far}"


# ---- concept_style_distance ---------------------------------------------


def test_concept_style_distance_self_zero():
    c = Concept("c", (3, 7, 11))
    assert concept_style_distance(c, c) == 0.0


def test_concept_style_distance_length_mismatch_raises():
    a = Concept("a", (3, 5))
    b = Concept("b", (7, 11, 13))
    with pytest.raises(ValueError):
        concept_style_distance(a, b)


def test_concept_style_distance_is_mean_of_pairs():
    a = Concept("a", (7, 27))
    b = Concept("b", (11, 41))
    expected = (style_distance(7, 11) + style_distance(27, 41)) / 2
    assert math.isclose(concept_style_distance(a, b), expected)


# ---- style_analogy and nearest_style ------------------------------------


def test_style_analogy_returns_sorted():
    a = Concept("a", (7,))
    b = Concept("b", (11,))
    c = Concept("c", (13,))
    candidates = [Concept(f"c{n}", (n,)) for n in [9, 15, 17, 19, 21, 25, 27, 41]]
    result = style_analogy(a, b, c, candidates)
    assert len(result) == len(candidates)
    scores = [s for _, s in result]
    assert scores == sorted(scores), "result must be ascending by score"
    # First entry's score should equal the actual mismatch.
    d, score = result[0]
    expected = abs(
        concept_style_distance(c, d) - concept_style_distance(a, b)
    )
    assert math.isclose(score, expected)


def test_nearest_style_returns_closest_first():
    target = Concept("target", (7,))
    candidates = [Concept(f"c{n}", (n,)) for n in [11, 15, 19, 27, 41, 137]]
    result = nearest_style(target, candidates)
    assert len(result) == len(candidates)
    scores = [s for _, s in result]
    assert scores == sorted(scores), "result must be ascending by distance"
