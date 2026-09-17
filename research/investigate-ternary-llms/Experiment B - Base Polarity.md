---
tags: [collatz, transformer, base, 2-adic, experiment, charton, loop-L7]
status: verified-with-open-conjecture
created: 2026-09-16
---

# Experiment B — Base Polarity (loop item L7)

**Question.** Charton & Narayanan (arXiv:2511.10811) found that transformers learn the "long Collatz step" far better in bases 16/24/32 (99.7%) than in base 3 (25%). A 2026 grokking paper on the *one-step* map (arXiv:2604.13082) reported the opposite polarity. Which is it, and is base 6 — the repo's lattice base — special?

Script: `scripts/base_polarity.py` (4-layer, d = 256 decoder-only transformer, LSB-first digits, random odd n < 2²⁴, 20,000 steps, exact match on 4,096 held-out n); analysis `scripts/stratify_by_valuation.py`; results `results/base_polarity.json`, `results/stratify_by_valuation.json`, log `results/base_polarity.log`. Total GPU time ≈ 2 h on the RTX 4080 (base 2 is slow: 25-digit inputs).

## Results — Verified

| base | one-step S(n) = (3n+1)/2^v | long step κ(n) (Charton's task) |
|---|---|---|
| 2 | 99.85% | 87.7% |
| 3 | **50.27%** | **17.7%** |
| 6 | 94.56% | 41.0% |
| 16 | 100% | 93.1% |
| 24 | 98.4% | 87.9% |

Same ordering on both tasks: 16 > 24 ≈ 2 > 6 > 3. **Charton–Narayanan's polarity holds on the one-step task in this setup.** Base 6 is not special — it sits between base 3 and base 2 on both tasks, and on the long step it is clearly worse than binary.

**Correction on the "opposite polarity" paper (arXiv:2604.13082).** On reading it: its task is the *full Collatz step* T(n) = n/2 or 3n+1 (not the Syracuse step), its digits are **most-significant first**, and it reports binary "collapsing" while bases divisible by 6 (24: 99.8%) do best. Our setup is LSB-first Syracuse. So the two results are not in conflict — they differ in digit order, and digit order is exactly the variable the mechanism below predicts matters: with MSB-first output, an autoregressive decoder must emit the high digits of 3n+1 before it has read the carries from the low ones, whereas LSB-first makes every carry local. Reproducing their MSB-first result and flipping it to LSB-first would be the clean test; it is not done here. Their "carry depth" statistic is the LSB-first transducer's carry chain — the same object as the [[Ternary Syracuse Circuit]].

## The numbers are cutoffs on the 2-adic ladder, not degrees of skill — Verified

Stratifying the one-step models by v = v₂(3n+1) (P(v = j) = 2^(−j)):

| v | share | base 3 | base 6 | base 2 | base 16 |
|---|---|---|---|---|---|
| 1 | 50.3% | 100% | 100% | 100% | 100% |
| 2 | 25.2% | 0% | 100% | 100% | 100% |
| 3 | 13.0% | 0% | 100% | 100% | 100% |
| 4 | 5.7% | 0% | 100% | 100% | 100% |
| 5 | 2.9% | 0% | 11% | 100% | 100% |
| 6 | 1.1% | 0% | 7% | 100% | 100% |
| 7–8 | 1.3% | 0% | 0% | 100% | 100% |
| 9–13 | 0.5% | 0% | 0% | 0–89% | 100% |

- **Base 3:** every one of the 2,037 wrong answers is exactly (3n+1)/2. The model learned the *Terras* map (halve once) and never determines v. Its accuracy is P(v = 1) = ½ to three digits. Reason: 3^i is odd for every i, so n mod 2^v is a global weighted digit sum in base 3 — there is no local place to read the 2-adic valuation.
- **Base 6:** exact through v = 4, collapse at v = 5. 6^i ≡ 0 (mod 2^i), so n mod 2^v is in the lowest v digits (local), but each halving still has to be *performed*.
- **Base 2:** exact through v = 8; fails only where v ≥ 9, which is 0.5% of the training distribution (no signal), not a capacity limit.
- **Base 16:** exact at every v seen (a hex digit carries 4 bits; v ≤ 13 needs ≤ 4 digits).

Long step, stratified by Charton's (k, k′) — the repo's residue subgroups ([[Neural Networks and Collatz - Prior Work]]):

| (k, k′) | n | base 2 | base 3 | base 6 | base 16 | base 24 |
|---|---|---|---|---|---|---|
| (1,1) | 1031 | 1.00 | 0.49 | 1.00 | 1.00 | 1.00 |
| (1,2) | 533 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| (2,1) | 502 | 1.00 | 0.32 | 0.11 | 1.00 | 1.00 |
| (3,1) | 267 | 1.00 | 0.13 | 0.04 | 1.00 | 1.00 |
| (2,2) | 246 | 1.00 | 0.00 | 0.05 | 1.00 | 1.00 |
| (1,3) | 234 | 1.00 | 0.09 | 0.06 | 1.00 | 1.00 |
| (3,2) | 148 | 1.00 | 0.00 | 0.06 | 1.00 | 0.99 |
| (2,3) | 140 | 1.00 | 0.00 | 0.05 | 1.00 | 1.00 |

Bases 2, 16, 24 are perfect on every subgroup shown; their 7–13% overall loss is in the long tail of rare (k, k′) (base 2's 87.7% = the classes with n ≥ 140 all at 1.00, the rest under-trained). Base 6 is perfect on (1,1) and (1,2) and dead elsewhere. Base 3 is partial on (1,1), (2,1), (3,1) only.

## Why base 6 stops where it does — Conjecture, test running

In base 6 both operations of a Terras step are *one-neighbour local*: multiplying by 3 has carry ⌊3d_{i−1}/6⌋ independent of the incoming carry (3d + c < next multiple of 6 for c ≤ 2), and halving gives digit (6·(d_{i+1} mod 2) + d_i)/2. So a Terras step is one local pass, and each extra halving one more. Pass counts:

- one-step, valuation v: 1 + (v − 1) = **v passes** → exact through v = 4, fails at 5 — matches a 4-pass budget;
- long step (k, k′): k Terras passes + k′ halvings — (1,1) = 2 ✓, (1,2) = 3 ✓, (2,1) = 3 ✗, (1,3) = 4 ✗. The (2,1) failure does *not* fit a pure pass count; the extra cost may be deciding k (reading trailing 1-bits of n through base-6 digits).

The clean test is to vary the number of layers: if the cutoff moves with depth, it is a pass budget. Base 6 with 2 and 8 layers, both tasks, is running (`results/base_polarity_layers.log`); result to be added below.

### Layer test
_(pending)_

## What it means for the repo

1. **A learner's ceiling on a Collatz task is P(v ≤ v_max(base)):** how many low bits the representation exposes cheaply. This is 2-adic determinism (`docs/Conjectures/Odd Stopping Time Spectrum.md`) seen from inside a network — the same fact that made the ternary MLP of [[Experiment A - Ternary Dropping-Set Classifier]] learn classes in order of bits needed.
2. **Report Collatz accuracy by v or by (k, k′), never as one number.** 50% and 94% are cutoffs, not degrees.
3. **Base 6 is the right coordinate for the dynamics (Paper 3), not for reading 2-adic structure:** a base-6 digit is worth exactly one bit of halving, so base 6 lands between 3 and 2.
4. For L9 (ternary vs full precision), the stratified table above is the baseline to compare against.

## Sources

1. F. Charton, A. Narayanan, "Transformers know more than they can tell — Learning the Collatz sequence", arXiv:2511.10811 (2025)
2. L. Gomezjurado Gonzalez, "The Long Delay to Arithmetic Generalization", arXiv:2604.13082 (2026) — the one-step polarity claim not reproduced here
3. [[Neural Networks and Collatz - Prior Work]]; [[Experiment A - Ternary Dropping-Set Classifier]]; `docs/Conjectures/Odd Stopping Time Spectrum.md`
4. Scripts and results listed above; artifact "Halvings by Base" (published for the user, 2026-09-16)
