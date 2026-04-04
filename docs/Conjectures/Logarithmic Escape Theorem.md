# Logarithmic Escape Theorem

**Status:** Proved by induction (modular tightening argument)

## Statement

For any [[Dropping Set]] $\text{Dset}_k$ with period $P = 2^{k-s}$, the maximum number of consecutive self-transitions (orbit steps where both $n$ and $\text{dest}(n)$ belong to $\text{Dset}_k$) starting from $n$ is at most

$$m \leq \log_P(n) - 1$$

Equivalently: **no orbit can remain in the same dropping set for more than $O(\log n)$ consecutive drops.**

## Examples

| $k$ | $P$ | Bound | $n = 10^6$ gives $m \leq$ |
|-----|-----|-------|---------------------------|
| 3   | 4   | $\log_4 n$ | 9 |
| 6   | 16  | $\log_{16} n$ | 4 |
| 8   | 32  | $\log_{32} n$ | 3 |
| 13  | 256 | $\log_{256} n$ | 2 |

Even Set$_{13}$ with contraction ratio 0.949 (barely contracting) forces escape after $\sim 2$ steps for any $n < 10^6$.

## Proof (Modular Tightening)

Each self-transition multiplies the required modular constraint by $P$.

**Claim:** $m$ consecutive self-transitions require $n$ to satisfy a specific residue class mod $P^{m+1}$.

**Base** ($m = 0$): Membership in $\text{Dset}_k$ requires $n \equiv r \pmod{P}$.

**Inductive step:** Suppose $m$ self-transitions require $n \equiv r_m \pmod{P^{m+1}}$.

Write $n = P^{m+1} \cdot a + r_m$. Then by the [[Affine Orbit Structure]]:

$$\text{dest}(n) = \frac{3^s}{P} \cdot n + C = 3^s \cdot P^m \cdot a + (\text{const})$$

For dest to lie in $\text{Dset}_k$ mod $P^{m+1}$ (not just mod $P^m$), we need:

$$3^s \cdot P^m \cdot a \equiv (\text{target}) \pmod{P^{m+1}} \implies 3^s \cdot a \equiv (\text{target}) \pmod{P}$$

Since $\gcd(3^s, P) = \gcd(3^s, 2^{k-s}) = 1$, this uniquely determines $a \bmod P$, giving $n \equiv r_{m+1} \pmod{P^{m+2}}$.

Since $n \geq P^{m+1}$ is required, the chain length $m \leq \log_P(n) - 1$. $\blacksquare$

## Verified Numerically

Set$_3$ ($P = 4$): self-chain length tracks $\log_4 n$ exactly.

| $m$ | Required modulus | Smallest $n$ | Chain |
|-----|-----------------|-------------|-------|
| 1 | $n \equiv 1 \pmod{16}$ | 17 | $17 \to 13$ |
| 2 | $n \equiv 1 \pmod{64}$ | 65 | $65 \to 49 \to 37$ |
| 3 | $n \equiv 1 \pmod{256}$ | 257 | $257 \to 193 \to 145 \to 109$ |
| 4 | $n \equiv 1 \pmod{1024}$ | 1025 | $1025 \to 769 \to 577 \to 433 \to 325$ |
| 7 | $n \equiv 1 \pmod{65536}$ | 65537 | 8-element chain |

## Significance

The contraction ratio alone allows arbitrarily long self-chains in principle (e.g., Set$_{13}$ with ratio 0.949 could theoretically self-loop $\sim 124$ times from $n \sim 10^5$). The modular tightening provides a **much stronger bound** that is independent of the contraction ratio — it depends only on the period $P$.

This means orbits are provably forced to **change neighborhoods** (switch dropping sets) frequently, preventing any strategy of "hiding" in a slow-contracting set.

## Related

- [[Affine Orbit Structure]] — the affine formula that makes modular tightening work
- [[Dropping Set]]
- [[Orbital Oddity Conjecture]]
