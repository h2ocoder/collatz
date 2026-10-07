# The Puzzle

Pick any positive integer. Apply two simple rules:
- If it's **even**, divide by 2
- If it's **odd**, multiply by 3 and add 1

Repeat. Does the sequence always reach 1?

This is the **Collatz conjecture** — proposed in 1937, checked by computer for every number up to at least $2^{68}$, and still unproven. Paul Erdos said: *"Mathematics is not yet ready for such problems."*

This tour won't solve it. It is a hands-on look at why the problem is so slippery, and at some of the structure people (including me) have found along the way.

## Try it yourself

Type any number up to 999,999 and watch its orbit. Try to find one that doesn't reach 1. (The widget's arithmetic is exact for every start below 319,804,831, so in this range what it shows is the true orbit.)

<OrbitPlayground />

Notice: the orbit bounces chaotically — sometimes climbing to enormous heights — but every number anyone has ever tried eventually comes back down. The number 27 reaches a peak of 9,232 before eventually settling to 1 after 111 steps.

## The view from above

Drag the slider to sweep across starting values. Watch how orbit shapes change — then toggle the log scale.

<HailstoneChart />

In raw values, the orbits look chaotic. In **log₂ scale** (which measures the *bit-length* of the number) the picture is calmer: every halving is one step down and every tripling about 1.58 steps up. Every orbit on this slider ends at 1, but most of them climb above their starting value first: 27 gains more than eight bits before it falls.

## Two threats

For the conjecture to fail, one of two things would need to happen:

1. **A loop**: the orbit could cycle forever without reaching 1 (like a car driving in circles)
2. **Escape to infinity**: the orbit could grow without bound (like a rocket that never runs out of fuel)

Nobody has ruled out either one. The tour ahead:

| Chapter | Question | Result |
|---------|----------|--------|
| [The Binary Engine](./binary-engine) | What does Collatz do to the *bits*? | A halving removes one bit; a tripling adds one or two |
| [No Loops?](./no-loops) | Can orbits get stuck cycling? | Why a loop needs $2^E$ to sit just above $3^S$, and what is known |
| [The Hidden Rotation](./the-rotation) | Why do orbits look quasi-periodic? | In base-6 coordinates it looks like a wobbly irrational rotation |
| [The Countdown](./the-countdown) | What does the +1 do to the low bits? | It runs a countdown: every climb ends in a step down |
| [Finite Fuel](./finite-fuel) | Why might positive integers be special? | A heuristic: natural numbers have finitely many bits |
| [The Big Picture](./the-picture) | How does it all fit together? | A map of the ideas, and what is still open |

Ready? Let's look at the bits.

<div style="text-align: center; margin-top: 24px;">
  <a href="./binary-engine" class="vp-button medium brand">Next: The Binary Engine →</a>
</div>
