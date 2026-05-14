"""Investigate the (c_1, c_2) balance in Dset_k.

Computes for each k in 1..K_max:
  - (|R_k|, c_1, c_2)
  - Δ_k = c_2 - c_1
  - balance ratio Δ_k / |R_k|
  - parity-class decomposition: which j* values appear in R_k, with what multiplicity

Then visualizes:
  - Δ_k / |R_k| vs k  (signed balance)
  - |Δ_k| / sqrt(|R_k|)  vs k  (CLT scaling test)
  - sign(Δ_k) vs k (sign pattern as binary signal)
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collatz.core import collatz_step  # noqa: E402


def find_j_star_and_oddcount(n_0, k):
    """Return (j*, o) where j* = position of last odd step, o = total odd-step count."""
    j_star = -1
    o = 0
    n = n_0
    for j in range(k):
        if n % 2 == 1:
            j_star = j
            o += 1
        n = collatz_step(n)
    return j_star, o


def compute_R_data(K_max: int, lift: int = 10**6):
    """Return dict {k: list of (r, j*, o, parity_tuple)}."""
    survivors = [(lift, lift)]
    result: dict[int, list[tuple[int, int, int, tuple]]] = {}
    for k in range(1, K_max + 1):
        new_survivors = []
        Rk = []
        for n_0, _ in survivors:
            for child in (n_0, n_0 + 2 ** (k - 1)):
                n_iter = child
                for _ in range(k):
                    n_iter = collatz_step(n_iter)
                if n_iter < child:
                    r = child % (2 ** k)
                    # also compute parity sequence and j*
                    par = []
                    n_walk = child
                    js = -1
                    for j in range(k):
                        par.append(n_walk % 2)
                        if n_walk % 2 == 1:
                            js = j
                        n_walk = collatz_step(n_walk)
                    o = sum(par)
                    Rk.append((r, js, o, tuple(par)))
                else:
                    new_survivors.append((child, n_iter))
        survivors = new_survivors
        if Rk:
            result[k] = Rk
    return result


def main():
    K_max = 30
    print(f"Computing R_k structures up to k = {K_max} ...")
    R_data = compute_R_data(K_max)

    out_dir = Path(__file__).resolve().parents[1] / "data"

    # Build summary table
    print(f"\n{'k':>3} {'|R_k|':>10} {'c_1':>10} {'c_2':>10} {'Δ_k':>12} "
          f"{'Δ/|R|':>10} {'|Δ|/sqrt|R|':>12} {'# par classes':>14}")
    print("-" * 100)
    ks, Rs, c1s, c2s = [], [], [], []
    parity_class_info: dict[int, dict[tuple, dict]] = {}
    for k in sorted(R_data.keys()):
        Rk = R_data[k]
        c1 = sum(1 for (_, js, _, _) in Rk if (js + k) % 2 == 1)
        c2 = sum(1 for (_, js, _, _) in Rk if (js + k) % 2 == 0)
        delta = c2 - c1
        Rk_sz = len(Rk)
        # Group by parity tuple
        par_groups: dict[tuple, list] = defaultdict(list)
        for r, js, o, par in Rk:
            par_groups[par].append((r, js, o))
        parity_class_info[k] = {par: {"count": len(items), "j_star": items[0][1], "o": items[0][2]}
                                 for par, items in par_groups.items()}
        ks.append(k); Rs.append(Rk_sz); c1s.append(c1); c2s.append(c2)
        print(f"{k:>3d} {Rk_sz:>10d} {c1:>10d} {c2:>10d} {delta:>+12d} "
              f"{delta/Rk_sz:>+10.4f} {abs(delta)/np.sqrt(Rk_sz):>12.4f} {len(par_groups):>14d}")

    # Print parity-class structure for low k
    print("\n=== Parity class breakdown (low k) ===")
    for k in [3, 6, 8, 11, 13, 16]:
        if k not in parity_class_info:
            continue
        print(f"\nk = {k}: |R_k| = {sum(info['count'] for info in parity_class_info[k].values())}")
        for par, info in sorted(parity_class_info[k].items()):
            par_str = ''.join(map(str, par))
            print(f"  parity {par_str}: j*={info['j_star']:>2d}, o={info['o']:>2d}, "
                  f"count={info['count']:>4d}, "
                  f"contrib to c_{2 if (info['j_star'] + k) % 2 == 0 else 1}")

    # Save for plotting
    ks_arr = np.array(ks); Rs_arr = np.array(Rs)
    c1_arr = np.array(c1s); c2_arr = np.array(c2s)
    deltas = c2_arr - c1_arr
    np.savez(out_dir / "sign_pattern.npz", k=ks_arr, R=Rs_arr,
             c1=c1_arr, c2=c2_arr, delta=deltas)

    # Plot 1: balance ratio
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    ax = axes[0]
    ax.axhline(0, color="black", lw=0.7)
    ax.axhline(0.5, color="gray", ls=":", lw=0.5, label="±1/2")
    ax.axhline(-0.5, color="gray", ls=":", lw=0.5)
    ax.scatter(ks_arr, deltas / Rs_arr, c="C0", s=80, edgecolor="black", linewidth=0.5)
    for x, y, R in zip(ks_arr, deltas / Rs_arr, Rs_arr):
        if R < 50:
            ax.annotate(f"|R|={R}", (x, y), fontsize=8, textcoords="offset points", xytext=(5, 5))
    ax.set_ylabel(r"$(c_2 - c_1) / |R_k|$ (signed balance)")
    ax.set_title(r"Balance ratio across dropping times")
    ax.set_xlabel("k (only k with |R_k| > 0)")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_ylim(-1.1, 1.1)

    ax = axes[1]
    ax.axhline(0, color="black", lw=0.5)
    ax.scatter(ks_arr, np.abs(deltas) / np.sqrt(Rs_arr), c="C1", s=80, edgecolor="black", linewidth=0.5)
    ax.set_ylabel(r"$|c_2 - c_1| / \sqrt{|R_k|}$")
    ax.set_title("Fluctuation scaling: if CLT-like, this should be O(1); if linear, this grows")
    ax.set_xlabel("k")
    ax.grid(alpha=0.3)

    ax = axes[2]
    signs = np.sign(deltas)
    colors = ["red" if s < 0 else "green" if s > 0 else "gray" for s in signs]
    ax.scatter(ks_arr, signs, c=colors, s=100, edgecolor="black", linewidth=0.5)
    for x, y, R in zip(ks_arr, signs, Rs_arr):
        ax.annotate(f"k={x}", (x, y), fontsize=8, textcoords="offset points", xytext=(0, 8 if y >= 0 else -15), ha="center")
    ax.axhline(0, color="black", lw=0.5)
    ax.set_ylabel(r"$\mathrm{sgn}(c_2 - c_1)$")
    ax.set_xlabel("k")
    ax.set_title("Sign pattern of c_2 - c_1 across dropping times")
    ax.grid(alpha=0.3)
    ax.set_ylim(-1.5, 1.5)

    fig.tight_layout()
    out_png = out_dir / "sign_pattern.png"
    fig.savefig(out_png, dpi=120)
    print(f"\nSaved {out_png}")

    # Final test: as k grows, does Δ/|R| → 0?
    print(f"\n|Δ_k|/|R_k| at largest k values:")
    for k in sorted(R_data.keys())[-6:]:
        i = ks.index(k)
        print(f"  k={k:>3d}: {abs(deltas[i])/Rs[i]:.4f}")


if __name__ == "__main__":
    main()
