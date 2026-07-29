# Gauss Circle Analogy

**Date:** 2026-07-28
**Scripts:** `scripts/collatz_gauss_circle.py`, `scripts/collatz_affine_orbit_sums.py`
**Module:** `collatz/affine.py` (new: exact affine machinery + dropping sieve)
**Spec:** `docs/superpowers/specs/2026-07-28-gauss-circle-dropping-design.md`

## Question

The Gauss circle problem splits a count into geometry plus fluctuation:
N(r) = πr² + E(r), with E(r) conjectured O(r^{1/2+ε}). Can dropping orbits be
given the same anatomy — a main term forced by structure, and an error term
measuring how the integers interfere with it? What does it mean, set-wise and
probabilistically, to exist inside a dropping orbit of length k — at its
beginning, its end, or summed over all its elements?

Two proved results supply the skeleton: [[Affine Orbit Structure]] (dest,
orbit sum, and orbit max are exact affine functions of n within each subgroup
mod 2^{k−s}) and the [[Lattice Path Formula]] (D_k has N(s) such subgroups,
N(s) = lattice paths strictly below y = x·log₂3).

## Experiment 2: the Collatz circle problem

Count lattice points (n, dest(n)) inside the disk of radius r:

$$C(r) = \#\{n \ge 2 : n^2 + \text{dest}(n)^2 \le r^2\}.$$

The point set is a **fan of affine lines** pinched between d = n/2 and d = n
(figure `data/collatz_gauss_circle_fan.png`): one arithmetic progression of
modulus 2^{k−s} per subgroup, slope λ_s = 3^s/2^{k−s} shared across each
level. Restricting to oddities s ≤ 14 (98.0% of integers),

$$C_S(r) = \kappa_S\, r + \beta_S + E_S(r), \qquad
\kappa_S = \tfrac{1}{2}(1+\tfrac14)^{-1/2} + \sum_{s=1}^{14} N(s)\,
2^{-(k-s)} (1+\lambda_s^2)^{-1/2}.$$

### Results (N = 10⁷, replicated at 3×10⁷)

| Quantity | Predicted | Observed |
|---|---|---|
| κ_S | **0.83329406** (exact, from lattice paths) | 0.83329455 fitted at 10⁷ (+5.9·10⁻⁷); 0.83329360 at 3×10⁷ (−5.6·10⁻⁷) |
| covered density | 0.979877 | 0.979879 |
| error range up to r = 10⁷ | — | E(r) ∈ [−90, +92] against C ≈ 8.3·10⁶ (relative 10⁻⁵) |
| error exponent θ (windowed std) | 1/2 = square-root cancellation | **0.357** (10⁷), 0.344 (3×10⁷) |
| independent-sawtooth null std (top window) | 72.2 | observed 26.9 — **rigidity factor 2.7** |

The deviation of the fitted slope flips sign between N = 10⁷ and 3×10⁷ —
the main term is unbiased at the 10⁻⁶ level.

E_S(r) is a sum of centered sawtooths, one per active progression. Under
independent phases its variance would be (#active classes)/12 (Bernoulli
p(1−p) while a class is sparse). Observed fluctuation runs a factor 1.7–2.7
**below** that null across all dyadic windows — even the windowed *max* stays
under the null's std curve (figure `data/collatz_gauss_circle_error.png`).
The residue phases interfere destructively: the same sub-random rigidity seen
in the zero-spacing statistics of [[Dropping Zeta Spectrum]] (more rigid than
GUE) reappears in physical counting space.

The measured θ ≈ 0.36 tracks the null's finite-size slope, which is driven by
class activation: #active(r) grows like r^{0.323} (since N(s) ~ 2^{0.512s}
activates at r ≈ 2^{1.585s}), so the null's asymptotic exponent is
0.323/2 ≈ **0.16** — the Collatz circle problem appears to beat square-root
cancellation not marginally but structurally.

## Experiment 1: what it means to exist inside a dropping orbit

Every subgroup α = (α_1..α_s) has exact Fraction invariants (now implemented
in `collatz/affine.py`): per-step coefficients f^j(n) = a_j n + b_j, orbit
sum A_α n + B_α, peak coefficient P_α = max_j a_j.

