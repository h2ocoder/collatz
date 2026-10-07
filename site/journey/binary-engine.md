# The Binary Engine

Forget the numbers. Watch the **bits**.

Every positive integer is a string of binary digits: 27 = `11011`. The Collatz map does two very different things to these bits:

- **Even step (÷2)**: Shift right. The rightmost bit falls off. **One bit destroyed.**
- **Odd step (×3+1)**: Multiply by 3 and add 1. The carry chain ripples through the bits. Bit length grows by **at most 2**.

Step through it yourself:

<BinaryStepVisualizer />

Watch the bit-length counter. Even steps always shrink it. Odd steps can grow it by up to 2 — but the next step after an odd number is *always* even (since 3n+1 is even when n is odd). So an odd step plus the halving after it adds at most one bit, and often none.

In every orbit anyone has computed, the halvings win in the end. Try 27 and watch: the bit-length starts at 5, climbs to 14 at the peak, then falls back to 1.

## The dropping sets

A number *drops* when its orbit first falls below where it started. Numbers do not all drop at the same rate. Some take 3 steps (fast), others take 13 steps (slow), others even more. (That every number drops at all is the conjecture itself. It is known for almost all numbers, by Terras, and for every number that has been checked.) Numbers that take the same number of steps to drop form a **dropping set**.

Explore the patterns:

<DroppingSetExplorer />

Notice something remarkable: the numbers in a dropping set line up in **arithmetic progressions**. All of Set₃ (green) are exactly the numbers ≡ 1 (mod 4). All of Set₆ (blue) are ≡ 3 (mod 16). This isn't a coincidence — it's the **affine orbit structure** known since Terras (1976): within each residue class of a set, the destination is an exact linear function of the starting value. (Terras proved that each dropping set is a union of such progressions apart from at most finitely many numbers. No exception is known.)

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

Every ratio is less than 1 — that is what it means to drop. And none can equal 1 exactly, because $\log_2 3$ is irrational: there's no way for $3^s$ to equal $2^{k-s}$. So a drop with $s \geq 1$ odd steps needs more than $s \log_2 3$ halvings, which means at least $\lceil s \log_2 3 \rceil$. In every case checked (all $n$ up to $10^7$) it uses exactly that many. That it always does would follow from Terras's *coefficient stopping time conjecture*, which is open. With exactly that many halvings, the ratio $3^s/2^{k-s}$ removes

$$\beta(s) = \lceil s \cdot \log_2 3 \rceil - s \cdot \log_2 3 > 0$$

bits. (The number itself loses a little less, because of the $+1$s: $5 \to 4$ loses 0.32 bits, and $\beta(1) = 0.415$.) This is always positive, which is another way of saying a drop is a decrease. But some are very close to zero (Set₁₃ has $\beta = 0.075$). The slowest sets correspond to the best rational approximations of $\log_2 3$ from above — convergents of its continued fraction and the intermediate fractions between them.

How close to zero can $\beta(s)$ get? Baker's theory of linear forms in logarithms gives $|E - S \log_2 3| > S^{-\kappa}$ for an effective constant $\kappa$ (Rhin: $\kappa \approx 13$). So the slow sets cannot get slow too fast, but the bound is weak.

## What this tells us

- The contraction ratio of every drop removes a positive number of bits ($\beta(s)$ in every case checked) — true, and a restatement of "a drop is a decrease"
- Averaged over the odd starting values up to $10^7$, a drop removes about 0.45 bits — computed
- How small $\beta(s)$ can get depends on how well fractions approximate $\log_2 3$

None of this says what a *particular* orbit does. Two questions remain open:

1. Can an orbit **loop** (visit the same values forever)?
2. Can an orbit **systematically dodge** the fast drops?

Next: loops.

<div style="text-align: center; margin-top: 24px;">
  <a href="./the-puzzle" class="vp-button medium">← The Puzzle</a>
  <a href="./no-loops" class="vp-button medium brand" style="margin-left: 12px;">Next: No Loops? →</a>
</div>
