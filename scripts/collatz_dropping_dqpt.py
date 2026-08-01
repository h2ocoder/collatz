"""DQPT probe of dropping-set L-functions (arXiv:2511.11199 template).

Each dropping set Dset_k is a finite union of residue classes mod 2^k, so its
Dirichlet series has an exact analytic continuation by Hurwitz zetas:

    L_k(s) = sum_{n in Dset_k} n^{-s} = 2^{-ks} * H_k(s),
    H_k(s) = sum_{r in R_k} zeta(s, r/2^k),   r taken in [1, 2^k].

The 2^{-ks} prefactor is zero-free, so zeros of L_k = zeros of H_k.  Phases:

  A. residue enumerator + vectorized Hurwitz zeta, validated against mpmath
     and against direct truncated sums at sigma > 1;
  B. zero map of H_k in the strip sigma in [-0.1, 1.3], t in (0, 60], with the
     k = 1 case (L_1 = 2^{-s} zeta(s)) validated against the Riemann zeros;
  C. spacing statistics of zero ordinates (clock vs GUE vs Poisson) and a
     periodic-fit test;
  D. truncated rate function  F_k(beta, t) = -ln|S_N(beta+it)| / ln N  (the
     DQPT free-energy density with system size log N), beta fan, plus the
     chi_6-twisted orbit-pair scan.

Calibration: Dset_1 = even numbers, so the k = 1 DQPT spectrum IS the Riemann
spectrum; higher k show how Collatz structure deforms it.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collatz.core import collatz_step  # noqa: E402
from collatz.lfunctions.characters import SexticResidueCharacter  # noqa: E402
from collatz.lfunctions.orbit_lift import orbit_pair  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"

K_LIST = [1, 3, 6, 8, 11]
KNOWN_RK = {1: 1, 3: 2, 6: 4, 8: 16, 11: 48}
SIGMA_GRID = np.arange(-0.50, 1.30 + 1e-9, 0.025)
T_MAX = 60.0
T_GRID = np.arange(0.05, T_MAX + 1e-9, 0.05)
EM_M = 80          # Euler-Maclaurin shift; must exceed max |Im s| for the tail
EM_V = 6           # Bernoulli tail terms B_2 .. B_12
CRIT_STURM = np.log2(1.5)  # 0.585, the renewal-boundary "critical line"

RIEMANN_T = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
             37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
             52.970321, 56.446248, 59.347044]

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
K_COLOR = {1: "0.45", 3: BLUE, 6: AQUA, 8: YELLOW, 11: ORANGE}
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "0.9", "grid.linewidth": 0.6,
    "font.size": 10,
})

BERNOULLI = [1 / 6, -1 / 30, 1 / 42, -1 / 30, 5 / 66, -691 / 2730]


# ---------------------------------------------------------------------------
# Phase A: machinery
# ---------------------------------------------------------------------------

def dropping_residues(k_max: int, lift: int = 10**9) -> dict[int, list[int]]:
    """Survivor-tree sieve returning the residues r mod 2^k (as ints in
    [0, 2^k)) whose orbits first drop below the start at exactly step k.

    Representatives are lifted near `lift` so the drop test is the generic
    (Terras) one, free of small-n boundary effects.
    """
    out: dict[int, list[int]] = {}
    survivors = [lift]
    for k in range(1, k_max + 1):
        new_survivors, dropped = [], []
        for n0 in survivors:
            for child in (n0, n0 + 2 ** (k - 1)):
                n = child
                for _ in range(k):
                    n = collatz_step(n)
                (dropped if n < child else new_survivors).append(child)
        out[k] = sorted(c % 2**k for c in dropped)
        survivors = new_survivors
    return out


def hurwitz_grid(s_flat: np.ndarray, a: float) -> np.ndarray:
    """zeta(s, a) for an array of complex s, Euler-Maclaurin with shift EM_M.

    Accurate to ~1e-11 for sigma >= -0.5, |Im s| <= EM_M - 10.
    """
    z = np.zeros_like(s_flat, dtype=np.complex128)
    for j in range(EM_M):
        z += np.exp(-s_flat * np.log(a + j))
    x = a + EM_M
    lx = np.log(x)
    z += np.exp((1 - s_flat) * lx) / (s_flat - 1)
    z += 0.5 * np.exp(-s_flat * lx)
    rising = s_flat.copy()          # (s)_{2v-1} rising factorial, v = 1 first
    fact = 2.0                      # (2v)!
    for v in range(1, EM_V + 1):
        z += BERNOULLI[v - 1] / fact * rising * np.exp(-(s_flat + 2 * v - 1) * lx)
        if v < EM_V:
            rising = rising * (s_flat + 2 * v - 1) * (s_flat + 2 * v)
            fact *= (2 * v + 1) * (2 * v + 2)
    return z


def H_k(s_flat: np.ndarray, residues: list[int], k: int) -> np.ndarray:
    """H_k(s) = sum_r zeta(s, r/2^k), r in [1, 2^k] (residue 0 -> 2^k)."""
    q = 2**k
    z = np.zeros_like(s_flat, dtype=np.complex128)
    for r in residues:
        z += hurwitz_grid(s_flat, (r if r != 0 else q) / q)
    return z


def validate_machinery(res: dict[int, list[int]]) -> None:
    import mpmath as mp
    mp.mp.dps = 25
    for k, n_exp in KNOWN_RK.items():
        assert len(res[k]) == n_exp, f"|R_{k}| = {len(res[k])} != {n_exp}"
    print("residue counts ok:", {k: len(res[k]) for k in K_LIST})

    pts = np.array([0.5 + 14.1j, 1.5 + 7.0j, 0.2 + 55.0j, 1.0 + 30.5j])
    worst = 0.0
    for a in (1.0, 3 / 8, 11 / 2048):
        ours = hurwitz_grid(pts, a)
        ref = np.array([complex(mp.zeta(complex(s), a)) for s in pts])
        worst = max(worst, float(np.max(np.abs(ours - ref) / np.abs(ref))))
    print(f"hurwitz vs mpmath: worst rel err {worst:.2e}")
    assert worst < 1e-9

    # truncated sum vs continuation at sigma = 1.5 (abscissa is 1)
    k, s0 = 3, 1.5 + 7.0j
    n = np.concatenate([np.arange(r if r else 2**k, 2 * 10**7, 2**k)
                        for r in res[k]]).astype(np.float64)
    direct = np.sum(np.exp(-s0 * np.log(n)))
    exact = 2.0**(-k * s0) * H_k(np.array([s0]), res[k], k)[0]
    err = abs(direct - exact) / abs(exact)
    print(f"truncated vs Hurwitz at s = {s0}: rel err {err:.2e}")
    assert err < 1e-3


# ---------------------------------------------------------------------------
# Phase B: zero map
# ---------------------------------------------------------------------------

def find_zeros(residues: list[int], k: int) -> np.ndarray:
    """Zeros of H_k in the strip, via grid minima + complex Newton."""
    sig, t = np.meshgrid(SIGMA_GRID, T_GRID, indexing="ij")
    s_flat = (sig + 1j * t).ravel()
    absH = np.abs(H_k(s_flat, residues, k)).reshape(sig.shape)

    cand = []
    interior = absH[1:-1, 1:-1]
    neigh = np.minimum.reduce([absH[:-2, 1:-1], absH[2:, 1:-1],
                               absH[1:-1, :-2], absH[1:-1, 2:]])
    ii, jj = np.where(interior < neigh)
    for i, j in zip(ii + 1, jj + 1):
        cand.append(sig[i, j] + 1j * t[i, j])

    def f(s):
        return H_k(np.array([s]), residues, k)[0]

    zeros = []
    h = 1e-6
    for s in cand:
        for _ in range(40):
            fs = f(s)
            dfs = (f(s + h) - f(s - h)) / (2 * h)
            if dfs == 0:
                break
            step = fs / dfs
            s -= step
            if abs(step) < 1e-11:
                break
        if abs(f(s)) < 1e-8 and -0.55 < s.real < 1.4 and 0.1 < s.imag <= T_MAX:
            if not any(abs(s - z) < 1e-5 for z in zeros):
                zeros.append(s)
    return np.array(sorted(zeros, key=lambda z: z.imag))


# ---------------------------------------------------------------------------
# Phase C: spacing statistics
# ---------------------------------------------------------------------------

def spacing_stats(zeros: np.ndarray) -> dict:
    ts = np.sort(zeros.imag)
    if len(ts) < 4:
        return {"n": len(ts), "r_mean": np.nan, "period_resid": np.nan,
                "period": np.nan}
    d = np.diff(ts)
    r = np.minimum(d[1:], d[:-1]) / np.maximum(d[1:], d[:-1])
    idx = np.arange(len(ts))
    slope, intercept = np.polyfit(idx, ts, 1)
    resid = np.std(ts - (slope * idx + intercept)) / slope
    return {"n": len(ts), "r_mean": float(np.mean(r)),
            "period": float(slope), "period_resid": float(resid)}


# ---------------------------------------------------------------------------
# Phase D: truncated rate function
# ---------------------------------------------------------------------------

def dset_members(residues: list[int], k: int, n_max: int) -> np.ndarray:
    n = np.concatenate([np.arange(r if r else 2**k, n_max + 1, 2**k)
                        for r in residues])
    return np.sort(n).astype(np.float64)


def partial_sums(n: np.ndarray, betas: list[float], t_grid: np.ndarray,
                 weights: np.ndarray | None = None,
                 chunk: int = 8192) -> np.ndarray:
    """S_N(beta + it) = sum w_n n^{-beta - i t}, vectorized.

    Rebuilds the phase matrix once per chunk and reuses it across betas.
    """
    logn = np.log(n)
    S = np.zeros((len(betas), len(t_grid)), dtype=np.complex128)
    for lo in range(0, len(n), chunk):
        ln = logn[lo:lo + chunk]
        E = np.exp(-1j * np.outer(t_grid, ln))
        for b, beta in enumerate(betas):
            w = np.exp(-beta * ln)
            if weights is not None:
                w = w * weights[lo:lo + chunk]
            S[b] += E @ w
    return S


def main_term(c: complex, betas: list[float], t_grid: np.ndarray,
              n_max: float) -> np.ndarray:
    """Boundary term c * N^{1-s} / (1-s) of a partial Dirichlet sum whose
    summatory function grows like A(x) ~ c x (c = density for an indicator).

    Subtracting it detrends the divergent part for beta < 1, so the residue
    converges to the analytic continuation — the paper's eta-factor trick,
    done explicitly.
    """
    s = np.array(betas)[:, None] + 1j * t_grid[None, :]
    return c * np.exp((1 - s) * np.log(n_max)) / (1 - s)


def exact_logamp(betas: list[float], t_grid: np.ndarray,
                 residues: list[int], k: int) -> np.ndarray:
    """-ln|L_k(beta + it)| from the Hurwitz continuation."""
    s = (np.array(betas)[:, None] + 1j * t_grid[None, :]).ravel()
    L = (2.0 ** (-k * s) * H_k(s, residues, k)).reshape(len(betas), -1)
    return -np.log(np.abs(L))


def chi6_weights(n_max: int) -> tuple[np.ndarray, np.ndarray]:
    chi = SexticResidueCharacter()
    ns, ws = [], []
    for n in range(3, n_max + 1, 2):
        ns.append(float(n))
        ws.append(chi.evaluate(orbit_pair(n)))
    return np.array(ns), np.array(ws, dtype=np.complex128)


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_zero_map(zeros_by_k: dict[int, np.ndarray]) -> None:
    fig, axes = plt.subplots(1, len(K_LIST), figsize=(13.5, 4.6), sharey=True)
    for ax, k in zip(axes, K_LIST):
        z = zeros_by_k[k]
        ax.axvline(0.5, color="0.55", lw=1.0, ls="--")
        ax.axvline(CRIT_STURM, color=ORANGE, lw=1.0, ls=":")
        if k == 1:
            ax.plot([0.5] * len(RIEMANN_T), RIEMANN_T, "x", color="0.2",
                    ms=7, mew=1.2, label="Riemann zeros")
            ax.legend(loc="lower left", fontsize=8, frameon=False)
        if len(z):
            ax.plot(z.real, z.imag, "o", color=K_COLOR[k], ms=4)
        ax.set_xlim(-0.55, 1.35)
        ax.set_ylim(0, T_MAX)
        ax.set_title(f"$H_{{{k}}}$  ({len(z)} zeros)", fontsize=10)
        ax.set_xlabel(r"$\sigma$")
    axes[0].set_ylabel("$t$")
    fig.suptitle("Zeros of dropping-set L-functions in the critical strip "
                 r"(grey: $\sigma=1/2$, orange: $\sigma=\log_2 3/2$)",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(DATA / "collatz_dqpt_zero_map.png", dpi=160)
    plt.close(fig)


def plot_rate_function(res: dict[int, list[int]],
                       zeros_by_k: dict[int, np.ndarray]) -> None:
    betas = [0.3, 0.5, CRIT_STURM, 0.8, 1.0]
    beta_cols = plt.cm.Blues(np.linspace(0.35, 0.95, len(betas)))
    t_grid = np.arange(0.02, 40.0, 0.02)
    n_show = 10**6

    fig, axes = plt.subplots(3, 1, figsize=(11, 9.5), sharex=True)

    # Panel 1: raw rate function — boundary-term dominated (Jentzsch comb)
    ax = axes[0]
    n = dset_members(res[3], 3, n_show)
    F = -np.log(np.abs(partial_sums(n, betas, t_grid))) / np.log(n.max())
    for b, beta in enumerate(betas):
        lbl = (r"$\beta=\log_2(3/2)$" if beta == CRIT_STURM
               else rf"$\beta={beta}$")
        ax.plot(t_grid, F[b], color=beta_cols[b], lw=1.1, label=lbl)
    ax.set_ylabel(r"$\mathcal{F}_3(\beta,t)$")
    ax.set_title(r"Raw rate function, Dset$_3$, $N=10^6$: boundary term "
                 r"dominates (comb period $2\pi/\ln N$)", fontsize=10)
    ax.legend(ncol=5, fontsize=8, frameon=False, loc="upper right")

    # Panels 2-3: detrended log-amplitude locks onto continuation zeros
    for ax, k in zip(axes[1:], (3, 11)):
        nset = dset_members(res[k], k, n_show)
        density = len(res[k]) / 2**k
        greys = ["0.75", "0.5", "0.15"]
        for c, expo in zip(greys, (4, 5, 6)):
            nn = nset[nset <= 10**expo]
            S = partial_sums(nn, [0.5], t_grid)
            S -= main_term(density, [0.5], t_grid, float(nn.max()))
            ax.plot(t_grid, -np.log(np.abs(S[0])), color=c, lw=0.9,
                    label=rf"$N=10^{expo}$")
        ax.plot(t_grid, exact_logamp([0.5], t_grid, res[k], k)[0],
                color=ORANGE, lw=1.4, alpha=0.85, label="exact $L_k$")
        for z in zeros_by_k[k]:
            if z.imag < 40:
                ax.axvline(z.imag, color=ORANGE, lw=0.6, alpha=0.35)
        ax.set_ylabel(rf"$-\ln|\tilde S_N|$,  $k={k}$")
        ax.set_title(rf"Detrended sum vs Hurwitz continuation, Dset$_{{{k}}}$,"
                     r" $\beta=1/2$ (spikes = DQPTs at exact zeros)",
                     fontsize=10)
        ax.legend(ncol=4, fontsize=8, frameon=False, loc="upper right")
    axes[2].set_xlabel("$t$")
    fig.tight_layout()
    fig.savefig(DATA / "collatz_dqpt_rate_function.png", dpi=160)
    plt.close(fig)


def plot_spacings(zeros_by_k: dict[int, np.ndarray],
                  stats: dict[int, dict]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))

    ax = axes[0]
    for k in K_LIST:
        z = zeros_by_k[k]
        if len(z) < 2:
            continue
        ts = np.sort(z.imag)
        ax.plot(np.arange(len(ts)), ts, "o-", color=K_COLOR[k], lw=1.0,
                ms=3.5, label=f"$k={k}$")
    ax.set_xlabel("zero index")
    ax.set_ylabel("ordinate $t$")
    ax.set_title("Zero ladders: straight line = clock (periodic) spectrum",
                 fontsize=10)
    ax.legend(fontsize=8, frameon=False)

    ax = axes[1]
    ks = [k for k in K_LIST if stats[k]["n"] >= 4]
    vals = [stats[k]["r_mean"] for k in ks]
    ax.bar(range(len(ks)), vals, color=[K_COLOR[k] for k in ks], width=0.6)
    for y, name in [(0.386, "Poisson"), (0.536, "GOE"), (0.603, "GUE")]:
        ax.axhline(y, color="0.55", lw=1.0, ls="--")
        ax.text(len(ks) - 0.45, y + 0.008, name, color="0.45", fontsize=8)
    ax.set_xticks(range(len(ks)), [f"$k={k}$" for k in ks])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel(r"$\langle r\rangle$ spacing ratio")
    ax.set_title(r"$\langle r\rangle \to 1$ means rigid clock spacing",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(DATA / "collatz_dqpt_spacings.png", dpi=160)
    plt.close(fig)


def plot_hecke(ns: np.ndarray, ws: np.ndarray) -> None:
    t_grid = np.arange(0.02, 40.0, 0.02)
    betas = [0.5, 0.8, 1.0, 1.2]
    beta_cols = plt.cm.Blues(np.linspace(0.35, 0.95, len(betas)))
    n_max = float(ns.max())
    c_hat = complex(ws.sum()) / n_max      # measured linear-growth constant

    S_raw = partial_sums(ns, betas, t_grid, weights=ws)
    S_det = S_raw - main_term(c_hat, betas, t_grid, n_max)

    fig, axes = plt.subplots(2, 1, figsize=(11, 7.0), sharex=True)
    for ax, S, tag in [(axes[0], S_raw, "raw"), (axes[1], S_det, "detrended")]:
        for b, beta in enumerate(betas):
            ax.plot(t_grid, -np.log(np.abs(S[b])), color=beta_cols[b],
                    lw=1.0, label=rf"$\beta={beta}$")
        ax.set_ylabel(rf"$-\ln|S_N|$ ({tag})")
    axes[0].set_title(r"$\chi_6$-twisted orbit-pair series, $N=10^5$: raw "
                      "partial sums (main term $\\hat c N^{1-s}/(1-s)$, "
                      f"$|\\hat c| = {abs(c_hat):.4f}$)", fontsize=10)
    axes[1].set_title("Main term removed: spikes = zeros of the "
                      "Collatz-twisted zeta beyond the proven linear growth",
                      fontsize=10)
    axes[0].legend(ncol=4, fontsize=8, frameon=False)
    axes[1].set_xlabel("$t$")
    fig.tight_layout()
    fig.savefig(DATA / "collatz_dqpt_hecke.png", dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------------------

def main() -> None:
    t0 = time.time()
    print("=== Phase A: machinery ===")
    res = dropping_residues(max(K_LIST))
    validate_machinery(res)

    print("\n=== Phase B: zero maps ===")
    zeros_by_k = {}
    for k in K_LIST:
        tk = time.time()
        zeros_by_k[k] = find_zeros(res[k], k)
        z = zeros_by_k[k]
        line = (f"k={k:>2}: {len(z):>3} zeros in {time.time()-tk:5.1f}s")
        if len(z):
            line += (f"  Re(s): mean {z.real.mean():.4f} "
                     f"std {z.real.std():.4f} "
                     f"range [{z.real.min():.3f}, {z.real.max():.3f}]")
        print(line)

    # k = 1 must reproduce the Riemann zeros
    z1 = np.sort(zeros_by_k[1].imag)
    ref = np.array(RIEMANN_T[:len(z1)])
    dev = np.max(np.abs(z1[:len(ref)] - ref)) if len(z1) else np.inf
    print(f"k=1 vs Riemann zeros: max |dt| = {dev:.2e}")
    assert dev < 1e-4, "k=1 calibration failed"

    print("\n=== Phase C: spacing statistics ===")
    stats = {k: spacing_stats(zeros_by_k[k]) for k in K_LIST}
    for k in K_LIST:
        s = stats[k]
        print(f"k={k:>2}: n={s['n']:>3}  <r>={s['r_mean']:.3f}  "
              f"period~{s['period']:.3f}  resid/period={s['period_resid']:.3f}")

    print("\n=== Phase D: rate functions ===")
    plot_zero_map(zeros_by_k)
    plot_rate_function(res, zeros_by_k)
    plot_spacings(zeros_by_k, stats)

    print("chi_6 weights ...")
    ns, ws = chi6_weights(10**5)
    print(f"  |sum chi| / N = {abs(ws.sum()) / 10**5:.4f}  (expect ~0.103)")
    plot_hecke(ns, ws)

    np.savez(DATA / "collatz_dqpt_zeros.npz",
             **{f"zeros_k{k}": zeros_by_k[k] for k in K_LIST})
    print(f"\nDone in {time.time()-t0:.1f}s. Plots in data/collatz_dqpt_*.png")


if __name__ == "__main__":
    main()
