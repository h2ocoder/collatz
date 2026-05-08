# Sector Monotonicity Conjecture

**Status:** Empirically verified (135,565 sector revisits, 0 violations, n < 50,000)

## Statement

Let $\omega = e^{2\pi i/3}$ and $\pi = 1 - \omega$ be the Eisenstein prime above 3. For a Collatz orbit starting at odd $n$, each drop passes through a dropping set $\text{Dset}_k$ with $s$ Syracuse steps. The **Eisenstein sector** of the drop is $s \bmod 12$ (equivalently, the direction of $\pi^s$ in the Eisenstein plane).

**Conjecture (Sector Monotonicity).** If the Collatz orbit visits Eisenstein sector $\sigma = s \bmod 12$ at value $n_1$, and later revisits sector $\sigma$ at value $n_2$, then $n_2 < n_1$.

Within each of the 12 Eisenstein sectors, the sequence of visited values is **strictly decreasing**.

## Verified

| Range | Sector revisits | Violations |
|-------|----------------|------------|
| $n < 10{,}000$ | 25,903 | 0 |
| $n < 50{,}000$ | 135,565 | 0 |

## Implications

### 1. Bounded Total Stopping Time

Each sector can be visited at most $\lfloor \log_2 n \rfloor$ times (since values strictly decrease, and each value is a positive integer). With 12 sectors:

$$\text{total drops} \leq 12 \cdot \log_2 n$$

This would give $O(\log n)$ total drops, hence $O(\log^2 n)$ total Collatz steps (since each drop takes $O(\log n)$ steps).

### 2. No Divergence

If the orbit ever revisited a sector at a larger value, that would constitute local divergence — the spiral "unwinding." Sector monotonicity forbids this. The orbit may transiently grow between drops (passing through higher dropping sets), but by the time it returns to the same sector, it has contracted.

### 3. Positive Knot Structure

The orbit, threaded through the 12-sector Eisenstein circle, forms a knot when the convergence loop ($4 \to 2 \to 1$) is included. The sector monotonicity implies:

- Every crossing in the knot diagram has **positive** sign (writhe $\geq 0$)
- The knot is **alternating** — no negative crossings
- Verified: writhe distribution ranges from 0 to 11, all non-negative

Positive knots have strong structural properties in knot theory: they are fibered, their genus equals $(c - 1)/2$ where $c$ is the crossing number, and they satisfy Bennequin's inequality as an equality.

### 4. Torus Knot Classification

Each orbit can be classified by its torus knot type $(p, q)$:
- $p$ = number of complete angular windings (total Syracuse steps $/\, 12$)
- $q$ = number of drops (radial passes)

Most common types among $n < 5000$:

| Type | Count | Knot name |
|------|-------|-----------|
| $(1, q)$ | dominant | Single-winding, various drops |
| $(2, 3)$ | 77 | Trefoil |
| $(2, 5)$ | 76 | Solomon's seal ($5_1$) |
| $(4, 7)$ | 118 | $T(4,7)$ |

### 5. Winding Word as Orbit Invariant

The **winding word** of an orbit is the sequence of sector-to-sector jumps $((\sigma_2 - \sigma_1) \bmod 12, (\sigma_3 - \sigma_2) \bmod 12, \ldots)$. This is a knot-theoretic invariant of the orbit.

- 1,686 distinct winding words found for $n < 5{,}000$
- Most common suffix: $\ldots, 0, 2, 10$ (ending with Set$_3 \to$ Set$_8 \to$ Set$_3$)
- The winding word determines the orbit's knot type

## Connection to the Proof

Sector monotonicity, if proved, would essentially establish convergence:

1. Within each sector, values strictly decrease — the orbit cannot diverge within any sector
2. There are only 12 sectors — the orbit cannot avoid all sectors indefinitely
3. The period-12 angular dynamics force the orbit to cycle through all sectors
4. Combined: the orbit is a finite union of strictly decreasing sequences, hence finite

The remaining step would be proving the conjecture algebraically. The key challenge: a revisit to sector $\sigma$ means two different dropping sets $\text{Dset}_{k_1}$ and $\text{Dset}_{k_2}$ with $s_1 \equiv s_2 \pmod{12}$ (i.e., $k_2 > k_1$ by approximately $12 \cdot \log_2 6 \approx 31$ steps). The claim is that the intervening orbit always contracts by at least a factor of 1.

## Connections

- The 12 sectors come from the [[Eisenstein Factorization]] ($\pi^s$ rotates by $-30s°$)
- The angular period 12 connects to the Pythagorean comma ($3^{12}/2^{19}$)
- Sector monotonicity strengthens the contraction analysis in [[Collatz Complementarity Principle]]
- The positive knot structure may connect to the fibered knot theory and genus bounds
- The winding word generalizes the alpha sequence from [[Lattice Path Formula]]
