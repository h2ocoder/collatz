---
tags: [pinball, mirror-map, fibonacci, experiments, prior-art]
status: verified
created: 2026-09-19
jira: SCRUM-30
---

# Mirror Experiments

Fourteen experiments on the mirror table of [[The Mirror Table]] (m → 3m − 1 for odd m, m → 3m/2 for even m), a proof of the Fibonacci law, and a literature check.

Run: `python -X utf8 scripts/mirror_experiments.py` (about 2 minutes). Raw numbers: `results/mirror_experiments.json`.

Labels: **Proved**, **Verified** (computed), **Negative** (the experiment showed less than hoped), **Open**.

## Summary table

| # | Question | Result |
|---|---|---|
| E1 | Does a 3-adic register on positive orbits give a new conservation law? | **Negative.** It restates the known one: halvings at the first drop = ⌈s·log₂3⌉, 99,999 of 99,999. |
| E2 | Where do the old cycles −1, −5, −17 sit? | Scattered: 2 members on 1 ray, 5 on 3 rays, 18 on 11 rays. All ages are 0 or 1. |
| E3 | Are stopping class and age independent? | **Yes for odd m** (mutual information 0.00005 bits, below the shuffled baseline 0.0004). For all m they share 0.09 bits, entirely through parity. |
| E4 | How complex are age words? | Factor complexity is exactly Fibonacci: 2, 3, 5, 8, …, 144. Forward rays are Markov with entropy ≈ 2/3 bit/step, below the golden-mean maximum 0.694. |
| E5 | Is the Fibonacci law special to 3? | **No.** Identical counts for q = 3, 5, 7, 9, 11. |
| E6 | Mean age? | Exactly 11/10. Empirical 1.09999. |
| E7 | Same law for the +1 mirror (qm + 1)? | Yes: 3, 5, 8, 13 for q = 3, 5, 7. |
| E8 | Forward versus backward halving runs? | Forward runs are geometric with ratio 1/2; backward runs geometric with ratio 1/3. Both exact to 4 decimals. |
| E10 | Is the published Fibonacci theorem (Reyes Jiménez) the forward dual of the age law? | **Yes.** "Avoids 4 mod 6" is exactly "no two consecutive halvings"; identical sets for m = 2..14. |
| E11 | How long can a positive integer avoid two consecutive halvings? | Records sit at 2.5–3.8 × log₂n for odd n < 4·10⁶ (random model predicts 3.27). No n > 1 reaches 1 inside the family. 2^B − 1 survives exactly B steps. |
| E12 | Does (*) hold exhaustively? | **Yes for every n < 2⁴⁰** (Fibonacci-tree search, 232 s). Longest survival 129 steps = 3.24 × log₂n; random model 3.27. |
| E13 | Do single rays follow the Markov model? | Yes: χ² z-scores +0.75, +0.31, −1.24 on 200,000 steps each. |
| E14 | Does Banerji's backward conjecture (the dual of (*)) hold exhaustively? | **Yes for every odd n < 2·3³² ≈ 2^51.7** (Rust, 50 s). Longest survival 83 steps = 1.78 × log₂n; random model 1.71. Survival rate per step 0.66667, 0.66665, 0.66663 against 2/3. |
| E9 | Relation to the Collatz inverse tree? | The +1 mirror's B step is exactly the odd branch of the Collatz inverse tree (at m ≡ 4 mod 6); its A step replaces 2m by 2m/3. The two never both apply, so the tree collapses to a line. |

## The Fibonacci law — Proved

**Theorem.** Let q ≥ 3 be odd and G(m) = qm − 1 for odd m, qm/2 for even m. Walking backwards, step A (m → 2m/q) applies iff q | m, and step B (m → (m+1)/q) applies iff m is even and m ≡ −1 (mod q). Let age(m) be the number of backward steps available. Then min(age, t) depends only on m mod 2q^t, and the number of residues mod 2q^t with age ≥ t is F(t+3). Hence

    P(age ≥ t) = F(t+3) / (2·q^t),    mean age = Σ_{t≥1} F(t+3)/(2q^t)  (= 11/10 for q = 3).

