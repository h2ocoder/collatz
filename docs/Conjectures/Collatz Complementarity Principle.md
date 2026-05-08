# Collatz Complementarity Principle

**Status:** Proved (structural result)

## Statement

For a dropping set $\text{Dset}_k$ with $s$ Syracuse steps, the affine constant $C$ in $\text{dest}(n) = (3^s / 2^{k-s}) \cdot n + C$ acts as a **hidden variable** that simultaneously encodes the mod-$p$ correlations between $n$ and $\text{dest}(n)$ for all primes $p$.

These correlations are subject to an **uncertainty relation**: when the lattice path bandwidth $B(s) < p \cdot q$, the mod-$p$ and mod-$q$ observations of $C$ cannot be independently specified.

## The Hidden Variable $C$

Within each subgroup of $\text{Dset}_k$, the affine relation $\text{dest}(n) = \frac{3^s}{2^{k-s}} n + C$ holds exactly. The constant $C$ is determined by the **alpha prefix** $(a_1, \ldots, a_{s-1})$ — the sequence of halvings at each Syracuse step before the orbit drops.

### Progressive Determination

$C$ is revealed by sequentially reading binary digits of $n$:

1. Read bit 1 (LSB): determines $\alpha_1$ (always 1 for $n \equiv 3 \pmod 4$)
2. Read bits 2-3: determines $\alpha_2$, constraining which subgroup
3. Continue: each bit narrows the subgroup, progressively determining $C$
4. After $s-1$ alpha values: $C$ is fully determined

Before all bits are read, the pair $(n, \text{dest}(n))$ is in a definite **relationship** (determined by $C$) but neither value is individually determined. Measuring either one instantly determines the other.

## Set-Dependent Correlations

The correlation between $n \bmod p$ and $\text{dest}(n) \bmod p$ depends on the **slope** $3^s / 2^{k-s}$:

$$\text{dest} \bmod p = \left(\frac{3^s}{2^{k-s}} \bmod p\right) \cdot n + (C \bmod p) \pmod{p}$$

| Slope $\bmod\, p$ | Correlation type |
|---|---|
| $\equiv 1$ | **Preserved**: $\text{dest} \equiv n + C \pmod p$ |
| $\equiv 0$ | **Locked**: $\text{dest} \equiv C \pmod p$ (independent of $n$) |
| other | **Scrambled**: $\text{dest}$ depends on both $n$ and $C$ |

### Verified Examples

| $\text{Dset}_k$ | $s$ | Slope mod 5 | Slope mod 7 |
|---|---|---|---|
| 6 | 2 | 4 (scrambled) | **1 (preserved)** |
| 8 | 3 | **1 (preserved)** | 5 (scrambled) |
| 11 | 4 | 2 (scrambled) | 2 (scrambled) |
| 13 | 5 | 3 (scrambled) | 3 (scrambled) |

The slope mod $p$ cycles with period $\text{ord}_p(3)$: period 4 for $p = 5$, period 6 for $p = 7$.

### Forbidden Correlations

In $\text{Dset}_6$: $\text{dest} \equiv n - 1 \pmod 7$, so $n \bmod 7 = \text{dest} \bmod 7$ is **impossible**. Verified: zero matches in 3,125 pairs.

In $\text{Dset}_8$: $\text{dest} \equiv n - 1 \pmod 5$, so $n \bmod 5 = \text{dest} \bmod 5$ is **impossible**. Verified: zero matches in 3,125 pairs.

### The 3-Adic Lock

For all sets: slope $\equiv 0 \pmod 3$ (since $3^s \equiv 0 \pmod 3$). This means $\text{dest} \bmod 3$ is always **locked** to a constant $C \bmod 3$, independent of $n$. This is the [[Affine Orbit Structure|3-adic lock]] proved earlier.

## The Uncertainty Relation

The valid alpha-prefix sums occupy a narrow band:

$$B(s) = \lfloor s \cdot (\log_2 3 - 1) \rfloor + 1 \approx 0.585 \cdot s$$

This bandwidth constrains which mod-$p$ residues of $C$ are achievable:

- If $B(s) < p$: some mod-$p$ residues of $C$ are **forbidden**
- If $B(s) < p \cdot q$: mod-$p$ and mod-$q$ observations are **complementary** (knowing one constrains the other)

| Constraint | Independent when $s \geq$ |
|---|---|
| mod 3 $\times$ mod 5 | $\sim 26$ |
| mod 3 $\times$ mod 7 | $\sim 36$ |
| mod 5 $\times$ mod 7 | $\sim 60$ |
| mod 5 $\times$ mod 11 | $\sim 94$ |

### The Information Gap

The number of valid prefixes $N(s)$ grows exponentially ($\sim 2.7^s$), but the bandwidth grows linearly ($\sim 0.585s$). By $s = 16$: 312,455 prefixes but only 10 possible sum values — a **15-bit information gap**.

The excess information lives in the **internal structure** of the prefix: how halvings are distributed among steps. No single modular measurement can capture this — multiple complementary measurements are needed.

## Analogy to Quantum Entanglement

The structure parallels entangled quantum systems:

| Quantum mechanics | Collatz |
|---|---|
| Entangled pair $\|\psi\rangle$ | The pair $(n, \text{dest}(n))$ |
| Hidden variable | The affine constant $C$ |
| Measurement basis | Choice of modulus $p$ |
| Outcome | Residue class mod $p$ |
| Measurement-dependent correlation | Slope mod $p$ varies by dropping set |
| Conservation law | 3-adic lock (slope $\equiv 0 \pmod 3$) |
| Complementarity | Narrow bandwidth forces mod-$p$, mod-$q$ dependence |

**Key difference:** The CHSH inequality is **not** violated ($S \approx 0.08$, well within the classical bound of 2). The system is deterministic; $C$ is a valid local hidden variable. The complementarity is a **resource constraint** (narrow band), not true quantum non-locality.

## Connections

- The hidden variable $C$ is the intercept from [[Affine Orbit Structure]]
- The bandwidth comes from the [[Lattice Path Formula]]
- The mod-$p$ cycling connects to the slope structure in [[Multiplication Symmetry Theorem]]
- The 3-adic lock is proved in [[Affine Orbit Structure]]
- The sequential bit-reading protocol connects to the 2-adic determinism in [[Odd Stopping Time Spectrum]]
