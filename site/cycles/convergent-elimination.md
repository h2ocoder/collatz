# Convergent Elimination

## The Cycle Equation

From the [Affine Orbit Structure](/proofs/affine-orbit), a Collatz cycle of total length $K$ with $S$ odd steps and $E = K - S$ even steps satisfies:

$$n = \frac{C_\text{total} \cdot 2^E}{2^E - 3^S}$$

where $C_\text{total}$ is the sum of affine corrections from each odd step. For a cycle to exist:
1. $2^E - 3^S$ must be nonzero (it is, since $\log_2 3$ is irrational)
2. The result must be a positive integer
3. $n$ must actually follow the proposed parity pattern

The viable $(S, E)$ pairs are the **convergents of $\log_2 3$** — the best rational approximations give the smallest gaps $|2^E - 3^S|$.

## Ascending Convergent Elimination

<div class="theorem">

**Theorem.** All convergents with $3^S > 2^E$ (ascending ratio) cannot produce positive integer cycles.

</div>

<div class="proof">

The affine constant $C_\text{total}$ is always positive: each odd step contributes $+1$, subsequently multiplied by positive factors ($3^j / 2^m$ for various $j, m$).

When $3^S > 2^E$, the denominator $2^E - 3^S < 0$, so:

$$n = \frac{C_\text{total} \cdot 2^E}{2^E - 3^S} = \frac{(\text{positive})}{(\text{negative})} < 0$$

No positive integer cycle exists.

</div>

This eliminates **half of all convergents** for free.

## Convergent Status Table

| $E$ | $S$ | $K$ | $p/q$ | vs $\log_2 3$ | Gap | Status |
|-----|-----|-----|-------|---------------|-----|--------|
| 1 | 1 | 2 | 1.000 | below | $-1$ | **Eliminated** (ascending) |
| 2 | 1 | 3 | 2.000 | above | $1$ | ✓ Trivial cycle (4→2→1) |
| 3 | 2 | 5 | 1.500 | below | $-1$ | **Eliminated** (ascending) |
| 8 | 5 | 13 | 1.600 | above | $13$ | **Eliminated** (divisibility) |
| 19 | 12 | 31 | 1.583 | below | $-7153$ | **Eliminated** (ascending) |
| 65 | 41 | 106 | 1.585 | above | $\sim 10^{1.3}$ | Open (too large to enumerate) |
| 84 | 53 | 137 | 1.585 | below | $\sim -10^{1.3}$ | **Eliminated** (ascending) |
| 485 | 306 | 791 | 1.585 | above | $\sim 10^{0.6}$ | Open |

## Gap = 13 Elimination

For $(S=5, E=8, K=13)$ with gap $= 2^8 - 3^5 = 256 - 243 = 13$:

A valid **parity word** is a circular binary string of length 13 with exactly 5 ones (odd positions) and no two consecutive ones (since $3n+1$ always produces an even number). There are exactly **91** such words.

For each word, the affine composition gives a specific constant $C$. The cycle equation requires:

$$13 \mid C \cdot 256$$

Since $\gcd(256, 13) = 1$, this reduces to $13 \mid C$.

<div class="theorem">

**Theorem.** No 13-step Collatz cycle exists. Among all 91 valid parity words, the remainder $C \cdot 256 \bmod 13$ is distributed over $\{1, 2, \ldots, 12\}$ — zero never appears.

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

The distribution is roughly uniform over $\{1, \ldots, 12\}$, but zero is **structurally excluded**.

## The Trivial Cycle

The convergent $(S=1, E=2, K=3)$ with gap $= 1$ produces the known cycle:

- Parity word $(1, 0, 0)$: $C = 1$, $n = 1 \cdot 4 / 1 = 4$. The cycle $4 \to 2 \to 1 \to 4$. ✓
- Parity word $(0, 1, 0)$: $n = 2$. The cycle $2 \to 1 \to 4 \to 2$. ✓
- Parity word $(0, 0, 1)$: $n = 4$. Same cycle, different starting point.

## Related

- [Divisibility Obstruction](/cycles/divisibility-obstruction) — the conjecture that generalizes gap=13
- [Affine Orbit Structure](/proofs/affine-orbit) — the affine maps underlying the cycle equation
- [abc Conjecture](/connections/abc-conjecture) — stronger bounds on the gap
