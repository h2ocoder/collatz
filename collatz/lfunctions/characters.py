"""Hecke characters on Z[omega] for the Collatz L-function machinery.

Phase 1: classical residue characters with conductor (pi) and (pi^2).

  - TrivialCharacter:        chi_0(alpha) = 1 if gcd(alpha, conductor) == 1, else 0.
  - CubicResidueCharacter:   chi_3 of conductor (pi); values in {1, omega, omega^2}.
  - SexticResidueCharacter:  chi_6 of conductor (pi^2) = (3); values in mu_6.

All characters are defined on principal ideals via their generator, with the
unit-ambiguity resolved by the "primary" normalization (the unique associate
that is congruent to a fixed reference value modulo the conductor).
"""

from __future__ import annotations

import cmath
import math
from typing import Protocol

from .eisenstein import EisensteinInt, divides, pi, reduce_mod, units


class HeckeCharacter(Protocol):
    """Interface for a Hecke character on principal ideals of Z[omega]."""

    def evaluate(self, alpha: EisensteinInt) -> complex:
        """Return chi(alpha). Returns 0 if gcd(alpha, conductor) > 1."""
        ...

    @property
    def order(self) -> int:
        """Order of the character (smallest n with chi^n trivial)."""
        ...

    @property
    def name(self) -> str: ...


# ---------------------------------------------------------------------------
# Trivial character
# ---------------------------------------------------------------------------

class TrivialCharacter:
    """chi_0: returns 1 on every nonzero ideal coprime to the conductor."""

    def __init__(self, conductor: EisensteinInt | None = None):
        self.conductor = conductor

    def evaluate(self, alpha: EisensteinInt) -> complex:
        if alpha.a == 0 and alpha.b == 0:
            return 0.0 + 0j
        if self.conductor is not None and divides(self.conductor, alpha):
            return 0.0 + 0j
        return 1.0 + 0j

    @property
    def order(self) -> int:
        return 1

    @property
    def name(self) -> str:
        return "trivial"


# ---------------------------------------------------------------------------
# Cubic residue character chi_3 on Z[omega], conductor (pi).
#
# (Z[omega] / (pi))* is the cyclic group of order N(pi) - 1 = 2.
# Wait: N(pi) = 3, so the residue field Z[omega]/(pi) has 3 elements,
# its unit group has 2 elements, which is too small for a nontrivial cubic.
#
# The right finite-order cubic character has conductor (pi^2) = (3).
# (Z[omega]/(3))* has order 6 (cyclic), so it admits both cubic (mu_3) and
# sextic (mu_6) characters.
#
# We implement chi_3 and chi_6 both via discrete log in (Z[omega]/(3))*.
# ---------------------------------------------------------------------------

# Modulus (pi^2) = (3) as ideals.
_MOD = EisensteinInt(3, 0)
_MOD_NORM = 9


def _residue_canonical(alpha: EisensteinInt) -> tuple[int, int]:
    """Reduce alpha mod (3) and return canonical (a mod 3, b mod 3) in [0,2]^2."""
    return (alpha.a % 3, alpha.b % 3)


def _residue_unit_class(alpha: EisensteinInt) -> int | None:
    """Identify alpha's unit-class index in (Z[omega]/(3))* of order 6.

    Returns None if alpha is not a unit modulo (3), i.e., divisible by pi.
    Otherwise returns k in 0..5 where chi(alpha) = generator^k.

    Generator chosen: g = (1, 1) corresponds to -omega^2, which generates
    the cyclic group (Z[omega]/(3))* (verified at module load time).
    """
    return _UNIT_CLASS_MAP.get(_residue_canonical(alpha))


def _is_pi_divisible(alpha: EisensteinInt) -> bool:
    """True iff pi | alpha. Equivalently, alpha mod (pi) == 0.

    Reduction mod pi: pi = 1 - omega ~ omega ~ 1 (mod pi), so
    a + b*omega ~ a + b (mod pi). Hence pi | alpha iff (a + b) % 3 == 0.
    """
    return (alpha.a + alpha.b) % 3 == 0


