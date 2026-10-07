"""Shared helpers for the figurate / 2-adic thread (scripts/thirty_six/figurate_2adic).

CONVENTIONS (stated once here, repeated on every table):

* Shortcut (Terras) map for a generalised rule (q, d):
      T(n) = n/2            if n even
      T(n) = (q*n + d)/2    if n odd            (q, d odd)
  Collatz is (q, d) = (3, +1); the mirror is (3, -1); the 5x+1 control is (5, +1).

* Terras stopping time  sigma(n) = least k >= 1 with T^k(n) < n  (number of T-steps).
  We also record s = number of odd steps among those k.

* Repo "dropping time" (collatz.dropping.dropping_time, Paper 1) counts steps of the
  UN-shortcut map f(n) = n/2 | 3n+1, so
      repo_dropping_time(n) = sigma(n) + s(n) = k + s.
  Terras spectrum  k = 1, 2, 4, 5, 7, 8, 10, 12, ...   (OEIS A020914)
  Repo spectrum  k+s = 1, 3, 6, 8, 11, 13, 16, 19, ... (OEIS A122437)
  "Dropping Set_j" in the repo is indexed by j = k + s.

* Coefficient stopping time (cst) of a RESIDUE r mod 2^K: the least k <= K such that the
  first k parity letters of r have  q^s < 2^k.  It depends only on r mod 2^k.  For an actual
  integer n >= 2 the Terras stopping time equals cst except for finitely many small n per
  class (conjecturally only n in a cycle); every script counts the exceptions it meets.
"""

from math import gcd


def step(n, q=3, d=1):
    return n >> 1 if n % 2 == 0 else (q * n + d) >> 1


def stop(n, q=3, d=1, limit=100000):
    """Terras stopping data (k, s) of the integer n >= 2 under rule (q, d).

    Returns None if the orbit does not go below n within `limit` steps (cycle member
    or divergent-looking orbit).
    """
    x = n
    k = s = 0
    while k < limit:
        if x & 1:
            x = (q * x + d) >> 1
            s += 1
        else:
            x >>= 1
        k += 1
        if x < n:
            return k, s
    return None


def cst(r, K, q=3, d=1):
    """Coefficient stopping data (k, s) of the residue r mod 2^K, or None if cst > K.

    Uses the parity vector of r, which for the first K steps is determined by r mod 2^K.
    Criterion: first k with q^s < 2^k.
    """
    x = r
    s = 0
    pw3 = 1
    pw2 = 1
    for k in range(1, K + 1):
        if x & 1:
            x = (q * x + d) >> 1
            s += 1
            pw3 *= q
        else:
            x >>= 1
        pw2 <<= 1
        if pw3 < pw2:
            return k, s
    return None


def class_table(K, q=3, d=1):
    """Return (lab, counts): lab[r] = cst k of residue r mod 2^K (0 if undetermined),
    counts[k] = number of residues mod 2^K with cst exactly k."""
    M = 1 << K
    lab = [0] * M
    counts = {}
    for r in range(M):
        c = cst(r, K, q, d)
        k = c[0] if c else 0
        lab[r] = k
        counts[k] = counts.get(k, 0) + 1
    return lab, counts


def primitive_counts(K, q=3, d=1):
    """N(k) = number of residues mod 2^k with cst exactly k, for k <= K.

    counts_at_level_K[k] = N(k) * 2^(K-k), so N(k) = counts[k] >> (K-k)."""
    _, counts = class_table(K, q, d)
    return {k: counts[k] >> (K - k) for k in sorted(counts) if k}


# OEIS A100982 (number of admissible sequences of order j), offset 1 here = s odd steps.
# Hard-coded from the OEIS b-file head; q21 recomputes and compares.
A100982 = [1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, 17637, 51033,
           108950, 312455, 663535, 1900470, 5936673]
# OEIS A020914: number of binary digits of 3^s  = Terras stopping time with s odd steps (s>=1)
A020914 = [1, 2, 4, 5, 7, 8, 10, 12, 13, 15, 16, 18, 20, 21, 23, 24, 26, 27, 29, 31, 32]


def v2(n):
    if n == 0:
        return None
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k


def tri(n):
    return n * (n + 1) // 2


def polygonal(s, n):
    return ((s - 2) * n * n - (s - 4) * n) // 2


class Tee:
    """print to stdout and to a log file."""

    def __init__(self, path):
        self.f = open(path, "w", encoding="utf-8")

    def __call__(self, *args):
        line = " ".join(str(a) for a in args)
        print(line)
        self.f.write(line + "\n")

    def close(self):
        self.f.close()
