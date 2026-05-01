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

## v3 finding: sector encoding is NOT the cause

Notebook `11-embeddings-v3-angular-sector.ipynb` swapped sector's one-hot
encoding for `(cos(2*pi*s/12), sin(2*pi*s/12))` and re-ran the v2 drift test
on the same 60 quads (same seed).

| | k=1 cosine | sign flips at k=1 | mean drift k=1..8 |
|---|---|---|---|
| one-hot sector | -0.267 | 47/60 | -0.042 |
| angular sector | -0.224 | 45/60 | -0.040 |

The angular fix improved drift by ~0.04 — well within the noise. Sign-flip
count went 47 -> 45, also within noise. The v2 diagnosis was wrong: sector's
discrete encoding is not the dominant source of lens-space discontinuity.

## v4 finding: the k=1 flip is a geometric artifact of one-hot encoding

Notebook `12-embeddings-v4-per-lens-drift.ipynb` projected the drift cosine onto
each lens's subspace alone:

| lens | k=1 cos | flips at k=1 |
|---|---|---|
| sector | -0.486 | **60/60** |
| alpha_prefix | -0.406 | 59/60 |
| drop_class | -0.405 | 51/60 |
| slope_log | -0.325 | 38/60 |
| mod3 | -0.292 | 37/60 |
| **force** | **-0.086** | 31/60 |
| (full Phi) | -0.267 | 47/60 |

Every lens flips. But the *reason* is structural, not dynamical.

**The math:** for a one-hot lens that shifts by one index per Syracuse step
(sector does this provably; alpha_prefix and drop_class do it noisily), the diff
vector `Phi_lens(b) - Phi_lens(a)` at step 0 has support on indices {s, s-1},
one with +1 and one with -1. At step 1 the support shifts to {s-1, s-2}. The two
diff vectors overlap on exactly one index, with opposite signs. Dot product = -1,
norms = sqrt(2) each, **cosine = -1/2 exactly**. sector measured -0.486 -- right at
the predicted -0.5. 60/60 quads, deterministically.

So the v2 "k=1 sign flip" wasn't a discontinuity in Collatz lens-space dynamics.
**It was the natural geometry of cosine on one-hot diff vectors under any shift dynamic.**

**force is the ONLY lens whose temporal behavior cosine can meaningfully measure**,
because it's real-valued. Its k=1 cosine of -0.09 is near-zero (uncorrelated), not
catastrophically negative. This re-validates v1's emphasis on force.

## v5 candidates (post-v4)

- **Real-valued-lenses-only drift test.** Re-run nb 10's force-binned drift
  experiment using only `force` and `slope_log` as the embedding. If those alone
  give a force-anchoring effect, v1's "epistemic confidence persists through iteration"
  interpretation comes back from the dead.
- **Structured per-lens similarity metric.** For sector, define
  `sim_sector(a, b) = 1 if sector(b) = sector(a) - delta_predicted else 0` -- respects the
  rotation. For alpha_prefix, define a left-shift overlap. Combine into a custom metric
  that doesn't naively cosine the one-hot diffs.
- **Trajectory-space embedding** (Approach B from spec). Embed orbits, use orbit-overlap
  distance. Side-steps the encoding issue entirely.
- **Done.** Accept that `Phi` is a working static embedding (force-driven). Use it for
  k=0 similarity / clustering / analogy. Don't try to track concepts through iteration
  in this representation.
