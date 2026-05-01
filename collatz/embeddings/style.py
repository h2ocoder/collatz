"""Style fingerprint embedding: statistical fingerprint of orbit local patterns.

Tempo- and key-invariant. Captures what an orbit FEELS like dynamically: the
distribution of step sizes (alphas), the rhythm of mod-3 transitions, the
spectrum of dropping-set passages. Two orbits with similar fingerprints are
'in the same style' even if they're not the same song or key.

Design notes:
- alpha_histogram bins alphas into [0, max_alpha]. Since real alpha values are
  >= 1 for n > 1, index 0 is normally unused (reserved for the sentinel n=1
  convention; see below). Alphas >= max_alpha clamp into the last bin.
- mod3 along the Syracuse orbit on odd values only ever takes values 1 or 2
  (since 3x+1 = 1 mod 3 always, the destination odd part can never be 0 mod 3).
  Transition alphabet is therefore {(1,1), (1,2), (2,1), (2,2)} in that order.
- For n=1 (and any n whose orbit yields no Syracuse step), we return an
  all-zero vector as the sentinel: not a valid PMF but distinguishable from
  any real fingerprint. style_distance treats zero-vectors as 'undefined'
  (returns 1.0 against any non-zero fingerprint).
"""

from collections import Counter

import numpy as np

from collatz.core import alpha_sequence
from collatz.embeddings.concept import Concept
from collatz.embeddings.iteration import _syr_step
from collatz.embeddings.lenses import _odd_part


def alpha_histogram(n: int, max_alpha: int = 8) -> tuple[float, ...]:
    """Empirical PMF of alpha values along n's Syracuse orbit.

    Bin alphas into [0, max_alpha] (alphas >= max_alpha clamp to last bin).
    Returns a tuple of length max_alpha+1 summing to 1.0.

    For n=1 (no Syracuse steps), return an all-zero tuple of length max_alpha+1
    as a sentinel (not a valid PMF; style_distance treats zero-vectors as
    'undefined').

    Example: alpha_histogram(3) bins alpha_sequence(3) = [1, 4]:
        index 1 -> 0.5, index 4 -> 0.5, others 0.
    """
    if n <= 0:
        raise ValueError(f"alpha_histogram requires n > 0, got {n}")
    odd_n = _odd_part(n)
    bins = max_alpha + 1
    if odd_n == 1:
        return tuple([0.0] * bins)
    seq = alpha_sequence(odd_n)
    if not seq:
        return tuple([0.0] * bins)
    counts = np.zeros(bins, dtype=np.float64)
    for a in seq:
        idx = max(0, min(int(a), max_alpha))
        counts[idx] += 1.0
    counts /= counts.sum()
    return tuple(float(x) for x in counts)


def mod3_transition_histogram(n: int) -> tuple[float, ...]:
    """Empirical distribution of (mod3(step_i), mod3(step_{i+1})) pairs along
    n's Syracuse orbit.

    The orbit visits odd integers; after the first Syracuse step every odd
    value is in {1, 2} mod 3 (since 3x+1 mod 3 = 1, the destination odd part
    cannot be 0 mod 3). Only the starting odd value n itself can be 0 mod 3.
    We drop any 0-mod-3 entries from the residue sequence and tally
    transitions among the remaining {1, 2} entries. There are 4 possible
    transitions: (1,1), (1,2), (2,1), (2,2). Returns a length-4 PMF in that
    fixed order.

    For orbits that produce fewer than 2 in-{1,2} entries (i.e. n=1 or
    starting value 3 with orbit (3, 5, 1) -> only 5 is in {1,2} after we drop
    leading 3 and trailing 1), returns (0, 0, 0, 0) as a sentinel.

    Example: orbit(7) = [7, 11, 17, 13, 5, 1]; mod3 sequence on odd values
    excluding the trivial 1 is [1, 2, 2, 1, 2]. Transitions: (1,2), (2,2),
    (2,1), (1,2). Counts: (1,1)=0, (1,2)=2, (2,1)=1, (2,2)=1. PMF: (0, 0.5,
    0.25, 0.25).
    """
    if n <= 0:
        raise ValueError(f"mod3_transition_histogram requires n > 0, got {n}")
    odd_n = _odd_part(n)
    if odd_n == 1:
        return (0.0, 0.0, 0.0, 0.0)
    # Walk the Syracuse orbit collecting odd-value mod3 residues. Exclude the
    # trivial terminating 1 to avoid forcing every fingerprint to end with a
    # `*->1` transition (1 mod 3 = 1).
    odds = [odd_n]
    cur = odd_n
    for _ in alpha_sequence(odd_n):
        cur = _syr_step(cur)
        odds.append(cur)
    if odds and odds[-1] == 1:
        odds = odds[:-1]
    # Drop 0-mod-3 entries (only the leading n can be 0 mod 3).
    residues = [x % 3 for x in odds if x % 3 != 0]
    if len(residues) < 2:
        return (0.0, 0.0, 0.0, 0.0)
    transitions = Counter()
    for a, b in zip(residues[:-1], residues[1:]):
        transitions[(a, b)] += 1
    total = sum(transitions.values())
    if total == 0:
        return (0.0, 0.0, 0.0, 0.0)
    keys = [(1, 1), (1, 2), (2, 1), (2, 2)]
    return tuple(transitions[k] / total for k in keys)