**The profile j ↦ log₂ a_j is the whole answer** (figure
`data/collatz_affine_orbit_profiles.png`): it is a sawtooth *bridge* —
pinned at altitude 0 at the beginning (a_0 = 1), pinned at altitude
log₂(2λ_s) ≈ 0..1 at the end, rising in between while staying inside the
Beatty bandwidth. Every member of the subgroup traces this same shape,
rescaled by n. So:

- **Beginning and end are pinned**: existing at either end of a dropping
  orbit means altitude O(1) relative to n. The dropping destination is not
  free — it is λ_s n + C with universal slope.
- **The middle is a constrained bridge**: mean peak height scales like
  **1.52·s^0.44 ≈ c√s** (Gaussian bridge fluctuation), while the maximum is
  attained exactly by the all-ones path on the bandwidth line
  (log₂3 − 1)s + 1 ≈ 0.585s + 1 (verified to equality, s ≤ 14).
  Typical members of D_k rise to ~2^{c√s}·n; the extreme subgroup rises to
  ~2·(3/2)^s·n — the classic record-excursion shape.
- **The +1 wobble shifts, it does not bend**: orbit sum = A(n + B/A). The
  relative shift |B/A| grows only linearly (max ≈ 0.157s, mean flattening
  near 1.3) — a vanishing perturbation of the affine geometry for large
  members, echoing [[Gear Spectrum and Wobble Channels]].

### The mass inversion

Summing orbit sums, M(N) = Σ_{n≤N} Σ_j f^j(n), inverts the Gauss hierarchy.
Level by level the affine prediction is *exact*:

| k | s | observed / predicted mass at N = 10⁷ |
|---|---|---|
| 3 | 1 | 1.0000 |
| 21 | 8 | 1.0000 |
| 26 | 10 | 1.0002 |
| 37 | 14 | 0.9967 (N-truncation) |

— yet **all levels s ≤ 14 together carry only 11.5% of M(N)**. 88.5% of the
orbit mass lives at k > 37, in classes whose moduli 2^{k−s} exceed N — carried
by "premature" small members of astronomically sparse classes. Three single
orbits (k = 362, 357, 349) each carry ≈ 8% of the total mass at N = 10⁷;
at N = 10³ the single orbit of n = 703 carries 26%. Empirically
M(N) ~ N^{2.12} over 10^3.5..10^7 and the per-level κ_M increments
(≈ 0.6–1.1 per s) do not decay — the mean of orbitsum(n)/n **diverges**.

The contrast is the finding:

| | Gauss circle | Collatz fan (counting) | Collatz fan (mass) |
|---|---|---|---|
| main term | area πr² | κ_S r, exact from lattice paths | exact per level, but no closed total |
| error | O(r^θ), θ ∈ [1/2, 0.63] | θ ≈ 0.36 → 0.16, sub-null rigidity | **the "error" is 88% of the total** |
| dominated by | bulk | bulk | exponentially rare deep classes |

**Counting dropping orbits is more regular than a random lattice; weighing
them is wilder than any lattice.** The counting measure and the mass measure
of the same fan sit on opposite sides of the Gauss circle problem. Any
averaging argument over dropping sets (cf. the anti-probabilistic stance in
the countdown-hierarchy plan) must respect this: densities equidistribute
with sub-random error, but expectations of orbit functionals are
record-dominated and divergent.

## Experiment 3: the rigidity mechanism — hyperuniform residue phases

`scripts/collatz_residue_rigidity.py` (figures
`data/collatz_residue_rigidity.png`, `data/collatz_residue_form_factor.png`).

New machinery: `residue_from_alphas` in `collatz/affine.py` reconstructs each
subgroup's residue r mod 2^{k−s} from its alpha-tuple by 2-adic bit-lifting
(cross-checked against `collatz/residues.py` for s ≤ 5). A subtlety surfaced:
the tuple's final alpha_s is a *minimum* — the class fixes only the first k
parities, and trajectories may keep halving past the drop.

Three results:

