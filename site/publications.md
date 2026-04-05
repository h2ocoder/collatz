# Prior Work

::: info About the Author
I'm a software engineer and polymath, not an academic mathematician. These are self-published explorations — not peer-reviewed papers. They represent several years of off-and-on investigation into the Collatz conjecture, each building on the last. The proof framework on this site is the culmination of that journey.

I share them here for transparency: so you can see how the ideas developed, and judge the work on its merits.
:::

## Writings

### The Collatz Conjecture, Pythagorean Triples, and the Riemann Hypothesis
*Unveiling a Novel Connection Through Dropping Times* (2024)

The starting point. Introduces dropping sets, the affine orbit structure, orbital oddity, and an unexpected connection between Collatz dynamics and Pythagorean triples. This is where the dropping time framework — used throughout the proof — was first developed.

[Read on viXra (2403.0077)](https://vixra.org/abs/2403.0077)

---

### The Geometric Collatz Correspondence (2023)

Develops the geometric side: stopping classes, stopping signatures, and the modular classification of orbits. The residue class hierarchy introduced here is what the countdown mechanism later exploits.

[Read on viXra (2309.0109)](https://vixra.org/abs/2309.0109)

---

### The Collatz Conjecture: A New Perspective on an Old Problem (2024)
*Proportional Power Ratios and the Base-6 Discovery*

A more accessible exploration, published on Medium. This is where I stumbled onto the base-6 structure: the Proportional Power Ratio function $P(x, 6)$ maps Collatz orbits onto a circle where they trace out a near-perfect irrational rotation. I didn't know it at the time, but this was independently confirmed by Shakibaei Asli (2026) as a formal near-conjugacy. The 44-step spoke pattern in polar plots turned out to be the convergent $27/44$ of $\log_6 3$.

[Read on Medium](https://medium.com/python-in-plain-english/the-collatz-conjecture-a-new-perspective-on-an-old-problem-f4bca7ff675a)

---

## How They Connect to This Site

| Writing | Key Idea | Role in the Proof |
|---------|----------|-------------------|
| Paper 1 (Pythagorean Triples) | Affine orbit structure, dropping sets | Foundation: the piecewise-linear maps underlying bit destruction |
| Paper 2 (Geometric Correspondence) | Stopping classes, modular classification | Framework: the residue class hierarchy the countdowns traverse |
| Medium article (PPR / Base-6) | Near-conjugacy to rotation by $\log_6 3$ | Geometry: why orbits equidistribute and can't systematically dodge drops |
| This site (2026) | Countdown hierarchy, finite propagation | The proof: carry propagation consumes bits faster than orbits generate them |

## Key References by Others

- Shakibaei Asli, B. (2026). [An explicit near-conjugacy between the Collatz map and a circle rotation](https://arxiv.org/abs/2601.04289). *arXiv:2601.04289*
- Chang, E. Y. (2026). [A structural reduction of the Collatz conjecture to one-bit orbit mixing](https://arxiv.org/abs/2603.25753). *arXiv:2603.25753*
- Terras, R. (1976). A stopping time problem on the positive integers. *Acta Arithmetica*, 30(3), 241-252.
- Tao, T. (2019). [Almost all orbits of the Collatz map attain almost bounded values](https://arxiv.org/abs/1909.03562). *Forum of Mathematics, Pi*.
