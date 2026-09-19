"""The pinball table: routing a ball by its parity word.

A table is a qx+c map played in Terras form, T(n) = (q*n + c)/2 for odd n
(a BUMPER) and n/2 for even n (GRAVITY). The ball DRAINS at the coefficient
stopping time -- the first step j where q^s < 2^j, s = bumpers hit so far --
or is caught at `depth` steps. The lane is the parity word up to that point.

The first j parities depend only on n mod 2^j, so a lane is a residue class:
for q = 3 a drained lane is exactly one affine subgroup of a stopping class.
Everything here is integer arithmetic.
"""

BUMPER = 1
GRAVITY = 0


class PinballTable:
    """A qx+c table of fixed depth. Classical Collatz is q=3, c=1."""

    def __init__(self, q: int = 3, c: int = 1, depth: int = 8):
        if q % 2 == 0 or c % 2 == 0:
            raise ValueError("q and c must be odd so that q*n + c is even for odd n")
        self.q = q
        self.c = c
        self.depth = depth

    def __repr__(self):
        return f"PinballTable(q={self.q}, c={self.c}, depth={self.depth})"

    def play(self, n: int) -> tuple[tuple[int, ...], bool]:
        """Return (parity word, drained) for a ball launched at n.

        Example: PinballTable().play(5) = ((1, 0), True)     -- class 3
        Example: PinballTable().play(3) = ((1, 1, 0, 0), True)  -- class 6
        """
        word = []
        q_pow = 1
        for j in range(1, self.depth + 1):
            if n % 2 == 1:
                word.append(BUMPER)
                n = (self.q * n + self.c) // 2
                q_pow *= self.q
            else:
                word.append(GRAVITY)
                n //= 2
            if q_pow < 2 ** j:
                return tuple(word), True
        return tuple(word), False

    def lane(self, n: int) -> tuple[int, ...]:
        """The routing key: the parity word up to the drain (or depth)."""
        return self.play(n)[0]

    def stopping_class(self, n: int):
        """Stopping class implied by the lane (Collatz steps), or None if caught.

        Each bumper is two Collatz steps, each gravity step one.
        Example: PinballTable().stopping_class(3) = 6
        """
        word, drained = self.play(n)
        return len(word) + sum(word) if drained else None
