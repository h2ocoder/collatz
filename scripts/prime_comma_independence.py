"""The archimedean twin of the Prime Dropping Residues exploration.

There are exactly two choice-free ways the primes 2 and 3 can "see" a
prime p: through residues (p mod 2^k, 3^k — additive, local, the world
of dropping sets and Dirichlet) and through size (theta_p = frac(log_6 p)
— the choice-free content of every Ryan-style 2-3 comma assignment, a
generalized leading-digit / Benford coordinate).  The Prime Dropping
Residues exploration showed the residue side is pure Dirichlet.  This
script tests the archimedean side and the independence of the two.

Predictions (from the log-6 duality, findings 5/14):

  P1  theta_p over primes is "equidistributed" once the trivial shape is
      removed: the raw histogram is tilted by (i) the exponential 6^theta
      crowding of integers within each band [6^m, 6^{m+1}) and (ii) the
      1/log p prime density and the truncation at N.  An analytic PNT
      model with NO free parameters should explain the histogram fully.
  P2  Dropping time (2-adic head data) is independent of theta_p
      (archimedean scale data): MI at the shuffled-null level, flat mean
      dropping time across theta bins.  Matched next-odd-composite
      controls should behave identically — primality adds nothing.
  P3  Gateway landmark vs theta_p: NOT independent — but the dependence
      is an INTEGER phenomenon, not a prime one (matched composites show
      it at least as strongly).  Mechanism: rigid rotation transport,
      theta(gateway) = theta_n + k*alpha + W (mod 1) exactly; with
      step-count spread of only ~44, k*alpha does not fully decohere
      the circle, so the tail faintly remembers the archimedean head.
      Together with finding 14 (gateway forgets the 2-adic head), the
      invariants correlate only within their own completion of Q.

Outputs:
    data/prime_comma_independence.png
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
N_MAIN = 10 ** 7
N_GATE = 10 ** 6
N_THETA_BINS = 12


def sieve(n: int) -> np.ndarray:
    is_p = np.ones(n + 1, dtype=bool)
    is_p[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if is_p[i]:
            is_p[i * i:: i] = False
    return is_p


def theta_of(arr: np.ndarray) -> np.ndarray:
    return (np.log(arr.astype(float)) / LOG6) % 1.0


def expected_prime_hist(bins: np.ndarray, n_max: int) -> np.ndarray:
    """Analytic null: integral of 1/ln x over each theta-bin's bands."""
    exp_counts = np.zeros(len(bins) - 1)
    m_max = int(math.log(n_max) / LOG6) + 1
    for b in range(len(bins) - 1):
        for m in range(m_max + 1):
            lo = 6.0 ** (m + bins[b])
            hi = min(6.0 ** (m + bins[b + 1]), float(n_max))
            if hi <= max(lo, 3.0):
                continue
            xs = np.geomspace(max(lo, 3.0), hi, 200)
            exp_counts[b] += np.trapezoid(1.0 / np.log(xs), xs)
    return exp_counts


def mutual_info_bits(table: np.ndarray) -> float:
    p = table / table.sum()
    pi = p.sum(1, keepdims=True)
    pj = p.sum(0, keepdims=True)
    mask = p > 0
    return float((p[mask] * np.log2(p[mask] / (pi @ pj)[mask])).sum())


def mi_vs_null(codes_a: np.ndarray, codes_b: np.ndarray,
               rng: np.random.Generator, n_shuffles: int = 20) -> dict:
    na, nb = codes_a.max() + 1, codes_b.max() + 1
    table = np.zeros((na, nb))
    np.add.at(table, (codes_a, codes_b), 1)
    mi = mutual_info_bits(table)
    nulls = []
    for _ in range(n_shuffles):
        t0 = np.zeros_like(table)
        np.add.at(t0, (rng.permutation(codes_a), codes_b), 1)
        nulls.append(mutual_info_bits(t0))
    return {"mi": mi, "null": float(np.mean(nulls)),
            "sd": float(np.std(nulls)),
            "z": (mi - np.mean(nulls)) / np.std(nulls)}


def gateway_of(n: int) -> int:
    return next(x for x in orbit(n) if x % 2 == 1 and x < 100)


