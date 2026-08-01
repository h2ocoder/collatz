# Prime Constellation Signatures Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an exploratory study of whether prime constellations (twins $g{=}2$, cousins $g{=}4$, sexy $g{=}6$) carry structure in their Collatz 2-adic / 3-adic dropping signatures beyond what the gap-forced coupling and Hardy–Littlewood already predict.

**Architecture:** One new library module `collatz/constellations.py` exposes pair enumeration, the joint dropping-signature histogram, an admissible-integer **coupling null**, and the forced-coupling residue table. One new script `scripts/prime_constellation_signatures.py` sweeps primes to $N=10^7$ over the three gaps, compares observed pairs to (a) the generic single-prime marginal and (b) the coupling null, and renders five figures. Tests pin the gap-forced coupling invariants and null determinism. A light notebook and a findings note complete it.

**Tech Stack:** Python 3.12, NumPy, Matplotlib (Agg backend), pytest. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-06-14-prime-constellation-signatures-design.md`

**Conventions to follow:**
- Tests live flat in `tests/test_<module>.py` (match `test_residues.py`).
- Functions get docstrings with concrete `Example:` lines.
- Scripts call `matplotlib.use("Agg")` at top-of-file and write PNGs to `data/`.
- Run tests via `python -m pytest tests/test_constellations.py -v`.
- Conventional Commits (`feat(constellations): …`, `test(constellations): …`).

**Reuse notes (DRY):**
- `collatz.residues.prime_sieve(n)` → sorted int64 primes ≤ n.
- `collatz.dropping.dropping_set(n)` → dropping time $k$ (n>1).
- `collatz.dropping.orbital_oddity(n)` → **the odd-step count $s$** (number of $3x{+}1$ steps before the drop). No new helper needed; `dropping.py` is NOT modified.
- Fact used by tests: $n \equiv 1 \pmod 4 \Rightarrow \text{dropping\_set}(n) = 3$ (Dropping Set 3 is exactly $\{n \equiv 1 \bmod 4\}$).

---

## File Structure

```
collatz/
  constellations.py                       # NEW (<~250 lines)
scripts/
  prime_constellation_signatures.py       # NEW
tests/
  test_constellations.py                  # NEW
notebooks/
  03-prime-constellations.ipynb           # NEW (light)
docs/Explorations/
  Prime Constellation Signatures.md       # NEW
data/
  collatz_constellation_coupling.png      # NEW (output)
  collatz_constellation_joint.png         # NEW (output)
  collatz_constellation_marginal.png      # NEW (output)
  collatz_constellation_genus.png         # NEW (output)
```

> The optional internal-space **phase** figure from the spec (layer 5) is
> intentionally **deferred to Phase D** — it is only worth building if layers
> 1–4 leave an open thread. This plan ships four figures; no task produces a
> phase PNG.

---

### Task 1: Module skeleton + `prime_pairs`

**Files:**
- Create: `collatz/constellations.py`
- Create: `tests/test_constellations.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_constellations.py
"""Tests for collatz.constellations — prime constellation dropping signatures."""

import numpy as np
import pytest

from collatz.constellations import prime_pairs


def _brute_pairs(n_max, gap):
    from collatz.residues import prime_sieve
    primes = set(prime_sieve(n_max + gap).tolist())
    return [p for p in sorted(primes) if p <= n_max and (p + gap) in primes]


def test_prime_pairs_twins_small():
    """Twins (g=2) up to 30: (3,5),(5,7),(11,13),(17,19),(29,31)."""
    ps = prime_pairs(30, 2)
    assert list(ps) == [3, 5, 11, 17, 29]


def test_prime_pairs_cousins_small():
    """Cousins (g=4) up to 20: (3,7),(7,11),(13,17),(19,23->23>20 excluded)."""
    ps = prime_pairs(20, 4)
    assert list(ps) == [3, 7, 13]


def test_prime_pairs_sexy_small():
    """Sexy (g=6) up to 20: (5,11),(7,13),(11,17),(13,19),(17,23)."""
    ps = prime_pairs(20, 6)
    assert list(ps) == [5, 7, 11, 13, 17]


def test_prime_pairs_matches_brute_force():
    """Agree with a set-membership brute force up to 10**4 for all three gaps."""
    for gap in (2, 4, 6):
        assert list(prime_pairs(10_000, gap)) == _brute_pairs(10_000, gap)


