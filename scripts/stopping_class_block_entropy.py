"""Block-complexity / return-word fingerprint of the Stopping Class parity sequence.

Background
----------
Part 5 proved the dropping-class sign rule: c_2 - c_1 = epsilon_o * A_o, where
epsilon_o is the Sturmian gap-symbol (proved in Part 5) and A_o is a Beatty-
bounded lattice-path count with closed recursion A_{o+1} = (P_o + sigma_o A_o)/2.

The Parity Lemma of Part 5 gives A_o = P_o (mod 2) where P_o is the number of
distinct parity classes in R_{k_o} — equivalently, Paper 2's Stopping Modulus
for the class at time k_o. So the binary sequence

    s_o := P_o mod 2  (o = 1, 2, ...)

is intrinsic to Paper 2's stopping classification and is NOT trivially fixed
by the dropping sign rule.

Question
--------
Does {P_o mod 2} land in the Sturmian complexity class, like the dropping sign
itself? Or does it have richer structure (linear with higher slope, k-automatic,
quasi-random)?

  * Positive answer (Sturmian): universality across Paper 1 ↔ Paper 2.
  * Negative answer: a *richer* intrinsic probe lives on the stopping side
    than on the dropping side, suggesting a non-trivial L-function-like
    object lives in the Stopping framework that the Dropping framework hides.

Computation
-----------
P_o = sum_T N(o-1, T) where N(j, S) is the count of Beatty-bounded paths of
length j ending at S. The recursion N(j, S) = sum_{prev in [j-1, min(B_{j-1},
S-1)]} N(j-1, prev) lifts to GF(2) by replacing addition with XOR. We track
f[S] := N(j, S) mod 2 directly, giving an O(O_max^2) algorithm with no
big-integer cost.

Outputs:
    data/stopping_class_block_entropy.npz
    data/stopping_class_block_entropy.png
"""
from __future__ import annotations

import math
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def compute_P_parity(O_max: int) -> np.ndarray:
    """Compute P_o mod 2 for o = 1..O_max using GF(2) Beatty-bounded path DP.

    Returns an array of length O_max with values in {0, 1}.
    """
    parities = np.zeros(O_max, dtype=np.int8)
    parities[0] = 1  # P_1 = 1
    B_prev = 0
    f = np.array([1], dtype=np.int8)
    log2_3 = math.log2(3.0)

    for j in range(1, O_max):
        B_j = int(math.floor(j * log2_3))
        # XOR prefix-sum of f: cumf[i] = XOR of f[0..i-1]
        cumf = np.zeros(len(f) + 1, dtype=np.int8)
        cumf[1:] = np.bitwise_xor.accumulate(f)

        new_f = np.zeros(B_j + 1, dtype=np.int8)
        lo = j - 1
        if lo <= B_prev:
            S_range = np.arange(j, B_j + 1)
            hi = np.minimum(B_prev, S_range - 1)
            valid = hi >= lo
            valid_S = S_range[valid]
            valid_hi = hi[valid]
            # GF(2): sum of f[lo..hi] = cumf[hi+1] XOR cumf[lo]
            new_f[valid_S] = cumf[valid_hi + 1] ^ cumf[lo]

        if len(new_f) > 0:
            parities[j] = int(np.bitwise_xor.reduce(new_f))
        f = new_f
        B_prev = B_j

    return parities


