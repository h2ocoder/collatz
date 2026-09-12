# Prime Distribution Across Dropping Sets — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the arithmetic form of each Collatz Dropping Set $D_k$ (its decomposition into residue classes mod $2^k$) explicit in code, then use Dirichlet's theorem on primes-in-arithmetic-progressions as a null model to surface any structural signal in how primes distribute across $D_k$ and across the individual residue classes inside $D_k$.

**Architecture:** One new module `collatz/residues.py` exposes the residue tables $R_k$, a Dirichlet null-model helper, and a fast sieve. One new script `scripts/prime_dropping_residues.py` consumes those tables, sieves primes up to $N=10^7$, classifies them, and writes three PNGs. One new test module `tests/test_residues.py` validates against known small-$k$ cases and a partition property. The existing notebook `02-prime-class-characters.ipynb` gets a new appended section that reuses these tools.

**Tech Stack:** Python 3.12, NumPy, Matplotlib (Agg backend), pytest. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-06-02-prime-dropping-residues-design.md`

**Conventions to follow:**
- Tests live flat in `tests/test_<module>.py` — match the `test_wavelets.py` / `test_walsh.py` pattern.
- Functions get docstrings with concrete `Example:` lines.
- Scripts use `matplotlib.use("Agg")` at top-of-file and write PNGs to `data/`.
- Run tests via `python -m pytest tests/test_residues.py -v` (the repo installs as `pip install -e .` then `pip install pytest`).
- Commits use Conventional Commits style matching recent history (`feat(residues): …`, `test(residues): …`).

**Math reference (residue convention):**

For dropping set $k \ge 1$, let $M = 2^k$. We say residue $r \in \{0, 1, \dots, M-1\}$ belongs to $R_k$ when every sufficiently large $n \equiv r \pmod M$ satisfies $\text{dropping\_set}(n) = k$. We compute $R_k$ by checking three large representatives $n \in \{r + M,\ r + 2M,\ r + 3M\}$ (skipping $n=0,1$ when $r=0$, $r$ being substituted with $M$); the residue is included iff all three representatives classify to $k$. The full Dropping Set is then $D_k = \bigcup_{r \in R_k} \{n \ge 2 : n \equiv r \pmod{2^k}\}$.

The Dirichlet null model: a prime $p > 2$ is coprime to $2^k$, so its residue $p \bmod 2^k$ lies in one of the $\varphi(2^k) = 2^{k-1}$ odd residue classes. Dirichlet's theorem says primes equidistribute across those classes. The expected number of primes $\le N$ in $D_k$ is $|R_k \cap \text{odd}| / 2^{k-1} \cdot \pi(N)$.

---

## File Structure

```
collatz/
  residues.py                       # NEW: prime_sieve, dropping_set_residues, dropping_set_residue_table, coprime_residues, dirichlet_prediction
scripts/
  prime_dropping_residues.py        # NEW: sieve + classify + 3 PNGs + console summary
tests/
  test_residues.py                  # NEW: small-k known values, partition property, Dirichlet sanity
notebooks/
  02-prime-class-characters.ipynb   # MODIFY: append section "Arithmetic Form and Dirichlet Null"
docs/Explorations/
  Prime Dropping Residues.md        # NEW: written-up findings (one-pager)
data/
  collatz_prime_dropping_residues_form.png         # NEW (output)
  collatz_prime_dropping_observed_vs_dirichlet.png # NEW (output)
  collatz_prime_dropping_residue_heatmap.png       # NEW (output)
```

`collatz/residues.py` stays under ~250 lines.

---

### Task 1: Module skeleton + fast prime sieve

**Files:**
- Create: `collatz/residues.py`
- Create: `tests/test_residues.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_residues.py
"""Tests for collatz.residues — arithmetic form of dropping sets and Dirichlet null."""

import numpy as np
import pytest

from collatz.residues import prime_sieve


def test_prime_sieve_small():
    """Sieve returns primes up to N inclusive, as a NumPy int array."""
    primes = prime_sieve(20)
    assert isinstance(primes, np.ndarray)
    assert primes.dtype.kind == "i"
    assert list(primes) == [2, 3, 5, 7, 11, 13, 17, 19]


