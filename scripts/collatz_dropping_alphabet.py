"""The dropping alphabet: one letter, two readings (2-adic partition / 3-adic overlap).

Companion to scripts/collatz_nested_dropping.py.  That script showed the
dropping map is one dictionary read two ways.  This one characterises the
ALPHABET of that dictionary from first principles and measures the asymmetry
between the two readings.

A *letter* is a primitive dropping word.  Stripped to its essence it is a
parity word that is

  (a) started by O           (the seed is odd),
  (b) free of adjacent O's   (3n+1 is always even, so O forces a following E),
  (c) ballot-admissible      (3^o > 2^e at every interior step; the first
                              drop, 3^o < 2^e, happens only at the very end).

The ONLY inputs are the integers 2 and 3, entering through the comparison
3^o vs 2^e.  No prime is privileged; arithmetic (2) and multiplicity (3) are
two *readings* of the same lattice path.  The number of letters with s odd
steps is

    1, 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, ...

which is exactly OEIS A100982 — the admissible Collatz sequences of the
stopping-time literature (Wagon 1985, Terras, Chamberland, Winkler,
Roosendaal); the length of the order-s letters is A020914(s) = ceil(s*log2 6).

Growth rate (verified numerically):

    lambda = beta^beta / (beta-1)^(beta-1),   beta = log2 3 ≈ 1.585,
           ≈ 2.8395,

the binomial entropy of choosing s odd steps among e_s = ceil(s*log2 3) even
slots (the ballot/positivity constraint costs only a polynomial factor).

THE TWO READINGS.  Each letter of level s carries two keys at the SAME scale,
because e_s = ceil(s*log2 3) gives 2^{e_s} in [3^s, 2*3^s):

  FORWARD  (2-adic):  key n mod 2^{e_s}.  These PARTITION Z_2 —
           sum_s w_s / 2^{e_s} = 1.  The forward map n -> word is a function;
           every integer has exactly one dropping word.  Arithmetic packs the
           alphabet disjointly: full measure, dimension 1.

  BACKWARD (3-adic):  key d mod 3^s.  These OVERLAP —
           sum_s w_s / 3^s = 1.690.  The backward map word -> destination is
           multivalued; a typical destination has ~1.69 one-round
           predecessors.  Multiplicity lets the alphabet overlap: redundant
           cover, per-level Cantor dust of dimension log3(lambda) ≈ 0.95.

So the SAME alphabet at the SAME resolution is a partition under the 2-adic
reading and a 1.69-fold overlap under the 3-adic reading.  The forward
direction is a function (disjoint preimages); the backward direction is
multivalued (overlapping images).  That functional/multivalued asymmetry is
the 2-adic/3-adic complementarity, and the excess mass 0.69 over the trivial
halving n=2d is exactly the overlap of dropping orbits.

Three views:
  1. Growth of the alphabet vs the closed-form rate lambda (A100982).
  2. The two readings: cumulative 2-adic mass -> 1 (partition) vs cumulative
     3-adic mass -> 1.69 (overlap).
  3. Predecessor multiplicity: histogram of one-round predecessors per
     destination, mean = the 3-adic overlap sum.

Outputs:
    data/collatz_dropping_alphabet.png
"""

from __future__ import annotations

import math
from collections import defaultdict
from fractions import Fraction

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from collatz.dropping import dropping_destination, dropping_time
from collatz.residues import dropping_set_residues

BETA = math.log2(3)
LAMBDA = BETA ** BETA / (BETA - 1) ** (BETA - 1)


def e_of(s: int) -> int:
    """Number of halvings (even steps) for a level-s letter = k_s - s."""
    return 1 if s == 0 else math.ceil(s * BETA)


def letter_counts(s_max: int) -> list[int]:
    """w_s = number of admissible dropping words with s odd steps (A100982)."""
    drops: dict[int, int] = defaultdict(int)
    e_max = int((s_max + 1) * BETA) + 3
    pow3 = [3 ** o for o in range(s_max + 2)]
    pow2 = [2 ** e for e in range(e_max + 2)]
    active = {(1, 0, True): 1}
    while active:
        nxt: dict = defaultdict(int)
        for (o, e, last_o), c in active.items():
            if not last_o and o + 1 <= s_max:           # O step (no OO)
                nxt[(o + 1, e, True)] += c
            if pow3[o] < pow2[e + 1]:                   # E step that drops
                drops[o] += c
            elif e + 1 <= e_max:                        # E step, still aloft
                nxt[(o, e + 1, False)] += c
        active = nxt
    drops[0] = 1
    return [drops[s] for s in range(s_max + 1)]


def build_dictionary(k_max: int) -> list[tuple[int, int, int]]:
    """Distinct (k, s, C) letters realised up to dropping time k_max."""
    dic = []
    for k in range(1, k_max + 1):
        R = dropping_set_residues(k)
        if not R:
            continue
        seen = set()
        for r in sorted(R):
            M = 1 << k
            n0 = r if r >= 2 else r + M
            mult, add, x, s = Fraction(1), Fraction(0), n0, 0
            for _ in range(k):
                if x % 2:
                    x = 3 * x + 1
                    mult, add, s = 3 * mult, 3 * add + 1, s + 1
                else:
                    x //= 2
                    mult, add = mult / 2, add / 2
            C = int(add * (1 << (k - s)))
            if (k, s, C) not in seen:
                seen.add((k, s, C))
                dic.append((k, s, C))
    return dic


