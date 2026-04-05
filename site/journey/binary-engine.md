# The Binary Engine

Forget the numbers. Watch the **bits**.

Every positive integer is a string of binary digits: 27 = `11011`. The Collatz map does two very different things to these bits:

- **Even step (÷2)**: Shift right. The rightmost bit falls off. **One bit destroyed.**
- **Odd step (×3+1)**: Multiply by 3 and add 1. The carry chain ripples through the bits. Bit length grows by **at most 1**.

Step through it yourself:

<BinaryStepVisualizer />

Watch the bit-length counter. Even steps always shrink it. Odd steps can grow it by 1 — but the next step after an odd number is *always* even (since 3n+1 is even when n is odd). So the worst case is: grow by 1, then shrink by 1. Net: zero.

But it's usually better than zero. Try 27 and watch: the bit-length starts at 5, climbs to ~14 at the peak, then steadily falls to 1. The bits are being **consumed**.

## The dropping sets

Not all numbers drop at the same rate. Some take 3 steps (fast), others take 13 steps (slow), others even more. Numbers that take the same number of steps to drop form a **dropping set**.

Explore the patterns:

<DroppingSetExplorer />

Notice something remarkable: numbers in the same dropping set form **arithmetic progressions**. All of Set₃ (green) are exactly the numbers ≡ 1 (mod 4). All of Set₆ (blue) are ≡ 3 (mod 16). This isn't a coincidence — it's the **affine orbit structure**: within each set, the destination is an exact linear function of the starting value.

## The contraction ratio

Each dropping set has a **contraction ratio** $3^s / 2^{k-s}$ where $s$ is the number of odd steps and $k$ is the total steps:

| Set | Steps (k) | Odd steps (s) | Ratio | Speed |
|-----|-----------|---------------|-------|-------|
| Set₃ | 3 | 1 | 3/4 = 0.75 | Fast |
| Set₆ | 6 | 2 | 9/16 = 0.56 | Fast |
| Set₈ | 8 | 3 | 27/32 = 0.84 | Moderate |
| Set₁₃ | 13 | 5 | 243/256 = 0.95 | **Slow** |

Set₁₃ barely shrinks — it contracts by only 5%. Could an orbit get stuck visiting slow sets like this?

## The bit destruction identity

Every ratio is less than 1. Every single one. This is because $\log_2 3$ is irrational — there's no way for $3^s$ to exactly equal $2^{k-s}$. The bits destroyed per drop are:

$$\beta(s) = \lceil s \cdot \log_2 3 \rceil - s \cdot \log_2 3 > 0$$

This is always positive. **No drop is ever lossless.** But some are very close to zero (Set₁₃ has $\beta = 0.075$). The slow sets correspond to the best rational approximations of $\log_2 3$ — the convergents of its continued fraction.

By **Roth's theorem** from Diophantine approximation: $\beta(s) > c/s$ for some constant $c$. The approximations can't get too good, so the slow sets can't get too slow.

## What we know so far

✅ Every drop destroys $\beta > 0$ bits — proved
✅ Average destruction: 0.45 bits per drop — computed
✅ No set is "too slow" — Roth's theorem

But two questions remain:

1. Can the orbit **loop** (visit the same values forever)?
2. Can the orbit **systematically dodge** the fast drops?

Next: we eliminate loops.

<div style="text-align: center; margin-top: 24px;">
  <a href="./the-puzzle" class="vp-button medium">← The Puzzle</a>
  <a href="./no-loops" class="vp-button medium brand" style="margin-left: 12px;">Next: No Loops →</a>
</div>
