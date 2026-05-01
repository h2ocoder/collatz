# Collatz Embeddings

A lens-bundle embedding (and a trajectory-space alternative) that turn integer
vectors into points where Collatz dynamics can be probed for semantic structure.
Originally motivated by treating concepts as integer triples (`man = [3, 17, 6]`)
and asking whether Collatz dynamics give them word2vec-style relations.

- **Spec:** [[../superpowers/specs/2026-04-30-collatz-embeddings-design]]
- **Plan:** [[../superpowers/plans/2026-04-30-collatz-embeddings]]
- **Code:** `collatz/embeddings/`
- **Notebooks:** `09` (v1) → `15` (v7)

## Two embeddings

**Lens-bundle (Φ).** Six dynamical lenses (sector, mod3, drop_class, alpha_prefix,
force, slope_log), one-hot or scalar-encoded, concatenated across components into
a 219-dim vector for m=3. Distance via cosine. v1–v5 explore this.

**Trajectory-space (orbit-bag).** Each integer is its full Syracuse orbit (sequence
of odd integers visited). Concepts are bags of orbits. Distance via mean pairwise
Jaccard distance on orbit *sets*. v6–v7 explore this.

## Chronological findings

### v1 — Static analogy works; `force` does the work

5 hand-built Syracuse-shift quads `(a, T_syr(a), c, T_syr(c))` against 50 distractors.

- Mean rank of expected d: **11.2 / 51** (chance baseline 25.0). One rank-0 hit.
- Lens ablation: zeroing **force** doubles mean rank to 23.4. Zeroing every other
  lens is neutral (sector 11.2, drop_class 11.0) or slightly *better*.

Force is the carrier; other lenses contribute noise or redundancy. v1's reading:
force = bit-precision = "epistemic confidence."

### v2 — Apparent temporal collapse: cos flips at k=1

Force-binned drift on 60 random quads, k = 0..8. Cosine drops to ~ −0.27 at k=1
then wanders around 0. All force tertiles overlap. Interpreted at the time as:
lens space is non-smooth under iteration; force is static-only.

### v3 — Angular sector encoding doesn't help

Hypothesis: sector's one-hot encoding causes the discontinuity. Replacing
with `(cos(2πs/12), sin(2πs/12))` improved k=1 cosine by only 0.04 (within noise).
Sector wasn't the (sole) cause.

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

The 60/60 sector result is the tell. For any one-hot lens shifting by one index
per step, the diff at step 0 has support `{s, s−1}` with values `{−1, +1}`; at
step 1 the support shifts to `{s−1, s−2}`. The two diff vectors share *exactly
one* index with opposite signs. Dot product = −1, norms √2 each. **Cosine = −1/2
exactly.** Sector measured −0.486 — within rounding.

This is a fact about cosine on one-hot diff vectors under any shift dynamic.
v2's "the analogy direction flips!" was the natural geometry of the metric, not
a property of the system. **Force is the only lens whose temporal behavior cosine
can meaningfully measure** because it's real-valued.

### v5 — Real-only drift fixes the artifact, but no force anchoring

Restricting Φ to force + slope_log axes: k=1 cosine improves from −0.267 to
−0.091 (3× artifact reduction); sign flips drop from 47/60 to 32/60. v4 diagnosis
confirmed.

But the force-binned tertile pattern at k=1 was actually the *opposite* of v1's
prediction (low > high), and the result is confounded by zero-diff vectors. The
"force = epistemic confidence persists through iteration" reading is **not
supported** even with a clean metric. Φ is a working *static* embedding only.

### v6 — Trajectory-space dominates Syracuse-shift

Pivoted to set-space. Each integer → Syracuse orbit set; distance = 1 − Jaccard.
On 30 random Syracuse-shift quads vs 100 distractors:

| method | mean rank | top-5 |
|---|---|---|
| (chance) | 50 | — |
| v1 lens-Phi | 37.0 | 5/30 |
| **v6 trajectory_analogy** | **0.2** | **30/30** |
| v6 nearest-orbit (no analogy) | **0.0** | **30/30** |

Essentially perfect. **But the test is structurally generous to v6:** d = T_syr(c)
makes orbit(d) literally a *suffix* of orbit(c), so nearest-neighbor in orbit-distance
trivially picks d. v1 loses because it compresses each integer's orbit into 6 lens
projections. The two methods capture different things; v6 wins when the relation
is orbit-overlap.

### v7 — Both embeddings fail intra-class and arithmetic analogies