**Proof.**
1. *No BB.* After B the value (m+1)/q is odd (m+1 odd, q odd). B needs an even value. So B never follows B.
2. *Parity takes care of itself.* After A the value 2m/q is even, so B's evenness condition holds automatically. The only parity condition in the whole walk is on m itself, and only if the first step is B.
3. *Each step reads one base-q digit.* Every back step is m → (u·m + v)/q with u ∈ {1, 2}, a unit mod q. After i steps the ancestor is (U·m + V)/q^i with U a unit mod q. The condition for step i+1 (ancestor ≡ 0 or ≡ −1 mod q) therefore selects exactly one of the q lifts of m mod q^i to m mod q^(i+1). By induction every word with no BB occurs, fixes m mod q^t uniquely, and different words give different residues.
4. *Count.* By the Chinese remainder theorem a word starting with A leaves the parity of m free (2 residues mod 2q^t); a word starting with B forces m even (1 residue). Words of length t with no BB number F(t+1) starting with A and F(t) starting with B. Total: 2F(t+1) + F(t) = F(t+3). ∎

The same argument covers qm + 1 (E7). Verified by exhaustive count for q ∈ {3, 5, 7, 9, 11} and t up to 9 (q = 3).

**What the proof shows.** Fibonacci comes from the 2, not the 3: the only constraint is "an odd value cannot take the odd-type step". The multiplier q only sets the denominator. That is why the law is universal, and why it is so much more regular than the stopping-class counts N(s), which carry the extra irrational boundary y = x·log₂3.

## The forward dual — Proved, Verified (E10)

Reyes Jiménez (arXiv:2606.02621) proves: exactly F(m+1) odd n ≤ 2^m have Terras orbits that avoid 4 mod 6 at positions 2..m. E10 reproduces the counts (2, 3, 5, …, 610 for m = 2..14; "steps 2..m" must be read as orbit positions, i.e. T¹..T^(m−1)) and shows the set is **exactly** the odd n whose parity word of length m contains no "00".

**Why (Proved).** After an odd step the value is (3x+1)/2 ≡ 2 (mod 3). Halving a value ≡ 2 (mod 3) gives a value ≡ 1 (mod 3). Values ≡ 1 (mod 3) arise in no other way, and orbit values are never ≡ 0 (mod 3) after the first step. A value is ≡ 4 (mod 6) iff it is ≡ 1 (mod 3) and even — that is, iff it was just produced by a halving and is about to be halved again. So "avoids 4 mod 6" ⇔ "no two consecutive halvings" ⇔ every α ≤ 2. By the Terras bijection, words of length m starting with 1 and containing no "00" correspond one-to-one to odd residues mod 2^m, and there are F(m+1) of them. ∎

So the two Fibonacci laws are one statement read in two directions:

| | Forward (Reyes Jiménez) | Backward (age law) |
|---|---|---|
| Forbidden pattern | "00" — two pure halvings in a row | "BB" — two odd-type steps in a row |
| Digit bijection | parity word ↔ n mod 2^m (Terras) | age word ↔ m mod 3^t (one base-3 digit per step) |
| Count | F(m+1) of 2^(m−1) odd residues | F(t+3) of 2·3^t residues |
| Decay | (φ/2)^m | (φ/3)^t |
| Status of the pattern | **imposed**: selects a thin set of orbits (all α ≤ 2) | **automatic**: every integer obeys it |

The last row is the real difference. On the forward side the golden-mean constraint picks out a measure-zero family; on the mirror side it is a law of the whole system, which is why ages have an exact closed-form distribution and stopping classes do not.

This gives a short independent proof of the published count, and places the age law as its 3-adic companion. It does not make the age law a corollary of that paper: the paper works mod 2^m with the mod-6 transition graph; the age law needs the base-q digit argument above.

## Survival in the slow family — Verified (E11)

The forward golden-mean orbits (no "00", every α ≤ 2) multiply by 3/2 or 3/4 per odd step. They are the slowest-contracting orbits, so they are the natural worst case.

- **No n > 1 reaches 1 without leaving the family** (0 of 2·10⁶ odd n). Reason: the only way into 1 from another odd number is through 5, 21, 85, … = (4^j − 1)/3 with α = 2j ≥ 4. So Collatz implies every n > 1 eventually has α ≥ 3, and *an n > 1 that stayed in this family forever would be a counterexample.*
- **Record survival grows like log n.** Records for odd n < 4·10⁶: 1665 (30 steps), 10881 (41), 687871 (67), 3041391 (81) — between 2.5 and 3.8 × log₂n. A random model with survival probability (φ/2)^m predicts records at log₂n / log₂(2/φ) = 3.27 × log₂n. The data are consistent with pure chance; nothing in the family behaves specially.
- **2^B − 1 survives exactly B steps**, one per bit (checked to B = 128): it imitates −1 until its ones run out. This is the [[Nesting and the Never-Drain Fractal]] §7 picture in miniature — a positive integer can shadow a never-draining 2-adic ball only for as long as it has bits to spend.

A clean, weaker-than-Collatz statement comes out of this:

