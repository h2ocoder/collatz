"""L1: exact N(s) (OEIS A100982) by dynamic programming, Kraft sum, Wagon's constant.

N(s) = number of admissible sequences of order s = number of alpha-prefixes
(a_1, ..., a_{s-1}) with a_1 = 1, a_i >= 1 and every partial sum S_i < i*log2(3).
Equivalently 1 <= S_1 < S_2 < ... < S_{s-1} with S_i <= floor(i*log2 3).
The comparison S < i*log2(3) is done exactly as 2^S < 3^i (no floats).

Densities (among odd n) of the dropping set with s Syracuse steps:
    dens(s) = N(s) / 2^(b(s) - 1),   b(s) = bitlen(3^s) = ceil(s log2 3)
Kraft sum  sum_s dens(s) -> 1  (Terras: almost every n has finite stopping time)
Wagon's constant = sum_s k(s) dens(s),  k(s) = s + b(s)  (mean stopping time of odd n)

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/admissible_dp.py [S_MAX]
Writes results/admissible_dp.json
"""
import json
import sys
import urllib.request
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
RESULTS.mkdir(exist_ok=True)


def cap(i):
    """floor(i*log2 3) computed exactly: largest S with 2^S < 3^i."""
    return (3**i).bit_length() - 1


def admissible_counts(s_max):
    """Return [N(1), ..., N(s_max)] via DP on (number of terms i, partial sum S)."""
    # f[S] = number of admissible (S_1..S_i) ending at S_i = S, for current i
    N = [0] * (s_max + 1)
    N[1] = 1  # empty prefix
    f = {1: 1}  # i = 1: S_1 = a_1 = 1 (cap(1) = 1 so it's admissible)
    N[2] = sum(f.values())
    for i in range(2, s_max):
        c = cap(i)
        # g[S] = sum_{S' < S} f[S'] for S <= c (strictly increasing sums)
        keys = sorted(f)
        g = {}
        run = 0
        ki = 0
        for S in range(2, c + 1):
            while ki < len(keys) and keys[ki] < S:
                run += f[keys[ki]]
                ki += 1
            if run:
                g[S] = run
        f = g
        N[i + 1] = sum(f.values())
    return N


def fetch_bfile():
    url = "https://oeis.org/A100982/b100982.txt"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            txt = r.read().decode()
    except Exception as e:  # offline: skip
        print(f"  (could not fetch b-file: {e})")
        return {}
    out = {}
    for line in txt.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        n, v = line.split()
        out[int(n)] = int(v)
    return out


if __name__ == "__main__":
    S_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    N = admissible_counts(S_MAX)
    print(f"N(s) for s=1..15: {N[1:16]}")

    b = fetch_bfile()
    if b:
        common = [s for s in range(1, S_MAX + 1) if s in b]
        mism = [s for s in common if b[s] != N[s]]
        print(f"OEIS b-file: compared {len(common)} terms (to s={max(common)}), mismatches = {len(mism)} {mism[:5]}")

    kraft = Fraction(0)
    wagon = Fraction(0)
    ebits = Fraction(0)  # E[b(s)] = expected halvings
    es = Fraction(0)
    rows = []
    for s in range(1, S_MAX + 1):
        bs = (3**s).bit_length()
        dens = Fraction(N[s], 2 ** (bs - 1))
        kraft += dens
        wagon += (s + bs) * dens
        ebits += bs * dens
        es += s * dens
        if s in (1, 2, 3, 5, 8, 10, 20, 30, 50, 100, 150, 200, 250, 300):
            rows.append((s, bs, s + bs, N[s], float(dens), float(kraft), float(wagon)))
    print("\n   s   b   k             N(s)        dens        Kraft     Wagon partial")
    for r in rows:
        print(f"{r[0]:4d} {r[1]:3d} {r[2]:3d} {r[3]:16d}  {r[4]:.3e}  {r[5]:.10f}  {r[6]:.10f}")

    tail = 1 - kraft
    print(f"\nKraft sum at s={S_MAX}: {float(kraft):.15f}   (1 - Kraft = {float(tail):.3e})")
    print(f"Wagon partial sum:     {float(wagon):.12f}   target 9.4779555565... (A122790)")
    print(f"E[s] partial = {float(es):.6f}, E[halvings] partial = {float(ebits):.6f}")
    # crude tail estimate: the missing mass 'tail' has k >= k(S_MAX+1); lower bound only
    print(f"Wagon lower bound with tail mass at k(S_MAX+1): {float(wagon + tail * (S_MAX + 1 + (3**(S_MAX+1)).bit_length())):.12f}")

    # fraction of odd n undecided after p low bits
    print("\n p   decided fraction (sum of dens with b(s) <= p)   undecided")
    dec = Fraction(0)
    by_b = {}
    for s in range(1, S_MAX + 1):
        by_b.setdefault((3**s).bit_length(), []).append(s)
    und = {}
    for p in range(1, 41):
        for s in by_b.get(p, []):
            dec += Fraction(N[s], 2 ** (p - 1))
        und[p] = 1 - dec
        if p in (2, 4, 5, 7, 8, 10, 12, 16, 20, 24, 30, 40):
            print(f"{p:2d}   {float(dec):.8f}   {float(1-dec):.3e}")

    json.dump(
        {
            "S_MAX": S_MAX,
            "N": [str(x) for x in N[1:]],
            "kraft": str(kraft),
            "kraft_float": float(kraft),
            "wagon_partial": str(wagon),
            "wagon_float": float(wagon),
            "undecided_by_bits": {p: float(v) for p, v in und.items()},
            "bfile_mismatches": mism if b else None,
        },
        open(RESULTS / "admissible_dp.json", "w"),
        indent=1,
    )
    print(f"\nwrote {RESULTS / 'admissible_dp.json'}")
