---
tags: [collatz, tag-system, de-mol, ternary, computation-models, research-questions]
status: results-and-questions
created: 2026-09-16
---

# Tag Systems and the Ternary Circuit

**Question (from the user).** The Collatz map has a famous 2-tag system (Wikipedia; De Mol 2008 [1]) over a *three-letter* alphabet. Is there an equivalence between that and the ternary computation models of this vault — the {−1, 0, +1} threshold circuit ([[Ternary Syracuse Circuit]], [[Minimal Ternary Circuit]]) and ternary networks? What do the two models say together or separately?

Script: `scripts/tag_system.py`; results `results/tag_system.json`. Everything in §2 is computed and exact.

## 1. The two models side by side

De Mol's tag system T_C ∈ TS(3, 2): alphabet {α, c, y} (Wikipedia writes a, b, c), shift number v = 2, productions α → cy, c → α, y → ααα. From α^n it produces α^{T(n)}, T the Terras map n/2 | (3n+1)/2 [1, Thm 2.1].

| | 2-tag system T_C | ternary threshold circuit |
|---|---|---|
| representation of n | **unary**, α^n (length n) | **binary**, LSB first (length log₂n) |
| the "3" | 3 letters: α = counter, c = even-phase output, y = odd-phase output | weights in {−1, 0, +1}; the ×3 is n + (n≪1) |
| how parity is decided | **by phase**: after scanning α^n two letters at a time, |word| mod 2 decides whether c or y is under the head next (De Mol: "|A| mod v determines what will be scanned") | **by reading bit 0** |
| time per Terras step | n (even) or n + 1 (odd) tag steps — Verified n < 600 | one pass over the bits: 5 units per bit |
| state | the whole word | 3 bits (p, prev, carry) |
| what it can express | universal in the class (TS(576,2) simulates any TM); TS(3,2)'s solvability *depends on* 3n+1 [1] | a finite transducer; not universal |
| visibility of 2-adic structure | none — unary hides everything; k rounds are decided by n mod 2^k but the machine must count to n to find out | total — the low k bits *are* the next k parities |

The honest one-line answer: **they compute the same function by opposite means.** The circuit reads the 2-adic information directly; the tag system computes it by counting, which is what makes it slow (Θ(n) per step) and what makes tag systems powerful enough to be universal.

## 2. Results — all Verified, exact

1. **Round length.** α^n → α^{T(n)} takes exactly n tag steps for even n and n + 1 for odd n (all n < 600; De Mol states the same [1, §2.1]).
2. **Total tag time is the orbit sum.** For a full orbit n → 1: tag steps = Σ (Terras iterates) + (number of odd rounds), exactly, for n = 3, 7, 27, 97, 871 (27: 40,656 steps = 40,615 + 41).
3. **Tag time is affine on dropping-set residue classes.** Since orbit sums are exact affine functions of n within each residue subgroup (`docs/Conjectures/Affine Orbit Structure.md`), so is the tag system's running time to the first drop. Checked on Set₁₃'s class n ≡ 39 (mod 256): tag steps to first drop = (2309/128)·n + const, one slope across 12 consecutive members. So **De Mol's machine has a closed-form running time per residue class, without running it** — the 2-adic structure that the machine cannot see governs its clock.
4. **The word-length walk is ternary.** Each production changes the word length by |P(x)| − v ∈ {0, −1, +1} for x = α, c, y. So the tag system is literally a **{−1, 0, +1} accumulator on word length**, and the Collatz value at the end of each round is the running sum. Over a full orbit the net change is c-reads − b-reads = 1 − n. The "zero density" of this walk (fraction of α-reads) is **exactly ½** for every odd n < 400 (each round is ⌈n/2⌉ α-reads followed by ⌈n/2⌉ y-reads or n/2 c-reads).
5. **The read word is the parity vector in unary.** The sequence of letters under the head is, round by round, α^{⌈n/2⌉} followed by y^{(n+1)/2} (n odd) or c^{n/2} (n even). The binary parity vector becomes a three-letter word whose *run lengths* are the orbit values. (I expected an alternating "y c y c" — the simulation corrected me: after reading y the deleted pair is "y c", so the head lands on y again.)

## 3. De Mol's theorems, as context

