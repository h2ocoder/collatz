---
tags: [loop, agenda, ternary, collatz]
status: running
created: 2026-09-16
---

# Exploration Loop — Agenda and Progress

Self-paced loop continuing SCRUM-28. Each iteration: take the first unchecked item, do it end-to-end (script → result → note), tick it here, append a dated entry to **Progress log** below, `task.log` the finding, commit. Every claim gets a label: Verified / Conjecture / Analogy / Dead end. A negative result is a result; record it and move on. If an item is going badly after ~30 min of compute, write what was learned, tick it as "partial", move on.

Environment: `C:\repos\collatz\.venv\Scripts\python.exe`, RTX 4080 via CUDA torch. Scripts go in `scripts/`, results (npz/png/json) in `results/`, notes in this folder, linked from [[00 Index]].

## Agenda (ordered by value ÷ cost)

### Tier 1 — exact number theory, no ML (each < 1 hour)
- [x] **L1. Exact N(s) to s = 300 by dynamic programming.** DP over (i, partial sum) with the constraint Σ < i·log₂3 (exact via 3^i > 2^Σ). Reproduce OEIS A100982 to the b-file, compute the Kraft sum Σ N(s)/2^(b(s)−1) → 1, and Wagon's constant Σ k(s)N(s)/2^(b(s)−1) to ≥ 10 digits (target 9.4779555565…). Note: `Exact Admissible Sequence DP.md`.
- [x] **L2. Is E[w(s)] = 1/2?** With L1's exact densities, compute E[w(s)] = E[bits shed at first drop] to convergence (partial sums gave 0.447). Compare with 1/2 (equidistribution) and with the Sturmian mean of {s log₂3} under the dropping-set measure. Bias ⇒ drops are systematically tighter packings than random. Label the answer.
- [x] **L3. Winkler tail bound.** Does (1/s)·C(⌊s log₂3⌋, s−1)·2^(−(b(s)−1)) sum to a finite tail, and how fast? Compute the fraction of odd n undecided by mod 2^p from the bound vs the exact DP vs the repo's empirical 89% at mod 4096. Turn into an explicit "fraction undecided ≤ f(p)" statement.
- [ ] **L4. Apply OEIS citations to the repo docs.** Add A100982 / A122437 / A122790 / A020914 and Winkler's bounds to `docs/Conjectures/Lattice Path Formula.md` and `Odd Stopping Time Spectrum.md` (a "Prior art" section each, minimal edits). This is the SCRUM-28 follow-up.

### Tier 2 — ternary networks on Collatz (GPU, each 1–3 hours)
- [ ] **L5. Proposal A — ternary dropping-set classifier.** Input: low 12 bits of odd n (one-hot ±1). Output: dropping set (classes 3, 6, 8, 11, 13, 16, 19, "≥21"). Model: 1–2 hidden layers with BitNet-style absmean ternary weights + straight-through estimator. Questions: (i) test accuracy vs bits shown — does it hit the 2-adic ceiling (class 3 needs 2 bits, 6 needs 4, 8 needs 5, 11 needs 7, 13 needs 8, 16 needs 10, 19 needs 12)? (ii) Are the ternary first-layer weights readable as residue tests (±1 on a bit = constraint, 0 = don't care)? Compare to the known residue classes. (iii) Zero density of the learned weights. Note: `Experiment A - Ternary Dropping-Set Classifier.md`.
- [ ] **L6. Proposal A′ — learning order.** Same setup, log per-class accuracy over training. Does the net learn classes in order of k (i.e. of register size b(s)), like Charton & Narayanan's transformer learns (k,k′) in order of k+k′? Add to the L5 note.
- [ ] **L7. Proposal B — base polarity on the one-step and long-step tasks.** Small transformer (≤ 4 layers) on Syracuse step and on Charton's long step, input bases 2, 3, 6, 16, 24. Does base 6 (the repo's lattice base) sit anywhere special? Does the one-step task really show the opposite polarity to the long-step task (arXiv:2604.13082 vs 2511.10811)? Note: `Experiment B - Base Polarity.md`.
- [ ] **L8. Proposal C — probe for the affine map.** In the L7 long-step model, linear-probe the residual stream for k, k′, and the intercept C. Does the model represent (k, k′) before it computes the output? Add to the L7 note.
- [ ] **L9. Ternary vs full-precision on L7.** Re-run the best L7 config with ternary weights (same STE as L5). Stratify accuracy by (k, k′). Does quantization damage control-flow depth (large k+k′) before arithmetic? This is a laptop-scale version of Proposal D. Note: `Experiment D - Quantization by Subgroup.md`.

