"""Hecke L-function machinery for Collatz exploration on Q(omega).

Phase 1: rational sextic residue character chi_6, smoke-test rail.
Phase 2: bespoke period-12 sector character chi_12 (TBD).

Spec: docs/superpowers/specs/2026-05-07-collatz-l-function-design.md
"""

from .eisenstein import EisensteinInt, norm, conjugate, units, pi, pi_bar
from .characters import (
    TrivialCharacter,
    CubicResidueCharacter,
    SexticResidueCharacter,
    NormPullbackCharacter,
    cubic_character_mod_7,
    sextic_character_mod_7,
)
from .lattice_paths import (
    b_imbalance_term,
    count_by_dest_residue,
    enumerate_subgroups,
    k_of,
    rho_diff_partial,
)

__all__ = [
    "EisensteinInt",
    "norm",
    "conjugate",
    "units",
    "pi",
    "pi_bar",
    "TrivialCharacter",
    "CubicResidueCharacter",
    "SexticResidueCharacter",
    "NormPullbackCharacter",
    "cubic_character_mod_7",
    "sextic_character_mod_7",
    "b_imbalance_term",
    "count_by_dest_residue",
    "enumerate_subgroups",
    "k_of",
    "rho_diff_partial",
]
