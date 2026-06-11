"""The +1 wobble in log-6 coordinates: dynamics, constraints, harmonic analysis.

In theta(x) = frac(log_6 x) coordinates every Collatz step is a rigid
rotation by alpha = log_6 3 (because -log_6 2 = log_6 3 mod 1), plus a
small positive "wobble" increment at odd steps only:

    theta_{k} = theta_0 + k*alpha + W_k  (mod 1)
    W_k = sum over odd x_j, j<k of  delta_j,   delta_j = log_6(1 + 1/(3 x_j))

The wobble W_k is the entire content of the +1; everything else is the
rotation.  Telescoping gives the exact identity

    W_total = log_6(x_T / x_0) - O*log_6 3 + E*log_6 2

(O, E = odd/even step counts), so for an orbit reaching 1 the wobble
budget equals log_6(2^E / (3^O x_0)) — the dropping inequality itself.

This script renders four views of the wobble:

  1. Wobble traces — cumulative W_k against orbit altitude log_6 x_k for
     three seeds.  Shows the wobble is a record of low-altitude visits:
     flat while the orbit is high, stepping up when it comes down.
  2. Increment law — the constraint that delta is fully determined by
     position: delta = log_6(1 + 6^-(m+theta)/3) where m = floor(log_6 x).
     Plotted vs theta colored by level m (parallel curves, one per level,
     self-similar with ratio 6), and collapsed onto the single master
     curve vs altitude a = m + theta.
  3. Debye-Waller damping — treating W_k as phase noise on the rotation,
     the coherence factor D(m) = |mean_k exp(2*pi*i*m*W_k)| measures how
     the wobble suppresses the m-th harmonic of the Weyl spectrum,
     exactly like thermal disorder damping Bragg peaks.  Compared with
     the Gaussian prediction exp(-2*pi^2*m^2*var(W)) and shown alongside
     the raw Weyl amplitudes |sum_k e^{2 pi i m theta_k}|/N vs the pure
     rotation's, with the near-return denominators 31/44/75/106 marked.
  4. Carrier statistics — the wobble's *timing* is the odd-step indicator
     train, whose gaps are g = 1 + v_2(3x+1).  Average periodogram over
     an ensemble of orbit windows vs a renewal null (i.i.d. gaps
     g = 1 + Geometric(1/2), mean gap 3, odd-step density 1/3), plus the
     pooled gap distribution and gap autocorrelation.  Tests whether the
     rotation leaves any harmonic fingerprint in the timing, or whether
     the timing is pure 2-adic renewal noise.  Windows are taken from
     step 32 onward of orbits seeded at random odd n in [2^33, 2^34) to
     avoid both the common anchored start (all seeds odd) and the
     selection bias toward climbing orbits that small seeds would give.

Outputs:
    data/collatz_log6_wobble_traces.png
    data/collatz_log6_wobble_increment_law.png
    data/collatz_log6_wobble_debye_waller.png
    data/collatz_log6_wobble_carrier_spectrum.png
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

TRACE_SEEDS = [27, 703, 670617279]
LONG_SEED = 670617279


# ---------------------------------------------------------------- helpers

def log6(x: int) -> float:
    return math.log(x) / LOG6


def wobble_series(seq: list[int]) -> np.ndarray:
    """Cumulative wobble W_k for k = 0..len(seq)-1 (W_0 = 0)."""
    w = np.zeros(len(seq))
    acc = 0.0
    for j, x in enumerate(seq[:-1]):
        if x % 2 == 1:
            acc += math.log1p(1.0 / (3.0 * x)) / LOG6
        w[j + 1] = acc
    return w


def identity_check(seq: list[int]) -> tuple[float, float]:
    """(W_total, exact RHS log_6(x_T/x_0) - O log_6 3 + E log_6 2)."""
    odd = sum(1 for x in seq[:-1] if x % 2 == 1)
    even = len(seq) - 1 - odd
    w_total = wobble_series(seq)[-1]
    rhs = log6(seq[-1]) - log6(seq[0]) - odd * ALPHA + even * (math.log(2) / LOG6)
    return w_total, rhs


# ---------------------------------------------------------------- view 1

def plot_traces(path: str) -> None:
    fig, axes = plt.subplots(len(TRACE_SEEDS), 1, figsize=(11, 9), sharex=False)
    for ax, n in zip(axes, TRACE_SEEDS):
        seq = orbit(n)
        w = wobble_series(seq)
        alt = np.array([log6(x) for x in seq])
        steps = np.arange(len(seq))
        ax.step(steps, w, where="post", color="crimson", lw=1.4,
                label=r"wobble $W_k$")
        ax.set_ylabel(r"$W_k$", color="crimson")
        ax.tick_params(axis="y", labelcolor="crimson")
        ax2 = ax.twinx()
        ax2.plot(steps, alt, color="steelblue", lw=0.8, alpha=0.7,
                 label=r"altitude $\log_6 x_k$")
        ax2.set_ylabel(r"$\log_6 x_k$", color="steelblue")
        ax2.tick_params(axis="y", labelcolor="steelblue")
        wt, rhs = identity_check(seq)
        ax.set_title(
            f"n = {n}:  {len(seq) - 1} steps,  "
            f"$W_{{total}}$ = {wt:.5f}  (identity check: {rhs:.5f})",
            fontsize=10)
    axes[-1].set_xlabel("step $k$")
    fig.suptitle("The +1 wobble is a record of low-altitude visits")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- view 2

def plot_increment_law(path: str, n_max: int = 30000) -> None:
    thetas, deltas, levels = [], [], []
    for n in range(3, n_max, 2):
        for x in orbit(n):
            if x % 2 == 1 and x > 1:
                a = log6(x)
                m = int(a)
                if m <= 5:
                    thetas.append(a - m)
                    deltas.append(math.log1p(1.0 / (3.0 * x)) / LOG6)
                    levels.append(m)
    thetas = np.array(thetas)
    deltas = np.array(deltas)
    levels = np.array(levels)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5))
    cmap = plt.get_cmap("viridis", 6)
    sc = ax1.scatter(thetas, np.log(deltas) / LOG6, c=levels, cmap=cmap,
                     s=4, alpha=0.5, vmin=-0.5, vmax=5.5)
    fig.colorbar(sc, ax=ax1, ticks=range(6), label="level $m$")
    ax1.set_xlabel(r"angle $\theta$")
    ax1.set_ylabel(r"$\log_6 \delta$")
    ax1.set_title("Increment vs angle: one curve per level,\n"
                  "self-similar with ratio 6")

    altitude = levels + thetas
    ax2.scatter(altitude, np.log(deltas) / LOG6, s=4, alpha=0.4,
                color="darkslateblue")
    aa = np.linspace(0.3, 6, 200)
    ax2.plot(aa, np.log(np.log1p(6.0 ** (-aa) / 3.0) / LOG6) / LOG6, "r--", lw=1,
             label=r"$\delta = \log_6(1 + 6^{-a}/3)$")
    ax2.set_xlabel(r"altitude $a = \log_6 x$")
    ax2.set_ylabel(r"$\log_6 \delta$")
    ax2.set_title("Collapse: increment is fully determined by altitude")
    ax2.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- view 3

def plot_debye_waller(path: str) -> dict:
    seq = orbit(LONG_SEED)
    n_pts = len(seq)
    theta = np.array([log6(x) % 1.0 for x in seq])
    w = wobble_series(seq)
    ms = np.arange(1, 151)

    weyl_obs = np.array(
        [abs(np.exp(2j * np.pi * m * theta).mean()) for m in ms])
    rigid = theta[0] + np.arange(n_pts) * ALPHA
    weyl_rot = np.array(
        [abs(np.exp(2j * np.pi * m * rigid).mean()) for m in ms])
    dw = np.array([abs(np.exp(2j * np.pi * m * w).mean()) for m in ms])
    var_w = w.var()
    gauss = np.exp(-2 * np.pi ** 2 * ms ** 2 * var_w)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8))
    ax1.plot(ms, weyl_rot, color="0.6", lw=1, label="pure rotation")
    ax1.plot(ms, weyl_obs, color="crimson", lw=1.2, label="orbit (with wobble)")
    for q in (31, 44, 75, 106, 137):
        ax1.axvline(q, color="steelblue", ls=":", lw=0.8)
        ax1.text(q, 0.93, str(q), ha="center", fontsize=8, color="steelblue",
                 transform=ax1.get_xaxis_transform())
    ax1.set_xlabel("harmonic $m$")
    ax1.set_ylabel(r"$|N^{-1}\sum_k e^{2\pi i m \theta_k}|$")
    ax1.set_title(f"Weyl spectrum of orbit({LONG_SEED}), N = {n_pts}: "
                  "near-return harmonics 31/44/75/106/137")
    ax1.legend()

    ax2.plot(ms, dw, color="crimson", lw=1.2,
             label=r"$D(m) = |\langle e^{2\pi i m W_k}\rangle|$")
    ax2.plot(ms, gauss, "k--", lw=1,
             label=rf"$e^{{-2\pi^2 m^2 \sigma_W^2}}$, $\sigma_W$ = {math.sqrt(var_w):.4f}")
    ax2.set_xlabel("harmonic $m$")
    ax2.set_ylabel("coherence $D(m)$")
    ax2.set_title("Debye-Waller factor of the wobble: "
                  "phase disorder damping high harmonics")
    ax2.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return {"sigma_w": math.sqrt(var_w), "ms": ms, "dw": dw, "gauss": gauss}


# ---------------------------------------------------------------- view 4

def plot_carrier_spectrum(path: str, window: int = 128, skip: int = 32,
                          n_orbits: int = 400, seed: int = 1) -> dict:
    rng = np.random.default_rng(seed)

    # ensemble of real orbit windows: odd-step indicator over `window` steps
    # starting at step `skip`, seeds random odd n in [2^33, 2^34)
    spectra, acfs, gaps = [], [], []
    collected = 0
    while collected < n_orbits:
        n = int(rng.integers(1 << 32, 1 << 33)) * 2 + 1
        seq = orbit(n)
        if len(seq) < skip + window:
            continue
        win = seq[skip:skip + window]
        ind = np.array([x % 2 for x in win], dtype=float)
        odd_pos = np.flatnonzero(ind)
        gaps.extend(np.diff(odd_pos))
        ind -= ind.mean()
        spectra.append(np.abs(np.fft.rfft(ind)) ** 2 / window)
        ac = np.correlate(ind, ind, "full")[window - 1:window + 30]
        acfs.append(ac / ac[0])
        collected += 1
    spec_orbit = np.mean(spectra, axis=0)
    acf_orbit = np.mean(acfs, axis=0)
    gaps = np.array(gaps)

    # renewal null: odd steps separated by gaps g = 1 + Geometric(1/2)
    null_spectra, null_acfs, null_gaps = [], [], []
    for _ in range(n_orbits):
        pos, t = [], int(rng.integers(0, 3))
        while t < window:
            pos.append(t)
            t += 1 + rng.geometric(0.5)
        pos = np.array(pos[:-1] if pos and pos[-1] >= window else pos)
        null_gaps.extend(np.diff(pos))
        ind = np.zeros(window)
        ind[pos] = 1.0
        ind -= ind.mean()
        null_spectra.append(np.abs(np.fft.rfft(ind)) ** 2 / window)
        ac = np.correlate(ind, ind, "full")[window - 1:window + 30]
        null_acfs.append(ac / ac[0])
    null_gaps = np.array(null_gaps)
    spec_null = np.mean(null_spectra, axis=0)
    null_sd = np.std(null_spectra, axis=0) / math.sqrt(n_orbits)
    acf_null = np.mean(null_acfs, axis=0)

    freqs = np.fft.rfftfreq(window)
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15.5, 4.6))
    ax1.plot(freqs[1:], spec_null[1:], color="0.55", lw=1.2,
             label="renewal null (geometric gaps)")
    ax1.fill_between(freqs[1:], (spec_null - 2 * null_sd)[1:],
                     (spec_null + 2 * null_sd)[1:], color="0.55", alpha=0.3)
    ax1.plot(freqs[1:], spec_orbit[1:], color="crimson", lw=1.2,
             label=f"Collatz windows (n = {n_orbits})")
    ax1.set_xlabel("frequency (cycles / step)")
    ax1.set_ylabel("mean periodogram")
    ax1.set_title("Spectrum of the odd-step carrier train")
    ax1.legend(fontsize=8)

    gmax = 12
    gvals = np.arange(2, gmax + 1)
    obs = np.array([(gaps == g).mean() for g in gvals])
    null_obs = np.array([(null_gaps == g).mean() for g in gvals])
    geo = 0.5 ** (gvals - 1)
    ax2.semilogy(gvals, geo, "--", color="0.75", lw=1,
                 label=r"exact geometric $2^{-(g-1)}$")
    ax2.semilogy(gvals, null_obs, "o-", color="0.55", ms=4, lw=1,
                 label=f"renewal null, censored ({len(null_gaps)} gaps)")
    ax2.semilogy(gvals, obs, "o-", color="crimson", ms=4, lw=1,
                 label=f"observed ({len(gaps)} gaps)")
    ax2.set_xlabel("gap $g$ between odd steps")
    ax2.set_ylabel("probability")
    ax2.set_title(r"Gap law: $g = 1 + v_2(3x+1)$ vs geometric")
    ax2.legend(fontsize=8)

    lags = np.arange(31)
    ax3.plot(lags, acf_null, "o-", color="0.55", ms=3, lw=1, label="renewal null")
    ax3.plot(lags, acf_orbit, "o-", color="crimson", ms=3, lw=1, label="Collatz windows")
    ax3.set_xlabel("lag (steps)")
    ax3.set_ylabel("autocorrelation")
    ax3.set_title("Carrier autocorrelation")
    ax3.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

    chi2 = float(np.sum(((spec_orbit[1:] - spec_null[1:]) / null_sd[1:]) ** 2))
    g1, g2 = gaps[:-1], gaps[1:]
    lag1_r = float(np.corrcoef(g1, g2)[0, 1])
    return {"chi2": chi2, "dof": len(spec_orbit) - 1,
            "odd_density": float(np.mean(gaps) ** -1),
            "mean_gap": float(gaps.mean()),
            "lag1_r": lag1_r, "n_gaps": len(gaps)}


# ---------------------------------------------------------------- main

def main() -> None:
    print(f"alpha = log_6 3 = {ALPHA:.6f}")

    for n in TRACE_SEEDS:
        seq = orbit(n)
        wt, rhs = identity_check(seq)
        print(f"orbit({n}): {len(seq)-1} steps, W_total = {wt:.10f}, "
              f"identity RHS = {rhs:.10f}, err = {abs(wt-rhs):.2e}")

    # how much of the wobble budget comes from low altitude?
    seq = orbit(LONG_SEED)
    deltas = [(x, math.log1p(1 / (3 * x)) / LOG6)
              for x in seq[:-1] if x % 2 == 1]
    total = sum(d for _, d in deltas)
    low = sum(d for x, d in deltas if x < 100)
    print(f"orbit({LONG_SEED}): {100*low/total:.1f}% of W_total from odd x < 100")

    plot_traces("data/collatz_log6_wobble_traces.png")
    plot_increment_law("data/collatz_log6_wobble_increment_law.png")
    dw = plot_debye_waller("data/collatz_log6_wobble_debye_waller.png")
    below = np.flatnonzero(dw["dw"] < 0.5)
    half_m = dw["ms"][below[0]] if below.size else f"> {dw['ms'][-1]}"
    gauss_half = math.sqrt(math.log(2) / (2 * math.pi ** 2)) / dw["sigma_w"]
    print(f"sigma_W (orbit {LONG_SEED}) = {dw['sigma_w']:.4f}; "
          f"min D(m) = {dw['dw'].min():.3f} at m = {dw['ms'][np.argmin(dw['dw'])]}; "
          f"D < 1/2 first at m = {half_m} "
          f"(Gaussian phase noise would predict m ~ {gauss_half:.0f})")
    carrier = plot_carrier_spectrum("data/collatz_log6_wobble_carrier_spectrum.png")
    print(f"carrier: mean gap = {carrier['mean_gap']:.3f} (renewal: 3), "
          f"odd density = {carrier['odd_density']:.3f} (renewal: 1/3), "
          f"lag-1 gap corr = {carrier['lag1_r']:+.4f} "
          f"({carrier['n_gaps']} gaps, 2SE = {2/math.sqrt(carrier['n_gaps']):.4f})")
    print(f"carrier spectrum vs renewal null: chi2 = {carrier['chi2']:.1f} "
          f"on {carrier['dof']} bins")
    print("wrote 4 PNGs to data/")


if __name__ == "__main__":
    main()
