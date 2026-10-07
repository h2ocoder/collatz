# The Wobble

[The Hidden Rotation](../journey/the-rotation) described a picture due to Shakibaei Asli (arXiv:2601.04289): in base-6 log coordinates, every Collatz step is the same rotation, $\theta \mapsto \theta + \log_6 3 \pmod 1$, because $-\log_6 2 \equiv \log_6 3 \pmod 1$. In the plain coordinate $\{\log_6 x\}$ used here, that picture has exactly one imperfection — the "+1" in $3n+1$. This page takes that imperfection apart by computation, on the orbits named below. It is an exploration, not a step towards a proof: an odd step and a halving turn the circle by the same angle, so the rotation carries no information about size, and nothing here says whether an orbit falls. The same decomposition exists for $3x-1$, with the wobble negative, and that map has cycles of its own.

Writing $\theta_k = \{\log_6 x_k\}$, the orbit satisfies **exactly**

$$\theta_k = \theta_0 + k\,\alpha + W_k \pmod 1, \qquad \alpha = \log_6 3 \approx 0.613147,$$

where the **wobble** $W_k$ collects one positive increment per odd step:

$$W_k = \sum_{\substack{j < k \\ x_j \text{ odd} } } \log_6\!\left(1 + \frac{1}{3x_j}\right).$$

The wobble *is* the +1. Everything else is rigid rotation. Telescoping gives the exact identity $W_{\text{total} } = \log_6\!\big(2^E / (3^O n)\big)$ for an orbit reaching 1 with $E$ halvings and $O$ odd steps: the wobble budget is the logarithm of the excess of halvings over triplings. The ratio $2^E/(3^O n)$ is what Roosendaal tabulates as the *residue* of $n$. Its largest value for $n$ below $10^5$ is 1.2531, at $n = 993$ (computed), and he conjectures that no $n$ does better.

![Cumulative wobble vs orbit altitude for three seeds — flat while the orbit is high, stepping up when it visits small values](/data/collatz_log6_wobble_traces.png)

For the 987-point orbit of 670617279, **92% of the total wobble comes from odd values below 100**. The wobble is a record of the orbit's visits to small numbers.

## Carrier × envelope: when it ticks and how much

The wobble is a pulse train with two components:

- **Envelope (how much):** the increment is *fully determined by position*: $\delta = \log_6(1 + 6^{-a}/3)$ where $a = \log_6 x$ is the altitude. This is the definition rewritten ($6^{-a} = 1/x$), so every orbit point lies on the one curve: the size of a tick depends only on where the orbit is.
- **Carrier (when):** the gaps between odd steps are $g = 1 + v_2(3x+1)$. Computed on 16,704 gaps from 400 orbit windows with random odd seeds between $2^{59}$ and $2^{60}$: the mean gap is 2.97 (independent geometric gaps would give 3), the correlation between successive gaps is $-0.004$ (two standard errors: $0.016$), and the averaged periodogram matches a renewal null ($\chi^2 = 65.3$ on 64 bins). At this resolution the timing looks like independent geometric gaps, the usual heuristic for the 3x+1 map, and no trace of the rotation was detected in it.

![The increment law: one curve per power-of-6 level, collapsing onto a single master curve in altitude](/data/collatz_log6_wobble_increment_law.png)

*When* the wobble ticks is read off the low binary digits of $x$; *how much* it ticks is read off the size of $x$. That much is exact, from the two formulas. Whether the two are independent along an orbit is a statistical question, and this page has only null results to offer on it: the carrier test above, and a test further down of dropping time against gateway.

## Coherence: the crystal analogy

Treat $W_k$ as phase disorder on the rotation. The coherence factor $D(m) = |\langle e^{2\pi i m W_k}\rangle|$ has the same form as the **Debye–Waller factor**, which gives the damping of the $m$-th Bragg peak of a crystal when the disorder is independent of position. Here that is an analogy only: the wobble is not independent of position, it only grows.

