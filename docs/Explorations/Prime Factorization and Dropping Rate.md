# Prime Factorization and Dropping Rate

**Date:** 2026-09-10
**Script:** `scripts/prime_factorization_dropping.py` (≈7 s; writes `data/prime_factorization_dropping.csv`)
**Question:** How does a number's prime factorization affect its dropping behaviour — the first drop ([[Dropping Time]], [[Dropping Set]]) and the whole orbit (total stopping time, peak, number of drops)?

## Summary

1. **For the first drop, factorization acts only through the 2-adic unit group.** The dropping time of odd $n$ is a function of $n \bmod 2^k$, and residues multiply. Writing every odd residue as $n \equiv (-1)^{\varepsilon}\,5^{t} \pmod{2^K}$, the pair $(\varepsilon, t)$ is *additive* over multiplication: $\varepsilon(pq)=\varepsilon(p)+\varepsilon(q) \bmod 2$, $t(pq)=t(p)+t(q) \bmod 2^{K-2}$. So the dropping set of a product is a function of the **sum of the 2-adic discrete logarithms of its prime factors**, and of nothing else about them.
2. **The coarsest law is a Dirichlet character.** $n \in \text{Dset}_3 \iff \varepsilon(n)=0 \iff \chi_{-4}(n)=+1 \iff n$ has an even number of prime factors $\equiv 3 \pmod 4$ (with multiplicity). Exact.
3. **Nothing finer about the factors' dropping sets propagates.** Two factors from *any* higher sets ($k_1,k_2\ge 6$) multiply into $\text{Dset}_3$ with certainty; a $\text{Dset}_3$ factor times a higher-set factor lands in the generic $n\equiv 3 \pmod 4$ distribution, identical for every higher set (Table A3). The set label of a prime factor carries one bit and no more.
4. **Prime powers are 2-adically continuous in the exponent.** $\text{Dset}(p^b)=3$ for every even $b$ (odd squares are $\equiv 1 \pmod 8$), and for odd $b$ membership in $\text{Dset}_k$ depends only on $b \bmod 2^{k-2}$ (because $(\mathbb{Z}/2^k)^*$ has exponent $2^{k-2}$). Verified for $p=3,5,7,11$, $b\le 33$.
5. **Whole-orbit statistics carry no factorization signal beyond residues.** For odd $n<2^{20}$, fourteen factorization classes (prime, composite, $\omega$, $\Omega$, squarefree, square, $3\mid n$, $5\mid n$, $7\mid n$, smallest-prime-factor, all-factors-$\equiv1\bmod 4$) were compared against a residue-matched null (class residue histogram mod $2^{12}$ × per-residue conditional mean). All $|z|\le 1.1$ except perfect squares on drops-per-bit ($z=2.4$, 511 samples). Primes vs composites in each dyadic range: $|{\rm diff}/{\rm se}|\le 1.3$ in all ten ranges. Total stopping time of $p$ and of $p^2$ are uncorrelated ($r=0.07$; control $0.10$).

**Conclusion.** Multiplicative structure is destroyed by the map ($\gcd(n,3n+1)=1$, see [[Gear Spectrum and Wobble Channels]]); the only multiplicative structure Collatz sees is the group $(\mathbb{Z}/2^k)^* \cong \langle -1\rangle\times\langle 5\rangle$. "How factorization affects dropping" has an exact answer — the discrete-log addition law — and that answer says the prime factors' own Collatz behaviour is irrelevant beyond their mod-4 class. This closes the composite-vs-factor question posed in `CLAUDE.md` and `collatz/factorization.py`, and is consistent with the Dirichlet null in [[Prime Dropping Residues]].

## A. Exact residue algebra (mod $2^{16}$)

### A1. Dropping sets in discrete-log coordinates

| $k$ | residues mod $2^k$ | $\varepsilon$ | $t \bmod 2^{k-2}$ |
|---|---|---|---|
| 3 | 2 | 0 | all |
| 6 | 4 | 1 | $\{3,7,11,15\}$ = $t\equiv 3 \pmod 4$ |
| 8 | 16 | 1 | $t \equiv 5,6 \pmod 8$ |
| 11 | 48 | 1 | 48 values |
| 13 | 224 | 1 | 224 values |
| 16 | 768 | 1 | 768 values |

$\text{Dset}_6 = \{-5^t : t\equiv 3 \bmod 4\}$ and $\text{Dset}_8=\{-5^t : t \equiv 5,6 \bmod 8\}$ are arithmetic progressions in $t$; the higher sets are not (they are the images of ballot-admissible words, [[Nested Dropping Sets]]).

### A3. Dropping set of a product $pq$ given the sets of $p$ and $q$ (exact under the Dirichlet null)

| $\text{Dset}(p)\times\text{Dset}(q)$ | →3 | →6 | →8 | →11 | →13 | →16 | →>16 |
|---|---|---|---|---|---|---|---|
| 3 × 3 | 1.000 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 × $k$, any $k\ge 6$ | 0 | 0.250 | 0.250 | 0.094 | 0.109 | 0.047 | 0.250 |
| $k_1\times k_2$, both $\ge 6$ | 1.000 | 0 | 0 | 0 | 0 | 0 | 0 |

