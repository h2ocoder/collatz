# The Eisenstein Lattice

The Collatz map speaks two languages: halving ($\div 2$) and tripling ($\times 3 + 1$). Both primes have a clean description in the **Eisenstein integers** $\mathbb{Z}[\omega]$, where $\omega = e^{2\pi i/3}$ is a primitive cube root of unity: 3 is the one prime that ramifies there, and 2 is the smallest prime that stays prime.

The Eisenstein integers form a **triangular lattice** in the complex plane. Every Collatz orbit can be drawn as a walk on this lattice, which turns questions about convergence into geometric questions about where the walk goes. This page is an exploration: a way of looking, not a set of results about every orbit.

## The Two Primes

The Eisenstein integers are complex numbers $a + b\omega$ where $a, b \in \mathbb{Z}$ and $\omega^2 + \omega + 1 = 0$. Their norm is:

$$N(a + b\omega) = a^2 - ab + b^2$$

The ring has **6 units**: $\{\pm 1, \pm\omega, \pm\omega^2\}$.

The two Collatz primes have distinct algebraic characters in $\mathbb{Z}[\omega]$:

| Prime | Behavior | Factorization | Norm |
|-------|----------|---------------|------|
| 2 | **Inert** (stays prime) | $(2)$ remains prime | $N(2) = 4$ |
| 3 | **Ramifies** (squares) | $3 = -(1+2\omega)^2$ | $N(1+2\omega) = 3$ |

Halving is division by the inert prime 2. Tripling is multiplication by $3 = -(1+2\omega)^2$, up to sign the square of the ramified prime. The norms $N(2) = 4$ and $N(1+2\omega) = 3$ are in the ratio $4/3$, the same number as in the average-drift heuristic (two halvings per tripling). I use that as a way of writing the heuristic, not as an explanation of it.

## Orbits as Lattice Walks

Each Syracuse step (triple once, then halve $\alpha$ times) is recorded as a displacement vector on the Eisenstein lattice:

$$\vec{v}_i = \alpha_i + \omega$$

where $\alpha_i = v_2(3x_i + 1)$ is the number of halvings after the $i$-th tripling. In Eisenstein coordinates, this is the lattice point $(\alpha_i, 1)$ with norm:

$$N(\alpha_i, 1) = \alpha_i^2 - \alpha_i + 1$$

| $\alpha$ | Vector $\alpha + \omega$ | Angle | Norm | Meaning |
|----------|--------------------------|-------|------|---------|
| 1 | $1 + \omega$ | 60$^\circ$ | 1 (unit) | Growth: $x$ becomes about $\tfrac32 x$ |
| 2 | $2 + \omega$ | 30$^\circ$ | 3 | Shrinks: about $\tfrac34 x$ |
| 3 | $3 + \omega$ | 19$^\circ$ | 7 | Shrinks: about $\tfrac38 x$ |
| 4 | $4 + \omega$ | 14$^\circ$ | 13 | Shrinks: about $\tfrac{3}{16} x$ |

As $\alpha$ grows, the displacement vector rotates toward the real axis — more horizontal, more contractive. The full orbit is the sum of all displacement vectors, landing at the Eisenstein lattice point $(h, s)$ where $h$ = total halvings and $s$ = total triplings.

<EisensteinWalk />

## The Geodesic

The **geodesic** is the line $h = s \cdot \log_2 3$ on the lattice. Which side of it the walk is on records where the orbit stands relative to its starting value:

- **Above the geodesic** ($h/s > \log_2 3$): more halvings so far than the triplings need — the value is back at or below its start, give or take the $+1$ corrections
- **Below the geodesic** ($h/s < \log_2 3$): not enough halvings yet to compensate — the value is above its start

Every orbit that reaches 1 ends **above** the geodesic. This is an identity, not a finding:

$$h - s \cdot \log_2 3 = \log_2(x_0) + \lvert\varepsilon\rvert > 0$$

The excess above the geodesic equals the initial bit-length $\log_2(x_0)$ plus the size of the cumulative $+1$ correction $\varepsilon$ (the same $\varepsilon$ as in the [conservation law](/connections/universal-dynamics)).

For the orbit of 27: 38 of the 41 points of the walk (93%) lie below the geodesic, where the value is above 27. The walk first gets above the line at step 37, and it ends above it with the steps $53 \to 5 \to 1$, which have $\alpha = 5$ and $\alpha = 4$.

## The Endgame

In a sample of orbits, large $\alpha$ values sit late. For the odd starts from 3 to 5999 (orbits with at least five odd steps), the mean relative position of each kind of step is:

