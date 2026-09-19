# The Puzzle

Pick any positive integer. Apply two simple rules:
- If it's **even**, divide by 2
- If it's **odd**, multiply by 3 and add 1

Repeat. Does the sequence always reach 1?

This is the **Collatz conjecture** — proposed in 1937, checked by computer for every number up to at least $2^{68}$, and still unproven. Paul Erdos said: *"Mathematics is not yet ready for such problems."*

This tour won't solve it. It is a hands-on look at why the problem is so slippery, and at some of the structure people (including me) have found along the way.

## Try it yourself

Type any number and watch its orbit. Try to find one that doesn't reach 1.

<OrbitPlayground />

Notice: the orbit bounces chaotically — sometimes climbing to enormous heights — but every number anyone has ever tried eventually comes back down. The number 27 reaches a peak of 9,232 before eventually settling to 1 after 111 steps.

## The view from above

Drag the slider to sweep across starting values. Watch how orbit shapes change — then toggle the log scale.

<HailstoneChart />

In raw values, the orbits look chaotic. But in **log₂ scale** (which measures the *bit-length* of the number), the picture transforms: the orbits trend downward. The bits are shrinking.

## Two threats

For the conjecture to fail, one of two things would need to happen:

1. **A loop**: the orbit could cycle forever without reaching 1 (like a car driving in circles)
2. **Escape to infinity**: the orbit could grow without bound (like a rocket that never runs out of fuel)

Nobody has ruled out either one. The tour ahead:

| Chapter | Question | Result |
|---------|----------|--------|
| [The Binary Engine](./binary-engine) | What does Collatz do to the *bits*? | It's a bit-destruction machine |
| [No Loops](./no-loops) | Can orbits get stuck cycling? | Why a loop needs $2^E$ to sit just above $3^S$, and what is known |
| [The Hidden Rotation](./the-rotation) | Why do orbits look quasi-periodic? | In base-6 coordinates it looks like a wobbly irrational rotation |
| [The Countdown](./the-countdown) | What forces orbits to drop? | The +1 carry propagation is a countdown timer |
| [Finite Fuel](./finite-fuel) | Why might positive integers be special? | A heuristic: natural numbers have finitely many bits |
| [The Big Picture](./the-picture) | How does it all fit together? | A map of the ideas, and what is still open |

Ready? Let's look at the bits.

<div style="text-align: center; margin-top: 24px;">
  <a href="./binary-engine" class="vp-button medium brand">Next: The Binary Engine →</a>
</div>
