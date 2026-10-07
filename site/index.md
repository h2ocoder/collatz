---
layout: home
hero:
  name: Why Collatz Works
  text: Exploring the 3n+1 Problem
  tagline: One amateur's field notes on the 3n+1 problem — playgrounds, explainers, a few small results, and honest notes on what didn't work. No proof is claimed.
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
    details: Pick a number, apply the rules, and watch where it goes. Every positive whole number tested so far ends at 1. Try to find one that doesn't.
    link: /journey/the-puzzle
  - title: "2. The Binary Engine"
    details: Watch what the two rules do to a number's bits. Halving removes one; 3n+1 adds one or two. Then meet the dropping sets.
    link: /journey/binary-engine
  - title: "3. No Loops?"
    details: Why a loop would need 2^E to sit absurdly close to 3^S, what is actually known about cycles, and a navigator for the near misses between powers of 2 and 3.
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

It has three kinds of material:

- **Explainers of known mathematics** — dropping sets, why log₂3 keeps appearing, Terras's parity vectors. None of it is mine; all of it is worth understanding.
- **A few small results of my own** — some proved in full, some only in outline, some checked by computer up to a stated bound. I have looked for them in the literature as far as I can; some may be folklore.
- **Explorations and analogies** — Eisenstein lattices, transfer operators, a thermodynamic analogy. Ideas thrown at the wall to see what sticks.

## Where to Start

**Just curious?** [Take the tour](/journey/the-puzzle) — seven interactive chapters — or go straight to the playgrounds: [Sturmian Bridge](/explore/sturmian-bridge), [Binary Shortcut](/explore/binary-shortcut), [Alpha Sequence](/explore/alpha-sequence).

**A mathematician?** Read [How to read this site](/about/how-to-read) first. It says what is and is not claimed, and how to tell a proof from a computation from an analogy, in one page.

**Working on Collatz yourself?** The one test every idea must pass: *it has to fail for −1*, because −1 → −2 → −1 loops forever under the same rule.

## Prior Work

This exploration grew out of several years of self-published work by an amateur mathematician working in industry. The earlier writings sorted the integers by stopping time under the name *dropping sets* (the classification itself goes back to Terras, 1976), drew a geometric picture of it, and plotted orbits in base 6. [Read more →](/publications)
