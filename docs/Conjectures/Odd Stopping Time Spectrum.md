# Odd Stopping Time Spectrum

**Status:** Numerically verified for all odd $n < 200{,}000$ (78 distinct stopping times, max 220)

## Statement

For any odd integer $n > 1$, the stopping time $k$ (number of Collatz steps to first reach a value $< n$) satisfies

$$k = \lceil s \cdot \log_2 6 \rceil$$

where $s$ is the number of Syracuse (odd-to-odd) steps in the stopping orbit.

Equivalently: the **only** stopping times possible for odd numbers are members of the sequence $3, 6, 8, 11, 13, 16, 19, 21, 24, 26, 29, 32, \ldots$

All other positive integers are **impossible** as stopping times for odd numbers.

## Derivation

Each Syracuse step consists of:
- 1 odd step: $n \to 3n+1$ (multiply by 3)
- $\alpha_i$ even steps: halve until odd (divide by $2^{\alpha_i}$)

So $k = s + \sum_{i=1}^{s} \alpha_i$.

The orbit drops below $n$ when $\prod (3/2^{\alpha_i}) < 1$, i.e., $3^s < 2^{\sum \alpha_i}$, requiring $\sum \alpha_i \geq \lceil s \log_2 3 \rceil$.

Crucially, stopping occurs at the **first** halving that brings the value below $n$. Extra halvings beyond the minimum would cause the orbit to drop sooner (within the same Syracuse step), not later. Therefore:

$$k = s + \lceil s \log_2 3 \rceil = \lceil s(1 + \log_2 3) \rceil = \lceil s \log_2 6 \rceil$$

## Connection to Base-6 Structure

$\log_2 6 = \log_2(2 \cdot 3)$ reflects the fundamental competition in Collatz dynamics: multiplication by 3 vs division by powers of 2. This is the same base-6 lattice structure identified in Paper 3 ("A New Perspective on an Old Problem") via the [[Proportional Power Ratio]].

## 2-Adic Determinism

Each stopping class $k(s)$ corresponds to a union of residue classes mod $2^{p(s)}$ for some power $p(s)$:

| $s$ | $k = \lceil s \log_2 6 \rceil$ | Resolved at $2^p$ | Residue classes |
|-----|-------------------------------|-------------------|-----------------|
| 1   | 3                             | $2^2$             | $n \equiv 1 \pmod{4}$ |
| 2   | 6                             | $2^4$             | $n \equiv 3 \pmod{16}$ |
| 3   | 8                             | $2^5$             | $n \equiv 11, 23 \pmod{32}$ |
| 4   | 11                            | $2^7$             | $n \equiv 7, 15, 59 \pmod{128}$ |
| 5   | 13                            | $2^8$             | 7 classes mod 256 |
| 6   | 16                            | $2^{10}$          | 12 classes mod 1024 |
| 7   | 19                            | $2^{12}$          | 30 classes mod 4096 |

The fraction resolved converges to 1: by $2^{12}$, **89%** of odd numbers are classified (exactly $911/1024$). The undecided fraction after $p$ low bits decays as $2^{-(1 - H(1/\log_2 3))\,p + o(p)} = 2^{-0.0500\,p}$, so each further bit resolves only about 3.4% of what remains (see `research/investigate-ternary-llms/Winkler Tail Bound.md`).

## Prior Art (added 2026-09-16)

The allowable stopping times $3, 6, 8, 11, 13, 16, 19, 21, \ldots$ are **OEIS A122437** (T. D. Noe, 2006), with the formula $a(n+1) = \lfloor 1 + n + n \log_2 3 \rfloor$ and the comment that $a(n)$ is the number of binary digits of $6^{\,n-1}$ — i.e. $k(s) = \operatorname{bitlen}(6^s) = s + \operatorname{bitlen}(3^s)$, the stopping time is the number of bits needed to store $s$ base-6 digits. The underlying fact goes back to Terras (1976); Wagon (1985) tabulates it. This note's contribution is the derivation and the 2-adic table, not the spectrum itself. Sources: https://oeis.org/A122437 , https://oeis.org/A020914 (the halving count $\lceil s \log_2 3 \rceil$), https://oeis.org/A060445 (dropping time of $2n+1$).

## Related

- [[Stopping Class]]
- [[Syracuse Map]]
- [[Alpha Value]]
- [[Proportional Power Ratio]]
