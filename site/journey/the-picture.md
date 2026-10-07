# The Big Picture

This chapter puts the tour's pieces side by side: how they fit together, how solid each one is, and what is still open. It is not a proof. The Collatz conjecture is open.

## A map of the ideas

Click any node to see what it says and how solid it is:

<ProofMap />

## The two questions

The conjecture can fail in two ways: an orbit could **loop**, or it could **escape** to infinity. Neither has been ruled out.

### Loops

| Piece | Status |
|------|--------|
| Negative gap ($3^S > 2^E$) gives no positive cycle | Elementary, known |
| No cycle with $S=5$, $E=8$ | Enumerated: none of the 35 parity words that start at an odd value (91 counting every starting point) |
| No cycle with $S=41$, $E=65$ | My own meet-in-the-middle search; already implied by the literature |
| No nontrivial $m$-cycles for $m \leq 91$ | Known: Simons and de Weger (2005), Hercher (2023) |
| Any nontrivial cycle has $E/S$ extremely close to $\log_2 3$ and is enormous | Known: Eliahou (1993) |
| No nontrivial cycles at all | **Open** |

See [No Loops?](/journey/no-loops) for the details.

### Escape

| Piece | Status |
|------|--------|
| The multiplier $3^s/2^{k-s}$ of every drop is at most $2^{-\beta(s)}$, with $\beta(s) = 1 - \{s \log_2 3\}$ | Elementary: the multiplier of a drop is below 1. Exactly $2^{-\beta(s)}$ in every case checked ($n \leq 10^7$); that it always is would follow from Terras's coefficient stopping time conjecture, which is open. The number itself shrinks by a little less, because of the $+1$s: $5 \to 4$ loses 0.32 bits, and $\beta(1) = 0.415$ |
| $v_2(m+1)$ countdown: every climb ends at a member of Set₃ | Elementary, proved |
| $v_2(m-1)$ countdown ends every run of weak drops: in a deep drop if $v_2(m-1)$ is even, in a new climb if it is odd | Elementary |
| Bounces before the first deep drop $\leq (B+3)/4$ | Computed for every odd $m \leq 5 \times 10^6$; over a whole orbit it fails ($m = 2919$) |
| Bits read faster than generated | The Finite Fuel bookkeeping; not measured, not proved |
| Every orbit eventually falls below its start | **Open** |

## How the pieces fit together

Every Collatz drop is a place where the halvings outpace the triplings. The carry propagation of $+1$ creates deterministic countdowns: every climb ends in a step down, and every run of weak drops ends. These are facts about the current value, not about the starting value. Natural numbers have **finite binary expansions**, and the Finite Fuel picture guesses that this is what stops the bounces; the only evidence offered is a count of bounces before the first deep drop, for odd starting values up to $5 \times 10^6$. Averaged over residue classes, an odd step together with the halvings that follow it multiplies a number by $3/4$ (geometric mean).

The gap between this picture and a proof is the gap between *on average* and *for every orbit*. Averages over residue classes hold just as well for the negative integers, where the same rule has cycles at $-1$, $-5$ and $-17$. Anything that closes the gap has to use the fact that a positive integer's bits run out — and that is the part nobody knows how to do.

## A physics analogy

Click any row to expand the analogy. It is a mnemonic for the Finite Fuel picture, not a mechanism and not evidence; the two rates in it are that picture's bookkeeping constants, not measurements.

<PhysicsAnalogy />

Summary table:

| Physics | Collatz |
|---------|---------|
| Speed of light | Carry propagation: ~1.92 bits/bounce |
| Particle velocity | Orbit growth: ~0.51 bits/bounce |
| Finite energy ($E = mc^2$) | Finite binary expansion ($B$ bits) |
| Event horizon | Position $B$: all zeros beyond |
| Heat death | Bit budget exhausted → deep drop |
| Hawking radiation | The ~0.51 bits of growth per bounce |
| Trivial zeros of $\zeta$ | Cycles at negative integers |

## The role of each ingredient

- **$\log_2 3$ irrational** → halvings and triplings never cancel exactly → the gap $2^E - 3^S$ is never zero
- **Base-6 rotation** → a picture of orbits as a slightly wobbly irrational rotation (Shakibaei Asli) → a step counter, which says nothing about size
- **$+1$ carry propagation** → deterministic countdowns → every climb ends in a forced step down (from the current value, not below the start)
- **Finite binary expansion** → a finite bit budget → the intuition for why positive integers might differ from $-1$

## Explore further

- [Affine Orbit Structure](/proofs/affine-orbit) — the piecewise-linear structure of orbits (Terras, Everett)
- [Bit Destruction](/proofs/bit-destruction) — the $\beta(s)$ picture of drops
- [Mixing Modulo Powers of Two](/proofs/mixing) — how destinations spread over residue classes
- [The Cycle Equation: Small Cases](/cycles/convergent-elimination) — the first few cases worked through by hand

<div style="text-align: center; margin-top: 24px;">
  <a href="./finite-fuel" class="vp-button medium">← Finite Fuel</a>
  <a href="/" class="vp-button medium brand" style="margin-left: 12px;">Home</a>
</div>
