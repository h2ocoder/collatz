# The Wobble

[The Hidden Rotation](../journey/the-rotation) showed that in base-6 log coordinates, every Collatz step is the same rotation: $\theta \mapsto \theta + \log_6 3 \pmod 1$, because $-\log_6 2 \equiv \log_6 3 \pmod 1$. That picture has exactly one imperfection — the "+1" in $3n+1$. This page is about what that imperfection *is*, harmonically: a complete dissection of the perturbation, with every visual mystery of the polar plots reduced to a named mechanism.

Writing $\theta_k = \{\log_6 x_k\}$, the orbit satisfies **exactly**

$$\theta_k = \theta_0 + k\,\alpha + W_k \pmod 1, \qquad \alpha = \log_6 3 \approx 0.613147,$$

where the **wobble** $W_k$ collects one positive increment per odd step:

$$W_k = \sum_{\substack{j < k \\ x_j \text{ odd}}} \log_6\!\left(1 + \frac{1}{3x_j}\right).$$

The wobble *is* the +1. Everything else is rigid rotation. Telescoping gives the exact identity $W_{\text{total}} = \log_6\!\big(2^E / (3^O n)\big)$ for an orbit reaching 1 — the wobble budget is literally the excess of halvings over triplings, the quantity every stopping-time argument is about.

![Cumulative wobble vs orbit altitude for three seeds — flat while the orbit is high, stepping up when it visits small values](/data/collatz_log6_wobble_traces.png)

For the 987-point orbit of 670617279, **92% of the total wobble comes from odd values below 100**. The wobble is a record of the orbit's visits to small numbers.

## Carrier × envelope: the two arithmetics factorize

The wobble is a pulse train, and its two components live in different arithmetics:

- **Envelope (how much):** the increment is *fully determined by position*: $\delta = \log_6(1 + 6^{-a}/3)$ where $a = \log_6 x$ is the altitude. Thousands of orbit points collapse exactly onto this one master curve — deterministic, archimedean clockwork.
- **Carrier (when):** the gaps between odd steps are $g = 1 + v_2(3x+1)$. Across ~17k gaps from unbiased large seeds: geometric gap law, zero lag correlation, periodogram flat against the renewal null. The timing is pure 2-adic noise — no fingerprint of the rotation survives in it.

![The increment law: one curve per power-of-6 level, collapsing onto a single master curve in altitude](/data/collatz_log6_wobble_increment_law.png)

*When* the wobble ticks is multiplicatively invisible; *how much* it ticks is additively invisible. The +1 decomposes across the two completions of $\mathbb{Q}$ it touches — and the decomposition is statistically exact (mutual information between head and tail invariants: $0.6\sigma$ from zero).

## The crystal that doesn't melt

Treat $W_k$ as phase disorder on the rotation. The coherence factor $D(m) = |\langle e^{2\pi i m W_k}\rangle|$ measures how the disorder damps the $m$-th harmonic of the Weyl spectrum — formally identical to the **Debye–Waller factor** that measures how thermal vibration damps Bragg peaks in a crystal.

![Weyl spectrum with near-return peaks at 31/44/75/106/137, and the coherence D(m) staying above 0.91 while Gaussian noise of equal variance would die by m≈60](/data/collatz_log6_wobble_debye_waller.png)

With $\sigma_W = 0.0082$, *Gaussian* phase noise would halve coherence by $m \approx 23$ and destroy it by $m \approx 60$. Observed: $D(m) \ge 0.915$ out to $m = 150$. The wobble is **shot noise** — long plateaus, rare discrete kicks — and discrete disorder preserves coherence that continuous jitter would destroy (the same reason the Mössbauer effect gives recoil-free emission). The quasicrystal structure of the orbit survives the +1 at every harmonic we can measure.

## Why 44 beats 31: a one-sided lens

The peaks sit at the continued-fraction denominators of $\alpha = [0; 1,1,1,1,2,2,3,1,5,\dots]$: 13, 31, 106, 137 are convergents; 44 = 31+13 is a *semiconvergent*. By pure Diophantine quality, 31 ($\epsilon = +0.0076$) beats 44 ($\epsilon = -0.0215$). So why do real orbit plots favor 44?

Because the wobble is **always positive**, it can only push a near-return one way: it *cancels* misses that close from below ($\epsilon < 0$: 13, 44, 75, 106) and *worsens* misses that close from above ($\epsilon > 0$: 31, 137). Over 8 long orbits, $\epsilon < 0$ peaks are enhanced with median ratio 2.08; $\epsilon > 0$ peaks are damped.

