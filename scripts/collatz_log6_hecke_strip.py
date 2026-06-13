"""Seventh pass on the log-6 wobble: the Hecke strip.

Hecke (1921) attached to an irrational rotation the Dirichlet series
L_alpha(s) = sum_k ({k alpha} - 1/2) k^{-s}, whose analytic structure in
the strip is governed entirely by the continued fraction of alpha: via
the Fourier expansion of {x} - 1/2, each harmonic m contributes a
polylogarithm Li_s(e^{2 pi i m alpha}) whose near-singular amplitude
scales like |eps_m|^{sigma - 1} when m alpha is close to an integer.
For alpha = log_6 3 the singular harmonics are our convergent
denominators 13/31/44(semi)/75(semi)/106/137.

This script measures what the +1 wobble does to that strip, replacing
the rigid rotation angles {k alpha} by the true orbit angles theta_k.

Research questions:

  RQ1 Pole survival — do the near-pole heights
      P_m(sigma) = |sum_k e^{2 pi i m theta_k} k^{-sigma}| survive the
      wobble across the strip?  (Debye-Waller rigidity predicts yes.)
  RQ2 Depth — Dirichlet weights k^{-sigma} emphasize EARLY orbit steps,
      which are high-altitude and wobble-free; the lens asymmetry
      should only switch on below a crossover depth sigma*(m), and the
      tail-first ordering (weights (N+1-k)^{-sigma}) should show the
      opposite dependence.  "The wobble lives at the tail" becomes an
      analytic statement about the strip.
  RQ3 Effective miss — inverting the pure-rotation scaling law
      P(eps; sigma) on the orbit data gives eps_eff(m); the strip
      should see the same signed lens as the sigma = 0 Weyl analysis
      (eps < 0 sharpened, eps > 0 blunted).
  RQ4 Noise class — true wobble vs shuffled increments (same multiset,
      random timing) vs Gaussian walk (matched per-step mean/variance):
      which strip signatures are shot-noise-specific, and which need
      the true tail timing?
  RQ5 Strip portrait — the near-pole factor (-2 pi i eps)^{s-1} has
      modulus ~ e^{+pi t/2} for eps > 0 and e^{-pi t/2} for eps < 0:
      the two pole families live in opposite half-strips.  Scan
      |L(sigma + i t)| and test whether the wobble breaks the t <-> -t
      symmetry toward the eps < 0 side.

Outputs:
    data/collatz_log6_hecke_poleprofiles.png   (RQ1, RQ2)
    data/collatz_log6_hecke_surrogates.png     (RQ3, RQ4)
    data/collatz_log6_hecke_lines.png          (RQ5)
"""

from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from collatz.core import orbit

LOG6 = math.log(6)
ALPHA = math.log(3) / LOG6
LONG_SEED = 670617279
HARMONICS = (13, 31, 44, 75, 106, 137)


def eps(m: int) -> float:
    return m * ALPHA - round(m * ALPHA)


def giant_seed(min_len: int = 3400, seed: int = 17) -> list[int]:
    rng = np.random.default_rng(seed)
    while True:
        n = int.from_bytes(rng.bytes(60)) | 1
        seq = orbit(n)
        if len(seq) >= min_len:
            return seq


def thetas_and_deltas(seq: list[int]) -> tuple[np.ndarray, np.ndarray]:
    theta = np.array([(math.log(x) / LOG6) % 1.0 for x in seq])
    d = np.zeros(len(seq))
    for j, x in enumerate(seq[:-1]):
        if x % 2 == 1:
            d[j + 1] = math.log1p(1.0 / (3.0 * x)) / LOG6
    return theta, d


def pole_proxy(theta: np.ndarray, m: int, sigmas: np.ndarray,
               tail_first: bool = False) -> np.ndarray:
    n_pts = len(theta)
    e = np.exp(2j * np.pi * m * theta)
    k = np.arange(1, n_pts + 1, dtype=float)
    if tail_first:
        e = e[::-1]
    logk = np.log(k)
    return np.array([abs((e * np.exp(-s * logk)).sum()) for s in sigmas])


# ------------------------------------------------------------- RQ1, RQ2

