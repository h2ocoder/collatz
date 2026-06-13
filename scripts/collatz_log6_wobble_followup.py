"""Follow-up on the log-6 wobble: interference mechanism, null check, budget.

Builds on scripts/collatz_log6_wobble.py.  Three threads:

  1. Why 44 beats 31 — the interference mechanism.  Writing
     theta_k = theta_0 + k*alpha + W_k exactly, the Weyl amplitude at
     harmonic m is

        A(m) = |sum_k e^{2 pi i (eps_m k + m W_k)}| / N,
        eps_m = m*alpha - round(m*alpha),

     i.e. a planar walk whose step direction drifts by eps_m per step
     (the Diophantine miss) plus m times the wobble.  The wobble is
     ALWAYS POSITIVE, so it should partially cancel the drift of
     near-returns that close from below (eps < 0, e.g. m = 13, 44, 75,
     106) and worsen near-returns that close from above (eps > 0, e.g.
     m = 31, 137).  View 1 draws the partial-sum walks for the long orbit;
     view 2 tests the sign rule across an ensemble of long orbits:
     damping ratio A_obs/A_rot vs signed eps_m for all near-returns.

  2. Carrier chi^2 — is the mild periodogram excess (chi2 ~ 119/64 in
     the first script) real v_2 correlation along orbits?  Resolution:
     no.  Two artifacts accounted for it: (a) at small seeds (~2^33),
     requiring orbits to survive skip+window steps selects climbing
     orbits, inflating odd density to 0.339 and under-dispersing
     per-window odd counts (variance ratio 0.76); with seeds ~2^59
     (orbits average ~430 steps, selection negligible) density, gap
     correlation and count variance all match renewal exactly.  (b) The
     original chi^2 divided by the null ensemble's SE only, ignoring the
     orbit ensemble's equal sampling error — doubling the statistic
     under the null (~128 on 64 dof).  With combined SE and large seeds
     the carrier is statistically indistinguishable from renewal.
     Printed only; also reports per-window odd-count variance vs null.

  3. The wobble budget W_total as a per-orbit invariant.  Exactly
     W_total = log_6(2^E / (3^O n)) for an orbit reaching 1.  Computed
     for all odd n < 10^5: distribution, growth with n, and whether
     dropping-set membership (the orbit's FIRST-drop behavior) is
     visible in the FULL-orbit wobble budget.

Outputs:
    data/collatz_log6_wobble_interference.png
    data/collatz_log6_wobble_sign_test.png
    data/collatz_log6_wobble_budget.png
"""

from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from collatz.core import orbit
from collatz.dropping import dropping_time

LOG6 = math.log(6)
LOG2_6 = math.log(2) / LOG6
ALPHA = math.log(3) / LOG6
LONG_SEED = 670617279


def wobble_series(seq: list[int]) -> np.ndarray:
    w = np.zeros(len(seq))
    acc = 0.0
    for j, x in enumerate(seq[:-1]):
        if x % 2 == 1:
            acc += math.log1p(1.0 / (3.0 * x)) / LOG6
        w[j + 1] = acc
    return w


def eps(m: int) -> float:
    return m * ALPHA - round(m * ALPHA)


# ---------------------------------------------------------------- view 1

def plot_interference(path: str, harmonics=(31, 44, 75, 106, 137, 150)) -> None:
    seq = orbit(LONG_SEED)
    n_pts = len(seq)
    w = wobble_series(seq)
    k = np.arange(n_pts)

    fig, axes = plt.subplots(2, 3, figsize=(13.5, 9))
    for ax, m in zip(axes.flat, harmonics):
        e = eps(m)
        rot = np.cumsum(np.exp(2j * np.pi * (e * k)))
        obs = np.cumsum(np.exp(2j * np.pi * (e * k + m * w)))
        ax.plot(rot.real, rot.imag, color="0.6", lw=0.8,
                label=f"rotation only: $|A|$ = {abs(rot[-1])/n_pts:.3f}")
        ax.plot(obs.real, obs.imag, color="crimson", lw=0.8,
                label=f"with wobble: $|A|$ = {abs(obs[-1])/n_pts:.3f}")
        ax.scatter([rot[-1].real, obs[-1].real], [rot[-1].imag, obs[-1].imag],
                   c=["0.4", "darkred"], s=15, zorder=3)
        ax.set_title(rf"$m$ = {m}:  $\epsilon$ = {e:+.4f}", fontsize=10)
        ax.legend(fontsize=7, loc="best")
        ax.set_aspect("equal")
        ax.tick_params(labelsize=7)
    fig.suptitle(
        f"Weyl partial-sum walks, orbit({LONG_SEED}): the positive wobble "
        "compensates $\\epsilon < 0$ near-returns\nand worsens "
        "$\\epsilon > 0$ ones — coherence selection by sign of the "
        "Diophantine miss")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- view 2

