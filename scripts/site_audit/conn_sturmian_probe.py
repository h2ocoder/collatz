"""Audit check for site/connections/sturmian-l-probe.md.

Questions:
  1. Is  D^(k_o)(N) = i*sqrt3 * eps_o * A_o * N_k / |R_k|  exact, for which N, and with
     which meaning of |R_k| ?  (The page never defines R_k.)
  2. Is D^(8)(N) = 0 "exactly" for every N ?
  3. Do the table values (per-n size) match, and per which n ?
"""
import math
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from collatz.lfunctions import SexticResidueCharacter  # noqa: E402
from collatz.lfunctions.eisenstein import EisensteinInt  # noqa: E402

chi = SexticResidueCharacter()
LOG23 = math.log2(3)


def B(j):
    return int(math.floor(j * LOG23)) if j else 0


def k_of(o):
    return o + B(o) + 1


def gap(o):
    return k_of(o) - k_of(o - 1)


def drop(n):
    """(dropping time in 3x+1 / x/2 steps, destination) for n > 1."""
    x, t = n, 0
    while True:
        x = 3 * x + 1 if x & 1 else x >> 1
        t += 1
        if x < n:
            return t, x


def paths(o_minus_1):
    """N(o-1, T): number of alpha-prefixes of length o-1 with partial sums <= B_j, ending at T."""
    f = {0: 1}
    for j in range(1, o_minus_1 + 1):
        g = {}
        for T, c in f.items():
            for a in range(1, B(j) - T + 1):
                g[T + a] = g.get(T + a, 0) + c
        f = g
    return f


def A_P(o):
    Nd = paths(o - 1)
    P = sum(Nd.values())
    A = sum((-1) ** (B(o - 1) - T) * c for T, c in Nd.items())
    return A, P


def D(k, N):
    s = 0j
    cnt = 0
    nz = 0
    for n in range(3, N + 1, 2):
        t, d = drop(n)
        if t == k:
            v = chi.evaluate(EisensteinInt(n, d))
            s += v
            cnt += 1
            nz += (v != 0)
    return s, cnt, nz


if __name__ == "__main__":
    print("chi6 table on Z[w]/3, rows i (n mod 3), cols j (dest mod 3):")
    for i in range(3):
        print("   ", [f"{chi.evaluate(EisensteinInt(i, j)):.3f}" for j in range(3)])
    for j in range(3):
        print(f"   column sum j={j}:", f"{sum(chi.evaluate(EisensteinInt(i, j)) for i in range(3)):.4f}")

    print("\n o  k gap  A_o  P_o | full period N=3*2^k: D, N_k, N_nz | predicted i*sqrt3*eps*A*N_k/(3P) | "
          "|D|/N_k  |D|/N_nz  (sqrt3/2)*A/P")
    for o in range(1, 9):
        k = k_of(o)
        A, P = A_P(o)
        eps = 1 if gap(o) == 3 else -1
        N = 3 * 2 ** k
        if N > 3 * 2 ** 21:
            break
        # start from n=3; n=1 is not in any dropping set
        d, cnt, nz = D(k, N)
        pred = 1j * math.sqrt(3) * eps * A * cnt / (3 * P)
        print(f"{o:2d} {k:2d} {gap(o):3d} {A:4d} {P:4d} | D={d.real:+.3f}{d.imag:+.3f}i N_k={cnt} N_nz={nz} | "
              f"pred={pred.imag:+.3f}i | {abs(d) / cnt:.4f} {abs(d) / nz if nz else 0:.4f} "
              f"{math.sqrt(3) / 2 * A / P:.4f} | page formula with |R|=P would give |D|/N_k={math.sqrt(3) * A / P:.4f}")

    print("\nNon-period N: is the formula exact?  (o=3, k=8 should be '0 exactly' per the page)")
    for N in (23, 100, 255, 500, 767, 768, 1000, 1536, 5000, 100000):
        d, cnt, nz = D(8, N)
        print(f"   k=8  N={N:6d}: D={d.real:+.4f}{d.imag:+.4f}i  |D|={abs(d):.4f}  N_k={cnt}")
    for (o, N) in ((1, 10), (1, 25), (1, 1000), (2, 100), (2, 1000), (4, 10000), (5, 100000)):
        k = k_of(o)
        A, P = A_P(o)
        eps = 1 if gap(o) == 3 else -1
        d, cnt, nz = D(k, N)
        pred = 1j * math.sqrt(3) * eps * A * cnt / (3 * P)
        print(f"   o={o} k={k} N={N}: D={d.real:+.4f}{d.imag:+.4f}i  pred={pred.imag:+.4f}i  "
              f"diff={abs(d - pred):.4f}  arg(D)={math.degrees(math.atan2(d.imag, d.real)):+.2f} deg")

    print("\nA_o, P_o and sign rule to o = 40 (exact integers):")
    ok = True
    row = []
    for o in range(1, 41):
        A, P = A_P(o)
        row.append((o, A, P))
        if o == 3:
            ok &= (A == 0)
        else:
            ok &= (A > 0)
        if o >= 4:
            ok &= (0 < A < P)
    print("   ", row[:10])
    print("   A_3 = 0, A_o > 0 otherwise, 0 < A_o < P_o for o >= 4, all o <= 40:", ok)
    print("   P_o:", [p for _, _, p in row[:12]], "(OEIS A100982: 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652)")
