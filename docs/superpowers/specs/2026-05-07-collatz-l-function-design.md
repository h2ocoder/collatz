# Collatz Hecke L-Function — Design Spec

**Date:** 2026-05-07
**Status:** Locked. Implementation proceeds in auto mode.

## Premise

Construct a standard Hecke L-function $L(s, \chi)$ on $\mathbb{Q}(\omega)$ — chosen so the Collatz dynamics already proved on $\mathbb{Z}[\omega]$ become *visible* through orbit-twisted partial sums against $\chi$. We are not building a "Collatz L-function" in the sense of Collatz-derived coefficients; we are building a probe whose character is selected because the Eisenstein factorization $3n+1 = \pi\bar\pi n + 1$ gives orbit data a natural action of $\chi$.

This is the analogue of how Riemann's zeta did not have to "encode primes" — primes are the data, $\zeta(s)$ is the probe, and the connection is `Mellin(π(x)) ↔ -ζ'/ζ`. Here Collatz orbits are the data, $L(s, \chi)$ is the probe, and the connection comes from twisting orbit sums by $\chi$.

## Why Hecke on $\mathbb{Q}(\omega)$

The substrate already proved (see `docs/Conjectures/Eisenstein Factorization.md`):

- $3 = -\omega^2 \cdot \pi^2$ where $\pi = 1 - \omega$, $|\pi| = \sqrt{3}$, $\arg\pi = -30°$.
- The Syracuse step factors as $S(n) = (\pi\bar\pi n + 1)/2^\alpha$. Each step rotates the Eisenstein phase by exactly $-30°$, period 12.
- The pair $(n, \text{dest}(n))$ has Eisenstein norm $N(n + \text{dest}(n)\omega) = n^2 - n\cdot\text{dest} + \text{dest}^2$ — a Loeschian number — verified for all odd $n < 500$.
- The 3-adic lock (`Affine Orbit Structure.md`): within each subgroup of $\text{Dset}_k$, $\text{dest}(n) \equiv r_3 \pmod{3^s}$. This is exactly "ramified at $\pi$."
- The Multiplication Symmetry Theorem gives a true arithmetic symmetry under $\times 3$ (= $\times \pi\bar\pi$) — this is functional-equation flavored.

Hecke on $\mathbb{Q}(\omega)$ is the *unique* number field where all four points are simultaneously natural.

## Locked decisions

| Decision | Choice | Why |
|---|---|---|
| Field | $K = \mathbb{Q}(\omega)$, $\omega = e^{2\pi i/3}$ | Eisenstein factorization lives here |
| L-function class | Standard Hecke: $L(s, \chi) = \sum_{\mathfrak{a}} \chi(\mathfrak{a}) N(\mathfrak{a})^{-s}$ | Free Tate's-thesis machinery; user picked option A |
| Character path | Staged: $\chi_6$ first, then bespoke $\chi_{12}$ | Smoke-test rail before bespoke; user picked option (v) |
| Phase 1 character | Sextic residue $\chi_6 = (\cdot/\pi)_6$, conductor $(\pi^2)$, values in $\mu_6$ | Off-the-shelf, classical, Eisenstein reciprocity available |
| Phase 2 character | Period-12 sector character $\chi_{12}$ with $\chi_{12}((\pi)) = \zeta_{12}$, conductor at least $(\pi^3)$ + nontrivial infinity type | Tracks Eisenstein orbit phase exactly; native to the substrate |
| Primary statistic | Orbit-pair character sum $D_\chi(N) = \sum_{n \le N \text{ odd}} \chi(n + \text{dest}(n)\omega)$ | Loeschian-norm pair is the natural Eisenstein lift of "drop" |
| Secondary statistic | Stopping-time-twisted sum $T_\chi(N) = \sum_{n \le N \text{ odd}} \chi(\iota(n)) \cdot T(n)$ where $\iota$ is the trivial Eisenstein lift | Directly tests `Odd Stopping Time Spectrum` against $\chi$ |
| Lift $\iota: \mathbb{Z} \hookrightarrow \mathbb{Z}[\omega]$ | $\iota(n) = n + 0\cdot\omega$ (canonical inclusion); orbit-pair lift $\iota_2(n) = n + \text{dest}(n)\omega$ for $D_\chi$ | Two lifts; both Eisenstein-natural; statistic chooses |

## Architecture

### Module layout

New subpackage `collatz/lfunctions/`:

```
collatz/lfunctions/
  __init__.py
  eisenstein.py          # Z[ω] arithmetic: norms, primes, factorization
  characters.py          # Hecke characters: trivial, χ_3, χ_6, sector χ_12
  lseries.py             # Dirichlet series partial sums; Euler-product partial products
  orbit_lift.py          # n ↦ Eisenstein image; orbit ↦ sequence of Eisenstein points
  averaging.py           # Orbit-twisted sums D_χ(N), T_χ(N), etc.
  diagnostics.py         # Comparison: empirical orbit-sum vs L-zero predictions
