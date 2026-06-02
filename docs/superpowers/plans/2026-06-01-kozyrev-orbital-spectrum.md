# Kozyrev Orbital Spectrum Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a discrete Kozyrev (= dyadic Haar) wavelet decomposition of Collatz dropping-set indicators, the Sturmian sign field $\chi$, and stopping time $T$, producing a single figure that shows their orbital-shell spectra and partial reconstructions.

**Architecture:** A new standalone module `collatz/wavelets.py` implements the fast Haar transform with the heap-style flat index `idx(j, a) = 2^j - 1 + a` and the orthonormal Kozyrev/Haar basis. A new script `scripts/collatz_kozyrev_spectrum.py` consumes shared helpers from `collatz/utils.py` (lifted out of `collatz_2adic_potential.py`) and the stopping/dropping APIs, runs the decomposition, and writes one PNG.

**Tech Stack:** Python 3.12, NumPy, Matplotlib (Agg backend), pytest. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-06-01-kozyrev-orbital-spectrum-design.md`

**Conventions to follow:**
- Tests live flat in `tests/test_<module>.py` — match the embeddings pattern.
- Functions get docstrings with concrete `Example:` lines.
- Scripts use `matplotlib.use("Agg")` and write to `data/`.
- Run tests via `python -m pytest tests/test_wavelets.py -v` (adapt to your interpreter; the repo's pyproject installs as `pip install -e .` then `pip install pytest`).
- Numerical tolerances: `rtol=1e-12, atol=1e-12` for Haar identities (the transform is exact in float64 up to rounding).

**Math reference (basis convention):**

For $N = 2^K$, the orthonormal Kozyrev basis on $\mathbb{Z}_2 / 2^K \mathbb{Z}_2$ consists of:

- One constant mode $\varphi \equiv 1/\sqrt{N}$.
- Wavelets $\psi_{j, a}$ for shell $j \in \{0, 1, \dots, K-1\}$ and offset $a \in \{0, \dots, 2^j - 1\}$, total $N - 1$. Each $\psi_{j,a}$ is supported on indices $[a \cdot 2^{K-j},\ (a+1) \cdot 2^{K-j})$, with value $+1/\sqrt{2^{K-j}}$ on the first half of its support and $-1/\sqrt{2^{K-j}}$ on the second half.

Shell $j = 0$ is *coarsest* (one wavelet, support all of $[0, N)$). Shell $j = K-1$ is *finest* (each support has just 2 indices). The flat index is $\text{idx}(j, a) = 2^j - 1 + a$ (heap layout).

Parseval: $\|f\|_2^2 = c_0^2 + \sum_{j, a} c_{j,a}^2$ where $c_0 = \langle f, \varphi \rangle$ and $c_{j,a} = \langle f, \psi_{j, a} \rangle$.

---

## File Structure

```
collatz/
  wavelets.py                       # NEW: forward/inverse Haar + shell energies + basis vector
  utils.py                          # MODIFY: add sturmian_sign, beatty_to_o, bits_to_2d
scripts/
  collatz_2adic_potential.py        # MODIFY: import lifted helpers from utils; use collatz.stopping.stopping_time
  collatz_kozyrev_spectrum.py       # NEW: build inputs, run FHT, write PNG
tests/
  test_wavelets.py                  # NEW: Parseval, round-trip, orthonormality, basis, partial recon
  test_utils.py                     # NEW: known values for the lifted helpers
docs/Explorations/
  Kozyrev Orbital Spectrum.md       # NEW: brief note linking spec, plan, output PNG
data/
  collatz_kozyrev_spectrum.png      # NEW: final figure (output, not committed code)
```

Each new module stays under ~250 lines.

---

### Task 1: Lift helpers into `collatz/utils.py`

**Files:**
- Modify: `collatz/utils.py`
- Create: `tests/test_utils.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_utils.py
"""Tests for collatz.utils helpers."""

import math

import numpy as np

from collatz.utils import (
    beatty_to_o,
    bits_to_2d,
    sturmian_sign,
)


LOG2_3 = math.log2(3.0)


def test_beatty_to_o_first_rungs():
    """Beatty rung k_o = o + floor(o * log2 3) + 1; verify first few values."""
    m = beatty_to_o()
    # o=1: k = 1 + 1 + 1 = 3
    # o=2: k = 2 + 3 + 1 = 6
    # o=3: k = 3 + 4 + 1 = 8
    # o=4: k = 4 + 6 + 1 = 11
    assert m[3] == 1
    assert m[6] == 2
    assert m[8] == 3
    assert m[11] == 4


def test_sturmian_sign_threshold():
    """epsilon_o = +1 if (o-1)*log2(3) mod 1 >= 2 - log2(3), else -1."""
    threshold = 2.0 - LOG2_3
    for o in range(1, 30):
        frac = ((o - 1) * LOG2_3) % 1.0
        expected = 1 if frac >= threshold else -1
        assert sturmian_sign(o) == expected, f"mismatch at o={o}"


