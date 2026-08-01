"""Phase B of the three-bit countdown search: the minimal-avoider function A(n).

A(n) = min{ m = 1 mod 4, m > 1 : the Syracuse orbit of m survives n Set_3
encounters (counting m itself) with every depth in {2,3}, i.e. no strong drop
v2(3m+1) >= 4 before the n-th encounter }.

A depth-3 countdown theorem is exactly a lower bound A(n) >= gamma^n: it would
give avoidance_time(m) <= log_gamma(m) pointwise. The class of m = 1 (trivial
cycle shadow, all-weak) survives ~n encounters spending ~2 bits/encounter, so
A(n) <= c*4^n. This script computes A(n) exactly up to a sieve bound and
inspects the minimizers: binary expansion, v2(m -+ 1), the streak's depth word,
and which 2-adic rational the minimizer is a truncation of.

Sieve: numpy uint64 batches with early exit at the first strong encounter;
values exceeding 2^59 spill to exact Python ints. m = 1 is excluded (its orbit
is the trivial cycle and never meets a strong drop).
"""

from __future__ import annotations

import argparse
from fractions import Fraction

import numpy as np


CAP = np.uint64(1) << np.uint64(59)


def encounters_until_strong_py(m: int, max_enc: int = 10_000) -> int:
    """Exact count of Set_3 encounters (depth in {2,3}) before the first
    strong one, counting from m's first encounter. Pure Python."""
    n = 0
    v = m
    while n < max_enc:
        if v % 4 == 3:
            v = (3 * v + 1) // 2
            continue
        t = 3 * v + 1
        d = (t & -t).bit_length() - 1
        if d >= 4:
            return n
        n += 1
        v = t >> d
        assert v != 1 or m == 1, f"orbit of {m} reached 1 while avoiding"
    return n


def depth_word(m: int):
    """(depth, growth-phase-length) word of m's avoidance streak."""
    word = []
    v = m
    grow = 0
    while True:
        if v % 4 == 3:
            v = (3 * v + 1) // 2
            grow += 1
            continue
        t = 3 * v + 1
        d = (t & -t).bit_length() - 1
        if d >= 4:
            return word
        word.append((d, grow))
        grow = 0
        v = t >> d


def sieve_chunk(ms: np.ndarray) -> np.ndarray:
    """Encounter counts until first strong drop for an array of m = 1 mod 4."""
    v = ms.astype(np.uint64)
    enc = np.zeros(len(ms), dtype=np.int64)
    active = np.ones(len(ms), dtype=bool)
    while active.any():
        idx = np.nonzero(active)[0]
        w = v[idx]
        # spill values near overflow to exact Python
        big = w >= CAP
        if big.any():
            for j in idx[big]:
                enc[j] = encounters_until_strong_py(int(ms[j]))
            active[idx[big]] = False
            idx = np.nonzero(active)[0]
            if len(idx) == 0:
                break
            w = v[idx]
        t = 3 * w + np.uint64(1)
        d = np.uint64(np.log2((t & (~t + np.uint64(1))).astype(np.float64)).astype(np.uint64))
        is_enc = (w & np.uint64(3)) == np.uint64(1)
        strong = is_enc & (d >= np.uint64(4))
        enc[idx[is_enc & ~strong]] += 1
        active[idx[strong]] = False
        keep = ~strong
        v[idx[keep]] = t[keep] >> d[keep]
    return enc


def match_rational(m: int, max_den: int = 99) -> tuple[Fraction, int]:
    """Best 2-adic rational match: the odd-denominator rational p/q (small |p|,q)
    whose 2-adic expansion agrees with m in the most low bits."""
    best, best_bits = None, -1
    bits = m.bit_length() + 2
    mod = 1 << bits
    for q in range(1, max_den + 1, 2):
        for p in range(-max_den, max_den + 1):
            if p == 0 or Fraction(p, q).denominator != q:
                continue
            r = (p * pow(q, -1, mod)) % mod
            agree = ((m - r) & (mod - 1))
            k = bits if agree == 0 else (agree & -agree).bit_length() - 1
            if k > best_bits:
                best_bits, best = k, Fraction(p, q)
    return best, best_bits


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-m", type=int, default=100_000_000)
    ap.add_argument("--chunk", type=int, default=2_000_000)
    args = ap.parse_args()

    # cross-check numpy sieve against pure Python on a small range
    small = np.arange(5, 20001, 4, dtype=np.uint64)
    got = sieve_chunk(small)
    for m, e in zip(small[:2000], got[:2000]):
        assert e == encounters_until_strong_py(int(m)), int(m)
    print("cross-check passed (numpy sieve == exact python, m <= 8001)")

    best: dict[int, int] = {}  # n -> min m with enc >= n
    for lo in range(5, args.max_m, args.chunk * 4):
        ms = np.arange(lo, min(lo + args.chunk * 4, args.max_m), 4, dtype=np.uint64)
        enc = sieve_chunk(ms)
        for n in range(1, int(enc.max()) + 1):
            mask = enc >= n
            if mask.any() and n not in best:
                best[n] = int(ms[mask].min())
    print(f"sieved m = 1 mod 4 up to {args.max_m:,}")

    print(f"\n{'n':>3} {'A(n)':>14} {'ratio':>7} {'v2(m-1)':>8} {'v2(m+1)':>8}  "
          f"{'2-adic match':>14} {'binary (LSB right)':<34} depth word (d,grow)")
    prev = None
    for n in sorted(best):
        m = best[n]
        r, k = match_rational(m)
        ratio = f"{m/prev:7.2f}" if prev else "      -"
        wd = depth_word(m)
        wd_s = ".".join(str(d) if g == 0 else f"{d}g{g}" for d, g in wd[:24])
        print(f"{n:>3} {m:>14} {ratio} {(m-1)&-(m-1) and ((m-1)&-(m-1)).bit_length()-1:>8} "
              f"{((m+1)&-(m+1)).bit_length()-1:>8}  {str(r):>10}@{k:<3} {bin(m)[2:]:<34} {wd_s}")
        prev = m


if __name__ == "__main__":
    main()
