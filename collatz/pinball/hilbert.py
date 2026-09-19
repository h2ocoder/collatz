"""The Hilbert-space side of the table, in finite checks.

The Terras map T preserves Haar measure on the 2-adic integers, so its Koopman
operator U f = f o T is an isometry of L^2(Z_2). At resolution 2^B this is the
statement that T: Z/2^B -> Z/2^(B-1) is exactly 2-to-1. Stopping classes are
disjoint unions of residue classes, so their indicator functions are orthogonal
vectors whose squared norms are the class densities.

This is classical probability in Hilbert-space clothing: the dynamics are
deterministic and no Bell-type inequality is violated (see
docs/Conjectures/Collatz Complementarity Principle.md).
"""

from fractions import Fraction

from collatz.pinball.table import PinballTable


def terras_preimage_counts(bits: int, q: int = 3, c: int = 1) -> set[int]:
    """Distinct preimage counts of T: Z/2^bits -> Z/2^(bits-1). Measure-preserving iff {2}.

    Example: terras_preimage_counts(8) = {2}
    """
    counts = [0] * (1 << (bits - 1))
    for n in range(1 << bits):
        image = (q * n + c) // 2 if n % 2 else n // 2
        counts[image % (1 << (bits - 1))] += 1
    return set(counts)


def class_densities(bits: int, q: int = 3, c: int = 1) -> dict:
    """Haar measure of each stopping class resolved by `bits` low bits.

    Returns {class k: Fraction}, with key None for the undecided remainder.
    These are the squared norms of the class indicator vectors.

    Example: class_densities(4)[3] = Fraction(1, 4);  [6] = Fraction(1, 16)
    """
    table = PinballTable(q, c, depth=bits)
    densities = {}
    for n in range(1 << bits):
        k = table.stopping_class(n)
        densities[k] = densities.get(k, 0) + Fraction(1, 1 << bits)
    return densities
