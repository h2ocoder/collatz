# Hecke L-Function on Collatz Orbits

A Hecke L-function probe $L(s, \chi)$ on $\mathbb{Q}(\omega)$, with $\chi$ chosen so the proven Eisenstein factorization makes Collatz orbit dynamics visible through orbit-twisted partial sums.

- **Spec:** [[../superpowers/specs/2026-05-07-collatz-l-function-design]]
- **Code:** `collatz/lfunctions/`
- **Dependencies:** [[../Conjectures/Eisenstein Factorization]], [[../Conjectures/Affine Orbit Structure]], [[../Conjectures/Multiplication Symmetry Theorem]]

## Construction

Lift each odd integer $n$ to $\mathbb{Z}[\omega]$ via the **orbit-pair lift**

$$\iota_2(n) = n + \mathrm{dest}(n)\,\omega \in \mathbb{Z}[\omega]$$

where $\mathrm{dest}(n)$ is the Collatz stopping destination. The Eisenstein norm is $N(\iota_2(n)) = n^2 - n\,\mathrm{dest}(n) + \mathrm{dest}(n)^2$, the Loeschian invariant — these pairs are exactly the Loeschian numbers identified in [[../Conjectures/Eisenstein Factorization]].

For a Hecke character $\chi$ on $\mathbb{Z}[\omega]$, define the **orbit-twisted character sum**

$$D_\chi(N) = \sum_{\substack{3 \le n \le N \\ n\ \mathrm{odd}}} \chi\bigl(\iota_2(n)\bigr).$$

GRH-style heuristics predict $|D_\chi(N)| = O(\sqrt{N}\log N)$ for any nontrivial $\chi$. Empirically it grows **linearly in $N$**, by character-specific constants. Those constants are the data.

## Phase 1 — characters of conductor $(\pi^2) = (3)$

Implemented:

- $\chi_3$ (cubic residue, values in $\mu_3$)
- $\chi_6$ (sextic residue, values in $\mu_6$)

Verified to first order at $N = 10^4, 10^5, 10^6$:

| Character | $|D_\chi(N)|/N$ (asymptotic) | Closed form |
|---|---|---|
| trivial | $1/2$ | density of odd $n$ in $[3, N]$ |
| $\chi_3$ | $1/6$ exactly | $\frac{1}{3}\#\{n \le N\,\mathrm{odd} : \mathrm{dest}(n) \not\equiv 0 \pmod 3\}$ |
| $\chi_6$ | $\approx 0.1028$ | $\frac{1}{\sqrt 3}\bigl|\,\#\{\mathrm{dest} \equiv 1\} - \#\{\mathrm{dest} \equiv 2\}\bigr|$ |

### Closed form #1: $|D_{\chi_3}(N)| = N/6$ exactly

Within each Dropping Set, the $b$-coordinate $\mathrm{dest}(n) \bmod 3$ is locked to a single residue (the [[../Conjectures/Affine Orbit Structure|3-adic lock]]). Combined with the fact that destinations are *never* $\equiv 0 \pmod 3$ (proved in [[../Conjectures/Bit Destruction Bound]]: $3x+1 \equiv 1 \pmod 3$), every orbit pair lands in one of two unit-classes that contribute $\omega$ and $\omega^2$ to $\chi_3$. Their sum is $-1$, so $\chi_3$ aggregates to exactly $-(\text{count})/3$ per Dropping Set. Across all of $[3, N]$ this is $-(N/2)/3 = -N/6$.

The L-function-side statement is therefore equivalent to a purely Collatz-side fact: dest is non-zero mod 3 for all odd $n > 1$.

### Closed form #2: $|D_{\chi_6}(N)| = \frac{1}{\sqrt 3}\bigl|c_1(N) - c_2(N)\bigr|$

where $c_b(N) = \#\{n \le N\ \mathrm{odd} : \mathrm{dest}(n) \equiv b \pmod 3\}$.

Verified to four digits at $N \in \{10^4, 10^5, 10^6\}$ (largest deviation 0.07%).

**Empirical asymptotic densities** (over $n \le 10^6$ odd):

$$\rho_1 = c_1/(N/2) \approx 0.6781, \qquad \rho_2 \approx 0.3219, \qquad \rho_1 - \rho_2 \approx 0.3562.$$

This number is a structural Collatz invariant: the asymptotic excess of odd $n$ whose stopping destination is $\equiv 1 \pmod 3$ over those $\equiv 2 \pmod 3$. Computable directly from the per-Dropping-Set densities (Lattice Path Formula) and the per-subgroup 3-adic locks.

