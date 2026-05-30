"""Three controls for the Part 8 stopping-class parity result.

Tests three orthogonal hypotheses about where the entropy lives:

  (1) Bernoulli equidistribution — chi-square test on length-n block
      frequencies of the irrational mod-2 sequence against the uniform
      null. Confirms or denies "indistinguishable from a fair coin."

  (2) Higher-radix structure — complexity fingerprint of {P_o mod 3}.
      If GF(2) is hiding Eisenstein-side arithmetic, mod 3 should land
      lower than max ternary entropy. If randomness is intrinsic, mod 3
      will also saturate at 3^n complexity.

  (3) Rational-slope controls — replace floor(j log_2 3) with
      floor(j p/q) for two rationals: (C) the crude convergent 3/2, and
      (D) the deep musical convergent 19/12. Cobham says any "automatic"
      structure inherited from rational slope would give factor
      complexity p(n) = O(n), not 2^n.

Outputs:
    data/stopping_class_controls.npz
    data/stopping_class_controls.png
"""
from __future__ import annotations

import math
import sys
from collections import Counter
from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stopping_class_block_entropy import block_stats, return_word_stats  # noqa: E402

LOG2_3 = math.log2(3.0)


def make_irrational(slope: float) -> Callable[[int], int]:
    return lambda j: int(math.floor(j * slope))


def make_rational(p: int, q: int) -> Callable[[int], int]:
    return lambda j: (j * p) // q


def compute_P_mod_m(O_max: int, m: int, B_func: Callable[[int], int]) -> np.ndarray:
    """P_o mod m via Beatty-bounded path DP with custom boundary B_func."""
    parities = np.zeros(O_max, dtype=np.int8)
    parities[0] = 1 % m  # P_1 = 1
    f = np.array([1], dtype=np.int64)
    B_prev = 0

    for j in range(1, O_max):
        B_j = B_func(j)
        cumf = np.zeros(len(f) + 1, dtype=np.int64)
        cumf[1:] = np.cumsum(f) % m

        new_f = np.zeros(B_j + 1, dtype=np.int64)
        lo = j - 1
        if lo <= B_prev:
            S_range = np.arange(j, B_j + 1)
            hi = np.minimum(B_prev, S_range - 1)
            valid = hi >= lo
            valid_S = S_range[valid]
            valid_hi = hi[valid]
            new_f[valid_S] = (cumf[valid_hi + 1] - cumf[lo]) % m

        if len(new_f) > 0:
            parities[j] = int(np.sum(new_f) % m)
        f = new_f
        B_prev = B_j

    return parities


def to_symbol_seq(par: np.ndarray, m: int) -> np.ndarray:
    """Convert {0,...,m-1}-valued sequence into bytes-compatible int8."""
    if m == 2:
        return np.where(par == 1, 1, -1).astype(np.int8)
    return par.astype(np.int8)


def chi_square_uniform(seq: np.ndarray, n: int, alphabet_size: int) -> dict:
    """Chi-square statistic for length-n block frequencies vs the uniform null.

    Returns dict with chi2, df, ratio, z (large-df normal approx of
    (chi2 - df) / sqrt(2 df)), distinct factors seen, and total bins.
    """
    counts: Counter = Counter()
    L = len(seq)
    view = seq.tobytes()
    for i in range(L - n + 1):
        counts[view[i : i + n]] += 1
    total = sum(counts.values())
    n_bins = alphabet_size ** n
    if n_bins == 0 or total == 0:
        return {"chi2": 0, "df": 0, "ratio": 0, "z": 0,
                "distinct": 0, "n_bins": n_bins, "total": total}
    E = total / n_bins
    sum_sq = sum((c - E) ** 2 for c in counts.values())
    n_unseen = n_bins - len(counts)
    chi2 = (sum_sq + n_unseen * E * E) / E
    df = n_bins - 1
    z = (chi2 - df) / math.sqrt(2 * df) if df > 0 else 0.0
    return {"chi2": chi2, "df": df, "ratio": chi2 / df, "z": z,
            "distinct": len(counts), "n_bins": n_bins, "total": total}


