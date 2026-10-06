"""Figure for Q3.1: the Terras kernel mod 5 as a folded pentagon walk.   Writes fig_pentagon.png.

Panel 1: Z/5 on the additive pentagon with the two branches  e: x -> x/2 = 3x  and  o: x -> (3x+1)/2 = 3 - x.
Panel 2: the same five residues placed by their role (apex -1/4; near pair +-1/2; far pair 0, -1): the branch
         graph is a pentagon except that the far side is replaced by the two fixed-point loops.
Panel 3: the regular pentagon: cos 72 = 1/(2 phi) and cos 36 = phi/2 as the two 'average of the neighbours' ratios.

Colour carries the branch (two hues, validated with the dataviz skill's validate_palette.js: all checks pass);
the residues' roles are given by direct labels, never by colour alone.  Static PNG: no hover layer.

Run:  python -X utf8 fig_pentagon.py
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

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "text.color": INK, "axes.edgecolor": HAIR})


def ring(order: list[int], radius: float = 1.0) -> dict[int, np.ndarray]:
    """positions of the residues in the given cyclic order, first one at the top, going counter-clockwise."""
    return {r: radius * np.array([np.cos(np.pi / 2 + 2 * np.pi * i / 5), np.sin(np.pi / 2 + 2 * np.pi * i / 5)]) for i, r in enumerate(order)}


def node(ax, xy, label, sub=None, off=(0.0, 0.0), ha="center"):
    ax.add_patch(Circle(xy, 0.135, facecolor=SURFACE, edgecolor=INK2, linewidth=1.4, zorder=5))
    ax.text(xy[0], xy[1], str(label), ha="center", va="center", fontsize=13, fontweight="bold", zorder=6)
    if sub:
        ax.text(xy[0] + off[0], xy[1] + off[1], sub, ha=ha, va="center", fontsize=9.5, color=INK2, zorder=6)


def arrow(ax, a, b, color, rad=0.0, both=False, lw=2.0, shrink=15):
    style = "<|-|>" if both else "-|>"
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=14, linewidth=lw, color=color,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=shrink, shrinkB=shrink, zorder=4))


def loop(ax, xy, color, direction=None):
    d = xy / np.linalg.norm(xy) if direction is None else np.array(direction, dtype=float)
    c = xy + 0.25 * d
    t = np.linspace(0, 2 * np.pi, 80)
    ax.plot(c[0] + 0.15 * np.cos(t), c[1] + 0.15 * np.sin(t), color=color, linewidth=2.0, zorder=3)
    tip = c + 0.15 * np.array([np.cos(0.3), np.sin(0.3)])
    tail = c + 0.15 * np.array([np.cos(0.0), np.sin(0.0)])
    ax.add_patch(FancyArrowPatch(tail, tip, arrowstyle="-|>", mutation_scale=12, linewidth=0, color=color, zorder=4))


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


fig, axes = plt.subplots(1, 3, figsize=(15.6, 6.4), facecolor=SURFACE)
for ax in axes:
    ax.set_facecolor(SURFACE)
    ax.set_aspect("equal")
    ax.set_xlim(-1.75, 1.75)
    ax.set_ylim(-1.95, 1.6)
    ax.axis("off")
CAP_Y = -1.42

# ------------------------------------------------------------------ panel 1: additive pentagon
ax = axes[0]
pos = ring([0, 1, 2, 3, 4])
polygon(ax, pos, [0, 1, 2, 3, 4], color=HAIR, linewidth=1.0, zorder=1)
draw_branches(ax, pos, rad_e={2: 0.3}, rad_o={1: 0.3})
for r in range(5):
    node(ax, pos[r], r)
ax.set_title("Z/5 in its additive order", fontsize=12.5, color=INK, pad=6, loc="left")
ax.text(-1.7, CAP_Y, "Even branch  e : x → x/2 = 3x  (order 4, fixes 0; it turns sides\n"
                     "of the pentagon into diagonals).  Odd branch  o : x → (3x+1)/2\n"
                     "= 3 − x  (a reflection, fixes 4 = −1).  Both send 2 to 1.", color=INK2, fontsize=9.6, va="top")

# ------------------------------------------------------------------ panel 2: residues by role
ax = axes[1]
order2 = [1, 2, 4, 0, 3]
pos2 = ring(order2)
polygon(ax, pos2, order2, color=HAIR, linewidth=1.0, zorder=1)
draw_branches(ax, pos2, rad_e={1: 0.22, 4: 0.22, 2: 0.22}, rad_o={0: 0.22, 1: 0.22}, loop_dir={0: (0, -1), 4: (0, -1)})
subs = {1: ("apex:  −1/4", (0.0, 0.3), "center"), 2: ("near pair\n−1/2", (-0.22, 0.0), "right"), 3: ("near pair\n+1/2", (0.22, 0.0), "left"),
        0: ("far pair\n0, fixed by e", (0.26, -0.02), "left"), 4: ("far pair\n−1, fixed by o", (-0.26, -0.02), "right")}
for r in range(5):
    node(ax, pos2[r], r, subs[r][0], off=subs[r][1], ha=subs[r][2])
ax.set_title("The same residues placed by role", fontsize=12.5, color=INK, pad=6, loc="left")
ax.text(-1.7, CAP_Y - 0.12, "Mass moves exactly as on a pentagon:  apex → near pair;\n"
                            "near pair → ½ apex + ½ far pair;  far pair → ½ near + ½ far\n"
                            "(the far side of the pentagon is the two fixed-point loops).", color=INK2, fontsize=9.6, va="top")

# ------------------------------------------------------------------ panel 3: geometry
ax = axes[2]
CEN = np.array([-0.72, 0.0])
RAD = 0.95
V = [CEN + RAD * np.array([np.cos(np.pi / 2 + 2 * np.pi * i / 5), np.sin(np.pi / 2 + 2 * np.pi * i / 5)]) for i in range(5)]
t = np.linspace(0, 2 * np.pi, 200)
ax.plot(CEN[0] + RAD * np.cos(t), CEN[1] + RAD * np.sin(t), color=HAIR, linewidth=0.9, zorder=1)
pts = np.array(V + [V[0]])
ax.plot(pts[:, 0], pts[:, 1], color=INK2, linewidth=1.6, zorder=2)
m1 = (V[1] + V[4]) / 2          # midpoint of the two neighbours of the start vertex: cos 72 from the centre
m2 = (V[2] + V[3]) / 2          # midpoint of the opposite side (the neighbours in star order): cos 36 from the centre
ax.plot([V[1][0], V[4][0]], [V[1][1], V[4][1]], color=MUTED, linewidth=1.2, linestyle=(0, (4, 3)), zorder=2)
ax.plot([m2[0], V[0][0]], [m2[1], V[0][1]], color=INK, linewidth=1.6, zorder=3)
for q in (V[0], m1, m2, CEN):
    ax.add_patch(Circle(q, 0.035, facecolor=INK, edgecolor=SURFACE, linewidth=1.2, zorder=6))
TX = 0.4
notes = ((V[0], "start vertex (circumradius 1)"),
         (m1, "midpoint of its two neighbours:\ncos 72° = 1/(2φ) = 0.3090"),
         (CEN, "centre"),
         (m2, "midpoint of the opposite side\n(its neighbours in star order):\ncos 36° = φ/2 = 0.8090"))
for q, txt in notes:
    ax.plot([q[0] + 0.05, TX - 0.04], [q[1], q[1]], color=HAIR, linewidth=0.8, zorder=1)
    ax.text(TX, q[1], txt, fontsize=9.4, color=INK, va="center", ha="left")
ax.set_title("Where φ/2 comes from", fontsize=12.5, color=INK, pad=6, loc="left")
ax.text(-1.7, CAP_Y, "A pentagon walk replaces a vertex by the average of its two\n"
                     "neighbours: eigenvalues 1, cos 72° and cos 144° = −cos 36°.\n"
                     "So T^k(n) mod 5 forgets its start at rate cos 36° = φ/2 per step.", color=INK2, fontsize=9.6, va="top")

# legend (two series: always present) and title
handles = [plt.Line2D([0], [0], color=C_E, linewidth=2.2, label="even branch  e : x → x/2"),
           plt.Line2D([0], [0], color=C_O, linewidth=2.2, label="odd branch  o : x → (3x+1)/2"),
           plt.Line2D([0], [0], color=HAIR, linewidth=1.2, label="pentagon sides (for reference)")]
fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.985, 0.985), frameon=False, fontsize=10, labelcolor=INK2, ncol=3)
fig.suptitle("3x+1 modulo 5 folds onto a pentagon walk (3 cells)", x=0.02, y=0.975, ha="left", fontsize=15, fontweight="bold", color=INK)
fig.text(0.02, 0.915, "Shortcut map T(n) = n/2 or (3n+1)/2.  Kernel K₅ f(x) = ½ f(x/2) + ½ f((3x+1)/2) on Z/5;  spectrum {1, ½, cos 72°, 0, −cos 36°}.",
         ha="left", fontsize=10.5, color=INK2)
fig.subplots_adjust(left=0.01, right=0.99, top=0.86, bottom=0.02, wspace=0.02)
out = Path(__file__).with_suffix(".png")
fig.savefig(out, dpi=150, facecolor=SURFACE)
print("wrote", out)
