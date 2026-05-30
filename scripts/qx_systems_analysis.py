"""qx+1 Collatz cousins — loops + Sturmian footprint.

For q ∈ {3, 5, 7, 9}, the qx+1 map is

    T_q(n) = (qn + 1) / 2   if n odd,
             n / 2          if n even.

Three structural predictions to test, all derived from the same picture
(Beatty line of slope log_2 q):

  (1) NONTRIVIAL CYCLES exist for q ≥ 5.
      For q = 3, the Collatz conjecture says only the trivial 1-cycle.

  (2) DROPPING SCHEDULE follows the Beatty list
          k_o = o + ⌊o log_2 q⌋ + 1
      regardless of q. So |R_k^{(q)}| is nonzero EXACTLY on this list.

  (3) THE TERRAS PARTIAL SUM Σ_k |R_k^{(q)}| / 2^k → 1 only if every
      residue eventually drops. For q ≥ 5 it stops short of 1 — the gap
      is the 2-adic density of cycle-residues. So the same data that
      verifies the Sturmian schedule (via Beatty rungs) ALSO verifies
      cycles (via the Terras gap), without needing to find them
      explicitly.

  (4) STURMIAN FOOTPRINT — the gap sequence k_o - k_{o-1} ∈ {⌊α⌋+1, ⌊α⌋+2}
      should have factor complexity p(n) = n + 1 for every n (Sturmian).

Outputs:
    data/qx_systems_analysis.png
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Hardcoded |R_k^{(3)}| from prior computations (extends past int64-safe range)
RK_Q3: dict[int, int] = {
    1: 1, 3: 2, 6: 4, 8: 16, 11: 48, 13: 224, 16: 768, 19: 3840,
    21: 21760, 24: 88576, 26: 487424, 29: 1968128,
}


def step_one(n: int, q: int) -> int:
    return n // 2 if n % 2 == 0 else q * n + 1


def find_cycles(q: int, n_max: int = 10000, step_limit: int = 50000,
                value_limit: int = 10 ** 14
                ) -> tuple[int, dict[int, list[int]], int]:
    """Search for nontrivial cycles in qx+1 from odd starts 1..n_max.

    Returns (converging_count, cycles, inconclusive_count) where
    cycles maps min(cycle) -> sorted list of cycle members.
    """
    converges_to_1: set[int] = {1}
    cycle_min_of: dict[int, int] = {}
    cycles: dict[int, list[int]] = {}
    converging = 0
    inconclusive = 0

    for n_start in range(1, n_max + 1, 2):
        n = n_start
        history: dict[int, int] = {}
        step = 0
        outcome = None
        new_cycle_min: int | None = None
        while step < step_limit:
            if n in converges_to_1:
                outcome = 'conv'
                break
            if n in cycle_min_of:
                outcome = 'cycle'
                new_cycle_min = cycle_min_of[n]
                break
            if n in history:
                # New cycle discovered between history[n] and step
                start_step = history[n]
                cycle_members: list[int] = []
                walk = n
                for _ in range(step - start_step):
                    cycle_members.append(walk)
                    walk = step_one(walk, q)
                m = min(cycle_members)
                if m not in cycles:
                    cycles[m] = sorted(set(cycle_members))
                for c in cycle_members:
                    cycle_min_of[c] = m
                outcome = 'cycle'
                new_cycle_min = m
                break
            if n > value_limit:
                outcome = 'incl'
                break
            history[n] = step
            n = step_one(n, q)
            step += 1
        else:
            outcome = 'incl'

        if outcome == 'conv':
            converging += 1
            for v in history:
                converges_to_1.add(v)
        elif outcome == 'cycle' and new_cycle_min is not None:
            for v in history:
                cycle_min_of[v] = new_cycle_min
        else:
            inconclusive += 1

    return converging, cycles, inconclusive


def compute_Rk_py(q: int, K_max: int) -> np.ndarray:
    """Empirical |R_k^{(q)}|, normalized as standard residues-mod-2^k counts.

    Enumerates r ∈ [1, 2^K_max). At each k, normalizes by 2^(K_max - k)
    because each residue class mod 2^k appears 2^(K_max - k) times in the
    enumeration. The result `sizes[k]` equals the standard |R_k| (count of
    residues mod 2^k that drop at exactly step k).
    """
    raw = [0] * (K_max + 1)
    R_total = 2 ** K_max
    for r in range(1, R_total):
        n = r
        for step in range(1, K_max + 1):
            if n % 2 == 0:
                n //= 2
            else:
                n = q * n + 1
            if n < r:
                raw[step] += 1
                break
    sizes = np.zeros(K_max + 1, dtype=np.int64)
    for k in range(1, K_max + 1):
        denom = 2 ** (K_max - k)
        # Round, not floor — accounts for excluded r=0 (which never drops)
        sizes[k] = round(raw[k] / denom)
    return sizes


def predicted_beatty(q: int, K_max: int, include_zero: bool = True) -> list[int]:
    """Predicted dropping times ≤ K_max.

    With `include_zero=True`, prepend k_0 = 1 to represent the even-start
    case (every even residue drops at step 1, giving |R_1| = 1 by the
    standard mod-2 convention).
    """
    slope = math.log2(q)
    ks: list[int] = [1] if include_zero else []
    for o in range(1, K_max + 1):
        k = o + int(math.floor(o * slope)) + 1
        if k <= K_max:
            ks.append(k)
    return ks


def beatty_gap_sequence(q: int, O_max: int) -> list[int]:
    """Predicted gap sequence k_o - k_{o-1} for o = 1..O_max."""
    slope = math.log2(q)
    gaps: list[int] = []
    prev = 1
    for o in range(1, O_max + 1):
        k = o + int(math.floor(o * slope)) + 1
        gaps.append(k - prev)
        prev = k
    return gaps


def block_factor_complexity(seq: list[int], n_max: int) -> list[int]:
    out: list[int] = []
    for n in range(1, n_max + 1):
        if n > len(seq):
            out.append(0); continue
        seen: set[tuple] = set()
        for i in range(len(seq) - n + 1):
            seen.add(tuple(seq[i:i + n]))
        out.append(len(seen))
    return out


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(exist_ok=True)

    qs = [3, 5, 7, 9]
    K_max_q = {3: 29, 5: 18, 7: 17, 9: 15}  # q=3 uses hardcoded R_k table
    O_max = 4096
    n_max_blk = 30

    results: dict[int, dict] = {}

    # ===== Part 1: Cycle detection =====
    print("=" * 78)
    print("Part 1 — Cycle detection (odd starts 1..10000)")
    print("=" * 78)
    for q in qs:
        print(f"\nSearching cycles in {q}x+1 dynamics...")
        conv, cycles, incl = find_cycles(q, n_max=10000)
        results[q] = {'converging': conv, 'cycles': cycles, 'inconclusive': incl}
        n_starts = (10000 + 1) // 2
        print(f"  {conv}/{n_starts} odd starts converge to 1")
        print(f"  {incl} inconclusive (exceeded value or step limit)")
        if cycles:
            print(f"  {len(cycles)} nontrivial cycle(s) found:")
            for min_elt, mems in sorted(cycles.items()):
                preview = ", ".join(str(x) for x in mems[:6])
                if len(mems) > 6:
                    preview += f", ... ({len(mems)} elts)"
                print(f"     • min={min_elt} (length {len(mems)}): [{preview}]")
        else:
            print(f"  no nontrivial cycles found "
                  f"(consistent with Collatz conjecture)")

    # ===== Part 2: Dropping schedule and Terras-style sum =====
    print()
    print("=" * 78)
    print("Part 2 — Dropping schedule |R_k^(q)| and Beatty prediction")
    print("=" * 78)
    for q in qs:
        K = K_max_q[q]
        if q == 3:
            sizes = np.zeros(K + 1, dtype=np.int64)
            for k, v in RK_Q3.items():
                if k <= K:
                    sizes[k] = v
            print(f"\nq={q}: using precomputed R_k table (K_max={K})")
        else:
            print(f"\nq={q}: computing |R_k| for k=1..{K} "
                  f"(2^{K} = {2**K} residues)...")
            sizes = compute_Rk_py(q, K)
        results[q]['Rk'] = sizes
        nonzero_k = [int(k) for k in np.where(sizes > 0)[0]]
        beatty_k = predicted_beatty(q, K)
        # Empirical may contain k=1 (even-residue case) and the o≥1 Beatty rungs
        match = nonzero_k == beatty_k[:len(nonzero_k)]
        print(f"  Beatty prediction (k_0=1, then k_o):  {beatty_k}")
        print(f"  Empirical nonzero k indices:           {nonzero_k}")
        print(f"  Beatty match: {'✓' if match else '✗'}")
        for k in nonzero_k:
            print(f"     k={k}: |R_{k}^({q})| = {int(sizes[k])}")
        # Terras-style partial sum
        partials = np.cumsum(sizes / np.power(2.0, np.arange(K + 1)))
        results[q]['terras'] = partials
        gap = 1.0 - partials[-1]
        print(f"  Σ_{{k≤{K}}} |R_k|/2^k = {partials[-1]:.6f}")
        if q == 3:
            print(f"     gap from 1 = {gap:.6f} (residues with stopping time > {K})")
        else:
            print(f"     gap from 1 = {gap:.6f} (includes density of cycle-residues)")

    # ===== Part 3: Sturmian footprint =====
    print()
    print("=" * 78)
    print("Part 3 — Sturmian factor-complexity footprint of gap sequence")
    print("=" * 78)
    for q in qs:
        slope = math.log2(q)
        gaps = beatty_gap_sequence(q, O_max)
        gap_pair = sorted(set(gaps))
        if len(gap_pair) != 2:
            print(f"\nq={q}: gap sequence has {len(gap_pair)} distinct values — "
                  f"not binary Sturmian")
            results[q]['fingerprint'] = None
            continue
        seq = [0 if g == gap_pair[0] else 1 for g in gaps]
        density = sum(seq) / len(seq)
        comp = block_factor_complexity(seq, n_max_blk)
        matches = sum(1 for n, p in enumerate(comp, 1) if p == n + 1)
        results[q]['fingerprint'] = {
            'slope': slope, 'gap_pair': gap_pair, 'density': density,
            'comp': comp, 'matches': matches,
        }
        print(f"\nq={q}: slope = log_2({q}) = {slope:.4f}")
        print(f"   gap-pair = {tuple(gap_pair)}   "
              f"density(gap={gap_pair[1]}) = {density:.4f}")
        print(f"   Predicted density: {slope} - {math.floor(slope) + 1} "
              f"= {slope - (math.floor(slope) + 1):.4f}  (fractional part of slope)")
        print(f"   p(n) = n+1 for {matches}/{n_max_blk} window sizes  "
              f"{'✓ Sturmian' if matches == n_max_blk else '✗ deviation'}")

    # ===== Plot =====
    fig, axes = plt.subplots(3, len(qs), figsize=(4.2 * len(qs), 11))
    for col, q in enumerate(qs):
        K = K_max_q[q]
        sizes = results[q]['Rk']
        terras = results[q]['terras']
        cycles = results[q]['cycles']
        ks = np.arange(K + 1)
        nonzero = sizes > 0

        # Row 1: |R_k| with Beatty rungs
        ax = axes[0, col]
        beatty_k = predicted_beatty(q, K)
        for bk in beatty_k:
            ax.axvline(bk, color='gray', ls=':', lw=0.6, alpha=0.45)
        if nonzero.any():
            ax.semilogy(ks[nonzero], np.maximum(sizes[nonzero], 1), 'o-',
                        color=f'C{col}', label='measured', ms=6)
        ax.set_title(f"q = {q}: |R_k| on Beatty rungs")
        ax.set_xlabel("k")
        ax.set_ylabel("|R_k|  (log scale)")
        ax.set_xlim(0, K + 1)
        ax.grid(True, alpha=0.3, which='both')
        ax.legend(fontsize=8)

        # Row 2: Terras partial sum
        ax = axes[1, col]
        ax.plot(ks, terras, color=f'C{col}', marker='.', ms=5, lw=1.2)
        ax.axhline(1.0, color='black', ls='--', lw=0.8)
        if terras[-1] < 1.0:
            ax.fill_between(ks, terras, 1.0,
                            where=terras < 1, alpha=0.15, color='red',
                            label='gap to 1')
        ax.set_title(f"q = {q}: Terras partial sum")
        ax.set_xlabel("K")
        ax.set_ylabel("partial sum")
        ax.set_ylim(0, 1.1)
        n_cyc = len(cycles)
        label = f"Σ → {terras[-1]:.4f}\n{n_cyc} cycle{'s' if n_cyc != 1 else ''}"
        ax.text(0.05, 0.05, label, transform=ax.transAxes, fontsize=10,
                bbox=dict(facecolor='white', edgecolor='gray', alpha=0.85))
        ax.legend(fontsize=8, loc='lower right')
        ax.grid(True, alpha=0.3)

        # Row 3: Sturmian factor complexity
        ax = axes[2, col]
        fp = results[q].get('fingerprint')
        if fp is not None:
            ns = np.arange(1, n_max_blk + 1)
            ax.plot(ns, ns + 1, 'k--', lw=1, label=r'Sturmian: $p(n)=n+1$')
            ax.plot(ns, 2.0 ** ns, 'r:', lw=0.8, label=r'$2^n$ (full)')
            ax.scatter(ns, fp['comp'], color=f'C{col}', s=30,
                       edgecolor='black', linewidth=0.5,
                       label=f"q={q}: {fp['matches']}/{n_max_blk}")
            ax.set_yscale('log')
            ax.set_ylim(1, 2 ** 15)
            ax.set_xlabel("n")
            ax.set_ylabel("p(n)  (log)")
            slope_str = f"log2({q}) = {fp['slope']:.3f}"
            mark = '[OK]' if fp['matches'] == n_max_blk else '[FAIL]'
            ax.set_title(f"q = {q}: factor complexity {mark}\nslope = {slope_str}")
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3, which='both')

    fig.suptitle("qx+1 Collatz cousins: loops, dropping schedule, "
                 "Sturmian footprint", fontsize=13, y=0.997)
    fig.subplots_adjust(hspace=0.5, wspace=0.35, left=0.06, right=0.98,
                        top=0.94, bottom=0.05)
    out_png = out_dir / "qx_systems_analysis.png"
    fig.savefig(out_png, dpi=120, bbox_inches='tight', facecolor='white')
    print(f"\nSaved {out_png}")

    # ===== Summary =====
    print()
    print("=" * 78)
    print("Summary")
    print("=" * 78)
    print(f"{'q':>3} {'cycles':>8} {'sample mins':>22} {'Terras':>10} "
          f"{'p(n)=n+1':>14}")
    print("-" * 70)
    for q in qs:
        r = results[q]
        n_cyc = len(r['cycles'])
        sample = ", ".join(str(m) for m in sorted(r['cycles'].keys())[:3]) or '—'
        terras_final = r['terras'][-1]
        fp = r.get('fingerprint')
        fp_str = f"{fp['matches']}/{n_max_blk}" if fp else 'n/a'
        print(f"{q:>3d} {n_cyc:>8d} {sample:>22} {terras_final:>10.4f} "
              f"{fp_str:>14}")


if __name__ == "__main__":
    main()
