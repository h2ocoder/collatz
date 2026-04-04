# Orbit Structure Exploration — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a library module and notebook for element-wise comparison of Collatz orbits within the same (dropping set, dropping modulus) group, probing for ratios, differences, and modular invariants.

**Architecture:** New `collatz/orbits.py` module with functions for grouping numbers by (set, modulus), aligning their orbits into a matrix, and computing element-wise relationships. New `notebooks/07-orbit-structure.ipynb` for visual exploration. Tests in new `tests/` directory.

**Tech Stack:** Python 3.12, pandas, fractions.Fraction, math.gcd, functools.reduce, matplotlib/seaborn (notebook only)

---

### Task 1: Create test directory and test scaffold

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_orbits.py`

**Step 1: Create empty test package**

```python
# tests/__init__.py
# (empty file)
```

**Step 2: Write failing tests for class_members**

```python
# tests/test_orbits.py
"""Tests for collatz.orbits module."""

from collatz.orbits import class_members


def test_class_members_set3_mod0():
    """Dropping set 3, modulus 0 should include 5, 9, 13, 17, ..."""
    members = class_members(3, 0, 50)
    # All members should have dropping time 3
    from collatz.dropping import dropping_time
    for m in members:
        assert dropping_time(m) == 3, f"{m} has dropping time {dropping_time(m)}, expected 3"
    # Should include known members
    assert 5 in members
    assert 9 in members
    assert 13 in members


def test_class_members_returns_sorted():
    members = class_members(3, 0, 100)
    assert members == sorted(members)


def test_class_members_respects_limit():
    members = class_members(3, 0, 20)
    assert all(m < 20 for m in members)
```

**Step 3: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest tests/test_orbits.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'collatz.orbits'`

**Step 4: Commit test scaffold**

```bash
git add tests/__init__.py tests/test_orbits.py
git commit -m "test: add orbit structure test scaffold"
```

---

### Task 2: Implement class_members

**Files:**
- Create: `collatz/orbits.py`

**Step 1: Write minimal implementation**

```python
"""Orbit structure comparison within dropping class groups.

Compare element-wise relationships (ratios, differences, modular equivalences)
between orbits of numbers sharing the same (dropping set, dropping modulus).
"""

from collatz.dropping import dropping_set, dropping_modulus, dropping_orbit


def class_members(set_k, modulus_m, limit):
    """Return sorted list of integers in [2, limit) with given (set, modulus).

    Parameters
    ----------
    set_k : int
        Dropping set (= dropping time).
    modulus_m : int
        Dropping modulus (inner subset index, 0-based).
    limit : int
        Upper bound (exclusive).

    Returns
    -------
    list[int]
        Sorted list of matching integers.
    """
    return sorted(
        n for n in range(2, limit)
        if dropping_set(n) == set_k and dropping_modulus(n) == modulus_m
    )
```

**Step 2: Run tests to verify they pass**

Run: `.venv/Scripts/python.exe -m pytest tests/test_orbits.py -v`
Expected: 3 PASS

**Step 3: Commit**

```bash
git add collatz/orbits.py
git commit -m "feat: add class_members to orbits module"
```

---

### Task 3: Implement aligned_orbits

**Files:**
- Modify: `tests/test_orbits.py`
- Modify: `collatz/orbits.py`

**Step 1: Write failing tests**

Append to `tests/test_orbits.py`:

```python
from collatz.orbits import class_members, aligned_orbits
import pandas as pd


def test_aligned_orbits_shape():
    """All orbits in same (set, modulus) should have equal length."""
    members = class_members(3, 0, 50)
    df = aligned_orbits(members)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == len(members)
    # All rows should have the same number of columns (no NaN)
    assert df.isna().sum().sum() == 0


def test_aligned_orbits_first_column_is_members():
    """Column 0 should be the members themselves."""
    members = class_members(3, 0, 30)
    df = aligned_orbits(members)
    assert list(df[0]) == members


def test_aligned_orbits_known_orbit():
    """dropping_orbit(5) = [5, 16, 8], so row for n=5 should be [5, 16, 8]."""
    df = aligned_orbits([5])
    assert list(df.iloc[0]) == [5, 16, 8]
```

**Step 2: Run tests to verify new tests fail**

Run: `.venv/Scripts/python.exe -m pytest tests/test_orbits.py::test_aligned_orbits_shape -v`
Expected: FAIL — `ImportError: cannot import name 'aligned_orbits'`

