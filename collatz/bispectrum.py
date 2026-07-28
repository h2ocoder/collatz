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
