"""Check whether zeros of 1 - g_K(z) stabilize as K grows.

Computes zeros at K = 15, 20, 25, 30 from the same R[] data and overlays them.
Convergence to a critical line/circle would manifest as zeros at low |Im(s)|
stabilizing while new ones fill in at higher |Im(s)|.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def roots_for_truncation(R: np.ndarray, K: int) -> tuple[np.ndarray, np.ndarray]:
    coeffs = np.array([-1.0] + [float(R[k]) for k in range(1, K + 1)])
    poly = coeffs[::-1]
    roots_z = np.roots(poly)
    roots_z = roots_z[np.argsort(np.abs(roots_z))]
    s = -np.log(roots_z) / np.log(2.0)
    return roots_z, s


def main() -> None:
    data_path = Path(__file__).resolve().parents[1] / "data" / "dropping_zeta_zeros.npz"
    out_dir = Path(__file__).resolve().parents[1] / "data"
    data = np.load(data_path)
    R = data["R"]

    Ks = [15, 20, 25, 30]
    colors = ["C2", "C1", "C4", "C0"]

    fig, axes = plt.subplots(1, 2, figsize=(15, 7))

    # z-plane
    ax = axes[0]
    theta = np.linspace(0, 2 * np.pi, 200)
    ax.plot(0.5 * np.cos(theta), 0.5 * np.sin(theta), "k--", lw=1, label="|z|=1/2")
    ax.plot(np.cos(theta), np.sin(theta), "k:", lw=0.6)

    # s-plane
    ax2 = axes[1]
    ax2.axvline(0.5, color="r", lw=1, ls="--", label="Re(s)=1/2")

    for K, color in zip(Ks, colors):
        z, s = roots_for_truncation(R, K)
        # Identify trivial root (closest to 0.5+0i)
        triv_idx = int(np.argmin(np.abs(z - 0.5)))
        mask = np.ones(len(z), dtype=bool); mask[triv_idx] = False
        ax.scatter(z[mask].real, z[mask].imag, c=color, s=25, alpha=0.7, label=f"K={K}")
        ax.scatter(z[triv_idx].real, z[triv_idx].imag, c=color, s=80, marker="*",
                   edgecolor="black", linewidth=0.5)
        ax2.scatter(s[mask].real, s[mask].imag, c=color, s=25, alpha=0.7, label=f"K={K}")
        ax2.scatter(s[triv_idx].real, s[triv_idx].imag, c=color, s=80, marker="*",
                    edgecolor="black", linewidth=0.5)

    ax.set_xlabel("Re(z)"); ax.set_ylabel("Im(z)")
    ax.set_title("Zeros of 1 − g_K(z) at K = 15, 20, 25, 30")
    ax.set_aspect("equal"); ax.legend(); ax.grid(alpha=0.3)

    ax2.set_xlabel("Re(s)"); ax2.set_ylabel("Im(s)")
    ax2.set_title("Same zeros in s-plane (s = -log₂ z)")
    ax2.set_xlim(0.3, 1.1)
    ax2.legend(); ax2.grid(alpha=0.3)

    fig.tight_layout()
    out_png = out_dir / "zeros_convergence.png"
    fig.savefig(out_png, dpi=120)
    print(f"Saved {out_png}")

    # Also: track the lowest-Re(s) non-trivial zero as K grows
    print("\nLowest Re(s) non-trivial zero by K:")
    for K in [10, 15, 18, 20, 22, 25, 28, 30]:
        z, s = roots_for_truncation(R, K)
        triv_idx = int(np.argmin(np.abs(z - 0.5)))
        mask = np.ones(len(z), dtype=bool); mask[triv_idx] = False
        if mask.sum() == 0:
            print(f"  K={K}: no non-trivial roots")
            continue
        nt = s[mask]
        idx = int(np.argmin(nt.real))
        print(f"  K={K}: min Re(s) = {nt[idx].real:.4f} at Im(s) = {nt[idx].imag:+.4f}; "
              f"max |Im(s)| in set = {np.abs(nt.imag).max():.4f}")


if __name__ == "__main__":
    main()