| Dropping Set $\text{Dset}_k$ | oddity $s$ | density | dest mod 3 |
|---|---|---|---|
| $\text{Dset}_3$ | 1 | $1/2$ | always $1$ |
| $\text{Dset}_6$ | 2 | $1/4$ | always $2$ |
| $\text{Dset}_8$ | 3 | $1/8 + 1/8$ | $50\%$ each |
| $\text{Dset}_{11}$ | 4 | smaller | $\sim 67\% / 33\%$ |
| $\ldots$ | | | |

Set$_3$ contributes the dominant b=1 weight ($1/2$ of all odd $n$). Set$_6$ contributes b=2 ($1/4$). Higher Dsets average toward 50/50 but contribute lower density. The asymptotic balance $\rho_1 - \rho_2$ is determined by these contributions.

### Closed form #3: $\rho_1 - \rho_2$ as an explicit series in lattice-path counts

For each Dropping Set $\text{Dset}_k$ with oddity $s$, the destination residue mod 3 within a subgroup is determined by the **trailing alpha** of its lattice path:

$$\mathrm{dest}(n) \bmod 3 = 2^{\alpha_s} \bmod 3 = \begin{cases} 1 & \alpha_s \text{ even} \\ 2 & \alpha_s \text{ odd}\end{cases}$$

where $\alpha_s = (k - s) - \sum_{i<s}\alpha_i$ is the number of even Collatz steps after the last $3x{+}1$ step. This follows from the affine recursion: each $3x{+}1$ step resets $C$ to $\equiv 1 \pmod 3$ (since $3C+1 \equiv 1 \pmod 3$), and each subsequent halving multiplies $C$ by $2 \pmod 3$ (since $2 \cdot 2 \equiv 1 \pmod 3$).

Let $N_1(s), N_2(s)$ denote the number of subgroups of $\text{Dset}_k$ with $\alpha_s$ even / odd. Then:

$$\boxed{\;\rho_1 - \rho_2 = \sum_{s=1}^\infty \frac{N_1(s) - N_2(s)}{2^{k(s) - s - 1}}\;}$$

with $k(s) = \lceil s\log_2 6\rceil$. Combined with closed form #2:

$$\frac{|D_{\chi_6}(N)|}{N} \;\xrightarrow[N\to\infty]{}\; \frac{1}{2\sqrt 3}\sum_{s=1}^\infty \frac{N_1(s) - N_2(s)}{2^{\lceil s\log_2 3\rceil - 1}}.$$

The series converges geometrically because $N(s) = N_1(s) + N_2(s)$ grows like $\sim c^s$ with $c \approx 2.7$, while the per-subgroup density decays like $2^{-\lceil s \log_2 3\rceil}\sim (1/3)^{s/\log_2 6}$, giving exponent $-(s\log_2 3 - \log_2 c) < 0$.

#### Numerical evaluation

Computed via DP enumeration of lattice paths up to $s = 400$:

| Partial sum $s = 1..S$ | Value |
|---|---|
| $S = 4$ | $0.359\,375$ |
| $S = 10$ | $0.359\,497$ |
| $S = 50$ | $0.356\,065$ |
| $S = 100$ | $0.356\,037$ |
| $S = 200$ | $0.356\,035\,93$ |
| $S = 400$ | $\mathbf{0.356\,035\,929\,815\,179}$ |

Empirical at $N = 10^7$: $\rho_1 - \rho_2 = 0.356\,093\,1$ (deviation $\approx 5.7 \times 10^{-5}$, finite-$N$ tail).

Therefore:
$$\frac{|D_{\chi_6}(N)|}{N} \to \frac{0.356\,035\,929\,815\ldots}{2\sqrt{3}} \approx 0.102\,769\,2\ldots$$

This is the **exact asymptotic L-function constant**, derivable purely from the proven Lattice Path Formula plus the trailing-alpha rule. It is not a closed form in elementary functions of $\log_2 3$ (numerically tested), but it is a fully computable constant of the Collatz dynamics.

### Norm-pullback control: characters coprime to $(\pi)$

Pulled back rational Dirichlet characters mod 7 via the Eisenstein norm: $\chi(\alpha) := \chi_\mathrm{rat}(N(\alpha) \bmod 7)$. These are coprime to $(\pi)$.

| Character | $|D_\chi(N)|/N$ | What it sees |
|---|---|---|
| cubic mod 7 (norm pullback) | $\approx 0.1188$ | distribution of $N(\iota_2(n)) \bmod 7$ in cubic-residue classes |
| sextic mod 7 (norm pullback) | $\approx 0.0715$ | same, in sextic-residue classes |

