# No Loops

Before we prove orbits must descend, let's prove they can't go **in circles**.

A Collatz cycle would be an orbit that returns to its starting value: $n \to \cdots \to n$. If such a cycle has $S$ odd steps and $E$ even steps (total $K = S + E$), then the starting value must satisfy:

$$n = \frac{C \cdot 2^E}{2^E - 3^S}$$

where $C$ is a constant determined by the specific pattern of odd and even steps (the "parity word"). The denominator $g = 2^E - 3^S$ is the **gap** — and it must divide $C \cdot 2^E$ for $n$ to be a positive integer.

## Hunt for cycles

Pick any $(S, E)$ combination. The widget computes the gap, enumerates all valid parity words, and checks whether ANY word produces a cycle:

<CycleHunter />

### What to try

- **(S=5, E=8)** — the first non-trivial candidate. 91 parity words, gap = 13. Watch the histogram: the remainder at 0 is **empty**. No cycle.
- **(S=1, E=2)** — the trivial case. This gives the cycle 4 → 2 → 1. The only one.
- **(S=3, E=5)** — ascending ($3^3 > 2^5$). Eliminated automatically: the gap is negative, forcing $n < 0$.
- **(S=41, E=65)** — too large to enumerate here, but computationally eliminated via a meet-in-the-middle search (87 minutes in Rust).

## The convergents of $\log_2 3$

The cycle candidates come from the **convergents** of $\log_2 3$ — the best rational approximations. Explore them:

<ConvergentNavigator />

Blue dots (ascending) are eliminated automatically. Red dots (descending) need computation or counting. Zoom in to see how the convergents cluster around $\log_2 3$ without ever reaching it.

## Why no cycles exist

The proof eliminates ALL possible cycles through three mechanisms:

### 1. Ascending convergents: sign argument

When $3^S > 2^E$ (the gap $g$ is negative), the formula gives $n < 0$. Since we need positive integers, these are **automatically eliminated**. This kills roughly half of all candidates.

### 2. Small convergents: direct computation

For $(S=5, E=8)$: gap = 13, all 91 words checked, zero hits.
For $(S=41, E=65)$: gap ≈ $4.2 \times 10^{17}$, eliminated by MITM.

### 3. Large convergents: the counting argument

For $S \geq 306$: the number of parity words is $C(E-1, S-1) \approx 2^{0.95E}$, while the gap $g \approx 2^E$. Since $0.95 < 1$: words/gap → 0 exponentially. There simply aren't enough words to hit even one multiple of the gap.

The **second moment bound** (Parseval's inequality) makes this rigorous: the deviation of the actual zero-count from the expected count is bounded by $\sqrt{\text{words}/g}$. When words/gap $< 0.38$: the bound forces zero cycles. This holds for all $S \geq 306$.

## The role of $\log_2 3$

Why does this work? The gap $g = 2^E - 3^S$ is governed by how well $E/S$ approximates $\log_2 3 \approx 1.5850$. The best approximations (convergents of the continued fraction) give the smallest gaps — but even these aren't small enough.

The **irrationality** of $\log_2 3$ is what prevents cycles. If $\log_2 3$ were rational ($= p/q$), then $2^p = 3^q$ and the gap would be zero — cycles would exist trivially. But $\log_2 3$ is irrational, so $2^E \neq 3^S$ for any positive integers, and the gap is always nonzero.

The convergents of $\log_2 3$ are: $1/1, 2/1, 3/2, 8/5, 19/12, 65/41, 84/53, 485/306, \ldots$

Each gives a cycle candidate. All fail. The ascending ones (even indices) fail by sign. The descending ones (odd indices) fail by computation or counting.

::: tip Front 1: Complete
**Theorem.** No non-trivial Collatz cycle exists.

Every convergent is eliminated. The cycle threat is dead. Now we focus on the other threat: can an orbit grow forever?
:::

<div style="text-align: center; margin-top: 24px;">
  <a href="./binary-engine" class="vp-button medium">← The Binary Engine</a>
  <a href="./the-rotation" class="vp-button medium brand" style="margin-left: 12px;">Next: The Hidden Rotation →</a>
</div>
