---
tags: [collatz, ternary, neural-network, experiment, bitnet, loop-L5, loop-L6]
status: verified
created: 2026-09-16
---

# Experiment A — Ternary Dropping-Set Classifier (loop items L5, L6)

The cheapest experiment from [[Research Directions - Ternary Nets x Collatz]]: train a BitNet-style ternary-weight MLP to predict the dropping set of odd n from its low bits, and ask whether the learned {−1, 0, +1} weights are literally readable as residue tests.

Script: `scripts/ternary_classifier.py` (106 s on the RTX 4080); results: `results/ternary_classifier.json`.

## Setup

- **Data:** all odd n < 2¹⁶ (32,768), 20% held out. Target = dropping set k ∈ {3, 6, 8, 11, 13, 16, 19} or "≥ 21" (8 classes; counts 16384 / 4096 / 4096 / 1536 / 1792 / 768 / 480 / 3616). Class k with s Syracuse steps is decided by n mod 2^b(s), b = k − s: 2, 4, 5, 7, 8, 10, 12 bits — so with bits 0…11 every class is exactly decidable (`docs/Conjectures/Odd Stopping Time Spectrum.md`).
- **Input:** bits 1…B of n as ±1 (bit 0 is always 1).
- **Model:** Linear(B, H) → ReLU → Linear(H, 8), both layers with the BitNet b1.58 absmean quantizer (W_q = round(W/γ) ∈ {−1, 0, +1}, γ = mean|W|) and a straight-through estimator; real biases. Adam, lr 0.02 cosine, 3000 full-batch steps.
- **Why the residue-test question is sharp:** with ±1 inputs and ±1 weights, a hidden unit whose quantized weights are ±1 on bits 1…j and 0 elsewhere, with threshold j − ½, fires **exactly** when n ≡ r (mod 2^(j+1)), r read off the signs. So "readable as a residue test" = "prefix support and firing pattern equal to the exact test", checkable unit by unit.

## (i) Accuracy vs bits shown — Verified

| B (bits shown) | Bayes ceiling | ternary test acc | gap |
|---|---|---|---|
| 1 | 0.625 | 0.614 | −0.011 |
| 2 | 0.713 | 0.711 | −0.002 |
| 4 | 0.860 | 0.856 | −0.005 |
| 6 | 0.928 | 0.923 | −0.005 |
| 8 | 0.968 | 0.960 | −0.008 |
| 10 | 0.985 | 0.976 | −0.009 |
| 11 | **1.000** | 0.980 | −0.020 |
| 15 | 1.000 | 0.978 | −0.022 |

The Bayes ceiling (majority class per residue mod 2^(B+1)) is the 2-adic determinism table: 62.5% at 2 bits, 71% at 3, …, 100% at 12. The ternary net (H = 64) tracks it to within 1% while the ceiling is below 1, then **plateaus at 98% once 100% becomes possible**. Showing extra irrelevant bits (B = 12…15) does not hurt: the net learns to ignore them.

## Control: is the 2% plateau ternary or optimisation? — Verified: ternary

| model | H | steps | test acc | class 16 | class 19 |
|---|---|---|---|---|---|
| ternary | 64 | 3000 | 0.980 | 0.83 | **0.00** |
| full precision | 64 | 3000 | **1.000** | 1.00 | 1.00 |
| ternary | 256 | 3000 | **1.000** | 1.00 | 1.00 |
| ternary | 256 | 10000 | 1.000 | 1.00 | 1.00 |
| ternary | 1024 | 3000 | 1.000 | 1.00 | 1.00 |

Same data, same optimiser. Full precision solves it at width 64; ternary needs ~4× the width, and what it loses at width 64 is exactly the two **deepest** classes (16 needs 10 bits, 19 needs 12) — the shallow ones are perfect. This is the [[Research Directions - Ternary Nets x Collatz]] Proposal D hypothesis ("quantisation damages control-flow depth before arithmetic") observed at toy scale: the damage lands on the classes with the longest residue conditions, i.e. the largest k + k′ in Charton–Narayanan's terms ([[Neural Networks and Collatz - Prior Work]]).

## (ii) Are the ternary weights readable as residue tests? — Verified: no

Three seeds at B = 11, H = 64:

| seed | dead units | prefix-support units | fire exactly as a residue test | of those, test a pure class |
|---|---|---|---|---|
| 0 | 3 | 4 | 1 | 1 |
| 1 | 7 | 5 | 0 | 0 |
| 2 | 4 | 6 | 1 | 1 |

The one exact residue test that appears is the trivial n ≡ 1 (mod 4) → class 3 (weight +1 on bit 1 only). Everything else has 3–5 non-zero weights on **non-contiguous** bits (support-size histogram at seed 0: {1: 3, 2: 4, 3: 10, 4: 16, 5: 16, 6: 6, 7: 6, 8: 2}) and does not fire as any single residue test. The representation is distributed: dropping sets are computed as sums of several partial-parity features, not as the hand-built AND-of-bits tests of the [[Ternary Syracuse Circuit]]. Gradient descent with the absmean quantiser does not find the sparse "human" circuit even when it exists and would be cheaper.

## (iii) Zero density — Verified

Quantised zero density: layer 1 **0.60–0.63**, layer 2 0.39–0.42 (three seeds). Higher than the 0.30–0.51 measured across 29 ternary LLMs in [[Paper - Breaking the 1.58-bit Barrier]]; BITCOS would store layer 1 at 2 − 0.62 = 1.38 bits/weight. No Collatz meaning — it reflects the absmean quantiser on a small input — recorded for completeness (Proposal F in the directions note: still a dead end).

## (L6) Learning order — Verified

First training step at which each class's held-out accuracy reaches 0.9 (seed 0, H = 64):

| class | bits needed | step |
|---|---|---|
| 3 | 2 | 50 |
| 6 | 4 | 50 |
| 8 | 5 | 50 |
| 11 | 7 | 50 |
| 13 | 8 | 100 |
| ≥21 (rest) | 12 | 350 |
| 16 | 10 | 500 |
| 19 | 12 | never |

Monotone in the number of low bits the class needs (the "≥ 21" catch-all is large and easy). This is the same ladder Charton & Narayanan report for their transformer — classes learned in order of k + k′, i.e. of the modulus 2^p that decides them — reproduced here in a 2-layer ternary MLP on a different task. The learning order is the 2-adic determinism table read top to bottom.

## Verdict

- **Positive:** a ternary MLP learns the 2-adic classification to the Bayes ceiling wherever it has capacity; learning order = register size; extra bits are ignored.
- **Negative (the interesting one):** the learned ternary weights are *not* residue tests. Proposal A's central hypothesis is refuted for gradient-trained absmean nets. The exact circuit exists ([[Ternary Syracuse Circuit]]) but is not what training finds.
- **New:** ternary quantisation removes the deepest classes first and costs ~4× width to recover — a clean, cheap instance of the quantisation-vs-depth question for L9.

## Sources

1. [[Research Directions - Ternary Nets x Collatz]] (Proposals A, D, F); [[Ternary Syracuse Circuit]]; [[Neural Networks and Collatz - Prior Work]] §1
2. S. Ma et al., "The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits", arXiv:2402.17764 (absmean quantiser, STE) — https://arxiv.org/abs/2402.17764
3. F. Charton, A. Narayanan, "Transformers know more than they can tell — Learning the Collatz sequence", arXiv:2511.10811 — https://arxiv.org/abs/2511.10811
4. `docs/Conjectures/Odd Stopping Time Spectrum.md` (2-adic determinism table)
5. `scripts/ternary_classifier.py`, `results/ternary_classifier.json`
