"""Audit checks: alpha-sequence page numbers, A100982 parity statistics
(sturmian pages), rational cutting sequences, 5x+1 non-droppers."""
from __future__ import annotations

import math

import numpy as np


def alpha_seq(n: int) -> list[int]:
    out = []
    while n > 1:
        if n & 1:
            m = 3 * n + 1
            a = (m & -m).bit_length() - 1
            out.append(a)
            n = m >> a
        else:
            n >>= 1
    return out


def quality(n: int) -> float:
    a = alpha_seq(n)
    rad = math.prod(set(a))
    return math.log2(n) / math.log2(rad) if rad > 1 else float("inf")


def main() -> None:
    print("=== 1. alpha-sequence page ===")
    for n in (3, 7, 27, 5461, 7253):
        a = alpha_seq(n)
        print(f"  n={n}: alphas={a if len(a) < 12 else str(a[:6]) + '...'} odd steps={len(a)} "
              f"distinct={sorted(set(a))} radical={math.prod(set(a))} quality={quality(n):.3f}")
    seq, x = [27], 27
    while x != 1:
        x = 3 * x + 1 if x & 1 else x >> 1
        seq.append(x)
    print(f"  27: steps={len(seq)-1}, max={max(seq)}")
    best = sorted(((quality(n), n) for n in range(3, 10000, 2)), reverse=True)[:6]
    print("  top qualities among odd n < 10000:", [(n, round(q, 3)) for q, n in best])
    print("  quality of (4^k-1)/3, k=2..40 step 6:",
          [(k, round(quality((4 ** k - 1) // 3), 2)) for k in range(2, 41, 6)])

    print("\n=== 2. parity of A100982 (P_o mod 2), o = 1..20000 ===")
    O = 20000
    out = np.zeros(O, dtype=np.uint8)
    out[0] = 1
    f = np.array([1], dtype=np.uint8)  # f[S] = N(j,S) mod 2, j = 0 : S = 0
    Bprev = 0
    pow3 = 1
    for j in range(1, O):
        pow3 *= 3
        Bj = pow3.bit_length() - 1
        cum = np.zeros(len(f) + 1, dtype=np.uint8)
        np.bitwise_xor.accumulate(f, out=cum[1:])
        newf = np.zeros(Bj + 1, dtype=np.uint8)
        lo = j - 1
        if lo <= Bprev:
            S = np.arange(j, Bj + 1)
            hi = np.minimum(Bprev, S - 1)
            ok = hi >= lo
            newf[S[ok]] = cum[hi[ok] + 1] ^ cum[lo]
        out[j] = np.bitwise_xor.reduce(newf)
        f = newf
        Bprev = Bj
    print("  first 13 parities:", out[:13].tolist(), " (A100982 = 1,1,2,3,7,12,30,85,173,476,961,2652,8045)")
    dens = out.mean()
    se = math.sqrt(0.25 / O)
    print(f"  share of 1s = {dens:.5f}; distance from 1/2 = {(0.5-dens)/se:.1f} standard errors")
    s = "".join(map(str, out.tolist()))
    for n in (5, 8, 11, 12, 14):
        blocks = {s[i:i + n] for i in range(len(s) - n + 1)}
        print(f"  distinct blocks of length {n}: {len(blocks)} of {2**n}")

    print("\n=== 3. rational cutting sequence vs log2 3 word ===")
    beta = math.log2(3)
    for p, q in ((3, 2), (8, 5), (19, 12), (84, 53)):
        j = 1
        while (j * p) // q == (3 ** j).bit_length() - 1:
            j += 1
        w = [((i * p) // q) - (((i - 1) * p) // q) for i in range(1, 4 * q + 1)]
        per = all(w[i] == w[i + q] for i in range(len(w) - q))
        print(f"  {p}/{q}: floor(j p/q) = floor(j log2 3) for j < {j}; increments purely periodic with period {q}: {per}")

    print("\n=== 4. 5x+1: integers below 2^16 that do not drop within 2000 steps ===")
    cyc = set()
    for start in (1, 13, 17):
        x = start
        while True:
            cyc.add(x)
            x = 5 * x + 1 if x & 1 else x >> 1
            if x == start:
                break
    nd = 0
    nd_cyc = 0
    for n in range(2, 1 << 16):
        x = n
        ok = False
        for _ in range(2000):
            x = 5 * x + 1 if x & 1 else x >> 1
            if x < n:
                ok = True
                break
        if not ok:
            nd += 1
            nd_cyc += n in cyc
    print(f"  non-droppers: {nd} of {(1<<16)-2} = {nd/((1<<16)-2):.4f}; of these on a known cycle: {nd_cyc}")
    print(f"  known cycle elements in total: {len(cyc)}")


if __name__ == "__main__":
    main()
