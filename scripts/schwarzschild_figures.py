"""SCRUM-65: figures for the vault, drawn from the JSON that the experiments write.

Run:  python -X utf8 scripts/schwarzschild_figures.py
Reads research/information-schwarzschild-radius/results/*.json
Writes research/information-schwarzschild-radius/figures/*.png

Colours: an ordinal blue ramp for bit sizes, and categorical slots 1 to 3 otherwise.
Both were checked with the dataviz skill's validate_palette.js against the surface.
"""

import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FixedFormatter, FixedLocator, NullLocator  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "research" / "information-schwarzschild-radius"
RESULTS = VAULT / "results"
FIGURES = VAULT / "figures"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
SECONDARY = "#52514e"
GRID = "#e7e6e2"
RAMP = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]    # ordinal, light to dark
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"


def load(name):
    return json.loads((RESULTS / f"{name}.json").read_text(encoding="utf-8"))


def style():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "font.size": 11, "text.color": INK, "axes.labelcolor": SECONDARY,
        "axes.edgecolor": GRID, "axes.linewidth": 1, "axes.grid": True,
        "grid.color": GRID, "grid.linewidth": 1, "xtick.color": SECONDARY,
        "ytick.color": SECONDARY, "xtick.major.size": 0, "ytick.major.size": 0,
        "xtick.minor.size": 0, "ytick.minor.size": 0, "lines.linewidth": 2,
        "legend.frameon": False, "legend.labelcolor": SECONDARY,
        "axes.titlelocation": "left", "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
    })


def title(axis, headline, detail):
    axis.set_title(headline, pad=26)
    axis.text(0, 1.02, detail, transform=axis.transAxes, color=SECONDARY, fontsize=10)


def finish(figure, name):
    FIGURES.mkdir(parents=True, exist_ok=True)
    figure.savefig(FIGURES / f"{name}.png", dpi=160, bbox_inches="tight")
    plt.close(figure)
    print(f"  wrote figures/{name}.png")


def survival_figure():
    scan = load("e4_family_scan")[0]
    constant = scan["lundberg_constant"]
    figure, axis = plt.subplots(figsize=(8.2, 4.8))
    wanted = (14, 18, 22, 26)
    for colour, bits in zip(RAMP, wanted):
        block = next(b for b in scan["blocks"] if b["bits"] == bits)
        total = 2 ** (bits - 1)
        rows = [(h, c / total) for h, c in block["survival"] if c > 0]
        axis.plot([r[0] for r in rows], [r[1] for r in rows], color=colour, label=f"{bits}-bit n")
        axis.annotate(f"{bits} bits", (rows[-1][0], rows[-1][1]), xytext=(-2, -15),
                      textcoords="offset points", color=SECONDARY, fontsize=9, ha="center")
    lifts = [0.5 + i * 0.5 for i in range(56)]
    axis.plot(lifts, [constant * 2.0 ** -h for h in lifts], color=SECONDARY, linewidth=1.5,
              linestyle=(0, (4, 3)), label=f"Haar law {constant:.2f} x 2^-M")
    axis.set_yscale("log", base=2)
    axis.set_ylim(2.0 ** -27, 1.3)
    axis.set_xlim(0, 28.5)
    axis.set_xlabel("lift M = log2(peak / n), bits")
    axis.set_ylabel("share of n with lift at least M")
    axis.legend(loc="lower left")
    title(axis, "Integers obey the Haar lift law until their bits run out",
          "Classic map, every n of each bit size. These four curves end 2 to 5 bits short of M = B.")
    finish(figure, "survival")


def axis_ticks(low):
    return (0.1, 0.25, 0.5, 1, 2, 4) if low < 1 else (1.25, 1.5, 2, 3, 5, 10)


def family_figure():
    rows = load("e4_family_scan")
    figure, (left, right) = plt.subplots(1, 2, figsize=(10.4, 4.7))
    theta = [r["theta"] for r in rows]
    slope = [r["blocks"][-1]["slope"] for r in rows]
    reach = [r["reach_predicted"] for r in rows]
    measured = [r["blocks"][-1]["max_reach"] for r in rows]
    for axis, x, y, low, high in ((left, theta, slope, 0.07, 6), (right, reach, measured, 1.1, 14)):
        axis.plot([low, high], [low, high], color=SECONDARY, linewidth=1.5, linestyle=(0, (4, 3)))
        axis.scatter(x, y, s=62, color=BLUE, edgecolors=SURFACE, linewidths=2, zorder=3)
        axis.set_xscale("log")
        axis.set_yscale("log")
        axis.set_xlim(low, high)
        axis.set_ylim(low, high)
        for axis_line, ticks in ((axis.xaxis, axis_ticks(low)), (axis.yaxis, axis_ticks(low))):
            axis_line.set_major_locator(FixedLocator(ticks))
            axis_line.set_major_formatter(FixedFormatter([f"{t:g}" for t in ticks]))
            axis_line.set_minor_locator(NullLocator())
    miss = len(rows) - 1
    left.annotate("(1,5,5)/3, 17 bits: slope misses", (theta[miss], slope[miss]), xytext=(10, 4),
                  textcoords="offset points", color=SECONDARY, fontsize=9)
    left.set_xlabel("theta, the exact Cramer root")
    left.set_ylabel("fitted slope of -log2 survival")
    right.set_xlabel("predicted reach 1 + 1 / theta")
    right.set_ylabel("largest log(peak) / log(n) in the top block")
    title(left, "Lift cost", "Twelve maps. The dashed line is equality.")
    title(right, "Reach", "Finite size pulls most maps below the line.")
    figure.tight_layout()
    finish(figure, "family")


