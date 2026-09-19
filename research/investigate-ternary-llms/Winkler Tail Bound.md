---
tags: [collatz, admissible-sequences, tail-bound, entropy, log2-3, three-distance, loop-L3]
status: verified
created: 2026-09-16
---

# Winkler Tail Bound (loop item L3)

**Question.** Winkler's bounds on the number of admissible sequences (OEIS A100982 [1]), with m = ⌊s log₂3⌋ = b(s) − 1,

$$\frac{1}{s}\binom{m-1}{s-1} \;\le\; N(s) \;\le\; \frac{1}{s}\binom{m}{s-1},$$

give a handle on the tail: the fraction U(p) of odd n whose dropping set is *not* decided by their low p bits. The repo knew U(12) ≈ 11% empirically. What is U(p) for all p, and at what rate does it go to zero?

Script: `scripts/winkler_tail.py`; results: `results/winkler_tail.json`. Exact N(s) from [[Exact Admissible Sequence DP]].

## 1. The bounds hold, and they pin the exponential rate — Verified

Checked exactly for s = 1…1000: 0 violations. The ratio upper/lower tends to e ≈ 2.7, so the bounds are tight to a constant.

Since s − 1 ≈ θ·m with θ = 1/log₂3 = 0.63093, the binomial gives

$$\operatorname{dens}(s) = \frac{N(s)}{2^{m}} = 2^{\,m\,(H(\theta)-1) + O(\log s)}, \qquad H(\theta) = 0.949956,$$

so the **sharp exponential rate** of the undecided fraction is

$$U(p) = 2^{-(1-H(\theta))\,p + o(p)}, \qquad 1 - H(1/\log_2 3) = 0.050044 \text{ bits per bit},$$

or 0.079319 per Syracuse step. Measured local rates −log₂(dens(s+100)/dens(s))/100 are 0.087 (s = 100), 0.095, 0.091, 0.090, 0.089 (s = 800), converging from above with the expected 1.5/(s ln 2) polynomial correction. So: **every extra low bit of n decides only 3.4% of the still-undecided odd numbers** (2^(−0.05) = 0.966). This is why "89% by mod 4096" grows so slowly: U(16) = 6.5%, U(32) = 1.9%, U(64) = 0.30%, U(100) = 4.8×10⁻⁴, U(200) = 6.1×10⁻⁶, U(400) = 2.3×10⁻⁹, U(1200) = 4.1×10⁻²².

## 2. Explicit bound — Verified numerically, conditional on Winkler's upper bound

Summing the upper bound over all s with b(s) > p (exactly to s = 3000, geometric remainder 5×10⁻⁷⁶ via 12-step ratio 0.69):

$$U(p) \;\le\; T(p) \;\le\; 0.756 \cdot 2^{-0.050044\,p} \quad\text{for every } p \le 1200,$$

with T(p)/U(p) → 1.6 and the constant A_p = T(p)·2^(cp) *decreasing* in p (0.73 at p = 2, 0.25 at p = 12, 0.001 at p = 800), so the same A = 0.756 works beyond the checked range as long as the trend continues. The exponent is sharp (§1), only the constant is loose.

