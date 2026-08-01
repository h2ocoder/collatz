# Prime Constellation Signatures — Design Spec

**Date:** 2026-06-14
**Status:** Draft (exploratory). Awaiting user review before writing-plans.

## Framing: this is an exploration, not a proof attempt

This spec operationalizes a *question*, not a claim. It builds the same kind of
artifact the repo already produces — a fingerprint, a null model, a handful of
figures, and a written-up findings note — and points it at prime constellations
(twins and their relatives) through the Collatz 2-adic / 3-adic lens. A perfectly
good outcome is **"no signal beyond the null at $N = 10^7$"**; that is reported as
honestly as a positive result. Nothing here purports to bear on the truth of the
twin prime conjecture. The reference point is Yitang Zhang's *bounded gaps*
framing — that prime *pairs* and *gaps* carry structure — borrowed as motivation,
not method (his tool was sieve theory / level of distribution, not 2-adics).

## Premise

A **prime constellation** of gap $g$ is a pair $(p,\, p+g)$ with both members
prime. This spec studies $g \in \{2, 4, 6\}$ — twins, cousins, sexy primes.

The repo already gives every integer a 2-adic **dropping signature**: its
Dropping Set $k = \text{dropping\_set}(n)$ is the residue-class-mod-$2^k$ label
established in `collatz/residues.py` (each $D_k = \bigcup_{r \in R_k}\{n \equiv r
\pmod{2^k}\}$). The organizing observation is that **the gap $g$ forces a fixed
2-adic (and, for $g=6$, 3-adic) coupling between the two members' signatures:**

| Gap $g$ | mod-4 relationship | Forced consequence | 3-adic note |
|---|---|---|---|
| 2 (twins)  | differ by 2 → one $\equiv 1$, one $\equiv 3 \pmod 4$ | always a **(fast $D_3$, slow)** couple | — |
| 4 (cousins)| differ by 4 → **same class mod 4**         | both fast $(D_3,D_3)$ **or** both slow; split at mod 8 | — |
| 6 (sexy)   | differ by 2 mod 4 → one of each            | (fast, slow) like twins | $6=2\cdot3$ adds a **3-adic** coupling: $p \equiv p+6 \pmod 3$ |

This coupling is a *theorem*, not data — it anchors the whole study. The
empirical question is whether the constellation constraint leaves any
**residual** structure in the joint signature beyond what the coupling alone
forces.

### The null model (the part that must stay honest)

A subtlety that shapes everything: for any **even** gap, the Hardy–Littlewood
singular series has **no nontrivial 2-adic factor**. Every odd residue $a
\pmod{2^k}$ is admissible, because $a$ odd $\Rightarrow a+g$ odd automatically.
Two consequences:

1. **Marginal prediction (falsifiable).** The slow member's $D_k$ distribution
   should match the *generic single-prime* distribution exactly. So the
   "generic-primes baseline" is not a mere eye test — it is a Hardy–Littlewood
   prediction. A deviation in the marginal is already a finding.
2. **Where signal can live: the joint distribution.** Given $p \equiv a
   \pmod{2^k}$, the partner $p+g \equiv a+g$ is *forced*, so $k_p$ and $k_{p+g}$
   are functionally coupled, not independent. The honest null computes that exact
   coupling over **admissible integers** $n$ (both $n,\, n+g$ odd and coprime to
   small primes), sampled by a fixed systematic stride. Hardy–Littlewood says
   prime-tuples inherit the integer residue distribution, so **any deviation of
   observed pairs from this integer null is genuine $(p, p{+}g)$ correlation**,
   not arithmetic bookkeeping.
3. **$g=6$ is a built-in cross-check.** Its 3-adic factor (sexy primes ~2× denser
   than twins; $p \equiv p+6 \pmod 3$) means the 3-adic *genus* layer should
   diverge for $g=6$ where $g=2,4$ do not. If the method sees real structure,
   that is where it must show.

The question, then: **do prime constellations distribute across Collatz dropping
signatures in a way the coupling null cannot explain — and does the 3-adic layer
behave as the $g=6$ cross-check predicts?**

## Why this approach

1. It reuses tested machinery (`prime_sieve`, `dropping_set`, `dropping_genus`)
   and mirrors the proven shape of the Prime Dropping Residues study — low risk,
   fast to stand up.
2. The forced-coupling table turns "twin primes are special" into a concrete,
   visual 2-adic statement before any sweep runs, so every figure has a baseline.
3. Studying the **joint** signature (not just the marginal) is the only place a
   constellation can carry signal the single-prime analysis cannot, given the
   marginal is pinned to the generic-prime distribution by Hardy–Littlewood.
4. The $g$ parameter makes the Zhang bounded-gaps thread literal: "does the
   Collatz signal vary with the gap?" is answered by sweeping $g \in \{2,4,6\}$.

## Scope and non-goals

**In scope:**
- Constellation enumeration for $g \in \{2, 4, 6\}$, primes up to $N = 10^7$.
- 2-adic layer: joint signature $(k_p, k_{p+g})$ and the slow-member marginal,
  vs (a) generic single-prime distribution and (b) the coupling-integer null.