def capture_figure():
    data = load("e11_capture_law")
    rows = data["maps"]
    cross_section = data["cross_section"]
    figure, axis = plt.subplots(figsize=(8.2, 4.4))
    axis.axhline(cross_section, color=SECONDARY, linewidth=1.5, linestyle=(0, (4, 3)))
    axis.scatter([r["a"] for r in rows[1:]], [r["ratio"] for r in rows[1:]], s=30, color=BLUE,
                 edgecolors=SURFACE, linewidths=1, zorder=3)
    axis.scatter([1], [rows[0]["ratio"]], s=62, color=ORANGE, edgecolors=SURFACE, linewidths=2, zorder=4)
    axis.annotate("a = 1: only n = 1 found", (1, rows[0]["ratio"]), xytext=(10, -3),
                  textcoords="offset points", color=SECONDARY, fontsize=9)
    axis.text(0.8, cross_section + 0.05, f"Sigma = {cross_section:.4f}, the Haar mean horizon",
              color=SECONDARY, fontsize=9)
    axis.set_xscale("log")
    axis.set_xlim(0.7, 2000)
    axis.xaxis.set_major_locator(FixedLocator((1, 10, 100, 1000)))
    axis.xaxis.set_major_formatter(FixedFormatter(("1", "10", "100", "1000")))
    axis.xaxis.set_minor_locator(NullLocator())
    axis.set_ylim(0.8, 3.8)
    axis.set_xlabel("mass a in 3x + a (odd)")
    axis.set_ylabel("captured integers / a")
    title(axis, "Captured integers grow linearly with the mass",
          f"Integers on or inside the horizon of their first contraction word, for {len(rows)} odd masses.")
    finish(figure, "capture")


def page_figure():
    data = load("e5_page_curve")
    drift = load("e1_rates")[0]["g"]
    figure, axis = plt.subplots(figsize=(8.2, 4.4))
    for colour, bits in zip(RAMP, ("12", "16", "20", "24")):
        curve = data[bits]
        size = int(bits)
        x = [t / size for t in curve["t"]]
        y = [value / size for value in curve["mutual_information"]]
        axis.plot(x, y, color=colour, label=f"B = {bits}")
    x = [i * 0.05 for i in range(101)]
    axis.plot(x, [max(min(v, 1) - drift * v, 0) for v in x], color=SECONDARY, linewidth=1.5,
              linestyle=(0, (4, 3)), label="leading order min(t/B, 1) - g t/B")
    axis.set_xlim(0, 5)
    axis.set_ylim(0, 0.95)
    axis.set_xlabel("steps / bits, t / B")
    axis.set_ylabel("I(value; word) / B")
    axis.legend(loc="upper right")
    title(axis, "What the value and the emitted word share peaks when the digits run out",
          "Exact entropies over one full period. The kink at t = B is pigeonhole.")
    finish(figure, "page_curve")


def mach_figure():
    data = load("e8_phase_sweep")["curve"]
    rows = [r for r in data if r["theta"] is not None]
    figure, axis = plt.subplots(figsize=(8.2, 4.4))
    mach = [r["mach"] for r in rows]
    axis.plot(mach, [r["theta"] for r in rows], color=BLUE, label="exact theta")
    axis.plot(mach, [r["weak"] for r in rows], color=ORANGE, label="weak field 2g / (sigma^2 ln 2)")
    classic = (1 - math.log2(3) / 2) / (math.log2(3) / 2)
    axis.scatter([classic], [1.0], s=62, color=INK, edgecolors=SURFACE, linewidths=2, zorder=4)
    axis.annotate("3x + 1", (classic, 1.0), xytext=(8, -12), textcoords="offset points",
                  color=SECONDARY, fontsize=9)
    axis.set_yscale("log")
    axis.set_xlim(0, 0.95)
    axis.set_xlabel("Mach number g / sigma of a two-branch walk, multiplier q from 4 down to 2")
    axis.set_ylabel("bits of address per bit of lift")
    axis.legend(loc="upper left")
    title(axis, "Lift is free at Mach 0 and impossible at Mach 1",
          "The Gaussian formula agrees as g goes to 0 and fails near the horizon.")
    finish(figure, "mach")


def main():
    style()
    selected = sys.argv[1:] or ["survival", "family", "capture", "page", "mach"]
    drawings = {"survival": survival_figure, "family": family_figure, "capture": capture_figure,
                "page": page_figure, "mach": mach_figure}
    for name in selected:
        drawings[name]()


if __name__ == "__main__":
    main()
