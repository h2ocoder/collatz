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
