"""Concept dataclass and Phi() stacking embedding."""

from dataclasses import dataclass

import numpy as np


def one_hot(value: int, cardinality: int) -> np.ndarray:
    """One-hot vector of length `cardinality`. Out-of-range values clamp to last bucket.

    Example: one_hot(0, 3) = [1, 0, 0]; one_hot(7, 3) = [0, 0, 1].
    """
    idx = max(0, min(int(value), cardinality - 1))
    v = np.zeros(cardinality, dtype=np.float64)
    v[idx] = 1.0
    return v


@dataclass(frozen=True)
class Concept:
    """A named integer vector. Default convention: m=3 components.

    The vector encodes the concept; meaning emerges from the lens projections.
    """

    name: str
    vec: tuple[int, ...]

    def __post_init__(self):
        if not isinstance(self.vec, tuple):
            object.__setattr__(self, "vec", tuple(self.vec))
        if len(self.vec) == 0:
            raise ValueError("Concept must have at least one component")
        if not all(isinstance(x, int) for x in self.vec):
            raise TypeError("Concept components must all be ints")

    @property
    def m(self) -> int:
        return len(self.vec)


def _encode_lens_value(spec, value) -> np.ndarray:
    """Encode one lens output for one component as a flat float vector."""
    if spec.name == "alpha_prefix":
        parts = [one_hot(v, spec.cardinality) for v in value]
        return np.concatenate(parts)
    if spec.kind == "discrete":
        return one_hot(int(value), spec.cardinality)
    return np.array([float(value)], dtype=np.float64)


def Phi(c: Concept) -> np.ndarray:
    """Embed a Concept into lens space as a flat float64 ndarray of shape (m*D,).

    D is the sum of per-lens encoded sizes (one-hot for discrete, scalar for real).
    """
    from collatz.embeddings.lenses import LENS_REGISTRY

    rows = []
    for n in c.vec:
        for spec in LENS_REGISTRY:
            rows.append(_encode_lens_value(spec, spec.fn(n)))
    return np.concatenate(rows)
