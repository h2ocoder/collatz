"""Third pass on the log-6 wobble: budget bands, lens test, closure spectrum.

Picks up the open threads of scripts/collatz_log6_wobble_followup.py.

  1. Budget bands — the (log_6 n, W_total) scatter shows discrete
     horizontal bands.  Hypothesis: orbit-tree merging.  Since ~92% of
     the wobble budget accrues at odd values < 100, define the LANDMARK
     s(n) = first odd orbit value < 100.  Every orbit funnels through
     some s, and from s onward the wobble contribution is the constant
     W_total(s).  Prediction:

        W_total(n) = W_pre(n) + W_total(s(n)),   W_pre >= 0 small,

     so the bands sit exactly at the ~50 values {W_total(s) : s odd < 100}
     and the residual W_pre (the pre-landmark wobble) is a small
     positive correction.  Tested for all odd n < 10^5.

  2. Lens test — make the sign-interference mechanism quantitative.
     Linearizing the wobble as W_k ~ wbar*k with wbar = W_total/N, the
     Weyl amplitude at a near-return m should be the Dirichlet kernel
     evaluated at the wobble-CORRECTED miss:

        A_lin(m) = |D_N(eps_eff)|/N,   eps_eff = eps_m + m*wbar.

     Compare A_obs against A_lin and against the uncorrected A_rot
     across the near-return peaks of 8 long orbits.

  3. Closure spectrum — the prediction that 137 (the convergent 84/137
     of log_6 3, unbeaten until q = 791) dominates long-orbit polar
     plots.  For each lag q, the RMS angular miss

        sigma(q) = sqrt(mean_k wrap(theta_{k+q} - theta_k)^2)

     measures how well the orbit closes after q steps, wobble included.
     Minima should sit at the convergent denominators 13/31/44/75/106
     with the global minimum at q = 137.  Plus the polar render
     (angle 2*pi*theta_k, radius k) where the spokes live.

Outputs:
    data/collatz_log6_wobble_bands.png
    data/collatz_log6_wobble_lens_test.png
    data/collatz_log6_closure_spectrum.png
"""

from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from collatz.core import orbit

LOG6 = math.log(6)
LOG2_6 = math.log(2) / LOG6
ALPHA = math.log(3) / LOG6
LONG_SEED = 670617279
CONVERGENT_QS = (13, 31, 44, 75, 106, 137)


def wobble_series(seq: list[int]) -> np.ndarray:
    w = np.zeros(len(seq))
    acc = 0.0
    for j, x in enumerate(seq[:-1]):
        if x % 2 == 1:
            acc += math.log1p(1.0 / (3.0 * x)) / LOG6
        w[j + 1] = acc
    return w


def w_total(seq: list[int]) -> float:
    odd = sum(1 for x in seq[:-1] if x % 2 == 1)
    even = len(seq) - 1 - odd
    return (even * LOG2_6 - odd * ALPHA
            + (math.log(seq[-1]) - math.log(seq[0])) / LOG6)


def eps(m: int) -> float:
    return m * ALPHA - round(m * ALPHA)


def wrap(x: np.ndarray) -> np.ndarray:
    return (x + 0.5) % 1.0 - 0.5


# ---------------------------------------------------------------- view 1

