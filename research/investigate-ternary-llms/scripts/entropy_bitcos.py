"""Information theory that the BITCOS paper (arXiv:2609.16338) leaves implicit.

Ternary source with P(0) = z, P(+1) = P(-1) = (1-z)/2.

    H(z) = h(z) + (1-z)          [h = binary entropy, in bits]
    BITCOS rate B(z) = 2 - z     [1 presence bit + 1 sign bit per nonzero]
    overhead  B(z) - H(z) = 1 - h(z)

Run:  .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/entropy_bitcos.py
"""
from __future__ import annotations

import heapq
import itertools
import math

LOG2_3 = math.log2(3.0)


def h(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def H(z: float) -> float:
    """Entropy of the ternary source in bits/weight."""
    return h(z) + (1 - z)


def bitcos(z: float) -> float:
    return 2.0 - z


def huffman_cost(probs) -> float:
    """Expected codeword length of a Huffman code for the given distribution."""
    heap = [(p, i, 0) for i, p in enumerate(probs) if p > 0]
    heapq.heapify(heap)
    if len(heap) == 1:
        return 1.0
    cost = 0.0
    while len(heap) > 1:
        p1, _, _ = heapq.heappop(heap)
        p2, _, _ = heapq.heappop(heap)
        cost += p1 + p2  # each merge adds one bit to every symbol below it
        heapq.heappush(heap, (p1 + p2, -1, 0))
    return cost


def block_huffman_rate(z: float, m: int) -> float:
    """Bits/weight of a Huffman code over blocks of m i.i.d. trits."""
    p = (z, (1 - z) / 2, (1 - z) / 2)
    probs = [math.prod(t) for t in itertools.product(p, repeat=m)]
    return huffman_cost(probs) / m


MODELS = [  # (name, zero density %) -- Table I of arXiv:2609.16338v1
    ("BitNet b1.58 2B4T", 42.19), ("Bonsai 1.7B", 39.89), ("Bonsai 4B", 37.71),
    ("Bonsai 8B", 38.25), ("Bonsai 27B", 29.66), ("CAT-Q Qwen3-1.7B", 51.48),
    ("CAT-Q Qwen3-8B", 46.70), ("CAT-Q Qwen3-30B-A3B", 32.88),
    ("CAT-Q Qwen3-32B", 47.11), ("CAT-Q Qwen3-235B-A22B", 34.07),
    ("ParetoQ 125M", 41.07), ("ParetoQ 350M", 41.58), ("ParetoQ 600M", 43.27),
    ("ParetoQ 1B", 44.18), ("ParetoQ 1.5B", 47.10), ("TriLM 99M", 40.97),
    ("TriLM 190M", 40.67), ("TriLM 390M", 40.79), ("TriLM 560M", 40.73),
    ("TriLM 830M", 40.54), ("TriLM 1.1B", 40.39), ("TriLM 1.5B", 40.21),
    ("TriLM 2.4B", 39.70), ("TriLM 3.9B", 38.70), ("Maple 20B-A1B", 40.67),
    ("BitCPM-CANN 0.5B", 37.67), ("BitCPM-CANN 1B", 38.39),
    ("BitCPM-CANN 3B", 38.06), ("BitCPM-CANN 8B", 39.30),
]


def main() -> None:
    print(f"log2(3)           = {LOG2_3:.6f}")
    print(f"H(1/3)            = {H(1/3):.6f}   (= log2 3 exactly)")
    print(f"2 - log2(3)       = {2 - LOG2_3:.6f}   (z where BITCOS ties log2 3)")
    print(f"BITCOS vs 1.625   : ties at z = {2 - 1.625:.6f} = 3/8")
    print(f"max_z H(z)        = {H(1/3):.6f} < 1.625: the deployed rate exceeds")
    print("                    the entropy bound for EVERY possible zero density.")
    print()

    hdr = f"{'model':24s} {'z':>7s} {'H(z)':>8s} {'BITCOS':>8s} {'gap=1-h(z)':>11s} {'gap%':>6s}"
    print(hdr)
    print("-" * len(hdr))
    zs = []
    for name, pct in MODELS:
        z = pct / 100
        zs.append(z)
        g = bitcos(z) - H(z)
        print(f"{name:24s} {z:7.4f} {H(z):8.4f} {bitcos(z):8.4f} {g:11.4f} "
              f"{100 * g / bitcos(z):5.1f}%")
    print("-" * len(hdr))
    zmin, zmax, zmean = min(zs), max(zs), sum(zs) / len(zs)
    for tag, z in (("min z", zmin), ("mean z", zmean), ("max z", zmax)):
        print(f"{tag:24s} {z:7.4f} {H(z):8.4f} {bitcos(z):8.4f} "
              f"{bitcos(z) - H(z):11.4f}")
    print()

    print("Block-Huffman rate (bits/weight) vs BITCOS and vs the entropy H(z):")
    print(f"{'z':>6s} {'H(z)':>8s} " + " ".join(f"{'m=' + str(m):>8s}" for m in
                                                (1, 2, 3, 4, 5, 6, 8)) +
          f" {'BITCOS':>8s}")
    for z in (0.2966, 1 / 3, 0.375, 0.4150, 0.4219, 0.4740, 0.5, 0.5148):
        row = [f"{z:6.4f}", f"{H(z):8.4f}"]
        for m in (1, 2, 3, 4, 5, 6, 8):
            row.append(f"{block_huffman_rate(z, m):8.4f}")
        row.append(f"{bitcos(z):8.4f}")
        print(" ".join(row))
    print()
    print("Check: single-symbol Huffman equals 2-z for z >= 1/3, and (3+z)/2 below:")
    for z in (0.20, 0.30, 1 / 3, 0.40, 0.50):
        print(f"  z={z:6.4f}  huffman={block_huffman_rate(z, 1):.6f}  "
              f"2-z={2 - z:.6f}  (3+z)/2={(3 + z) / 2:.6f}")
    print()
    n_weights = 2e9
    for z in (0.4219, 0.5148):
        save = (bitcos(z) - H(z)) * n_weights / 8 / 1e6
        print(f"2e9 weights at z={z:.4f}: arithmetic coding would save "
              f"{save:.0f} MB over BITCOS "
              f"({bitcos(z) * n_weights / 8 / 1e6:.0f} MB -> "
              f"{H(z) * n_weights / 8 / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
