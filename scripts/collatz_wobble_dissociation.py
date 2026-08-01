# scripts/collatz_wobble_dissociation.py
"""The +1 wobble: geometrically negligible exactly where it is arithmetically maximal.

At every odd step m -> 3m+1 the "+1" acts in two channels at once:

  * Geometric (quasicrystal phase): it shifts log_6 x by
        dtheta = log_6(1 + 1/(3m)),
    which -> 0 as m grows -- vanishing at the orbit's peak.
  * Arithmetic (factor gears): 3m and 3m+1 are coprime, and every odd prime
    dividing m satisfies 3m+1 ≡ 1 (mod p), so the step EJECTS every odd gear of
    m and slots in the (unrelated) gears of 3m+1. This ejection is TOTAL at
    every size -- a theorem, verified here as a sanity check.

So the same +1 fades geometrically yet stays arithmetically total. The only
thing the two channels share is size m: the geometric wobble is exactly 1/(3m),
while the number of injected gears omega(3m+1) grows like loglog(3m+1)
(Erdos-Kac). This script visualizes that dissociation and tests whether the
injected factors are otherwise statistically generic.

Outputs:
    data/collatz_wobble_dissociation.png
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sympy import primefactors  # noqa: E402

from collatz.core import orbit  # noqa: E402

LOG6 = math.log(6)
SEED_HI = 4000                          # collect odd orbit values from seeds < this
SYNTHETIC = [10**7, 10**8, 10**9, 10**10, 10**11, 10**12]  # extend the size axis
OUT = Path(__file__).resolve().parent.parent / "data" / "collatz_wobble_dissociation.png"


def collect_odd_values(seed_hi: int) -> list[int]:
    """Distinct odd values m >= 3 appearing in orbits of odd seeds < seed_hi."""
    seen = set()
    for seed in range(3, seed_hi, 2):
        for x in orbit(seed):
            if x >= 3 and x % 2 == 1:
                seen.add(x)
    return sorted(seen)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ms = collect_odd_values(SEED_HI) + SYNTHETIC
    logm = np.array([math.log10(m) for m in ms])

    wobble = np.array([math.log1p(1.0 / (3 * m)) / LOG6 for m in ms])  # geometric
    eject_overlap = []      # |odd primes(3m+1) ∩ primes(m)|  -- must be 0 (theorem)
    omega = []              # distinct prime factors of 3m+1 (injected gears + the 2)
    for m in ms:
        fm = set(primefactors(m))
        f1 = set(primefactors(3 * m + 1))
        eject_overlap.append(len(fm & (f1 - {2})))
        omega.append(len(f1))
    eject_overlap = np.array(eject_overlap)
    omega = np.array(omega, dtype=float)

    total_ejection = int((eject_overlap == 0).all())
    print(f"odd values sampled: {len(ms)}  (max {max(ms):.3g})")
    print(f"ejection total at every step (overlap always 0): {bool(total_ejection)}; "
          f"max overlap seen = {eject_overlap.max()}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.6))

    # ---- Panel 1: the dissociation -------------------------------------
    order = np.argsort(logm)
    ax1.semilogy(logm[order], wobble[order], color="navy", lw=1.8,
                 label=r"geometric wobble $\log_6(1+\frac{1}{3m})$")
    ax1.set_xlabel(r"$\log_{10} m$  (orbit value size)")
    ax1.set_ylabel("geometric phase shift per step", color="navy")
    ax1.tick_params(axis="y", labelcolor="navy")
    axr = ax1.twinx()
    axr.plot(logm[order], 1.0 - eject_overlap[order], color="crimson", lw=1.6,
             label="arithmetic ejection completeness")
    axr.set_ylim(-0.05, 1.15)
    axr.set_ylabel("fraction of odd gears ejected", color="crimson")
    axr.tick_params(axis="y", labelcolor="crimson")
    ax1.set_title("Same +1: geometric effect $\\to 0$, arithmetic ejection stays total")
    l1, lab1 = ax1.get_legend_handles_labels()
    l2, lab2 = axr.get_legend_handles_labels()
    ax1.legend(l1 + l2, lab1 + lab2, fontsize=8, loc="center left")

    # ---- Panel 2: are the injected factors generic? (Erdos-Kac) --------
    ax2.scatter(logm, omega, s=5, alpha=0.12, color="seagreen", label=r"$\omega(3m+1)$")
    bins = np.linspace(logm.min(), logm.max(), 20)
    idx = np.digitize(logm, bins)
    bc = [logm[idx == i].mean() for i in range(1, len(bins)) if np.any(idx == i)]
    bm = [omega[idx == i].mean() for i in range(1, len(bins)) if np.any(idx == i)]
    ax2.plot(bc, bm, color="darkgreen", lw=2.2, marker="o", ms=4, label="binned mean")
    xs = np.linspace(logm.min(), logm.max(), 200)
    ek = [math.log(math.log(10 ** x)) for x in xs]   # loglog N = Erdos-Kac mean
    ax2.plot(xs, ek, color="black", ls="--", lw=1.6, label=r"Erdos-Kac $\log\log N$")
    ax2.set_xlabel(r"$\log_{10}(3m+1)$")
    ax2.set_ylabel(r"distinct prime factors $\omega(3m+1)$")
    ax2.set_title("Injected gears are statistically generic (track Erdos-Kac)")
    ax2.legend(fontsize=8, loc="upper left")

    fig.suptitle(
        "The +1 wobble: geometrically negligible where it is arithmetically maximal",
        fontsize=13.5, y=1.0,
    )
    plt.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(OUT, dpi=140)
    plt.close(fig)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
