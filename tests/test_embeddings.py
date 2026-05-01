"""Tests for collatz.embeddings package."""

import math

import numpy as np
import pytest

from collatz.embeddings import LENS_REGISTRY, Concept, Phi, T, T_syracuse, advance_lens
from collatz.embeddings.concept import one_hot
from collatz.embeddings.distance import ablate_lens, analogy, cosine, l2, weighted
from collatz.embeddings.lenses import (
    alpha_prefix,
    drop_class,
    force,
    mod3,
    sector,
    slope_log,
)


# ---- Task 1: package import smoke test ----------------------------------


def test_package_imports():
    """The embeddings package and all submodules should import cleanly."""
    from collatz import embeddings  # noqa: F401
    from collatz.embeddings import concept, distance, iteration, lenses  # noqa: F401


# ---- Task 2: mod3 lens ---------------------------------------------------


def test_mod3_basic():
    assert mod3(3) == 0
    assert mod3(7) == 1
    assert mod3(8) == 2
    assert mod3(11) == 2


# ---- Task 3: drop_class lens --------------------------------------------


def test_drop_class_basic():
    assert drop_class(3) == 6
    assert drop_class(5) == 3
    assert drop_class(7) == 11


# ---- Task 4: alpha_prefix lens ------------------------------------------


def test_alpha_prefix_pad_short():
    # alpha_sequence(3) = [1, 4]; pad to length 3 with 0.
    assert alpha_prefix(3, k=3) == (1, 4, 0)


def test_alpha_prefix_truncate_long():
    # alpha_sequence(7) = [1, 1, 2, 3, 4]; truncate to length 3.
    assert alpha_prefix(7, k=3) == (1, 1, 2)


def test_alpha_prefix_default_k():
    assert alpha_prefix(11) == (1, 2, 3)


# ---- Task 5: sector lens ------------------------------------------------


def test_sector_basic():
    assert sector(3) == 2
    assert sector(5) == 1
    assert sector(7) == 5
    assert sector(11) == 4


def test_sector_rotates_under_syracuse_step():
    """One Syracuse step decreases sector by 1 (mod 12)."""
    from collatz.core import alpha_sequence
    from collatz.embeddings.iteration import _syr_step

    for n in [3, 7, 11, 17, 27]:
        if len(alpha_sequence(n)) <= 1:
            continue
        assert sector(_syr_step(n)) == (sector(n) - 1) % 12, f"failed for n={n}"


# ---- Task 6: force, slope_log lenses ------------------------------------


def test_force_basic():
    assert force(3) == 4   # 6 - 2
    assert force(5) == 2   # 3 - 1
    assert force(7) == 7   # 11 - 4


def test_slope_log_matches_formula():
    expected_3 = 2 * math.log2(3) - 4
    assert math.isclose(slope_log(3), expected_3, rel_tol=1e-12)
    expected_5 = 1 * math.log2(3) - 2
    assert math.isclose(slope_log(5), expected_5, rel_tol=1e-12)


# ---- Task 7: registry and one_hot ---------------------------------------


def test_lens_registry_shape():
    names = {spec.name for spec in LENS_REGISTRY}
    assert names == {"sector", "mod3", "drop_class", "alpha_prefix", "force", "slope_log"}
    by_name = {spec.name: spec for spec in LENS_REGISTRY}
    assert by_name["sector"].kind == "discrete" and by_name["sector"].cardinality == 12
    assert by_name["mod3"].kind == "discrete" and by_name["mod3"].cardinality == 3
    assert by_name["force"].kind == "real" and by_name["force"].cardinality is None


def test_one_hot_basic():
    np.testing.assert_array_equal(one_hot(0, 3), np.array([1.0, 0.0, 0.0]))
    np.testing.assert_array_equal(one_hot(2, 3), np.array([0.0, 0.0, 1.0]))


def test_one_hot_clamps_out_of_range():
    np.testing.assert_array_equal(one_hot(7, 3), np.array([0.0, 0.0, 1.0]))


# ---- Task 8: Concept dataclass ------------------------------------------


def test_concept_construction():
    c = Concept("man", (3, 17, 6))
    assert c.name == "man"
    assert c.vec == (3, 17, 6)
    assert c.m == 3


def test_concept_rejects_non_int():
    with pytest.raises(TypeError):
        Concept("bad", (3.5, 17, 6))


def test_concept_rejects_empty():
    with pytest.raises(ValueError):
        Concept("empty", ())