**Step 3: Write implementation**

Add to `collatz/orbits.py`:

```python
import pandas as pd


def aligned_orbits(members):
    """Build a DataFrame of aligned dropping orbits.

    Each row is one member's dropping orbit. All members in the same
    (set, modulus) group produce orbits of equal length, so the result
    is a clean rectangular matrix.

    Parameters
    ----------
    members : list[int]
        Numbers to compute orbits for (should share same set/modulus).

    Returns
    -------
    pd.DataFrame
        Rows = members (indexed by n), columns = orbit positions [0, 1, ...].
    """
    orbits = {n: dropping_orbit(n) for n in members}
    return pd.DataFrame.from_dict(orbits, orient="index").sort_index()
```

**Step 4: Run all tests**

Run: `.venv/Scripts/python.exe -m pytest tests/test_orbits.py -v`
Expected: 6 PASS

**Step 5: Commit**

```bash
git add collatz/orbits.py tests/test_orbits.py
git commit -m "feat: add aligned_orbits to orbits module"
```

---

### Task 4: Implement pairwise_ratios

**Files:**
- Modify: `tests/test_orbits.py`
- Modify: `collatz/orbits.py`

**Step 1: Write failing tests**

Append to `tests/test_orbits.py`:

```python
from fractions import Fraction
from collatz.orbits import class_members, aligned_orbits, pairwise_ratios


def test_pairwise_ratios_shape():
    """Ratios DataFrame should have same shape as orbits."""
    members = class_members(3, 0, 50)
    df = aligned_orbits(members)
    ratios = pairwise_ratios(df)
    assert ratios.shape == df.shape


def test_pairwise_ratios_first_row_is_one():
    """First row (reference) should be all 1s."""
    members = class_members(3, 0, 30)
    df = aligned_orbits(members)
    ratios = pairwise_ratios(df)
    assert all(r == Fraction(1) for r in ratios.iloc[0])


def test_pairwise_ratios_are_fractions():
    """All ratio values should be Fraction instances."""
    members = class_members(3, 0, 30)
    df = aligned_orbits(members)
    ratios = pairwise_ratios(df)
    for col in ratios.columns:
        for val in ratios[col]:
            assert isinstance(val, Fraction), f"Expected Fraction, got {type(val)}"
```

**Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest tests/test_orbits.py::test_pairwise_ratios_shape -v`
Expected: FAIL

**Step 3: Write implementation**

Add to `collatz/orbits.py`:

```python
from fractions import Fraction


def pairwise_ratios(orbit_df):
    """Compute element-wise ratios relative to the first member's orbit.

    For each position i and member j: ratio = orbit[j][i] / orbit[0][i].
    Uses Fraction for exact rational arithmetic.

    Parameters
    ----------
    orbit_df : pd.DataFrame
        Output of aligned_orbits().

    Returns
    -------
    pd.DataFrame
        Same shape, values are Fraction instances.
    """
    ref = orbit_df.iloc[0]
    return orbit_df.apply(
        lambda row: [Fraction(int(row[c]), int(ref[c])) for c in orbit_df.columns],
        axis=1,
        result_type="expand",
    )
```

**Step 4: Run all tests**

Run: `.venv/Scripts/python.exe -m pytest tests/test_orbits.py -v`
Expected: 9 PASS

**Step 5: Commit**

```bash
git add collatz/orbits.py tests/test_orbits.py
git commit -m "feat: add pairwise_ratios to orbits module"
```

---

### Task 5: Implement pairwise_differences

**Files:**
- Modify: `tests/test_orbits.py`
- Modify: `collatz/orbits.py`

**Step 1: Write failing tests**

Append to `tests/test_orbits.py`:

```python
from collatz.orbits import class_members, aligned_orbits, pairwise_differences


def test_pairwise_differences_first_row_zero():
    """First row should be all zeros (reference minus itself)."""
    members = class_members(3, 0, 30)
    df = aligned_orbits(members)
    diffs = pairwise_differences(df)
    assert all(d == 0 for d in diffs.iloc[0])


def test_pairwise_differences_known():
    """Check difference between n=5 and n=9 orbits.

    dropping_orbit(5) = [5, 16, 8]
    dropping_orbit(9) = [9, 28, 14]
    diffs = [4, 12, 6]
    """
    df = aligned_orbits([5, 9])
    diffs = pairwise_differences(df)
    assert list(diffs.iloc[1]) == [4, 12, 6]