def style_fingerprint(n: int, max_alpha: int = 8) -> tuple[float, ...]:
    """Concatenated fingerprint vector: alpha_histogram | mod3_transition_histogram.

    Length = (max_alpha + 1) + 4 = 13 by default.

    For n with a normal Syracuse orbit (n > 1 odd, or n even with odd part > 1),
    each piece sums to 1.0, so the total sums to 2.0. For n with odd part 1 the
    fingerprint is all zeros (sentinel; not a valid PMF).
    """
    return alpha_histogram(n, max_alpha=max_alpha) + mod3_transition_histogram(n)


def _chi_squared_distance(
    p: np.ndarray, q: np.ndarray, eps: float = 1e-12
) -> float:
    """Symmetric chi-squared distance: sum_i (p_i - q_i)^2 / (p_i + q_i + eps).

    Works on arbitrary non-negative vectors (need not be PMFs). Returns 0 for
    identical vectors. The eps avoids division-by-zero where both bins are zero.
    """
    diff = p - q
    s = p + q + eps
    return float(np.sum(diff * diff / s))


def style_distance(n1: int, n2: int, max_alpha: int = 8) -> float:
    """Chi-squared distance between style fingerprints, normalized to [0, 1].

    Compute on the concatenated fingerprint. Returns 0 for identical
    fingerprints. The chi-squared distance on two PMFs that each sum to 1 is
    bounded above by 2; we concatenate two PMFs (total mass 2) so the upper
    bound is 4. We divide by 4 to land in [0, 1].
    """
    f1 = np.asarray(style_fingerprint(n1, max_alpha=max_alpha), dtype=np.float64)
    f2 = np.asarray(style_fingerprint(n2, max_alpha=max_alpha), dtype=np.float64)
    # If either fingerprint is the all-zero sentinel and the other isn't, the
    # comparison is undefined; report maximum distance (1.0).
    nz1 = bool(np.any(f1))
    nz2 = bool(np.any(f2))
    if nz1 != nz2:
        return 1.0
    if not nz1 and not nz2:
        return 0.0
    return _chi_squared_distance(f1, f2) / 4.0


def concept_style_distance(c1: Concept, c2: Concept, max_alpha: int = 8) -> float:
    """Mean pairwise style_distance between paired components of c1 and c2.

    Components are paired in order. Concepts must have the same length.

    Example: c1 = (3, 5), c2 = (7, 11) ->
        mean(style_distance(3, 7), style_distance(5, 11)).
    """
    if c1.m != c2.m:
        raise ValueError(f"concept lengths differ: {c1.m} vs {c2.m}")
    return sum(
        style_distance(a, b, max_alpha=max_alpha) for a, b in zip(c1.vec, c2.vec)
    ) / c1.m


def style_analogy(
    a: Concept,
    b: Concept,
    c: Concept,
    candidates: list[Concept],
    max_alpha: int = 8,
):
    """Solve a:b :: c:?  Rank candidates d by
        |concept_style_distance(c, d) - concept_style_distance(a, b)|.

    The "relationship" between two concepts is their style distance; we look
    for a candidate d whose style-distance to c matches the style-distance from
    a to b.

    Returns list of (Concept, score) sorted by score *ascending* (best first;
    score = absolute distance mismatch).
    """
    target = concept_style_distance(a, b, max_alpha=max_alpha)
    scored = []
    for d in candidates:
        actual = concept_style_distance(c, d, max_alpha=max_alpha)
        scored.append((d, abs(actual - target)))
    scored.sort(key=lambda x: x[1])
    return scored


def nearest_style(
    target: Concept, candidates: list[Concept], max_alpha: int = 8
):
    """Rank candidates by style similarity to target (ascending distance).

    More natural for style than analogy: 'find concepts that feel like target'.
    Returns list of (Concept, distance) sorted ascending (closest first).
    """
    scored = [
        (d, concept_style_distance(target, d, max_alpha=max_alpha))
        for d in candidates
    ]
    scored.sort(key=lambda x: x[1])
    return scored
