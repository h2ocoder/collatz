"""Collatz orbits as sawtooth billiards in (step, log_2 n) space.

Under the shortcut Collatz map T(n) = (3n+1)/2 if n odd, n/2 if n even,
each step changes the log magnitude of the orbit by

    +log_2(3/2) ≈ +0.585   (odd step — a "launcher" upward)
    −1                       (even step — a "hole" downward)

The orbit traces a piecewise-linear sawtooth path. The "floor" is the
horizontal line at altitude log_2(n_start); the orbit drops when the
sawtooth crosses that floor.

This is literally a 1D billiard interpretation of the dropping
classification: the dropping time = first floor-crossing time of the
sawtooth trajectory.

Four figures:

  1. Sawtooth orbits — famous long-orbit starting values rendered with
     odd / even step segments colored differently.
  2. Billiard caustics — many orbits overlaid in (step, relative-altitude)
     coordinates, with orbits that drop (green) and orbits still above
     the floor (red) distinguished. Compares q ∈ {3, 5, 7, 9}.
  3. 5x+1 cycle closeup — orbits that fall into the 5x+1 cycles trace
     closed loops in (step, altitude) space.
  4. Stopping-class colored caustics — same caustic as (2) but with
     each orbit colored by its actual shortcut stopping time. The
     caustic resolves into colored bands, one per Beatty rung. Dropped
     orbits cluster into Sturmian-spaced color stripes; non-droppers
     are shown as gray background.

Outputs:
    data/collatz_sawtooth_orbits.png
    data/collatz_billiard_caustic.png
    data/collatz_5x1_cycles.png
    data/collatz_billiard_caustic_colored.png
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


def collatz_orbit(n_start: int, q: int = 3, max_steps: int = 10000
                  ) -> tuple[list[int], np.ndarray]:
    """Run the shortcut q*x+1 orbit, return (values, log2_values)."""
    values: list[int] = [n_start]
    logs: list[float] = [math.log2(n_start)]
    cur = n_start
    for _ in range(max_steps):
        if cur % 2 == 0:
            cur //= 2
        else:
            cur = (q * cur + 1) // 2
        values.append(cur)
        logs.append(math.log2(cur) if cur > 0 else 0.0)
        if cur == 1:
            break
    return values, np.asarray(logs, dtype=np.float64)


def first_drop_step(values: list[int], n_start: int) -> int:
    """Step at which orbit first dips strictly below n_start (or -1 if never)."""
    for i in range(1, len(values)):
        if values[i] < n_start:
            return i
    return -1


def first_return_step(values: list[int], n_start: int) -> int:
    """Step at which orbit first returns to n_start (or -1 if never)."""
    for i in range(1, len(values)):
        if values[i] == n_start:
            return i
    return -1


def plot_sawtooth_segments(ax, steps, logs, lw=1.0, alpha=0.75):
    """Plot the sawtooth with odd / even step segments colored."""
    for i in range(len(steps) - 1):
        up = logs[i + 1] > logs[i]
        ax.plot([steps[i], steps[i + 1]], [logs[i], logs[i + 1]],
                color='#e74c3c' if up else '#3498db', lw=lw, alpha=alpha)


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(exist_ok=True)

    # ============ Figure 1: Single-orbit sawtooths ============
    print("Generating Figure 1: single-orbit sawtooths...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    examples = [
        (27,     "n = 27",     "stopping time 96 — the canonical hailstone"),
        (703,    "n = 703",    "stopping time 137 — bigger climb"),
        (10971,  "n = 10971",  "stopping time 267 — high peak before drop"),
        (837799, "n = 837799", "stopping time 524 — Lagarias record-holder"),
    ]
    for ax, (n_start, title, subtitle) in zip(axes.flat, examples):
        values, logs = collatz_orbit(n_start, q=3, max_steps=10000)
        drop_step = first_drop_step(values, n_start)
        end = drop_step + 1 if drop_step > 0 else len(values)
        steps = np.arange(end)
        logs_show = logs[:end]

        plot_sawtooth_segments(ax, steps, logs_show, lw=1.0, alpha=0.8)

        floor = math.log2(n_start)
        ax.axhline(floor, color='black', ls='--', lw=1.2, alpha=0.65,
                   label=f"altitude = log₂({n_start}) = {floor:.3f}")
        max_idx = int(np.argmax(logs_show))
        ax.scatter([steps[max_idx]], [logs_show[max_idx]], s=80, c='#f39c12',
                   edgecolor='black', linewidth=1, zorder=5,
                   label=f"peak: 2^{logs_show[max_idx]:.2f} at step {max_idx}")
        if drop_step > 0:
            ax.scatter([drop_step], [logs[drop_step]], s=110, c='#2ecc71',
                       edgecolor='black', linewidth=1.5, zorder=6,
                       label=f"drop @ step {drop_step}")
        ax.set_xlabel("step")
        ax.set_ylabel(r"$\log_2 n$")
        ax.set_title(f"{title} — {subtitle}", fontsize=11)
        ax.legend(fontsize=8, loc='best')
        ax.grid(alpha=0.3)

    fig.suptitle(
        r"Collatz sawtooth billiard: red = odd step ($+\log_2(3/2)$), "
        r"blue = even step ($-1$)",
        fontsize=13, y=0.99,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out1 = out_dir / "collatz_sawtooth_orbits.png"
    fig.savefig(out1, dpi=120, facecolor='white', bbox_inches='tight')
    print(f"  Saved {out1}")

    # ============ Figure 2: Billiard caustics across qx+1 ============
    print("Generating Figure 2: billiard caustics...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    max_steps_caustic = 100
    odd_starts = list(range(11, 401, 2))  # 195 odd starting values

    for ax, q in zip(axes.flat, [3, 5, 7, 9]):
        drop_count = 0
        no_drop_count = 0
        for n_start in odd_starts:
            values, logs = collatz_orbit(n_start, q=q, max_steps=max_steps_caustic)
            relative = logs - math.log2(n_start)
            drop_step = first_drop_step(values, n_start)
            if drop_step > 0:
                drop_count += 1
                end = min(drop_step + 1, len(relative))
                color = '#2ecc71'
            else:
                no_drop_count += 1
                end = len(relative)
                color = '#e74c3c'
            steps = np.arange(end)
            ax.plot(steps, relative[:end], color=color, alpha=0.08, lw=0.6)

        ax.axhline(0, color='black', ls='--', lw=1.5)
        ax.set_xlabel("step")
        ax.set_ylabel(r"$\log_2 n - \log_2 n_{\rm start}$")
        ax.set_title(
            f"{q}x+1: {len(odd_starts)} orbits — {drop_count} dropped, "
            f"{no_drop_count} still above floor (within {max_steps_caustic} steps)",
            fontsize=11,
        )
        ax.set_xlim(0, max_steps_caustic)
        ax.grid(alpha=0.3)
        legend_elements = [
            Patch(facecolor='#2ecc71', alpha=0.45, label='orbits that drop'),
            Patch(facecolor='#e74c3c', alpha=0.45, label='still above floor'),
            plt.Line2D([0], [0], color='black', ls='--', label='floor (altitude 0)'),
        ]
        ax.legend(handles=legend_elements, fontsize=9, loc='upper left')

    fig.suptitle(
        "Collatz billiard caustics: many orbits, ensemble pattern across qx+1\n"
        "(envelope shape encodes the average drift; q=3 droops down, "
        "q≥5 fans upward)",
        fontsize=12, y=0.99,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out2 = out_dir / "collatz_billiard_caustic.png"
    fig.savefig(out2, dpi=120, facecolor='white', bbox_inches='tight')
    print(f"  Saved {out2}")

    # ============ Figure 3: 5x+1 cycle close-up ============
    print("Generating Figure 3: 5x+1 cycle closeup...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))

    # Panel A: trapped orbits (the two 5x+1 cycles)
    ax = axes[0]
    trapped_starts = [13, 17]
    cmap_trap = ['#e74c3c', '#9b59b6']
    for n_start, color in zip(trapped_starts, cmap_trap):
        values, logs = collatz_orbit(n_start, q=5, max_steps=20)
        rel = logs - math.log2(n_start)
        return_step = first_return_step(values, n_start)
        end = (return_step + 1) if return_step > 0 else len(values)
        steps = np.arange(end)
        ax.plot(steps, rel[:end], color=color, lw=2, alpha=0.9, marker='o',
                ms=5, label=f"n = {n_start} (cycle, length {return_step})")
        # Highlight cycle members
        cycle_vals = values[:return_step]
        for j, v in enumerate(cycle_vals):
            ax.annotate(str(v), (j, rel[j]),
                        textcoords="offset points", xytext=(5, 6),
                        fontsize=8, color=color)
    ax.axhline(0, color='black', ls='--', lw=1.2, label='altitude n_start')
    ax.set_xlabel("step")
    ax.set_ylabel(r"$\log_2 n - \log_2 n_{\rm start}$")
    ax.set_title("5x+1 cycles as closed sawtooth loops\n"
                 "(orbit returns to its start without ever crossing the floor)",
                 fontsize=11)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(alpha=0.3)

    # Panel B: orbits that converge to 1 (for comparison)
    ax = axes[1]
    converge_starts = [3, 7, 9, 11, 21]
    cmap_conv = plt.cm.viridis(np.linspace(0.1, 0.85, len(converge_starts)))
    for n_start, color in zip(converge_starts, cmap_conv):
        values, logs = collatz_orbit(n_start, q=5, max_steps=200)
        rel = logs - math.log2(n_start)
        # Stop when reaching 1 (or when relative altitude hits log_2(1/n_start) = -log_2 n_start)
        end = len(rel)
        for i, v in enumerate(values):
            if v == 1:
                end = i + 1
                break
        steps = np.arange(end)
        ax.plot(steps, rel[:end], color=color, lw=1.5, alpha=0.85, marker='.',
                ms=4, label=f"n = {n_start} → 1 in {end-1} steps")
    ax.axhline(0, color='black', ls='--', lw=1.2, label='altitude n_start')
    ax.set_xlabel("step")
    ax.set_ylabel(r"$\log_2 n - \log_2 n_{\rm start}$")
    ax.set_title("5x+1 orbits that DO reach 1\n"
                 "(small starts that fall through the floor and bottom out)",
                 fontsize=11)
    ax.legend(fontsize=9, loc='upper right')
    ax.grid(alpha=0.3)

    fig.suptitle(
        "5x+1 system: two qualitatively different orbit types in (step, altitude) space",
        fontsize=12, y=1.0,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out3 = out_dir / "collatz_5x1_cycles.png"
    fig.savefig(out3, dpi=120, facecolor='white', bbox_inches='tight')
    print(f"  Saved {out3}")

    # ============ Figure 4: Stopping-class color-coded caustic ============
    print("Generating Figure 4: stopping-class color-coded caustic...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))

    for ax, q in zip(axes.flat, [3, 5, 7, 9]):
        # First pass: collect orbit data
        orbit_data: list[dict] = []
        for n_start in odd_starts:
            values, logs = collatz_orbit(n_start, q=q, max_steps=max_steps_caustic)
            relative = logs - math.log2(n_start)
            drop_step = first_drop_step(values, n_start)
            orbit_data.append({
                'n_start': n_start, 'drop_step': drop_step, 'rel': relative,
            })

        dropped_data = [d for d in orbit_data if d['drop_step'] > 0]
        distinct_ks = sorted({d['drop_step'] for d in dropped_data})

        # Viridis mapped to the range of observed stopping times
        if distinct_ks:
            kmin, kmax = min(distinct_ks), max(distinct_ks)
            cmap = plt.cm.viridis
            norm = plt.Normalize(vmin=kmin, vmax=max(kmax, kmin + 1))
            k_to_color = {k: cmap(norm(k)) for k in distinct_ks}
        else:
            k_to_color = {}

        # Background: orbits that didn't drop
        for d in orbit_data:
            if d['drop_step'] <= 0:
                steps = np.arange(len(d['rel']))
                ax.plot(steps, d['rel'], color='#cccccc', alpha=0.15, lw=0.5)

        # Foreground: dropped orbits, sorted by stopping time (so smaller k
        # bands sit underneath visually)
        for d in sorted(dropped_data, key=lambda x: x['drop_step']):
            end = d['drop_step'] + 1
            steps = np.arange(end)
            color = k_to_color[d['drop_step']]
            ax.plot(steps, d['rel'][:end], color=color, alpha=0.45, lw=0.7)
            ax.scatter([d['drop_step']], [d['rel'][d['drop_step']]],
                       color=color, s=10, alpha=0.7, edgecolor='none', zorder=4)

        ax.axhline(0, color='black', ls='--', lw=1.5, zorder=3)

        # Faint vertical guides at the predicted shortcut Beatty rungs
        slope_log = math.log2(q / 2)
        beatty_shortcut: list[int] = []
        for o in range(1, 60):
            k = o + int(math.floor(o * slope_log)) + 1
            if k <= max_steps_caustic:
                beatty_shortcut.append(k)
        for k in beatty_shortcut:
            if k in distinct_ks:
                ax.axvline(k, color='black', ls=':', lw=0.5, alpha=0.25, zorder=1)

        ax.set_xlabel("step")
        ax.set_ylabel(r"$\log_2 n - \log_2 n_{\rm start}$")
        n_drop = len(dropped_data)
        ax.set_title(
            f"{q}x+1: {n_drop}/{len(odd_starts)} dropped, "
            f"{len(distinct_ks)} distinct shortcut stopping times "
            f"(slope = log₂({q}/2) = {slope_log:.3f})",
            fontsize=10,
        )

        # Legend showing the most common stopping times
        legend_items = []
        if dropped_data:
            counts_by_k = {k: sum(1 for d in dropped_data if d['drop_step'] == k)
                           for k in distinct_ks}
            top_ks = sorted(distinct_ks, key=lambda k: -counts_by_k[k])[:8]
            top_ks = sorted(top_ks)
            for k in top_ks:
                legend_items.append(plt.Line2D(
                    [0], [0], color=k_to_color[k], lw=3,
                    label=f"k = {k} ({counts_by_k[k]} orbits)",
                ))
            if len(distinct_ks) > len(top_ks):
                legend_items.append(plt.Line2D(
                    [0], [0], color='none',
                    label=f"+ {len(distinct_ks) - len(top_ks)} more rungs",
                ))
        if any(d['drop_step'] <= 0 for d in orbit_data):
            legend_items.append(Patch(facecolor='#cccccc', alpha=0.6,
                                      label='did not drop'))
        ax.legend(handles=legend_items, fontsize=7, loc='upper right')
        ax.set_xlim(0, max_steps_caustic)
        ax.grid(alpha=0.3)

    fig.suptitle(
        "Billiard caustics, color-coded by shortcut stopping time\n"
        "(each color = one Beatty rung — the Sturmian schedule made visible "
        "as bands)",
        fontsize=12, y=0.99,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out4 = out_dir / "collatz_billiard_caustic_colored.png"
    fig.savefig(out4, dpi=120, facecolor='white', bbox_inches='tight')
    print(f"  Saved {out4}")

    print("\nDone — four sawtooth-billiard figures generated.")


if __name__ == "__main__":
    main()
