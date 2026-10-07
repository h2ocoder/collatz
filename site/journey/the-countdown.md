# The Countdown

The carry propagation in $3n+1$ is not random. It's a **countdown timer**.

## The v₂ countdown

For any odd number $m$, define $v_2(m+1)$ — the exponent of the largest power of 2 dividing $m+1$. This number has a magical property:

**It decreases by exactly 1 at every non-dropping Syracuse step.**

Watch it in action:

<CountdownVisualizer />

Step through the orbit and watch the $v_2(m+1)$ counter. When $m \equiv 3 \pmod{4}$ (non-dropping step), the counter ticks down: $v_2 \to v_2 - 1$. When it reaches 1, the current value is $m \equiv 1 \pmod{4}$ — a member of **Set₃** — and the next odd value is smaller than it. (The two widgets on this page are exact for starts below 100,000. Above about 113,000 some orbits pass what their 32-bit arithmetic can hold, and they then show a wrong orbit.)

This is **deterministic**. Not statistical. Not "on average." The countdown will reach 1, and the orbit will take a step down. It is a step down from the current value, not a fall below the starting value: the orbit climbed by a factor of about $3/2$ at every tick, and more often than not it is still above where the countdown began (in 57 per cent of cases, for the $m \equiv 3 \pmod{4}$ below 200,000).

## Why does the countdown work?

**Theorem (elementary; no novelty claimed).** For $m \equiv 3 \pmod{4}$: $v_2(S(m)+1) = v_2(m+1) - 1$.

**Proof.** Write $m = 2^v c - 1$ where $c$ is odd and $v = v_2(m+1)$. The Syracuse step gives $S(m) = (3m+1)/2 = 3 \cdot 2^{v-1} c - 1$. Then $S(m) + 1 = 3 \cdot 2^{v-1} c$, so $v_2(S(m)+1) = v-1$. ∎

Starting from $v$: after exactly $v-1$ steps, $v_2 = 1$, meaning $m \equiv 1 \pmod{4}$. The orbit has reached a member of Set₃.

## The two-bit countdown

A member of Set₃ steps down to about 3/4 of its value, or lower. A "weak drop" is the 3/4 case. Not very powerful. But there's a **second countdown**: $v_2(m-1)$ counts down through a run of weak drops.

At Set₃ encounters with $m \equiv 1 \pmod{8}$: the drop depth is only 2 (weak, factor 3/4). But with $m \equiv 5 \pmod{8}$: the drop depth is $\geq 3$ (medium or strong, factor $\leq 3/8$).

The second countdown ends every run of weak drops. Each weak drop lowers $v_2(m-1)$ by exactly 2: write $m = 1 + 2^w c$ with $c$ odd and $w \geq 3$, and the next odd value is $(3m+1)/4 = 1 + 3 \cdot 2^{w-2} c$. If $v_2(m-1)$ started even, the run ends at $v_2(m-1) = 2$, which is $m \equiv 5 \pmod{8}$: a deep drop. If it started odd, the run ends at $v_2(m-1) = 1$, which is $m \equiv 3 \pmod{4}$: no deep drop, and the orbit starts climbing again. Among the $m \equiv 1 \pmod{8}$ the odd case is the commoner one, two times in three.

## Drop depth = 2-adic distance from $-1/3$

Here's a lovely way to see it: the drop depth $v_2(3m+1)$ counts how many of the **lowest binary digits of $m$ match the pattern $\ldots 010101$**.

That pattern is $-1/3$ in the 2-adic integers. The number $-1/3 = \ldots 01010101_2$ (the alternating binary pattern).

$$v_2(3m+1) \geq k \quad \Longleftrightarrow \quad m \equiv -\tfrac{1}{3} \pmod{2^k}$$

Explore it: watch the binary digits of each orbit value alongside the $-1/3$ pattern. Green highlights show matching digits.

<DepthExplorer />

Deep drops happen when $m$ "accidentally" agrees with $-1/3$ in many binary digits. The more digits match, the deeper the drop:

| Matching digits | Depth | Factor | Residue |
|----------------|-------|--------|---------|
| 2 | 2 | 3/4 | $m \equiv 1 \pmod{8}$ |
| 3 | 3 | 3/8 | $m \equiv 13 \pmod{16}$ |
| 4 | 4 | 3/16 | $m \equiv 5 \pmod{32}$ |
| 5 | 5 | 3/32 | $m \equiv 53 \pmod{64}$ |
| 6 | 6 | 3/64 | $m \equiv 21 \pmod{128}$ |

Each depth level has **exactly one** residue class. The deeper levels give more powerful contraction but occur less frequently (density $1/2^k$).

## What the countdowns give, and what they don't

The countdown hierarchy:

1. **One-Bit Countdown** (elementary, proved above): $v_2(m+1)$ decreases by 1 per step → every climb ends at a member of Set₃
2. **Two-Bit Countdown** (elementary, shown above): $v_2(m-1)$ decreases by 2 per weak drop → every run of weak drops ends, in a deep drop if $v_2(m-1)$ started even and in a new climb if it started odd
3. **Bounce regime**: at $v_2(m-1) = 3$ a weak drop is followed straight away by a new climb, and the orbit can go round again. How long it can keep bouncing is not proved; the next chapter gives a heuristic picture.

The countdowns are deterministic — they work for every orbit, not just typical ones. But they do not show convergence: each drop contracts, and the orbit grows between drops. Whether the drops always win is the open question. The next chapter is one way of thinking about it.

<div style="text-align: center; margin-top: 24px;">
  <a href="./the-rotation" class="vp-button medium">← The Hidden Rotation</a>
  <a href="./finite-fuel" class="vp-button medium brand" style="margin-left: 12px;">Next: Finite Fuel →</a>
</div>