Marginal over odd $n$: 3: 0.500, 6: 0.125, 8: 0.125, 11: 0.047, 13: 0.055, 16: 0.023, >16: 0.125. The middle row is exactly the marginal conditioned on $n\equiv 3 \pmod 4$ — the higher-set label of the factor is forgotten.

## B. Whole-orbit statistics, residue-matched (odd $n<2^{20}$)

Excerpt (full table in the CSV). Overall mean of total steps$/\log_2 n$ is 7.442.

| class | count | total steps / $\log_2 n$ | residue-matched | $z$ | peak bits above $n$ | matched | $z$ |
|---|---:|---:|---:|---:|---:|---:|---:|
| prime | 82,024 | 7.432 | 7.441 | −0.9 | 2.760 | 2.761 | −0.2 |
| composite | 442,263 | 7.444 | 7.443 | +0.4 | 2.760 | 2.760 | +0.1 |
| $\omega\ge 3$ | 233,827 | 7.442 | 7.443 | −0.1 | 2.762 | 2.761 | +0.8 |
| not squarefree | 99,315 | 7.451 | 7.442 | +1.1 | 2.762 | 2.760 | +0.6 |
| perfect square | 511 | 7.537 | 7.445 | +0.7 | 2.490 | 2.478 | +0.3 |
| $3\mid n$ | 174,763 | 7.445 | 7.442 | +0.4 | 2.760 | 2.760 | −0.1 |
| all factors $\equiv 1 \bmod 4$ | 91,999 | 7.112 | 7.107 | +0.5 | 2.173 | 2.174 | −0.7 |

The last row is the only class with a visibly different mean, and the residue-matched null reproduces it exactly: such $n$ are $\equiv 1 \pmod 4$, hence in $\text{Dset}_3$, with the finer residue bias that the class inherits. No class shows anything the residues do not already predict.

## C. Special families

- **Odd squares** $m^2$: dropping time 3, always ($m^2 = 8\binom{t+1}{2}+1$). The *second* drop is again 3 iff $m\equiv \pm 1 \pmod 8$, otherwise it follows the generic $n\equiv 3\pmod 4$ distribution.
- **$2^a+1$, $(4^a-1)/3$**: always $\text{Dset}_3$ ($\equiv 1 \pmod 4$). **$2^a-1$**: the classical rising family, dropping times $6, 11, 11, 91, 88, 24, 21, 29, 29, 94, \dots$
- **$3^b$**: $6,3,96,3,6,3,8,3,6,3,19,3,\dots$ — $b$ even → 3; $b\equiv 1 \pmod 4$ → 6; $b\equiv 3\pmod 4$ → depends on $b \bmod 8, 16,\dots$ (2-adic continuity in $b$). Same shape for $7^b$ ($b\equiv 3 \bmod 4$ → 8) and $11^b$ ($b\equiv 3\bmod 4$ → 6, $b \equiv 1 \bmod 8$ → 8).

## Where a factorization signal could still hide

Only in quantities that are neither residue-determined nor averaged: e.g. the exact *value* of the peak for numbers of special multiplicative shape ($2^a\pm1$, $3^b\pm 2$, repunits), where the parity word is forced for the first $O(a)$ steps. That is 2-adic structure wearing multiplicative clothing, not a factorization effect.

## Related

[[Prime Dropping Residues]] · [[Multiplication Symmetry Theorem]] · [[Nested Dropping Sets]] · [[Gear Spectrum and Wobble Channels]] · [[Affine Orbit Structure]]

## Addendum (2026-09-10): the drop triangle in prime-exponent space

**Script:** `scripts/factorization_space.py` (odd $n \le 3\times10^5$). Represent $n$ by $v(n) = (v_p(n))_p$ and look at the "up" vector to $3n+1$ and the "down" vector to $\text{dest}(n)$.

Exact: $\langle v(n), v(3n+1)\rangle = 0$ (coprime); $\gcd(n,\text{dest}) \mid C_w$ where $C_w$ is the word constant, since $2^L\,\text{dest} = 3^s n + C_w$ (0 violations); $v_3(\text{dest}) = 0$ always.

| test | result |
|---|---|
| $P(\gcd(n,\text{dest})>1)$ per class vs $1-\prod_{p \mid C_w,\ p>2}(1-1/p)$ | agree to 3–4 decimals in every class with $\ge 1000$ members (e.g. $C_w=65$: 0.2619 vs 0.2615) |
| $\cos(v(n), v(\text{dest}))$ | mean 0.019 vs 0.073 for size-matched random integers: destinations are *more* orthogonal to $n$ than random, because overlap is confined to the primes of $C_w$ |
| $\omega(\text{dest})$ vs control matched on size ($\pm 5\%$), $\not\equiv 0 \bmod 3$, parity | 2.4503 vs 2.4477, diff/se $=+0.8$; distributions identical to 3 decimals |
| $\text{corr}(\omega(n), \omega(\text{dest}))$ | $-0.016$ (random pairs $+0.013$): no propagation of factorization richness across a drop |

**Conclusion.** In factorization space a Collatz drop is: an orthogonal up-step, a down-step whose overlap with $n$ is fixed by the word constant with exactly predicted frequencies, the hyperplane $v_3 = 0$, and otherwise Erdős–Kac noise. The dynamics live on the single coordinate $v_2$ together with archimedean size; the exponent-vector embedding treats those as two coordinates among infinitely many, which is why it sees nothing.
