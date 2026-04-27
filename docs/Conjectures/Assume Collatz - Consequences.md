# Assume Collatz — Consequences

**Status:** Working catalog (breadth-first scan). Each lens lists what it means, key sub-questions, attack vectors, ties to existing results, and the most promising single spike to deepen next.

## Premise

Treat "Collatz is true" as an axiom and study the theory it generates. The classical model is the Riemann hypothesis: a single unproven statement spawned a literature of conditional theorems that turned out to be more useful than the hypothesis itself. We are looking for:

1. New mathematical structure forced by truth.
2. Computational artifacts (encodings, hashes, fast algorithms).
3. Statements `X ⇒ Collatz` where `X` may be easier to prove.
4. A foundational/axiomatic placement of Collatz alongside other arithmetic statements.

Each lens below is a candidate research line.

---

## Lens A — A New Universe / Metric on ℕ

### What it means

If Collatz holds, every $n \in \mathbb{N}_{>0}$ has a unique forward path to $1$ via the Syracuse map. The pair (orbit tree $\mathcal{T}$, parity word $\alpha(n)$) gives a canonical address for every integer. We can build a metric, topology, and measure on $\mathbb{N}$ where Collatz dynamics *is* the geometry — a sister to the $p$-adic line.

### Sub-questions

1. Is the parity-word symmetric-difference $d_\alpha(m, n) = 2^{-\ell(m,n)}$ (where $\ell$ is the longest common prefix of $\alpha(m), \alpha(n)$) an ultrametric on $\mathbb{N}$?
2. What is the completion of $\mathbb{N}$ under $d_\alpha$? Conjecture: the dyadic Cantor set, with the Collatz IFS measure as natural measure.
3. How does the Collatz topology compare to the $2$-adic, $3$-adic, and archimedean topologies? Which is finer? Where do they agree?
4. Is there a "Collatz Fourier transform" — a Walsh-like basis indexed by parity-word prefixes? What are its eigenfunctions for the Syracuse operator?
5. Hausdorff dimension of $(\mathbb{N}, d_\alpha)$? Should relate to similarity dimension $s = \log 2 / \log(2/\sqrt{3}) = 4.82$ from the Adelic IFS.
6. Does the metric distinguish primes? E.g., do primes have measurable density in this metric different from $1/\log n$?

### Attack vectors

- Define $d_\alpha$ formally and prove ultrametric inequality (likely immediate from prefix structure).
- Compute small-case distances: $d_\alpha(7, 9)$, $d_\alpha(27, 31)$ — look for surprises.
- Check whether the completion under $d_\alpha$ is canonically $\mathbb{Z}_2$ via Lagarias' parity vector function.
- Pull the Collatz IFS measure (Adelic Bridge) back through this metric; is it Lebesgue-equivalent on the completion?

### Ties to existing work

- [[Proof Attempt - Adelic IFS Bridge]] — already constructs the natural measure on this universe from the IFS side.
- [[Eisenstein Factorization]] — period-12 gives a discrete circle on which the universe rotates; possible quotient structure.
- [[Lattice Path Formula]] — counts orbits at each "depth," gives Hausdorff-style scaling data.
- 2-adic determinism (mod 4096 ⇒ 89% classified) — this universe is essentially the 2-adic boundary at finite resolution.

### Most promising spike

**Define $d_\alpha$ explicitly, prove it is an ultrametric, and identify its completion.** If completion = $\mathbb{Z}_2$ (or a quotient thereof), we get the universe almost for free from existing 2-adic theory, and Lens A merges with the Adelic Bridge. If not, we have a genuinely new space worth studying.

---

## Lens B — Computational Coordinates / Canonical Encoding

### What it means

Collatz-truth ⇒ every $n$ has a unique parity word $\alpha(n)$. This is a binary encoding of $\mathbb{N}$ distinct from base-2. The question: what becomes computationally cheap or expensive in $\alpha$-coordinates? Are there compression, hashing, or algorithmic gains?

### Sub-questions

1. What is the expected length of $\alpha(n)$? From the conservation law, $T(n) \approx \log_2(n) \cdot \log_2(6) \approx 2.58 \log_2 n$ — i.e., 2.58× base-2. So $\alpha$ is **not** a compression in the worst case. But is it *structurally* better?
2. Which operations on $n$ become cheap in $\alpha$-coordinates?
   - Set-membership ($n \in \text{Set}_k$?) — trivial: read first $k$ bits.
   - Orbit max, orbit sum — affine in $n$ within each subgroup of $\text{Set}_k$ ([[Affine Orbit Structure]]).
   - Addition / multiplication — almost certainly hard.
   - Primality / factoring — open.
