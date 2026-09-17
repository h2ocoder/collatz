---
tags: [summary, ternary, llm, collatz, log2-3]
status: complete
created: 2026-09-16
updated: 2026-09-16
jira: SCRUM-28
---

# Summary — Findings and Open Questions

SCRUM-28 asked two things about Georganas, Heinecke & Dubey, *Breaking the 1.58-bit Barrier for Ternary LLMs* (arXiv:2609.16338): can the Collatz research use anything from it, and is there a meaningful way to model neural networks with Collatz computations. The initial survey answered both; the exploration loop ([[LOOP]], items L1–L15) then turned the answers into exact results and experiments. Index: [[00 Index]].

## Findings, ranked

### 1. Prior art for two repo results — Verified on OEIS
The Lattice Path Formula sequence N(s) = 1, 1, 2, 3, 7, 12, 30, 85, … is **A100982** ("admissible sequences": Wagon 1985, Roosendaal 2005, Zarubin, Winkler); the repo's density N(s)/2^(b−1) is the published definition of **Wagon's constant** (A122790); the Odd Stopping Time Spectrum is **A122437** (Noe 2006, "binary digits of 6^(n−1)"). Prior-art sections were added to both repo notes (L4). *Cite, don't claim.*

### 2. N(s) equals the cycle-lemma count exactly at the record trit packings — Verified to s = 1000, iff Conjecture
Winkler's upper bound C(⌊s log₂3⌋, s−1)/s is attained exactly at s = 1, 3, 5, 17, 29, 41, 94, 147, 200, 253, 306, 971 — the upper semiconvergents of log₂3 — and at no other s ≤ 1000. Elsewhere N/upper is a step function of the waste w(s) with breakpoints at w(1) = 2 − log₂3, w(3), w(2) ([[Winkler Tail Bound]]). Corollary: the dropping-set measure is Gibbs-tilted at ln 2 per wasted bit, E[w] = 0.4496 ([[Waste Bias at First Drop]]). **The best candidate for a theorem** — pending a read of Winkler's preprints.

### 3. The 2-adic hierarchy has a rate — Verified
Fraction of odd n undecided by p low bits: U(p) = 2^(−(1 − H(1/log₂3))p + o(p)) = 2^(−0.0500p); explicit U(p) ≤ 0.756·2^(−0.05004p). The repo's "89% by mod 4096" is exactly 911/1024 ([[Exact Admissible Sequence DP]], [[Winkler Tail Bound]]). Rate constant probably classical in substance (Terras/Everett/Lagarias bounds).

### 4. Stopping time = trits + bits; contraction = packing waste — Verified
k(s) = s + bitlen(3^s) = bitlen(6^s); first-drop slope 2^(−w(s)); the five-trit byte *is* Set₁₃ (243/256), the Pythagorean comma *is* 12 trits overflowing 19 bits ([[Collatz Bridge - Trits and Stopping Times]]). A dictionary, and the one that produced finding 2.

### 5. A learner's Collatz accuracy is a cutoff on the 2-adic ladder — Verified (L7, L8, L15)
Same transformer, five bases: one-step 99.85 / 50.27 / 94.56 / 100 / 98.4 % (bases 2/3/6/16/24); long step 87.7 / 17.7 / 41.0 / 93.1 / 87.9 %. Base 3 learns *exactly* the Terras map (100% at v = 1, 0% above, every error = (3n+1)/2); base 6 is exact through v = 4; base 2 through v = 8. Unary input: 1.5% on held-out n, 0% on odd n. Linear probes at SEP decode the affine class (k, k′) at 99.9% from layer 1–3 in bases 16 and 2, and for 81–94% of inputs in base-6 models that execute only 23–57% — "knows more than it can tell", quantified ([[Experiment B - Base Polarity]], [[Tag Systems and the Ternary Circuit]] Q2). Charton–Narayanan's long step is the repo's affine orbit law and their classes are its residue subgroups (verified).

