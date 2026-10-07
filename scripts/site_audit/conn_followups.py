"""Follow-up checks for the connections audit.

A. L-probe: exactness over whole periods (second and third period; shifted windows).
B. AlphaPositionChart: the mean positions exactly as the component computes them (20 bins).
C. Transfer matrix: which moduli 6*2^j carry extra cycles; first few bad multiples of 6.
D. 5x+1 / 7x+1 at the widget's default modulus 24: full list of non-zero eigenvalues.
"""
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from conn_sturmian_probe import A_P, D, chi, drop, gap, k_of  # noqa: E402
from conn_transfer_cycles import cycles, matrix  # noqa: E402
from collatz.lfunctions.eisenstein import EisensteinInt  # noqa: E402


def D_window(k, lo, hi):
    s = 0j
    cnt = 0
    for n in range(lo | 1, hi + 1, 2):
        if n < 3:
            continue
        t, d = drop(n)
        if t == k:
            s += chi.evaluate(EisensteinInt(n, d))
            cnt += 1
    return s, cnt


def v2(n):
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c


def syr(m):
    seq = [m]
    while m != 1:
        m = 3 * m + 1
        while m % 2 == 0:
            m //= 2
        seq.append(m)
    return seq


if __name__ == "__main__":
    print("A. whole periods")
    for o in range(1, 7):
        k = k_of(o)
        A, P = A_P(o)
        eps = 1 if gap(o) == 3 else -1
        per = 3 * 2 ** k
        for (lo, hi) in ((3, per), (per + 1, 2 * per), (2 * per + 1, 3 * per), (5, per + 4), (1001, 1000 + per)):
            d, cnt = D_window(k, lo, hi)
            pred = 1j * eps * A / P * cnt / math.sqrt(3)
            print(f"   o={o} k={k} window [{lo}, {hi}]: N_k={cnt}  D={d.real:+.4f}{d.imag:+.4f}i  "
                  f"pred={pred.imag:+.4f}i  exact={abs(d - pred) < 1e-6}")

    print("B. AlphaPositionChart replication (20 bins, odd n 3..5999, s >= 5)")
    BINS = 20
    hist = {g: [0] * BINS for g in (1, 2, 3, 4)}
    for n in range(3, 6000, 2):
        orb = syr(n)
        s = len(orb) - 1
        if s < 5:
            continue
        for i in range(s):
            a = min(v2(3 * orb[i] + 1), 4)
            b = min(int(i / (s - 1) * BINS), BINS - 1)
            hist[a][b] += 1
    for g in (1, 2, 3, 4):
        tot = sum(hist[g])
        mean = sum((b + 0.5) / BINS * c for b, c in enumerate(hist[g])) / tot
        print(f"   alpha group {g}{'+' if g == 4 else ''}: marker (binned mean) at {mean:.3f};  "
              f"share of this group's steps in the last bin: {hist[g][-1] / tot:.3f}")

    print("C. moduli 6*2^j")
    for j in range(0, 16):
        M = 6 * 2 ** j
        cs = [c for c, _ in cycles(M, 3) if c not in ((0,), (1, 4, 2))]
        print(f"   M=6*2^{j}={M}: extra cycles: {len(cs)}" + (f" lengths {[len(c) for c in cs]}" if cs else ""))

    print("D. non-zero eigenvalues at M = 24 for n = 3, 5, 7 (numpy)")
    for n in (3, 5, 7):
        ev = [e for e in np.linalg.eigvals(matrix(24, n)) if abs(e) > 1e-3]
        ev.sort(key=lambda z: -abs(z))
        print(f"   n={n}: {len(ev)} non-zero: moduli {sorted({round(abs(e), 4) for e in ev}, reverse=True)}; "
              f"cycles {[(c, str(w)) for c, w in cycles(24, n)]}")
    print("   widget claims for n=5: 6 non-zero, radius", round((4 / 5) ** 0.2, 4),
          "; for n=7: 8 non-zero, radius", round((4 / 7) ** (1 / 7), 4))
