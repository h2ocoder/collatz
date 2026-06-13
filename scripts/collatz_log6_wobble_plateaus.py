"""Fourth pass on the log-6 wobble: plateau-sum Weyl model, landmark arithmetic.

Picks up the open threads of scripts/collatz_log6_wobble_bands.py.

  1. Plateau-sum Weyl model.  The wobble W_k is a staircase: constant on
     plateaus, jumping by delta_j = log_6(1 + 1/(3 x_j)) at each odd
     step.  The linear model failed (corr -0.09); the exact object is

        A(m) = (1/N) |sum_j e^{2 pi i m w_j} S_j(eps_m)|

     over plateaus j with phases set by the staircase heights w_j.  The
     model question: HOW MANY jumps matter?  Keep only the P largest
     jumps of the orbit (piecewise-constant approximation W~_k of W_k),
     compute A_P(m) = (1/N)|sum_k e^{2 pi i (eps_m k + m W~_k)}|, and
     sweep P.  P = 0 reproduces the pure rotation, P = all reproduces
     A_obs exactly.  The convergence curve corr(A_obs, A_P) vs P over
     the near-return peaks of 8 long orbits measures how concentrated
     the spectral control is: if corr saturates at small P, the whole
     Weyl spectrum is governed by the orbit's few deep visits to small
     values.

  2. Landmark arithmetic.  The gateway fibers F_s = {n : s(n) = s}
     (s(n) = first odd orbit value < 100) explain 99% of the wobble
     budget.  Are they residue-definable, like dropping sets (which are
     exactly unions of classes mod 2^k)?  Tests:
       (a) purity of the landmark within residue classes mod 2^j,
           j = 1..14, against a shuffled-landmark null with identical
           marginals — residue-defined fibers would hit purity 1 at
           finite j, structureless fibers track the null;
       (b) association between landmark and dropping time (Cramer's V);
       (c) the gateway hierarchy: variance of W_total explained vs the
           landmark threshold T (number of fibers grows ~T/2 as the
           partition refines toward the merge tree).

Outputs:
    data/collatz_log6_plateau_model.png
    data/collatz_log6_landmark_residues.png
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


def delta_series(seq: list[int]) -> np.ndarray:
    """Wobble jumps: d[k] = W_{k+1} - W_k (nonzero where x_k is odd)."""
    d = np.zeros(len(seq))
    for j, x in enumerate(seq[:-1]):
        if x % 2 == 1:
            d[j + 1] = math.log1p(1.0 / (3.0 * x)) / LOG6
    return d


def w_total(seq: list[int]) -> float:
    odd = sum(1 for x in seq[:-1] if x % 2 == 1)
    even = len(seq) - 1 - odd
    return (even * LOG2_6 - odd * ALPHA
            + (math.log(seq[-1]) - math.log(seq[0])) / LOG6)


def eps(m: int) -> float:
    return m * ALPHA - round(m * ALPHA)


def long_odd_seeds(count: int, min_len: int, start: int = 10 ** 6) -> list[int]:
    seeds, n = [], start + 1
    while len(seeds) < count:
        if len(orbit(n)) >= min_len:
            seeds.append(n)
        n += 2
    return seeds


# ---------------------------------------------------------------- view 1

def plot_plateau_model(path: str, m_max: int = 150,
                       eps_cut: float = 0.03) -> dict:
    seeds = [LONG_SEED] + long_odd_seeds(7, min_len=500)
    p_grid = [0, 1, 2, 4, 8, 16, 32, 64, 128]

    peaks = []  # (deltas, order, k, eps, m, a_rot, a_obs)
    for n in seeds:
        seq = orbit(n)
        n_pts = len(seq)
        d = delta_series(seq)
        order = np.argsort(d)[::-1]  # jump positions, largest first
        w_full = np.cumsum(d)
        k = np.arange(n_pts)
        for m in range(2, m_max + 1):
            e = eps(m)
            if abs(e) > eps_cut:
                continue
            a_rot = abs(np.exp(2j * np.pi * e * k).sum()) / n_pts
            if a_rot <= 0.02:
                continue
            a_obs = abs(np.exp(2j * np.pi * (e * k + m * w_full)).sum()) / n_pts
            peaks.append((d, order, k, e, m, a_rot, a_obs))

    a_obs_arr = np.array([p[6] for p in peaks])
    corrs, med_err = [], []
    preds_by_p = {}
    for p_keep in p_grid:
        preds = []
        for d, order, k, e, m, a_rot, a_obs in peaks:
            d_kept = np.zeros_like(d)
            if p_keep:
                idx = order[:p_keep]
                d_kept[idx] = d[idx]
            w_approx = np.cumsum(d_kept)
            preds.append(abs(np.exp(
                2j * np.pi * (e * k + m * w_approx)).sum()) / len(k))
        preds = np.array(preds)
        preds_by_p[p_keep] = preds
        corrs.append(np.corrcoef(preds, a_obs_arr)[0, 1])
        med_err.append(float(np.median(np.abs(preds - a_obs_arr)
                                       / a_obs_arr)))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.2))
    ax1.plot(p_grid, corrs, "o-", color="crimson", lw=1.2,
             label=r"corr$(A_P, A_{obs})$")
    ax1.plot(p_grid, med_err, "s--", color="darkslateblue", lw=1,
             label="median relative error")
    ax1.set_xscale("symlog", linthresh=1)
    ax1.set_xlabel("$P$ = number of largest wobble jumps kept")
    ax1.set_ylabel("convergence")
    ax1.set_title("Plateau-sum convergence over "
                  f"{len(peaks)} near-return peaks")
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.25)

    p_show = 8
    ax2.scatter(preds_by_p[0], a_obs_arr, s=18, alpha=0.55, color="0.6",
                label=f"$P$ = 0 (pure rotation), r = "
                      f"{np.corrcoef(preds_by_p[0], a_obs_arr)[0, 1]:.2f}")
    ax2.scatter(preds_by_p[p_show], a_obs_arr, s=18, alpha=0.7,
                color="crimson",
                label=f"$P$ = {p_show}, r = "
                      f"{np.corrcoef(preds_by_p[p_show], a_obs_arr)[0, 1]:.2f}")
    lim = (0, a_obs_arr.max() * 1.1)
    ax2.plot(lim, lim, "k--", lw=0.8)
    ax2.set_xlim(lim)
    ax2.set_ylim(lim)
    ax2.set_xlabel("predicted $A_P$")
    ax2.set_ylabel("observed $A_{obs}$")
    ax2.set_title(f"Keeping the {p_show} biggest jumps")
    ax2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

    return {"p_grid": p_grid, "corrs": [float(c) for c in corrs],
            "med_err": med_err, "n_peaks": len(peaks)}


# ---------------------------------------------------------------- view 2

def landmark_of(seq: list[int], threshold: int) -> int:
    return next(x for x in seq if x % 2 == 1 and x < threshold)


def purity(codes: np.ndarray, residues: np.ndarray, n_codes: int) -> float:
    """Weighted max-fraction of a single landmark code per residue class."""
    key = residues.astype(np.int64) * n_codes + codes
    counts = np.bincount(key, minlength=(int(residues.max()) + 1) * n_codes)
    table = counts.reshape(-1, n_codes)
    return float(table.max(axis=1).sum() / len(codes))


def plot_landmark_residues(path: str, n_max: int = 100001,
                           thresholds=(4, 8, 16, 32, 64, 100, 200, 400, 1000),
                           seed: int = 3) -> dict:
    t_max = max(thresholds)
    tails = {s: w_total(orbit(s)) for s in range(1, t_max, 2)}

    ns, w_tot, k_drop = [], [], []
    landmarks = {t: [] for t in thresholds}
    for n in range(3, n_max, 2):
        seq = orbit(n)
        ns.append(n)
        w_tot.append(w_total(seq))
        k_drop.append(dropping_time(n))
        for t in thresholds:
            landmarks[t].append(landmark_of(seq, t))
    ns = np.array(ns)
    w_tot = np.array(w_tot)
    k_drop = np.array(k_drop)
    land100 = np.array(landmarks[100])

    # (a) residue purity of the T=100 landmark, real vs shuffled null
    rng = np.random.default_rng(seed)
    codes = (land100 - 1) // 2
    shuffled = rng.permutation(codes)
    js = np.arange(1, 15)
    pur_real = [purity(codes, ns % (1 << j), 50) for j in js]
    pur_null = [purity(shuffled, ns % (1 << j), 50) for j in js]

    # (b) landmark vs dropping time: Cramer's V
    k_codes, k_inv = np.unique(k_drop, return_inverse=True)
    table = np.zeros((50, len(k_codes)))
    np.add.at(table, (codes, k_inv), 1)
    expected = table.sum(1, keepdims=True) * table.sum(0) / table.sum()
    mask = expected > 0
    chi2 = float(((table - expected)[mask] ** 2 / expected[mask]).sum())
    v = math.sqrt(chi2 / (table.sum() * (min(*table.shape) - 1)))

    # (c) hierarchy: variance explained vs threshold
    var_exp, n_fibers = [], []
    for t in thresholds:
        lm = np.array(landmarks[t])
        resid = w_tot - np.array([tails[s] for s in lm])
        var_exp.append(1.0 - resid.var() / w_tot.var())
        n_fibers.append(len(set(lm)))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.2))
    ax1.plot(js, pur_real, "o-", color="crimson", lw=1.2,
             label="landmark $s(n)$, $T$ = 100")
    ax1.plot(js, pur_null, "o-", color="0.6", lw=1.2,
             label="shuffled null (same marginals)")
    ax1.set_xlabel(r"$j$:  residue classes mod $2^j$")
    ax1.set_ylabel("purity (weighted max landmark fraction)")
    ax1.set_title("Are gateway fibers residue-definable?\n"
                  "(dropping sets would hit 1.0 at their $k$)")
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.25)

    ax2.semilogx(thresholds, var_exp, "o-", color="crimson", lw=1.2)
    ax2.set_xlabel("gateway threshold $T$ (landmark = first odd value < $T$)")
    ax2.set_ylabel(r"variance of $W_{total}$ explained", color="crimson")
    ax2.tick_params(axis="y", labelcolor="crimson")
    ax2.grid(alpha=0.25)
    ax2b = ax2.twinx()
    ax2b.loglog(thresholds, n_fibers, "s--", color="darkslateblue", lw=1)
    ax2b.set_ylabel("number of fibers", color="darkslateblue")
    ax2b.tick_params(axis="y", labelcolor="darkslateblue")
    ax2.set_title("The gateway hierarchy: refining toward the merge tree")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

    return {"js": list(js), "pur_real": pur_real, "pur_null": pur_null,
            "cramers_v": v, "thresholds": list(thresholds),
            "var_exp": [float(x) for x in var_exp], "n_fibers": n_fibers}


# ---------------------------------------------------------------- main

def main() -> None:
    pm = plot_plateau_model("data/collatz_log6_plateau_model.png")
    print(f"plateau model over {pm['n_peaks']} peaks:")
    for p, c, e in zip(pm["p_grid"], pm["corrs"], pm["med_err"]):
        print(f"  P = {p:4d}: corr = {c:+.3f}, median rel err = {e:.3f}")

    lr = plot_landmark_residues("data/collatz_log6_landmark_residues.png")
    print("\nlandmark residue purity (real vs shuffled null):")
    for j, pr, pn in zip(lr["js"], lr["pur_real"], lr["pur_null"]):
        print(f"  mod 2^{j:<2d}: {pr:.3f} vs null {pn:.3f} "
              f"(excess {pr - pn:+.3f})")
    print(f"Cramer's V (landmark vs dropping time) = {lr['cramers_v']:.4f}")
    print("\ngateway hierarchy:")
    for t, ve, nf in zip(lr["thresholds"], lr["var_exp"], lr["n_fibers"]):
        print(f"  T = {t:5d}: {nf:4d} fibers, variance explained = "
              f"{100 * ve:.2f}%")
    print("wrote 2 PNGs to data/")


if __name__ == "__main__":
    main()
