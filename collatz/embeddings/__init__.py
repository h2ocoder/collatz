"""Collatz Embeddings: lens-bundle embeddings of integer vectors as concepts.

See docs/superpowers/specs/2026-04-30-collatz-embeddings-design.md.
"""

from .concept import Concept, Phi, Phi_angular
from .iteration import T, T_syracuse, advance_lens
from .lenses import LENS_REGISTRY
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
    "concept_orbit_distance",
    "jaccard",
    "orbit_distance",
    "orbit_set",
    "syracuse_orbit",
    "trajectory_analogy",
]
