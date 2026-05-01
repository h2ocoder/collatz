# Collatz Embeddings v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a "Lens-Bundle Embedding" toolkit on top of the existing `collatz` package: a small subpackage that turns integer vectors into points in a multi-lens dynamical-invariant space, supports analogy/distance/iteration operations, and ships with a notebook running first experiments.

**Architecture:** Six pure lens functions ℤ → coordinate (sector, mod3, drop_class, alpha_prefix, force, slope_log). A `Concept` is a fixed-length tuple of ints. Embedding `Φ(c)` stacks per-component lens evaluations with one-hot encoding for discrete lenses. Distance / analogy use cosine in ℝ^(m·D). Iteration applies Collatz step-wise to components; some lenses have closed-form transformations.

**Tech Stack:** Python 3.12, existing `.venv`, `collatz` package (Fraction, pandas), `numpy` for vectors, pytest for tests, `matplotlib` + optional `umap-learn` for notebook viz.

**Spec:** `docs/superpowers/specs/2026-04-30-collatz-embeddings-design.md`

**Conventions to follow:**
- Existing tests live flat in `tests/test_<module>.py` — match that.
- Functions have docstrings with `Example:` lines giving concrete inputs/outputs.
- Imports inside functions are fine for optional deps (umap, matplotlib).
- Run tests via `.venv/Scripts/python.exe -m pytest tests/test_embeddings.py -v` (Windows path; bash shell).

**Verified ground-truth values for tests:**

| n  | dropping_time | orbital_oddity | force=k−s | alpha_sequence | sector=len(αs)%12 | mod3 |
|----|---------------|-----------------|-----------|-----------------|--------------------|------|
| 3  | 6             | 2               | 4         | [1, 4]          | 2                  | 0    |
| 5  | 3             | 1               | 2         | [4]             | 1                  | 2    |
| 7  | 11            | 4               | 7         | [1, 1, 2, 3, 4] | 5                  | 1    |
| 11 | 8             | 3               | 5         | [1, 2, 3, 4]    | 4                  | 2    |
| 17 | 3             | 1               | 2         | [2, 3, 4]       | 3                  | 2    |

(Computed live; trust these.)

---

## File Structure

```
collatz/embeddings/
  __init__.py            # public API re-exports
  lenses.py              # 6 lens fns + LENS_REGISTRY metadata
  concept.py             # Concept dataclass + Phi() stacker + one-hot helper
  distance.py            # cosine, l2, weighted, force_weighted, analogy
  iteration.py           # T(c), T_syracuse(c), advance_lens
tests/
  test_embeddings.py     # all unit tests in one file
notebooks/
  09-collatz-embeddings.ipynb
docs/Explorations/
  Collatz Embeddings.md  # short Obsidian note linking spec + notebook
```

Each module ≤ ~150 lines.

---

### Task 1: Scaffold the embeddings subpackage

**Files:**
- Create: `collatz/embeddings/__init__.py`
- Create: `collatz/embeddings/lenses.py`
- Create: `collatz/embeddings/concept.py`
- Create: `collatz/embeddings/distance.py`
- Create: `collatz/embeddings/iteration.py`
- Create: `tests/test_embeddings.py`

- [ ] **Step 1: Write the failing import test**

```python
# tests/test_embeddings.py
"""Tests for collatz.embeddings package."""


def test_package_imports():
    """The embeddings package and all submodules should import cleanly."""
    from collatz import embeddings  # noqa: F401
    from collatz.embeddings import lenses, concept, distance, iteration  # noqa: F401
```

- [ ] **Step 2: Run test to verify it fails**

```
.venv/Scripts/python.exe -m pytest tests/test_embeddings.py::test_package_imports -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'collatz.embeddings'`

- [ ] **Step 3: Create the package files (all empty modules with docstrings)**

```python
# collatz/embeddings/__init__.py
"""Collatz Embeddings: lens-bundle embeddings of integer vectors as concepts.

See docs/superpowers/specs/2026-04-30-collatz-embeddings-design.md.
"""
```

```python
# collatz/embeddings/lenses.py
"""Lens functions: Z -> coordinate. One-line summary per lens in docstring."""
```

```python
# collatz/embeddings/concept.py
"""Concept dataclass and Phi() stacking embedding."""
```

```python
# collatz/embeddings/distance.py
"""Distance metrics and analogy search in lens space."""
```

```python
# collatz/embeddings/iteration.py
"""Iteration of concepts and closed-form lens advances."""
```

- [ ] **Step 4: Run test to verify it passes**

```
.venv/Scripts/python.exe -m pytest tests/test_embeddings.py::test_package_imports -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add collatz/embeddings/ tests/test_embeddings.py
git commit -m "feat(embeddings): scaffold package with empty submodules"
```

---

### Task 2: `mod3` lens

**Files:**
- Modify: `collatz/embeddings/lenses.py`
- Modify: `tests/test_embeddings.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_embeddings.py`:

```python
from collatz.embeddings.lenses import mod3


def test_mod3_basic():
    assert mod3(3) == 0
    assert mod3(7) == 1
    assert mod3(8) == 2
    assert mod3(11) == 2
```

- [ ] **Step 2: Run, verify it fails**

```
.venv/Scripts/python.exe -m pytest tests/test_embeddings.py::test_mod3_basic -v
```
Expected: FAIL with `ImportError: cannot import name 'mod3'`

- [ ] **Step 3: Implement**

Add to `collatz/embeddings/lenses.py`:

```python
def mod3(n: int) -> int:
    """3-adic residue. Encodes the 3-Adic Lock state.

    Example: mod3(3) = 0, mod3(7) = 1, mod3(8) = 2.
    """
    return n % 3
```