def test_prime_sieve_excludes_one():
    """1 is not prime; 2 is."""
    primes = prime_sieve(2)
    assert list(primes) == [2]


def test_prime_sieve_count_at_1e5():
    """Pi(1e5) = 9592 (well-known)."""
    primes = prime_sieve(100_000)
    assert primes.size == 9592
    assert primes[0] == 2
    assert primes[-1] == 99991


def test_prime_sieve_rejects_small_n():
    """N < 2 returns an empty array (no primes exist)."""
    assert prime_sieve(1).size == 0
    assert prime_sieve(0).size == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_residues.py -v`
Expected: FAIL with `ImportError: cannot import name 'prime_sieve' from 'collatz.residues'` (module does not exist yet).

- [ ] **Step 3: Write the module skeleton + sieve**

```python
# collatz/residues.py
"""Arithmetic form of Collatz Dropping Sets and Dirichlet null model.

Each Dropping Set D_k is a finite union of residue classes mod 2^k.  This
module exposes that decomposition (`dropping_set_residues`,
`dropping_set_residue_table`), the subset of those residues coprime to 2^k
(`coprime_residues`), and a Dirichlet-equidistribution null model for how
primes distribute across D_k (`dirichlet_prediction`).  A fast Sieve of
Eratosthenes (`prime_sieve`) is included for convenience.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from .dropping import dropping_set


def prime_sieve(n: int) -> np.ndarray:
    """All primes p with 2 <= p <= n, as a 1-D int64 NumPy array.

    Plain Sieve of Eratosthenes on a boolean array of length n+1.
    Returns an empty array when n < 2.

    Example: prime_sieve(10) -> array([2, 3, 5, 7])
    """
    if n < 2:
        return np.empty(0, dtype=np.int64)
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[:2] = False
    for p in range(2, int(n**0.5) + 1):
        if is_prime[p]:
            is_prime[p * p :: p] = False
    return np.nonzero(is_prime)[0].astype(np.int64)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_residues.py -v`
Expected: 4 PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/residues.py tests/test_residues.py
git commit -m "feat(residues): add module skeleton and prime_sieve"
```

---

### Task 2: `dropping_set_residues(k)` — the arithmetic form

**Files:**
- Modify: `collatz/residues.py`
- Modify: `tests/test_residues.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_residues.py`:

```python
from collatz.residues import dropping_set_residues
from collatz.dropping import dropping_set


def test_R_1_is_evens_only():
    """Dropping Set 1 = all even numbers, so R_1 = {0} mod 2."""
    assert dropping_set_residues(1) == frozenset({0})


def test_R_3_matches_1_mod_4():
    """Dropping Set 3 = {n : n ≡ 1 mod 4, n > 1}, so R_3 = {1, 5} mod 8."""
    assert dropping_set_residues(3) == frozenset({1, 5})


def test_R_2_is_empty():
    """Set 2 requires n odd AND (3n+1)/2 < n, which is impossible for positive n."""
    assert dropping_set_residues(2) == frozenset()


def test_partition_up_to_4096():
    """For every n in [2, 4096], n mod 2^k must lie in R_k where k = dropping_set(n)."""
    for n in range(2, 4097):
        k = dropping_set(n)
        r = n % (1 << k)
        assert r in dropping_set_residues(k), (
            f"n={n}, k={k}, r={r} not in R_{k}={sorted(dropping_set_residues(k))}"
        )


def test_residue_density_consistent():
    """Empirical Set_k density up to N matches |R_k| / 2^k within tolerance for small k."""
    N = 4096
    empirical = {k: 0 for k in range(1, 12)}
    for n in range(2, N + 1):
        k = dropping_set(n)
        if k < 12:
            empirical[k] += 1
    for k in range(1, 12):
        R_k = dropping_set_residues(k)
        if not R_k:
            assert empirical[k] == 0
            continue
        predicted_density = len(R_k) / (1 << k)
        observed_density = empirical[k] / (N - 1)
        # Loose: density tracks within 30% at N = 4096 (small-N regime)
        if predicted_density > 0.01:
            assert abs(observed_density - predicted_density) / predicted_density < 0.30, (
                f"k={k}: predicted {predicted_density:.4f}, observed {observed_density:.4f}"
            )
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python -m pytest tests/test_residues.py -v`
Expected: 4 PASS (old) + 5 FAIL (new) with `ImportError: cannot import name 'dropping_set_residues'`.

- [ ] **Step 3: Implement `dropping_set_residues`**

Append to `collatz/residues.py`:

```python
@lru_cache(maxsize=None)
def dropping_set_residues(k: int) -> frozenset[int]:
    """Residues r mod 2^k such that every large n ≡ r (mod 2^k) has dropping_set(n) = k.

    Computed by checking three large representatives (r+2^k, r+2·2^k, r+3·2^k)
    and accepting r only if all three classify to k.  This guards against
    residues where the orbit accidentally drops at step k for small n but not
    asymptotically.

    Returns frozenset() when no residue class satisfies the property
    (e.g. k=2 has no qualifying residue: 3x+1 dynamics cannot drop in
    exactly 2 steps).

    Example: dropping_set_residues(1) == frozenset({0})
    Example: dropping_set_residues(3) == frozenset({1, 5})
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    M = 1 << k
    R = set()
    for r in range(M):
        base = r if r >= 2 else M
        reps = (base, base + M, base + 2 * M)
        if all(dropping_set(n) == k for n in reps):
            R.add(r)
    return frozenset(R)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_residues.py -v`
Expected: 9 PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/residues.py tests/test_residues.py
git commit -m "feat(residues): add dropping_set_residues with partition tests"
```