def run_probe(name: str, par: np.ndarray, m: int,
              n_max: int = 30, chi2_n_max: int = 12) -> dict:
    seq = to_symbol_seq(par, m)
    L = len(seq)
    print(f"\n=== {name} ===")
    densities = [(par == d).mean() for d in range(m)]
    print(f"  length            : {L}")
    print(f"  symbol density    : " +
          ", ".join(f"≡{d}→{densities[d]:.4f}" for d in range(m)))

    ns = np.arange(1, n_max + 1)
    p_arr = np.zeros(n_max, dtype=np.int64)
    H_arr = np.zeros(n_max, dtype=np.float64)
    for n in ns:
        p_arr[n - 1], H_arr[n - 1] = block_stats(seq, int(n))

    print(f"  factor complexity :")
    print(f"    {'n':>3} {'p(n)':>9} {'m^n':>12} {'p / m^n':>10}")
    for n in [1, 3, 5, 8, 11, 14, 20, n_max]:
        if n > n_max:
            continue
        target = m ** n
        ratio = p_arr[n - 1] / target
        tgt_s = f"{target:>12d}" if target < 1e10 else f"{target:>12.1e}"
        print(f"    {n:>3d} {p_arr[n-1]:>9d} {tgt_s} {ratio:>10.4f}")

    print(f"  chi^2/df vs uniform null (m={m}):")
    print(f"    {'n':>3} {'chi2/df':>10} {'z':>10} {'distinct':>10} {'/bins':>10}")
    chi2_results: dict[int, dict] = {}
    # Cap chi2 n at a value where expected count per bin is at least ~3
    actual_max = chi2_n_max
    for n in range(1, chi2_n_max + 1):
        if m ** n > L / 3:
            actual_max = n - 1
            break
    for n in range(1, actual_max + 1):
        cs = chi_square_uniform(seq, n, m)
        chi2_results[n] = cs
        print(f"    {n:>3d} {cs['ratio']:>10.4f} {cs['z']:>10.2f} "
              f"{cs['distinct']:>10d} {cs['n_bins']:>10d}")

    # Return-word check at a few n's
    print(f"  return-word counts at selected n:")
    rw_table = []
    for n in [2, 4, 6, 8, 10]:
        rs = return_word_stats(seq, n)
        if rs is None:
            continue
        rw_table.append((n, rs))
        flag = "✓ =2" if rs["min"] == 2 and rs["max"] == 2 else f"✗ [{rs['min']},{rs['max']}]"
        print(f"    n={n:>2d}: min={rs['min']:>4d}, max={rs['max']:>4d}, "
              f"mean={rs['mean']:>6.2f}, obs={rs['n_observed']:>5d}  {flag}")

    return {
        "name": name, "m": m, "ns": ns,
        "p_arr": p_arr, "H_arr": H_arr,
        "chi2": chi2_results, "densities": densities,
        "rw_table": rw_table, "parities": par, "seq": seq,
    }


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(exist_ok=True)

    O_max = 20000
    n_max = 30

    print(f"Stopping-class parity controls — O_max = {O_max}\n")

    # (A) Baseline: irrational log_2 3, mod 2 (re-verify Part 8)
    parA = compute_P_mod_m(O_max, 2, make_irrational(LOG2_3))
    assert parA[:8].tolist() == [1, 1, 0, 1, 1, 0, 0, 1], "P mod 2 sanity check failed"
    A = run_probe("(A) irrational log_2(3), mod 2  [Part 8 baseline]", parA, 2, n_max)

    # (B) Higher-radix: irrational mod 3
    parB = compute_P_mod_m(O_max, 3, make_irrational(LOG2_3))
    expected_B = [1, 1, 2, 0, 1, 0, 0, 1]  # P = 1,1,2,3,7,12,30,85
    assert parB[:8].tolist() == expected_B, f"P mod 3 sanity failed: got {parB[:8].tolist()}"
    B = run_probe("(B) irrational log_2(3), mod 3", parB, 3, n_max, chi2_n_max=8)

    # (C) Crude rational 3/2, mod 2 — large divergence from log_2 3
    parC = compute_P_mod_m(O_max, 2, make_rational(3, 2))
    C = run_probe("(C) rational slope 3/2, mod 2  [crude CF convergent]", parC, 2, n_max)

    # (D) Deep convergent 19/12, mod 2 — agrees with irrational at low j
    parD = compute_P_mod_m(O_max, 2, make_rational(19, 12))
    D = run_probe("(D) rational slope 19/12, mod 2  [deep CF convergent / 12-TET]",
                  parD, 2, n_max)

    # Detect convergent regime: how long does D agree with A?
    diverge_idx = int(np.argmax(parA != parD)) if not np.array_equal(parA, parD) else O_max
    print(f"\n  (A) vs (D) parities first differ at o = {diverge_idx}")

    # Save
    np.savez(
        out_dir / "stopping_class_controls.npz",
        n=A["ns"],
        parA=parA, parB=parB, parC=parC, parD=parD,
        pA=A["p_arr"], HA=A["H_arr"],
        pB=B["p_arr"], HB=B["H_arr"],
        pC=C["p_arr"], HC=C["H_arr"],
        pD=D["p_arr"], HD=D["H_arr"],
        diverge_AD=diverge_idx,
    )

    # ---------- Plotting ----------
    fig, axes = plt.subplots(2, 1, figsize=(11, 9))

    ax = axes[0]
    ax.plot(A["ns"], A["ns"] + 1, color="black", ls="--", lw=1,
            label=r"Sturmian: $n+1$")
    binary_cap = np.minimum(2.0 ** A["ns"], float(O_max))
    ternary_cap = np.minimum(3.0 ** A["ns"], float(O_max))
    ax.plot(A["ns"], binary_cap, color="gray", ls=":", lw=1,
            label=r"binary max $\min(2^n, L)$")
    ax.plot(A["ns"], ternary_cap, color="olive", ls=":", lw=1,
            label=r"ternary max $\min(3^n, L)$")
    ax.scatter(A["ns"], A["p_arr"], c="C0", s=40, edgecolor="black", linewidth=0.5,
               label="(A) irrational, mod 2")
    ax.scatter(B["ns"], B["p_arr"], c="C2", s=40, marker="s",
               edgecolor="black", linewidth=0.5,
               label="(B) irrational, mod 3")
    ax.scatter(C["ns"], C["p_arr"], c="C3", s=40, marker="^",
               edgecolor="black", linewidth=0.5,
               label="(C) rational 3/2, mod 2")
    ax.scatter(D["ns"], D["p_arr"], c="C4", s=40, marker="D",
               edgecolor="black", linewidth=0.5,
               label=f"(D) rational 19/12, mod 2  (A=D until o={diverge_idx})")
    ax.set_yscale("log")
    ax.set_ylim(1, max(O_max * 1.5, 2 ** 15))
    ax.set_xlabel("window size n")
    ax.set_ylabel("# distinct length-n factors")
    ax.set_title(r"Factor complexity $p(n)$ across the four controls")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(alpha=0.3, which="both")

    ax = axes[1]
    ax.axhline(1.0, color="black", ls="--", lw=1, label="Bernoulli null χ²/df = 1")
    for probe, color, marker, label in [
        (A, "C0", "o", "(A) irrational, mod 2"),
        (C, "C3", "^", "(C) rational 3/2, mod 2"),
        (D, "C4", "D", "(D) rational 19/12, mod 2"),
    ]:
        ns_chi = sorted(probe["chi2"].keys())
        if not ns_chi:
            continue
        ratios = [probe["chi2"][n]["ratio"] for n in ns_chi]
        ax.plot(ns_chi, ratios, marker=marker, color=color, lw=1.5, label=label)
    ax.set_yscale("log")
    ax.set_xlabel("block length n")
    ax.set_ylabel(r"$\chi^2 / \mathrm{df}$  (log scale)")
    ax.set_title("Chi-square against uniform null — mod-2 sequences")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3, which="both")

    fig.subplots_adjust(hspace=0.35, left=0.08, right=0.97, top=0.95, bottom=0.06)
    out_png = out_dir / "stopping_class_controls.png"
    fig.savefig(out_png, dpi=120, bbox_inches="tight")
    print(f"\nSaved {out_png}")

    # ---------- Verdict ----------
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    for probe in [A, B, C, D]:
        m = probe["m"]
        ns = probe["ns"]
        p_arr = probe["p_arr"]
        # Where does p(n) fall off the max-complexity curve?
        max_n = max([int(n) for n in ns if p_arr[n - 1] >= 0.99 * min(m ** n, O_max - n + 1)],
                    default=0)
        last_chi2 = max(probe["chi2"].keys()) if probe["chi2"] else 0
        cs = probe["chi2"].get(last_chi2, {})
        ratio = cs.get("ratio", float("nan"))
        z = cs.get("z", float("nan"))
        print(f"\n  {probe['name']}")
        print(f"    p(n) hits max-complexity envelope up to n = {max_n}")
        print(f"    chi^2/df at n={last_chi2}: {ratio:.4f}  (z = {z:+.2f})")


if __name__ == "__main__":
    main()
