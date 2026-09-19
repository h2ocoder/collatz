---
tags: [collatz, admissible-sequences, oeis, wagon-constant, verified, loop-L1]
status: verified
created: 2026-09-16
---

# Exact Admissible Sequence DP (loop item L1)

**Status: Verified.** An O(s²) dynamic program computes N(s) = OEIS A100982 exactly to any order, reproduces the OEIS b-file, and from it the Kraft sum and Wagon's constant to 12 digits. Script: `scripts/admissible_dp.py` (0.5 s to s = 1000). Results: `results/admissible_dp.json`.

## The DP

N(s) counts alpha-prefixes (a₁, …, a_{s−1}) with a₁ = 1, aᵢ ≥ 1 and every partial sum Sᵢ < i·log₂3 — equivalently strictly increasing 1 ≤ S₁ < … < S_{s−1} with Sᵢ ≤ ⌊i log₂3⌋. The comparison is done exactly as 2^S < 3^i (bit lengths), no floats. State = (number of terms i, partial sum S); transition adds any a ≥ 1 while staying under the cap; prefix sums make each layer linear. This replaces the repo's brute-force enumeration (`docs/Conjectures/Lattice Path Formula.md`, "verified to s = 10") and Roosendaal's order-1000 count with something that runs in under a second.

## Checks

| Check | Result |
|---|---|
| N(1..15) vs A100982 | 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, 17637, 51033 — match |
| N(20), N(30), N(50), N(100), N(200) vs the OEIS b-file (all digits) | 5936673; 84141805077; 52028134169251235063; 752276648034035903600966817196471179765521; 656806675415484094200100898233709221596805033311728420917526057942832163142676382702260 — all match [1] |
| Kraft sum Σ N(s)/2^(b(s)−1) | 0.9999999998718 at s = 300; 1 − 4.3×10⁻²⁸ at s = 1000 → **1** (Terras's density-one theorem, numerically exact) |
| Wagon's constant Σ k(s)·N(s)/2^(b(s)−1) | 9.477955556559 at s = 1000 (float64 summation); A122790 = 9.47795555659274736916681… [2] — agree to 11 significant digits, the float precision of the printout; the exact rational partial sum is in the JSON |

Here b(s) = bitlen(3^s) = ⌈s log₂3⌉ and k(s) = s + b(s) is the stopping time (A122437). The densities N(s)/2^(b(s)−1) are densities **among odd n**.

## By-products (all exact)

- **Mean Syracuse steps to first drop** E[s] = 3.492652; **mean halvings** E[b(s)] = 5.985304; sum = Wagon's constant 9.477956. A typical odd n stores ~3.5 trits in ~6 bits before it drops — between the (3, 5) and (5, 8) record packings of [[Trit Packing and log2(3)]].
- **Mean packing waste** E[w(s)] = E[b] − log₂3·E[s] = 0.4496 bits per first drop — the exact value of the "~0.45" partial sum in [[Collatz Bridge - Trits and Stopping Times]] §4. Whether this is a structural bias below 1/2 or just small-s dominance is item L2.
- **Fraction of odd n undecided after p low bits** (1 − Σ_{b(s) ≤ p} dens):

| p (bits) | decided | undecided |
|---|---|---|
| 2 | 0.5000 | 0.500 |
| 4 | 0.6250 | 0.375 |
| 5 | 0.7500 | 0.250 |
| 8 | 0.8516 | 0.148 |
| 12 | **0.8896** | 0.110 |
| 16 | 0.9355 | 0.0645 |
| 20 | 0.9479 | 0.0521 |
| 30 | 0.9762 | 0.0238 |
| 40 | 0.9884 | 0.0117 |

The p = 12 row is the repo's empirical "89% of odd numbers classified by mod 4096" (`docs/Conjectures/Odd Stopping Time Spectrum.md`), now exact: 0.88964844 = 911/1024. The decay is exponential but slow to settle: −log₂U(p)/p falls from 0.26 at p = 12 to 0.059 at p = 1200, approaching the sharp rate 1 − H(1/log₂3) = 0.0500 bits per bit derived in [[Winkler Tail Bound]] (item L3).

## Growth of N(s)

N(300) has 134 digits; N(s) ≈ 2^(b(s)−1)·dens(s) with dens(s) ≈ 6.7×10⁻¹² at s = 300, so N(s) grows like 2^(s log₂3) up to a slowly decaying factor — consistent with Winkler's binomial bounds [1] and the "lattice paths under an irrational slope" asymptotics question in [[Collatz Bridge - Trits and Stopping Times]] §7.

## What this does not say

Convergence of the Kraft sum to 1 is the *density* statement (almost every n drops), which was already Terras's theorem. It says nothing about individual orbits or about the conjecture. The value of this item is (a) exact tooling, (b) exact confirmation that the repo's density formula is the published definition of Wagon's constant, (c) the exact undecided-fraction table.

## Sources

1. OEIS A100982 and b-file (to n = 661) — https://oeis.org/A100982 , https://oeis.org/A100982/b100982.txt
2. OEIS A122790, Wagon's constant — https://oeis.org/A122790
3. OEIS A122437, allowable dropping times — https://oeis.org/A122437
4. `docs/Conjectures/Lattice Path Formula.md`, `docs/Conjectures/Odd Stopping Time Spectrum.md` (this repo)
5. Script: `scripts/admissible_dp.py`; results: `results/admissible_dp.json`
