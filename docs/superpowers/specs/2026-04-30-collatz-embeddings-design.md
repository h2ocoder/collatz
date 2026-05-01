# Collatz Embeddings — v1 Design

**Date:** 2026-04-30
**Status:** Approved (sections 1–4 reviewed in brainstorm)
**Related:** `docs/Conjectures/Eisenstein Factorization.md`, `docs/Conjectures/Affine Orbit Structure.md`, `docs/Conjectures/Lattice Path Formula.md`

## Motivation

Word embeddings (word2vec et al.) work because semantic relationships project onto linear structure in a high-dimensional vector space — `king − man + woman ≈ queen`. The premise of this exploration is that the dynamical invariants discovered in this project (Eisenstein sector rotation, 3-adic lock, dropping-set affine slope, alpha sequence, bit-budget force) form a *lens basis* on the integers, and integer vectors used as concept encodings can support analogous semantic operations in this lens space.

Mental model: a concept is a high-dimensional object viewed from many angles. The lenses are the angles. The dynamical invariants are the descriptions that survive rotation. Iteration of Collatz is the rotation, and what survives iteration is what anchors a concept's identity.

## Approach

We chose **Lens-Bundle Embedding** (Approach A) over Orbit-Trajectory Embedding (B) and Affine-Class Embedding (C). Approach A subsumes the others as special cases — B is "trajectory-as-lens", C is "subgroup-coords-as-lens" — and lets us swap or weight lenses experimentally.

## Architecture

### Lens

A `Lens` is a pure callable ℤ → ℝ (or → small finite set encoded numerically) extracting one dynamical invariant. Stateless and composable.

Starter library:

| Lens | Signature | Encodes | Source |
|---|---|---|---|
| `sector(n)` | int → int ∈ {0..11} | Eisenstein angle bin of first Syracuse step | Eisenstein Factorization |
| `mod3(n)` | int → int ∈ {0,1,2} | 3-adic residue | 3-Adic Lock |
| `drop_class(n)` | int → int k | dropping set k | `collatz.dropping` |
| `alpha_prefix(n, k=3)` | int → tuple[int] | first k entries of α-sequence | `collatz.dropping` |
| `force(n)` | int → float | log₂(P) where P = 2^(k−s) | bit-precision of subgroup |
| `slope_log(n)` | int → float | log₂(3^s / 2^(k−s)) | affine slope of subgroup |

`force` carries a dual interpretation:
- **Mathematical:** bit-precision of n's affine subgroup; high force = narrow subgroup, more bits stable.
- **Epistemic:** semantic confidence — high-force components are well-determined claims ("dog is animal"), low-force ones are loose ("dog is cuter than cat").

### Concept

```python
@dataclass
class Concept:
    name: str
    vec: tuple[int, ...]   # fixed length m, default 3
```

### Embedding Φ

For concept c with components (n₁, …, n_m) and lens set (φ₁, …, φ_d):

- per-component lens vector v_i = (φ₁(n_i), …, φ_d(n_i))
- concatenate across components: Φ(c) = (v₁, …, v_m) ∈ ℝ^(m·D), where D is the post-encoding lens dimensionality
- discrete-output lenses (`sector`, `mod3`, `drop_class`, individual `alpha_prefix` entries) are **one-hot encoded**
- real-valued lenses (`force`, `slope_log`) kept as-is

Fixed dimensionality is what makes analogy arithmetic well-defined.

### File layout

```
collatz/embeddings/
  __init__.py      # public API
  lenses.py        # 6 lenses + Lens protocol
  concept.py       # Concept dataclass + Φ stacker
  distance.py      # cosine, l2, weighted, analogy
  iteration.py     # T(c), advance_lens for closed-form lenses
tests/
  test_embeddings.py
notebooks/
  09-collatz-embeddings.ipynb
docs/Explorations/
  Collatz Embeddings.md   # short Obsidian note linking to spec + notebook
```

Each module ≤ ~150 lines; one job per file.

## Distance, analogy, purity

### Metrics (`distance.py`)

- `cosine(a, b)`
- `l2(a, b)`
- `weighted(a, b, w)` — per-axis weights; supports lens ablation (set weight = 0)
- `force_weighted(a, b)` — special case where axis weights derive from components' `force` values

### Analogy

