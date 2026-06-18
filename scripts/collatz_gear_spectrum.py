# scripts/collatz_gear_spectrum.py
"""Fourier (gear) spectrum of mod-q divisibility along Collatz orbits.

Building on the gear picture (scripts/collatz_prime_gears.py): an odd prime q
"engages" with the orbit whenever a 3x+1 step lands on a multiple of q, then
persists through the following run of /2 steps and is ejected at the next odd
step. The indicator signal

    s_k = 1 if q | x_k else 0

is therefore a train of bursts. This script asks the spectral question: are the
bursts *periodic* (a real gear resonance) or *white* (Collatz mixing, no gear)?

Method: ensemble-averaged periodogram. For many seeds we take the full orbit to
1 (the trailing powers-of-2 ramp contributes only zeros for odd q, so no
artifact), build s_k, remove its mean, take |rFFT|^2, and average the spectra
over the ensemble on a common normalized-frequency grid. The null is the same
pipeline with each orbit's s_k randomly permuted -- identical burst density,
time structure destroyed -> a flat white floor. Peaks above the null band are
gear resonances; flatness means the transient mixes.

Output:
    data/collatz_gear_spectrum.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from collatz.core import orbit  # noqa: E402

PRIMES = (5, 7, 11, 13)
SEED_LO, SEED_HI = 5001, 25001          # odd seeds in [lo, hi)
GRID = np.linspace(0.0, 0.5, 256)       # normalized frequency grid
MIN_LEN = 24                            # skip very short orbits (poor resolution)
OUT = Path(__file__).resolve().parent.parent / "data" / "collatz_gear_spectrum.png"
RNG = np.random.default_rng(20260618)   # fixed seed: reproducible null


def periodogram_on_grid(signal: np.ndarray) -> np.ndarray:
    """Mean-removed periodogram of `signal`, interpolated onto GRID."""
    s = signal - signal.mean()
    if not np.any(s):
        return np.zeros_like(GRID)
    power = np.abs(np.fft.rfft(s)) ** 2 / len(s)
    freq = np.fft.rfftfreq(len(s))
    return np.interp(GRID, freq, power)


def ensemble_spectra(q: int):
    """Average observed and shuffled-null periodograms of [q | x_k] over seeds."""
    obs_acc = np.zeros_like(GRID)
    null_acc = np.zeros_like(GRID)
    count = 0
    for seed in range(SEED_LO, SEED_HI, 2):
        seq = orbit(seed)
        if len(seq) < MIN_LEN:
            continue
        s = (np.array(seq) % q == 0).astype(float)
        if not np.any(s):
            continue
        obs_acc += periodogram_on_grid(s)
        null_acc += periodogram_on_grid(RNG.permutation(s))
        count += 1
    return obs_acc / count, null_acc / count, count


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharex=True)
    for ax, q in zip(axes.ravel(), PRIMES):
        obs, null, count = ensemble_spectra(q)
        ax.plot(GRID, obs, color="crimson", lw=1.6, label="observed [q | x_k]")
        ax.plot(GRID, null, color="0.5", lw=1.4, ls="--",
                label="shuffled null (white)")
        ax.fill_between(GRID, null * 0.85, null * 1.15, color="0.5", alpha=0.18)
        ratio = obs.max() / null.mean() if null.mean() > 0 else float("nan")
        ax.set_title(f"q = {q}   (peak/null = {ratio:.2f},  N={count} orbits)")
        ax.set_ylabel("avg power")
        ax.legend(fontsize=8, loc="upper right")
        ax.set_xlim(0, 0.5)
    for ax in axes[1]:
        ax.set_xlabel("normalized frequency  (cycles / step)")
    fig.suptitle(
        "Gear spectrum: is mod-q divisibility along Collatz orbits periodic or white?",
        fontsize=13.5, y=0.98,
    )
    plt.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(OUT, dpi=140)
    plt.close(fig)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
