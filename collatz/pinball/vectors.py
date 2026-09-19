"""Stopping vectors: a launched ball as a lattice point.

The stopping vector of n is (n, *stopping_orbit(n)) -- the launch value
followed by every value up to and including the stopping destination.
A member of stopping class k is therefore a point of Z^(k+1).

By the proved Affine Orbit Structure (docs/Conjectures/Affine Orbit
Structure.md) every coordinate is an affine function of n inside a residue
subgroup, so each subgroup is a lattice LINE in Z^(k+1):

    stopping_vector(residue + j*P) = base + (j - j0) * direction,   P = 2^(k-s)

and (k, s, residue, j) are unique coordinates for n -- the 'factorization'
of a class member.
"""

from collatz.core import stopping_orbit


def stopping_vector(n: int) -> list[int]:
    """Return [n, f(n), ..., d]: n followed by its stopping orbit.

    Example: stopping_vector(5) = [5, 16, 8, 4]   (stopping class 3)
    Example: stopping_vector(3) = [3, 10, 5, 16, 8, 4, 2]   (class 6)
    """
    return [n] + stopping_orbit(n)


def class_coordinates(n: int) -> tuple[int, int, int, int]:
    """Return (k, s, residue, j) with n = residue + j * 2^(k-s).

    k = stopping class, s = odd values among the first k entries of the
    stopping vector, residue = n mod 2^(k-s), j = index along the subgroup line.

    Example: class_coordinates(5) = (3, 1, 1, 1)   -- 5 = 1 + 1*4
    Example: class_coordinates(19) = (6, 2, 3, 1)  -- 19 = 3 + 1*16
    """
    vec = stopping_vector(n)
    k = len(vec) - 1
    s = sum(1 for v in vec[:-1] if v % 2 == 1)
    period = 2 ** (k - s)
    return (k, s, n % period, n // period)


def subgroup_direction(n: int) -> list[int]:
    """Integer direction vector of the subgroup line through n.

    Component i is 2^(k-s) * 3^(odd steps before i) / 2^(halvings before i):
    the change in coordinate i when n advances to the next subgroup member.

    Example: subgroup_direction(5) = [4, 12, 6, 3]
             (stopping_vector(9) - stopping_vector(5) = [4, 12, 6, 3])
    """
    vec = stopping_vector(n)
    k, s, _, _ = class_coordinates(n)
    d = 2 ** (k - s)
    direction = [d]
    for v in vec[:-1]:
        d = 3 * d if v % 2 == 1 else d // 2
        direction.append(d)
    return direction


def vector_from_coordinates(k: int, s: int, residue: int, j: int) -> list[int]:
    """Inverse of class_coordinates, built along the subgroup line.

    Uses the smallest subgroup member > 1 as the base point and steps
    (j - j0) times along subgroup_direction -- no orbit of the target is run.

    Example: vector_from_coordinates(3, 1, 1, 1) = [5, 16, 8, 4]
    """
    period = 2 ** (k - s)
    j0 = 0 if residue > 1 else 1
    base_n = residue + j0 * period
    if class_coordinates(base_n)[:3] != (k, s, residue):
        raise ValueError(f"({k}, {s}, {residue}) is not a subgroup of class {k}")
    base = stopping_vector(base_n)
    direction = subgroup_direction(base_n)
    return [b + (j - j0) * d for b, d in zip(base, direction)]