3. Is there a "Collatz hash" — fast forward, hard reverse? Forward map $n \to \alpha(n)$ is $O(\log n)$ Collatz iterations. Reverse $\alpha \to n$ is also poly-time (compose affine maps). So the bijection is *not* one-way in the cryptographic sense — but **partial information** ($T(n)$ alone, no $\alpha$) requires search of $|\text{Set}_k|$ residue classes.
4. Compression of "structured" integers: integers $n$ whose orbit has unusually low entropy ($\alpha$ is highly compressible). Connection to Kolmogorov-style measures of integers.
5. Does the encoding give a fast factoring shortcut? (Likely no — multiplicative structure has no clean form in $\alpha$.) But: $\alpha(p \cdot q)$ vs $\alpha(p), \alpha(q)$ — anything systematic?

### Attack vectors

- Empirical: tabulate $|\alpha(n)|$ vs $\log_2(n)$ for $n \le 10^7$; histogram of compression ratios.
- Build a "Collatz dictionary": for each $\alpha$-prefix of length $\le k$, store the affine map $(slope, C)$ that takes the residue class to $\text{dest}(n)$. Use it to precompute orbit max / sum in $O(1)$.
- Define formally and benchmark: a Collatz-coordinate library where the native representation is $(s, \text{residue mod } 2^{k-s})$ instead of base-2.
- Try: is $\gcd$ cheap? Is $\bmod p$ cheap?

### Ties to existing work

- [[Affine Orbit Structure]] — orbit invariants are affine in $n$ within parity-word subgroups; this *is* the computational payoff.
- [[Lattice Path Formula]] — gives the address-space sizing.
- [[Multiplication Symmetry Theorem]] — constrains how multiplication interacts with $\alpha$ (mod-4 wall).
- [[Stopping Class]] / Stopping Signature framework — already a coordinate system.

### Most promising spike

**Build the parity-word affine dictionary up to depth $k = 16$** (covers ~89% of odd integers via 2-adic determinism) and test: which integer operations admit $O(1)$ Collatz-coordinate algorithms once this dictionary is in place? This is concrete, immediately implementable, and either produces a useful primitive or rules out the lens cheaply.

---

## Lens C — Reverse-Engineering for Proof

### What it means

Enumerate statements $X$ such that $X \Rightarrow$ Collatz, and search for an $X$ that may be easier to prove. You already have several; this lens is about completing the catalog and grading by proof-theoretic distance.

### Known and candidate $X$'s

| $X$ | Status | Distance to proof |
|---|---|---|
| Discrete Denjoy theorem (rotation number $\log_6 3$) | Open, plausible | Hard — needs new circle-map theory |
| Absolute continuity of Collatz IFS measure | Open ([[Proof Attempt - Adelic IFS Bridge]]) | One step beyond Hochman/Shmerkin (handle expanding branch $r_1 = 3/2$) |
| Sector Monotonicity (every revisit decreases) | Conjecture, 0 counterexamples [[Sector Monotonicity]] | Algebraic — could yield to bounded-orbit + period-12 argument |
| Bit-destruction net rate $> 0$ in expectation | Proved on average; need pointwise | Pointwise version is open |
| Tao 2019: almost all orbits attain almost-bounded values | Theorem | The remaining gap to "all orbits, bounded by 1" is the smallest known |
| Equidistribution of Set_3 visits under natural measure | Likely proved via CRT | Probably not enough alone |

### Sub-questions

1. Which $X$ is closest to provable in **elementary** terms (no new theory)?
2. Are there *equivalences* $X \Leftrightarrow$ Collatz (not just implications)? Equivalences identify the structural heart.
3. Cross-pollination: can two weak $X$'s combined give Collatz?
4. **Negative direction**: assume Collatz is *false* — what structural cost? If "false" forces an unrealizable configuration, contradiction proves Collatz.
5. Conway showed a slight generalization of Collatz is undecidable (FRACTRAN-encoding). What separates Collatz from undecidable cases? Identifying the separator is the right $X$.
6. Tao's gap: Tao proved Collatz on a density-1 set in a strong statistical sense. The exact statement of "what's left" is the smallest known proof distance.

### Attack vectors

- Build a literature-backed dependency graph: Lagarias 1985, Krasikov-Lagarias 2003, Sinai 2003, Tao 2019, Siegel 2026, Shakibaei Asli 2026.
- Grade each $X$ by reverse-mathematics strength (RCA₀, WKL₀, ACA₀).
- For Sector Monotonicity specifically: try to prove via Eisenstein period-12 + boundedness of revisits in radial coordinate.
- Translate Tao's gap into the Adelic IFS framework — does AC of $\mu$ close it?

### Ties to existing work

- [[Proof Attempt - Adelic IFS Bridge]], [[Proof Attempt - Denjoy Bridge]] — already this lens.
- [[Finite Propagation Theorem]] — partial bound from one specific $X$.
- [[Sector Monotonicity]], [[Bit Destruction Bound]] — concrete candidates.

### Most promising spike

**Write a one-page comparison table grading every candidate $X$ by: (a) proof-theoretic strength estimate, (b) tools needed, (c) what's already done.** The exercise itself surfaces which $X$ to attack next. Sector Monotonicity is suspected to be the lowest-hanging — it has zero counterexamples in 135K samples and a clean algebraic statement.

