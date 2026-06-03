# Prime Distribution Across Dropping Sets — Design Spec

**Date:** 2026-06-02
**Status:** Draft. Awaiting user review before writing-plans.

## Premise

Each Collatz Dropping Set $D_k$ — the integers whose stopping time equals exactly $k$ — is, by repeated application of the 2-adic Collatz dynamics, a finite **union of residue classes mod $2^k$**. This is the **arithmetic form** of $D_k$: a finite Diophantine description
$$
D_k = \bigcup_{r \in R_k} \{\, n : n \equiv r \pmod{2^k} \,\},
$$
where $R_k \subset \{0,1,\dots,2^k-1\}$ is a computable residue set. Docs reference this fact (`docs/00-Index.md:36`) but no code currently exposes $R_k$ or uses it as a hypothesis-testing scaffold.

A prime $p > 2$ is by definition coprime to $2^k$, so its residue mod $2^k$ lies in one of the $2^{k-1}$ **odd residues**. **Dirichlet's theorem on arithmetic progressions** is the natural null model: primes equidistribute across the $\varphi(2^k) = 2^{k-1}$ odd residues mod $2^k$. The expected number of primes $\le N$ falling in $D_k$ is therefore
$$
\mathbb{E}_{\text{Dirichlet}}[\pi(N; D_k)] \approx \frac{|R_k \cap \text{odd}|}{2^{k-1}} \cdot \pi(N).
$$
Any deviation from this prediction — at the $D_k$ level, or finer at the individual-residue level inside $D_k$ — is **structural signal**: a property of Collatz that goes beyond the 2-adic equidistribution of primes.

The question this spec operationalizes: **does Collatz organize primes into its dropping-set hierarchy in a way that the Dirichlet null cannot explain?**

## Why this approach

Three reasons this is the right next step in this repo:

1. The arithmetic-form claim is asserted in docs but never used as code. Writing $R_k$ explicitly turns a verbal claim into a falsifiable function that other explorations (Kozyrev, billiards, gears) can also reuse.
2. The existing `notebooks/02-prime-class-characters.ipynb` plots prime counts per $D_k$ as raw bars with no null model. The result is purely descriptive — any peak or trough is unfalsifiable without a baseline. A Dirichlet baseline gives us "expected versus observed," which is what we actually want to look at.
3. Dirichlet's theorem is the **strongest tool we have for the residue-level question**, and the residue level is finer than any current visualization. If signal exists below the $D_k$ aggregate — for example, certain residue classes in $D_k$ persistently over/under-represented — we will only see it by going down to residues.

## Scope and non-goals

**In scope (this spec):**
- The 2-adic arithmetic form: residue classes mod $2^k$ for each $D_k$ up to $K_{\max} = 15$.
- Dirichlet null model derived from $R_k$.
- Empirical sweep of primes up to $N = 10^7$ with classification into $D_k$ and into residue class within $D_k$.
- Three figures: (i) residue-form table, (ii) observed vs. Dirichlet bar chart per $D_k$, (iii) per-residue heatmap inside each $D_k$ up to $k \le 10$.

**Explicit non-goals (out of scope for this spec):**
- The 3-adic refinement (combined modulus $2^{k-2s} \cdot 6^s$). Phase D follow-up if Phase A–C surface something interesting.
- Stopping classes (Paper 2 terminology). This stays in Paper 1 / dropping-set territory.
- Anything touching Kozyrev wavelets, Walsh spectra, billiards, or prime-gear engagement. Adjacent but separate.
- Generalized Collatz, $5x+1$, or other variants.
- Theoretical proofs about Dirichlet rates of convergence per $D_k$. The χ² statistics are descriptive, not asymptotic.

## Locked decisions

