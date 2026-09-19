---
tags: [pinball, stopping-vector, affine-orbit-structure]
status: verified
created: 2026-09-19
jira: SCRUM-30
---

# Pinball Model

Every claim is labelled **Verified** (test or proof in this repo), **Analogy** (a way of speaking, no mathematical content beyond what is stated) or **Dead end**.

## The dictionary

| Pinball | Collatz | Code |
|---|---|---|
| Launch / flip | choose n | `launch_integer(bits)` |
| Bumper | odd step, n → (3n+1)/2 | `BUMPER` in `collatz/pinball/table.py` |
| Gravity | even step, n → n/2 | `GRAVITY` |
| Drain | first time 3^s < 2^j (coefficient stopping time) | `PinballTable.play` |
| Lane | parity word up to the drain | `PinballTable.lane` |
| Table | a qx+c map; classical is q=3, c=1 | `PinballTable(q, c, depth)` |
| Trajectory | stopping vector (n, *stopping_orbit(n)) | `stopping_vector` |

## Stopping vectors are lattice lines — Verified

`stopping_vector(5) = [5, 16, 8, 4]`, a point of ℤ⁴ in stopping class 3.

By the [[Affine Orbit Structure]], every coordinate of the stopping vector is affine in n inside a residue subgroup. So a subgroup of Set_k is a **lattice line** in ℤ^(k+1):

    stopping_vector(residue + j·P) = base + (j − j₀)·direction,   P = 2^(k−s)

For Set_3: base `[5, 16, 8, 4]`, direction `[4, 12, 6, 3]`, giving `[9, 28, 14, 7]`, `[13, 40, 20, 10]`, …

- Direction component i is `P · 3^(odd steps before i) / 2^(halvings before i)` — always an integer (`subgroup_direction`).
- `class_coordinates(n) = (k, s, residue, j)` is the "unique factorization within the class". `vector_from_coordinates` inverts it without running the target's orbit. Round trip tested for every n in 2..4095.
- A stopping class is a bundle of N(s) parallel-in-slope lines (N(s) = OEIS A100982, see [[Lattice Path Formula]]). All lines of one class share the last-coordinate slope 3^s/2^(k−s).

So "a dimension in which you can play" is exact: within a class the playable freedom is **one integer j per line, plus the choice of line**. The ambient dimension k+1 is large, but the class occupies only a 1-dimensional lattice in it.

## The table is a Sturmian billiard — Verified (inherited)

The set of reachable classes (3, 6, 8, 11, 13, 16, …) has gaps 3, 2, 3, 2, 3, 3, … = the Sturmian cutting sequence of slope log₂3 (`docs/Explorations/Dropping Zeta Spectrum.md`, Parts 6–7). A cutting sequence of irrational slope is precisely the bounce sequence of a billiard ball in a square. The pinball picture is therefore not loose: the class spectrum is a billiard trajectory.

## A lane is a residue class — Verified

The first j parities depend only on n mod 2^j (`test_lane_depends_only_on_low_bits`), and the map (n mod 2^j) ↦ (first j parities) is a bijection (Terras). Consequences used in [[Integer Decision Model]]:

1. A drained lane is exactly one affine subgroup.
2. Played to full depth D with no early drain, the table partitions inputs **identically** to reading the low D bits. The dynamics add no information beyond the bits; the only Collatz-specific choice is *where to stop reading*.
