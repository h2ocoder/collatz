"""Exact affine structure of dropping orbits.

The Affine Orbit Structure theorem (docs/Conjectures/Affine Orbit
Structure.md) proves that within each residue subgroup mod 2^(k-s) of
Dropping Set D_k, every element of the dropping orbit is an exact affine
function of the starting value:

    f^j(n) = a_j * n + b_j,   j = 0 .. k-1,

with (a_0, b_0) = (1, 0) and the recursion

    even step:  (a, b) -> (a/2, b/2)
    odd step:   (a, b) -> (3a, 3b + 1)

The parity word is determined by n mod 2^(k-s), so the coefficient profile
is a subgroup invariant.  Consequently the orbit sum sum_j f^j(n) = A*n + B
and the destination dest(n) = lambda*n + C are affine with subgroup-constant
(A, B, lambda, C).  This module exposes those coefficients exactly (as
Fractions), both from a concrete n and from a subgroup's alpha-tuple
(see collatz/lfunctions/lattice_paths.py).
"""
from __future__ import annotations

from fractions import Fraction

from .core import collatz_step


def affine_orbit_profile(n: int) -> list[tuple[Fraction, Fraction]]:
    """Exact coefficients [(a_j, b_j)] with f^j(n) = a_j*n + b_j for the dropping orbit.

    Follows n's actual parity word until the orbit first drops below n.
    Length equals the dropping time k; the destination (step k) is excluded,
    matching the dropping-orbit convention of `collatz.dropping.dropping_orbit`.

    Example: affine_orbit_profile(5) == [(1, 0), (3, 1), (3/2, 1/2)]
             (orbit 5 -> 16 -> 8 -> 4; three steps, destination excluded)
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    start = n
    a, b = Fraction(1), Fraction(0)
    profile = [(a, b)]
    while True:
        if n % 2 == 0:
            a, b = a / 2, b / 2
        else:
            a, b = 3 * a, 3 * b + 1
        n = collatz_step(n)
        if n < start:
            return profile
        profile.append((a, b))


def affine_destination_coefficients(n: int) -> tuple[Fraction, Fraction]:
    """Exact (lambda, C) with dest(n) = lambda*n + C, constant on n's subgroup.

    Example: affine_destination_coefficients(5) == (Fraction(3, 4), Fraction(1, 4))
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    start = n
    a, b = Fraction(1), Fraction(0)
    while True:
        if n % 2 == 0:
            a, b = a / 2, b / 2
        else:
            a, b = 3 * a, 3 * b + 1
        n = collatz_step(n)
        if n < start:
            return a, b


def orbit_sum(n: int) -> int:
    """Sum of the dropping orbit [n, f(n), ..., f^(k-1)(n)] (destination excluded).

    Example: orbit_sum(5) == 5 + 16 + 8 == 29
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    start = n
    total = n
    while True:
        n = collatz_step(n)
        if n < start:
            return total
        total += n


def orbit_max(n: int) -> int:
    """Maximum of the dropping orbit (destination excluded).

    Example: orbit_max(5) == 16
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    start = n
    peak = n
    while True:
        n = collatz_step(n)
        if n < start:
            return peak
        peak = max(peak, n)


def orbit_sum_coefficients(n: int) -> tuple[Fraction, Fraction]:
    """Exact (A, B) with orbit_sum(m) = A*m + B for every m in n's subgroup.

    Example: orbit_sum_coefficients(5) == (Fraction(11, 2), Fraction(3, 2))
             (A*5 + B = 55/2 + 3/2 = 29 = orbit_sum(5))
    """
    profile = affine_orbit_profile(n)
    return (
        sum(a for a, _ in profile),
        sum(b for _, b in profile),
    )


def profile_from_alphas(alphas: tuple[int, ...]) -> list[tuple[Fraction, Fraction]]:
    """Coefficient profile for the subgroup with alpha-tuple (alpha_1..alpha_s).

    The parity word is: odd step, alpha_1 halvings, odd step, alpha_2
    halvings, ..., odd step, alpha_s halvings — the dropping orbit of any
    n ≡ 3 (mod 4) member (or n ≡ 1 mod 4 for s = 1, alphas = (2,)).
    Length k = s + sum(alphas); destination excluded.
    """
    if not alphas or any(a < 1 for a in alphas):
        raise ValueError("alphas must be a non-empty tuple of positive ints")
    a, b = Fraction(1), Fraction(0)
    profile = [(a, b)]
    for i, alpha in enumerate(alphas):
        a, b = 3 * a, 3 * b + 1
        profile.append((a, b))
        for j in range(alpha):
            a, b = a / 2, b / 2
            # the very last halving lands on the destination, which the
            # dropping orbit excludes
            if i == len(alphas) - 1 and j == alpha - 1:
                return profile
            profile.append((a, b))
    return profile


def subgroup_summary(alphas: tuple[int, ...]) -> dict:
    """Exact affine invariants of one subgroup, keyed for batch analysis.

    Returns dict with: s, k, alphas, A (orbit-sum slope), B (orbit-sum
    intercept), P (peak coefficient max_j a_j), lam (destination slope),
    C (destination intercept).  All coefficient values are Fractions.
    """
    profile = profile_from_alphas(alphas)
    s = len(alphas)
    k = s + sum(alphas)
    a_last, b_last = profile[-1]
    return {
        "s": s,
        "k": k,
        "alphas": alphas,
        "A": sum(a for a, _ in profile),
        "B": sum(b for _, b in profile),
        "P": max(a for a, _ in profile),
        "lam": a_last / 2,
        "C": b_last / 2,
    }