![Weyl spectrum with near-return peaks at 31/44/75/106/137, and the coherence D(m) staying above 0.91 while Gaussian noise of equal variance would die by m≈60](/data/collatz_log6_wobble_debye_waller.png)

For the 987-point orbit of 670617279, $\sigma_W = 0.0082$. *Gaussian* phase noise of that size would halve the coherence by $m \approx 23$ and destroy it by $m \approx 60$. Computed: $D(m) \ge 0.915$ out to $m = 150$. The reason is visible in the traces above: the wobble is long plateaus and a few late kicks, and 98% of this orbit's points come before a tenth of the wobble has accrued. $D(m)$ does not give the height of the peaks, though: on the same orbit the 31-peak is half what the pure rotation gives and the 44-peak three times as much. That is the next section.

## 44 against 31: a one-sided lens

The peaks sit at the continued-fraction denominators of $\alpha = [0; 1,1,1,1,2,2,3,1,5,\dots]$: 13, 31, 106, 137 are convergents; 44 = 31+13 is a *semiconvergent*. By pure Diophantine quality, 31 ($\epsilon = +0.0076$) beats 44 ($\epsilon = -0.0215$). Yet in the Weyl spectrum of the orbit of 670617279 the 44-peak stands above the 31-peak (0.033 against 0.022), where the pure rotation has them the other way round (0.010 against 0.042). Why?

Because the wobble is **always positive**, it can only push a near-return one way: it *cancels* misses that close from below ($\epsilon < 0$: 13, 44, 75, 106) and *worsens* misses that close from above ($\epsilon > 0$: 31, 137). Over 8 long orbits and 37 near-return peaks (computed), the $\epsilon \lt 0$ peaks came out enhanced in 75% of cases (median ratio 2.08) and the $\epsilon > 0$ peaks damped in 62% (median ratio 0.94): a tendency, not a rule. On the orbit above, the peaks at 13 and 106 are damped although their $\epsilon$ is negative.

By the identity at the top of the page, the $q$-step closure miss is exactly $|\epsilon_q + \Delta W|$, with $\Delta W \ge 0$ the wobble gained in those $q$ steps (as long as that sum stays below $\tfrac12$; on the orbits used here it never exceeds 0.13). For $\epsilon_q > 0$ the miss can never be less than $\epsilon_q$. For $\epsilon_q \lt 0$ it shrinks towards zero as $\Delta W$ approaches $|\epsilon_q|$ and grows again beyond. The wobble rate rises as the orbit comes down, so each $\epsilon \lt 0$ closure comes nearest to cancelling at an altitude of its own. Binning the miss by $r = \Delta W_{\text{window} } / |\epsilon_q|$, and by altitude, over 500 orbits (the first 500 odd seeds above $10^6$ whose orbits have at least 250 points):

![Every ε<0 harmonic dips sharply at exactly r = 1; ε>0 harmonics only climb. Right panel: the descent chirps through the resonances 106 → 75 → 44 → 13 in altitude order](/data/collatz_log6_resonance.png)

