"""Lens functions: Z -> coordinate. One-line summary per lens in docstring.

Each lens extracts one dynamical invariant of an integer. Lenses are pure
functions and stateless. The LENS_REGISTRY records each lens with its kind
("discrete" or "real") and cardinality (for one-hot encoding).
"""

import math
from collections.abc import Callable
from dataclasses import dataclass

from collatz.core import alpha_sequence
from collatz.dropping import dropping_set, dropping_time, orbital_oddity


def _odd_part(n: int) -> int:
    """Largest odd divisor of n; the Syracuse-equivalent of n.

    Even n share dynamics with their odd part (after stripping halvings),
    so alpha-based lenses lift evens to their odd part.

    Example: _odd_part(6) = 3, _odd_part(40) = 5, _odd_part(1) = 1.
    """
    if n <= 0:
        raise ValueError(f"_odd_part requires n > 0, got {n}")
    while n % 2 == 0:
        n //= 2
    return n


def sector(n: int) -> int:
    """Eisenstein angle bin: number of Syracuse steps to 1, mod 12.

    For even n, lifts to the odd part (n stripped of factors of 2). Sentinel 0 for n=1.

    Rotation property: under one Syracuse step on an odd n, sector decreases by 1 mod 12.

    Example: sector(3) = 2 (alpha_sequence has length 2).
    """
    if n == 1:
        return 0
    return len(alpha_sequence(_odd_part(n))) % 12


def mod3(n: int) -> int:
    """3-adic residue. Encodes the 3-Adic Lock state.

    Example: mod3(3) = 0, mod3(7) = 1, mod3(8) = 2.
    """
    return n % 3


def drop_class(n: int) -> int:
    """Dropping set k of n (steps to first value < n). Sentinel 0 for n=1.

    Example: drop_class(3) = 6, drop_class(5) = 3, drop_class(6) = 1.
    """
    if n == 1:
        return 0
    return dropping_set(n)


def alpha_prefix(n: int, k: int = 3) -> tuple[int, ...]:
    """First k entries of the alpha (Syracuse 2-adic-valuation) sequence, padded with 0.

    For even n, lifts to the odd part. All-zero tuple for n=1.

    Example: alpha_prefix(3, k=3) = (1, 4, 0); alpha_prefix(7, k=3) = (1, 1, 2).
    """
    if n == 1:
        return (0,) * k
    seq = alpha_sequence(_odd_part(n))
    if len(seq) >= k:
        return tuple(seq[:k])
    return tuple(seq) + (0,) * (k - len(seq))


def force(n: int) -> int:
    """Bit-precision of n's affine subgroup: log2(P) where P = 2^(k - s).

    k = dropping_time(n), s = orbital_oddity(n) (count of odd values in dropping orbit).
    Higher force = narrower subgroup = more bits stable under iteration.

    Dual reading: epistemic confidence -- high force = well-determined,
    low force = loose.

    Example: force(3) = 6 - 2 = 4. Sentinel 0 for n=1.
    """
    if n == 1:
        return 0
    return dropping_time(n) - orbital_oddity(n)


def slope_log(n: int) -> float:
    """Log2 of the affine slope of n's subgroup: s*log2(3) - (k - s).

    Identifies the affine class within Set_k. Sentinel 0.0 for n=1.

    Example: slope_log(3) = 2*log2(3) - 4 ~= -0.830.
    """
    if n == 1:
        return 0.0
    s = orbital_oddity(n)
    k = dropping_time(n)
    return s * math.log2(3) - (k - s)


@dataclass(frozen=True)
class LensSpec:
    """Metadata for one lens.

    kind == "discrete": output is an int in [0, cardinality); one-hot encoded.
    kind == "real": output is a float; passed through as a single axis.
    alpha_k applies only to alpha_prefix (length of the prefix tuple).
    """

    name: str
    fn: Callable[[int], object]
    kind: str
    cardinality: int | None
    alpha_k: int = 3


ALPHA_MAX = 8

LENS_REGISTRY: tuple[LensSpec, ...] = (
    LensSpec("sector", sector, "discrete", 12),
    LensSpec("mod3", mod3, "discrete", 3),
    LensSpec("drop_class", drop_class, "discrete", 32),
    LensSpec("alpha_prefix", alpha_prefix, "discrete", ALPHA_MAX, alpha_k=3),
    LensSpec("force", force, "real", None),
    LensSpec("slope_log", slope_log, "real", None),
)
