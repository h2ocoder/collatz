# The Countdown

The carry propagation in $3n+1$ is not random. It's a **countdown timer**.

## The v₂ countdown

For any odd number $m$, define $v_2(m+1)$ — the largest power of 2 dividing $m+1$. This number has a magical property:

**It decreases by exactly 1 at every non-dropping Syracuse step.**

Watch it in action:

<CountdownVisualizer />

Step through the orbit and watch the $v_2(m+1)$ counter. When $m \equiv 3 \pmod{4}$ (non-dropping step), the counter ticks down: $v_2 \to v_2 - 1$. When it reaches 1, the orbit is forced into $m \equiv 1 \pmod{4}$ — **Set₃** — and drops.

This is **deterministic**. Not statistical. Not "on average." The countdown WILL reach zero, and the orbit WILL drop.

## Why does the countdown work?

**Theorem.** For $m \equiv 3 \pmod{4}$: $v_2(S(m)+1) = v_2(m+1) - 1$.

**Proof.** Write $m = 2^v c - 1$ where $c$ is odd and $v = v_2(m+1)$. The Syracuse step gives $S(m) = (3m+1)/2 = 3 \cdot 2^{v-1} c - 1$. Then $S(m) + 1 = 3 \cdot 2^{v-1} c$, so $v_2(S(m)+1) = v-1$. ∎

Starting from $v$: after exactly $v-1$ steps, $v_2 = 1$, meaning $m \equiv 1 \pmod{4}$. The orbit enters Set₃.

## The two-bit countdown

Set₃ gives a "weak drop" — contraction by 3/4. Not very powerful. But there's a **second countdown**: $v_2(m-1)$ tracks the approach to a **deep drop**.

At Set₃ encounters with $m \equiv 1 \pmod{8}$: the drop depth is only 2 (weak). But with $m \equiv 5 \pmod{8}$: the drop depth is $\geq 3$ (medium or strong, factor $\leq 3/8$).

The second countdown forces the orbit from weak drops to deep drops. It decreases by 2 per immediate weak drop. When it's exhausted: a deep drop is forced.

## Drop depth = 2-adic distance from $-1/3$

Here's the deepest insight: the drop depth $v_2(3m+1)$ counts how many **leading binary digits of $m$ match the pattern $\ldots 010101$**.

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

## What we've proved

The countdown hierarchy:

1. **One-Bit Countdown** (proved): $v_2(m+1)$ decreases by 1 per step → forces Set₃
2. **Two-Bit Countdown** (proved): $v_2(m-1)$ decreases by 2 per immediate weak drop → forces deep drops
3. **Bounce regime**: at $v_2(m-1) = 3$, the orbit can oscillate before exiting → bounded by the **Finite Propagation Theorem**

The countdowns are deterministic — they work for EVERY orbit, not just typical ones. But they don't yet prove convergence: each deep drop contracts, but the orbit grows between drops. We need one more insight: the orbit's **fuel runs out**.

<div style="text-align: center; margin-top: 24px;">
  <a href="./the-rotation" class="vp-button medium">← The Hidden Rotation</a>
  <a href="./finite-fuel" class="vp-button medium brand" style="margin-left: 12px;">Next: Finite Fuel →</a>
</div>
