"""Plot the minimal-avoider function A(n) against reference growth rates."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main(path: str) -> None:
    ns, As = [], []
    for line in Path(path).read_text().splitlines():
        m = re.match(r"\s*(\d+)\s+(\d+)\s", line)
        if m:
            ns.append(int(m.group(1)))
            As.append(int(m.group(2)))
    ns, As = np.array(ns), np.array(As, dtype=float)

    # least-squares slope of log2 A(n) over the tail (n >= 10)
    tail = ns >= 10
    slope, icpt = np.polyfit(ns[tail], np.log2(As[tail]), 1)
    gamma = 2 ** slope

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.semilogy(ns, As, "o-", color="#1f77b4", label="A(n) exact (sieve to 3e7)", ms=4)
    xs = np.array([ns[0], ns[-1]])
    ax.semilogy(xs, (4 / 3) ** xs * As[0] / (4 / 3) ** xs[0], "--", color="gray",
                label="(4/3)^n  — pure weak-preimage chain")
    ax.semilogy(xs, 4.0 ** xs * As[0] / 4.0 ** xs[0], ":", color="gray",
                label="4^n  — trivial-cycle shadow (2 bits/enc)")
    ax.semilogy(xs, 2 ** (slope * xs + icpt), "-", color="#d62728", alpha=0.7,
                label=f"fit gamma = {gamma:.3f}  ({slope:.3f} bits/encounter)")
    ax.set_xlabel("n  (Set$_3$ encounters survived with no strong drop)")
    ax.set_ylabel("A(n) = minimal avoider")
    ax.set_title("Minimal strong-drop avoider A(n): growth rate of the three-bit countdown")
    ax.legend()
    ax.grid(alpha=0.3)
    out = Path(__file__).resolve().parent.parent / "data" / "collatz_three_bit_avoiders.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"gamma = {gamma:.4f} ({slope:.4f} bits/encounter), wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1])
