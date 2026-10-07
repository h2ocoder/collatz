"""Shared helpers for the harmonic_cycles thread (thread 1 of the '36' investigation).

CONVENTIONS (used by every script in this directory)
----------------------------------------------------
* Shortcut (Terras) map, generalised:
      T_{q,c}(n) = n/2            if n is even
                   (q*n + c)/2    if n is odd          (q, c odd)
  The Collatz case is q = 3, c = 1.  The map is defined on all of Z.
* A parity word w = (w_0, ..., w_{k-1}) records w_j = parity of T^j(n).
  k = len(w) is the number of shortcut steps (so each odd step already
  contains one halving), s = sum(w) is the number of odd steps.
  This is NOT the step count of collatz.core / collatz.dropping in the repo,
  which use the non-shortcut map n -> 3n+1 (k_repo = k + s).
* Along w the map is affine:  T_w(x) = (q^s x + c*C(w)) / 2^k  with
      C(w) = sum over j with w_j = 1 of  q^(number of ones after j) * 2^j.
* "Cell" (k, s) = all words of length k with s ones.  Cell denominator
      D(k, s) = 2^k - q^s.
  The fixed point of T_w is x(w) = c*C(w) / D(k, s).
"""
from fractions import Fraction
from math import comb, gcd


def T(n, q=3, c=1):
    """One shortcut step of the (q x + c)/2 map on Z."""
    return n // 2 if n % 2 == 0 else (q * n + c) // 2


def word_constant(w, q=3):
    """C(w): T_w(x) = (q^s x + C(w)) / 2^k."""
    C = 0
    for j, b in enumerate(w):
        if b:
            C = q * C + (1 << j)
    return C


def cell_denominator(k, s, q=3):
    return 2 ** k - q ** s


def fixed_point(w, q=3, c=1):
    """Exact rational fixed point of the affine word map."""
    k, s = len(w), sum(w)
    return Fraction(c * word_constant(w, q), cell_denominator(k, s, q))


def parity_word(n, k, q=3, c=1):
    """First k parities of the T_{q,c}-orbit of n, and T^k(n)."""
    w = []
    for _ in range(k):
        w.append(n & 1)
        n = T(n, q, c)
    return tuple(w), n


def orbit(n, k, q=3, c=1):
    out = [n]
    for _ in range(k - 1):
        n = T(n, q, c)
        out.append(n)
    return out


def rotations(w):
    return [w[i:] + w[:i] for i in range(len(w))]


def is_primitive(w):
    k = len(w)
    return all(w[i:] + w[:i] != w for i in range(1, k))


def necklace_rep(w):
    return min(rotations(w))


def words(k, s):
    """All binary words of length k with s ones, as tuples."""
    from itertools import combinations
    for pos in combinations(range(k), s):
        w = [0] * k
        for p in pos:
            w[p] = 1
        yield tuple(w)


def mobius(n):
    res, p = 1, 2
    while p * p <= n:
        if n % p == 0:
            n //= p
            if n % p == 0:
                return 0
            res = -res
        p += 1
    if n > 1:
        res = -res
    return res


def n_primitive_necklaces(k, s):
    """Number of primitive (aperiodic) binary necklaces with k beads, s ones."""
    if k == 0:
        return 0
    g = gcd(k, s)
    tot = 0
    for d in range(1, g + 1):
        if g % d == 0:
            tot += mobius(d) * comb(k // d, s // d)
    return tot // k


def factorint_small(n):
    """Trial-division factorisation, fine for |n| < 1e14 or smooth-ish n."""
    n = abs(n)
    out = {}
    p = 2
    while p * p <= n:
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
        p += 1 if p == 2 else 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def fmt_factor(n):
    if abs(n) == 1:
        return "1"
    f = factorint_small(n)
    return "*".join(f"{p}^{e}" if e > 1 else f"{p}" for p, e in sorted(f.items()))


class Tee:
    """print() to stdout and to a log file."""

    def __init__(self, path):
        self.f = open(path, "w", encoding="utf-8")

    def __call__(self, *a):
        line = " ".join(str(x) for x in a)
        print(line)
        self.f.write(line + "\n")

    def close(self):
        self.f.close()
