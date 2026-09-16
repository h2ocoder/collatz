---
tags: [summary, ternary, llm, collatz, log2-3]
status: complete
created: 2026-09-16
jira: SCRUM-28
---

# Summary — Findings and Open Questions

SCRUM-28 asked two things about Georganas, Heinecke & Dubey, *Breaking the 1.58-bit Barrier for Ternary LLMs* (arXiv:2609.16338): can the Collatz research use anything from it, and is there a meaningful way to model neural networks with Collatz computations. Index: [[00 Index]].

## Findings, ranked

### 1. Prior art for two repo results — Verified on OEIS
Chasing the packing arithmetic 3^t ≤ 2^b through OEIS found that:
- the Lattice Path Formula sequence N(s) = 1, 1, 2, 3, 7, 12, 30, 85, … is **OEIS A100982**, "admissible sequences" (Wagon 1985; Roosendaal to order 1000, 2005; Zarubin's recursion; Winkler's binomial bounds), and the repo's density N(s)/2^(b−1) is the published definition of **Wagon's constant** 9.4779… (A122790);
- the Odd Stopping Time Spectrum k = ⌈s log₂6⌉ is **OEIS A122437** (Noe 2006), "number of binary digits of 6^(n−1)".

Both repo notes should cite these rather than claim novelty. Winkler's bounds C(m−1, s−1)/s ≤ N(s) ≤ C(m, s−1)/s (m = ⌊s log₂3⌋, verified s ≤ 12) supply the growth rate the repo lacks. Details: [[Collatz Bridge - Trits and Stopping Times]] §3.

### 2. Charton & Narayanan's "long Collatz step" is the repo's affine orbit law — Verified
Their κ(n) = ((3/2)^k (n+1) − 1)/2^k′ equals, within each (k, k′) class, (3^k/2^(k+k′))·n + (3^k − 2^k)/2^(k+k′) — the repo's dest(n) = (3^s/2^(k−s))·n + C. Checked for all odd n < 20,000 (0 violations); their learned classes land on the repo's residues: (1,1) → 1 mod 8, (2,1) → 11 mod 16, (1,2) → 13 mod 16, (3,1) → 7 mod 32. So **a transformer trained on Collatz learns one dropping-set subgroup at a time, in order of k + k′** — their mod-2^p learning ladder *is* the repo's 2-adic determinism table, and their k (trailing 1-bits) is the repo's v₂(m+1) countdown. Their accuracy: 99.7% (bases 24/16/32) down to 25% (base 3); >90% of failures are correct arithmetic with an underestimated loop length. Details: [[Neural Networks and Collatz - Prior Work]] §1.

### 3. Stopping time = trits + bits; contraction = packing waste — Verified
Odd stopping time k(s) = s + bitlen(3^s) = bitlen(6^s): the halvings in a stopping orbit are *exactly* the minimum bits to store s trits (0 violations, odd n < 10⁶ and random 128-bit n). The first-drop contraction is 2^(−w(s)) where w(s) is the packing waste, so the record trit packings (5-in-8 = Set₁₃ with slope 243/256; 41-in-65) are the weakest-contracting dropping sets and the lower convergents (12, 53 — the Pythagorean comma) the strongest. The two families of "special s" already in the repo are the two sides of one continued fraction. Restatement of proved results, not a new theorem; it does not bound s. [[Collatz Bridge - Trits and Stopping Times]] §1–2.

### 4. Collatz is natively 1.58-bit arithmetic — Verified
An 11-unit network with weights in {−1, 0, +1} (threshold neurons; 3n+1 = n + (n≪1) + 1 as a carry transducer) computes the Terras map and stopping times exactly (27 → 96) and shows 2-adic determinism as a receptive-field property. Ternary LLM hardware (add/sub only) is the right primitive for Collatz; the network re-encodes the map, it does not analyse it. [[Ternary Syracuse Circuit]].

