"""Machines within machines: nesting, free composition, the never-drain set.

Three structural facts about the pinball table (see
research/investigate-pinball-analogy/Nesting and the Never-Drain Fractal.md):

  drop_chain / drop_tree -- a stopping orbit is its first step followed by a
      chain of complete smaller drops, recursively: a finite tree of parts.
  realizing_residue -- ANY finite sequence of parts is played by exactly one
      residue class. Composition has no forbidden arrangements.
  undrained_count -- the balls that never drain form a Cantor-like set in the
      2-adic integers whose lane count grows like 2^(H * depth), H = H(log_3 2).
"""

import math

from collatz.core import stopping_orbit


def drop_chain(n: int) -> list[tuple[int, int]]:
    """The complete drops inside n's stopping orbit, as (start, stopping class).

    For odd n the orbit is the bumper step n -> 3n+1 followed by successive
    drops 3n+1 -> dest -> dest -> ... until the value falls below n, so
    stopping_time(n) = 1 + sum of the chain's classes. Even n has no chain.

    Example: drop_chain(27) = [(82, 1), (41, 3), (31, 91)]   -- 96 = 1 + 1 + 3 + 91
    Example: drop_chain(5) = [(16, 1), (8, 1)]               -- 3 = 1 + 1 + 1
    """
    x = stopping_orbit(n)[0]
    chain = []
    while x > n:
        sub = stopping_orbit(x)
        chain.append((x, len(sub)))
        x = sub[-1]
    return chain


def drop_tree(n: int) -> tuple:
    """Recursive nesting: (n, stopping class, [drop_tree of each chain start]).

    Example: drop_tree(5) = (5, 3, [(16, 1, []), (8, 1, [])])
    """
    chain = drop_chain(n)
    return (n, 1 + sum(k for _, k in chain), [drop_tree(start) for start, _ in chain])


def realizing_residue(word) -> tuple[int, int]:
    """Return (r, 2^L): the unique residue whose first L Terras parities are `word`.

    Works for ANY 0/1 word, so any concatenation of lanes is playable: flipping
    bit j of n changes T^j(n) by 3^s, which is odd, so exactly one choice of
    each bit matches the required parity.

    Example: realizing_residue((1, 0)) = (1, 4)        -- Set_3 is n = 1 mod 4
    Example: realizing_residue((1, 1, 1, 1)) = (15, 16)  -- all bumpers: -1 mod 16
    """
    r = 0
    for j, parity in enumerate(word):
        x = r
        for _ in range(j):
            x = (3 * x + 1) // 2 if x % 2 else x // 2
        if x % 2 != parity:
            r += 1 << j
    return r, 1 << len(word)


def undrained_count(depth: int, q: int = 3) -> int:
    """Number of parity words of length `depth` that never drain (q^s > 2^j throughout).

    Each is a residue class mod 2^depth, so undrained_count / 2^depth is the
    measure still in play and the counts are a box-counting cover of the
    never-drain set.

    Example: undrained_count(2) = 1   -- only (1, 1), i.e. n = 3 mod 4
    """
    by_bumpers = {0: 1}
    for j in range(1, depth + 1):
        step = {}
        for s, count in by_bumpers.items():
            for bumper in (0, 1):
                if q ** (s + bumper) > 2 ** j:
                    step[s + bumper] = step.get(s + bumper, 0) + count
        by_bumpers = step
    return sum(by_bumpers.values())


def undrained_growth_rate(depth: int, q: int = 3) -> float:
    """log2(U(2*depth) / U(depth)) / depth -- estimates the set's dimension.

    The difference quotient cancels most of the polynomial prefactor that makes
    log2(U(depth)) / depth converge slowly.
    """
    return math.log2(undrained_count(2 * depth, q) / undrained_count(depth, q)) / depth


def entropy_dimension(q: int = 3) -> float:
    """H(theta), theta = log_q(2): the predicted dimension of the never-drain set.

    A ball stays in play only while its bumper density stays above theta;
    words of density theta number about 2^(H(theta) * length).

    For q >= 5, theta < 1/2: typical words already qualify, the dimension is 1
    and a positive fraction of balls never drains. q = 3 is the only odd q > 1
    with a thin never-drain set.

    Example: round(entropy_dimension(), 4) = 0.95;  entropy_dimension(5) = 1.0
    """
    theta = math.log(2) / math.log(q)
    if theta <= 0.5:
        return 1.0
    return -theta * math.log2(theta) - (1 - theta) * math.log2(1 - theta)
