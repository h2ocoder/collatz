"""Fibonacci-word fractals from Collatz-related binary sequences.

Following the Wikipedia Fibonacci-word-fractal turtle recipe:

  For each symbol s_i in a binary sequence (i = 0, 1, 2, ...):
      Draw a unit segment forward.
      If s_i == 0:
          Turn 90° left if i is even, right if i is odd.
      (If s_i == 1: don't turn.)

The shape of the resulting curve is a structural fingerprint of the
sequence's complexity class:

  * Sturmian sequence (Fibonacci word, slope 1/phi): self-similar fractal
    with bounded factor complexity. Wikipedia's reference image.
  * Sturmian sequence (our log_2 3 dropping sign): same complexity class,
    different slope — the natural "Collatz-Fibonacci" fractal.
  * Stopping-Class parity (Part 8 result, full-entropy): the same recipe
    applied to a near-Bernoulli sequence produces a 2D random walk, not
    a fractal — visually demonstrating the dichotomy of Part 8.
  * Single Collatz orbit (e.g. n = 27): a finite, irregular sample of
    the same recipe — what one specific trajectory looks like.

Outputs:
    data/collatz_fibonacci_fractal.png
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collatz.core import collatz_step  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stopping_class_block_entropy import compute_P_parity  # noqa: E402


def fibonacci_word(min_len: int) -> np.ndarray:
    """Standard Fibonacci word via morphism 0 -> 01, 1 -> 0."""
    s = [0]
    while len(s) < min_len:
        out: list[int] = []
        for c in s:
            if c == 0:
                out.extend([0, 1])
            else:
                out.append(0)
        s = out
    return np.array(s[:min_len], dtype=np.int8)


def sturmian_log2_3(N: int) -> np.ndarray:
    """Sturmian cutting sequence of slope log_2(3), mapped to {0, 1}.

    Per Part 4 of the doc: "0" = gap-2 (less common, density 2 - log_2 3),
    "1" = gap-3 (more common, density log_2 3 - 1). So "0" plays the
    role of the Wikipedia turn symbol exactly.
    """
    log2_3 = math.log2(3.0)
    floors = np.floor(np.arange(N + 1) * log2_3)
    return (np.diff(floors).astype(np.int8) - 1).astype(np.int8)


def collatz_parity(n: int, max_steps: int = 100_000) -> np.ndarray:
    """Parity bits of the Collatz orbit of n until reaching 1."""
    seq: list[int] = []
    while n > 1 and len(seq) < max_steps:
        seq.append(n % 2)
        n = collatz_step(n)
    return np.array(seq, dtype=np.int8)


def fibonacci_word_fractal_turtle(
    symbols: np.ndarray, angle_deg: float = 90.0, turn_symbol: int = 0
) -> tuple[np.ndarray, np.ndarray]:
    """Turtle graphics with the Fibonacci-word-fractal recipe."""
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
        if int(s) == turn_symbol:
            if i % 2 == 0:
                heading += angle_rad
            else:
                heading -= angle_rad
    return xs, ys


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data"

    N = 8192

    print("Generating sequences...")
    fib = fibonacci_word(N)
    print(f"  Fibonacci word     length {len(fib):>5}  first 30: {fib[:30].tolist()}")
    stm = sturmian_log2_3(N)
    print(f"  log_2 3 Sturmian   length {len(stm):>5}  first 30: {stm[:30].tolist()}")

    scp = compute_P_parity(N)
    print(f"  Stopping-Class par length {len(scp):>5}  first 30: {scp[:30].tolist()}")

    c27 = collatz_parity(27)
    print(f"  Collatz n=27       length {len(c27):>5}  first 30: {c27[:30].tolist()}")

    print("\nRendering turtle paths...")
    xs_fib, ys_fib = fibonacci_word_fractal_turtle(fib)
    xs_stm, ys_stm = fibonacci_word_fractal_turtle(stm)
    xs_scp, ys_scp = fibonacci_word_fractal_turtle(scp)
    xs_c27, ys_c27 = fibonacci_word_fractal_turtle(c27)

    fig, axes = plt.subplots(2, 2, figsize=(14, 14))

    panels = [
        (axes[0, 0], xs_fib, ys_fib, "#1f77b4",
         "Fibonacci word fractal",
         fr"slope $1/\varphi$, {N} symbols (reference)"),
        (axes[0, 1], xs_stm, ys_stm, "#2ca02c",
         r"Sturmian sign of $\log_2 3$",
         fr"Collatz dropping rule, {N} symbols"),
        (axes[1, 0], xs_scp, ys_scp, "#d62728",
         r"Stopping-Class parity $P_o\,\mathrm{mod}\,2$",
         fr"{N} symbols (Part 8 full-entropy sequence)"),
        (axes[1, 1], xs_c27, ys_c27, "#9467bd",
         r"Collatz orbit of $n = 27$",
         fr"parity sequence, {len(c27)} symbols"),
    ]

    for ax, xs, ys, color, title, subtitle in panels:
        ax.plot(xs, ys, color=color, lw=0.6, solid_capstyle="round")
        # Mark the starting point
        ax.scatter([xs[0]], [ys[0]], c=color, s=30, zorder=3, edgecolor="black",
                   linewidth=0.5)
        ax.scatter([xs[-1]], [ys[-1]], c=color, s=30, zorder=3, marker="s",
                   edgecolor="black", linewidth=0.5)
        ax.set_aspect("equal")
        ax.set_title(f"{title}\n{subtitle}", fontsize=11)
        ax.axis("off")

    fig.suptitle("Fibonacci-word fractals from Collatz-related sequences",
                 fontsize=14, y=0.985)
    fig.tight_layout(rect=(0, 0, 1, 0.96))

    out_png = out_dir / "collatz_fibonacci_fractal.png"
    fig.savefig(out_png, dpi=140, bbox_inches="tight", facecolor="white")
    print(f"\nSaved {out_png}")


if __name__ == "__main__":
    main()
