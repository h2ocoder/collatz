"""Audit checks for site/explore/sturmian-bridge.md, sturmian-fractals.md and
SturmianBridge.vue: Terras sums for qx+1 and 3x-1, class-size tables, the sign
rule at o = 3, coefficient-stopping-time check on individual integers.
"""
from __future__ import annotations

import math
from collections import defaultdict
from fractions import Fraction


def floor_o_log2_q(o: int, q: int) -> int:
    return (q ** o).bit_length() - 1


def N_q(o_max: int, q: int) -> list[int]:
    """Number of shortcut dropping words with o ones for qx+1 (coefficient def).

    Syracuse form: (a_1..a_o), a_i >= 1, partial sums S_j <= B_j = floor(j log2 q)
    for j < o, S_o = B_o + 1.  N(o) = number of valid prefixes of length o-1.
    """
    out = [1]  # o = 0 : the word E
    cur = {0: 1}  # S_0 = 0
    for o in range(1, o_max + 1):
        out.append(sum(cur.values()))  # last a_o is forced
        B = floor_o_log2_q(o, q)
        nxt: dict[int, int] = defaultdict(int)
        keys = sorted(cur)
        acc, idx = 0, 0
        for S in range(1, B + 1):
            while idx < len(keys) and keys[idx] < S:
                acc += cur[keys[idx]]
                idx += 1
            if acc:
                nxt[S] = acc
        cur = nxt
    return out


def sign_table(o_max: int):
    """c2 - c1 for 3x+1: (#words with last alpha odd) - (#words with last alpha even)."""
    res = {}
    cur = {0: 1}
    for o in range(1, o_max + 1):
        Bo = floor_o_log2_q(o, 3)
        diff = 0
        for S, c in cur.items():
            a_last = Bo + 1 - S
            diff += c if a_last % 2 else -c
        gap = 1 + Bo - floor_o_log2_q(o - 1, 3)
        res[o] = (gap, diff)
        nxt: dict[int, int] = defaultdict(int)
        keys = sorted(cur)
        acc, idx = 0, 0
        for S in range(1, Bo + 1):
            while idx < len(keys) and keys[idx] < S:
                acc += cur[keys[idx]]
                idx += 1
            if acc:
                nxt[S] = acc
        cur = nxt
    return res


def main() -> None:
    print("=== A. Terras sums  sum_o N_q(o) / 2^(B_o+1)  (2-adic measure of 'drops') ===")
    for q, omax in ((3, 3000), (5, 400), (7, 400), (9, 400)):
        N = N_q(omax, q)
        tot = Fraction(0)
        marks = []
        for o in range(0, omax + 1):
            tot += Fraction(N[o], 2 ** (floor_o_log2_q(o, q) + 1))
            if o in (5, 10, 20, 50, 100, 200, 400, 1000, 3000):
                marks.append((o, float(tot)))
        print(f"  q={q}:", ", ".join(f"o<={o}: {v:.6f}" for o, v in marks))
    print("  3x-1: dropping words obey the same coefficient test 3^o < 2^e, so the sum is the q=3 sum (-> 1),")
    print("        although 3x-1 has the cycles {1,2}, {5,14,7,20,10} and the 17-cycle.")

    print("\n=== B. direct check of 3x-1: share of n in [2, 2^20) that drop within 400 steps ===")
    M = 1 << 20
    dropped = 0
    never = []
    for n in range(2, M):
        x = n
        ok = False
        for _ in range(400):
            x = x // 2 if x % 2 == 0 else 3 * x - 1
            if x < n:
                ok = True
                break
        if ok:
            dropped += 1
        elif len(never) < 12:
            never.append(n)
    print(f"  dropped: {dropped}/{M-2} = {dropped/(M-2):.6f}; first non-droppers: {never}")

    print("\n=== C. direct check of 5x+1: share of n in [2, 2^18) that drop within 60 steps ===")
    M = 1 << 18
    dropped = 0
    for n in range(2, M):
        x = n
        for _ in range(60):
            x = x // 2 if x % 2 == 0 else 5 * x + 1
            if x < n:
                dropped += 1
                break
    print(f"  dropped: {dropped}/{M-2} = {dropped/(M-2):.6f}")

    print("\n=== D. class sizes |R_k^(q)| = N_q(o) * 2^o  vs component tables ===")
    comp = {
        5: {1: 1, 4: 2, 7: 8, 10: 40, 14: 224, 17: 1792},
        7: {1: 1, 4: 2, 8: 8, 12: 56, 16: 480},
        9: {1: 1, 5: 2, 9: 12, 13: 96},
    }
    for q, tab in comp.items():
        N = N_q(8, q)
        row = []
        for o in range(0, len(tab)):
            k = o + floor_o_log2_q(o, q) + 1
            row.append((k, N[o] * 2 ** o, tab.get(k)))
        print(f"  q={q}:", row, "OK" if all(a == b for _, a, b in row) else "MISMATCH")
    N3 = N_q(22, 3)
    print("  q=3 correct table (k: |R_k|):")
    print("   ", ", ".join(f"{o + floor_o_log2_q(o,3) + 1}: {N3[o] * 2**o}" for o in range(0, 22)))

    print("\n=== E. sign of c2 - c1 vs gap rule, o = 1..60 ===")
    st = sign_table(60)
    bad = []
    for o, (gap, diff) in st.items():
        pred = 1 if gap == 3 else -1
        sgn = (diff > 0) - (diff < 0)
        if sgn != pred:
            bad.append((o, gap, diff))
    print("  exceptions (o, gap, c2-c1):", bad)
    print("  first values:", [(o, st[o]) for o in range(1, 9)])

    print("\n=== F. coefficient stopping time = stopping time, every n in [2, 10^7] ===")
    # shortcut map; n drops at step L with s odd steps  =>  check L == floor(s log2 3) + 1
    LIM = 10 ** 7
    viol = 0
    maxL = 0
    for n in range(2, LIM + 1):
        if n % 4 != 3:
            # even: L=1,s=0 ; n = 1 mod 4: L=2,s=1 (3n+1)/4 < n for n>1
            continue
        x, L, s = n, 0, 0
        while True:
            if x & 1:
                x = (3 * x + 1) >> 1
                s += 1
            else:
                x >>= 1
            L += 1
            if x < n:
                break
        if L != (3 ** s).bit_length():  # floor(s log2 3) + 1 == bit_length(3^s)
            viol += 1
            print("   VIOLATION", n, L, s)
        if L > maxL:
            maxL = L
    print(f"  n = 2..{LIM}: violations = {viol}; longest shortcut stopping time = {maxL}")

    print("\n=== G. Beatty list and gaps ===")
    ks = [o + floor_o_log2_q(o, 3) + 1 for o in range(0, 14)]
    print("  k_o, o=0..13:", ks)
    print("  gaps:", [ks[i] - ks[i - 1] for i in range(1, len(ks))])
    print("  tau = 2 - log2 3 =", 2 - math.log2(3))


if __name__ == "__main__":
    main()