- [ ] **Step 4: Run, verify it passes**

```
.venv/Scripts/python.exe -m pytest tests/test_embeddings.py::test_mod3_basic -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add collatz/embeddings/lenses.py tests/test_embeddings.py
git commit -m "feat(embeddings): add mod3 lens (3-adic residue)"
```

---

### Task 3: `drop_class` lens

**Files:**
- Modify: `collatz/embeddings/lenses.py`
- Modify: `tests/test_embeddings.py`

- [ ] **Step 1: Write the failing test**

```python
from collatz.embeddings.lenses import drop_class


def test_drop_class_basic():
    # Verified: dropping_time(3) = 6, dropping_time(5) = 3.
    assert drop_class(3) == 6
    assert drop_class(5) == 3
    assert drop_class(7) == 11
```

- [ ] **Step 2: Run, verify it fails**

```
.venv/Scripts/python.exe -m pytest tests/test_embeddings.py::test_drop_class_basic -v
```
Expected: FAIL (ImportError).

- [ ] **Step 3: Implement**

```python
# collatz/embeddings/lenses.py
from collatz.dropping import dropping_set


def drop_class(n: int) -> int:
    """Dropping set k of n (steps to first value < n). Wraps collatz.dropping.dropping_set.

    Example: drop_class(3) = 6, drop_class(5) = 3.
    """
    return dropping_set(n)
```

- [ ] **Step 4: Run, verify pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/embeddings/lenses.py tests/test_embeddings.py
git commit -m "feat(embeddings): add drop_class lens"
```

---

### Task 4: `alpha_prefix` lens (with padding)

**Files:**
- Modify: `collatz/embeddings/lenses.py`
- Modify: `tests/test_embeddings.py`

- [ ] **Step 1: Write the failing tests**

```python
from collatz.embeddings.lenses import alpha_prefix


def test_alpha_prefix_pad_short():
    # alpha_sequence(3) = [1, 4]; pad to length 3 with 0.
    assert alpha_prefix(3, k=3) == (1, 4, 0)


def test_alpha_prefix_truncate_long():
    # alpha_sequence(7) = [1, 1, 2, 3, 4]; truncate to length 3.
    assert alpha_prefix(7, k=3) == (1, 1, 2)


def test_alpha_prefix_default_k():
    # Default k=3.
    assert alpha_prefix(11) == (1, 2, 3)
```

- [ ] **Step 2: Run, verify it fails**

Expected: FAIL.

- [ ] **Step 3: Implement**

```python
from collatz.core import alpha_sequence


def alpha_prefix(n: int, k: int = 3) -> tuple[int, ...]:
    """First k entries of n's alpha (Syracuse 2-adic-valuation) sequence, padded with 0.

    Example: alpha_prefix(3, k=3) = (1, 4, 0); alpha_prefix(7, k=3) = (1, 1, 2).
    """
    seq = alpha_sequence(n)
    if len(seq) >= k:
        return tuple(seq[:k])
    return tuple(seq) + (0,) * (k - len(seq))
```

- [ ] **Step 4: Run, verify pass**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/embeddings/lenses.py tests/test_embeddings.py
git commit -m "feat(embeddings): add alpha_prefix lens with pad/truncate to k"
```

---

### Task 5: `sector` lens with rotation property

**Files:**
- Modify: `collatz/embeddings/lenses.py`
- Modify: `tests/test_embeddings.py`

- [ ] **Step 1: Write the failing tests**

```python
from collatz.embeddings.lenses import sector


def test_sector_basic():
    # sector(n) = len(alpha_sequence(n)) mod 12
    assert sector(3) == 2
    assert sector(5) == 1
    assert sector(7) == 5
    assert sector(11) == 4


def test_sector_rotates_under_syracuse_step():
    """One Syracuse step decreases sector by 1 (mod 12)."""
    from collatz.core import alpha_sequence

    def syr(n):
        v = 1
        n = 3 * n + 1
        while n % 2 == 0 and v >= 0:
            n //= 2
            v += 1
            if v > 64:
                break
        return n

    for n in [3, 7, 11, 17, 27]:
        if len(alpha_sequence(n)) <= 1:
            continue
        assert sector(syr(n)) == (sector(n) - 1) % 12, f"failed for n={n}"
```

- [ ] **Step 2: Run, verify it fails**

Expected: FAIL (ImportError).

- [ ] **Step 3: Implement**

```python
def sector(n: int) -> int:
    """Eisenstein angle bin: number of Syracuse steps mod 12.

    Rotation property: under one Syracuse step n -> (3n+1)/2^v,
    sector decreases by 1 mod 12 (matches the -30 deg per step result).

    Example: sector(3) = 2 (alpha_sequence has length 2).
    """
    return len(alpha_sequence(n)) % 12
```

`alpha_sequence` is already imported from `collatz.core`.

- [ ] **Step 4: Run, verify pass**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/embeddings/lenses.py tests/test_embeddings.py
git commit -m "feat(embeddings): add sector lens with verified rotation property"
```

---

### Task 6: `force` and `slope_log` lenses

**Files:**
- Modify: `collatz/embeddings/lenses.py`
- Modify: `tests/test_embeddings.py`

- [ ] **Step 1: Write the failing tests**

```python
import math

from collatz.embeddings.lenses import force, slope_log


def test_force_basic():
    # force(n) = dropping_time(n) - orbital_oddity(n) = k - s.
    assert force(3) == 4   # 6 - 2
    assert force(5) == 2   # 3 - 1
    assert force(7) == 7   # 11 - 4


