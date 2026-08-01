"""Equidistribution of avoidance-class residues: the second-moment experiment.

Every length-n avoidance word w = ((d_1,g_1),...,(d_n,g_n)), d_i in {2,3},
is realized by exactly one residue class r_w mod 2^E, E = 1 + sum(d_i + g_i)
(2-adic pullback / Terras correspondence; ALL such words are realizable, the
machine's fuel constraints being encoded automatically in the class bits).

The Three-Bit Countdown needs anti-concentration: no r_w < (4/3 - eps)^n.
Front 1 closed the analogous gap for cycle constants with a second-moment /
Parseval bound, which works when the residue set is spectrally flat. This
script measures, for each (n, E) bucket:

  * N(n, E), the word count, and the density N / 2^(E-1)
  * the minimal residue vs the uniform prediction 2^(E-1)/N (order statistic:
    expected min ~ 2^(E-1)/N for a "random" set)
  * dyadic-interval discrepancy: max over intervals [0, 2^j) of
    |#hits - N 2^j/2^E| / sqrt(N)   (sqrt-normalized, CLT scale)
  * spectral flatness: max_k |S(k)|/N over sampled frequencies k,
    S(k) = sum_w e(k r_w / 2^E) - power-saving here is what a Parseval proof
    of the countdown needs.

Cross-check: the union over words of small residues must reproduce the sieve
values A(n) for the same n (an integer m avoids n encounters iff m = r_w for
its own word).
"""

from __future__ import annotations

import cmath
import math
import random
from collections import defaultdict


def enumerate_classes(n: int, g_cap: int):
    """DFS over reversed words, pulling the class constraint back through each
    prepended step.  Yields (r, E_bits) per full word; constraint state is
    (rho, mu): value = rho mod 2^mu, rho odd."""
    inv3 = {}
    maxmu = 2 + n * (3 + g_cap) + 2
    for mu in range(1, maxmu + 1):
        inv3[mu] = pow(3, -1, 1 << mu)

    out = []

    def prepend_step(rho: int, mu: int, halvings: int):
        """value -> (3*value+1)/2^halvings == rho mod 2^mu; return (rho', mu')."""
        mu2 = mu + halvings
        return (inv3[mu2] * (((rho << halvings) - 1) % (1 << mu2))) % (1 << mu2), mu2

    def dfs(depth: int, rho: int, mu: int):
        if depth == n:
            out.append((rho, mu))
            return
        for d in (2, 3):
            for g in range(g_cap + 1):
                r2, m2 = rho, mu
                for _ in range(g):          # growth steps nearest the suffix
                    r2, m2 = prepend_step(r2, m2, 1)
                r2, m2 = prepend_step(r2, m2, d)
                dfs(depth + 1, r2, m2)

    dfs(0, 1, 1)  # empty suffix: value merely odd
    return out


def analyze(n: int, g_cap: int, seed: int = 1) -> None:
    classes = enumerate_classes(n, g_cap)
    buckets: dict[int, list[int]] = defaultdict(list)
    for r, e in classes:
        buckets[e].append(r)
    print(f"\n=== n = {n} encounters, g <= {g_cap}: {len(classes)} words, "
          f"E-buckets {min(buckets)}..{max(buckets)} ===")
    print(f"{'E':>4} {'N':>9} {'density':>10} {'min r':>12} {'unif pred':>12} "
          f"{'ratio':>7} {'disc/sqrtN':>11} {'max|S|/N':>9}")

    rng = random.Random(seed)
    glob_min = None
    for e in sorted(buckets):
        rs = buckets[e]
        N = len(rs)
        mod = 1 << e
        assert len(set(rs)) == N, "Terras bijection violated"
        rmin = min(rs)
        glob_min = rmin if glob_min is None else min(glob_min, rmin)
        pred = mod / 2 / N
        # dyadic discrepancy
        disc = 0.0
        for j in range(2, e):
            hits = sum(1 for r in rs if r < (1 << j))
            disc = max(disc, abs(hits - N * (1 << j) / mod))
        # spectral flatness over sampled odd and structured frequencies
        ks = {1, 3, 5, mod // 2 - 1, mod // 4 + 1}
        ks |= {rng.randrange(1, mod) | 1 for _ in range(40)}
        ks |= {(1 << j) + 1 for j in range(1, e - 1, 3)}
        smax = 0.0
        for k in ks:
            s = sum(cmath.exp(2j * math.pi * ((k * r) % mod) / mod) for r in rs)
            smax = max(smax, abs(s))
        print(f"{e:>4} {N:>9} {N/(mod/2):>10.2e} {rmin:>12} {pred:>12.1f} "
              f"{rmin/pred:>7.2f} {disc/math.sqrt(N):>11.2f} {smax/N:>9.3f}")
    print(f"global min residue over all E at n={n}: {glob_min}")


if __name__ == "__main__":
    analyze(6, 3)
    analyze(8, 2)