| Decision | Choice | Why |
|---|---|---|
| Maximum dropping set | $K_{\max} = 15$ | Residues mod $2^{15} = 32{,}768$. With $N = 10^7$ giving $\pi(N) \approx 6.2 \times 10^5$, we expect $\sim 38$ primes per odd residue class — enough for meaningful per-residue heatmaps without thinning to noise. |
| Prime ceiling | $N = 10^7$ | Sieve of Eratosthenes fits in $\sim 10$ MB; sweep classifies in seconds. Two orders of magnitude beyond the existing notebook 02 baseline of $10^4$. |
| Adic refinement | 2-adic only in this spec | The 3-adic split (combined modulus $2^{k-2s} \cdot 6^s$) is a documented refinement but adds substantial machinery. Defer to Phase D. |
| Null model | Dirichlet equidistribution across $\varphi(2^k)$ odd residues | The unique-up-to-rescaling theorem for primes in arithmetic progressions mod $2^k$. No tunable parameter. |
| Numeric type | Python `int` for residues; `np.float64` for ratios and χ² | Residue computations are exact integer arithmetic. χ² is float. |
| Sieve | Plain Eratosthenes sieve on `np.bool_` array, single-threaded | $N = 10^7$ runs in well under a second. No need for segmented sieve or external dependency. |
| Module location | New module `collatz/residues.py` | The arithmetic-form function `dropping_set_residues(k)` belongs alongside `dropping.py`, not inside it — different abstraction level (residue enumeration vs. per-integer classification). |
| Script location | New script `scripts/prime_dropping_residues.py` | Matches repo convention (`collatz_2adic_potential.py`, `collatz_billiard_sawtooth.py`, etc.). Single PNG output convention. |
| Notebook integration | Append cells to `notebooks/02-prime-class-characters.ipynb` | Do not rewrite existing exploration cells; extend with a new section "Arithmetic Form and Dirichlet Null." |
| Figure output | Three PNGs in `data/` | `collatz_prime_dropping_residues_form.png`, `collatz_prime_dropping_observed_vs_dirichlet.png`, `collatz_prime_dropping_residue_heatmap.png`. |
| Test depth | Validate $R_k$ for $k \le 12$ against brute-force enumeration of $\{0,\dots,2^k-1\}$ classified via `dropping_set`. Spot-check $k = 13, 14, 15$ on random samples. | Brute force costs $2^{12} = 4096$ classifications — cheap. Full $2^{15}$ takes longer but is still tractable; we use it as an end-to-end sanity in the script, not a unit test. |

## Architecture

### Module layout

```
collatz/
  residues.py            # NEW: dropping_set_residues(k), dirichlet_prediction(k, N)
scripts/
  prime_dropping_residues.py   # NEW: sieve + classify + plot
tests/
  test_residues.py             # NEW: brute-force validation up to k=12
notebooks/
  02-prime-class-characters.ipynb   # EXTENDED: new section appended
data/
  collatz_prime_dropping_residues_form.png            # NEW
  collatz_prime_dropping_observed_vs_dirichlet.png    # NEW
  collatz_prime_dropping_residue_heatmap.png          # NEW
```

### Components

**`collatz/residues.py`**

