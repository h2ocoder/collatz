# Finite Fuel

This chapter is a **heuristic picture**, not a proof. It is my favourite way of thinking about why positive integers might behave differently from other number systems where the same rule has loops.

Here's the idea: **natural numbers end.**

A natural number like 76,827 has 17 bits: `10010110000011011`. After bit 17, every digit is 0. Forever. This is what "finite" means in binary.

A 2-adic integer like $-1 = \ldots 11111$ has **infinitely many** nonzero bits. It never ends. And under the very same rule, $-1 \to -2 \to -1$ loops forever. So if every positive integer does fall to 1, the reason has to use the fact that their bits run out. That is the intuition behind this chapter.

## The fuel gauge

In this chapter a *bounce* (the rows the simulator below marks BOUNCE) is a visit to Set₃ with $m \equiv 41 \pmod{128}$, a special case of the bounce regime of the countdown chapter. It is a weak drop followed by a climb of at least four steps, so the number comes out at least $243/64$ times larger than it went in. Which bounces happen depends on more and more of the starting number's binary digits. The picture keeps two tallies per bounce:
- **1.92 bit positions** read by the carry: $\log_2(243/64)$
- **0.51 new bits** from growth: $3 \log_2(9/8)$, where $9/8 = \tfrac34 \cdot \tfrac32$ is a weak drop times a single climbing step
- **Net: about 1.4 bits per bounce**

These are bookkeeping constants read off the algebra of single steps, not measured averages. (The 1.92 is also the least the number itself grows across a bounce, so the number gains at least as many bits as the tally says are read.) Nothing here shows that any orbit uses up its bits at this rate.

The gauge below runs the same tally: 1.92 for each BOUNCE row and 0.5 for every other visit to Set₃. It is not measured from the number's bits.

<BounceSimulator />

Try these (rows are numbered from 0):
- **76,827** (17 bits) — BOUNCE at rows 0 and 3, then a strong drop at row 6
- **1,227,079** (21 bits) — two BOUNCE rows before its first deep drop at row 14, and three more later in the orbit
- **27** (5 bits) — a BOUNCE at row 0, a deep drop at row 6, and a second BOUNCE at row 8, by which time the tally has passed the 5-bit budget
- Any odd number up to 300 million. (The arithmetic is exact for every start below 319,804,831; from there on an orbit can climb past $2^{53}$ and would be shown wrongly.)

## The event horizon

A natural number with $B$ bits has an **event horizon** at position $B$: beyond this, all bits are zero. In the picture, each bounce reads bits at higher positions than the last. When the reading window crosses the event horizon, the bits it reads are all zero. The guess at the heart of this picture is that zeros cannot go on satisfying the bounce condition for long, so the bounce sequence stops. That guess is not proved.

**By computer:** counting bounces only up to an orbit's first deep drop (depth 3 or more), there are at most $(B+3)/4$ of them for every odd starting value up to $5 \times 10^6$. Over a whole orbit there can be more: 2919 has four, with $B = 12$. That is evidence, not a proof — the orbit's growth also moves the event horizon, and nobody has shown the reading window always wins the race.

## The speed-of-light analogy

| Physics | Collatz |
|---------|---------|
| Speed of light $c$ | Carry propagation: ~1.92 bits/bounce |
| Object velocity | Orbit growth: ~0.51 bits/bounce |
| Finite energy | Natural number: $B$ bits |
| Event horizon | Position $B$: all zeros beyond |

The picture: if the carry reads bits faster than the orbit generates them, a finite budget should eventually be exhausted. The rates above are bookkeeping, not measurements, and even a measured average would say nothing about every orbit. That step, from an average to every orbit, is exactly the hard part of the Collatz conjecture, and this picture does not take it.

## Natural numbers vs 2-adic integers

See the difference side by side:

<NaturalVs2Adic />

**Natural number** ($B$ bits, then zeros):
- Fuel: $B$ bits
- Consumption: about 1.4 bits per bounce in the picture's bookkeeping
- In every example tested: the bounces come to an end and the orbit reaches 1

**2-adic integer with infinitely many 1-bits**:
- Fuel: unlimited
- Bounces: can go on forever
- Example: the negative integers $-1$, $-5$ and $-17$ each sit on a cycle, and in 2-adic terms they have infinitely many 1-bits

## What is missing

To make this an argument one would need to show that, for **every** positive integer, the constraints imposed at successive bounces cannot all be satisfied by its finitely many bits. What is elementary is local: what a single bounce does to the number (a weak drop followed by at least four climbing steps). The claim that successive bounces must run out of bits is open.

$$\text{Finite bits} \overset{?}{\implies} \text{finite bounces} \overset{?}{\implies} \text{deep drops} \overset{?}{\implies} \text{reaching } 1$$

<div style="text-align: center; margin-top: 24px;">
  <a href="./the-countdown" class="vp-button medium">← The Countdown</a>
  <a href="./the-picture" class="vp-button medium brand" style="margin-left: 12px;">Next: The Big Picture →</a>
</div>
