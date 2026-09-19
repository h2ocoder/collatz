# The Hidden Rotation

In the right coordinates, the chaos looks much calmer.

Plot every Collatz orbit value on a circle, where the position is the **fractional part of $\log_6(\text{value})$**. This picture is due to Shakibaei Asli (arXiv:2601.04289), who showed that in these coordinates the Collatz map is an irrational rotation plus a small perturbation. (I came to the same transformation independently through my proportional power ratios in base 6.)

<Base6Circle />

In the orbits you can try here, the points spread out around the circle. They don't visibly cluster, and they fill the circle more and more evenly as the orbit progresses.

Turn on "ideal rotation" and compare: the gray dots show a **pure irrational rotation** by $\log_6 3 \approx 0.6131$ per step. The colored dots (actual Collatz orbit) follow nearly the same pattern. The difference — the perturbation from the "+1" in $3n+1$ — is small and shrinks for larger numbers.

## Why base 6?

Each Collatz step does two things:
- **Multiplies by 3** (the odd step: $3n+1 \approx 3n$)
- **Divides by 2** (the even steps)

In **base 6 = 2 × 3**: these two operations combine into a single rotation. The $\times 3$ contributes $\log_6 3$, and the $\div 2$ subtracts $\log_6 2$. Net per Syracuse step: advance by $\log_6 3 \approx 0.613$ on the circle.

This matches a simple bookkeeping identity: $s \cdot \log_2 6 = T - \log_2 n + \varepsilon$, where $s$ is odd steps, $T$ is total steps, and $\varepsilon$ is a small error from the "+1". Base 6 is a natural coordinate system for keeping track of the two operations at once.

## The 44-step quasi-period

Watch an orbit with many points (set points to 200+). You'll notice a subtle pattern: the orbit almost returns to its starting position after **44 steps**. This is because $27/44 = 0.6136 \approx \log_6 3 = 0.6131$ — after 44 rotations by $\log_6 3$, you've gone around the circle almost exactly 27 times.

$27/44$ is a good rational approximation of $\log_6 3$ (an intermediate fraction between the convergents $8/13$ and $19/31$ of its continued fraction). The quasi-period 44 is a fingerprint of the irrational rotation structure.

## The destruction landscape

How much does each dropping set destroy? Hover over the bars:

<BitDestructionLandscape />

The red bars are the **record-slow sets** — each one slower than every set before it (s = 1, 3, 5, 17, 29, 41). They come from the best rational approximations of $\log_2 3$ from above. Even the slowest one shown (s=41, $\beta = 0.017$) still removes bits. How small $\beta(s)$ can get in general is controlled by Baker's theory of linear forms in logarithms: $|E - S \log_2 3| > S^{-\kappa}$ for an effective constant $\kappa$ (Rhin: $\kappa \approx 13$).

## What this does and doesn't say

For an exact irrational rotation, **Weyl's equidistribution theorem** says every orbit spreads evenly around the circle. Collatz is not an exact rotation: the "+1" perturbs every step, so Weyl's theorem does not apply to it directly, and nothing here guarantees what an individual orbit does. The picture is suggestive, not a proof.

There is a second gap. Even if an orbit visited every region of the circle, the drop type also depends on the **low bits** of the number, which the circle position does not see. Something else has to decide whether the orbit actually takes deep drops. The next chapter looks at one such mechanism: the **countdown**.

<div style="text-align: center; margin-top: 24px;">
  <a href="./no-loops" class="vp-button medium">← No Loops</a>
  <a href="./the-countdown" class="vp-button medium brand" style="margin-left: 12px;">Next: The Countdown →</a>
</div>
