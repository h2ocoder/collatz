---
layout: home
hero:
  name: Collatz Research
  text: Toward a Proof
  tagline: New structural results on the Collatz conjecture using affine orbit theory, modular arithmetic, and connections to the abc conjecture.
  actions:
    - theme: brand
      text: Read the Proofs
      link: /proofs/affine-orbit
    - theme: alt
      text: Path to Proof
      link: /roadmap/path-to-proof

features:
  - title: Affine Orbit Structure
    details: Every drop through a dropping set is an exact affine map. Proved by induction.
    link: /proofs/affine-orbit
  - title: Logarithmic Escape
    details: No orbit can stay in one dropping set for more than O(log n) steps.
    link: /proofs/logarithmic-escape
  - title: Bit Destruction Bound
    details: Every drop destroys β(s) = 1 − {s·log₂3} bits. Connected to Roth's theorem.
    link: /proofs/bit-destruction
  - title: Cycle Elimination
    details: Half of all convergents killed by sign. First non-trivial convergent (gap=13) eliminated.
    link: /cycles/convergent-elimination
---

::: tip What's New (April 2026)
Six new structural results proved, including the Affine Orbit Structure theorem, Logarithmic Escape bound, and the first computational elimination of a non-trivial cycle candidate (gap=13). See the [roadmap](/roadmap/path-to-proof) for the full picture.
:::

## The Research

This work approaches the Collatz conjecture through three complementary lenses:

1. **Dropping Sets, Pythagorean Triples & Riemann** (Paper 1) — Classification of integers by dropping time, orbital triples, complex multipliers
2. **Stopping Classes & Geometric Correspondence** (Paper 2) — Diophantine lines, stopping signatures, geometric structure
3. **Proportional Power Ratios** (Paper 3) — Base-6 lattice, polar structure, the log₂6 spectrum

The results on this site unify these perspectives through the **affine orbit framework**, revealing that every Collatz drop is a computable linear map whose properties connect to deep number theory (Roth's theorem, the abc conjecture, S-unit equations).