```

### Components

**`eisenstein.py`** — primitive arithmetic in $\mathbb{Z}[\omega]$:
- `EisensteinInt(a, b)` representing $a + b\omega$, with `+ - * /` and conjugation.
- `norm(α) = a² - ab + b²` (Loeschian).
- `is_loeschian(n)`, `prime_factor_eisenstein(p)` for rational primes (split/inert/ramified at $p=3$).
- `eisenstein_primes_up_to(B)` — enumerate primes of $\mathbb{Z}[\omega]$ with norm $\le B$.

**`characters.py`** — Hecke character family:
- `trivial_character()`
- `cubic_residue_character()` — $\chi_3$: $\chi_3(\alpha) = \alpha^{(N(\mathfrak{p})-1)/3} \pmod{\mathfrak{p}}$
- `sextic_residue_character()` — $\chi_6 = \chi_3 \cdot \chi_2$ where $\chi_2$ is the quadratic part
- `sector_character_12()` — Phase 2 bespoke
- All with the same interface: `χ.evaluate(α) -> complex`, `χ.conductor`, `χ.is_principal`.

**`lseries.py`** — partial sums and Euler products:
- `partial_sum(χ, X, s)` returns $\sum_{N(\mathfrak{a}) \le X} \chi(\mathfrak{a})/N(\mathfrak{a})^s$
- `partial_euler(χ, B, s)` returns $\prod_{N(\mathfrak{p}) \le B} (1 - \chi(\mathfrak{p})/N(\mathfrak{p})^s)^{-1}$
- Comparison utility: empirical convergence rate.

**`orbit_lift.py`** — bridge between Collatz and Eisenstein:
- `orbit_pair(n) -> EisensteinInt`: returns $n + \text{dest}(n)\omega$.
- `orbit_eisenstein_sequence(n)`: full orbit lifted to $\mathbb{Z}[\omega]$ via the natural inclusion plus phase tracking $\pi^s$ at each Syracuse step.
- `eisenstein_sector(n) -> int in {0..11}`: returns the sector $s(n) \bmod 12$ (uses `core.oddity_count`).

**`averaging.py`** — the actual experiments:
- `D_chi(χ, N)` returns $\sum_{n \le N \text{ odd}} \chi(n + \text{dest}(n)\omega)$.
- `T_chi(χ, N)` returns $\sum_{n \le N \text{ odd}} \chi(n) \cdot T(n)$.
- `sector_chi(χ, N)` returns $\sum_{n \le N \text{ odd}} \chi(\pi^{s(n)})$ — the cleanest sector probe.
- All return both the running partial sum and the bound predicted by GRH (square-root cancellation + $\log N$).

**`diagnostics.py`** — what we report:
- For each statistic and character, plot $|D_\chi(N)|$ vs $\sqrt{N}$ and vs $N$; tabulate the ratio.
- Detect the "Collatz signal": where the orbit-twisted sum *exceeds* the GRH bound (signal that the orbit is correlated with the character beyond random).

### Data flow

```
n (odd integer)
  → core.dest(n), core.oddity_count(n)        # existing
  → orbit_lift.orbit_pair(n) ∈ Z[ω]
  → characters.χ.evaluate(...) → complex value
  → averaging.D_chi sum
  → diagnostics: compare with √N, log² N