def test_concept_normalizes_list_to_tuple():
    c = Concept("xs", [3, 17, 6])
    assert c.vec == (3, 17, 6)
    assert isinstance(c.vec, tuple)


# ---- Task 9: Phi stacker ------------------------------------------------


# Per-component stride D:
#   sector: 12, mod3: 3, drop_class: 32,
#   alpha_prefix: 3 * 8 = 24, force: 1, slope_log: 1.
# Total: 73.
PER_COMPONENT_D = 73


def test_phi_shape():
    c = Concept("test", (3, 5, 7))
    v = Phi(c)
    assert v.shape == (3 * PER_COMPONENT_D,)


def test_phi_pure_concept_constant_in_anchoring_lenses():
    """Two pure-mod3 concepts with same residue produce identical mod3 segments."""
    a = Concept("a", (1, 4, 7))
    b = Concept("b", (10, 13, 16))
    va = Phi(a)
    vb = Phi(b)
    for i in range(3):
        offset = i * PER_COMPONENT_D + 12
        assert (va[offset:offset + 3] == vb[offset:offset + 3]).all()


def test_phi_returns_float_ndarray():
    v = Phi(Concept("x", (3, 5, 7)))
    assert v.dtype == np.float64


# ---- Task 10: cosine, l2 ------------------------------------------------


def test_cosine_self_is_one():
    v = np.array([1.0, 2.0, 3.0])
    assert math.isclose(cosine(v, v), 1.0)


def test_cosine_orthogonal_is_zero():
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    assert math.isclose(cosine(a, b), 0.0)


def test_l2_self_is_zero():
    v = np.array([1.0, 2.0, 3.0])
    assert math.isclose(l2(v, v), 0.0)


def test_l2_known():
    a = np.array([0.0, 0.0])
    b = np.array([3.0, 4.0])
    assert math.isclose(l2(a, b), 5.0)


# ---- Task 11: weighted, ablate_lens -------------------------------------


def test_weighted_unit_weights_equals_cosine():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([2.0, 1.0, 4.0])
    w = np.ones_like(a)
    assert math.isclose(weighted(a, b, w), cosine(a, b))


def test_weighted_zero_weights_returns_zero_vector_distance():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0])
    w = np.zeros_like(a)
    assert weighted(a, b, w) == 0.0


def test_ablate_lens_zeros_only_target_axes():
    w = ablate_lens("mod3", m=3)
    for i in range(3):
        offset = i * PER_COMPONENT_D
        assert (w[offset + 12 : offset + 15] == 0).all()
        assert (w[offset : offset + 12] == 1).all()


def test_ablate_lens_unknown_raises():
    with pytest.raises(ValueError):
        ablate_lens("not_a_lens", m=3)


# ---- Task 12: analogy ---------------------------------------------------


def test_analogy_returns_ranked_list():
    a = Concept("a", (3, 5, 7))
    b = Concept("b", (5, 7, 9))
    c = Concept("c", (11, 13, 15))
    cands = [Concept(f"d{i}", (i, i + 2, i + 4)) for i in range(13, 25, 2)]
    ranked = analogy(a, b, c, cands)
    assert len(ranked) == len(cands)
    scores = [s for _, s in ranked]
    assert scores == sorted(scores, reverse=True)


def test_analogy_self_consistency():
    """If a == b, target is Phi(c), so c should be top."""
    a = Concept("a", (3, 5, 7))
    c = Concept("c", (11, 13, 15))
    far = Concept("far", (1000, 2000, 3000))
    cands = [c, far]
    ranked = analogy(a, a, c, cands)
    assert ranked[0][0] is c


# ---- Task 13: T, T_syracuse ---------------------------------------------


def test_T_step_each_component():
    c = Concept("man", (3, 17, 6))
    out = T(c)
    assert out.vec == (10, 52, 3)
    assert out.name == "man"


def test_T_syracuse_collapses_evens():
    assert T_syracuse(Concept("x", (3, 5, 6))).vec == (5, 1, 3)


# ---- Task 14: advance_lens ----------------------------------------------


def test_advance_lens_sector_rotates():
    assert advance_lens(2, "sector") == 1
    assert advance_lens(0, "sector") == 11


def test_advance_lens_mod3_not_supported():
    with pytest.raises(ValueError):
        advance_lens(1, "mod3")


def test_advance_lens_unsupported_lens_raises():
    with pytest.raises(ValueError):
        advance_lens(5, "force")
