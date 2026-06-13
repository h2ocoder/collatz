# How Large a 3x+1 Cycle Must Be

A self-contained derivation of lower bounds on any nontrivial Collatz cycle, via
the dropping dictionary.

**Honest scope.** This is a *lower bound*, not a proof that no cycle exists
(that is open). Conditional on the standard computational verification (no cycle
below `B = 2^68`), every nontrivial `3x+1` cycle has:

- at least **72,057,431,991** odd elements,
- a full period of at least **1.86 × 10¹¹** steps,
- least element at least **2^68 ≈ 2.95 × 10²⁰**.

These coincide with the published bounds of Eliahou and Hercher; the contribution
is the clean, elementary packaging and the link to the continued fraction of
`log₂3` that governs the base-6 rotation.

## Files
- `collatz-cycle-bounds.tex` — the paper (LaTeX).
- `collatz-cycle-bounds.pdf` — compiled, 5 pages.

## Build
```bash
tectonic collatz-cycle-bounds.tex      # or: pdflatex collatz-cycle-bounds.tex (x2)
```

## Reproduce the numbers
```bash
.venv/bin/python scripts/verify_cycle_bound.py
```
Checks the closed-word equation, the product identity and geometric-mean bound
(exact on the trivial cycle), and recomputes the simplest fraction in the forced
interval at 120-digit precision.

## Prize
The author offers **US$25** to the first person who finds a genuine mathematical
error in the argument (Sections 2–3 and Theorem 1). See §7 of the paper.
"Already known" does not qualify — the prior art is cited; the claim is
correctness, not novelty.
