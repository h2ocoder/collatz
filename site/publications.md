# Prior Work

::: info About the Author
I'm a software engineer and polymath, not an academic mathematician. These are self-published explorations — not peer-reviewed papers. They represent several years of off-and-on investigation into the Collatz conjecture, each building on the last. This site is where that work continues.

I share them here for transparency: so you can see how the ideas developed, and judge the work on its merits.
:::

## Writings

### The Collatz Conjecture, Pythagorean Triples, and the Riemann Hypothesis
*Unveiling a Novel Connection Through Dropping Times* (2024)

The starting point. Introduces dropping sets, orbital oddity, and an unexpected connection between Collatz dynamics and Pythagorean triples, and works with the affine structure of orbits within residue classes (known since Terras, 1976, and Everett, 1977). The dropping-set language used throughout this site comes from here.

[Read on viXra (2403.0077)](https://vixra.org/abs/2403.0077)

---

### The Geometric Collatz Correspondence (2023)

Develops the geometric side: stopping classes, stopping signatures, and the modular classification of orbits. The residue class hierarchy here is the same one the countdown chapter walks through.

[Read on viXra (2309.0109)](https://vixra.org/abs/2309.0109)

---

### The Collatz Conjecture: A New Perspective on an Old Problem (2024)
*Proportional Power Ratios in Base 6*

A more accessible exploration, published on Medium. This is where I stumbled onto the base-6 structure: the Proportional Power Ratio function $P(x, 6)$ maps Collatz orbits onto a circle where they trace out something close to an irrational rotation. Shakibaei Asli (2026) independently found the same picture and proved it as a formal near-conjugacy. The 44-step spoke pattern in polar plots comes from the close approximation $27/44$ to $\log_6 3$.

[Read on Medium](https://medium.com/python-in-plain-english/the-collatz-conjecture-a-new-perspective-on-an-old-problem-f4bca7ff675a)

---

## How They Connect to This Site

| Writing | Key Idea | Where it shows up here |
|---------|----------|-------------------|
| Paper 1 (Pythagorean Triples) | Affine orbit structure, dropping sets | Foundations and Structure pages |
| Paper 2 (Geometric Correspondence) | Stopping classes, modular classification | The Countdown chapter |
| Medium article (PPR / Base-6) | Near-conjugacy to rotation by $\log_6 3$ | The Hidden Rotation chapter |
| This site (2026) | Countdown hierarchy, finite-fuel heuristic | The Tour and Connections pages |

## Key References by Others

- Shakibaei Asli, B. (2026). [An explicit near-conjugacy between the Collatz map and a circle rotation](https://arxiv.org/abs/2601.04289). *arXiv:2601.04289*
- Chang, E. Y. (2026). [A structural reduction of the Collatz conjecture to one-bit orbit mixing](https://arxiv.org/abs/2603.25753). *arXiv:2603.25753*
- Terras, R. (1976). A stopping time problem on the positive integers. *Acta Arithmetica*, 30(3), 241-252.
- Everett, C. J. (1977). Iteration of the number-theoretic function f(2n) = n, f(2n+1) = 3n+2. *Advances in Mathematics*, 25(1), 42-45.
- Steiner, R. P. (1977). A theorem on the Syracuse problem. *Proceedings of the 7th Manitoba Conference on Numerical Mathematics*, 553-559.
- Böhm, C. and Sontacchi, G. (1978). On the existence of cycles of given length in integer sequences like x_{n+1} = x_n/2 if x_n even, and x_{n+1} = 3x_n + 1 otherwise. *Atti della Accademia Nazionale dei Lincei*, 64, 260-264.
- Eliahou, S. (1993). The 3x+1 problem: new lower bounds on nontrivial cycle lengths. *Discrete Mathematics*, 118, 45-56.
- Simons, J. and de Weger, B. (2005). Theoretical and computational bounds for m-cycles of the 3n+1 problem. *Acta Arithmetica*, 117, 51-70.
- Hercher, C. (2023). There are no Collatz m-cycles with m ≤ 91. *Journal of Integer Sequences*, 26, Article 23.3.5.
- OEIS [A100982](https://oeis.org/A100982) (counts of admissible parity words) and [A122437](https://oeis.org/A122437) (possible stopping times).
- Tao, T. (2019). [Almost all orbits of the Collatz map attain almost bounded values](https://arxiv.org/abs/1909.03562). *Forum of Mathematics, Pi*.
