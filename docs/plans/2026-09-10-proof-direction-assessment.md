# Proof Direction Assessment — 2026-09-10

**Purpose.** Audit what this repo has actually established, place it against the published frontier, and pick the direction with the best chance of producing *rigorous* progress toward the Collatz conjecture.

**Bottom line.** The repo's exact machinery (affine orbit structure, dropping-set alphabet, backward inversion, the $F_d$ countdown family) is genuine and well built. Its two proof programs both stall at the same wall — statements about *measure* (almost all $n$) do not become statements about *every* $n$ — and the one document claiming to cross that wall does so invalidly. The direction with the best rigorous yield is the one the repo has not yet tried: **turn the dropping-set alphabet into a Krasikov–Lagarias difference-inequality system and attack the density exponent** (currently $x^{0.84}$, unchanged since 2003). It is the only frontier where the repo's Tier-A assets map onto a method that has actually produced theorems, and where progress is measurable.

---

## 1. Audit of claimed results

| Claim (doc) | Repo status | Audit verdict |
|---|---|---|
| Affine orbit structure, 3-adic lock, lattice-path counts, Eisenstein period 12 | Proved | **Correct.** Standard-flavoured (Terras parity-vector algebra) but cleanly done and exact to $k=37$. |
| $F_d(m)=(2^d-3)m-1$, $F_d(m_2)=3F_d(m)/2^d$ ([[Three-Bit Countdown]]) | Proved | **Correct and the best algebra in the repo.** It is the linearisation about the fixed point $1/(2^d-3)$ of the depth-$d$ branch, i.e. 2-adic distance to the period-$d$ periodic point. Generalises to every periodic word (Bernstein–Lagarias periodic points). Bounds *runs* of a fixed word by $v_2/d$; says nothing about mixed words. |
| One-Bit Lemma: no orbit stays $\equiv 3 \pmod 4$ forever | Proved | **Correct but trivial** ($v_2(m+1)$ drops by 1 per step), and — as the Denjoy Bridge itself concedes in "The Growth Problem" — **insufficient**: a drop is relative to the *current* value, which may already exceed the start. `path-to-proof.md` §"Single Remaining Question" still presents it as sufficient; that paragraph is wrong. |
| Front 1 (no cycles) COMPLETE via "second moment / Parseval, $|N-W/g|\le\sqrt{W/g}$" | Proved | **Not a proof.** The inequality is asserted without derivation; it is the standard deviation of the *random model* for $C_w \bmod g$, i.e. the very equidistribution one would need to prove. Non-convergent $(S,E)$ are also never handled. The rigorous frontier is Hercher (2023): no cycles with $\le 91$ odd-run blocks, resting on Barina's verification to $2^{71}$ and Baker-type bounds. The repo's $(41,65)$ MITM is subsumed by Simons–de Weger/Hercher. |
| Sector Monotonicity (Lens C's ★★ top pick) | "0 violations, $n<50{,}000$" | **Dead.** No verification code exists in the repo. Under the reading "value at each drop, sector = that drop's oddity mod 12", the values are consecutive dropping destinations, which decrease *by definition* — the conjecture is a tautology and the claimed "$\le \log_2 n$ visits per sector" does not follow (strictly decreasing integers give $\le n$, not $\le \log n$). Under the reading "cumulative Syracuse count mod 12", it is **false**: 14,244 violations among odd $n<50{,}000$; $n=27$ violates at $s=12$ ($27\to 233$), and $2^{20}-1$ rises to $136{,}048{,}895$. |
| Adelic IFS Bridge Step 6: exceptional set has dimension 0, $\mathbb{N}$ is countable, hence $\mathbb{N}$ avoids it | Claimed | **Invalid.** Every countable set has dimension 0; a dimension-0 set can contain all of $\mathbb{N}$. This is the almost-all→all barrier restated as if crossed. Lens C §6 already withdrew the adelic "knife edge" as the tautology $\prod_\ell |x|_\ell = 1$. |
| Finite Propagation Theorem | "Corollary: every $n$ reaches 1" | **Not a proof**: four incompatible bounds, a self-flagged sign error left in the text, and a counting step that treats mod-$64$ window conditions as constraints on $1.92n$ distinct bit positions. |
| Bit Destruction: $\beta(s) > c/s$ by Roth | Proved | Roth gives $c_\varepsilon/s^{1+\varepsilon}$ with an *ineffective* constant; use Baker/Rhin for effective bounds. Table row $s=53$ is wrong ($53\log_2 3 = 84.003$, $\beta=0.997$); the true slow continuation is $s=94, 306$. |
| AEH ⟹ Three-Bit Countdown (conditional theorem) | Proved conditional | The conditional proof is fine, but AEH as needed requires the additive error term $<1$ in initial segments of length $\approx(4/3)^n$ — i.e. "the minimal avoider behaves like the random model". That is very close to the statement it is meant to prove, verified only to $n\le 8$. Treat as heuristic, not a target. |
| Prime / constellation / factorization signals | Null | **Correct and now complete**: primes are Dirichlet-generic ([[Prime Dropping Residues]]); factorization acts only through the 2-adic discrete log ([[Prime Factorization and Dropping Rate]]). |
| L-function / zeta / DQPT / quasicrystal / SHG explorations | Various | Honest, self-correcting instrumentation. None produces a statement about individual orbits; the Sturmian skeleton is universal across $qx+1$ and therefore not the content of the conjecture (the repo's own conclusion). |

**One obstacle, three costumes.** Spectral gap, AC of the IFS measure, Denjoy density, AEH, "almost all" via Terras — every route delivers a *measure* statement. The conjecture is a *pointwise* $\Pi_2$ statement, and Terras' theorem (every finite parity word is realised by a residue class) guarantees that no argument local in the 2-adic topology can force a drop. The only pointwise tools that have ever worked on Collatz are Diophantine (Baker-type bounds, for cycles). For divergence there is no known pointwise tool at all. Any plan must be honest about this.

## 2. The published frontier (as of 2026-09)

- **Verification:** all $n < 2^{71}$ converge (Barina, *J. Supercomputing* 2025; arXiv 2602.10466 gives a faster checker).
- **Cycles:** no non-trivial cycle with $m\le 91$ odd runs (Hercher, arXiv 2201.00406 / JIS 2023). Length bounds $\sim 10^{11}$ follow from $2^{71}$ plus continued fractions of $\log_2 3$.
- **Density:** $\#\{n\le x : n \to 1\} \ge x^{0.84}$ (Krasikov–Lagarias 2003, difference inequalities mod $3^k$; earlier $x^{0.81}$ Applegate–Lagarias 1995, $x^{3/7}$ Krasikov 1989).
- **Almost all:** almost all $n$ (logarithmic density) reach below any $f(n)\to\infty$ (Tao 2019/2022). Upgrading logarithmic to natural density is open.
- **Near-conjugacy:** $T(x)=\{\log_6(x+\tfrac15)\}$ rotates by $\log_6 3$ with $|\varepsilon|\le 0.2749$ (Shakibaei Asli, arXiv 2601.04289) — the repo's PPR(x, 6). The paper itself says this does not resolve the conjecture.

## 3. Ranking of directions

| # | Direction | Rigorous? | Novel vs literature? | Tractable here? | Verdict |
|---|---|---|---|---|---|
| **1** | **Density exponent via the dropping-set alphabet** (Krasikov–Lagarias in the $(k,s,C)$ basis) | Yes | Yes — nobody has run KL in the first-return basis | Yes: `affine.py`, `residues.py`, `lattice_paths`, backward inversion already exist | **Pursue.** |
| 2 | Effective / natural-density version of Tao's theorem, using the repo's residue-transition chain (the "3-adic lock" *is* Tao's Syracuse random variable) | Yes | Incremental | Heavy analytic machinery; numerics help little | Second choice; read Tao §1–3 first. |
| 3 | Cycles: push Hercher's $m\le 91$ with the MITM code + $2^{71}$ | Yes | Marginal | Computational | Only if compute is cheap; not a proof direction. |
| 4 | $F_d$ family → general periodic-word ledger (2-adic distance to Bernstein–Lagarias periodic points) | Yes | Mostly known | Easy | Worth a short write-up as a clean theorem; no proof leverage. |
| 5 | AEH / Three-Bit Countdown | Conditional | — | — | Keep as heuristic model; do not invest as a proof target. |
| 6 | Sector Monotonicity, Finite Propagation, Adelic Bridge, Denjoy density | No | — | — | Retire; mark superseded. |
| 7 | Prime factorization / constellation signals | Done | — | — | Closed (null, with exact explanation). |

## 4. The recommended program

**Target theorem.** $\#\{n\le x : \text{orbit of } n \text{ reaches } 1\} \ge x^{\theta}$ with $\theta > 0.84$.

**Why the dropping-set basis might beat the single-step basis.** Krasikov–Lagarias track counts of tree nodes in residue classes mod $3^k$ under the *single-step* backward map $n\mapsto 2n$, $n \mapsto (2n-1)/3$, and derive linear difference inequalities whose growth rate is bounded by an eigenvalue problem; the exponent is limited by how much 2-adic/3-adic correlation the inequalities can see. The repo's dropping dictionary packages the 2-adic side *exactly*: a drop of type $(k,s,C)$ is one residue class mod $2^k$ and one 3-adic condition mod $3^s$ ([[Nested Dropping Sets]]: coverage $1/3, 1/9, 2/27, 3/81, 7/243,\dots$; forward mass $\sum w_s 2^{-e_s} = 1$ exactly; backward cover $\sum w_s 3^{-s} = 1.69$). Running the same inequality machinery on the first-return map should absorb correlations that the single-step system must bound crudely. Whether it actually improves $\theta$ is an empirical question with a definite answer — the eigenvalue of the resulting system.

**Milestones.**
1. *Reproduce KL.* Implement their inequality system (mod $3^k$, small $k$) and recover $\theta\approx 0.81$–$0.84$. This calibrates the tooling and the exact statement (the repo's Lens C flags "verify exact statement" — do that first).
2. *Dropping-set basis.* Build the backward tree in the $(k,s,C)$ alphabet: node counts by size and by residue mod $3^{s_{\max}}$, with the exact preimage map $n=(2^{k-s}d-C)/3^s$. Derive the analogous difference inequalities; compute the growth exponent numerically for increasing alphabet depth.
3. *Decide.* If $\theta$ exceeds $0.84$ at any finite depth, write the proof (the inequalities are elementary; the work is bookkeeping and the eigenvalue bound). If it plateaus at or below $0.84$, the negative result is itself informative and cheap.

**Sub-project with guaranteed output (do alongside).** Write up the $F_d$ identity in its general form: for a periodic parity word $w$ with $(S,E)$ and constant $C_w$, the quantity $G_w(m) = (2^E-3^S)m - C_w$ satisfies $G_w(T^w m) = 3^S G_w(m)/2^E$, so consecutive repetitions of $w$ are bounded by $v_2(G_w(m))/E$. This is the exact content of "2-adic closeness to the periodic point $C_w/(2^E-3^S)$" and unifies One-Bit, Two-Bit, Three-Bit and Logarithmic Escape into one lemma.

## 5. Repo hygiene (recommended, not done here)

- Mark `Sector Monotonicity.md`, `Finite Propagation Theorem.md`, `Proof Attempt - Adelic IFS Bridge.md` as superseded/refuted; add the $n=27$ counterexample.
- Change Front 1 status in `path-to-proof.md` and the Denjoy Bridge from PROVED to *heuristic beyond $K=106$*; cite Hercher for the rigorous bound.
- Fix the $s=53$ row in `Bit Destruction Bound.md`.
- Retire the "One-Bit Lemma suffices" paragraph in `path-to-proof.md`; the Summary doc's own reduction ("bounce termination ≡ Collatz") is the honest one.

## Sources

- Barina, verification to $2^{71}$: https://pcbarina.fit.vutbr.cz/ and https://www.fit.vut.cz/research/result/c197809/.en
- Hercher, no $m$-cycles with $m\le 91$: https://arxiv.org/abs/2201.00406
- Shakibaei Asli, near-conjugacy to a circle rotation: https://arxiv.org/abs/2601.04289
- Faster verification algorithm (2026): https://arxiv.org/html/2602.10466v1
- Krasikov–Lagarias, *Bounds for the 3x+1 problem using difference inequalities*, Acta Arith. 109 (2003).
- Tao, *Almost all orbits of the Collatz map attain almost bounded values*, Forum Math. Pi 10 (2022).

---

## Execution log (2026-09-10, same day)

Milestones 1–3 executed; see [[Density Exponent]] and `scripts/density_exponent_kl.py`.

- **Milestone 1 (reproduce KL):** done. Power iteration + bisection on the nonlinear Perron root of the KL map reproduces Table 2 to six decimals at $k=2,5,9,11$.
- **Milestone 2 (dropping-set basis):** done, **negative**. The DROP system is below KL at every $k\ge 3$ (0.813 vs 0.830 at $k=10$), exactly as the min-of-sums vs sum-of-mins comparison predicts. The alphabet does not absorb 3-adic information loss any better than single steps.
- **Milestone 3 (decide):** the exponent moved anyway, by pushing the *unchanged* KL system past $k=11$: certified $\gamma = 0.853$ ($k=12$), $0.863$ ($k=13$), $0.872$ ($k=14$), $0.881$ ($k=15$), $0.889$ ($k=16$), $0.897$ ($k=17$), $0.903$ ($k=18$), each with an exact integer certificate of LP feasibility. The gap $2-\lambda_k$ decays geometrically (ratio $0.934\pm0.002$ for $k=9..17$); predictions for $k=17,18$ made before the runs held to $3\times10^{-4}$ and $6\times10^{-4}$, while a $1/k$ alternative was rejected at $k=18$. Conjecture: $\lambda_k\to 2$, i.e. $\pi_a(x)\ge x^{1-\varepsilon}$. Section 4's premise (the basis) was wrong; its target ($\theta>0.84$) was reached by the method's own scaling.

**Next steps on this front:** (i) $k=19$ needs ~18 GB, beyond this machine; (ii) fit $\gamma_k$ vs $k$ to estimate the method's limit; (iii) write the certificate check in a form a referee can rerun (it already is a 40-line function); (iv) check the KL Theorem 2.2 proof of the advanced-term elimination before publishing.