def block_stats(seq: np.ndarray, n: int) -> tuple[int, float]:
    """Return (#distinct length-n factors, Shannon entropy in bits)."""
    if n > len(seq):
        return 0, 0.0
    counts: Counter = Counter()
    L = len(seq)
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

    A factor with fewer than 2 occurrences is excluded. Returns dict with
    min / max / mean of #distinct return words across observed factors,
    or None if no factor occurs at least twice.
    """
    if n > len(seq) - 1:
        return None
    positions: dict[bytes, list[int]] = {}
    L = len(seq)
    view = seq.tobytes()
    for i in range(L - n + 1):
        positions.setdefault(view[i : i + n], []).append(i)
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
    }


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(exist_ok=True)

    O_max = 20000
    n_max = 40

    print(f"Computing P_o mod 2 for o = 1..{O_max} ...")
    parities = compute_P_parity(O_max)
    print(f"Sanity check (P_1..P_8 mod 2):")
    print(f"  expected: [1, 1, 0, 1, 1, 0, 0, 1]   (since P = 1,1,2,3,7,12,30,85)")
    print(f"  computed: {parities[:8].tolist()}")
    assert parities[:8].tolist() == [1, 1, 0, 1, 1, 0, 0, 1], "P_o parity mismatch!"

    seq = np.where(parities == 1, 1, -1).astype(np.int8)
    plus_density = float((seq == 1).mean())
    print(f"\nSequence length:    {O_max}")
    print(f"+1 density:         {plus_density:.5f}")

    rng = np.random.default_rng(20250528)
    iid = np.where(rng.random(O_max) < plus_density, 1, -1).astype(np.int8)

    ns = np.arange(1, n_max + 1)
    p_seq = np.zeros(n_max, dtype=np.int64)
    H_seq = np.zeros(n_max, dtype=np.float64)
    p_iid = np.zeros(n_max, dtype=np.int64)
    H_iid = np.zeros(n_max, dtype=np.float64)

    print(f"\n--- Factor complexity p(n) ---")
    print(f"{'n':>3} {'p_seq':>10} {'n+1':>6} {'fit':>6} "
          f"{'H_seq':>10} {'log2(n+1)':>11} {'p_iid':>10} {'H_iid':>10}")
    print("-" * 90)
    for n in ns:
        ps, Hs = block_stats(seq, int(n))
        pi, Hi = block_stats(iid, int(n))
        p_seq[n - 1], H_seq[n - 1] = ps, Hs
        p_iid[n - 1], H_iid[n - 1] = pi, Hi
        flag = "n+1" if ps == n + 1 else ("2n+1" if ps == 2 * n + 1 else f"p≠n+1")
        print(f"{n:>3d} {ps:>10d} {n + 1:>6d} {flag:>6} "
              f"{Hs:>10.5f} {math.log2(n + 1):>11.5f} {pi:>10d} {Hi:>10.5f}")

    print(f"\n--- Return-word counts ---")
    print(f"{'n':>3} {'min':>5} {'max':>6} {'mean':>8} {'obs':>6} "
          f"{'iid:min':>9} {'iid:max':>9}  Sturmian?")
    print("-" * 80)
    rw_min = np.zeros(n_max, dtype=np.int64)
    rw_max = np.zeros(n_max, dtype=np.int64)
    rw_mean = np.zeros(n_max, dtype=np.float64)
    rw_iid_min = np.zeros(n_max, dtype=np.int64)
    rw_iid_max = np.zeros(n_max, dtype=np.int64)

    for n in ns:
        rs = return_word_stats(seq, int(n))
        ri = return_word_stats(iid, int(n))
        if rs is None:
            continue
        rw_min[n - 1] = rs["min"]
        rw_max[n - 1] = rs["max"]
        rw_mean[n - 1] = rs["mean"]
        if ri is not None:
            rw_iid_min[n - 1] = ri["min"]
            rw_iid_max[n - 1] = ri["max"]
        is_sturm = rs["min"] == 2 and rs["max"] == 2
        flag = "✓ =2" if is_sturm else f"✗ [{rs['min']},{rs['max']}]"
        iid_str = (f"{ri['min']:>9d} {ri['max']:>9d}" if ri else f"{'—':>9} {'—':>9}")
        print(f"{n:>3d} {rs['min']:>5d} {rs['max']:>6d} {rs['mean']:>8.3f} "
              f"{rs['n_observed']:>6d} {iid_str}  {flag}")

    np.savez(
        out_dir / "stopping_class_block_entropy.npz",
        n=ns, parities=parities, plus_density=plus_density, O_max=O_max,
        p_seq=p_seq, H_seq=H_seq, p_iid=p_iid, H_iid=H_iid,
        rw_min=rw_min, rw_max=rw_max, rw_mean=rw_mean,
        rw_iid_min=rw_iid_min, rw_iid_max=rw_iid_max,
    )

    # ---------- Plotting ----------
    fig, axes = plt.subplots(3, 1, figsize=(11, 12))

    ax = axes[0]
    ax.plot(ns, ns + 1, color="black", ls="--", lw=1,
            label=r"Sturmian: $p(n)=n+1$")
    ax.plot(ns, 2 * ns + 1, color="purple", ls=":", lw=1,
            label=r"Arnoux–Rauzy: $2n+1$")
    iid_envelope = np.minimum(2.0 ** ns, float(O_max - ns[0] + 1))
    ax.plot(ns, iid_envelope, color="C3", ls=":", lw=1,
            label=r"i.i.d. upper bound $\min(2^n, L{-}n{+}1)$")
    ax.scatter(ns, p_seq, c="C2", s=50, edgecolor="black", linewidth=0.5,
               label=r"$\{P_o \,\mathrm{mod}\, 2\}$ sequence")
    ax.scatter(ns, p_iid, c="C3", marker="x", s=50, label="i.i.d. baseline")
    ax.set_yscale("log")
    ax.set_ylim(1, max(O_max * 1.5, 2 ** 14))
    ax.set_xlabel("window size n")
    ax.set_ylabel("# distinct length-n factors")
    ax.set_title(r"Factor complexity $p(n)$ of stopping-class parity sequence")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3, which="both")

    ax = axes[1]
    p = plus_density
    h1 = (-p * math.log2(p) - (1 - p) * math.log2(1 - p)) if 0 < p < 1 else 0.0
    ax.plot(ns, np.log2(ns + 1), color="black", ls="--", lw=1,
            label=r"$\log_2(n+1)$ (Sturmian bound)")
    ax.plot(ns, ns * h1, color="C3", ls=":", lw=1,
            label=fr"$n \cdot h({p:.3f}) = {h1:.4f}n$ (i.i.d. theory)")
    ax.scatter(ns, H_seq, c="C2", s=50, edgecolor="black", linewidth=0.5,
               label=r"$\{P_o \,\mathrm{mod}\, 2\}$ sequence")
    ax.scatter(ns, H_iid, c="C3", marker="x", s=50, label="i.i.d. baseline")
    ax.set_xlabel("window size n")
    ax.set_ylabel(r"$H(n)$ (bits)")
    ax.set_title("Shannon block entropy")
    ax.legend()
    ax.grid(alpha=0.3)

    ax = axes[2]
    ax.axhline(2, color="black", ls="--", lw=1,
               label="Sturmian prediction: exactly 2")
    ax.scatter(ns, rw_max, c="C2", s=50, edgecolor="black", linewidth=0.5,
               label=r"$\{P_o \,\mathrm{mod}\, 2\}$: max")
    ax.scatter(ns, rw_min, c="C2", marker="v", s=30,
               label=r"$\{P_o \,\mathrm{mod}\, 2\}$: min")
    iid_valid = rw_iid_max > 0
    ax.scatter(ns[iid_valid], rw_iid_max[iid_valid], c="C3", marker="x", s=50,
               label="i.i.d.: max")
    ax.scatter(ns[iid_valid], rw_iid_min[iid_valid], c="C3", marker="+", s=50,
               label="i.i.d.: min")
    ax.set_yscale("log")
    ax.set_xlabel("factor length n")
    ax.set_ylabel("# distinct return words")
    ax.set_title("Return-word count per factor (Justin–Vuillon)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3, which="both")

    fig.subplots_adjust(hspace=0.4, left=0.08, right=0.97, top=0.96, bottom=0.05)
    out_png = out_dir / "stopping_class_block_entropy.png"
    fig.savefig(out_png, dpi=120, bbox_inches="tight")
    print(f"\nSaved {out_png}")

    # Summary classification
    print("\n=== Verdict ===")
    matches_sturm = int(np.sum(p_seq == ns + 1))
    matches_ar = int(np.sum(p_seq == 2 * ns + 1))
    matches_iid = int(np.sum(p_seq == np.minimum(2 ** ns, O_max - ns + 1)))
    print(f"p(n) = n+1 (Sturmian):         {matches_sturm} / {n_max}")
    print(f"p(n) = 2n+1 (Arnoux–Rauzy):    {matches_ar} / {n_max}")
    print(f"p(n) ≈ min(2^n, L−n+1) (i.i.d. saturation): {matches_iid} / {n_max}")

    n_rw_obs = int(sum(1 for M in rw_max if M > 0))
    n_rw_strict = int(sum(1 for m, M in zip(rw_min, rw_max) if M > 0 and m == 2 and M == 2))
    print(f"Return-word count exactly 2:   {n_rw_strict} / {n_rw_obs}")

    if matches_sturm == n_max and n_rw_strict == n_rw_obs:
        print("\n  ✓ Stopping-class parity sequence IS Sturmian.")
        print("    Universality of Sturmian class across Paper 1 ↔ Paper 2.")
    elif p_seq[-1] >= 2 ** min(n_max, 15):
        print("\n  ✗ p(n) saturates at the i.i.d. upper bound.")
        print("    Stopping-class parity has positive topological entropy.")
    else:
        # Estimate complexity growth: linear or polynomial?
        # Fit log p(n) ~ alpha * log n + beta
        if matches_sturm < n_max:
            log_ns = np.log(ns[5:])  # skip small n
            log_p = np.log(p_seq[5:])
            slope, intercept = np.polyfit(log_ns, log_p, 1)
            print(f"\n  ? Non-Sturmian. Power-law fit log p(n) ≈ {slope:.3f} log n + {intercept:.3f}")
            # Also fit linear: p(n) ~ c*n
            slope_lin, _ = np.polyfit(ns[5:], p_seq[5:], 1)
            print(f"    Linear fit p(n) ≈ {slope_lin:.3f} n + ...")


if __name__ == "__main__":
    main()
