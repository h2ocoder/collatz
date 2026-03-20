"""Orbit structure comparison within dropping class groups.

Compare element-wise relationships (ratios, differences, modular equivalences)
between orbits of numbers sharing the same (dropping set, dropping modulus).
"""

from fractions import Fraction

import pandas as pd

from collatz.dropping import dropping_set, dropping_modulus, dropping_orbit


def class_members(set_k, modulus_m, limit):
    """Return sorted list of integers in [2, limit) with given (set, modulus).

    Parameters
    ----------
    set_k : int
        Dropping set (= dropping time).
    modulus_m : int
        Dropping modulus (inner subset index, 0-based).
    limit : int
        Upper bound (exclusive).

    Returns
    -------
    list[int]
        Sorted list of matching integers.
    """
    return sorted(
        n for n in range(2, limit)
        if dropping_set(n) == set_k and dropping_modulus(n) == modulus_m
    )


def aligned_orbits(members):
    """Build a DataFrame of aligned dropping orbits.

    Each row is one member's dropping orbit. All members in the same
    (set, modulus) group produce orbits of equal length, so the result
    is a clean rectangular matrix.

    Parameters
    ----------
    members : list[int]
        Numbers to compute orbits for (should share same set/modulus).

    Returns
    -------
    pd.DataFrame
        Rows = members (indexed by n), columns = orbit positions [0, 1, ...].
    """
    orbits = {n: dropping_orbit(n) for n in members}
    return pd.DataFrame.from_dict(orbits, orient="index").sort_index()


def pairwise_ratios(orbit_df):
    """Compute element-wise ratios relative to the first member's orbit.

    For each position i and member j: ratio = orbit[j][i] / orbit[0][i].
    Uses Fraction for exact rational arithmetic.

    Parameters
    ----------
    orbit_df : pd.DataFrame
        Output of aligned_orbits().

    Returns
    -------
    pd.DataFrame
        Same shape, values are Fraction instances.
    """
    ref = orbit_df.iloc[0]
    return orbit_df.apply(
        lambda row: [Fraction(int(row[c]), int(ref[c])) for c in orbit_df.columns],
        axis=1,
        result_type="expand",
    )


def pairwise_differences(orbit_df):
    """Compute element-wise differences relative to the first member's orbit.

    For each position i and member j: diff = orbit[j][i] - orbit[0][i].

    Parameters
    ----------
    orbit_df : pd.DataFrame
        Output of aligned_orbits().

    Returns
    -------
    pd.DataFrame
        Same shape, integer differences.
    """
    ref = orbit_df.iloc[0]
    return orbit_df.subtract(ref)
