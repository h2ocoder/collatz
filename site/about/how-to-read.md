# How to Read This Site

**No proof of the Collatz conjecture is claimed here.** The conjecture is open. This site is one amateur's field notes from years of exploring it: some explainers of what is already known, a few small results, some computation, and some playful analogies. It is a work in progress.

The name *Why Collatz Works* is a question I keep asking, not an answer I have.

## Five kinds of statement

Every statement on this site is meant to be one of these, and the pages say which as they go. Where a page does not say, assume the most cautious reading.

| Kind | Meaning |
|---|---|
| **Known mathematics** | A result from the literature, with a reference. Not mine. |
| **Proved here** | A short, elementary proof given in full on this site. Not peer-reviewed. Possibly folklore. |
| **Verified by computation** | Checked by computer up to a stated bound, with the code linked where I have published it. Evidence, not proof. |
| **Conjecture / heuristic** | Looks true, fits the data, not proved. |
| **Exploration / analogy** | A way of looking at the problem. Fun, sometimes illuminating, not a claim. |

## One test every idea must pass

Any proposed route to a proof has to pass one test: **it must fail for −1.** The same 3n+1 rule sends −1 → −2 → −1 forever, and −5 and −17 sit on cycles too. An argument that never uses the fact that n is a *positive* integer would prove something false. Averages over residue classes, mixing rates and equidistribution statements all hold just as well for the negative integers, which is why none of them alone can settle the conjecture.

## What I think is actually worth your time

- **The Sturmian sign rule** for a character sum over dropping sets, on [the Sturmian L-probe page](/connections/sturmian-l-probe). It is supported by the computations shown there; the proof on that page is an outline, not a full proof.
- **The playgrounds.** They are the best way to get a feel for the problem, whatever you make of the rest.

More results from the current round of work are being written up and will appear here.

## Who this is for

- **Curious, no background needed:** start with [the puzzle](/journey/the-puzzle) and the playgrounds under *Explore*.
- **Maths student:** read the [definitions](/foundations/definitions), then the *Structure* pages, which explain mostly known mathematics, with references.
- **Number theorist:** start with the short list above. A few other pages carry short proofs, marked as such; everything else is exposition, computation or play.
- **Fellow Collatz hobbyist:** the −1 test above is the most useful thing on the site. Apply it to every idea, including mine.

Corrections are welcome: the source is on [GitHub](https://github.com/h2ocoder/collatz).
