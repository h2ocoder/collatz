---
tags: [pinball, integer-model, system-one, distillation, results]
status: verified
created: 2026-09-19
jira: SCRUM-30
---

# Integer Decision Model

Code: `collatz/pinball/` · tests: `tests/test_pinball.py` (23) · experiments: `scripts/pinball_experiments.py` · raw numbers: `results/pinball_experiments.json`.

## The model

1. **Encode.** A state (bits, text, or a JSON-like dict) becomes feature bits. Text is tokenized to words and bigrams and hashed with crc32 into a fixed width (`encode_state`).
2. **Launch.** A member reads up to `depth` feature bits in its own order and packs them above a forced low 1 bit: an odd integer (`launch_integer`).
3. **Route.** The integer is played on a qx+c table. The lane is the parity word up to the drain (`PinballTable.lane`).
4. **Count.** Training adds one integer count per example to its lane and to every prefix of the lane (`fit`). Unseen lanes back off to the longest seen prefix.
5. **Decide.** A lane posterior is `(count + a) / (total + a·K)`, a `Fraction`. Members are combined by an exact mean or product. The result is a `Decision`: choice, full distribution, confidence, `score()`, `probability_of(label)`.
6. **Distil.** `fit_soft` adds a teacher's probabilities as fixed-point integer weights instead of one hard count.

No float appears in fit or decide. Probabilities sum to exactly 1 (tested). The ECE *metric* accumulates confidences in 2⁻³² fixed point, because summing a thousand exact fractions with unrelated 6000-bit denominators costs minutes per model (measured: 4.8 s for 300, growing superlinearly).

## Controls

Every ensemble comparison reuses the same members' bit orders; only the router changes.

- **Fixed-depth prefix**: reads the same bits, never drains early. Tests whether the Collatz drain schedule helps.
- **Scrambled lanes**: plays the table on crc32(n), so the lane-size distribution is identical but lanes pool unrelated inputs. Tests whether lane coherence matters.

## Results

Ensembles: 64 members, depth 8. "Learned order" = each member reads a random subset of bits sorted by the integer informativeness score `bit_scores`. One train/test split per task unless stated; no variance estimates except where noted.

### Task A — stopping class of odd n < 2¹⁶ from its low 10 bits (8 labels)

| Model | Accuracy | ECE |
|---|---|---|
| Exact Bayes ceiling (population) | 0.9854 | — |
| **Pinball 3x+1, single table** | **0.9834** | **0.039** |
| Control: fixed-depth prefix | 0.9834 | 0.294 |
| Control: scrambled lanes | 0.5112 | 0.019 |
| Integer decision tree (depth 10) | 0.9834 | 0.031 |
| Integer naive Bayes | 0.8367 | 0.088 |

**Verified:** trained on the whole population with no smoothing, lane posteriors equal the exact Bayes posterior per residue (`test_model_matches_exact_bayes_posterior`). On a 50/50 split the table reaches the ceiling and is 7.5× better calibrated than the fixed-depth router, because its lanes pool data along exactly the right boundaries. A greedy tree rediscovers the same partition.

### Task B — synthetic boolean functions, 15 bits, 2000 train / 2000 test

Accuracy (ECE in brackets):

| Model | Majority | Weighted threshold | Parity of 3 bits | Noisy rule (ceiling 0.875) |
|---|---|---|---|---|
| Pinball 3x+1, random order | 0.868 (0.30) | 0.847 (0.28) | 0.703 (0.19) | 0.715 (0.18) |
| Control: fixed-depth, random order | **0.958** (0.32) | 0.927 (0.29) | 0.864 (0.32) | 0.801 (0.22) |
| Control: scrambled, random order | 0.878 (0.35) | 0.833 (0.30) | 0.759 (0.25) | 0.589 (0.07) |
| Pinball 3x+1, learned order | 0.752 (0.16) | 0.799 (0.17) | 0.733 (0.21) | 0.715 (0.12) |
| Control: fixed-depth, learned order | 0.896 (0.24) | 0.920 (0.26) | **0.995** (0.41) | 0.795 (0.20) |
| Pinball mixed qx+c, learned order | 0.832 (0.22) | 0.854 (0.22) | 0.879 (0.35) | 0.713 (0.12) |
| Integer naive Bayes | **0.993** (0.24) | **0.961** (0.21) | 0.495 (0.05) | 0.675 (0.02) |
| Integer decision tree (depth 8) | 0.754 (0.07) | 0.839 (0.03) | 0.703 (0.10) | **0.806** (0.07) |