| $\alpha$ | Mean position in orbit | Interpretation |
|----------|----------------------|----------------|
| 1 | 0.46 | Slightly early — these are the growth steps |
| 2 | 0.45 | Slightly early |
| 3 | 0.55 | Slightly late |
| $\geq 4$ | **0.70** | Late |

<AlphaPositionChart />

Much of this is built in rather than discovered. The last step of every orbit that reaches 1 comes from 5, 21, 85, … and so always has $\alpha \geq 4$; with that final step left out, the mean for $\alpha \geq 4$ falls to 0.60, and over the odd starts below $10^5$ it is 0.65 (0.57 without the final step). It is not that small numbers are more divisible: the share of odd $x$ with $v_2(3x+1) \geq 4$ is $1/8$ at every size. Likewise every orbit that reaches 1 ends above the geodesic, by the identity above. Whether any walk stays below the geodesic forever is open: such a walk would belong to a number that never falls below its start, a counterexample to the conjecture.

## The Eigenvalue Connection

The matrix on the [transfer operator](/connections/hilbert-polya) page has three eigenvalues satisfying:

$$\lambda^3 = \frac{4}{3} = \frac{N(2)}{N(1+2\omega)}$$

The equation comes from the trivial cycle $1 \to 4 \to 2 \to 1$: two halvings of weight 2 and one tripling of weight $1/3$ (see that page). The numbers 4 and 3 are also the norms of the Eisenstein primes 2 and $1+2\omega$, so it can be *written* as a ratio of **Eisenstein norms**; nothing about $\mathbb{Z}[\omega]$ was used to get it. The three eigenvalues are:

$$\lambda_k = \left(\frac{4}{3}\right)^{1/3} \cdot \omega^k, \quad k = 0, 1, 2$$

They lie on a circle of radius $(4/3)^{1/3} \approx 1.1006$, equally spaced at $0°$, $120°$, $240°$, as the three cube roots of any positive number are. The three directions are the Eisenstein units $1, \omega, \omega^2$.

The radius exceeds 1 exactly because $4 > 3$:

$$(4/3)^{1/3} > 1 \iff N(2) > N(1+2\omega) \iff 4 > 3$$

It is the same inequality, $2^2 > 3$, that appears in the average-drift heuristic, because the trivial cycle has the average number of halvings, two. It is a statement about the trivial cycle, not about every orbit, and the same matrix for $5x+1$ also has radius above 1.

## The Three Layers

Three ways of looking, side by side:

| Layer | Question | Tool | What it shows |
|-------|----------|------|--------|
| **Thermodynamics** | Does energy dissipate on average? | Criticality $\mu = 3/4$ | Yes — $E[\alpha] = 2 > \log_2 3$ |
| **Spectral** | What does the cut-off matrix show? | Transfer matrix $\lambda^3 = 4/3$ | The trivial cycle: two halvings, one tripling |
| **Geometric** | Where do the large steps sit? | Eisenstein lattice walk | Late in the sample — $\alpha \geq 4$ at mean position 0.70 (0.60 without the forced last step) |

The first two come back to one arithmetic fact, $2^2 > 3$: an odd step is followed by two halvings on average, and by exactly two around the trivial cycle. In $\mathbb{Z}[\omega]$ the same inequality reads $N(2) > N(1+2\omega)$, which is a way of writing it, not a reason for it. **4 is greater than 3** is the heuristic for why orbits shrink on average. It does not show that every orbit does.

One lap of the trivial cycle $\{1, 2, 4\}$ is the step $2 + \omega$, the lattice point $(2, 1)$, whose norm is 3: it is the ramified prime $1+2\omega$ times the unit $-\omega$. That is a pleasant coincidence of the encoding, not a structural fact: the norm of $\alpha + \omega$ is $\alpha^2 - \alpha + 1$, which equals 3 at $\alpha = 2$.

## Related

- [The Transfer Operator](/connections/hilbert-polya) — the matrix whose three eigenvalues are the cube roots of $4/3$
- [The Collatz Zoo](/connections/universal-dynamics) — the $nx+c$ family and the thermodynamic analogy
- [The Hidden Rotation](/journey/the-rotation) — the base-6 circle: an irrational rotation plus a small perturbation
- [Finite Fuel](/journey/finite-fuel) — a heuristic picture, not a proof, of why positive integers might not keep climbing
- [abc Conjecture](/connections/abc-conjecture) — how close powers of 2 and 3 can be
