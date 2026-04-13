# The Transfer Operator

## From Dynamics to Spectrum

The Collatz map acts on individual numbers, but it induces a **linear operator** on the space of distributions over $\mathbb{Z}/M\mathbb{Z}$. This is the Perron-Frobenius (or Ruelle) transfer operator:

$$\mathcal{L}[g](y) = \sum_{f(x) = y} \frac{g(x)}{|f'(x)|}$$

For the Collatz map, the two branches contribute differently:

- **Even branch** $x \mapsto x/2$: derivative $1/2$, weight $2$
- **Odd branch** $x \mapsto 3x+1$: derivative $3$, weight $1/3$

<SpectrumVisualizer />

## The Spectrum

Computing the eigenvalues of $\mathcal{L}$ on $\mathbb{Z}/M\mathbb{Z}$ for any multiple of 6 reveals a striking fact: the operator has **exactly four non-zero eigenvalues**, regardless of dimension.

| Eigenvalue | Value | Magnitude |
|------------|-------|-----------|
| $\lambda_1$ | $2$ | $2$ |
| $\lambda_2$ | $(4/3)^{1/3}$ | $\approx 1.1006$ |
| $\lambda_3$ | $(4/3)^{1/3} \cdot \omega$ | $\approx 1.1006$ |
| $\lambda_4$ | $(4/3)^{1/3} \cdot \omega^2$ | $\approx 1.1006$ |

where $\omega = e^{2\pi i/3}$ is a primitive cube root of unity.

The operator has **rank 4**. All remaining eigenvalues are exactly zero. The entire dynamics of the Collatz map, at the operator level, is captured by four modes.

## Why Cube Roots of 4/3?

The characteristic equation for the non-trivial eigenvalues is:

$$\lambda^3 = \frac{4}{3} = \frac{y^2}{n}$$

This arises because:

1. The **exponent 3** comes from the 3-fold symmetry: the map $3x+1$ cycles through residue classes mod 3 (since $3x + 1 \equiv 1 \pmod{3}$ for all $x$). The operator decomposes into three sectors related by $\omega$.

2. The **ratio $4/3$** is the energy balance: each halving contributes weight $y = 2$ (two inverse images), while each odd step contributes weight $1/n = 1/3$. Over one full cycle through all three sectors: $y^2/n = 4/3$.

For a general $(n, y)$ system, the eigenvalue equation becomes $\lambda^n = y^2/n$, and convergence requires $|y^2/n| > 1$, i.e., $y^2 > n$.

## The Critical Circle

The non-trivial eigenvalues lie on a **circle** in the complex plane:

$$|\lambda| = \left(\frac{4}{3}\right)^{1/3} \approx 1.1006$$

This is the **critical circle** — the Collatz analogue of the critical line $\text{Re}(s) = 1/2$ in the theory of the Riemann zeta function.

The Hilbert-Polya conjecture proposes that the zeros of $\zeta(s)$ are eigenvalues of a self-adjoint operator, which would force them onto the critical line. Here, the eigenvalues of the Collatz transfer operator are forced onto the critical circle by the **3-fold rotational symmetry** of the map.

| Riemann Zeta | Collatz Transfer |
|---|---|
| Zeros on the critical line $\text{Re}(s) = 1/2$ | Eigenvalues on the critical circle $\|\lambda\| = (4/3)^{1/3}$ |
| Constrained by functional equation $\zeta(s) = \chi(s)\zeta(1-s)$ | Constrained by 3-fold symmetry $\lambda \mapsto \omega\lambda$ |
| Line position forced by self-adjointness | Circle position forced by rotational symmetry |
| $1/2$ from the balance of $\Gamma$ factors | $(4/3)^{1/3}$ from the balance of weights $y^2/n$ |

## The Convergence Criterion

The trivial eigenvalue $\lambda_1 = 2$ controls the gross scaling (it comes from the halving map's weight). The **dynamically relevant** eigenvalues are $\lambda_2, \lambda_3, \lambda_4$ on the critical circle.

Convergence of all orbits requires:

$$\left(\frac{4}{3}\right)^{1/3} > 1 \quad \iff \quad \frac{4}{3} > 1 \quad \iff \quad 4 > 3$$

The entire Collatz conjecture, at the spectral level, reduces to the statement that **4 is greater than 3**.

For $5x+1$: the eigenvalue equation gives $\lambda^5 = 4/5$, so the critical circle has radius $(4/5)^{1/5} \approx 0.955 < 1$. This means the transfer operator's non-trivial modes decay — the system *mixes* efficiently. But mixing alone doesn't imply convergence: the trivial eigenvalue $\lambda_1 = 2$ still dominates, and the energy input per kick ($\log_2 5 \approx 2.32$ bits) exceeds the average drain (2 bits). The spectral gap measures how fast the system forgets its initial distribution; the criticality $\mu$ measures whether the average orbit contracts. For $5x+1$, the system mixes well but grows on average — uniform divergence.

## Self-Adjointness

The transfer operator $\mathcal{L}$ is **not** symmetric (it has asymmetry ratio $\approx 1.41$). However, its non-trivial spectrum is entirely real or comes in conjugate pairs with equal magnitude — exactly the behavior of a **normal** operator (one that commutes with its adjoint).

The 3-fold symmetry $\lambda \mapsto \omega\lambda$ is a stronger constraint than self-adjointness. It forces the eigenvalues onto a circle rather than a line, and the radius of that circle is determined by a single number: $y^2/n$.

## The Berry-Keating Connection

The Berry-Keating program seeks an operator related to the classical Hamiltonian $H = xp$ whose eigenvalues give the Riemann zeros. In the Collatz setting, the analogous Hamiltonian is:

$$H_{\text{Collatz}} = \log_2(x) \cdot v_2(3x+1)$$

This is the product of "position" (the bit-length $\log_2 x$) and "momentum" (the 2-adic valuation $v_2(3x+1)$, which controls how many halvings follow each kick). The conservation law

$$s \cdot \log_2(6) = T - \log_2(n) + \varepsilon$$

is the Collatz analogue of $E = H(x, p)$ — the total energy expressed in terms of position and momentum.

## Across the Zoo

The spectral structure changes predictably across the [Collatz Zoo](/connections/universal-dynamics):

| System | Critical circle radius | Eigenvalue equation | Convergent? |
|--------|----------------------|---------------------|-------------|
| $3x+1, \; x/2$ | $(4/3)^{1/3} \approx 1.10$ | $\lambda^3 = 4/3$ | Yes |
| $5x+1, \; x/2$ | $(4/5)^{1/5} \approx 0.96$ | $\lambda^5 = 4/5$ | No |
| $7x+1, \; x/2$ | $(4/7)^{1/7} \approx 0.92$ | $\lambda^7 = 4/7$ | No |

The critical circle shrinks below 1 as $n$ exceeds $y^2 = 4$. Only $n = 3$ keeps the radius above 1.

## Related

- [Eisenstein Lattice](/connections/eisenstein) — the eigenvalue equation as a ratio of Eisenstein norms
- [Universal Dynamics](/connections/universal-dynamics) — the thermodynamic framework and Collatz Zoo
- [abc Conjecture](/connections/abc-conjecture) — why $\text{rad}(6) = 6$ is the minimal radical
- [3-Adic Mixing](/proofs/mixing) — spectral gap on the Markov chain (related but distinct operator)
- [The Hidden Rotation](/journey/the-rotation) — the near-conjugacy to irrational rotation