- **Thm 2.1:** 3n+1 reduces to T_C ∈ TS(3, 2). The 3n+1 problem is a *reachability* problem for T_C: does α ever appear alone.
- **Thm 2.2:** any Collatz-like function with modulus d (Michel's form, G(n) = a_i(n − i)/d + r_i on n ≡ i mod d) is simulated by a tag system with shift v = d and μ ≤ 2d + 3 symbols; **Thm 2.3:** μ ≤ d + 2 under a size condition. The shift number *is* the modulus. Conway (1972): such functions are universal, so tag systems are unsolvable via Collatz-like functions — an alternative proof to Minsky's.
- The solvability ladder: TS(2, 2) recursively solvable (Post; De Mol); TS(3, 2) contains 3n+1 (so proving it solvable is at least as hard as Collatz); TS(576, 2) universal (Cocke–Minsky). The "3n+1 line" sits one symbol above the solvable line.
- Maslov's condition for unsolvable tag systems, l_min = v − 1 and l_max = v + 1, is satisfied by T_C [1, §2.1] — and it is exactly the statement that the length increments are in {−1, 0, +1}. **The ternary walk of §2.4 is Maslov's minimality condition.** That is the one place where "ternary" in the tag system and "ternary" in the circuit have a shared meaning: both are "one unit up, one down, or stay" — the minimal nontrivial increment set. (Label: Analogy with a theorem behind it, not an equivalence.)

## 4. Is the "3" the same 3? — mostly no

- Tag alphabet size 3 = (one counter symbol) + (one output symbol per residue class mod 2). For modulus d it is d + 1 or d + 2, so it counts *residue classes*, not the multiplier.
- Circuit weights {−1, 0, +1} come from shift-and-add and would be the same for 5n+1. The FST's *carry* alphabet, however, is {0, 1, 2} for ×3 (and {0,…,a−1} for ×a) — that is where the multiplier shows up as a "3", and it is a different 3 from the alphabet's.
- Word-length increments {−1, 0, +1}: Maslov's condition, independent of 3n+1.

So the two threes are not the same object. **Dead end as an equivalence; alive as a comparison of computation models.**

## 5. Research questions

**Q1 (answered here, Verified).** Does the tag system's running time have closed form? Yes — orbit sum + odd count; affine per residue class (§2.2–2.3). Corollary: E[tag time to first drop]/n over a residue class is the class's affine slope; Wagon's constant counts *rounds*, orbit sums count *tag steps*.

**Q2 (open, concrete).** *Unary as the worst base.* [[Experiment B - Base Polarity]] showed a learner's ceiling is P(v ≤ v_max(base)), with base 3 hiding the 2-adic structure. Unary is the limit: the tag rewriting rule is trivially local (a transformer would learn one tag *step* instantly), but a "round" α^n → α^{T(n)} requires counting. Experiment: train the same transformer on unary round-outcomes for n ≤ 200. Prediction: it learns nothing beyond P(v=1) unless it can count exactly — the base-3 result in its purest form. Cheap; proposed as loop item L15.

**Q3 (open, harder).** *A "3n+1 line" for ternary threshold circuits.* De Mol places Collatz one symbol above the solvable tag systems and far below the universal ones. In the circuit model: 4 units impossible, 5 units = the Terras step ([[Minimal Ternary Circuit]]). What is the smallest ternary recurrent threshold layer that simulates a universal tag system (via Cocke–Minsky) or a small universal Turing machine? A descriptive-complexity ladder — solvable / Collatz / universal — measured in ternary threshold units, matching De Mol's Fig. 2 measured in (μ, v). Nobody has done this; it is well-defined and finite.

**Q4 (open, theoretical).** *Phase versus bits.* The tag system decides parity by |word| mod v; the 2-adic law says k rounds are decided by n mod 2^k. Is there a tag-system-internal statement of 2-adic determinism — e.g. that the sequence of head phases over k rounds is a function of n mod 2^k that the machine can only reach by counting — and does it give a lower bound Ω(n) per round for *any* tag simulation of Collatz, i.e. is unary forced? (A binary-tape tag system is the FST; the question is whether tag systems with v = 2 can ever be log-time on this function.)

**Q5 (open, expository).** *Run-length view.* The read word encodes the orbit as run lengths of a strictly alternating three-letter word (§2.5). Its length is the orbit sum; its entropy is ≈ log₂n (it is a function of n). A BITCOS-style encoding at 2 − z = 1.5 bits/letter is therefore absurdly wasteful — the "right" code for a Collatz orbit is n itself. Nothing to prove; a nice paragraph for [[Summary - Findings and Open Questions]] on why "ternary storage" and "ternary computation" are unrelated even when both show up.

**Q6 (speculative).** *Maslov's ternary and Sturmian words.* T_C's length walk takes values in {−1, 0, +1} with zero density exactly ½ and a rigid block structure. The repo's Sturmian sign rule (`docs/Explorations/Dropping Zeta Spectrum.md`) is also a ±1 sequence over a rigid structure. Is there a substitution mapping the read word's block structure onto the Sturmian coding of s·log₂3? Probably not (one is governed by n, the other by an irrational rotation), but the test is a few lines.

## 6. What the two models say together

Separately: the circuit says *Collatz is 1.58-bit arithmetic with total 2-adic visibility*; the tag system says *Collatz is one symbol above decidability in the simplest universal rewriting model*. Together they say something sharper: **the same map is trivial-to-read and universal-in-class depending only on whether the number is stored positionally or by length.** That is the base-polarity result of [[Experiment B - Base Polarity]] pushed to its endpoint, and it is the strongest argument in this vault for choosing representations — in code and in learners — by how much 2-adic information they expose.

## Sources

1. L. De Mol, "Tag systems and Collatz-like functions", *Theoretical Computer Science* 390 (2008) 92–101; preprint 22 Oct 2007 (Ghent University) — https://backoffice.biblio.ugent.be/download/436211/6812232
2. Wikipedia, "Tag system — Example: Computation of Collatz sequences" — https://en.wikipedia.org/wiki/Tag_system#Example:_Computation_of_Collatz_sequences
3. J. Cocke, M. Minsky, "Universality of tag systems with P = 2", J. ACM 11 (1964); S. Maslov, on minimal unsolvable tag systems (as cited in [1]).
4. J. H. Conway, "Unpredictable iterations" (1972); P. Michel, "Small Turing machines and generalized busy beaver competition" (Collatz-like functions, as cited in [1]).
5. [[Ternary Syracuse Circuit]], [[Minimal Ternary Circuit]], [[Experiment B - Base Polarity]]; `docs/Conjectures/Affine Orbit Structure.md`.
6. `scripts/tag_system.py`, `results/tag_system.json`.
