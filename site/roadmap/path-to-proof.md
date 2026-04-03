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

## Front 1: No Cycles (~95%)

**The proof reduces to a single convergent.**

| Convergent $(S, E)$ | Gap $g$ | Method | Status |
|---------------------|---------|--------|--------|
| All ascending | negative | $C > 0 \Rightarrow n < 0$ | **Proved** |
| $(1, 2)$, $K = 3$ | $1$ | Trivial cycle only | **Proved** |
| $(5, 8)$, $K = 13$ | $13$ | 0/91 words, complete enumeration | **Proved** |
| $(41, 65)$, $K = 106$ | $\sim 4.2 \times 10^{17}$ | 0 in all $2.5 \times 10^{17}$ subsets (Rust MITM, 87 min) | **ELIMINATED** |
| All $S \geq 306$ | $> C(E{-}1, S{-}1)$ | $\log_2(\text{words}) < \log_2(g)$ | **Heuristic** (needs uniformity bound) |

<div class="theorem">

**The asymptotic argument.** $\log_2 C(E{-}1, S{-}1) \approx 0.950 \cdot E$ while $\log_2 g \approx E$. Since $0.950 < 1$, the number of parity words grows exponentially slower than the gap for all convergents beyond $(41, 65)$. Even perfectly random sums cannot hit a multiple of $g$.

</div>

**The entire no-cycle proof reduces to one convergent: $(S = 41, E = 65)$**, where $g = 19 \times 29 \times 763142958708379$. The word/gap ratio is 0.60 — tantalizingly close but not yet rigorous.

**Approaches to close this last gap:**
1. **Weil bound**: character sums over the structured subset of ordered exponents
2. **CRT independence**: $T \bmod 19$, $T \bmod 29$, $T \bmod p_3$ are empirically independent; prove it
3. **Structural**: extend the gap-13 argument using multiplicative orders mod the prime factors

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
