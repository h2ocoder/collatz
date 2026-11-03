"""The reversible tape: nothing is destroyed until the parity record is thrown away.

T is many-to-one, but n -> (T^t(n), word) is one-to-one: the value and the word
together rebuild n. So "bits destroyed" means bits moved onto a tape, and the
price of forgetting them is Landauer's.

Take n uniform over one full period mod d^B. Then the word of length t has
min(t, B) log2 d bits, the pair (value, word) has B log2 d bits, and

    I(value; word) = H(value) + H(word) - H(pair)

rises until t = B and then falls, the shape of a Page curve. It is a classical
mutual information. Nothing here is quantum, and the kink at t = B is pigeonhole.
See research/information-schwarzschild-radius/Toy Physics Systems.md.
"""

import numpy as np
import pandas as pd

from collatz.schwarzschild.system import COLLATZ, CollatzLike


def emit(n: int, t: int, system: CollatzLike = COLLATZ) -> tuple[int, tuple[int, ...]]:
    """(T^t(n), word): t forward steps, keeping the record.

    Example: emit(5, 2) = (4, (1, 0))
    """
    word = []
    for _ in range(t):
        word.append(n % system.d)
        n = system.step(n)
    return n, tuple(word)


def absorb(value: int, word, system: CollatzLike = COLLATZ) -> int:
    """The inverse of emit: run the word backwards from value.

    Example: absorb(4, (1, 0)) = 5
    """
    for r in reversed(word):
        value = (system.d * value - system.a[r]) // system.q[r]
    return value


def causal_depth(n: int, position: int, t: int, system: CollatzLike = COLLATZ) -> bool:
    """True if adding d^position to n leaves the first t digits of the word unchanged.

    The first `position` digits of the word never see this address digit, and that
    is the causal cone. Digit `position` of the word always does.

    Example: causal_depth(27, 5, 5) = True;  causal_depth(27, 5, 6) = False
    """
    return system.word(n, t) == system.word(n + system.d ** position, t)


def _entropy_of(values: np.ndarray) -> float:
    _, counts = np.unique(values, return_counts=True)
    probabilities = counts / counts.sum()
    return float(-(probabilities * np.log2(probabilities)).sum())


def page_curve(digits: int, steps: int, system: CollatzLike = COLLATZ) -> pd.DataFrame:
    """Exact entropies over one full period n in [d^digits, 2 d^digits).

    Columns: t, value_entropy H(T^t(n)), word_entropy H(word_t) = min(t, digits)
    log2 d, and mutual_information I(value; word). All are in bits.

    Falls back to exact Python integers if a value could overflow 64 bits.
    """
    d = system.d
    bits_per_digit = np.log2(d)
    values = np.arange(d ** digits, 2 * d ** digits, dtype=np.int64)
    q = np.array(system.q, dtype=np.int64)
    a = np.array(system.a, dtype=np.int64)
    limit = (1 << 62) // max(system.q)
    rows = []
    for t in range(steps + 1):
        value_entropy = _entropy_of(values)
        word_entropy = min(t, digits) * bits_per_digit
        rows.append({
            "t": t,
            "value_entropy": value_entropy,
            "word_entropy": word_entropy,
            "mutual_information": value_entropy + word_entropy - digits * bits_per_digit,
        })
        if values.dtype == object or int(np.abs(values).max()) >= limit:
            values = np.array([system.step(int(v)) for v in values], dtype=object)
        else:
            residues = values % d
            values = (q[residues] * values + a[residues]) // d
    return pd.DataFrame(rows)


def erased_bits(trits: int, tolerance: float = 1e-13, max_iterations: int = 200_000) -> dict:
    """The stationary law of the coin recursion on Z / 3^m, and what one step erases.

    Runs x -> x / 2 or (3x + 1) / 2 with a fair coin until the law on Z / 3^m
    settles, then returns H(y mod 3^m) as "entropy" and H(coin | y mod 3^m) as
    "erased". The exact relation between levels m - 1 and m is

        erased(m) = 1 - (entropy(m) - entropy(m - 1)) / 2

    which erased_bits(m)["identity_gap"] measures. The limit is g = 1 - log2(3) / 2
    exactly when the residues are used at full capacity.
    """
    if trits < 1:
        raise ValueError("trits must be at least 1")
    laws = {}
    for level in (trits - 1, trits):
        modulus = 3 ** level
        half = (modulus + 1) // 2
        x = np.arange(modulus, dtype=np.int64)
        halve = (x * half) % modulus
        kick = (((3 * x + 1) % modulus) * half) % modulus
        law = np.full(modulus, 1 / modulus)
        for _ in range(max_iterations):
            new = 0.5 * (np.bincount(halve, law, modulus) + np.bincount(kick, law, modulus))
            done = np.abs(new - law).sum() < tolerance
            law = new
            if done:
                break
        laws[level] = (law, halve, kick)
    law, halve, kick = laws[trits]
    from_halve = 0.5 * np.bincount(halve, law, 3 ** trits)
    from_kick = 0.5 * np.bincount(kick, law, 3 ** trits)
    total = from_halve + from_kick
    mask = (from_halve > 0) & (from_kick > 0)
    erased = -float((from_halve[mask] * np.log2(from_halve[mask] / total[mask])
                     + from_kick[mask] * np.log2(from_kick[mask] / total[mask])).sum())

    def entropy(p):
        p = p[p > 0]
        return float(-(p * np.log2(p)).sum())

    upper, lower = entropy(law), entropy(laws[trits - 1][0])
    return {"entropy": upper, "erased": erased,
            "identity_gap": erased - (1 - (upper - lower) / 2)}
