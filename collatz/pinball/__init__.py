"""Pinball: stopping vectors, the routing table, and an integer decision model."""

from collatz.pinball.vectors import (
    stopping_vector,
    class_coordinates,
    subgroup_direction,
    vector_from_coordinates,
)
from collatz.pinball.table import PinballTable
from collatz.pinball.encode import launch_integer, integer_bits, encode_state, hash_bits, text_tokens
from collatz.pinball.model import PinballModel, Decision, bit_scores, fixed_point
from collatz.pinball.nesting import (
    drop_chain, drop_tree, realizing_residue, undrained_count, undrained_growth_rate, entropy_dimension,
)
from collatz.pinball.hilbert import terras_preimage_counts, class_densities

__all__ = [
    "stopping_vector", "class_coordinates", "subgroup_direction", "vector_from_coordinates",
    "PinballTable", "launch_integer", "integer_bits", "encode_state", "hash_bits", "text_tokens",
    "PinballModel", "Decision", "bit_scores", "fixed_point",
    "terras_preimage_counts", "class_densities",
    "drop_chain", "drop_tree", "realizing_residue", "undrained_count", "undrained_growth_rate",
    "entropy_dimension",
]
