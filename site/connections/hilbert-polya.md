# The Transfer Operator

This page is an exploration. It builds a small matrix from the Collatz rule, computes its spectrum, and finds that the spectrum records the fixed point 0 and the trivial cycle $1 \to 4 \to 2 \to 1$, and nothing else. The comparison with the Riemann zeta function further down is an analogy between two pictures, not a mechanism.

## From Dynamics to Spectrum

The Collatz map acts on individual numbers. Cut it off at a modulus $M$ and it becomes a map on the finite set $\{0, 1, \dots, M-1\}$: halve an even number as an integer, and send an odd $x$ to $3x+1$ reduced modulo $M$. This is a model, not the map induced on residues, because $x/2$ modulo $M$ is not determined by $x$ modulo $M$. On that finite set one can write down a matrix in the style of the Perron-Frobenius (or Ruelle) transfer operator:

$$\mathcal{L}[g](y) = \sum_{f(x) = y} \frac{g(x)}{|f'(x)|}$$

For the Collatz map, the two branches contribute differently:

- **Even branch** $x \mapsto x/2$: derivative $1/2$, weight $2$
- **Odd branch** $x \mapsto 3x+1$: derivative $3$, weight $1/3$

So each column of the matrix has a single non-zero entry: $2$ in row $x/2$ for an even $x$, and $1/3$ in row $(3x+1) \bmod M$ for an odd $x$.

<SpectrumVisualizer />

## The Spectrum

For $M = 6, 12, 24, 48, 96$ (the sizes offered above; computed, and the same holds for every multiple of 6 below 114) this matrix has **exactly four non-zero eigenvalues**:

| Eigenvalue | Value | Magnitude |
|------------|-------|-----------|
| $\lambda_1$ | $2$ | $2$ |
| $\lambda_2$ | $(4/3)^{1/3}$ | $\approx 1.1006$ |
| $\lambda_3$ | $(4/3)^{1/3} \cdot \omega$ | $\approx 1.1006$ |
| $\lambda_4$ | $(4/3)^{1/3} \cdot \omega^2$ | $\approx 1.1006$ |

where $\omega = e^{2\pi i/3}$ is a primitive cube root of unity.

All remaining eigenvalues are exactly zero. That is not the same as rank 4: the rank is 14 at $M = 24$, and the rest of the matrix is nilpotent, the part of the map that lies on no loop.

It is not true for every multiple of 6. At $M = 114$ the reduction modulo $M$ closes an extra loop, $23 \to 70 \to 35 \to 106 \to 53 \to 46 \to 23$ (because $3 \cdot 53 + 1 = 160 \equiv 46$), and six more non-zero eigenvalues appear, of modulus $\sqrt{2/3} \approx 0.816$.

## Why Cube Roots of 4/3?

There is an elementary reason. Every number in $\{0, \dots, M-1\}$ has exactly one image, so the matrix is a weighted map on a finite set, and the non-zero eigenvalues of such a matrix are the $\ell$-th roots of the product of the weights around each loop of length $\ell$.

1. The fixed point $0 \to 0$ carries weight 2. That is $\lambda_1 = 2$.

2. The trivial cycle $1 \to 4 \to 2 \to 1$ has length 3 and weights $\tfrac13 \cdot 2 \cdot 2 = \tfrac43$. That gives the three cube roots of $4/3$:

$$\lambda^3 = \frac{4}{3}$$

For the moduli above, the cut-off map has no other loop, so nothing else is non-zero. The four eigenvalues are the fixed point at 0 and the trivial cycle, seen through the matrix. The exponent 3 is the length of that cycle and $4/3$ is its two halvings against one tripling. Neither is a formula in the multiplier, as the [table for other multipliers](#across-the-zoo) shows.

## The Critical Circle

The three non-trivial eigenvalues lie on a **circle** in the complex plane:

$$|\lambda| = \left(\frac{4}{3}\right)^{1/3} \approx 1.1006$$

I call this the **critical circle**, by loose analogy with the critical line $\text{Re}(s) = 1/2$ in the theory of the Riemann zeta function.

The Hilbert-Pólya conjecture proposes that the non-trivial zeros of $\zeta(s)$ correspond to the eigenvalues of a self-adjoint operator, which would force them onto the critical line. Here the three eigenvalues share a circle for a much plainer reason: they are the three cube roots of one number, because the trivial cycle has three steps. Nothing like self-adjointness is involved. The resemblance to the critical line is a resemblance of pictures only.

| Riemann zeta | This matrix |
|---|---|
| Non-trivial zeros conjectured to lie on the line $\text{Re}(s) = 1/2$ (the Riemann hypothesis, open) | Three eigenvalues on the circle $\lvert\lambda\rvert = (4/3)^{1/3}$ (computed, and elementary) |
| Zeros symmetric under $s \mapsto 1-s$ by the functional equation | Eigenvalues permuted by $\lambda \mapsto \omega\lambda$, because they are cube roots of one number |
| A self-adjoint operator would put them on the line (Hilbert-Pólya, a conjecture) | The length of the trivial cycle puts them on the circle |
| $1/2$ is the centre of the symmetry $s \mapsto 1-s$ | $(4/3)^{1/3}$ comes from the weights $\tfrac13 \cdot 2 \cdot 2$ around $1 \to 4 \to 2 \to 1$ |

## What 4 > 3 does and doesn't say

The eigenvalue $\lambda_1 = 2$ is the fixed point $0 \to 0$ with its halving weight. The other three, $\lambda_2, \lambda_3, \lambda_4$, are the trivial cycle.

The radius of the critical circle exceeds 1 exactly because

$$\left(\frac{4}{3}\right)^{1/3} > 1 \quad \iff \quad \frac{4}{3} > 1 \quad \iff \quad 4 > 3$$

This is the statement that the trivial cycle has two halvings for one tripling, $2^2 > 3$. It does **not** reduce the Collatz conjecture to $4 > 3$, and it is not special to $3x+1$. Around any cycle of positive integers of $nx+1$, with $E$ halvings and $S$ odd steps at the odd values $x_i$, the product of the weights is $2^E/n^S = \prod (1 + 1/(n x_i)) > 1$. So the radius is above 1 for $5x+1$ and $7x+1$ as well (about $1.036$ and $1.034$ at $M = 24$). For $3x-1$ the same product is below 1: its cycles $1 \to 2 \to 1$ and $5 \to 14 \to 7 \to 20 \to 10 \to 5$ give radii $0.816$ and $0.977$, and they are cycles all the same. The matrix only records the loops of the map cut off at $M$. It cannot see an orbit that climbs out of the window, and the size of an eigenvalue says nothing about which other cycles exist.

What separates $5x+1$ from $3x+1$ heuristically is not this spectrum but the average drift: an odd step of $5x+1$ adds $\log_2 5 \approx 2.32$ bits against an average of 2 halvings, where $3x+1$ adds $\log_2 3 \approx 1.58$. Most $5x+1$ orbits appear to grow without bound, although no single one has been proved to, and $5x+1$ also has cycles (through 1, 13 and 17).

## Self-Adjointness

The matrix is **not** symmetric (in the Frobenius norm, the size of $L - L^{T}$ relative to $L$ is 1.36 at $M = 24$ and 1.40 at $M = 96$), so nothing like the Hilbert-Pólya mechanism applies. Its non-trivial eigenvalues lie on a circle only because they are the cube roots of one number, the weight $4/3$ of the trivial cycle.

## A Berry-Keating-style analogy

The Berry-Keating program seeks an operator related to the classical Hamiltonian $H = xp$ whose eigenvalues give the Riemann zeros. Purely by analogy, one can write down

$$H_{\text{Collatz} } = \log_2(x) \cdot v_2(3x+1)$$

This is the product of "position" (the bit-length $\log_2 x$) and "momentum" (the 2-adic valuation $v_2(3x+1)$, the number of halvings that follow an odd step). I have not done anything with this expression: it is not an operator, nothing has been quantised, and no spectrum has been derived from it.

## Across the Zoo

The same matrix for other multipliers in the [Collatz Zoo](/connections/universal-dynamics), at $M = 24$ (computed):

| System | Loop through 1 | Eigenvalue equation | Radius | Average drift (heuristic) |
|--------|----------------|---------------------|--------|---------------------------|
| $3x+1, \; x/2$ | $1 \to 4 \to 2 \to 1$ | $\lambda^3 = 4/3$ | $\approx 1.101$ | Down |
| $5x+1, \; x/2$ | $1 \to 6 \to 3 \to 16 \to 8 \to 4 \to 2 \to 1$ | $\lambda^7 = 32/25$ | $\approx 1.036$ | Up |
| $7x+1, \; x/2$ | $1 \to 8 \to 4 \to 2 \to 1$ | $\lambda^4 = 8/7$ | $\approx 1.034$ | Up |

The radius is above 1 in every row, so it does not follow the drift. It reports that each map has a cycle through 1, and nothing more. (For $7x+1$ the reduction modulo 24 also creates a spurious loop $3 \to 22 \to 11 \to 6 \to 3$, with $\lambda^4 = 4/49$.)

## Related

- [Eisenstein Lattice](/connections/eisenstein) — the same $4/3$ written as a ratio of Eisenstein norms
- [The Collatz Zoo](/connections/universal-dynamics) — the average-drift heuristic across the $nx+c$ family
- [abc Conjecture](/connections/abc-conjecture) — how close powers of 2 and 3 can be
- [Mixing Modulo Powers of Two](/proofs/mixing) — how drops spread numbers over residue classes (averages, not individual orbits)
- [The Folded Pentagon](/explore/folded-pentagon) — a different operator again, the residue chain modulo 5, which forgets a starting residue at the rate $\cos 36^\circ = \varphi/2$ exactly
- [The Hidden Rotation](/journey/the-rotation) — the base-6 circle: an irrational rotation plus a small perturbation
