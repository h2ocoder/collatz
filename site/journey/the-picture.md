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
| No cycle with $S=5$, $E=8$ | Checked by hand (0 of 91 words) |
| No cycle with $S=41$, $E=65$ | My own meet-in-the-middle search; already implied by the literature |
| No nontrivial $m$-cycles for $m \leq 91$ | Known: Simons and de Weger (2005), Hercher (2023) |
| Any nontrivial cycle has $E/S$ extremely close to $\log_2 3$ and is enormous | Known: Eliahou (1993) |
| No nontrivial cycles at all | **Open** |

See [No Loops?](/journey/no-loops) for the details.

### Escape

| Piece | Status |
|------|--------|
| Every drop removes $\beta(s) = 1 - \{s \log_2 3\}$ bits beyond break-even | Elementary restatement of "a drop is a decrease" |
| $v_2(m+1)$ countdown forces Set₃ | Elementary, proved |
| $v_2(m-1)$ countdown forces deeper drops | Elementary |
| Bounce count $\leq (B+3)/4$ | Verified for every $m \leq 5 \times 10^6$ |
| Bits consumed faster than generated | Heuristic: true on average |
| Every orbit eventually falls below its start | **Open** |

## How the pieces fit together

Every Collatz drop is a place where the halvings outpace the triplings. The carry propagation of $+1$ creates deterministic countdowns that force drops at every depth level. Natural numbers have **finite binary expansions**, and in every orbit I have tested, bounces stop once the orbit has used up the bits it started with. On average the arithmetic consumes bits faster than it creates them.

The gap between this picture and a proof is the gap between *on average* and *for every orbit*. Averages over residue classes hold just as well for the negative integers, where the same rule has cycles at $-1$, $-5$ and $-17$. Anything that closes the gap has to use the fact that a positive integer's bits run out — and that is the part nobody knows how to do.

## The physics of it

Click any row to expand the analogy:

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
- **Base-6 rotation** → a picture of orbits as a slightly wobbly irrational rotation (Shakibaei Asli)
- **$+1$ carry propagation** → deterministic countdowns → forced drops
- **Finite binary expansion** → a finite bit budget → the intuition for why positive integers might differ from $-1$

## Explore further

- [Affine Orbit Structure](/proofs/affine-orbit) — the piecewise-linear structure of orbits (Terras, Everett)
- [Bit Destruction](/proofs/bit-destruction) — the $\beta(s)$ picture of drops
- [3-Adic Mixing](/proofs/mixing) — how destinations spread over residue classes
- [Convergent Elimination](/cycles/convergent-elimination) — the cycle equation worked through small cases

<div style="text-align: center; margin-top: 24px;">
  <a href="./finite-fuel" class="vp-button medium">← Finite Fuel</a>
  <a href="/" class="vp-button medium brand" style="margin-left: 12px;">Home</a>
</div>
