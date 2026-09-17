---
tags: [index, ternary, llm, collatz]
status: complete
created: 2026-09-16
jira: SCRUM-28
task: task-1789596416215-h1u4rh
---

# Investigate Ternary LLMs — Index

**Ticket:** [SCRUM-28](https://alpha36.atlassian.net/browse/SCRUM-28) · **Trigger paper:** Georganas, Heinecke, Dubey, *Breaking the 1.58-bit Barrier for Ternary LLMs*, arXiv:2609.16338 (Sept 2026).

Two questions were asked:

1. The paper lives at log₂ 3 ≈ 1.585 — is there anything in it, or in the trit-to-bit packing it rests on, that the Collatz research can use?
2. Ternary LLMs are new to us — is there a meaningful way to model a neural network with Collatz computations?

Start with [[Summary - Findings and Open Questions]].

## Notes

### The paper and its mathematics
- [[Paper - Breaking the 1.58-bit Barrier]] — what the paper does (five-trit packing, BITCOS = 2 − z bits/weight, kernels, results) and the entropy analysis it leaves implicit.
- [[Trit Packing and log2(3)]] — how many bits t trits need, why 5-in-8 and 41-in-65 are the records, and the continued fraction of log₂ 3 behind them.

### The Collatz bridge
- [[Collatz Bridge - Trits and Stopping Times]] — **Verified:** odd stopping time = s + (minimum bits to store s trits). Plus the other candidate connections, each labelled Verified / Conjecture / Analogy.
- [[Ternary Syracuse Circuit]] — **Verified:** an 11-unit network with weights in {−1, 0, +1} that computes the Terras map and stopping times exactly, and shows 2-adic determinism as a receptive-field property.

### Ternary neural networks
- [[Ternary LLMs - State of the Art]] — what they are, lineage (TWN → BitNet → b1.58 → 2026), training, kernels, hardware, open problems; glossary for non-specialists.
- [[Neural Networks and Collatz - Prior Work]] — transformers learning Collatz, arithmetic in transformers, undecidability, Collatz cellular automata.
- [[Research Directions - Ternary Nets x Collatz]] — proposed experiments, ranked.

### Loop results (see [[LOOP]] for the agenda and progress log)
- [[Experiment B - Base Polarity]] — L7: transformer accuracy by base on one-step and long-step tasks = cutoffs on the 2-adic ladder (base 3 learns only the Terras map); Charton's polarity reproduced; base 6 not special.
- [[Minimal Ternary Circuit]] — L10: the Terras layer needs exactly 5 ternary threshold units (exhaustive, verified end-to-end); optimal circuit uses zeros and is not human-readable.
- [[Experiment A - Ternary Dropping-Set Classifier]] — L5/L6: ternary MLP reaches the Bayes ceiling but its weights are NOT residue tests; quantisation kills the deepest classes first (needs 4× width); learning order = bits needed.
- [[Winkler Tail Bound]] — L3: undecided fraction after p bits is 2^(−0.05 p) (rate 1 − H(1/log₂3), sharp); N(s) equals the cycle-lemma count C(m,s−1)/s exactly at the record trit packings.
- [[Waste Bias at First Drop]] — L2: E[bits shed at first drop] = 0.4496 < 1/2; the dropping-set measure is 2^(−w)-tilted (Gibbs at ln 2 per wasted bit); residual Sturmian dependence of N(s) is open.
- [[Exact Admissible Sequence DP]] — L1: N(s) = A100982 exact to s = 1000; Kraft → 1; Wagon's constant to 12 digits; exact undecided-fraction table.

### Verifiable delay (user question, 2026-09-16)
- [[VDF Feasibility - Collatz as a Delay Function]] — the affine/2-adic structure is a two-sided shortcut; the only one-sided asymmetry is the closed-form inverse of the parity-vector map (verifier: one congruence). Sloth-class at best.
- [[VDF Literature - Sequential Functions]] — definitions, constructions (Wesolowski, Pietrzak, Sloth, MinRoot), attacks, Collatz-in-cryptography search, F₂[x] analogue.

### Wrap-up
- [[Summary - Findings and Open Questions]]

## Scripts
`research/investigate-ternary-llms/scripts/`
- `stopping_time_trit_bits.py` — exact integer check of T = s + bitlen(3^s) and halvings = bitlen(3^s).
- `ternary_syracuse_circuit.py` — the ternary threshold network and its test suite.
- `collatz_packing_check.py` — N(s) = A100982 (three definitions agree), Winkler bounds, prefix-code / Kraft check.
- `packing_records.py` — record trit packings = upper semiconvergents of log₂3; slope = 2^(−waste); Wagon-constant partial sums.
- `admissible_dp.py` — L1: exact N(s) DP, Kraft sum, Wagon's constant, undecided fraction by bits.
- `waste_bias.py` — L2: conditional mean waste by s-window, 2^(−w) prediction, smoothness of N(s)/3^s.
- `winkler_tail.py` — L3: Winkler bounds to s = 1000, U(p) exact and bounded, N/upper vs waste.
- `ternary_classifier.py` — L5/L6: BitNet-style ternary MLP on low bits → dropping set; interpretability and learning-order analysis (GPU).
- `minimal_circuit.py`, `verify_minimal_circuit.py` — L10: exhaustive search for the minimal ternary Terras transducer and its end-to-end check.
- `snark_cost_model.py` — L14: divide-and-conquer identities for evaluator/verifier; constraints per step vs MinRoot.
- `parity_vector_rank.py` — L13: communication-rank test of the parity-vector map vs its inverse; speculative-execution bound.
- `parity_vector_vdf.py` — VDF: closed-form inverse of the parity-vector map, table tradeoff, ANF degrees, evaluator/verifier timing.
- `base_polarity.py`, `stratify_by_valuation.py` — L7: transformer base sweep (GPU) and stratification by v₂(3n+1) / (k,k′).
- `entropy_bitcos.py` — H(z), BITCOS overhead 1 − h(z), arithmetic-coding savings over the 29 models.

## Related repo docs (other vault)
- `docs/Conjectures/Odd Stopping Time Spectrum.md`
- `docs/Conjectures/Lattice Path Formula.md`
- `docs/Explorations/Dropping Zeta Spectrum.md` (Sturmian sign rule, Three Distance, CF tower)
- `docs/Explorations/Collatz Embeddings.md`
