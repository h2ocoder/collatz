"""SCRUM-30 E14: exhaustive search for Banerji's backward conjecture (the dual of (Q)).

Backward Syracuse iteration restricted to exponents <= 2 is deterministic on odd n:
    b(n) = (2n - 1)/3  if n = 2 mod 3      (exponent 1)
    b(n) = (4n - 1)/3  if n = 1 mod 3      (exponent 2)
    undefined          if n = 0 mod 3
Banerji (1996) conjectured every odd n reaches a multiple of 3. n = 1 is fixed
(b(1) = 1), so the statement is for n > 1.

Survivors of t steps are 2^t of the 3^t odd residues mod 2*3^t (each step reads one
base-3 digit and one of the three lifts dies). Walk that tree to depth t and finish
each leaf directly: exhaustive for odd n < 2*3^t at cost O(2^t).

Run:  python -X utf8 scripts/banerji_backward_search.py [t]
"""

import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "investigate-pinball-analogy" / "results" / "banerji_backward_search.json"


def survival(n: int) -> int:
    steps = 0
    while n % 3:
        n = (2 * n - 1) // 3 if n % 3 == 2 else (4 * n - 1) // 3
        steps += 1
        if n == 1:
            return -1
    return steps


def search(depth: int):
    # node: (r, x, mult, level): r odd, r < 2*3^level, x = b^level(r), and
    # b^level(r + 2*3^level*d) = x + mult*d with mult = 2 * 2^(sum of exponents)
    stack = [(1, 1, 2, 0)]                    # level 0: r = 1 mod 2, x = r, lifting by 2 changes x by 2
    leaves, best, records, hist = 0, 0, [], {}
    while stack:
        r, x, mult, level = stack.pop()
        if level == depth:
            leaves += 1
            if r == 1:
                continue
            steps, y = level, x
            while y % 3 and y != 1:
                y = (2 * y - 1) // 3 if y % 3 == 2 else (4 * y - 1) // 3
                steps += 1
            if y == 1:
                records.append((r, -1, 0.0))
                continue
            hist[steps] = hist.get(steps, 0) + 1
            if steps > best:
                best = steps
                records.append((r, steps, round(steps / math.log2(r), 3)))
            continue
        modulus = 2 * 3 ** level
        for d in range(3):
            r2, x2 = r + modulus * d, x + mult * d
            if x2 % 3 == 2:
                stack.append((r2, (2 * x2 - 1) // 3, mult * 2, level + 1))
            elif x2 % 3 == 1:
                stack.append((r2, (4 * x2 - 1) // 3, mult * 4, level + 1))
    return leaves, best, records, hist


if __name__ == "__main__":
    depth = int(sys.argv[1]) if len(sys.argv) > 1 else 18
    # validate the tree against brute force on a small range
    small = 8
    brute = sum(1 for n in range(1, 2 * 3 ** small, 2) if survival(n) == -1 or survival(n) >= small)
    assert search(small)[0] == brute == 2 ** small, (search(small)[0], brute)
    start = time.time()
    leaves, best, records, hist = search(depth)
    print(f"odd n < 2*3^{depth} = 2^{math.log2(2 * 3 ** depth):.1f}: {leaves} survive {depth} steps (2^{depth})")
    stuck = [r for r, s, _ in records if s == -1]
    print(f"reach the fixed point 1 from n > 1: {stuck}")
    print(f"longest survival {best}; records (n, steps, steps/log2 n): "
          f"{sorted((t for t in records if t[1] > 0), key=lambda t: -t[1])[:6]}")
    print(f"random-model record ratio: {1 / math.log2(1.5):.3f} * log2 n;  elapsed {time.time() - start:.0f}s")
    tail, run = {}, 0
    for k in sorted(hist, reverse=True):
        run += hist[k]
        tail[k] = run
    rates = [(k, round(tail[k + 1] / tail[k], 4)) for k in range(depth, depth + 12, 2) if tail.get(k + 1) and tail[k] > 3000]
    print(f"P(survive one more step): {rates}   (free-digit model: 2/3 = 0.6667)")
    OUT.write_text(json.dumps({"depth": depth, "leaves": leaves, "longest": best, "records": records,
                               "histogram": sorted(hist.items())}, indent=1))
