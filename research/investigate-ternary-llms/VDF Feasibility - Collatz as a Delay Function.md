---
tags: [collatz, vdf, verifiable-delay, sequential-work, parity-vector, cryptography, feasibility]
status: analysis
created: 2026-09-16
---

# VDF Feasibility — Collatz as a Delay Function

**Question (from the user).** Could today's findings — the trit/bit identity, the affine orbit law, 2-adic determinism, the 5-unit ternary gate, ternary networks — found a verifiable delay function (VDF), a proof of sequential work, or a verifiable puzzle?

**Short answer.** There is exactly one asymmetry in Collatz that points the right way, and it is not one of the "ternary" findings: **the parity-vector map n ↦ v is (conjecturally) sequential to compute but has a closed-form inverse**, so a verifier can check a transcript with one modular product while the evaluator must iterate. That gives a *Sloth-class* primitive (verification cheaper and parallel, not succinct), with a built-in time–memory tradeoff that must be priced in. Everything else — the affine law, the dropping-set tables, the ternary circuit — is a *shortcut available to both parties*, which helps a verifier only if the evaluator lacks it, and here the evaluator does not. Literature context in [[VDF Literature - Sequential Functions]].

Script: `scripts/parity_vector_vdf.py`; results: `results/parity_vector_vdf.json`.

## 1. What a VDF needs

A VDF (Boneh–Bonneau–Bünz–Fisch 2018) is a function f with a delay parameter T such that:

1. **Sequentiality:** computing f takes T sequential steps, and no algorithm with poly(T) parallel processors does it materially faster;
2. **Efficient verification:** given (input, output, proof), checking takes polylog(T) time;
3. **Uniqueness:** for each input exactly one output verifies.

Weaker relatives: *proofs of sequential work* (drop uniqueness), *Sloth* (Lenstra–Wesolowski; verification only a modest factor faster than evaluation), *time-lock puzzles*. The killer requirement is (1) against *all* speedups — parallel, precomputation, special hardware — and (2) being asymptotic, not a constant factor.

## 2. Mapping today's findings onto those requirements

| Finding | Helps sequentiality? | Helps verification? | Verdict |
|---|---|---|---|
| Affine orbit law dest = (3^s/2^(k−s))n + C ([[Collatz Bridge - Trits and Stopping Times]]) | **Hurts**: it is a k-step shortcut for anyone who knows the residue class | Yes, but the evaluator has the same shortcut | cancels |
| 2-adic determinism: k steps decided by n mod 2^k | **Hurts**: a table of 2^p residues jumps p steps per lookup (§4) | Yes, same table | cancels, and adds a memory speedup |
| Stopping time = s + bitlen(3^s) | neutral (a fact about first drops, not about computing them) | no | irrelevant |
| 5-unit ternary Terras gate ([[Minimal Ternary Circuit]]) | neutral: it is an *implementation*, not a hardness source; per-step depth is O(bits) bit-serial or O(log bits) with lookahead | no | irrelevant to hardness; relevant to cost (§6) |
| Ternary MLP learns the 2-adic ladder ([[Experiment A - Ternary Dropping-Set Classifier]]) | neutral | no; L5 shows weights are not readable proofs | "proof in the network weights" does not work |
| **Parity vector has a closed-form inverse** (Terras 1976; §3) | the forward map is the only candidate for sequential hardness | **Yes**: one modular product checks a k-bit transcript | the one real lead |

## 3. The one real asymmetry — Verified (formula), Conjecture (hardness)

Let T(n) = n/2 (n even), (3n+1)/2 (n odd) and v = (v₀, …, v_{k−1}) the parities of n, T(n), …, T^{k−1}(n). Terras proved v depends only on n mod 2^k and that n mod 2^k ↦ v is a bijection of {0,1}^k. Writing s = #ones(v) and r(v) = Σ_{i: vᵢ=1} 2^i · 3^{#ones after i},

$$T^k(n) = \frac{3^s n + r(v)}{2^k}, \qquad\text{hence}\qquad n \equiv -\,r(v)\cdot 3^{-s} \pmod{2^k}.$$

So **given v, the residue is a closed form**: one sum, one modular inverse, one product. Verified: bijection and inverse exact for all residues at k = 4, 8, 12, 14; affine formula and inverse check correct for 200 random n at each of k = 64, 256, 1024; a single flipped bit is rejected.

