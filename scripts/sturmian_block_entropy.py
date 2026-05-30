"""Block-complexity / block-entropy of the dropping-set sign sequence.

The sign sequence is the Sturmian cutting sequence of slope log_2(3):
each o produces a symbol in {+, -} according to whether
{(o-1) log_2 3} ≥ 2 - log_2 3 (threshold τ ≈ 0.4150).

For a Sturmian word the factor-complexity function is exactly
        p(n) = n + 1
and the Shannon block entropy is bounded by log_2(n+1), giving
topological entropy 0. We measure both directly against a fair-coin
baseline of the same length and density.

Outputs:
    data/sturmian_block_entropy.npz
    data/sturmian_block_entropy.png
"""
from __future__ import annotations

import math
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def sign_sequence(O_max: int) -> np.ndarray:
    """Return the +1/-1 sign sequence for o = 1..O_max (length O_max)."""
    log2_3 = math.log2(3.0)
    threshold = 2.0 - log2_3
    seq = np.empty(O_max, dtype=np.int8)
    for o in range(1, O_max + 1):
        # gap_o = 3 (sign +1) iff {(o-1) log_2 3} ≥ threshold
        frac = ((o - 1) * log2_3) % 1.0
        seq[o - 1] = +1 if frac >= threshold else -1
    return seq


def block_stats(seq: np.ndarray, n: int) -> tuple[int, float]:
    """Return (#distinct length-n factors, Shannon entropy in bits)."""
    if n > len(seq):
        return 0, 0.0
    counts: Counter = Counter()
    L = len(seq)
    # Pack length-n window as bytes-of-int8 keys
    view = seq.tobytes()
    for i in range(L - n + 1):
        counts[view[i : i + n]] += 1
    total = sum(counts.values())
    p_n = len(counts)
    H_n = 0.0
    for c in counts.values():
        p = c / total
        H_n -= p * math.log2(p)
    return p_n, H_n


