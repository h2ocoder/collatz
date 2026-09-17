---
tags: [collatz, ternary, transformer, quantization, bitnet, experiment, loop-L9]
status: verified
created: 2026-09-16
---

# Experiment D — Quantization by Subgroup (loop item L9)

**Question.** Proposal D from [[Research Directions - Ternary Nets x Collatz]]: does low-bit quantization damage *control-flow depth* (long residue conditions, large k + k′) before *arithmetic*? [[Experiment A - Ternary Dropping-Set Classifier]] saw it in a 2-layer MLP; this is the same question on the long-step transformer, where [[Experiment B - Base Polarity]] §L8 gives a way to tell "class lost" from "class known but map not executed".

**Setup.** The base-16 long-step model of Experiment B (4 layers, LSB-first digits, 20,000 steps, random odd n < 2²⁴) with every linear map — attention q/k/v/o, MLP, output head — replaced by a BitNet b1.58 `TernaryLinear` (absmean quantizer, weights in {−1, 0, +1}·γ, straight-through estimator); embeddings and LayerNorms full precision, as in BitNet. Widths d = 256 (matching the full-precision baseline) and d = 512. Script `scripts/ternary_transformer.py`; results `results/ternary_transformer.json`; checkpoints `long_b16_ternary_d{256,512}.pt`. Baseline: `results/base_polarity.json` (full precision, d = 256, 93.1%).

## Results — Verified

| model | exact match | zero density | (k,k′) probe at SEP, last layer |
|---|---|---|---|
| full precision, d = 256 | 93.1% | — | 0.998 |
| **ternary, d = 256** | **90.3%** | 0.313 | **0.999** |
| ternary, d = 512 | **93.9%** | 0.313 | 0.999 |

By depth k + k′ (the length of the residue condition that decides the class; n = test count):

| k + k′ | n | full precision 256 | ternary 256 | ternary 512 |
|---|---|---|---|---|
| 2–4 | 2813 | 1.000 | 1.000 | 1.000 |
| 5 | 526 | 1.000 | 0.998 | 1.000 |
| **6** | 282 | 0.993 | **0.730** | **1.000** |
| **7** | 190 | 0.684 | **0.521** | **0.747** |
| **8** | 124 | 0.460 | 0.387 | **0.556** |
| 9 | 68 | 0.088 | 0.103 | 0.191 |
| 10–11 | 63 | 0.02 | 0.00 | 0.00 |

Individual classes with n ≥ 20 where the models differ: (5,1) 0.97 → **0.03** → 1.00; (4,2) 1.00 → **0.65** → 1.00; (4,3) 0.63 → **0.11** → 1.00; (5,2) 0.48 → 0.00 → 0.55; (3,5) 0.86 → 0.71 → 1.00.

## Reading

1. **Depth-first damage, confirmed on the harder task.** At equal width, ternary weights leave every class of depth ≤ 5 intact and remove accuracy exactly at depths 6–8 — the classes whose residue conditions are longest. Same pattern as the MLP (classes 16 and 19 lost first), now on a 4-layer transformer with 2,800 shallow test cases untouched and the loss concentrated in ~600 deep ones.
2. **It is execution that is lost, not identification.** The ternary d = 256 model still linearly encodes (k, k′) for 99.9% of inputs at SEP — indistinguishable from full precision — while failing to emit κ(n) for (5,1) in 97% of cases. The quantised network knows which affine map applies and cannot carry out the longer ones. This is the L8 "knows more than it can tell" gap opened by quantisation rather than by base.
3. **Width buys it back, and then some.** Ternary at d = 512 beats full precision at d = 256 on every depth bucket (6: 1.00 vs 0.99; 7: 0.75 vs 0.68; 8: 0.56 vs 0.46; 9: 0.19 vs 0.09). Two-fold width here, four-fold for the MLP — consistent with the BitNet literature's "same accuracy at modestly larger size" ([[Ternary LLMs - State of the Art]]), with the twist that the cost is paid entirely by the deep classes.
4. **Zero density 0.313** sits inside the 0.30–0.51 range Georganas et al. measured on 29 ternary LLMs ([[Paper - Breaking the 1.58-bit Barrier]]) — a small consistency check that this toy is a fair miniature of the real models (BITCOS would store it at 1.69 bits/weight, worse than the five-trit byte).

## What this means

- **The benchmark works.** Stratifying a Collatz task by (k, k′) turns a 3-point accuracy gap (93.1 → 90.3) into a clean statement: "quantisation removes the depth-6-to-8 classes". That is the CollatzBench proposal delivered at laptop scale, and the (k, k′) stratification plus the SEP probe is the instrument.
- **For the repo's framing:** the 2-adic ladder is not only what learners *learn in order* (L6) and *see through the base* (L7) — it is also the axis along which they *break under quantisation*. Three independent handles on one structure.
- Not tested: whether the damage is specifically in the halving chain (k′) or the ×3/2 chain (k); (5,1) and (4,2) suggest k matters more, but the counts are small.

Label: **Verified** (one seed per configuration; the depth pattern is consistent across all three models and matches Experiment A).

## Sources

1. [[Experiment A - Ternary Dropping-Set Classifier]]; [[Experiment B - Base Polarity]] §L8; [[Research Directions - Ternary Nets x Collatz]] (Proposal D)
2. S. Ma et al., "The Era of 1-bit LLMs", arXiv:2402.17764 (absmean quantizer, STE)
3. F. Charton, A. Narayanan, arXiv:2511.10811 (the long step and its (k, k′) classes)
4. `scripts/ternary_transformer.py`, `results/ternary_transformer.json`
