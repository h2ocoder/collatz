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

In the Weyl spectrum of the real orbit, the wobble damps the $m = 31$ peak by roughly half (0.043 → 0.021) while $m = 44$ survives nearly intact (0.040 → 0.033) — so although 31 is the better Diophantine near-return, **44 is the most coherent visible near-return in the presence of the +1**. Also: both spectra are dominated by $m = 137$ ($137\alpha \approx 84.001$). Note $\alpha = [0; 1,1,1,1,2,2,3,1,5,\dots]$, so $84/137$ is a full *convergent*, and with the next partial quotient being 5, no better rational approximation exists until $q = 791$ — the 137-closure is the undisputed best over $138 \le q \le 790$, which is why it towers over the spectrum and should be visible in polar plots of long orbits. (Coincidence with the fine-structure constant $1/137$: cosmetic only — this 137 is a property of $\ln 3 / \ln 6$ and vanishes in any other base.)

## Follow-up Findings (`scripts/collatz_log6_wobble_followup.py`)

**4. The 31-vs-44 selection is sign-interference, and the wobble *sharpens* some peaks.**

Exactly, $A(m) = |\sum_k e^{2\pi i(\epsilon_m k + mW_k)}|/N$ with $\epsilon_m = m\alpha - \text{round}(m\alpha)$: a planar walk whose drift is the Diophantine miss plus $m$ times the wobble. Since the wobble is *always positive*, it partially cancels the drift of near-returns that close from below ($\epsilon < 0$: 13, 44, 75, 106) and worsens those that close from above ($\epsilon > 0$: 31, 137). Over 8 long orbits and 37 near-return peaks (`collatz_log6_wobble_sign_test.png`): $\epsilon < 0$ peaks *enhanced* 75% of the time with **median ratio 2.08** — the +1 doesn't just preserve those harmonics, it actively focuses them — while $\epsilon > 0$ peaks are damped 62% (median 0.94). The partial-sum walks (`collatz_log6_wobble_interference.png`) show the mechanism directly. So 44 beats 31 because $\epsilon_{44} < 0 < \epsilon_{31}$: the wobble is a one-sided lens.

**5. The carrier is renewal. Full stop.** The apparent $\chi^2$ excess dissolved under scrutiny: (a) at seeds $\sim 2^{33}$, requiring orbits to survive the window selects climbing orbits (odd density 0.339, count-variance ratio 0.76 — *under*-dispersed); at seeds $\sim 2^{59}$ (no selection) density = 0.3325, variance ratio 1.02–1.06, lag-1 gap correlation $+0.006 \pm 0.016$. (b) The original $\chi^2$ divided by the null's SE only, ignoring the orbit ensemble's equal sampling error — doubling the statistic under the null. Corrected: $\chi^2 = 65.3$ on 64 bins. No harmonic fingerprint of the rotation exists in the timing at this resolution.

**6. The wobble budget is independent of dropping time — but it is *banded*.**

Over all odd $n < 10^5$: $\overline{W_{\text{total}}} = 0.0852 \pm 0.030$, and per dropping-time-$k$ means are flat ($0.084$–$0.091$ across $k = 3$ to $75$, no trend). The budget is dominated by the universal tail through small values, which every orbit shares; the first drop (the head) leaves no imprint. **But** the distribution is strongly multimodal and the $(\log_6 n, W_{\text{total}})$ scatter shows discrete horizontal bands (`collatz_log6_wobble_budget.png`) — presumably orbit-tree merging: all $n$ funneling into a shared trajectory inherit nearly identical budgets, so $W_{\text{total}}$ quantizes on the merge tree.

## Third-pass Findings (`scripts/collatz_log6_wobble_bands.py`)

**7. The bands are landmark tails — 99.0% of the budget variance.**

Define the landmark $s(n)$ = first odd orbit value $< 100$. Then $W_{\text{total}}(n) = W_{\text{pre}}(n) + W_{\text{total}}(s)$ with $W_{\text{pre}} \ge 0$ tiny: over all odd $n < 10^5$, the 50 landmark tail values $\{W_{\text{total}}(s) : s \text{ odd} < 100\}$ explain **99.0% of the variance**; the residual $W_{\text{pre}}$ has median $0.0028$ and 95th percentile $0.0094$ (`collatz_log6_wobble_bands.png`). So the wobble budget is, to 1%, just *which of 50 small gateways the orbit enters through* — the bands in the histogram sit exactly at the $W_{\text{total}}(s)$ values. This gives the clean equivalence relation: seeds are partitioned into landmark fibers, and within a fiber the budget varies only by the pre-gateway wobble. (The residual histogram is itself multimodal — the partition refines hierarchically, presumably tracking the merge tree above the gateway.)

