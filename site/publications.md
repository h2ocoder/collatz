# Prior Work

::: info About the Author
I'm a software engineer, not an academic mathematician. These are self-published explorations — not peer-reviewed papers. They represent several years of off-and-on investigation into the Collatz conjecture, each building on the last. This site is where that work continues.

I share them here for transparency: so you can see how the ideas developed, and judge the work on its merits.
:::

## Writings

### The Collatz Conjecture, Pythagorean Triples, and the Riemann Hypothesis
*Unveiling a Novel Connection Through Dropping Times* (2024)

The most recent of the three, and the source of the dropping-set language used throughout this site. It sorts the integers into *dropping sets* by dropping time (the classification by stopping time goes back to Terras, 1976), counts the odd steps in each (*orbital oddity*), and observes that the first few sets are arithmetic progressions. Neither of the two connections in its title is special to Collatz. Its Pythagorean triples come from putting a number $n$ and its dropping destination $d$ into Euclid's formula, $(n^2 - d^2,\; 2nd,\; n^2 + d^2)$, which gives a triple for any pair of integers $n > d > 0$. Its "critical line" is a real part of $\tfrac12$ that turns out to be the identity $\mathrm{Re}\,\frac{(n-d) + di}{n + ni} = \tfrac12$, true for any two numbers, so it shows no link to the Riemann hypothesis.

[Read on viXra (2403.0077)](https://vixra.org/abs/2403.0077)

---

### The Geometric Collatz Correspondence (2023)

The earlier of the two papers. It sorts the integers into *stopping classes* by stopping time (the same sets as the dropping sets above, under an earlier name), gives each number a *stopping signature*, and plots each number as a point in the plane. By its own account its statements are conjectures without rigorous proofs, most of them tested on the first million integers. The [Terminology Map](/foundations/terminology) lines its vocabulary up with the later paper's.

[Read on viXra (2309.0109)](https://vixra.org/abs/2309.0109)

---

### The Collatz Conjecture: A New Perspective on an Old Problem (2022)
*Proportional Power Ratios in Base 6*

A more accessible exploration, published on Medium, and the earliest of the three. This is where I first plotted Collatz orbits against powers of 6: the Proportional Power Ratio $P(x, 6)$, the position of $x$ between consecutive powers of 6, turns an orbit into a strikingly regular pattern, with a 44-step near-repeat that I could not explain at the time. The explanation is that in base-6 logarithmic coordinates every Collatz step is close to a rotation by $\log_6 3$; Shakibaei Asli (2026) made this precise as an explicit near-conjugacy with a bounded error. The 44 in the article's polar plots is partly a plotting effect (the angle there is the step index in radians, and 44 radians is almost exactly 7 full turns) and partly arithmetic ($44 \log_6 3 \approx 26.98$, so the radius nearly repeats as well).

[Read on Medium](https://medium.com/python-in-plain-english/the-collatz-conjecture-a-new-perspective-on-an-old-problem-f4bca7ff675a)

---

## How They Connect to This Site

| Writing | Key Idea | Where it shows up here |
|---------|----------|-------------------|
| Paper 1 (Pythagorean Triples) | The dropping-set vocabulary | Foundations and Structure pages |
| Paper 2 (Geometric Correspondence) | Stopping classes, the same sets under an earlier name | Terminology Map |
| Medium article (PPR / Base-6) | Base-6 plots of orbits and their 44-step near-repeat | The Hidden Rotation chapter |
| This site (2026) | Countdown hierarchy, finite-fuel heuristic | The Tour and Connections pages |

## Key References by Others

- Shakibaei Asli, B. (2026). [An explicit near-conjugacy between the Collatz map and a circle rotation](https://arxiv.org/abs/2601.04289). *arXiv:2601.04289*
- Terras, R. (1976). A stopping time problem on the positive integers. *Acta Arithmetica*, 30(3), 241-252.
- Everett, C. J. (1977). Iteration of the number-theoretic function f(2n) = n, f(2n+1) = 3n+2. *Advances in Mathematics*, 25(1), 42-45.
- Steiner, R. P. (1977). A theorem on the Syracuse problem. *Proceedings of the 7th Manitoba Conference on Numerical Mathematics*, 553-559.
- Böhm, C. and Sontacchi, G. (1978). On the existence of cycles of given length in integer sequences like x_{n+1} = x_n/2 if x_n even, and x_{n+1} = 3x_n + 1 otherwise. *Atti della Accademia Nazionale dei Lincei*, 64, 260-264.
- Lagarias, J. C. (1985). The 3x+1 problem and its generalizations. *American Mathematical Monthly*, 92(1), 3-23.
- Eliahou, S. (1993). The 3x+1 problem: new lower bounds on nontrivial cycle lengths. *Discrete Mathematics*, 118, 45-56.
- Simons, J. and de Weger, B. (2005). Theoretical and computational bounds for m-cycles of the 3n+1 problem. *Acta Arithmetica*, 117, 51-70.
- Hercher, C. (2023). There are no Collatz m-cycles with m ≤ 91. *Journal of Integer Sequences*, 26, Article 23.3.5.
- Rozier, O. and Terracol, C. (2026). [Paradoxical behavior in Collatz sequences](https://arxiv.org/abs/2502.00948). *Discrete Mathematics*, 349, 115167.
- Winkler, M. (2026). [Admissible qx+1 sequences, semiconvergents, and rational Catalan numbers](https://arxiv.org/abs/2609.22303). *arXiv:2609.22303*
- OEIS [A060445](https://oeis.org/A060445) (dropping times of the odd numbers), [A100982](https://oeis.org/A100982) (counts of admissible parity words) and [A122437](https://oeis.org/A122437) (allowable dropping times).
- Tao, T. (2019). [Almost all orbits of the Collatz map attain almost bounded values](https://arxiv.org/abs/1909.03562). arXiv:1909.03562; published in *Forum of Mathematics, Pi*, 10 (2022), e12.
