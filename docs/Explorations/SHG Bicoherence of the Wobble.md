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
of orbits from odd seeds in `[50001, 150001)`. The first pass on this
ensemble was confounded and was hardened before this note was written — see
below.

*Confound found and fixed.* The raw run standardized 30542 surviving windows
(19458/50000 seeds skipped for having fewer than 32 odd steps) and reported a
peak b² = 0.5675 at the 100th percentile against both nulls — but Collatz
orbits merge downstream, and 21756/50000 (43.5%) of the raw seed pool turned
out to duplicate an already-accepted window's final-16-odd-step tail, while
both nulls (phase-randomized surrogate, AR(5) Gaussian) drew fresh randomness
per row at the same nominal M. The ensemble also shared a common
deterministic ramp — wobble grows in size as an orbit descends toward its
dropping/stopping destination — which bicoherence can register as spurious
phase coupling. Either effect alone could manufacture an "above both nulls
everywhere" result with no real chi^(2) coupling behind it.

The pipeline was hardened accordingly (human-approved amendment) and rerun:
windows whose final 16 odd steps duplicate an already-accepted window's tail
are now dropped before the ensemble is built, and the ensemble-mean waveform
is subtracted from every surviving window so all downstream statistics —
observed bicoherence *and* both nulls, which consume whatever
`build_ensemble()` returns — measure fluctuation coupling rather than the
shared descent ramp. Two falsifiers, 95% bands over 100 ensembles each, run
on this deduplicated, mean-subtracted ensemble: phase-randomized surrogates
(same spectra, coupling destroyed) and a matched AR(5) Gaussian null. The
estimator itself is validated on synthetic phase-coupled controls at
startup.

**Result** (hardened pipeline, final numbers). Self-check: coupled
b²=0.959 (>0.8), uncoupled b²=0.004 (<0.2) — estimator PASS. Final ensemble:
**M = 8786 windows** (19458/50000 seeds skipped = 38.9% for orbits too short
to reach 32 odd steps, plus 21756/50000 merged-tail duplicates dropped =
43.5% — only 17.6% of the original 50000-seed pool survives both filters).
Ensemble-mean waveform removed, carrying **29.742%** of pre-removal
variance — confirming the common descent ramp was a substantial component.
AR(5) fit on the residual: `phi = [0.528, 0.021, 0.003, -0.001, -0.021]`,
`sigma = 0.706`.

Global peak **b² = 0.3056** at `(f1, f2) = (10, 6)` (normalized
`f = (0.312, 0.188)`), at the **100th percentile** of the surrogate
max-distribution — still above every one of the 100 surrogate ensembles'
max statistic, now on the reduced, deduplicated, fluctuation-only ensemble.
This peak is off the strict SHG diagonal (`f1+f2=16`, general sum-frequency
coupling, not literal `f -> 2f` doubling). The diagonal-only channel
`b²(f,f)` is lower and reshaped: it rises with frequency from ≈0.09 at the
lowest plotted diagonal point up to ≈0.20 at the highest (f≈0.25, a
qualitative reversal from the pre-fix run, which fell from ≈0.44 to ≈0.17 —
consistent with the low-frequency-dominant deterministic ramp having been
subtracted out). Both null bands (95% surrogate, 95% AR(5)) sit flat at
essentially the floor across the entire probed range, visually
indistinguishable from each other and from zero. The observed diagonal curve
sits clearly and uniformly above both bands at every plotted frequency, with
the gap widening rather than closing at high frequency.

**Caveats.**
- The global peak (10,6) is off the strict diagonal; the diagonal-restricted
  SHG channel peaks lower (~0.20 at high f). The headline statistic is
  general sum-frequency coupling (`f1+f2=16`), not literal second-harmonic
  doubling.
- The 16-step tail-dedup key only catches merges that complete *before* the
  final 16 steps of a window; merges landing inside that trailing stretch
  are invisible to it, so some residual tail correlation may remain
  unremoved.
- The AR(5) null re-standardizes its simulated windows to unit variance,
  while the observed (mean-subtracted) ensemble has heterogeneous,
  sub-unit variance per window — a mismatch the surrogate null does not
  share, yet the surrogate null independently sits at the same floor as the
  AR band, which is reassuring but does not make the AR comparison
  apples-to-apples.
- Only 17.6% of the original 50000-seed pool contributes an independent
  window to the final ensemble (38.9% too-short + 43.5% merged-tail
  duplicates of the remainder); M=8786 is the number to cite, not the
  pre-fix M=30542.

**Verdict.** Quadratic phase coupling in the wobble field survives both
independent nulls after removing the two known confounds (merged-tail
duplication and the shared deterministic descent ramp): the diagonal
`b²(f,f)` sits above both the surrogate and AR(5) 95% bands at every probed
frequency on a deduplicated, fluctuation-only ensemble, and the global peak
`b²=0.3056` still exceeds 100% of the surrogate max-distribution. This is
evidence *for* chi^(2)-like behavior of the `+1` — reduced in magnitude from
the confounded first pass (peak roughly halved, 0.5675 -> 0.3056) and
reshaped (diagonal channel now rises with frequency rather than falling),
but not eliminated, and qualified by the caveats above. Follow-ups: test
phase-matching / conversion-efficiency growth with L, repeat on mod-q
fields and the parity-word variant, and close caveats (b) and (c) (a
full-window dedup key; an AR null with matched heterogeneous variance).

![[collatz_shg_bicoherence.png]]

**Related:** [[Collatz as a Quasicrystal]], [[Gear Spectrum and Wobble Channels]].
