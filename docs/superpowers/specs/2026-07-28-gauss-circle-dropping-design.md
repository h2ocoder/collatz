# Gauss Circle Analogy for Dropping Orbits — Design

**Date:** 2026-07-28
**Status:** Approved (autonomous session — user directive: propose and run experiments)
**Branch:** `feature/gauss-circle`

## Research question

The Gauss circle problem counts lattice points in a disk of radius r:
N(r) = πr² + E(r), with the error E(r) conjectured O(r^{1/2+ε}). Main term =
geometry (area); error = boundary/lattice interaction.

Can dropping orbits be given the same anatomy? Given a dropping orbit of
length k, what are the essential properties of its members — start n, end
dest(n), and the sum of all elements — as a set and probabilistically?

Two proved repo results make this precise rather than metaphorical:

1. **[[Affine Orbit Structure]]** — within each residue subgroup mod 2^{k−s},
   dest(n) = λ_k·n + C with λ_k = 3^s/2^{k−s}, and the orbit sum
   Σ_{j=0}^{k−1} f^j(n) = A·n + B is exactly affine (asserted, never coded).
2. **[[Lattice Path Formula]]** — D_k has N(s) subgroups, each an arithmetic
   progression of density 2^{−(k−s)}, where N(s) counts lattice paths strictly
   below the irrational line y = x·log₂3.

So the point set {(n, dest(n))} is a fan of lines with exactly known slopes,
intercepts, and densities — and counting it inside a disk is a genuine
one-dimensional sibling of the Gauss circle problem, with a computable main
term and an honest error term.

## Experiment 2 (headline): the Collatz circle problem

Define C(r) = #{n ≥ 2 : n² + dest(n)² ≤ r²} — lattice points (n, dest(n))
inside the disk of radius r.

Per residue class c (modulus m_c = 2^{k−s}, slope λ, intercept C_c), the
constraint n² + (λn + C_c)² ≤ r² gives n ≤ X_c(r) ≈ r/√(1+λ²) − λC_c/(1+λ²),
so each class contributes X_c(r)/m_c + O(1). Truncating at oddity s ≤ S
(dropping times k ≤ k(S), ≈97% of integers at S=11):

    C_S(r) = κ_S·r + β_S + E_S(r)

    κ_S = (1/2)·(1+1/4)^{−1/2}  +  Σ_{s=1}^{S} N(s)·2^{−(k−s)}·(1+λ_s²)^{−1/2}

κ_S is exactly computable from `lattice_paths` (N(s) via DP, λ_s exact
rationals). E_S(r) is a sum over active classes of centered fractional-part
sawtooths — the exact analog of the Gauss error.

**Measurements:**
- Compute dest(n), dropping time for all n ≤ N_max = 10⁷ (vectorized sieve).
- C_S(r) on a dense r-grid; subtract exact κ_S·r and fitted β_S.
- Growth of |E_S(r)|: log-log fit of windowed max and std vs r. Compare the
  exponent θ against 1/2 (square-root cancellation, Gauss-conjecture analog),
  0.63 (best known Gauss bound), and 0 (bounded error).
- Sanity: empirical slope Ĉ(r)/r vs κ_S; per-class κ contributions.

**Decision rule:** θ ≈ 1/2 supports "dropping structure equidistributes like a
generic lattice" (square-root cancellation); θ ≈ 0 or ≈ 1 would each be a
structural surprise worth its own follow-up.

## Experiment 1: affine orbit-sum spectra (what it means to live in D_k)

Implement the never-coded affine machinery, then characterize each subgroup α
= (α_1..α_s) of D_k by its exact coefficients:

- Per-step: x_j = a_j·n + b_j with (a_0,b_0) = (1,0), odd step (3a, 3b+1),
  even step (a/2, b/2). All Fractions.
- Orbit sum: A_α = Σ a_j, B_α = Σ b_j. Orbit max coefficient P_α = max_j a_j.

**Key prediction to test.** log₂ a_j traced along j is the deficiency of the
lattice path below the Beatty line — a bridge constrained negative, returning
to ≈0 at step s. If subgroup paths fluctuate like constrained bridges,
log₂ P_α and log₂ A_α should scale like c·√s (Gaussian window), NOT like s
(which naive 3^s reasoning suggests). This decides whether the aggregate
orbit mass M(N) = Σ_{n≤N} orbitsum(n) scales as c·N² (convergent mean) or as
N^{2+δ} (heavy-tail dominated) — the "area term" of the analogy.

**Measurements:**
- Verify exactness: orbit_sum(n) == A·n + B for members; invariance across
  n, n + 2^{k−s}, n + 2·2^{k−s}.
- Distributions of log₂ A_α, log₂ P_α, and relative wobble B_α/A_α across all
  N(s) subgroups for s = 1..14; scaling of mean/max vs s and vs √s.
- Empirical M(N) exponent for N ≤ 10⁷ vs the convergent/divergent prediction.
- Orbit profile figure: log₂ a_j paths for all subgroups at fixed s
  (the sawtooth billiard picture, now exact per subgroup).

## Non-goals / YAGNI

- No counting of lattice points inside the per-n circumcircles from
  `geometry.py` (radius (n²+d²)/2 — no known structural hook).
- No 3-adic refinement (Phase D of 2026-06-02 spec stays deferred).
- No new notebook; scripts + figures + exploration note only.

## Deliverables

| Item | Path |
|---|---|
| Affine module | `collatz/affine.py` |
| Tests | `tests/test_affine.py` |
| Experiment 1 script | `scripts/collatz_affine_orbit_sums.py` |
| Experiment 2 script | `scripts/collatz_gauss_circle.py` |
| Figures | `data/collatz_affine_*.png`, `data/collatz_gauss_circle_*.png` |
| Write-up | `docs/Explorations/Gauss Circle Analogy.md` |

## Locked decisions

| Decision | Value |
|---|---|
| N_max for sieve | 10⁷ |
| Oddity truncation S | 11 (k ≤ 29, ≈97.1% coverage) |
| Subgroup enumeration range | s = 1..14 (N(14) = 17637) |
| Arithmetic | `Fraction` for coefficients; int64 numpy for sieve with overflow guard |
| Python | `.venv/bin/python` (darwin; CLAUDE.md's Scripts/ path is the Windows form) |
