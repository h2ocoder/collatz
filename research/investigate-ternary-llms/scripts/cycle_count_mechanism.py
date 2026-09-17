"""Why other 3x+k have many cycles: the divisibility mechanism, exactly and heuristically.

Exact: a necklace (cyclic word) v of length b with s ones is a cycle of 3x+k iff
    (2^b - 3^s) | k * r(v)      (then x_min = k r(v) / (2^b - 3^s), and it is automatically the
                                 min-rotation element; all rotations give the other elements).
For k | 2^b - 3^s with cofactor c = (2^b - 3^s)/k this is  c | r(v).  E.g. k = 499, (b,s) = (16,10):
c = 13, so the (16,10)-cycles of 3x+499 are exactly the Set_16-shaped necklaces with 13 | r(v).

Heuristic: E[#cycles(k)] ~ sum over shapes (b,s) of  #necklaces(b,s) * gcd(k, 2^b-3^s) / (2^b-3^s),
treating r(v) mod (2^b-3^s)/gcd as uniform.  Compared with the census counts for k <= 600.

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/cycle_count_mechanism.py
"""
import json
import math
from collections import defaultdict
from itertools import combinations
from math import comb, gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"


def r_of_bits(bits, b):
    r, pow3 = 0, 1
    for i in range(b - 1, -1, -1):
        if bits >> i & 1:
            r += pow3 << i
            pow3 *= 3
    return r


def necklaces(b, s):
    """All necklaces (min rotation representative) of length b with s ones, as bitmasks."""
    seen = set()
    for ones in combinations(range(b), s):
        m = sum(1 << i for i in ones)
        rots = [((m << t) | (m >> (b - t))) & ((1 << b) - 1) for t in range(b)]
        seen.add(min(rots))
    return seen


def exact_cycles_of_shape(k, b, s):
    d = (1 << b) - 3**s
    return sum(1 for m in necklaces(b, s) if (k * r_of_bits(m, b)) % d == 0)


if __name__ == "__main__":
    census = json.load(open(RESULTS / "cycles_3xk_census.json"))["census"]["per_k_counts"]
    print("Exact mechanism on cycle-rich k:")
    for k, (b, s) in ((499, (16, 10)), (233, (13, 8)), (269, (9, 5)), (295, (10, 6)), (517, (14, 8)), (13, (8, 5)), (5, (5, 3)), (7, (4, 2))):
        d = (1 << b) - 3**s
        n_neck = len(necklaces(b, s))
        n_cyc = exact_cycles_of_shape(k, b, s)
        print(f"  k={k:4d}, shape (b,s)=({b},{s}), 2^b-3^s={d} = {d//k if d%k==0 else 'n/a'}*k: necklaces {n_neck}, "
              f"of which cycles of 3x+{k}: {n_cyc}  (census total for k: {census.get(str(k))})")

    # heuristic count over shapes with b <= 44
    print("\nHeuristic E[#cycles(k)] = sum_(b,s) necklaces(b,s) * gcd(k, 2^b-3^s) / (2^b-3^s), b <= 44, vs census:")
    shapes = []
    for s in range(1, 30):
        for b in range((3**s).bit_length(), 45):
            d = (1 << b) - 3**s
            # number of necklaces ~ C(b,s)/b (exact for primitive words; fine as a heuristic)
            shapes.append((b, s, d, comb(b, s) / b))
    pred = {}
    for k in range(1, 601, 2):
        if k % 3 == 0:
            continue
        pred[k] = sum(nn * gcd(k, d) / d for b, s, d, nn in shapes)
    ks = sorted(pred)
    obs = [census.get(str(k), 0) for k in ks]
    pr = [pred[k] for k in ks]
    mo, mp_ = sum(obs) / len(obs), sum(pr) / len(pr)
    cov = sum((o - mo) * (p - mp_) for o, p in zip(obs, pr))
    corr = cov / math.sqrt(sum((o - mo) ** 2 for o in obs) * sum((p - mp_) ** 2 for p in pr))
    print(f"  correlation(observed, predicted) over {len(ks)} values of k: {corr:.3f}")
    top = sorted(ks, key=lambda k: -pred[k])[:10]
    print("  top predicted k:", [(k, round(pred[k], 1), census.get(str(k), 0)) for k in top])
    print("  k=1 predicted:", round(pred[1], 3), "observed:", census.get("1"))
    json.dump(dict(corr=corr, predicted={k: pred[k] for k in ks}), open(RESULTS / "cycle_count_mechanism.json", "w"), indent=1)
