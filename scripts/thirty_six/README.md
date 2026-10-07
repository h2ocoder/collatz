# Thirty-six: what do the facts about 36 = 2²·3² say about Collatz?

Run of 2026-10-06. Synthesis: `docs/Explorations/Thirty-Six.md`.

Five threads, one per directory. Each was investigated by one researcher and then re-derived by a
skeptic with separate code (`verify/` in each directory), who also ran the 3x−1 and 5x+1 controls,
searched prior art and corrected the thread README in place. Every thread README ends with a
"Skeptic pass" section listing what was changed and what was not checked.

| Directory | Fact about 36 | Headline (after the skeptic pass) |
|---|---|---|
| `golden_kernel/` | cos 36° = φ/2 | The 3x+1 residue chain modulo 5 has an exact three-cell quotient that is a pentagon walk folded along a mirror, so it mixes at cos 36°. N = 5 is the only modulus with an all-real spectrum (proved). The exceptional prime 11 is explained; 31, 37, 41 are not. |
| `harmonic_cycles/` | triangular and square | 36 = T₈ is the triangular number of the unit cell 9 − 8 = 1, which holds the cycle {−5, −7, −10}. The word 1ᵃ0 closes on an integer iff 6ᵃ is triangular (a ≤ 2). Prior art re-assembled (Gersonides, Davison, Steiner). |
| `figurate_2adic/` | triangle, square, cube | Three exact 2-adic types: fold, collapse, isometry. Triangular numbers carry the natural dropping-class law exactly. Squares meet two classes for 3x+1 and infinitely many for 3x−1. |
| `totient_lattice/` | eight solutions of φ(x) = 36 | Solutions of φ(x) = 2ᵃ3ᵇ are counted by a generating function over Pierpont points; 8 = 1 + 2 + 3 + 2 at (2,2). The n-gon needs a − 1 square roots and b trisections. Collatz side: null. |
| `nicomachus_paths/` | 1³ + 2³ + 3³ | n → Σ_{d\|n} τ(d) is completely solvable with attractors 1, 3, 18, 36, {6, 9}. The structure of A100982 along the convergents of log₂3 is Winkler, arXiv:2609.22303; Bizley closed forms at multiples of convergent denominators are added. |

Nothing here is a step toward the conjecture: every Collatz-facing statement is sign-blind
(identical for 3x−1) or residue-only.

Run any script from its own directory with
`C:/repos/collatz/.venv/Scripts/python.exe -X utf8 <script>.py`; each writes a `.log` or `.json`
next to itself.