def test_slope_log_matches_formula():
    # slope_log(n) = s*log2(3) - (k - s) where s = orbital_oddity, k = dropping_time.
    expected_3 = 2 * math.log2(3) - 4
    assert math.isclose(slope_log(3), expected_3, rel_tol=1e-12)
    expected_5 = 1 * math.log2(3) - 2
    assert math.isclose(slope_log(5), expected_5, rel_tol=1e-12)
```

- [ ] **Step 2: Run, verify it fails**

Expected: FAIL.

- [ ] **Step 3: Implement**

```python
import math

from collatz.dropping import dropping_time, orbital_oddity


def force(n: int) -> int:
    """Bit-precision of n's affine subgroup: log2(P) where P = 2^(k - s).

    k = dropping_time(n), s = orbital_oddity(n) (count of odd values in dropping orbit).
    Higher force = narrower subgroup = more bits stable under iteration.

    Dual reading: epistemic confidence -- high force = well-determined, low force = loose.

    Example: force(3) = 6 - 2 = 4.
    """
    return dropping_time(n) - orbital_oddity(n)


def slope_log(n: int) -> float:
    """Log2 of the affine slope of n's subgroup: s*log2(3) - (k - s).

    Identifies the affine class within Set_k.

    Example: slope_log(3) = 2*log2(3) - 4 ~= -0.830.
    """
    s = orbital_oddity(n)
    k = dropping_time(n)
    return s * math.log2(3) - (k - s)
```

- [ ] **Step 4: Run, verify pass**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/embeddings/lenses.py tests/test_embeddings.py
git commit -m "feat(embeddings): add force and slope_log lenses"
```

---

### Task 7: Lens registry + one-hot helper

**Files:**
- Modify: `collatz/embeddings/lenses.py`
- Modify: `collatz/embeddings/concept.py`
- Modify: `tests/test_embeddings.py`

The registry tells `Phi` which lenses are discrete (need one-hot) and what their cardinalities are.

- [ ] **Step 1: Write the failing tests**

```python
import numpy as np

from collatz.embeddings.lenses import LENS_REGISTRY
from collatz.embeddings.concept import one_hot


def test_lens_registry_shape():
    # Names of every lens in registry; cardinality positive int for discrete, None for real.
    names = {spec.name for spec in LENS_REGISTRY}
    assert names == {"sector", "mod3", "drop_class", "alpha_prefix", "force", "slope_log"}
    by_name = {spec.name: spec for spec in LENS_REGISTRY}
    assert by_name["sector"].kind == "discrete" and by_name["sector"].cardinality == 12
    assert by_name["mod3"].kind == "discrete" and by_name["mod3"].cardinality == 3
    assert by_name["force"].kind == "real" and by_name["force"].cardinality is None


def test_one_hot_basic():
    np.testing.assert_array_equal(one_hot(0, 3), np.array([1.0, 0.0, 0.0]))
    np.testing.assert_array_equal(one_hot(2, 3), np.array([0.0, 0.0, 1.0]))


def test_one_hot_clamps_out_of_range():
    """Values outside [0, cardinality) clamp to last bucket."""
    np.testing.assert_array_equal(one_hot(7, 3), np.array([0.0, 0.0, 1.0]))
```

- [ ] **Step 2: Run, verify it fails**

Expected: FAIL.

- [ ] **Step 3: Implement**

In `collatz/embeddings/lenses.py`, append:

```python
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class LensSpec:
    name: str
    fn: Callable[[int], object]
    kind: str               # "discrete" or "real"
    cardinality: int | None  # for discrete: number of buckets; for real: None
    alpha_k: int = 3        # only used for alpha_prefix

# alpha_prefix yields a tuple of length alpha_k; treat each entry as discrete in [0, ALPHA_MAX).
ALPHA_MAX = 8  # cap; alphas above this are folded into the last bucket.

LENS_REGISTRY: tuple[LensSpec, ...] = (
    LensSpec("sector",       sector,       "discrete", 12),
    LensSpec("mod3",         mod3,         "discrete", 3),
    LensSpec("drop_class",   drop_class,   "discrete", 32),  # cap at 32 (covers all small n)
    LensSpec("alpha_prefix", alpha_prefix, "discrete", ALPHA_MAX, alpha_k=3),
    LensSpec("force",        force,        "real",     None),
    LensSpec("slope_log",    slope_log,    "real",     None),
)
```

In `collatz/embeddings/concept.py`:

```python
import numpy as np


def one_hot(value: int, cardinality: int) -> np.ndarray:
    """One-hot vector of length `cardinality`. Out-of-range values clamp to last bucket.

    Example: one_hot(0, 3) = [1, 0, 0]; one_hot(7, 3) = [0, 0, 1].
    """
    idx = max(0, min(int(value), cardinality - 1))
    v = np.zeros(cardinality, dtype=np.float64)
    v[idx] = 1.0
    return v
```

- [ ] **Step 4: Run, verify pass**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/embeddings/lenses.py collatz/embeddings/concept.py tests/test_embeddings.py
git commit -m "feat(embeddings): add LENS_REGISTRY metadata + one_hot helper"
```

---

### Task 8: `Concept` dataclass

**Files:**
- Modify: `collatz/embeddings/concept.py`
- Modify: `tests/test_embeddings.py`

- [ ] **Step 1: Write the failing tests**

```python
import pytest

from collatz.embeddings.concept import Concept


def test_concept_construction():
    c = Concept("man", (3, 17, 6))
    assert c.name == "man"
    assert c.vec == (3, 17, 6)
    assert c.m == 3


def test_concept_rejects_non_int():
    with pytest.raises(TypeError):
        Concept("bad", (3.5, 17, 6))


def test_concept_rejects_empty():
    with pytest.raises(ValueError):
        Concept("empty", ())


