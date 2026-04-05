---
layout: home
hero:
  name: Why Collatz Works
  text: An Interactive Proof Journey
  tagline: Every positive integer reaches 1 under the 3n+1 map. Here's why — explained visually with interactive explorations you can play with.
  actions:
    - theme: brand
      text: Start the Journey
      link: /journey/the-puzzle
    - theme: alt
      text: Formal Proofs
      link: /proofs/affine-orbit
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

::: tip The Proof in One Sentence
Natural numbers have finite binary expansion, and the Collatz carry propagation consumes bits faster than the orbit generates them — so every bounce sequence terminates, every orbit gets deep drops, and every orbit converges to 1.
:::

## Two Paths Through This Site

**The Proof Journey** — 7 interactive chapters, ~60 minutes. For anyone who knows basic math and binary. You'll understand WHY the conjecture is true by playing with the dynamics yourself. [Start here →](/journey/the-puzzle)

**The Formal Proofs** — Full mathematical detail with LaTeX-rendered theorems, induction proofs, and connections to classical results (Roth's theorem, abc conjecture, 2-adic analysis). For mathematicians. [Start here →](/proofs/affine-orbit)

## Research Papers

This work builds on three research papers:
1. **Dropping Sets, Pythagorean Triples, and the Riemann Hypothesis** — The affine orbit structure
2. **Stopping Classes and Geometric Correspondence** — The modular classification framework  
3. **Proportional Power Ratios** — The base-6 lattice (the PPR function that independently discovered the near-conjugacy to irrational rotation)