def main() -> None:
    rng = np.random.default_rng(42)
    print(f"sieving to {N_MAIN:.0e} ...")
    is_p = sieve(N_MAIN)
    primes = np.flatnonzero(is_p)
    primes = primes[primes >= 3]
    print(f"{len(primes)} odd primes")

    theta_p = theta_of(primes)

    # matched controls: next odd composite after each prime
    print("building matched odd-composite controls ...")
    controls = []
    for p in primes:
        q = p + 2
        while q <= N_MAIN and is_p[q]:
            q += 2
        controls.append(q if q <= N_MAIN else p - 2)
    controls = np.array(controls)

    print("computing dropping times ...")
    k_p = np.array([dropping_time(int(p)) for p in primes])
    k_c = np.array([dropping_time(int(q)) for q in controls])

    # P1: theta histogram vs analytic PNT null
    bins = np.linspace(0, 1, 41)
    obs, _ = np.histogram(theta_p, bins=bins)
    exp = expected_prime_hist(bins, N_MAIN)
    exp *= obs.sum() / exp.sum()
    chi2_p1 = float((((obs - exp) ** 2) / exp).sum())

    # P2: MI(theta bin; dropping time), primes and controls
    tcodes = np.minimum((theta_p * N_THETA_BINS).astype(int), N_THETA_BINS - 1)
    tcodes_c = np.minimum((theta_of(controls) * N_THETA_BINS).astype(int),
                          N_THETA_BINS - 1)
    _, kcode = np.unique(np.minimum(k_p, 30), return_inverse=True)
    _, kcode_c = np.unique(np.minimum(k_c, 30), return_inverse=True)
    mi_primes = mi_vs_null(tcodes, kcode, rng)
    mi_ctrl = mi_vs_null(tcodes_c, kcode_c, rng)

    # P3: gateway vs theta, primes in [1e4, 1e6] vs matched odd composites
    # (cutoff removes the trivial p < 100 "gateway = p" coupling)
    print("computing gateways for primes and composites in [1e4, 1e6] ...")
    odd = np.arange(10 ** 4 + 1, N_GATE, 2)
    small = odd[is_p[odd]]
    comp = odd[~is_p[odd]]
    comp = rng.choice(comp, size=len(small), replace=False)

    def gate_mi(ns: np.ndarray) -> dict:
        gates = np.array([gateway_of(int(n)) for n in ns])
        _, gcode = np.unique(gates, return_inverse=True)
        tsm = np.minimum((theta_of(ns) * N_THETA_BINS).astype(int),
                         N_THETA_BINS - 1)
        return mi_vs_null(tsm, gcode, rng)

    mi_gate = gate_mi(small)
    mi_gate_c = gate_mi(comp)

    # ------------------------------------------------------------ figure
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
    mids = 0.5 * (bins[:-1] + bins[1:])
    axes[0].bar(mids, obs, width=bins[1] - bins[0], color="darkslateblue",
                alpha=0.8, label="primes $\\leq 10^7$")
    axes[0].plot(mids, exp, "r-", lw=1.5,
                 label="analytic PNT null (no free params)")
    axes[0].set_xlabel(r"comma coordinate $\theta_p = \{\log_6 p\}$")
    axes[0].set_ylabel("count")
    axes[0].set_title(f"P1: shape fully explained by density + truncation\n"
                      f"$\\chi^2$ = {chi2_p1:.0f} on {len(mids) - 1} bins")
    axes[0].legend(fontsize=8)

    tb = np.arange(N_THETA_BINS)
    mean_k = [k_p[tcodes == b].mean() for b in tb]
    se_k = [2 * k_p[tcodes == b].std() / math.sqrt((tcodes == b).sum())
            for b in tb]
    axes[1].errorbar(tb / N_THETA_BINS + 0.5 / N_THETA_BINS, mean_k,
                     yerr=se_k, fmt="o-", ms=4, lw=1, color="crimson",
                     capsize=3)
    axes[1].axhline(k_p.mean(), color="0.6", lw=0.8)
    axes[1].set_xlabel(r"$\theta_p$ bin")
    axes[1].set_ylabel("mean dropping time $\\pm$ 2SE")
    axes[1].set_title("P2: dropping time is flat across the comma coordinate")

    labels = ["primes:\ndropping", "composites:\ndropping",
              "primes:\ngateway", "composites:\ngateway"]
    zs = [mi_primes["z"], mi_ctrl["z"], mi_gate["z"], mi_gate_c["z"]]
    axes[2].bar(range(4), zs,
                color=["crimson", "0.6", "crimson", "0.6"], alpha=0.85)
    axes[2].axhline(2, color="0.5", ls=":", lw=0.8)
    axes[2].axhline(-2, color="0.5", ls=":", lw=0.8)
    axes[2].set_xticks(range(4))
    axes[2].set_xticklabels(labels, fontsize=8)
    axes[2].set_ylabel("MI excess over shuffled null ($\\sigma$)")
    axes[2].set_title("P2: dropping $\\perp$ $\\theta$ (both null).  "
                      "P3: gateway $\\leftrightarrow$ $\\theta$ —\nbut for "
                      "composites too: rotation transport, not primality")
    fig.tight_layout()
    fig.savefig("data/prime_comma_independence.png", dpi=150)
    plt.close(fig)

    print(f"\nP1: theta histogram vs analytic null: chi2 = {chi2_p1:.1f} "
          f"on {len(mids) - 1} dof")
    for name, r in (("primes MI(theta; dropping)", mi_primes),
                    ("controls MI(theta; dropping)", mi_ctrl),
                    ("primes [1e4,1e6] MI(theta; gateway)", mi_gate),
                    ("composites [1e4,1e6] MI(theta; gateway)", mi_gate_c)):
        print(f"{name}: {r['mi']:.5f} bits vs null {r['null']:.5f} "
              f"+/- {r['sd']:.5f}  (z = {r['z']:+.1f})")
    print("wrote data/prime_comma_independence.png")


if __name__ == "__main__":
    main()