```

Phase 2 (sector character) extends `orbit_lift.orbit_eisenstein_sequence` to track $\pi^s$ at each step, but the call interface stays the same.

### Error handling

Internal arithmetic only — no user-input boundary, no external services. Trust the existing `collatz.core` library and `fractions.Fraction` for exact arithmetic. The only thing that *can* go wrong is character-evaluation at a prime where the conductor is non-coprime: handle by returning $0$ (standard Hecke convention) and assert in tests that this happens at the expected places.

### Testing

- `tests/test_eisenstein.py`: $\pi\bar\pi = 3$, $\omega^3 = 1$, norm-multiplicativity on 100 random pairs.
- `tests/test_characters.py`: $\chi_6$ trivial on units (must be 1 on $\{\pm 1, \pm\omega, \pm\omega^2\}$); $\chi_6(\pi)^6 = 1$; $\chi_6$ multiplicative on coprime pairs.
- `tests/test_lseries.py`: trivial-character $L(s, \chi_0)$ partial sum agrees with the partial Euler product at $s = 2$ to 4+ digits; trivial-character partial sum matches the known value of $\zeta_K(2) = \tfrac{4\pi^4}{81\sqrt{3}}\cdot(?)$ (actual constant looked up at implementation time and frozen as a test vector).
- `tests/test_orbit_lift.py`: `orbit_pair(n)` has Loeschian norm for first 500 odd $n$ (matches Eisenstein-Factorization doc claim).
- `tests/test_averaging.py`: trivial character recovers $\sum N(\text{pair})^0$ = count; smoke test on small $N$.

## Verification plan

After implementation:

1. **Sanity layer.** Reproduce `Eisenstein Factorization.md` numbers exactly:
   - $\pi^{12} \in \mathbb{R}$ (12-fold rotation closes).
   - All $(n, \text{dest})$ pairs Loeschian for odd $n < 500$.
   - $L(s, \chi_6)$ has the expected functional equation (Gauss-sum check).

2. **Phase 1 experiments.** Compute $D_{\chi_6}(N)$ and $T_{\chi_6}(N)$ for $N = 10^k$, $k = 3..6$. Compare $|D_{\chi_6}(N)|$ to $\sqrt{N \log N}$ (the GRH-predicted square-root cancellation). Two outcomes are interesting:
   - **(a)** $|D| \sim \sqrt{N}$: orbit-twisted destination is "random" in $\chi_6$'s eyes — confirms expected null hypothesis.
   - **(b)** $|D|$ much smaller (e.g. $O(\log N)$) or much larger ($\Omega(N^{1-\epsilon})$): orbit-twisted destination has *correlation* with $\chi_6$. This is the signal we'd want for "the L-function sees Collatz."

3. **Phase 1.5 cross-check.** Compute $D_{\chi_6}$ split by Dropping Set $\text{Dset}_k$. The Multiplication Symmetry Theorem predicts the $\times 3$ map preserves the $|D|$ distribution; verify.

4. **Phase 2 build & repeat.** Once Phase 2 character $\chi_{12}$ is implemented, compute the same statistics. The prediction: $D_{\chi_{12}}(N)$ should behave very differently from $D_{\chi_6}(N)$, because $\chi_{12}$ resolves the full sector dynamics. Specifically, if Sector Monotonicity is true, then $D_{\chi_{12}}$ should have a *bias* — orbit pairs concentrate on certain sectors with positive frequency.

5. **Findings report.** Whatever happens, write up:
   - Magnitudes and rates for each statistic at each character.
   - Where we exceed / fall below the GRH bound.
   - Whether any structural prediction (Sector Monotonicity, Multiplication Symmetry, 3-adic lock) is *visible* in the L-function picture.

## What success looks like

Phase 1 success: working machinery that produces $D_{\chi_6}(N)$, $T_{\chi_6}(N)$, $\text{sector}_{\chi_6}(N)$ at $N = 10^5$ in under a minute, with all sanity tests passing.

Phase 2 success: $\chi_{12}$ implemented; the orbit-twisted sums show *systematic deviation* from $\sqrt{N}$ behavior, in a direction consistent with one of the existing conjectures (Sector Monotonicity is the headline candidate).

Stretch: identify a concrete "Collatz $\Rightarrow$ statement about zeros of $L(s, \chi)$" or vice versa. This is the actual long game; Phase 2 is the *minimum* work needed to even ask whether such a connection exists.

## Open questions (to be resolved during implementation)

1. **Conductor for Phase 2 $\chi_{12}$.** The unit group of $\mathbb{Z}[\omega]$ is $\langle -\omega \rangle$ of order 6. To make $\chi_{12}((\pi)) = \zeta_{12}$ well-defined on principal ideals, we need $\chi_{12}$ trivial on units — *but* a pure infinity-type character of weight $k = 6m$ gives $\chi(\pi)$ values in $\mu_2$ only. Need to add a ramified part at $(\pi)$ to bump the resolution to $\mu_{12}$. Concrete conductor: $(\pi^3)$ should suffice (will verify; if not, escalate to $(\pi^4)$ or $(2 \cdot \pi^3)$).

2. **Whether Phase 2 character is unique.** Multiple $\chi_{12}$'s satisfy the constraints; pick the one with smallest conductor. If multiple at same conductor, prefer the one whose Gauss sum is real.

3. **Computational scaling.** Phase 1 should hit $N = 10^6$ in pure Python with `fractions.Fraction` and `cmath`. If not, drop to floating-point complex inside the character (errors stay $O(\epsilon \log N)$, fine for the magnitude comparisons we care about). No need for a numpy port unless we hit $N = 10^7$.

## Build sequence (auto-execute)

1. `collatz/lfunctions/eisenstein.py` + tests.
2. `collatz/lfunctions/characters.py` (trivial, $\chi_3$, $\chi_6$) + tests.
3. `collatz/lfunctions/lseries.py` + tests.
4. `collatz/lfunctions/orbit_lift.py` + tests.
5. `collatz/lfunctions/averaging.py` + tests.
6. `notebooks/19-l-function-phase-1.ipynb` — Phase 1 experiments and report.
7. **Findings report** to user.
8. (Conditional on Phase 1 results) Phase 2 character + Phase 2 notebook.

## Connections

- `Eisenstein Factorization.md` — primary substrate.
- `Affine Orbit Structure.md` (3-adic lock) — predicts character ramification at $(\pi)$.
- `Multiplication Symmetry Theorem.md` — predicts a real arithmetic symmetry that should appear in $D_\chi$ as $\times 3$ invariance.
- `Sector Monotonicity.md` — Phase 2 target; predicts $D_{\chi_{12}}$ has structure beyond GRH-random.
- `Proof Attempt - Adelic IFS Bridge.md` — the AC-of-$\mu$ conjecture. Long shot: $\hat\mu(\xi)$ decay might be readable from $L(s, \chi_{12})$.
- `hilbert-polya.md` — already has critical-circle $(4/3)^{1/3}$. Worth checking whether $L(s, \chi_{12})$ zeros sit on that circle in any limit.
