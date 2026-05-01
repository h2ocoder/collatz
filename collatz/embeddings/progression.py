"""Progression embedding: orbits as sequences over a finite alphabet, compared
with edit distance.

Distinct from trajectory.py: trajectory uses orbit SETS (Jaccard, order-free).
Progression uses orbit SEQUENCES with edit distance (order-sensitive,
tempo-flexible via insertion/deletion).

Musical intuition: a chord progression is a *sequence* over a finite alphabet of
chords; two songs that share a progression sound related even if they differ in
key or style. Edit distance is tempo-flexible (insertions/deletions handle
different orbit lengths) but progression-strict (substitutions cost — two
progressions that differ in step k incur cost).

For Collatz, the natural finite alphabet is sector (Z/12) along the Syracuse
orbit; richer alphabets like sector x mod3 capture more state.
"""

from collections.abc import Iterable, Sequence

from collatz.core import alpha_sequence
from collatz.embeddings.concept import Concept
from collatz.embeddings.iteration import _syr_step
from collatz.embeddings.lenses import _odd_part, mod3


def sector_progression(n: int) -> tuple[int, ...]:
    """Sequence of sector values along n's Syracuse orbit.

    sector(x) = number of Syracuse steps from x to 1, mod 12. Walking the orbit
    of n with L = len(alpha_sequence(odd_part(n))) Syracuse steps, sectors visited
    are L mod 12, (L-1) mod 12, ..., 1 mod 12, 0.

    For even n, lifts to the odd part first. For n=1, returns (0,).

    Example:
        sector_progression(3) = (2, 1, 0)        # alpha_seq=[1,4], L=2
        sector_progression(7) = (5, 4, 3, 2, 1, 0)  # alpha_seq=[1,1,2,3,4], L=5
    """
    if n <= 0:
        raise ValueError(f"sector_progression requires n > 0, got {n}")
    n = _odd_part(n)
    if n == 1:
        return (0,)
    L = len(alpha_sequence(n))
    return tuple((L - i) % 12 for i in range(L + 1))


def joint_progression(n: int) -> tuple[tuple[int, int], ...]:
    """Richer alphabet: sequence of (sector, mod3) pairs along the Syracuse orbit.

    Captures the joint state Z/12 x Z/3, period 36 in principle. The sector axis
    rotates deterministically (-1 mod 12 per step); the mod3 axis depends on the
    actual visited integers.

    For even n, lifts to the odd part. For n=1, returns ((0, 1),).

    Example:
        joint_progression(3) = ((2, 0), (1, 2), (0, 1))   # 3 -> 5 -> 1
    """
    if n <= 0:
        raise ValueError(f"joint_progression requires n > 0, got {n}")
    n = _odd_part(n)
    if n == 1:
        return ((0, mod3(1)),)
    seq: list[tuple[int, int]] = []
    L = len(alpha_sequence(n))
    cur = n
    seq.append((L % 12, mod3(cur)))
    for i in range(1, L + 1):
        cur = _syr_step(cur)
        seq.append(((L - i) % 12, mod3(cur)))
    return tuple(seq)


def edit_distance(s1: Sequence, s2: Sequence) -> int:
    """Standard Levenshtein edit distance over sequences of hashable items.

    Insertion, deletion, and substitution each cost 1. Returns the minimum
    number of single-element edits to transform s1 into s2.

    O(len(s1) * len(s2)) time, O(min(len(s1), len(s2))) space.

    Example:
        edit_distance("abc", "abc") == 0
        edit_distance("abc", "abd") == 1
        edit_distance("abc", "abcd") == 1
        edit_distance("abc", "") == 3
    """
    a = list(s1)
    b = list(s2)
    if len(a) < len(b):
        a, b = b, a
    # a is now the longer (or equal-length) one.
    if not b:
        return len(a)

    # Two-row DP: previous row, current row.
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cost_sub = prev[j - 1] + (0 if ca == cb else 1)
            cost_del = prev[j] + 1
            cost_ins = curr[j - 1] + 1
            curr[j] = min(cost_sub, cost_del, cost_ins)
        prev = curr
    return prev[-1]


def normalized_edit_distance(s1: Sequence, s2: Sequence) -> float:
    """Edit distance normalized by max(len(s1), len(s2)) to give a [0, 1] score.

    Returns 0.0 for identical sequences, 1.0 for completely disjoint sequences
    of unequal alphabets, and intermediate values otherwise. Returns 0.0 for
    two empty sequences.
    """
    m = max(len(s1), len(s2))
    if m == 0:
        return 0.0
    return edit_distance(s1, s2) / m


def progression_distance(n1: int, n2: int, joint: bool = False) -> float:
    """Normalized edit distance between two integers' Syracuse progressions.

    If joint=False, compares sector_progression sequences (Z/12 alphabet).
    If joint=True, compares joint_progression sequences (Z/12 x Z/3 alphabet).

    Returns a value in [0, 1]; 0 means identical progressions, 1 means
    completely disjoint sequences (per max-length normalization).
    """
    if joint:
        s1 = joint_progression(n1)
        s2 = joint_progression(n2)
    else:
        s1 = sector_progression(n1)
        s2 = sector_progression(n2)
    return normalized_edit_distance(s1, s2)


def concept_progression_distance(c1: Concept, c2: Concept, joint: bool = False) -> float:
    """Mean pairwise progression_distance between paired components.

    Components are paired in order. Concepts must have the same length.

    Example:
        c1 = Concept("c1", (3, 5)), c2 = Concept("c2", (7, 11))
        -> mean(progression_distance(3, 7), progression_distance(5, 11))
    """
    if c1.m != c2.m:
        raise ValueError(f"concept lengths differ: {c1.m} vs {c2.m}")
    return sum(progression_distance(a, b, joint=joint) for a, b in zip(c1.vec, c2.vec)) / c1.m


def progression_analogy(
    a: Concept,
    b: Concept,
    c: Concept,
    candidates: Iterable[Concept],
    joint: bool = False,
):
    """Solve a:b :: c:?  Rank candidates d by |dist(c,d) - dist(a,b)|.

    The "relationship" between two concepts is their progression distance; we
    look for a candidate d whose progression-distance to c matches the
    progression-distance from a to b.

    Returns list of (Concept, score) sorted ascending by score (best first;
    score = absolute distance mismatch in [0, 1]).
    """
    target = concept_progression_distance(a, b, joint=joint)
    scored: list[tuple[Concept, float]] = []
    for d in candidates:
        actual = concept_progression_distance(c, d, joint=joint)
        scored.append((d, abs(actual - target)))
    scored.sort(key=lambda x: x[1])
    return scored


def nearest_progression(
    target: Concept,
    candidates: Iterable[Concept],
    joint: bool = False,
):
    """Rank candidates by progression-distance to target. Lower is closer.

    Useful for the "nearest-neighbor in progression space" baseline that strips
    the analogy framing.
    """
    scored: list[tuple[Concept, float]] = [
        (d, concept_progression_distance(target, d, joint=joint)) for d in candidates
    ]
    scored.sort(key=lambda x: x[1])
    return scored
