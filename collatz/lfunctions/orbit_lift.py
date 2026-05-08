"""Lift of Collatz orbit data to Eisenstein integers Z[omega].

Two canonical lifts:
  - iota(n) = n + 0*omega: trivial inclusion Z -> Z[omega].
  - iota_2(n) = n + dest(n)*omega: pair lift, where dest is the stopping
    destination (first orbit value below n).

Sector data: each Syracuse step rotates the Eisenstein phase by -30°. The
sector index s(n) mod 12 is the cumulative Eisenstein phase angle / -30°
along the dropping orbit, equal to the count of Syracuse (odd) steps in
the dropping orbit (the "oddity" s of the dropping set).
"""

from __future__ import annotations

from collatz.core import (
    alpha_sequence,
    stopping_destination,
    stopping_orbit,
    syracuse_orbit,
    syracuse_step,
)

from .eisenstein import EisensteinInt


def iota(n: int) -> EisensteinInt:
    """Trivial inclusion: n -> n + 0 * omega."""
    return EisensteinInt(n, 0)


def orbit_pair(n: int) -> EisensteinInt:
    """Pair lift: n -> n + dest(n) * omega, where dest(n) is the
    stopping destination (first value below n in the Collatz orbit).
    """
    if n <= 1:
        # n = 1 has no proper drop; lift to 1 + 0*omega.
        return EisensteinInt(n, 0)
    if n % 2 == 0:
        # For even n, "dest" = n / 2.
        return EisensteinInt(n, n // 2)
    d = stopping_destination(n)
    return EisensteinInt(n, d)


def oddity_count(n: int) -> int:
    """Count of Syracuse (odd) steps in the dropping orbit of n.

    For odd n > 1, this is the number of (3x+1) steps until the orbit
    first drops below n. Equivalently the number of alpha values consumed.

    Returns 0 for n in {1, 2} (no proper drop).
    """
    if n <= 1:
        return 0
    if n % 2 == 0:
        return 0  # no odd step needed; dest = n/2
    # Walk the orbit counting odd steps until we drop below n.
    start = n
    s = 0
    while True:
        if n % 2 == 1:
            n = 3 * n + 1
            s += 1
        else:
            n //= 2
        if n < start:
            return s


def eisenstein_sector(n: int) -> int:
    """Cumulative Eisenstein phase index s(n) mod 12 for the dropping orbit.

    Each Syracuse step rotates by -30°, so after s odd steps the phase has
    rotated by -30° * s, i.e., the sector is (-s) mod 12 in absolute terms,
    or equivalently s mod 12 if we agree on a sign convention.
    """
    return oddity_count(n) % 12
