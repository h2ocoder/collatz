"""The Collatz quasicrystal: a synthetic diffractogram.

In base-6 log coordinates every Collatz step is a rigid rotation by
alpha = log_6 3, so the orbit's phases theta_k = {log_6 x_k} form a cut-and-
project set -- the canonical construction of a 1D quasicrystal -- decorated by
the +1 "wobble" W_k.  This script makes "crystal-like" literal by computing an
actual diffraction pattern.

Three views:

 1. The crystal.  The cut-and-project chain for slope alpha: atoms at two tile
    lengths in the Sturmian (aperiodic, ordered) word of log_6 3 -- the
    geometric backbone of the rotation.

 2. The diffractogram.  The structure factor S(q) = |sum_n e^{-i q x_n}|^2 / N
    of that chain.  Pure-point Bragg peaks at q = 2pi(h + h' alpha)/norm; the
    brightest sit exactly at the continued-fraction convergents of log_6 3
    (h'/h = 1/1, 1/2, 2/3, 3/5, 8/13, 19/31, ...).  This is what a real
    quasicrystal diffraction experiment looks like.

 3. The Collatz orbit realises it.  The internal-space spectrum
    I(m) = |mean_k e^{2pi i m theta_k}|^2 of a long real orbit, against the
    ideal rotation.  Bragg peaks at the convergent denominators 13, 31, 44,
    106, 137; the +1 wobble damps them by the Debye-Waller factor
    D(m) = |mean_k e^{2pi i m W_k}|, but only weakly (shot noise, not Gaussian)
    -- the crystal survives the disorder.

Outputs:
    data/collatz_quasicrystal_diffraction.png
"""

from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from collatz.core import orbit

ALPHA = math.log(3) / math.log(6)            # log_6 3
LOG6 = math.log(6)


def cut_and_project(half: int = 900):
    """1D quasicrystal chain: project Z^2 points in the strip onto the line."""
    norm = math.hypot(1, ALPHA)
    w = (ALPHA + 1) / norm                    # acceptance window (projected cell)
    xs = []
    for m in range(-half, half):
        for n in range(int(m * ALPHA) - 2, int(m * ALPHA) + 3):
            xperp = (-m * ALPHA + n) / norm
            if 0 <= xperp < w:
                xs.append((m + n * ALPHA) / norm)
    return np.sort(np.array(xs)), norm


def convergents(x: float, n: int):
    a, xx = [], x
    for _ in range(n):
        ai = math.floor(xx)
        a.append(ai)
        xx -= ai
        if xx < 1e-12:
            break
        xx = 1 / xx
    P, Q, out = [0, 1], [1, 0], []
    for ai in a:
        P.append(ai * P[-1] + P[-2])
        Q.append(ai * Q[-1] + Q[-2])
        out.append((P[-1], Q[-1]))
    return out


def long_orbit_phases(seed: int):
    """theta_k = {log_6 x_k} and the wobble W_k for a long real orbit."""
    seq = orbit(seed)
    theta = np.array([(math.log(x) / LOG6) % 1.0 for x in seq])
    # wobble W_k = theta_k - theta_0 - k*alpha (mod 1), unwrapped to the small part
    k = np.arange(len(seq))
    W = (theta - theta[0] - k * ALPHA)
    W = W - np.round(W)                        # the small +1 perturbation
    return theta, W


