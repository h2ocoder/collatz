# Collatz Exploration Repo

## Project overview
Mathematical exploration of the Collatz conjecture through three research lenses:
1. **Dropping Sets / Pythagorean Triples / Riemann** (Paper 1)
2. **Stopping Classes / Geometric Correspondence** (Paper 2)
3. **Proportional Power Ratios** (Paper 3 / Medium article)

New research direction: investigating whether Collatz classification of composites relates to their prime factors' classifications.

## Repo structure
- `collatz/` — Core Python library (core, dropping, stopping, geometry, factorization, utils)
- `notebooks/` — Jupyter notebooks for systematic exploration (00-05)
- `docs/` — Obsidian vault with definitions, explorations, conjectures
- `my-writings/` — Original research papers (PDFs)

## Conventions
- Python 3.12, using existing `.venv`
- Use `from fractions import Fraction` for exact arithmetic where precision matters
- All classification functions should work on single integers and support batch operations returning DataFrames
- Notebooks numbered 00-05, prefixed with their purpose
- Obsidian docs use `[[wikilinks]]` for cross-referencing

## Key terminology mapping
| Paper 1 (Dropping)     | Paper 2 (Stopping)      | Same concept?          |
|------------------------|-------------------------|------------------------|
| Dropping Time          | Stopping Time           | Yes — steps to first < n |
| Dropping Destination   | Stopping Destination    | Yes — first value < n  |
| Dropping Set_k         | Stopping Class_k        | Yes — all n with time=k |
| Dropping Modulus       | Stopping Modulus         | Yes — inner subsets    |
| Dropping Index         | Stopping Page + Offset  | Related               |
| Dropping Genus (S,M,I) | Stopping Signature (T,P,O) | Analogous tuples    |
| Orbital Oddity         | —                       | Paper 1 only          |

## Running
```bash
.venv/Scripts/python.exe -m pip install -e .
.venv/Scripts/python.exe -c "from collatz import core; print(core.orbit(27))"
```
