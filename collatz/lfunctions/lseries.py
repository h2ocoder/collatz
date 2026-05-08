"""Dirichlet series and Euler products for Hecke characters on Z[omega].

Two summation modes:

  - Naive: sum over ALL Eisenstein integers with norm <= X. For a character
    nontrivial on the unit group, this sum is identically zero (by unit
    cancellation). Useful as a sanity check.

  - Primary: sum over the unique "primary" generator of each principal ideal,
    where primary means alpha is congruent to -1 mod 3 (unit-class index 3 in
    the canonical generator chosen in characters.py). This is the partial
    Hecke L-function on principal ideals.

For Phase 1 (chi_6 of conductor (3)), the primary L-function is also zero
because the unit group fills (Z[omega]/(3))*: there is no nontrivial Hecke
character at this conductor. To get a meaningful Hecke L-function we need
to enlarge the conductor (Phase 2).

The orbit-twisted sums in averaging.py do NOT have this issue: they evaluate
chi on a specific lift iota(n) = n + dest(n)*omega, never quotienting by
units. That is the meaningful Phase 1 statistic.
"""

from __future__ import annotations

import cmath
from typing import Iterable, Iterator

from .characters import (
    HeckeCharacter,
    _residue_unit_class,
    divisible_by_pi,
    unit_class_of,
)
from .eisenstein import EisensteinInt


def eisenstein_integers_up_to_norm(X: int) -> Iterator[EisensteinInt]:
    """Yield every Eisenstein integer alpha with 0 < N(alpha) <= X.

    Bound: a^2 - ab + b^2 <= X.
    Standard parameterization: write the form as
        a^2 - ab + b^2 = (a - b/2)^2 + (3/4) * b^2 <= X.
    So |b| <= 2*sqrt(X/3) and given b, |a - b/2|^2 <= X - (3/4)*b^2.
    """
    import math

    b_bound = int(2 * math.sqrt(X / 3.0)) + 1
    for b in range(-b_bound, b_bound + 1):
        # For each b, a ranges so that (a - b/2)^2 <= X - 3 b^2 / 4.
        rad_sq = X - 0.75 * b * b
        if rad_sq < 0:
            continue
        rad = math.sqrt(rad_sq)
        a_low = math.ceil(b / 2.0 - rad)
        a_high = math.floor(b / 2.0 + rad)
        for a in range(a_low, a_high + 1):
            n = a * a - a * b + b * b
            if 1 <= n <= X:
                yield EisensteinInt(a, b)


def is_primary(alpha: EisensteinInt) -> bool:
    """alpha is primary iff alpha ≡ -1 (mod 3), unit-class index 3."""
    if divisible_by_pi(alpha):
        return False
    return _residue_unit_class(alpha) == 3


def primary_eisenstein_integers_up_to_norm(X: int) -> Iterator[EisensteinInt]:
    """Yield primary Eisenstein integers (one per ideal coprime to pi)."""
    for alpha in eisenstein_integers_up_to_norm(X):
        if is_primary(alpha):
            yield alpha


def partial_sum_naive(chi: HeckeCharacter, X: int, s: complex) -> complex:
    """Sum of chi(alpha) / N(alpha)^s over all Eisenstein alpha with N(alpha) <= X."""
    total = 0.0 + 0j
    for alpha in eisenstein_integers_up_to_norm(X):
        c = chi.evaluate(alpha)
        if c == 0:
            continue
        n = alpha.norm()
        total += c / (n ** s)
    return total


def partial_sum_primary(chi: HeckeCharacter, X: int, s: complex) -> complex:
    """Sum of chi(alpha) / N(alpha)^s over primary alpha with N(alpha) <= X.

    This is the partial Hecke L-function on principal ideals.
    """
    total = 0.0 + 0j
    for alpha in primary_eisenstein_integers_up_to_norm(X):
        c = chi.evaluate(alpha)
        if c == 0:
            continue
        n = alpha.norm()
        total += c / (n ** s)
    return total


def primary_primes_up_to_norm(X: int) -> list[EisensteinInt]:
    """Return primary Eisenstein primes with norm <= X.

    A primary alpha is prime iff it is irreducible iff its norm is a rational
    prime (split case) or a square of an inert rational prime.

    For Hecke L-function purposes we want primary generators of prime ideals.
    """
    from sympy import isprime

    primes: list[EisensteinInt] = []
    for alpha in primary_eisenstein_integers_up_to_norm(X):
        n = alpha.norm()
        if isprime(n):
            primes.append(alpha)
        elif _is_square_of_prime(n):
            primes.append(alpha)
    return primes


def _is_square_of_prime(n: int) -> bool:
    """True iff n = p^2 for some rational prime p."""
    import math

    from sympy import isprime

    r = int(math.isqrt(n))
    return r * r == n and isprime(r)


def partial_euler_primary(
    chi: HeckeCharacter, X: int, s: complex
) -> complex:
    """Partial Euler product over primary Eisenstein primes with norm <= X."""
    product = 1.0 + 0j
    for p in primary_primes_up_to_norm(X):
        c = chi.evaluate(p)
        if c == 0:
            continue
        n = p.norm()
        product *= 1.0 / (1.0 - c / (n ** s))
    return product