def main() -> None:
    fig = plt.figure(figsize=(15.5, 5.4))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.25, 1.25], wspace=0.27)

    pts, norm = cut_and_project()
    X = pts - pts.mean()
    N = len(X)
    print(f"cut-and-project chain: {N} atoms, span {X.max()-X.min():.0f}")

    # ---- Panel 1: the real-space chain ----
    ax0 = fig.add_subplot(gs[0, 0])
    seg = pts[(pts > pts.mean()) & (pts < pts.mean() + 55)]
    seg = seg - seg.min()
    for x in seg:
        ax0.plot([x, x], [0, 1], color="darkslateblue", lw=1.3)
    diffs = np.round(np.diff(seg), 3)
    ax0.set_yticks([])
    ax0.set_xlabel("position")
    ax0.set_title("1. The crystal\ncut-and-project chain of "
                  r"$\alpha=\log_6 3$ (two tiles, Sturmian order)",
                  fontsize=9.5)
    ax0.set_ylim(-0.4, 1.4)
    ax0.text(0, -0.32, f"tile lengths {sorted(set(diffs))[:2]}", fontsize=7.5,
             color="0.3")

    # ---- Panel 2: the diffractogram S(q) ----
    ax1 = fig.add_subplot(gs[0, 1])
    qs = np.linspace(0.02, 40, 40000)
    S = np.abs(np.exp(-1j * np.outer(qs, X)).sum(1)) ** 2 / N
    ax1.plot(qs, S / N, color="crimson", lw=0.7)
    # label the bright peaks by their convergent index h'/h
    cv = convergents(ALPHA, 7)                  # (p, q) with p/q -> alpha
    for (p, q) in cv:
        if q == 0 or p == 0:
            continue
        qphys = 2 * math.pi * (q + p * ALPHA) / norm   # h=q, h'=p  (h'/h = p/q -> alpha)
        if qphys < 40:
            j = np.argmin(np.abs(qs - qphys))
            if S[j] / N > 0.04:
                ax1.annotate(rf"$\frac{{{p}}}{{{q}}}$", (qphys, S[j] / N),
                             (qphys, S[j] / N + 0.06), fontsize=8,
                             ha="center", color="black")
    ax1.set_xlabel("wavevector $q$")
    ax1.set_ylabel("intensity  $S(q)/N$")
    ax1.set_title("2. The diffractogram\npure-point Bragg peaks at the "
                  r"convergents of $\log_6 3$", fontsize=9.5)
    ax1.set_ylim(0, 1.15)

    # ---- Panel 3: the Collatz orbit realises it (Debye-Waller) ----
    ax2 = fig.add_subplot(gs[0, 2])
    seed = 3 ** 10 * 2 ** 350 + 27             # big seed -> long, well-mixed orbit
    theta, W = long_orbit_phases(seed)
    ms = np.arange(1, 145)
    k = np.arange(len(theta))
    ideal = np.array([abs(np.mean(np.exp(2j * math.pi * m * (k * ALPHA)))) ** 2
                      for m in ms])
    real = np.array([abs(np.mean(np.exp(2j * math.pi * m * theta))) ** 2
                     for m in ms])
    ax2.plot(ms, ideal, color="orange", lw=1.4, ls="--", alpha=0.9,
             label="ideal rotation (crystal)")
    ax2.plot(ms, real, color="darkslateblue", lw=1.0,
             label=f"Collatz orbit ({len(theta)} steps)")
    for q in [13, 31, 44, 106, 137]:
        ax2.axvline(q, color="seagreen", ls=":", lw=0.7)
        ax2.text(q, ax2.get_ylim()[1] * 0.0 + 0.92, str(q), color="seagreen",
                 fontsize=7.5, ha="center",
                 transform=ax2.get_xaxis_transform())
    ax2.set_xlabel("Bragg order $m$  (internal space)")
    ax2.set_ylabel(r"intensity  $|\langle e^{2\pi i m\theta}\rangle|^2$")
    ax2.set_title("3. The orbit realises the crystal\n"
                  "peaks at 13/31/44/106/137; the +1 damps but doesn't melt",
                  fontsize=9.5)
    ax2.legend(fontsize=8)
    ax2.set_yscale("log")
    ax2.set_ylim(1e-5, 1.5)

    fig.suptitle("The Collatz quasicrystal: a synthetic diffractogram "
                 r"($\alpha=\log_6 3$)", fontsize=12.5, y=1.02)
    fig.savefig("data/collatz_quasicrystal_diffraction.png", dpi=150,
                bbox_inches="tight")
    plt.close(fig)

    sigW = W.std()
    print(f"orbit: {len(theta)} steps, wobble sigma_W = {sigW:.4f}")
    print(f"Debye-Waller at m=137: ideal {ideal[136]:.3f} vs orbit {real[136]:.3f}")
    print("wrote data/collatz_quasicrystal_diffraction.png")


if __name__ == "__main__":
    main()
