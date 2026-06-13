"""Fifth pass on the log-6 wobble: altitude cutoff, head x tail, visibility.

Picks up the open threads of scripts/collatz_log6_wobble_plateaus.py.

  1. Altitude cutoff.  Pass four showed Weyl amplitudes need the ~64
     largest wobble jumps.  Is that an absolute count, or "every visit
     below some altitude X*"?  Re-run the staircase truncation keeping
     jumps with x_j < X and sweep X over 10..10^9 separately for each of
     8 long orbits (lengths 500-990).  If the per-orbit error curves
     collapse at a common X* independent of orbit length, the spectral
     control is an altitude shell, not a count.  (Theory: dropping the
     jumps above X neglects total wobble ~ sum of 1/(3 x ln 6) over
     visits above X, and the phase error is m times that — so X* should
     be set by the harmonic range m, not by the orbit.)

  2. Head x tail factorization.  Cramer's V between dropping time
     (head, 2-adic) and gateway landmark (tail, archimedean) was 0.049 —
     small, but with ~50k samples possibly significant.  Quantify with
     mutual information against a shuffled null (which carries the
     finite-sample bias), locate any deviating cells via standardized
     residuals, and re-test excluding small n (n < 100 has s(n) = n,
     a trivial association; small n generally couple head and tail
     because the orbit is short).

  3. Visibility vs point count.  The article's polar plots used ~100
     points and saw 44; the closure spectrum of the full long orbit
     crowns 137.  Raw Weyl amplitude is the wrong "visibility" metric at
     small N (any m with |eps_m|*N << 1 scores ~1 trivially — the drift
     just hasn't wrapped yet).  What the eye traces in a spiral of dots
     is a PARASTICHY count, exactly as in sunflower heads: the visible
     arm count is the modal index difference between spatial
     nearest-neighbor points.  Compute that mode over the outer half of
     the first N points of the long orbit as N grows; the prediction is
     a staircase through the convergent denominators of log_6 3
     (44 visible at article-scale N, 137 taking over for long orbits).
     Plus the two polar renders (N = 110 vs N = 987) side by side.

Outputs:
    data/collatz_log6_cutoff.png
    data/collatz_log6_head_tail.png
    data/collatz_log6_visibility.png
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
ALPHA = math.log(3) / LOG6
LONG_SEED = 670617279
CONVERGENT_QS = (13, 31, 44, 75, 106, 137)


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

def plot_cutoff(path: str, m_max: int = 150, eps_cut: float = 0.03) -> dict:
    seeds = [LONG_SEED] + long_odd_seeds(7, min_len=500)
    x_grid = np.logspace(1, 9, 17)

    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    cmap = plt.get_cmap("viridis", len(seeds))
    all_err = {x: [] for x in x_grid}
    for i, n in enumerate(seeds):
        seq = orbit(n)
        n_pts = len(seq)
        k = np.arange(n_pts)
        xs = np.array([float(x) for x in seq])
        d = np.zeros(n_pts)
        odd = (xs[:-1] % 2 == 1)
        d[1:][odd] = np.log1p(1.0 / (3.0 * xs[:-1][odd])) / LOG6

        peaks = []
        w_full = np.cumsum(d)
        for m in range(2, m_max + 1):
            e = eps(m)
            if abs(e) > eps_cut:
                continue
            a_rot = abs(np.exp(2j * np.pi * e * k).sum()) / n_pts
            if a_rot <= 0.02:
                continue
            a_obs = abs(np.exp(2j * np.pi * (e * k + m * w_full)).sum()) / n_pts
            peaks.append((m, e, a_obs))

        errs = []
        for x_cut in x_grid:
            d_kept = d.copy()
            keep = np.zeros(n_pts, dtype=bool)
            keep[1:] = odd & (xs[:-1] < x_cut)
            d_kept[~keep] = 0.0
            w_approx = np.cumsum(d_kept)
            rel = []
            for m, e, a_obs in peaks:
                a_p = abs(np.exp(
                    2j * np.pi * (e * k + m * w_approx)).sum()) / n_pts
                rel.append(abs(a_p - a_obs) / a_obs)
            med = float(np.median(rel))
            errs.append(med)
            all_err[x_cut].append(med)
        ax.semilogx(x_grid, errs, "o-", ms=3, lw=1, color=cmap(i),
                    label=f"n = {n} ({n_pts - 1} steps)")

    ax.set_xlabel(r"altitude cutoff $X$: keep wobble jumps with $x < X$")
    ax.set_ylabel("median relative amplitude error")
    ax.axhline(0.05, color="0.6", ls=":", lw=0.8)
    ax.set_title("Spectral control is an altitude shell:\n"
                 "per-orbit truncation error vs cutoff $X$")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

    med_curve = {float(x): float(np.median(v)) for x, v in all_err.items()}
    x_star = next((x for x in x_grid if med_curve[float(x)] < 0.05), None)
    return {"x_star": float(x_star) if x_star else None,
            "med_curve": med_curve}


# ---------------------------------------------------------------- view 2

def mutual_info_bits(table: np.ndarray) -> float:
    p = table / table.sum()
    pi = p.sum(1, keepdims=True)
    pj = p.sum(0, keepdims=True)
    mask = p > 0
    return float((p[mask] * np.log2(p[mask] / (pi @ pj)[mask])).sum())


def plot_head_tail(path: str, n_max: int = 100001, seed: int = 5) -> dict:
    rng = np.random.default_rng(seed)
    ns, k_drop, land = [], [], []
    for n in range(3, n_max, 2):
        seq = orbit(n)
        ns.append(n)
        k_drop.append(dropping_time(n))
        land.append(next(x for x in seq if x % 2 == 1 and x < 100))
    ns = np.array(ns)
    k_drop = np.array(k_drop)
    land = np.array(land)

    def stats(sel: np.ndarray) -> dict:
        s_codes, s_inv = np.unique(land[sel], return_inverse=True)
        k_codes, k_inv = np.unique(k_drop[sel], return_inverse=True)
        table = np.zeros((len(s_codes), len(k_codes)))
        np.add.at(table, (s_inv, k_inv), 1)
        mi = mutual_info_bits(table)
        null_mis = []
        for _ in range(20):
            t0 = np.zeros_like(table)
            np.add.at(t0, (rng.permutation(s_inv), k_inv), 1)
            null_mis.append(mutual_info_bits(t0))
        expected = table.sum(1, keepdims=True) * table.sum(0) / table.sum()
        with np.errstate(divide="ignore", invalid="ignore"):
            std_resid = np.where(expected > 5,
                                 (table - expected) / np.sqrt(expected), 0.0)
        chi2 = float((std_resid ** 2).sum())
        v = math.sqrt(chi2 / (table.sum() * (min(*table.shape) - 1)))
        return {"mi": mi, "null_mi": float(np.mean(null_mis)),
                "null_sd": float(np.std(null_mis)), "v": v,
                "table": table, "std_resid": std_resid,
                "s_codes": s_codes, "k_codes": k_codes}

    full = stats(np.ones(len(ns), dtype=bool))
    big = stats(ns > 1000)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.4))
    for ax, st, lbl in ((ax1, full, "all odd $n < 10^5$"),
                        (ax2, big, "odd $1000 < n < 10^5$")):
        kc = st["k_codes"]
        keep = kc <= 26
        im = ax.imshow(st["std_resid"][:, keep], aspect="auto",
                       cmap="RdBu_r", vmin=-6, vmax=6)
        ax.set_xticks(range(int(keep.sum())))
        ax.set_xticklabels(kc[keep], fontsize=7)
        yticks = np.arange(0, len(st["s_codes"]), 5)
        ax.set_yticks(yticks)
        ax.set_yticklabels(st["s_codes"][yticks], fontsize=7)
        ax.set_xlabel("dropping time $k$ (head)")
        ax.set_ylabel("gateway landmark $s$ (tail)")
        excess = st["mi"] - st["null_mi"]
        ax.set_title(f"{lbl}:  V = {st['v']:.3f},  "
                     f"MI excess = {excess:.4f} bits "
                     f"({excess / st['null_sd']:.0f}$\\sigma$)", fontsize=10)
        fig.colorbar(im, ax=ax, label="standardized residual")
    fig.suptitle("Head $\\times$ tail: is the joint partition a product?")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(path, dpi=150)
    plt.close(fig)

    return {"full": {k: v for k, v in full.items()
                     if k in ("mi", "null_mi", "null_sd", "v")},
            "big": {k: v for k, v in big.items()
                    if k in ("mi", "null_mi", "null_sd", "v")}}


# ---------------------------------------------------------------- view 3

def parastichy_mode(theta: np.ndarray, n_pts: int) -> tuple[int, dict]:
    """Visible spiral-arm count: mode of nearest-neighbor index gaps.

    Render the first n_pts orbit points at (angle 2*pi*theta_k,
    radius k); for each point in the outer half find its nearest spatial
    neighbor; the modal index difference |i - j| is the parastichy
    number — the arm count the eye traces (sunflower-spiral logic).
    """
    idx = np.arange(n_pts)
    ang = 2 * np.pi * theta[:n_pts]
    x = idx * np.cos(ang)
    y = idx * np.sin(ang)
    d2 = (x[:, None] - x) ** 2 + (y[:, None] - y) ** 2
    np.fill_diagonal(d2, np.inf)
    outer = idx >= n_pts // 2
    nn = d2[outer].argmin(1)
    diffs = np.abs(nn - idx[outer])
    vals, counts = np.unique(diffs, return_counts=True)
    mode = int(vals[counts.argmax()])
    return mode, dict(zip(vals.tolist(), counts.tolist()))


def plot_visibility(path: str) -> dict:
    seq = orbit(LONG_SEED)
    theta = np.array([(math.log(x) / LOG6) % 1.0 for x in seq])
    n_grid = [60, 80, 110, 150, 200, 300, 450, 650, 987]

    modes = [parastichy_mode(theta, n)[0] for n in n_grid]

    fig = plt.figure(figsize=(15, 5))
    ax1 = fig.add_subplot(1, 3, 1)
    ax1.semilogx(n_grid, modes, "o-", color="crimson", lw=1.2)
    for q in CONVERGENT_QS:
        ax1.axhline(q, color="0.75", ls=":", lw=0.8)
        ax1.text(n_grid[0], q + 2, str(q), fontsize=7, color="0.4")
    ax1.set_xlabel("points plotted $N$")
    ax1.set_ylabel("visible arm count (parastichy mode, outer half)")
    ax1.set_title("What the eye sees vs how much orbit is plotted:\n"
                  "nearest-neighbor index gaps select the convergent")
    ax1.grid(alpha=0.25)

    for sub, n_pts in ((2, 110), (3, 987)):
        ax = fig.add_subplot(1, 3, sub, projection="polar")
        ax.scatter(2 * np.pi * theta[:n_pts], np.arange(n_pts), s=3,
                   c=np.arange(n_pts), cmap="viridis", alpha=0.85)
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        mode, _ = parastichy_mode(theta, n_pts)
        ax.set_title(f"$N$ = {n_pts}: visible arms = {mode}", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

    return {"n_grid": n_grid, "modes": modes}


# ---------------------------------------------------------------- main

def main() -> None:
    c = plot_cutoff("data/collatz_log6_cutoff.png")
    print("altitude cutoff: pooled median error vs X")
    for x, e in c["med_curve"].items():
        print(f"  X = {x:.1e}: err = {e:.3f}")
    print(f"pooled error < 5% from X = {c['x_star']:.1e}")

    ht = plot_head_tail("data/collatz_log6_head_tail.png")
    for lbl, st in (("all n", ht["full"]), ("n > 1000", ht["big"])):
        excess = st["mi"] - st["null_mi"]
        print(f"\nhead x tail ({lbl}): V = {st['v']:.4f}, "
              f"MI = {st['mi']:.4f} bits vs null {st['null_mi']:.4f} "
              f"+/- {st['null_sd']:.4f} (excess {excess:.4f}, "
              f"{excess / st['null_sd']:.1f} sigma)")

    vis = plot_visibility("data/collatz_log6_visibility.png")
    print("\nvisibility (parastichy mode = visible arm count):")
    for n_pts, mode in zip(vis["n_grid"], vis["modes"]):
        print(f"  N = {n_pts:4d}: {mode} arms")
    print("wrote 3 PNGs to data/")


if __name__ == "__main__":
    main()