def test_concept_normalizes_list_to_tuple():
    c = Concept("xs", [3, 17, 6])
    assert c.vec == (3, 17, 6)
    assert isinstance(c.vec, tuple)
```

- [ ] **Step 2: Run, verify it fails**

Expected: FAIL.

- [ ] **Step 3: Implement**

In `collatz/embeddings/concept.py`, append:

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Concept:
    """A named integer vector. Default convention: m=3 components.

    The vector encodes the concept; meaning emerges from the lens projections.
    """
    name: str
    vec: tuple[int, ...]

    def __post_init__(self):
        # Normalize list -> tuple (frozen dataclass requires object.__setattr__).
        if not isinstance(self.vec, tuple):
            object.__setattr__(self, "vec", tuple(self.vec))
        if len(self.vec) == 0:
            raise ValueError("Concept must have at least one component")
        if not all(isinstance(x, int) for x in self.vec):
            raise TypeError("Concept components must all be ints")

    @property
    def m(self) -> int:
        return len(self.vec)
```

- [ ] **Step 4: Run, verify pass**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/embeddings/concept.py tests/test_embeddings.py
git commit -m "feat(embeddings): add Concept dataclass"
```

---

### Task 9: `Phi` stacker

**Files:**
- Modify: `collatz/embeddings/concept.py`
- Modify: `collatz/embeddings/__init__.py`
- Modify: `tests/test_embeddings.py`

- [ ] **Step 1: Write the failing tests**

```python
from collatz.embeddings.concept import Phi
from collatz.embeddings.lenses import LENS_REGISTRY


def test_phi_shape():
    """Phi(c) length = m * (sum of per-lens output sizes).

    Per-lens sizes:
      sector: 12, mod3: 3, drop_class: 32, alpha_prefix: 3*8 = 24,
      force: 1, slope_log: 1
    Total per component D = 12 + 3 + 32 + 24 + 1 + 1 = 73.
    For m=3: total = 219.
    """
    c = Concept("test", (3, 5, 7))
    v = Phi(c)
    assert v.shape == (3 * 73,)


def test_phi_pure_concept_constant_in_anchoring_lenses():
    """Two pure-mod3 concepts with same residue produce identical mod3 segments."""
    a = Concept("a", (1, 4, 7))    # all mod3 == 1
    b = Concept("b", (10, 13, 16)) # all mod3 == 1
    va = Phi(a)
    vb = Phi(b)
    # Mod3 segment offset within one component: 12 (after sector).
    # Per-component stride D = 73.
    # Compare mod3 one-hot for each of the m=3 components.
    for i in range(3):
        offset = i * 73 + 12
        assert (va[offset:offset + 3] == vb[offset:offset + 3]).all()


def test_phi_returns_float_ndarray():
    import numpy as np
    v = Phi(Concept("x", (3, 5, 7)))
    assert v.dtype == np.float64
```

- [ ] **Step 2: Run, verify it fails**

Expected: FAIL.

- [ ] **Step 3: Implement**

Append to `collatz/embeddings/concept.py`:

```python
def _encode_lens_value(spec, value) -> np.ndarray:
    """Encode one lens output for one component as a flat float vector."""
    if spec.name == "alpha_prefix":
        # tuple of length alpha_k; one-hot each entry.
        parts = [one_hot(v, spec.cardinality) for v in value]
        return np.concatenate(parts)
    if spec.kind == "discrete":
        return one_hot(int(value), spec.cardinality)
    # real-valued lens: single float.
    return np.array([float(value)], dtype=np.float64)


def Phi(c: Concept) -> np.ndarray:
    """Embed a Concept into lens space as a flat float64 ndarray of shape (m*D,).

    D is the sum of per-lens encoded sizes (one-hot for discrete, scalar for real).
    """
    from collatz.embeddings.lenses import LENS_REGISTRY  # local import avoids cycle
    rows = []
    for n in c.vec:
        for spec in LENS_REGISTRY:
            rows.append(_encode_lens_value(spec, spec.fn(n)))
    return np.concatenate(rows)
```

Update `collatz/embeddings/__init__.py`:

```python
"""Collatz Embeddings: lens-bundle embeddings of integer vectors as concepts."""

from .concept import Concept, Phi
from .lenses import LENS_REGISTRY

__all__ = ["Concept", "Phi", "LENS_REGISTRY"]
```

- [ ] **Step 4: Run, verify pass**

```
.venv/Scripts/python.exe -m pytest tests/test_embeddings.py -v
```
Expected: ALL PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/embeddings/ tests/test_embeddings.py
git commit -m "feat(embeddings): add Phi() stacker and public API"
```

---

### Task 10: `cosine` and `l2` distance metrics

**Files:**
- Modify: `collatz/embeddings/distance.py`
- Modify: `tests/test_embeddings.py`

- [ ] **Step 1: Write the failing tests**

```python
import numpy as np

from collatz.embeddings.distance import cosine, l2


def test_cosine_self_is_one():
    v = np.array([1.0, 2.0, 3.0])
    assert np.isclose(cosine(v, v), 1.0)


def test_cosine_orthogonal_is_zero():
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    assert np.isclose(cosine(a, b), 0.0)


def test_l2_self_is_zero():
    v = np.array([1.0, 2.0, 3.0])
    assert np.isclose(l2(v, v), 0.0)


def test_l2_known():
    a = np.array([0.0, 0.0])
    b = np.array([3.0, 4.0])
    assert np.isclose(l2(a, b), 5.0)
```

- [ ] **Step 2: Run, verify it fails**

Expected: FAIL.

- [ ] **Step 3: Implement**

```python
# collatz/embeddings/distance.py
"""Distance metrics and analogy search in lens space."""

import numpy as np


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity in [-1, 1]; 1 means parallel, 0 orthogonal, -1 antiparallel."""
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def l2(a: np.ndarray, b: np.ndarray) -> float:
    """Euclidean distance."""
    return float(np.linalg.norm(a - b))
```

