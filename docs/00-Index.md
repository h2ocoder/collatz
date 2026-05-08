# Collatz Exploration Index

## Definitions
Core concepts from the research papers:
- [[Dropping Time]]
- [[Dropping Destination]]
- [[Dropping Orbit]]
- [[Dropping Set]]
- [[Dropping Modulus]]
- [[Dropping Index]]
- [[Dropping Genus]]
- [[Orbital Oddity]]
- [[Stopping Time]]
- [[Stopping Destination]]
- [[Stopping Orbit]]
- [[Stopping Point]]
- [[Stopping Class]]
- [[Stopping Modulus]]
- [[Stopping Page]]
- [[Stopping Offset]]
- [[Stopping Signature]]
- [[Collatz Address Space]]
- [[Orbital Triple Mapping]]
- [[Complex Multiplier]]
- [[Proportional Power Ratio]]

### Syracuse / Odd-Only Dynamics
- [[Syracuse Map]]
- [[Alpha Value]]
- [[Alpha Sequence]]
- [[2-adic Valuation]]

## Explorations
Findings from notebook investigations:
- **Odd Stopping Time Spectrum**: Only stopping times of form ceil(s * log2(6)) are possible for odd numbers. Gap classes (4, 5, 7, 9, 10, ...) are impossible. Verified for n < 200,000.
- **2-Adic Determinism**: Each stopping class is a union of residue classes mod 2^p. Fraction resolved converges to 1 (89% by mod 4096).
- **Syracuse Multiplication Table**: For semiprimes pq, class(pq) partially determined by factor classes. Non-class-3 x non-class-3 always gives class 3.
- **Affine Orbit Invariants**: Within each residue subgroup of Set_k, orbit sum, max, and destination are exact affine functions of n. The destination slope 3^s/2^(k-s) is universal across all subgroups of a given k.
- **Dual Constraint (2-adic x 3-adic)**: Membership in Set_k is 2-adic (mod 2^(k-s)), but destinations are locked to a single residue mod 3^s. Combined modulus = 2^(k-2s) · 6^s — the base-6 lattice reappears.
- **Transition Graph Connectivity**: The dropping set transition graph is fully connected (every Set_k can reach every Set_j), proved via gcd(3^s, 2^m) = 1. No forbidden pairwise transitions exist.
- **Logarithmic Escape**: Self-chains (consecutive drops within the same Set_k) are bounded by log_P(n) where P = 2^(k-s), via modular tightening. Much stronger than the contraction ratio bound.
- **Ascending Convergent Elimination**: All cycle candidates with 3^S > 2^E eliminated (C>0 forces n<0). Half of all convergents killed for free.
- **First Convergent Eliminated**: No 13-step cycle exists. All 91 parity words checked; none have 13 | C. Gap=13 ruled out.
- **Divisibility Obstruction Conjecture**: For gap g = 2^E - 3^S > 1, g never divides 2^E * C. Would prove no non-trivial cycles.

## Research Plans
- [[path-to-proof]] — structured roadmap toward proving the Collatz conjecture

## Conjectures & Theorems
- [[Orbital Oddity Conjecture]]
- [[Stopping Point Line Conjecture]]
- [[Odd Stopping Time Spectrum]] — k = ceil(s * log2(6)), base-6 emerges naturally
- [[Affine Orbit Structure]] — dest(n) = (3^s / 2^(k-s))·n + C within each subgroup, proved by induction
- [[Logarithmic Escape Theorem]] — self-chains in any Set_k bounded by O(log n) via modular tightening
- [[Bit Destruction Bound]] — bits destroyed per drop = 1 - {s·log₂3}, bounded by Roth's theorem; 3-adic mixing proved
- [[Multiplication Symmetry Theorem]] — P(shift=+s) = P(shift=-s) under x3; mod-4 wall partitions odd numbers
- [[Lattice Path Formula]] — N(s) = lattice paths below y = x·log₂(3); explains subgroup counts 1,2,3,7,12,30,85,...
- [[Collatz Complementarity Principle]] — narrow bandwidth creates mod-p uncertainty relations; C as hidden variable
- [[Eisenstein Factorization]] — 3n+1 = pi*pi_bar*n+1 in Z[omega]; decouples into period-12 angular + radial dynamics
- [[Sector Monotonicity]] — within each Eisenstein sector, orbit values strictly decrease; 135K revisits, 0 violations
- [[Proof Attempt - Adelic IFS Bridge]] — reduces Collatz to absolute continuity of a self-similar measure via Siegel's Hydra framework

## Papers
1. "The Collatz Conjecture, Pythagorean Triples, and the Riemann Hypothesis" — Dropping Sets, Genus, Orbital Triples, Complex Plane
2. "The Geometric Collatz Correspondence" — Stopping Classes, Signatures, Diophantine Lines, Circles
3. "A New Perspective on an Old Problem" — Proportional Power Ratios, Base-6 Lattice, Polar Plots
