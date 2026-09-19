# How to Read This Site

**No proof of the Collatz conjecture is claimed here.** The conjecture is open. This site is one amateur's field notes from years of exploring it: some explainers of what is already known, a few small results, some computation, and some playful analogies. It is a work in progress.

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

## One test every idea must pass

Any proposed route to a proof has to pass one test: **it must fail for −1.** The same 3n+1 rule sends −1 → −2 → −1 forever, and −5 and −17 sit on cycles too. An argument that never uses the fact that n is a *positive* integer would prove something false. Averages over residue classes, mixing rates and equidistribution statements all hold just as well for the negative integers, which is why none of them alone can settle the conjecture.

## What I think is actually worth your time

- **The Sturmian sign rule** for a character sum over dropping sets, on [the Sturmian L-probe page](/connections/sturmian-l-probe).
- **The playgrounds.** They are the best way to get a feel for the problem, whatever you make of the rest.

More results from the current round of work are being written up and will appear here.

## Who this is for

- **Curious, no background needed:** start with [the puzzle](/journey/the-puzzle) and the playgrounds under *Explore*.
- **Maths student:** read the [definitions](/foundations/definitions), then the *Structure* pages, which explain known mathematics with references.
- **Number theorist:** the short list above is the whole claim. Everything else is exposition or play.
- **Fellow Collatz hobbyist:** the −1 test above is the most useful thing on the site. Apply it to every idea, including mine.

Corrections are welcome: the source is on [GitHub](https://github.com/h2ocoder/collatz).
