"""Word horizons: the value-space face of the Schwarzschild analogy.

A word w acts as A(n) = (Q n + C) / d^k. Its fixed point

    F(w) = C / (d^k - Q)

is the word's horizon. Everything here is exact algebra on that one number:

    1 - A(n) / n  =  (1 - Q / d^k) (1 - F / n)     the factor 1 - r_s / r
    A(n) - F      =  (Q / d^k) (n - F)             infall onto the horizon
    A(n) < n  <=>  n > F, when Q < d^k             a drop is being outside

Periodic points sit exactly on their own horizon (Bohm-Sontacchi's cycle
equation). F is linear in the offsets, so the offset plays the part of mass, and
bits destroyed sit in the denominator: F = zeta / (2^beta - 1) with
zeta = C / Q and beta = k log2 d - log2 Q. See
research/information-schwarzschild-radius/Word Horizons.md.
"""

import math
from fractions import Fraction

import pandas as pd

from collatz.schwarzschild.system import COLLATZ, CollatzLike


def log2_ratio(x: int, y: int) -> float:
    """log2(x / y) for positive integers, accurate when x and y nearly agree.

    Plain log2(x) - log2(y) loses every digit once x and y share most of their
    bits, and near-critical words are the ones that matter here.
    """
    gap = x - y
    if 2 * abs(gap) < y:
        return math.log1p(float(Fraction(gap, y))) / math.log(2)
    return math.log2(x) - math.log2(y)


def horizon(word, system: CollatzLike = COLLATZ) -> Fraction:
    """F(w) = C / (d^k - Q), the fixed point of the word's affine map.

    Example: horizon((1, 0)) = 1          -- (3n + 1) / 4 fixes 1, the trivial cycle
    Example: horizon((1,)) = -1           -- (3n + 1) / 2 fixes the cycle at -1
    """
    Q, C, k = system.word_map(word)
    if k == 0:
        raise ValueError("the empty word has no horizon")
    return Fraction(C, system.d ** k - Q)


def word_mass(word, system: CollatzLike = COLLATZ) -> Fraction:
    """zeta(w) = C / Q: the offsets a word pumps in, in units of the starting value.

    It is exact that T^k(n) = (Q / d^k)(n + zeta) along the word.

    Example: word_mass((1, 0)) = 1/3
    """
    Q, C, _ = system.word_map(word)
    return Fraction(C, Q)


def bits_destroyed(word, system: CollatzLike = COLLATZ) -> float:
    """beta(w) = k log2 d - log2 Q, the size a word removes at large n.

    Over a first-drop word of the classic map this is the repo's bit destruction
    beta(s) = ceil(s log2 3) - s log2 3 (docs/Conjectures/Bit Destruction Bound.md).

    Example: round(bits_destroyed((1, 0)), 4) = 0.415
    """
    Q, _, k = system.word_map(word)
    return log2_ratio(system.d ** k, Q)


def lapse(word, n: int, system: CollatzLike = COLLATZ) -> Fraction:
    """f(n) = 1 - F / n: positive outside the horizon, zero on it, negative inside.

    Example: lapse((1, 0), 5) = 4/5
    """
    return 1 - horizon(word, system) / n


def drop_fraction(word, n: int, system: CollatzLike = COLLATZ) -> Fraction:
    """1 - A(n) / n, the fraction of n that the word removes.

    It equals (1 - Q / d^k) lapse(word, n) for every n, realizing the word or not.

    Example: drop_fraction((1, 0), 5) = 1/5    -- 5 -> 4 = (3 * 5 + 1) / 4
    """
    Q, C, k = system.word_map(word)
    return 1 - Fraction(Q * n + C, system.d ** k * n)


def contraction_word(n: int, system: CollatzLike = COLLATZ,
                     max_steps: int = 10_000) -> tuple[int, ...] | None:
    """n's shortest orbit prefix with Q < d^k, or None if none appears in max_steps.

    Its length is Terras's coefficient stopping time. With non-negative offsets it
    can never be longer than the first drop, because a drop needs Q n + C < d^k n.

    Example: contraction_word(3) = (1, 1, 0, 0)    -- 3^2 < 2^4
    """
    Q, word, power = 1, [], 1
    x = n
    for _ in range(max_steps):
        r = x % system.d
        word.append(r)
        Q *= system.q[r]
        power *= system.d
        x = (system.q[r] * x + system.a[r]) // system.d
        if Q < power:
            return tuple(word)
    return None


def compactness(n: int, system: CollatzLike = COLLATZ) -> Fraction | None:
    """F(w) / n for n's first contraction word: the analogue of r_s / R.

    Terras's coefficient stopping time conjecture is exactly the statement that
    compactness(n) < 1 for every n >= 2 of the classic map.

    Example: compactness(3) = 5/21
    """
    if n < 1:
        raise ValueError("n must be a positive integer")
    word = contraction_word(n, system)
    return None if word is None else horizon(word, system) / n


def captured(n: int, system: CollatzLike = COLLATZ) -> bool:
    """True if n lies on or inside the horizon of its first contraction word.

    Then T^k(n) >= n although the coefficient has contracted, and n's coefficient
    stopping time misses its first drop. For the classic map only n = 1 is known.

    Example: captured(1) = True;  captured(27) = False
    """
    value = compactness(n, system)
    return value is not None and value >= 1