- 3-adic layer: refine the signature with the Dropping Genus $(S,M,I)$
  (`dropping_genus`) and the odd-step count $s$; highlight $g=6$ vs $g=2,4$.
- Optional phase layer: internal-space $\{\log_6 x\}$ scatter, pairs vs generic.
- Five figures + a console summary ($\chi^2$ marginal, total-variation joint,
  top deviating joint cells) + a findings note.

**Explicit non-goals:**
- No analytic Hardy–Littlewood / singular-series constants computed. The 3-adic
  factor is obtained empirically from the $g=6$ cross-check — simpler and
  self-checking.
- Gaps beyond 6 (the code parameterizes $g$, so this is config, not a rewrite,
  but it is not run here).
- No claims about the twin prime conjecture, prime gaps asymptotics, or Zhang's
  theorems. Descriptive statistics only.
- No Kozyrev / Walsh / billiard / gear machinery. Adjacent but separate.
- Generalized Collatz, $5x+1$, or other variants.

## Locked decisions

| Decision | Choice | Why |
|---|---|---|
| Gaps | $g \in \{2, 4, 6\}$ | Twins, cousins, sexy — the smallest admissible family; spans both forced-coupling regimes (one-of-each vs same-class) and introduces 3-adic structure at $g=6$. |
| Prime ceiling | $N = 10^7$ | Matches the Prime Dropping Residues sweep. ~58,980 twin pairs — ample for joint histograms. |
| Dropping-set cap | $k_{\text{cap}} = 15$ | Same cap as `residues.py` work; slow members beyond it fold into a $k \ge 15$ bin. |
| Joint null | Coupling distribution over admissible integers, fixed systematic stride | Deterministic, reproducible PNGs (no RNG); HL guarantees prime-tuples inherit this distribution at the 2-adic level. |
| Stride | Coarse fixed stride over odd $n \le N$ (tuned so the null histogram is smooth; e.g. every odd $n$, or every $m$-th for speed) | Pure-Python `dropping_set` over up to $5\times10^6$ integers is the cost driver; stride trades resolution for runtime, deterministically. |
| Generic baseline | Single-prime $D_k$ distribution from the existing sieve | Already available; it *is* the HL marginal prediction. |
| 3-adic descriptor | `dropping_genus(n)` $(S,M,I)$ + new `dropping_odd_steps(n)` = count of $3x{+}1$ steps before the drop | Genus is tested and present; the odd-step count $s$ is the quantity the $2^{k-2s}6^s$ modulus is built from and is a ~10-line helper. |
| Module location | New `collatz/constellations.py` | Pair-level abstraction belongs beside `residues.py`/`dropping.py`, not inside them. |
| Script location | New `scripts/prime_constellation_signatures.py` | Matches repo convention; PNGs to `data/`. |
| Figure output | Five PNGs in `data/` (`collatz_constellation_*.png`) | Layered 2-adic → 3-adic → phase; phase figure optional. |
| Numeric type | `int` for residues/signatures; `np.float64` for ratios/χ² | Exact integer classification; float statistics. |

## Architecture

### Module layout

```
collatz/
  constellations.py                       # NEW: pairs, joint signatures, coupling null
  dropping.py                             # EXTENDED: dropping_odd_steps(n) helper (~10 lines)
scripts/
  prime_constellation_signatures.py       # NEW: sweep + 5 figures + console summary
tests/
  test_constellations.py                  # NEW: small-pair cases, forced-coupling invariants, null sanity
notebooks/
  03-prime-constellations.ipynb           # NEW (light): a runnable section mirroring the script
docs/Explorations/
  Prime Constellation Signatures.md       # NEW: findings note
data/
  collatz_constellation_coupling.png      # NEW: forced-coupling skeleton (all gaps)
  collatz_constellation_joint.png         # NEW: joint k_p × k_{p+g} heatmaps (3 panels)
  collatz_constellation_marginal.png      # NEW: headline — marginal bars + joint deviation
  collatz_constellation_genus.png         # NEW: 3-adic genus / odd-step refinement
  collatz_constellation_phase.png         # NEW (optional): internal-space phase scatter
```

`collatz/constellations.py` stays under ~250 lines.

### Components

**`collatz/dropping.py` (extend)**
- `dropping_odd_steps(n: int) -> int` — number of $3x{+}1$ (odd) steps taken
  before `n` first drops below itself; the $s$ in the $2^{k-2s}6^s$ modulus.

**`collatz/constellations.py` (new)**
- `prime_pairs(n_max: int, gap: int) -> np.ndarray` — primes $p \le n_{\max}$
  with $p+gap$ also prime (membership test against the sieve).
- `pair_signature(p: int, gap: int) -> tuple[int, int]` — $(k_p, k_{p+g})$ via
  `dropping_set`, each capped at $k_{\text{cap}}$.
- `joint_signature_counts(pairs, gap, k_cap) -> dict[tuple[int,int], int]` —
  Counter over capped $(k_p, k_{p+g})$.
