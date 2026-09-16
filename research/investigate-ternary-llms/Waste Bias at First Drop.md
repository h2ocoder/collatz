---
tags: [collatz, packing-waste, dropping-sets, log2-3, loop-L2]
status: verified-with-open-mechanism
created: 2026-09-16
---

# Waste Bias at First Drop (loop item L2)

**Question.** w(s) = bitlen(3^s) − s·log₂3 ∈ (0, 1) is the storage waste of an s-trit register and, by [[Collatz Bridge - Trits and Stopping Times]] §2, the number of bits an orbit sheds at its first drop (slope 3^s/2^b = 2^(−w)). Under the dropping-set measure dens(s) = N(s)/2^(b(s)−1), is E[w] = 1/2 (as equidistribution of {s log₂3} would give), or are drops systematically *tighter packings* than random?

**Answer: biased low — Verified.** E[w] = 0.44958 (exact N(s) to s = 1000, [[Exact Admissible Sequence DP]]). The bias is not a small-s artefact: every window of s gives a conditional mean below 1/2 while the unweighted mean of w over the same s is 1/2.

| s window | measure mass | E[w \| window] | unweighted mean w |
|---|---|---|---|
| 1–5 | 0.852 | 0.4427 | 0.4451 |
| 6–20 | 0.129 | 0.4967 | 0.5288 |
| 21–50 | 0.0179 | 0.4380 | 0.5005 |
| 51–100 | 1.3×10⁻³ | 0.4431 | 0.4953 |
| 101–200 | 3.5×10⁻⁵ | 0.4684 | 0.5031 |
| 201–400 | 5.5×10⁻⁸ | 0.4449 | 0.4988 |
| 401–700 | 3.4×10⁻¹³ | 0.4519 | 0.5015 |
| 701–1000 | 1.1×10⁻²⁰ | 0.4418 | 0.4994 |

Script: `scripts/waste_bias.py`; results: `results/waste_bias.json`.

## Mechanism, part 1: the Boltzmann factor — Verified arithmetic

Writing 2^(b(s)−1) = 2^(s log₂3 + w(s) − 1) gives an exact identity

$$\operatorname{dens}(s) = 2\cdot\frac{N(s)}{3^s}\cdot 2^{-w(s)}.$$

If N(s)/3^s were smooth in s, the measure would weight each s by 2^(−w) and the conditional mean of w in any large window would be

$$m^\ast = \frac{\int_0^1 w\,2^{-w}\,dw}{\int_0^1 2^{-w}\,dw} = \frac{1}{\ln 2} - 1 = 0.442695\ldots$$

The observed window means (0.438–0.468, global 0.4496) sit around this, and the s = 1–5 window — which carries 85% of the mass — gives 0.4427 to four digits by coincidence of the small values. So **most of the bias is the explicit 2^(−w) factor**: a set with small waste has slope close to 1, i.e. its members drop only *just* below n, and there are proportionally more of them per residue class because 2^(b−1) is smaller relative to 3^s.

Interpretation in packing language: *the dropping-set measure is a Gibbs measure on trit packings at inverse temperature ln 2 per wasted bit.*

## Mechanism, part 2: N(s)/3^s is not smooth — Conjecture

Detrending log₂(N(s)/3^s) by a ±6 local mean and regressing the residual on w(s) (s = 50…994): residual std 0.132 bits, slope −0.247, correlation −0.54. So N(s) itself knows the waste: high-waste s (3^s just under a power of two — the lower convergents 12, 53, 665, …) have *fewer* admissible sequences than the trend, beyond the explicit factor. And the dependence is not monotone. Mass per s relative to the window average, s = 101…1000, by waste bin:

| w bin | measure mass / count (relative) | pure 2^(−w) would give |
|---|---|---|
| [0.0, 0.2) | 1.14 | 1.29 |
| [0.2, 0.4) | 1.27 | 1.13 |
| [0.4, 0.6) | 0.92 | 0.98 |
| [0.6, 0.8) | 0.72 | 0.85 |
| [0.8, 1.0) | 0.95 | 0.74 |

The bump at w ∈ [0.8, 1) and the dip at [0, 0.2) say that the *count* of lattice paths under the line y = x·log₂3 depends on the whole Sturmian prefix ({i log₂3} for i ≤ s), not just on the endpoint gap w(s). This is the same object as the Three Distance / Sturmian structure in `docs/Explorations/Dropping Zeta Spectrum.md`, and it is where the "irrational-slope lattice path asymptotics" question ([[Collatz Bridge - Trits and Stopping Times]] §7) lives. **Conjecture:** N(s)/3^s = C·s^(−γ)·F({i log₂3}_{i≤s}) with F a bounded Sturmian functional; the −0.25 slope is F's first-order dependence on the endpoint.

## What this means for the Collatz work

- The repo's "mean contraction per drop ≈ 0.605" and E[bits shed] ≈ 0.45 are now exact and explained to first order: E[2^(−w)] and E[w] under a 2^(−w)-tilted Sturmian measure.
- The bias is small (0.45 vs 0.50) and does not bear on convergence; it is a statement about *which* dropping sets carry the mass, not about how long orbits wait to drop.
- Label summary: bias **Verified**; Boltzmann-factor explanation **Verified as arithmetic, first-order as mechanism**; residual Sturmian dependence of N(s) **Conjecture**.

## Sources

1. [[Exact Admissible Sequence DP]] — N(s) to s = 1000, `results/admissible_dp.json`
2. [[Collatz Bridge - Trits and Stopping Times]] §2, §4, §7
3. `docs/Conjectures/Affine Orbit Structure.md` (slope 3^s/2^(k−s)); `docs/Explorations/Dropping Zeta Spectrum.md` (Sturmian, Three Distance)
4. Script `scripts/waste_bias.py`
