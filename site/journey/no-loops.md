# No Loops?

There are two ways the conjecture could fail: an orbit could grow forever, or it could go **in circles**. This chapter is about the circles. Nobody has ruled them out. What we can do is see why a loop is so hard to build, and what is actually known.

A Collatz cycle would be an orbit that returns to its starting value: $n \to \cdots \to n$. If such a cycle has $S$ odd steps and $E$ even steps (total $K = S + E$), then the starting value must satisfy the **cycle equation** (Böhm and Sontacchi, 1978):

$$n = \frac{C \cdot 2^E}{2^E - 3^S}$$

where $C$ is a constant determined by the specific pattern of odd and even steps (the "parity word"). The denominator $g = 2^E - 3^S$ is the **gap** — and it must divide $C \cdot 2^E$ for $n$ to be a positive integer.

## Hunt for cycles

For a small pair $(S, E)$ the hunt can be done exhaustively: list every parity word, compute its constant $C$, and see whether the gap divides $C \cdot 2^E$.

- **(S=5, E=8)** — the first interesting case. 35 parity words that start at an odd value (91 if every starting point of the loop is counted), gap = 13, and 13 divides $C \cdot 2^E$ for none of them. No cycle of this shape.
- **(S=1, E=2)** — the trivial case. One word, gap = 1, and it gives the cycle 4 → 2 → 1.
- **(S=2, E=3)** — here $3^2 = 9 > 2^3 = 8$, so the gap is negative and the equation forces $n < 0$ (it lands on $-5$ and $-7$, which loop among the negative integers). No positive cycle of this shape.
- **(S=41, E=65)** — too large to list by brute force. My own meet-in-the-middle search found no cycle of this shape either, though the known results below already rule out cycles this short.

## Why E/S has to sit just above log₂ 3

Along a cycle the values are multiplied by 3 a total of $S$ times and divided by 2 a total of $E$ times, with the $+1$ terms making up the difference. Coming back to $n$ means the two balance exactly: $2^E / 3^S$ equals the product of $1 + \frac{1}{3 n_i}$ over the odd members $n_i$ of the cycle. Every factor is a little above 1, so a cycle of positive numbers needs $2^E$ bigger than $3^S$. And since every number below $2^{68}$ is known to reach 1, every member of a nontrivial cycle is larger than that, every factor is within $2^{-69}$ of 1, and $E/S$ can exceed $\log_2 3 \approx 1.58496$ only by less than $2^{-69}$.

Because $\log_2 3$ is irrational, $2^E \neq 3^S$ for any positive integers, so the gap is never zero. But it can be relatively small, and the pairs where it is smallest come from the **convergents** of $\log_2 3$ — its best rational approximations:

$$1/1,\ 2/1,\ 3/2,\ 8/5,\ 19/12,\ 65/41,\ 84/53,\ 485/306,\ \ldots$$

<ConvergentNavigator />

Blue dots have $3^S > 2^E$ (negative gap, no positive cycle possible). Red dots have $2^E > 3^S$. Zoom in to see how the convergents cluster around $\log_2 3$ without ever reaching it.

The convergents are the *most dangerous* candidates, but they are not the only ones. Any pair whose ratio $E/S$ falls in that narrow window above $\log_2 3$ is a candidate in principle, and ruling out every one of them is exactly the open problem.

## Counting words against the gap

There is a tempting heuristic. For a pair with $E/S$ close to $\log_2 3$, the number of parity words is roughly $\binom{E}{S} \approx 2^{0.95 E}$, while the gap is often close to $2^E$ in size. If the constants $C$ were spread out like random numbers, the *expected* number of words with $g \mid C \cdot 2^E$ would be about the number of words divided by the gap. Far out that is tiny: about one in a million at $(S, E) = (306, 485)$. For the small cases above it is not: about 2.7 at $(5, 8)$ and 0.6 at $(41, 65)$, and neither has a cycle. Added up over every $E$ it comes to roughly one for each value of $S$, and the trivial cycle run $S$ times is one such solution. Summed over all $S$ the naive count grows without bound, so by itself it says nothing about whether nontrivial cycles exist.

That is a heuristic, not a proof. The constants $C$ are not random, the gap can be far smaller than $2^E$ when $E/S$ is near a convergent, and an expected count below one does not show the actual count is zero.

## What is actually known

Ruling out nontrivial cycles is open. The strongest results use the cycle equation together with lower bounds on $|2^E - 3^S|$ from Baker's theory of linear forms in logarithms, and computer verification of small numbers:

- **Steiner (1977)** — there is no nontrivial cycle made of a single run of odd steps followed by a single run of even steps (a "1-cycle").
- **Eliahou (1993)** — since every number below a verified bound reaches 1, the ratio $E/S$ of any nontrivial cycle must lie extremely close to $\log_2 3$, and the cycle must be enormously long; the bound grows as verification extends.
- **Simons and de Weger (2005)** — no nontrivial $m$-cycles for $m \leq 68$ (an $m$-cycle has $m$ separate climbing runs).
- **Hercher (2023)** — extended this to $m \leq 91$.

The small cases and the convergent list on this page are the first few cases of the problem these authors attacked.

<div style="text-align: center; margin-top: 24px;">
  <a href="./binary-engine" class="vp-button medium">← The Binary Engine</a>
  <a href="./the-rotation" class="vp-button medium brand" style="margin-left: 12px;">Next: The Hidden Rotation →</a>
</div>