def test_prime_pairs_returns_int_array():
    ps = prime_pairs(30, 2)
    assert isinstance(ps, np.ndarray)
    assert ps.dtype.kind == "i"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_constellations.py -v`
Expected: FAIL with `ImportError: cannot import name 'prime_pairs' from 'collatz.constellations'`.

- [ ] **Step 3: Write the module skeleton + `prime_pairs`**

```python
# collatz/constellations.py
"""Prime constellation dropping signatures (exploratory).

A constellation of gap g is a pair (p, p+g) with both members prime.  This
module enumerates such pairs (`prime_pairs`), attaches each pair its joint
Collatz dropping signature (`pair_signature`, `joint_signature_counts`),
builds an admissible-integer **coupling null** for that joint distribution
(`coupling_null_counts`), and tabulates the gap-forced residue coupling
(`forced_coupling_table`).

Reuses `collatz.residues.prime_sieve` and `collatz.dropping.dropping_set`;
the 3-adic odd-step count s is `collatz.dropping.orbital_oddity`.
"""
from __future__ import annotations

from collections import Counter

import numpy as np

from .dropping import dropping_set
from .residues import prime_sieve

K_CAP = 15  # dropping sets at or beyond this fold into a single k>=K_CAP bin


def prime_pairs(n_max: int, gap: int) -> np.ndarray:
    """Primes p <= n_max such that p + gap is also prime, as an int64 array.

    Example: prime_pairs(30, 2) -> array([ 3,  5, 11, 17, 29])
    """
    if gap <= 0 or gap % 2 != 0:
        raise ValueError("gap must be a positive even integer")
    primes = prime_sieve(n_max + gap)
    is_prime = np.zeros(n_max + gap + 1, dtype=bool)
    is_prime[primes] = True
    base = primes[primes <= n_max]
    keep = is_prime[base + gap]
    return base[keep].astype(np.int64)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_constellations.py -v`
Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/constellations.py tests/test_constellations.py
git commit -m "feat(constellations): module skeleton + prime_pairs"
```

---

### Task 2: `pair_signature` + `joint_signature_counts`

**Files:**
- Modify: `collatz/constellations.py`
- Modify: `tests/test_constellations.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_constellations.py`:

```python
from collatz.constellations import pair_signature, joint_signature_counts
from collatz.dropping import dropping_set


def test_pair_signature_twin_3_5():
    """(3,5): dropping_set(3)=6, dropping_set(5)=3 -> capped unchanged."""
    assert pair_signature(3, 2) == (dropping_set(3), dropping_set(5))


def test_pair_signature_caps_large_k():
    """A k above the cap folds to K_CAP; small k passes through."""
    from collatz.constellations import K_CAP
    kp, kq = pair_signature(3, 2, k_cap=2)
    assert kp == 2 and kq == 2  # both real k>2, capped to 2


def test_joint_counts_total_equals_pair_count():
    """Sum of the joint histogram equals the number of pairs."""
    from collatz.constellations import prime_pairs
    pairs = prime_pairs(10_000, 2)
    counts = joint_signature_counts(pairs, 2)
    assert sum(counts.values()) == len(pairs)


def test_joint_counts_twin_fast_slow_forced():
    """Every twin pair has exactly one member in dropping set 3 (the 1-mod-4 one)."""
    from collatz.constellations import prime_pairs
    pairs = prime_pairs(100_000, 2)
    counts = joint_signature_counts(pairs, 2)
    # In every (kp, kq) key, exactly one coordinate is 3.
    for (kp, kq), c in counts.items():
        assert (kp == 3) ^ (kq == 3), f"twin signature {(kp, kq)} not fast/slow"
```

- [ ] **Step 2: Run new tests to verify they fail**

Run: `python -m pytest tests/test_constellations.py -v`
Expected: 5 PASS + 4 FAIL with `ImportError`.

- [ ] **Step 3: Implement both functions**

Append to `collatz/constellations.py`:

```python
def _capped_set(n: int, k_cap: int) -> int:
    """dropping_set(n) clipped to k_cap."""
    return min(dropping_set(n), k_cap)


def pair_signature(p: int, gap: int, k_cap: int = K_CAP) -> tuple[int, int]:
    """Joint dropping signature (k_p, k_{p+gap}), each capped at k_cap.

    Example: pair_signature(3, 2) == (6, 3)
    """
    return (_capped_set(p, k_cap), _capped_set(p + gap, k_cap))


def joint_signature_counts(pairs, gap: int, k_cap: int = K_CAP) -> dict:
    """Counter over capped (k_p, k_{p+gap}) for every p in `pairs`.

    `pairs` is any iterable of ints (e.g. the output of prime_pairs).
    Returns a plain dict keyed by (int, int).
    """
    counts = Counter()
    for p in np.asarray(pairs).tolist():
        counts[pair_signature(p, gap, k_cap)] += 1
    return dict(counts)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_constellations.py -v`
