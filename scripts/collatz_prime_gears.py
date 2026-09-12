"""Collatz orbits viewed through their prime-factor "gears".

Each integer n in a Collatz orbit carries a multiset of prime factors — a
collection of gears of different sizes.  Under the full Collatz map
f(n) = n/2 (even) or 3n+1 (odd):

  * An even step n -> n/2 strips one tooth from the 2-gear and leaves
    every other gear untouched (gcd(2, odd p) = 1).
  * An odd step n -> 3n+1 ejects every odd prime that was engaged with n
    (because (3n+1) ≡ 1 (mod p) whenever p | n with p odd) and slots in
    whichever primes happen to factor 3n+1 instead.

So in the gear metaphor an odd prime engages briefly: it shows up once
3n+1 lands on a multiple of p, persists through the run of /2 steps that
follow, and is ejected at the very next odd step.  The trivial cycle
1 -> 4 -> 2 -> 1 runs entirely on the 2-gear.

This script renders four views of that mechanism:

  1. Gear engagement diagram for a single orbit (n = 27) — horizontal
     "lane" per prime, lit up across the steps where that prime divides
     n_t with height proportional to its exponent.  Shows how each
     odd-prime gear engages and disengages, and the 2-gear's sawtooth.
  2. Ensemble occupancy heatmap for a dropping set — for every (set k,
     modulus m) group up to a limit, the average exponent of each small
     prime at each orbit step.  Reveals which primes are characteristic
     of which orbit phases of a class.
  3. Gear-period scatter — for primes p ≤ 200, (ord_p(2), ord_p(3))
     colored by dropping_set(p).  Tests whether a prime's gear size (its
     multiplicative order under doubling / tripling) correlates with the
     dropping class the prime itself sits in.
  4. Mod-p Lissajous portrait — for one long orbit (n = 27), the
     trajectory (n_t mod p1, n_t mod p2) for several prime pairs.  The
     attractor in every panel is the 4-2-1 cycle, traced as a tight
     three-point loop the orbit spirals into.

Outputs:
    data/collatz_prime_gear_engagement.png
    data/collatz_prime_occupancy_heatmap.png
    data/collatz_prime_gear_periods.png
    data/collatz_prime_lissajous.png
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch, Rectangle

from collatz.core import orbit
from collatz.dropping import dropping_orbit, dropping_set, dropping_modulus
from collatz.factorization import is_prime, prime_factorization
from collatz.orbits import class_members


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def exponent_of(n: int, p: int) -> int:
    """v_p(n): exponent of prime p in n."""
    if n <= 0:
        return 0
    e = 0
    while n % p == 0:
        n //= p
        e += 1
    return e


def mult_order(a: int, p: int) -> int:
    """Multiplicative order of a modulo prime p (0 if undefined)."""
    if p < 2 or a % p == 0:
        return 0
    a %= p
    cur = a
    o = 1
    while cur != 1:
        cur = (cur * a) % p
        o += 1
        if o > p:
            return 0
    return o


def orbit_prime_signature(seq: list[int], primes: list[int]) -> np.ndarray:
    """Matrix [len(primes), len(seq)] of v_p(n_t) for each (p, t)."""
    M = np.zeros((len(primes), len(seq)), dtype=np.int32)
    for j, n in enumerate(seq):
        for i, p in enumerate(primes):
            M[i, j] = exponent_of(n, p)
    return M


def primes_up_to(limit: int) -> list[int]:
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    return [i for i in range(2, limit + 1) if sieve[i]]


# ----------------------------------------------------------------------
# Figure 1: single-orbit prime-gear engagement diagram
# ----------------------------------------------------------------------


def figure_engagement(out_path: Path, n_start: int = 27) -> None:
    print(f"Generating Figure 1: prime-gear engagement for n = {n_start}...")
    seq = orbit(n_start)
    T = len(seq)

    # Collect every prime that ever appears, ordered by first-appearance step.
    first_seen: dict[int, int] = {}
    for t, n in enumerate(seq):
        if n < 2:
            continue
        for p in prime_factorization(n):
            first_seen.setdefault(p, t)
    # Lane ordering: 2 always at bottom, then by first appearance.
    primes_ordered = [2] + [p for p in sorted(first_seen, key=lambda q: (first_seen[q], q)) if p != 2]
    primes_ordered = list(dict.fromkeys(primes_ordered))
    lane_of = {p: i for i, p in enumerate(primes_ordered)}

    # Build (step, prime, exponent) triples.
    triples: list[tuple[int, int, int]] = []
    for t, n in enumerate(seq):
        if n < 2:
            continue
        for p, e in prime_factorization(n).items():
            triples.append((t, p, e))

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(15, 9),
        gridspec_kw={"height_ratios": [0.45, 0.55]},
    )

    # Top panel: log2 n trajectory, for orientation
    log_vals = [math.log2(v) for v in seq]
    odd_mask = [v % 2 == 1 for v in seq]
    for t in range(T - 1):
        col = "#e74c3c" if seq[t] % 2 == 1 else "#3498db"
        ax_top.plot([t, t + 1], [log_vals[t], log_vals[t + 1]],
                    color=col, lw=1.2, alpha=0.85)
    ax_top.scatter(
        [t for t, on in enumerate(odd_mask) if on],
        [log_vals[t] for t, on in enumerate(odd_mask) if on],
        s=18, c="#e74c3c", edgecolor="none", zorder=4, label="odd n_t (3n+1 step)",
    )
    ax_top.axhline(math.log2(n_start), color="black", ls="--", lw=1, alpha=0.55,
                   label=f"altitude = log₂({n_start}) = {math.log2(n_start):.2f}")
    ax_top.set_ylabel(r"$\log_2 n_t$")
    ax_top.set_title(
        f"Collatz orbit of n = {n_start}  —  {T - 1} steps, "
        f"max = {max(seq)} (≈ 2^{math.log2(max(seq)):.2f})",
        fontsize=12,
    )
    ax_top.set_xlim(-0.5, T - 0.5)
    ax_top.grid(alpha=0.3)
    ax_top.legend(fontsize=9, loc="upper right")

    # Bottom panel: gear engagement
    # Lane height = 1.  We draw a rectangle per (step, prime, exponent) with
    # height ∝ exponent (capped via log so the 2-gear doesn't dominate).
    def lane_height(e: int) -> float:
        return 0.18 + 0.45 * math.log2(1 + e)

    cmap = plt.cm.tab20
    prime_colors = {p: cmap(i % 20) for i, p in enumerate(primes_ordered)}
    prime_colors[2] = "#34495e"  # always dark slate for the 2-gear

    for (t, p, e) in triples:
        y = lane_of[p]
        h = lane_height(e)
        rect = Rectangle(
            (t - 0.45, y - h / 2),
            0.9, h,
            facecolor=prime_colors[p], edgecolor="none", alpha=0.85,
        )
        ax_bot.add_patch(rect)
        if e >= 2:
            ax_bot.text(t, y, str(e), ha="center", va="center",
                        fontsize=7, color="white", fontweight="bold")

    # Faint gridlines per lane
    for p, y in lane_of.items():
        ax_bot.axhline(y, color="#dddddd", lw=0.6, zorder=0)

    ax_bot.set_yticks(list(lane_of.values()))
    ax_bot.set_yticklabels([f"p = {p}" for p in primes_ordered])
    ax_bot.set_xlabel("orbit step  t")
    ax_bot.set_xlim(-0.5, T - 0.5)
    ax_bot.set_ylim(-0.8, len(primes_ordered) - 0.2)
    ax_bot.set_title(
        "Prime-gear engagement   "
        "(lane height ∝ log₂(1 + exponent); odd primes engage only between odd steps)",
        fontsize=11,
    )
    ax_bot.grid(False)
    ax_bot.invert_yaxis()

    fig.tight_layout()
    fig.savefig(out_path, dpi=120, facecolor="white", bbox_inches="tight")
    print(f"  Saved {out_path}")
    plt.close(fig)

    # Print summary stats
    distinct_primes = sorted(first_seen)
    odd_primes = [p for p in distinct_primes if p != 2]
    print(f"  distinct primes seen in orbit of {n_start}: {len(distinct_primes)} "
          f"(odd: {len(odd_primes)})  -- {distinct_primes[:12]}{'...' if len(distinct_primes) > 12 else ''}")
    avg_window = np.mean([
        sum(1 for q in prime_factorization(n) if q != 2)
        for n in seq if n >= 2
    ])
    print(f"  mean odd-prime gears engaged per step: {avg_window:.2f}")


# ----------------------------------------------------------------------
# Figure 2: ensemble occupancy heatmap across (set, modulus) groups
# ----------------------------------------------------------------------


def figure_occupancy(out_path: Path,
                     dropping_sets: list[int] = (3, 6, 8, 11),
                     limit: int = 4000,
                     small_primes: list[int] | None = None) -> None:
    print(f"Generating Figure 2: occupancy heatmaps for sets {list(dropping_sets)}...")
    if small_primes is None:
        small_primes = primes_up_to(60)  # 2, 3, 5, ..., 59

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    panels = list(zip(axes.flat, dropping_sets))

    for ax, k in panels:
        # Pick the largest non-trivial (set, modulus) group inside limit.
        # Try moduli 0, 1, ..., a few; take the first non-empty.
        members: list[int] = []
        chosen_mod = 0
        for m in range(0, 8):
            cand = class_members(k, m, limit)
            if len(cand) > len(members):
                members, chosen_mod = cand, m
        if not members:
            ax.set_title(f"Set_{k}: no members in [2, {limit})")
            continue

        # Aligned orbits — within a (set, modulus) group every member's
        # dropping_orbit has the same length (= k), so we can just stack.
        orbits = [dropping_orbit(n) for n in members]
        L = max(len(o) for o in orbits)
        # Build occupancy[p, t] = mean exponent of p in member's n_t.
        occ = np.zeros((len(small_primes), L), dtype=np.float64)
        for o in orbits:
            for t, n in enumerate(o):
                if n < 2:
                    continue
                facs = prime_factorization(n)
                for i, p in enumerate(small_primes):
                    occ[i, t] += facs.get(p, 0)
        occ /= len(orbits)

        im = ax.imshow(
            occ, aspect="auto", origin="lower",
            cmap="magma", interpolation="nearest",
        )
        ax.set_yticks(range(len(small_primes)))
        ax.set_yticklabels([str(p) for p in small_primes], fontsize=7)
        ax.set_xticks(range(L))
        ax.set_xticklabels([str(t) for t in range(L)], fontsize=8)
        ax.set_xlabel("dropping-orbit step  t")
        ax.set_ylabel("prime p")
        ax.set_title(
            f"Set_{k}, modulus = {chosen_mod}, "
            f"{len(members)} members up to {limit} — mean v_p(n_t)",
            fontsize=10,
        )
        fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02, label="mean exponent")

    fig.suptitle(
        "Ensemble prime-gear occupancy across dropping sets\n"
        "(each tile is the mean exponent of prime p in n_t, averaged over all members of (set, modulus))",
        fontsize=12, y=0.99,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path, dpi=120, facecolor="white", bbox_inches="tight")
    print(f"  Saved {out_path}")
    plt.close(fig)


# ----------------------------------------------------------------------
# Figure 3: gear-period scatter, primes colored by their own dropping_set
# ----------------------------------------------------------------------


def figure_gear_periods(out_path: Path,
                        prime_limit: int = 300,
                        max_class: int = 25) -> None:
    print(f"Generating Figure 3: gear periods for primes ≤ {prime_limit}...")
    ps = [p for p in primes_up_to(prime_limit) if p > 2]
    ord2 = [mult_order(2, p) for p in ps]
    ord3 = [mult_order(3, p) for p in ps]
    classes = [dropping_set(p) for p in ps]

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(15, 6.5))

    # Panel A: (ord_p 2, ord_p 3) scatter, colored by dropping set of p
    cmap = plt.cm.viridis
    norm = plt.Normalize(vmin=1, vmax=min(max(classes), max_class))
    colors = [cmap(norm(min(c, max_class))) for c in classes]

    ax_a.scatter(ord2, ord3, c=colors, s=42, edgecolor="black", linewidth=0.4, alpha=0.9)
    for p, x, y, c in zip(ps, ord2, ord3, classes):
        if p <= 30 or (x, y) in {(1, 1)}:
            ax_a.annotate(
                f"{p}", (x, y),
                textcoords="offset points", xytext=(4, 4),
                fontsize=7, color="black",
            )
    # Identity guides
    xlim = max(ord2) * 1.05
    ylim = max(ord3) * 1.05
    ax_a.plot([0, max(xlim, ylim)], [0, max(xlim, ylim)],
              color="black", ls=":", lw=0.8, alpha=0.4, label="ord₂ = ord₃")
    ax_a.set_xlabel(r"$\mathrm{ord}_p(2)$ — gear-teeth count under doubling")
    ax_a.set_ylabel(r"$\mathrm{ord}_p(3)$ — gear-teeth count under tripling")
    ax_a.set_title(f"Prime-gear sizes for odd p ≤ {prime_limit}, colored by dropping_set(p)",
                   fontsize=11)
    ax_a.set_xlim(0, xlim)
    ax_a.set_ylim(0, ylim)
    ax_a.grid(alpha=0.3)
    ax_a.legend(fontsize=9, loc="upper left")
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax_a, fraction=0.04, pad=0.02,
                 label="dropping_set(p)  (capped at "
                       f"{min(max(classes), max_class)})")

    # Panel B: marginal — dropping_set(p) vs ord_p(2)/ord_p(3) ratio.
    ratios = [o2 / o3 if o3 else 0 for o2, o3 in zip(ord2, ord3)]
    ax_b.scatter(classes, ratios, s=42, c=colors,
                 edgecolor="black", linewidth=0.4, alpha=0.85)
    ax_b.axhline(1.0, color="black", ls=":", lw=0.8, alpha=0.5)
    ax_b.set_xlabel("dropping_set(p)  =  Collatz dropping time of the prime itself")
    ax_b.set_ylabel(r"$\mathrm{ord}_p(2)\ /\ \mathrm{ord}_p(3)$")
    ax_b.set_xlim(0, min(max(classes), max_class) + 1)
    ax_b.grid(alpha=0.3)
    ax_b.set_title("Gear-ratio (doubling : tripling) by prime's dropping class", fontsize=11)

    fig.suptitle(
        "Gear-period view of the primes: each prime carries a doubling-gear and a tripling-gear;\n"
        "do primes that share a Collatz dropping class also share a gear-shape?",
        fontsize=12, y=0.99,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out_path, dpi=120, facecolor="white", bbox_inches="tight")
    print(f"  Saved {out_path}")
    plt.close(fig)


# ----------------------------------------------------------------------
# Figure 4: mod-p Lissajous for one long orbit
# ----------------------------------------------------------------------


def figure_lissajous(out_path: Path,
                     n_start: int = 27,
                     pairs: list[tuple[int, int]] | None = None) -> None:
    print(f"Generating Figure 4: mod-p Lissajous for orbit of n = {n_start}...")
    if pairs is None:
        pairs = [(3, 5), (5, 7), (3, 7), (7, 11)]
    seq = orbit(n_start)
    T = len(seq)

    fig, axes = plt.subplots(2, 2, figsize=(13, 12.5))
    for ax, (p1, p2) in zip(axes.flat, pairs):
        xs = [n % p1 for n in seq]
        ys = [n % p2 for n in seq]
        # Color by step index — viridis from start (purple) to end (yellow)
        ts = np.arange(T)
        # Draw connecting lines first, then scatter on top
        for i in range(T - 1):
            ax.plot([xs[i], xs[i + 1]], [ys[i], ys[i + 1]],
                    color=plt.cm.viridis(i / max(T - 1, 1)),
                    alpha=0.55, lw=0.9)
        ax.scatter(xs, ys, c=ts, cmap="viridis", s=22,
                   edgecolor="white", linewidth=0.4, zorder=3)
        # Highlight the 4-2-1 attractor (in mod p₁, p₂ coords)
        attractor = [(4 % p1, 4 % p2), (2 % p1, 2 % p2), (1 % p1, 1 % p2)]
        ax_x, ax_y = zip(*attractor)
        ax.scatter(ax_x, ax_y, s=140, marker="*", c="#e74c3c",
                   edgecolor="black", linewidth=0.8, zorder=4,
                   label="4-2-1 attractor (mod p₁, p₂)")
        ax.set_xlim(-0.5, p1 - 0.5)
        ax.set_ylim(-0.5, p2 - 0.5)
        ax.set_xticks(range(p1))
        ax.set_yticks(range(p2))
        ax.set_xlabel(f"n_t mod {p1}")
        ax.set_ylabel(f"n_t mod {p2}")
        ax.set_title(
            f"({p1}, {p2})  —  ord_{p1}(2)={mult_order(2, p1)}, "
            f"ord_{p1}(3)={mult_order(3, p1)},  "
            f"ord_{p2}(2)={mult_order(2, p2)}, ord_{p2}(3)={mult_order(3, p2)}",
            fontsize=10,
        )
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8, loc="upper right")

    fig.suptitle(
        f"Mod-p Lissajous: orbit of n = {n_start} projected onto (mod p₁, mod p₂)\n"
        "color = step index (purple → yellow);  red stars = 4-2-1 attractor",
        fontsize=12, y=0.99,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path, dpi=120, facecolor="white", bbox_inches="tight")
    print(f"  Saved {out_path}")
    plt.close(fig)


# ----------------------------------------------------------------------
# Cross-orbit prime statistics (printed report)
# ----------------------------------------------------------------------


def print_prime_shedding_stats(limit: int = 2000) -> None:
    """For every odd n in [3, limit), measure how fast distinct odd primes
    are shed along its orbit (until reaching 1).  This gives a numerical
    handle on the 'gear ejection rate' the figures visualise."""
    print(f"\nPrime-shedding stats over odd n in [3, {limit}):")
    samples = []
    for n in range(3, limit, 2):
        seq = orbit(n)
        # distinct odd primes ever engaged
        engaged: set[int] = set()
        for v in seq:
            if v < 2:
                continue
            for q in prime_factorization(v):
                if q != 2:
                    engaged.add(q)
        # rough mean "lifetime" of an odd prime: how many consecutive
        # steps any given odd prime stays engaged once it appears
        lifetimes: list[int] = []
        for q in engaged:
            run = 0
            for v in seq:
                if v % q == 0:
                    run += 1
                else:
                    if run > 0:
                        lifetimes.append(run)
                    run = 0
            if run > 0:
                lifetimes.append(run)
        samples.append({
            "n": n,
            "steps": len(seq) - 1,
            "distinct_odd_primes": len(engaged),
            "mean_lifetime": float(np.mean(lifetimes)) if lifetimes else 0.0,
        })

    steps = np.array([s["steps"] for s in samples])
    n_op = np.array([s["distinct_odd_primes"] for s in samples])
    life = np.array([s["mean_lifetime"] for s in samples])
    print(f"  orbits sampled: {len(samples)}")
    print(f"  mean orbit length: {steps.mean():.1f}  (max {steps.max()})")
    print(f"  mean distinct odd primes engaged per orbit: {n_op.mean():.2f}  "
          f"(max {n_op.max()})")
    print(f"  mean odd-prime lifetime (consecutive steps engaged): {life.mean():.2f}")
    # Quick correlation: longer orbits -> more distinct primes?
    if np.std(steps) > 0:
        corr = np.corrcoef(steps, n_op)[0, 1]
        print(f"  corr(orbit length, distinct odd primes engaged) = {corr:+.3f}")


# ----------------------------------------------------------------------


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(exist_ok=True)

    figure_engagement(out_dir / "collatz_prime_gear_engagement.png", n_start=27)
    figure_occupancy(out_dir / "collatz_prime_occupancy_heatmap.png",
                     dropping_sets=[3, 6, 8, 11], limit=4000)
    figure_gear_periods(out_dir / "collatz_prime_gear_periods.png",
                        prime_limit=300, max_class=25)
    figure_lissajous(out_dir / "collatz_prime_lissajous.png",
                     n_start=27, pairs=[(3, 5), (5, 7), (3, 7), (7, 11)])

    print_prime_shedding_stats(limit=2000)

    print("\nDone — four prime-gear figures generated.")


if __name__ == "__main__":
    main()
