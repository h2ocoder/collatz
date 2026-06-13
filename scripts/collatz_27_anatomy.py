"""Why is 27 so long?  It is a 2-adic accident, not a fact about 3^3.

27 takes 111 Collatz steps to reach 1 and climbs to a peak of 9232 -- famously
long for so small a number.  This script dissects why, and answers three
questions:

  * Is there a shortcut to its length?      -> sigma(n) = drop_time(n) + sigma(dest),
                                               the letter-chain recursion (memoised).
  * Can we guess it statistically?          -> sigma is ~ c*log2(n) on average with
                                               ENORMOUS variance; 27 is only a ~2 sigma
                                               outlier among numbers its size.
  * Is it about 27 = 3^3 / its 3-adics?     -> No.  Powers of 3 are not special
                                               (mean z = -0.10 over 3^3..3^33), and the
                                               forward map is purely 2-adic: the whole
                                               move-sequence is a function of n's binary
                                               digits, blind to its factorisation.

The real cause: 86% of 27's orbit is ONE 96-step ascending dropping round (a
single "letter") that lifts it to 9232; 27 is the *smallest* integer whose low
bits encode a climb that long (smallest n with dropping time >= 96).  The "big
UPs" are a sustained run of odd values x = 3 (mod 4), each sending x -> ~1.5x.

Outputs:
    data/collatz_27_anatomy.png
"""

from __future__ import annotations

import math
from functools import lru_cache

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def traj(n: int) -> list[int]:
    s = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        s.append(n)
    return s


def drop_time(n: int) -> int:
    x, k = n, 0
    while True:
        x = x // 2 if x % 2 == 0 else 3 * x + 1
        k += 1
        if x < n:
            return k


import sys
sys.setrecursionlimit(1 << 20)
_memo = {1: 0}


def sigma(n: int) -> int:
    if n in _memo:
        return _memo[n]
    x, k = n, 0
    while True:
        x = x // 2 if x % 2 == 0 else 3 * x + 1
        k += 1
        if x < n:
            break
    _memo[n] = k + sigma(x)
    return _memo[n]


def main() -> None:
    t27 = traj(27)
    peak = max(t27)
    print(f"27: {len(t27)-1} steps, peak {peak} (2^{math.log2(peak):.2f}), "
          f"first letter {drop_time(27)} steps "
          f"({drop_time(27)/(len(t27)-1):.0%} of orbit)")

    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9))

    # ---- Panel 1: 27's altitude profile ----
    ax = axes[0, 0]
    alt = [math.log2(x) for x in t27]
    ax.plot(alt, "-", color="darkslateblue", lw=1.3)
    ax.fill_between(range(drop_time(27) + 1), 0, alt[:drop_time(27) + 1],
                    color="crimson", alpha=0.12)
    pk = alt.index(max(alt))
    ax.annotate(f"peak 9232 ($2^{{{math.log2(peak):.1f}}}$)",
                (pk, max(alt)), (pk - 30, max(alt) - 0.3), fontsize=8,
                arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.axhline(math.log2(27), color="0.6", ls=":", lw=0.8)
    ax.axvline(drop_time(27), color="crimson", ls="--", lw=0.9)
    ax.text(drop_time(27) / 2, 1.0, "first dropping round\n(96 steps = 86%)",
            color="crimson", fontsize=8, ha="center")
    ax.set_xlabel("step")
    ax.set_ylabel(r"altitude $\log_2 x$")
    ax.set_title("1. 27's orbit is one long climb, then a fall", fontsize=10)

    # ---- Panel 2: powers of 3 are NOT special ----
    ax = axes[0, 1]
    rng = np.random.default_rng(0)
    ks = list(range(3, 34))
    zs = []
    for k in ks:
        n = 3 ** k
        samp = rng.integers(int(n * 0.5) | 1, int(n * 1.5) | 1, 600) | 1
        ctrl = np.array([sigma(int(m)) for m in samp])
        zs.append((sigma(n) - ctrl.mean()) / ctrl.std())
    ax.axhspan(-2, 2, color="0.9")
    ax.axhline(0, color="0.5", lw=0.8)
    ax.plot(ks, zs, "o-", color="seagreen", ms=4)
    ax.plot(3, zs[0], "o", color="crimson", ms=9, label="$3^3=27$ (z=%.1f)" % zs[0])
    ax.text(20, np.mean(zs) + 0.25, f"mean z = {np.mean(zs):+.2f}",
            color="seagreen", fontsize=9)
    ax.set_xlabel("$k$ in $3^k$")
    ax.set_ylabel("length z-score vs same-size random odds")
    ax.set_title("2. Being a power of 3 doesn't predict length\n"
                 "(factorisation / 3-adics are irrelevant)", fontsize=10)
    ax.legend(fontsize=8)

    # ---- Panel 3: it's 2-adic -- dropping time vs n, 27 the first big spike ----
    ax = axes[1, 0]
    N = 2000
    dts = [drop_time(n) for n in range(2, N)]
    ax.plot(range(2, N), dts, lw=0.5, color="steelblue")
    ax.plot(27, drop_time(27), "o", color="crimson", ms=8)
    ax.annotate("27: smallest $n$ with\ndropping time $\\geq 96$",
                (27, 96), (200, 86), fontsize=8.5, color="crimson",
                arrowprops=dict(arrowstyle="->", lw=0.7, color="crimson"))
    ax.set_xlabel("$n$")
    ax.set_ylabel("dropping time (first-letter length)")
    ax.set_title("3. The climb is 2-adic: a record-long ascending letter\n"
                 "(the move-sequence is a function of $n$'s binary digits)",
                 fontsize=10)

    # ---- Panel 4: outlier context + the shortcut ----
    ax = axes[1, 1]
    ns = np.arange(3, 20000, 2)
    sg = np.array([sigma(int(n)) for n in ns])
    ax.plot(ns, sg, ".", ms=1, color="0.7", alpha=0.5)
    # local mean trend
    lg = np.log2(ns)
    a, b = np.polyfit(lg, sg, 1)
    xx = np.linspace(lg.min(), lg.max(), 50)
    ax.plot(2 ** xx, a * xx + b, "k-", lw=1.2, label=f"mean $\\approx${a:.1f}$\\log_2 n$")
    ax.plot(27, sigma(27), "o", color="crimson", ms=9, label="27 ($\\sim$2$\\sigma$ high)")
    ax.set_xscale("log")
    ax.set_xlabel("$n$ (log scale)")
    ax.set_ylabel("total steps $\\sigma(n)$")
    ax.set_title("4. 27 is only a ~2$\\sigma$ outlier (variance is huge)\n"
                 "shortcut: $\\sigma(n)=\\mathrm{drop}(n)+\\sigma(\\mathrm{dest})$, memoised",
                 fontsize=10)
    ax.legend(fontsize=8)

    fig.suptitle("Why 27 is long: a 2-adic accident of its binary expansion, "
                 "not a fact about $3^3$", fontsize=13, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig("data/collatz_27_anatomy.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote data/collatz_27_anatomy.png")


if __name__ == "__main__":
    main()
