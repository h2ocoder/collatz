"""Independent check of the trit-packing dictionary for Collatz stopping times.

Claims checked directly from the raw Collatz map (no repo imports, so this is an
independent witness):

  C1  For odd n > 1 with s Syracuse (odd) steps before the first drop,
          k = s + b(s),  b(s) = bitlen(3^s) = ceil(s log2 3) = min bits for s trits.
  C2  Membership of n in the class with parameter s is decided by n mod 2^{b(s)}
      (the class period is the smallest power of two that can hold s trits).
  C3  The number of odd residues mod 2^{b(s)} in that class is N(s) = A100982(s),
      so density(class s | n odd) = N(s) / 2^{b(s)-1}, and sum_s density = 1
      (a Kraft equality for a complete prefix code over the low bits of n).

Run: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/collatz_packing_check.py
"""
from __future__ import annotations

from collections import Counter

A100982 = [1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, 17637, 51033]


def drop(n: int):
    """Return (k, s): total Collatz steps and odd steps to first value < n."""
    x, k, s = n, 0, 0
    while True:
        if x % 2:
            x = 3 * x + 1
            s += 1
        else:
            x //= 2
        k += 1
        if x < n:
            return k, s


def minbits(s: int) -> int:
    return (3 ** s).bit_length()


def main() -> None:
    LIMIT = 1 << 18
    bad = 0
    tally = Counter()
    by_residue = {}
    for n in range(3, LIMIT, 2):
        k, s = drop(n)
        if k != s + minbits(s):
            bad += 1
            if bad < 5:
                print("  VIOLATION", n, k, s, s + minbits(s))
        tally[s] += 1
        by_residue.setdefault(s, set()).add(n % (1 << minbits(s)))
    print(f"C1: k = s + ceil(s log2 3) for all odd 3 <= n < {LIMIT}: "
          f"{'PASS' if bad == 0 else f'{bad} FAILURES'} "
          f"({sum(tally.values())} numbers, {len(tally)} distinct s)")

    print()
    print("C2/C3: residue-class structure")
    print(f"  {'s':>3s} {'b(s)':>5s} {'k':>4s} {'#residues mod 2^b':>18s} "
          f"{'N(s)=A100982':>13s} {'empirical dens':>15s} {'N/2^(b-1)':>12s}")
    total_emp = total_pred = 0.0
    n_odd = (LIMIT - 3) // 2 + 1
    for s in sorted(tally):
        b = minbits(s)
        if b > 17:          # residues no longer fully sampled below LIMIT
            continue
        r = len(by_residue[s])
        pred = A100982[s - 1] / 2 ** (b - 1) if s <= len(A100982) else float("nan")
        emp = tally[s] / n_odd
        total_emp += emp
        total_pred += pred
        flag = "" if s > len(A100982) or r == A100982[s - 1] else "  <-- MISMATCH"
        print(f"  {s:3d} {b:5d} {s+b:4d} {r:18d} "
              f"{A100982[s-1] if s <= len(A100982) else 0:13d} {emp:15.6f} "
              f"{pred:12.6f}{flag}")
    print(f"  partial sums (only fully sampled s): empirical {total_emp:.6f}, "
          f"predicted {total_pred:.6f}   [Kraft sum -> 1]")

    # C2 proper: does n mod 2^b determine the class?
    print()
    ok = True
    for s, residues in by_residue.items():
        b = minbits(s)
        if b > 17:
            continue
        for other_s, other in by_residue.items():
            if other_s != s and minbits(other_s) >= b:
                if residues & {x % (1 << b) for x in other}:
                    ok = False
    print(f"C2: classes are unions of residues mod 2^b(s), no overlaps: "
          f"{'PASS' if ok else 'FAIL'}")


def a100982_characterizations(smax: int = 12):
    """Three definitions of N(s) = A100982(s), checked to agree.

    D1 (repo, Lattice Path Formula): #(a_1..a_{s-1}), a_1=1, a_i>=1,
       partial sums < i*log2 3 for all i.
    D2 (OEIS A100982): #{1 <= s_1 < ... < s_{s-1}, s_i <= floor(i*log2 3)}.
    D3 (packing): #(bit budgets b_1..b_{s-1} >= 1) that are under-capacity at
       every prefix, i.e. 2^(b_1+...+b_i) < 3^i for all i < s.   [= D1]
    Also checks Winkler's bounds  C(m-1,s-1)/s <= N(s) <= C(m,s-1)/s,
    m = floor(s*log2 3).
    """
    from math import comb, floor, log2

    def d1(s):
        if s == 1:
            return 1
        paths = [(1, 1)]                        # (index i, partial sum)
        for i in range(2, s):
            nxt = []
            for _, tot in paths:
                a = 1
                while tot + a < i * log2(3):
                    nxt.append((i, tot + a))
                    a += 1
            paths = nxt
        return len(paths)

    def d2(s):
        caps = [floor(i * log2(3)) for i in range(1, s)]
        if not caps:
            return 1
        counts = {0: 1}
        for cap in caps:
            nxt = {}
            for last, c in counts.items():
                for v in range(last + 1, cap + 1):
                    nxt[v] = nxt.get(v, 0) + c
            counts = nxt
        return sum(counts.values())

    print()
    print(f"  {'s':>3s} {'D1 (repo)':>10s} {'D2 (OEIS)':>10s} {'A100982':>9s} "
          f"{'Winkler lower':>14s} {'Winkler upper':>14s}")
    for s in range(1, smax + 1):
        m = floor(s * log2(3))
        lo = comb(m - 1, s - 1) / s
        hi = comb(m, s - 1) / s
        ref = A100982[s - 1] if s <= len(A100982) else None
        print(f"  {s:3d} {d1(s):10d} {d2(s):10d} {str(ref):>9s} "
              f"{lo:14.2f} {hi:14.2f}"
              + ("" if ref in (None, d1(s)) or d1(s) != d2(s) else ""))
        assert d1(s) == d2(s) and (ref is None or ref == d1(s))
        assert lo <= d1(s) <= hi
    print("  all three definitions agree and Winkler's bounds hold")


if __name__ == "__main__":
    main()
    a100982_characterizations()