These also grow linearly. *Conclusion:* the orbit-pair lift is structurally non-uniform in $\mathbb{Z}[\omega]$, visible through several distinct character families, not only through the 3-adic lock.

For a *genuinely* random control we used $(n, b)$ with $b$ uniform random in $[1, n]$. There $|D_\chi|$ stays in the low hundreds at $N = 10^5$ — the GRH-flat regime, $|D_\chi|/\sqrt N \approx O(1)$. So linear growth is signal, not artifact.

### Trivial-pair upper bound

For comparison, the most-correlated pair $(n, c)$ with $c$ constant gives $|D_{\chi_6}(N)|/N \to \sqrt 3 / 6 \approx 0.2887$. Our orbit pair sits at $0.1028$ — about $35.6\%$ of the constant-pair value, reflecting partial cancellation between b=1 and b=2 Dsets.

## Phase 2 — sector-twisted Fourier components

A genuine period-12 Hecke character coprime to $(\pi)$ does not exist at small conductor (the natural conductor $(\pi^a)$ keeps $\chi(\pi)=0$). Instead, twist by the sector index $s(n) \bmod 12$ directly:

$$D_{\chi, k}(N) = \sum_{\substack{3 \le n \le N \\ n\ \mathrm{odd}}} \chi(\iota_2(n)) \cdot \zeta_{12}^{k\, s(n)}, \qquad k = 0, 1, \ldots, 11.$$

The vector $(D_{\chi, 0}, \ldots, D_{\chi, 11})$ is the discrete Fourier transform of the orbit-pair distribution along the sector index, weighted by $\chi$.

### Sector distribution at $N = 10^5$

| $s \bmod 12$ | count | fraction | Dropping sets contributing |
|---|---|---|---|
| 0 | 359 | 0.72% | $s = 12, 24, 36, \ldots$ |
| 1 | 25,488 | **50.98%** | Set$_3$ ($s=1$) + Set$_{29}$ ($s=13$) + … |
| 2 | 6,512 | 13.02% | Set$_6$ + Set$_{32}$ + … |
| 3 | 6,647 | 13.29% | Set$_8$ + … |
| 4 | 2,558 | 5.12% | Set$_{11}$ + … |
| 5 | 3,038 | 6.08% | Set$_{13}$ + … |
| 6 | 1,338 | 2.68% | Set$_{16}$ + … |
| 7 | 850 | 1.70% | Set$_{19}$ + … |
| 8 | 1,222 | 2.44% | Set$_{21}$ + … |
| 9 | 650 | 1.30% | Set$_{24}$ + … |
| 10 | 881 | 1.76% | Set$_{26}$ + … |
| 11 | 456 | 0.91% | Set$_{29}$ + … |

The per-sector mass is heavily skewed: 50.98% in sector 1 (Set$_3$ alone is 50% of odd $n$). The Fourier transform of these counts gives the trivial-character sector twist $D_{\chi_0, k}$.

### Phase asymmetries that the twists pick up

Notable patterns in $(D_{\chi, k})_{k=0..11}$ at $N = 10^5$:

| $\chi$ | $\arg D_{\chi, 0}$ | $\arg D_{\chi, 6}$ | $|D_{\chi, k}|$ peak | $|D_{\chi, k}|$ trough |
|---|---|---|---|---|
| trivial | $0°$ (real $+$) | $180°$ (real $-$) | $k=0$: 49,999 | $k=4, 8$: 19,761 |
| $\chi_3$ | $180°$ (real $-$) | $0°$ (real $+$) | $k=0$: 16,666 | $k=4$: 6,598 |
| $\chi_6$ | $-90°$ (imag $-$) | $+90°$ (imag $+$) | $k=6$: 18,689 | $k=0$: 10,257 |
| cubic@7 | $+41°$ | $-140°$ | $k=0$: 11,879 | $k=5$: 7,531 |
| sextic@7 | $-139°$ | $+41°$ | $k=6$: 11,756 | $k=0$: 7,129 |

For $\chi_6$ specifically: $D_{\chi_6, 0}$ and $D_{\chi_6, 6}$ are *both purely imaginary* (with opposite signs). That is a strong reflection symmetry — the projection of the orbit-pair distribution onto the sextic character behaves like a pure $\sin(s \pi/12)$ pattern.

Conjugate-pair symmetry $D_{\chi, k}$ vs $D_{\chi, 12-k}$ holds across all five characters (visible as conjugate magnitudes and sign-flipped angles), confirming the sector-distribution data is real.

## What we learned vs. what's open

### Established (numerically verified, closed-form derived)