def return_word_stats(seq: np.ndarray, n: int) -> dict | None:
    """Justin–Vuillon return-word measurement at factor length n.

    For each distinct length-n factor u, collect all occurrence positions
    (i_1 < i_2 < ... < i_m) and define the m-1 observed return words
    r_j = w[i_j : i_{j+1}]. A factor with fewer than 2 occurrences is
    excluded (cannot observe a return).

    Returns a dict with min / max / mean of #distinct return words across
    all factors that occurred ≥ 2 times, plus counts of how many factors
    were observed and how many fall in the Sturmian "exactly 2" bucket.
    Returns None if no factor occurred twice (window too long).
    """
    if n > len(seq) - 1:
        return None
    positions: dict[bytes, list[int]] = {}
    L = len(seq)
    view = seq.tobytes()
    for i in range(L - n + 1):
        key = view[i : i + n]
        positions.setdefault(key, []).append(i)

    counts: list[int] = []
    for occs in positions.values():
        if len(occs) < 2:
            continue
        rw: set[bytes] = set()
        for i_a, i_b in zip(occs, occs[1:]):
            rw.add(view[i_a:i_b])
        counts.append(len(rw))

    if not counts:
        return None
    arr = np.asarray(counts, dtype=np.int64)
    return {
        "min": int(arr.min()),
        "max": int(arr.max()),
        "mean": float(arr.mean()),
        "n_observed": int(arr.size),
        "n_total_factors": len(positions),
        "n_factors_rw2": int((arr == 2).sum()),
    }


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(exist_ok=True)

    O_max = 20000
    n_max = 40

    seq = sign_sequence(O_max)
    plus_density = float((seq == 1).mean())
    print(f"Sequence length:    {O_max}")
    print(f"+1 density:         {plus_density:.5f}  "
          f"(theoretical: 1 - τ = log_2 3 - 1 ≈ {math.log2(3) - 1:.5f})")

    # Density-matched fair-coin baseline (Bernoulli with same +1 probability)
    rng = np.random.default_rng(20250528)
    iid = np.where(rng.random(O_max) < plus_density, 1, -1).astype(np.int8)

    ns = np.arange(1, n_max + 1)
    p_sturm = np.zeros(n_max, dtype=np.int64)
    H_sturm = np.zeros(n_max, dtype=np.float64)
    p_iid = np.zeros(n_max, dtype=np.int64)
    H_iid = np.zeros(n_max, dtype=np.float64)

    print(f"\n{'n':>3} {'p_Sturmian(n)':>15} {'n+1':>6} "
          f"{'H_Sturmian(n)':>15} {'log2(n+1)':>12} "
          f"{'p_iid(n)':>10} {'H_iid(n)':>10}")
    print("-" * 90)
    for n in ns:
        p_s, H_s = block_stats(seq, int(n))
        p_i, H_i = block_stats(iid, int(n))
        p_sturm[n - 1] = p_s
        H_sturm[n - 1] = H_s
        p_iid[n - 1] = p_i
        H_iid[n - 1] = H_i
        match = "✓" if p_s == n + 1 else "✗"
        print(f"{n:>3d} {p_s:>15d} {n + 1:>6d} {H_s:>15.5f} "
              f"{math.log2(n + 1):>12.5f} {p_i:>10d} {H_i:>10.5f}  {match}")

    # ---------- Return-word measurement (Justin–Vuillon) ----------
    print(f"\n--- Return-word counts (Sturmian iff every factor has exactly 2) ---")
    print(f"{'n':>3} "
          f"{'sign:min':>9} {'sign:max':>9} {'sign:mean':>10} {'sign:obs':>9} "
          f"{'iid:min':>9} {'iid:max':>9} {'iid:mean':>10} {'iid:obs':>9}  fingerprint")
    print("-" * 105)
    rw_sign_min = np.zeros(n_max, dtype=np.int64)
    rw_sign_max = np.zeros(n_max, dtype=np.int64)
    rw_sign_mean = np.zeros(n_max, dtype=np.float64)
    rw_iid_min = np.zeros(n_max, dtype=np.int64)
    rw_iid_max = np.zeros(n_max, dtype=np.int64)
    rw_iid_mean = np.zeros(n_max, dtype=np.float64)
    sturmian_holds = []
    for n in ns:
        rs = return_word_stats(seq, int(n))
        ri = return_word_stats(iid, int(n))
        if rs is None:
            continue
        rw_sign_min[n - 1] = rs["min"]
        rw_sign_max[n - 1] = rs["max"]
        rw_sign_mean[n - 1] = rs["mean"]
        if ri is not None:
            rw_iid_min[n - 1] = ri["min"]
            rw_iid_max[n - 1] = ri["max"]
            rw_iid_mean[n - 1] = ri["mean"]
        is_sturm = rs["min"] == 2 and rs["max"] == 2
        sturmian_holds.append(is_sturm)
        flag = "✓ exactly 2" if is_sturm else f"✗ range [{rs['min']},{rs['max']}]"
        iid_str = (f"{ri['min']:>9d} {ri['max']:>9d} {ri['mean']:>10.3f} {ri['n_observed']:>9d}"
                   if ri is not None else f"{'—':>9} {'—':>9} {'—':>10} {'—':>9}")
        print(f"{n:>3d} "
              f"{rs['min']:>9d} {rs['max']:>9d} {rs['mean']:>10.3f} {rs['n_observed']:>9d} "
              f"{iid_str}  {flag}")

    np.savez(
        out_dir / "sturmian_block_entropy.npz",
        n=ns, p_sturm=p_sturm, H_sturm=H_sturm,
        p_iid=p_iid, H_iid=H_iid,
        rw_sign_min=rw_sign_min, rw_sign_max=rw_sign_max, rw_sign_mean=rw_sign_mean,
        rw_iid_min=rw_iid_min, rw_iid_max=rw_iid_max, rw_iid_mean=rw_iid_mean,
        plus_density=plus_density, O_max=O_max,
    )

    # ---------- Plotting ----------
    fig, axes = plt.subplots(4, 1, figsize=(11, 14))

    # Plot 1: complexity p(n) vs n
    ax = axes[0]
    ax.plot(ns, ns + 1, color="black", ls="--", lw=1,
            label=r"Sturmian prediction $p(n) = n+1$")
    ax.scatter(ns, p_sturm, c="C0", s=50, edgecolor="black", linewidth=0.5,
               label="measured (sign sequence)")
    ax.scatter(ns, p_iid, c="C3", marker="x", s=50,
               label="i.i.d. coin baseline")
    ax.set_yscale("log")
    ax.set_xlabel("window size n")
    ax.set_ylabel("# distinct length-n factors")
    ax.set_title(r"Factor complexity $p(n)$ — Sturmian fingerprint is exactly $n+1$")
    ax.legend()
    ax.grid(alpha=0.3, which="both")

    # Plot 2: Shannon block entropy H(n) vs n
    ax = axes[1]
    ax.plot(ns, np.log2(ns + 1), color="black", ls="--", lw=1,
            label=r"$\log_2(n+1)$ (Sturmian upper bound)")
    ax.scatter(ns, H_sturm, c="C0", s=50, edgecolor="black", linewidth=0.5,
               label="measured (sign sequence)")
    ax.scatter(ns, H_iid, c="C3", marker="x", s=50,
               label="i.i.d. coin baseline")
    # i.i.d. theoretical entropy is n * H(p)
    p = plus_density
    h1 = -p * math.log2(p) - (1 - p) * math.log2(1 - p)
    ax.plot(ns, ns * h1, color="C3", ls=":", lw=1,
            label=fr"i.i.d. theory: $n \cdot h({p:.3f}) = {h1:.4f} n$")
    ax.set_xlabel("window size n")
    ax.set_ylabel(r"$H(n)$  (bits)")
    ax.set_title("Shannon block entropy")
    ax.legend()
    ax.grid(alpha=0.3)

    # Plot 3: per-symbol entropy rate H(n)/n
    ax = axes[2]
    ax.axhline(0, color="black", lw=0.5)
    ax.axhline(h1, color="C3", ls=":", lw=1,
               label=fr"i.i.d. limit $h({p:.3f}) \approx {h1:.4f}$")
    ax.scatter(ns, H_sturm / ns, c="C0", s=50, edgecolor="black", linewidth=0.5,
               label="sign sequence: $H(n)/n$")
    ax.scatter(ns, H_iid / ns, c="C3", marker="x", s=50,
               label="i.i.d. baseline: $H(n)/n$")
    ax.plot(ns, np.log2(ns + 1) / ns, color="black", ls="--", lw=1,
            label=r"$\log_2(n+1)/n \to 0$")
    ax.set_xlabel("window size n")
    ax.set_ylabel(r"$H(n) / n$  (bits/symbol)")
    ax.set_title("Per-symbol entropy rate — Sturmian sequence has topological entropy 0")
    ax.legend(loc="center right")
    ax.grid(alpha=0.3)
    ax.set_ylim(-0.02, max(h1 * 1.1, 1.05))

    # Plot 4: return-word counts (Justin–Vuillon characterization)
    ax = axes[3]
    ax.axhline(2, color="black", ls="--", lw=1,
               label="Sturmian prediction: exactly 2 return words for every factor")
    # Sign sequence: min and max coincide at 2 if Sturmian
    ax.scatter(ns, rw_sign_max, c="C0", s=50, edgecolor="black", linewidth=0.5,
               label="sign sequence: max distinct return words")
    ax.scatter(ns, rw_sign_min, c="C0", marker="v", s=30,
               label="sign sequence: min distinct return words")
    # i.i.d. — max grows
    iid_valid = rw_iid_max > 0
    ax.scatter(ns[iid_valid], rw_iid_max[iid_valid], c="C3", marker="x", s=50,
               label="i.i.d. baseline: max distinct return words")
    ax.scatter(ns[iid_valid], rw_iid_min[iid_valid], c="C3", marker="+", s=50,
               label="i.i.d. baseline: min distinct return words")
    ax.set_yscale("log")
    ax.set_xlabel("factor length n")
    ax.set_ylabel("# distinct return words")
    ax.set_title("Return-word count per factor (Justin–Vuillon Sturmian fingerprint)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(alpha=0.3, which="both")

    fig.tight_layout()
    out_png = out_dir / "sturmian_block_entropy.png"
    fig.savefig(out_png, dpi=120)
    print(f"\nSaved {out_png}")

    # Summary
    print("\n=== Summary ===")
    matches = int(np.sum(p_sturm == ns + 1))
    print(f"p(n) = n+1 holds for {matches} / {n_max} window sizes "
          f"(Sturmian iff equality at every n)")
    if matches == n_max:
        print(f"  ✓ Exact Sturmian factor-complexity fingerprint over n = 1..{n_max}.")
    else:
        bad = ns[p_sturm != ns + 1]
        print(f"  ✗ Deviations at n = {bad.tolist()}")

    n_measured_rw = int(sum(1 for m, M in zip(rw_sign_min, rw_sign_max) if M > 0))
    rw_strict = int(sum(
        1 for m, M in zip(rw_sign_min, rw_sign_max) if M > 0 and m == 2 and M == 2
    ))
    print(f"Return-word count = 2 for every factor at {rw_strict} / {n_measured_rw} "
          f"measurable window sizes (Justin–Vuillon characterization)")
    if rw_strict == n_measured_rw and n_measured_rw > 0:
        print("  ✓ Justin–Vuillon Sturmian fingerprint confirmed independently of factor complexity.")
    else:
        bad = [int(n) for n, m, M in zip(ns, rw_sign_min, rw_sign_max)
               if M > 0 and (m != 2 or M != 2)]
        print(f"  ✗ Deviations at n = {bad} — Part 5 proof has a hole to chase.")


if __name__ == "__main__":
    main()
