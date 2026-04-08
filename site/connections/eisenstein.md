# The Eisenstein Lattice

The Collatz map speaks two languages: halving ($\div 2$) and tripling ($\times 3 + 1$). These are exactly the two primes that define the **Eisenstein integers** $\mathbb{Z}[\omega]$, where $\omega = e^{2\pi i/3}$ is a primitive cube root of unity.

The Eisenstein integers form a **triangular lattice** in the complex plane. Every Collatz orbit traces a walk on this lattice — and convergence becomes a geometric question about where the walk ends.

## The Two Primes

The Eisenstein integers are complex numbers $a + b\omega$ where $a, b \in \mathbb{Z}$ and $\omega^2 + \omega + 1 = 0$. Their norm is:

$$N(a + b\omega) = a^2 - ab + b^2$$

The ring has **6 units**: $\{\pm 1, \pm\omega, \pm\omega^2\}$ — and $6 = \text{rad}(6)$, the radical that appears throughout the Collatz theory.

The two Collatz primes have distinct algebraic characters in $\mathbb{Z}[\omega]$:

| Prime | Behavior | Factorization | Norm |
|-------|----------|---------------|------|
| 2 | **Inert** (stays prime) | $(2)$ remains prime | $N(2) = 4$ |
| 3 | **Ramifies** (squares) | $3 = -(1+2\omega)^2$ | $N(1+2\omega) = 3$ |

The inert prime 2 controls **halving**. The ramified prime $1+2\omega$ controls **tripling**. Their norm ratio $N(2)/N(1+2\omega) = 4/3$ is the fundamental constant of the dynamics.

## Orbits as Lattice Walks

Each Syracuse step (triple once, then halve $\alpha$ times) corresponds to a displacement vector on the Eisenstein lattice:

$$\vec{v}_i = \alpha_i + \omega$$

where $\alpha_i = v_2(3x_i + 1)$ is the number of halvings after the $i$-th tripling. In Eisenstein coordinates, this is the lattice point $(\alpha_i, 1)$ with norm:

$$N(\alpha_i, 1) = \alpha_i^2 - \alpha_i + 1$$

| $\alpha$ | Vector $\alpha + \omega$ | Angle | Norm | Meaning |
|----------|--------------------------|-------|------|---------|
| 1 | $1 + \omega$ | 60$^\circ$ | 1 (unit) | Neutral — no net contraction |
| 2 | $2 + \omega$ | 30$^\circ$ | 3 | One net halving |
| 3 | $3 + \omega$ | 19$^\circ$ | 7 | Two net halvings |
| 4 | $4 + \omega$ | 14$^\circ$ | 13 | Strong contraction |

As $\alpha$ grows, the displacement vector rotates toward the real axis — more horizontal, more contractive. The full orbit is the sum of all displacement vectors, landing at the Eisenstein lattice point $(h, s)$ where $h$ = total halvings and $s$ = total triplings.

<EisensteinWalk />

## The Geodesic

The **geodesic** is the line $h = s \cdot \log_2 3$ on the lattice. It separates two regimes:

- **Above the geodesic** ($h/s > \log_2 3$): the orbit contracts — more halvings than needed to balance the triplings
- **Below the geodesic** ($h/s < \log_2 3$): the orbit grows — not enough halvings to compensate

Every convergent orbit must end **above** the geodesic, because:

$$h - s \cdot \log_2 3 = \log_2(x_0) + \varepsilon > 0$$

The excess above the geodesic equals the initial bit-length $\log_2(x_0)$, adjusted by the cumulative $+1$ correction $\varepsilon$.

For the orbit of 27: the walk spends **93% of its time below the geodesic** — the orbit is growing, accumulating energy. Only in the final 7% does the walk curve above, as large $\alpha$ values appear and force rapid contraction.

## The Endgame

Why do large $\alpha$ values cluster at the end of orbits? Because as the orbit value shrinks, $3x+1$ for small $x$ is more likely to be divisible by high powers of 2. The data is striking:

| $\alpha$ | Mean position in orbit | Interpretation |
|----------|----------------------|----------------|
| 1 | 0.46 | Slightly early — neutral steps dominate the growth phase |
| 2 | 0.44 | Early — moderate contraction spread throughout |
| 3 | 0.55 | Slightly late |
| $\geq 4$ | **0.74** | Late — strong contraction forced at the end |

<AlphaPositionChart />

This is the [Finite Propagation Theorem](/proofs/bit-destruction) expressed geometrically: the lattice walk **must** eventually produce large $\alpha$ steps, because modular constraints tighten exponentially as the orbit value decreases. The walk cannot stay below the geodesic forever.

## The Eigenvalue Connection

The [transfer operator](/connections/hilbert-polya) has eigenvalues satisfying:

$$\lambda^3 = \frac{4}{3} = \frac{N(2)}{N(1+2\omega)}$$

The eigenvalue equation is a statement about **Eisenstein norms**. The three non-trivial eigenvalues are:

$$\lambda_k = \left(\frac{4}{3}\right)^{1/3} \cdot \omega^k, \quad k = 0, 1, 2$$

They lie on a circle of radius $(4/3)^{1/3} \approx 1.1006$, equally spaced at $0°$, $120°$, $240°$ — because $\omega$ is a **unit of $\mathbb{Z}[\omega]$**. The critical circle is the unit circle of the Eisenstein ring, scaled by the cube root of the norm ratio.

Convergence requires the critical circle radius $> 1$:

$$(4/3)^{1/3} > 1 \iff N(2) > N(1+2\omega) \iff 4 > 3$$

## The Three Layers

The Eisenstein lattice unifies three independent proof strategies:

| Layer | Question | Tool | Answer |
|-------|----------|------|--------|
| **Thermodynamics** | Does energy dissipate on average? | Criticality $\mu = 3/4$ | Yes — $E[\alpha] = 2 > \log_2 3$ |
| **Spectral** | Can orbits avoid the average? | Transfer operator $\lambda^3 = 4/3$ | No — $N(2) > N(1+2\omega)$ |
| **Geometric** | Where does convergence happen? | Eisenstein lattice walk | Late — $\alpha \geq 4$ at position 0.74 |

All three reduce to the same arithmetic fact: in $\mathbb{Z}[\omega]$, the norm of the inert prime exceeds the norm of the ramified prime. **4 is greater than 3.**

The trivial cycle $\{1, 2, 4\}$ maps to the lattice point $(2, 1)$ with Eisenstein norm $N(2, 1) = 3$ — the norm of the ramified prime $(1+2\omega)$ itself. The ground state of the Collatz system is literally the Eisenstein prime that generates the tripling operation.

## Related

- [The Transfer Operator](/connections/hilbert-polya) — spectral analysis and the critical circle
- [Universal Dynamics](/connections/universal-dynamics) — the thermodynamic framework and Collatz Zoo
- [The Hidden Rotation](/journey/the-rotation) — the near-conjugacy to irrational rotation on the base-6 circle
- [Bit Destruction Bound](/proofs/bit-destruction) — the Finite Propagation Theorem
- [abc Conjecture](/connections/abc-conjecture) — $\text{rad}(6) = 6$ as the minimal radical
