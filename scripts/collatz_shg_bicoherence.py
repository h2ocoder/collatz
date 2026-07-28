# scripts/collatz_shg_bicoherence.py
"""SHG probe: does the Collatz +1 wobble generate second harmonics?

In nonlinear optics, a chi^(2) medium (inversion symmetry broken) converts
light at frequency f into phase-locked light at 2f -- second harmonic
generation. The signal fingerprint is quadratic phase coupling, detected by
bicoherence: b^2(f1, f2) ~ 1 when the phase at f1+f2 is locked to the sum of
the phases at f1 and f2, and ~ 0 for any linear or Gaussian process. Crucially
the power spectrum is blind to this (it discards phase): the gear-spectrum
result "mod-q bursts are white" leaves bicoherence completely open.

Collatz mapping: the odd step T(x) = (3x+1)/2 is affine; the +1 is the
inversion-symmetry breaker of the pure rotation x -> 3x/2 (alpha = log_6 3).
Field under test: the per-step wobble kick w_k = log_6(1 + 1/(3 x_k)), one
per odd orbit value, first L=32 kicks per seed, standardized per window.

Interpretation contract (docs/superpowers/specs/2026-07-27-shg-bicoherence-design.md):
  - diagonal b^2(f, f) above BOTH null bands  => the +1 acts as a chi^(2)
    medium: quadratic phase coupling / harmonic generation along orbits.
  - flat at the null level => the wobble phases mix linearly, consistent
    with the gear-spectrum whiteness result.

Nulls (both 95% bands over R ensembles):
  1. phase-randomized surrogates -- exact same power spectra, all bispectral
     phase relations destroyed by construction.
  2. matched AR(5) -- best linear Gaussian model of the wobble, simulated at
     the same ensemble size.

Startup self-check: the estimator must light up on a synthetic phase-coupled
pair (positive control) and stay at the floor when the 2f phase is unlocked
(negative control); the run aborts if either fails.

Output:
    data/collatz_shg_bicoherence.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from collatz.bispectrum import (  # noqa: E402
    bicoherence,
    fit_ar,
    phase_randomize,
    qpc_ensemble,
    simulate_ar,
    standardize_windows,
    wobble_increments,
)

SEED_LO, SEED_HI = 50001, 150001   # odd seeds in [lo, hi)
L = 32                              # odd steps per window
AR_ORDER = 5
N_NULL = 100                        # null ensembles per falsifier
RNG = np.random.default_rng(20260727)  # fixed seed: reproducible nulls
OUT = Path(__file__).resolve().parent.parent / "data" / "collatz_shg_bicoherence.png"


def self_check() -> None:
    """Positive + negative QPC control; abort the run if the estimator fails."""
    rng = np.random.default_rng(7)
    pos = bicoherence(qpc_ensemble(200, 64, 8, coupled=True, rng=rng))[8, 8]
    neg = bicoherence(qpc_ensemble(200, 64, 8, coupled=False, rng=rng))[8, 8]
    ok = pos > 0.8 and neg < 0.2
    print(f"self-check: coupled b2={pos:.3f} (>0.8), uncoupled b2={neg:.3f} (<0.2)"
          f" -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        sys.exit(1)


def build_ensemble() -> np.ndarray:
    """Standardized (M, L) wobble windows; logs the skipped-seed fraction."""
    windows, skipped, total = [], 0, 0
    for seed in range(SEED_LO, SEED_HI, 2):
        total += 1
        w = wobble_increments(seed)
        if w.size < L:
            skipped += 1
            continue
        windows.append(w[:L])
    print(f"ensemble: {len(windows)} windows of L={L} odd steps "
          f"({skipped}/{total} seeds skipped = {skipped / total:.1%})")
    return standardize_windows(np.array(windows))


def null_band(estimates: np.ndarray) -> np.ndarray:
    """Pointwise 95th percentile across null ensembles (axis 0), NaN-safe."""
    return np.nanpercentile(estimates, 95.0, axis=0)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    self_check()
    win = build_ensemble()
    M = win.shape[0]

    b2_obs = bicoherence(win)
    K = L // 2

    # Null 1: phase-randomized surrogates of the real windows.
    surr = np.array([bicoherence(phase_randomize(win, RNG)) for _ in range(N_NULL)])
    # Null 2: matched AR(AR_ORDER) linear model at the same ensemble size.
    phi, sigma = fit_ar(win, AR_ORDER)
    print(f"AR({AR_ORDER}) fit: phi={np.round(phi, 3)}, sigma={sigma:.3f}")
    ar = np.array([
        bicoherence(standardize_windows(simulate_ar(phi, sigma, M, L, RNG)))
        for _ in range(N_NULL)
    ])
    surr_band, ar_band = null_band(surr), null_band(ar)

    # Console verdict: observed peak vs the surrogate max-statistic distribution.
    tri = ~np.isnan(b2_obs)
    peak = float(np.nanmax(b2_obs))
    f1p, f2p = np.unravel_index(int(np.nanargmax(np.where(tri, b2_obs, -1.0))), b2_obs.shape)
    surr_max = np.nanmax(surr, axis=(1, 2))
    pctile = float(np.mean(peak > surr_max)) * 100.0
    print(f"peak b2 = {peak:.4f} at (f1, f2) = ({f1p}, {f2p}) "
          f"[normalized f = ({f1p / L:.3f}, {f2p / L:.3f})]")
    print(f"peak percentile vs surrogate max-distribution: {pctile:.0f}%")

    diag = np.arange(1, K // 2 + 1)          # (f, f) with 2f <= K
    freqs = diag / L

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))

    ax = axes[0]
    im = ax.imshow(b2_obs.T, origin="lower", cmap="viridis", aspect="equal",
                   extent=(-0.5, K + 0.5, -0.5, K + 0.5))
    ax.plot([1, K // 2], [1, K // 2], color="w", lw=0.8, ls=":")
    ax.set_xlabel("f1 (rFFT bin)")
    ax.set_ylabel("f2 (rFFT bin)")
    ax.set_title(f"bicoherence b$^2$(f1, f2), M={M} windows")
    fig.colorbar(im, ax=ax, shrink=0.85)

    ax = axes[1]
    ax.plot(freqs, b2_obs[diag, diag], color="crimson", lw=1.8, marker="o",
            ms=3.5, label="observed b$^2$(f, f)")
    ax.plot(freqs, surr_band[diag, diag], color="0.4", lw=1.4, ls="--",
            label="surrogate null (95%)")
    ax.plot(freqs, ar_band[diag, diag], color="darkorange", lw=1.4, ls="-.",
            label=f"AR({AR_ORDER}) null (95%)")
    ax.set_xlabel("normalized frequency f (cycles / odd step)")
    ax.set_ylabel("b$^2$")
    ax.set_title("the SHG channel: diagonal (f, f) -> 2f")
    ax.legend(fontsize=8)

    ax = axes[2]
    power = np.mean(np.abs(np.fft.rfft(win, axis=1)) ** 2, axis=0) / L
    ax.plot(np.arange(K + 1) / L, power, color="steelblue", lw=1.6)
    ax.set_xlabel("normalized frequency f (cycles / odd step)")
    ax.set_ylabel("avg power")
    ax.set_title("ensemble power spectrum of standardized w_k")

    fig.suptitle(
        "SHG probe: does the +1 wobble quadratically phase-couple (chi^(2)) "
        "or mix linearly?",
        fontsize=13, y=0.99,
    )
    plt.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT, dpi=140)
    plt.close(fig)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
