"""Phase A of the three-bit countdown search: ansatz family I(m) = v2(m - a).

Both proved countdown invariants are 2-adic distances to fixed rationals:
  I2 = v2(m+1)   (One-Bit: decreases by exactly 1 per non-dropping step)
  I3 = v2(m-1)/2 (Two-Bit: decreases per immediate weak Set_3 drop)
and drop depth itself is v2-distance to -1/3.  This script tests whether any
member of the family v2(m - a), a in a curated set of odd constants and 2-adic
truncations of small rationals, behaves as a countdown along orbits that AVOID
strong drops (v2(3m+1) >= 4).

Avoidance streak = maximal run of consecutive Set_3 encounters (m = 1 mod 4)
with depth d = v2(3m+1) in {2,3}, i.e. m mod 16 in {1, 9, 13}.

For each candidate we measure, over all consecutive encounter pairs inside
streaks: P(decrease), P(same), P(increase), the maximum run of consecutive
increases, and whether I at streak start bounds the remaining streak length.
A true countdown must have max-increase-run bounded (ideally 0-1) and
streak_length <= c * I(start) with c constant across the sample.

Exact integer arithmetic throughout; floats only in the summary/plot.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collatz.core import v2  # noqa: E402


def trunc_2adic(frac: Fraction, bits: int) -> int:
    """2-adic truncation of p/q (q odd) mod 2^bits, as an integer in [0, 2^bits)."""
    p, q = frac.numerator, frac.denominator
    mod = 1 << bits
    return (p * pow(q, -1, mod)) % mod


def build_candidates(bits: int = 10) -> dict[str, int]:
    """Candidate targets a for I(m) = v2(m - a)."""
    cands: dict[str, int] = {}
    for a in [1, -1, 3, -3, 5, -5, 7, -7, 9, -9, 11, 13, 21, 85]:
        cands[f"a={a}"] = a
    for num, den in [(-1, 3), (1, 3), (-1, 9), (1, 9), (5, 3), (-5, 3), (7, 9), (-7, 9)]:
        fr = Fraction(num, den)
        cands[f"a={num}/{den}|{bits}b"] = trunc_2adic(fr, bits)
    return cands


def syracuse_encounters(m: int):
    """Yield (encounter_value, depth) at each Set_3 encounter of the Syracuse
    orbit of odd m, until the orbit reaches 1."""
    while m != 1:
        if m % 4 == 3:
            m = (3 * m + 1) // 2
            continue
        d = v2(3 * m + 1)
        yield m, d
        m = (3 * m + 1) >> d


def collect_streaks(max_n: int, min_len: int):
    """Maximal avoidance streaks (list of encounter values, all depth in {2,3})
    of length >= min_len, deduped by first value."""
    seen_starts: set[int] = set()
    streaks: list[list[int]] = []
    for m0 in range(3, max_n, 2):
        cur: list[int] = []
        for val, d in syracuse_encounters(m0):
            if d >= 4:
                if len(cur) >= min_len and cur[0] not in seen_starts:
                    seen_starts.add(cur[0])
                    streaks.append(cur)
                cur = []
            else:
                cur.append(val)
        if len(cur) >= min_len and cur[0] not in seen_starts:
            seen_starts.add(cur[0])
            streaks.append(cur)
    return streaks


def sanity_checks() -> None:
    """Reproduce the proved residue characterizations before trusting anything."""
    for m in range(1, 1 << 16, 4):
        d = v2(3 * m + 1)
        assert (d == 2) == (m % 8 == 1), m
        assert (d == 3) == (m % 16 == 13), m
        assert (d >= 4) == (m % 16 == 5), m
    # One-bit countdown: v2(m+1) drops by exactly 1 per non-dropping step
    for m in range(3, 1 << 14, 4):
        s = (3 * m + 1) // 2
        assert v2(s + 1) == v2(m + 1) - 1, m
    print("sanity checks passed (residue depth classes + one-bit countdown)")


def evaluate(streaks: list[list[int]], cands: dict[str, int]):
    rows = []
    for name, a in cands.items():
        dec = same = inc = 0
        max_inc_run = 0
        double_inc = 0
        ratios = []  # streak_len / I(start) where I(start) > 0
        for st in streaks:
            vals = [v2(abs(m - a)) if m != a else 60 for m in st]
            run = 0
            for x, y in zip(vals, vals[1:]):
                if y < x:
                    dec += 1
                    run = 0
                elif y == x:
                    same += 1
                    run = 0
                else:
                    inc += 1
                    run += 1
                    if run >= 2:
                        double_inc += 1
                    max_inc_run = max(max_inc_run, run)
            if vals[0] > 0:
                ratios.append(len(st) / vals[0])
        tot = dec + same + inc
        rows.append({
            "cand": name,
            "P_dec": dec / tot if tot else 0.0,
            "P_same": same / tot if tot else 0.0,
            "P_inc": inc / tot if tot else 0.0,
            "max_inc_run": max_inc_run,
            "double_inc": double_inc,
            "max_len/I0": max(ratios) if ratios else float("nan"),
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=1_000_000)
    ap.add_argument("--min-streak", type=int, default=6)
    args = ap.parse_args()

    sanity_checks()
    streaks = collect_streaks(args.max_n, args.min_streak)
    lens = sorted(len(s) for s in streaks)
    print(f"streaks >= {args.min_streak}: {len(streaks)}  "
          f"(max len {lens[-1] if lens else 0}, median {lens[len(lens)//2] if lens else 0})")

    rows = evaluate(streaks, build_candidates())
    rows.sort(key=lambda r: (r["max_inc_run"], -r["P_dec"]))
    hdr = f"{'candidate':<16}{'P_dec':>8}{'P_same':>8}{'P_inc':>8}{'maxIncRun':>11}{'dblInc':>8}{'max L/I0':>10}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['cand']:<16}{r['P_dec']:>8.3f}{r['P_same']:>8.3f}{r['P_inc']:>8.3f}"
              f"{r['max_inc_run']:>11d}{r['double_inc']:>8d}{r['max_len/I0']:>10.2f}")


if __name__ == "__main__":
    main()