def _build_unit_class_map() -> dict[tuple[int, int], int]:
    """Build a dict mapping (a%3, b%3) -> generator power.

    The generator g is chosen as the EisensteinInt(0, 1) = omega.
    But omega has order 3 in (Z/3)*: omega -> omega^2 -> 1 -> omega. So omega
    alone generates only mu_3.

    The full cyclic-of-order-6 generator must combine: omega (order 3) and
    -1 (order 2). A natural choice is g = -omega = (0, -1) which has order 6.

    Verify: (-omega)^2 = omega^2 = (-1, -1).
            (-omega)^3 = -omega^3 = -1 = (-1, 0).
            (-omega)^6 = 1.
    """
    one = EisensteinInt(1, 0)
    g = EisensteinInt(0, -1)  # -omega; verify order 6 below
    powers = {}
    cur = one
    for k in range(6):
        key = (cur.a % 3, cur.b % 3)
        powers[key] = k
        cur = cur * g
    # Verify: closing the cycle returns to identity.
    assert cur == one or _residue_canonical(cur) == _residue_canonical(one), (
        f"generator -omega did not have order 6 mod (3): cur = {cur}"
    )
    if len(powers) != 6:
        # The generator does not give 6 distinct residues; fall back to brute search.
        powers.clear()
        # Enumerate all 6 unit residues; assign powers via inspection.
        unit_residues = []
        for a in range(3):
            for b in range(3):
                alpha = EisensteinInt(a, b)
                if (a + b) % 3 != 0 and (a, b) != (0, 0):
                    unit_residues.append((a, b))
        # Pick a known generator empirically.
        for cand_a, cand_b in unit_residues:
            cand = EisensteinInt(cand_a, cand_b)
            seen: list[tuple[int, int]] = []
            cur = one
            for _ in range(6):
                key = (cur.a % 3, cur.b % 3)
                seen.append(key)
                cur = cur * cand
            if len(set(seen)) == 6:
                # cand is a generator.
                cur = one
                for k in range(6):
                    key = (cur.a % 3, cur.b % 3)
                    powers[key] = k
                    cur = cur * cand
                break
        else:
            raise RuntimeError("no generator of (Z[omega]/(3))* found")
    return powers


_UNIT_CLASS_MAP = _build_unit_class_map()


class CubicResidueCharacter:
    """chi_3 of conductor (pi^2) = (3). Values in {1, omega, omega^2}.

    Defined as chi_3(alpha) = chi_6(alpha)^2 = zeta_3^k where alpha lies in
    unit-class k of (Z[omega]/(3))*.
    """

    def __init__(self):
        self._zeta = cmath.exp(2j * math.pi / 3)

    def evaluate(self, alpha: EisensteinInt) -> complex:
        k = _residue_unit_class(alpha)
        if k is None:
            return 0.0 + 0j
        return self._zeta ** (k % 3)

    @property
    def order(self) -> int:
        return 3

    @property
    def name(self) -> str:
        return "cubic_residue"


class SexticResidueCharacter:
    """chi_6 of conductor (pi^2) = (3). Values in mu_6.

    Defined as chi(alpha) = zeta_6^k where alpha lies in unit-class k of
    (Z[omega]/(3))*.
    """

    def __init__(self):
        self._zeta = cmath.exp(1j * math.pi / 3)  # zeta_6

    def evaluate(self, alpha: EisensteinInt) -> complex:
        k = _residue_unit_class(alpha)
        if k is None:
            return 0.0 + 0j
        return self._zeta ** k

    @property
    def order(self) -> int:
        return 6

    @property
    def name(self) -> str:
        return "sextic_residue"


