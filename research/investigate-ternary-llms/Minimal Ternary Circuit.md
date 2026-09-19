---
tags: [collatz, ternary, threshold-circuit, exhaustive-search, verified, loop-L10]
status: verified
created: 2026-09-16
---

# Minimal Ternary Circuit (loop item L10)

**Question.** The hand-built [[Ternary Syracuse Circuit]] computes the Terras map T(n) = n/2 or (3n+1)/2 with an 8-unit recurrent layer of ternary-weight threshold neurons. Is 8 minimal? Does an optimal circuit use zero weights?

**Answer: the minimum is exactly 5 units — Verified by exhaustive search (K ≤ 4 impossible) and end-to-end simulation.**

Scripts: `scripts/minimal_circuit.py` (search, 54 s), `scripts/verify_minimal_circuit.py`; result: `results/minimal_circuit.json`.

## The model of computation

Per input bit (LSB first) the layer sees five lines — `start`, `x` (current bit), and the state `p` (parity of n, latched), `prev` (previous bit), `carry` — and must output

- `y` = (x + g + carry) mod 2 with g = (p ∧ prev) ∨ (start ∧ x) — the sum bit (delayed one step = the halving),
- `p′` = p ∨ (start ∧ x),
- `carry′` = majority(x, g, carry);

`prev′ = x` is a free copy. A unit is [Σ wⱼ·inⱼ ≥ θ] with wⱼ ∈ {−1, 0, +1} over the five lines and any earlier unit of the same step, θ an integer. Only the 14 reachable (start, x, p, prev, carry) combinations matter (start = 1 forces p = prev = carry = 0; p = 0 forces carry = 0).

## Search

- 354 distinct Boolean functions of the 14 rows are realizable by a single ternary threshold unit of the five lines; **none of the three targets is among them**, so K ≥ 4 trivially... and the search shows K = 3 and K = 4 (one helper, any dependency order among targets) are impossible.
- K = 5 succeeds in 6 s:

```
h1     = [ −start −x −p −prev −carry ≥ −2 ]      "at most two lines are on"
carry′ = [ +start +x +carry −h1 ≥ 1 ]
p′     = [ +p −h1 +carry′ ≥ 0 ]
h4     = [ −start −x −p −prev −carry −h1 +carry′ −p′ ≥ −3 ]
y      = [ −start +x −p −carry′ +p′ −h4 ≥ 0 ]
```

Dense weight matrix: 35 weights, 9 zeros → **zero density 0.257**. So yes, the optimal circuit uses zero weights (the hand-built 8-unit circuit, read as a dense matrix over all available inputs, has 48 zeros in 68 weights, density 0.71 — the "27 weights, none zero" figure in the earlier note counted only the wired inputs and is corrected here).

## Verification (end-to-end, not just the truth table)

| Check | Result |
|---|---|
| 5-unit layer vs T(n), all n < 65,536 | 0 mismatches |
| 2000 random 64-bit n | 0 mismatches |
| Stacked layers + 3-unit comparator vs `collatz.core.stopping_time`, 2 ≤ n < 3000 | 0 mismatches |
| n = 27 | 96 ✓ |

## Remarks

- The optimal circuit is *not* human-readable: it exploits the unreachable states (e.g. `h1` = "at most two of the five lines are on", which is a threshold test only because certain combinations never occur). This is the same flavour as the L5 finding ([[Experiment A - Ternary Dropping-Set Classifier]]): the cheapest ternary solution is a distributed encoding, not the AND/majority/parity decomposition a person writes down.
- With the comparator, a complete ternary Collatz stopping-time machine is **8 threshold units** (5 + 3), 3 state bits, weights in {−1, 0, +1}.
- Lower bound is *within this model*: single-layer-per-step, ternary weights, integer thresholds, targets as named. Allowing weight 2 (or duplicated input lines) would change the count; that is a different model.
- Minimality search does not scale past K ≈ 6 in this brute-force form (354 single-unit functions per level); it was not needed.

## Sources

1. [[Ternary Syracuse Circuit]] (the 8-unit construction and its checks)
2. R. Terras, "A stopping time problem on the positive integers", Acta Arith. 30 (1976)
3. `scripts/minimal_circuit.py`, `scripts/verify_minimal_circuit.py`, `results/minimal_circuit.json`
