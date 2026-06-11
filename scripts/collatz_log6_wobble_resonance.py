"""Sixth pass on the log-6 wobble: closure resonances, the 137-arm test.

Picks up the final open threads of scripts/collatz_log6_wobble_cutoff.py.

  1. Closure resonances — reconciling the article's 44.  The local
     per-step wobble rate at altitude x is

        w(x) ~ (1/3) * log_6(1 + 1/(3x)) ~ 1 / (9 ln6 x)

     (odd steps have density ~1/3).  A q-step closure with Diophantine
     miss eps_q < 0 is locally CANCELLED by the wobble when
     q * w(x) = |eps_q|, i.e. at the resonant altitude

        x*_q = q / (9 ln6 |eps_q|).

     Predictions: q = 13 rings at x ~ 28, q = 44 at x ~ 127, q = 75 at
     x ~ 333, q = 106 at x ~ 1029 — while q = 31 and q = 137 (eps > 0)
     have no resonance and only lose closure as the orbit descends.
     The descent CHIRPS through the eps < 0 closures in turn, and 44 is
     the resonance sitting in the small-value band every orbit's tail
     occupies — the band Paper 3's polar plots render most densely.
     Test: pool the q-step angular miss |wrap(theta_{k+q} - theta_k)|
     over hundreds of orbits, bin by mean window altitude, and check
     each eps < 0 curve dips at its predicted x*_q.

  2. The 137-arm test.  The parastichy selection rule is LOCAL in
     radius: at radius k the visible arm count is
     q*(k) = argmin q^2 + (2 pi k eps_q)^2, predicting transitions at
     k ~ 160 (13 -> 31) and k ~ 2840 (31 -> 137) with 106 NEVER optimal
     (31 holds until 137 takes over).  Orbits reaching k ~ 3400 need
     seeds ~ 10^140 (total steps ~ 10.4 ln n) — trivial with bigints.
     Find one, measure the parastichy mode per radial band, render the
     chirping-arm finale.

Outputs:
    data/collatz_log6_resonance.png
    data/collatz_log6_137_arms.png
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
QS = (13, 31, 44, 75, 106, 137)


def eps(m: int) -> float:
    return m * ALPHA - round(m * ALPHA)


def resonant_altitude(q: int) -> float | None:
    e = eps(q)
    if e >= 0:
        return None
    return q / (9 * LOG6 * abs(e))


def wrap(x: np.ndarray) -> np.ndarray:
    return (x + 0.5) % 1.0 - 0.5


# ---------------------------------------------------------------- view 1

def plot_resonance(path: str, n_orbits: int = 500, min_len: int = 250,
                   start: int = 10 ** 6) -> dict:
    per_q = {q: ([], [], []) for q in QS}  # ratio r, altitude, |miss|
    n, used = start + 1, 0
    while used < n_orbits:
        seq = orbit(n)
        n += 2
        if len(seq) < min_len:
            continue
        used += 1
        a = np.array([math.log(x) / LOG6 for x in seq])
        theta = a % 1.0
        d = np.zeros(len(seq))
        for j, x in enumerate(seq[:-1]):
            if x % 2 == 1:
                d[j + 1] = math.log1p(1.0 / (3.0 * x)) / LOG6
        w = np.cumsum(d)
        ca = np.concatenate([[0.0], np.cumsum(a)])
        for q in QS:
            if len(seq) <= q:
                continue
            miss = np.abs(wrap(theta[q:] - theta[:-q]))
            ratio = (w[q:] - w[:-q]) / abs(eps(q))  # window wobble / |eps|
            a_mean = (ca[q:] - ca[:-q]) / q
            per_q[q][0].append(ratio)
            per_q[q][1].append(a_mean[:len(miss)])
            per_q[q][2].append(miss)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.6))
    cmap = plt.get_cmap("plasma", len(QS) + 1)

    # (a) exact mechanism: miss vs r = Delta W / |eps_q| — eps<0 dips at r=1
    r_bins = np.arange(0.0, 3.05, 0.1)
    r_mids = 0.5 * (r_bins[:-1] + r_bins[1:])
    for i, q in enumerate(QS):
        r = np.concatenate(per_q[q][0])
        miss = np.concatenate(per_q[q][2])
        idx = np.digitize(r, r_bins) - 1
        mm = np.array([miss[idx == b].mean() if (idx == b).sum() >= 50
                       else np.nan for b in range(len(r_mids))])
        ax1.semilogy(r_mids, mm, "o-", ms=3, lw=1.2, color=cmap(i),
                     label=rf"$q$ = {q} ($\epsilon$ = {eps(q):+.4f})")
    ax1.axvline(1.0, color="0.4", ls="--", lw=1)
    ax1.set_xlabel(r"$r = \Delta W_{window} \,/\, |\epsilon_q|$")
    ax1.set_ylabel(r"mean closure miss $|\mathrm{wrap}(\theta_{k+q}-\theta_k)|$")
    ax1.set_title("Exact cancellation test: $\\epsilon < 0$ harmonics\n"
                  "dip at $r = 1$; $\\epsilon > 0$ harmonics only worsen")
    ax1.legend(fontsize=7)
    ax1.grid(alpha=0.25)

    # (b) the chirp in altitude coordinates
    a_bins = np.arange(0.5, 8.25, 0.25)
    a_mids = 0.5 * (a_bins[:-1] + a_bins[1:])
    dips = {}
    for i, q in enumerate(QS):
        alt = np.concatenate(per_q[q][1])
        miss = np.concatenate(per_q[q][2])
        idx = np.digitize(alt, a_bins) - 1
        mm = np.array([miss[idx == b].mean() if (idx == b).sum() >= 30
                       else np.nan for b in range(len(a_mids))])
        ax2.semilogy(a_mids, mm, "o-", ms=3, lw=1.2, color=cmap(i),
                     label=rf"$q$ = {q}")
        if eps(q) < 0:
            ok = ~np.isnan(mm)
            dips[q] = (float(a_mids[ok][np.argmin(mm[ok])]),
                       math.log(resonant_altitude(q)) / LOG6)
    ax2.set_xlabel(r"window-mean altitude $\bar{a} = \overline{\log_6 x}$")
    ax2.set_ylabel("mean closure miss")
    ax2.set_title(f"The descent chirps through the resonances\n"
                  f"(pooled over {n_orbits} orbits): 106 → 75 → 44 → 13")
    ax2.legend(fontsize=7)
    ax2.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

    return {"dips": dips}


# ---------------------------------------------------------------- view 2

def giant_seed(min_len: int, seed: int = 17) -> tuple[int, list[int]]:
    rng = np.random.default_rng(seed)
    while True:
        n = int.from_bytes(rng.bytes(60)) | 1  # ~145-digit odd integer
        seq = orbit(n)
        if len(seq) >= min_len:
            return n, seq


def nn_index_gaps(theta: np.ndarray, n_pts: int) -> np.ndarray:
    """|index gap| to the spatial nearest neighbor, per point (radius = k)."""
    idx = np.arange(n_pts)
    ang = 2 * np.pi * theta[:n_pts]
    x = idx * np.cos(ang)
    y = idx * np.sin(ang)
    nn = np.empty(n_pts, dtype=int)
    for lo in range(0, n_pts, 500):
        hi = min(lo + 500, n_pts)
        d2 = (x[lo:hi, None] - x) ** 2 + (y[lo:hi, None] - y) ** 2
        d2[np.arange(hi - lo), np.arange(lo, hi)] = np.inf
        nn[lo:hi] = d2.argmin(1)
    return np.abs(nn - idx)


def predicted_arms(k: int) -> int:
    return min(QS, key=lambda q: q ** 2 + (2 * np.pi * k * eps(q)) ** 2)


def plot_137_arms(path: str, min_len: int = 3400) -> dict:
    n, seq = giant_seed(min_len)
    n_pts = len(seq)
    theta = np.array([(math.log(x) / LOG6) % 1.0 for x in seq])
    gaps = nn_index_gaps(theta, n_pts)

    # parastichy mode per radial band (radius = index k)
    bands = np.linspace(0, n_pts, 13).astype(int)
    centers, modes, preds = [], [], []
    for lo, hi in zip(bands[:-1], bands[1:]):
        g = gaps[lo:hi]
        vals, counts = np.unique(g, return_counts=True)
        centers.append((lo + hi) // 2)
        modes.append(int(vals[counts.argmax()]))
        preds.append(predicted_arms((lo + hi) // 2))

    fig = plt.figure(figsize=(13, 5.4))
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.plot(centers, preds, "s--", color="0.55", ms=4, lw=1,
             label=r"predicted $\arg\min_q\, q^2 + (2\pi k \epsilon_q)^2$")
    ax1.plot(centers, modes, "o-", color="crimson", ms=4, lw=1.2,
             label="observed parastichy mode")
    for q in QS:
        ax1.axhline(q, color="0.85", ls=":", lw=0.8)
        ax1.text(centers[0], q + 3, str(q), fontsize=7, color="0.4")
    ax1.set_xlabel("radial band center $k$")
    ax1.set_ylabel("visible arm count in band")
    digits = len(str(n))
    ax1.set_title(f"Giant orbit ({digits}-digit seed, {n_pts - 1} steps):\n"
                  "arms chirp 13 → 31 → 137 with radius, 106 skipped")
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.25)

    ax2 = fig.add_subplot(1, 2, 2, projection="polar")
    ax2.scatter(2 * np.pi * theta, np.arange(n_pts), s=1.0,
                c=np.arange(n_pts), cmap="viridis", alpha=0.75)
    ax2.set_yticklabels([])
    ax2.set_xticklabels([])
    outer_mode = modes[-1]
    ax2.set_title(f"$N$ = {n_pts}: outer-band arms = {outer_mode}",
                  fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

    return {"digits": digits, "steps": n_pts - 1, "centers": centers,
            "modes": modes, "preds": preds}


# ---------------------------------------------------------------- main

def main() -> None:
    r = plot_resonance("data/collatz_log6_resonance.png")
    print("closure resonances (observed dip altitude vs predicted log_6 x*):")
    for q, (obs, pred) in sorted(r["dips"].items()):
        print(f"  q = {q:4d}: dip at a = {obs:.2f}, predicted {pred:.2f}")

    g = plot_137_arms("data/collatz_log6_137_arms.png")
    print(f"\ngiant orbit: {g['digits']}-digit seed, {g['steps']} steps")
    print("  band center k : observed arms (predicted)")
    for c, mode, pred in zip(g["centers"], g["modes"], g["preds"]):
        print(f"  {c:6d}: {mode:4d} ({pred})")
    print("wrote 2 PNGs to data/")


if __name__ == "__main__":
    main()