The dip at $r = 1$ is that identity, not a measurement, and 31 and 137 can only climb. What is measured is where along the descent each harmonic meets it. In these 500 orbits the dips sit at window-mean altitudes of about 6.1 for 106, 4.6 for 75, 3.6 for 44 (values of several hundred) and 2.4 for 13. That suggests one more possible ingredient of the 44-cycles in the original [Proportional Power Ratios article](https://python.plainenglish.io/the-collatz-conjecture-a-new-perspective-on-an-old-problem-f4bca7ff675a): the +1 nearly cancelling the 44-step miss low in the orbit. The 44 in the article's polar plots already has two plainer sources, given on the [Prior Work](../publications) page: the angle there is the step index in radians, and 44 radians is almost exactly 7 turns; and $44 \log_6 3 \approx 26.98$. Whether the cancellation adds anything visible to those plots has not been tested. The 31-step miss never falls below 0.0076, but averaged over the whole orbit of 670617279 it is still the smaller of the two (RMS 0.0116 against 0.0219 for 44).

## The wobble budget is set near the bottom

$W_{\text{total} }(n)$ looks like a per-orbit quantity, but in the range tested it is 99% a *per-gateway* quantity (computed): defining the landmark $s(n)$ = first odd orbit value below 100, the 50 tail budgets $\{W_{\text{total} }(s)\}$ explain **99.0% of the variance** over all odd $n < 10^5$.

![The wobble budget histogram is banded; the bands sit at the 50 landmark tail values; the residual pre-gateway wobble is tiny](/data/collatz_log6_wobble_bands.png)

In the same range the gateway classification shows no relation to the dropping-time framework (computed, odd $n$ below $10^5$): inside residue classes mod $2^j$, $j \le 14$, the landmark fibers are about as pure as a shuffled null (excess at most 0.004); Cramér's V between landmark and dropping time is 0.049; their mutual information is within 1.2 standard deviations of the shuffled null. Dropping time is a *head* quantity, read from the low binary digits of $n$. The gateway is a *tail* quantity, and no residue structure was found in it. These are null results at this sample size, not a proof of independence; and that every integer has a gateway at all is the Collatz conjecture.

## The sunflower test: predicting 137

What the eye sees in a polar render of the orbit (angle $2\pi\theta_k$, radius $k$) is a **parastichy count** — the same mathematics as the spiral arms of a sunflower head. Take the arm count at radius $k$ to be the index gap between a point and its nearest neighbour; for a rotation that is, to a good approximation,

$$q^*(k) = \arg\min_q \; q^2 + (2\pi k\,\epsilon_q)^2,$$

which predicts: 13 arms inside $k \approx 160$, 31 arms to $k \approx 2840$, then **137 arms — with 106 skipped entirely**. Orbits that long typically need seeds around $10^{140}$. A 145-digit seed gives a 3449-step orbit, and the observed arm count matches the prediction in **all 12 radial bands**:

![Giant orbit: observed parastichy mode equals the predicted arm count in every radial band — 13, then 31, then 137, with 106 skipped](/data/collatz_log6_137_arms.png)

The prediction was made before the orbit was computed. It is a statement about the rotation number alone: a rigid rotation by $\log_6 3$ with as many points shows the same twelve arm counts (computed). What the giant orbit adds is that the wobble is too small to disturb them.

## A dictionary of physics analogies

| Collatz object | Physics counterpart |
|---|---|
| Rotation by $\log_6 3$ | Integrable system; the unperturbed flow |
| Weyl peaks at 13/31/44/106/137 | Bragg diffraction of a 1D quasicrystal |
| Wobble $W_k$ | Disorder field / phase noise |
| Coherence $D(m)$ | Debye–Waller factor (same formula; it does not give the peak heights here) |
| Odd-step train × increment law | AM signal: renewal carrier, deterministic envelope |
| Timing read from the low binary digits, amplitude from the size | Loosely adelic: one factor for each completion of $\mathbb{Q}$, as in the Freund–Witten product formula of p-adic string theory |
| Near-cancellation at $\Delta W / \lvert\epsilon_q\rvert = 1$ | Phase-locking of a driven oscillator; mode pulling |
| Arm counts 13 → 31 → 137 | Phyllotaxis / parastichy |

These are analogies, some closer than others: the Debye–Waller and parastichy rows share a formula with their counterpart, the rest only a resemblance. None is a claim of physical mechanism, and none is evidence about the conjecture.

## Where this lives in the repo

- Research note: [Log-6 Rotation Duality](https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Log-6%20Rotation%20Duality.md) (working notes)
- Scripts: `scripts/collatz_log6_wobble*.py` (six passes: dynamics, mechanism, bands, plateaus, cutoff, resonances)
- The same quantity elsewhere on the site: the $\varepsilon$ in the bookkeeping identity on [The Hidden Rotation](../journey/the-rotation) is $-W_{\text{total} } \log_2 6$