- **Evaluator:** k sequential Terras steps (each cheap). No faster way to compute v from n is known.
- **Verifier:** compute r(v), s, and check the congruence. Work O(k) big-integer operations, **depth O(log k)** (r is a prefix-structured sum; 3^{−s} is a modular exponentiation). Measured single-threaded in Python: 4.3× less work at k = 20,000, 4.9× at k = 100,000; the real gain is that it parallelises and the evaluator (conjecturally) does not.
- **Hardness conjecture needed:** *computing the parity vector of n mod 2^k requires depth Ω(k) even with poly(k) processors.* Nobody has studied this as a cryptographic assumption. Evidence is thin: (i) no shortcut is known; (ii) constant-depth transformers fail at long-step counts (Charton–Narayanan, [[Neural Networks and Collatz - Prior Work]]); (iii) generalised Collatz maps are undecidable (Conway) — which says nothing about depth for fixed k. **Algebraic degree is not evidence:** vⱼ has ANF degree exactly j with ~2^(j−1) monomials over bits 0…j, but the inverse's bits have the same degrees and monomial counts and the inverse is a log-depth computation. High degree ≠ high depth.

What this buys: a **proof of sequential work with parallel verification**, output length k bits for k steps. Not a VDF: verification is O(k) work, not polylog, and the transcript is not succinct.

## 4. The built-in time–memory tradeoff — Verified

2-adic determinism *is* a precomputation attack. With a table of parity vectors for all residues mod 2^p (2^p entries of p bits), the evaluator computes v in blocks: look up the next p bits from x mod 2^p, then x ← (3^s x + r)/2^p in one affine op. Verified: 240 steps in 20 lookups + 20 affine ops, 0 mismatches vs sequential (p = 12, 100 random 300-bit n).

Sequential depth drops by the factor p for memory 2^p: 2^32 entries (≈16 GB) → 32×; 2^40 (≈5 TB) → 40×. A logarithmic speedup in memory is not fatal for a Sloth-class primitive, but it is a structural advantage for a well-resourced evaluator that repeated squaring (the standard VDF) does not have, and it is exactly the kind of "hardware advantage" that led the Ethereum Foundation to pause VDF deployment. It must be priced into any security parameter.

## 5. Why the affine and dropping-set structure does not give the verifier an edge