---

## Lens D — Foundational / Axiomatic

### What it means

Treat "Collatz is true" as an axiom in arithmetic and study its placement. Two sub-angles:

**D1. Independence.** Is Collatz independent of Peano arithmetic, in the spirit of Goodstein's theorem, Paris-Harrington, or Friedman's combinatorial principles? Such results often appear when the growth bound being verified sits at the edge of PA-provable totality. Collatz is $\Pi_2$ in the arithmetic hierarchy: $\forall n\, \exists k\, (\text{orbit reaches 1 by step } k)$. The function $n \mapsto \min k$ is the natural witness.

**D2. Conservation as axiom.** The Adelic IFS Bridge identifies a knife-edge identity $\rho_\infty \cdot \rho_2 \cdot \rho_3 = (3/4)(4)(1/3) = 1$. Conjecture: this conservation law, taken as a single number-theoretic axiom, is *equivalent* to (or directly implies) Collatz. That makes Collatz one instance of a deeper structural law, with $5n+1$, $7n+1$, etc. as deviations from the law in calculable ways.

### Sub-questions

1. What is the proof-theoretic strength of Collatz? RCA₀? WKL₀? ACA₀? Is Collatz provable in PA at all?
2. Does the witness function $W(n) = \min\{k : T^k(n) = 1\}$ grow slower than $\varepsilon_0$-recursive? (Goodstein's witness does *not* — that's why Goodstein needs ε₀-induction. If Collatz' witness sits below $\varepsilon_0$, PA suffices in principle.)
3. Is there a single conservation identity $\sum_\ell \log \rho_\ell = 0$ that (a) holds for all "Collatz-like" maps with terminating orbits, (b) fails for divergent ones? If so, Collatz becomes a corollary of the conservation.
4. What other arithmetic statements share Collatz' proof-theoretic neighborhood? Are they all "iterated map terminates"-style?
5. Does Collatz decide other conjectures? E.g., does Collatz + PA prove the equidistribution of $\{s \log_2 3\}$ on $[0,1)$ (a Weyl-style statement)?

### Attack vectors

- Bound the witness $W(n)$ in PA: is $W(n) \le 2 \uparrow\uparrow \log\log n$ provable in PA? In RCA₀?
- For each Collatz-like map (Hydra rules with rationals $r_j$): compute the adelic product $\prod_\ell \rho_\ell$. Tabulate for $\{(an+1)/2 : a = 3, 5, 7, 9, 11, \dots\}$. Cross-correlate with empirical behavior (the $5n+1$ map is *conjectured* to have divergent orbits but unproved; the $7n+1$ map has small cycles; etc.).
- State the conservation law cleanly: "If $H$ is a finite Hydra and $\prod_\ell \rho_{H,\ell} \le 1$, then $H$ terminates on $\mathbb{Z}$." Try to prove for $\le 1$, look for counterexample at $> 1$.
- Reverse mathematics: in which subsystem of second-order arithmetic does $\prod_\ell \rho_\ell \le 1 \Rightarrow$ termination first become provable?

### Ties to existing work

- [[Proof Attempt - Adelic IFS Bridge]] — D2 *is* the conservation framing; needs to be promoted from a step in a proof attempt to a standalone axiom-candidate.
- [[Eisenstein Factorization]] — period-12 as another conservation invariant (closure of orbital angles).
- Pythagorean comma identity $(3/2)^{12} / 2^7 \approx 1$ — same conservation in disguise, suggesting the law is robust under representation change.

### Most promising spike

**Compute $\prod_\ell \rho_\ell$ for a family of $(an+1)/2$-type maps with $a \in \{3, 5, 7, 9, 11, 13\}$ and compare to known empirical behavior** (3 terminates, 5 has a known divergent orbit on conjecture, 7 has cycles, etc.). If $\prod_\ell \rho_\ell \le 1$ correlates perfectly with termination, the conservation law becomes a concrete provable target.

---

## Cross-Lens Notes

- **A and D2 likely merge.** The natural measure on the Collatz universe (Lens A) is the Adelic IFS measure (Lens D2). Proving anything substantial in A probably proves something for D2.
- **B is the most independent.** Even if Collatz is unprovable in PA, the parity-word coordinates are still a useful encoding for finite-$n$ work.
- **C feeds A, B, and D.** Any structural result from A/B/D adds a new candidate $X$ to C.

## Next Move

After breadth-first scan: pick **one lens** to deepen. Recommended order based on cost-to-payoff:

1. **C first** (cheapest): the comparison table is one afternoon and tells us where the rest of our effort should go. Likely identifies Sector Monotonicity as the highest-yield target.
2. **B second** (concrete artifact): the parity-word affine dictionary is implementable code; it produces a tangible deliverable regardless of proof outcomes.
3. **A and D in parallel** (theoretical): A's ultrametric question and D's Hydra-family conservation law are both small experiments that could collapse the lens or open it up.

Drop into one of these on the user's pick.
