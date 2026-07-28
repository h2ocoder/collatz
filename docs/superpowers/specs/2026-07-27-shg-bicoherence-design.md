# Design: Collatz SHG probe via ensemble bicoherence

**Date:** 2026-07-27
**Status:** Approved

## Motivation

Second harmonic generation (SHG) in nonlinear optics: a medium with a
nonzero second-order susceptibility chi^(2) converts light at frequency
omega into light at 2*omega. Two structural facts make it a probe rather
than a curiosity: chi^(2) vanishes identically in centrosymmetric media
(SHG detects broken inversion symmetry), and the signal-processing
fingerprint of a chi^(2) process is **quadratic phase coupling** — power
at 2f whose phase is locked to twice the phase at f. The standard
detector is the bispectrum B(f1, f2) = <X(f1) X(f2) X*(f1+f2)> and its
normalized form, bicoherence. Linear and Gaussian processes have zero
bispectrum; the power spectrum is blind to this because it discards
phase.

Collatz mapping: the odd step T(x) = (3x+1)/2 is affine, and the "+1" is
the inversion-symmetry breaker. In base-6 log coordinates the pure map
x -> 3x/2 is a rigid rotation by alpha = log_6 3; the +1 contributes a
per-step wobble kick. The quasicrystal exploration
(`scripts/collatz_quasicrystal_diffraction.py`) treated the accumulated
wobble W_k as passive Debye-Waller disorder damping the Bragg peaks. The
SHG question is sharper: **is the wobble merely damping the fundamental,
or actively generating phase-locked second harmonics — bicoherent
(f, f) -> 2f coupling that no linear model can produce?** Notably, the
gear-spectrum exploration found the power spectrum of mod-q burst
signals to be white; bicoherence can be nonzero even where the power
spectrum is flat.

## Field under test

The per-step wobble increment at the k-th odd step of an orbit:

    w_k = log_6(1 + 1/(3 x_k))

where x_k is the k-th odd value. This is the exact phase kick the +1
injects into the alpha-rotation. We use increments, not the accumulated
walk W_k = theta_k - theta_0 - k*alpha: the integrated signal is
non-stationary and biases bispectrum estimation.

## Method

New script: `scripts/collatz_shg_bicoherence.py`.

### Signal extraction

- For each odd seed in [50001, 150001), walk the orbit to 1 and record
  w_k at each odd step. (Heuristically ~ln(n)/ln(4/3) ~ 40 odd steps at
  this scale, so most seeds survive the L = 32 cut; adjust the range if
  the logged skip fraction says otherwise.)
- Keep the first **L = 32** odd steps per seed. Seeds with fewer odd
  steps are skipped, and the skipped fraction is logged (guards against
  silent selection bias).
- Each window is demeaned and standardized to unit variance: w_k
  amplitude scales like 1/x_k, and the probe targets phase structure,
  not amplitude.

### Estimator

- Per window, X(f) = rfft(w). Accumulate the bispectrum
  B(f1, f2) = <X(f1) X(f2) X*(f1+f2)> over the principal triangle
  (f1 >= f2 >= 0, f1 + f2 <= Nyquist), ensemble-averaged over windows.
- Normalize to bicoherence b^2(f1, f2) in [0, 1] with the standard
  normalization b^2 = |<X1 X2 X3*>|^2 / (<|X1 X2|^2> <|X3|^2>).
- The diagonal b(f, f) is the SHG channel (f + f -> 2f); the
  off-diagonal plane catches general sum-frequency coupling.

### Estimator self-validation (runs at startup, prints pass/fail)

- Positive control: synthetic quadratically phase-coupled signal
  (cos at f0 and cos at 2*f0 with locked phases, plus noise) must light
  up at (f0, f0).
- Negative control: same construction with the 2*f0 phase randomized
  per-realization must stay at the noise floor.

### Nulls (two independent falsifiers)

1. **Phase-randomized surrogates:** each real window gets its FFT phases
   scrambled with magnitudes kept — power spectrum preserved exactly,
   bicoherence destroyed by construction. Repeated to build a 95% null
   band.
2. **Matched linear (AR) null:** fit AR(p ~ 5) to the pooled
   standardized windows, simulate an equal-size window ensemble with
   Gaussian innovations, run the identical pipeline.

A claimed signal must clear **both** bands.

## Output

`data/collatz_shg_bicoherence.png`, three panels:

1. Bicoherence heatmap over the (f1, f2) principal triangle.
2. **The SHG plot:** diagonal slice b(f, f) vs f with both null bands
   overlaid.
3. Context: ensemble power spectrum of w_k (where the fundamentals sit
   relative to any coupling).

Console summary: peak bicoherence, its (f1, f2) location, and its
percentile against the surrogate distribution.

## Interpretation contract (stated in the script docstring)

- Diagonal bicoherence above both nulls => the +1 term acts as a
  chi^(2) medium: quadratic phase coupling / harmonic generation along
  Collatz orbits.
- Flat at the null level => the wobble phases mix linearly, consistent
  with the gear-spectrum whiteness result.

## Out of scope (natural follow-ups if the diagonal lights up)

- Phase-matching / conversion-efficiency-vs-length analysis (bicoherent
  power growth with window length L: coherent ~L^2 vs incoherent ~L).
- Mod-q gear indicator fields as the input signal.
- Symbolic parity-word variant (ties to the Sturmian work).

## Amendment (2026-07-27, after first run)

The first run's "positive" verdict was confounded: Collatz orbits merge, so
~49% of ensemble windows shared an identical 16-odd-step tail while both
nulls drew fresh randomness per row — the observed statistic had far fewer
effective independent samples than its null bands assumed. Two hardenings,
human-approved:

1. **Merge dedup:** windows whose final 16 odd steps duplicate an
   already-accepted window are dropped (fraction logged).
2. **Ensemble-mean subtraction:** after standardization, the ensemble-mean
   waveform is subtracted (variance fraction logged), so bicoherence
   measures fluctuation coupling rather than the trivial common
   deterministic ramp of the wobble. All nulls operate on the same
   mean-subtracted ensemble.

## Conventions

- Python 3.12, existing `.venv`, matplotlib Agg backend, outputs to
  `data/` — matching the existing exploration-script pattern
  (`collatz_gear_spectrum.py`, `collatz_quasicrystal_diffraction.py`).