And the cancellation is *resonant*. The local wobble rate falls as the orbit's altitude falls, so each $\epsilon < 0$ closure passes through **exact cancellation** at its own altitude. Binning the $q$-step closure miss by $r = \Delta W_{\text{window}} / |\epsilon_q|$ over 500 orbits:

![Every ε<0 harmonic dips sharply at exactly r = 1; ε>0 harmonics only climb. Right panel: the descent chirps through the resonances 106 → 75 → 44 → 13 in altitude order](/data/collatz_log6_resonance.png)

Every $\epsilon < 0$ harmonic dips at exactly $r = 1$ — no free parameters — while 31 and 137 only climb. A falling orbit **chirps** through the resonances in order: 106 rings near altitude $6^{6}$, then 75, then **44 rings in the few-hundreds band that every orbit's visible tail occupies**, then 13. The 44-cycles in the original [Proportional Power Ratios article](https://python.plainenglish.io/the-collatz-conjecture-a-new-perspective-on-an-old-problem-f4bca7ff675a) were never an approximation artifact — they are the +1 perturbation itself, caught at resonance. 31, the "better" approximation, never closes anywhere on a real orbit.

## The wobble budget is a new invariant

$W_{\text{total}}(n)$ looks like a per-orbit quantity, but it's 99% a *per-gateway* quantity: defining the landmark $s(n)$ = first odd orbit value below 100, the 50 tail budgets $\{W_{\text{total}}(s)\}$ explain **99.0% of the variance** over all odd $n < 10^5$.

![The wobble budget histogram is banded; the bands sit exactly at the 50 landmark tail values; the residual pre-gateway wobble is tiny](/data/collatz_log6_wobble_bands.png)

And this gateway classification is **provably transverse** to the dropping-time framework: landmark fibers show zero residue structure mod $2^j$ for all $j \le 14$ (purity = shuffled null), and zero mutual information with dropping time. Dropping time is a *head* invariant — 2-adic, determined by $n \bmod 2^k$. The gateway is a *tail* invariant — archimedean, residue-free. Every integer carries both coordinates, and they are independent.

## The sunflower test: predicting 137

What the eye sees in a polar render of the orbit (angle $2\pi\theta_k$, radius $k$) is a **parastichy count** — the same mathematics as the spiral arms of a sunflower head. The visible arm count at radius $k$ is

$$q^*(k) = \arg\min_q \; q^2 + (2\pi k\,\epsilon_q)^2,$$

which predicts: 13 arms inside $k \approx 160$, 31 arms to $k \approx 2840$, then **137 arms — with 106 skipped entirely**. Orbits that long need seeds around $10^{140}$. A 145-digit seed gives a 3449-step orbit, and the observed arm count matches the prediction in **all 12 radial bands**:

![Giant orbit: observed parastichy mode equals the predicted arm count in every radial band — 13, then 31, then 137, with 106 skipped](/data/collatz_log6_137_arms.png)

A falsifiable prediction, made before the orbit was computed, confirmed on a number $10^{130}$ times larger than anything in the original article.

## Physics dictionary

| Collatz object | Physics counterpart |
|---|---|
| Rotation by $\log_6 3$ | Integrable system; the unperturbed flow |
| Weyl peaks at 13/31/44/106/137 | Bragg diffraction of a 1D quasicrystal |
| Wobble $W_k$ | Disorder field / phase noise |
| Coherence $D(m)$ | Debye–Waller factor; shot-noise analogue of the Mössbauer recoil-free fraction |
| Odd-step train × increment law | AM signal: renewal carrier, deterministic envelope |
| 2-adic timing ⊥ archimedean amplitude | Adelic factorization (the Freund–Witten lesson from p-adic string theory) |
| Resonance at $\Delta W / \|\epsilon_q\| = 1$ | Phase-locking of a driven oscillator; mode pulling |
| Arm counts 13 → 31 → 137 | Phyllotaxis / parastichy |

These are structural correspondences — the same mathematics on a different substrate — not claims of physical mechanism.

## Where this lives in the repo

- Research note: [Log-6 Rotation Duality](https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Log-6%20Rotation%20Duality.md) — 17 numbered findings
- Scripts: `scripts/collatz_log6_wobble*.py` (five passes: dynamics, mechanism, bands, plateaus, resonances)
- The companion proof-side view of the same obstruction: [The Countdown](../journey/the-countdown) and the $\varepsilon$ term in the conservation law
