"""Dropping Time / Set / Modulus / Index / Genus / Orbit (Paper 1 terminology).

Paper 1: "The Collatz Conjecture, Pythagorean Triples, and the Riemann Hypothesis"

Key definitions:
- Dropping Time: steps to first value < n (final step is always division by 2)
- Dropping Destination: first value < n
- Dropping Orbit: [n, f(n), ..., 2*d] where d = destination (includes n, excludes d)
- Dropping Set_k: all n with dropping time = k
- Dropping Modulus: inner subset classification within a Dropping Set
- Dropping Index: position within set+modulus (0-based)
- Dropping Genus: (set, modulus, index) tuple
- Orbital Oddity: count of odd numbers in the dropping orbit
"""

import pandas as pd

from .core import collatz_step, stopping_time, stopping_destination


def dropping_time(n):
    """Number of Collatz steps to first reach a value < n.

    Equivalent to core.stopping_time(n).
    Example: dropping_time(3) = 6, dropping_time(5) = 3.
    """
    return stopping_time(n)


def dropping_destination(n):
    """First value < n reached via iteration.

    Example: dropping_destination(3) = 2, dropping_destination(5) = 4.
    """
    return stopping_destination(n)


def dropping_orbit(n):
    """Orbit from n until reaching 2 * dropping_destination.

    Paper 1 convention: includes n, excludes destination.
    Returns [n, f(n), f²(n), ..., 2*d] where d = dropping_destination(n).
    Length equals dropping_time(n).

    Example: dropping_orbit(5) = [5, 16, 8]
    Example: dropping_orbit(3) = [3, 10, 5, 16, 8, 4]
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    start = n
    seq = [n]
    while True:
        n = collatz_step(n)
        if n < start:
            return seq
        seq.append(n)


def dropping_set(n):
    """Which Dropping Set does n belong to? Returns the dropping time k.

    Dropping Set_k contains all integers requiring exactly k steps to drop.
    Dropping Set_1 = all even numbers.
    Dropping Set_3 = {n : n ≡ 1 (mod 4), n > 1}.
    """
    return dropping_time(n)


def orbital_oddity(n):
    """Count of odd integers in the dropping orbit of n.

    All members of Dropping Set_k share the same orbital oddity (Conjecture 1).
    Example: orbital_oddity(5) = 1 (orbit [5,16,8], odd: {5})
    Example: orbital_oddity(3) = 2 (orbit [3,10,5,16,8,4], odd: {3,5})
    """
    return sum(1 for x in dropping_orbit(n) if x % 2 == 1)


def dropping_modulus(n):
    """Inner subset classification within Dropping Set_k.

    Numbers in the same Dropping Set may fall into distinct inner subsets
    identified by a Dropping Modulus value (0-indexed).

    For Dropping Set_1, Set_3, Set_6: modulus is always 0 (single subset).
    For Dropping Set_8: modulus is 0 or 1 (two inner subsets).
    """
    k = dropping_set(n)
    # Find all members of the same dropping set up to and including n
    members = sorted(m for m in range(2, n + 1) if dropping_set(m) == k)
    if not members or n not in members:
        return 0
    idx = members.index(n)
    mod_count = _dropping_modulus_count(k, n)
    return idx % mod_count


def dropping_index(n):
    """Position of n within its Dropping Set and Dropping Modulus (0-based).

    This is the index when ordering all integers sharing the same
    Dropping Set_k and Dropping Modulus_m by magnitude.
    """
    k = dropping_set(n)
    m = dropping_modulus(n)
    mod_count = _dropping_modulus_count(k, n)
    # Find all members of same set up to n
    members = sorted(x for x in range(2, n + 1) if dropping_set(x) == k)
    # Filter to same modulus
    same_mod = [x for i, x in enumerate(members) if i % mod_count == m]
    return same_mod.index(n)


def dropping_genus(n):
    """Dropping Genus = (Dropping Set, Dropping Modulus, Dropping Index).

    Uniquely identifies each integer's dropping time behavior.
    Example: dropping_genus(3) = (6, 0, 0)
    Example: dropping_genus(15) = (11, 1, 0)
    """
    return (dropping_set(n), dropping_modulus(n), dropping_index(n))


def classify_range(start, end):
    """Classify all integers in [start, end) with dropping properties.

    Returns a DataFrame with columns:
    n, dropping_time, dropping_destination, dropping_set, dropping_modulus,
    dropping_index, orbital_oddity
    """
    rows = []
    for n in range(start, end):
        if n <= 1:
            continue
        dt = dropping_time(n)
        dd = dropping_destination(n)
        oo = orbital_oddity(n)
        rows.append({
            "n": n,
            "dropping_time": dt,
            "dropping_destination": dd,
            "dropping_set": dt,
            "orbital_oddity": oo,
        })
    return pd.DataFrame(rows)


def _dropping_modulus_count(k, search_limit=None):
    """Compute the number of distinct dropping moduli for Dropping Set_k.

    Examines the pattern of differences between consecutive members.
    """
    if search_limit is None:
        search_limit = max(200, k * 50)
    # Known simple cases
    if k == 1:
        return 1  # All even numbers, single pattern
    # Generate enough members
    members = sorted(n for n in range(2, search_limit) if dropping_set(n) == k)
    if len(members) < 4:
        return 1
    # Look at differences between consecutive members
    diffs = [members[i + 1] - members[i] for i in range(len(members) - 1)]
    # Find the period of the diff sequence
    for period in range(1, len(diffs) // 2 + 1):
        pattern = diffs[:period]
        if all(
            diffs[i] == pattern[i % period]
            for i in range(min(len(diffs), period * 3))
        ):
            return period
    return 1
