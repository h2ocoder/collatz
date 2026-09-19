---
layout: home
hero:
  name: Why Collatz Works
  text: Exploring the 3n+1 Problem
  tagline: One amateur's field notes on the 3n+1 problem — playgrounds, explainers, a few new results, and honest notes on what didn't work. No proof is claimed.
  actions:
    - theme: brand
      text: Take the Tour
      link: /journey/the-puzzle
    - theme: alt
      text: Connections
      link: /connections/
    - theme: alt
      text: How to read this site
      link: /about/how-to-read

features:
  - title: "1. The Puzzle"
    details: Pick any number, apply the rules, watch it reach 1. Try to find one that doesn't.
    link: /journey/the-puzzle
  - title: "2. The Binary Engine"
    details: Watch bits get destroyed step by step. Every drop eats information.
    link: /journey/binary-engine
  - title: "3. No Loops"
    details: Why a loop would need 2^E to sit absurdly close to 3^S, what is actually known about cycles, and a playground for hunting them.
    link: /journey/no-loops
  - title: "4. The Hidden Rotation"
    details: In log₆ coordinates, Collatz looks like an irrational rotation with a small wobble. An analogy worth playing with.
    link: /journey/the-rotation
  - title: "5. The Countdown"
    details: The +1 carry acts like a countdown on the trailing bits. An elementary lemma you can watch run.
    link: /journey/the-countdown
  - title: "6. Finite Fuel"
    details: A heuristic picture — finite bits as fuel. Not a theorem, and the page says what is missing.
    link: /journey/finite-fuel
---

::: info
This is a work in progress by an amateur. No proof of the Collatz conjecture is claimed.
:::

## What This Site Is

I am not a professional mathematician. I have been circling the 3n+1 problem for years because it is the most approachable hard problem I know: you can explain it to a child, and nobody can solve it. This site is where I keep what I find.

It has three kinds of page:

- **Explainers of known mathematics** — dropping sets, why log₂3 keeps appearing, Terras's parity vectors. None of it is mine; all of it is worth understanding.
- **A few results of my own** — small, fully proved or exhaustively computed, and checked against the literature as far as I can.
- **Explorations and analogies** — Eisenstein lattices, transfer operators, thermodynamics, pinball. Ideas thrown at the wall to see what sticks.

## Where to Start

**Just curious?** [Take the tour](/journey/the-puzzle) — seven interactive chapters — or go straight to the playgrounds: [Sturmian Bridge](/explore/sturmian-bridge), [Binary Shortcut](/explore/binary-shortcut), [Alpha Sequence](/explore/alpha-sequence).

**A mathematician?** Read [How to read this site](/about/how-to-read) first. It states exactly what is and is not claimed, in one page.

**Working on Collatz yourself?** The one test every idea must pass: *it has to fail for −1*, because −1 → −2 → −1 loops forever under the same rule.

## Prior Work

This exploration grew out of several years of self-published work by an amateur mathematician working in industry. The earlier writings developed the dropping set framework, the geometric correspondence, and proportional power ratios in base 6. [Read more →](/publications)
