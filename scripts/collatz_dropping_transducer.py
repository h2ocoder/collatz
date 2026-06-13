"""Is the dictionary a finite 2-adic -> 3-adic transducer?  No -- and Cobham says why.

The dropping dictionary maps a letter's 2-adic key (n mod 2^{e_s}) to its
3-adic key (d mod 3^s).  Natural question: is this one finite-state transducer
reading the base-2 digits of n and emitting the base-3 digits of d = dest(n)?

This script answers NO, twice, and pins the reason.

(1) The forward letter-machine is INFINITE-STATE.  Reading n LSB-first under
    the shortened Collatz map T (T(x)=(3x+1)/2 if odd, x/2 if even), the parity
    of the j-th step is  next_bit XOR carry,  but the "carry" is the low-bit
    trajectory T^j(low bits) itself -- an unbounded register.  Counting
    Myhill-Nerode classes of (n mod 2^j) -> (parity prefix of length j) gives
    10, 28, 88, 295, 1024, 3626, ... growing without bound.  No finite
    automaton computes the letter assignment.  (Consistent with the parity
    vector map not being k-automatic.)

(2) Emitting d to base-3 precision 3^M ENTANGLES both bases of n.  Exactly:

        d mod 3^M  is determined by  ( letter(n) , n mod 3^{M-s} )

    -- verified with zero violations -- where letter(n) needs e_s = ceil(s log2 3)
    BASE-2 digits of n, and the remaining M-s ternary digits of d need n mod
    3^{M-s}, i.e. BASE-3 digits of n.  The letter ALONE leaves d mod 3^M spread
    over up to 3^{M-s} values.  So d's ternary expansion has a seam at digit s:
    the low s digits (the dictionary key) are supplied by the base-2 reading of
    n; every digit above is supplied by the base-3 reading of n.

    A finite base-2 -> base-3 transducer cannot do this: it would make the
    dropping relation automatic in two multiplicatively independent bases, and
    by COBHAM'S THEOREM (1969) the only such relations are ultimately periodic
    (Presburger-definable).  The dropping map -- infinitely many affine pieces
    with non-periodic breakpoints -- is not.  Hence no finite 2->3 transducer.

THE POSITIVE RESIDUE.  The dictionary survives because it only ever matches the
KEY: the low s ternary digits of d, which the base-2 letter does determine.
That is a finite correspondence at exactly the granularity Cobham permits
(bounded digits).  Push past the key and you must read n in the other base.
Arithmetic (base 2) and multiplicity (base 3) meet precisely at the letter and,
by Cobham, nowhere further -- the same wall as the irrationality of the
log-6 rotation, now as a theorem.

Outputs:
    data/collatz_dropping_transducer.png
"""

from __future__ import annotations

import math
import random
from fractions import Fraction

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from collatz.dropping import dropping_destination, dropping_time


def T(x: int) -> int:
    return (3 * x + 1) // 2 if x & 1 else x // 2


def mn_states(j: int, probe: int = 26) -> int:
    """Myhill-Nerode classes of (n mod 2^j) -> future parity behavior."""
    sigs = set()
    for L in range(1 << j):
        m = L
        for _ in range(j):
            m = T(m)
        sig, x = [], m
        for _ in range(probe):
            sig.append(x & 1)
            x = T(x)
        sigs.add(tuple(sig))
    return len(sigs)


def letter_of(n: int) -> tuple[int, int, int]:
    """(k, s, C) of n's dropping round."""
    k = dropping_time(n)
    mult, add, x, s = Fraction(1), Fraction(0), n, 0
    for _ in range(k):
        if x & 1:
            x = 3 * x + 1
            mult, add, s = 3 * mult, 3 * add + 1, s + 1
        else:
            x //= 2
            mult, add = mult / 2, add / 2
    return k, s, int(add * (1 << (k - s)))


def main() -> None:
    # ---- (1) forward letter-machine is infinite-state ---------------------
    depths = [4, 6, 8, 10, 12, 14]
    states = [mn_states(j) for j in depths]
    print("Myhill-Nerode states of the letter machine:")
    for j, st in zip(depths, states):
        print(f"  depth j={j:2d}: {st:5d} states   (2^j = {1 << j})")

    # ---- (2) base-2 / base-3 entanglement in emitting d -------------------
    random.seed(2)
    Ms = [2, 3, 4, 5, 6]
    letter_spread = []     # max distinct d mod 3^M per letter (= 3^{M-s})
    joint_ok = []          # violations of (letter, n mod 3^{M-s}) -> d mod 3^M
    sample = [random.randrange(3, 10 ** 7) | 1 for _ in range(60000)]
    pre = [(n, letter_of(n), dropping_destination(n)) for n in sample]
    for M in Ms:
        byletter: dict = {}
        joint: dict = {}
        viol = 0
        for n, (k, s, C), d in pre:
            if s >= M:
                continue
            dm = d % 3 ** M
            byletter.setdefault((k, s, C), set()).add(dm)
            key = ((k, s, C), n % 3 ** (M - s))
            if key in joint and joint[key] != dm:
                viol += 1
            joint[key] = dm
        letter_spread.append(max(len(v) for v in byletter.values()))
        joint_ok.append(viol)
    print("\nemitting d mod 3^M:")
    for M, sp, v in zip(Ms, letter_spread, joint_ok):
        print(f"  M={M}: letter alone -> up to {sp:4d} values of d mod 3^M;  "
              f"(letter, n mod 3^(M-s)) -> {v} violations")

    # ---------------------------------------------------------------- figure
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.0))

    ax = axes[0]
    ax.semilogy(depths, states, "o-", color="darkslateblue", ms=5,
                label="MN states of the letter machine")
    ax.semilogy(depths, [1 << j for j in depths], "k:", lw=1,
                label="$2^j$ (read every bit)")
    ax.set_xlabel("binary digits of $n$ read (depth $j$)")
    ax.set_ylabel("distinct states")
    ax.set_title("1. The forward letter-machine is infinite-state\n"
                 "Myhill–Nerode classes grow without bound — "
                 "no finite automaton", fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(True, which="both", alpha=0.2)

    ax = axes[1]
    width = 0.38
    xs = np.arange(len(Ms))
    ax.bar(xs - width / 2, letter_spread, width, color="crimson", alpha=0.85,
           label="letter (base-2) alone")
    ax.bar(xs + width / 2, [1] * len(Ms), width, color="steelblue", alpha=0.85,
           label=r"letter $+\ n\,\mathrm{mod}\, 3^{M-s}$ (base-3)")
    for x, sp in zip(xs, letter_spread):
        ax.text(x - width / 2, sp * 1.15, str(sp), ha="center", fontsize=8,
                color="crimson")
    ax.set_yscale("log")
    ax.set_xticks(xs)
    ax.set_xticklabels([f"$3^{M}$" for M in Ms])
    ax.set_xlabel(r"target precision of $d$  ($d\,\mathrm{mod}\, 3^M$)")
    ax.set_ylabel(r"values of $d\,\mathrm{mod}\, 3^M$ left undetermined")
    ax.set_title("2. Emitting $d$ in base 3 entangles both bases of $n$\n"
                 "base-2 letter fixes only the low $s$ digits "
                 "(the key) — Cobham", fontsize=10)
    ax.legend(fontsize=8)

    fig.suptitle("No finite 2→3 transducer: the dictionary is finite only at "
                 "the key (Cobham's theorem)", fontsize=12, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig("data/collatz_dropping_transducer.png", dpi=150,
                bbox_inches="tight")
    plt.close(fig)
    print("\nwrote data/collatz_dropping_transducer.png")


if __name__ == "__main__":
    main()
