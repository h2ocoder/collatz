# Divisibility Obstruction

This page states the no-cycles question as a divisibility problem and shows some computations. The statement below is **equivalent** to "there are no nontrivial Collatz cycles": it is just the Böhm–Sontacchi cycle equation written out term by term. So it is exactly as hard as the cycle problem, which is open.

## The statement

<div class="theorem">

**Conjecture (Divisibility Obstruction).** For any $(S, E)$ with gap $g = 2^E - 3^S > 0$, the sum

$$T = \sum_{j=0}^{S-1} 3^{S-1-j} \cdot 2^{q_j}$$

with strictly increasing exponents $0 = q_0 < q_1 < \cdots < q_{S-1} \leq E - 1$ is divisible by $g$ only when $q_j = 2j$ for all $j$ — the **trivial cycle pattern** $(1,0,0)$ repeated.

</div>

Why this is the cycle problem: an odd number $n$ starts a cycle with $S$ odd steps and $E$ halvings exactly when $n = T / g$ for the exponents $q_j$ recording how many halvings have happened before the $j$-th odd step (Böhm and Sontacchi, 1978). So "$g \mid T$ only for the trivial pattern" says "the only cycle is $1 \to 4 \to 2 \to 1$".

## The trivial cycle has period 3

The cycle $1 \to 4 \to 2 \to 1$ has parity word $(1, 0, 0)$: one odd step, two even steps. When repeated $m$ times, it gives $(S, E) = (m, 2m)$ with $K = 3m$ and gap $g = 4^m - 3^m$. The resulting $n$ values are always $\{1, 2, 4\}$.

For that pattern the sum telescopes: $\sum_{j} 3^{S-1-j} \cdot 4^j = 4^S - 3^S = g$, so $T \equiv 0$ automatically. For any other increasing sequence it no longer telescopes, and in every case I have tested it never hits zero.

## Evidence

### Exhaustive check ($K \leq 30$, gap $< 10{,}000$)

All $(S, E)$ pairs with $K = S + E \leq 30$ and $0 < g < 10{,}000$ were tested:

- **When $3 \nmid K$**: no parity word gives $g \mid T$.
- **When $3 \mid K$**: the only words giving $g \mid T$ produce $n \in \{1, 2, 4\}$ — the trivial cycle.

This is consistent with, and much weaker than, the known results on cycles (Steiner 1977, Eliahou 1993, Simons and de Weger 2005, Hercher 2023), which rule out every nontrivial cycle of this size and far beyond.

### Gap = 13

For $(S=5, E=8, K=13)$, taking all 91 circular parity words (every starting point, odd or even), the residue of the cycle equation mod 13 is distributed as:

| Remainder | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|-----------|---|---|---|---|---|---|---|---|---|---|----|----|-----|
| Count | **0** | 7 | 6 | 9 | 7 | 6 | 10 | 7 | 6 | 10 | 6 | 8 | 9 |

Roughly uniform over $\{1, \ldots, 12\}$, with zero missing.

### The ordering matters

For gap 13, assigning the five coefficients $[3^4, 3^3, 3^2, 3^1, 3^0]$ to five distinct exponents **in any order** gives $T \equiv 0$ for 7.7% of assignments, close to $1/13$. Restricting to the increasing assignment $q_0 < q_1 < \cdots < q_4$ removes every zero. The increasing order — larger 2-exponents paired with smaller 3-coefficients — is what the cycle equation actually requires, and it is where any proof would have to find its leverage.

## Ideas worth trying

1. **Induction on $S$**: understand how adding one more term to an increasing sum changes its residue mod $g$.
2. **$p$-adic analysis**: look at the sum modulo the individual primes dividing $g$.
3. **Mixed-radix digits**: the sum resembles a representation in bases 2 and 3 at once, where the ordering might prevent the "carrying" that cancellation needs.

None of these has produced a proof.

## Related

- [Convergent Elimination](/cycles/convergent-elimination) — the cycle equation and the small cases
- [No Loops?](/journey/no-loops) — the tour chapter on cycles, with playgrounds
- [abc Conjecture](/connections/abc-conjecture) — the number theory connection
