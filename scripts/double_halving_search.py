"""SCRUM-30 E12: exhaustive search for positive integers that avoid two consecutive halvings.

Statement (*): every n > 1 has '00' somewhere in its Terras parity word
(equivalently some Syracuse iterate is 5 mod 8). Implied by Collatz; false for -1.

Instead of scanning all n < 2^B, walk the tree of residues mod 2^j whose first j
steps contain no '00' -- only Fibonacci(j+1) of them -- then finish each leaf by
direct iteration. Exhaustive for all n < 2^B.

Run:  python -X utf8 scripts/double_halving_search.py [B]
"""

import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "investigate-pinball-analogy" / "results" / "double_halving_search.json"


def search(bits: int):
    # node: (r, x, pow3, last_was_halving, depth); x = T^depth(r) exactly, r < 2^depth
    stack = [(1, 2, 3, False, 1)]          # n odd: first step is (3n+1)/2; r=1 -> x=2
    best, records, leaves = 0, [], 0
    histogram = {}
    while stack:
        r, x, pow3, halved, depth = stack.pop()
        if depth == bits:
            leaves += 1
            if r == 1:
                continue
            steps, y, h = depth, x, halved
            while True:
                if y % 2 == 0:
                    if h:
                        break
                    y, h = y // 2, True
                else:
                    y, h = (3 * y + 1) // 2, False
                steps += 1
            histogram[steps] = histogram.get(steps, 0) + 1
            if steps > best:
                best = steps
                records.append((r, steps, round(steps / math.log2(r), 3)))
            continue
        for bit in (0, 1):
            r2 = r + (bit << depth)
            x2 = x + bit * pow3
            if x2 % 2 == 0:
                if not halved:
                    stack.append((r2, x2 // 2, pow3, True, depth + 1))
            else:
                stack.append((r2, (3 * x2 + 1) // 2, pow3 * 3, False, depth + 1))
    return leaves, best, records, histogram


if __name__ == "__main__":
    bits = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    start = time.time()
    leaves, best, records, histogram = search(bits)
    ratio = 1 / math.log2(4 / (1 + 5 ** 0.5))
    print(f"all n < 2^{bits}: {leaves} residues survive {bits} steps (Fibonacci({bits + 1}))")
    print(f"every one of them except n = 1 hits '00'; longest survival {best} steps")
    print(f"top records (n, steps, steps/log2 n): {sorted(records, key=lambda t: -t[1])[:8]}")
    print(f"random-model record ratio: {ratio:.3f};  elapsed {time.time() - start:.0f}s")
    OUT.write_text(json.dumps({"bits": bits, "leaves": leaves, "longest": best, "records": records,
                               "histogram": sorted(histogram.items())}, indent=1))
