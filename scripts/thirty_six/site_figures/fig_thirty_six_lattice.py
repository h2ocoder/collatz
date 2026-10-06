"""Figure A for site/explore/thirty-six.md: the four facts about 36 on the exponent lattice.

Each dot is the number 2^a 3^b at the lattice point (a, b).  Four small multiples of the same
lattice, one overlay each:

  1. the four consecutive pairs (1,2), (2,3), (3,4), (8,9) as links, and the rectangle
     8 x 9 = 72: the corner 72 is the cell (3,2), and T_8 = 36 is half of it;
  2. the anti-diagonal 4 -> 6 -> 9 walked by the cycle {-5, -7, -10} in the coordinate v = n + 1,
     the rectangle 4 x 9 = 36, and the line 2^a = 3^b labelled;
  3. the point (2,2) = 36 with the three Pierpont points (1,1), (1,2), (2,2) that carry the
     primes 7, 19, 37, and the 3 x 3 block of the nine divisors of 36 (which have 36 divisors
     in all: F(36) = 36);
  4. 5 = 3 + 2 = 9 - 4, the modulus of the folded pentagon.

Everything drawn is asserted first (no number is typed in without a check).

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 fig_thirty_six_lattice.py
Output: site/public/data/collatz_thirty_six_lattice.png
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

OUT = Path(__file__).resolve().parents[3] / "site" / "public" / "data" / "collatz_thirty_six_lattice.png"

# palette (categorical slots 1-3 of the dataviz reference palette, light surface)
SURFACE = "#ffffff"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
EDGE = "#c3c2b7"
BLUE, BLUE_T = "#2a78d6", "#d6e7fb"
ORANGE, ORANGE_T = "#eb6834", "#fbdccd"
AQUA, AQUA_T = "#1baf7a", "#cdefe2"

A_MAX, B_MAX = 4, 2
XLIM = (-0.52, A_MAX + 0.52)
YLIM = (-0.52, B_MAX + 0.80)        # head-room above the top row for tags
R = 0.235                           # node radius in lattice units
SLOPE = math.log(2) / math.log(3)   # the line 2^a = 3^b is b = a * log_3(2)

FS_NODE, FS_TAG, FS_SUB, FS_TITLE, FS_AX = 13, 12, 12, 15, 12.5


def num(a: int, b: int) -> int:
    return 2 ** a * 3 ** b


def is_prime(n: int) -> bool:
    return n > 1 and all(n % p for p in range(2, int(n ** 0.5) + 1))


def shortcut(n: int) -> int:
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


# ----------------------------------------------------------------------------- facts drawn
PAIRS = [((0, 0), (1, 0)), ((1, 0), (0, 1)), ((0, 1), (2, 0)), ((3, 0), (0, 2))]
for (p, q) in PAIRS:
    assert abs(num(*p) - num(*q)) == 1, (p, q)
assert sorted(tuple(sorted((num(*p), num(*q)))) for p, q in PAIRS) == [(1, 2), (2, 3), (3, 4), (8, 9)]
RATIO = {(1, 2): "2:1", (2, 3): "3:2", (3, 4): "4:3", (8, 9): "9:8"}
# the cell (3, 2) of the pair (8, 9) is the lattice point 72 = 8 x 9; its triangular number is half
assert num(3, 0) * num(0, 2) == num(3, 2) == 72 == 2 * num(2, 2) and 8 * 9 // 2 == 36

CYCLE_N = [-5, -7, -10]
assert [shortcut(n) for n in CYCLE_N] == [-7, -10, -5]
CYCLE_V = [n + 1 for n in CYCLE_N]
assert CYCLE_V == [-4, -6, -9] and CYCLE_V[0] * CYCLE_V[2] == 36 == CYCLE_V[1] ** 2
assert all(2 * w == 3 * v for v, w in zip(CYCLE_V, CYCLE_V[1:]))          # each odd step is v -> 3v/2
ANTI = [(2, 0), (1, 1), (0, 2)]
assert [num(*p) for p in ANTI] == [-v for v in CYCLE_V]

PIERPONT = [(1, 1), (1, 2), (2, 2)]
PRIMES = [num(*p) + 1 for p in PIERPONT]
assert PRIMES == [7, 19, 37] and all(is_prime(p) for p in PRIMES)
assert sum(1 for a in range(3) for b in range(3) if 36 % num(a, b) == 0) == 9   # divisors of 36
# the divisor 2^i 3^j of 36 has (i+1)(j+1) divisors: 36 in all, and (1+2+3)^2 = 1^3 + 2^3 + 3^3
assert sum((i + 1) * (j + 1) for i in range(3) for j in range(3)) == 36 == 1 ** 3 + 2 ** 3 + 3 ** 3

assert num(0, 1) + num(1, 0) == 5 == num(0, 2) - num(2, 0)
assert num(2, 2) == 36


# ----------------------------------------------------------------------------- drawing
def base(ax, hi: dict, show_x: bool, show_y: bool, ring=((2, 2),)) -> None:
    """Lattice, the line 2^a = 3^b and the number nodes.  hi: {(a, b): (edge, fill)};
    ring: nodes drawn with a black ring and a bold number (36 everywhere, 72 in panel 1)."""
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_aspect("equal")
    ax.set_facecolor(SURFACE)
    for a in range(A_MAX + 1):
        ax.plot([a, a], [0, B_MAX], color=GRID, lw=1.0, zorder=0, solid_capstyle="butt")
    for b in range(B_MAX + 1):
        ax.plot([0, A_MAX], [b, b], color=GRID, lw=1.0, zorder=0, solid_capstyle="butt")
    x_end = min(XLIM[1] - 0.05, (B_MAX + 0.52) / SLOPE)
    ax.plot([0, x_end], [0, SLOPE * x_end], color=MUTED, lw=1.4, zorder=1)
    for a in range(A_MAX + 1):
        for b in range(B_MAX + 1):
            edge, fill = hi.get((a, b), (EDGE, SURFACE))
            strong = (a, b) in hi
            is36 = (a, b) in ring
            ax.add_patch(Circle((a, b), R, facecolor=fill, edgecolor=INK if is36 and not strong else edge,
                                lw=2.8 if strong else (2.2 if is36 else 1.0), zorder=4))
            ax.text(a, b, str(num(a, b)), ha="center", va="center", zorder=5,
                    fontsize=FS_NODE, color=INK if (strong or is36) else INK2,
                    fontweight="bold" if (strong or is36) else "normal")
    ax.set_xticks(range(A_MAX + 1))
    ax.set_yticks(range(B_MAX + 1))
    ax.tick_params(length=0, labelsize=FS_AX, colors=MUTED, pad=4,
                   labelbottom=show_x, labelleft=show_y)
    for sp in ax.spines.values():
        sp.set_visible(False)
    if show_x:
        ax.set_xlabel("a  (how many factors 2)", fontsize=FS_AX, color=INK2, labelpad=6)
    if show_y:
        ax.set_ylabel("b  (how many factors 3)", fontsize=FS_AX, color=INK2, labelpad=6)


def head(ax, title: str, sub: str) -> None:
    ax.annotate(title, xy=(0, 1), xycoords="axes fraction", xytext=(0, 43), textcoords="offset points",
                fontsize=FS_TITLE, fontweight="bold", color=INK, ha="left", va="bottom")
    ax.annotate(sub, xy=(0, 1), xycoords="axes fraction", xytext=(0, 4), textcoords="offset points",
                fontsize=FS_SUB, color=INK2, ha="left", va="bottom", linespacing=1.3)


def link(ax, p, q, color, lw=4.2) -> None:
    ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=lw, zorder=2, solid_capstyle="round")


def tag(ax, x, y, s) -> None:
    ax.text(x, y, s, ha="center", va="center", fontsize=FS_TAG, color=INK, zorder=6,
            bbox=dict(boxstyle="round,pad=0.2", facecolor=SURFACE, edgecolor="none"))


def main() -> None:
    # manual layout in inches, so the lattice keeps its shape and nothing collides
    W, left, right, cgap = 10.6, 0.80, 0.15, 0.30
    pw = (W - left - right - cgap) / 2
    unit = pw / (XLIM[1] - XLIM[0])
    ph = (YLIM[1] - YLIM[0]) * unit
    top_block, header, rgap, bottom = 1.00, 1.08, 0.22, 0.78
    H = top_block + 2 * (header + ph) + rgap + bottom
    fig = plt.figure(figsize=(W, H))
    fig.patch.set_facecolor(SURFACE)
    y_top = H - top_block - header - ph
    y_bot = bottom
    xs = (left, left + pw + cgap)
    axes = {(r, c): fig.add_axes([xs[c] / W, (y_top if r == 0 else y_bot) / H, pw / W, ph / H])
            for r in (0, 1) for c in (0, 1)}

    # 1. consecutive pairs ---------------------------------------------------------------
    ax = axes[0, 0]
    hi = {p: (BLUE, BLUE_T) for pq in PAIRS for p in pq}
    base(ax, hi, show_x=False, show_y=True, ring=((2, 2), (3, 2)))
    # the rectangle 8 x 9 = 72 (exponent vectors (3,0) + (0,2) = (3,2)): the cell (3, 2)
    ax.plot([3, 3, 0], [0, 2, 2], color=BLUE_T, lw=8, zorder=1.5, solid_capstyle="round",
            solid_joinstyle="round")
    where = {(1, 2): (0.50, -0.31), (2, 3): (0.50, 0.50), (3, 4): (1.40, 0.30), (8, 9): (0.84, 1.44)}
    for p, q in PAIRS:
        link(ax, p, q, BLUE)
        key = tuple(sorted((num(*p), num(*q))))
        tag(ax, *where[key], RATIO[key])
    tag(ax, 2.5, 2.52, "8 × 9 = 72 = 2 × 36")
    head(ax, "Triangular and square",
         "the only consecutive pairs: (1, 2), (2, 3), (3, 4), (8, 9);\n"
         "the corner 72 = 8 × 9 is the cell (3, 2); 36 is half of it")

    # 2. the -5 cycle on an anti-diagonal --------------------------------------------------
    ax = axes[0, 1]
    hi = {p: (BLUE, BLUE_T) for p in ANTI}
    base(ax, hi, show_x=False, show_y=False)
    # the rectangle 4 x 9 = 36 (exponent vectors (2,0) + (0,2) = (2,2))
    ax.plot([2, 2, 0], [0, 2, 2], color=BLUE_T, lw=8, zorder=1.5, solid_capstyle="round",
            solid_joinstyle="round")
    for p, q in zip(ANTI, ANTI[1:]):
        ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=24, lw=3.6, color=BLUE,
                                     shrinkA=17, shrinkB=17, zorder=3))
    tag(ax, 2.0, 2.52, "4 × 9 = 6² = 36")
    ang = math.degrees(math.atan(SLOPE))
    ax.text(3.58, SLOPE * 3.58 + 0.21, r"$2^a = 3^b$", rotation=ang, rotation_mode="anchor",
            ha="center", va="center", fontsize=FS_TAG + 1, color=INK2, zorder=6)
    head(ax, "The cycle −5, −7, −10",
         "in v = n + 1 it walks −4 → −6 → −9 (each step × 3/2),\n"
         "one anti-diagonal; its ends multiply to 36")

    # 3. the point (2,2): Pierpont points and the 3 x 3 block ------------------------------
    ax = axes[1, 0]
    hi = {p: (ORANGE, ORANGE_T) for p in PIERPONT}
    base(ax, hi, show_x=True, show_y=True)
    ax.add_patch(Rectangle((-0.40, -0.40), 2.80, 2.80, facecolor=ORANGE_T, alpha=0.40,
                           edgecolor="none", zorder=0.5))
    spot = {(1, 1): (1.5, 1.5), (1, 2): (0.62, 2.52), (2, 2): (2.5, 2.52)}
    for p, pr in zip(PIERPONT, PRIMES):
        tag(ax, *spot[p], f"{num(*p)} + 1 = {pr}")
    head(ax, "Eight solutions, and the 3 × 3 block",
         "the primes 7, 19, 37 are one more than 6, 18, 36;\n"
         "shaded: the divisors of 36, which have 36 divisors in all")

    # 4. the modulus 5 --------------------------------------------------------------------
    ax = axes[1, 1]
    hi = {p: (AQUA, AQUA_T) for p in ((1, 0), (0, 1), (2, 0), (0, 2))}
    base(ax, hi, show_x=True, show_y=False)
    link(ax, (1, 0), (0, 1), AQUA)
    link(ax, (2, 0), (0, 2), AQUA)
    tag(ax, 0.5, 0.5, "3 + 2 = 5")
    tag(ax, 0.5, 1.5, "9 − 4 = 5")
    head(ax, "cos 36° is half the golden ratio",
         "the pentagon is the modulus 5 = 3 + 2 = 9 − 4;\n"
         "the number 36 plays no part")

    fig.text(left / W, 1 - 0.20 / H, r"Four facts about 36, on the lattice of numbers $2^a\,3^b$",
             fontsize=18, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(left / W, 1 - 0.58 / H, "Each dot is the number $2^a 3^b$; 36 is the point (2, 2). "
             "The grey line is $2^a = 3^b$, where halvings and triplings balance.",
             fontsize=12, color=INK2, ha="left", va="top")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=170, facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {OUT}  ({W:.1f} x {H:.2f} in)")


if __name__ == "__main__":
    main()
