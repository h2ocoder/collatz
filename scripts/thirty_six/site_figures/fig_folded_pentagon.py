"""Site figure for site/explore/folded-pentagon.md: modulo 5 the 3x+1 map folds onto a pentagon walk.

Adapted from scripts/thirty_six/golden_kernel/fig_pentagon.py for the width of the site's text column:
narrower canvas, larger type, shorter captions, and a title worded as Theorem A states it (a quotient
of the residue chain, not an isomorphism).  Writes site/public/data/collatz_folded_pentagon.png.

Panel 1: Z/5 on the additive pentagon with the two branches  e: x -> x/2 = 3x  and  o: x -> (3x+1)/2 = 3 - x.
Panel 2: the same five residues placed by their role (apex -1/4; near pair +-1/2; far pair 0, -1).
Panel 3: the regular pentagon: cos 72 = 1/(2 phi) and cos 36 = phi/2 as the two 'mean of the neighbours' ratios.

Colour carries the branch (two hues, the pair validated in the original script with the dataviz skill's
validate_palette.js); the residues' roles are given by direct labels, never by colour alone.

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 fig_folded_pentagon.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch  # noqa: E402

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
HAIR = "#c3c2b7"
C_E = "#2a78d6"   # even branch  (categorical slot 1)
C_O = "#eb6834"   # odd branch   (categorical slot 2)

FS = 13.0         # smallest type on the figure: about 10 px when the PNG is shown 688 px wide
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": FS, "text.color": INK, "axes.edgecolor": HAIR})


def ring(order: list[int], radius: float = 1.0) -> dict[int, np.ndarray]:
    """positions of the residues in the given cyclic order, first one at the top, going counter-clockwise."""
    return {r: radius * np.array([np.cos(np.pi / 2 + 2 * np.pi * i / 5), np.sin(np.pi / 2 + 2 * np.pi * i / 5)]) for i, r in enumerate(order)}


def node(ax, xy, label, sub=None, off=(0.0, 0.0), ha="center"):
    ax.add_patch(Circle(xy, 0.16, facecolor=SURFACE, edgecolor=INK2, linewidth=1.5, zorder=5))
    ax.text(xy[0], xy[1], str(label), ha="center", va="center", fontsize=15, fontweight="bold", zorder=6)
    if sub:
        ax.text(xy[0] + off[0], xy[1] + off[1], sub, ha=ha, va="center", fontsize=FS, color=INK2, zorder=6, linespacing=1.15)


def arrow(ax, a, b, color, rad=0.0, both=False, lw=2.2, shrink=17):
    style = "<|-|>" if both else "-|>"
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=15, linewidth=lw, color=color,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=shrink, shrinkB=shrink, zorder=4))


def loop(ax, xy, color, direction=None):
    d = xy / np.linalg.norm(xy) if direction is None else np.array(direction, dtype=float)
    c = xy + 0.29 * d
    t = np.linspace(0, 2 * np.pi, 80)
    ax.plot(c[0] + 0.16 * np.cos(t), c[1] + 0.16 * np.sin(t), color=color, linewidth=2.2, zorder=3)
    tip = c + 0.16 * np.array([np.cos(0.3), np.sin(0.3)])
    tail = c + 0.16 * np.array([np.cos(0.0), np.sin(0.0)])
    ax.add_patch(FancyArrowPatch(tail, tip, arrowstyle="-|>", mutation_scale=13, linewidth=0, color=color, zorder=4))


def polygon(ax, pos, order, **kw):
    pts = np.array([pos[r] for r in order] + [pos[order[0]]])
    ax.plot(pts[:, 0], pts[:, 1], **kw)


def draw_branches(ax, pos, rad_e, rad_o, loop_dir=None):
    loop_dir = loop_dir or {}
    e = {x: 3 * x % 5 for x in range(5)}
    o = {x: (3 - x) % 5 for x in range(5)}
    for x in range(5):
        if e[x] == x:
            loop(ax, pos[x], C_E, loop_dir.get(x))
        else:
            arrow(ax, pos[x], pos[e[x]], C_E, rad=rad_e.get(x, 0.0))
    done = set()
    for x in range(5):
        if o[x] == x:
            loop(ax, pos[x], C_O, loop_dir.get(x))
        elif x not in done:
            arrow(ax, pos[x], pos[o[x]], C_O, rad=rad_o.get(x, 0.0), both=True)
            done |= {x, o[x]}


fig, axes = plt.subplots(1, 3, figsize=(12.0, 6.1), facecolor=SURFACE)
for ax in axes:
    ax.set_facecolor(SURFACE)
    ax.set_aspect("equal")
    ax.set_xlim(-1.75, 1.75)
    ax.set_ylim(-2.45, 1.62)
    ax.axis("off")
CAP_Y = -1.62
CAP = dict(color=INK2, fontsize=FS, va="top", linespacing=1.25)

# ------------------------------------------------------------------ panel 1: additive pentagon
ax = axes[0]
pos = ring([0, 1, 2, 3, 4])
polygon(ax, pos, [0, 1, 2, 3, 4], color=HAIR, linewidth=1.0, zorder=1)
draw_branches(ax, pos, rad_e={2: 0.3}, rad_o={1: 0.3})
for r in range(5):
    node(ax, pos[r], r)
ax.set_title("Z/5 in its additive order", fontsize=14.5, color=INK, pad=4, loc="left")
ax.text(-1.7, CAP_Y, "Blue:  x → x/2 = 3x, of order 4,\n"
                     "fixes 0.  Orange:  x → (3x+1)/2\n"
                     "= 3 − x, a reflection that fixes\n"
                     "4 = −1.  Both send 2 to 1.", **CAP)

# ------------------------------------------------------------------ panel 2: residues by role
ax = axes[1]
order2 = [1, 2, 4, 0, 3]
pos2 = ring(order2)
polygon(ax, pos2, order2, color=HAIR, linewidth=1.0, zorder=1)
draw_branches(ax, pos2, rad_e={1: 0.22, 4: 0.22, 2: 0.22}, rad_o={0: 0.22, 1: 0.22}, loop_dir={0: (0, -1), 4: (0, -1)})
subs = {1: ("apex  −1/4", (0.0, 0.34), "center"), 2: ("near\n−1/2", (-0.25, 0.0), "right"), 3: ("near\n+1/2", (0.25, 0.0), "left"),
        0: ("far\n0", (0.27, -0.02), "left"), 4: ("far\n−1", (-0.27, -0.02), "right")}
for r in range(5):
    node(ax, pos2[r], r, subs[r][0], off=subs[r][1], ha=subs[r][2])
ax.set_title("The same residues placed by role", fontsize=14.5, color=INK, pad=4, loc="left")
ax.text(-1.7, CAP_Y, "Mass spread evenly on a cell moves\n"
                     "as on a pentagon folded in half:\n"
                     "apex → near;  near → ½ apex + ½ far;\n"
                     "far → ½ near + ½ far (the two loops).", **CAP)

# ------------------------------------------------------------------ panel 3: geometry
ax = axes[2]
CEN = np.array([-0.75, 0.0])
RAD = 0.95
V = [CEN + RAD * np.array([np.cos(np.pi / 2 + 2 * np.pi * i / 5), np.sin(np.pi / 2 + 2 * np.pi * i / 5)]) for i in range(5)]
t = np.linspace(0, 2 * np.pi, 200)
ax.plot(CEN[0] + RAD * np.cos(t), CEN[1] + RAD * np.sin(t), color=HAIR, linewidth=0.9, zorder=1)
pts = np.array(V + [V[0]])
ax.plot(pts[:, 0], pts[:, 1], color=INK2, linewidth=1.7, zorder=2)
m1 = (V[1] + V[4]) / 2          # midpoint of the two neighbours of the start vertex: cos 72 from the centre
m2 = (V[2] + V[3]) / 2          # midpoint of the opposite side (the neighbours in star order): cos 36 from the centre
ax.plot([V[1][0], V[4][0]], [V[1][1], V[4][1]], color=MUTED, linewidth=1.2, linestyle=(0, (4, 3)), zorder=2)
ax.plot([m2[0], V[0][0]], [m2[1], V[0][1]], color=INK, linewidth=1.7, zorder=3)
for q in (V[0], m1, m2, CEN):
    ax.add_patch(Circle(q, 0.04, facecolor=INK, edgecolor=SURFACE, linewidth=1.2, zorder=6))
TX = 0.36
notes = ((V[0], "start vertex\n(circumradius 1)"),
         (m1, "mean of its two\nneighbours:\ncos 72° = 0.309"),
         (m2, "mean of the\nopposite side:\ncos 36° = φ/2\n= 0.809"))
for q, txt in notes:
    ax.plot([q[0] + 0.06, TX - 0.05], [q[1], q[1]], color=HAIR, linewidth=0.8, zorder=1)
    ax.text(TX, q[1], txt, fontsize=FS, color=INK, va="center", ha="left", linespacing=1.15)
ax.set_title("Where φ/2 comes from", fontsize=14.5, color=INK, pad=4, loc="left")
ax.text(-1.7, CAP_Y, "A pentagon walk averages the two\n"
                     "neighbours: eigenvalues 1, cos 72°\n"
                     "and cos 144° = −cos 36°.  The start\n"
                     "is forgotten at rate φ/2 per step.", **CAP)

# legend (two series: always present) and title
handles = [plt.Line2D([0], [0], color=C_E, linewidth=2.4, label="even branch  e : x → x/2"),
           plt.Line2D([0], [0], color=C_O, linewidth=2.4, label="odd branch  o : x → (3x+1)/2"),
           plt.Line2D([0], [0], color=HAIR, linewidth=1.4, label="pentagon sides (for reference)")]
fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.012, 0.895), frameon=False, fontsize=FS, labelcolor=INK2, ncol=3,
           columnspacing=2.2, handlelength=2.2)
fig.suptitle("Modulo 5 the 3x+1 map folds onto a pentagon walk", x=0.02, y=0.975, ha="left", fontsize=16.5, fontweight="bold", color=INK)
fig.text(0.02, 0.905, "Shortcut map T(n) = n/2 or (3n+1)/2.  K₅ f(x) = ½ f(x/2) + ½ f((3x+1)/2) on Z/5 has eigenvalues 1, ½, 0, cos 72°, −cos 36°.",
         ha="left", fontsize=FS, color=INK2)
fig.subplots_adjust(left=0.01, right=0.99, top=0.80, bottom=0.01, wspace=0.02)
out = Path(__file__).resolve().parents[3] / "site" / "public" / "data" / "collatz_folded_pentagon.png"
fig.savefig(out, dpi=180, facecolor=SURFACE)
print("wrote", out)