# ---------------------------------------------------------------------------
# Norm-pullback Dirichlet character: control for Phase 1 sanity check.
#
# Given a rational Dirichlet character chi_q: (Z/qZ)* -> C* of conductor q
# coprime to 3, define a Hecke character on Z[omega] by
#   chi(alpha) := chi_q(N(alpha) mod q)
# where N(alpha) = a^2 - ab + b^2 is the Eisenstein norm.
#
# This is multiplicative because the Eisenstein norm is multiplicative.
# Its conductor is supported only at primes above q, so it is coprime to
# (pi) as long as q is coprime to 3. Used as a control: if the orbit-twisted
# sum behaves randomly against this character (sqrt(N) cancellation), then
# the chi_3/chi_6 signal we observe is specifically a 3-adic-lock effect,
# not a generic L-function-correlation phenomenon.
# ---------------------------------------------------------------------------


class NormPullbackCharacter:
    """Pullback of a rational Dirichlet character via the Eisenstein norm.

    chi(alpha) = chi_rat(N(alpha) mod q).

    Parameters
    ----------
    q : int
        Modulus of the rational Dirichlet character. Must be coprime to 3
        for the pullback to be coprime to (pi).
    rat_char : callable[[int], complex]
        The rational Dirichlet character: rat_char(k) for k in 0..q-1.
        Must be 0 on k that share a factor with q. The character order is
        inferred from rat_char's image (must be a root of unity).
    name : str
        Human-readable name for diagnostics.
    order : int
        Character order (smallest n with chi^n = trivial).
    """

    def __init__(self, q: int, rat_char, name: str, order: int):
        if q % 3 == 0:
            raise ValueError(
                "Norm-pullback requires q coprime to 3 to be coprime to (pi)"
            )
        self.q = q
        self.rat_char = rat_char
        self._name = name
        self._order = order

    def evaluate(self, alpha: EisensteinInt) -> complex:
        n = alpha.norm()
        return complex(self.rat_char(n % self.q))

    @property
    def order(self) -> int:
        return self._order

    @property
    def name(self) -> str:
        return self._name


def cubic_character_mod_7() -> NormPullbackCharacter:
    """Cubic character on Z[omega] pulled back from (Z/7Z)* via norm.

    (Z/7Z)* is cyclic of order 6 with generator 3 (verified). Cubic character
    sends 3 -> omega, 3^2 -> omega^2, 3^3 = 6 -> 1, 3^4 = 4 -> omega, etc.
    Equivalently chi(k) = omega^(log_3(k) mod 3).
    """
    omega_3 = cmath.exp(2j * math.pi / 3)
    # Build the discrete-log table for (Z/7Z)* with generator 3.
    # Powers of 3 mod 7: 3^0=1, 3^1=3, 3^2=2, 3^3=6, 3^4=4, 3^5=5, 3^6=1.
    log_table: dict[int, int] = {}
    cur = 1
    for k in range(6):
        log_table[cur] = k
        cur = (cur * 3) % 7
    # log_table now {1:0, 3:1, 2:2, 6:3, 4:4, 5:5}.

    def rat_char(k: int) -> complex:
        if k == 0:
            return 0.0 + 0j
        return omega_3 ** (log_table[k % 7] % 3)

    return NormPullbackCharacter(
        q=7, rat_char=rat_char, name="cubic_norm_pullback_7", order=3
    )


def sextic_character_mod_7() -> NormPullbackCharacter:
    """Sextic character on Z[omega] pulled back from (Z/7Z)* via norm."""
    zeta_6 = cmath.exp(1j * math.pi / 3)
    log_table: dict[int, int] = {}
    cur = 1
    for k in range(6):
        log_table[cur] = k
        cur = (cur * 3) % 7

    def rat_char(k: int) -> complex:
        if k == 0:
            return 0.0 + 0j
        return zeta_6 ** log_table[k % 7]

    return NormPullbackCharacter(
        q=7, rat_char=rat_char, name="sextic_norm_pullback_7", order=6
    )


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def unit_class_of(alpha: EisensteinInt) -> int | None:
    """Public alias for _residue_unit_class."""
    return _residue_unit_class(alpha)


def divisible_by_pi(alpha: EisensteinInt) -> bool:
    """Public alias for _is_pi_divisible."""
    return _is_pi_divisible(alpha)