- [ ] **Step 4: Run, verify pass**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/embeddings/distance.py tests/test_embeddings.py
git commit -m "feat(embeddings): add cosine and l2 distance metrics"
```

---

### Task 11: `weighted` distance with lens ablation

**Files:**
- Modify: `collatz/embeddings/distance.py`
- Modify: `tests/test_embeddings.py`

- [ ] **Step 1: Write the failing tests**

```python
from collatz.embeddings.distance import weighted, ablate_lens
from collatz.embeddings import Concept, Phi


def test_weighted_unit_weights_equals_cosine():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([2.0, 1.0, 4.0])
    w = np.ones_like(a)
    assert np.isclose(weighted(a, b, w), cosine(a, b))


def test_weighted_zero_weights_returns_zero_vector_distance():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0])
    w = np.zeros_like(a)
    # Both projected vectors are zero -> cosine returns 0.0 by convention.
    assert weighted(a, b, w) == 0.0


def test_ablate_lens_zeros_only_target_axes():
    """ablate_lens('mod3') returns weights with mod3 axes = 0, others = 1."""
    w = ablate_lens("mod3", m=3)
    # Per-component stride D=73; mod3 occupies axes [12, 15) within each component.
    for i in range(3):
        offset = i * 73
        assert (w[offset + 12 : offset + 15] == 0).all()
        # sector axes (offset .. offset+12) untouched
        assert (w[offset : offset + 12] == 1).all()
```

- [ ] **Step 2: Run, verify it fails**

Expected: FAIL.

- [ ] **Step 3: Implement**

Append to `collatz/embeddings/distance.py`:

```python
def weighted(a: np.ndarray, b: np.ndarray, w: np.ndarray) -> float:
    """Weighted cosine: cosine(w*a, w*b). Zero weights ablate axes."""
    return cosine(a * w, b * w)


def ablate_lens(name: str, m: int) -> np.ndarray:
    """Return a weight vector that zeros only the axes of the named lens.

    The vector matches the shape of Phi(c) for a concept of m components.
    """
    from collatz.embeddings.lenses import LENS_REGISTRY

    # Compute per-lens slice within one component.
    slices: dict[str, slice] = {}
    offset = 0
    for spec in LENS_REGISTRY:
        if spec.name == "alpha_prefix":
            size = spec.alpha_k * spec.cardinality
        elif spec.kind == "discrete":
            size = spec.cardinality
        else:
            size = 1
        slices[spec.name] = slice(offset, offset + size)
        offset += size
    D = offset

    if name not in slices:
        raise ValueError(f"unknown lens: {name}")

    w = np.ones(m * D, dtype=np.float64)
    sl = slices[name]
    for i in range(m):
        w[i * D + sl.start : i * D + sl.stop] = 0.0
    return w
```

Re-import `cosine` from same module (already there). Note: tests need `from ... import cosine` too — append to imports at top of test file.

- [ ] **Step 4: Run, verify pass**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/embeddings/distance.py tests/test_embeddings.py
git commit -m "feat(embeddings): add weighted distance and ablate_lens helper"
```

---

### Task 12: `analogy` search

**Files:**
- Modify: `collatz/embeddings/distance.py`
- Modify: `tests/test_embeddings.py`

- [ ] **Step 1: Write the failing tests**

```python
from collatz.embeddings.distance import analogy
from collatz.embeddings import Concept


def test_analogy_returns_ranked_list():
    a = Concept("a", (3, 5, 7))
    b = Concept("b", (5, 7, 9))
    c = Concept("c", (11, 13, 15))
    cands = [Concept(f"d{i}", (i, i + 2, i + 4)) for i in range(13, 25, 2)]
    ranked = analogy(a, b, c, cands)
    assert len(ranked) == len(cands)
    # Ranked is list of (Concept, score) sorted descending by score.
    scores = [s for _, s in ranked]
    assert scores == sorted(scores, reverse=True)


def test_analogy_self_consistency():
    """If d == c (so a:b :: c:c), then c should be among top results."""
    a = Concept("a", (3, 5, 7))
    b = Concept("b", (5, 7, 9))
    c = Concept("c", (11, 13, 15))
    cands = [c, Concept("far", (1000, 2000, 3000))]
    ranked = analogy(a, a, c, cands)  # a:a :: c:?  -> c
    assert ranked[0][0] is c
```

- [ ] **Step 2: Run, verify it fails**

Expected: FAIL.

- [ ] **Step 3: Implement**

```python
def analogy(
    a, b, c, candidates, *, weight: np.ndarray | None = None
) -> list[tuple[object, float]]:
    """Solve a:b :: c:?  Returns candidates ranked by cosine to (Phi(a) - Phi(b) + Phi(c))."""
    from collatz.embeddings import Phi

    target = Phi(a) - Phi(b) + Phi(c)
    scores = []
    for d in candidates:
        v = Phi(d)
        score = weighted(v, target, weight) if weight is not None else cosine(v, target)
        scores.append((d, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores
```

- [ ] **Step 4: Run, verify pass**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/embeddings/distance.py tests/test_embeddings.py
git commit -m "feat(embeddings): add analogy ranking"
```

---

### Task 13: Concept iteration `T(c)` and `T_syracuse(c)`

**Files:**
- Modify: `collatz/embeddings/iteration.py`
- Modify: `collatz/embeddings/__init__.py`
- Modify: `tests/test_embeddings.py`

- [ ] **Step 1: Write the failing tests**

```python
from collatz.embeddings.iteration import T, T_syracuse
from collatz.embeddings import Concept