> **(*)** Every positive integer n > 1 has two consecutive halvings somewhere in its orbit. Equivalently: some Syracuse iterate is ≡ 5 (mod 8); the orbit hits 4 (mod 6) after the first step; some α ≥ 3.

It is necessary for Collatz, it concerns a set of dimension log₂φ ≈ 0.694 rather than 0.95, and it uses positivity (−1 and the cycle −5, −7 violate it).

**Prior art: (*) is already posed as an open question.** Reyes Jiménez, arXiv:2606.02621, Section 5, asks whether every odd n > 2 has a finite first level m₀(n) at which the orbit meets 4 (mod 6), and notes that an explicit bound m₀(n) ≤ f(n) would settle it. Nothing is proved toward it there; even "every nontrivial positive cycle visits 4 mod 6" is left open. That paper does not remark that Collatz implies (*), nor mention negative integers or the dimension. So (*) is **Open, and not ours.** What we add is evidence and context (E11, E12 below).

**Why the known cycle theorems do not settle the cycle half.** Simons–de Weger and Hercher bound the number of local minima of a cycle; a cycle with every α ≤ 2 has unrestricted many. It is excluded only in the weak sense that any nontrivial cycle is known to be astronomically long.

**Structure of (*).** An orbit that avoids 5 (mod 8) forever is either bounded — hence eventually periodic, hence a nontrivial cycle with every α ≤ 2, since 1 cannot be entered from outside without α ≥ 4 — or divergent. Inside the family α = 1 occurs for residues 3, 7 (mod 8) and α = 2 for 1 (mod 8), so a typical member *grows* (drift ⅔·log 1.5 + ⅓·log 0.75 > 0). (*) therefore says: growing orbits cannot stay in the family. It has the flavour of a divergence problem and I see no route to a proof.

## Exhaustive search for (*) — Verified (E12)

`scripts/double_halving_search.py` does not scan all n < 2^B. It walks the tree of residues mod 2^j whose first j steps contain no "00" — only F(j+1) of them — and finishes each leaf by direct iteration. This is exhaustive for n < 2^B at a cost of F(B+1) instead of 2^B.

| Range | Survivors of B steps | Longest survival | At n | steps / log₂n |
|---|---|---|---|---|
| n < 2²⁴ | 75,025 = F(25) | 82 | 3,041,391 | 3.81 |
| n < 2³² | 3,524,578 = F(33) | 100 | 1,548,635,775 | 3.28 |
| n < 2⁴⁰ | 165,580,141 = F(41) | 129 | 971,145,319,023 | 3.24 |

(2⁴⁰ took 232 s in pure Python. Integers that leave the family before step B are pruned by the tree — they satisfy (*) trivially — so the search is exhaustive.)

**The bits an orbit makes for itself are as good as random.** Among the 165,580,141 integers below 2⁴⁰ that survive their own 40 bits, the chance of surviving one more step is 0.8090, 0.8090, 0.8093, 0.8090, 0.8096, 0.8089 at L = 40, 46, 52, 58, 64, 70 — against φ/2 = 0.8090. Past step 40 the parity is no longer read from n's own digits; it comes from digits created by the ×3 growth. Those created digits leave the family at exactly the rate free digits would. This is the finite-bit-string question of [[Nesting and the Never-Drain Fractal]] §7 measured directly: no sign of any structure a never-draining integer could exploit.

**Every n > 1 in range satisfies (*).** The random model (survival probability φ/2 per step) predicts records at log₂n / log₂(2/φ) = 3.27 × log₂n. Observed records sit on that line. Empirically m₀(n) ≤ 4·log₂n throughout; that is the explicit bound the open question asks for, as a conjecture.

## The backward dual, searched the same way — Verified (E14)

