# Orbit Structure Exploration — Design

## Goal

Explore element-wise relationships between orbits of numbers sharing the same (dropping set, dropping modulus) classification. Numbers in the same group follow identical odd/even step patterns, producing orbits of equal length with structurally parallel trajectories. We want to discover invariants, ratios, modular equivalences, or other patterns that might reveal axiomatic properties of Collatz dynamics.

## New Module: `collatz/orbits.py`

### Functions

1. **`class_members(set_k, modulus_m, limit)`** → `list[int]`
   - Returns all integers in `[2, limit)` with `dropping_set == set_k` and `dropping_modulus == modulus_m`.
   - Uses `dropping.classify_range()` for efficiency.

2. **`aligned_orbits(members)`** → `pd.DataFrame`
   - Rows = members, columns = orbit positions `[0, 1, ..., length-1]`.
   - Uses `dropping.dropping_orbit()` for each member.
   - All members in the same (set, modulus) group produce orbits of equal length.

3. **`pairwise_ratios(orbit_df)`** → `pd.DataFrame`
   - Computes `orbit[j][i] / orbit[0][i]` for each member `j` relative to the first member (row 0).
   - Uses `fractions.Fraction` for exact rational values.

4. **`pairwise_differences(orbit_df)`** → `pd.DataFrame`
   - Computes `orbit[j][i] - orbit[0][i]` for each member `j` relative to the first member.

5. **`modular_equivalences(orbit_df)`** → `pd.Series`
   - For each column (orbit position), finds the largest modulus `m` such that all values in that column are congruent mod `m`.
   - Returns a Series indexed by position.

6. **`orbit_summary(set_k, modulus_m, limit)`** → `dict`
   - Convenience function: calls `class_members`, `aligned_orbits`, `pairwise_ratios`, `pairwise_differences`, `modular_equivalences`.
   - Returns `{"members", "orbits", "ratios", "differences", "modular"}`.

### Dependencies

- `collatz.dropping`: `dropping_set`, `dropping_modulus`, `dropping_orbit`, `classify_range`
- `fractions.Fraction` for exact ratios
- `pandas` for DataFrames
- `math.gcd` for modular equivalence computation

## New Notebook: `notebooks/06-orbit-structure.ipynb`

### Sections

1. **Setup** — imports, select 2-3 (set, modulus) groups of varying dropping time
2. **Orbit alignment** — display aligned orbit matrix, verify step patterns match
3. **Ratio analysis** — heatmap of ratios across positions; check for constancy, convergence, rational structure
4. **Difference analysis** — plot differences, compute GCDs per column, check for smooth factorizations (2^a * 3^b)
5. **Modular equivalences** — bar chart of modulus per position, look for growth/decay patterns
6. **Cross-group comparison** — repeat for a second group, check universality vs group-specificity
7. **Observations** — summarize findings

## Out of Scope

- Reshaping orbits into multi-dimensional arrays (future work)
- Statistical tests or automated pattern detection
- Merkle/hash tree structures
- Changes to existing modules
