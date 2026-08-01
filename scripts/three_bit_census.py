"""Census of minimal-avoider streaks + the exact tank-refill rules.

Part 1 — step census of A(n) minimizers.  For a streak with a weak drops,
b medium drops, c growth steps and strong root z, the exact telescoping gives
    log2 m = log2 z + (2 - log2 3) a + (3 - log2 3) b - (log2 3 - 1) c + eps
with eps = accumulated log(1 + 1/(3v)) corrections.  The Three-Bit Countdown
conjecture A(n) >= C (4/3)^n is EQUIVALENT (up to constants) to the census
bound   c <= (b + log2 z) / (log2 3 - 1)  ~  1.7095 (b + log2 z).

Part 2 — refill rules.  The medium tank W = v2(5m-1) empties by exactly 3 per
medium drop (ledger).  Under a WEAK drop it refills; algebra predicts, with
V = v2(m-1) at the weak encounter:
    V = 3   -> W' = 1
    V >= 5  -> W' = 2
    V = 4   -> W' >= 3, value set by higher bits of m   (the escape hatch)
Under a MEDIUM drop the weak tank refills via V' = v2(3t-1) - 1, t = (m-1)/4.
This script measures both rules exhaustively.

Part 3 — how much local state determines the NEXT encounter's type.
"""

from __future__ import annotations

import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collatz.core import v2  # noqa: E402

LOG2_3 = math.log2(3)


def streak_census(m: int):
    """(a, b, c, z, n) for m's avoidance streak; z = the strong-encounter value."""
    a = b = c = 0
    v = m
    while True:
        if v % 4 == 3:
            v = (3 * v + 1) // 2
            c += 1
            continue
        t = 3 * v + 1
        d = v2(t)
        if d >= 4:
            return a, b, c, v, a + b
        if d == 2:
            a += 1
        else:
            b += 1
        v = t >> d


def part1(avoiders: list[int]) -> None:
    print("n   A(n)        a   b   c   log2z   eps     c_bound=1.71(b+log2z)  slack")
    for m in avoiders:
        a, b, c, z, n = streak_census(m)
        lz = math.log2(z)
        eps = math.log2(m) - (lz + (2 - LOG2_3) * a + (3 - LOG2_3) * b - (LOG2_3 - 1) * c)
        bound = (b + lz) / (LOG2_3 - 1)
        print(f"{n:<3} {m:<11} {a:<3} {b:<3} {c:<3} {lz:6.2f} {eps:7.3f}   "
              f"{bound:8.2f}              {bound - c:6.2f}")


def part2(limit: int) -> None:
    weak = defaultdict(Counter)    # V -> Counter of W' = v2(5*m2-1)
    med = defaultdict(Counter)     # W -> Counter of V' = v2(m2-1)
    for m in range(9, limit, 4):
        d = v2(3 * m + 1)
        if d == 2:
            V = v2(m - 1)
            m2 = (3 * m + 1) // 4
            weak[V][v2(5 * m2 - 1)] += 1
        elif d == 3:
            W = v2(5 * m - 1)
            m2 = (3 * m + 1) // 8
            med[W][v2(m2 - 1)] += 1
    print("\nWeak-drop refill of medium tank W' = v2(5m2-1), by V = v2(m-1):")
    for V in sorted(weak):
        dist = dict(sorted(weak[V].items()))
        print(f"  V={V:<2}  W' dist: {dist}")
    print("\nMedium-drop refill of weak tank V' = v2(m2-1), by W = v2(5m-1):")
    for W in sorted(med):
        dist = dict(sorted(med[W].items()))
        print(f"  W={W:<2}  V' dist: {dist}")


def part3(limit: int) -> None:
    """Is the next encounter type determined by (V, W) at the current one?"""
    table = defaultdict(Counter)
    for m in range(9, limit, 4):
        d = v2(3 * m + 1)
        if d >= 4:
            continue
        V, W = min(v2(m - 1), 8), min(v2(5 * m - 1), 8)
        v = (3 * m + 1) >> d
        while v % 4 == 3:
            v = (3 * v + 1) // 2
        d2 = v2(3 * v + 1)
        table[(d, V, W)]["weak" if d2 == 2 else "medium" if d2 == 3 else "strong"] += 1
    det = tot = 0
    for k, cnt in table.items():
        s = sum(cnt.values())
        tot += s
        det += max(cnt.values())
    print(f"\nNext-type predictability from (d, V<=8, W<=8): best-guess accuracy "
          f"{det/tot:.4f} over {tot} encounters ({len(table)} states)")
    ent = sum(-c / tot * math.log2(c / sum(cnt.values()))
              for cnt in table.values() for c in cnt.values() if c)
    print(f"conditional entropy H(next type | state) = {ent:.4f} bits (max log2 3 = 1.585)")


if __name__ == "__main__":
    avoiders = [9, 25, 33, 41, 73, 97, 129, 257, 685, 825, 1081, 1441, 1921, 2561,
                6829, 9105, 34041, 90777, 154633, 206177, 340153, 453537, 826785,
                1737849, 1780281, 3397753, 4530337, 6040449, 7322617, 9763489,
                11871913, 15377593, 20503457, 24381193]
    part1(avoiders)
    part2(2_000_000)
    part3(2_000_000)
