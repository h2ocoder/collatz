# Logarithmic Escape Theorem

## Statement

<div class="theorem">

**Theorem (Logarithmic Escape).** For any Dropping Set $\text{Dset}_k$ with period $P = 2^{k-s}$, the maximum number of consecutive self-transitions (drops where both $n$ and $\text{dest}(n)$ belong to $\text{Dset}_k$) starting from $n$ is at most:

$$m \leq \log_P(n) - 1$$

Equivalently: no orbit can remain in the same dropping set for more than $O(\log n)$ consecutive drops.

</div>

## Significance

The contraction ratio alone would allow long self-chains (e.g., Set$_{13}$ with ratio 0.949 could theoretically self-loop ~124 times from $n \sim 10^5$). The modular tightening bound is **much stronger** and independent of the contraction ratio — it depends only on the period $P$. This forces orbits to change dropping sets frequently.

## Examples

Bounds by set:

| $k$ | $P$ | Bound | $n = 10^6$ gives $m \leq$ |
|-----|-----|-------|---------------------------|
| 3 | 4 | $\log_4 n$ | 9 |
| 6 | 16 | $\log_{16} n$ | 4 |
| 8 | 32 | $\log_{32} n$ | 3 |
| 13 | 256 | $\log_{256} n$ | 2 |

Verified chains for $\text{Dset}_3$ ($P = 4$):

| $m$ | Required modulus | Smallest $n$ | Chain |
|-----|-----------------|-------------|-------|
| 1 | $n \equiv 1 \pmod{16}$ | 17 | $17 \to 13$ |
| 2 | $n \equiv 1 \pmod{64}$ | 65 | $65 \to 49 \to 37$ |
| 3 | $n \equiv 1 \pmod{256}$ | 257 | $257 \to 193 \to 145 \to 109$ |
| 4 | $n \equiv 1 \pmod{1024}$ | 1025 | $1025 \to 769 \to 577 \to 433 \to 325$ |
| 7 | $n \equiv 1 \pmod{65536}$ | 65537 | 8-element chain |

## Proof

<div class="proof">

**By induction on chain length $m$ (modular tightening).**

Each self-transition multiplies the required modular constraint by $P$.

**Claim:** $m$ consecutive self-transitions require $n$ to satisfy a specific residue class mod $P^{m+1}$.

**Base** ($m = 0$): Membership in $\text{Dset}_k$ requires $n \equiv r \pmod{P}$.

**Inductive step:** Suppose $m$ self-transitions require $n \equiv r_m \pmod{P^{m+1}}$.

Write $n = P^{m+1} \cdot a + r_m$. By the [Affine Orbit Structure](/proofs/affine-orbit):

$$\text{dest}(n) = \frac{3^s}{P} \cdot n + C = 3^s \cdot P^m \cdot a + (\text{const})$$

For dest to lie in $\text{Dset}_k$ mod $P^{m+1}$ (not just mod $P^m$), we need:

$$3^s \cdot P^m \cdot a \equiv (\text{target}) \pmod{P^{m+1}} \implies 3^s \cdot a \equiv (\text{target}) \pmod{P}$$

Since $\gcd(3^s, P) = \gcd(3^s, 2^{k-s}) = 1$, this uniquely determines $a \bmod P$, giving:

$$n \equiv r_{m+1} \pmod{P^{m+2}}$$

Since $n \geq P^{m+1}$ is required, the chain length satisfies $m \leq \log_P(n) - 1$.

</div>

## Corollaries

<div class="corollary">

**Corollary 1.** No orbit can "camp" in a slow-contracting set. Even Set$_{13}$ ($P = 256$, ratio 0.949) forces escape after ~2 steps for $n < 10^6$.

</div>

<div class="corollary">

**Corollary 2.** Combined with the [Bit Destruction Bound](/proofs/bit-destruction), this gives progress guarantees: orbits cannot accumulate many low-destruction drops from any single set.

</div>

## Related Results

- [Affine Orbit Structure](/proofs/affine-orbit) — prerequisite: the affine formula that makes modular tightening work
- [Bit Destruction Bound](/proofs/bit-destruction) — uses this result to bound slow-drop windows
- [3-Adic Mixing](/proofs/mixing) — complements this: Log Escape bounds same-set chains, mixing bounds cross-set slow chains
