---
tags: [collatz, ternary, rnn, transducer, mealy-machine, experiment, loop-L11]
status: verified
created: 2026-09-16
---

# Experiment E — A Ternary RNN Rediscovers the Transducer (loop item L11)

**Question.** [[Minimal Ternary Circuit]] found by exhaustive search that the Terras step T(n) = n/2 | (3n+1)/2 needs 5 ternary threshold units per bit; [[Ternary Syracuse Circuit]] notes the underlying object is Shallit–Wilson's LSB-first carry transducer. Does a ternary-weight RNN *trained by gradient descent* on bit streams converge to that machine — and can we tell?

Scripts: `scripts/ternary_rnn.py` (training, extraction), `scripts/rnn_state_match.py` (behavioural matching); results `results/ternary_rnn*.json`, `results/rnn_state_match.txt`, checkpoints `ternary_rnn_*.pt`.

## Setup

- **Task:** bit-serial, LSB first. Input at time t is (start flag, bit t of n); target at time t is bit t−1 of T(n) — the one-step delay *is* the halving. Training sequences 12–32 bits; test on 2,000 random 40-bit n (longer than anything seen in training).
- **Model:** Elman RNN, h_t = ReLU(W_in u_t + W_hh h_{t−1} + b), y_t = σ(w_out h_t + c); every weight matrix a BitNet `TernaryLinear` (absmean quantiser, {−1, 0, +1}·γ, straight-through estimator). Hidden size H = 16 or 64. Full-precision control with the same architecture.
- **The yardstick.** Computed here from the circuit's reachable (p, prev, carry) states by partition refinement: the **minimal Mealy machine of the Terras transducer has 5 states** — a start state (never revisited) and 4 working states. (Shallit–Wilson 1992 give the 3x+1 carry rule with carry ∈ {0, 1, 2}; adding the parity branch and start state gives 5; the count itself appears to be unstated in the literature.)
- **How to tell what the RNN implements.** Binarising hidden activations is useless (64–692 sign patterns for models that are provably right). Instead, *behavioural* states: two reachable hidden states are equivalent if the RNN emits identical outputs on **every** input continuation of length 8 (256 continuations × 8 outputs = 2,048 bits of signature). An exact implementation of the transducer must show exactly 4 classes on states reached after the first input, each matching an ideal state's signature.

## Results — Verified

| model | seeds | exact match, 40-bit n | behavioural classes (ideal: 4) | hidden states matching an ideal state | zero density |
|---|---|---|---|---|---|
| full precision, H = 16, 6k steps | 2/2 succeed | 1.000, 1.000 | 24 | 9703 / 9761 = **99.4%** (58 glitch states, most 1–2 bits from an ideal signature) | — |
| ternary, H = 16, 20k steps, lr 3e-3 | **1/3** succeed | 0.0025, 0.35, **1.000** | — | — | 0.31–0.47 |
| ternary, H = 16, 6k steps, lr 1e-3 | 0/2 | 0.05, 0.02 | — | — | — |
| **ternary, H = 64, 6k steps** | **2/2 succeed** | **1.000, 1.000** | **4** | **9761 / 9761 = 100%**, 0 glitch states | 0.35–0.44 |

Training curves for the failing ternary H = 16 seeds show the STE pathology: loss falls to 0.04 by step 5,000 and then *rises* to 0.2 as quantised weights flip; the successful seed's loss goes 0.0076 → 0.0002 monotonically.

## Reading

1. **Yes — a gradient-trained ternary RNN finds the transducer, exactly.** Both H = 64 ternary models implement a machine with precisely 4 behavioural states after the first input, each state's 2,048-bit signature identical to an ideal state's, with no exceptions over 9,761 reachable hidden states. That is the 5-state minimal Mealy machine (4 + start), realised in {−1, 0, +1} weights. The extracted machine is exact, not approximate.
2. **The ternary model is cleaner than the full-precision one.** The FP H = 16 model is 100% on 2,000 test sequences but has 24 behavioural classes: 0.6% of its reachable states deviate on one or two rare continuations. The ternary H = 64 models have none. Quantised weights and ReLU give crisp, discrete hidden states — the "finite automaton in disguise" is more literally an automaton when the weights are ternary.
3. **Width again.** At H = 16 ternary succeeds in 1 of 3 seeds (and is unstable when it fails); at H = 64 it succeeds 2 of 2 in a third of the steps. Same pattern as [[Experiment A - Ternary Dropping-Set Classifier]] (4× width) and [[Experiment D - Quantization by Subgroup]] (2× width): ternary weights want more units, and then they are fine.
4. **What it does not say.** "Matches the minimal machine" is a statement about the *function computed from every reachable state*, not about the weights being readable as the 5-unit circuit. Given L5's finding that trained ternary weights are distributed rather than residue tests, the internal encoding of the four states in 64 units is almost certainly not the (p, prev, carry) bits; that is a separate (and cheap) question — extract the 4 state clusters and look at their centroids.

Label: **Verified** (behavioural equivalence over all 256 continuations of length 8 from all reachable states; two seeds).

## Sources

1. J. Shallit, D. Wilson, "The '3x+1' problem and finite automata", Bull. EATCS 46 (1992) — the LSB-first carry rule
2. S. Ma et al., "The Era of 1-bit LLMs", arXiv:2402.17764 — absmean quantiser, STE
3. [[Minimal Ternary Circuit]], [[Ternary Syracuse Circuit]], [[Experiment A - Ternary Dropping-Set Classifier]], [[Experiment D - Quantization by Subgroup]]
4. `scripts/ternary_rnn.py`, `scripts/rnn_state_match.py`, `results/rnn_state_match.txt`
