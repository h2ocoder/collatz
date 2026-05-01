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


def _angular(value: int, cardinality: int) -> np.ndarray:
    """Encode a cyclic discrete value as (cos, sin) on the unit circle.

    Smooth alternative to one-hot for lenses whose values rotate predictably
    (notably: sector, which decrements by 1 mod 12 per Syracuse step).
    """
    theta = 2.0 * np.pi * (int(value) % cardinality) / cardinality
    return np.array([np.cos(theta), np.sin(theta)], dtype=np.float64)


def _encode_lens_value(spec, value, *, sector_angular: bool = False) -> np.ndarray:
    """Encode one lens output for one component as a flat float vector."""
    if spec.name == "alpha_prefix":
        parts = [one_hot(v, spec.cardinality) for v in value]
        return np.concatenate(parts)
    if spec.kind == "discrete":
        if sector_angular and spec.name == "sector":
            return _angular(int(value), spec.cardinality)
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


def Phi_angular(c: Concept) -> np.ndarray:
    """Variant of Phi where `sector` is encoded as (cos, sin) on the unit circle.

    Smooth under Syracuse iteration: a -1-mod-12 sector step becomes a
    -30 deg rotation in the sector subspace rather than a one-hot index flip.
    All other lenses unchanged. Vector size is m*(D - 12 + 2) = m*63.
    """
    from collatz.embeddings.lenses import LENS_REGISTRY

    rows = []
    for n in c.vec:
        for spec in LENS_REGISTRY:
            rows.append(_encode_lens_value(spec, spec.fn(n), sector_angular=True))
    return np.concatenate(rows)
