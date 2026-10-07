"""Figure B for site/explore/thirty-six.md: triangular numbers, cubes and squares against the
dropping sets.

Computed, not sketched.  For K = 16 take the first 2^K members of each family (n = 0 .. 2^K - 1),
find the actual dropping time of every value, and compare the share in each dropping set with
the natural share N(k)/2^k of all integers (N = OEIS A100982 with the class "even" prepended).

  panel 1  triangular numbers, rule 3x+1   (fold: exactly natural)
  panel 2  cubes, rule 3x+1                (isometry on odd residues: exactly natural)
  panel 3  squares, rule 3x+1              (collapse: Dset_1 and Dset_3 only)
  panel 4  squares, rule 3x-1              (spread over many sets)

Conventions.  The site's dropping time counts un-shortcut steps (n/2 and 3n+1 are separate
steps), so a class of Terras level k with s odd steps is Dset_(k+s): levels 1, 2, 4, 5, 7, 8,
10, 12, 13, 15, 16 are Dset_1, 3, 6, 8, 11, 13, 16, 19, 21, 24, 26.  The values 0 and 1 do not
drop under 3x+1 (0 is fixed, 1 is on the cycle 1, 2); they are filed by residue (0 with the
evens, 1 with 1 mod 4).  Under 3x-1 the value 1 is a fixed point and goes in the last bucket.

Checked against scripts/thirty_six/figurate_2adic/README.md (Corollary 1, Theorem 2, Theorem 2')
by assertion before anything is drawn.  The plotted numbers are also written to
fig_thirty_six_figurate.json.

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 fig_thirty_six_figurate.py
Output: site/public/data/collatz_thirty_six_figurate.png
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

from check_thirty_six_page import dropping_word_counts, level_of, stop_ks, tri

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / "site" / "public" / "data" / "collatz_thirty_six_figurate.png"

SURFACE = "#ffffff"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
BLUE = "#2a78d6"       # rule 3x+1
ORANGE = "#eb6834"     # rule 3x-1

K = 16
M = 1 << K
S_TOP = 10                                   # orders 0..10 have Terras level <= 16
LEVELS = [level_of(s) for s in range(S_TOP + 1)]
DSET = [level_of(s) + s for s in range(S_TOP + 1)]
assert LEVELS == [1, 2, 4, 5, 7, 8, 10, 12, 13, 15, 16]
assert DSET == [1, 3, 6, 8, 11, 13, 16, 19, 21, 24, 26]
NEXT_DSET = level_of(S_TOP + 1) + S_TOP + 1
assert NEXT_DSET == 29
LABELS = [str(j) for j in DSET] + [f"{NEXT_DSET}+"]


def shares(values, q: int, d: int) -> list[Fraction]:
    """Share of the values in each listed dropping set, plus one last bucket for the rest."""
    cnt = {lv: 0 for lv in LEVELS}
    rest = 0
    total = 0
    for v in values:
        total += 1
        if v == 0:
            lv = 1
        elif v == 1:
            lv = 2 if (q, d) == (3, 1) else None
        else:
            ks = stop_ks(v, q, d)
            lv = ks[0] if ks else None
        if lv in cnt:
            cnt[lv] += 1
        else:
            rest += 1
    assert total == M
    return [Fraction(cnt[lv], M) for lv in LEVELS] + [Fraction(rest, M)]


def compute() -> dict:
    N = dropping_word_counts(S_TOP)
    assert N == [1, 1, 1, 2, 3, 7, 12, 30, 85, 173, 476]
    natural = [Fraction(N[s], 1 << level_of(s)) for s in range(S_TOP + 1)]
    natural.append(1 - sum(natural))
    tri_s = shares((tri(n) for n in range(M)), 3, 1)
    cub_s = shares((n ** 3 for n in range(M)), 3, 1)
    sq_p = shares((n * n for n in range(M)), 3, 1)
    sq_m = shares((n * n for n in range(M)), 3, -1)

    # the statements of the figurate README, asserted
    assert tri_s == natural, "triangular numbers must carry the natural law exactly (Corollary 1)"
    assert cub_s == natural, "cubes must carry the natural law exactly (Theorem 2)"
    half = Fraction(1, 2)
    assert sq_p == [half, half] + [0] * 10, "squares under 3x+1: Dset_1 and Dset_3 only (Theorem 2)"
    assert sq_m[0] == half and sq_m[1] == 0 and sq_m[2] == 0
    assert sq_m[3:6] == [half * Fraction(1, 4), half * Fraction(1, 8), half * Fraction(5, 32)], \
        "odd squares under 3x-1: 1/4, 1/8, 5/32 at Terras levels 5, 7, 8 (README, leads)"
    assert all(x > 0 for x in sq_m[3:]), "squares under 3x-1 meet every later set shown (Theorem 2')"
    return {"natural": natural, "triangular_3x+1": tri_s, "cubes_3x+1": cub_s,
            "squares_3x+1": sq_p, "squares_3x-1": sq_m}


def main() -> None:
    data = compute()
    (HERE / "fig_thirty_six_figurate.json").write_text(json.dumps({
        "K": K, "count": M, "dropping_set": LABELS, "terras_level": LEVELS + [f">{LEVELS[-1]}"],
        "shares": {k: [float(x) for x in v] for k, v in data.items()},
        "exact": {k: [str(x) for x in v] for k, v in data.items()},
    }, indent=1), encoding="utf-8")
    for name, v in data.items():
        print(f"{name:>16}: " + " ".join(f"{float(x):.4f}" for x in v))

    nat = [float(x) for x in data["natural"]]
    panels = [
        ("Triangular numbers under 3x + 1", "a fold: exactly the natural share, set by set",
         data["triangular_3x+1"], BLUE),
        ("Cubes under 3x + 1", "rigid on the odd numbers: exactly natural again",
         data["cubes_3x+1"], BLUE),
        ("Squares under 3x + 1", "a collapse: two sets hold every square above 1",
         data["squares_3x+1"], BLUE),
        ("Squares under 3x − 1", "the same squares, spread over set after set",
         data["squares_3x-1"], ORANGE),
    ]
    xs = list(range(len(LABELS)))
    fig, axes = plt.subplots(2, 2, figsize=(10.6, 9.2), sharey=True)
    fig.patch.set_facecolor(SURFACE)
    pct = FuncFormatter(lambda y, _: f"{100 * y:.0f}%")
    for idx, (ax, (title, sub, sh, color)) in enumerate(zip(axes.flat, panels)):
        vals = [float(x) for x in sh]
        ax.set_facecolor(SURFACE)
        ax.bar(xs, vals, width=0.70, color=color, zorder=2, linewidth=0)
        ax.hlines(nat, [x - 0.46 for x in xs], [x + 0.46 for x in xs], color=INK, lw=2.4, zorder=3)
        ax.set_ylim(0, 0.58)
        ax.set_xlim(-0.7, len(xs) - 0.3)
        ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ax.yaxis.set_major_formatter(pct)
        ax.set_xticks(xs)
        ax.set_xticklabels(LABELS)
        ax.tick_params(axis="both", length=0, labelsize=13, colors=INK2, pad=5)
        ax.grid(axis="y", color=GRID, lw=1.0, zorder=0)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(AXIS)
        ax.annotate(title, xy=(0, 1), xycoords="axes fraction", xytext=(0, 27), textcoords="offset points",
                    fontsize=14.5, fontweight="bold", color=INK, ha="left", va="bottom")
        ax.annotate(sub, xy=(0, 1), xycoords="axes fraction", xytext=(0, 7), textcoords="offset points",
                    fontsize=12.5, color=INK2, ha="left", va="bottom")
        if idx % 2 == 0:
            ax.set_ylabel("share of the first 65,536", fontsize=13, color=INK2, labelpad=8)
        if idx >= 2:
            rule = "3x − 1" if idx == 3 else "3x + 1"
            ax.set_xlabel(f"dropping time under {rule}", fontsize=13, color=INK2, labelpad=8)

    # selective direct labels
    ax = axes[1, 0]
    ax.text(0.5, 0.512, "50% each", ha="center", va="bottom", fontsize=12.5, color=INK)
    ax.text(6.6, 0.33, "no square above 1\nin any other set", ha="center", va="center",
            fontsize=12.5, color=INK2, linespacing=1.3)
    ax = axes[1, 1]
    ax.text(0, 0.512, "50%", ha="center", va="bottom", fontsize=12.5, color=INK)
    ax.text(6.9, 0.33, "squares of 2 … 200,000:\n103 different dropping times", ha="center", va="center",
            fontsize=12.5, color=INK2, linespacing=1.3)
    ax.text(1.5, 0.006, "none", ha="center", va="bottom", fontsize=12.5, color=INK2)

    handles = [Patch(facecolor=BLUE, label="share of the family, rule 3x + 1"),
               Patch(facecolor=ORANGE, label="share of the family, rule 3x − 1"),
               Line2D([0], [0], color=INK, lw=2.4, label="natural share: all integers")]
    # one legend for all four panels, in the header (kept clear of the gridlines)
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.066, 0.892), ncol=3, fontsize=12.5,
               frameon=False, handlelength=1.3, labelcolor=INK2, columnspacing=1.8, borderaxespad=0.0)

    fig.text(0.075, 0.978, "Triangle, cube, square: three ways to meet the dropping sets",
             fontsize=18, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.075, 0.940, "Where the first 65,536 members of each family fall, by dropping time "
             "(the index of the dropping set).\n"
             "Bars come from the actual orbits, n = 0 to 65,535; 0 and 1, which never drop, are filed by residue.",
             fontsize=12.5, color=INK2, ha="left", va="top", linespacing=1.35)
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.08, top=0.765, wspace=0.07, hspace=0.50)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=170, facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
