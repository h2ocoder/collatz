---
layout: home
hero:
  name: Why Collatz Works
  text: Exploring the 3n+1 Problem
  tagline: Interactive explorations of the Collatz conjecture — uncovering structural patterns, deep connections, and a possible path to proof.
  actions:
    - theme: brand
      text: Start the Journey
      link: /journey/the-puzzle
    - theme: alt
      text: Connections
      link: /connections/
    - theme: alt
      text: Research Roadmap
      link: /roadmap/path-to-proof

features:
  - title: "1. The Puzzle"
    details: Pick any number, apply the rules, watch it reach 1. Try to find one that doesn't.
    link: /journey/the-puzzle
  - title: "2. The Binary Engine"
    details: Watch bits get destroyed step by step. Every drop eats information.
    link: /journey/binary-engine
  - title: "3. No Loops"
    details: The irrationality of log₂3 prevents any orbit from cycling. Every candidate fails.
    link: /journey/no-loops
  - title: "4. The Hidden Rotation"
    details: In log₆ coordinates, Collatz is an irrational rotation on a circle. Chaos becomes order.
    link: /journey/the-rotation
  - title: "5. The Countdown"
    details: The +1 carry propagation is a deterministic timer. Not random. Not statistical. Algebraic.
    link: /journey/the-countdown
  - title: "6. Finite Fuel"
    details: Natural numbers have finite bits. The carry reads faster than the orbit generates. The fuel runs out.
    link: /journey/finite-fuel
---

::: warning Status
This is an **exploration**, not a completed proof. The results here include proved theorems, verified computations, and structural conjectures. Some arguments have gaps — notably the finite propagation bound needs full algebraic verification, and the asymptotic cycle elimination needs a rigorous uniformity bound. We describe both what we've proved and what remains open. Peer review and collaboration are welcome.
:::

## What This Site Is

An amateur mathematician's multi-year exploration of the Collatz conjecture, presented as interactive visualizations you can play with. The goal is not to claim a proof, but to share genuinely interesting structural discoveries:

- **The Collatz map is a thermodynamic system** — with a conservation law, a dissipation rate, and a critical threshold. Among all $nx+c$, $x/y$ systems, $3x+1$ is the *only* nontrivial convergent one, because 3 is the only odd prime less than $2^2 = 4$. [Read more →](/connections/universal-dynamics)

- **The transfer operator has exactly 4 non-zero eigenvalues** — the cube roots of $4/3$, spaced at $120°$ intervals. This connects to the Hilbert-Polya conjecture and Eisenstein integers. [Read more →](/connections/hilbert-polya)

- **Orbits trace walks on the Eisenstein lattice** — and convergence becomes a geometric question: does a biased random walk on $\mathbb{Z}[\omega]$ always end above a geodesic? [Read more →](/connections/eisenstein)

- **Carry propagation is a countdown timer** — the $+1$ in $3n+1$ reads bits of $n$ at a rate that exceeds the orbit's ability to generate new ones. This is verified computationally but not yet fully proved for all integers. [Read more →](/journey/the-countdown)

## Two Paths Through This Site

**The Proof Journey** — 7 interactive chapters. For anyone who knows basic math and binary. Explore WHY the conjecture should be true by playing with the dynamics yourself. [Start here →](/journey/the-puzzle)

**The Research** — Proved results, structural connections, and the roadmap of what's done and what remains. For mathematicians. [Proved results →](/proofs/affine-orbit) | [Connections →](/connections/) | [Roadmap →](/roadmap/path-to-proof)

## Prior Work

This exploration grew out of several years of self-published work by an amateur mathematician working in industry. The earlier writings developed the dropping set framework, the geometric correspondence, and the base-6 rotation discovery. [Read more →](/publications)