def plot_bands(path: str, n_max: int = 100001) -> dict:
    tail = {s: w_total(orbit(s)) for s in range(1, 100, 2)}

    w_tot, w_land, landmarks = [], [], []
    for n in range(3, n_max, 2):
        seq = orbit(n)
        s = next(x for x in seq if x % 2 == 1 and x < 100)
        w_tot.append(w_total(seq))
        w_land.append(tail[s])
        landmarks.append(s)
    w_tot = np.array(w_tot)
    w_land = np.array(w_land)
    landmarks = np.array(landmarks)
    resid = w_tot - w_land

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15.5, 4.8))

    ax1.hist(w_tot, bins=150, color="darkslateblue", alpha=0.85)
    top_s = [s for s, _ in
             sorted(((s, (landmarks == s).sum()) for s in set(landmarks)),
                    key=lambda t: -t[1])[:8]]
    for s in top_s:
        ax1.axvline(tail[s], color="crimson", lw=0.8, alpha=0.7)
        ax1.text(tail[s], ax1.get_ylim()[1] * 0.97, str(s), rotation=90,
                 fontsize=7, color="crimson", ha="right", va="top")
    ax1.set_xlabel(r"$W_{total}$")
    ax1.set_ylabel("count")
    ax1.set_title("Budget histogram; lines at $W_{total}(s)$\n"
                  "for the 8 most common landmarks $s$")

    ax2.scatter(w_land, w_tot, s=3, alpha=0.25, color="darkslateblue")
    lim = (min(w_land.min(), w_tot.min()) - 0.005, w_tot.max() + 0.005)
    ax2.plot(lim, lim, "r--", lw=1, label=r"$W_{total} = W_{total}(s)$")
    ax2.set_xlim(lim)
    ax2.set_ylim(lim)
    ax2.set_xlabel(r"$W_{total}(s)$ of landmark $s$ = first odd value < 100")
    ax2.set_ylabel(r"$W_{total}(n)$")
    ax2.set_title("Bands = landmark tails: budget vs landmark budget")
    ax2.legend(fontsize=8)

    ax3.hist(resid, bins=120, color="darkslateblue", alpha=0.85, log=True)
    ax3.set_xlabel(r"residual $W_{pre} = W_{total}(n) - W_{total}(s)$")
    ax3.set_ylabel("count (log)")
    ax3.set_title(f"Pre-landmark wobble: median = {np.median(resid):.4f}, "
                  f"95% < {np.quantile(resid, 0.95):.4f}")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

    return {"var_explained": 1.0 - resid.var() / w_tot.var(),
            "median_resid": float(np.median(resid)),
            "min_resid": float(resid.min()),
            "n_landmarks": len(set(landmarks))}


# ---------------------------------------------------------------- view 2

def long_odd_seeds(count: int, min_len: int, start: int = 10 ** 6) -> list[int]:
    seeds, n = [], start + 1
    while len(seeds) < count:
        if len(orbit(n)) >= min_len:
            seeds.append(n)
        n += 2
    return seeds


def dirichlet(e: float, n_pts: int) -> float:
    if abs(math.sin(math.pi * e)) < 1e-12:
        return 1.0
    return abs(math.sin(math.pi * e * n_pts)
               / (n_pts * math.sin(math.pi * e)))


def plot_lens_test(path: str, m_max: int = 150, eps_cut: float = 0.03) -> dict:
    seeds = [LONG_SEED] + long_odd_seeds(7, min_len=500)
    rows = []
    for n in seeds:
        seq = orbit(n)
        n_pts = len(seq)
        w = wobble_series(seq)
        wbar = w[-1] / (n_pts - 1)
        k = np.arange(n_pts)
        for m in range(2, m_max + 1):
            e = eps(m)
            if abs(e) > eps_cut:
                continue
            a_rot = abs(np.exp(2j * np.pi * e * k).sum()) / n_pts
            if a_rot <= 0.02:
                continue
            a_obs = abs(np.exp(2j * np.pi * (e * k + m * w)).sum()) / n_pts
            rows.append((e, e + m * wbar, a_rot, dirichlet(e + m * wbar, n_pts),
                         a_obs))
    e_raw, e_eff, a_rot, a_lin, a_obs = map(np.array, zip(*rows))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.4))
    ax1.scatter(a_rot, a_obs, s=18, alpha=0.6, color="0.6",
                label=f"uncorrected $A_{{rot}}$ (r = "
                      f"{np.corrcoef(a_rot, a_obs)[0, 1]:.2f})")
    ax1.scatter(a_lin, a_obs, s=18, alpha=0.7, color="crimson",
                label=f"lens-corrected $A_{{lin}}$ (r = "
                      f"{np.corrcoef(a_lin, a_obs)[0, 1]:.2f})")
    lim = (0, max(a_obs.max(), a_lin.max(), a_rot.max()) * 1.05)
    ax1.plot(lim, lim, "k--", lw=0.8)
    ax1.set_xlim(lim)
    ax1.set_ylim(lim)
    ax1.set_xlabel("predicted amplitude")
    ax1.set_ylabel(r"observed $A_{obs}$")
    ax1.set_title("Linear-wobble Dirichlet prediction\n"
                  r"$A_{lin} = |D_N(\epsilon_m + m\bar{w})|$")
    ax1.legend(fontsize=8)

    ax2.axhline(1, color="0.7", lw=0.8)
    ax2.axvline(0, color="0.7", lw=0.8)
    ax2.scatter(e_raw, a_obs / a_rot, s=14, alpha=0.45, color="0.6",
                label=r"vs raw $\epsilon_m$")
    ax2.scatter(e_eff, a_obs / a_rot, s=14, alpha=0.7, color="crimson",
                label=r"vs corrected $\epsilon_m + m\bar{w}$")
    ax2.set_xlabel("Diophantine miss")
    ax2.set_ylabel(r"$A_{obs} / A_{rot}$")
    ax2.set_title("The lens correction re-centers the enhancement\n"
                  "cloud around zero miss")
    ax2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

    return {"n_peaks": len(rows),
            "r_rot": float(np.corrcoef(a_rot, a_obs)[0, 1]),
            "r_lin": float(np.corrcoef(a_lin, a_obs)[0, 1])}


