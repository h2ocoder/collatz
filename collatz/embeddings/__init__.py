"""Collatz Embeddings: lens-bundle embeddings of integer vectors as concepts.

See docs/superpowers/specs/2026-04-30-collatz-embeddings-design.md.
"""

from .concept import Concept, Phi, Phi_angular
from .iteration import T, T_syracuse, advance_lens
from .keys import (
    concept_coset_distance,
    coset_distance,
    key_signature,
    keys_analogy,
    subgroup_id,
)
from .lenses import LENS_REGISTRY
from .progression import (
    concept_progression_distance,
    edit_distance,
    joint_progression,
    nearest_progression,
    normalized_edit_distance,
    progression_analogy,
    progression_distance,
    sector_progression,
)
from .style import (
    alpha_histogram,
    concept_style_distance,
    mod3_transition_histogram,
    nearest_style,
    style_analogy,
    style_distance,
    style_fingerprint,
)
from .trajectory import (
    concept_orbit_distance,
    jaccard,
    orbit_distance,
    orbit_set,
    syracuse_orbit,
    trajectory_analogy,
)

__all__ = [
    "Concept",
    "LENS_REGISTRY",
    "Phi",
    "Phi_angular",
    "T",
    "T_syracuse",
    "advance_lens",
    # trajectory (v6)
    "concept_orbit_distance",
    "jaccard",
    "orbit_distance",
    "orbit_set",
    "syracuse_orbit",
    "trajectory_analogy",
    # keys (v8a)
    "concept_coset_distance",
    "coset_distance",
    "key_signature",
    "keys_analogy",
    "subgroup_id",
    # style (v8b)
    "alpha_histogram",
    "concept_style_distance",
    "mod3_transition_histogram",
    "nearest_style",
    "style_analogy",
    "style_distance",
    "style_fingerprint",
    # progression (v8c)
    "concept_progression_distance",
    "edit_distance",
    "joint_progression",
    "nearest_progression",
    "normalized_edit_distance",
    "progression_analogy",
    "progression_distance",
    "sector_progression",
]
