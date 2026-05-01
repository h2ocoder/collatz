"""Trajectory-space embedding: concepts as bags of Syracuse orbits.

Alternative to the lens-bundle Phi embedding. Each integer's Syracuse orbit
(sequence of odd integers visited en route to 1) is a discrete trajectory;
concepts are bags of trajectories; distance is mean pairwise Jaccard.

Sidesteps the cosine-on-one-hot-diffs measurement issue from v2-v4 by working
in set space rather than vector space.
"""

from collections.abc import Iterable

from collatz.core import alpha_sequence
from collatz.embeddings.concept import Concept
from collatz.embeddings.iteration import _syr_step
from collatz.embeddings.lenses import _odd_part


def syracuse_orbit(n: int) -> tuple[int, ...]:
    """Sequence of odd integers visited in n's Syracuse orbit, including the trivial 1.

    Even n is lifted to its odd part first. Lossy in that we drop halving steps
    but lossless in dynamical content (the Syracuse map captures all of Collatz).

    Example: syracuse_orbit(7) = (7, 11, 17, 13, 5, 1)
    Example: syracuse_orbit(3) = (3, 5, 1)
    Example: syracuse_orbit(1) = (1,)
    """
    if n <= 0:
        raise ValueError(f"syracuse_orbit requires n > 0, got {n}")
    n = _odd_part(n)
    seq = [n]
    if n == 1:
        return tuple(seq)
    # alpha_sequence(n) gives one alpha per Syracuse step; we re-walk to get values.
    for _ in alpha_sequence(n):
        n = _syr_step(n)
        seq.append(n)
    return tuple(seq)


def orbit_set(n: int) -> frozenset[int]:
    """Set of odd integers in n's Syracuse orbit. Drops sequence order, keeps support.

    Example: orbit_set(7) = frozenset({1, 5, 7, 11, 13, 17})
    """
    return frozenset(syracuse_orbit(n))


def jaccard(a: Iterable[int], b: Iterable[int]) -> float:
    """Jaccard similarity: |A intersect B| / |A union B|. Returns 0 for empty union.

    Symmetric, in [0, 1]. 1 means identical sets, 0 means disjoint.
    """
    sa, sb = frozenset(a), frozenset(b)
    union = sa | sb
    if not union:
        return 0.0
    return len(sa & sb) / len(union)


def orbit_distance(n1: int, n2: int) -> float:
    """1 - Jaccard of two integers' Syracuse orbit sets. In [0, 1].

    Two integers with identical orbit support have distance 0; with disjoint orbits
    (rare in Collatz since most orbits share the common suffix near 1), distance 1.
    """
    return 1.0 - jaccard(orbit_set(n1), orbit_set(n2))


def concept_orbit_distance(c1: Concept, c2: Concept) -> float:
    """Mean pairwise orbit distance between paired components of c1 and c2.

    Components are paired in order. Concepts must have the same length.

    Example: c1 = (3, 5), c2 = (7, 11) -> mean(orbit_distance(3, 7), orbit_distance(5, 11)).
    """
    if c1.m != c2.m:
        raise ValueError(f"concept lengths differ: {c1.m} vs {c2.m}")
    return sum(orbit_distance(a, b) for a, b in zip(c1.vec, c2.vec)) / c1.m


def trajectory_analogy(a: Concept, b: Concept, c: Concept, candidates: list[Concept]):
    """Solve a:b :: c:?  Rank candidates d by |orbit_dist(c, d) - orbit_dist(a, b)|.

    The "relationship" between two concepts is their orbit distance; we look for
    a candidate d whose orbit-distance to c matches the orbit-distance from a to b.

    Returns list of (Concept, score) sorted by score *ascending* (best first;
    score = absolute distance mismatch).
    """
    target = concept_orbit_distance(a, b)
    scored = []
    for d in candidates:
        actual = concept_orbit_distance(c, d)
        scored.append((d, abs(actual - target)))
    scored.sort(key=lambda x: x[1])
    return scored
