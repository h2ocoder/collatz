# Dropping-Set DQPT Probe — Design

**Date:** 2026-08-01
**Status:** approved (design discussed and approved in conversation)
**Inspiration:** arXiv:2511.11199 — "The Riemann Hypothesis Emerges in Dynamical Quantum Phase Transitions"

## Motivation

The paper encodes ζ(β+it) as a Loschmidt amplitude of a "primon gas" (H₀ with spectrum
E_n = log n) and reads Riemann zeros as dynamical quantum phase transitions (DQPTs):
nonanalyticities of the rate function ℱ(β,t) = −log|Σ_{n≤N} n^{−β−it}|/log N, occurring
only at β = 1/2 iff RH.

[[../../Explorations/Dropping Zeta Spectrum]] Part 1 concluded the naive dropping zeta
g(z) = Σ|R_k|z^k is not Riemann-like because it (a) has no analytic continuation past its
convergence boundary and (b) uses only marginal counts. The DQPT template fixes both:
work with the **residue-level Dirichlet series** of each dropping set. Because Dset_k is a
finite union of residue classes mod 2^k,

L_k(s) = Σ_{n∈Dset_k} n^{−s} = 2^{−ks} · H_k(s),  H_k(s) := Σ_{r∈R_k} ζ(s, r/2^k)

has an **exact analytic continuation** (Hurwitz zetas) — the missing ingredient. Zeros of
L_k = zeros of H_k (the 2^{−ks} prefactor is zero-free).

**Calibration gift:** Dset₁ = even numbers, so L₁(s) = 2^{−s}ζ(s) — its zero spectrum IS
the Riemann spectrum. The zero-finder must recover 14.134, 21.022, 25.011, … Higher k then
show how Collatz structure deforms the Riemann spectrum.

## Questions

1. **Where do the zeros of H_k(s) live** for k = 3, 6, 8, 11 in the strip σ ∈ [0, 1.2],
   t ∈ [0, T≈60]? On a vertical line (which one — 1/2? log₂(3/2) ≈ 0.585?) or scattered
   (Davenport–Heilbronn-style, as generic Hurwitz combinations)?
2. **Clock vs chaotic:** are the zero ordinates rigidly periodic (the integrable/clock
   prediction from the Part-1 spacing statistic ⟨r⟩ = 0.842) or irregular like ζ's?
3. **Does the truncated rate function ℱ_k(β,t) develop nonanalyticities at the exact
   zeros** as N grows (the DQPT signature), and how does the β-fan locate the critical line?
4. **(Stretch)** What does the rate-function scan of the χ₆-twisted series
   Σ χ₆(ι₂(n)) n^{−s} look like — where does cancellation beyond the proven linear main
   term occur?

## Components

One script, `scripts/collatz_dropping_dqpt.py`, four phases:

- **Phase A — machinery + validation.**
  - Residue enumerator: survivor-tree sieve returning the actual residues R_k mod 2^k
    (not just counts), validated against known |R_k| (1, 2, 4, 16, 48 for k = 1,3,6,8,11).
  - Vectorized Hurwitz zeta ζ(s, a) via Euler–Maclaurin in numpy complex128 (truncation
    M ≈ 30, Bernoulli tail to B₁₀), validated against mpmath to ≲1e−10 relative error.
  - Cross-check: truncated Dset sum at β = 1.5 vs Hurwitz continuation value.
- **Phase B — exact zero map.** |H_k| on a fine (σ,t) grid; local-minima candidates
  refined by Newton iteration on the numpy Hurwitz function; dedupe; validate k=1 against
  Riemann zeros. Output: zero scatter in the strip per k + |H_k| heatmap.
- **Phase C — spacing statistics.** Consecutive-spacing r-ratio statistic of zero
  ordinates per k vs Poisson/GOE/GUE/clock; periodicity test (fit to arithmetic
  progression, report residual).
- **Phase D — rate function.** ℱ_k(β,t) = −ln|Σ_{n∈Dset_k, n≤N} n^{−β−it}|/ln N by direct
  numpy summation, N ∈ {10⁴, 10⁵, 10⁶}, β ∈ {0.3, 0.5, log₂(3/2), 0.8, 1.0}, t ∈ [0, 40].
  Overlay exact zero ordinates. Plus the χ₆-twisted truncated scan at β fan (reusing
  `collatz.lfunctions` for χ₆∘ι₂), flagged exploratory.

## Outputs

- `data/collatz_dqpt_zero_map.png` — zeros in the strip, per k, Riemann zeros marked.
- `data/collatz_dqpt_rate_function.png` — ℱ_k(β,t) fan with zero overlay.
- `data/collatz_dqpt_spacings.png` — spacing/periodicity diagnostics.
- `data/collatz_dqpt_hecke.png` — χ₆-twisted scan.
- `data/collatz_dqpt_zeros.npz` — zero locations for reuse.
- `docs/Explorations/Collatz as a Quantum Quench.md` — write-up.

## Error handling / rigor

- All zero claims double-checked by |H_k| < 1e−8 at the refined point and winding of the
  phase around a small circle (argument principle spot check).
- Grid resolution chosen so adjacent known Riemann zeros (k=1 case) are not missed;
  same resolution reused for k > 1.
- Disk-space caution (machine previously hit ENOSPC): npz kept small (zeros only, no grids).

## Non-goals

- No claim of proving anything about zero locations — this is an empirical map.
- No quantum simulation content; we take only the classical rate-function formalism.
- Functional-equation/Hardy-Z construction deferred (needs the DFT-coefficient
  bookkeeping; the numpy Hurwitz continuation suffices for zero hunting in the strip).