def test_T_step_each_component():
    # T(3) = 10, T(17) = 52, T(6) = 3.
    c = Concept("man", (3, 17, 6))
    out = T(c)
    assert out.vec == (10, 52, 3)
    assert out.name == "man"


def test_T_syracuse_collapses_evens():
    # T_syr(3) = (3*3+1)/2 = 5; T_syr(5) = (16)/16 = 1; T_syr(6) = 3 (one halving).
    assert T_syracuse(Concept("x", (3, 5, 6))).vec == (5, 1, 3)
```

- [ ] **Step 2: Run, verify it fails**

Expected: FAIL.

- [ ] **Step 3: Implement**

```python
# collatz/embeddings/iteration.py
"""Iteration of concepts and closed-form lens advances."""

from collatz.core import collatz_step
from collatz.embeddings.concept import Concept


def _syr_step(n: int) -> int:
    """One Syracuse step: T_syr(n) = (3n+1)/2^v if n odd; n/2 if even (single halving)."""
    if n % 2 == 0:
        return n // 2
    n = 3 * n + 1
    while n % 2 == 0:
        n //= 2
    return n


def T(c: Concept) -> Concept:
    """Apply one Collatz step to each component independently."""
    return Concept(c.name, tuple(collatz_step(n) for n in c.vec))


def T_syracuse(c: Concept) -> Concept:
    """Apply one Syracuse step (collapse trailing halvings on odd-step result)."""
    return Concept(c.name, tuple(_syr_step(n) for n in c.vec))
```

Update `collatz/embeddings/__init__.py`:

```python
from .concept import Concept, Phi
from .lenses import LENS_REGISTRY
from .iteration import T, T_syracuse

__all__ = ["Concept", "Phi", "LENS_REGISTRY", "T", "T_syracuse"]
```

- [ ] **Step 4: Run, verify pass**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/embeddings/iteration.py collatz/embeddings/__init__.py tests/test_embeddings.py
git commit -m "feat(embeddings): add T() and T_syracuse() concept iteration"
```

---

### Task 14: `advance_lens` for closed-form lenses