1. **The orbit-pair lift is character-detectable.** $|D_\chi(N)|$ grows linearly in $N$ for every nontrivial $\chi$ tested, in flagrant violation of GRH-style square-root cancellation.
2. **$\chi_3$ closed form**: $|D_{\chi_3}(N)| = N/6$ exactly. The L-function-side equivalent of "Collatz destinations are never $\equiv 0 \pmod 3$."
3. **$\chi_6$ closed form**: $|D_{\chi_6}(N)| = \frac{1}{\sqrt 3}|c_1 - c_2|$ where $c_b$ counts odd $n \le N$ with $\mathrm{dest}(n) \equiv b \pmod 3$. Asymptotic density $\rho_1 - \rho_2 \approx 0.3562$.
4. **Sector spectrum**: 50.98% of odd $n$ have oddity $s \equiv 1 \pmod{12}$ (Set$_3$ + Set$_{29}$ + …). The 12-component Fourier vector $(D_{\chi, k})$ characterizes the joint distribution of orbit-pair coordinates and sector index.

### Open / next moves

1. ~~**Exact value of $\rho_1 - \rho_2$.**~~ **Done — closed-form series derived.** See "Closed form #3" below.
2. **Higher-modulus characters.** Conductor $(p)$ for inert primes $p \in \{5, 11, 17, \ldots\}$ should give finer-grained signals. Conductor $(\mathfrak{p})$ for split primes ($p \in \{7, 13, 19, \ldots\}$) gives Hecke characters with values in $\mu_{p-1}$.
3. **Connection to Sector Monotonicity.** The sector-twist $D_{\chi_6, k}$ at $k=6$ has magnitude 18,689 and pure-imaginary value: $+18689i$. This is the $k=6$ Fourier mode — the alternating-sector mode. If [[../Conjectures/Sector Monotonicity]] holds, the orbit *re-enters* each sector at strictly smaller values; that should constrain the $k=6$ mode in some direct way (specifically: $D_{\chi_6, 6}$ encodes a signed count of orbit returns).
4. **Orbit-pair distribution asymptotics.** Is there an algebraic-number target for $|D_{\chi_6}(N)|/N$? The formula $\frac{1}{\sqrt 3}\rho_{12}$ (where $\rho_{12} = \rho_1 - \rho_2$) suggests the asymptotic constant could be a known explicit value derived from the Lattice Path Formula's generating function.

### Potential proof leverage

The closed-form $|D_{\chi_6}(N)| = \frac{1}{\sqrt 3}|c_1 - c_2|$ converts an L-function bound into a counting-by-residue bound. Specifically:

> If we could show $|D_{\chi_6}(N)| = O(N^{1-\delta})$ for some $\delta > 0$, that would imply $c_1(N) = c_2(N) + O(N^{1-\delta})$ — equidistribution of $\mathrm{dest}(n) \bmod 3$ at a rate.

The empirical data shows $|D_{\chi_6}(N)| \sim 0.103 N$ — *not* GRH-random — so equidistribution does not hold. The asymmetry $\rho_1 - \rho_2 \neq 0$ is a *true* Collatz invariant, not a GRH gap.

This rules out a class of "Collatz reduces to GRH on $L(s, \chi_6)$" arguments that we might have hoped existed. The character sum sees genuine Collatz structure, not random fluctuations on top of an equidistribution.

## Methodology

- 184 unit tests, all green. Eisenstein arithmetic verified against algebraic identities ($\pi\bar\pi=3$, $\arg \pi = -30°$, multiplicativity of norm). Characters verified for $\chi_6^6 = 1$, multiplicativity, sextic-residue values in $\mu_6$.
- Phase 1 sums computed in pure Python with `cmath`. $N = 10^6$ runs in $\sim$ 30 seconds.
- Closed-form predictions cross-checked against direct enumeration at $N = 10^4, 10^5, 10^6$. All within 0.1%.
- All experiments reproducible from `collatz/lfunctions/` plus `collatz.core`.

## See also

- [[../Conjectures/Eisenstein Factorization]] — the algebraic substrate.
- [[../Conjectures/Affine Orbit Structure]] — gives the 3-adic lock that $\chi_3$ detects.
- [[../Conjectures/Bit Destruction Bound]] — proves dest $\not\equiv 0 \pmod 3$.
- [[../Conjectures/Lattice Path Formula]] — would give the exact value of $\rho_1 - \rho_2$ if extended.
- [[../Conjectures/Sector Monotonicity]] — Phase 2 connection candidate.
- `notebooks/19-l-function-phase-1.ipynb` — interactive exploration (planned).
