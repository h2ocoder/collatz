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
- [ ] **L1. Exact N(s) to s = 300 by dynamic programming.** DP over (i, partial sum) with the constraint Σ < i·log₂3 (exact via 3^i > 2^Σ). Reproduce OEIS A100982 to the b-file, compute the Kraft sum Σ N(s)/2^(b(s)−1) → 1, and Wagon's constant Σ k(s)N(s)/2^(b(s)−1) to ≥ 10 digits (target 9.4779555565…). Note: `Exact Admissible Sequence DP.md`.
- [ ] **L2. Is E[w(s)] = 1/2?** With L1's exact densities, compute E[w(s)] = E[bits shed at first drop] to convergence (partial sums gave 0.447). Compare with 1/2 (equidistribution) and with the Sturmian mean of {s log₂3} under the dropping-set measure. Bias ⇒ drops are systematically tighter packings than random. Label the answer.
- [ ] **L3. Winkler tail bound.** Does (1/s)·C(⌊s log₂3⌋, s−1)·2^(−(b(s)−1)) sum to a finite tail, and how fast? Compute the fraction of odd n undecided by mod 2^p from the bound vs the exact DP vs the repo's empirical 89% at mod 4096. Turn into an explicit "fraction undecided ≤ f(p)" statement.
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