Expected: 9 PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/constellations.py tests/test_constellations.py
git commit -m "feat(constellations): pair_signature + joint_signature_counts"
```

---

### Task 3: `coupling_null_counts` (admissible-integer null)

**Files:**
- Modify: `collatz/constellations.py`
- Modify: `tests/test_constellations.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_constellations.py`:

```python
from collatz.constellations import coupling_null_counts


def test_null_keys_are_signature_pairs():
    """Null histogram keys are (int, int) dropping-set signatures."""
    null = coupling_null_counts(10_000, 2, stride=1)
    assert null
    for key in null:
        assert isinstance(key, tuple) and len(key) == 2


def test_null_is_deterministic():
    """Same arguments -> identical histogram (no RNG)."""
    a = coupling_null_counts(50_000, 2, stride=5)
    b = coupling_null_counts(50_000, 2, stride=5)
    assert a == b


def test_null_fast_slow_forced_for_twins():
    """The g=2 integer null also forces exactly one dropping-set-3 coordinate."""
    null = coupling_null_counts(20_000, 2, stride=1)
    for (kp, kq) in null:
        assert (kp == 3) ^ (kq == 3)


def test_null_stride_subsamples():
    """A larger stride yields no more sampled integers than a smaller one."""
    fine = sum(coupling_null_counts(50_000, 2, stride=1).values())
    coarse = sum(coupling_null_counts(50_000, 2, stride=10).values())
    assert coarse <= fine
    assert coarse > 0
```

- [ ] **Step 2: Run new tests to verify they fail**

Run: `python -m pytest tests/test_constellations.py -v`
Expected: 9 PASS + 4 FAIL with `ImportError`.

- [ ] **Step 3: Implement `coupling_null_counts`**

Append to `collatz/constellations.py`:

```python
def coupling_null_counts(
    n_max: int, gap: int, k_cap: int = K_CAP, stride: int = 1
) -> dict:
    """Joint dropping-signature histogram over admissible integers (the null).

    Iterates odd n in [3, n_max - gap], taking every `stride`-th odd value,
    and counts the capped signature (dropping_set(n), dropping_set(n+gap)).
    Because every odd n with even gap has n+gap odd, these are exactly the
    integers admissible for the constellation at the prime 2 -- so by
    Hardy-Littlewood the prime pairs inherit this 2-adic distribution, and
    any deviation of observed pairs from it is genuine correlation.

    Deterministic: no randomness, fixed systematic stride.

    Example: sum(coupling_null_counts(31, 2, stride=1).values()) == 14
             (odd n = 3,5,...,29; n+2 <= 31)
    """
    if gap <= 0 or gap % 2 != 0:
        raise ValueError("gap must be a positive even integer")
    if stride < 1:
        raise ValueError("stride must be >= 1")
    counts = Counter()
    step = 2 * stride  # stay on odd integers
    n = 3
    upper = n_max - gap
    while n <= upper:
        sig = (_capped_set(n, k_cap), _capped_set(n + gap, k_cap))
        counts[sig] += 1
        n += step
    return dict(counts)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_constellations.py -v`
Expected: 13 PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/constellations.py tests/test_constellations.py
git commit -m "feat(constellations): admissible-integer coupling null"
```

---

### Task 4: `forced_coupling_table` (the residue skeleton)

**Files:**
- Modify: `collatz/constellations.py`
- Modify: `tests/test_constellations.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_constellations.py`:

```python
from collatz.constellations import forced_coupling_table


def test_coupling_table_twin_one_of_each_mod4():
    """g=2: in every odd residue row, exactly one member is 1 mod 4 (fast)."""
    rows = forced_coupling_table(2, 8)
    for a, b, fast_a, fast_b in rows:
        assert fast_a == (a % 4 == 1)
        assert fast_b == (b % 4 == 1)
        assert fast_a ^ fast_b  # exactly one fast member


def test_coupling_table_cousin_same_mod4():
    """g=4: both members share their mod-4 class (both fast or both slow)."""
    rows = forced_coupling_table(4, 8)
    for a, b, fast_a, fast_b in rows:
        assert fast_a == fast_b


def test_coupling_table_covers_odd_residues():
    """Rows are exactly the odd residues mod the modulus."""
    rows = forced_coupling_table(2, 8)
    assert [r[0] for r in rows] == [1, 3, 5, 7]
```