Sanity anchors: U(2) = 1/2 (n ≡ 3 mod 4), U(4) = 3/8, U(12) = 113/1024 = 0.1104 (the repo's 89%).

**Is this known? Yes — it is Theorem D of Lagarias's 1985 survey, with the same constant.** Checked against the source (2026-09-16): Lagarias, "The 3x+1 problem and its generalizations", Amer. Math. Monthly 92 (1985), Theorem D, eq. (2.17)–(2.18):

> 1 − F(k) = lim_{x→∞} (1/x)·#{n ≤ x : σ(n) > k} ≤ 2^{−ηk}, where η = 1 − H(θ) ≈ .05004…, H(x) = −x log₂x − (1−x) log₂(1−x),

followed by "Theorem D cannot be substantially improved; it can be proved that for any ε > 0, |C₂| ≥ 2^{(H(θ)−ε)k} for all sufficiently large k" — i.e. the rate is sharp. The methods are Terras's (1976) and Everett's (1977). So §1 above is a rediscovery of a 40-year-old theorem, constant and all; what this note adds is only (a) the exact U(p) table from the DP, (b) the explicit constant 0.756 in U(p) ≤ 0.756·2^{−ηp} for p ≤ 1200, and (c) the observation that Winkler's binomial bounds reproduce Lagarias's η immediately. Label: rate **Known (Lagarias 1985, Thm D)**; explicit constant and table **Verified, minor**.

## 3. Surprise: N(s) hits the upper bound exactly at the record packings — Verified to s = 1000

N(s) = C(m, s−1)/s **exactly** at

s = 1, 3, 5, 17, 29, 41, 94, 147, 200, 253, 306, 971

— and these are precisely the record-low-waste s (upper semiconvergents of log₂3) from [[Trit Packing and log2(3)]] and [[Collatz Bridge - Trits and Stopping Times]] §2: the trit packings 2/1, 5/3, 8/5, 27/17, 46/29, 65/41, 149/94, 233/147, 317/200, 401/253, 485/306, 1539/971. Wastes: 0.415, 0.245, 0.075, 0.056, 0.036, 0.017, 0.014, 0.011, 0.0075, 0.0045, 0.0015, 0.0014.

Mechanism (cycle lemma): C(m, s−1)/s is the number of lattice paths strictly below the *rational* line through the origin and (s, m+1)… i.e. the Nakamigawa–Tokushige / Dvoretzky–Motzkin count for a line of slope (m+1)/s [2]. When s is a best upper approximation, ⌊i·log₂3⌋ = ⌊i·(m+1)/s⌋ − [i = s] for every i ≤ s, so the irrational-slope constraint coincides with the rational one and the count is exact. Between records the irrational line sits strictly below the rational one at some i, some paths are lost, and N < upper. **Conjecture:** N(s) = C(m_s, s−1)/s ⟺ s is an upper semiconvergent of log₂3. (Verified in both directions for s ≤ 1000: all 12 record s hit, no other s does.)

## 4. N(s)/upper(s) is a step function of the waste — Verified numerically

Binning s = 50…1000 by w(s):

| w(s) bin | mean N/upper | spread |
|---|---|---|
| [0.0, 0.1) | 0.981 | 0.943–1.000 |
| [0.1, 0.2) | 0.928 | 0.913–0.945 |
| [0.2, 0.245) | 0.906 | |
| [0.245, 0.3) | 0.827 | |
| [0.3, 0.4) | 0.801 | 0.783–0.824 |
| [0.35, **0.415**) | 0.792 | 0.781–0.803 |
| [**0.415**, 0.5) | 0.542 | 0.523–0.549 |
| [0.5, 0.6) | 0.517 | |
| [0.6, 0.7) | 0.493 | |
| [0.7, 0.8) | 0.463 | |
| [0.8, 0.830) | 0.453 | |
| [0.830, 0.9) | 0.393 | |
| [0.9, 1.0) | 0.378 | 0.370–0.397 |

The largest jump between w-neighbours (0.23) sits between w = 0.41497 and 0.41645, i.e. at **w = 2 − log₂3 = w(1) = 0.41504**; the next breaks are at **w(3) = 0.2451** and **w(2) = 0.8301**. So the correction factor N(s)/upper(s) is (to within a few percent) a function F(w(s)) alone, piecewise-constant-ish with breakpoints at the wastes of the smallest s — the Three Distance partition of the circle by {j log₂3}. Reading: the paths lost relative to the rational count are lost at the first few steps i = 1, 2, 3, …, and step i is "lossy" exactly when w(s) > w(i).

This is the missing piece of [[Waste Bias at First Drop]] §"Mechanism, part 2": the non-monotone histogram there is 2^(−w) × F(w) with F a step function. Combined:

$$\operatorname{dens}(s) \approx \frac{2}{s}\binom{m_s}{s-1}\,2^{-m_s}\cdot F(w(s)), \qquad F \in [0.37, 1],\ F = 1 \text{ at record packings}.$$

**Conjecture:** F is a Sturmian functional determined by which of the first few {i log₂3} exceed 1 − w(s); computing it exactly is the irrational-slope cycle-lemma problem ([[Collatz Bridge - Trits and Stopping Times]] §7).

## What this means for the Collatz work

- The 2-adic determinism table in `docs/Conjectures/Odd Stopping Time Spectrum.md` now has a rate: **undecided fraction ≈ 2^(−0.05 p)**, so reaching 99.9% needs ~200 low bits, 1 − 10⁻⁹ needs ~400. "Converges to 100%" is true but slowly, at the binary-entropy deficit of θ = 1/log₂3.
- The record trit packings (five-trit byte etc.) are now doubly special: weakest contraction (bridge §2) *and* exactly cycle-lemma-countable dropping sets.
- Nothing here bounds an individual orbit. It is density.

## Sources

1. OEIS A100982 (Winkler's bounds, Zarubin's recursion) — https://oeis.org/A100982
2. T. Nakamigawa, N. Tokushige, "Counting lattice paths via a new cycle lemma", SIAM J. Discrete Math. 26 (2012); Dvoretzky–Motzkin cycle lemma (1947).
3. J. C. Lagarias, "The 3x+1 problem and its generalizations", Amer. Math. Monthly 92 (1985); R. Terras, Acta Arith. 30 (1976); C. J. Everett, Adv. Math. 25 (1977); I. Krasikov, J. C. Lagarias, "Bounds for the 3x+1 problem using difference inequalities", Acta Arith. 109 (2003).
4. `scripts/winkler_tail.py`, `results/winkler_tail.json`; [[Exact Admissible Sequence DP]]; [[Waste Bias at First Drop]]; [[Trit Packing and log2(3)]].