```

**Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest tests/test_orbits.py::test_pairwise_differences_first_row_zero -v`
Expected: FAIL

**Step 3: Write implementation**

Add to `collatz/orbits.py`:

```python
def pairwise_differences(orbit_df):
    """Compute element-wise differences relative to the first member's orbit.

    For each position i and member j: diff = orbit[j][i] - orbit[0][i].

    Parameters
    ----------
    orbit_df : pd.DataFrame
        Output of aligned_orbits().

    Returns
    -------
    pd.DataFrame
        Same shape, integer differences.
    """
    ref = orbit_df.iloc[0]
    return orbit_df.subtract(ref)
```

**Step 4: Run all tests**

Run: `.venv/Scripts/python.exe -m pytest tests/test_orbits.py -v`
Expected: 11 PASS

**Step 5: Commit**

```bash
git add collatz/orbits.py tests/test_orbits.py
git commit -m "feat: add pairwise_differences to orbits module"
```

---

### Task 6: Implement modular_equivalences

**Files:**
- Modify: `tests/test_orbits.py`
- Modify: `collatz/orbits.py`

**Step 1: Write failing tests**

Append to `tests/test_orbits.py`:

```python
from collatz.orbits import class_members, aligned_orbits, modular_equivalences


def test_modular_equivalences_returns_series():
    members = class_members(3, 0, 50)
    df = aligned_orbits(members)
    mods = modular_equivalences(df)
    assert isinstance(mods, pd.Series)
    assert len(mods) == len(df.columns)


def test_modular_equivalences_positive():
    """All moduli should be >= 1."""
    members = class_members(3, 0, 100)
    df = aligned_orbits(members)
    mods = modular_equivalences(df)
    assert all(m >= 1 for m in mods)


def test_modular_equivalences_valid():
    """All values in a column should be congruent mod the returned modulus."""
    members = class_members(3, 0, 100)
    df = aligned_orbits(members)
    mods = modular_equivalences(df)
    for col in df.columns:
        m = mods[col]
        residues = set(int(v) % m for v in df[col])
        assert len(residues) == 1, f"Column {col}: expected 1 residue mod {m}, got {residues}"
```

**Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest tests/test_orbits.py::test_modular_equivalences_returns_series -v`
Expected: FAIL

**Step 3: Write implementation**

Add to `collatz/orbits.py`:

```python
from math import gcd
from functools import reduce


def modular_equivalences(orbit_df):
    """Find the largest modulus where all values in each column are congruent.

    For each orbit position, computes the GCD of all pairwise differences.
    This GCD is the largest m such that all values ≡ r (mod m) for some r.

    Parameters
    ----------
    orbit_df : pd.DataFrame
        Output of aligned_orbits().

    Returns
    -------
    pd.Series
        Indexed by column (orbit position), values are the moduli.
    """
    result = {}
    for col in orbit_df.columns:
        values = [int(v) for v in orbit_df[col]]
        if len(values) <= 1:
            result[col] = values[0] if values else 1
            continue
        diffs = [abs(values[i] - values[0]) for i in range(1, len(values))]
        diffs = [d for d in diffs if d > 0]
        if not diffs:
            result[col] = values[0]  # all identical
            continue
        result[col] = reduce(gcd, diffs)
    return pd.Series(result)
```

**Step 4: Run all tests**

Run: `.venv/Scripts/python.exe -m pytest tests/test_orbits.py -v`
Expected: 14 PASS

**Step 5: Commit**

```bash
git add collatz/orbits.py tests/test_orbits.py
git commit -m "feat: add modular_equivalences to orbits module"
```

---

### Task 7: Implement orbit_summary

**Files:**
- Modify: `tests/test_orbits.py`
- Modify: `collatz/orbits.py`

**Step 1: Write failing test**

Append to `tests/test_orbits.py`:

```python
from collatz.orbits import orbit_summary


def test_orbit_summary_keys():
    result = orbit_summary(3, 0, 50)
    assert set(result.keys()) == {"members", "orbits", "ratios", "differences", "modular"}


def test_orbit_summary_members_match():
    result = orbit_summary(3, 0, 50)
    assert result["members"] == class_members(3, 0, 50)