def test_bits_to_2d_split():
    """Splitting K bits of n into (high, low) returns the expected coordinates."""
    K = 6
    # n = 0b101_010 = 42; high half (top 3 bits) = 0b101 = 5; low half = 0b010 = 2
    hi, lo = bits_to_2d(42, K)
    assert hi == 5
    assert lo == 2
    # n = 0 -> (0, 0)
    assert bits_to_2d(0, K) == (0, 0)
    # n = 2^K - 1 -> (max, max)
    assert bits_to_2d((1 << K) - 1, K) == ((1 << (K - K // 2)) - 1, (1 << (K // 2)) - 1)


def test_helpers_are_pure():
    """Helpers should not mutate global state; calling twice returns equal results."""
    a = beatty_to_o()
    b = beatty_to_o()
    assert a == b
    assert sturmian_sign(5) == sturmian_sign(5)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_utils.py -v
```
Expected: `ImportError: cannot import name 'beatty_to_o' from 'collatz.utils'` (or similar).

- [ ] **Step 3: Implement the helpers in `collatz/utils.py`**

Append to `collatz/utils.py`:

```python
import math

import numpy as np


LOG2_3 = math.log2(3.0)


def beatty_to_o(max_o: int = 100) -> dict[int, int]:
    """Map standard Beatty rung k_o = o + floor(o * log2 3) + 1 back to o.

    Returns a dict {k: o} covering o in [1, max_o). Used to identify which
    odd-stopping-time class a given Collatz drop time belongs to.

    Example: beatty_to_o()[3] == 1; beatty_to_o()[6] == 2.
    """
    m: dict[int, int] = {}
    for o in range(1, max_o):
        k = o + int(math.floor(o * LOG2_3)) + 1
        m[k] = o
    return m


def sturmian_sign(o: int) -> int:
    """Sturmian sign epsilon_o for o >= 1: +1 if gap_o = 3, -1 if gap_o = 2.

    The threshold is 2 - log2(3); compared against fractional part of
    (o - 1) * log2(3).

    Example: sturmian_sign(1) == 1; sturmian_sign(2) == -1.
    """
    threshold = 2.0 - LOG2_3
    frac = ((o - 1) * LOG2_3) % 1.0
    return 1 if frac >= threshold else -1


def bits_to_2d(n: int, K: int) -> tuple[int, int]:
    """Split n's K bits into (high half, low half) for 2D bit-split imaging.

    Returns (row, col) where row indexes the top (K - K//2) bits and col
    indexes the low K//2 bits. Used by 2-adic visualizations so that
    2-adically close integers land in nearby pixels.

    Example: bits_to_2d(42, 6) == (5, 2).
    """
    half = K // 2
    low = n & ((1 << half) - 1)
    high = n >> half
    return high, low


def trailing_zeros_vec(arr: np.ndarray) -> np.ndarray:
    """v_2 (2-adic valuation) of each element of arr; arr must be > 0.

    Vectorized via the bit trick `low = a & -a`.
    """
    a = arr.astype(np.int64)
    low = a & -a
    return np.round(np.log2(low.astype(np.float64))).astype(np.int64)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_utils.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add collatz/utils.py tests/test_utils.py
git commit -m "refactor(utils): lift sturmian_sign, beatty_to_o, bits_to_2d helpers"
```

---

### Task 2: Migrate `collatz_2adic_potential.py` to shared helpers

**Files:**
- Modify: `scripts/collatz_2adic_potential.py`

- [ ] **Step 1: Replace local helper definitions with imports**

Open `scripts/collatz_2adic_potential.py` and:

1. Delete the local definitions of `standard_stopping_time`, `beatty_to_o`, `sturmian_sign`, `trailing_zeros_vec`, and `bits_to_2d` (lines roughly 47–93).
2. Add to the imports block near the top:

```python
from collatz.stopping import stopping_time
from collatz.utils import (
    beatty_to_o,
    bits_to_2d,
    sturmian_sign,
    trailing_zeros_vec,
    LOG2_3,
)
```

3. Inside `main()`, replace every call to `standard_stopping_time(n, max_steps=400)` with `stopping_time(n)` and remove the `max_steps` parameter (the canonical implementation handles bounds).

- [ ] **Step 2: Run the script to confirm it still produces the figure**

```bash
python scripts/collatz_2adic_potential.py
```
Expected: prints `Saved data/collatz_2adic_potential.png`, no errors. The PNG is regenerated; visual content should match.

- [ ] **Step 3: Run all existing tests to ensure no regressions**

```bash
python -m pytest -v
```
Expected: previously-green tests stay green; new `tests/test_utils.py` is green.

- [ ] **Step 4: Commit**

```bash
git add scripts/collatz_2adic_potential.py
git commit -m "refactor(scripts): collatz_2adic_potential uses shared utils + collatz.stopping"
```

---

### Task 3: Create `collatz/wavelets.py` scaffold with `idx` and `kozyrev_basis_vector`

**Files:**
- Create: `collatz/wavelets.py`
- Create: `tests/test_wavelets.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_wavelets.py
"""Tests for collatz.wavelets — Kozyrev/Haar transform."""

import numpy as np
import pytest

from collatz.wavelets import idx, kozyrev_basis_vector


def test_idx_layout():
    """Heap-style flat index: idx(j, a) = 2^j - 1 + a."""
    # Shell 0 has 1 wavelet at index 0
    assert idx(0, 0) == 0
    # Shell 1 has 2 wavelets at indices 1, 2
    assert idx(1, 0) == 1
    assert idx(1, 1) == 2
    # Shell 2 has 4 wavelets at indices 3..6
    assert idx(2, 0) == 3
    assert idx(2, 3) == 6


def test_kozyrev_basis_vector_K2():
    """For K = 2 (N = 4), verify the three explicit basis vectors."""
    psi_00 = kozyrev_basis_vector(0, 0, 2)
    psi_10 = kozyrev_basis_vector(1, 0, 2)
    psi_11 = kozyrev_basis_vector(1, 1, 2)

    np.testing.assert_allclose(psi_00, [0.5, 0.5, -0.5, -0.5])
    np.testing.assert_allclose(psi_10, [1 / np.sqrt(2), -1 / np.sqrt(2), 0, 0])
    np.testing.assert_allclose(psi_11, [0, 0, 1 / np.sqrt(2), -1 / np.sqrt(2)])


def test_kozyrev_orthonormal_K5():
    """All N-1 basis vectors at K=5 should be pairwise orthonormal."""
    K = 5
    N = 1 << K
    vectors = []
    for j in range(K):
        for a in range(1 << j):
            vectors.append(kozyrev_basis_vector(j, a, K))
    M = np.stack(vectors)  # shape (N-1, N)
    gram = M @ M.T
    np.testing.assert_allclose(gram, np.eye(N - 1), atol=1e-12)


def test_kozyrev_basis_orthogonal_to_constant():
    """Every wavelet should be orthogonal to the constant function."""
    K = 5
    N = 1 << K
    phi = np.ones(N) / np.sqrt(N)
    for j in range(K):
        for a in range(1 << j):
            psi = kozyrev_basis_vector(j, a, K)
            assert abs(phi @ psi) < 1e-12, f"non-orthogonal at j={j}, a={a}"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_wavelets.py -v
```
Expected: `ModuleNotFoundError: No module named 'collatz.wavelets'`.

- [ ] **Step 3: Implement `collatz/wavelets.py`**

```python
# collatz/wavelets.py
"""Kozyrev/Haar wavelet transform on Z_2 / 2^K Z_2.

The Kozyrev wavelet basis on Z_p (Kozyrev, 2002) consists of eigenfunctions
of the Vladimirov p-adic Laplacian. For p = 2 they coincide with the
discrete dyadic Haar wavelets on the integers [0, 2^K).

Basis convention:
    - phi(n) = 1 / sqrt(N)                            (one constant mode)
    - psi_{j, a}(n), j in [0, K), a in [0, 2^j)       (N - 1 wavelets)
      supp(psi_{j, a}) = [a * 2^{K-j}, (a+1) * 2^{K-j})
      values: +1/sqrt(2^{K-j}) on the first half of the support,
              -1/sqrt(2^{K-j}) on the second half.

Shell j = 0 is coarsest; j = K-1 is finest. Flat index: 2^j - 1 + a.

Parseval: ||f||^2 = c0^2 + sum_{j,a} c_{j,a}^2.
"""
from __future__ import annotations

import numpy as np


def idx(j: int, a: int) -> int:
    """Heap-style flat index for wavelet (j, a).

    Example: idx(0, 0) == 0, idx(1, 0) == 1, idx(2, 3) == 6.
    """
    return (1 << j) - 1 + a


def kozyrev_basis_vector(j: int, a: int, K: int) -> np.ndarray:
    """Build psi_{j, a} explicitly as a length-2^K array.

    Used for tests and illustration; not called by the fast transform.

    Example: kozyrev_basis_vector(1, 0, 2) == [1/sqrt(2), -1/sqrt(2), 0, 0].
    """
    if not (0 <= j < K):
        raise ValueError(f"shell j={j} out of range [0, {K})")
    if not (0 <= a < (1 << j)):
        raise ValueError(f"offset a={a} out of range [0, {1 << j})")
    N = 1 << K
    support_size = 1 << (K - j)
    half = support_size // 2
    start = a * support_size
    scale = 1.0 / np.sqrt(support_size)
    vec = np.zeros(N, dtype=np.float64)
    vec[start : start + half] = scale
    vec[start + half : start + support_size] = -scale
    return vec
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_wavelets.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add collatz/wavelets.py tests/test_wavelets.py
git commit -m "feat(wavelets): Kozyrev basis vector + idx for K-truncated Z_2"
```

---

### Task 4: Implement `haar_forward` (fast Kozyrev transform)

**Files:**
- Modify: `collatz/wavelets.py`
- Modify: `tests/test_wavelets.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_wavelets.py`:

```python
from collatz.wavelets import haar_forward


def test_haar_forward_K2_known_values():
    """For K=2, transform of [a, b, c, d] matches hand calculation."""
    f = np.array([1.0, 2.0, 3.0, 4.0])
    c0, coeffs = haar_forward(f)
    # c0 = (1+2+3+4)/2 = 5.0
    assert abs(c0 - 5.0) < 1e-12
    # coeffs[0] (shell 0) = (1+2-3-4)/2 = -2.0
    # coeffs[1] (shell 1, a=0) = (1-2)/sqrt(2) = -1/sqrt(2)
    # coeffs[2] (shell 1, a=1) = (3-4)/sqrt(2) = -1/sqrt(2)
    np.testing.assert_allclose(coeffs, [-2.0, -1 / np.sqrt(2), -1 / np.sqrt(2)])


def test_haar_forward_basis_vector_is_one_hot():
    """The forward transform of a basis vector psi_{j,a} should be a one-hot at idx(j,a)."""
    K = 4
    N = 1 << K
    for j in range(K):
        for a in range(1 << j):
            psi = kozyrev_basis_vector(j, a, K)
            c0, coeffs = haar_forward(psi)
            assert abs(c0) < 1e-12, f"c0 nonzero for psi_{j},{a}"
            expected = np.zeros(N - 1)
            expected[idx(j, a)] = 1.0
            np.testing.assert_allclose(coeffs, expected, atol=1e-12)


def test_haar_forward_constant_function():
    """For f ≡ c, all wavelet coefficients should be zero; c0 = c * sqrt(N)."""
    K = 6
    N = 1 << K
    f = np.full(N, 3.5)
    c0, coeffs = haar_forward(f)
    np.testing.assert_allclose(coeffs, np.zeros(N - 1), atol=1e-12)
    assert abs(c0 - 3.5 * np.sqrt(N)) < 1e-10


def test_haar_forward_parseval():
    """||f||^2 == c0^2 + sum |c_{j,a}|^2 for random f."""
    rng = np.random.default_rng(42)
    K = 8
    N = 1 << K
    f = rng.standard_normal(N)
    c0, coeffs = haar_forward(f)
    lhs = float(f @ f)
    rhs = c0 * c0 + float(coeffs @ coeffs)
    assert abs(lhs - rhs) / lhs < 1e-12


def test_haar_forward_rejects_non_power_of_two():
    with pytest.raises(ValueError):
        haar_forward(np.zeros(7))
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_wavelets.py -v
```
Expected: 5 failures with `ImportError` or `AttributeError` on `haar_forward`.

- [ ] **Step 3: Implement `haar_forward` in `collatz/wavelets.py`**

Append to `collatz/wavelets.py`:

```python
def haar_forward(f: np.ndarray) -> tuple[float, np.ndarray]:
    """Fast orthonormal Haar/Kozyrev transform.

    Args:
        f: length-N array, N a power of 2.

    Returns:
        (c0, coeffs) where
            c0      = <f, phi>  with phi(n) = 1/sqrt(N)
            coeffs  = length-(N-1) array; coeffs[idx(j, a)] = <f, psi_{j, a}>

    Implementation: standard in-place dyadic cascade, O(N log N).
    The finest details (shell j = K - 1) are computed first; the coarsest
    (shell j = 0) last.

    Example: haar_forward(np.array([1., 2., 3., 4.])) -> (5.0, [-2.0, -1/sqrt(2), -1/sqrt(2)]).
    """
    f = np.asarray(f, dtype=np.float64)
    N = f.size
    if N == 0 or (N & (N - 1)) != 0:
        raise ValueError(f"length {N} is not a positive power of 2")
    K = int(round(np.log2(N)))

    s = f.copy()
    coeffs = np.empty(N - 1, dtype=np.float64)
    inv_sqrt2 = 1.0 / np.sqrt(2.0)
    # Cascade from finest (j = K-1) down to coarsest (j = 0).
    for j in range(K - 1, -1, -1):
        # s has length 2^(j+1) at this point.
        new_s = (s[0::2] + s[1::2]) * inv_sqrt2
        new_d = (s[0::2] - s[1::2]) * inv_sqrt2
        coeffs[(1 << j) - 1 : (1 << (j + 1)) - 1] = new_d
        s = new_s
    c0 = float(s[0])
    return c0, coeffs
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_wavelets.py -v
```
Expected: all wavelet tests pass.

- [ ] **Step 5: Commit**

```bash
git add collatz/wavelets.py tests/test_wavelets.py
git commit -m "feat(wavelets): fast forward Haar/Kozyrev transform"
```

---

### Task 5: Implement `haar_inverse` with `depth_cutoff` for partial reconstructions

**Files:**
- Modify: `collatz/wavelets.py`
- Modify: `tests/test_wavelets.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_wavelets.py`:

```python
from collatz.wavelets import haar_inverse


def test_haar_inverse_round_trip_random():
    """haar_inverse(*haar_forward(f)) ≈ f to float64 precision."""
    rng = np.random.default_rng(7)
    for K in (2, 4, 6, 9):
        N = 1 << K
        f = rng.standard_normal(N)
        c0, coeffs = haar_forward(f)
        g = haar_inverse(c0, coeffs)
        np.testing.assert_allclose(g, f, atol=1e-12, rtol=1e-12)


def test_haar_inverse_full_reconstruction_equals_input():
    """With depth_cutoff = K (default), full reconstruction is exact."""
    f = np.array([1.0, 2.0, 3.0, 4.0, -1.0, 0.5, 7.0, -2.0])
    c0, coeffs = haar_forward(f)
    g = haar_inverse(c0, coeffs, depth_cutoff=None)
    np.testing.assert_allclose(g, f, atol=1e-12)


def test_haar_inverse_partial_reconstruction_monotone():
    """||f - f_J||^2 is non-increasing as J increases (Parseval projection)."""
    rng = np.random.default_rng(11)
    K = 8
    N = 1 << K
    f = rng.standard_normal(N)
    c0, coeffs = haar_forward(f)
    prev_err = np.inf
    for J in range(K + 1):
        f_J = haar_inverse(c0, coeffs, depth_cutoff=J)
        err = float(np.sum((f - f_J) ** 2))
        assert err <= prev_err + 1e-12, f"reconstruction error grew at J={J}"
        prev_err = err
    # At J = K, error must be ~0
    assert prev_err < 1e-20


def test_haar_inverse_J0_returns_mean():
    """With depth_cutoff = 0, reconstruction is f's mean projected onto phi."""
    f = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    c0, coeffs = haar_forward(f)
    f_0 = haar_inverse(c0, coeffs, depth_cutoff=0)
    expected = np.full_like(f, f.mean())
    np.testing.assert_allclose(f_0, expected, atol=1e-12)


def test_haar_inverse_ball_indicator_concentrates_at_coarse_shells():
    """Indicator of a 2-adic ball at level j0 has zero coefficients at shells j > j0."""
    K = 5
    N = 1 << K
    j0 = 2  # ball of support size N / 2^j0 = 8
    a0 = 1  # ball at indices [8, 16)
    support = 1 << (K - j0)
    f = np.zeros(N)
    f[a0 * support : (a0 + 1) * support] = 1.0
    c0, coeffs = haar_forward(f)
    # All wavelet coefficients at shells j > j0 must be zero
    for j in range(j0 + 1, K):
        for a in range(1 << j):
            assert abs(coeffs[idx(j, a)]) < 1e-12, f"nonzero at j={j}, a={a}"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_wavelets.py -v
```
Expected: 5 failures on `haar_inverse` not found.

- [ ] **Step 3: Implement `haar_inverse` in `collatz/wavelets.py`**

Append to `collatz/wavelets.py`:

```python
def haar_inverse(
    c0: float,
    coeffs: np.ndarray,
    depth_cutoff: int | None = None,
) -> np.ndarray:
    """Inverse fast Haar/Kozyrev transform.

    Args:
        c0:            constant-mode coefficient.
        coeffs:        length-(N-1) wavelet coefficients in flat layout.
        depth_cutoff:  if J is given, only shells j < J are used (partial
                       reconstruction f_J). J = None or J = K is exact.

    Returns:
        length-N float64 array.

    Example: haar_inverse(*haar_forward(f)) == f for any power-of-2 length f.
    """
    coeffs = np.asarray(coeffs, dtype=np.float64)
    N = coeffs.size + 1
    if N == 0 or (N & (N - 1)) != 0:
        raise ValueError(f"coeffs length {coeffs.size} is not 2^K - 1")
    K = int(round(np.log2(N)))
    if depth_cutoff is None:
        depth_cutoff = K
    if not (0 <= depth_cutoff <= K):
        raise ValueError(f"depth_cutoff={depth_cutoff} out of range [0, {K}]")

    inv_sqrt2 = 1.0 / np.sqrt(2.0)
    s = np.array([c0], dtype=np.float64)
    # Inverse cascade from coarsest (j = 0) to finest (j = K - 1).
    for j in range(0, K):
        d_slice = coeffs[(1 << j) - 1 : (1 << (j + 1)) - 1]
        if j >= depth_cutoff:
            d = np.zeros_like(d_slice)
        else:
            d = d_slice
        new_s = np.empty(s.size * 2, dtype=np.float64)
        new_s[0::2] = (s + d) * inv_sqrt2
        new_s[1::2] = (s - d) * inv_sqrt2
        s = new_s
    return s
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_wavelets.py -v
```
Expected: all wavelet tests pass.

- [ ] **Step 5: Commit**

```bash
git add collatz/wavelets.py tests/test_wavelets.py
git commit -m "feat(wavelets): inverse Haar with depth_cutoff for partial reconstructions"
```

---

### Task 6: Add `shell_energies` and `coefficient_grid`

**Files:**
- Modify: `collatz/wavelets.py`
- Modify: `tests/test_wavelets.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_wavelets.py`:

```python
from collatz.wavelets import coefficient_grid, shell_energies


def test_shell_energies_sum_to_total_wavelet_energy():
    """sum(shell_energies) == sum(coeffs^2)."""
    rng = np.random.default_rng(3)
    K = 7
    N = 1 << K
    f = rng.standard_normal(N)
    _, coeffs = haar_forward(f)
    E = shell_energies(coeffs, K)
    assert E.shape == (K,)
    np.testing.assert_allclose(E.sum(), coeffs @ coeffs, rtol=1e-12)


def test_shell_energies_basis_vector():
    """A single basis vector psi_{j0, a0} has all its energy at shell j0."""
    K = 5
    j0 = 2
    a0 = 1
    psi = kozyrev_basis_vector(j0, a0, K)
    _, coeffs = haar_forward(psi)
    E = shell_energies(coeffs, K)
    expected = np.zeros(K)
    expected[j0] = 1.0
    np.testing.assert_allclose(E, expected, atol=1e-12)


def test_coefficient_grid_shape_and_padding():
    """Triangle grid is (K, 2^(K-1)) with NaN padding outside (j, a) range."""
    K = 4
    N = 1 << K
    coeffs = np.arange(N - 1, dtype=np.float64)
    grid = coefficient_grid(coeffs, K)
    assert grid.shape == (K, 1 << (K - 1))
    # Row j = 0 has 1 valid entry (rest NaN)
    assert not np.isnan(grid[0, 0])
    assert np.isnan(grid[0, 1])
    # Row j = K - 1 is fully populated
    assert not np.any(np.isnan(grid[K - 1]))
    # Value at (j, a) should be coeffs[idx(j, a)]^2
    assert abs(grid[2, 0] - coeffs[idx(2, 0)] ** 2) < 1e-12
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_wavelets.py -v
```

- [ ] **Step 3: Implement the two functions**

Append to `collatz/wavelets.py`:

```python
def shell_energies(coeffs: np.ndarray, K: int) -> np.ndarray:
    """Per-shell wavelet energy E_j = sum_a c_{j, a}^2.

    Returns a length-K array, indexed by shell j in [0, K).
    """
    coeffs = np.asarray(coeffs, dtype=np.float64)
    if coeffs.size != (1 << K) - 1:
        raise ValueError(f"coeffs size {coeffs.size} != 2^K - 1 for K={K}")
    out = np.empty(K, dtype=np.float64)
    sq = coeffs * coeffs
    for j in range(K):
        out[j] = sq[(1 << j) - 1 : (1 << (j + 1)) - 1].sum()
    return out


def coefficient_grid(coeffs: np.ndarray, K: int) -> np.ndarray:
    """Reshape coeffs into a (K, 2^(K-1)) triangle for spectrogram plotting.

    Row j contains |c_{j, a}|^2 for a in [0, 2^j); remaining cells are NaN.
    """
    coeffs = np.asarray(coeffs, dtype=np.float64)
    if coeffs.size != (1 << K) - 1:
        raise ValueError(f"coeffs size {coeffs.size} != 2^K - 1 for K={K}")
    width = 1 << (K - 1) if K > 0 else 1
    grid = np.full((K, width), np.nan, dtype=np.float64)
    for j in range(K):
        row = coeffs[(1 << j) - 1 : (1 << (j + 1)) - 1] ** 2
        grid[j, : row.size] = row
    return grid
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_wavelets.py -v
```

- [ ] **Step 5: Commit**

```bash
git add collatz/wavelets.py tests/test_wavelets.py
git commit -m "feat(wavelets): shell_energies and coefficient_grid"
```

---

### Task 7: Build the input-field constructors used by the spectrum script

**Files:**
- Create: `scripts/collatz_kozyrev_spectrum.py` (initial skeleton with input helpers only)

- [ ] **Step 1: Create the script with input-field helpers**

```python
# scripts/collatz_kozyrev_spectrum.py
"""Kozyrev orbital spectrum of Collatz dropping sets.

Decomposes three fields on Z / 2^K Z in the orthonormal Kozyrev (= dyadic
Haar) wavelet basis:

  - chi(n)        the proved Sturmian sign of n's dropping class,
                  zero on off-Beatty values
  - 1_{D_k}(n)    indicator of dropping set k (selected k values)
  - T(n)          standard stopping time

For each field we compute the shell-energy spectrum E_j, partial
reconstructions f_J at increasing J, and a shuffle-based null band for chi.

Output: data/collatz_kozyrev_spectrum.png
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from collatz.dropping import dropping_set
from collatz.stopping import stopping_time
from collatz.utils import beatty_to_o, bits_to_2d, sturmian_sign
from collatz.wavelets import (
    coefficient_grid,
    haar_forward,
    haar_inverse,
    shell_energies,
)


# ---------- Input field constructors ----------


def build_chi(N: int) -> np.ndarray:
    """Sturmian sign field chi(n) for n in [0, N).

    chi[0] := 0 (no class). For n >= 1:
      - if stopping_time(n) == 1: chi[n] = +1 (k_0 convention)
      - if stopping_time(n) maps back to a Beatty rung o: chi[n] = sturmian_sign(o)
      - else (off-Beatty tail): chi[n] = 0
    """
    k_to_o = beatty_to_o()
    chi = np.zeros(N, dtype=np.float64)
    for n in range(1, N):
        t = stopping_time(n)
        if t == 1:
            chi[n] = 1.0
        elif t in k_to_o:
            chi[n] = float(sturmian_sign(k_to_o[t]))
        else:
            chi[n] = 0.0
    return chi


def build_dropping_indicator(N: int, k: int) -> np.ndarray:
    """Indicator vector 1_{D_k}(n) for n in [0, N): 1 if dropping_set(n) == k."""
    out = np.zeros(N, dtype=np.float64)
    for n in range(2, N):
        if dropping_set(n) == k:
            out[n] = 1.0
    return out


def build_stopping_time_field(N: int) -> np.ndarray:
    """Stopping-time field T(n) as float for n in [0, N); T(0) = T(1) = 0."""
    out = np.zeros(N, dtype=np.float64)
    for n in range(2, N):
        out[n] = float(stopping_time(n))
    return out


# ---------- Wavelet analysis helpers ----------


def shuffle_null_band(
    f: np.ndarray, K: int, n_shuffles: int = 100, seed: int = 0
) -> tuple[np.ndarray, np.ndarray]:
    """Estimate per-shell null mean and std under random permutations of f.

    Returns (mean[K], std[K]) of shell energies over `n_shuffles` random
    permutations.
    """
    rng = np.random.default_rng(seed)
    samples = np.empty((n_shuffles, K), dtype=np.float64)
    for i in range(n_shuffles):
        idx = rng.permutation(f.size)
        _, c = haar_forward(f[idx])
        samples[i] = shell_energies(c, K)
    return samples.mean(axis=0), samples.std(axis=0)


def field_to_2d(field: np.ndarray, K: int) -> np.ndarray:
    """Lay out a length-2^K field as a 2D bit-split image (high bits row, low bits col)."""
    half = K // 2
    rows = 1 << (K - half)
    cols = 1 << half
    img = np.full((rows, cols), np.nan, dtype=np.float64)
    for n in range(1, field.size):
        hi, lo = bits_to_2d(n, K)
        if hi < rows and lo < cols:
            img[hi, lo] = field[n]
    return img


def main() -> None:
    raise SystemExit("Pipeline not yet implemented; see Task 8.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-test the input builders interactively**

```bash
python -c "
import numpy as np
from scripts.collatz_kozyrev_spectrum import (
    build_chi, build_dropping_indicator, build_stopping_time_field,
    shuffle_null_band, field_to_2d,
)
from collatz.wavelets import haar_forward, shell_energies

K = 8
N = 1 << K
chi = build_chi(N)
T = build_stopping_time_field(N)
D1 = build_dropping_indicator(N, 1)
print('chi nonzero:', int(np.count_nonzero(chi)))
print('D1 nonzero:', int(D1.sum()))
print('T mean:', float(T.mean()))
c0, c = haar_forward(chi)
E = shell_energies(c, K)
print('shell energies chi:', E)
mean, std = shuffle_null_band(chi, K, n_shuffles=20, seed=1)
print('null mean:', mean)
img = field_to_2d(chi, K)
print('img shape:', img.shape)
"
```
Expected: prints non-trivial values; no exceptions. (Note: invoking a script as `scripts.collatz_kozyrev_spectrum` requires the project be on `sys.path`, which `pip install -e .` provides — alternatively change to `import importlib.util` or run from `python scripts/...`.)

- [ ] **Step 3: Commit**

```bash
git add scripts/collatz_kozyrev_spectrum.py
git commit -m "feat(scripts): kozyrev_spectrum — input field builders + analysis helpers"
```

---

### Task 8: Implement the figure pipeline and produce `collatz_kozyrev_spectrum.png`

**Files:**
- Modify: `scripts/collatz_kozyrev_spectrum.py`

- [ ] **Step 1: Replace the `main()` stub with the full pipeline**

Replace the `main()` function (and remove the `SystemExit`) in `scripts/collatz_kozyrev_spectrum.py` with:

```python
def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(exist_ok=True)

    K = 11
    N = 1 << K
    target_dropping_classes = [1, 2, 4, 5, 7, 8]
    partial_recon_depths = [2, 4, 6, 8, K]

    print(f"K = {K}, N = {N}")
    print("Building input fields...")
    chi = build_chi(N)
    T = build_stopping_time_field(N)
    indicators = {
        k: build_dropping_indicator(N, k) for k in target_dropping_classes
    }
    nonempty = [k for k, v in indicators.items() if v.sum() > 0]
    if len(nonempty) < len(target_dropping_classes):
        skipped = sorted(set(target_dropping_classes) - set(nonempty))
        print(f"  skipping empty dropping classes: {skipped}")
    target_dropping_classes = nonempty

    print("Running Haar transforms...")
    c0_chi, coeffs_chi = haar_forward(chi)
    c0_T, coeffs_T = haar_forward(T)
    coeffs_Dk = {k: haar_forward(indicators[k])[1] for k in target_dropping_classes}

    E_chi = shell_energies(coeffs_chi, K)
    E_T = shell_energies(coeffs_T, K)
    E_Dk = {k: shell_energies(coeffs_Dk[k], K) for k in target_dropping_classes}

    print("Estimating shuffle null band for chi (100 shuffles)...")
    null_mean, null_std = shuffle_null_band(chi, K, n_shuffles=100, seed=0)

    print("Building partial reconstructions of chi...")
    chi_reconstructions = {
        J: haar_inverse(c0_chi, coeffs_chi, depth_cutoff=J)
        for J in partial_recon_depths
    }

    # ---------- Figure ----------
    fig = plt.figure(figsize=(16, 13))
    gs = fig.add_gridspec(3, 3, hspace=0.45, wspace=0.32)

    # Row 0: shell-energy curves
    ax = fig.add_subplot(gs[0, 0])
    js = np.arange(K)
    ax.plot(js, E_chi, marker="o", color="#2c3e50", label=r"$E_j(\chi)$")
    ax.fill_between(
        js,
        null_mean - 2 * null_std,
        null_mean + 2 * null_std,
        color="#bdc3c7",
        alpha=0.6,
        label=r"shuffle null $\pm 2\sigma$",
    )
    ax.plot(js, null_mean, color="#7f8c8d", lw=0.8, linestyle="--", label="null mean")
    ax.set_xlabel("shell j")
    ax.set_ylabel(r"$E_j$")
    ax.set_title(r"Sturmian field $\chi$: shell energies vs shuffle null")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    ax = fig.add_subplot(gs[0, 1])
    cmap = plt.colormaps["viridis"]
    for i, k in enumerate(target_dropping_classes):
        color = cmap(i / max(1, len(target_dropping_classes) - 1))
        norm = E_Dk[k].sum()
        if norm > 0:
            ax.plot(js, E_Dk[k] / norm, marker="o", color=color, label=f"$D_{k}$")
    ax.set_xlabel("shell j")
    ax.set_ylabel(r"$\hat E_j$ (normalized)")
    ax.set_title("Dropping-class fingerprints")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    ax = fig.add_subplot(gs[0, 2])
    ax.plot(js, E_T, marker="o", color="#c0392b", label=r"$E_j(T)$")
    ax.set_xlabel("shell j")
    ax.set_ylabel(r"$E_j$")
    ax.set_title("Stopping time T(n) — control")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Row 1: bit-split images of partial reconstructions of chi
    selected_recon = [partial_recon_depths[0], partial_recon_depths[len(partial_recon_depths) // 2], partial_recon_depths[-1]]
    titles = [rf"$\chi_{{J={J}}}$" for J in selected_recon]
    for col, (J, title) in enumerate(zip(selected_recon, titles)):
        img = field_to_2d(chi_reconstructions[J], K)
        ax = fig.add_subplot(gs[1, col])
        vmax = float(np.nanmax(np.abs(img))) or 1.0
        ax.imshow(
            img,
            cmap="RdBu_r",
            aspect="auto",
            vmin=-vmax,
            vmax=vmax,
            interpolation="nearest",
            origin="lower",
        )
        ax.set_xlabel(f"low {K // 2} bits of n")
        ax.set_ylabel(f"high {K - K // 2} bits of n")
        ax.set_title(title)

    # Row 2: dyadic spectrograms (triangle plots) of chi, D_1 (if present), T
    spectro_targets: list[tuple[str, np.ndarray]] = [
        (r"$\chi$", coeffs_chi),
    ]
    if target_dropping_classes:
        k0 = target_dropping_classes[0]
        spectro_targets.append((rf"$\mathbf{{1}}_{{D_{k0}}}$", coeffs_Dk[k0]))
    spectro_targets.append(("T(n)", coeffs_T))

    for col, (label, c) in enumerate(spectro_targets):
        grid = coefficient_grid(c, K)
        ax = fig.add_subplot(gs[2, col])
        ax.imshow(
            np.log1p(grid),
            cmap="viridis",
            aspect="auto",
            origin="lower",
            interpolation="nearest",
        )
        ax.set_xlabel("offset a")
        ax.set_ylabel("shell j")
        ax.set_title(f"dyadic spectrogram: {label} (log scale)")

    fig.suptitle(
        "Kozyrev orbital spectrum of Collatz dropping classification\n"
        rf"$N = 2^{{{K}}} = {N}$ — shell-energy fingerprints + chi partial reconstructions",
        fontsize=13,
        y=0.995,
    )

    out_png = out_dir / "collatz_kozyrev_spectrum.png"
    fig.savefig(out_png, dpi=120, facecolor="white", bbox_inches="tight")
    print(f"Saved {out_png}")
```

- [ ] **Step 2: Run the script end-to-end**

```bash
python scripts/collatz_kozyrev_spectrum.py
```
Expected: prints `Saved data/collatz_kozyrev_spectrum.png`, completes in under 60 s on a laptop. No exceptions.

- [ ] **Step 3: Verify the PNG exists and has reasonable size**

```bash
ls -l data/collatz_kozyrev_spectrum.png
```
Expected: file exists, size > 100 KB.

- [ ] **Step 4: Run the full test suite to confirm no regressions**

```bash
python -m pytest -v
```
Expected: all tests pass.

- [ ] **Step 5: Commit code + figure**

```bash
git add scripts/collatz_kozyrev_spectrum.py data/collatz_kozyrev_spectrum.png
git commit -m "feat(spectrum): Kozyrev orbital spectrum figure for chi, dropping classes, T"
```

---

### Task 9: Write the Exploration note

**Files:**
- Create: `docs/Explorations/Kozyrev Orbital Spectrum.md`

- [ ] **Step 1: Write the note**

```markdown
# Kozyrev Orbital Spectrum

**Spec:** [[../superpowers/specs/2026-06-01-kozyrev-orbital-spectrum-design]]
**Plan:** [[../superpowers/plans/2026-06-01-kozyrev-orbital-spectrum]]
**Figure:** `data/collatz_kozyrev_spectrum.png`

## What it shows

Decomposition of three fields on $\mathbb{Z} / 2^K \mathbb{Z}$ (with $K = 11$) in the orthonormal Kozyrev wavelet basis — the eigenbasis of the 2-adic Vladimirov operator $D^\alpha$, which for $p = 2$ coincides with dyadic Haar wavelets.

Fields:

- $\chi(n)$ — Sturmian sign of the dropping class containing $n$ (the proved sign rule from [[Sturmian Bridge]]).
- $\mathbf{1}_{D_k}(n)$ for selected dropping classes.
- $T(n)$ — standard stopping time, as a control.

For each field we plot:

- **Shell-energy spectrum** $E_j = \sum_a |c_{j, a}|^2$ — interpretable as the "radial probability distribution" in the QM-orbital analogy ($j$ = principal quantum number).
- **Partial reconstructions** $\chi_J$ — the field reconstructed using only shells $j < J$, plotted bit-split so that 2-adically nearby integers land in nearby pixels. These are the "orbital approximations".
- **Dyadic spectrograms** — heatmap of $|c_{j, a}|^2$ on the $(j, a)$ triangle.

## Hypotheses (see spec for falsifiability)

- **H1 — Sturmian shell concentration.** Does $E_j(\chi)$ depart from the shuffled-$\chi$ null band at shells related to the $\log_2 3$ Beatty rhythm?
- **H2 — Dropping-class fingerprint.** Do different $\mathbf{1}_{D_k}$ have distinguishable normalized spectra?
- **H3 — $T$ is not Haar-sparse.** Stopping time should spread energy across many shells.

## Notes on interpretation

- Shell $j = 0$ is the coarsest wavelet (one wavelet, support of size $N$). Shell $j = K - 1$ is finest (support of size 2). The bit-split layout puts shell-$j$ structure as $2^j$-period stripes in either bit-half axis.
- Off-Beatty values of $n$ get $\chi(n) = 0$. This adds energy to *no* specific shell — it broadens any spectral peak.
```

- [ ] **Step 2: Commit**

```bash
git add "docs/Explorations/Kozyrev Orbital Spectrum.md"
git commit -m "docs: Kozyrev Orbital Spectrum exploration note"
```

---

## Self-Review

**1. Spec coverage:**
- Operator + basis (Vladimirov / Kozyrev / Haar) → Tasks 3–6.
- Input fields $\chi$, $\mathbf{1}_{D_k}$, $T$ → Task 7.
- Shell-energy spectra → Task 6 + 8.
- Partial reconstructions $f_J$ → Task 5 + 8.
- Dyadic spectrogram → Task 6 + 8.
- Shuffle null band → Task 7 helper + Task 8.
- Refactor: lift helpers to `utils.py` → Task 1; migrate consumer script → Task 2.
- Tests (Parseval, round-trip, single-ball-style, orthonormality, partial-reconstruction monotonicity) → Tasks 3–6.
- Exploration note → Task 9.
- Output PNG `data/collatz_kozyrev_spectrum.png` → Task 8.

All spec sections accounted for.

**2. Placeholder scan:** none — every code step shows the code; every test step shows the asserts; every commit step gives the command.

**3. Type consistency:** `haar_forward` returns `(float, np.ndarray)` in Task 4 and is consumed that way in Tasks 5, 6, 7, 8. `coeffs` length is always $N - 1$. `shell_energies(coeffs, K)` shape is `(K,)`. `coefficient_grid(coeffs, K)` shape is `(K, 2^{K-1})`. `idx(j, a) = 2^j - 1 + a` is used consistently. `depth_cutoff` semantics match: shells `j < J` are kept; the test at `J = 0` returns the mean-projection (constant), and at `J = K` returns the exact original.