### 5. The paper itself: nothing transfers — Dead end
BITCOS is a storage layout (presence bitmap + compacted signs, 2 − z bits/weight) plus SIMD/GPU kernels; speedups 1.1–1.28×. Its implicit information theory is worked out in [[Paper - Breaking the 1.58-bit Barrier]] §7: source entropy H(z) = h(z) + (1 − z) peaks at log₂3 at z = 1/3, so the "barrier" is the *maximum* of the true bound; BITCOS is per-symbol Huffman for z ≥ 1/3 with overhead 1 − h(z) (mean 0.026 bpw over 29 models). Every proposed bridge from BITCOS's structure to Collatz failed cleanly: presence/sign vs 2-adic/3-adic (Collatz has no zero symbol — the 3-adic lock gives the *opposite* statistics), zero density z ≈ 1/3 vs odd-step density (true value 1/log₂6 = 0.387), 128-block padding vs Three Distance (byte alignment, already optimal). One real identity: BITCOS's tie point 2 − log₂3 is the Collatz per-step drift — the same subtraction, labelled Analogy only.

### 6. Ternary LLMs, for the record
Weights in {−1, 0, +1} turn every matmul into add/subtract; lineage TWN/TTQ (2016) → BitNet (2023) → BitNet b1.58 (2024) → 2B4T, bitnet.cpp, ParetoQ (2025) → Bonsai 27B, Maple 20B-A1B, CAT-Q (2026). Trained with quantization-aware training and the straight-through estimator; accuracy near full precision at scale; nobody has trained a ternary or low-bit net on any Collatz task. [[Ternary LLMs - State of the Art]].

## Recommendation

1. **Do now (no ML):** cite A100982 / A122437 / Winkler in `docs/Conjectures/Lattice Path Formula.md` and `Odd Stopping Time Spectrum.md`; import Winkler's bounds as the N(s) growth rate. Separate ticket.
2. **Best cheap experiment:** proposal A in [[Research Directions - Ternary Nets x Collatz]] — a ternary-weight classifier of dropping set from the low bits of n. Tests whether learned ternary weights are literally readable as residue tests (±1 = bit constraint, 0 = don't-care). Laptop, minutes.
3. **Most citable:** proposal D, "CollatzBench" — evaluate ternary vs full-precision models on Collatz tasks *stratified by (k, k′)*, i.e. by dropping-set subgroup, to see whether low-bit quantization preferentially destroys control-flow depth rather than arithmetic. No training needed.
4. **Do not pursue:** anything built on BITCOS's zero density or presence/sign split.

## Open questions

- Explicit tail bound for densities N(s)/2^(b(s)−1) from Winkler's bounds — enough to quantify "89% by mod 4096 → 100%"?
- Is E[w(s)] under the dropping-set measure 1/2, or biased low (~0.45 from partial sums)? A bias would mean drops are systematically tighter packings than random.
- Base polarity: Charton & Narayanan find binary-friendly bases (16, 24, 32) easiest for the long step; a 2026 grokking paper on the *one-step* map (arXiv:2604.13082) reports the opposite. Cheap to probe; is base 6 special?
- Does a trained ternary net on proposal A recover the residue structure, and in what order (k + k′)?
- Asymptotics of lattice paths under an irrational slope (Nakamigawa–Tokushige; Banderier–Wallner's announced sequel) for N(s).

## Verification ledger

| Claim | Script / check | Status |
|---|---|---|
| k = s + bitlen(3^s), halvings = bitlen(3^s) | `scripts/stopping_time_trit_bits.py` | 0 violations, odd n < 10⁶ + 20k random 128-bit |
| Ternary network = Terras map and stopping time | `scripts/ternary_syracuse_circuit.py` | 0 mismatches (n < 65,536 / n < 20,000 / 300 random 64-bit) |
| N(s) = A100982; three definitions agree; Winkler bounds | `scripts/collatz_packing_check.py` | s ≤ 12, all agree |
| Record packings = upper semiconvergents; slope = 2^(−w) | `scripts/packing_records.py` | t ≤ 20,000 |
| H(z), BITCOS overhead, arithmetic-coding savings | `scripts/entropy_bitcos.py` | 29 models |
| Long step = affine law; (k,k′) → residues | inline check (main agent) | 0 violations, odd n < 20,000 |

## Citations not independently verified
Tequila (2509.23809), TWLA (2606.13054), Sherry (2601.07892), T-MAC / LUT-NN / TernGEMM / TABv2 — taken from Georganas et al.'s reference list and flagged in-note. Conway 1972 via secondary sources. Winkler's 2026 ResearchGate preprints seen only via the OEIS citation.