1. **The sawtooth model is exact.** Rebuilding C(r) from the 30,086 classes
   (residue, modulus, slope, intercept — no sieve) reproduces the sieved
   count with **max |diff| = 0** across all 7,680 grid points up to 10⁷.
   E(r) is fully explained: it *is* the sum of 30,086 deterministic
   sawtooths, one per subgroup.
2. **The rigidity lives in the phases.** Each class sits at phase
   φ = {(r₀ + λC/(1+λ²))/m} on its sawtooth wheel. Re-running the exact
   model with phases drawn uniformly at random restores the independent
   null: the data/model curve sits below the entire 6-realization shuffled
   band at every window. Per-level pair-correlation energy
   V_s/(N_s/12) = Σ_h |F_s(h)|²/(2π²h²) / (N_s/12) runs 0.12–0.86
   (s = 10 is the most rigid at 0.117; s = 12 the least at 0.860).
3. **The phase sets are disordered hyperuniform, not quasicrystalline.**
   Structure factor S(h) = |F(h)|²/N by harmonic band:

   | s | N | h=1–4 | 5–16 | 17–64 | 65–256 | 257–1024 | 1025–4096 |
   |---|---|---|---|---|---|---|---|
   | 8 | 85 | 0.18 | 0.46 | 0.75 | 0.97 | 1.00 | 1.01 |
   | 10 | 476 | **0.06** | 0.40 | 0.47 | 0.94 | 0.94 | 1.02 |
   | 13 | 8045 | 0.11 | 1.41 | 1.42 | 0.54 | 0.81 | 0.90 |
   | 14 | 17637 | 0.15 | 0.43 | 0.72 | 0.80 | 0.73 | 0.91 |

   Long-wavelength fluctuations are suppressed by up to 17× while high
   harmonics sit at the Poisson level — and since V_s weights harmonics by
   1/h², the low-h suppression is exactly what produces the rigidity. But
   the gap spectrum rules out a Kronecker/cut-and-project set: gap CV ≈ 0.93
   (locally Poisson-like), with hundreds of distinct gaps — quantized on a
   fine 2-adic sublattice (multiples of ≈16/m at s = 13, 14), not the ≤ 3
   gaps of a three-distance set. Locally random, globally rigid: the
   residues of D_k form a **disordered hyperuniform point set on the
   circle**, the same class as maximally-jammed packings — a different
   beast from the Bragg-peaked orbit phases of
   [[Collatz as a Quasicrystal]]. The s = 12 level is an outlier
   (S(1–4) = 1.35, least rigid) worth its own look.

## Where signal could still hide

- ~~The rigidity factor (1.7–2.7 below null) is unexplained.~~ Resolved by
  Experiment 3: it is low-harmonic hyperuniformity of the residue phases.
  The remaining theorem-shaped question is *why* the lattice-path prefix
  tree produces hyperuniform residues — a closed form for S(h) at small h
  from the alpha-tuple recursion would turn θ ≈ 0.16 into a conjecture with
  a mechanism, and explain the s = 12 anomaly.
- Number-variance check: σ²(L)/(NL) falls monotonically with window size
  (s = 14: 0.77 at L = 0.0005 → 0.33 at L = 0.128; Poisson = 1) —
  confirming hyperuniform decay, at a rate suggesting the weaker classes
  (II/III) rather than crystal-like class I. A wider L-range (larger s,
  more subgroups) would pin the class.
- The all-ones path saturates the peak bound at *every* s. Its members
  (n ≡ 2^{s+1} − 1 patterns) are the record-breakers; the mass measure is
  essentially a sum over all-ones-like paths. A Meyer-set / cut-and-project
  view of just those paths connects to [[Collatz as a Quasicrystal]].
- Phase D of the 2026-06-02 spec (combined 2^{k−2s}·6^s modulus) would refine
  the fan into the base-6 lattice; the circle count could then be run per
  3-adic sector, testing whether the rigidity is 2-adic or 6-adic in origin.

## Related

- [[Affine Orbit Structure]] — now implemented in `collatz/affine.py`
- [[Lattice Path Formula]] — supplies N(s) and κ_S
- [[Odd Stopping Time Spectrum]] — the achievable levels k(s)
- [[Dropping Zeta Spectrum]] — the earlier sub-GUE rigidity signal
