"""Orbit-twisted character sums: the Phase 1 statistics.

For a character chi on Z[omega], we sum chi evaluated on various Collatz-
derived Eisenstein lifts of odd integers n <= N. The sum is compared to
sqrt(N) (the GRH-style bound).

Statistics:
  - D_chi(N): pair-lift sum sum_{n odd <= N} chi(n + dest(n)*omega)
  - T_chi(N): stopping-time sum    sum_{n odd <= N} chi(n) * T(n)
  - sector_chi(N): sector sum     sum_{n odd <= N} chi(pi)^{s(n)}

For sector_chi we use chi(pi). Phase 1 chi (chi_3, chi_6) has chi(pi) = 0
since pi divides the conductor; so this statistic is identically zero in
Phase 1 and becomes meaningful only in Phase 2 with a character coprime
to pi.
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass

from collatz.core import stopping_time

from .characters import HeckeCharacter
from .eisenstein import EisensteinInt, pi
from .orbit_lift import (
    eisenstein_sector,
    iota,
    oddity_count,
    orbit_pair,
)


@dataclass
class TwistedSumResult:
    statistic: str
    character: str
    N: int
    n_terms: int
    raw_sum: complex
    abs_sum: float
    bound_sqrt_N: float
    bound_n_logn: float
    ratio_to_sqrt_N: float

    def summary(self) -> str:
        return (
            f"{self.statistic}[{self.character}] N={self.N}: "
            f"|sum|={self.abs_sum:.3f}, sqrt(N)={self.bound_sqrt_N:.3f}, "
            f"|sum|/sqrt(N)={self.ratio_to_sqrt_N:.3f}, "
            f"|sum|/N={self.abs_sum / max(self.N, 1):.4g}, "
            f"terms={self.n_terms}"
        )


def D_chi(chi: HeckeCharacter, N: int) -> TwistedSumResult:
    """Pair-lift orbit sum: sum_{n odd, 3 <= n <= N} chi(n + dest(n) * omega)."""
    total = 0.0 + 0j
    count = 0
    for n in range(3, N + 1, 2):
        alpha = orbit_pair(n)
        total += chi.evaluate(alpha)
        count += 1
    abs_sum = abs(total)
    sqrtN = math.sqrt(N)
    n_logn = sqrtN * max(math.log(N), 1)
    return TwistedSumResult(
        statistic="D_chi",
        character=chi.name,
        N=N,
        n_terms=count,
        raw_sum=total,
        abs_sum=abs_sum,
        bound_sqrt_N=sqrtN,
        bound_n_logn=n_logn,
        ratio_to_sqrt_N=abs_sum / sqrtN if sqrtN > 0 else 0.0,
    )


def T_chi(chi: HeckeCharacter, N: int) -> TwistedSumResult:
    """Stopping-time-twisted sum: sum_{n odd, 3 <= n <= N} chi(n) * T(n)."""
    total = 0.0 + 0j
    count = 0
    for n in range(3, N + 1, 2):
        c = chi.evaluate(iota(n))
        if c == 0:
            count += 1
            continue
        T = stopping_time(n)
        total += c * T
        count += 1
    abs_sum = abs(total)
    sqrtN = math.sqrt(N)
    return TwistedSumResult(
        statistic="T_chi",
        character=chi.name,
        N=N,
        n_terms=count,
        raw_sum=total,
        abs_sum=abs_sum,
        bound_sqrt_N=sqrtN,
        bound_n_logn=sqrtN * max(math.log(N), 1),
        ratio_to_sqrt_N=abs_sum / sqrtN if sqrtN > 0 else 0.0,
    )


def sector_chi(chi: HeckeCharacter, N: int) -> TwistedSumResult:
    """Sector sum: sum_{n odd, 3 <= n <= N} chi(pi)^{s(n)}.

    Probes the distribution of the Eisenstein sector index s(n) mod 12
    (oddity count modulo 12).
    """
    cpi = chi.evaluate(pi)
    total = 0.0 + 0j
    count = 0
    for n in range(3, N + 1, 2):
        s = oddity_count(n)
        if cpi == 0:
            # zero on pi; the only contribution is when s == 0 (chi(pi)^0 = 1)
            if s == 0:
                total += 1.0
        else:
            total += cpi ** s
        count += 1
    abs_sum = abs(total)
    sqrtN = math.sqrt(N)
    return TwistedSumResult(
        statistic="sector_chi",
        character=chi.name,
        N=N,
        n_terms=count,
        raw_sum=total,
        abs_sum=abs_sum,
        bound_sqrt_N=sqrtN,
        bound_n_logn=sqrtN * max(math.log(N), 1),
        ratio_to_sqrt_N=abs_sum / sqrtN if sqrtN > 0 else 0.0,
    )


def D_chi_by_sector(
    chi: HeckeCharacter, N: int
) -> dict[int, complex]:
    """Pair-lift sum split by Eisenstein sector s(n) mod 12.

    Returns a dict {sector_index: sum_chi}. Useful for visualizing whether
    the orbit-twisted sum has bias on any of the 12 sectors.
    """
    sums: dict[int, complex] = {k: 0.0 + 0j for k in range(12)}
    for n in range(3, N + 1, 2):
        alpha = orbit_pair(n)
        v = chi.evaluate(alpha)
        if v == 0:
            continue
        sec = eisenstein_sector(n)
        sums[sec] += v
    return sums


def D_chi_by_dropping_set(
    chi: HeckeCharacter, N: int
) -> dict[int, tuple[complex, int]]:
    """Pair-lift sum split by Dropping Set Dset_k = (oddity, stopping-time).

    Returns {(s, T): (sum_chi, count)}.
    """
    sums: dict[int, tuple[complex, int]] = {}
    for n in range(3, N + 1, 2):
        alpha = orbit_pair(n)
        v = chi.evaluate(alpha)
        s = oddity_count(n)
        cur, cnt = sums.get(s, (0.0 + 0j, 0))
        sums[s] = (cur + v, cnt + 1)
    return sums


def sector_twist_chi(
    chi: HeckeCharacter, k: int, N: int
) -> TwistedSumResult:
    """Sector-twisted orbit-pair sum.

    D_{chi, k}(N) = sum_{n odd, 3 <= n <= N} chi(orbit_pair(n)) * exp(2 pi i k s(n) / 12)

    where s(n) is the Eisenstein sector (oddity count mod 12). For k=0 this
    coincides with D_chi(N); for k=1..11 it extracts the k-th Fourier
    component of the orbit-pair distribution along the sector index.

    Captures the period-12 sector dynamics that no single Hecke character on
    Z[omega] of small conductor can express directly.
    """
    if not (0 <= k < 12):
        raise ValueError("k must be in 0..11")
    omega12 = cmath.exp(2j * math.pi * k / 12)
    total = 0.0 + 0j
    count = 0
    for n in range(3, N + 1, 2):
        alpha = orbit_pair(n)
        v = chi.evaluate(alpha)
        if v == 0:
            count += 1
            continue
        s = oddity_count(n) % 12
        total += v * (omega12 ** s)
        count += 1
    abs_sum = abs(total)
    sqrtN = math.sqrt(N)
    return TwistedSumResult(
        statistic=f"sector_twist_chi(k={k})",
        character=chi.name,
        N=N,
        n_terms=count,
        raw_sum=total,
        abs_sum=abs_sum,
        bound_sqrt_N=sqrtN,
        bound_n_logn=sqrtN * max(math.log(N), 1),
        ratio_to_sqrt_N=abs_sum / sqrtN if sqrtN > 0 else 0.0,
    )
