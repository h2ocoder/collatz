"""The information-theoretic Schwarzschild radius of Collatz-like maps (SCRUM-65)."""

from collatz.schwarzschild.system import COLLATZ, CollatzLike, WordMap
from collatz.schwarzschild.horizon import (
    bits_destroyed,
    capture_cross_section,
    captured,
    certified_kicks,
    compactness,
    contraction_sums,
    contraction_word,
    contraction_words,
    drop_fraction,
    horizon,
    horizon_table,
    lapse,
    largest_horizon,
    log2_ratio,
    mass_bound,
    word_mass,
)
from collatz.schwarzschild.rates import (
    Path,
    cheapest_climb,
    cramer_exponent,
    drift,
    head_speed,
    information_radius,
    lift_tail,
    longest_fall,
    longest_hover,
    mach_number,
    memory_rate,
    phase,
    place_exponents,
    reach_exponent,
    size_steps,
    stagnation_radius,
    step_sigma,
    tail_constant,
    tilted_law,
    trapping_radius,
    weak_field_exponent,
)
from collatz.schwarzschild.tape import absorb, causal_depth, emit, erased_bits, page_curve

__all__ = [
    "COLLATZ", "CollatzLike", "WordMap",
    "bits_destroyed", "capture_cross_section", "captured", "certified_kicks", "compactness",
    "contraction_sums", "contraction_word", "contraction_words", "drop_fraction", "horizon",
    "horizon_table", "lapse",
    "largest_horizon", "log2_ratio", "mass_bound", "word_mass",
    "Path", "cheapest_climb", "cramer_exponent", "drift", "head_speed", "information_radius",
    "lift_tail", "longest_fall", "longest_hover", "mach_number", "memory_rate", "phase",
    "place_exponents", "reach_exponent", "size_steps", "stagnation_radius", "step_sigma",
    "tail_constant", "tilted_law", "trapping_radius", "weak_field_exponent",
    "absorb", "causal_depth", "emit", "erased_bits", "page_curve",
]