- `dropping_set_residues(k: int) -> frozenset[int]`
  Returns the set $R_k$ of residues $r \in \{0, \dots, 2^k - 1\}$ such that every $n \equiv r \pmod{2^k}$ (with $n$ large enough that the next $k$ steps don't dip below the sieve floor) has $\text{dropping\_set}(n) = k$. Implementation: for each $r$, classify $r + 2^k$ (which guarantees $n > 2^k$ so the stopping-time logic is well-defined) and accept iff its dropping set is $k$. Cached by `functools.lru_cache`. Validity domain: $k \ge 1$.
- `dropping_set_residue_table(k_max: int) -> dict[int, frozenset[int]]`
  Convenience: precomputes $R_1, \dots, R_{k_{\max}}$.
- `dirichlet_prediction(k: int, prime_count_upper: int) -> float`
  Returns $|R_k \cap \text{odd}| / 2^{k-1} \cdot \pi(N)$. The caller provides $\pi(N)$; this module does not depend on the sieve.
- `coprime_residues(k: int) -> frozenset[int]`
  Returns $R_k \cap \{r : r \text{ odd}\}$. Pure derivation from `dropping_set_residues`.

**`scripts/prime_dropping_residues.py`**

1. Sieve primes up to $N = 10^7$ via Eratosthenes.
2. Build residue tables $R_1, \dots, R_{15}$ via `dropping_set_residue_table(15)`.
3. Classify each prime $p$: compute $k(p) = \text{dropping\_set}(p)$ and its residue $p \bmod 2^{k(p)}$.
4. Aggregate: observed count per $D_k$; observed count per (k, residue).
5. Render three figures:
   - **Residue-form table** — heatmap-style grid: rows $k$, columns $r$ (capped at $r < 2^{10}$ for visibility), cell colored iff $r \in R_k$. Captioned with $|R_k|$ and $|R_k \cap \text{odd}|$ per row.
   - **Observed vs. Dirichlet** — grouped bars per $D_k$: predicted (gray) vs. observed (color). Y-axis log if dynamic range warrants. Annotate χ² and log-ratio per bar.
   - **Per-residue heatmap** — for each $k \in \{5, 7, 9, 11, 13\}$, a strip with one cell per odd residue $r \in R_k$, colored by observed prime count. Same color scale across strips so structural over/under-representation is visually comparable. Skips $k \le 4$ where $|R_k \cap \text{odd}|$ is too small for a meaningful strip (reported as text instead).

**`tests/test_residues.py`**

- `test_R_k_matches_brute_force[k=1..12]`: for each $k$, verify $r \in R_k \iff \text{dropping\_set}(r + 2^k) = k$.
- `test_R_k_partitions_modulus`: union $\bigcup_k (R_k + 2^k \mathbb{Z})$ covers all positive integers exactly once (test up to $n = 4096$ to bound $k \le 12$).
- `test_dirichlet_prediction_matches_density`: for a synthetic uniform random distribution of "primes" across odd residues mod $2^{10}$, the prediction matches observed within Poisson noise.

### Data flow

```
sieve (N=1e7) ──► list[prime] ──┐
                                 ├──► classify ──► {k: {r: count}}
R_k table (k=1..15) ─────────────┘                         │
                                                            ├──► observed_vs_dirichlet plot
dirichlet_prediction per k ─────────────────────────────────┤
                                                            └──► residue_heatmap plot
R_k table ─────────────────────────────────────────────────────► residue_form plot
```

### Error handling

Two ways things can go wrong; both are caught explicitly:

- $R_k$ at large $k$ might depend on the choice of representative. Mitigation: `dropping_set_residues` documents and tests that $r$ and $r + 2^k$ classify identically iff the orbit's $k$-step window stays above the threshold. The brute-force test at $k \le 12$ pins this down for the regime we care about.
- A prime $p < 2^{k(p)}$ (i.e., a small prime) might have residue $p$ itself, not "$p$ mod $2^{k(p)}$" in the asymptotic sense. Mitigation: such primes are at most $\sim 2^{15} \approx 32{,}768$ out of $\sim 6.2 \times 10^5$ total ($\sim 5\%$). The script reports their contribution separately and excludes them from the Dirichlet χ² (where the asymptotic prediction does not apply).

## Success criteria

- `dropping_set_residues(k)` is exposed, cached, tested, and used by both the script and any future spec.
- Observed-vs-Dirichlet figure makes it possible to say, by eyeball, **which $D_k$ deviate from the Dirichlet null and which don't.**
- Per-residue heatmap makes it possible to see, by eyeball, **whether deviation (if any) is uniform across $D_k$ or concentrated in specific residues.**
- A written-up finding in `docs/explorations/` (one-pager) summarizing observed vs. predicted, with χ² per $D_k$ and three example residues that deviate most from Dirichlet. The finding may be "no structural signal beyond Dirichlet at $N = 10^7$" — that is a valid and informative outcome.

## Phase D (deferred, not in this spec)

If Phase A–C find signal, Phase D promotes the analysis from 2-adic to combined 2-adic × 3-adic:

- Replace modulus $2^k$ with $2^{k-2s} \cdot 6^s$ where $s$ is the number of $3x+1$ steps inside the $k$-step drop.
- Replace Dirichlet on $\varphi(2^k)$ classes with Dirichlet on $\varphi(2^{k-2s} \cdot 6^s)$ classes.
- Look for whether 3-adic structure absorbs the 2-adic deviation (which would say "the 2-adic-only model was incomplete, not that Collatz preferentially picks primes").

Phase D is opened as a new spec only if Phase C concludes with measurable signal.
