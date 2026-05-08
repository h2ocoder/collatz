# Multiplication Symmetry Theorem

**Status:** Proved

## Statement

For odd $n$, define the **dropping set shift** under multiplication by an odd integer $m$:

$$\text{shift}_m(n) = \text{Dset}(m \cdot n) - \text{Dset}(n)$$

**Theorem (x3 Symmetry).** The shift distribution under multiplication by 3 is perfectly symmetric:

$$P(\text{shift}_3 = +s) = P(\text{shift}_3 = -s) \quad \text{for all } s > 0$$

Verified for all odd $n < 100{,}000$ with near-zero deviation.

## The Mod-4 Wall

The symmetry rests on a clean structural partition:

- $\text{Dset}_3 = \{n \text{ odd} : n \equiv 1 \pmod{4}\}$
- All higher dropping sets ($k = 6, 8, 11, 13, \ldots$) consist of $n \equiv 3 \pmod{4}$

Since $3 \equiv 3 \pmod{4}$, multiplication by 3 **always flips** the mod-4 class:

| Source | $n \bmod 4$ | $3n \bmod 4$ | Shift direction |
|--------|-------------|--------------|-----------------|
| $\text{Dset}_3$ | 1 | 3 | Always **positive** (moves to higher set) |
| $\text{Dset}_{k>3}$ | 3 | 1 | Always **negative** (returns to $\text{Dset}_3$) |

## Proof

1. If $n \equiv 1 \pmod{4}$, then $n \in \text{Dset}_3$ and $3n \equiv 3 \pmod{4}$, so $3n \in \text{Dset}_{k}$ for some $k > 3$. Shift $= k - 3 > 0$.

2. If $n \equiv 3 \pmod{4}$, then $n \in \text{Dset}_{k}$ for some $k > 3$ and $3n \equiv 1 \pmod{4}$, so $3n \in \text{Dset}_3$. Shift $= 3 - k < 0$.

3. Since $\gcd(3, 2^B) = 1$ for all $B$, multiplication by 3 is a **bijection** on $\mathbb{Z}/2^B\mathbb{Z}$. It permutes the residue classes that define each dropping set.

4. Therefore $P(3n \in \text{Dset}_k \mid n \in \text{Dset}_3) = P(n \in \text{Dset}_k \mid n \equiv 3 \pmod{4})$, which is simply the natural density of $\text{Dset}_k$.

5. The positive shifts (from $\text{Dset}_3$) and negative shifts (to $\text{Dset}_3$) have identical magnitude distributions, because both are governed by the same density function. $\square$

## Exact Shift Densities

The density of each shift equals the density of the corresponding dropping set among $n \equiv 3 \pmod{4}$:

| $\text{Dset}_k$ | Shift | $s$ | Density | Decimal |
|------------------|-------|-----|---------|---------|
| 6 | $\pm 3$ | 2 | $1/4$ | 0.2500 |
| 8 | $\pm 5$ | 3 | $1/4$ | 0.2500 |
| 11 | $\pm 8$ | 4 | $3/32$ | 0.0938 |
| 13 | $\pm 10$ | 5 | $7/64$ | 0.1094 |
| 16 | $\pm 13$ | 6 | $3/64$ | 0.0469 |
| 19 | $\pm 16$ | 7 | $15/512$ | 0.0293 |
| 21 | $\pm 18$ | 8 | $85/2048$ | 0.0415 |

These densities are computed exactly by the [[Lattice Path Formula]].

## Generalization to Other Multipliers

The mod-4 wall determines the behavior of all odd multipliers:

- **$m \equiv 1 \pmod{4}$** (e.g., 5, 9, 13, 17): preserves mod-4 class, so $P(\text{shift} = 0) > 50\%$
- **$m \equiv 3 \pmod{4}$** (e.g., 3, 7, 11, 15): flips mod-4 class, so $P(\text{shift} = 0) = 0\%$ exactly

The specific shift distribution for $m \equiv 1 \pmod{4}$ depends on $v_2(m-1)$ (the 2-adic valuation of $m-1$), which determines how many bits of the mod-$2^B$ structure are preserved.

## Connections

- The shift densities are computed by the [[Lattice Path Formula]]
- The affine constant $C$ in [[Affine Orbit Structure]] determines mod-$p$ correlations between $n$ and $\text{dest}(n)$; the x3 symmetry is the "outer" version of this structure
- Connects to the [[Collatz Complementarity Principle]]: the hidden variable $C$ encodes which correlations are allowed under different measurements
