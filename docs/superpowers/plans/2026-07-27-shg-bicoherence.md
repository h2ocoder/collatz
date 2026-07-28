# SHG Bicoherence Probe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Detect (or refute) SHG-like quadratic phase coupling in the Collatz +1 wobble via ensemble bicoherence with two independent nulls.

**Architecture:** A small library module `collatz/bispectrum.py` holds the testable numerics (wobble extraction, window standardization, bicoherence estimator, phase-randomized surrogates, AR fit/simulate). A driver script `scripts/collatz_shg_bicoherence.py` runs startup self-validation, builds the seed ensemble, computes observed bicoherence plus two null bands, and writes a three-panel figure to `data/`. This mirrors the existing `collatz/walsh.py` + `scripts/collatz_gear_spectrum.py` split.

**Tech Stack:** Python 3.12 (existing `.venv`), numpy, matplotlib (Agg), pytest.

**Spec:** `docs/superpowers/specs/2026-07-27-shg-bicoherence-design.md` — read it first; the interpretation contract and null definitions live there.

## Global Constraints

- Field under test: per-step wobble increment `w_k = log_6(1 + 1/(3 x_k))` at each odd orbit value `x_k` (increments, NOT the accumulated walk).
- Ensemble: odd seeds in `[50001, 150001)`; first `L = 32` odd steps per surviving seed; skipped fraction must be logged.
- Windows demeaned and standardized to unit variance before any spectral step.
- Bicoherence normalization: `b^2 = |<X1 X2 X3*>|^2 / (<|X1 X2|^2> <|X3|^2>)`, principal triangle `1 <= f2 <= f1`, `f1 + f2 <= L/2` (DC excluded).
- Two nulls, both 95% bands: phase-randomized surrogates and matched AR(5) simulation.
- Startup self-validation (QPC positive + negative control) must print pass/fail and abort on fail.
- Output figure: `data/collatz_shg_bicoherence.png`, matplotlib Agg backend, style matching `scripts/collatz_gear_spectrum.py` (module constants in CAPS, fixed RNG seed, `dpi=140`, `print("wrote", OUT)`).
- Run commands with the project venv: `.venv/bin/python` (this repo's CLAUDE.md shows a Windows-style path; on this Darwin machine use `.venv/bin/python`; verify with `ls .venv/bin/python` and fall back to `.venv/Scripts/python.exe` if absent).

---

### Task 1: Wobble extraction + window standardization (`collatz/bispectrum.py`)

**Files:**
- Create: `collatz/bispectrum.py`
- Create: `tests/test_bispectrum.py`

**Interfaces:**
- Consumes: `collatz.core.orbit(n) -> list[int]` (full orbit from n down to 1, inclusive).
- Produces:
  - `wobble_increments(seed: int) -> np.ndarray` — float64 array of `w_k = log(1 + 1/(3*x_k)) / log(6)` for every odd value `x_k > 1` in `orbit(seed)`, in orbit order (the trailing 1 is excluded; the seed itself is included when odd).
  - `standardize_windows(windows: np.ndarray) -> np.ndarray` — input shape `(M, L)`; per-row demean and divide by per-row std (`ddof=0`); raises `ValueError` if any row std is 0.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_bispectrum.py`:

```python
"""Tests for collatz.bispectrum — bicoherence probe of the +1 wobble."""

import numpy as np
import pytest

from collatz.bispectrum import standardize_windows, wobble_increments


def test_wobble_increments_seed_27():
    """w_k matches the log_6(1 + 1/(3 x_k)) formula at every odd orbit value."""
    from collatz.core import orbit

    seq = orbit(27)
    odds = [x for x in seq if x % 2 == 1 and x > 1]
    w = wobble_increments(27)
    assert w.shape == (len(odds),)
    expected = np.log(1.0 + 1.0 / (3.0 * np.array(odds, dtype=float))) / np.log(6.0)
    np.testing.assert_allclose(w, expected, rtol=1e-12)
    # first odd value is the seed itself
    assert odds[0] == 27


def test_wobble_increments_power_of_two_is_empty():
    """Orbit of 16 has no odd values > 1 — no wobble kicks at all."""
    w = wobble_increments(16)
    assert w.shape == (0,)


def test_standardize_windows_zero_mean_unit_variance():
    rng = np.random.default_rng(41)
    win = rng.standard_normal((5, 32)) * 3.0 + 7.0
    z = standardize_windows(win)
    assert z.shape == (5, 32)
    np.testing.assert_allclose(z.mean(axis=1), 0.0, atol=1e-12)
    np.testing.assert_allclose(z.std(axis=1), 1.0, rtol=1e-12)


def test_standardize_windows_rejects_constant_row():
    win = np.ones((2, 8))
    with pytest.raises(ValueError):
        standardize_windows(win)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_bispectrum.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'collatz.bispectrum'`

- [ ] **Step 3: Write the implementation**

Create `collatz/bispectrum.py`:

```python
"""Bicoherence machinery for the SHG probe of the Collatz +1 wobble.

Second harmonic generation analogy: the odd step T(x) = (3x+1)/2 is affine,
and the "+1" breaks the scale symmetry of the pure x -> 3x/2 rotation
(alpha = log_6 3) exactly the way a non-centrosymmetric crystal's chi^(2)
breaks inversion symmetry. The signal-processing fingerprint of a chi^(2)
process is quadratic phase coupling: power at f1 + f2 whose phase is locked
to the sum of the phases at f1 and f2. The detector is the bispectrum

    B(f1, f2) = <X(f1) X(f2) X*(f1 + f2)>

and its normalized form, bicoherence b^2 in [0, 1]. Linear and Gaussian
processes have zero bispectrum; the power spectrum is blind to this because
it discards phase.

Field under test: the per-step wobble increment w_k = log_6(1 + 1/(3 x_k))
at each odd orbit value x_k -- the exact phase kick the +1 injects into the
alpha-rotation. Increments, not the accumulated walk: the integrated signal
is non-stationary and biases bispectrum estimation.

See docs/superpowers/specs/2026-07-27-shg-bicoherence-design.md.
"""
from __future__ import annotations

import numpy as np

from collatz.core import orbit

LOG6 = np.log(6.0)


def wobble_increments(seed: int) -> np.ndarray:
    """Per-step wobble kicks w_k = log_6(1 + 1/(3 x_k)) along orbit(seed).

    One entry per odd value x_k > 1 in the orbit (the seed itself included
    when odd, the terminal 1 excluded), in orbit order.
    """
    odds = np.array([x for x in orbit(seed) if x % 2 == 1 and x > 1], dtype=float)
    if odds.size == 0:
        return np.empty(0)
    return np.log1p(1.0 / (3.0 * odds)) / LOG6


def standardize_windows(windows: np.ndarray) -> np.ndarray:
    """Demean and scale each row of `windows` (shape (M, L)) to unit variance.

    The wobble amplitude scales like 1/x_k, so raw windows mix amplitude with
    phase structure; standardization makes the probe a pure phase question.
    """
    w = np.asarray(windows, dtype=np.float64)
    mu = w.mean(axis=1, keepdims=True)
    sd = w.std(axis=1, keepdims=True)
    if np.any(sd == 0.0):
        raise ValueError("constant window: cannot standardize")
    return (w - mu) / sd
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_bispectrum.py -v`
Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
git add collatz/bispectrum.py tests/test_bispectrum.py
git commit -m "feat(bispectrum): wobble increments + window standardization"
```

---

### Task 2: Bicoherence estimator with QPC controls

**Files:**
- Modify: `collatz/bispectrum.py` (append)
- Modify: `tests/test_bispectrum.py` (append)

**Interfaces:**
- Consumes: `standardize_windows` from Task 1 (tests only).
- Produces:
  - `bicoherence(windows: np.ndarray) -> np.ndarray` — input shape `(M, L)` with `L` even; returns `b2` of shape `(L//2 + 1, L//2 + 1)`, `b2[f1, f2]` filled on the principal triangle `1 <= f2 <= f1`, `f1 + f2 <= L//2`, `np.nan` elsewhere. Frequencies are rFFT bin indices (bin f ↔ normalized frequency f/L).
  - `qpc_ensemble(n_windows: int, length: int, f0_bin: int, coupled: bool, rng: np.random.Generator) -> np.ndarray` — synthetic control ensemble, shape `(n_windows, length)`: cos at bin `f0_bin` with per-window uniform random phase `phi`, plus 0.5·cos at bin `2*f0_bin` with phase `2*phi` when `coupled=True` (locked — the SHG signature) or an independent random phase when `coupled=False`, plus Gaussian noise of sd 0.3.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_bispectrum.py`:

```python
from collatz.bispectrum import bicoherence, qpc_ensemble


def test_bicoherence_shape_and_triangle():
    rng = np.random.default_rng(42)
    b2 = bicoherence(rng.standard_normal((50, 32)))
    assert b2.shape == (17, 17)
    assert np.isnan(b2[0, 0])          # DC excluded
    assert np.isnan(b2[3, 5])          # f2 > f1 excluded
    assert np.isnan(b2[16, 1])         # f1 + f2 > 16 excluded
    tri = ~np.isnan(b2)
    assert np.all(b2[tri] >= 0.0) and np.all(b2[tri] <= 1.0 + 1e-9)


def test_bicoherence_qpc_positive_control():
    """Phase-locked f0 + 2*f0 lights up the diagonal at (f0, f0)."""
    rng = np.random.default_rng(43)
    win = qpc_ensemble(n_windows=200, length=64, f0_bin=8, coupled=True, rng=rng)
    b2 = bicoherence(win)
    assert b2[8, 8] > 0.8
    tri = ~np.isnan(b2)
    background = np.nanmedian(b2[tri])
    assert background < 0.2


def test_bicoherence_qpc_negative_control():
    """Same spectrum, unlocked 2*f0 phase: the diagonal stays at the floor."""
    rng = np.random.default_rng(44)
    win = qpc_ensemble(n_windows=200, length=64, f0_bin=8, coupled=False, rng=rng)
    b2 = bicoherence(win)
    assert b2[8, 8] < 0.2


def test_bicoherence_gaussian_noise_floor():
    """Pure Gaussian noise: bicoherence ~ O(1/M) everywhere on the triangle."""
    rng = np.random.default_rng(45)
    b2 = bicoherence(rng.standard_normal((500, 32)))
    assert np.nanmax(b2) < 0.15
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_bispectrum.py -v`
Expected: 4 new FAIL with `ImportError: cannot import name 'bicoherence'`; 4 old PASS

- [ ] **Step 3: Write the implementation**

Append to `collatz/bispectrum.py`:

```python
def bicoherence(windows: np.ndarray) -> np.ndarray:
    """Ensemble bicoherence b^2(f1, f2) of real windows, shape (M, L).

    b^2 = |<X(f1) X(f2) X*(f1+f2)>|^2 / (<|X(f1) X(f2)|^2> <|X(f1+f2)|^2>)

    with the ensemble average over the M windows. Filled on the principal
    triangle 1 <= f2 <= f1, f1 + f2 <= L//2 (DC excluded); NaN elsewhere.
    b^2 = 1 iff the phase of X(f1+f2) is perfectly locked to the sum of the
    phases at f1 and f2 across the whole ensemble -- the chi^(2) signature.
    """
    w = np.asarray(windows, dtype=np.float64)
    M, L = w.shape
    if L % 2 != 0:
        raise ValueError("window length must be even")
    K = L // 2
    X = np.fft.rfft(w, axis=1)  # (M, K+1)
    b2 = np.full((K + 1, K + 1), np.nan)
    for f1 in range(1, K + 1):
        for f2 in range(1, f1 + 1):
            f3 = f1 + f2
            if f3 > K:
                continue
            prod = X[:, f1] * X[:, f2]
            num = np.abs(np.mean(prod * np.conj(X[:, f3]))) ** 2
            den = np.mean(np.abs(prod) ** 2) * np.mean(np.abs(X[:, f3]) ** 2)
            b2[f1, f2] = num / den if den > 0 else 0.0
    return b2


def qpc_ensemble(
    n_windows: int,
    length: int,
    f0_bin: int,
    coupled: bool,
    rng: np.random.Generator,
) -> np.ndarray:
    """Synthetic quadratic-phase-coupling control ensemble.

    Each window: cos at bin f0 with random phase phi, plus 0.5 cos at bin
    2*f0 whose phase is 2*phi (coupled=True: the SHG-locked case) or an
    independent draw (coupled=False: same power spectrum, no coupling),
    plus Gaussian noise. The estimator must separate the two.
    """
    t = np.arange(length)
    phi = rng.uniform(0.0, 2.0 * np.pi, size=(n_windows, 1))
    psi = 2.0 * phi if coupled else rng.uniform(0.0, 2.0 * np.pi, size=(n_windows, 1))
    f0 = f0_bin / length
    win = (
        np.cos(2.0 * np.pi * f0 * t + phi)
        + 0.5 * np.cos(2.0 * np.pi * 2.0 * f0 * t + psi)
        + 0.3 * rng.standard_normal((n_windows, length))
    )
    return win
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_bispectrum.py -v`
Expected: 8 PASS

- [ ] **Step 5: Commit**

```bash
git add collatz/bispectrum.py tests/test_bispectrum.py
git commit -m "feat(bispectrum): ensemble bicoherence estimator + QPC controls"
```

---

### Task 3: Phase-randomized surrogates

**Files:**
- Modify: `collatz/bispectrum.py` (append)
- Modify: `tests/test_bispectrum.py` (append)

**Interfaces:**
- Consumes: `bicoherence`, `qpc_ensemble` from Task 2 (tests only).
- Produces:
  - `phase_randomize(windows: np.ndarray, rng: np.random.Generator) -> np.ndarray` — same shape as input; each row keeps its rFFT magnitudes exactly (DC and Nyquist bins untouched, interior bins get fresh uniform phases). Power spectrum preserved, bicoherence destroyed.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_bispectrum.py`:

```python
from collatz.bispectrum import phase_randomize


def test_phase_randomize_preserves_power_spectrum():
    rng = np.random.default_rng(46)
    win = rng.standard_normal((20, 32))
    surr = phase_randomize(win, rng)
    assert surr.shape == win.shape
    np.testing.assert_allclose(
        np.abs(np.fft.rfft(surr, axis=1)),
        np.abs(np.fft.rfft(win, axis=1)),
        rtol=1e-9,
        atol=1e-9,
    )
    # and it actually changed the signal
    assert not np.allclose(surr, win)


def test_phase_randomize_destroys_qpc():
    """Surrogates of the coupled ensemble drop to the noise floor at (f0, f0)."""
    rng = np.random.default_rng(47)
    win = qpc_ensemble(n_windows=200, length=64, f0_bin=8, coupled=True, rng=rng)
    assert bicoherence(win)[8, 8] > 0.8
    surr = phase_randomize(win, rng)
    assert bicoherence(surr)[8, 8] < 0.2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_bispectrum.py -v`
Expected: 2 new FAIL with `ImportError: cannot import name 'phase_randomize'`; 8 old PASS

- [ ] **Step 3: Write the implementation**

Append to `collatz/bispectrum.py`:

```python
def phase_randomize(windows: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Phase-randomized surrogate of each row: same rFFT magnitudes, fresh
    uniform phases on the interior bins (DC and Nyquist stay real).

    This preserves each window's power spectrum exactly while destroying all
    bispectral phase relations -- the null of "everything the power spectrum
    already knows."
    """
    w = np.asarray(windows, dtype=np.float64)
    M, L = w.shape
    X = np.fft.rfft(w, axis=1)
    theta = rng.uniform(0.0, 2.0 * np.pi, size=X.shape)
    theta[:, 0] = 0.0
    if L % 2 == 0:
        theta[:, -1] = 0.0
    return np.fft.irfft(np.abs(X) * np.exp(1j * theta), n=L, axis=1)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_bispectrum.py -v`
Expected: 10 PASS

- [ ] **Step 5: Commit**

```bash
git add collatz/bispectrum.py tests/test_bispectrum.py
git commit -m "feat(bispectrum): phase-randomized surrogate null"
```

---

### Task 4: Matched AR linear null

**Files:**
- Modify: `collatz/bispectrum.py` (append)
- Modify: `tests/test_bispectrum.py` (append)

**Interfaces:**
- Consumes: nothing from earlier tasks (self-contained numerics).
- Produces:
  - `fit_ar(windows: np.ndarray, order: int) -> tuple[np.ndarray, float]` — Yule-Walker fit on the window ensemble: per-window biased autocovariances up to lag `order`, averaged across windows, Toeplitz solve. Returns `(phi, sigma)` with `phi` shape `(order,)` (convention `x_t = sum_i phi[i] * x_{t-1-i} + sigma * eps_t`) and `sigma > 0` the innovation sd.
  - `simulate_ar(phi: np.ndarray, sigma: float, n_windows: int, length: int, rng: np.random.Generator, burnin: int = 200) -> np.ndarray` — shape `(n_windows, length)` Gaussian-innovation AR simulation, first `burnin` samples of each row discarded.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_bispectrum.py`:

```python
from collatz.bispectrum import fit_ar, simulate_ar


def test_fit_ar_recovers_known_ar2():
    """Round-trip: simulate AR(2) with known phi, refit, recover within 0.05."""
    rng = np.random.default_rng(48)
    phi_true = np.array([0.5, -0.3])
    win = simulate_ar(phi_true, sigma=1.0, n_windows=400, length=256, rng=rng)
    phi_hat, sigma_hat = fit_ar(win, order=2)
    np.testing.assert_allclose(phi_hat, phi_true, atol=0.05)
    assert 0.9 < sigma_hat < 1.1


def test_simulate_ar_shape_and_stationarity():
    rng = np.random.default_rng(49)
    win = simulate_ar(np.array([0.5, -0.3]), sigma=1.0, n_windows=10, length=64, rng=rng)
    assert win.shape == (10, 64)
    # burned-in AR(2) with these coefficients has sd near
    # sqrt((1-phi2)/((1+phi2)((1-phi2)^2-phi1^2))) ~ 1.06; loose check
    assert 0.7 < win.std() < 1.5


def test_ar_null_of_gaussian_ar_process_has_flat_bicoherence():
    """A linear AR process must NOT trigger the detector (that is the point)."""
    rng = np.random.default_rng(50)
    win = simulate_ar(np.array([0.6]), sigma=1.0, n_windows=500, length=32, rng=rng)
    assert np.nanmax(bicoherence(win)) < 0.15
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_bispectrum.py -v`
Expected: 3 new FAIL with `ImportError: cannot import name 'fit_ar'`; 10 old PASS

- [ ] **Step 3: Write the implementation**

Append to `collatz/bispectrum.py`:

```python
def fit_ar(windows: np.ndarray, order: int) -> tuple[np.ndarray, float]:
    """Yule-Walker AR(order) fit to a window ensemble.

    Biased per-window autocovariances up to `order` lags, averaged over
    windows, then the Toeplitz normal equations. Returns (phi, sigma):
    x_t = sum_i phi[i] x_{t-1-i} + sigma eps_t.
    """
    w = np.asarray(windows, dtype=np.float64)
    w = w - w.mean(axis=1, keepdims=True)
    M, L = w.shape
    if order >= L:
        raise ValueError("order must be < window length")
    acov = np.zeros(order + 1)
    for lag in range(order + 1):
        acov[lag] = np.mean(np.sum(w[:, : L - lag] * w[:, lag:], axis=1) / L)
    # Toeplitz normal equations, solved with plain numpy (scipy not in venv).
    T = acov[np.abs(np.subtract.outer(np.arange(order), np.arange(order)))]
    phi = np.linalg.solve(T, acov[1 : order + 1])
    sigma2 = acov[0] - phi @ acov[1 : order + 1]
    return phi, float(np.sqrt(max(sigma2, 1e-15)))


def simulate_ar(
    phi: np.ndarray,
    sigma: float,
    n_windows: int,
    length: int,
    rng: np.random.Generator,
    burnin: int = 200,
) -> np.ndarray:
    """Simulate Gaussian-innovation AR windows: shape (n_windows, length)."""
    p = len(phi)
    total = length + burnin
    x = np.zeros((n_windows, total))
    eps = sigma * rng.standard_normal((n_windows, total))
    for t in range(total):
        for i in range(p):
            if t - 1 - i >= 0:
                x[:, t] += phi[i] * x[:, t - 1 - i]
        x[:, t] += eps[:, t]
    return x[:, burnin:]
```

Note: scipy is NOT in the venv (verified 2026-07-27), hence the plain-numpy Toeplitz solve above — do not add a scipy dependency.

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_bispectrum.py -v`
Expected: 13 PASS

- [ ] **Step 5: Commit**

```bash
git add collatz/bispectrum.py tests/test_bispectrum.py
git commit -m "feat(bispectrum): Yule-Walker AR fit + simulation for the linear null"
```

---

### Task 5: Driver script, figure, and the actual experiment

**Files:**
- Create: `scripts/collatz_shg_bicoherence.py`
- Output: `data/collatz_shg_bicoherence.png`

**Interfaces:**
- Consumes: everything from Tasks 1-4 (`wobble_increments`, `standardize_windows`, `bicoherence`, `qpc_ensemble`, `phase_randomize`, `fit_ar`, `simulate_ar`).
- Produces: the figure and a console summary; no downstream code consumers.

- [ ] **Step 1: Write the script**

Create `scripts/collatz_shg_bicoherence.py`:

```python
# scripts/collatz_shg_bicoherence.py
"""SHG probe: does the Collatz +1 wobble generate second harmonics?

In nonlinear optics, a chi^(2) medium (inversion symmetry broken) converts
light at frequency f into phase-locked light at 2f -- second harmonic
generation. The signal fingerprint is quadratic phase coupling, detected by
bicoherence: b^2(f1, f2) ~ 1 when the phase at f1+f2 is locked to the sum of
the phases at f1 and f2, and ~ 0 for any linear or Gaussian process. Crucially
the power spectrum is blind to this (it discards phase): the gear-spectrum
result "mod-q bursts are white" leaves bicoherence completely open.

Collatz mapping: the odd step T(x) = (3x+1)/2 is affine; the +1 is the
inversion-symmetry breaker of the pure rotation x -> 3x/2 (alpha = log_6 3).
Field under test: the per-step wobble kick w_k = log_6(1 + 1/(3 x_k)), one
per odd orbit value, first L=32 kicks per seed, standardized per window.

Interpretation contract (docs/superpowers/specs/2026-07-27-shg-bicoherence-design.md):
  - diagonal b^2(f, f) above BOTH null bands  => the +1 acts as a chi^(2)
    medium: quadratic phase coupling / harmonic generation along orbits.
  - flat at the null level => the wobble phases mix linearly, consistent
    with the gear-spectrum whiteness result.

Nulls (both 95% bands over R ensembles):
  1. phase-randomized surrogates -- exact same power spectra, all bispectral
     phase relations destroyed by construction.
  2. matched AR(5) -- best linear Gaussian model of the wobble, simulated at
     the same ensemble size.

Startup self-check: the estimator must light up on a synthetic phase-coupled
pair (positive control) and stay at the floor when the 2f phase is unlocked
(negative control); the run aborts if either fails.

Output:
    data/collatz_shg_bicoherence.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from collatz.bispectrum import (  # noqa: E402
    bicoherence,
    fit_ar,
    phase_randomize,
    qpc_ensemble,
    simulate_ar,
    standardize_windows,
    wobble_increments,
)

SEED_LO, SEED_HI = 50001, 150001   # odd seeds in [lo, hi)
L = 32                              # odd steps per window
AR_ORDER = 5
N_NULL = 100                        # null ensembles per falsifier
RNG = np.random.default_rng(20260727)  # fixed seed: reproducible nulls
OUT = Path(__file__).resolve().parent.parent / "data" / "collatz_shg_bicoherence.png"


def self_check() -> None:
    """Positive + negative QPC control; abort the run if the estimator fails."""
    rng = np.random.default_rng(7)
    pos = bicoherence(qpc_ensemble(200, 64, 8, coupled=True, rng=rng))[8, 8]
    neg = bicoherence(qpc_ensemble(200, 64, 8, coupled=False, rng=rng))[8, 8]
    ok = pos > 0.8 and neg < 0.2
    print(f"self-check: coupled b2={pos:.3f} (>0.8), uncoupled b2={neg:.3f} (<0.2)"
          f" -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        sys.exit(1)


def build_ensemble() -> np.ndarray:
    """Standardized (M, L) wobble windows; logs the skipped-seed fraction."""
    windows, skipped, total = [], 0, 0
    for seed in range(SEED_LO, SEED_HI, 2):
        total += 1
        w = wobble_increments(seed)
        if w.size < L:
            skipped += 1
            continue
        windows.append(w[:L])
    print(f"ensemble: {len(windows)} windows of L={L} odd steps "
          f"({skipped}/{total} seeds skipped = {skipped / total:.1%})")
    return standardize_windows(np.array(windows))


def null_band(estimates: np.ndarray) -> np.ndarray:
    """Pointwise 95th percentile across null ensembles (axis 0), NaN-safe."""
    return np.nanpercentile(estimates, 95.0, axis=0)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    self_check()
    win = build_ensemble()
    M = win.shape[0]

    b2_obs = bicoherence(win)
    K = L // 2

    # Null 1: phase-randomized surrogates of the real windows.
    surr = np.array([bicoherence(phase_randomize(win, RNG)) for _ in range(N_NULL)])
    # Null 2: matched AR(AR_ORDER) linear model at the same ensemble size.
    phi, sigma = fit_ar(win, AR_ORDER)
    print(f"AR({AR_ORDER}) fit: phi={np.round(phi, 3)}, sigma={sigma:.3f}")
    ar = np.array([
        bicoherence(standardize_windows(simulate_ar(phi, sigma, M, L, RNG)))
        for _ in range(N_NULL)
    ])
    surr_band, ar_band = null_band(surr), null_band(ar)

    # Console verdict: observed peak vs the surrogate max-statistic distribution.
    tri = ~np.isnan(b2_obs)
    peak = float(np.nanmax(b2_obs))
    f1p, f2p = np.unravel_index(int(np.nanargmax(np.where(tri, b2_obs, -1.0))), b2_obs.shape)
    surr_max = np.nanmax(surr, axis=(1, 2))
    pctile = float(np.mean(peak > surr_max)) * 100.0
    print(f"peak b2 = {peak:.4f} at (f1, f2) = ({f1p}, {f2p}) "
          f"[normalized f = ({f1p / L:.3f}, {f2p / L:.3f})]")
    print(f"peak percentile vs surrogate max-distribution: {pctile:.0f}%")

    diag = np.arange(1, K // 2 + 1)          # (f, f) with 2f <= K
    freqs = diag / L

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))

    ax = axes[0]
    im = ax.imshow(b2_obs.T, origin="lower", cmap="viridis", aspect="equal",
                   extent=(-0.5, K + 0.5, -0.5, K + 0.5))
    ax.plot([1, K // 2], [1, K // 2], color="w", lw=0.8, ls=":")
    ax.set_xlabel("f1 (rFFT bin)")
    ax.set_ylabel("f2 (rFFT bin)")
    ax.set_title(f"bicoherence b$^2$(f1, f2), M={M} windows")
    fig.colorbar(im, ax=ax, shrink=0.85)

    ax = axes[1]
    ax.plot(freqs, b2_obs[diag, diag], color="crimson", lw=1.8, marker="o",
            ms=3.5, label="observed b$^2$(f, f)")
    ax.plot(freqs, surr_band[diag, diag], color="0.4", lw=1.4, ls="--",
            label="surrogate null (95%)")
    ax.plot(freqs, ar_band[diag, diag], color="darkorange", lw=1.4, ls="-.",
            label=f"AR({AR_ORDER}) null (95%)")
    ax.set_xlabel("normalized frequency f (cycles / odd step)")
    ax.set_ylabel("b$^2$")
    ax.set_title("the SHG channel: diagonal (f, f) -> 2f")
    ax.legend(fontsize=8)

    ax = axes[2]
    power = np.mean(np.abs(np.fft.rfft(win, axis=1)) ** 2, axis=0) / L
    ax.plot(np.arange(K + 1) / L, power, color="steelblue", lw=1.6)
    ax.set_xlabel("normalized frequency f (cycles / odd step)")
    ax.set_ylabel("avg power")
    ax.set_title("ensemble power spectrum of standardized w_k")

    fig.suptitle(
        "SHG probe: does the +1 wobble quadratically phase-couple (chi^(2)) "
        "or mix linearly?",
        fontsize=13, y=0.99,
    )
    plt.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT, dpi=140)
    plt.close(fig)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the full test suite (regression gate)**

Run: `.venv/bin/python -m pytest tests/ -q`
Expected: all PASS (13 bispectrum + existing suite)

- [ ] **Step 3: Run the experiment**

Run: `.venv/bin/python scripts/collatz_shg_bicoherence.py`
Expected console output, in order:
- `self-check: ... -> PASS` (abort here means Task 2's estimator regressed)
- ensemble line with a skipped fraction well under 50% (if most seeds are skipped, the L=32 cut is too aggressive for this seed range — flag it, do not silently proceed)
- AR fit line, peak line, percentile line, `wrote .../collatz_shg_bicoherence.png`

Runtime expectation: a few minutes (50k orbits + 200 null bicoherence passes). If it exceeds ~15 minutes, stop and profile rather than waiting.

- [ ] **Step 4: Inspect the figure**

Open `data/collatz_shg_bicoherence.png` (Read tool). Check: heatmap triangle populated, diagonal panel shows observed curve plus two null bands, power-spectrum panel non-degenerate. Record the observed verdict (above / at the null bands) for Task 6.

- [ ] **Step 5: Commit**

```bash
git add scripts/collatz_shg_bicoherence.py data/collatz_shg_bicoherence.png
git commit -m "feat(scripts): SHG bicoherence probe of the +1 wobble + figure"
```

---

### Task 6: Exploration note

**Files:**
- Create: `docs/Explorations/SHG Bicoherence of the Wobble.md`

**Interfaces:**
- Consumes: the Task 5 console numbers (M, skip fraction, peak b², peak location, percentile) and figure verdict. This task CANNOT be written before Task 5 runs.

- [ ] **Step 1: Write the note**

Follow the house style of `docs/Explorations/Gear Spectrum and Wobble Channels.md` (premise -> method -> result -> verdict, `[[wikilinks]]`, tables where they pay). Required content — fill the bracketed slots with the real Task 5 numbers, and write the verdict the data supports, not the one that is exciting:

```markdown
# SHG Bicoherence of the Wobble

**Premise.** In nonlinear optics a chi^(2) medium — one with broken inversion
symmetry — converts light at f into phase-locked light at 2f (second harmonic
generation). The Collatz odd step `T(x) = (3x+1)/2` is affine: the `+1` is
precisely the symmetry-breaker of the pure rotation `x -> 3x/2`
(`alpha = log_6 3`). The [[Collatz as a Quasicrystal]] note treated the wobble
as *passive* disorder (Debye-Waller damping). This probe asks whether it is
*active*: does the wobble field quadratically phase-couple, `(f, f) -> 2f`,
in a way no linear process can?

**Why the power spectrum cannot answer this.** Bicoherence measures phase
locking between `f1`, `f2`, and `f1+f2`; the periodogram discards phase
entirely. The [[Gear Spectrum and Wobble Channels]] whiteness result
therefore leaves this question fully open.

**Method** (`scripts/collatz_shg_bicoherence.py`). Ensemble bicoherence of
the per-step wobble kicks `w_k = log_6(1 + 1/(3 x_k))`, first L=32 odd steps
of [M] orbits (odd seeds in `[50001, 150001)`, [skip]% skipped),
standardized per window. Estimator validated on synthetic phase-coupled
controls at startup. Two falsifiers, 95% bands over 100 ensembles each:
phase-randomized surrogates (same spectra, coupling destroyed) and a matched
AR(5) Gaussian null.

**Result.** Peak `b^2 = [peak]` at `(f1, f2) = [(loc)]`, at the [pct]%
percentile of the surrogate max-distribution. [Describe the diagonal panel
against both bands.]

**Verdict.** [One of: "The wobble is a chi^(2) medium: ... " with the
surviving frequencies and what to probe next (phase-matching / conversion-
efficiency growth, mod-q fields, parity word) — or "No quadratic phase
coupling: the wobble phases mix linearly, extending the gear-spectrum
whiteness from power to bispectral phase. The +1 breaks the symmetry but
generates no harmonics at this L and ensemble."]

![[collatz_shg_bicoherence.png]]
```

- [ ] **Step 2: Verify the note renders and numbers match**

Re-read the note; cross-check every bracketed number against the Task 5 console output verbatim. Check the image embed filename matches the actual file in `data/`.

- [ ] **Step 3: Commit**

```bash
git add "docs/Explorations/SHG Bicoherence of the Wobble.md"
git commit -m "docs(exploration): SHG bicoherence probe of the +1 wobble"
```
