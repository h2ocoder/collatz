"""Eisenstein integers Z[omega] with omega = exp(2*pi*i/3).

Representation: a + b*omega for integers a, b.
Multiplication uses omega^2 = -1 - omega.

Norm: N(a + b*omega) = a^2 - a*b + b^2 (Loeschian numbers).
Units: {1, -1, omega, -omega, omega^2, -omega^2} (six units).
Pi = 1 - omega is the ramified prime above 3, with N(pi) = 3.
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class EisensteinInt:
    """Eisenstein integer alpha = a + b*omega with omega = exp(2*pi*i/3)."""

    a: int
    b: int

    def __add__(self, other: "EisensteinInt") -> "EisensteinInt":
        return EisensteinInt(self.a + other.a, self.b + other.b)

    def __sub__(self, other: "EisensteinInt") -> "EisensteinInt":
        return EisensteinInt(self.a - other.a, self.b - other.b)

    def __neg__(self) -> "EisensteinInt":
        return EisensteinInt(-self.a, -self.b)

    def __mul__(self, other: "EisensteinInt | int") -> "EisensteinInt":
        if isinstance(other, int):
            return EisensteinInt(self.a * other, self.b * other)
        # (a + b*w)(c + d*w) = ac + ad*w + bc*w + bd*w^2
        # w^2 = -1 - w  =>  bd*w^2 = -bd - bd*w
        # Total: (ac - bd) + (ad + bc - bd)*w
        a, b = self.a, self.b
        c, d = other.a, other.b
        return EisensteinInt(a * c - b * d, a * d + b * c - b * d)

    __rmul__ = __mul__

    def __pow__(self, exp: int) -> "EisensteinInt":
        if exp < 0:
            raise ValueError("negative powers not supported on Eisenstein integers")
        result = EisensteinInt(1, 0)
        base = self
        e = exp
        while e:
            if e & 1:
                result = result * base
            base = base * base
            e >>= 1
        return result

    def conjugate(self) -> "EisensteinInt":
        # conj(omega) = omega^2 = -1 - omega
        # conj(a + b*w) = a + b*(-1-w) = (a - b) + (-b)*w
        return EisensteinInt(self.a - self.b, -self.b)

    def norm(self) -> int:
        return self.a * self.a - self.a * self.b + self.b * self.b

    def to_complex(self) -> complex:
        # omega = exp(2*pi*i/3) = -1/2 + i*sqrt(3)/2
        return complex(self.a - 0.5 * self.b, 0.5 * math.sqrt(3) * self.b)

    def arg(self) -> float:
        z = self.to_complex()
        return cmath.phase(z)

    def __repr__(self) -> str:
        if self.b == 0:
            return f"E({self.a})"
        if self.a == 0:
            return f"E({self.b}w)"
        sign = "+" if self.b > 0 else "-"
        return f"E({self.a}{sign}{abs(self.b)}w)"


def norm(alpha: EisensteinInt) -> int:
    return alpha.norm()


def conjugate(alpha: EisensteinInt) -> EisensteinInt:
    return alpha.conjugate()


# The six units of Z[omega]
_UNITS = (
    EisensteinInt(1, 0),
    EisensteinInt(-1, 0),
    EisensteinInt(0, 1),
    EisensteinInt(0, -1),
    EisensteinInt(-1, -1),  # omega^2 = -1 - omega
    EisensteinInt(1, 1),  # -omega^2 = 1 + omega
)


def units() -> tuple[EisensteinInt, ...]:
    return _UNITS


# pi = 1 - omega: the ramified prime above 3.
pi = EisensteinInt(1, -1)
# pi_bar = 1 - omega^2 = 1 - (-1 - omega) = 2 + omega
pi_bar = EisensteinInt(2, 1)


def divides(divisor: EisensteinInt, alpha: EisensteinInt) -> bool:
    """Test whether divisor | alpha in Z[omega] via norm-based exact division."""
    n = divisor.norm()
    if n == 0:
        raise ValueError("division by zero")
    # alpha / divisor = alpha * conj(divisor) / N(divisor)
    prod = alpha * divisor.conjugate()
    return prod.a % n == 0 and prod.b % n == 0


def quotient(alpha: EisensteinInt, divisor: EisensteinInt) -> EisensteinInt:
    """Exact quotient alpha / divisor. Raises if not exact."""
    n = divisor.norm()
    if n == 0:
        raise ValueError("division by zero")
    prod = alpha * divisor.conjugate()
    if prod.a % n != 0 or prod.b % n != 0:
        raise ValueError(f"{divisor!r} does not divide {alpha!r} exactly")
    return EisensteinInt(prod.a // n, prod.b // n)


def reduce_mod(alpha: EisensteinInt, modulus: EisensteinInt) -> EisensteinInt:
    """Reduce alpha modulo (modulus). Returns canonical representative.

    Uses the lattice-point closest-quotient round-to-nearest algorithm.
    """
    n = modulus.norm()
    if n == 0:
        raise ValueError("modulus has zero norm")
    prod = alpha * modulus.conjugate()
    # Round each coordinate to nearest integer
    qa = round(prod.a / n)
    qb = round(prod.b / n)
    q = EisensteinInt(qa, qb)
    return alpha - q * modulus


def is_unit(alpha: EisensteinInt) -> bool:
    return alpha.norm() == 1


def is_associate(a: EisensteinInt, b: EisensteinInt) -> bool:
    """Two Eisenstein ints are associates iff they differ by a unit."""
    if a.norm() != b.norm():
        return False
    if a == b:
        return True
    for u in _UNITS:
        if u * a == b:
            return True
    return False


def split_or_inert(p: int) -> str:
    """Classify a rational prime p in Z[omega]: 'ramified', 'split', or 'inert'."""
    if p < 2:
        raise ValueError("p must be a prime")
    if p == 3:
        return "ramified"
    if p % 3 == 1:
        return "split"
    return "inert"  # p % 3 == 2


def find_split_prime(p: int) -> EisensteinInt:
    """For a rational prime p == 1 mod 3, return alpha with N(alpha) = p.

    Solves a^2 - a*b + b^2 = p by brute-force search (p small).
    """
    if p % 3 != 1 or p < 7:
        raise ValueError(f"{p} is not a split rational prime in Z[omega]")
    # Bound: |a|, |b| <= ceil(2*sqrt(p)/sqrt(3)).
    bound = int(2 * math.sqrt(p) / math.sqrt(3)) + 2
    for a in range(1, bound + 1):
        for b in range(-bound, bound + 1):
            if a * a - a * b + b * b == p:
                return EisensteinInt(a, b)
    raise RuntimeError(f"no representation found for split prime {p}")
