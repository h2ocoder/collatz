---
tags: [pinball, mirror-map, zeta-function, golden-mean-shift, dropping-zeta]
status: verified-with-limits
created: 2026-09-19
jira: SCRUM-30
---

# Zeta Functions: Age Words versus Dropping Sets

Question: the mirror map's constraint produces Fibonacci numbers. Does it have a zeta function, is it new, and can research questions be put to it?

Labels: **Proved**, **Verified**, **Known** (textbook), **Analogy**, **Hypothesis** (testable, not tested).

## 1. The age-word zeta function — Proved, and Known

Count N_t = residues mod 2·3^t with age ≥ t. Then N_t = F(t+3) and

    A(z) = Σ N_t z^t = (2 + z) / (1 − z − z²).

Verified: the series coefficients 2, 3, 5, 8, 13, 21, 34, 55, 89 equal the exhaustive counts for t = 0..8. Setting z = 1/3 and halving gives Σ P(age ≥ t) = 2.1, so the mean age is 1.1 (matches E6).

The denominator is the whole story. 1/(1 − z − z²) = 1/det(I − zM) with M = [[1,1],[1,0]] is the **Artin–Mazur zeta function of the golden-mean shift** — the standard first example in symbolic dynamics (Lind & Marcus, *An Introduction to Symbolic Dynamics and Coding*; Bowen–Lanford). It is not a new function. Winkler's transfer matrix is the same M.

**It is completely understood.**
- Rational, so it continues to the whole plane with no work.
- Exactly two poles: z = 1/φ and z = −φ. Their product is −1, so the pole set is symmetric under z ↦ −1/z.
- With z = 3^(−s) the poles lie on the two vertical lines **Re(s) = ± log₃φ = ± 0.4380**, repeating with period 2πi/ln 3, and the symmetry becomes s ↦ −s + iπ/ln 3.
- For the forward family (no "00", Reyes Jiménez's count) the series is (1 + z)/(1 − z − z²) with z = 2^(−s): poles on **Re(s) = ± log₂φ = ± 0.6942**. The right-hand line is the Hausdorff dimension of the exceptional set (0.694, see [[Mirror Experiments]]). That the leading pole equals the dimension is Bowen's formula — **Known**.

So this zeta function satisfies a toy "Riemann hypothesis" — all singularities on vertical lines, with a reflection symmetry — for the same reason the zeta function of a curve over a finite field does: it is a rational function coming from a finite matrix. **Analogy**, and an old one. There is nothing left to discover about this function itself.

## 2. The contrast with the repo's dropping zeta

`docs/Explorations/Dropping Zeta Spectrum.md` studies g(z) = Σ |R_k| z^k, where |R_k| counts residues mod 2^k that first drop at step k, and finds (Part 1): the dominant root approaches z = 1/2 (s = 1); the other roots do **not** lie on a line; they drift toward Re(s) = log₂(3/2) ≈ 0.585 as the truncation grows (Jentzsch's theorem: zeros of partial sums pile up on the circle of convergence); spacings are more rigid than GUE.

The mirror side explains *why* that happened, by showing what the easy case looks like:

| | constraint | recognised by | generating function | singularities |
|---|---|---|---|---|
| age words; no-"00" family | a forbidden factor | a 2-state machine | **rational** | 2 poles, on vertical lines |
| paths under a line of **rational** slope p/q | first passage over a line | a counter (unbounded memory) | **algebraic** (kernel method; Catalan-like) | a branch point at the radius of convergence |
| dropping sets: paths under slope **log₂3** | first passage over an irrational line | nothing finite | neither rational nor algebraic (expected) | unknown; numerics suggest a natural boundary |

Correction to something said in conversation: a rational-slope constraint is **not** finite-state — the distance below the line is unbounded — so it gives an algebraic, not a rational, generating function. Only forbidden-factor constraints give rational ones.

**The dropping zeta has no critical line because it is not the zeta function of a finite-state system.** The mirror map is the finite-state shadow of the same dynamics, and its zeta has the clean structure the dropping zeta was hoped to have.

## 3. What can be asked — Hypotheses

The function in §1 is closed. The research questions live in the gap between rows 1 and 3 of the table.

**H1. Rational-slope approximants.** Replace log₂3 by its convergents 3/2, 8/5, 19/12, 65/41, 84/53. For each, the first-passage counts |R_k^(p/q)| have an algebraic generating function with a computable branch point ρ(p/q). *Prediction:* ρ(p/q) → 2/3 (the 3/2 growth rate, s = 0.585) monotonically along convergents from each side, and the algebraic degree grows with q. *Test:* count by DP for k ≤ 400, fit the growth rate and the k^(−3/2) prefactor. *Prior art to check first:* Banderier & Wallner on lattice paths below lines of rational and irrational slope (kernel method) — cited from memory, not verified.

**H2. Does the exchange family have a rational zeta at every p?** In [[Signed Primes and the Exchange Family]] each 2 is deleted or exchanged. At p = 1 (mirror) the age zeta is rational. At p = 0 (Collatz) the dropping zeta is not. *Question:* for deterministic "exchange every K-th halving" maps, which K give finite-state backward structure? *Prediction:* none except the pure mirror, because any deleted 2 makes the inverse branch.

**H3. The pole is the dimension, the dimension is the survival rate.** Forward: pole 1/φ in z = 2^(−s) ↔ survival φ/2 = 0.809017 (measured to six decimals in E12). Backward for Banerji: 2^t of 3^t survivors ↔ pole at z = 1/2 in z = 3^(−s) ↔ survival 2/3 = 0.66667 (measured). *Hypothesis:* for any forbidden-factor family F of parity words, the per-step survival of positive integers *past their own bits* equals λ(F)/2 exactly, where λ is the Perron root. *Test:* pick three more families (forbid 000; forbid 101; forbid 0000) and run the tree search — the code needs only a different automaton. A deviation would mean self-generated bits are *not* free, which would be real news; agreement is expected.

H3 is the cheapest and the most informative: it generalises the one measurement in this project that nobody else has.