```

**Step 2: Run tests to verify they fail**

Run: `.venv/Scripts/python.exe -m pytest tests/test_orbits.py::test_orbit_summary_keys -v`
Expected: FAIL

**Step 3: Write implementation**

Add to `collatz/orbits.py`:

```python
def orbit_summary(set_k, modulus_m, limit):
    """Run all orbit comparison analyses for a (set, modulus) group.

    Parameters
    ----------
    set_k : int
        Dropping set (= dropping time).
    modulus_m : int
        Dropping modulus (0-based).
    limit : int
        Upper bound for member search.

    Returns
    -------
    dict
        Keys: "members", "orbits", "ratios", "differences", "modular".
    """
    members = class_members(set_k, modulus_m, limit)
    orbits = aligned_orbits(members)
    return {
        "members": members,
        "orbits": orbits,
        "ratios": pairwise_ratios(orbits),
        "differences": pairwise_differences(orbits),
        "modular": modular_equivalences(orbits),
    }
```

**Step 4: Run all tests**

Run: `.venv/Scripts/python.exe -m pytest tests/test_orbits.py -v`
Expected: 16 PASS

**Step 5: Commit**

```bash
git add collatz/orbits.py tests/test_orbits.py
git commit -m "feat: add orbit_summary convenience function"
```

---

### Task 8: Create exploration notebook

**Files:**
- Create: `notebooks/07-orbit-structure.ipynb`

**Step 1: Create notebook with all sections**

Create a Jupyter notebook with these cells:

**Cell 1 (markdown):** Title and purpose
```markdown
# 07 — Orbit Structure Within Dropping Classes

Explore element-wise relationships between orbits of numbers sharing the same (dropping set, dropping modulus). Numbers in the same group follow the same odd/even step pattern, producing parallel orbits of equal length.

**Questions:**
- Are element-wise ratios constant, converging, or structured?
- Do differences factor as smooth numbers (2^a × 3^b)?
- What modular equivalences hold at each orbit position?
```

**Cell 2 (code):** Setup
```python
import sys
sys.path.insert(0, "..")
from collatz.orbits import (
    class_members, aligned_orbits, pairwise_ratios,
    pairwise_differences, modular_equivalences, orbit_summary
)
from collatz.dropping import dropping_orbit, dropping_set, dropping_modulus
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fractions import Fraction

pd.set_option("display.max_columns", 20)
```

**Cell 3 (markdown):**
```markdown
## 1. Orbit Alignment — Dropping Set 3, Modulus 0
All n ≡ 1 (mod 4), n > 1: orbit length 3, step pattern: odd→even→even.
```

**Cell 4 (code):**
```python
summary_3_0 = orbit_summary(3, 0, 200)
print(f"Members: {summary_3_0['members'][:15]}...")
print(f"\nAligned orbits (first 10):")
summary_3_0["orbits"].head(10)
```

**Cell 5 (markdown):**
```markdown
## 2. Ratio Analysis
For each orbit position, compute orbit[j][i] / orbit[0][i]. If ratios are constant across positions, orbits are scalar multiples.
```

**Cell 6 (code):**
```python
ratios = summary_3_0["ratios"]
print("Ratios (first 8 members):")
print(ratios.head(8).to_string())

# Check: are ratios constant across columns for each row?
print("\n--- Are ratios constant across positions? ---")
for idx in list(ratios.index[:5]):
    row = ratios.loc[idx]
    unique = set(row)
    print(f"n={idx}: {list(row)} → {'CONSTANT' if len(unique) == 1 else f'{len(unique)} distinct'}")
```

**Cell 7 (code):**
```python
# Heatmap of ratios (as floats for visualization)
ratio_floats = ratios.head(20).map(float)
fig, ax = plt.subplots(figsize=(8, 10))
sns.heatmap(ratio_floats, annot=True, fmt=".3f", cmap="YlOrRd", ax=ax)
ax.set_title("Element-wise Ratios (Set 3, Mod 0)")
ax.set_xlabel("Orbit Position")
ax.set_ylabel("n")
plt.tight_layout()
plt.show()
```

**Cell 8 (markdown):**
```markdown
## 3. Difference Analysis
Compute orbit[j][i] - orbit[0][i]. Check for GCD structure, smooth factorizations.
```

**Cell 9 (code):**
```python
diffs = summary_3_0["differences"]
print("Differences (first 8 members):")
print(diffs.head(8).to_string())

# Factor the differences
from math import gcd
from functools import reduce

