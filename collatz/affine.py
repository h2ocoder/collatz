"""Exact affine structure of dropping orbits.

The Affine Orbit Structure theorem (docs/Conjectures/Affine Orbit
Structure.md) proves that within each residue subgroup mod 2^(k-s) of
Dropping Set D_k, every element of the dropping orbit is an exact affine
function of the starting value:

    f^j(n) = a_j * n + b_j,   j = 0 .. k-1,

with (a_0, b_0) = (1, 0) and the recursion

    even step:  (a, b) -> (a/2, b/2)
    odd step:   (a, b) -> (3a, 3b + 1)

The parity word is determined by n mod 2^(k-s), so the coefficient profile
is a subgroup invariant.  Consequently the orbit sum sum_j f^j(n) = A*n + B
and the destination dest(n) = lambda*n + C are affine with subgroup-constant
(A, B, lambda, C).  This module exposes those coefficients exactly (as
Fractions), both from a concrete n and from a subgroup's alpha-tuple
(see collatz/lfunctions/lattice_paths.py).
"""
from __future__ import annotations

from fractions import Fraction

import numpy as np

from .core import collatz_step


def affine_orbit_profile(n: int) -> list[tuple[Fraction, Fraction]]:
    """Exact coefficients [(a_j, b_j)] with f^j(n) = a_j*n + b_j for the dropping orbit.

    Follows n's actual parity word until the orbit first drops below n.
    Length equals the dropping time k; the destination (step k) is excluded,
    matching the dropping-orbit convention of `collatz.dropping.dropping_orbit`.

    Example: affine_orbit_profile(5) == [(1, 0), (3, 1), (3/2, 1/2)]
             (orbit 5 -> 16 -> 8 -> 4; three steps, destination excluded)
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    start = n
    a, b = Fraction(1), Fraction(0)
    profile = [(a, b)]
    while True:
        if n % 2 == 0:
            a, b = a / 2, b / 2
        else:
            a, b = 3 * a, 3 * b + 1
        n = collatz_step(n)
        if n < start:
            return profile
        profile.append((a, b))


def affine_destination_coefficients(n: int) -> tuple[Fraction, Fraction]:
    """Exact (lambda, C) with dest(n) = lambda*n + C, constant on n's subgroup.

    Example: affine_destination_coefficients(5) == (Fraction(3, 4), Fraction(1, 4))
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    start = n
    a, b = Fraction(1), Fraction(0)
    while True:
        if n % 2 == 0:
            a, b = a / 2, b / 2
        else:
            a, b = 3 * a, 3 * b + 1
        n = collatz_step(n)
        if n < start:
            return a, b


def orbit_sum(n: int) -> int:
    """Sum of the dropping orbit [n, f(n), ..., f^(k-1)(n)] (destination excluded).

    Example: orbit_sum(5) == 5 + 16 + 8 == 29
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    start = n
    total = n
    while True:
        n = collatz_step(n)
        if n < start:
            return total
        total += n


def orbit_max(n: int) -> int:
    """Maximum of the dropping orbit (destination excluded).

    Example: orbit_max(5) == 16
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    start = n
    peak = n
    while True:
        n = collatz_step(n)
        if n < start:
            return peak
        peak = max(peak, n)


def orbit_sum_coefficients(n: int) -> tuple[Fraction, Fraction]:
    """Exact (A, B) with orbit_sum(m) = A*m + B for every m in n's subgroup.

    Example: orbit_sum_coefficients(5) == (Fraction(11, 2), Fraction(3, 2))
             (A*5 + B = 55/2 + 3/2 = 29 = orbit_sum(5))
    """
    profile = affine_orbit_profile(n)
    return (
        sum(a for a, _ in profile),
        sum(b for _, b in profile),
    )


def profile_from_alphas(alphas: tuple[int, ...]) -> list[tuple[Fraction, Fraction]]:
    """Coefficient profile for the subgroup with alpha-tuple (alpha_1..alpha_s).

    The parity word is: odd step, alpha_1 halvings, odd step, alpha_2
    halvings, ..., odd step, alpha_s halvings — the dropping orbit of any
    n ≡ 3 (mod 4) member (or n ≡ 1 mod 4 for s = 1, alphas = (2,)).
    Length k = s + sum(alphas); destination excluded.
    """
    if not alphas or any(a < 1 for a in alphas):
        raise ValueError("alphas must be a non-empty tuple of positive ints")
    a, b = Fraction(1), Fraction(0)
    profile = [(a, b)]
    for i, alpha in enumerate(alphas):
        a, b = 3 * a, 3 * b + 1
        profile.append((a, b))
        for j in range(alpha):
            a, b = a / 2, b / 2
            # the very last halving lands on the destination, which the
            # dropping orbit excludes
            if i == len(alphas) - 1 and j == alpha - 1:
                return profile
            profile.append((a, b))
    return profile