def plot_pole_profiles(path: str) -> dict:
    seq = giant_seed()
    theta, _ = thetas_and_deltas(seq)
    n_pts = len(theta)
    rot = (theta[0] + np.arange(n_pts) * ALPHA) % 1.0
    sigmas = np.arange(0.0, 1.51, 0.05)

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4), sharey=True)
    cmap = plt.get_cmap("plasma", len(HARMONICS) + 1)
    cross = {}
    for tail, ax in zip((False, True), axes):
        for i, m in enumerate(HARMONICS):
            p_orb = pole_proxy(theta, m, sigmas, tail)
            p_rot = pole_proxy(rot, m, sigmas, tail)
            ratio = p_orb / p_rot
            ax.plot(sigmas, ratio, "o-", ms=2.5, lw=1.1, color=cmap(i),
                    label=rf"$m$ = {m} ($\epsilon$ = {eps(m):+.4f})")
            if not tail:
                far = np.flatnonzero(np.abs(ratio - 1) > 0.1)
                cross[m] = float(sigmas[far[-1]]) if far.size else 0.0
        ax.axhline(1, color="0.6", lw=0.8)
        ax.set_xlabel(r"$\sigma$ (Dirichlet depth)")
        ax.set_title("head-first weights $k^{-\\sigma}$" if not tail
                     else "tail-first weights $(N{+}1{-}k)^{-\\sigma}$")
        ax.grid(alpha=0.25)
    axes[0].set_ylabel(r"pole-height ratio  $P^{orb}_m(\sigma) / P^{rot}_m(\sigma)$")
    axes[0].legend(fontsize=7)
    fig.suptitle(f"The wobble in the Hecke strip (giant orbit, N = {n_pts}): "
                 "poles survive; the lens switches on only at shallow depth")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return {"crossover": cross, "n_pts": n_pts}


# ------------------------------------------------------------- RQ3, RQ4

def synth_pole_curve(n_pts: int, sigma: float,
                     eps_grid: np.ndarray) -> np.ndarray:
    k = np.arange(1, n_pts + 1, dtype=float)
    w = k ** (-sigma)
    return np.array([abs((np.exp(2j * np.pi * e * k) * w).sum())
                     for e in eps_grid])


def plot_surrogates(path: str, sigma: float = 0.5, n_draws: int = 40,
                    seed: int = 23) -> dict:
    rng = np.random.default_rng(seed)
    seq = giant_seed()
    theta, d = thetas_and_deltas(seq)
    n_pts = len(theta)
    rigid = (theta[0] + np.arange(n_pts) * ALPHA) % 1.0
    sigmas = np.arange(0.0, 1.51, 0.05)

    # RQ3: effective miss from the rotation scaling law at fixed sigma
    eps_grid = np.logspace(-4.5, -1.2, 400)
    curve = synth_pole_curve(n_pts, sigma, eps_grid)  # decreasing in eps
    order = np.argsort(curve)
    eps_eff = {}
    k = np.arange(1, n_pts + 1, dtype=float)
    w = k ** (-sigma)
    for m in HARMONICS:
        p_orb = abs((np.exp(2j * np.pi * m * theta) * w).sum())
        p_rot = abs((np.exp(2j * np.pi * m * rigid) * w).sum())
        e_orb = float(np.interp(p_orb, curve[order], eps_grid[order]))
        e_rot = float(np.interp(p_rot, curve[order], eps_grid[order]))
        # calibrate against the rotation's own inversion to cancel
        # Dirichlet-kernel oscillation bias
        eps_eff[m] = (e_orb, e_rot)

    # RQ4: surrogate wobbles
    def proxy_with_w(w_series: np.ndarray, m: int) -> np.ndarray:
        ph = rigid + w_series
        e = np.exp(2j * np.pi * m * ph)
        logk = np.log(k)
        return np.array([abs((e * np.exp(-s * logk)).sum()) for s in sigmas])

    w_true = np.cumsum(d)
    mu, sd = d.mean(), d.std()
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4))
    for ax, m in zip(axes, (44, 137)):
        p_rot = pole_proxy(rigid, m, sigmas)
        ax.plot(sigmas, proxy_with_w(w_true, m) / p_rot, "-", lw=1.6,
                color="crimson", label="true wobble")
        for label, color, gen in (
                ("shuffled increments", "darkslateblue",
                 lambda: np.cumsum(rng.permutation(d))),
                ("Gaussian walk (matched)", "0.55",
                 lambda: np.cumsum(rng.normal(mu, sd, n_pts)))):
            runs = np.array([proxy_with_w(gen(), m) / p_rot
                             for _ in range(n_draws)])
            lo, mid, hi = np.percentile(runs, [10, 50, 90], axis=0)
            ax.plot(sigmas, mid, "--", lw=1.2, color=color, label=label)
            ax.fill_between(sigmas, lo, hi, color=color, alpha=0.25)
        ax.axhline(1, color="0.6", lw=0.8)
        ax.set_xlabel(r"$\sigma$")
        ax.set_ylabel("pole-height ratio vs rotation")
        ax.set_title(rf"$m$ = {m} ($\epsilon$ = {eps(m):+.4f})")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.25)
    fig.suptitle("Noise class in the strip: true wobble vs shuffled timing "
                 "vs Gaussian walk")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return {"eps_eff": eps_eff, "sigma": sigma}


# ------------------------------------------------------------- RQ5

