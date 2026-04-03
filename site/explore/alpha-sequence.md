# Alpha Sequence Explorer

## What is an Alpha Sequence?

Every time you hit an **odd number** in the Collatz sequence, two things happen:
1. You compute $3n + 1$ (which always gives an even number)
2. You keep **halving** until you reach the next odd number

The **alpha value** is simply **how many times you halved**. The alpha sequence records this for every odd number you visit, all the way down to 1.

### Example: n = 7

| Odd number | $3n+1$ | Result | Halvings | Alpha |
|---|---|---|---|---|
| 7 | $3(7)+1 = 22$ | $22 \to 11$ | 1 | **1** |
| 11 | $3(11)+1 = 34$ | $34 \to 17$ | 1 | **1** |
| 17 | $3(17)+1 = 52$ | $52 \to 26 \to 13$ | 2 | **2** |
| 13 | $3(13)+1 = 40$ | $40 \to 20 \to 10 \to 5$ | 3 | **3** |
| 5 | $3(5)+1 = 16$ | $16 \to 8 \to 4 \to 2 \to 1$ | 4 | **4** |

**Alpha sequence of 7:** $[1, 1, 2, 3, 4]$

The alpha sequence is the **DNA of the orbit** — it completely determines its shape.

## Why It Matters

- **sum(alphas)** = total number of halvings (even steps) in the orbit
- **len(alphas)** = total number of $3n+1$ steps (odd steps)
- **Distinct alphas** = the "alphabet" the orbit uses
- **Collatz radical** = product of distinct alpha values (like the [radical](/connections/abc-conjecture) in number theory)
- **Collatz quality** = $\log_2(n) / \log_2(\text{radical})$ — how much "size" $n$ has per unit of orbital complexity

### Smooth vs. Rough Orbits

A **smooth orbit** uses few distinct alpha values — the 3n+1 steps keep hitting similar powers of 2. The smoothest possible orbit has $3n+1 = 2^k$ exactly, giving alpha sequence $[k]$ (a single step!).

A **rough orbit** uses many distinct alpha values — the 3n+1 steps produce varied results, and the orbit wanders.

The connection to the [abc conjecture](/connections/abc-conjecture): in both cases, "quality" measures how well **addition** ($3n+1$) aligns with **multiplicative structure** (powers of 2). The abc conjecture says this alignment is fundamentally limited.

## Try It Yourself

Enter any odd number to see its alpha sequence, radical, and quality:

<AlphaExplorer />

### Numbers to Try

- **3** — Simple: alpha sequence $[1, 4]$, two steps
- **7** — Classic: $[1, 1, 2, 3, 4]$, five distinct behaviors
- **27** — The famous slow number: 41 odd steps, reaches 9232 before descending
- **5461** — Binary $1010101010101$: alpha sequence $[14]$, one step! $3(5461)+1 = 2^{14}$
- **7253** — Highest quality under 10000: alpha $[8, 8]$, just two steps
- **1** — Trivial: already at 1, empty alpha sequence
