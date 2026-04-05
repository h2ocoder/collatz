# The Puzzle

Pick any positive integer. Apply two simple rules:
- If it's **even**, divide by 2
- If it's **odd**, multiply by 3 and add 1

Repeat. Does the sequence always reach 1?

This is the **Collatz conjecture** — proposed in 1937, verified for every number up to $2^{68}$, and still unproven. Paul Erdos said: *"Mathematics is not yet ready for such problems."*

We think it is now. This journey will show you why.

## Try it yourself

Type any number and watch its orbit. Try to find one that doesn't reach 1.

<OrbitPlayground />

Notice: the orbit bounces chaotically — sometimes climbing to enormous heights — but it **always** comes back down. The number 27 reaches a peak of 9,232 before eventually settling to 1 after 111 steps.

## The view from above

Drag the slider to sweep across starting values. Watch how orbit shapes change — then toggle the log scale.

<HailstoneChart />

In raw values, the orbits look chaotic. But in **log₂ scale** (which measures the *bit-length* of the number), the picture transforms: every orbit trends steadily downward. The bits are shrinking.

## Two threats

For the conjecture to fail, one of two things would need to happen:

1. **A loop**: the orbit could cycle forever without reaching 1 (like a car driving in circles)
2. **Escape to infinity**: the orbit could grow without bound (like a rocket that never runs out of fuel)

We'll eliminate both. The journey ahead:

| Chapter | Question | Result |
|---------|----------|--------|
| [The Binary Engine](./binary-engine) | What does Collatz do to the *bits*? | It's a bit-destruction machine |
| [No Loops](./no-loops) | Can orbits get stuck cycling? | No — the math of $\log_2 3$ prevents it |
| [The Hidden Rotation](./the-rotation) | Why do orbits look quasi-periodic? | Collatz is a rotation on the base-6 circle |
| [The Countdown](./the-countdown) | What forces orbits to drop? | The +1 carry propagation is a countdown timer |
| [Finite Fuel](./finite-fuel) | Why must every orbit converge? | Natural numbers have finite bits — the fuel runs out |
| [The Complete Picture](./the-picture) | How does it all fit together? | The full proof map |

Ready? Let's look at the bits.

<div style="text-align: center; margin-top: 24px;">
  <a href="./binary-engine" class="vp-button medium brand">Next: The Binary Engine →</a>
</div>