A tempting design: prover reports the sequence of dropping-set residues (r, k, s) visited; verifier checks each drop with one affine op instead of k steps. It works — but the prover can use the same table (89% of drops are decided by 12 bits, [[Exact Admissible Sequence DP]]), so the sequential depth of *evaluation* is the number of drops, not of steps; the verifier gains the same factor (≈ Wagon's constant 9.48 per drop) that the evaluator already has. A shortcut both sides own is compression, not verification. The only structure that is one-sided is §3.

## 6. If one wants a real VDF from this: the SNARK route, and why it is not obviously better than MinRoot

Any sequential function plus incrementally verifiable computation is a VDF; the cost metric is then *constraints per step* in the proof system. Two observations:

- **The closed-form inverse does *not* make the statement smaller — it makes it parallel.** (Corrected by L14, below.) Proving "v is the parity vector of n" step by step costs k steps × O(k) bits; proving the congruence −r(v)·3^{−s} ≡ n (mod 2^k) costs k running products mod 2^k × O(k) bits — the same order. With fast multiplication both are Õ(k). The difference is that r(v) splits as 3^{s_high}·r_low + 2^{k/2}·r_high, so the verifier's work is a parallel divide-and-conquer of depth O(log² k), while the evaluator's divide-and-conquer (v_high from (3^{s_low}n + r_low)/2^{k/2}) still waits for v_low and has depth Θ(k). "Proof in the structure" made precise: **the structure is Terras's affine formula, and what it buys is parallel verification, not a shorter proof.**
- **Per step, Collatz is worse than MinRoot.** MinRoot iterates a degree-5 map in a prime field: one constraint per step. A Terras step needs a parity extraction (a bit decomposition of the running value, O(log M) constraints) plus an affine map. The ternary-ness of the gate is irrelevant to arithmetic proof systems (constraints live in a prime field, not in {−1, 0, +1}). So a Collatz-based STARK VDF would pay a log factor per step for no known hardness benefit. Label: **Dead end** as a competitor to MinRoot-style designs unless the parity-vector hardness conjecture turns out to be stronger than algebraic-degree hardness (MinRoot's assumption was attacked in 2023; see the literature note).

## 7. The puzzle idea — not a delay function

"Find the smallest ternary circuit that computes Collatz function X" is an instance of the Minimum Circuit Size Problem. Verification is easy (simulate the truth table); the search is embarrassingly parallel. That makes it a proof-of-work-style *search puzzle*, the opposite of a VDF. Our exhaustive search ([[Minimal Ternary Circuit]]) is exactly such a solution, and it took 54 s on one core — the puzzle is also small. Fun, not foundational.

## 8. Verdict and what would change it

- **VDF from today's findings: no.** The ternary results are about implementation cost and learnability, not hardness; the affine/2-adic structure is a two-sided shortcut and a precomputation attack.
- **Proof of sequential work with parallel verification: plausible primitive**, built on the parity-vector map and its closed-form inverse. Weaker than a VDF, unstudied hardness assumption, log-in-memory speedup. Worth one careful write-up if the literature survey finds no prior proposal; worth nothing more without cryptanalysis.
- **The genuinely new observation:** the verification statement for k Collatz steps is a single congruence n ≡ −r(v)·3^{−s} (mod 2^k). Whether or not it becomes a primitive, it is the right way to *certify* long Collatz computations (e.g. distributed verification of orbit records), and it is cheap.

What would change the verdict: a proof or strong evidence that computing Φ: n mod 2^k ↦ v has depth Ω(k) (would upgrade "plausible" to "candidate"); or a parallel algorithm for Φ (would kill it — and would be a nice Collatz result in its own right).

### Verdict after the literature survey ([[VDF Literature - Sequential Functions]])

Four facts from the survey sharpen the verdict, mostly downward:

1. **No Collatz VDF, PoSW or serious Collatz cryptographic primitive exists.** What exists is an abandoned Apple Collatz-hash patent (2011), a heuristic one-way-function candidate, two proof-of-work variants and a 2025 "Collatz Hash" ePrint — none with a security definition, reduction or cryptanalysis, and every PoW variant is a parallelisable search puzzle. So the parity-vector congruence of §3 would be new as a *certification* idea; nobody has proposed it as a primitive either.
2. **The adversary model that shelved MinRoot is exactly the one Collatz fails.** The Ethereum Foundation stopped recommending VDFs on 18 Sept 2023 after Leurent–Mennink–Pietrzak–Rijmen's report; at CRYPTO 2024 Biryukov et al. cut MinRoot's per-step latency from 256 nominal squarings to 6 using 2^54.5 processors (42×), with precomputed tables in the picture. The 2-adic table jump of §4 gives Collatz a **p× latency reduction with 2^p processors (or memory)** — 54× at 2^54 — the same order as the attack that ended MinRoot, and it is built into the map by Terras's theorem, not discovered by cryptanalysis. On the VDF community's current bar, that alone disqualifies raw Collatz iteration.
3. **Partial parallelism is already proved.** Stérin–Woods (RP 2020, arXiv:2007.06979) show that about half the bits of T^i(x), for i = O(log x), are in NC¹ (fast in parallel); the other half are only known to be in P. No P-completeness result exists. So the sequentiality conjecture of §3 is not merely unstudied — for short runs (k ≲ log n) it is partly false, and the honest form of the conjecture is restricted to k ≫ log n, where the parity word depends on bits produced by earlier steps.
4. **The polynomial analogue gives what integers cannot, and loses what they have.** Over F₂[x] (Hicks–Mullen–Yucas–Zavislak 2008; Alon–Behajaina–Paran 2024) every polynomial reaches 1 in a *provable* O(deg^1.5) steps — a predictable delay T — but with no carries the k-step map is linear, so there is nothing sequential to protect.

**Final label: Dead end as a VDF; the parity-vector congruence survives as a cheap certification method for long Collatz computations (Verified), and the sequentiality question for k ≫ log n survives as an open complexity problem (Conjecture) that is interesting independently of cryptography.**

## L13 result: attacking the sequentiality conjecture — no attack found, and the natural tests cannot see one

Script: `scripts/parity_vector_rank.py`; results: `results/parity_vector_rank.json`.

**Communication rank.** Split the input bits 0…j of vⱼ into a low half A and a high half B and take the GF(2) rank of M[A][B] = vⱼ(A + 2^h B). A small rank would mean vⱼ = ⊕ᵢ fᵢ(A)gᵢ(B) with few terms — a divide-and-conquer evaluation from the two halves in parallel.

| j | h | forward rank | inverse rank (control) | full (2^h) |
|---|---|---|---|---|
| 9 | 5 | 17 | 17 | 32 |
| 13 | 7 | 65 | 57 | 128 |
| 17 | 9 | 234 | 194 | 512 |
| 21 | 11 | 814 | 665 | 2048 |

The forward map's rank grows like ~0.4·2^h — exponential, no low-rank decomposition. **But the closed-form inverse, which is a log-depth computation, has the same growth** (665 vs 814 at j = 21; identical ranks over GF(2) and over ℚ). So communication rank, like algebraic degree (§3), is *not* a witness of depth for this pair of maps. A split with a tiny low part (A = bits 0…2) has rank 7 of 8 for all j tested: vⱼ does not factor through a small summary of the low bits either.

**Speculative execution.** With P processors, guess the next log₂P parities in parallel and keep the consistent branch: verified equivalent to the 2^p-table jump, speedup exactly log₂P. No larger speedup was found.

**Status of the conjecture:** open, with no attack and no supporting evidence beyond "nobody knows a shortcut". Two structural measures that might have exposed a parallel algorithm are blind to the one parallel algorithm we know exists (the inverse), so a genuine attack would have to come from the arithmetic — e.g. a way to compose two half-length parity computations using only (s, r) of the first half without its full residue. Label: **Conjecture, untested by any decisive method**.

## L14 result: SNARK cost model — Collatz steps cost 2–86× MinRoot's, for a different kind of hardness

Script: `scripts/snark_cost_model.py`; results: `results/snark_cost_model.json`.

**Verified identities (0 mismatches, k ≤ 4096):** evaluator divide-and-conquer v_high = Φ((3^{s_low}n + r_low)/2^{k/2} mod 2^{k/2}) and verifier divide-and-conquer r(v) = 3^{s_high}r_low + 2^{k/2}r_high, s = s_low + s_high. Consequence: evaluator and verifier have the same *work* (Õ(k) with fast multiplication, Θ(k²/16) with 16-bit limbs); the evaluator's recursion is sequential across halves (depth Θ(k)), the verifier's is not (depth O(log² k)). §6 above has been corrected accordingly: no k-fold smaller statement, only a parallel one.

**Per-step cost of a fixed-width delay step** x → (x + b(2x+1))/2 with b = x mod 2, in an arithmetic circuit over a prime field. The parity bit must be proved consistent with x, which means a bit decomposition (w + 2 constraints) or w/16 lookups into a 2^16 table (+2):

| state width w | bit-decompose | 16-bit lookups | MinRoot | lookups ÷ MinRoot |
|---|---|---|---|---|
| 64 | 66 | 6 | 3 | 2.0× |
| 128 | 130 | 10 | 3 | 3.3× |
| 256 | 258 | 18 | 3 | 6.0× |
| 1024 | 1026 | 66 | 3 | 22× |
| 4096 | 4098 | 258 | 3 | 86× |

MinRoot verifies x_{i+1}⁵ = x_i + y_i in 3 multiplications with no bit operations. Collatz pays for the parity extraction every step; the ternary nature of the gate is irrelevant here (constraints live in a prime field).

**Whole statement, k steps of the k-bit parity vector:** step-by-step k(k/16 + 2) vs congruence ≈ 2k(k/16) + inverse: ratio 0.5 at every k from 2¹⁰ to 2¹⁶ — same order, the congruence slightly *more* constraints, because r(v) is a k-term sum of k-bit numbers.

**Reading.** As a STARK-proved VDF, Collatz-mod-2^w is 2–6× more expensive per step than MinRoot at practical widths (64–256 bits), with the one compensating property that its hardness — if it exists — is *bit-level*, not algebraic: the parity branch is exactly what makes the map non-algebraic over the field, so the algebraic attacks that hit MinRoot's assumption do not transfer. That is a real design difference, not a demonstrated advantage. Label: **Conjecture-grade design note; not a dead end, not a recommendation.** It would become interesting only with (a) a sequentiality argument for the parity-vector map and (b) a proof system with cheap bit operations (binary-field STARKs such as Binius change this table; the literature note should say whether they do).

## Follow-ups (added to the loop)

- **L13.** Try to *break* the sequentiality conjecture: search for a divide-and-conquer or NC algorithm for the parity vector (e.g. via the mixed-radix form −n·3^s ≡ Σ 2^i 3^{ones after i}); test whether v for the top half of a block can be computed from partial information about the bottom half. A negative result is evidence; a positive one is a theorem.
- **L14.** Cost model: constraints per step for a Terras-step STARK vs the congruence statement, to quantify §6.

## Sources

1. R. Terras, "A stopping time problem on the positive integers", Acta Arith. 30 (1976) — parity vectors, bijection, affine formula.
2. D. Boneh, J. Bonneau, B. Bünz, B. Fisch, "Verifiable Delay Functions", CRYPTO 2018 — https://eprint.iacr.org/2018/601
3. A. K. Lenstra, B. Wesolowski, "A random zoo: sloth, unicorn, and trx", 2015 — https://eprint.iacr.org/2015/366
4. [[VDF Literature - Sequential Functions]] (sub-agent survey; constructions, attacks, Collatz-in-crypto search, F₂[x] analogue).
5. [[Collatz Bridge - Trits and Stopping Times]], [[Minimal Ternary Circuit]], [[Experiment A - Ternary Dropping-Set Classifier]], [[Exact Admissible Sequence DP]].
6. `scripts/parity_vector_vdf.py`, `results/parity_vector_vdf.json`.
