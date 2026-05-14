"""Plot zeros of the dropping zeta function in z- and s-planes."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    data_path = Path(__file__).resolve().parents[1] / "data" / "dropping_zeta_zeros.npz"
    out_dir = Path(__file__).resolve().parents[1] / "data"
    data = np.load(data_path)
    R = data["R"]
    roots_z = data["roots_z"]
    roots_s = data["roots_s"]
    K_max = int(data["K_max"])

    # Split trivial (the one near z = 1/2 / s = 1) from rest
    abs_z = np.abs(roots_z)
    trivial_idx = int(np.argmin(np.abs(abs_z - 0.5)))
    nontrivial_mask = np.ones(len(roots_z), dtype=bool)
    nontrivial_mask[trivial_idx] = False

    z_triv = roots_z[trivial_idx]
    s_triv = roots_s[trivial_idx]
    z_nt = roots_z[nontrivial_mask]
    s_nt = roots_s[nontrivial_mask]

    print(f"Trivial root: z = {z_triv:.6f}, s = {s_triv:.6f}")
    print(f"Non-trivial roots: {len(z_nt)} (Re(s) range = "
          f"{s_nt.real.min():.4f} to {s_nt.real.max():.4f})")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # z-plane
    ax = axes[0]
    theta = np.linspace(0, 2 * np.pi, 200)
    ax.plot(0.5 * np.cos(theta), 0.5 * np.sin(theta), "k--", lw=1, label="|z| = 1/2")
    ax.plot(np.cos(theta), np.sin(theta), "k:", lw=0.7, label="|z| = 1 (unit)")
    ax.scatter(z_nt.real, z_nt.imag, c="C0", s=40, label="non-trivial roots")
    ax.scatter([z_triv.real], [z_triv.imag], c="C3", s=80, marker="*", label="trivial root (≈ 1/2)")
    ax.axhline(0, color="gray", lw=0.5)
    ax.axvline(0, color="gray", lw=0.5)
    ax.set_xlabel("Re(z)")
    ax.set_ylabel("Im(z)")
    ax.set_title(f"Roots of 1 - g(z), g(z) = Σ |R_k| z^k, k≤{K_max}")
    ax.set_aspect("equal")
    ax.legend()
    ax.grid(alpha=0.3)

    # s-plane
    ax = axes[1]
    ax.axvline(0.5, color="r", lw=1, ls="--", label="Re(s) = 1/2 (critical line)")
    ax.axvline(1.0, color="gray", lw=0.7, ls=":", label="Re(s) = 1")
    ax.scatter(s_nt.real, s_nt.imag, c="C0", s=40, label="non-trivial zeros")
    ax.scatter([s_triv.real], [s_triv.imag], c="C3", s=80, marker="*",
               label=f"trivial (≈1, found {s_triv.real:.3f})")
    ax.set_xlabel("Re(s)")
    ax.set_ylabel("Im(s)")
    ax.set_title("Zeros in s-plane (s = -log₂ z)")
    ax.set_xlim(0.4, 1.05)
    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()
    out_png = out_dir / "dropping_zeta_zeros.png"
    fig.savefig(out_png, dpi=120)
    print(f"Saved plot to {out_png}")

    # Also print: Re(s) vs |Im(s)| to see if curve structure
    print("\nNon-trivial zeros sorted by Re(s):")
    order = np.argsort(s_nt.real)
    for idx in order:
        s = s_nt[idx]
        print(f"  Re(s) = {s.real:.4f}  Im(s) = {s.imag:+.4f}  |Im(s)| = {abs(s.imag):.4f}")


if __name__ == "__main__":
    main()
