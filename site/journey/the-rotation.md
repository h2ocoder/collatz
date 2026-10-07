# The Hidden Rotation

In the right coordinates, the chaos looks much calmer.

Plot every Collatz orbit value on a circle, where the position is the **fractional part of $\log_6(\text{value})$**. This picture is due to Shakibaei Asli (arXiv:2601.04289), who showed that with the slightly shifted coordinate $\{\log_6(x + 1/5)\}$ every Collatz step is a rotation by $\log_6 3$ plus a uniformly bounded error that shrinks like $1/x$. (I came to the base-6 logarithm independently, through my proportional power ratios; the shift and the error bound are his.)

<Base6Circle />

The widget plots the odd values of an orbit. In the orbits you can try here, the points spread out around the circle and don't visibly cluster.

Turn on "ideal rotation" and compare: the gray dots show a **pure irrational rotation** by $\log_6 3 \approx 0.6131$ per step, from the same starting point. They do not pair up dot for dot with the colored ones, because the colored dots are only the odd values, and between one odd value and the next the orbit takes two or more steps. Counted step by step, an orbit does stay close to the pure rotation: for every start below 100,000 it has drifted by at most 0.13 of a turn by the time it reaches 1. The drift comes from the "+1" in $3n+1$, and each nudge is smaller the larger the number.

## Why base 6?

A Collatz step does one of two things:
- **Multiplies by 3** (the odd step: $3n+1 \approx 3n$)
- **Divides by 2** (the even step)

In **base 6 = 2 × 3** the two operations become the same rotation. Multiplying by 3 moves the point forward by $\log_6 3$. Dividing by 2 moves it back by $\log_6 2 = 1 - \log_6 3$, and on a circle that is the same as moving forward by $\log_6 3$. So every step, odd or even, advances by $\log_6 3 \approx 0.613$ (an odd step by a touch more, because of the $+1$).

For an orbit that reaches 1 this matches a simple bookkeeping identity: $s \cdot \log_2 6 = T - \log_2 n + \varepsilon$, where $s$ is the number of odd steps, $T$ the total number of steps, and $\varepsilon$ a small error from the "+1". Because the two operations look the same on the base-6 circle, the position works as a step counter: it records how many steps the orbit has taken, not whether the number has grown or shrunk.

## The 44-step quasi-period

Count every step of an orbit, halvings and triplings alike, and a subtle pattern appears: after **44 steps** the point is almost back where it started. This is because $27/44 = 0.6136 \approx \log_6 3 = 0.6131$ — 44 rotations by $\log_6 3$ go around the circle almost exactly 27 times, falling short by about 0.02 of a turn. (The widget above plots only the odd values, so the 44 does not show up in it.)

$27/44$ is a good rational approximation of $\log_6 3$ (an intermediate fraction between the convergents $8/13$ and $19/31$ of its continued fraction). The quasi-period 44 is a fingerprint of the rotation by $\log_6 3$. How 44 compares on real orbits with the closer approximation 31 is the subject of [The Wobble](../explore/log6-wobble).

## The destruction landscape

How much does each dropping set destroy? Hover over the bars:

<BitDestructionLandscape />

The red bars are the **record-slow sets** — each one slower than every set before it (s = 1, 3, 5, 17, 29, 41). They come from the best rational approximations of $\log_2 3$ from above. Even the slowest one shown (s=41, $\beta = 0.017$) still removes bits. How small $\beta(s)$ can get in general is controlled by Baker's theory of linear forms in logarithms: $|E - S \log_2 3| > S^{-\kappa}$ for an effective constant $\kappa$ (Rhin: $\kappa \approx 13$).

## What this does and doesn't say

For an exact irrational rotation, **Weyl's equidistribution theorem** says every orbit spreads evenly around the circle. Collatz is not an exact rotation: the "+1" nudges every odd step, so Weyl's theorem does not apply to it directly, and nothing here says what an individual orbit does. The picture is a way of seeing the step count; it is not evidence that orbits fall.

There is a more basic limit. Because a halving and a tripling turn the circle by the same angle, the position records how many steps the orbit has taken and nothing about whether the number has grown or shrunk. The same picture can be drawn for $3x - 1$, which has loops through 5 and through 17, so it cannot be evidence that orbits of $3x + 1$ fall. Which kind of step comes next is decided by the **low bits** of the number, which the circle does not see. The next chapter looks at what the low bits do: the **countdown**.

<div style="text-align: center; margin-top: 24px;">
  <a href="./no-loops" class="vp-button medium">← No Loops?</a>
  <a href="./the-countdown" class="vp-button medium brand" style="margin-left: 12px;">Next: The Countdown →</a>
</div>