def twisted_line(theta: np.ndarray, m: int, sigma: float,
                 ts: np.ndarray) -> np.ndarray:
    """|Lambda_m(sigma + it)| for the COMPLEX series sum e^{2pi i m theta_k} k^{-s}.

    Unlike the real-coefficient Hecke series (whose |L| is even in t by
    Schwarz reflection), Lambda_m has no t-symmetry: by stationary phase
    the ridge sum_k e^{2 pi i eps k} k^{-sigma - it} only has a
    stationary point x* = t / (2 pi eps) inside [1, N] when sign(t) =
    sign(eps) — the pole families really do live in opposite
    half-strips.
    """
    k = np.arange(1, len(theta) + 1, dtype=float)
    base = np.exp(2j * np.pi * m * theta) * k ** (-sigma)
    logk = np.log(k)
    return np.array([abs((base * np.exp(-1j * t * logk)).sum())
                     for t in ts])


def plot_lines(path: str, sigma: float = 0.5, ms=(31, 44)) -> dict:
    seq = giant_seed()
    theta, _ = thetas_and_deltas(seq)
    n_pts = len(theta)
    rigid = (theta[0] + np.arange(n_pts) * ALPHA) % 1.0

    fig, axes = plt.subplots(len(ms), 1, figsize=(12.5, 7.5))
    asym = {}
    for ax, m in zip(axes, ms):
        e = eps(m)
        t_max = 1.3 * 2 * np.pi * abs(e) * n_pts
        ts = np.linspace(-t_max, t_max, 601)
        l_orb = twisted_line(theta, m, sigma, ts)
        l_rot = twisted_line(rigid, m, sigma, ts)
        u = ts / (2 * np.pi * abs(e) * n_pts)
        ax.plot(u, l_rot, color="0.6", lw=0.9, label="pure rotation")
        ax.plot(u, l_orb, color="crimson", lw=0.9, alpha=0.85,
                label="orbit (with wobble)")
        ax.axvspan(0 if e > 0 else -1, 1 if e > 0 else 0,
                   color="steelblue", alpha=0.08)
        ax.set_ylabel(rf"$|\Lambda_{{{m}}}({sigma} + it)|$")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.25)

        def half_energy(l):
            return ((l[u > 0] ** 2).sum(), (l[u < 0] ** 2).sum())

        po, no_ = half_energy(l_orb)
        pr, nr = half_energy(l_rot)
        asym[m] = {"orbit": (po - no_) / (po + no_),
                   "rotation": (pr - nr) / (pr + nr)}
        ax.set_title(
            rf"$m$ = {m}, $\epsilon$ = {e:+.4f}: ridge predicted on the "
            rf"sign($\epsilon$) side (shaded); asymmetry — rotation "
            rf"{asym[m]['rotation']:+.3f}, orbit {asym[m]['orbit']:+.3f}",
            fontsize=10)
    axes[-1].set_xlabel(r"$u = t / (2\pi|\epsilon_m|N)$  "
                        r"(ridge support is $0 < u\,\mathrm{sign}(\epsilon) < 1$)")
    fig.suptitle(f"Half-strip ridges of the twisted lines (giant orbit, "
                 f"N = {n_pts}, $\\sigma$ = {sigma})")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return asym


# ------------------------------------------------------------------ main

def main() -> None:
    pp = plot_pole_profiles("data/collatz_log6_hecke_poleprofiles.png")
    print(f"RQ1/RQ2 (giant orbit, N = {pp['n_pts']}): head-first crossover "
          "depth sigma* (largest sigma with |ratio - 1| > 0.1):")
    for m, s in pp["crossover"].items():
        print(f"  m = {m:4d} (eps = {eps(m):+.5f}): sigma* = {s:.2f}")

    sg = plot_surrogates("data/collatz_log6_hecke_surrogates.png")
    print(f"\nRQ3: effective miss at sigma = {sg['sigma']}, calibrated "
          "(orbit inversion / rotation inversion):")
    for m, (e_orb, e_rot) in sg["eps_eff"].items():
        r = e_orb / e_rot
        print(f"  m = {m:4d} (eps = {eps(m):+.5f}): eps_eff ratio = {r:.3f} "
              f"({'sharpened' if r < 1 else 'blunted'})")

    asym = plot_lines("data/collatz_log6_hecke_lines.png")
    print("\nRQ5 (corrected): half-strip energy asymmetry of the twisted "
          "lines |Lambda_m|^2 (positive = upper half):")
    for m, a in asym.items():
        print(f"  m = {m:4d} (sign eps = {'+' if eps(m) > 0 else '-'}): "
              f"rotation {a['rotation']:+.3f}, orbit {a['orbit']:+.3f}")
    print("wrote 3 PNGs to data/")


if __name__ == "__main__":
    main()