print("\n--- GCD of each column (excluding row 0) ---")
for col in diffs.columns:
    col_vals = [int(v) for v in diffs[col].iloc[1:] if v != 0]
    if col_vals:
        g = reduce(gcd, col_vals)
        print(f"Position {col}: GCD = {g}")
```

**Cell 10 (code):**
```python
# Check if differences are multiples of a base difference
print("--- Difference ratios (diff[j] / diff[1]) ---")
if len(diffs) > 2:
    base_diff = diffs.iloc[1]
    for idx in list(diffs.index[2:8]):
        row = diffs.loc[idx]
        ratios_d = [Fraction(int(row[c]), int(base_diff[c])) if base_diff[c] != 0 else None
                    for c in diffs.columns]
        print(f"n={idx}: {ratios_d}")
```

**Cell 11 (markdown):**
```markdown
## 4. Modular Equivalences
For each orbit position, find the largest modulus m where all values are congruent.
```

**Cell 12 (code):**
```python
mods = summary_3_0["modular"]
print("Modular equivalences per position:")
print(mods)

# What residue at each position?
orbits_df = summary_3_0["orbits"]
print("\nResidue class at each position:")
for col in orbits_df.columns:
    m = int(mods[col])
    r = int(orbits_df[col].iloc[0]) % m
    print(f"Position {col}: all ≡ {r} (mod {m})")
```

**Cell 13 (code):**
```python
# Bar chart of moduli
fig, ax = plt.subplots(figsize=(8, 4))
mods.plot(kind="bar", ax=ax, color="steelblue")
ax.set_title("Largest Shared Modulus per Orbit Position (Set 3, Mod 0)")
ax.set_xlabel("Orbit Position")
ax.set_ylabel("Modulus")
plt.tight_layout()
plt.show()
```

**Cell 14 (markdown):**
```markdown
## 5. Cross-Group Comparison — Dropping Set 6, Modulus 0
Repeat the analysis for a different dropping class to check universality.
```

**Cell 15 (code):**
```python
summary_6_0 = orbit_summary(6, 0, 200)
print(f"Members (set 6, mod 0): {summary_6_0['members'][:10]}...")
print(f"\nAligned orbits:")
summary_6_0["orbits"].head(8)
```

**Cell 16 (code):**
```python
# Ratios for set 6
ratios_6 = summary_6_0["ratios"]
print("Ratios (set 6, mod 0, first 5 members):")
for idx in list(ratios_6.index[:5]):
    row = ratios_6.loc[idx]
    unique = set(row)
    print(f"n={idx}: constant={len(unique)==1}, values={list(row)}")
```

**Cell 17 (code):**
```python
# Modular equivalences for set 6
mods_6 = summary_6_0["modular"]
print("Modular equivalences per position (set 6, mod 0):")
for col in summary_6_0["orbits"].columns:
    m = int(mods_6[col])
    r = int(summary_6_0["orbits"][col].iloc[0]) % m
    print(f"Position {col}: all ≡ {r} (mod {m})")
```

**Cell 18 (markdown):**
```markdown
## 6. Observations

*Fill in after running the notebook. Look for:*
- Are ratios ever constant across positions? (scalar multiples)
- Do moduli grow/shrink predictably along the orbit?
- Are differences always smooth (only factors of 2 and 3)?
- Do patterns differ between groups or are they universal?
```

**Step 2: Run the notebook to verify it executes**

Run: `.venv/Scripts/python.exe -m jupyter nbconvert --to notebook --execute notebooks/07-orbit-structure.ipynb --output 07-orbit-structure-executed.ipynb`

**Step 3: Commit**

```bash
git add notebooks/07-orbit-structure.ipynb
git commit -m "feat: add orbit structure exploration notebook"
```

---

### Task 9: Final integration test

**Step 1: Run full test suite**

Run: `.venv/Scripts/python.exe -m pytest tests/ -v`
Expected: All 16 tests PASS

**Step 2: Verify package import works end-to-end**

Run: `.venv/Scripts/python.exe -c "from collatz.orbits import orbit_summary; r = orbit_summary(3, 0, 50); print(f'Members: {len(r[\"members\"])}, Moduli: {list(r[\"modular\"])}')"`
Expected: Prints member count and moduli list without error

**Step 3: Final commit if any cleanup needed**

```bash
git add -A
git commit -m "chore: orbit structure exploration complete"
```