---

### Task 3: Residue table cache + coprime residues + Dirichlet prediction

**Files:**
- Modify: `collatz/residues.py`
- Modify: `tests/test_residues.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_residues.py`:

```python
from collatz.residues import (
    coprime_residues,
    dirichlet_prediction,
    dropping_set_residue_table,
)


def test_residue_table_covers_range():
    """Table returns frozensets for k in 1..k_max."""
    table = dropping_set_residue_table(8)
    assert set(table.keys()) == set(range(1, 9))
    for k, R in table.items():
        assert isinstance(R, frozenset)
        assert R == dropping_set_residues(k)


def test_coprime_residues_filters_odds():
    """coprime_residues(k) = R_k intersect odd residues mod 2^k."""
    # R_3 = {1, 5}; both odd, so coprime = R_3.
    assert coprime_residues(3) == frozenset({1, 5})
    # R_1 = {0}; 0 is even, so coprime = empty.
    assert coprime_residues(1) == frozenset()


def test_dirichlet_prediction_zero_when_no_coprime_residues():
    """A set with no odd residues asymptotically contains no primes."""
    # k=1: only even residue, so prediction = 0 regardless of pi(N).
    assert dirichlet_prediction(1, prime_count=10_000) == 0.0


def test_dirichlet_prediction_matches_formula():
    """Prediction = |R_k ∩ odd| / 2^(k-1) * pi(N)."""
    # k=3: 2 coprime residues out of 4 odd residues mod 8 -> ratio = 0.5
    pi_N = 78_498  # pi(1e6)
    expected = 2 / 4 * pi_N
    assert dirichlet_prediction(3, prime_count=pi_N) == pytest.approx(expected)
```

- [ ] **Step 2: Run new tests to verify they fail**

Run: `python -m pytest tests/test_residues.py -v`
Expected: 9 PASS + 4 FAIL with `ImportError`.

- [ ] **Step 3: Implement the three helpers**

Append to `collatz/residues.py`:

