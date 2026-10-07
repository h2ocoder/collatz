# Bit Destruction

A way of measuring how big a drop is, in bits. It is an explainer: the fact that $\beta(s) > 0$ is just a restatement of "a drop is a decrease", and it is not a step toward proving convergence.

## Statement

<div class="theorem">

**Identity.** A drop of $k$ steps, $s$ of them odd, has contraction ratio $3^s/2^{k-s}$, which removes $(k-s) - s \log_2 3$ bits. The ratio has to be below 1, so $k - s \geq \lfloor s \log_2 3 \rfloor + 1$, and with exactly that many halvings it removes

$$\beta(s) = \lfloor s \cdot \log_2 3 \rfloor + 1 - s \cdot \log_2 3 = 1 - \{s \cdot \log_2 3\}$$

bits, where $\{x\}$ is the fractional part. So $\beta(s)$ is positive and at most 1, and it equals 1 only at $s = 0$, because $\log_2 3$ is irrational.

Every dropping set with $k \le 39$, and every $n \le 10^7$, uses exactly this smallest number of halvings. It is not proved that every $n$ does (see [Affine Orbit Structure](/proofs/affine-orbit)).

</div>

## Why it is interesting

A drop through a set with small $\beta(s)$ barely shrinks the number. How small $\beta(s)$ can get is governed by how well $\log_2 3$ can be approximated by rationals, which ties the size of drops to Diophantine approximation.

## The Bit Destruction Landscape

Table of $\beta(s)$ for $s = 0$ through $29$:

| $s$ | $s \cdot \log_2 3$ | $\beta(s)$ | Set$_k$ | Status |
|-----|---------------------|-------------|---------|--------|
| 0 | 0.000 | 1.000 | 1 | |
| 1 | 1.585 | 0.415 | 3 | |
| 2 | 3.170 | 0.830 | 6 | |
| 3 | 4.755 | 0.245 | 8 | |
| 4 | 6.340 | 0.660 | 11 | |
| 5 | 7.925 | 0.075 | 13 | **slow** |
| 6 | 9.510 | 0.490 | 16 | |
| 7 | 11.095 | 0.905 | 19 | |
| 8 | 12.680 | 0.320 | 21 | |
| 9 | 14.265 | 0.735 | 24 | |
| 10 | 15.850 | 0.150 | 26 | slow |
| 11 | 17.435 | 0.565 | 29 | |
| 12 | 19.020 | 0.980 | 32 | |
| 13 | 20.605 | 0.395 | 34 | |
| 14 | 22.189 | 0.811 | 37 | |
| 15 | 23.774 | 0.226 | 39 | |
| 16 | 25.359 | 0.641 | 42 | |
| 17 | 26.944 | 0.056 | 44 | **slow** |
| 18 | 28.529 | 0.471 | 47 | |
| 19 | 30.114 | 0.886 | 50 | |
| 20 | 31.699 | 0.301 | 52 | |
| 21 | 33.284 | 0.716 | 55 | |
| 22 | 34.869 | 0.131 | 57 | slow |
| 23 | 36.454 | 0.546 | 60 | |
| 24 | 38.039 | 0.961 | 63 | |
| 25 | 39.624 | 0.376 | 65 | |
| 26 | 41.209 | 0.791 | 68 | |
| 27 | 42.794 | 0.206 | 70 | |
| 28 | 44.379 | 0.621 | 73 | |
| 29 | 45.964 | 0.036 | 75 | **slow** |

Pattern: slow sets occur when $s \cdot \log_2 3$ approaches an integer from below.

## Proof

<div class="proof">

The contraction ratio for a drop of $k$ steps with $s$ odd steps is $3^s / 2^{k-s}$. With the smallest number of halvings that brings the ratio below 1, $k - s = \lfloor s \cdot \log_2 3 \rfloor + 1$ (these values of $k$ are OEIS A122437).

The bits destroyed equal the negative log of the contraction ratio:

$$\beta(s) = -\log_2\!\left(\frac{3^s}{2^{k-s} }\right) = (k-s) - s \cdot \log_2 3 = \lfloor s \cdot \log_2 3 \rfloor + 1 - s \cdot \log_2 3$$

A fractional part is always below 1, so $\beta(s) = 1 - \{s \cdot \log_2 3\} > 0$ always.

</div>

## How small can $\beta(s)$ get?

The slowest sets come from rational approximations $p/s$ to $\log_2 3$ that lie just **above** it, so that $s \log_2 3$ falls just short of the integer $p$:

| $p$ | $s$ | $p/s$ | $\beta(s)$ |
|-----|---------|-------|-------------|
| 8 | 5 | 1.600 | 0.075 |
| 65 | 41 | 1.585 | 0.017 |
| 485 | 306 | 1.585 | 0.0015 |

(Convergents that lie just below $\log_2 3$, such as $19/12$ and $84/53$, give $\beta(s)$ close to 1 instead.)

Since $\log_2 3$ is transcendental, the lower bounds that are proved come from Baker's theory of linear forms in logarithms: $|E - S \log_2 3| > S^{-\kappa}$ for an effective constant $\kappa$ (Rhin: $\kappa \approx 13$). So $\beta(s)$ can shrink as $s$ grows, but not faster than a power of $s$.

## What this does not say

Knowing that every drop removes a positive number of bits says nothing about how many times an orbit drops, or whether it grows without bound between drops. It is a convenient scale for measuring drops, not an ingredient of a proof.

## Related

- [Affine Orbit Structure](/proofs/affine-orbit) — the contraction ratio $3^s/2^{k-s}$
- [Mixing Modulo Powers of Two](/proofs/mixing) — how drops spread numbers over residue classes
- [abc Conjecture Connection](/connections/abc-conjecture) — the size of $2^E - 3^S$
