# How to Read This Site

**No proof of the Collatz conjecture is claimed here.** The conjecture is open. This site is one amateur's field notes from years of exploring it: some real mathematics, some explainers of what is already known, some playful analogies, and some ideas that turned out to be wrong.

The name *Why Collatz Works* is a question I keep asking, not an answer I have.

## What the labels mean

Every page is one of these. If a page is not labelled yet, assume the most cautious reading.

| Label | Meaning |
|---|---|
| **Known mathematics** | An explainer of results from the literature, with references. Nothing here is mine. |
| **Proved here** | A short, elementary proof given in full on this site. Not peer-reviewed. Possibly folklore. |
| **Verified by computation** | Checked exhaustively up to a stated bound, with the code linked. Evidence, not proof. |
| **Conjecture / heuristic** | Looks true, fits the data, not proved. |
| **Exploration / analogy** | A way of looking at the problem. Fun, sometimes illuminating, not a claim. |
| **Retracted** | I believed it, and it is wrong or empty. Kept on purpose, with the reason. |

## Where the site has been wrong

Earlier versions of this site were written as a "proof journey" and marked several things as proved that are not. An audit in September 2026 found the following. The pages carry a warning until they are rewritten.

- **"No cycles" was never proved.** The argument counted *expected* numbers of cycles, which is a heuristic, and it assumed a cycle's step counts must be a continued-fraction convergent of log₂3, which is false. What is actually known comes from Steiner, Simons and de Weger, Eliahou, and Hercher.
- **The "Logarithmic Escape Theorem" is false as stated.** Counterexample: 294583 → 248555 → 209719 → 176951 → 149303 → 125975 makes six consecutive drops in the same class, where the stated bound allows fewer than three. The proof assumed a chain stays in one residue subgroup; it does not.
- **"Finite Propagation" was presented as proved on the strength of a computer check** up to 5 million. It is a heuristic picture, not a theorem, and an average was applied as if it held for every number.
- **Roth's theorem was misapplied.** It concerns algebraic numbers; log₂3 is transcendental. The bound the site wanted does not follow. What is known is the much weaker Baker–Rhin bound.
- **"Bit destruction is always positive"** only restates that a drop is a decrease. It is true and empty.
- **Prior art was not cited.** The affine structure of orbits within residue classes is due to Terras (1976) and Everett (1977). The counts of admissible parity words are OEIS A100982, and the spectrum of odd stopping times is A122437.

Any proposed route to a proof has to pass one test, and none of the old arguments did: **it must fail for −1.** The same 3n+1 rule sends −1 → −2 → −1 forever, and −5 and −17 sit on cycles too. An argument that never uses the fact that n is a *positive* integer would prove something false.

## What I think is actually worth your time

- **The mirror map and the Fibonacci age law** — a complete, short proof of something that appears to be unrecorded.
- **An exhaustive computer verification, for every n below 2⁶⁰,** of an open question posed in a 2026 paper, using a search that visits a Fibonacci number of cases instead of all of them.
- **The Sturmian sign rule** for a character sum over dropping sets.
- **The playgrounds.** They are the best way to get a feel for the problem, whatever you make of the rest.

## Who this is for

- **Curious, no background needed:** start with [the puzzle](/journey/the-puzzle) and the playgrounds under *Explore*.
- **Maths student:** read the *Known mathematics* pages in order, then the Fibonacci age law, then the retractions above as an exercise in finding the gap.
- **Number theorist:** the results list above is the whole claim. Everything else is exposition or play.
- **Fellow Collatz hobbyist:** read the retractions first. They are the mistakes I made so that you need not.

Corrections are welcome: the source is on [GitHub](https://github.com/h2ocoder/collatz).
