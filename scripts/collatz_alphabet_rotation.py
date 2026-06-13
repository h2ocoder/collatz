"""The dropping alphabet and the log-6 rotation are one continued fraction.

The alphabet of the dropping dictionary (scripts/collatz_dropping_alphabet.py)
is built from blocks A = OE (altitude step +log2 3 - 1) and B = E (step -1).
A level-s letter is a ballot path of s A-blocks and (e_s - s) B-blocks,
e_s = ceil(s*log2 3).  Climbing one level adds exactly one A-block and
(e_{s+1} - e_s - 1) in {0,1} B-blocks.

That 0/1 schedule -- equivalently the increments e_{s+1}-e_s in {1,2} -- is
*exactly* the Beatty / Sturmian word of log2 3:

    e_{s+1} - e_s = floor((s+1) log2 3) - floor(s log2 3)  in  {1,2}.

And log2 3 is the same irrational that drives the log-6 rotation: with
alpha = log6 3 = log2(3)/(1+log2 3), the two share a continued-fraction tail,
so the convergent denominators of alpha -- 1,1,2,3,5,13,31,106,137,791,... --
are simultaneously

  * the rotation's near-return periods (the 13/31/137 parastichy arms,
    the 44-step quasi-period as a semiconvergent), AND
  * the resonant levels of the alphabet, where s*log2 3 is closest to an
    integer so the leading letter (OE)^s E^(k-2s) lands its final drop with
    the smallest altitude margin (the "tightest" ballot paths).

Two faces of one number: the combinatorial alphabet (arithmetic) and the
harmonic rotation (multiplicity) are stitched by the continued fraction of
log2 3.

Outputs:
    data/collatz_alphabet_rotation.png
"""

from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

B = math.log2(3)
ALPHA = math.log(3) / math.log(6)


def cf(x: float, n: int) -> list[int]:
    a = []
    for _ in range(n):
        i = math.floor(x)
        a.append(i)
        x -= i
        if x < 1e-12:
            break
        x = 1.0 / x
    return a


def convergent_denoms(a: list[int]) -> list[int]:
    k0, k1 = 0, 1
    out = [1]
    for ai in a[1:]:
        k0, k1 = k1, ai * k1 + k0
        out.append(k1)
    return out


def main() -> None:
    S = 80
    # Beatty word of log2 3 = the block schedule
    beatty = [math.floor((s + 1) * B) - math.floor(s * B) for s in range(S)]
    # final-drop altitude margin of the leading letter at level s:
    #   margin_s = e_s - s*log2 3  (how far 2^{e_s} overshoots 3^s, in log2)
    margin = [math.ceil(s * B) - s * B for s in range(1, S)]

    alpha_denoms = convergent_denoms(cf(ALPHA, 13))
    log2_3_denoms = convergent_denoms(cf(B, 12))
    # resonant s-levels = convergent denominators of log2 3 (tight margins)
    res_s = [q for q in log2_3_denoms if 0 < q < S]

    fig, axes = plt.subplots(1, 2, figsize=(14.5, 5.0))

    # ---- Panel 1: the schedule + the tightening margins -------------------
    ax = axes[0]
    s_axis = np.arange(1, S)
    ax.plot(s_axis, margin, "-", color="0.7", lw=0.8, zorder=1)
    ax.scatter(s_axis, margin, c=[("crimson" if (b == 2) else "steelblue")
                                  for b in beatty[1:S]], s=18, zorder=2)
    for q in res_s:
        if q < S:
            ax.axvline(q, color="seagreen", ls=":", lw=0.9, zorder=0)
            ax.text(q, 0.97, str(q), color="seagreen", fontsize=8,
                    ha="center", va="top", rotation=0)
    ax.set_xlabel("level $s$ (odd-step count)")
    ax.set_ylabel(r"final-drop margin  $e_s - s\log_2 3$")
    ax.set_title("Alphabet block schedule = Beatty word of $\\log_2 3$\n"
                 "red = a $B$-block added (jump 2) · blue = none (jump 1)\n"
                 "green = convergent levels $s$ (tightest ballot paths)",
                 fontsize=9.5)
    from matplotlib.lines import Line2D
    ax.legend(handles=[
        Line2D([0], [0], marker="o", ls="", color="crimson",
               label="jump 2 (add $B$)"),
        Line2D([0], [0], marker="o", ls="", color="steelblue",
               label="jump 1 (no $B$)")], fontsize=8, loc="upper right")

    # ---- Panel 2: the shared continued-fraction ladder --------------------
    ax = axes[1]
    ax.axis("off")
    ax.set_title("One continued fraction stitches both sides", fontsize=11)
    rows = [
        (r"$\log_2 3$", cf(B, 10)),
        (r"$\alpha=\log_6 3$", cf(ALPHA, 11)),
    ]
    y = 0.95
    ax.text(0.02, y, "continued fractions (shared tail):", fontsize=9,
            fontweight="bold")
    y -= 0.085
    for name, a in rows:
        ax.text(0.04, y, f"{name} = [{a[0]}; " +
                ", ".join(str(x) for x in a[1:]) + "]", fontsize=9)
        y -= 0.07
    y -= 0.05
    ax.text(0.02, y, r"convergent denominators of $\alpha$ = rotation periods:",
            fontsize=9, fontweight="bold")
    y -= 0.075
    txt = "  ".join(str(q) for q in alpha_denoms if q <= 800)
    ax.text(0.04, y, txt, fontsize=10, color="darkslateblue")
    y -= 0.085
    ax.text(0.04, y, "13, 31, 137  →  the parastichy arms / near-return "
            "periods\nseen in the rotation (44 is the 27/44 semiconvergent).",
            fontsize=8.5, color="0.3")
    y -= 0.135
    ax.text(0.02, y, "same denominators are the alphabet's resonant levels:",
            fontsize=9, fontweight="bold")
    y -= 0.075
    ax.text(0.04, y, "  ".join(str(q) for q in res_s),
            fontsize=10, color="seagreen")
    y -= 0.075
    ax.text(0.04, y, "levels $s$ where $s\\log_2 3$ is nearest an integer —\n"
            "the tightest letters, smallest final-drop margin (panel 1).",
            fontsize=8.5, color="0.3")
    y -= 0.145
    ax.text(0.02, y, "Arithmetic (the alphabet) and multiplicity (the\n"
            "rotation) are two readings of one irrational, $\\log_2 3$.",
            fontsize=9.5, style="italic")

    fig.suptitle("The dropping alphabet and the log-6 rotation: "
                 "one continued fraction", fontsize=12, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig("data/collatz_alphabet_rotation.png", dpi=150,
                bbox_inches="tight")
    plt.close(fig)

    print("Beatty word of log2 3 (block schedule):", beatty[1:25])
    print("e_{s+1}-e_s increments match Beatty:",
          [math.ceil((s + 1) * B) - math.ceil(s * B) for s in range(1, 25)]
          == beatty[1:25])
    print("alpha convergent denominators (rotation periods):", alpha_denoms)
    print("log2 3 convergent denominators (resonant levels):", res_s)
    print("wrote data/collatz_alphabet_rotation.png")


if __name__ == "__main__":
    main()