**Note:** `mod3` does NOT have a closed-form transition under one Syracuse step from value alone. The post-step residue is `2^v mod 3` where v is the alpha of n — it depends on alpha, not just on the input residue. So v1 only supports `sector`. (The spec's iteration table called mod3 "Conserved (finite-state attractor)" — meaning the orbit stays in {1,2}, not that the transition is deterministic from value alone.)

**Files:**
- Modify: `collatz/embeddings/iteration.py`
- Modify: `tests/test_embeddings.py`

- [ ] **Step 1: Write the failing tests**

```python
import pytest

from collatz.embeddings.iteration import advance_lens


def test_advance_lens_sector_rotates():
    # sector decreases by 1 mod 12 per Syracuse step.
    assert advance_lens(2, "sector") == 1
    assert advance_lens(0, "sector") == 11


def test_advance_lens_mod3_not_supported():
    # mod3 is not closed-form from value alone (depends on alpha).
    with pytest.raises(ValueError):
        advance_lens(1, "mod3")


def test_advance_lens_unsupported_lens_raises():
    with pytest.raises(ValueError):
        advance_lens(5, "force")  # no closed form
```

- [ ] **Step 2: Run, verify it fails**

Expected: FAIL (ImportError).

- [ ] **Step 3: Implement**

```python
_LENS_TRANSITIONS = {
    "sector": lambda v: (v - 1) % 12,
}


def advance_lens(value: int, lens_name: str) -> int:
    """Advance a discrete lens value by one Syracuse step in closed form.

    Only supported for lenses whose post-step value is a function of the pre-step
    value alone (currently: sector).
    """
    if lens_name not in _LENS_TRANSITIONS:
        raise ValueError(f"no closed-form advance for lens '{lens_name}'")
    return _LENS_TRANSITIONS[lens_name](value)
```

- [ ] **Step 4: Run, verify pass**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add collatz/embeddings/iteration.py tests/test_embeddings.py
git commit -m "feat(embeddings): add advance_lens for closed-form lens transitions"
```

---

### Task 15: Notebook 09 — lens sanity (cells 1–3)

**Files:**
- Create: `notebooks/09-collatz-embeddings.ipynb`

- [ ] **Step 1: Create notebook with intro markdown + setup imports**

Use `.venv/Scripts/python.exe -m jupyter nbclassic` or just write the JSON directly. Easiest: write a Python helper that emits an ipynb skeleton, then add cells.

Cell 1 (markdown):
```markdown
# 09 — Collatz Embeddings (v1)

Treat dropping-set / Eisenstein / 3-adic / alpha / force / slope as a lens basis.
Integer vectors as concept encodings. Analogy arithmetic in lens space.

Spec: `docs/superpowers/specs/2026-04-30-collatz-embeddings-design.md`
Plan: `docs/superpowers/plans/2026-04-30-collatz-embeddings.md`
```

Cell 2 (code):
```python
import sys
sys.path.insert(0, '..')
import numpy as np
import matplotlib.pyplot as plt
from collatz.embeddings import Concept, Phi, LENS_REGISTRY, T, T_syracuse
from collatz.embeddings.lenses import sector, mod3, drop_class, alpha_prefix, force, slope_log
from collatz.embeddings.distance import cosine, l2, weighted, analogy, ablate_lens
```

Cell 3 (markdown): `## 1. Lens sanity & fixtures`

Cell 4 (code):
```python
fixtures = [
    (3,  {"sector": 2, "mod3": 0, "drop_class": 6,  "alpha_prefix": (1, 4, 0), "force": 4, "slope_log": 2*np.log2(3)-4}),
    (5,  {"sector": 1, "mod3": 2, "drop_class": 3,  "alpha_prefix": (4, 0, 0), "force": 2}),
    (7,  {"sector": 5, "mod3": 1, "drop_class": 11, "alpha_prefix": (1, 1, 2), "force": 7}),
    (11, {"sector": 4, "mod3": 2, "drop_class": 8,  "alpha_prefix": (1, 2, 3), "force": 5}),
]
fns = {"sector": sector, "mod3": mod3, "drop_class": drop_class, "alpha_prefix": alpha_prefix, "force": force, "slope_log": slope_log}
for n, expected in fixtures:
    for k, v in expected.items():
        got = fns[k](n)
        ok = np.isclose(got, v) if isinstance(v, float) else got == v
        print(f"n={n} {k}: got {got!r:>12} expected {v!r:>12} {'OK' if ok else 'FAIL'}")
```

- [ ] **Step 2: Run notebook to verify cells execute and produce expected output**

```bash
.venv/Scripts/python.exe -m jupyter nbconvert --to notebook --execute notebooks/09-collatz-embeddings.ipynb --output 09-collatz-embeddings.ipynb
```
Expected: all "OK", no exceptions.

- [ ] **Step 3: Commit**

```bash
git add notebooks/09-collatz-embeddings.ipynb
git commit -m "feat(notebook): 09 cells 1-3 lens sanity & fixtures"
```

---

### Task 16: Notebook 09 — pure-concept geometry (PCA viz)

**Files:**
- Modify: `notebooks/09-collatz-embeddings.ipynb`

- [ ] **Step 1: Add cells for pure-concept construction and PCA**

Cell 5 (markdown): `## 2. Pure-concept geometry`

Cell 6 (code) — construct concepts:
```python
# Pure-Set_3 concept: all components in dropping set 3 (members are 1 mod 4).
from collatz.utils import members_of_class
from collatz.dropping import dropping_set
set3 = members_of_class(dropping_set, 3, 200)
set6 = members_of_class(dropping_set, 6, 200)
# Random mixed concept.
import random; random.seed(0)
concepts = [
    Concept("pure_set3_a", tuple(set3[:3])),
    Concept("pure_set3_b", tuple(set3[3:6])),
    Concept("pure_set3_c", tuple(set3[6:9])),
    Concept("pure_set6_a", tuple(set6[:3])),
    Concept("pure_set6_b", tuple(set6[3:6])),
    Concept("mixed_a", (set3[0], set6[0], set3[1])),
    Concept("mixed_b", (set3[1], set6[1], set3[2])),
]
X = np.stack([Phi(c) for c in concepts])
print(X.shape)
```

Cell 7 (code) — PCA viz:
```python
from numpy.linalg import svd
Xc = X - X.mean(0, keepdims=True)
U, S, Vt = svd(Xc, full_matrices=False)
proj = Xc @ Vt.T[:, :2]
fig, ax = plt.subplots(figsize=(8, 6))
for (c, p) in zip(concepts, proj):
    ax.scatter(*p, s=60)
    ax.annotate(c.name, p, fontsize=9)
ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
ax.set_title("Pure vs mixed concepts in lens space")
plt.tight_layout()
```

Cell 8 (markdown): note observed clustering (pure-Set_3 should cluster together, etc.)

- [ ] **Step 2: Run notebook, inspect figure**

Same nbconvert command as Task 15 step 2.

- [ ] **Step 3: Commit**

```bash
git add notebooks/09-collatz-embeddings.ipynb
git commit -m "feat(notebook): 09 cells 5-8 pure-concept geometry + PCA"
```

---

### Task 17: Notebook 09 — hand-built analogy quads

**Files:**
- Modify: `notebooks/09-collatz-embeddings.ipynb`

- [ ] **Step 1: Add analogy experiment cells**

Cell 9 (markdown): `## 3. Hand-built analogy quads`

Cell 10 (code) — build quads:
```python
# Quad 1: same Syracuse-step transformation. (n, T_syr(n)) :: (m, T_syr(m)).
from collatz.embeddings.iteration import _syr_step
def shift_concept(c: Concept) -> Concept:
    return Concept(c.name + "_shifted", tuple(_syr_step(x) for x in c.vec))

quads = []
for ns in [(3, 5, 7), (11, 13, 17), (19, 23, 27)]:
    a = Concept("a", ns)
    b = shift_concept(a)
    a2 = Concept("c", tuple(x + 4 for x in ns))   # different starting points
    b2 = shift_concept(a2)
    quads.append((a, b, a2, b2))

# Distractor pool: 50 random integer triples avoiding the quad components.
random.seed(1)
distractors = [
    Concept(f"dist_{i}", tuple(random.randint(2, 1000) for _ in range(3)))
    for i in range(50)
]
```

Cell 11 (code) — run analogy ranking:
```python
ranks = []
for a, b, c, expected_d in quads:
    pool = distractors + [expected_d]
    ranked = analogy(a, b, c, pool)
    rank = next(i for i, (cand, _) in enumerate(ranked) if cand is expected_d)
    ranks.append(rank)
    print(f"{a.name} -> {b.name} :: {c.name} -> ?  expected_rank={rank} of {len(pool)}")
print(f"\nMean rank of expected d: {np.mean(ranks):.1f} (chance baseline: {len(distractors)/2:.1f})")
```

- [ ] **Step 2: Execute, observe results, write a markdown cell summarizing**

Cell 12 (markdown): record observed mean rank, whether above-chance, surprises.

- [ ] **Step 3: Commit**

```bash
git add notebooks/09-collatz-embeddings.ipynb
git commit -m "feat(notebook): 09 cells 9-12 analogy quads + ranking"
```

---

### Task 18: Notebook 09 — iteration drift + lens ablation

**Files:**
- Modify: `notebooks/09-collatz-embeddings.ipynb`

- [ ] **Step 1: Drift curve cells**

Cell 13 (markdown): `## 4. Iteration drift & anchoring`

Cell 14 (code):
```python
def iterate_concept(c: Concept, k: int) -> Concept:
    for _ in range(k):
        c = T_syracuse(c)
    return c

K = 8
fig, ax = plt.subplots(figsize=(9, 5))
for a, b, c, expected_d in quads:
    base_diff = Phi(b) - Phi(a)
    drifts = []
    for k in range(K + 1):
        ak = iterate_concept(a, k)
        bk = iterate_concept(b, k)
        drift = cosine(Phi(bk) - Phi(ak), base_diff)
        drifts.append(drift)
    ax.plot(range(K + 1), drifts, marker="o", label=f"{a.name}->{b.name}")
ax.set_xlabel("Syracuse iterations k")
ax.set_ylabel("cosine(initial diff, k-step diff)")
ax.set_title("Analogy-vector drift under iteration")
ax.legend(fontsize=8)
plt.tight_layout()
```

Cell 15 (code) — lens ablation. `analogy()` from v1 supports an optional `weight=` kwarg (added in Task 12), so use it directly:

```python
for lens_name in ["sector", "mod3", "drop_class", "alpha_prefix", "force", "slope_log"]:
    w = ablate_lens(lens_name, m=3)
    ranks = []
    for a, b, c, expected_d in quads:
        pool = distractors + [expected_d]
        ranked = analogy(a, b, c, pool, weight=w)
        rank = next(i for i, (cand, _) in enumerate(ranked) if cand is expected_d)
        ranks.append(rank)
    print(f"ablate {lens_name}: mean rank = {np.mean(ranks):.1f}")
```

- [ ] **Step 2: Execute, observe results, write a markdown cell summarizing which lens carries the analogy (rank should *worsen* most when the carrying lens is ablated).**

- [ ] **Step 3: Commit**

```bash
git add notebooks/09-collatz-embeddings.ipynb
git commit -m "feat(notebook): 09 cells 13-15 drift curves + lens ablation"
```

---

### Task 19: Notebook 09 — open-questions + Obsidian note

**Files:**
- Modify: `notebooks/09-collatz-embeddings.ipynb`
- Create: `docs/Explorations/Collatz Embeddings.md`

- [ ] **Step 1: Add closing markdown cells**

Cell 16 (markdown): `## 5. Open questions for v2` — bullet list of what surprised you, candidate v2 hypotheses (component coupling, learned weights, longer α-prefixes, cross-component differences).

- [ ] **Step 2: Create Obsidian exploration note**

```markdown
# Collatz Embeddings

A first attempt at treating dynamical invariants as a lens basis on the integers,
turning integer vectors into "concept" embeddings analogous to word2vec.

- **Spec:** [[../superpowers/specs/2026-04-30-collatz-embeddings-design]]
- **Plan:** [[../superpowers/plans/2026-04-30-collatz-embeddings]]
- **Notebook:** `notebooks/09-collatz-embeddings.ipynb`
- **Code:** `collatz/embeddings/`

## Lens basis (v1)

| Lens | Class | What it captures |
|---|---|---|
| sector | conserved (cycles, period 12) | Eisenstein angle |
| mod3 | conserved (finite-state attractor on {1,2}) | 3-adic state |
| drop_class | drifting | bit-budget |
| alpha_prefix | decaying | leading dynamics |
| force | decaying (entropy-like) | bit-precision / epistemic confidence |
| slope_log | mostly anchoring | affine-class identity |

Anchoring lenses carry meaning through iteration; decaying lenses measure age.
```

- [ ] **Step 3: Run final notebook execute end-to-end**

```bash
.venv/Scripts/python.exe -m jupyter nbconvert --to notebook --execute notebooks/09-collatz-embeddings.ipynb --output 09-collatz-embeddings.ipynb
```
Expected: all cells run without error.

- [ ] **Step 4: Commit**

```bash
git add notebooks/09-collatz-embeddings.ipynb "docs/Explorations/Collatz Embeddings.md"
git commit -m "feat(notebook): 09 close-out + add Obsidian exploration note"
```

---

### Task 20: Final integration check

**Files:** none modified

- [ ] **Step 1: Run the full test suite**

```
.venv/Scripts/python.exe -m pytest tests/test_embeddings.py -v
```
Expected: all green, no warnings.

- [ ] **Step 2: Confirm public API surface**

```
.venv/Scripts/python.exe -c "
from collatz.embeddings import Concept, Phi, LENS_REGISTRY, T, T_syracuse
from collatz.embeddings.distance import cosine, l2, weighted, analogy, ablate_lens
from collatz.embeddings.iteration import advance_lens
print('public API OK')
"
```

- [ ] **Step 3: Confirm notebook re-executes cleanly**

```
.venv/Scripts/python.exe -m jupyter nbconvert --to notebook --execute notebooks/09-collatz-embeddings.ipynb --output 09-collatz-embeddings.ipynb
```

- [ ] **Step 4: No commit needed unless something was fixed in this task**

---

## Notes for the executor

- **Always run from the repo root** so relative paths in the notebook work.
- **`alpha_prefix` cardinality cap (ALPHA_MAX=8)**: alphas can exceed 8 in larger orbits. The clamping in `one_hot` handles overflow gracefully — sanity-check in the notebook by printing alpha_sequence(27) and confirming behavior is sensible.
- **No new top-level dependencies.** Everything uses numpy + matplotlib (already in environment).
- **Frequent commits.** Each task ends with a commit; do not skip.