**Finding:** off Collatz data, the drain schedule hurts. The fixed-depth control beats the 3x+1 router on every task, by 8–26 points. Cause: half of all balls drain after reading one feature bit, so most members are one-bit stumps. The fixed-depth ensemble is a respectable integer model in its own right (it solves 3-bit parity, which naive Bayes cannot, and beats the tree on three of four tasks), but it is badly under-confident (ECE 0.2–0.4): mean-combining many weak posteriors pulls confidence toward 1/2.

### Task C — SMS spam (UCI), 4459 train / 1115 test, 512 hashed bits, majority class 0.868

| Model | Accuracy | ECE |
|---|---|---|
| Pinball 3x+1, random order | 0.868 | 0.003 |
| Control: fixed-depth, random order | 0.868 | 0.116 |
| Pinball 3x+1, learned order, mean | 0.875 | 0.099 |
| Control: fixed-depth, learned order | 0.905 | 0.073 |
| Control: scrambled, learned order | 0.868 | 0.136 |
| Pinball mixed qx+c, learned order | 0.883 | 0.102 |
| Pinball 3x+1, learned order, product | 0.909 | 0.084 |
| **Pinball 3x+1 distilled from naive Bayes** | 0.899 | 0.137 |
| Integer naive Bayes | 0.885 | 0.101 |
| Integer decision tree (depth 8) | **0.934** | 0.035 |

**Finding:** with random bit order nothing beats the majority class — 8 random bits out of 512 sparse ones carry no signal. Learned routing is what makes the model work at all. The best pinball variant (product combine, 0.909) beats naive Bayes on the same features but loses to a plain tree. All numbers here are weak in absolute terms: a 512-bit hashed signature is a lossy encoder (bag-of-words naive Bayes is commonly reported near 0.98 on this dataset; not reproduced here).

### Distillation

| Student | Hard labels | Soft labels | Gain |
|---|---|---|---|
| Noisy rule, 300 examples, oracle teacher, 3x+1 student (mean of 5 seeds) | 0.695 | 0.704 | +0.9 |
| Same, fixed-depth student (mean of 5 seeds) | 0.690 | 0.737 | +4.7 |
| SMS spam, naive Bayes teacher, 3x+1 student (one split) | 0.875 | 0.899 | +2.4 |

**Finding:** soft labels help, and help more when the student has the capacity to use them (fixed-depth > 3x+1). On SMS the distilled student beats both its hard-label twin and its own teacher (0.899 vs 0.885) — the usual "student regularized by teacher" effect, on one split, so treat it as suggestive.

## Why Collatz routing cannot beat bit truncation — Verified

The Terras bijection: the first D parities of n and n mod 2^D determine each other. So a table played to full depth partitions inputs **exactly** as reading D low bits does. Collatz dynamics carry no information the bits do not; the only thing a table contributes is a rule for stopping early. That rule is optimal when the label is the drain itself (Task A) and arbitrary otherwise (Tasks B, C).

This settles the ticket's third question. **An integer-only System One model is feasible, and this repo now has one. Collatz primitives are the right inductive bias for Collatz questions and a handicap for everything else.**

## What would make it better (not done)

- Calibrate the ensemble (the mean is under-confident, the product over-confident): fit a single integer temperature on held-out data.
- A less lossy text encoder (wider signature, or per-member hashing so collisions differ between members).
- Hill-climbing over bit orders against held-out accuracy, instead of the one-shot `bit_scores` ranking.
- A float teacher trained with torch, to practise the gradient side of distillation. The count-model student needs no change.
