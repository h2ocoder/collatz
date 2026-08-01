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


def test_bicoherence_shape_and_triangle():
    from collatz.bispectrum import bicoherence
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
    from collatz.bispectrum import bicoherence, qpc_ensemble
    rng = np.random.default_rng(43)
    win = qpc_ensemble(n_windows=200, length=64, f0_bin=8, coupled=True, rng=rng)
    b2 = bicoherence(win)
    assert b2[8, 8] > 0.8
    tri = ~np.isnan(b2)
    background = np.nanmedian(b2[tri])
    assert background < 0.2


def test_bicoherence_qpc_negative_control():
    """Same spectrum, unlocked 2*f0 phase: the diagonal stays at the floor."""
    from collatz.bispectrum import bicoherence, qpc_ensemble
    rng = np.random.default_rng(44)
    win = qpc_ensemble(n_windows=200, length=64, f0_bin=8, coupled=False, rng=rng)
    b2 = bicoherence(win)
    assert b2[8, 8] < 0.2


def test_bicoherence_gaussian_noise_floor():
    """Pure Gaussian noise: bicoherence ~ O(1/M) everywhere on the triangle."""
    from collatz.bispectrum import bicoherence
    rng = np.random.default_rng(45)
    b2 = bicoherence(rng.standard_normal((500, 32)))
    assert np.nanmax(b2) < 0.15


def test_phase_randomize_preserves_power_spectrum():
    from collatz.bispectrum import phase_randomize
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
    from collatz.bispectrum import phase_randomize, bicoherence, qpc_ensemble
    rng = np.random.default_rng(47)
    win = qpc_ensemble(n_windows=200, length=64, f0_bin=8, coupled=True, rng=rng)
    assert bicoherence(win)[8, 8] > 0.8
    surr = phase_randomize(win, rng)
    assert bicoherence(surr)[8, 8] < 0.2


def test_fit_ar_recovers_known_ar2():
    """Round-trip: simulate AR(2) with known phi, refit, recover within 0.05."""
    from collatz.bispectrum import fit_ar, simulate_ar

    rng = np.random.default_rng(48)
    phi_true = np.array([0.5, -0.3])
    win = simulate_ar(phi_true, sigma=1.0, n_windows=400, length=256, rng=rng)
    phi_hat, sigma_hat = fit_ar(win, order=2)
    np.testing.assert_allclose(phi_hat, phi_true, atol=0.05)
    assert 0.9 < sigma_hat < 1.1


def test_simulate_ar_shape_and_stationarity():
    from collatz.bispectrum import simulate_ar

    rng = np.random.default_rng(49)
    win = simulate_ar(np.array([0.5, -0.3]), sigma=1.0, n_windows=10, length=64, rng=rng)
    assert win.shape == (10, 64)
    # burned-in AR(2) with these coefficients has sd near
    # sqrt((1-phi2)/((1+phi2)((1-phi2)^2-phi1^2))) ~ 1.06; loose check
    assert 0.7 < win.std() < 1.5


def test_ar_null_of_gaussian_ar_process_has_flat_bicoherence():
    """A linear AR process must NOT trigger the detector (that is the point)."""
    from collatz.bispectrum import simulate_ar, bicoherence

    rng = np.random.default_rng(50)
    win = simulate_ar(np.array([0.6]), sigma=1.0, n_windows=500, length=32, rng=rng)
    assert np.nanmax(bicoherence(win)) < 0.15
