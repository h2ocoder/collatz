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
