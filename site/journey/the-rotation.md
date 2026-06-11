# The Hidden Rotation

In the right coordinates, the chaos disappears.

Plot every Collatz orbit value on a circle, where the position is the **fractional part of $\log_6(\text{value})$**. Something remarkable emerges:

<Base6Circle />

The points equidistribute around the circle. They don't cluster, don't avoid any region, and fill the circle uniformly as the orbit progresses.

Turn on "ideal rotation" and compare: the gray dots show a **pure irrational rotation** by $\log_6 3 \approx 0.6131$ per step. The colored dots (actual Collatz orbit) follow nearly the same pattern. The difference — the perturbation from the "+1" in $3n+1$ — is small and shrinks for larger numbers.

## Why base 6?

Each Collatz step does two things:
- **Multiplies by 3** (the odd step: $3n+1 \approx 3n$)
- **Divides by 2** (the even steps)

In **base 6 = 2 × 3**: these two operations combine into a single rotation. The $\times 3$ contributes $\log_6 3$, and the $\div 2$ subtracts $\log_6 2$. Net per Syracuse step: advance by $\log_6 3 \approx 0.613$ on the circle.

This is the **conservation law**: $s \cdot \log_2 6 = T - \log_2 n + \varepsilon$, where $s$ is odd steps, $T$ is total steps, and $\varepsilon$ is a small error from the "+1". The base-6 lattice is not a coincidence — it's the natural coordinate system for the dynamics.

## The 44-step quasi-period

Watch an orbit with many points (set points to 200+). You'll notice a subtle pattern: the orbit almost returns to its starting position after **44 steps**. This is because $27/44 = 0.6136 \approx \log_6 3 = 0.6131$ — after 44 rotations by $\log_6 3$, you've gone around the circle almost exactly 27 times.

$27/44$ is a **semiconvergent** of $\log_6 3$ in its continued fraction expansion ($31$ and $106$ are the neighboring true convergents — and $31$ is actually the *better* rational approximation). So why does the eye see 44 and not 31? Because the "+1" perturbation is always positive, it can only tighten near-returns that miss from below ($\epsilon < 0$, like 44) and always worsens those that miss from above ($\epsilon > 0$, like 31) — and the cancellation becomes *exact* in the small-value band every orbit's tail passes through. The quasi-period 44 is a fingerprint of the rotation *and* the perturbation together: it's the closure the wobble selects. The full dissection lives in [The Wobble](../explore/log6-wobble).

## The destruction landscape

How much does each dropping set destroy? Hover over the bars:

<BitDestructionLandscape />

The red bars are the **convergents** — the slowest sets. They correspond to the best rational approximations of $\log_2 3$. But even the slowest one (s=41, $\beta = 0.017$) still destroys bits. Roth's theorem guarantees $\beta(s) > c/s$ — they can't get too slow.

## What this means for convergence

Irrational rotations have a powerful property: **Weyl's equidistribution theorem** guarantees that every orbit visits every region of the circle. There are no "safe zones" that the orbit avoids.

Combined with the bit destruction identity ($\beta > 0$ for every drop): the orbit visits the "fast drop" regions periodically. It can't systematically dodge them.

But "visits fast drop regions" isn't quite the same as "actually takes fast drops." The orbit visits the RIGHT REGION on the circle, but the drop type also depends on the **low bits** of the number — which are independent of the circle position (by the Chinese Remainder Theorem).

So we need one more ingredient: something that forces the orbit to actually take deep drops, not just visit the right neighborhoods. That's the **countdown**.

<div style="text-align: center; margin-top: 24px;">
  <a href="./no-loops" class="vp-button medium">← No Loops</a>
  <a href="./the-countdown" class="vp-button medium brand" style="margin-left: 12px;">Next: The Countdown →</a>
</div>
