---
tags: [pinball, signed-primes, units, galois, liouville, exchange-family]
status: verified-with-limits
created: 2026-09-19
jira: SCRUM-30
---

# Signed Primes and the Exchange Family

Idea: a positive number is one whose prime factorization has an even number of negative primes, a negative number an odd number — but nothing says *which* primes are negative. 30 = 2·3·5 = (−2)(−3)·5 = (−2)·3·(−5) = … Is there hidden structure in those choices, given that changing the halving rule for negatives produced the Fibonacci law?

Script: `scripts/signed_prime_experiments.py`. Labels: **Proved**, **Verified**, **Analogy**, **Dead end**.

## 1. What the sign choices are — Proved

A number with k prime factors (with multiplicity) has 2^(k−1) sign assignments with the right product. They form a vector space over 𝔽₂ of dimension k − 1: the kernel of "multiply the signs".

**Dead end, stated precisely.** Any operation defined on the *number* n cannot see the assignment, because every assignment multiplies out to the same n. There are no invariants to find in the assignments themselves. They become visible only to a machine that takes the *list of factors* as its input.

This freedom has a name: the **unit group**. In ℤ the units are ±1 and primes are only defined up to units (2 and −2 are the "same" prime — *associates*). The sign of n is the one unit-invariant quantity.

## 2. Where the idea has real content

**Eisenstein integers — Analogy that becomes mathematics.** ℤ[ω] has six units (the sixth roots of unity). The same idea there attaches a *phase in ℤ/6* to each prime factor, and the invariant is the total phase. The repo already lives there: 3 = −ω²(1 − ω)², the sector lens is a phase in ℤ/12, and rad(6) = 6 keeps appearing. ± signs are the two-element version of the six-fold structure in [[Eisenstein Factorization]].

**"Swap something and the expression stays true" is Galois theory.** The symmetries of a polynomial's roots that preserve every algebraic relation form its Galois group; the Langlands program is, at its base, the study of how primes behave under those symmetries. In this project the relevant instance is small and concrete:

- The Galois group of ℚ(ω)/ℚ has one non-trivial element, ω ↔ ω². It swaps π = 1 − ω with π̄ = 1 − ω².
- 3n + 1 = π·π̄·n + 1 is **unchanged by that swap**. This is exactly "swap the factors and the expression is still true".
- How an ordinary prime p behaves in ℤ[ω] is decided by p mod 3: p ≡ 1 splits into two conjugate primes, p ≡ 2 stays prime (2 is *inert*), and 3 *ramifies* (π and π̄ are associates). That trichotomy is quadratic reciprocity for −3 — the GL(1) case of Langlands — and the repo's `collatz/lfunctions/` Hecke characters are its L-functions.

So the structure being sensed is: **units (which sign/phase) and Galois conjugation (which conjugate factor)**. Both are gauge-like freedoms; invariants are what survive them.

**Canonical sign assignments — Proved.** To give every number a definite sign pattern, fix a set S of primes to be negative. That is a completely multiplicative character χ_S(n) = (−1)^(number of prime factors of n in S). S = all primes gives the **Liouville function** λ(n) = (−1)^Ω(n) — the "parity of negative primes" count, made canonical.

## 3. The mirror map in this language — Proved, Verified

The even step n → n − |n/2| multiplies n by ½ when n > 0 and by 3/2 when n < 0. In factor terms:

- positive: **delete** a 2
- negative: **exchange** a 2 for a 3

Verified for every even m < 400,000: Ω(3m/2) = Ω(m), while Ω(m/2) = Ω(m) − 1. **The mirror even step conserves the number of prime factors; Collatz halving does not.** The 3n + 1 step rebuilds the factorization from nothing, which is the wall every factor-based approach to Collatz hits.

## 4. The exchange family — Verified (E15)

Let each 2 be "negative" with probability p: on each halving, delete the 2 (probability 1 − p) or exchange it for a 3 (probability p). p = 0 is Collatz, p = 1 is the mirror table.

**Prediction.** Per odd step the expected growth is log₂3 − E[α] + p·E[α]·log₂3 with E[α] = 2, which vanishes at

    p_c = (2 ln 2 − ln 3) / (2 ln 3) = 0.1309.

| p | drift (bits / odd step) | predicted |
|---|---|---|
| 0.14 | +0.013 | +0.029 |
| 0.16 | +0.079 | +0.092 |
| 0.25 | +0.375 | +0.377 |
| 0.50 | +1.171 | +1.170 |
| 1.00 | +2.755 | +2.755 |

Deterministic versions straddle the threshold exactly as predicted (1/p_c = 7.64): exchanging every **7th** halving gives drift +0.034 (orbits escape); every **8th** gives −0.053 (orbits drain).

Caveat: below p_c orbits are absorbed near 1, and stopping there biases the measured drift downward (−0.479 measured at p = 0 against −0.415 predicted). The sign change between p = 0.13 and 0.14 is robust; the sub-critical numbers are not unbiased estimates.

**Reading.** Collatz sits at p = 0, well inside the draining phase; the margin is 13% of halvings. This is the same budget as the repo's conservation law seen from a new side: roughly one halving in eight could be "wasted" before the average contraction is lost.

## 5. Liouville signs along orbits — Verified, Negative (E16)

If sign structure in the factorization interacted with the dynamics, λ would correlate across steps. It does not:

- mean λ(n)·λ(3n+1) over odd n < 400,000: +0.0029 (noise scale 0.0022)
- mean λ(n)·λ(Syracuse(n)): −0.0024
- mean λ by stopping class: all within about 1.5 standard errors of 0 (largest: class 11, −0.022 on 4,689 numbers)

The factor-count parity is blind to Collatz structure. This is what the Chowla-type conjectures predict for λ along linear forms, and it is consistent with §1: stopping class is a function of n mod 2^k, and that residue is the product of the factors' residues — a multiplicative-group computation in which a factor and its negative differ only by the unit −1.

## 6. A factor-fed machine — what it could and could not learn

Feeding prime factors one at a time to a recurrent model (as with the ternary RNN of SCRUM-28) is well-posed. To predict stopping class it must carry the running product mod 2^k and then look the class up: a finite-state machine with 2^(k−1) states, the multiplicative analogue of the 5-state Terras transducer. It would be a clean demonstration that *stopping class is a function on the group (ℤ/2^k)^×*, and the learned state graph would be the Cayley graph of that group. It would not reveal new number theory — the structure is known in advance — but it is a good, small distillation exercise with an exactly known target.
