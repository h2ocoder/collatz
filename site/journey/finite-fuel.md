# Finite Fuel

This chapter is a **heuristic picture**, not a proof. It is my favourite way of thinking about why positive integers might behave differently from other number systems where the same rule has loops.

Here's the idea: **natural numbers end.**

A natural number like 76,827 has 17 bits: `10010110000011011`. After bit 17, every digit is 0. Forever. This is what "finite" means in binary.

A 2-adic integer like $-1 = \ldots 11111$ has **infinitely many** nonzero bits. It never ends. And under the very same rule, $-1 \to -2 \to -1$ loops forever. So whatever makes positive integers fall to 1, it has to use the fact that their bits run out. That is the intuition behind this chapter.

## The fuel gauge

The bounce mechanism (from the countdown chapter) reads bits from the number's binary representation. In the numbers I have tested, at each bounce:
- The **carry propagation** shifts the reading window by about **1.92 bit positions** on average
- The **orbit growth** adds only about **0.51 new bits** per bounce on average (from the 9/8 growth factor)
- **Net consumption: about 1.4 bits per bounce**

These are averages. Nothing here shows that every individual orbit behaves like the average.

Watch the fuel drain:

<BounceSimulator />

Try these:
- **76,827** (17 bits) — 4 bounces, then the bounces stop and a deep drop follows
- **1,227,079** (21 bits) — 5 bounces, more fuel, same outcome
- **27** (5 bits) — very little fuel, drops quickly
- Any number you like

## The event horizon

A natural number with $B$ bits has an **event horizon** at position $B$: beyond this, all bits are zero. The bounce mechanism reads bits at progressively higher positions. When the reading window crosses the event horizon, the bits it reads are zero, and zero bits rarely satisfy the bounce condition, so the bounce sequence tends to stop.

**By computer:** the number of bounces is at most $(B+3)/4$ for every $m \leq 5 \times 10^6$, with no exceptions. That is evidence, not a proof — the orbit's growth also moves the event horizon, and nobody has shown the reading window always wins the race.

## The speed-of-light analogy

| Physics | Collatz |
|---------|---------|
| Speed of light $c$ | Carry propagation: ~1.92 bits/bounce |
| Object velocity | Orbit growth: ~0.51 bits/bounce |
| Finite energy | Natural number: $B$ bits |
| Event horizon | Position $B$: all zeros beyond |

The picture: the carry reads bits faster, on average, than the orbit generates them, so a finite budget should eventually be exhausted. Turning "on average" into "for every orbit" is exactly the hard part of the Collatz conjecture, and this picture does not do it.

## Natural numbers vs 2-adic integers

See the difference side by side:

<NaturalVs2Adic />

**Natural number** ($B$ bits, then zeros):
- Fuel: $B$ bits
- Consumption: ~1.4 bits/bounce on average
- In every example tested: the bounces stop, a deep drop follows

**2-adic integer** (infinitely many bits):
- Fuel: unlimited
- Bounces: can go on forever
- Example: the negative integers $-1$, $-5$ and $-17$ each sit on a cycle, and in 2-adic terms they have infinitely many 1-bits

## What is missing

To make this an argument one would need to show that, for **every** positive integer, the constraints imposed at successive bounces cannot all be satisfied by its finitely many bits. The pieces I can prove are local (what one bounce requires of the next few bits); the claim that they combine into a bound for every orbit is open.

$$\text{Finite bits} \overset{?}{\implies} \text{finite bounces} \overset{?}{\implies} \text{deep drops} \overset{?}{\implies} \text{reaching } 1$$

<div style="text-align: center; margin-top: 24px;">
  <a href="./the-countdown" class="vp-button medium">← The Countdown</a>
  <a href="./the-picture" class="vp-button medium brand" style="margin-left: 12px;">Next: The Big Picture →</a>
</div>
