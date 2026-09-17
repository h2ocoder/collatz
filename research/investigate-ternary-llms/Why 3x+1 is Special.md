---
tags: [collatz, 3x+k, cycles, divergence, diophantine, log2-3, synthesis]
status: argument-with-verified-parts
created: 2026-09-17
---

# Why 3x+1 is Special

**Goal (user).** Follow the bread crumbs — dropping-set intercepts → cycle minima of 3x+k (A226607) — to a convincing argument for (a) what makes 3x+1 special, (b) why cycles exist for other 3x+k, and (c) why some maps blow up to infinity. Every step below is labelled; the argument is a chain of three exact facts and one heuristic, and the heuristic is the same one the literature relies on. Literature context in [[Literature - 3x+k Cycles and Divergence]].

Scripts: `scripts/cycles_3xk_census.py`, `scripts/cycle_count_mechanism.py`, `scripts/cycle_diophantine_k1.py`; results in `results/` under the same names.

## 0. The one equation

Write T_k(x) = x/2 (x even), (3x + k)/2 (x odd), for k coprime to 6. A cyclic parity word v of length b with s ones, applied to x, gives

$$T_k^{\,b}(x) = \frac{3^s x + k\,r(v)}{2^b}, \qquad r(v) = \sum_{i:\,v_i = 1} 2^i\,3^{\#\{\text{ones after } i\}}.$$

So v is the word of a cycle of T_k with minimum x_min exactly when

$$x_{\min}\,(2^b - 3^s) = k\,r(v) \qquad\text{(cycle equation)},$$

i.e. **iff (2^b − 3^s) divides k·r(v)**, and then x_min = k·r(v)/(2^b − 3^s). Write d(b, s) = 2^b − 3^s and w = b − s·log₂3 > 0, so d ≈ 3^s(2^w − 1). Everything below is this equation read three ways. (Verified on all 727 primitive cycles of 3x+k, k ≤ 600, found from 2·10⁶ starts: 0 violations.)

## 1. Why other 3x+k have cycles — Verified

**k supplies the divisor.** For any k coprime to 6, 2 and 3 are units mod k, so with b a multiple of ord_k(2) and s a multiple of ord_k(3) we get 2^b ≡ 1 ≡ 3^s, hence **k | d(b, s)**. For such a shape the cycle equation reads x_min = r(v)·(k/d): *every* necklace of that shape is a cycle. The cleanest case is k = d(b, s) itself, where x_min = r(v):

| k = 2^b − 3^s | shape | necklaces | cycles of 3x+k of that shape |
|---|---|---|---|
| 7 = 2⁴ − 3² | (4, 2) | 2 | 2 (one primitive: {5, 11, 20, 10}) |
| 5 = 2⁵ − 3³ | (5, 3) | 2 | 2 ({19, …}, {23, …}) |
| 13 = 2⁸ − 3⁵ | (8, 5) | 7 | 7 — the seven Set₁₃ intercepts of A226607's row 13 |
| 269 = 2⁹ − 3⁵ | (9, 5) | 14 | 14 |
| 295 = 2¹⁰ − 3⁶ | (10, 6) | 22 | 22 |

And when k is a proper divisor of d, exactly the necklaces whose r(v) is divisible by the cofactor d/k are cycles: 3x+499 has 2¹⁶ − 3¹⁰ = 6487 = 13·499, and its (16, 10)-cycles are precisely the 41 of the 504 necklaces with 13 | r(v) (≈ 504/13). That is why 499 is the cycle-richest k below 600 (52 cycles), and why 233 (7·233 = 2¹³ − 3⁸), 269, 295, 355, 517 (11·47 = 2¹⁴ − 3⁸ … with 517 | 9823) are next. A one-line heuristic, E[#cycles(k)] = Σ_{(b,s)} (#necklaces)·gcd(k, d)/d, correlates 0.65 with the census over 200 values of k.

**Reading.** Cycles of 3x+k are not accidents; they are necklaces whose denominator d(b, s) the constant k can absorb. Every k > 1 coprime to 6 absorbs *some* d completely, and inherits that whole necklace family. This also identifies the dropping sets of 3x+1 with cycles: the residue classes of Set_{s+b(s)} are the cycles of 3x+d(b(s), s) started at their minima ([[Primes and the Circuit]] §9), and at the record packings every necklace is such a class ([[Winkler Tail Bound]] §3).

## 2. Why 3x+1 is special — Verified inequality, verified computation, heuristic tail

**k = 1 is the unique k with no slack: gcd(1, d) = 1 for every shape.** A 3x+1 cycle needs d(b, s) | r(v) with nothing to help. Two consequences, one rigorous and one heuristic.

**(i) The slack inequality forces long cycles to record packings.** Over a cycle, 2^b/3^s = Π_{odd steps}(1 + k/(3xᵢ)) ≤ (1 + k/(3x_min))^s, hence

$$x_{\min} \;\le\; \frac{k\,s}{3\,w\,\ln 2}.$$

(Verified on all 727 cycles, 0 violations; the ratio x_min/bound has median 0.20, max 0.86.) For k = 1: a cycle with s odd steps and waste w has minimum at most s/(3 w ln 2). Since every n < 2⁷¹ is known to reach 1, a nontrivial cycle has x_min ≥ 2⁷¹, so w ≤ s/(3·2⁷¹·ln 2) ≈ s/(4.9·10²¹): the pair (b, s) must approximate log₂3 from above to a precision only the **upper semiconvergents — the record trit packings — can reach**. Walking the semiconvergents of log₂3:

| s (record) | b | w(s) | x_min ≤ s/(3 w ln 2) | vs 2⁷¹ ≈ 2.4·10²¹ |
|---|---|---|---|---|
| 5 | 8 | 0.0752 | 32 | impossible |
| 41 | 65 | 0.0165 | 1,192 | impossible |
| 306 | 485 | 0.00147 | 99,781 | impossible |
| 15,601 | 24,727 | 2.6·10⁻⁵ | 2.9·10⁸ | impossible |
| **72,057,431,991** | **114,208,327,604** | 8.0·10⁻¹² | 4.4·10²¹ | first possible |

So **any nontrivial 3x+1 cycle has at least 7.2·10¹⁰ odd steps and length ≥ 1.14·10¹¹** — which is exactly the published Hercher–Puchert bound (from the same Barina verification), reproduced here from one inequality and the continued fraction of log₂3. For k = d(b, s) the same inequality gives x_min ≤ s·3^s(2^w − 1)/(3 w ln 2) ≈ s·3^s/3 — no constraint at all, which is why those maps have all their necklaces as cycles.

**(ii) The expected number of surviving cycles is 2^(−5.7·10⁹).** Treating r(v) mod d as uniform (the same heuristic as §1's formula, which the census supports), the expected number of 3x+1 cycles is Σ_{(b,s)} C(b,s)/(b·d(b,s)). Summed over shapes with b ≤ 60 it is **5.3** — one of which is the trivial cycle {1, 2} (shape (2,1), d = 1) and the rest come from the small record-adjacent shapes (5,3), (8,5), (16,10), … whose cycles would have minima < 10⁵ and are excluded by (i). Beyond, the per-length contribution is 2^{b(H(θ)−1)}/(b·w) with θ = 1/log₂3, i.e. it decays at **η = 1 − H(θ) = 0.05004 bits per unit of b — Lagarias's Theorem D constant** (the same one that governs how fast the low bits of n decide its stopping time, [[Winkler Tail Bound]] §2). Expected cycles of length ≥ 100: 2^(−6.9); ≥ 1,000: 2^(−59); ≥ 10⁴: 2^(−514); ≥ 1.14·10¹¹: **2^(−5.7·10⁹)**.

**Reading.** 3x+1 is special because it is the *only* member of the family with nothing to absorb the denominator 2^b − 3^s. For every other k, cycles are guaranteed by divisibility; for k = 1 they require r(v) to hit a multiple of 2^b − 3^s by itself, the naive expectation of ≈ 4 such coincidences is confined to tiny cycles that direct computation has excluded, and the Diophantine structure of log₂3 pushes any survivor to length > 10¹¹, where the entropy-rate heuristic makes its expected number 2^(−5·10⁹). This is a *convincing* argument, not a proof: the two heuristic inputs are the uniformity of r(v) mod d (well supported) and the independence of that from the verification bound. What is rigorous is the slack inequality, the record-packing constraint, and the length bound.

## 3. Why some maps blow up — Verified drift, verified numerics, heuristic in the literature

Divergence is a property of the **multiplier**, not of k. Each Terras step of px+k halves once and multiplies by p half the time, so the expected change in log₂x per step is

$$\mathbb{E}[\Delta \log_2 x] = \tfrac12\log_2 p - 1: \qquad p = 3:\ -0.2075,\quad p = 5:\ +0.1610,\quad p = 7:\ +0.4037.$$

The sign is the sign of p − 4. For p = 3 every 3x+k contracts on average (k only adds a bounded additive term), and no orbit should escape: in the census, all 2·10⁶ starts across 200 values of k reached a cycle (28 needed values above 10⁹ — the longest transients peak near 1.7·10¹⁰ — none above 10³⁰). For p ≥ 5 the drift is positive: of 1,000 odd starts below 2,000, **910 orbits of 5x+1 and 990 of 7x+1 exceeded 10⁴⁰** within 20,000 steps; the rest fell into the few known cycles. So "3x+k blows up" is not expected for any k; "5x+1 blows up" is expected for almost every start. The precise form (Benford-type large-deviation models, Kontorovich–Lagarias) is in the literature note; the sign of ½log₂p − 1 is the whole story at this level.

Where 3 sits: 3 < 4 = 2² is the statement that one multiplication is beaten by two halvings on average; log₂3 = 1.585 < 2 is the same inequality, and its fractional part is what all of the cycle Diophantine analysis is about. **3x+1 is the largest odd multiplier that contracts**, and 1 is the additive constant that absorbs nothing — the map sits exactly at the corner of the (p, k) family where orbits must return yet have no cycle to return to except the trivial one.

## 4. The whole picture in one table

| map | drift ½log₂p − 1 | denominator slack gcd(k, 2^b − 3^s) | consequence |
|---|---|---|---|
| 3x+1 | −0.21 (contracts) | none, for every shape | orbits must fall; only the trivial cycle can exist below 10¹¹ steps; expected survivors 2^(−5·10⁹) |
| 3x+k, k > 1 coprime to 6 | −0.21 (contracts) | full for every shape with k \| 2^b − 3^s | orbits fall into one of finitely many cycles; cycle count grows with how small a d the k divides |
| 5x+1, 7x+1, … | > 0 (expands) | (irrelevant) | almost every orbit diverges; the few cycles are islands |

## 5. What is proved, what is not, and what this vault added

- **Proved / verified:** the cycle equation and its divisibility reading; "every k > 1 coprime to 6 absorbs some d, so every necklace of that shape is a cycle"; the slack inequality; the record-packing constraint and the 1.14·10¹¹ length bound (matching Hercher–Puchert); the drift signs; the census facts.
- **Heuristic:** uniformity of r(v) mod d (hence the expected-count formula and the 2^(−5·10⁹) tail); "no divergence for 3x+k" (Lagarias's conjecture; the drift argument is not a proof); "almost all 5x+1 orbits diverge" (same status).
- **Not addressed:** the actual 3x+1 conjecture. Nothing here rules out the astronomically long cycles or a divergent orbit; it explains *why they would be miracles*, which is a different thing.
- **What is ours:** the identification of the dropping-set intercepts with A226607, the slack inequality in the form x_min ≤ k s/(3 w ln 2) as the single object separating k = 1 from the rest, the exact necklace-divisibility mechanism on cycle-rich k, and the observation that the cycle-expectation tail and Lagarias's Theorem D share the constant 1 − H(1/log₂3). The literature note records which of these are already known.

## Sources

1. J. C. Lagarias, "The set of rational cycles for the 3x+1 problem", Acta Arith. 56 (1990) 33–53.
2. OEIS A226607 (G. H. Morley), primitive cycles of 3x+k — https://oeis.org/A226607
3. C. Hercher, "There are no Collatz m-cycles with m ≤ 91", J. Integer Seq. 26 (2023); Hercher & Puchert, cycle bound K > 7.2·10¹⁰ odd steps; D. Barina, verification to 2⁷¹.
4. J. C. Lagarias, "The 3x+1 problem and its generalizations", Amer. Math. Monthly 92 (1985), Theorem D (η = 1 − H(θ)).
5. A. Kontorovich, J. C. Lagarias, "Stochastic models for the 3x+1 and 5x+1 problems", arXiv:0910.1944.
6. [[Literature - 3x+k Cycles and Divergence]]; [[Primes and the Circuit]] §9; [[Winkler Tail Bound]]; [[Collatz Bridge - Trits and Stopping Times]].
7. Scripts and results named at the top.
