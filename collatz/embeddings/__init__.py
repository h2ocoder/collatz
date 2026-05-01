"""Collatz Embeddings: lens-bundle embeddings of integer vectors as concepts.

See docs/superpowers/specs/2026-04-30-collatz-embeddings-design.md.
"""

from .concept import Concept, Phi, Phi_angular
from .iteration import T, T_syracuse, advance_lens
from .lenses import LENS_REGISTRY

__all__ = [
    "Concept",
    "LENS_REGISTRY",
    "Phi",
    "Phi_angular",
    "T",
    "T_syracuse",
    "advance_lens",
]
