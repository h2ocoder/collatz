# Convergent Elimination

This page works through the small cases of the cycle equation by hand. It does not rule out cycles in general — that is open — and the cases here are already covered by the literature (Steiner 1977, Eliahou 1993, Simons and de Weger 2005, Hercher 2023). It is a worked example of how the equation behaves.

## The Cycle Equation

A Collatz cycle of total length $K$ with $S$ odd steps and $E = K - S$ even steps satisfies (Böhm and Sontacchi, 1978):

$$n = \frac{C_\text{total} \cdot 2^E}{2^E - 3^S}$$

where $C_\text{total}$ is the sum of affine corrections from each odd step (see [Affine Orbit Structure](/proofs/affine-orbit)). For a cycle to exist:
1. $2^E - 3^S$ must be nonzero (it is, since $\log_2 3$ is irrational)
2. The result must be a positive integer
3. $n$ must actually follow the proposed parity pattern

Any pair with $2^E > 3^S$ is a candidate. The pairs where the gap $|2^E - 3^S|$ is smallest relative to $2^E$ come from the **convergents of $\log_2 3$**, so they make natural test cases, but they are not the only candidates. Eliahou (1993) showed that for any nontrivial cycle, $E/S$ must be very close to $\log_2 3$ — close, not necessarily a convergent.

## Negative gaps give no positive cycles

<div class="theorem">

**Lemma.** If $3^S > 2^E$, there is no positive integer cycle with $S$ odd and $E$ even steps.

</div>

<div class="proof">

The affine constant $C_\text{total}$ is always positive: each odd step contributes $+1$, subsequently multiplied by positive factors ($3^j / 2^m$ for various $j, m$).

When $3^S > 2^E$, the denominator $2^E - 3^S < 0$, so:

$$n = \frac{C_\text{total} \cdot 2^E}{2^E - 3^S} = \frac{(\text{positive})}{(\text{negative})} < 0$$

</div>

This is elementary and well known. It is also exactly where the negative integers come in: $-1$, $-5$ and $-17$ sit on cycles of this kind.

## The first few convergents

| $E$ | $S$ | $K$ | $E/S$ | vs $\log_2 3$ | Gap $2^E - 3^S$ | What happens |
|-----|-----|-----|-------|---------------|-----|--------|
| 1 | 1 | 2 | 1.000 | below | $-1$ | Negative gap |
| 2 | 1 | 3 | 2.000 | above | $1$ | Trivial cycle (4→2→1) |
| 3 | 2 | 5 | 1.500 | below | $-1$ | Negative gap |
| 8 | 5 | 13 | 1.600 | above | $13$ | No cycle (checked below) |
| 19 | 12 | 31 | 1.583 | below | $-7153$ | Negative gap |
| 65 | 41 | 106 | 1.585 | above | $\approx 4.2 \times 10^{17}$ | Too large to enumerate by hand |
| 84 | 53 | 137 | 1.585 | below | $\approx -4.0 \times 10^{22}$ | Negative gap |
| 485 | 306 | 791 | 1.585 | above | $\approx 1.0 \times 10^{143}$ | Too large to enumerate |

## Gap = 13

For $(S=5, E=8, K=13)$ with gap $= 2^8 - 3^5 = 256 - 243 = 13$:

A valid **parity word** is a circular binary string of length 13 with exactly 5 ones (odd positions) and no two consecutive ones (since $3n+1$ always produces an even number). There are exactly **91** such words.

For each word, the affine composition gives a specific constant $C$. The cycle equation requires:

$$13 \mid C \cdot 256$$

Since $\gcd(256, 13) = 1$, this reduces to $13 \mid C$.

<div class="theorem">

**Check.** No Collatz cycle has $S = 5$ odd and $E = 8$ even steps. Among all 91 valid parity words, the remainder $C \cdot 256 \bmod 13$ is distributed over $\{1, 2, \ldots, 12\}$ — zero never appears.

</div>

Distribution of $C \cdot 256 \bmod 13$:

| Remainder | Count |
|-----------|-------|
| 1 | 7 |
| 2 | 6 |
| 3 | 9 |
| 4 | 7 |
| 5 | 6 |
| 6 | 10 |
| 7 | 7 |
| 8 | 6 |
| 9 | 10 |
| 10 | 6 |
| 11 | 8 |
| 12 | 9 |
| **0** | **0** |

The distribution is roughly uniform over $\{1, \ldots, 12\}$, and zero is missing.

## The Trivial Cycle

The convergent $(S=1, E=2, K=3)$ with gap $= 1$ produces the known cycle:

- Parity word $(1, 0, 0)$: $C = 1$, $n = 1 \cdot 4 / 1 = 4$. The cycle $4 \to 2 \to 1 \to 4$. ✓
- Parity word $(0, 1, 0)$: $n = 2$. The cycle $2 \to 1 \to 4 \to 2$. ✓
- Parity word $(0, 0, 1)$: $n = 4$. Same cycle, different starting point.

## Related

- [No Loops?](/journey/no-loops) — the tour chapter, with the CycleHunter playground
- [Divisibility Obstruction](/cycles/divisibility-obstruction) — the cycle problem restated as a divisibility question
- [Affine Orbit Structure](/proofs/affine-orbit) — the affine maps underlying the cycle equation
- [abc Conjecture](/connections/abc-conjecture) — the size of the gap $2^E - 3^S$
