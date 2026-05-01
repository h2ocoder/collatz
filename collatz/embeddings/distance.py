"""Distance metrics and analogy search in lens space."""

import numpy as np


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity in [-1, 1]; 1 means parallel, 0 orthogonal, -1 antiparallel.

    Returns 0.0 if either vector is zero (no defined direction).
    """
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def l2(a: np.ndarray, b: np.ndarray) -> float:
    """Euclidean distance."""
    return float(np.linalg.norm(a - b))


def weighted(a: np.ndarray, b: np.ndarray, w: np.ndarray) -> float:
    """Weighted cosine: cosine(w*a, w*b). Zero weights ablate axes."""
    return cosine(a * w, b * w)


def ablate_lens(name: str, m: int) -> np.ndarray:
    """Return a weight vector that zeros only the axes of the named lens.

    The vector matches the shape of Phi(c) for a concept of m components.
    """
    from collatz.embeddings.lenses import LENS_REGISTRY

    slices: dict[str, slice] = {}
    offset = 0
    for spec in LENS_REGISTRY:
        if spec.name == "alpha_prefix":
            size = spec.alpha_k * spec.cardinality
        elif spec.kind == "discrete":
            size = spec.cardinality
        else:
            size = 1
        slices[spec.name] = slice(offset, offset + size)
        offset += size
    D = offset

    if name not in slices:
        raise ValueError(f"unknown lens: {name}")

    w = np.ones(m * D, dtype=np.float64)
    sl = slices[name]
    for i in range(m):
        w[i * D + sl.start : i * D + sl.stop] = 0.0
    return w


def analogy(a, b, c, candidates, *, weight: np.ndarray | None = None):
    """Solve a:b :: c:?  Returns candidates ranked by cosine to (Phi(a) - Phi(b) + Phi(c)).

    Returns list of (Concept, score) sorted descending by score.
    """
    from collatz.embeddings import Phi

    target = Phi(a) - Phi(b) + Phi(c)
    scores = []
    for d in candidates:
        v = Phi(d)
        score = weighted(v, target, weight) if weight is not None else cosine(v, target)
        scores.append((d, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores
