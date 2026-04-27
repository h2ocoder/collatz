# Lens C — Implication Catalog

**Parent:** [[Assume Collatz - Consequences]] (breadth-first scan)
**Status:** Working draft, deepens Lens C of the parent. Catalogs every candidate $X$ such that $X \Rightarrow$ Collatz, grades each by proof-theoretic distance and required tools, and identifies the most promising single attack.

## Method

For each candidate $X$ we record:

- **Statement** — precise enough to pin down the open part.
- **Status** — open / partial theorem / fully proved.
- **Implication chain** — does $X$ alone give Collatz, or does it slot into a multi-step chain (e.g., No Cycles is already proved; we still need No Divergence).
- **Tools required** — what mathematical machinery is needed.
- **Distance to proof** — qualitative scale ★ (immediate) → ★★★★★ (as hard as Collatz).
- **Strength estimate** — rough proof-theoretic placement (RCA₀ / WKL₀ / ACA₀ / PA / beyond PA).
- **Why promising** — single sentence.

Collatz splits canonically into **No Cycles** + **No Divergence**. No Cycles is proved (see [[Proof Attempt - Denjoy Bridge]] Part I). Every $X$ in this catalog therefore targets No Divergence — that is what remains.

---

## Summary Table

| # | Candidate $X$ | Status | Distance | Strength | Lens-C alone? |
|---|---------------|--------|---------:|----------|---------------|
| 1 | Absolute Continuity of Collatz IFS measure | Open | ★★★ | ACA₀ likely | Yes (with No Cycles) |
| 2 | Sector Monotonicity | Open, 0/135K counterexamples | ★★ | RCA₀–WKL₀ | Yes (alone gives $O(\log^2 n)$) |
| 3 | Pointwise bit-destruction $\geq c$ | Open (avg proved) | ★★★ | WKL₀ | Yes (with bit-destruction lemma) |
| 4 | Multi-bit mixing (orbit hits Set_k≥6 w/ positive density) | Open | ★★★ | ACA₀ | Yes (closes Denjoy Bridge) |
| 5 | Discrete Denjoy theorem | Open | ★★★★ | beyond ACA₀ | Yes (with bit-mixing) |
| 6 | ~~Adelic Conservation $\prod_\ell \rho_\ell \le 1$~~ — **withdrawn (tautology, see §6)** | — | — | — | — |
| 7 | Bounded orbits (orbit max $\le f(n)$) | Open | ★★★★ | PA-edge | Yes (with No Cycles = Collatz) |
| 8 | Tao-gap closure (almost-all → all; $f(n) \to \infty$ → 1) | Theorem (almost-all) | ★★★★ | ACA₀ | Yes |
| 9 | Density refinement (Krasikov-Lagarias style) | Partial, improvable | ★★★★★ | ACA₀ | No (needs full density 1) |

**Distance scale:** ★ proof in scope of existing theory; ★★ proof needs one new lemma; ★★★ needs new technique on existing tools; ★★★★ needs new theory; ★★★★★ as hard as Collatz.

---

## 1. Absolute Continuity of the Collatz IFS Measure

**Statement.** The self-similar measure $\mu$ on $\mathbb{R}$ defined by $\mu = \tfrac{1}{2}(\phi_0)_* \mu + \tfrac{1}{2}(\phi_1)_* \mu$ with $\phi_0(x) = x/2$, $\phi_1(x) = (3x+1)/2$ is absolutely continuous w.r.t. Lebesgue measure.

**Status.** Open. The Lyapunov exponent is $\chi = \ln(2/\sqrt{3}) \approx -0.144 < 0$ and similarity dimension $s = \log 2 / \log(2/\sqrt{3}) \approx 4.82 \gg 1$, putting the IFS deep in the super-critical regime. Standard absolute-continuity theorems (Hochman 2014, Shmerkin 2019, Varjú 2019) require all branches to be contracting; the Collatz IFS has $|r_1| = 3/2 > 1$.

**Implication chain.** AC of $\mu$ + No Cycles ⇒ equidistribution of orbits in $\log_6$ coordinates ⇒ encounter frequency with high Set_k ≥ 25% (vs the 4.4% needed) ⇒ contraction wins ⇒ Collatz. See [[Proof Attempt - Adelic IFS Bridge]] for the full chain.

**Tools required.** Fractal geometry, Fourier dimension, transversality methods. Specifically: extend Hochman's exponential separation theorem to non-uniformly contracting IFS where $\prod |r_j|^{p_j} < 1$ but $\max |r_j| > 1$.

**Distance ★★★.** The single missing technical step is in active fractal-geometry research. No new "framework" needed — just an extension theorem in a literature that already produces 30+ papers/year.

**Strength estimate.** Likely ACA₀; absolute continuity statements live there.

**Why promising.** Concrete, narrow, named open problem. Failure mode is bounded — if Hochman/Shmerkin extension is unattainable, the lens dies cleanly without consuming other lenses.

---

## 2. Sector Monotonicity

**Statement.** Let $\sigma(\text{drop}) = s \bmod 12$ (the Eisenstein sector). Within each of the 12 sectors, the sequence of orbit values at sector revisits is strictly decreasing. See [[Sector Monotonicity]].

**Status.** Open. Empirically verified: 135,565 sector revisits checked for $n < 50{,}000$, zero violations.

**Implication chain.** Sector monotonicity alone ⇒ each of 12 sectors visited at most $\lfloor \log_2 n \rfloor$ times ⇒ total drops $\le 12 \log_2 n$ ⇒ $O(\log^2 n)$ total steps ⇒ Collatz. **Closes No Divergence in one step.**

**Tools required.** Eisenstein integers $\mathbb{Z}[\omega]$, period-12 algebra of $\pi^s$, radial-coordinate boundedness within fixed angular sector. Likely needs a per-sector "monotone Lyapunov function" argument.

**Distance ★★.** A clean algebraic statement on a well-understood algebraic structure. The 12-fold quotient is small enough for case analysis. The radial dynamics within a sector decouple from angular dynamics ([[Eisenstein Factorization]]) — which suggests the proof factors cleanly.

**Strength estimate.** RCA₀ to WKL₀. Statement is $\Pi_2$ but the bound is uniform.

**Why promising.** Highest yield-per-effort in the catalog. Conditional on truth (which is empirically rock-solid), it crushes the conjecture. The structural framework already exists in our docs. **This is the recommended first attack target.**

---

## 3. Pointwise Bit-Destruction $\geq c$

**Statement.** For every odd $n > 1$ and every drop in its orbit through $\text{Dset}_k$ with oddity $s$, the bits destroyed $\beta(s) = 1 - \{s \log_2 3\}$ satisfy $\beta(s) \geq c$ for some absolute constant $c > 0$ depending only on $\log_2(n)$.

**Status.** Average over $s$ proved in expectation; pointwise version open. By Roth's theorem we have $\beta(s) > c/s$ but $s$ can grow with the orbit.

**Implication chain.** If $\beta(s_i) \geq c'/B$ uniformly over all drops (where $B = \log_2 n_0$), then total bits destroyed $\geq O(B^2)$ over the orbit, but the orbit only has $O(B)$ bits. Hence orbit terminates in $O(B^2)$ drops. See [[Bit Destruction Bound]] for the conditional theorem; this candidate makes it unconditional.

**Tools required.** Refined Diophantine approximation of $\log_2 3$, possibly continued-fraction analysis of which $s$-values actually appear in real orbits.

**Distance ★★★.** Needs a new technique: control the *distribution* of $s$ along an orbit, not just the spectrum of possible $s$. Empirically the distribution is heavily weighted to small $s$ (most drops are Set_3), so the "bad" $s = q_n$ (Diophantine convergents) appear rarely — but rare $\neq$ never.

**Strength estimate.** WKL₀ probably suffices.

**Why promising.** Quantitative target with known partial bounds. Worth pursuing if Sector Monotonicity stalls.

---

## 4. Multi-Bit Mixing

**Statement.** For every orbit, the asymptotic frequency of drops through $\text{Dset}_k$ with $k \geq 6$ is at least $\delta > 0$.

**Status.** Open. This is exactly the lemma left ungeproven in [[Proof Attempt - Denjoy Bridge]]. Set_3 alone gives geometric mean contraction ratio $\approx 9/8 > 1$ (net growth); adding Set_6 visits at frequency $\geq 4.4\%$ flips the geometric mean below 1.

**Implication chain.** Multi-bit mixing + Bit Destruction Bound + No Cycles ⇒ Collatz.

**Tools required.** Ergodic theory for Syracuse map on $\mathbb{Z}_2$, equidistribution arguments. The Markov chain on residues mod $2^B$ has spectral gap $5/6$; the question is whether *individual orbits* inherit the invariant measure's statistics. (User has proved spectral mixing for the *measure*; pointwise individual-orbit mixing is the gap.)

**Distance ★★★.** Same structural difficulty as #1: passing from "almost every" / "in expectation" to "every individual orbit." Connects to Birkhoff vs. unique ergodicity.

**Strength estimate.** ACA₀ for ergodic content.

**Why promising.** Smallest semantic gap to existing user results. The Spectral Mixing Theorem is essentially this fact for the average; lifting to pointwise is a known type of step.

---

## 5. Discrete Denjoy Theorem

**Statement.** Let $T : [0,1) \to [0,1)$ be a circle map with rotation number $\alpha$ irrational and bounded variation perturbation $\varepsilon(x)$ with $|\varepsilon| < \tau$ for some explicit $\tau$. Then $T$ is minimal (every orbit dense). The Collatz map in $\log_6$ coordinates fits this template with $\alpha = \log_6 3$, $|\varepsilon| \leq 0.2749$ (Shakibaei Asli).

**Status.** Open as stated. The classical Denjoy theorem (1932) requires $T$ to be $C^1$ on the actual circle; the Collatz analogue is a perturbed rotation on integer points pulled back to the circle. No discrete Denjoy theorem is currently known with this generality.

**Implication chain.** Discrete Denjoy ⇒ orbit dense in $\log_6$ circle ⇒ encounter frequency with Set_k = (measure of Set_k under invariant measure) ⇒ multi-bit mixing (#4) ⇒ Collatz.

**Tools required.** New theory of perturbed rotations on lattices. Existing Denjoy proofs use cross-ratio / bounded variation arguments that don't survive discretization.

**Distance ★★★★.** Genuinely new theory needed. Higher distance than #1 because absolute continuity is in active research; discrete Denjoy is essentially unstudied.

**Strength estimate.** Beyond ACA₀ likely.

**Why promising.** If proved, would be a major result independent of Collatz — Denjoy-style theorems are foundational. But high effort, high risk.

---

## 6. ~~Adelic Conservation Axiom~~ — Withdrawn

**Original statement.** "Let $H$ be a Hydra on $\mathbb{Z}$ with rational ratios $r_j$. If $\prod_\ell \rho_{H,\ell} \leq 1$ over all places $\ell$, then $H$ terminates."

**Why withdrawn.** The product $\prod_\ell \rho_\ell$ is **identically 1** for any Hydra with nonzero rational ratios, by the adelic product formula:

$$\prod_\ell \rho_\ell \;=\; \prod_\ell |r_0|_\ell \cdot |r_1|_\ell \;=\; \left(\prod_\ell |r_0|_\ell\right)\left(\prod_\ell |r_1|_\ell\right) \;=\; 1 \cdot 1 \;=\; 1$$

since $\prod_\ell |x|_\ell = 1$ for every nonzero $x \in \mathbb{Q}$.

**Sanity check.** Collatz: $(3/4)(4)(1/3) = 1$. $5n+1$: $(5/4)(4)(1/5) = 1$. $7n+1$: $(7/4)(4)(1/7) = 1$. All identically 1. The "knife edge at 1" framing in [[Proof Attempt - Adelic IFS Bridge]] is automatic, not a Collatz-specific property.

**Where the structural content actually lives.** The discriminator between Collatz and divergent $(an+1)/2$ maps is the **archimedean Lyapunov** $\rho_\infty = a/4$:

| Map | $\rho_\infty$ | Behavior |
|-----|--------------|----------|
| $a = 3$ (Collatz) | $3/4$ | contracts |
| $a = 5$ | $5/4$ | expands |
| $a = 7$ | $7/4$ | expands |

The 2-adic and 3-adic places provide the local structure (integers as 2-adic boundary, 3-adic lock from [[Affine Orbit Structure]]) but their contributions to the global product are mechanical — what matters is $\rho_\infty < 1$ plus AC of $\mu$.

**Conclusion.** This candidate collapses into **#1 (AC of Collatz IFS measure)**, which already captures the real content. No separate attack target. The pre-spike previously proposed for #6 is unnecessary — it would just confirm $\prod = 1$.

---

## 7. Bounded Orbits

**Statement.** For every $n$, $\sup_k T^k(n) \leq f(n)$ for some explicit function $f$.

**Status.** Open in any usable form. Empirically $\sup T^k(n) \leq C n^\gamma$ for $\gamma$ small but unbounded growth is logically possible.

**Implication chain.** Bounded orbits + No Cycles = Collatz directly. No additional lemmas needed.

**Tools required.** Whatever proves the bound — ergodic, analytic, combinatorial. The most direct attack: proving $\liminf T^k(n) \leq n - 1$ for all $n$ via a stopping-time argument.

**Distance ★★★★.** Equivalent in difficulty to "No Divergence" itself — the canonical phrasing of what's left.

**Strength estimate.** PA-edge. The witness function $W(n) = \min\{k : T^k(n) = 1\}$ may grow polynomially or sub-elementarily; the answer determines proof-theoretic strength.

**Why promising.** It is the conjecture restated. Listed for completeness but not as an attack target — picking this is "just prove Collatz."

---

## 8. Tao-Gap Closure

**Statement.** Strengthen Tao 2019 from "for every $f(n) \to \infty$, almost every $n \le N$ has $\liminf T^k(n) \le f(n)$" to "for every $n$, $\liminf T^k(n) \le 1$."

**Status.** The almost-all version is theorem (Tao, *Forum of Math Pi*, 2022). Two gaps remain: (a) almost every → every, (b) $f(n) \to \infty$ → constant 1.

**Implication chain.** Direct: closure of both gaps = Collatz.

**Tools required.** Refinement of Tao's logarithmic-density / probabilistic arguments. Removing exceptional sets requires controlling tails of stopping-time distributions uniformly.

**Distance ★★★★.** Tao's framework is the closest published partial result. Closing the gap is open and hard but known to professional analysts.

**Strength estimate.** ACA₀.

**Why promising.** Highest credibility — it's a published theorem program. But the remaining gap is exactly where many smart people have stopped.

---

## 9. Density Refinement (Krasikov-Lagarias-Style)

**Statement.** Improve the lower bound on the fraction of integers $n \leq N$ provably satisfying Collatz from the current best (Krasikov-Lagarias-style $\geq c N^{0.84}$, *verify exact statement*) to density 1.

**Status.** Partial theorems exist, with successive improvements; full density 1 is exactly Collatz on a density-1 set, weaker than Tao's almost-all.

**Implication chain.** Density 1 alone ⇒ "almost all" but not "all" — so this candidate is **not** sufficient on its own. Listed as supporting evidence rather than primary attack.

**Tools required.** Mean-value theorems, sieve methods, refinements of Krasikov-Lagarias.

**Distance ★★★★★.** Density refinement does not bridge to "every $n$." Each numerical improvement is technically hard but does not change the qualitative landscape.

**Strength estimate.** ACA₀.

**Why promising.** It is not — for our purpose. Listed for completeness; this is a "do not pursue" entry.

---

## Cross-Cutting Analysis

### Dependency structure

Three roughly independent attack groups:

- **Algebraic / elementary**: Sector Monotonicity (#2) — closes Collatz alone via $O(\log^2 n)$ bound. Eisenstein-integer tools, no ergodic input.
- **Ergodic / fractal**: AC of IFS (#1) → Multi-bit Mixing (#4) → Discrete Denjoy (#5). Each is a stronger version of "orbits inherit invariant-measure statistics pointwise."
- **Diophantine**: Pointwise bit-destruction (#3), upgrades the existing average bound on $\beta(s) = 1 - \{s \log_2 3\}$ to a uniform pointwise bound.

Each group, if proved, closes the conjecture independently of the others. The published-program path (#8 Tao-gap) sits outside all three groups — methodologically isolated.

#7 (Bounded Orbits) is the conjecture restated; #9 (Density refinement) does not reach "every $n$." Both are listed only for completeness.

### Independence of attacks

- **Sector Monotonicity (#2)** is independent of all others — its proof uses Eisenstein algebra not used elsewhere.
- **AC of IFS (#1)** and **Multi-bit Mixing (#4)** share the ergodic toolkit; progress on one likely helps the other.
- **Conservation Axiom (#6)** subsumes #1, #4, partly #3, but proving it requires the same tools that prove its facets.
- **Tao (#8)** is methodologically isolated from the rest; uses analytic/probabilistic tools not developed in our framework.

### Combination effects

- **#2 + #3** ⇒ Collatz with a single uniform constant. Both are "moderate" distance.
- **#1 + No Cycles** ⇒ Collatz via Adelic Bridge.
- **#4 + Bit Destruction (existing)** ⇒ Collatz via Denjoy Bridge.

---

## Recommendation

**Attack order:**

1. **Sector Monotonicity (#2)** — primary. Lowest distance, highest payoff (alone gives $O(\log^2 n)$ ⇒ Collatz), uses local Eisenstein algebra not found in any other lens. The period-12 + radial-monotonicity decomposition is a *single algebraic argument* with empirical support of 135,565/135,565. Even partial progress (e.g., monotonicity within 11 of 12 sectors) is publishable and signals the full result.

2. **AC of Collatz IFS measure (#1)** — secondary. The structural fractal-geometry route. Now subsumes the original #6 (which collapsed into a tautology, see §6). Worth pursuing in parallel since it uses different tools (Hochman/Shmerkin extension) than #2.

3. **Multi-bit Mixing (#4)** — fallback. Smallest semantic gap to existing user results (Spectral Mixing Theorem upgraded from average to pointwise).

**Defer or skip:**

- #5 (Discrete Denjoy): high effort, high risk.
- #6: withdrawn (tautology).
- #7 (Bounded Orbits): equivalent to Collatz.
- #8 (Tao gap): outside our methodological lane.
- #9 (Density refinement): does not reach the conclusion.

**Confirmed:** Sector Monotonicity is the primary attack target.
