"""Zeros of the chi_6-twisted Collatz zeta (Quantum Quench, Part 2).

The orbit-pair Hecke sum A(N) = sum_{n<=N odd} chi_6(iota_2(n)) obeys the
proven linear law A(N) = c N + E(N) with c = -i * 0.356035929815179/(2 sqrt 3)
(Dropping Zeta Spectrum Parts 3-5).  By Abel summation the detrended series

    G_N(s) = sum_{n<=N} a_n n^{-s} - c N^{1-s}/(1-s)
           -> c s/(s-1) + s * int_1^inf E(x) x^{-s-1} dx

converges for sigma > theta, where theta is the growth exponent of E.  G is
the analytic continuation of the twisted zeta in that half-plane (simple pole
at s = 1, residue c).  Its zeros are the "Collatz-twisted DQPTs" — the object
where a square-root-cancellation / RH-analog question about Collatz is well
posed.  Phases:

  A. compute a_n up to N_MAX, validate |A(N)|/N against the proven constant,
     and measure theta from |E(x)| on log-spaced x;
  B. zero map of G_N on sigma in [SIGMA_MIN, 1.3], t in (0, 60], with an
     N-stability filter (G_N vs G_{N/2}) so zeros are claimed only where the
     truncation has converged;
  C. spacing statistics, compared with the dropping-set band of Part 1.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
from collatz_dropping_dqpt import chi6_weights, spacing_stats  # noqa: E402

DATA = REPO / "data"
N_MAX = 2 * 10**6
C_EXACT = -1j * 0.356035929815179 / (2 * np.sqrt(3.0))
T_MAX = 60.0
T_GRID = np.arange(0.05, T_MAX + 1e-9, 0.05)
SIGMA_GRID = np.arange(0.40, 1.30 + 1e-9, 0.02)
STAB_TOL = 0.05          # |G_N - G_{N/2}| threshold for a converged point

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "0.9", "grid.linewidth": 0.6,
    "font.size": 10,
})


def G_scan(ns: np.ndarray, ws: np.ndarray, sigmas: np.ndarray,
           t_grid: np.ndarray, chunk: int = 8192) -> np.ndarray:
    """G_N(sigma + it) on a (sigma, t) product grid.

    Factors n^{-sigma-it} = n^{-sigma} e^{-it ln n} so the t-phase matrix is
    built once per chunk and reused across all sigmas.
    """
    logn = np.log(ns)
    G = np.zeros((len(sigmas), len(t_grid)), dtype=np.complex128)
    for lo in range(0, len(ns), chunk):
        ln = logn[lo:lo + chunk]
        E = np.exp(-1j * np.outer(t_grid, ln))
        W = ws[lo:lo + chunk, None] * np.exp(-np.outer(ln, sigmas))
        G += (E @ W).T
    s = sigmas[:, None] + 1j * t_grid[None, :]
    n_max = float(ns.max())
    G -= C_EXACT * np.exp((1 - s) * np.log(n_max)) / (1 - s)
    return G


def G_point(ns: np.ndarray, ws: np.ndarray, s: complex,
            logn: np.ndarray) -> complex:
    """Scalar G_N(s) by direct summation (used in Newton refinement)."""
    val = np.sum(ws * np.exp(-s * logn))
    n_max = float(ns.max())
    return val - C_EXACT * np.exp((1 - s) * np.log(n_max)) / (1 - s)


def error_exponent(ns: np.ndarray, ws: np.ndarray) -> tuple[np.ndarray, ...]:
    A = np.cumsum(ws)
    xs = np.unique(np.logspace(3, np.log10(len(ns) - 1), 60).astype(int))
    x_vals = ns[xs]
    E_vals = np.abs(A[xs] - C_EXACT * x_vals)
    theta, logc = np.polyfit(np.log(x_vals), np.log(E_vals), 1)
    return x_vals, E_vals, theta


def find_zeros(ns: np.ndarray, ws: np.ndarray) -> tuple[np.ndarray, float]:
    half = ns <= ns[len(ns) // 2]
    t0 = time.time()
    G_full = G_scan(ns, ws, SIGMA_GRID, T_GRID)
    G_half = G_scan(ns[half], ws[half], SIGMA_GRID, T_GRID)
    print(f"  grid evals in {time.time() - t0:.0f}s")
    absG = np.abs(G_full)
    stable = np.abs(G_full - G_half) < STAB_TOL

    interior = absG[1:-1, 1:-1]
    neigh = np.minimum.reduce([absG[:-2, 1:-1], absG[2:, 1:-1],
                               absG[1:-1, :-2], absG[1:-1, 2:]])
    ii, jj = np.where((interior < neigh) & stable[1:-1, 1:-1])

    logn = np.log(ns)
    logn_h = logn[half]

    def f(s):
        return G_point(ns, ws, s, logn)

    zeros, h = [], 1e-6
    for i, j in zip(ii + 1, jj + 1):
        s = SIGMA_GRID[i] + 1j * T_GRID[j]
        for _ in range(40):
            fs = f(s)
            dfs = (f(s + h) - f(s - h)) / (2 * h)
            if dfs == 0:
                break
            step = fs / dfs
            s -= step
            if abs(step) < 1e-10:
                break
        if not (abs(f(s)) < 1e-4 and SIGMA_GRID[0] - 0.05 < s.real < 1.35
                and 0.1 < s.imag <= T_MAX):
            continue
        # N-stability at the refined point
        if abs(f(s) - G_point(ns[half], ws[half], s, logn_h)) > STAB_TOL:
            continue
        if not any(abs(s - z) < 1e-4 for z in zeros):
            zeros.append(s)
    frac_stable = float(stable.mean())
    return np.array(sorted(zeros, key=lambda z: z.imag)), frac_stable


def main() -> None:
    t0 = time.time()
    print(f"=== Phase A: coefficients to N = {N_MAX:.0e} ===")
    cache = DATA / f"chi6_weights_{N_MAX}.npz"
    if cache.exists():
        z = np.load(cache)
        ns, ws = z["ns"], z["ws"]
        print("  (loaded from cache)")
    else:
        ns, ws = chi6_weights(N_MAX)
        np.savez_compressed(cache, ns=ns, ws=ws)
    c_hat = ws.sum() / N_MAX
    print(f"  A(N)/N = {c_hat:.5f}  vs exact {C_EXACT:.5f}  "
          f"(|diff| = {abs(c_hat - C_EXACT):.2e})")
    x_vals, E_vals, theta = error_exponent(ns, ws)
    print(f"  error exponent theta = {theta:.3f}  "
          f"(E(N) = {E_vals[-1]:.1f} at N = {x_vals[-1]:.0f})")

    print("=== Phase B: zero map of G(s) ===")
    zeros, frac_stable = find_zeros(ns, ws)
    print(f"  stable fraction of grid: {frac_stable:.2f}")
    print(f"  {len(zeros)} zeros")
    if len(zeros):
        print(f"  Re(s): mean {zeros.real.mean():.4f} std {zeros.real.std():.4f}"
              f" range [{zeros.real.min():.3f}, {zeros.real.max():.3f}]")
        for z in zeros:
            print(f"    s = {z.real:.4f} + {z.imag:.4f} i")

    print("=== Phase C: spacings ===")
    st = spacing_stats(zeros)
    print(f"  n={st['n']}  <r>={st['r_mean']:.3f}  period~{st['period']:.3f}  "
          f"resid/period={st['period_resid']:.3f}")

    # ---- figure ----
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6))

    ax = axes[0]
    ax.loglog(x_vals, E_vals, "o-", color=BLUE, ms=3.5, lw=1.0)
    ref = E_vals[-1] * (x_vals / x_vals[-1]) ** 0.5
    ax.loglog(x_vals, ref, "--", color="0.55", lw=1.0)
    ax.text(x_vals[2], ref[2] * 1.4, r"$N^{1/2}$", color="0.45", fontsize=9)
    ax.set_xlabel("$N$")
    ax.set_ylabel(r"$|E(N)| = |A(N) - cN|$")
    ax.set_title(rf"Hecke error term: $\theta \approx {theta:.2f}$",
                 fontsize=10)

    ax = axes[1]
    ax.axvline(0.5, color="0.55", lw=1.0, ls="--")
    ax.axvline(1.0, color="0.8", lw=1.0, ls=":")
    if len(zeros):
        ax.plot(zeros.real, zeros.imag, "o", color=ORANGE, ms=4.5)
    ax.axvspan(SIGMA_GRID[0] - 0.1, max(theta, SIGMA_GRID[0]),
               color="0.92", zorder=0)
    ax.set_xlim(SIGMA_GRID[0] - 0.1, 1.35)
    ax.set_ylim(0, T_MAX)
    ax.set_xlabel(r"$\sigma$")
    ax.set_ylabel("$t$")
    ax.set_title(rf"Zeros of the $\chi_6$-twisted zeta ({len(zeros)}), "
                 rf"$N = 2{{\times}}10^6$", fontsize=10)

    ax = axes[2]
    if len(zeros) >= 2:
        ts = np.sort(zeros.imag)
        ax.plot(np.arange(len(ts)), ts, "o-", color=ORANGE, lw=1.0, ms=3.5)
    ax.set_xlabel("zero index")
    ax.set_ylabel("ordinate $t$")
    ax.set_title(rf"Zero ladder: $\langle r\rangle = {st['r_mean']:.3f}$",
                 fontsize=10)

    fig.suptitle(r"The Collatz-twisted zeta $\sum_n \chi_6(\iota_2(n))\,n^{-s}$"
                 " — detrended continuation, N-stability-filtered zeros",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(DATA / "collatz_chi6_zeta_zeros.png", dpi=160)
    plt.close(fig)

    np.savez(DATA / "collatz_chi6_zeta_zeros.npz", zeros=zeros, theta=theta)
    print(f"\nDone in {time.time() - t0:.0f}s -> data/collatz_chi6_zeta_zeros.png")


if __name__ == "__main__":
    main()