**8. The lens is directional, not linear.**

The naive quantitative version of the sign mechanism — replace $\epsilon_m$ by the corrected miss $\epsilon_m + m\bar{w}$ (with $\bar{w} = W_{\text{total}}/N$) in a Dirichlet kernel — **fails**: corr$(A_{\text{obs}}, A_{\text{lin}}) = -0.09$ versus corr$(A_{\text{obs}}, A_{\text{rot}}) = 0.98$ for no correction at all (`collatz_log6_wobble_lens_test.png`). Yet the *ratio* cloud does re-center: enhanced peaks cluster near zero corrected miss. Reading: the sign selection is real, but $W_k$ is a step function, not a ramp — the orbit is a sequence of constant-phase plateaus, so the Weyl sum is a sum of per-plateau Dirichlet kernels with phase offsets $2\pi m W_{\text{plateau}}$, and no single effective rotation number captures it.

**9. 137 confirmed as the dominant closure.**

The closure spectrum $\sigma(q) = \text{RMS}_k\,\text{wrap}(\theta_{k+q} - \theta_k)$ of orbit(670617279) has minima exactly at the convergent denominators, with the global minimum at $q = \mathbf{137}$ ($\sigma = 0.0092$); the top lags are $\{137, 106, 31, 168{=}137{+}31, 75\}$ (`collatz_log6_closure_spectrum.png`, with the polar render alongside). Note $\sigma(q)$ ranks by raw Diophantine quality (31 beats 44 here), while *Weyl visibility* ranks by wobble-corrected coherence (44 beats 31) — the two metrics answer different questions, and the polar-plot eye sees the latter.

## Fourth-pass Findings (`scripts/collatz_log6_wobble_plateaus.py`)

**10. The spectrum is controlled by the small-value cascade — concentrated, but not few.**

Approximating the wobble staircase by its $P$ largest jumps and recomputing the Weyl amplitudes: median relative error stays at 30–48% for $P \le 16$, drops to 9.4% at $P = 32$ and to 0.1% at $P = \mathbf{64}$ (`collatz_log6_plateau_model.png`). Of the ~300 odd steps in a long orbit, the smallest ~240 wobble jumps are irrelevant, but no *handful* of big jumps suffices either: amplitude prediction requires the full cascade of the ~64 deepest small-value visits. The non-monotone error at small $P$ (worse at $P=8$ than $P=2$) shows the jumps interfere — partial staircases can dephase peaks that the complete staircase re-phases.

**11. Gateway fibers are NOT residue-definable — they are transverse to the dropping framework.**

Unlike [[Dropping Set]]s (exactly unions of residue classes mod $2^k$), the landmark fibers show *zero* residue structure: purity within classes mod $2^j$ sits on the shuffled null for every $j = 1..14$ (excess $\le 0.004$), and Cramér's V between landmark and dropping time is **0.049** (`collatz_log6_landmark_residues.png`). The two partitions of the integers carry independent information, and the duality says why: dropping time is determined by the *head* of the orbit, finitely 2-adically ($n \bmod 2^k$); the gateway is determined by the *tail*, archimedean and not finitely determined by any modulus. The wobble budget is a genuinely new invariant, orthogonal to the dropping classification.

**12. The gateway hierarchy converges like $T^{-2}$.**

Variance of $W_{\text{total}}$ explained by the first-odd-below-$T$ landmark: 41% ($T{=}8$), 61% (16), 86% (32), 95% (64), 99.0% (100), 99.78% (200), 99.99% (1000) — unexplained residual falling roughly like $T^{-2}$, consistent with $W_{\text{pre}}$ being a sum of $O(1)$ jumps of size $O(1/T)$... squared in the variance. The fiber count grows as $T/2$, refining toward the full merge tree.

## Fifth-pass Findings (`scripts/collatz_log6_wobble_cutoff.py`)

**13. The spectral control is an altitude shell: $X^* \approx 3 \times 10^3$.**

Re-running the staircase truncation with an altitude cutoff (keep jumps from visits $x < X$) instead of a count: the error curves of all 8 orbits (lengths 500–990) **collapse onto a common curve**, crossing 5% at $X^* \approx 3{\times}10^3$ and 1% by $10^5$, independent of orbit length (`collatz_log6_cutoff.png`). The $P = 64$ of pass four was just this shell in disguise. The Weyl spectrum of an orbit is determined by the rigid rotation plus *what the orbit does below altitude $\sim 6^{4.5}$* — everything above is spectrally invisible.

