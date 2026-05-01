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

## v2 finding: lens space is NOT smooth under iteration

Notebook `10-embeddings-v2-force-drift.ipynb` tested whether high-force quads
preserve analogies through Syracuse iteration. Result: clean falsification.

- **Cosine of `Phi(b) - Phi(a)` vs `Phi(T(b)) - Phi(T(a))` flips to ~ -0.27 at k=1**, then wanders around 0 for k=2..8.
- Force-tertile binning shows no separation — high/mid/low all decay together within noise.

**Diagnosis:** sector is one-hot encoded, and we proved it decrements by 1 mod 12
per Syracuse step. So the sector segment of every embedding *shifts its support
by one index* every step — vector arithmetic is dominated by orthogonal one-hot
flips, making lens space non-smooth under iteration even though the integer
dynamics underneath are deterministic.

**Updated reading of v1:** force is the analogy carrier *statically* (at k=0),
but it is not a temporal anchor. The "epistemic confidence persists through
iteration" interpretation is not supported.

## v3 candidates (post-v2)

- **Angular encoding of sector.** Replace one-hot with `(cos(2*pi*s/12), sin(2*pi*s/12))`
  so the rotation becomes smooth in lens space rather than a discrete index hop. Re-run drift.
- **Trajectory-space embedding** (Approach B from spec). If static lens space is
  fragile, embed the *whole orbit* (or its alpha-sequence) and use orbit-overlap distance.
- **Component coupling.** Apply T to whichever component has highest force rather
  than independently — treat the concept as a single dynamical entity.
- **Cross-component lens correlations** (`sector(n_i) - sector(n_j)`, etc.) to capture
  internal concept structure.
- **Accept lens space as static-only.** Use `Phi` for similarity / clustering / one-shot
  analogy at k=0; don't expect it to survive iteration.
