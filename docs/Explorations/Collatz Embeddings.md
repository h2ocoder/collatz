# Collatz Embeddings

A lens-bundle embedding that turns integer vectors into points in ℝ^(m·D) via
six dynamical-invariant lenses (sector, mod3, drop_class, alpha_prefix, force,
slope_log). Originally motivated by treating concepts as integer triples
(`man = [3, 17, 6]`) and asking whether Collatz dynamics give them
word2vec-style semantic structure.

- **Spec:** [[../superpowers/specs/2026-04-30-collatz-embeddings-design]]
- **Plan:** [[../superpowers/plans/2026-04-30-collatz-embeddings]]
- **Code:** `collatz/embeddings/`
- **Notebooks:** `notebooks/09-collatz-embeddings.ipynb` (v1), `10-embeddings-v2-force-drift.ipynb` (v2), `11-embeddings-v3-angular-sector.ipynb` (v3), `12-embeddings-v4-per-lens-drift.ipynb` (v4)

## Lens basis

| Lens | Encoding | What it captures |
|---|---|---|
| sector | one-hot (12) | Eisenstein angle bin (rotates −1 mod 12 per Syracuse step) |
| mod3 | one-hot (3) | 3-adic residue |
| drop_class | one-hot (32) | bit-budget / dropping set |
| alpha_prefix | one-hot (3 × 8) | first 3 alphas (left-shifts under iteration) |
| force | scalar | bit-precision of subgroup (k − s); decays ~1.42/bounce |
| slope_log | scalar | log₂ of affine slope of n's subgroup |

Φ(c) concatenates per-component lens encodings into a 219-dim vector for m=3.

## Findings to date

### v1 — Static analogy works; `force` does the work

5 hand-built Syracuse-shift quads `(a, T_syr(a), c, T_syr(c))` against 50 distractors.

- Mean rank of expected d: **11.2 / 51** (chance baseline 25.0). One rank-0 hit.
- Lens ablation: zeroing **force** doubles mean rank to 23.4. Zeroing every other lens
  is neutral (sector 11.2, drop_class 11.0) or slightly *better* (mod3 10.0,
  alpha_prefix 9.6, slope_log 10.4).

**Reading:** the embedding picks up Syracuse-shift structure, and force is the carrier.
The other lenses contribute noise or redundancy for this task. v1's interpretation:
force = bit-precision = "epistemic confidence."

### v2 — Apparent temporal collapse, k=1 sign flip

Force-binned drift on 60 random quads, k = 0..8, three force tertiles. The hypothesis
was that high-force quads should preserve `cos(Φ(b)−Φ(a), Φ(Tᵏb)−Φ(Tᵏa))` longer.

- **Cosine drops to ~ −0.27 at k=1** (sign flip), then wanders around 0.
- All force tertiles overlap; high − low oscillates between −0.14 and +0.17 with
  no monotonic trend.

Interpreted at the time as: lens space is non-smooth under iteration. Force is a
static signal, not a temporal anchor.

### v3 — Angular sector encoding doesn't help

Hypothesis: sector's one-hot encoding causes the discontinuity. Fix: encode as
`(cos(2πs/12), sin(2πs/12))` so a sector decrement becomes a 30° rotation.

- one-hot k=1 cosine: −0.267
- angular k=1 cosine: −0.224
- Sign flips at k=1: 47/60 (one-hot) vs 45/60 (angular)

Improvement of 0.04 — within noise. Sector is *not* the (sole) cause.

### v4 — The k=1 flip is a measurement artifact

Per-lens drift in each lens's subspace alone:

| lens | k=1 cos | flips at k=1 |
|---|---|---|
| sector | **−0.486** | **60/60** |
| alpha_prefix | −0.406 | 59/60 |
| drop_class | −0.405 | 51/60 |
| slope_log | −0.325 | 38/60 |
| mod3 | −0.292 | 37/60 |
| **force** | **−0.086** | 31/60 |

The 60/60 sector result is the tell.

**The geometry:** for any one-hot lens that shifts by one index per step,
the diff vector at step 0 has support `{s, s−1}` with values `{−1, +1}`.
At step 1 the support shifts to `{s−1, s−2}`. The two diffs overlap on
*exactly one* index, with opposite signs. Dot product = −1, norms = √2 each.
**Cosine = −1/2 exactly.** sector measured −0.486 — within rounding.

This is a fact about cosine on one-hot diff vectors under any shift dynamic.
It has nothing to do with Collatz. v2's "the analogy direction flips!" was
the natural geometry of the metric, not a property of the system.

**Force is the only lens whose temporal behavior cosine can meaningfully measure**
because it's real-valued. Its k=1 cosine of −0.09 means "uncorrelated," not
"flipping." 31/60 sign flips ≈ chance.

## Synthesis

What's actually true about Φ:

- **At k=0**, Φ is a working static embedding for similarity / clustering /
  one-shot analogy. `force` carries the dynamical structure; other lenses are
  largely noise for the Syracuse-shift task we tested.
- **For temporal tracking under T**, cosine on Φ(b) − Φ(a) is a broken metric
  because most lenses are one-hot. The "−0.27 cos at k=1" we kept seeing is
  an artifact, not a finding.
- **Force is the only lens that admits cosine-style temporal analysis.**
  Whether high-force quads anchor analogies through iteration is now an
  *unanswered* question — v2 didn't actually test it cleanly.

## Methodology lessons (transferable)

These are general points that apply beyond this project:

1. **Cosine on one-hot diff vectors under shift dynamics → cos = −1/2 by
   construction.** If your embedding has discrete features that translate
   predictably under your transformation T, "tracking the diff vector" with
   cosine will look like a sign flip even if the underlying structure is
   perfectly preserved. Diagnose by projecting onto each feature's subspace
   alone before claiming a dynamical finding.
2. **A fix for one feature gets drowned out** if the rest of the embedding
   is still in the broken regime. v3's angular sector helped sector's
   subspace go from −0.5 to ~+0.87, but the other 200+ axes still contributed
   their −0.5, so the full-Φ improvement was 0.04. Either fix everything
   uniformly or use a per-feature metric.
3. **When a result looks too dramatic too quickly** (a 1-step "phase
   transition" from cos=1 to cos=−0.27), suspect the metric before the
   dynamics. The diagnostic experiment is cheap; do it before designing fixes.

## Open questions

- **v5 — does force-binned drift in the real-valued subspace anchor?**
  Re-run v2's experiment using only `force` and `slope_log` (the two scalar
  lenses). If high-force quads preserve cosine longer than low-force, v1's
  "epistemic confidence" interpretation is back on the table. This is the
  next obvious experiment — it actually tests v2's original question
  with a clean metric.
- **Structured per-lens similarity.** For sector, define `sim_sector(a,b)
  = δ(sector(b) − sector(a) = predicted_shift)`. For alpha_prefix, a
  left-shift overlap. Combine into a metric that respects each lens's
  group structure rather than naively cosining one-hot diffs.
- **Trajectory-space embedding** (Approach B from spec). Embed full
  orbits with orbit-overlap distance; sidesteps the encoding question
  entirely.
- **Component coupling.** v1/v2/v3/v4 all evolved components independently
  under T. v2 candidate: apply T to whichever component has highest force.
- **Cross-component correlations.** `sector(n_i) − sector(n_j)` etc.,
  capturing concept-internal structure beyond the bag-of-projections view.
