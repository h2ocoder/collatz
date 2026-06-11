# Log-6 Rotation Duality

**Question:** Why does the base-6 [[Proportional Power Ratio]] plot look so ordered — as if the space were warped in a way that a single dot's location determines its number? And what structure remains once the warp is undone?

**Status:** Active. Rotation structure verified; wobble dynamics explored in `scripts/collatz_log6_wobble.py` (results below).

## The Duality

Logarithm is the exact dictionary between the two arithmetics of $\mathbb{R}^+$: it is an isomorphism $(\mathbb{R}^+, \times) \to (\mathbb{R}, +)$. Multiplication and addition are the same structure in different coordinates. The Collatz map is hard because it mixes both, and each half is trivial in one coordinate system and warped in the other:

| | $x$-space | $\log$-space |
|---|---|---|
| $+1$ | trivial (shift) | nonlinear wobble $\log_6(1 + \tfrac{1}{3x})$ |
| $\times 3$, $\div 2$ | "warping" | trivial (rigid translation) |

No coordinate system linearizes both at once. The conjecture lives in the seam — the same seam as the abc conjecture, Furstenberg's $\times 2, \times 3$ problem, and the reason Tao (2019) works in logarithmic density. This is the log-coordinate face of [[The +1 Perturbation]].

## The Rotation

Define $\theta(x) = \{\log_6 x\}$ (fractional part). Under one Collatz step:

- odd: $x \to 3x+1$, so $\theta \mapsto \theta + \log_6 3 + \log_6(1 + \tfrac{1}{3x}) \pmod 1$
- even: $x \to x/2$, so $\theta \mapsto \theta - \log_6 2 \pmod 1$

But $\log_6 2 + \log_6 3 = 1$, so $-\log_6 2 \equiv \log_6 3 \pmod 1$. **Every step, odd or even, rotates $\theta$ by the same irrational angle** $\alpha = \log_6 3 \approx 0.613147$, plus (at odd steps only) a small positive wobble. This identity ($2 \cdot 3 = 6$) is the entire reason base 6 is special — bases 2 and 3 see two different step sizes; base 6 sees one.

So in $(k, \theta)$ coordinates the orbit is a **rigid circle rotation plus a bounded wobble**:

$$\theta_k = \theta_0 + k\alpha + W_k \pmod 1, \qquad W_k = \sum_{\substack{j < k \\ x_j \text{ odd}}} \log_6\!\left(1 + \frac{1}{3x_j}\right)$$

**Verified:** over the 987-step orbit of $670617279$, $\max_k |W_k| < 0.094$; over orbit(27), $< 0.102$. A dot's angle determines its step index and vice versa, to within $\pm 0.1$ — the "orderly warp" of the base-6 picture, made literal.

## Why 44

The polar plot closes up every $k$ steps when $k\alpha$ is nearly an integer. Distances of $k\alpha$ from the nearest integer:

| $k$ | $\|k\alpha - \text{round}(k\alpha)\|$ |
|---:|---:|
| 31 | 0.0076 |
| **44** | **0.0215** ($44\alpha \approx 26.978$: ~27 full turns) |
| 106 | 0.0064 |

$27/44$ is a semiconvergent of the continued fraction of $\alpha = \ln 3 / \ln 6$. The article's open question "why 44?" reduces to Diophantine approximation of $\alpha$. (Open sub-question: 31 and 106 are *better* near-returns — why does 44 visually dominate the polar plots? Likely an interaction with point count and the radial coordinate.)

## The Wobble Is the Conjecture

The wobble $W_k$ is a monotone increasing sum of positive increments $\delta_j = \log_6(1 + \tfrac{1}{3x_j})$, one per odd step, with size $\sim \frac{1}{3x_j \ln 6}$. It is the entire content of the +1; everything else is rigid rotation. Exactly (telescoping the orbit product):

$$W_{\text{total}} = \log_6\frac{x_T}{x_0} - O\log_6 3 + E \log_6 2$$