def predecessor_count(d: int, dic: list[tuple[int, int, int]]) -> int:
    """How many letters reconstruct a genuine one-round predecessor of d."""
    c = 0
    for (k, s, C) in dic:
        num = (1 << (k - s)) * d - C
        if num > 0 and num % (3 ** s) == 0:
            n = num // (3 ** s)
            if n > 1 and dropping_time(n) == k and dropping_destination(n) == d:
                c += 1
    return c


def main() -> None:
    S_MAX = 200
    w = letter_counts(S_MAX)
    print("letters per level w_s:", w[:14], "...")
    print(f"closed-form lambda = beta^beta/(beta-1)^(beta-1) = {LAMBDA:.5f}  "
          f"(beta=log2 3); log3(lambda) = {math.log(LAMBDA)/math.log(3):.4f}")

    fwd_terms = [w[s] / 2.0 ** e_of(s) for s in range(len(w))]
    bwd_terms = [w[s] / 3.0 ** s for s in range(len(w))]
    fwd_cum = np.cumsum(fwd_terms)
    bwd_cum = np.cumsum(bwd_terms)
    print(f"FORWARD  sum w_s/2^e_s = {fwd_cum[-1]:.6f}  (partition of Z_2 -> 1)")
    print(f"BACKWARD sum w_s/3^s   = {bwd_cum[-1]:.6f}  (avg predecessors / dest)")

    # empirical predecessor multiplicity over a destination range
    dic = build_dictionary(22)
    D_HI = 3000
    counts = np.array([predecessor_count(d, dic) for d in range(2, D_HI)])
    print(f"empirical mean predecessors per destination (k<=22): {counts.mean():.4f}")

    # ---------------------------------------------------------------- figure
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))

    # View 1 — growth of the alphabet
    ax = axes[0]
    s_show = np.arange(1, 30)
    ax.semilogy(s_show, [w[s] for s in s_show], "o-", ms=4,
                color="darkslateblue", label="$w_s$  (letters, A100982)")
    ref = [w[6] * LAMBDA ** (s - 6) for s in s_show]
    ax.semilogy(s_show, ref, "r--", lw=1.2,
                label=rf"$\lambda^s$,  $\lambda={LAMBDA:.3f}$")
    ax.set_xlabel("odd-step count $s$ (order)")
    ax.set_ylabel("number of letters")
    ax.set_title("1. The alphabet = admissible Collatz words\n"
                 r"$\lambda=\beta^\beta/(\beta-1)^{\beta-1}$, $\beta=\log_2 3$",
                 fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(True, which="both", alpha=0.2)

    # View 2 — two readings
    ax = axes[1]
    smax_plot = 28
    ax.plot(range(smax_plot), fwd_cum[:smax_plot], "o-", ms=3,
            color="steelblue", label=r"2-adic: $\sum w_s/2^{e_s}$ (forward)")
    ax.plot(range(smax_plot), bwd_cum[:smax_plot], "s-", ms=3,
            color="crimson", label=r"3-adic: $\sum w_s/3^{s}$ (backward)")
    ax.axhline(1.0, color="steelblue", ls=":", lw=0.9)
    ax.axhline(bwd_cum[-1], color="crimson", ls=":", lw=0.9)
    ax.text(smax_plot * 0.55, 1.03, "PARTITION (mass 1)\nforward map is a function",
            color="steelblue", fontsize=8)
    ax.text(smax_plot * 0.30, bwd_cum[-1] + 0.03,
            f"OVERLAP (mass {bwd_cum[-1]:.2f})\nbackward map is multivalued",
            color="crimson", fontsize=8)
    ax.set_xlabel("levels included (up to $s$)")
    ax.set_ylabel("cumulative measure")
    ax.set_title("2. Same alphabet, same scale "
                 r"($2^{e_s}\!\in[3^s,2\cdot3^s)$)" "\n"
                 "2-adic packs it disjointly · 3-adic overlaps",
                 fontsize=10)
    ax.legend(fontsize=8, loc="center right")
    ax.set_ylim(0, bwd_cum[-1] + 0.25)

    # View 3 — predecessor multiplicity
    ax = axes[2]
    maxc = counts.max()
    ax.hist(counts, bins=np.arange(-0.5, maxc + 1.5, 1),
            color="crimson", alpha=0.8, rwidth=0.85)
    ax.axvline(counts.mean(), color="black", lw=1.4,
               label=f"mean = {counts.mean():.2f}")
    ax.axvline(bwd_cum[-1], color="0.4", ls="--", lw=1.1,
               label=rf"$\sum w_s/3^s={bwd_cum[-1]:.2f}$")
    ax.set_xlabel("one-round predecessors of a destination $d$")
    ax.set_ylabel(f"count over $d\\in[2,{D_HI})$")
    ax.set_title("3. The overlap, concretely\n"
                 "how many letters reconstruct each destination",
                 fontsize=10)
    ax.legend(fontsize=8)

    fig.suptitle("The dropping alphabet: one letter, two readings — "
                 "2-adic partition vs 3-adic overlap", fontsize=12, y=1.02)
    fig.savefig("data/collatz_dropping_alphabet.png", dpi=150,
                bbox_inches="tight")
    plt.close(fig)
    print("wrote data/collatz_dropping_alphabet.png")


if __name__ == "__main__":
    main()