### 6. Ternary quantisation removes the deepest classes first, and width buys them back — Verified (L5, L9)
MLP: classes 16 and 19 lost at width 64, recovered at 256. Transformer on the long step: 93.1 → 90.3% at equal width with the loss entirely at depth k + k′ = 6–8 ((5,1): 0.97 → 0.03) while (k, k′) stays 99.9% decodable; d = 512 ternary beats full precision at every depth ([[Experiment A - Ternary Dropping-Set Classifier]], [[Experiment D - Quantization by Subgroup]]). The (k, k′) stratification plus the SEP probe is a working "CollatzBench".

### 7. Collatz is natively 1.58-bit arithmetic, and ternary nets find the machine — Verified (L10, L11)
The Terras step needs exactly 5 ternary threshold units per bit (exhaustive; no 4-unit circuit) and its minimal Mealy machine has 5 states. A gradient-trained ternary RNN (H = 64) implements exactly those states — behavioural equivalence over all length-8 continuations from all 9,761 reachable hidden states, zero glitches — cleaner than the full-precision control (24 classes) ([[Minimal Ternary Circuit]], [[Experiment E - Ternary RNN Rediscovers the Transducer]]). The transducer itself is classical (Shallit–Wilson 1992); the ternary encoding, the 5, and the RNN result are new but modest. Trained ternary weights are *not* readable residue tests (L5).

### 8. Verifiable delay function — Dead end, with one survivor
Affine law and 2-adic tables are two-sided shortcuts; the 2^p-table jump is exactly the latency attack that shelved MinRoot (p× with 2^p processors). No Collatz VDF exists in the literature. Survivor: Terras's closed-form inverse n ≡ −r(v)·3^(−s) (mod 2^k) makes verification of a k-step transcript one congruence — parallel, Sloth-class, a cheap certification method. Sequentiality of the parity-vector map for k ≫ log n is an open complexity question; rank and degree tests cannot see depth ([[VDF Feasibility - Collatz as a Delay Function]], [[VDF Literature - Sequential Functions]]).

### 9. Tag systems — no equivalence, a good comparison
De Mol's TS(3,2) computes the same map by phase-counting in unary; its running time is orbit sum + odd rounds (exact) and therefore affine per residue class; its length walk is {−1, 0, +1} = Maslov's minimality condition. The three "3"s (alphabet, weights, carry) are different objects. Together the models say the same map is trivial-to-read positionally and universal-in-class by length ([[Tag Systems and the Ternary Circuit]]).

### 10. The paper itself — Dead end, recorded
BITCOS transfers nothing; every structural bridge failed cleanly ([[Paper - Breaking the 1.58-bit Barrier]]).

## Recommendations

1. **Papers:** apply the OEIS citations to any manuscript that presents N(s) or the stopping-time spectrum as new.
2. **Write up finding 2** as a short note after checking Winkler's preprints; a MathOverflow question is the cheap first step.
3. **Write up findings 5–7** as one ML note: "Collatz accuracy is a 2-adic cutoff" — base-3 = Terras map, SEP probes, quantisation by depth, the RNN that finds the 5-state machine. Before that: run 2604.13082's MSB-first setup directly.
4. **Expository piece** ("trits, bits and drops") for the Medium audience.
5. Do not pursue the VDF or BITCOS-structure directions further.

## Open questions
- Proof of the semiconvergent equality (irrational-slope cycle lemma); exact form of the step function F(w).
- Is the one-step base-6 ceiling at v = 4 optimisation or capacity? (8 layers did not move it.)
- Does MSB-first digit order flip the base polarity, as the mechanism predicts?
- How are the 4 machine states encoded in the ternary RNN's 64 units?
- Depth complexity of the parity-vector map for k ≫ log n.

## Verification ledger
Every note carries Verified / Conjecture / Analogy / Dead end labels and names its script; all scripts are in `scripts/`, all outputs in `results/`, and the loop's progress log in [[LOOP]] records each item with its commit. Citations taken only from a paper's reference list are flagged as unverified in the notes that use them.
