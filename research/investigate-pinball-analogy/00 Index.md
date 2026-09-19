---
tags: [pinball, index]
status: complete
created: 2026-09-19
jira: SCRUM-30
---

# Investigate Pinball Analogy (SCRUM-30)

Three questions from the ticket, with the answers this vault reaches.

| Question | Answer | Note |
|---|---|---|
| Can a pinball machine be modelled with stopping orbits as vectors? | **Yes, exactly.** Each subgroup of a stopping class is a lattice line in ℤ^(k+1); (k, s, residue, j) are unique coordinates; the class spectrum is a Sturmian billiard. | [[Pinball Model]] |
| Does it resemble quantum physics / action in a Hilbert space? | **Hilbert space yes, quantum no.** The Koopman operator of the Terras map is an isometry on L²(ℤ₂) and classes are orthogonal vectors. No phases, no interference, no Bell violation. | [[Hilbert Space and the Quantum Analogy]] |
| Can a Jev-style model be built from integers and Collatz primitives, for more than Collatz? | **An integer-only System One model works. Collatz routing is optimal for Collatz questions and a handicap elsewhere** — by the Terras bijection it can never see more than the low bits do. | [[Integer Decision Model]] |

Follow-up question — can composition rules guarantee no machine runs forever? **No: composition is free (any arrangement is played by some 2-adic ball). The structure is a provable fractal (nesting theorem, never-drain set of dimension 0.95), and the conjecture is that this fractal holds no positive integer > 1.** See [[Nesting and the Never-Drain Fractal]].

Second follow-up — replace halving with n → n − |n/2|? **Positives unchanged; negatives become an injective, always-escaping map that converts 2s into 3s. Its "age classes" are the 3-adic mirror of stopping classes, with P(age ≥ t) = F(t+3)/(2·3^t) exactly. It does not weaken the barrier.** See [[The Mirror Table]] and [[Mirror Experiments]] (ten experiments, a proof that the law is F(t+3)/(2·q^t) for every odd q, and a literature check: closest prior art is Reyes Jiménez arXiv:2606.02621, which E10 shows is the forward dual. Its Open Question 1 — every n > 1 eventually halves twice in a row — is verified here for all n < 2⁴⁰).

Third follow-up — signed prime factorizations? **The sign choices are the unit group: invisible to any map on n. The real structures are units and Galois conjugation in ℤ[ω] (3n+1 = π·π̄·n + 1 is invariant under π ↔ π̄). In factor language the mirror step exchanges a 2 for a 3 and conserves Ω. An exchange family joining Collatz to the mirror has a phase transition at p_c = 0.1309 (every 7th halving escapes, every 8th drains).** See [[Signed Primes and the Exchange Family]].

Also: [[Jev and System One Models]] — what Jev is, and why it is never used as a teacher (its customer agreement prohibits distillation and benchmarking).

## Headline numbers

- Task A (Collatz): pinball 0.9834 accuracy vs exact Bayes ceiling 0.9854; ECE 0.039 vs 0.294 for the fixed-depth control.
- Task B (boolean): fixed-depth control beats 3x+1 routing on all four tasks by 8–26 points.
- Task C (SMS spam, majority 0.868): best pinball 0.909, naive Bayes 0.885, decision tree 0.934.
- Distillation: soft labels add +0.9 to +4.7 points; on SMS the distilled student (0.899) beats its teacher (0.885), one split.

## Files

- `collatz/pinball/` — `vectors.py`, `table.py`, `encode.py`, `model.py`, `baselines.py`, `hilbert.py`, `nesting.py`, `mirror.py`
- `tests/test_pinball.py` — 35 tests
- `scripts/mirror_experiments.py` — E1–E10 on the mirror table (≈ 2 min)
- `scripts/double_halving_search.py [B]` — exhaustive Fibonacci-tree search (B = 40 in ≈ 4 min)
- `scripts/signed_prime_experiments.py` — E15 exchange family, E16 Liouville signs
- `scripts/banerji_backward_search.py`, `scripts/double_halving_rs/` — tree searches (Python, Rust)
- `scripts/pinball_experiments.py` — `python -X utf8 scripts/pinball_experiments.py [A] [B] [C]` (A and B together ≈ 2 min; C a few minutes more)
- `results/pinball_experiments.json` — raw numbers

## Follow-ups (not done)

- Notebook `19-pinball-stopping-vectors.ipynb` (geometry plots, reliability diagrams).
- Site playground for the table.
- Integer temperature calibration; per-member hashing; hill-climbed bit orders; a torch float teacher.
