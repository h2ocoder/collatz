---
tags: [schwarzschild, index]
status: complete
created: 2026-11-02
jira: SCRUM-65
---

# Information-Theoretic Schwarzschild Radius (SCRUM-65)

The question: find the information-theoretic version of r_s = 2GM/c² from its definition, with corollaries for radius, mass, gravity and the speed of light, and see what it says about Collatz-like functions and toy physics.

| Question | Answer | Note |
|---|---|---|
| What is the Schwarzschild radius here? | **The address depth that can carry a lift.** r_s(M) = θM + O(1) bits, and in the weak field it has the form 2GM/c², with c the step spread σ. Counting candidates, the largest lift among B-bit integers sits near r_s(M) = B. | [[The Schwarzschild Dictionary]] |
| Speed of light? | **Address digits read per step**, c = log₂ d, the same on every branch. An exact causal cone. | [[Information Radius]] |
| Gravity? | **Drift**, g = 0.2075 bits per step for 3x+1, the same for every n. | [[Information Radius]] |
| Mass? | **Lift** in address space, **the offset** in value space. Captured integers grow as Σa, with Σ = 1.8137 (lower bound proved, constant measured). | [[Word Horizons]] |
| Radius? | **Address depth** in address space, **the value** in value space. | [[The Schwarzschild Dictionary]] |
| Where does bit destruction fit? | **In the denominator.** A word's horizon is F = ζ/(2^β − 1), and the 1 − r_s/r factor is an exact identity. | [[Word Horizons]] |
| Anything about Collatz-like maps in general? | **Yes.** Five phases, a hard horizon below q = d, q = d + 1 always exactly critical, peak ≈ n^(1 + 1/θ) on twelve maps. | [[Collatz-like Maps in General]] |
| Toy physics? | **The 2D dilaton black hole fits best**, with the same metric function. Acoustic horizons, a barometric atmosphere and a reversible tape fit parts. | [[Toy Physics Systems]] |
| Is it a step toward a proof? | **No.** | [[Audit]] |

## The one-paragraph version

Every step reads one digit of a number's 2-adic address, on either branch, so c = log₂ d is a true speed limit. Size falls at g bits per step whatever the size. Rising is paid for in address bits at θ bits per bit, where θ solves (1/d) Σ (q_r/d)^θ = 1, and θ = 1 exactly for 3x+1. A B-bit integer owns B address bits, so a count over all of them puts the largest lift near B/θ, which gives peak ≈ n², the Lagarias–Weiss constant. That is a heuristic, and small integers such as 27 beat it. The same θ governs value-space horizons, the fixed points F(w) of parity words: a horizon of M bits costs θM bits of address.

## Headline results

- **Exact:** 1 − A(n)/n = (1 − 2^(−β))(1 − F/n), the Schwarzschild factor, for every word and every n.
- **Exact:** a word is the time-1 map of the null ray dr/dt = −β(1 − F/n) with r = log₂ n, so bits destroyed are the ray's speed.
- **Exact:** the Lagarias–Weiss constant 41.677647 comes from H(p) = E_p[log₂ q], and the digit entropy equals the memory written.
- **Closed form:** μ(F > t) ~ 1/(t ln(27/16)), confirmed to about 1 part in 200,000 on the functional equation.
- **Rate proved via Tao:** bits erased per step, given the full 3-adic value, equal g exactly.
- **New law, measured:** captured integers of 3x+a are 1.817 a against Σ = 1.8137 in the top mass band, with a proved lower bound.
- **Low mass:** every odd a from 3 to 1401 has genuine failures of the 3x+a version of Terras's conjecture, at least 3 each. For a = 1 none is known, and the count expects about 1.14.
- **Certificate:** no integer fails that conjecture with 47,467 kicks or fewer.
- **Measured:** lift slopes within 2% of θ on ten of twelve maps, θ from 0.43 to 4.06. The near-critical map with θ = 0.09 misses by 38%.

## Files

- `collatz/schwarzschild/` — `system.py` (the maps), `horizon.py` (word horizons), `rates.py` (Haar rates and paths), `tape.py` (reversible tape, entropy curves).
- `tests/test_schwarzschild.py` — exact claims, cross-checked against `collatz.core`, `collatz.pinball.nesting` and OEIS A100982.
- `scripts/schwarzschild_experiments.py` — `python -X utf8 scripts/schwarzschild_experiments.py [E1 ... E11]`. All together take about 8 minutes on a 32-thread machine.
- `scripts/schwarzschild_figures.py` — redraws `figures/` from `results/`.
- `results/` — raw numbers as JSON. `figures/` — the PNGs embedded in these notes.

## Follow-ups (not done)

- The site's physics tables (`site/journey/the-picture.md`, `finite-fuel.md`) could use this dictionary. Site work needs its own branch from origin/main.
- Bound the upper side of the capture law.
- Check whether E[min(F, cap)] explains the capture counts for more maps.
- Search further for prior art on the capture cross-section before calling it new.
