# No Loops?

There are two ways the conjecture could fail: an orbit could grow forever, or it could go **in circles**. This chapter is about the circles. Nobody has ruled them out. What we can do is see why a loop is so hard to build, and what is actually known.

A Collatz cycle would be an orbit that returns to its starting value: $n \to \cdots \to n$. If such a cycle has $S$ odd steps and $E$ even steps (total $K = S + E$), then the starting value must satisfy the **cycle equation** (Böhm and Sontacchi, 1978):

$$n = \frac{C \cdot 2^E}{2^E - 3^S}$$

where $C$ is a constant determined by the specific pattern of odd and even steps (the "parity word"). The denominator $g = 2^E - 3^S$ is the **gap** — and it must divide $C \cdot 2^E$ for $n$ to be a positive integer.

## Hunt for cycles

Pick any $(S, E)$ combination. The widget computes the gap, enumerates all valid parity words, and checks whether any word produces a cycle:

<CycleHunter />

### What to try

- **(S=5, E=8)** — the first interesting case. 91 parity words, gap = 13. Watch the histogram: the remainder at 0 is **empty**. No cycle of this shape.
- **(S=1, E=2)** — the trivial case. This gives the cycle 4 → 2 → 1.
- **(S=3, E=5)** — here $3^3 > 2^5$, so the gap is negative and the equation forces $n < 0$. No positive cycle of this shape.
- **(S=41, E=65)** — too large to enumerate here. My own meet-in-the-middle search found no cycle of this shape either, though the known results below already rule out cycles this short.

## Why the gap has to be tiny

Along a cycle the values are multiplied by 3 a total of $S$ times and divided by 2 a total of $E$ times, with the $+1$ terms making up the difference. For the orbit to come back to $n$, the product $3^S / 2^E$ has to be very close to 1 — just a little below it. So a cycle needs $2^E$ slightly bigger than $3^S$, which means $E/S$ slightly bigger than $\log_2 3 \approx 1.58496$.

Because $\log_2 3$ is irrational, $2^E \neq 3^S$ for any positive integers, so the gap is never zero. But it can be relatively small, and the pairs where it is smallest come from the **convergents** of $\log_2 3$ — its best rational approximations:

$$1/1,\ 2/1,\ 3/2,\ 8/5,\ 19/12,\ 65/41,\ 84/53,\ 485/306,\ \ldots$$

<ConvergentNavigator />

Blue dots have $3^S > 2^E$ (negative gap, no positive cycle possible). Red dots have $2^E > 3^S$. Zoom in to see how the convergents cluster around $\log_2 3$ without ever reaching it.

The convergents are the *most dangerous* candidates, but they are not the only ones. Any pair with $2^E > 3^S$ is a candidate in principle, and ruling out every one of them for every $S$ is exactly the open problem.

## Counting words against the gap

There is a tempting heuristic. The number of parity words for a given $(S, E)$ is roughly $\binom{E}{S} \approx 2^{0.95 E}$, while the gap is often close to $2^E$ in size. If the constants $C$ were spread out like random numbers, the *expected* number of words with $g \mid C \cdot 2^E$ would be tiny, and shrink as $S$ grows.

That is a heuristic, not a proof. The constants $C$ are not random, the gap can be far smaller than $2^E$ when $E/S$ is near a convergent, and an expected count below one does not show the actual count is zero.

## What is actually known

Ruling out nontrivial cycles is open. The strongest results use the cycle equation together with lower bounds on $|2^E - 3^S|$ from Baker's theory of linear forms in logarithms, and computer verification of small numbers:

- **Steiner (1977)** — there is no nontrivial cycle made of a single run of odd steps followed by a single run of even steps (a "1-cycle").
- **Eliahou (1993)** — since every number below a verified bound reaches 1, the ratio $E/S$ of any nontrivial cycle must lie extremely close to $\log_2 3$, and the cycle must be enormously long; the bound grows as verification extends.
- **Simons and de Weger (2005)** — no nontrivial $m$-cycles for $m \leq 68$ (an $m$-cycle has $m$ separate climbing runs).
- **Hercher (2023)** — extended this to $m \leq 91$.

The widgets on this page are a hands-on way to see the first few cases of the problem these authors attacked.

<div style="text-align: center; margin-top: 24px;">
  <a href="./binary-engine" class="vp-button medium">← The Binary Engine</a>
  <a href="./the-rotation" class="vp-button medium brand" style="margin-left: 12px;">Next: The Hidden Rotation →</a>
</div>