where $O, E$ count odd/even steps. For an orbit reaching 1, $W_{\text{total}} = \log_6(2^E / 3^O x_0) > 0$ — the wobble budget *is* the excess of halvings over triplings, i.e. the quantity [[Dropping Time]] inequalities are about.

Because $\delta_j \sim 1/x_j$, the wobble is a record of the orbit's visits to *small* values: flat while the orbit is high, stepping up when it comes down. For orbit(670617279), **92% of $W_{\text{total}}$ comes from odd $x < 100$**.

## Wobble Findings (`scripts/collatz_log6_wobble.py`)

**1. The wobble decomposes as carrier × envelope, and the duality splits them cleanly.**

- **Envelope (amplitude):** the increment is *fully determined by position in log space*: $\delta = \log_6(1 + 6^{-a}/3)$ where $a = m + \theta$ is the altitude. Verified to overlay exactly (`collatz_log6_wobble_increment_law.png`): one curve per level $m$, self-similar with ratio 6, collapsing onto a single master curve in $a$. The amplitude is **archimedean-deterministic** — your "warped space" intuition made exact.
- **Carrier (timing):** odd steps occur with gaps $g = 1 + v_2(3x+1)$. Over 400 orbit windows (seeds $\sim 2^{33}$, ~17k gaps): gap law matches geometric $2^{-(g-1)}$ (the $g \ge 10$ deficit is window-censoring, reproduced by the censored null), mean gap $2.949$ vs $3$, lag-1 gap correlation $-0.015 \pm 0.015$, autocorrelation and average periodogram inside the renewal null band (`collatz_log6_wobble_carrier_spectrum.png`). The timing is **2-adically random** — no harmonic fingerprint of the rotation survives in the carrier.

So the two arithmetics literally factor the wobble: *when* it ticks is 2-adic noise; *how much* it ticks is archimedean clockwork. (Residual: ensemble periodogram $\chi^2 \approx 119$ on 64 bins — mildly elevated, plausibly the surviving-orbit selection bias on odd density, 0.339 vs 1/3. Worth a closer look.)

**2. The wobble is shot noise, not diffusion — and the rotation lattice survives it (Debye–Waller).**

Treating $W_k$ as phase disorder on the rotation, the coherence factor $D(m) = |\langle e^{2\pi i m W_k}\rangle|$ measures damping of the $m$-th Weyl harmonic, exactly like thermal disorder damping Bragg peaks. For orbit(670617279), $\sigma_W = 0.0082$: Gaussian phase noise of that variance would halve coherence by $m \approx 23$ and kill it by $m \approx 60$. Observed: $D(m) \ge 0.915$ out to $m = 150$ (`collatz_log6_wobble_debye_waller.png`). The wobble's plateau-and-jump (shot-noise) profile keeps the orbit phase-locked to the rigid rotation at *all* observed harmonics. The crystal does not melt.

**3. A candidate answer to "why 44 beats 31".**

In the Weyl spectrum of the real orbit, the wobble damps the $m = 31$ peak by roughly half (0.043 → 0.021) while $m = 44$ survives nearly intact (0.040 → 0.033) — so although 31 is the better Diophantine near-return, **44 is the most coherent visible near-return in the presence of the +1**. Also: both spectra are dominated by $m = 137$ ($84/137$, the next semiconvergent, $137\alpha \approx 84.001$) — a sharper closure that should be visible in polar plots of long orbits.

## Open Threads

- Explain *which* near-return harmonics the wobble damps and why (the 31-vs-44 selection). The damping is not monotone in $m$, so it must interact with where on the orbit the wobble jumps occur.
- The mild carrier-spectrum excess ($\chi^2 = 119/64$) — selection artifact or weak real correlation in $v_2$ along orbits?
- $W_{\text{total}}$ as a per-orbit invariant: its distribution over $n$, and whether [[Dropping Set]] membership is visible in wobble statistics.

## Related

- [[The +1 Perturbation]] — the $x$-space view of the same obstruction
- [[Proportional Power Ratio]] — the original Paper 3 definition
- [[Dropping Time]] — $W_{\text{total}}$ rewrites the dropping inequality
- [[Logarithmic Escape Theorem]]
