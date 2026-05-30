"""Fibonacci-word fractal variants — angle scan and dragon-curve recipe.

Experiment 1: Wikipedia recipe at four turn angles (60°, 72°, 90°, 120°).
    The original 90° version gave a regular stripe for log_2 3 because the
    Wikipedia turtle is custom-fit to the Fibonacci morphism 0 -> 01, 1 -> 0.
    Different angles change the lattice geometry and may expose richer
    structure for log_2 3.

Experiment 2: dragon-curve recipe — every symbol triggers a turn (left on
    "0", right on "1"), no parity alternation. For binary Sturmian words
    this generally produces a strongly-directional self-similar curve;
    for full-entropy sequences it produces a Brownian-style walk on a
    square lattice (Heighway-dragon visual cousin).

Outputs:
    data/collatz_fractal_angles.png
    data/collatz_fractal_dragon.png
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collatz_fibonacci_fractal import (  # noqa: E402
    collatz_parity,
    fibonacci_word,
    fibonacci_word_fractal_turtle,
    sturmian_log2_3,
)
from stopping_class_block_entropy import compute_P_parity  # noqa: E402


def dragon_turtle(symbols: np.ndarray, angle_deg: float = 90.0
                  ) -> tuple[np.ndarray, np.ndarray]:
    """Forward 1 unit each step, then turn: left on '0', right on '1'."""
    L = len(symbols)
    xs = np.zeros(L + 1, dtype=np.float64)
    ys = np.zeros(L + 1, dtype=np.float64)
    x = 0.0
    y = 0.0
    heading = 0.0
    angle_rad = math.radians(angle_deg)
    for i, s in enumerate(symbols):
        x += math.cos(heading)
        y += math.sin(heading)
        xs[i + 1] = x
        ys[i + 1] = y
        if int(s) == 0:
            heading += angle_rad
        else:
            heading -= angle_rad
    return xs, ys


def render_panel(ax, xs, ys, color, title, lw=0.5):
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round")
    ax.scatter([xs[0]], [ys[0]], c=color, s=22, zorder=3,
               edgecolor="black", linewidth=0.4)
    ax.scatter([xs[-1]], [ys[-1]], c=color, s=22, zorder=3, marker="s",
               edgecolor="black", linewidth=0.4)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=10)
    ax.axis("off")


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data"
    N = 8192

    print("Generating sequences...")
    fib = fibonacci_word(N)
    stm = sturmian_log2_3(N)
    scp = compute_P_parity(N)
    c27 = collatz_parity(27)

    # ---------- Experiment 1: angle scan of Wikipedia recipe ----------
    angles = [60.0, 72.0, 90.0, 120.0]
    fig, axes = plt.subplots(2, len(angles), figsize=(4.4 * len(angles), 9))

    print("\nExperiment 1 — Wikipedia recipe at angles 60°/72°/90°/120°...")
    for col, angle in enumerate(angles):
        xs, ys = fibonacci_word_fractal_turtle(fib, angle_deg=angle)
        render_panel(axes[0, col], xs, ys, "#1f77b4",
                     fr"Fibonacci word — {angle:.0f}°")
        xs, ys = fibonacci_word_fractal_turtle(stm, angle_deg=angle)
        render_panel(axes[1, col], xs, ys, "#2ca02c",
                     fr"$\log_2 3$ Sturmian — {angle:.0f}°")

    fig.suptitle("Experiment 1 — Wikipedia turtle recipe across turn angles "
                 f"(top: Fibonacci ref / bottom: Collatz $\\log_2 3$ sign — "
                 f"{N} symbols each)", fontsize=12, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out1 = out_dir / "collatz_fractal_angles.png"
    fig.savefig(out1, dpi=130, bbox_inches="tight", facecolor="white")
    print(f"Saved {out1}")

    # ---------- Experiment 2: dragon-curve recipe ----------
    print("\nExperiment 2 — Dragon-curve recipe (left on 0, right on 1) at 90°...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 14))
    panels = [
        (fib,  axes[0, 0], "#1f77b4", "Fibonacci word",
         fr"slope $1/\varphi$, {N} symbols"),
        (stm,  axes[0, 1], "#2ca02c", r"Sturmian sign of $\log_2 3$",
         fr"Collatz dropping rule, {N} symbols"),
        (scp,  axes[1, 0], "#d62728", r"Stopping-Class parity $P_o\,\mathrm{mod}\,2$",
         fr"{N} symbols (full-entropy)"),
        (c27,  axes[1, 1], "#9467bd", r"Collatz orbit of $n = 27$",
         fr"parity sequence, {len(c27)} symbols"),
    ]
    for seq, ax, color, name, sub in panels:
        xs, ys = dragon_turtle(seq, angle_deg=90.0)
        render_panel(ax, xs, ys, color, f"{name}\n{sub}", lw=0.5)

    fig.suptitle("Experiment 2 — Dragon-curve recipe (turn left on '0', "
                 "right on '1', 90°)", fontsize=13, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out2 = out_dir / "collatz_fractal_dragon.png"
    fig.savefig(out2, dpi=140, bbox_inches="tight", facecolor="white")
    print(f"Saved {out2}")


if __name__ == "__main__":
    main()
