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

## 4. H3 tested (2026-09-19) — Verified, with an unexplained 1/√N correction

`scripts/double_halving_rs/src/bin/family.rs` generalises the tree search to any forbidden factor; `scripts/family_survival_analysis.py` compares the per-step survival of positive integers past their own B bits (pooled over levels B+2..B+14) with λ/2. It reproduces the "00" run exactly (same leaves, same records). Depth B = 38:

| forbidden | integers surviving B bits | reach 1 inside the family | λ/2 | measured | difference |
|---|---|---|---|---|---|
| 00 | 63,245,986 | 1 (n = 1) | 0.809017 | 0.808988 | −0.000029 |
| 000 | 7,046,319,384 | 1 | 0.919643 | 0.919648 | +0.000005 |
| 0000 | 38,317,465,040 | 37,929,896 | 0.963781 | 0.963782 | +0.000001 |
| 101 | 1,042,002,567 | 0 | 0.877439 | 0.877393 | −0.000046 |
| 1001 | 11,411,317,488 | 20,246,218 | 0.933380 | 0.933372 | −0.000008 |
| 111 | 5,913,882,532 | 123,922,649 | 0.919643 | 0.919630 | −0.000013 |
| 11 | 39,088,169 | 378,934 | 0.809017 | 0.809838 | +0.000821 |

**H3 holds to 4–6 decimals in every family.** ("11" is the exception that proves the rule: 1% of its members reach the cycle at 1 and then never leave, because 1010… avoids "11"; absorbed orbits are counted as survivors, which is why it sits above λ/2.)

**The differences are real, and they are a finite-size effect.** Standard errors estimated from 24 independent shards agree with the binomial ones, so orbit merging is not inflating significance. Varying the depth:

| B | 101 | 1001 | 000 |
|---|---|---|---|
| 26 | −1.05·10⁻³ (z −8.0) | −3.43·10⁻⁴ (z −9.6) | −1.60·10⁻⁴ (z −3.4) |
| 30 | −3.62·10⁻⁴ (z −8.5) | −1.14·10⁻⁴ (z −11.2) | +4.4·10⁻⁵ (z +3.2) |
| 34 | −1.29·10⁻⁴ (z −9.3) | −3.2·10⁻⁵ (z −10.9) | +1.9·10⁻⁵ (z +4.6) |
| 38 | −4.6·10⁻⁵ (z −10.3) | −8.0·10⁻⁶ (z −9.5) | +4.4·10⁻⁶ (z +3.6) |
| 42 | −1.5·10⁻⁵ (z −10.2) | −2.4·10⁻⁶ (z −10.0) | — |

The difference shrinks by λ^(−2) per four bits (0.33 for "101", 0.29 for "1001"): it is proportional to **1/√N**, where N ≈ λ^B is the number of integers tested, and for "101" and "1001" the z-score is constant (≈ −10 at every depth). "000" is less clean: its gap is negative at B = 26 (z −3.4), then positive and roughly constant (z ≈ +3 to +5) from B = 30 on. "00" is within noise (z ≈ −1). So

    survival = λ/2 + c_F / √N,      c_F a constant of the family.

The limit is λ/2: self-generated digits are free, in every family tested. But a purely random model would give z-scores that wander around 0 with both signs; a *constant* z of −10 is a structured term of size √N that I cannot yet explain. **Open.** Candidate: a sub-population of about √N integers (for instance those below 2^(B/2), whose orbits are no longer in a random-looking regime by level B) that behaves deterministically.

**Dead end recorded:** splitting trials by whether the current value is above or below 2²⁴ does not test digit freedom — value size is correlated with the recent step history, hence with the automaton state, so the two halves have different *predicted* rates. Do not reuse that design.

## 5. Where the correction comes from (2026-09-19) — mostly explained

Three experiments (`scripts/family_correction_analysis.py`; `family.rs` with `FAMILY_LIFT` / `FAMILY_BUCKET`; `family_paired.rs`). Results in `results/family_correction.json`, `family_paired_B34.json`, `family_small_value_scaling.json`.