```python
def dropping_set_residue_table(k_max: int) -> dict[int, frozenset[int]]:
    """Map {k: R_k} for k in 1..k_max.

    Each R_k is the output of `dropping_set_residues(k)`.

    Example: dropping_set_residue_table(3) ==
             {1: frozenset({0}), 2: frozenset(), 3: frozenset({1, 5})}
    """
    if k_max < 1:
        raise ValueError("k_max must be >= 1")
    return {k: dropping_set_residues(k) for k in range(1, k_max + 1)}


@lru_cache(maxsize=None)
def coprime_residues(k: int) -> frozenset[int]:
    """Residues in R_k that are coprime to 2^k (equivalently, odd).

    Primes p > 2 with dropping_set(p) = k must have p mod 2^k in this set.

    Example: coprime_residues(3) == frozenset({1, 5})
    """
    return frozenset(r for r in dropping_set_residues(k) if r % 2 == 1)


def dirichlet_prediction(k: int, prime_count: int) -> float:
    """Expected number of primes <= N falling in Dropping Set k, under Dirichlet.

    Formula: |R_k ∩ odd| / 2^(k-1) * pi(N), with pi(N) supplied as `prime_count`.

    Example: dirichlet_prediction(3, prime_count=78498) == 39249.0
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    coprime_count = len(coprime_residues(k))
    odd_residues_total = 1 << (k - 1)
    return coprime_count / odd_residues_total * prime_count
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_residues.py -v`
Expected: 13 PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/residues.py tests/test_residues.py
git commit -m "feat(residues): add residue table, coprime filter, Dirichlet prediction"
```

---

### Task 4: Empirical sweep + 3 figures

**Files:**
- Create: `scripts/prime_dropping_residues.py`

This task has no unit tests — it is a one-shot script. Its correctness is established by (a) using only tested library code and (b) inspecting the printed χ² table and the three PNGs.

- [ ] **Step 1: Create the script**

```python
# scripts/prime_dropping_residues.py
"""Prime distribution across Collatz Dropping Sets: observed vs Dirichlet null.

For primes p <= N (default 1e7), classify each by its Dropping Set k and
its residue p mod 2^k.  Compare counts to the Dirichlet null model
(equidistribution of primes across odd residues mod 2^k).  Render:

  1. Arithmetic-form table: which residues r mod 2^k populate D_k.
  2. Observed vs Dirichlet bar chart per D_k, with chi-squared annotation.
  3. Per-residue heatmap inside D_k for k in {5, 7, 9, 11, 13}.

Outputs:
    data/collatz_prime_dropping_residues_form.png
    data/collatz_prime_dropping_observed_vs_dirichlet.png
    data/collatz_prime_dropping_residue_heatmap.png
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from collatz.dropping import dropping_set
from collatz.residues import (
    coprime_residues,
    dirichlet_prediction,
    dropping_set_residue_table,
    dropping_set_residues,
    prime_sieve,
)


# ----- Configuration ---------------------------------------------------

N = 10_000_000  # prime ceiling
K_MAX = 15  # maximum dropping set considered
HEATMAP_KS = (5, 7, 9, 11, 13)  # k values that get a per-residue strip
OUT_DIR = Path(__file__).resolve().parent.parent / "data"


# ----- Step 1: sieve and classify --------------------------------------


def sieve_and_classify(n_max: int, k_max: int):
    """Sieve primes <= n_max, classify into (k, r) buckets.

    Returns:
      primes: 1-D int64 array of primes <= n_max
      counts_by_k: dict k -> int  (number of primes with dropping_set = k)
      counts_by_k_r: dict k -> Counter mapping residue r -> count
      small_primes: list of primes p with p < 2**k(p), tracked separately
    """
    primes = prime_sieve(n_max)
    counts_by_k = Counter()
    counts_by_k_r = defaultdict(Counter)
    small_primes = []
    for p in primes.tolist():
        k = dropping_set(p)
        counts_by_k[k] += 1
        r = p % (1 << k)
        counts_by_k_r[k][r] += 1
        if p < (1 << k):
            small_primes.append(p)
    return primes, counts_by_k, counts_by_k_r, small_primes


# ----- Step 2: arithmetic-form figure ----------------------------------


def plot_residue_form(residue_table, out_path):
    """Heatmap: rows = k (1..K_max), columns = r (0..1023 for visibility).

    Cells light up when r in R_k.  Side annotations: |R_k|, |R_k ∩ odd|.
    """
    k_max = max(residue_table.keys())
    n_cols = min(1024, 1 << k_max)
    grid = np.zeros((k_max, n_cols), dtype=float)
    for k, R in residue_table.items():
        M = 1 << k
        for r in R:
            # Project to first n_cols columns by folding mod n_cols
            if r < n_cols:
                grid[k - 1, r] = 1.0
            else:
                grid[k - 1, r % n_cols] = max(grid[k - 1, r % n_cols], 0.5)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.imshow(grid, aspect="auto", cmap="viridis", interpolation="nearest")
    ax.set_xlabel(f"Residue r (mod $2^{{{k_max}}}$, folded to first {n_cols} columns)")
    ax.set_ylabel("Dropping Set k")
    ax.set_yticks(range(k_max))
    ax.set_yticklabels(range(1, k_max + 1))
    ax.set_title(f"Arithmetic Form of Dropping Sets: residues r mod $2^k$ that populate $D_k$")

    # Side-text with sizes
    for i, k in enumerate(range(1, k_max + 1)):
        R = residue_table[k]
        coprime = coprime_residues(k)
        ax.text(
            n_cols + 5,
            i,
            f"|R|={len(R)}, |odd|={len(coprime)}",
            fontsize=8,
            va="center",
        )
    plt.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


# ----- Step 3: observed-vs-Dirichlet figure ----------------------------


def chi_squared(observed: float, expected: float) -> float:
    """One-cell chi-squared contribution; returns 0 when expected is 0."""
    if expected == 0:
        return 0.0
    return (observed - expected) ** 2 / expected


def plot_observed_vs_dirichlet(counts_by_k, prime_count, k_max, out_path):
    """Grouped bars: predicted (gray) vs observed (color) per k.

    Annotate each bar pair with log10(observed / predicted).
    """
    ks = list(range(1, k_max + 1))
    predicted = [dirichlet_prediction(k, prime_count) for k in ks]
    observed = [counts_by_k.get(k, 0) for k in ks]

    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(ks))
    width = 0.4
    ax.bar(x - width / 2, predicted, width, label="Dirichlet null", color="0.7")
    ax.bar(x + width / 2, observed, width, label="Observed", color="mediumseagreen")
    ax.set_yscale("symlog", linthresh=1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(ks)
    ax.set_xlabel("Dropping Set k")
    ax.set_ylabel("Prime count (symlog)")
    ax.set_title(
        f"Primes per Dropping Set vs Dirichlet null (N = {prime_count} = pi({N}))"
    )

    # Annotate log-ratio above each observed bar
    for xi, p, o in zip(x, predicted, observed):
        if p > 0 and o > 0:
            ratio = np.log10(o / p)
            ax.text(
                xi + width / 2,
                o * 1.15 + 1,
                f"{ratio:+.2f}",
                ha="center",
                fontsize=8,
            )

    # Chi-squared total in the legend area
    chi2_total = sum(chi_squared(o, p) for o, p in zip(observed, predicted))
    ax.text(
        0.02,
        0.95,
        f"$\\chi^2$ total = {chi2_total:.1f}",
        transform=ax.transAxes,
        fontsize=10,
        va="top",
    )
    ax.legend(loc="upper right")
    plt.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


# ----- Step 4: per-residue heatmap -------------------------------------


def plot_residue_heatmap(counts_by_k_r, residue_table, prime_count, ks, out_path):
    """One row per k in `ks`; cells = one per odd residue in R_k, colored by count.

    Color scale: counts normalized by (predicted per residue) so a value of
    1.0 means "matches Dirichlet exactly".  Values > 1 are over-represented;
    < 1 under-represented.
    """
    fig, axes = plt.subplots(len(ks), 1, figsize=(14, 2 * len(ks)))
    if len(ks) == 1:
        axes = [axes]

    for ax, k in zip(axes, ks):
        R_odd = sorted(coprime_residues(k))
        if not R_odd:
            ax.text(0.5, 0.5, f"R_{k} ∩ odd is empty", transform=ax.transAxes, ha="center")
            ax.set_axis_off()
            continue
        expected_per = dirichlet_prediction(k, prime_count) / len(R_odd) if R_odd else 0.0
        observed = np.array([counts_by_k_r.get(k, {}).get(r, 0) for r in R_odd])
        ratio = observed / expected_per if expected_per > 0 else observed.astype(float)

        im = ax.imshow(
            ratio.reshape(1, -1),
            aspect="auto",
            cmap="RdBu_r",
            vmin=0.0,
            vmax=2.0,
            interpolation="nearest",
        )
        ax.set_yticks([])
        ax.set_xticks(np.linspace(0, len(R_odd) - 1, min(8, len(R_odd))).astype(int))
        ax.set_xticklabels(
            [str(R_odd[i]) for i in np.linspace(0, len(R_odd) - 1, min(8, len(R_odd))).astype(int)],
            fontsize=8,
        )
        ax.set_xlabel(f"odd residue r mod $2^{{{k}}}$ (in $R_{{{k}}}$, |·|={len(R_odd)})")
        ax.set_title(f"k = {k} — observed / Dirichlet per residue")
        fig.colorbar(im, ax=ax, fraction=0.02, pad=0.01)

    fig.suptitle(
        "Per-residue prime counts inside each Dropping Set, normalized by Dirichlet null"
    )
    plt.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


# ----- Step 5: summary printer -----------------------------------------


def print_summary(counts_by_k, prime_count, k_max, small_primes):
    print(f"\nTotal primes <= {N}: {prime_count}")
    print(f"Small primes (p < 2**k(p)): {len(small_primes)}\n")
    print(f"{'k':>3} {'|R_k|':>6} {'|odd|':>6} {'predicted':>12} {'observed':>10} {'log10 obs/pred':>15} {'chi2':>10}")
    for k in range(1, k_max + 1):
        predicted = dirichlet_prediction(k, prime_count)
        observed = counts_by_k.get(k, 0)
        R = dropping_set_residues(k)
        odd = coprime_residues(k)
        ratio = np.log10(observed / predicted) if (predicted > 0 and observed > 0) else float("nan")
        chi2 = chi_squared(observed, predicted)
        print(f"{k:>3} {len(R):>6} {len(odd):>6} {predicted:>12.1f} {observed:>10d} {ratio:>15.3f} {chi2:>10.1f}")


# ----- Main ------------------------------------------------------------


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Building residue table for k=1..{K_MAX}...")
    residue_table = dropping_set_residue_table(K_MAX)
    print(f"Sieving primes up to {N}...")
    primes, counts_by_k, counts_by_k_r, small_primes = sieve_and_classify(N, K_MAX)
    prime_count = int(primes.size)

    print(f"Rendering arithmetic-form figure...")
    plot_residue_form(
        residue_table, OUT_DIR / "collatz_prime_dropping_residues_form.png"
    )
    print(f"Rendering observed-vs-Dirichlet figure...")
    plot_observed_vs_dirichlet(
        counts_by_k,
        prime_count,
        K_MAX,
        OUT_DIR / "collatz_prime_dropping_observed_vs_dirichlet.png",
    )
    print(f"Rendering per-residue heatmap...")
    plot_residue_heatmap(
        counts_by_k_r,
        residue_table,
        prime_count,
        HEATMAP_KS,
        OUT_DIR / "collatz_prime_dropping_residue_heatmap.png",
    )

    print_summary(counts_by_k, prime_count, K_MAX, small_primes)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-run the script at reduced N**

Run a fast smoke test by editing `N = 100_000` and `K_MAX = 10` temporarily:

```bash
python -c "
import sys
sys.path.insert(0, '.')
# Monkey-patch script constants for a fast smoke run
import scripts.prime_dropping_residues as s
s.N = 100_000
s.K_MAX = 10
s.HEATMAP_KS = (5, 7, 9)
s.main()
"
```

Expected: script completes in under ~30 seconds. Three PNGs appear in `data/`. The summary table shows nonzero observed counts for at least k ∈ {1, 3, 6, 8} within the displayed range (k=11 also has nonzero counts in the underlying Counter — it just won't appear in the K_MAX=10 bar chart) and zeros for k ∈ {2, 4, 5, 7, 9, 10} (empty $R_k$). Log-ratios on populated rows are within a few standard deviations of 0 — that is, observed ≈ predicted in order of magnitude.

Verify the smoke output by checking PNG existence:

```bash
ls -la data/collatz_prime_dropping_*.png
```

Expected: three files with size > 10 KB each.

- [ ] **Step 3: Run the full sweep at N = 1e7**

```bash
python scripts/prime_dropping_residues.py
```

Expected: completes in 1–3 minutes. Console prints χ² table. Three PNGs (re-)written in `data/`. χ² total should be a finite number — note its value for the exploration writeup in Task 6.

- [ ] **Step 4: Commit script and outputs**

```bash
git add scripts/prime_dropping_residues.py data/collatz_prime_dropping_residues_form.png data/collatz_prime_dropping_observed_vs_dirichlet.png data/collatz_prime_dropping_residue_heatmap.png
git commit -m "feat(scripts): prime distribution across dropping sets vs Dirichlet null"
```

---

### Task 5: Extend notebook 02 with a new section

**Files:**
- Modify: `notebooks/02-prime-class-characters.ipynb`

This task adds cells; do not rewrite the existing exploration. Append at the end.

- [ ] **Step 1: Append the section markdown cell**

Open `notebooks/02-prime-class-characters.ipynb` in Jupyter and add a new markdown cell at the end with:

```markdown
## Arithmetic Form and Dirichlet Null

Each Dropping Set $D_k$ is a union of residue classes mod $2^k$.  We expose
that decomposition via `collatz.residues.dropping_set_residues(k)`, derive
the Dirichlet null model for prime counts per $D_k$, and compare against
observation.

Dirichlet's theorem says primes equidistribute across the $\varphi(2^k)
= 2^{k-1}$ odd residues mod $2^k$, so the expected prime count in $D_k$
is $|R_k \cap \text{odd}| / 2^{k-1} \cdot \pi(N)$.  Deviation from this
prediction is the structural signal we are after.
```

- [ ] **Step 2: Append the residue-table code cell**

```python
from collatz.residues import (
    coprime_residues,
    dirichlet_prediction,
    dropping_set_residue_table,
    prime_sieve,
)

K_MAX = 12
residue_table = dropping_set_residue_table(K_MAX)

print(f"{'k':>3} {'|R_k|':>6} {'|R_k odd|':>10} {'density':>10}")
for k in range(1, K_MAX + 1):
    R = residue_table[k]
    odd = coprime_residues(k)
    density = len(R) / (1 << k)
    print(f"{k:>3} {len(R):>6} {len(odd):>10} {density:>10.5f}")
```

Run the cell. Expected output: a table where the densities sum (over k) toward 1 as k_max grows, with $D_1$ taking density 0.5 and $D_3$ taking 0.25.

- [ ] **Step 3: Append the observed-vs-Dirichlet code cell**

```python
import numpy as np
from collatz.dropping import dropping_set

N = 1_000_000
primes = prime_sieve(N)
prime_count = primes.size
print(f"pi({N}) = {prime_count}")

observed = {k: 0 for k in range(1, K_MAX + 1)}
for p in primes.tolist():
    k = dropping_set(p)
    if k <= K_MAX:
        observed[k] += 1

predicted = {k: dirichlet_prediction(k, prime_count) for k in range(1, K_MAX + 1)}

ks = list(range(1, K_MAX + 1))
fig, ax = plt.subplots(figsize=(12, 5))
width = 0.4
x = np.arange(len(ks))
ax.bar(x - width / 2, [predicted[k] for k in ks], width, label="Dirichlet null", color="0.7")
ax.bar(x + width / 2, [observed[k] for k in ks], width, label="Observed", color="mediumseagreen")
ax.set_yscale("symlog", linthresh=1.0)
ax.set_xticks(x); ax.set_xticklabels(ks)
ax.set_xlabel("Dropping Set k"); ax.set_ylabel("Prime count (symlog)")
ax.set_title(f"Primes per Dropping Set vs Dirichlet null (N = {N})")
ax.legend()
plt.tight_layout(); plt.show()
```

Run the cell. Expected: a bar chart with paired predicted/observed bars per $k$.

- [ ] **Step 4: Save and commit**

```bash
git add notebooks/02-prime-class-characters.ipynb
git commit -m "docs(notebook): extend 02 with arithmetic form + Dirichlet null"
```

---

### Task 6: Write up findings in `docs/Explorations/`

**Files:**
- Create: `docs/Explorations/Prime Dropping Residues.md`

- [ ] **Step 1: Create the exploration note**

Use the printed χ² table and observed PNGs from Task 4 Step 3. The note links the spec, plan, code, and figures. Replace the bracketed `[…]` placeholders with the actual χ² total and the three residue / k pairs with the largest |observed - predicted| from the summary printed by `scripts/prime_dropping_residues.py`.

```markdown
# Prime Dropping Residues

**Question:** Do primes distribute across [[Dropping Sets]] in a way that the Dirichlet null (equidistribution across odd residues mod $2^k$) cannot explain?

**Method:** see [Spec](../superpowers/specs/2026-06-02-prime-dropping-residues-design.md) and [Plan](../superpowers/plans/2026-06-02-prime-dropping-residues.md). Briefly: write each $D_k$ as $\bigcup_{r \in R_k} (r + 2^k \mathbb{Z})$ via `collatz.residues.dropping_set_residues`, sieve primes up to $N = 10^7$, classify, compare to Dirichlet.

**Result at $N = 10^7$, $K_{\max} = 15$:**

- $\chi^2$ total across $D_1, \dots, D_{15}$: **[fill in from script output]**
- Largest deviating $D_k$: **[fill in: k, observed, predicted, log10 ratio]**
- Largest deviating residues inside the heatmap range $k \in \{5, 7, 9, 11, 13\}$: **[fill in: three (k, r, observed/expected) triples]**

**Figures:**

- ![Arithmetic form](../../data/collatz_prime_dropping_residues_form.png)
- ![Observed vs Dirichlet](../../data/collatz_prime_dropping_observed_vs_dirichlet.png)
- ![Per-residue heatmap](../../data/collatz_prime_dropping_residue_heatmap.png)

**Interpretation:** [fill in: did the Dirichlet null fit, or is there signal? If signal, in which $D_k$ or residues, and is the deviation consistent with finite-$N$ Dirichlet bias rather than Collatz structure?]

**Open Phase D (if signal):** lift from 2-adic modulus $2^k$ to the combined 2-adic × 3-adic modulus $2^{k-2s} \cdot 6^s$ where $s$ counts the $3x+1$ steps inside the $k$-step drop; re-run with the refined Dirichlet null. See [[Dropping Zeta Spectrum]] for related 3-adic structure.

**Related explorations:** [[Collatz Embeddings]], [[Kozyrev Orbital Spectrum]], [[Dropping Zeta Spectrum]].
```

- [ ] **Step 2: Run the script once and fill in the placeholders**

If Task 4 Step 3 has already been run, copy the printed χ² total and the worst-deviating row(s) from the summary table into the bracketed placeholders. Identify the three residues with largest |observed - predicted| / sqrt(predicted) inside the heatmap range by reading them off the heatmap PNG (largest red and largest blue cells).

- [ ] **Step 3: Commit**

```bash
git add docs/Explorations/Prime\ Dropping\ Residues.md
git commit -m "docs(exploration): prime dropping residues findings"
```

---

## Verification at end

Run the full test suite to confirm nothing else broke:

```bash
python -m pytest tests/ -v
```

Expected: all tests pass, including the 13 new ones in `tests/test_residues.py`.

Visually inspect the three PNGs in `data/` for:

- **`collatz_prime_dropping_residues_form.png`**: each row $k$ shows a sparse pattern of lit cells. Row 1 has a single lit cell at column 0. Row 3 has cells at columns 1 and 5 (or their fold). Row 2 is entirely dark.
- **`collatz_prime_dropping_observed_vs_dirichlet.png`**: paired bars where observed (green) tracks predicted (gray) closely on a symlog scale. Empty $D_k$ (like $k=2$) have both bars at 0.
- **`collatz_prime_dropping_residue_heatmap.png`**: each strip is a row of cells colored by observed/expected ratio. Cells near 1.0 (white) confirm Dirichlet; saturated red or blue cells are the structural signal candidates.
