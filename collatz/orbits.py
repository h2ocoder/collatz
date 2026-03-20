"""Orbit structure comparison within dropping class groups.

Compare element-wise relationships (ratios, differences, modular equivalences)
between orbits of numbers sharing the same (dropping set, dropping modulus).
"""

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