Three analogy categories, n=30 quads each, 100 distractors:

| category | chance | v1 lens-Phi | v6 trajectory |
|---|---|---|---|
| Syracuse-shift | 50 | 49.9 | **0.1** |
| Tripling `(a, 3a, c, 3c)` | 50 | **66.2** (worse) | 43.2 |
| Set-mate (consecutive Set_3 windows) | 50 | 56.4 | 58.4 |

v1 wins nothing — at chance on Syracuse-shift, *worse* than chance on tripling,
slightly worse than chance on set-mate.

**The set-mate result was the surprise.** I predicted v1 would dominate because
drop_class explicitly captures Set_3 membership. It failed because the **distractor
pool was all Set_3 triples** — drop_class becomes non-discriminative, and no other
lens tracks ordinal position within the class. v6 fails for the same reason:
orbit-overlap doesn't encode within-class index ordering.

**Methodological lesson:** the distractor pool determines what the benchmark
tests. Distractors spanning categories → tests *category recognition* (drop_class
shines). Distractors sharing a category → tests *intra-category structure*
(neither embedding captures it).

## Synthesis

What's actually true:

- **Φ at k=0** is a working static embedding for category-level analogies. Force
  is the carrier when the relation involves dropping-set/orbit-bit-budget structure.
- **Φ under iteration:** cosine on one-hot diff vectors gives meaningless results
  by construction. Force is the only lens that admits cosine-style temporal analysis,
  and even there, force-anchoring of analogies isn't supported by the data.
- **v6 trajectory-space** dominates orbit-overlap analogies (Syracuse-shift) and
  is essentially perfect there. It does *not* generalize to arithmetic or
  intra-class analogies.
- **Neither embedding captures fine ordinal/sequential structure within a class
  or multiplicative transformations** — they need new features (magnitude `log n`,
  positional index within class, multiplicative residues) for those tasks.

The two embeddings are *complementary*, not competing: lens-Φ for coarse category
recognition (when distractors span categories), v6 for orbit-overlap relations.
Hybrid embeddings or per-relation custom metrics would handle a wider range.

## Methodology lessons (transferable beyond this project)

1. **Cosine on one-hot diff vectors under shift dynamics → cos = −1/2 by
   construction.** If your embedding has discrete features that translate
   predictably under T, "tracking the diff vector" with cosine looks like a sign
   flip even if the underlying structure is preserved. Diagnose by projecting onto
   each feature's subspace alone before claiming a dynamical finding.
2. **A fix for one feature gets drowned out** if the rest of the embedding is
   still in the broken regime. v3's angular sector helped sector's subspace go
   from −0.5 to ~+0.87, but the other 200+ axes still contributed −0.5, so the
   full-Φ improvement was 0.04. Either fix everything uniformly or use a per-feature
   metric.
3. **When a result looks too dramatic too quickly** (1-step jump from cos=1 to
   cos=−0.27), suspect the metric before the dynamics. The diagnostic is cheap.
4. **The distractor pool determines what the benchmark measures.** A test that
   looks like it probes class structure may actually probe intra-class structure
   if your distractors share the class. State your pool composition explicitly
   when reporting analogy benchmarks.
5. **Embedding dominance can be structurally pre-determined.** v6's perfect score
   on Syracuse-shift was a forced consequence of how the test was constructed —
   d's orbit was literally a suffix of c's orbit. Always ask: "is my expected
   answer structurally embedded in the test definition?"

## Open questions / candidate next moves

- **Hybrid embedding.** Distance is `α·lens_cosine + (1−α)·orbit_distance`. Tune α
  per relation type. Cheap; would handle Syracuse-shift and category recognition
  in one model.
- **Add a magnitude lens** (`log n` per component) and re-test tripling. Predicts
  tripling moves should be a fixed log-3 shift.
- **Add a positional-index-within-class lens** (`rank of n among Set_k members`).
  Predicts set-mate moves should be a fixed +1 shift.
- **Structured per-lens similarity metrics** that respect each lens's group
  structure (sector rotation, alpha_prefix left-shift) — would re-open the
  temporal-anchoring question with a metric designed for it.
- **Component coupling.** All v1–v7 evolved components independently under T.
  v8 candidate: apply T to whichever component has highest force.
- **Cross-component correlations** (`sector(n_i) − sector(n_j)` etc.) — concept-internal
  structure beyond the bag-of-projections view.
- **Stop here.** We have a clean seven-experiment story with falsifiable findings,
  documented methodology lessons, and concrete v8 candidates. There's no shame.