**1. Random-lift control — the correction belongs to the integers.** Replace each surviving r < 2^B by r + 2^B·j with j pseudo-random. The first B parities are unchanged (T^B(r + 2^B j) = T^B(r) + 3^s j) and every later digit is genuinely fresh. The z-scores collapse:

| | 101 | 1001 | 000 | 00 |
|---|---|---|---|---|
| real, B = 30 / 34 / 38 | −8.5 / −9.3 / −10.3 | −11.2 / −10.9 / −9.5 | +3.2 / +4.6 / +3.6 | −0.4 / −0.4 / −1.1 |
| lifted, same depths | −0.1 / −2.3 / −1.4 | −0.9 / −1.6 / +0.9 | −0.6 / +1.5 / −0.2 | +0.2 / −0.8 / −0.8 |

**2. First guess refuted — small *starting* numbers are not the cause.** Dropping every r < 2^(B/2) (about √N of them, which is why the guess was natural) leaves the gap unchanged to three digits.

**3. The cause — survivors whose value *after B steps* is small.** `family_paired.rs` runs the real and the lifted continuation from the same survivor and files both under the bit length of the real T^B(r), so the automaton-state mix is identical in both columns. For **101** at B = 34 the real−lifted gap is −8.2·10⁻⁵ (z −4.2); removing survivors whose value after 34 steps has ≤ 10 bits (0.7 % of trials) removes it (z +1.1). Across depths:

| 101 (small = T^B(n) ≤ 10 bits) | B = 26 | 30 | 34 | 38 |
|---|---|---|---|---|
| share of trials | 6.4 % | 2.3 % | 0.74 % | 0.23 % |
| their share of the real−lifted gap | 104 % | 110 % | 128 % | 85 % |
| share ratio per 4 bits | | 0.354 | 0.326 | 0.309 |

For **1001** the same holds with a 20-bit cut (82–103 % of the gap). A survivor whose value is small after B steps runs through a small integer for the next 14 steps, and small integers' orbits are specific rather than random — for 101 they fall towards 1 → 2 → 1, whose word 1010… contains 101, so they die (negative gap).

**Why about 1/√N.** T^B(r) ≈ 3^s·r/2^B, so a small value needs r in a sliver of relative width ~3^(−s). The share of such survivors is therefore E[3^(−s)] over pattern-avoiding words, which decays like (μ/λ)^B with μ the Perron root of the transfer matrix whose odd-step edges carry weight 1/3:

| factor | λ | μ | predicted decay | per 4 bits | measured per 4 bits |
|---|---|---|---|---|---|
| 101 | 1.7549 | 1.2767 | N^(−0.566) | 0.280 | 0.354 → 0.326 → 0.309 (falling towards it) |
| 1001 | 1.8668 | 1.2884 | N^(−0.594) | 0.227 | 0.549 → 0.465 → 0.405 (falling; fixed 20-bit cut converges slowly) |
| 000 | 1.8393 | 1.0000 | N^(−1.0) | 0.087 | — (small values essentially absent) |
| 00 | 1.6180 | 0.7676 | N^(−1.55) | 0.051 | — (no measurable gap, as predicted) |

So the "c/√N" was an exponent near ½ at the depths reachable, not exactly ½. **Prediction (testable with more compute):** for 101, the share ratio keeps falling towards 0.280 and the z-score, which scales like (μ/√λ)^B = 0.964^B, eventually starts to shrink. At B ≤ 42 it has not yet (−8 → −10).

**Still open.**
- **000.** Real z ≈ +3 to +5 against lifted ≈ 0 at three depths, so a small non-freshness exists, but it is *not* carried by small values (values ≤ 20 bits are < 0.1 % of trials). Unexplained.
- The pre-asymptotic behaviour: why the measured ratios sit above (μ/λ)⁴ and how fast they converge.

**What this settles for H3.** Past a number's own digits, the digits the orbit manufactures are statistically fresh *except* on the thin set of survivors that have already become small — a set whose share decays at a rate computable from a weighted transfer matrix. For the Collatz question this is the expected picture: structure appears only near small numbers, never in the bulk.