### Tier 3 — the circuit (cheap, do when a GPU run is in flight)
- [ ] **L10. Minimal ternary Syracuse circuit.** Can the 11-unit layer be reduced (e.g. merge parity/majority via a single 3-input unit with two thresholds)? Exhaustive search over ≤ 6-unit ternary threshold layers for the Terras transducer. Report the minimum and whether any optimal circuit uses a zero weight.
- [ ] **L11. Does a trained ternary RNN find the transducer?** Train a ternary-weight recurrent net (STE) on LSB-first bit streams n → T(n). Does it converge to a carry transducer, and do its weights match L10's minimal circuit up to symmetry?

### Tier 4 — write-up
- [ ] **L12. Update `Summary - Findings and Open Questions.md` and [[00 Index]]** with everything above; refresh SCRUM-28 and close the ACE task log with a final outcome.

## Progress log
<!-- newest first; one entry per iteration: date/time, item, result in one or two lines, files touched -->
- **2026-09-16 (L3)** — Winkler's bounds hold exactly to s = 1000. Sharp rate of the undecided fraction: U(p) = 2^(−(1−H(1/log₂3))p + o(p)) = 2^(−0.0500 p); explicit U(p) ≤ 0.756·2^(−0.05004 p) for p ≤ 1200 (conditional on Winkler's upper bound). Surprise: N(s) = C(m,s−1)/s EXACTLY at s = 1, 3, 5, 17, 29, 41, 94, 147, 200, 253, 306, 971 — precisely the record trit packings (cycle lemma); elsewhere N/upper is a step function of w(s) with breakpoints at w(1) = 2 − log₂3, w(3), w(2) — this is the L2 residual explained. Files: `scripts/winkler_tail.py`, `results/winkler_tail.json`, `Winkler Tail Bound.md`. Labels: Verified (rate, equality cases to 1000); Conjecture (iff with semiconvergents; Sturmian form of F).
- **2026-09-16 (L2)** — E[waste at first drop] = 0.4496, biased below 1/2 in every s-window (0.44–0.47) while the unweighted mean of w is 0.50. Exact identity dens(s) = 2·(N(s)/3^s)·2^(−w) makes the measure Gibbs-tilted at ln 2 per wasted bit, predicting 0.4427 — explains most of it. Residual: N(s)/3^s itself anti-correlates with w (corr −0.54, non-monotone) → Sturmian-prefix dependence, left as Conjecture. Files: `scripts/waste_bias.py`, `results/waste_bias.json`, `Waste Bias at First Drop.md`.
- **2026-09-16 (L1)** — DP for N(s) exact to s = 1000 in 0.5 s; matches OEIS A100982 b-file at n = 20, 30, 50, 100, 200 (all digits). Kraft sum → 1 (1 − 4×10⁻²⁸ at s = 1000). Wagon's constant = 9.477955556559 (12 digits, matches A122790). E[s] = 3.4927, E[halvings] = 5.9853, E[waste] = 0.4496. Repo's "89% by mod 4096" is exactly 911/1024. Files: `scripts/admissible_dp.py`, `results/admissible_dp.json`, `Exact Admissible Sequence DP.md`. Label: Verified.