def long_odd_seeds(count: int, min_len: int, start: int = 10 ** 6) -> list[int]:
    seeds, n = [], start + 1
    while len(seeds) < count:
        if len(orbit(n)) >= min_len:
            seeds.append(n)
        n += 2
    return seeds


def plot_sign_test(path: str, m_max: int = 150, eps_cut: float = 0.03) -> dict:
    seeds = [LONG_SEED] + long_odd_seeds(7, min_len=500)
    pts = []
    for n in seeds:
        seq = orbit(n)
        n_pts = len(seq)
        w = wobble_series(seq)
        k = np.arange(n_pts)
        for m in range(2, m_max + 1):
            e = eps(m)
            if abs(e) > eps_cut:
                continue
            a_rot = abs(np.exp(2j * np.pi * e * k).sum()) / n_pts
            a_obs = abs(np.exp(2j * np.pi * (e * k + m * w)).sum()) / n_pts
            if a_rot > 0.02:  # only meaningful peaks
                pts.append((e, a_obs / a_rot, m, n))
    e_arr = np.array([p[0] for p in pts])
    r_arr = np.array([p[1] for p in pts])

    fig, ax = plt.subplots(figsize=(8.5, 6))
    ax.axhline(1, color="0.7", lw=0.8)
    ax.axvline(0, color="0.7", lw=0.8)
    ax.scatter(e_arr, r_arr, s=18, alpha=0.65, color="crimson")
    ax.set_xlabel(r"Diophantine miss $\epsilon_m = m\alpha - \mathrm{round}(m\alpha)$")
    ax.set_ylabel(r"damping ratio $A_{\mathrm{obs}}(m) / A_{\mathrm{rot}}(m)$")
    ax.set_title("Sign selection: the positive wobble enhances near-returns\n"
                 f"with $\\epsilon < 0$, damps those with $\\epsilon > 0$ "
                 f"({len(seeds)} long orbits, $m \\leq {m_max}$)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

    neg = r_arr[e_arr < 0]
    pos = r_arr[e_arr > 0]
    return {"n_pts": len(pts),
            "frac_enhanced_neg": float((neg > 1).mean()),
            "frac_damped_pos": float((pos < 1).mean()),
            "median_neg": float(np.median(neg)),
            "median_pos": float(np.median(pos))}


# ---------------------------------------------------------------- thread 2

def carrier_chi2(window: int = 128, skip: int = 32, n_orbits: int = 400,
                 seed: int = 1) -> dict:
    rng = np.random.default_rng(seed)
    spectra, gaps, odd_counts = [], [], []
    collected = 0
    while collected < n_orbits:
        n = int(rng.integers(1 << 58, 1 << 59)) * 2 + 1
        seq = orbit(n)
        if len(seq) < skip + window:
            continue
        win = seq[skip:skip + window]
        ind = np.array([x % 2 for x in win], dtype=float)
        gaps.extend(np.diff(np.flatnonzero(ind)))
        odd_counts.append(ind.sum())
        ind -= ind.mean()
        spectra.append(np.abs(np.fft.rfft(ind)) ** 2 / window)
        collected += 1
    spec_orbit = np.mean(spectra, axis=0)
    orbit_sd = np.std(spectra, axis=0) / math.sqrt(n_orbits)
    mean_gap = float(np.mean(gaps))

    def null_run(p: float) -> tuple[float, float]:
        null_spectra, null_counts = [], []
        for _ in range(n_orbits):
            pos, t = [], int(rng.integers(0, 3))
            while t < window:
                pos.append(t)
                t += 1 + rng.geometric(p)
            ind = np.zeros(window)
            ind[pos] = 1.0
            null_counts.append(ind.sum())
            ind -= ind.mean()
            null_spectra.append(np.abs(np.fft.rfft(ind)) ** 2 / window)
        spec_null = np.mean(null_spectra, axis=0)
        sd = np.sqrt(np.std(null_spectra, axis=0) ** 2 / n_orbits
                     + orbit_sd ** 2)
        chi2 = float(np.sum(((spec_orbit[1:] - spec_null[1:]) / sd[1:]) ** 2))
        return chi2, float(np.var(null_counts))

    p_matched = 1.0 / (mean_gap - 1.0)
    chi2_std, _ = null_run(0.5)
    chi2_mat, var_null = null_run(p_matched)
    return {"mean_gap": mean_gap, "dof": len(spec_orbit) - 1,
            "chi2_standard": chi2_std,
            "chi2_matched": chi2_mat,
            "p_matched": p_matched,
            "odd_count_var": float(np.var(odd_counts)),
            "odd_count_var_null": var_null}


# ---------------------------------------------------------------- view 3

def plot_budget(path: str, n_max: int = 100001) -> dict:
    ns, w_tot, k_drop = [], [], []
    for n in range(3, n_max, 2):
        odd = even = 0
        for x in orbit(n)[:-1]:
            if x % 2 == 1:
                odd += 1
            else:
                even += 1
        # exact identity: W_total = log_6(2^E / (3^O n))
        w = even * LOG2_6 - odd * ALPHA - math.log(n) / LOG6
        ns.append(n)
        w_tot.append(w)
        k_drop.append(dropping_time(n))
    ns = np.array(ns)
    w_tot = np.array(w_tot)
    k_drop = np.array(k_drop)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))
    ax1.hist(w_tot, bins=120, color="darkslateblue", alpha=0.85)
    ax1.set_xlabel(r"$W_{total}$")
    ax1.set_ylabel("count")
    ax1.set_title(f"Wobble budget, odd $n <$ {n_max - 1}\n"
                  f"mean = {w_tot.mean():.4f}, median = "
                  f"{np.median(w_tot):.4f}, max = {w_tot.max():.4f}")

    sc = ax2.scatter(np.log(ns) / LOG6, w_tot, s=3, alpha=0.4,
                     c=np.minimum(k_drop, 40), cmap="viridis")
    fig.colorbar(sc, ax=ax2, label="dropping time $k$ (capped at 40)")
    ax2.set_xlabel(r"$\log_6 n$")
    ax2.set_ylabel(r"$W_{total}$")
    ax2.set_title("Budget vs size, colored by dropping time $k$")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

    # does dropping time predict the full-orbit budget?
    stats = {}
    for k in sorted(set(k_drop)):
        sel = k_drop == k
        if sel.sum() >= 50:
            stats[k] = (float(w_tot[sel].mean()), float(w_tot[sel].std()),
                        int(sel.sum()))
    return {"mean": float(w_tot.mean()), "per_set": stats}