def contraction_words(s: int, q: int = 3) -> list[tuple[int, ...]]:
    """Every first-contraction parity word of qx + a with exactly s kicks.

    Their number is OEIS A100982 for q = 3 (the Lattice Path Formula's N(s)), and
    each one is a residue class mod 2^k, where k is the first length with q^s < 2^k.

    Example: contraction_words(3) = [(1, 1, 1, 0, 0), (1, 1, 0, 1, 0)]    -- k = 5
    """
    length = (q ** s).bit_length()
    words = []

    def extend(prefix, kicks):
        t = len(prefix)
        if t == length:
            if kicks == s:
                words.append(tuple(prefix))
            return
        for bit in (1, 0):
            j = kicks + bit
            if j > s:
                continue
            if t + 1 == length or q ** j > 2 ** (t + 1):
                extend(prefix + [bit], j)

    extend([], 0)
    return words


def mass_bound(word, system: CollatzLike = COLLATZ) -> Fraction:
    """The sum of a_r / q_r over a first-contraction word's digits, for offsets a_r >= 0.

    A first-contraction word has Q_t >= d^t before each digit t, so the t-th term
    of zeta = sum a_r d^t / (Q_t q_r) is at most a_r / q_r. For the classic map
    with s kicks this reads zeta <= s / 3.

    Example: mass_bound((1, 1, 0, 0)) = 2/3
    """
    return sum((Fraction(system.a[r], system.q[r]) for r in word), Fraction(0))


def largest_horizon(s: int) -> Fraction:
    """The bound F(w) <= s 3^(s-1) / (2^k - 3^s) for any classic word with s kicks.

    Here k is the first length with 3^s < 2^k. Bit destruction sits in the
    denominator, so horizons are large only near a convergent of log2 3.

    Example: largest_horizon(1) = 1;  largest_horizon(5) = 405/13
    """
    power = 3 ** s
    return Fraction(s * 3 ** (s - 1), 2 ** power.bit_length() - power) if s else Fraction(0)


def certified_kicks(verified_up_to: int, s_limit: int = 400_000) -> int:
    """The largest S such that largest_horizon(s) <= verified_up_to for all s <= S.

    Suppose every n in [2, N] has T^tau(n) < n, where tau is the coefficient
    stopping time. A failure at any larger n with s kicks would need
    n <= largest_horizon(s). So if largest_horizon(s) <= N, no integer of any
    size fails with s kicks. Stops at s_limit if no s below it breaks the bound.

    Example: certified_kicks(10) = 4    -- s = 5 has a bound of 31.2
    """
    power = 1
    for s in range(1, s_limit + 1):
        power *= 3
        gap = (1 << power.bit_length()) - power
        if s * power > 3 * verified_up_to * gap:
            return s - 1
    return s_limit


def contraction_sums(s_max: int, q: int = 3) -> dict:
    """For each s <= s_max: (k, word count, sum of C) over first-contraction words.

    A word's C updates as C -> q C + 2^t on a kick and C -> C on a halving, so the
    sum over all words needs one pair of integers per lattice cell, not a listing.

    Example: contraction_sums(3)[3] = (5, 2, 42)    -- C = 19 and C = 23
    """
    alive = {0: (1, 0)}     # kicks -> (word count, sum of C) for prefixes of length t
    finished = {}
    t = 0
    while alive and min(alive) <= s_max:
        grown = {}
        for kicks, (count, total) in alive.items():
            for j, c_sum in ((kicks + 1, q * total + (1 << t) * count), (kicks, total)):
                if q ** j > 1 << (t + 1):
                    held = grown.get(j, (0, 0))
                    grown[j] = (held[0] + count, held[1] + c_sum)
                elif j <= s_max:
                    held = finished.get(j, (t + 1, 0, 0))
                    finished[j] = (t + 1, held[1] + count, held[2] + c_sum)
        alive = grown
        t += 1
    return finished


def capture_cross_section(s_max: int = 800, q: int = 3) -> float:
    """Sigma = E[F(w)]: the Haar mean horizon of the first contraction word of qx + 1.

    It is the sum of F(w) / 2^k over all first-contraction words. For qx + a every
    horizon scales by a, so a word of length k captures a F(w) / 2^k + O(1)
    integers, and the number of captured n grows like Sigma a. This is the
    mass-radius relation, with the constant Sigma in the place of 2 G / c^2.

    Example: round(capture_cross_section(), 4) = 1.8137 for q = 3
    """
    total = Fraction(0)
    for s, (k, _, sum_c) in contraction_sums(s_max, q).items():
        total += Fraction(sum_c, ((1 << k) - q ** s) << k)
    return float(total)


def horizon_table(start: int, end: int, system: CollatzLike = COLLATZ) -> pd.DataFrame:
    """Batch view: one row per n in [start, end) with its first contraction word.

    Columns are n, k (word length), kicks (digits with q_r > 1), horizon, mass,
    beta, compactness and captured. Horizon and compactness are floats here. Use
    horizon() and compactness() when exactness matters.
    """
    if start < 1:
        raise ValueError("start must be a positive integer")
    rows = []
    for n in range(start, end):
        word = contraction_word(n, system)
        if word is None:
            rows.append({"n": n, "k": None, "kicks": None, "horizon": None, "mass": None,
                         "beta": None, "compactness": None, "captured": None})
            continue
        radius = horizon(word, system)
        rows.append({
            "n": n,
            "k": len(word),
            "kicks": sum(system.q[r] > 1 for r in word),
            "horizon": float(radius),
            "mass": float(word_mass(word, system)),
            "beta": bits_destroyed(word, system),
            "compactness": float(radius / n),
            "captured": radius >= n,
        })
    return pd.DataFrame(rows)