Banerji (1996, via Lagarias's annotation) conjectured that backward Syracuse iteration restricted to exponents ≤ 2 always reaches a multiple of 3. On odd n that iteration is **deterministic**:

    b(n) = (2n − 1)/3  if n ≡ 2 (mod 3),      b(n) = (4n − 1)/3  if n ≡ 1 (mod 3),      stop if 3 | n.

n = 1 is fixed. This is (*) with time reversed and the primes swapped, and the same tree idea applies with base-3 digits: lifting r by 2·3^j·d changes b^j(r) by a power of 2 times d, so exactly one of the three lifts dies and the other two continue. Survivors of t steps are 2^t of the 3^t odd residues mod 2·3^t, and a walk of that tree is exhaustive for odd n < 2·3^t at cost 2^t. (`scripts/banerji_backward_search.py`, with the tree count asserted against brute force at t = 8; `scripts/double_halving_rs/src/bin/banerji.rs` for depth, cross-checked against the Python version at t = 22.)

| | forward (*) — Reyes Jiménez Q1 | backward — Banerji |
|---|---|---|
| map | T restricted to "no 00" | b, deterministic |
| survivors | F(B+1) of 2^(B−1) residues | 2^t of 3^t residues |
| dimension of the exceptional set | log₂φ ≈ 0.694 (2-adic) | log₃2 ≈ 0.631 (3-adic) |
| typical behaviour inside | grows | shrinks (mean log factor ½·log(8/9) < 0) |
| survival per step, measured | 0.80902 (φ/2 = 0.80902) | 0.66667 (2/3) |
| records, measured / model | 3.24–3.44 / 3.27 × log₂n | 1.67–1.78 / 1.71 × log₂n |
| exhaustive range | see E12 | odd n < 2·3³² ≈ 2^51.7 |
| fixed point excluded | n = 1 | n = 1 |

No odd n > 1 in range reaches the fixed point 1 from outside, and none survives. Both directions behave exactly like free digits. The pair is the cleanest statement of the 2-adic/3-adic duality this investigation has found: **one question read forward in base 2, the same question read backward in base 3.**

## Single-ray statistics — Verified (E13)

Three mirror rays (seeds 1, 5, 7), 200,000 steps each, cut into 25,000 non-overlapping blocks of length 8 and compared with the Markov prediction (π_A = 2/3, P(B|A) = 1/2, P(A|B) = 1) over the 55 allowed blocks: χ² = 61.8, 57.2, 41.1 on 54 degrees of freedom (z = +0.75, +0.31, −1.24). No "BB" occurs. Single rays are statistically indistinguishable from the Markov model. This remains unprovable for the same reason as Mahler's 3/2 problem.

## An arrow of time — Proved, Verified (E8)

The same run of halvings has two different distributions depending on the direction of reading:

- **Forward**: the run after odd b is v₂(3b − 1). Under the uniform 2-adic measure P(run ≥ r) = 2^−(r−1).
- **Backward**: a run of A steps continues iff 3 divides the ancestor. Under the uniform 3-adic measure P(run ≥ r | run ≥ 1) = 3^−(r−1).

Forward in time the dynamics are 2-adically uniform; backward they are 3-adically uniform. This is the repo's [[Dual Constraint]] as a statement about time direction. Entropy per step is 2/3 bit forward (E4), against log₂φ ≈ 0.694 for the maximal-entropy measure on the same language: real orbits do not sample the golden-mean shift uniformly.

Caution: that a *single* forward ray has these statistics is measured (four rays, 20,000 steps, P(B|A) between 0.492 and 0.502), not proved. Proving it is a relative of Mahler's problem on the distribution of (3/2)^k mod 1, which is open.

## Negative results

- **E1.** The register adds bookkeeping but no new law. At the first drop its exponent is ⌈s·log₂3⌉ for every odd n < 200,001, which is the Odd Stopping Time Spectrum theorem (k = ⌈s·log₂6⌉) minus s. My first run of E1 reported 50% agreement; that was an error in the experiment (stepping by whole Syracuse steps overshoots the drop — the overshoot is itself geometric: 0.499, 0.250, 0.125, …). Fixed and rerun.
- **E2.** The old cycles have no special position on the mirror table. Their members are never multiples of 3, so their ages are 0 or 1, and they spread over many rays.
- **Barrier unchanged.** None of E1–E9 produces a property that separates positive integers from −1. See [[Nesting and the Never-Drain Fractal]] §6.

## Literature check (2026-09-19)

Web search plus abstracts; one paper skimmed (Frougny–Klouda, pp. 1–6). No full-text reading otherwise. **Do not claim novelty on this basis.**

| Source | What it has | Closeness |
|---|---|---|
| OEIS search for 1, 2, 3, 8, 12, 18, 27, 80, 120, 180, 270, 405, 1214 | No match. Seeds 1, 4, 5, 7, 10, 11, … are A047259 (≡ 1, 4, 5 mod 6), with no Collatz reference in the listing. | The map G not found as a named object. |
| M.-A. Reyes Jiménez, "A Fibonacci theorem for Collatz trajectories via modular graph structure", arXiv:2606.02621 (28 May 2026) | Exactly F(m+1) odd integers in {1..2^m} have T-orbits avoiding 4 mod 6 during steps 2..m; decay (φ/2)^m; golden-mean subgraph of the mod-6 transition graph. | **Closest prior art. Must cite.** Same mechanism (Fibonacci from a mod-6 constraint) and the same special class: 4 mod 6 is exactly where our B step applies (E9). Theirs counts mod 2^m forward; ours counts mod 2·3^t backward. Plausibly dual; not identical. |
| Albert, Gudmundsson, Ulfarsson, "Collatz meets Fibonacci", arXiv:1404.3054 | Fibonacci enumeration of Collatz-induced permutations; reportedly because two up-steps are never consecutive. | Same no-BB combinatorics, different object. |
| Akiyama, Frougny, Sakarovitch, "Powers of rationals modulo 1 and rational base number systems", Israel J. Math. 168 (2008) | Base 3/2 number system; division step 2s = 3s′ + a, a ∈ {0, 1, 2}. | Our A step is their digit-0 edge. Our B step, (m+1)/3, is *not* one of their edges (theirs are (2s − a)/3). Their tree gives every integer a parent; ours leaves half of all integers with none. |
| Frougny, Klouda, "Rational base number systems for p-adic numbers", RAIRO-ITA 46 (2012) | Negative integers in base 3/2; expansions converge r-adically exactly for primes r dividing 3 (Lemma 3.5). | Explains in general why backward structure is 3-adic. No Fibonacci counts seen in pp. 1–6. |
| Mahler, "An unsolved problem on the powers of 3/2", J. Austral. Math. Soc. 8 (1968) | The map g(x) = (3x+1)/2 for odd x, 3x/2 for even x; a Z-number exists in [n, n+1) iff no iterate of n is ≡ 3 mod 4. | **Closest named relative of the mirror map**: same 3x/2 even branch and a residue-avoidance question. The odd branch differs (ours is 3m ± 1 with no halving), which is what makes ours injective with predecessor-free seeds. |
| Banerji, "Some properties of the 3n+1 function", Cybernetics and Systems 27 (1996), via Lagarias's annotation | Conjectures that backward Syracuse iteration using only α ≤ 2 preimages always reaches a multiple of 3 in finitely many steps. | The backward-time dual of (*). Closely related, not identical. Original not seen. |
| Wirsching, LNM 1681 (1998) | 3-adic equidistribution hypothesis for predecessor sets under backward iteration. | Confirms backward structure is studied 3-adically. Book not accessed; no Fibonacci mention in the annotations. |
| Mahler (1968) Z-numbers; Flatto–Lagarias–Pollington; Odlyzko–Wilf (Josephus, ⌈3n/2⌉) | Distribution of (3/2)^k mod 1. | Governs the open single-ray question above. Not read this session. |

Checked since: both Lagarias annotated bibliographies (arXiv math/0309224, math/0608208) were text-searched in full — no entry for the map 3m − 1 / 3m/2, for an injective Collatz variant of this form, or for a Fibonacci count of backward residues. Reyes Jiménez states "To our knowledge, no prior work establishes a Fibonacci count of this kind for Collatz trajectories" for the forward count. Third pass (secondary sources only): Wirsching's admissible vectors are decided mod 3^m — the same mechanism as the age law, for the map T, with non-Fibonacci counts; Kohl treats the opposite (surjective, non-injective) case; Merlini–Sala's "Fibonacci attractor" is a heuristic inverse-tree growth rate. More forward-direction prior art turned up: German (NKS 2004, golden-mean shift of 3x+1 itineraries) and Winkler arXiv:1412.0519 (Fibonacci counts of residue classes mod 2^k). Full citations in [[Draft Note - A Fibonacci Age Law]] §6. Backward law still not found anywhere.

**Assessment.** The map G itself and the age law were not found. The ingredients are all known (no consecutive odd steps; base-3/2 backward division is 3-adic; Fibonacci from mod-6 graphs). The likeliest status is "elementary, possibly folklore, apparently unrecorded" — worth a short note only after the unchecked sources are read.

## Suggested next experiments

1. **Done as E10.** Follow-up: the forward golden-mean orbits (all α ≤ 2) multiply by 3/2 or 3/4 per odd step. Which of them drain, and how fast? They are the slowest-contracting admissible orbits and a natural worst case for the never-drain question.
2. **The mirror inside the inverse tree.** E9 says the +1 mirror is the Collatz inverse tree with 2m replaced by 2m/3. Interpolate: allow k doublings before the ÷3. Does the predecessor-count growth rate of the real inverse tree (the quantity in Applegate–Lagarias density bounds) come out as a Fibonacci-like recurrence in this family?
3. **Single-ray normality.** Push one ray to 10⁶ steps and test the Markov prediction with a proper χ² test. A deviation would be news; agreement is expected and unprovable.
4. **Age as a feature.** Add age and seed residue to `collatz/embeddings` lenses. E3 says they are independent of stopping class for odd n, so they are genuinely new coordinates, not redundant ones.