- `coupling_null_counts(n_max, gap, k_cap, stride) -> dict[tuple[int,int], int]`
  — same joint histogram over admissible integers $n$ (both $n, n+g$ odd, coprime
  to a small-prime list), sampled by `stride`. Deterministic.
- `forced_coupling_table(gap, modulus) -> list[tuple]` — for each odd residue
  $a \bmod \text{modulus}$, the populated $(a, (a+g)\bmod M)$ cell with its
  fast/slow ($D_3$/non-$D_3$) tag. Pure arithmetic, no sieve.

**`scripts/prime_constellation_signatures.py` (new)**
1. Sieve primes up to $N$ once; reuse across gaps.
2. For each $g \in \{2,4,6\}$: enumerate `prime_pairs`, build
   `joint_signature_counts`, `coupling_null_counts`, and the slow-member
   marginal; pull the generic single-prime $D_k$ distribution.
3. Render five figures (below) and print the summary.

**`tests/test_constellations.py` (new)**
- Known small pairs: twins $\{3,5,7,11,13,17,29\}$-anchored, cousins
  $\{3,7,13\}$, sexy $\{5,7\}$ — `prime_pairs` agrees with brute force up to $10^4$.
- Forced-coupling invariants: every twin splits $\{1,3\} \bmod 4$; every cousin
  shares its mod-4 class; every twin/sexy pair has exactly one $D_3$ member.
- `dropping_odd_steps` against hand-checked orbits (e.g. $n=3,7,27$).
- `coupling_null_counts` is deterministic under fixed stride and sums correctly.

### Figures

1. **`collatz_constellation_coupling.png`** — forced-coupling skeleton: a mod-8
   joint-residue map per gap, fast/slow tagged. Theorem, not data; anchors the rest.
2. **`collatz_constellation_joint.png`** — three panels, observed prime pairs on
   the $k_p \times k_{p+g}$ grid. The coupling is visible (off-diagonal fast–slow
   band for $g=2,6$; near-diagonal same-class structure for $g=4$).
3. **`collatz_constellation_marginal.png`** (headline) — per gap: slow-member
   $D_k$ as grouped bars (observed vs generic-prime vs coupling null — the HL
   falsification test) beside the observed/null **ratio heatmap** on the joint
   grid (where correlation signal survives).
4. **`collatz_constellation_genus.png`** — 3-adic refinement using
   `dropping_genus` $(S,M,I)$ and `dropping_odd_steps`; $g=6$ called out against
   $g=2,4$ as the cross-check.
5. **`collatz_constellation_phase.png`** (optional, last) — internal-space
   $\{\log_6 x\}$ scatter, pair members vs generic primes; rendered only if
   layers 1–4 leave a thread worth chasing.

### Data flow

```
sieve(N) ──► prime set ──┬─► prime_pairs(g) ──► joint_signature_counts ─┐
                         │                       slow-member marginal ──┤
                         └─► generic D_k dist ────────────────────────── ┤
admissible ints (stride) ─► coupling_null_counts(g) ────────────────────┤
                                                                         ├─► 5 figures
forced_coupling_table(g) ─────────────────────────────────────────────── ┘  + summary
```

### Error handling

- **Small members ($p < 2^{k(p)}$).** A handful of small primes whose residue
  label is not yet in the asymptotic regime. Reported and counted separately;
  excluded from the χ² where the asymptotic prediction does not apply (same
  policy as the Prime Dropping Residues script).
- **Null stride too coarse.** If the null histogram is too sparse to compare, the
  script halves the stride and re-runs (bounded retries); the chosen stride is
  printed for reproducibility.
- **Capped tail.** Slow members with $k > k_{\text{cap}}$ fold into a single
  $k \ge k_{\text{cap}}$ bin in both observed and null, so the comparison stays
  apples-to-apples.

## Success criteria

- `constellations.py` exposes tested pair-enumeration and null functions reusable
  by future specs.
- The headline figure makes it possible to say, by eye, **whether any
  constellation's joint signature deviates from the coupling null**, and the
  marginal panel **whether the slow member departs from the generic-prime
  (Hardy–Littlewood) prediction**.
- The genus figure shows **whether $g=6$ behaves differently from $g=2,4$**, the
  built-in sanity check that the method tracks real 3-adic structure.
- A one-page findings note in `docs/Explorations/` with $\chi^2$ / total-variation
  per gap and the top deviating joint cells. **"No signal beyond the null at
  $N=10^7$" is a valid, informative outcome.**

## Phase D (deferred, not in this spec)

If a gap shows joint-distribution signal the coupling null cannot absorb:

- Promote the null from the 2-adic modulus $2^k$ to the combined $2^{k-2s}6^s$
  modulus (using `dropping_odd_steps` for $s$), and re-test whether the 3-adic
  refinement absorbs the deviation.
- Run the spectral / diffraction layer (treat the ordered pair-fingerprint
  sequence as a signal and look for constellation-specific Bragg peaks, reusing
  the quasicrystal machinery).
- Extend $g$ beyond 6 to test whether the signal tracks the singular series.

Phase D opens as its own spec only if this exploration concludes with measurable
signal.
