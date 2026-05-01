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

### v8 — Music-theoretic reframe: three orthogonal distances

The user proposed reframing the whole project through music theory. In music, a
song is identifiable by **progression** (chord sequence), **key** (transposition
class), and **style** (rhythm/feel — tempo-invariant statistical fingerprint).
Three independent dimensions, each captured by a different mathematical structure.

The mapping turned out to be unusually clean:

| Music | Collatz |
|---|---|
| Pitch class (Z/12) | Eisenstein sector (Z/12) — *literal Z/12 group structure* |
| Note duration | Alpha value (halvings per Syracuse step) |
| Progression | Sequence of (sector, mod3) along orbit |
| Key (transposition class) | Affine subgroup of Set_k — *we already proved this!* |
| Style (statistical feel) | Empirical (alpha, mod3-transition) fingerprint |

The "key = affine subgroup" identification is mathematically tight: the proved
**affine orbit structure** result says all members of a subgroup of Set_k share
the same `dest(n) = α·n + C`. They produce **identical Syracuse progressions in
the quotient sense** — literally "same song, different keys."

Three subagents built three independent embeddings in parallel:

**`collatz/embeddings/keys.py`** — coset-quotient distance.
`subgroup_id(n) = (k, s, n mod 2^(k-s))` uniquely identifies n's affine subgroup.
On 30 same-subgroup analogy quads vs 100 distractors:

| method | mean rank |
|---|---|
| (chance) | 50 |
| lens-Φ | 3.0 |
| trajectory (Jaccard) | 59.8 |
| **keys (coset)** | **0.8** |

Keys dominates same-subgroup analogies. **It's useless on Syracuse-shift (78.1)
— by design**, since T_syr moves to a different subgroup ~79% of the time.
Clean orthogonality.

**`collatz/embeddings/style.py`** — statistical fingerprint, chi-squared distance.
Strongly tempo-invariant: `style_distance(27, 41) = 0.0001` despite orbit lengths
of 41/40. **But style does NOT cluster by dropping set.** Set_3↔Set_8 mean
distance (0.108) is actually *smaller* than Set_3 within itself (0.124).

This is **exactly what we should expect** — the **spectral gap → 5/6** result we
already proved says alpha distributions equidistribute across the lattice via
mixing. Style fingerprints integrate over the whole orbit and inherit the limiting
distribution, which is the same for every starting class. **The previously-proved
spectral gap predicts that style cannot be a category discriminator** — and the
experiment confirms it numerically. Style is a similarity metric for "feel,"
complementary to keys, not a substitute.

**`collatz/embeddings/progression.py`** — edit distance on orbit sequences.
The `joint_progression` (sector × mod3) is the practical default. The agent caught
a real spec bug: **`sector_progression(n)` alone is just a function of orbit
length L** (deterministic countdown L mod 12, …, 0), so any two integers with
the same L have *identical* sector progressions. The mod3 axis breaks this
degeneracy because mod3 depends on actually-visited integers, not just length.
Joint progression ties v6 trajectory on Syracuse-shift (mean rank 0.5).

**Cross-method orthogonality verified at integration:** 5 and 9 are in the same
Set_3 subgroup, so `coset_distance(5, 9) = 0` (same key). But their actual orbits
differ — `orbit_distance / progression_distance / style_distance` are all 0.6-0.7
(same key, different songs). The decomposition the user proposed is *real*: each
distance captures a structural relation the others can't.

## Synthesis

After v8, four embeddings cover four different structural questions. **They are
genuinely orthogonal — none is a substitute for any other.**

| Embedding | Question it answers | When to use |
|---|---|---|
| **lens-Φ** (cosine) | "How similar are these via dynamical-invariant projections?" | Coarse category recognition when distractors span categories |
| **trajectory** (Jaccard) | "Do these orbits visit similar territory?" | Orbit-overlap relations (Syracuse-shift, near-merge orbits) |
| **keys** (coset) | "Are these the same song in different keys?" | Equivalence under affine orbit law (proved structure) |
| **style** (chi-squared) | "Do these orbits *feel* the same?" | Tempo-invariant similarity; integrates over the whole orbit |
| **progression** (edit) | "Do these orbits traverse the same sequence?" | Sequence-level comparison; tempo-flexible via insertions |

What's true under iteration:

- **Φ at k=0** is a working static embedding. Force is the lens-bundle carrier
  for category-level analogies.
- **Φ under iteration:** cosine on one-hot diff vectors gives meaningless results
  by construction (v4). Force is the only lens that admits cosine-style temporal
  analysis, but force-anchoring of analogies isn't supported (v5).
- **The set-space and sequence-space embeddings (trajectory, keys, style,
  progression)** sidestep the cosine-on-one-hot problem entirely. None of them
  needs the iteration-direction question to be coherent.

What's true about the music-theoretic decomposition:

- **The Z/12 ↔ Z/12 mapping** between Eisenstein sectors and chromatic pitches
  isn't poetic — it's the same group structure in different domains.
- **The "key = affine subgroup" identification** is mathematically tight: the
  proved affine orbit structure result IS the transposition equivalence.
- **The spectral-gap → 5/6 result IS the prediction that style cannot be a
  category discriminator.** Notebook 17 confirms numerically what the theory says.
- **The four embeddings are orthogonal because the structural questions are
  orthogonal**, not because of measurement artifacts.

What still hasn't been captured:

- **Multiplicative transformations** (tripling). No embedding tracks `log n` cleanly.
- **Intra-class ordinal structure** (set-mate within Set_3 distractors). No
  embedding has a "position within class" feature.
- **Component coupling.** All work has evolved components independently under T.

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

- **Multiplicative-residue / magnitude lens** (`log n` and/or `n mod p` for primes p).
  Predicts tripling moves are a fixed log-3 shift on `log n` axis. Direct test of
  whether v7's tripling failure was about missing features.
- **Positional-index-within-class lens** (`rank of n among Set_k members`).
  Predicts set-mate moves are a fixed +1 shift. Test: does v7's set-mate failure
  go away with this feature?
- **Hybrid distance** combining the four orthogonal embeddings: per-relation
  weighted ensemble. Cheap; would handle Syracuse-shift, key-identification, and
  progression-matching in one query.
- **Structured per-lens similarity metrics** for the discrete lenses (sector
  rotation, alpha_prefix left-shift) — the "real fix" for v2's temporal question.
- **Component coupling.** All work has evolved components independently. Apply T
  to whichever component has highest force; treat as a single dynamical entity.
- **Cross-component correlations** (`sector(n_i) − sector(n_j)` etc.) — concept-internal
  structure beyond the bag-of-projections view.
- **Stop here.** Eight experiments, four orthogonal embeddings characterized,
  documented methodology lessons, the user's musical intuition mathematically
  vindicated. There's no shame.