def residue_from_alphas(alphas: tuple[int, ...]) -> int:
    """The residue r mod 2^(k-s) of the subgroup with alpha-tuple (alpha_1..alpha_s).

    Every large n ≡ r (mod 2^(k-s)) follows the parity word
    [odd, alpha_1 evens, odd, alpha_2 evens, ...] and so has dropping time
    k = s + sum(alphas).  Computed by 2-adic bit-lifting: each step whose
    parity is not yet determined by the known bits of r fixes one more bit.

    Example: residue_from_alphas((2,)) == 1      (n ≡ 1 mod 4)
    Example: residue_from_alphas((1, 3)) == 3    (n ≡ 3 mod 16)
    """
    if not alphas or any(a < 1 for a in alphas):
        raise ValueError("alphas must be a non-empty tuple of positive ints")
    word: list[int] = []
    for a in alphas:
        word += [1] + [0] * a
    k = len(word)
    s = len(alphas)
    r, t = 1, 1          # bit 0 fixed: members are odd
    x = 1                # trajectory of the representative r
    halvings, odd_steps = 0, 0
    for w in word:
        if halvings + 1 > t:
            # parity of the current value needs bit t of r; adding 2^t
            # shifts the current value by 3^odd_steps (odd), flipping parity
            if (x & 1) != w:
                r += 1 << t
                x += 3**odd_steps
            t += 1
        if w:
            if x & 1 == 0:
                raise AssertionError("parity word inconsistent (odd step)")
            x = 3 * x + 1
            odd_steps += 1
        else:
            if x & 1:
                raise AssertionError("parity word inconsistent (even step)")
            x >>= 1
            halvings += 1
    if t != k - s:
        raise AssertionError(f"expected {k - s} bits, fixed {t}")
    return r


def sieve_dropping(n_max: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Vectorized dropping-time / destination / orbit-sum sieve for n = 2..n_max.

    Returns (ktime, dest, osum), each of length n_max + 1 (indices 0 and 1
    unused, set to 0).  osum is the dropping-orbit sum (destination excluded),
    matching `orbit_sum`.  All arrays int64; raises on int64 overflow risk.
    """
    if n_max < 2:
        raise ValueError("n_max must be >= 2")
    cur = np.arange(n_max + 1, dtype=np.int64)
    osum = cur.copy()
    dest = np.zeros(n_max + 1, dtype=np.int64)
    ktime = np.zeros(n_max + 1, dtype=np.int32)
    osum[:2] = 0
    idx = np.arange(2, n_max + 1, dtype=np.int64)
    step = 0
    while idx.size:
        step += 1
        c = cur[idx]
        if c.max() > (1 << 61):
            raise OverflowError("orbit value approaching int64 limit")
        odd = c & 1 == 1
        c = np.where(odd, 3 * c + 1, c >> 1)
        cur[idx] = c
        dropped = c < idx
        d_idx = idx[dropped]
        dest[d_idx] = c[dropped]
        ktime[d_idx] = step
        idx = idx[~dropped]
        osum[idx] += cur[idx]
    return ktime, dest, osum


def subgroup_summary(alphas: tuple[int, ...]) -> dict:
    """Exact affine invariants of one subgroup, keyed for batch analysis.

    Returns dict with: s, k, alphas, A (orbit-sum slope), B (orbit-sum
    intercept), P (peak coefficient max_j a_j), lam (destination slope),
    C (destination intercept).  All coefficient values are Fractions.
    """
    profile = profile_from_alphas(alphas)
    s = len(alphas)
    k = s + sum(alphas)
    a_last, b_last = profile[-1]
    return {
        "s": s,
        "k": k,
        "alphas": alphas,
        "A": sum(a for a, _ in profile),
        "B": sum(b for _, b in profile),
        "P": max(a for a, _ in profile),
        "lam": a_last / 2,
        "C": b_last / 2,
    }