# ---------------------------------------------------------------- view 3

def plot_closure_spectrum(path: str, q_max: int = 200) -> dict:
    seq = orbit(LONG_SEED)
    theta = np.array([(math.log(x) / LOG6) % 1.0 for x in seq])
    n_pts = len(theta)

    qs = np.arange(1, q_max + 1)
    sigma = np.array([
        float(np.sqrt(np.mean(wrap(theta[q:] - theta[:-q]) ** 2)))
        for q in qs])

    fig = plt.figure(figsize=(13, 5.4))
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.semilogy(qs, sigma, color="darkslateblue", lw=1)
    for q in CONVERGENT_QS:
        ax1.axvline(q, color="crimson", ls=":", lw=0.8)
        ax1.text(q, 0.93, str(q), ha="center", fontsize=8, color="crimson",
                 transform=ax1.get_xaxis_transform())
    ax1.set_xlabel("lag $q$ (steps)")
    ax1.set_ylabel(r"RMS angular miss $\sigma(q)$")
    ax1.set_title(f"Closure spectrum of orbit({LONG_SEED}):\n"
                  "minima at the convergent denominators of $\\log_6 3$")

    ax2 = fig.add_subplot(1, 2, 2, projection="polar")
    ax2.scatter(2 * np.pi * theta, np.arange(n_pts), s=2.5,
                c=np.arange(n_pts), cmap="viridis", alpha=0.8)
    ax2.set_yticklabels([])
    ax2.set_xticklabels([])
    ax2.set_title("Polar render: angle $2\\pi\\theta_k$, radius $k$",
                  fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

    best = int(qs[np.argmin(sigma)])
    order = [int(q) for q in qs[np.argsort(sigma)[:6]]]
    return {"best_q": best, "top6": order,
            "sigma_at": {q: float(sigma[q - 1]) for q in CONVERGENT_QS}}


# ---------------------------------------------------------------- main

def main() -> None:
    b = plot_bands("data/collatz_log6_wobble_bands.png")
    print(f"bands: landmark tails explain {100 * b['var_explained']:.1f}% of "
          f"W_total variance over {b['n_landmarks']} landmarks; "
          f"median residual = {b['median_resid']:.4f}, "
          f"min residual = {b['min_resid']:.2e}")

    lens = plot_lens_test("data/collatz_log6_wobble_lens_test.png")
    print(f"lens test over {lens['n_peaks']} peaks: corr(A_obs, A_rot) = "
          f"{lens['r_rot']:.3f} vs corr(A_obs, A_lin) = {lens['r_lin']:.3f}")

    c = plot_closure_spectrum("data/collatz_log6_closure_spectrum.png")
    print(f"closure spectrum: best lag q = {c['best_q']}; "
          f"top-6 lags by closure: {c['top6']}")
    print("sigma at convergent denominators:")
    for q, s in c["sigma_at"].items():
        print(f"  q = {q:4d}: sigma = {s:.4f}")
    print("wrote 3 PNGs to data/")


if __name__ == "__main__":
    main()
