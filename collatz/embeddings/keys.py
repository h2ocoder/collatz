"""Coset-quotient (keys) embedding: 'same song, different key' equivalence.

Two integers are 'in the same key' if they live in the same affine subgroup
of Set_k -- i.e., share the same affine map dest(n) = alpha*n + C. This is
the Collatz analog of musical transposition equivalence.

Background: the proved Affine Orbit Structure (docs/Conjectures/Affine Orbit
Structure.md) shows that within each subgroup of Set_k, the dropping
destination is an exact affine function of n with universal slope
alpha = 3^s / 2^(k-s) where s = orbital_oddity. The subgroup is the set
of integers sharing a residue mod 2^(k-s); two integers in the same
subgroup share the SAME alpha and the SAME C, i.e. the same affine map.

Musically: the subgroup IS the key. Integers in the same subgroup of Set_k
produce identical Syracuse progressions (just at different absolute pitches).
"""

import math

from collatz.dropping import dropping_time, orbital_oddity
from collatz.embeddings.concept import Concept


def subgroup_id(n: int) -> tuple[int, int, int]:
    """Return (k, s, residue) uniquely identifying n's affine subgroup.

    k = dropping_time(n)
    s = orbital_oddity(n) (count of odd values in dropping orbit)
    residue = n mod 2^(k-s)

    Two integers with the same (k, s, residue) are in the same subgroup of Set_k
    and share the same affine orbit law dest(n) = alpha*n + C with
    alpha = 3^s / 2^(k-s).

    For n = 1, return (0, 0, 1) as a sentinel (1 has no dropping orbit).

    Example: subgroup_id(5) = (3, 1, 1) -- in Set_3, s=1, residue 1 mod 4.
    Same subgroup as 9, 13, 17, 21, 25, 29 (all n=1 mod 4 with k=3).

    Example: subgroup_id(3) = (6, 2, 3) -- in Set_6, s=2, residue 3 mod 16.
    Same subgroup as 19, 35, 51, 67, 83, 99 (all n=3 mod 16 with k=6).
    """
    if n <= 0:
        raise ValueError(f"subgroup_id requires n > 0, got {n}")
    if n == 1:
        return (0, 0, 1)
    k = dropping_time(n)
    s = orbital_oddity(n)
    period = 2 ** (k - s)
    residue = n % period
    return (k, s, residue)


def key_signature(n: int) -> tuple[float, int, int]:
    """Return (slope_log, k, s) -- the affine-class identity (key family).

    slope_log = s*log2(3) - (k - s)

    This is log2(alpha) where alpha = 3^s / 2^(k-s) is the universal
    affine slope of the subgroup. Two integers in the same Set_k with the
    same s share key_signature (slope_log is the same), but may live in
    different subgroups (different residues mod 2^(k-s)).

    Two integers with the same key_signature are in the same 'key family'
    -- their orbit dynamics scale by the same factor under one drop --
    even if not the same key (subgroup).

    For n = 1, return (0.0, 0, 0) as a sentinel.
    """
    if n <= 0:
        raise ValueError(f"key_signature requires n > 0, got {n}")
    if n == 1:
        return (0.0, 0, 0)
    k = dropping_time(n)
    s = orbital_oddity(n)
    slope_log = s * math.log2(3) - (k - s)
    return (slope_log, k, s)


def coset_distance(n1: int, n2: int) -> float:
    """Discrete coset-aware distance in [0, 1].

    Same subgroup (same k, s, residue mod 2^(k-s)) -> 0.0
    Same Set_k same s but different residue -> 0.25
    Same Set_k different s -> 0.5  (rare; many Set_k have a single s value)
    Different Set_k -> 1.0

    For n=1 vs anything (other than 1) -> 1.0.
    For n=1 vs n=1 -> 0.0.
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError(f"coset_distance requires positive integers, got {n1}, {n2}")

    id1 = subgroup_id(n1)
    id2 = subgroup_id(n2)

    if id1 == id2:
        return 0.0

    # Sentinel n=1 cases: if exactly one is the sentinel, max distance.
    if id1[0] == 0 or id2[0] == 0:
        return 1.0

    k1, s1, _ = id1
    k2, s2, _ = id2

    if k1 != k2:
        return 1.0
    # Same Set_k from here.
    if s1 != s2:
        return 0.5
    # Same k, same s, different residue.
    return 0.25


def concept_coset_distance(c1: Concept, c2: Concept) -> float:
    """Mean pairwise coset_distance between paired components of c1 and c2.

    Components are paired in order. Concepts must have the same length.

    Returns a float in [0, 1] (mean of per-pair coset_distance values).
    """
    if c1.m != c2.m:
        raise ValueError(f"concept lengths differ: {c1.m} vs {c2.m}")
    return sum(coset_distance(a, b) for a, b in zip(c1.vec, c2.vec)) / c1.m


def keys_analogy(
    a: Concept, b: Concept, c: Concept, candidates: list[Concept]
) -> list[tuple[Concept, float]]:
    """Solve a:b :: c:?  Rank candidates d by |coset_dist(c, d) - coset_dist(a, b)|.

    The 'relationship' between two concepts is their concept_coset_distance;
    we look for a candidate d whose distance from c matches the distance from
    a to b. Same idea as trajectory_analogy but in coset space.

    Returns list of (Concept, score) sorted by score *ascending* (best first;
    score = absolute distance mismatch).
    """
    target = concept_coset_distance(a, b)
    scored = []
    for d in candidates:
        actual = concept_coset_distance(c, d)
        scored.append((d, abs(actual - target)))
    scored.sort(key=lambda x: x[1])
    return scored
