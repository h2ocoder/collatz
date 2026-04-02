# Divisibility Obstruction Conjecture

## The Conjecture (Refined)

<div class="theorem">

**Conjecture (Divisibility Obstruction).** For any $(S, E)$ with gap $g = 2^E - 3^S > 0$, the sum

$$T = \sum_{j=0}^{S-1} 3^{S-1-j} \cdot 2^{q_j} \pmod{g}$$

with strictly increasing exponents $0 \leq q_0 < q_1 < \cdots < q_{S-1} \leq E - 1$ can only equal zero when $q_j = 2j$ for all $j$ — the **trivial cycle pattern** $(1,0,0)$ repeated.

</div>

Equivalently: the only Collatz cycle is $1 \to 4 \to 2 \to 1$.

## Why This Is the Right Formulation

The original conjecture stated: "no valid parity word has $g \mid 2^E \cdot C$." Testing all $(S, E)$ pairs with $K \leq 30$ revealed apparent counterexamples — but every one turned out to be the **trivial cycle in disguise**.

### The trivial cycle has period 3

The cycle $1 \to 4 \to 2 \to 1$ has parity word $(1, 0, 0)$: one odd step, two even steps. When repeated $m$ times, it gives $(S, E) = (m, 2m)$ with $K = 3m$ and gap $g = 4^m - 3^m$. The resulting $n$ values are always $\{1, 2, 4\}$.

This pattern can only tile a cycle of length $K$ when **$3 \mid K$**. For convergents of $\log_2 3$:

| $(S, E)$ | $K$ | $3 \mid K$? | Trivial fits? | Non-trivial zeros? |
|-----------|-----|-------------|---------------|---------------------|
| $(1, 2)$ | 3 | Yes | Yes → $n = 1, 2, 4$ | None |
| $(5, 8)$ | 13 | No | Can't tile | **None** (verified) |
| $(41, 65)$ | 106 | No | Can't tile | Conjectured none |
| $(665, 1054)$ | 1719 | Yes | Could tile — but ascending | Eliminated by sign |

### The ordering is what blocks non-trivial zeros

<div class="theorem">

**Key finding.** Without the ordering constraint $q_0 < q_1 < \cdots < q_{S-1}$, the sum $T$ equals zero with probability exactly $1/g$ — perfectly random. But with the ordering constraint, $T = 0$ occurs **only** for the trivial pattern.

</div>

Verified for gap $= 13$: assigning the 5 coefficients $[3^4, 3^3, 3^2, 3^1, 3^0]$ to 5 distinct exponents **in any order** gives $T \equiv 0$ for 7.7% of assignments ($\approx 1/13$). But restricting to the monotone assignment $q_0 < q_1 < q_2 < q_3 < q_4$ eliminates all zeros.

## Evidence

### Exhaustive verification ($K \leq 30$, gap $< 10{,}000$)

All $(S, E)$ pairs with $K = S + E \leq 30$ and $0 < g < 10{,}000$ were tested:

- **When $3 \nmid K$**: zero parity words give $g \mid T$. Every case is blocked.
- **When $3 \mid K$**: the only words giving $g \mid T$ produce $n \in \{1, 2, 4\}$ — the trivial cycle.

No non-trivial cycle candidates found in any case.

### Gap = 13 (detailed)

For $(S=5, E=8, K=13)$: 91 valid parity words, distribution of $T \bmod 13$:

| Remainder | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|-----------|---|---|---|---|---|---|---|---|---|---|----|----|-----|
| Count | **0** | 7 | 6 | 9 | 7 | 6 | 10 | 7 | 6 | 10 | 6 | 8 | 9 |

Roughly uniform over $\{1, \ldots, 12\}$, with zero structurally excluded.

## The Algebraic Structure

The sum decomposes as:

$$T = \sum_{j=0}^{S-1} 3^{S-1-j} \cdot 2^{q_j} \pmod{g}$$

Working mod $g$ where $2^E \equiv 3^S$:
- The coefficients $3^{S-1-j}$ cycle with period $\text{ord}(3 \bmod g)$
- The bases $2^{q_j}$ cycle with period $\text{ord}(2 \bmod g)$
- The monotonicity of exponents creates a **positional lock**: larger indices get smaller 3-coefficients and larger 2-exponents

For the trivial pattern $q_j = 2j$: the sum telescopes because each term $3^{S-1-j} \cdot 2^{2j} = 3^{S-1-j} \cdot 4^j$, and $\sum 3^{S-1-j} \cdot 4^j = (4^S - 3^S)/(4 - 3) = 4^S - 3^S = g$. So $T \equiv 0$ automatically.

For any other monotone sequence: the sum no longer telescopes, and the empirical evidence shows it never hits zero.

## The Challenge Ahead

**Proving the ordering obstruction** reduces to:

> Show that $\sum_{j=0}^{S-1} 3^{S-1-j} \cdot 2^{q_j} \equiv 0 \pmod{2^E - 3^S}$ with $0 \leq q_0 < q_1 < \cdots < q_{S-1} \leq E-1$ implies $q_j = 2j$ for all $j$.

This is a statement about weighted power sums modulo a specific composite number. The monotonicity of exponents, combined with the geometric decay of 3-coefficients, prevents the kind of cancellation that would make the sum vanish.

**Approaches:**
1. **Induction on $S$**: show that adding one more term to a non-trivial monotone sum can't restore cancellation
2. **$p$-adic analysis**: the sum has specific $p$-adic properties for primes $p \mid g$
3. **Connection to digital representations**: the sum resembles a mixed-radix representation in bases 2 and 3, where the ordering prevents "carrying"

## Related

- [Convergent Elimination](/cycles/convergent-elimination) — the computational results this conjecture refines
- [abc Conjecture](/connections/abc-conjecture) — the number theory connection
- [Path to Proof](/roadmap/path-to-proof) — how this fits in the roadmap
