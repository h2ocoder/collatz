# Lattice Path Formula

**Status:** Proved (constructive enumeration + verified for all computable cases)

## Statement

The number of residue-class subgroups within $\text{Dset}_k$ (where $k = \lceil s \cdot \log_2 6 \rceil$ for $s$ Syracuse steps) is:

$$N(s) = \#\{(a_1, \ldots, a_{s-1}) : a_1 = 1,\; a_i \geq 1,\; \textstyle\sum_{j=1}^{i} a_j < i \cdot \log_2 3 \;\;\forall\, i\}$$

The exact density of $\text{Dset}_k$ among odd $n \equiv 3 \pmod{4}$ is:

$$\text{density}(\text{Dset}_k) = \frac{N(s)}{2^{k-s-2}}$$

## The Sequence

$$N(s) = 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, 17637, 51033, 108950, \ldots$$

(Starting from $s = 1$. The first nontrivial value $N(2) = 1$ corresponds to $\text{Dset}_6$.)

| $s$ | $k = \lceil s \log_2 6 \rceil$ | $N(s)$ | Density among $3 \bmod 4$ |
|-----|------|--------|---------------------------|
| 2 | 6 | 1 | $1/4$ |
| 3 | 8 | 2 | $1/4$ |
| 4 | 11 | 3 | $3/32$ |
| 5 | 13 | 7 | $7/64$ |
| 6 | 16 | 12 | $3/64$ |
| 7 | 19 | 30 | $15/512$ |
| 8 | 21 | 85 | $85/2048$ |
| 9 | 24 | 173 | $173/8192$ |
| 10 | 26 | 476 | $119/4096$ |

All values verified exactly against empirical subgroup enumeration up to $s = 10$.

## Interpretation: Lattice Paths Below an Irrational Line

Each valid prefix $(a_1, \ldots, a_{s-1})$ is a **lattice path** in $\mathbb{Z}^2$:

- Start at $(1, a_1) = (1, 1)$
- At step $i$: move to $(i, \sum_{j=1}^{i} a_j)$
- The path must stay **strictly below** the line $y = x \cdot \log_2 3$

The constraint $\sum a_j < i \cdot \log_2 3$ says: the cumulative halvings must not outpace the cumulative $\times 3$ growth. Once they do, the orbit drops below $n$, exiting the set.

## Why $a_1 = 1$ Always

For $n \equiv 3 \pmod{4}$ (all members of $\text{Dset}_{k>3}$):

$$3n + 1 \equiv 3(3) + 1 = 10 \equiv 2 \pmod{4}$$

So $3n + 1$ is divisible by 2 but not 4, giving $v_2(3n+1) = 1$, hence $\alpha_1 = 1$ always.

## The Irrational Ceiling and Growth Irregularity

The sequence $N(s)$ grows irregularly because the fractional part $\{i \cdot \log_2 3\}$ oscillates quasi-periodically (by Weyl's equidistribution theorem). At steps where $\{i \cdot \log_2 3\}$ is large (near 1), $\lfloor i \cdot \log_2 3 \rfloor$ jumps by 2 instead of 1, giving extra headroom and a surge in valid paths.

The continued fraction of $\log_2 3 = [1; 1, 1, 2, 1, 1, 1, 2, \ldots]$ determines when these surges occur. The 44-step quasi-period (from the convergent $27/44$ of $\log_6 3$) appears here as a long-range modulation of the growth rate.

## Bandwidth and the Complementarity Principle

The valid sums $S = \sum a_i$ occupy a narrow band:

$$S \in [s, \lfloor s \cdot \log_2 3 \rfloor]$$

The **bandwidth** $B(s) = \lfloor s \cdot (\log_2 3 - 1) \rfloor + 1 \approx 0.585 \cdot s$ grows only linearly, while $N(s)$ grows exponentially. This creates the information gap underlying the [[Collatz Complementarity Principle]].

## Connection to No-Cycles Argument

In $\log_3$ coordinates, each Syracuse step adds exactly 1 and each halving subtracts $\log_3 2 \approx 0.631$. A cycle requires total displacement zero:

$$s - \textstyle\sum a_i \cdot \log_3 2 = 0 \implies \textstyle\sum a_i = s \cdot \log_2 3$$

Since $\sum a_i$ is an integer and $s \cdot \log_2 3$ is irrational, the displacement is **never zero**. The $+1$ correction in $3n+1$ adds $\epsilon(n) = \log_3(1 + 1/3n) \approx 1/(3n \ln 3)$ per step, which is exponentially smaller than the gap from Diophantine approximation for $s \geq 12$.

## Prior Art (added 2026-09-16)

The sequence $N(s) = 1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, \ldots$ is **OEIS A100982**, "Number of admissible sequences of order $n$; related to 3x+1 problem and Wagon's constant". It was defined by Wagon (1985), enumerated to order 1000 by Roosendaal (2005), and has a recursion due to Zarubin and binomial bounds due to Winkler:

$$\frac{1}{s}\binom{m_s - 1}{s - 1} \;\le\; N(s) \;\le\; \frac{1}{s}\binom{m_s}{s - 1}, \qquad m_s = \lfloor s \log_2 3 \rfloor .$$

The density formula above, summed against the stopping time, is the published definition of **Wagon's constant** $9.4779555565\ldots$ (OEIS A122790) $= \sum_s k(s)\,N(s)/2^{m_s}$, the mean stopping time of odd $n$. The bit-count $\lceil s \log_2 3 \rceil$ is A020914 and the still-undecided residues mod $2^n$ are A076227.

What is new here relative to the OEIS entries is the lattice-path reading, the connection to the affine subgroup count, and (in `research/investigate-ternary-llms/`) three exact results: an $O(s^2)$ DP reproducing the b-file to $s = 1000$; the sharp decay rate $2^{-(1 - H(1/\log_2 3))\,p}$ of the undecided fraction after $p$ bits; and the fact that $N(s)$ equals Winkler's upper bound exactly when $s$ is an upper semiconvergent of $\log_2 3$ ($s = 1, 3, 5, 17, 29, 41, 94, \ldots$). Sources: https://oeis.org/A100982 , https://oeis.org/A122790 ; S. Wagon, "The Collatz problem", *Math. Intelligencer* 7 (1985) 72–76.

## Connections

- Explains the shift densities in the [[Multiplication Symmetry Theorem]]
- The bandwidth constraint creates the [[Collatz Complementarity Principle]]
- The irrational constant $\log_2 3$ connects to the near-conjugacy result (Shakibaei Asli) and the PPR base-6 lattice
- The subgroup count determines the number of affine formulas in [[Affine Orbit Structure]]