**14. Head × tail factorizes — the joint partition is a product.**

Mutual information between dropping time (head) and gateway landmark (tail) is statistically zero: MI excess over the shuffled null = 0.0009 bits (1.2$\sigma$) for all odd $n < 10^5$, and 0.0004 bits (0.6$\sigma$) excluding $n \le 1000$; the standardized-residual heatmaps are featureless (`collatz_log6_head_tail.png`). So (dropping set, gateway) is a genuine product coordinate system: the head invariant is 2-adic and finitely residue-determined, the tail invariant is archimedean and residue-free, and they carry no information about each other.

**15. What the eye sees is parastichy — and it can never be 44.**

Raw Weyl amplitude is the wrong visibility metric at small $N$ ($|\epsilon_m| N \ll 1$ scores $\approx 1$ trivially). The correct one is the **parastichy count** (sunflower-spiral logic): the visible arm count of a dot spiral is the modal index gap between spatial nearest neighbors. For the radius-$\propto k$ render of the long orbit: **13 arms** for $N \le 250$, **31 arms** for $N \ge 300$ (`collatz_log6_visibility.png`), matching the geometric selection rule $q^* = \arg\min_q\, q^2 + (2\pi N \epsilon_q)^2$, which also predicts a jump to **137 arms near $N \approx 3000$, skipping 106 entirely**. Crucially, parastichy selection only ever picks *convergent* denominators — and 44 = 31+13 is a semiconvergent, so no dot-spiral render at any $N$ shows 44 arms. The article's 44 must therefore come from its specific plot recipe (most plausibly the *connected path* closing into a 44-gon, where the wobble-corrected Weyl coherence — which *does* favor 44 over 31, finding 4 — sets visibility, or a different radial coordinate).

## Sixth-pass Findings (`scripts/collatz_log6_wobble_resonance.py`)

**16. Closure resonances: the descent chirps, and the cancellation is exact at $r = 1$.**

The local wobble rate cancels a $q$-closure with $\epsilon_q < 0$ when the window wobble equals the miss. Binning the $q$-step closure miss by $r = \Delta W_{\text{window}} / |\epsilon_q|$ over 500 orbits: **every $\epsilon < 0$ harmonic (13, 44, 75, 106) dips sharply at exactly $r = 1$**, while the $\epsilon > 0$ harmonics (31, 137) climb monotonically — the one-sided lens (finding 4) caught in the act, with no free parameters (`collatz_log6_resonance.png`). In altitude coordinates the resonances ring in strict descending order — 106 ($\bar{a} \approx 6.1$) → 75 (4.6) → 44 (3.6) → 13 (2.4) — the orbit *chirps* through them as it falls. (Dips sit ~1 unit above the naive $x^*_q = q/(9 \ln 6 |\epsilon_q|)$ point estimate because window wobble is dominated by the window's smallest values, not its mean.) This is the final reconciliation of the article's 44: **31 never closes anywhere on a real orbit — the wobble only pushes it open. 44 rings, resonantly, in the few-hundreds altitude band that every orbit's visible tail occupies.**

**17. The 137-arm prediction confirmed, 12 bands for 12.**

A 145-digit seed gives a 3449-step orbit. Parastichy mode measured per radial band against the local selection rule $q^*(k) = \arg\min_q\, q^2 + (2\pi k \epsilon_q)^2$: **observed = predicted in all 12 bands** — 13 arms at $k \approx 143$, 31 arms from $k \approx 430$ through $2731$, **137 arms from $k \approx 3018$, with 106 skipped**, exactly as the rule requires (`collatz_log6_137_arms.png`). The polar render shows the arms chirping with radius in a single image. The selection rule is local in radius, not global in $N$ — pass five's "arms vs $N$" was this rule evaluated at the rim.

## Open Threads

- Reproduce Paper 3's literal figure recipe (PPR angle warp $P = (6^\theta - 1)/5$ and its actual radial coordinate) to identify which closure its specific rendering selects — the last unchecked box on the 2022 figures.
- The resonance dip offset (~1 altitude unit above the point estimate): replace mean altitude with the harmonic-mean altitude of the window and check the offset closes.
- The altitude shell $X^*$ (finding 13) should scale with $m_{\max}$ — testable by sweeping the harmonic range.

## Related

- [[The +1 Perturbation]] — the $x$-space view of the same obstruction
- [[Proportional Power Ratio]] — the original Paper 3 definition
- [[Dropping Time]] — $W_{\text{total}}$ rewrites the dropping inequality
- [[Logarithmic Escape Theorem]]
