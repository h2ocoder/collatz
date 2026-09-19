---
tags: [pinball, hilbert-space, koopman, quantum-analogy]
status: verified-with-limits
created: 2026-09-19
jira: SCRUM-30
---

# Hilbert Space and the Quantum Analogy

Question from the ticket: does the pinball model resemble quantum physics and action in a Hilbert space?

Short answer: there is a genuine Hilbert space and a genuine operator on it. There is nothing quantum about the dynamics.

## What is mathematics

**Verified — the Terras map preserves Haar measure on ℤ₂.** At resolution 2^B, T: ℤ/2^B → ℤ/2^(B−1) is exactly 2-to-1 (`terras_preimage_counts(10) == {2}`, also for 5x+1). This is classical (Terras 1976, Lagarias 1985); the finite check is ours.

**Verified consequence — the Koopman operator is an isometry.** U f = f∘T acts on L²(ℤ₂, Haar) and preserves norms. That is "action in a Hilbert space" in the literal sense. U is an isometry, not unitary: T is 2-to-1, so U is not onto. T is conjugate to the one-sided Bernoulli shift on parity sequences, and U is the shift's Koopman operator.

**Verified — stopping classes are orthogonal vectors.** Classes are disjoint unions of residue classes, so their indicator functions are orthogonal in L²(ℤ₂). Squared norms are the class densities: 1/2 (class 1, even n), 1/4 (class 3), 1/16 (class 6), 1/16 (class 8), … summing to 1 (`class_densities`). A probability distribution over classes is a unit vector in this basis.

**Verified — the model's output is a vector in that picture.** A lane posterior is a normalized count vector over answers; ensemble combination is an exact average of such vectors.

## What is analogy only

**Analogy — "measurement".** Reading low bits refines which lane the ball is in, the way a measurement refines a state. But the refinement is ordinary conditioning of a classical probability measure. Nothing is disturbed by reading.

**Analogy — "superposition" of lanes.** A caught (undrained) ball has a distribution over deeper classes. That is ignorance of high bits, not amplitude. There are no phases and no interference: probabilities add, amplitudes never appear.

**Dead end — entanglement / Bell violation.** Already settled in `docs/Conjectures/Collatz Complementarity Principle.md`: CHSH S ≈ 0.08, no violation, and the affine intercept C is a valid local hidden variable. The pinball picture does not change this. Do not reopen.

**Dead end — non-commuting observables.** All observables here are functions on ℤ₂ and commute. The "uncertainty relation" in the Complementarity note is a bandwidth limit, not a commutator.

## Where a real operator-theoretic question lives

The transfer (Perron–Frobenius) operator is the adjoint of U. Its spectrum is what the repo's spectral-gap result (λ₂ → 1/6) measures on finite quotients. That is the rigorous version of "quantum-like" structure in this project, and it is where further work belongs — see `site/connections/hilbert-polya.md` and the negative result in Part 1 of `Dropping Zeta Spectrum.md`.
