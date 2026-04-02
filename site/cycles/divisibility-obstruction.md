# Divisibility Obstruction Conjecture

## The Conjecture

<div class="theorem">

**Conjecture (Divisibility Obstruction).** For every descending convergent of $\log_2 3$ with gap $g = 2^E - 3^S > 1$, no valid parity word of length $K = S + E$ produces an affine constant $C$ satisfying:

$$g \mid 2^E \cdot C$$

</div>

If true, this proves **no non-trivial Collatz cycles exist** — because ascending convergents are [eliminated by sign](/cycles/convergent-elimination), and descending convergents with gap $> 1$ are eliminated by this divisibility obstruction. Only gap $= 1$ (the trivial 4→2→1 cycle) survives.

## Evidence

### Gap = 13 (exhaustive)

All 91 valid parity words for $(S=5, E=8)$ were checked. The distribution of $C \cdot 2^8 \bmod 13$ over $\{1, \ldots, 12\}$ is roughly uniform, but **zero never appears**. This is a complete, computer-verified proof for this convergent.

### Structural hints

Working mod 13:
- $\text{ord}(3 \bmod 13) = 3$: powers of 3 cycle through $\{1, 3, 9\}$
- $\text{ord}(2 \bmod 13) = 12$: powers of 2 cycle through all 12 nonzero residues
- $2^8 \equiv 3^5 \equiv 9 \pmod{13}$ — this is *why* $13 \mid (2^8 - 3^5)$

The affine constant $C$ is a sum of terms of the form $3^a / 2^b$ mod 13. The restricted cycling of powers of 3 (period 3) versus powers of 2 (period 12) creates structural constraints on which residues $C$ can take.

## The Challenge Ahead

The next descending convergent is $(S = 41, E = 65, K = 106)$ with gap $= 2^{65} - 3^{41}$. The number of valid parity words is approximately $\binom{66}{41} \sim 10^{17}$ — far too many to enumerate.

**Approaches:**
1. **Algebraic proof:** Show that the sum-of-affine-contributions can never be divisible by the gap, using the group structure of $(\mathbb{Z}/g\mathbb{Z})^*$.
2. **Random sampling:** Test a large random sample of parity words for the next convergent to build confidence.
3. **Connection to abc:** The abc conjecture constrains $|2^E - 3^S|$ from below, potentially making the divisibility condition easier to rule out for large gaps.

## Related

- [Convergent Elimination](/cycles/convergent-elimination) — the computational results this conjecture generalizes
- [abc Conjecture](/connections/abc-conjecture) — the number theory connection
- [Path to Proof](/roadmap/path-to-proof) — how this fits in the roadmap
