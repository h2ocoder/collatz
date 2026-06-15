# scripts/twin_dropping_orbit_search.py
"""Search for twin primes that share a Collatz dropping orbit.

Two twin primes (p, p+2) share a dropping orbit iff the smaller climbs to
the larger before falling below itself: p reaches p+2 under the Collatz map
with every intermediate value >= p.  Then p+2 lies *inside* dropping_orbit(p)
(it is reached before the first drop below p).  The descending direction
(p+2 -> p) does NOT count: it makes p the dropping *destination*, which
Paper 1's convention excludes from the orbit -- e.g. 7 -> ... -> 5 does not
put 5 and 7 in a common dropping orbit, since 5 is 7's excluded destination.

Empirically (this script) the ONLY such pairs up to 10^9 are (3, 5) and
(11, 13).  See docs/Explorations/Twin Primes in Dropping Orbits.md for the
1-step / 2-step path theorem that proves these are the only short-path
solutions.

Run:  python scripts/twin_dropping_orbit_search.py [LIMIT]
"""
from __future__ import annotations

import math
import sys

import numpy as np

from collatz.core import collatz_step

SEG = 1 << 23  # ~8.4M numbers per segment


def _base_primes(root: int) -> np.ndarray:
    """Primes up to `root` via a plain sieve (for the segmented sieve)."""
    sieve = np.ones(root + 1, dtype=bool)
    sieve[:2] = False
    for i in range(2, int(math.isqrt(root)) + 1):
        if sieve[i]:
            sieve[i * i :: i] = False
    return np.nonzero(sieve)[0]


def forward_steps(p: int, max_steps: int = 5000) -> int | None:
    """Collatz steps for p to reach p+2 while staying >= p, else None."""
    x, n = p, 0
    while n <= max_steps:
        x = collatz_step(x)
        n += 1
        if x == p + 2:
            return n
        if x < p:
            return None
    return None


def search(limit: int):
    """Yield (p, p+2, forward_steps, p mod 8) for co-occurring twin primes."""
    root = int(math.isqrt(limit)) + 1
    base = _base_primes(root)
    prev_prime = None
    lo = 2
    while lo <= limit:
        hi = min(lo + SEG, limit + 1)
        seg = np.ones(hi - lo, dtype=bool)
        for q in base:
            start = max(q * q, ((lo + q - 1) // q) * q)
            if start < hi:
                seg[start - lo :: q] = False
        for p in (np.nonzero(seg)[0] + lo):
            p = int(p)
            if prev_prime is not None and p - prev_prime == 2:
                tp = prev_prime
                fwd = forward_steps(tp)
                if fwd is not None:
                    yield (tp, tp + 2, fwd, tp % 8)
            prev_prime = p
        lo = hi


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000_000
    print(f"Searching twin primes (p, p+2) sharing a dropping orbit, up to {limit}...")
    hits = list(search(limit))
    print(f"\n{'(p, p+2)':>14}  {'steps':>6}  {'p mod 8':>7}")
    for p, q, fwd, m8 in hits:
        print(f"  ({p}, {q})".rjust(14) + f"  {fwd:>6}  {m8:>7}")
    print(f"\nTotal co-occurring twin pairs up to {limit}: {len(hits)}")


if __name__ == "__main__":
    main()
