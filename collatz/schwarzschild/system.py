"""Collatz-like maps with one affine branch per residue mod d.

    T(n) = (q_r n + a_r) / d    for n = r (mod d)

The Terras form of the classic map is d = 2, q = (1, 3), a = (0, 1): halve even
n, send odd n to (3n + 1) / 2. Every step reads exactly one base-d digit of n.

A word is the sequence of residues an orbit visits. Applying word w of length k
is the affine map A_w(n) = (Q n + C) / d^k, where Q multiplies the branches and
C collects the offsets. These are the same two numbers as the slope and the
intercept in docs/Conjectures/Affine Orbit Structure.md.
"""

from dataclasses import dataclass
from math import gcd
from typing import NamedTuple


class WordMap(NamedTuple):
    """The affine map A(n) = (Q n + C) / d^k applied by a word of length k."""

    Q: int
    C: int
    k: int


@dataclass(frozen=True)
class CollatzLike:
    """T(n) = (q[r] n + a[r]) / d for n = r (mod d).

    Requires gcd(q[r], d) = 1, which is what makes digit words a bijection with
    residue classes, and q[r] r + a[r] = 0 (mod d), which makes T integer valued.

    Example: CollatzLike(2, (1, 3), (0, 1)) is the classic map.
    Example: CollatzLike(2, (1, 3), (0, 2)) raises ValueError: (3n + 2) / 2 is not an integer.
    """

    d: int
    q: tuple[int, ...]
    a: tuple[int, ...]

    def __post_init__(self):
        if self.d < 2:
            raise ValueError("d must be at least 2")
        if len(self.q) != self.d or len(self.a) != self.d:
            raise ValueError("q and a need one entry per residue mod d")
        for r, (qr, ar) in enumerate(zip(self.q, self.a)):
            if qr < 1:
                raise ValueError(f"multiplier q[{r}] must be positive")
            if gcd(qr, self.d) != 1:
                raise ValueError(f"q[{r}] = {qr} is not coprime to d = {self.d}")
            if (qr * r + ar) % self.d:
                raise ValueError(f"branch {r} is not integer valued")

    @classmethod
    def qx_plus_a(cls, q: int = 3, a: int = 1) -> "CollatzLike":
        """n / 2 on even n, (q n + a) / 2 on odd n, for odd q and odd a.

        Example: CollatzLike.qx_plus_a(3, -1) is the 3x - 1 mirror.
        """
        return cls(2, (1, q), (0, a))

    @classmethod
    def from_multipliers(cls, q) -> "CollatzLike":
        """The map with these multipliers and the smallest offsets in [0, d).

        Example: CollatzLike.from_multipliers((1, 4, 4)).a = (0, 2, 1)
        """
        q = tuple(q)
        d = len(q)
        return cls(d, q, tuple((-qr * r) % d for r, qr in enumerate(q)))

    def scaled(self, m: int) -> "CollatzLike":
        """The conjugate T_m(n) = m T(n / m), for m coprime to d.

        This multiplies every offset by m, so it is the way to change the mass of
        a map. Its orbits through multiples of m are m times the orbits of T, and
        its orbits through other integers are the orbits of T on rationals with
        denominator m. Digit r of T becomes digit m r (mod d).

        Example: COLLATZ.scaled(5) == CollatzLike.qx_plus_a(3, 5)
        """
        if m == 0 or gcd(m, self.d) != 1:
            raise ValueError("the scale must be coprime to d")
        q = [0] * self.d
        a = [0] * self.d
        for r in range(self.d):
            image = m * r % self.d
            q[image] = self.q[r]
            a[image] = m * self.a[r]
        return CollatzLike(self.d, tuple(q), tuple(a))

    def step(self, n: int) -> int:
        """One application of T."""
        r = n % self.d
        return (self.q[r] * n + self.a[r]) // self.d

    def word(self, n: int, k: int) -> tuple[int, ...]:
        """The first k digits (residues mod d) of n's orbit.

        Example: COLLATZ.word(3, 4) = (1, 1, 0, 0)    -- 3, 5, 8, 4
        """
        out = []
        for _ in range(k):
            out.append(n % self.d)
            n = self.step(n)
        return tuple(out)

    def word_map(self, word) -> WordMap:
        """(Q, C, k) with T^k(n) = (Q n + C) / d^k for every n realizing word.

        Example: COLLATZ.word_map((1, 0)) = WordMap(3, 1, 2)    -- (3n + 1) / 4
        """
        Q, C, power = 1, 0, 1
        for r in word:
            Q, C = self.q[r] * Q, self.q[r] * C + self.a[r] * power
            power *= self.d
        return WordMap(Q, C, len(word))

    def residue(self, word) -> tuple[int, int]:
        """(r, d^k): the unique residue class whose orbit starts with word.

        This solves Q r + C = 0 (mod d^k). The congruence has one solution
        because gcd(Q, d) = 1, and every member of the class satisfies it.

        Example: COLLATZ.residue((1, 0)) = (1, 4)    -- Set_3 is n = 1 mod 4
        """
        Q, C, k = self.word_map(word)
        modulus = self.d ** k
        return (-C * pow(Q, -1, modulus)) % modulus, modulus

    def cycle_through(self, n: int, max_steps: int = 100_000) -> list[int] | None:
        """The cycle n's orbit enters, smallest element first, or None past max_steps.

        Example: COLLATZ.cycle_through(7) = [1, 2]
        """
        seen = {}
        path = []
        for step in range(max_steps):
            if n in seen:
                cycle = path[seen[n]:]
                start = cycle.index(min(cycle))
                return cycle[start:] + cycle[:start]
            seen[n] = step
            path.append(n)
            n = self.step(n)
        return None


COLLATZ = CollatzLike.qx_plus_a(3, 1)