- [ ] **Step 2: Run new tests to verify they fail**

Run: `python -m pytest tests/test_constellations.py -v`
Expected: 13 PASS + 3 FAIL with `ImportError`.

- [ ] **Step 3: Implement `forced_coupling_table`**

Append to `collatz/constellations.py`:

```python
def forced_coupling_table(gap: int, modulus: int) -> list[tuple[int, int, bool, bool]]:
    """The gap-forced residue coupling, one row per odd residue mod `modulus`.

    Each row is (a, (a+gap) mod modulus, fast_a, fast_b) where `fast_x` marks
    a member in dropping set 3 (equivalently x ≡ 1 mod 4, the fast dropper).
    This is a pure-arithmetic theorem -- no primes involved -- and anchors the
    empirical figures.

    Example: forced_coupling_table(2, 8)[0] == (1, 3, True, False)
    """
    if gap <= 0 or gap % 2 != 0:
        raise ValueError("gap must be a positive even integer")
    rows = []
    for a in range(1, modulus, 2):
        b = (a + gap) % modulus
        rows.append((a, b, a % 4 == 1, b % 4 == 1))
    return rows
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_constellations.py -v`
Expected: 16 PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/constellations.py tests/test_constellations.py
git commit -m "feat(constellations): forced-coupling residue table"
```

---

### Task 5: Script — sweep + console summary (data pipeline)

**Files:**
- Create: `scripts/prime_constellation_signatures.py`

No unit tests — correctness rests on tested library code plus a smoke run.

- [ ] **Step 1: Create the script with the data pipeline and summary**

```python
# scripts/prime_constellation_signatures.py
"""Prime constellation dropping signatures: observed pairs vs nulls.

For gaps g in {2, 4, 6} (twins, cousins, sexy primes) and primes p <= N:
classify each pair (p, p+g) by its joint Collatz dropping signature, and
compare to (a) the generic single-prime marginal and (b) the admissible-
integer coupling null.  Render five figures and print a per-gap summary.

Outputs (data/):
    collatz_constellation_coupling.png   forced-coupling skeleton (all gaps)
    collatz_constellation_joint.png      joint k_p x k_{p+g} heatmaps
    collatz_constellation_marginal.png   headline: marginal bars + joint ratio
    collatz_constellation_genus.png      3-adic odd-step (s) refinement
    collatz_constellation_phase.png      optional internal-space phase scatter
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from collatz.constellations import (  # noqa: E402
    K_CAP,
    coupling_null_counts,
    forced_coupling_table,
    joint_signature_counts,
    prime_pairs,
)
from collatz.dropping import dropping_set, orbital_oddity  # noqa: E402
from collatz.residues import prime_sieve  # noqa: E402

# ----- Configuration ---------------------------------------------------
N = 10_000_000
GAPS = (2, 4, 6)
NULL_STRIDE = 5  # systematic subsample of odd integers for the null
OUT_DIR = Path(__file__).resolve().parent.parent / "data"
GAP_NAME = {2: "twins", 4: "cousins", 6: "sexy"}


# ----- Data pipeline ---------------------------------------------------
def generic_prime_marginal(primes: np.ndarray, k_cap: int = K_CAP) -> dict:
    """Dropping-set distribution over all single primes (the HL marginal)."""
    counts = Counter()
    for p in primes.tolist():
        counts[min(dropping_set(p), k_cap)] += 1
    return dict(counts)


def slow_member_marginal(joint: dict) -> dict:
    """Marginal over the SLOW member (the coordinate that is not dropping set 3).

    Falls back to the larger coordinate when neither is exactly 3 (cousins).
    """
    counts = Counter()
    for (kp, kq), c in joint.items():
        slow = kq if kp == 3 else (kp if kq == 3 else max(kp, kq))
        counts[slow] += c
    return dict(counts)


def odd_step_joint(pairs: np.ndarray, gap: int, coprime3: bool) -> dict:
    """Joint (s_p, s_{p+g}) histogram via orbital_oddity (the 3-adic layer)."""
    counts = Counter()
    for p in pairs.tolist():
        if coprime3 and (p % 3 == 0 or (p + gap) % 3 == 0):
            continue
        counts[(orbital_oddity(p), orbital_oddity(p + gap))] += 1
    return dict(counts)


def odd_step_null(n_max: int, gap: int, stride: int, coprime3: bool) -> dict:
    """Coupling null for the (s_p, s_{p+g}) odd-step histogram."""
    counts = Counter()
    step = 2 * stride
    n = 3
    while n <= n_max - gap:
        if not (coprime3 and (n % 3 == 0 or (n + gap) % 3 == 0)):
            counts[(orbital_oddity(n), orbital_oddity(n + gap))] += 1
        n += step
    return dict(counts)


def chi_squared(obs: dict, exp_density: dict, total_obs: int) -> float:
    """Chi-squared of observed marginal vs an expected density (normalized)."""
    chi = 0.0
    for k, d in exp_density.items():
        expected = d * total_obs
        if expected > 0:
            chi += (obs.get(k, 0) - expected) ** 2 / expected
    return chi


def total_variation(obs: dict, null: dict) -> float:
    """Total-variation distance between two histograms (normalized to densities)."""
    so, sn = sum(obs.values()) or 1, sum(null.values()) or 1
    keys = set(obs) | set(null)
    return 0.5 * sum(abs(obs.get(k, 0) / so - null.get(k, 0) / sn) for k in keys)


def density(hist: dict) -> dict:
    total = sum(hist.values()) or 1
    return {k: v / total for k, v in hist.items()}


def print_summary(gap, pairs, joint, null, generic):
    name = GAP_NAME[gap]
    slow = slow_member_marginal(joint)
    gen_density = density(generic)
    chi = chi_squared(slow, gen_density, sum(slow.values()))
    tv = total_variation(joint, null)
    print(f"\n=== g={gap} ({name}) — {len(pairs)} pairs ===")
    print(f"  chi^2 (slow marginal vs generic primes): {chi:.1f}")
    print(f"  total-variation (joint vs coupling null): {tv:.4f}")
    obs_d, null_d = density(joint), density(null)
    devs = sorted(
        ((obs_d.get(k, 0) - null_d.get(k, 0), k) for k in set(obs_d) | set(null_d)),
        key=lambda t: abs(t[0]),
        reverse=True,
    )[:5]
    print("  top deviating joint cells (obs_density - null_density):")
    for d, k in devs:
        print(f"    {k}: {d:+.5f}")
```

- [ ] **Step 2: Add the `main()` data driver (figures come in Task 6)**

Append to `scripts/prime_constellation_signatures.py`:

```python
def compute(gap):
    """All histograms for one gap. Returns a dict bundle."""
    pairs = prime_pairs(N, gap)
    joint = joint_signature_counts(pairs, gap)
    null = coupling_null_counts(N, gap, stride=NULL_STRIDE)
    coprime3 = gap % 3 == 0  # the g=6 3-adic cross-check
    return {
        "gap": gap,
        "pairs": pairs,
        "joint": joint,
        "null": null,
        "s_joint": odd_step_joint(pairs, gap, coprime3),
        "s_null": odd_step_null(N, gap, NULL_STRIDE, coprime3),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Sieving primes up to {N}...")
    primes = prime_sieve(N)
    generic = generic_prime_marginal(primes)
    print(f"pi({N}) = {primes.size}")

    bundles = []
    for gap in GAPS:
        print(f"Computing g={gap} ({GAP_NAME[gap]})...")
        b = compute(gap)
        bundles.append(b)
        print_summary(gap, b["pairs"], b["joint"], b["null"], generic)

    # Figures (defined in Task 6)
    render_all(bundles, generic)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Add a temporary stub so the script imports cleanly**

Append (will be replaced in Task 6):

```python
def render_all(bundles, generic):  # noqa: F811  (replaced in Task 6)
    print("[render_all stub — figures added in Task 6]")
```

- [ ] **Step 4: Smoke-run the pipeline at reduced N**

```bash
python -c "
import scripts.prime_constellation_signatures as s
s.N = 200_000
s.NULL_STRIDE = 3
s.main()
"
```

Expected: completes in well under a minute; prints `pi(200000) = 17984`, then a summary block per gap. Twins and sexy summaries show every top-deviating joint cell having exactly one coordinate equal to 3; cousins do not. χ² values are finite; total-variation values are small (order 1e-3 to 1e-2). The render stub line prints last.

- [ ] **Step 5: Commit**

```bash
git add scripts/prime_constellation_signatures.py
git commit -m "feat(scripts): constellation signature pipeline + console summary"
```

---

### Task 6: Script — five figures

**Files:**
- Modify: `scripts/prime_constellation_signatures.py`

- [ ] **Step 1: Replace the `render_all` stub with the figure functions**

Delete the Task-5 `render_all` stub and append:

```python
def _joint_grid(hist, k_cap=K_CAP):
    """Dense (k_cap+1) x (k_cap+1) array from a sparse joint histogram."""
    g = np.zeros((k_cap + 1, k_cap + 1), dtype=float)
    for (kp, kq), c in hist.items():
        g[min(kp, k_cap), min(kq, k_cap)] = c
    return g


def fig_coupling(out_path):
    """Forced-coupling skeleton: mod-8 residue map per gap, fast/slow tagged."""
    fig, axes = plt.subplots(1, len(GAPS), figsize=(15, 4))
    for ax, gap in zip(axes, GAPS):
        rows = forced_coupling_table(gap, 8)
        grid = np.zeros((len(rows), 2))
        labels = []
        for i, (a, b, fa, fb) in enumerate(rows):
            grid[i] = [1.0 if fa else 0.2, 1.0 if fb else 0.2]
            labels.append(f"{a}|{b}")
        ax.imshow(grid, aspect="auto", cmap="coolwarm", vmin=0, vmax=1)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["p", f"p+{gap}"])
        ax.set_title(f"g={gap} ({GAP_NAME[gap]})\nred=fast (D3), blue=slow")
        ax.set_ylabel("odd residue a | (a+g) mod 8")
    fig.suptitle("Gap-forced 2-adic coupling (theorem, not data)")
    plt.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def fig_joint(bundles, out_path):
    """Observed joint k_p x k_{p+g} heatmap per gap (log counts)."""
    fig, axes = plt.subplots(1, len(bundles), figsize=(16, 5))
    for ax, b in zip(axes, bundles):
        grid = _joint_grid(b["joint"])
        im = ax.imshow(
            np.log10(grid + 1), origin="lower", cmap="viridis", aspect="auto"
        )
        ax.set_xlabel("$k_{p+g}$")
        ax.set_ylabel("$k_p$")
        ax.set_title(f"g={b['gap']} ({GAP_NAME[b['gap']]}) — log10(count+1)")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle("Observed joint dropping signatures of prime pairs")
    plt.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def fig_marginal(bundles, generic, out_path):
    """Headline: slow-member marginal bars + observed/null joint ratio heatmap."""
    fig, axes = plt.subplots(2, len(bundles), figsize=(16, 9))
    gen_d = density(generic)
    ks = sorted(gen_d)
    for j, b in enumerate(bundles):
        slow = slow_member_marginal(b["joint"])
        slow_d = density(slow)
        ax = axes[0, j]
        x = np.arange(len(ks))
        w = 0.4
        ax.bar(x - w / 2, [gen_d.get(k, 0) for k in ks], w,
               label="generic primes (HL)", color="0.7")
        ax.bar(x + w / 2, [slow_d.get(k, 0) for k in ks], w,
               label="slow member", color="mediumseagreen")
        ax.set_xticks(x)
        ax.set_xticklabels(ks, fontsize=7)
        ax.set_xlabel("dropping set k")
        ax.set_title(f"g={b['gap']} ({GAP_NAME[b['gap']]}) — slow marginal vs generic")
        ax.legend(fontsize=8)

        obs_d = _joint_grid(density(b["joint"]))
        null_d = _joint_grid(density(b["null"]))
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(null_d > 0, obs_d / null_d, np.nan)
        ax2 = axes[1, j]
        im = ax2.imshow(ratio, origin="lower", cmap="RdBu_r", vmin=0, vmax=2,
                        aspect="auto")
        ax2.set_xlabel("$k_{p+g}$")
        ax2.set_ylabel("$k_p$")
        ax2.set_title("observed / coupling-null (joint)")
        fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    fig.suptitle("Constellation signatures: marginal HL test (top) + joint correlation (bottom)")
    plt.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def fig_genus(bundles, out_path):
    """3-adic odd-step (s) refinement: observed/null ratio per gap, g=6 cross-check."""
    fig, axes = plt.subplots(1, len(bundles), figsize=(16, 5))
    smax = 0
    for b in bundles:
        for (sp, sq) in list(b["s_joint"]) + list(b["s_null"]):
            smax = max(smax, sp, sq)
    smax = min(smax, 20)
    for ax, b in zip(axes, bundles):
        obs = np.zeros((smax + 1, smax + 1))
        nul = np.zeros((smax + 1, smax + 1))
        for (sp, sq), c in b["s_joint"].items():
            if sp <= smax and sq <= smax:
                obs[sp, sq] = c
        for (sp, sq), c in b["s_null"].items():
            if sp <= smax and sq <= smax:
                nul[sp, sq] = c
        od, nd = obs / (obs.sum() or 1), nul / (nul.sum() or 1)
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(nd > 0, od / nd, np.nan)
        im = ax.imshow(ratio, origin="lower", cmap="PuOr_r", vmin=0, vmax=2,
                       aspect="auto")
        tag = " (3-adic coupled)" if b["gap"] % 3 == 0 else ""
        ax.set_xlabel("$s_{p+g}$ (odd steps)")
        ax.set_ylabel("$s_p$")
        ax.set_title(f"g={b['gap']} ({GAP_NAME[b['gap']]}){tag}")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle("Odd-step (3-adic) signature: observed / null — watch g=6 vs g=2,4")
    plt.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def render_all(bundles, generic):
    fig_coupling(OUT_DIR / "collatz_constellation_coupling.png")
    fig_joint(bundles, OUT_DIR / "collatz_constellation_joint.png")
    fig_marginal(bundles, generic, OUT_DIR / "collatz_constellation_marginal.png")
    fig_genus(bundles, OUT_DIR / "collatz_constellation_genus.png")
    print("Figures written to", OUT_DIR)
```

- [ ] **Step 2: Smoke-run the full render at reduced N**

```bash
python -c "
import scripts.prime_constellation_signatures as s
s.N = 200_000
s.NULL_STRIDE = 3
s.main()
"
ls -la data/collatz_constellation_*.png
```

Expected: four PNGs (`coupling`, `joint`, `marginal`, `genus`), each > 15 KB. No exceptions.

- [ ] **Step 3: Run the full sweep at N = 1e7**

```bash
python scripts/prime_constellation_signatures.py
```

Expected: completes in roughly 3–8 minutes (the null and odd-step loops over odd integers dominate; `NULL_STRIDE=5` keeps it bounded). Console prints three summary blocks. Four PNGs (re-)written. Note the χ² and total-variation values per gap for the findings note.

- [ ] **Step 4: Commit script and outputs**

```bash
git add scripts/prime_constellation_signatures.py data/collatz_constellation_coupling.png data/collatz_constellation_joint.png data/collatz_constellation_marginal.png data/collatz_constellation_genus.png
git commit -m "feat(scripts): five constellation-signature figures + full sweep"
```

---

### Task 7: Light notebook `03-prime-constellations.ipynb`

**Files:**
- Create: `notebooks/03-prime-constellations.ipynb`

A short runnable companion (not a rewrite of the script). Create it with `jupyter` or by hand; cells below.

- [ ] **Step 1: Markdown intro cell**

```markdown
# 03 — Prime Constellation Signatures

Twins (g=2), cousins (g=4), sexy primes (g=6) through the Collatz dropping
signature. The gap forces a 2-adic coupling between the two members; we test
for residual structure beyond it against the generic-prime marginal (a
Hardy–Littlewood prediction) and an admissible-integer coupling null.

See `docs/superpowers/specs/2026-06-14-prime-constellation-signatures-design.md`.
```

- [ ] **Step 2: Forced-coupling cell**

```python
from collatz.constellations import forced_coupling_table
for gap in (2, 4, 6):
    print(f"g={gap}:")
    for a, b, fa, fb in forced_coupling_table(gap, 8):
        print(f"  {a:>2} -> {b:>2}   fast(p)={fa}  fast(p+g)={fb}")
```

Run it. Expected: g=2/6 rows always have exactly one `True`; g=4 rows have matching flags.

- [ ] **Step 3: Joint-signature cell**

```python
import numpy as np
from collatz.constellations import prime_pairs, joint_signature_counts, coupling_null_counts

N = 1_000_000
for gap in (2, 4, 6):
    pairs = prime_pairs(N, gap)
    joint = joint_signature_counts(pairs, gap)
    null = coupling_null_counts(N, gap, stride=5)
    so, sn = sum(joint.values()), sum(null.values())
    tv = 0.5 * sum(abs(joint.get(k, 0)/so - null.get(k, 0)/sn)
                   for k in set(joint) | set(null))
    print(f"g={gap}: {len(pairs)} pairs, total-variation(joint, null) = {tv:.4f}")
```

Run it. Expected: three lines; total-variation values are small (~1e-3 to 1e-2).

- [ ] **Step 4: Save and commit**

```bash
git add notebooks/03-prime-constellations.ipynb
git commit -m "docs(notebook): 03 prime constellations companion"
```

---

### Task 8: Findings note

**Files:**
- Create: `docs/Explorations/Prime Constellation Signatures.md`

- [ ] **Step 1: Create the note (fill bracketed values from Task 6 Step 3 output)**

```markdown
# Prime Constellation Signatures

**Question:** Do prime constellations — twins $(p,p{+}2)$, cousins $(p,p{+}4)$,
sexy $(p,p{+}6)$ — distribute across Collatz dropping signatures in a way the
gap-forced coupling and Hardy–Littlewood cannot explain?

**Method:** see [Spec](../superpowers/specs/2026-06-14-prime-constellation-signatures-design.md)
and [Plan](../superpowers/plans/2026-06-14-prime-constellation-signatures.md).
Each pair gets a joint signature $(k_p, k_{p+g})$; we compare the slow-member
marginal to the generic single-prime distribution (an HL prediction) and the
joint distribution to an admissible-integer coupling null. The odd-step count
$s$ = `orbital_oddity` gives the 3-adic layer, where $g=6$ is the cross-check.

**The forced coupling (theorem):** every twin/sexy pair is one fast dropper
($\equiv 1\bmod4$, dropping set 3) and one slow member; every cousin pair shares
its mod-4 class. This is the spine of all four figures.

**Results at $N = 10^7$:**

| gap | pairs | $\chi^2$ (slow vs generic) | TV (joint vs null) |
|-----|-------|----------------------------|--------------------|
| 2   | [fill] | [fill]                    | [fill]             |
| 4   | [fill] | [fill]                    | [fill]             |
| 6   | [fill] | [fill]                    | [fill]             |

- Top deviating joint cells: [fill from console]
- $g=6$ odd-step cross-check vs $g=2,4$: [fill — did the 3-adic layer diverge?]

**Figures:**
- ![Forced coupling](../../data/collatz_constellation_coupling.png)
- ![Joint signatures](../../data/collatz_constellation_joint.png)
- ![Marginal + joint ratio](../../data/collatz_constellation_marginal.png)
- ![Odd-step refinement](../../data/collatz_constellation_genus.png)

**Interpretation:** [fill — did the slow marginal match the generic-prime HL
prediction? Did the joint deviate from the coupling null beyond finite-N noise?
Did g=6 behave differently from g=2,4 as the 3-adic factor predicts? "No signal
beyond the null" is a valid, informative outcome.]

**Open (Phase D, if signal):** lift the null to the combined $2^{k-2s}6^s$
modulus; run the spectral/diffraction layer on the ordered pair-fingerprint
sequence; extend $g$ beyond 6 to track the singular series. See
[[Collatz as a Quasicrystal]], [[Prime Dropping Residues]], [[Dropping Zeta Spectrum]].

**Related:** [[Prime Dropping Residues]], [[Kozyrev Orbital Spectrum]], [[Collatz Embeddings]].
```

- [ ] **Step 2: Run the full script once and fill placeholders**

If Task 6 Step 3 has run, copy the three summary blocks into the table and the
interpretation. Read the largest red/blue cells off the marginal and genus PNGs.

- [ ] **Step 3: Commit**

```bash
git add "docs/Explorations/Prime Constellation Signatures.md"
git commit -m "docs(exploration): prime constellation signatures findings"
```

---

## Verification at end

- [ ] Run the full suite:

```bash
python -m pytest tests/test_constellations.py -v
```

Expected: 16 PASS.

- [ ] Confirm no regression in the wider suite:

```bash
python -m pytest tests/ -q
```

Expected: all pre-existing tests still pass.

- [ ] Visually inspect the four PNGs in `data/`:
  - **coupling**: g=2/6 panels alternate red/blue across rows (one fast member); g=4 panel has matching colors per row.
  - **joint**: g=2/6 show an off-diagonal fast–slow band (one axis pinned near $k=3$); g=4 shows near-diagonal same-class structure.
  - **marginal**: top bars — slow member tracks generic primes closely (HL holds) unless there is signal; bottom heatmap — cells near 1.0 (white) confirm the coupling null, saturated cells are candidates.
  - **genus**: watch whether the $g=6$ panel (tagged "3-adic coupled") departs from $g=2,4$.
```
