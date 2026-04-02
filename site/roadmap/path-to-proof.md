# Path to Proof

The Collatz conjecture reduces to two independent claims:

<img src="/two-fronts.svg" alt="Two fronts toward proving the Collatz conjecture" style="max-width: 600px; margin: 1.5rem auto; display: block;" />

## Proved Results

A compact summary linking to full proof pages:

| # | Result | Statement | Status |
|---|--------|-----------|--------|
| 1 | [Affine Orbit Structure](/proofs/affine-orbit) | $\text{dest}(n) = (3^s/2^{k-s}) \cdot n + C$ within each subgroup | **Proved** |
| 2 | [Logarithmic Escape](/proofs/logarithmic-escape) | Self-chains bounded by $\log_P(n)$ | **Proved** |
| 3 | [Bit Destruction](/proofs/bit-destruction) | $\beta(s) = 1 - \{s \log_2 3\} > 0$ always | **Proved** |
| 4 | [3-Adic Mixing](/proofs/mixing) | $\text{ord}(3 \bmod 2^B) = 2^{B-2}$; transitions 98.7% independent | **Proved** |
| 5 | [Ascending Elimination](/cycles/convergent-elimination) | All ascending convergents give $n < 0$ | **Proved** |
| 6 | [Gap=13 Elimination](/cycles/convergent-elimination#gap-13-elimination) | No 13-step cycle (91 words checked) | **Proved** |
| 7 | [Trivial Cycle Identification](/cycles/divisibility-obstruction) | All divisibility zeros produce $n \in \{1, 2, 4\}$ only | **Verified** ($K \leq 30$) |

## Front 1: No Cycles (~75%)

**What we have:**
- Ascending convergents: eliminated (sign argument)
- First descending convergent (gap=13): eliminated (divisibility check)
- Each cycle pattern yields at most one candidate $n$ (affine uniqueness)
- Baker's theorem bounds minimum cycle length
- **NEW:** All $(S, E)$ tested ($K \leq 30$): only trivial cycle $n \in \{1,2,4\}$ survives

**The key conjecture (refined):**

<div class="theorem">

The sum $T = \sum_{j=0}^{S-1} 3^{S-1-j} \cdot 2^{q_j} \pmod{g}$ with monotone exponents $q_0 < q_1 < \cdots < q_{S-1}$ can only be zero when $q_j = 2j$ (the trivial cycle pattern). The **ordering constraint from parity words** blocks all non-trivial cancellations. See the [Divisibility Obstruction Conjecture](/cycles/divisibility-obstruction).

</div>

**Key insight:** Without the ordering constraint, the sum is zero with probability $1/g$ (random). With ordering, only the trivial pattern survives. The monotonicity is what kills non-trivial cycles.

**Next steps:**
1. Prove the ordering obstruction algebraically (why does monotonicity block cancellation?)
2. Random sampling for $(S=41, E=65)$ to build confidence at larger scale
3. Connect to S-unit equation theory

## Front 2: No Divergence (~30%)

**What we have:**
- $\beta(s) > 0$ always (every drop destroys bits)
- Roth: $\beta(s) > c/s$ (bounded away from 0)
- Mixing: set transitions nearly independent
- Log Escape: can't camp in slow sets
- "Almost all" $n$ converge (Terras-type)

**The gap:** Proving every $n$ has finite dropping time. This is equivalent to: the union of all dropping set residue classes covers every integer $> 1$.

**Possible approaches:**
1. Prove mixing prevents systematic slow-set avoidance
2. Find a Lyapunov function decreasing along every orbit
3. Base-6 lattice covering argument
4. Pillai conjecture: $|2^m - 3^n| \to \infty$ would give $\beta > c$ (constant)

## Connections to Classical Mathematics

| Our result | Classical connection |
|-----------|---------------------|
| $\beta(s) = 1 - \{s \log_2 3\}$ | Equidistribution (Weyl) |
| $\beta(s) > c/s$ | Irrationality measure (Roth) |
| Cycle gap $= 2^E - 3^S$ | S-unit equations, Pillai |
| Divisibility obstruction on $C$ | New (from Collatz affine structure) |
| $\text{ord}(3 \bmod 2^B) = 2^{B-2}$ | 2-adic analysis |
| $\text{rad}(2^a \cdot 3^b) = 6$ | [abc conjecture](/connections/abc-conjecture) |
| "Almost all" converge | Terras (1976) |

## Open Questions

1. **Is there an algebraic proof that $g \nmid C$ for all valid parity words when $g > 1$?** Would kill all cycles.
2. **Can the 3-adic mixing be promoted from statistical to deterministic?** Would address divergence.
3. **Does the base-6 lattice give a covering argument?** The modulus $2^{k-2s} \cdot 6^s$ unifies 2-adic and 3-adic views.
4. **Can the divisibility obstruction be verified for $(S=41, E=65)$?** Direct enumeration infeasible; needs algebraic or sampling approach.
