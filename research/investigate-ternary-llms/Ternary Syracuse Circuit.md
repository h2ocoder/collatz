---
tags: [collatz, ternary, neural-network, threshold-circuit, verified]
status: verified
created: 2026-09-16
---

# Ternary Syracuse Circuit

**Status: Verified.** An exact Collatz computer built from nothing but ternary-weight threshold neurons (weights in {−1, 0, +1}, integer thresholds). This is the "can a neural network run Collatz computations?" question from SCRUM-28 answered in the most literal way: yes, and it needs 11 distinct units.

Script: `research/investigate-ternary-llms/scripts/ternary_syracuse_circuit.py` (≈7 min for the full check suite).

## Why ternary is the natural arithmetic for Collatz

A ternary LLM replaces every multiply-accumulate with additions and subtractions, because multiplying by {−1, 0, +1} is sign-flip, drop, or copy ([[Ternary LLMs - State of the Art]]). Collatz needs only one multiplication ever, and it is by the constant 3:

$$3n + 1 = n + (n \ll 1) + 1$$

So the Syracuse step is a shift-and-add, and shift-and-add is exactly what a ternary network can express with no loss. There is no analogue of this for a general "multiply by w" layer — the fit is specific to constant multipliers.

## Construction

Numbers are streamed least-significant bit first. One recurrent layer computes the Terras map

$$T(n) = \begin{cases} n/2 & n \text{ even} \\ (3n+1)/2 & n \text{ odd} \end{cases}$$

as a carry transducer (a finite-state machine reading bits). Per time step the layer sees `(start, x_i)` and keeps state `(p, x_{i-1}, carry)`:

| Unit | Weights | θ | Computes |
|---|---|---|---|
| `start_and_x` | (1, 1) | 2 | start ∧ x_i (the parity bit, seen once) |
| `latch_p` | (1, 1) | 1 | p ← p ∨ (start ∧ x) — latches parity of n |
| `p_and_prev` | (1, 1) | 2 | p ∧ x_{i−1} — the shifted addend (2n term) |
| `addend` | (1, 1) | 1 | (p ∧ x_{i−1}) ∨ (start ∧ x) — also injects the +1 |
| `sum_ge1` | (1, 1, 1) | 1 | x + g + c ≥ 1 |
| `sum_ge2` | (1, 1, 1) | 2 | x + g + c ≥ 2 → the **carry** (majority) |
| `sum_ge3` | (1, 1, 1) | 3 | x + g + c ≥ 3 |
| `parity` | (1, −1, 1) | 1 | h1 − h2 + h3 = (x + g + c) mod 2 → the sum bit |

The output bit stream is delayed by one position — that single delay *is* the division by 2 (the low bit of n + p(2n+1) is always 0). Stacking K copies of this layer computes T^K(n). A three-unit LSB-first comparator (`b_gt_a`, `a_gt_b`, `lt_update`, weights (∓1, ±1) and (1, −1, 1)) reports the first K with T^K(n) < n. Converting Terras steps to Collatz steps: each odd step counts twice, so stopping time = K + (number of odd steps).

Eleven distinct units, 27 stored weights, all in {−1, +1}, none zero. (BITCOS from [[Paper - Breaking the 1.58-bit Barrier]] would gain nothing here: zero density z = 0.)

## What was verified

| Check | Range | Result |
|---|---|---|
| One layer equals T(n) | all n < 65,536 | 0 mismatches |
| Stacked network stopping time equals `collatz.core.stopping_time` | 2 ≤ n < 20,000 | 0 mismatches |
| Same, random 64-bit n | 300 samples | 0 mismatches |
| n = 27 | — | 96 (matches Paper 1) |
| First 10 parities of T^j(n) depend only on n mod 2^10 | n < 16,384 | 0 mismatches |

The last row is the network-level form of the repo's **2-adic determinism** (`docs/Conjectures/Odd Stopping Time Spectrum.md`): the parity vector (v₀ … v_{K−1}) is a function of n mod 2^K only, which is Terras's 1976 theorem [1]. In circuit terms the parity output of layer j has a *receptive field* of exactly j + 1 input bits. That is why stopping classes are unions of residue classes mod 2^p, and it is what a trained network would have to discover ([[Research Directions - Ternary Nets x Collatz]]).

## Complexity reading

- **Depth** = number of Terras steps to drop; **width** = bit length. Every layer is the same 8-unit block, so this is a weight-tied recurrent network, not a transformer.
- Multiplication by a constant is in TC⁰ (constant-depth threshold circuits), but the *iterated* map is where hardness lives: Conway showed generalised Collatz-type maps are undecidable [2]. The network is a Turing-machine-style unrolling, so it cannot do better than simulation — no "shortcut" layer exists in general. Related literature is collected in [[Neural Networks and Collatz - Prior Work]].
- The carry chain is the only non-local element. A drop is detected by the comparator scanning to the top bit; nothing here escapes the O(bits) per step cost.

## What this does and does not say

- **Does:** Collatz is natively "1.58-bit arithmetic". Any pipeline that runs a ternary LLM already has the hardware primitive (add/sub of bit vectors) that Collatz needs.
- **Does not:** It says nothing about whether a *trained* ternary network would find this circuit. That is an experiment, proposed in [[Research Directions - Ternary Nets x Collatz]].
- **Does not:** It gives no leverage on the conjecture. It re-encodes the map; it does not analyse it.

See [[Collatz Bridge - Trits and Stopping Times]] for the information-theoretic side (stopping time = trits + bits) and [[Summary - Findings and Open Questions]].

## Sources

1. R. Terras, "A stopping time problem on the positive integers", *Acta Arithmetica* 30 (1976), 241–252. https://eudml.org/doc/205476
2. J. H. Conway, "Unpredictable iterations", *Proc. 1972 Number Theory Conference*, Univ. of Colorado, 49–52 (1972). Summarised in J. C. Lagarias, "The 3x+1 problem and its generalizations", *Amer. Math. Monthly* 92 (1985) — https://www.jstor.org/stable/2322189
3. Script: `research/investigate-ternary-llms/scripts/ternary_syracuse_circuit.py` (this repo).