```python
analogy(a, b, c, candidates) → ranked list
```
Score: `cosine(Φ(d), Φ(a) − Φ(b) + Φ(c))` per candidate d.

### Pure concepts

Concept c is *pure* with respect to lens φ if all components share φ-value. *Fully pure* = pure in every lens (all components in one subgroup).

Pure concepts are test fixtures: their iteration behavior is predictable from theory, so they validate lens implementations and serve as experimental controls.

## Iteration semantics

### Step iteration

```python
T(c) = Concept(c.name, (T(n_1), ..., T(n_m)))
```

Components evolve independently in v1; both single-step `T` and Syracuse-collapsed `T_syracuse` are provided.

### Per-lens behavior under one Syracuse step

| Lens | Behavior | Class |
|---|---|---|
| sector | rotates by exactly −30°; period 12 | **Conserved** (cycles, doesn't drift) |
| mod3 | deterministic transition on {1,2}; never 0 | **Conserved** (finite-state attractor) |
| alpha_prefix | left-shift; drops α₁ | **Decaying** (information loss) |
| drop_class | no closed form across steps | **Drifting** |
| slope_log | invariant within subgroup; jumps at exit | **Mostly anchoring** |
| force | monotone-decreasing (~1.42 bits/bounce) | **Decaying** (entropy-like) |

This gives a natural decomposition: anchoring lenses carry identity through iteration; decaying lenses measure how much specificity has been spent. Meaning lives in anchoring lenses; trajectory/age lives in decaying ones.

### Lens-level closed forms (`iteration.advance_lens`)

For lenses with closed-form transformations under T, provide direct lens-space updates without re-running Collatz on integers. v1 starts with `sector` (n → (n−1) mod 12) and `mod3` (deterministic transition table). Other lenses fall back to applying T to the integer and re-evaluating.

### Central empirical question

Does analogy structure survive iteration?

$$\Phi(\text{a}) - \Phi(\text{b}) \approx \Phi(T^k(\text{a})) - \Phi(T^k(\text{b}))$$

If anchoring lenses dominate → analogy persists. If decaying lenses dominate → analogy dissolves on a force-predictable timescale. Both outcomes are informative.

## Experiments (notebook 09)

1. **Lens sanity & fixtures** — verify each lens on hand-checked inputs (`alpha_prefix(7) = (1,1,1)`, etc.).
2. **Pure-concept geometry** — construct fully-pure and mixed concepts; visualize via PCA/UMAP. Pure concepts should cluster tightly; mixed ones sit between.
3. **Hand-built analogy quads** — 5–10 structurally-designed quads. Measure rank of expected d among 50 distractors. Chance baseline = top-5 → 10%; above chance means better than 10%.
4. **Iteration drift & anchoring** — for each quad, iterate components k = 0…10 Syracuse steps. Plot `cosine(Φ(b)−Φ(a), Φ(Tᵏb)−Φ(Tᵏa))` per k. Ablate one lens at a time (zero its axis weights) to identify which lenses carry the analogy.
5. **Open questions for v2** — log surprises and candidate next moves.

## Success criteria

This is research, not a shipping product, so success is *informational*:

- End-to-end path works: construct → Φ → distance → analogy → iterate.
- At least one hand-built analogy is recovered above chance (rank of expected d in top-5 of 50, i.e. > 10% baseline).
- Drift-curve experiment cleanly separates anchoring vs decaying lenses, **or** it doesn't (a clean negative result is also valuable — it tells us the lens basis isn't capturing the structure we expected).
- A concrete v2 hypothesis list emerges from the experiments.

## Future work (v2 candidates)

- **Component coupling.** v1 evolves components independently under T. v2 could couple them — e.g., apply one Collatz step to whichever component has the highest `force`, treating the concept as a single dynamical entity rather than a parallel bundle.
- **Learned lens weights.** Gradient-fit axis weights against a labeled analogy set instead of treating all lenses equal.
- **Longer α-prefixes** or full α-trajectories as a richer dynamical fingerprint — effectively folding Approach B into Approach A as one lens.
- **Cross-component lens correlations** — embed not just Φ(n_i) per i but pairwise differences `sector(n_i) − sector(n_j)`, etc.

## Out of scope (v1)

- Training a model from a corpus — this is a hand-crafted exploration, not a learned embedding.
- Comparison against word2vec / GloVe — interesting but later.
- Variable-length concepts; m fixed at 3 for v1.
