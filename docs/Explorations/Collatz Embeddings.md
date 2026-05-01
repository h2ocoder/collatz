# Collatz Embeddings

A first attempt at treating dynamical invariants as a lens basis on the integers,
turning integer vectors into "concept" embeddings analogous to word2vec.

- **Spec:** [[../superpowers/specs/2026-04-30-collatz-embeddings-design]]
- **Plan:** [[../superpowers/plans/2026-04-30-collatz-embeddings]]
- **Notebook:** `notebooks/09-collatz-embeddings.ipynb`
- **Code:** `collatz/embeddings/`

## Lens basis (v1)

| Lens | Class | What it captures |
|---|---|---|
| sector | conserved (cycles, period 12) | Eisenstein angle |
| mod3 | conserved (finite-state attractor on {1, 2}) | 3-adic state |
| drop_class | drifting | bit-budget |
| alpha_prefix | decaying | leading dynamics |
| force | decaying (entropy-like) | bit-precision / epistemic confidence |
| slope_log | mostly anchoring | affine-class identity |

Anchoring lenses carry meaning through iteration; decaying lenses measure age.

## v1 empirical findings

Hand-built analogy quads of the form `(a, T_syr(a), c, T_syr(c))` against 50 random
distractors:

- **Mean rank of expected d: 11.2** out of 51 (chance baseline: 25.0).
- **One perfect hit** (rank 0/51).
- **`force` is the analogy carrier.** Ablating it doubles mean rank to 23.4; ablating
  any other lens is neutral or slightly improves the rank. The bit-budget lens encodes
  the Syracuse-shift transformation cleanly while the others contribute noise.

This is a *positive but narrow* result: the embedding captures one specific structural
relation (Syracuse-step transformation) via one specific lens. Whether it captures
richer semantic relationships requires v2 work.

## v2 candidates

- **Component coupling.** Apply T to whichever component has highest `force` rather
  than independently — treat the concept as a single dynamical entity.
- **Learned lens weights.** The ablation result above is a primitive form of feature
  importance; gradient-fit weights against a labeled analogy set.
- **Force-binned drift analysis.** Hypothesis: high-force quads preserve analogy under
  iteration longer than low-force quads.
- **Cross-component lens correlations** (`sector(n_i) - sector(n_j)`, etc.) to capture
  internal concept structure.