# ---------------------------------------------------------------- main

def main() -> None:
    print("eps_m for the marked harmonics:")
    for m in (13, 31, 44, 75, 106, 137):
        print(f"  m = {m:4d}: eps = {eps(m):+.5f}")

    plot_interference("data/collatz_log6_wobble_interference.png")
    sign = plot_sign_test("data/collatz_log6_wobble_sign_test.png")
    print(f"\nsign test over {sign['n_pts']} near-return peaks: "
          f"eps<0 enhanced {100*sign['frac_enhanced_neg']:.0f}% "
          f"(median ratio {sign['median_neg']:.2f}); "
          f"eps>0 damped {100*sign['frac_damped_pos']:.0f}% "
          f"(median ratio {sign['median_pos']:.2f})")

    c = carrier_chi2()
    print(f"\ncarrier chi2 on {c['dof']} bins: standard null (p=1/2) = "
          f"{c['chi2_standard']:.1f}; density-matched null (p = "
          f"{c['p_matched']:.3f}, mean gap {c['mean_gap']:.3f}) = "
          f"{c['chi2_matched']:.1f}")
    print(f"per-window odd-count variance: orbits = {c['odd_count_var']:.2f}, "
          f"null = {c['odd_count_var_null']:.2f} "
          f"(ratio {c['odd_count_var']/c['odd_count_var_null']:.2f}; "
          f">1 means between-window density heterogeneity)")
    c64 = carrier_chi2(skip=64, seed=2)
    print(f"deeper window (skip=64): standard = {c64['chi2_standard']:.1f}, "
          f"matched = {c64['chi2_matched']:.1f} (mean gap {c64['mean_gap']:.3f}), "
          f"count-var ratio = {c64['odd_count_var']/c64['odd_count_var_null']:.2f}")

    b = plot_budget("data/collatz_log6_wobble_budget.png")
    print(f"\nW_total over odd n < 1e5: mean = {b['mean']:.4f}")
    print("per dropping-time k: mean(W_total), std, count")
    for k, (mu, sd, cnt) in sorted(b["per_set"].items()):
        print(f"  k = {k:3d}: {mu:.4f} +/- {sd:.4f}  (n = {cnt})")
    print("wrote 3 PNGs to data/")


if __name__ == "__main__":
    main()
