# Collatz Scrambling Protocol

> Cross-universe observation protocol for Emanon. Logs compress and scramble
> between universes using the Syracuse function T(n). P-adic closeness reduces
> bandwidth cost because 2-adic determinism lets the observer infer parity bits
> from their own log's structure.
>
> Drafted 2026-04-13 from the brainstorming session establishing hex=universe,
> entanglement=p-adic closeness, and the Collatz dynamics as the physics of
> information exchange.

## Overview

Every universe has a log. The log is a sequence of events interpreted as a
big integer n. When information crosses between universes, the source's log
is scrambled by k iterations of the Syracuse function:

```
T(n) = (3n + 1) / 2   if n is odd
T(n) = n / 2          if n is even
```

The observer receives T^k(n_source) and some number of parity bits. Parity
bits are the bandwidth currency. Each parity bit w_i tells whether the i-th
iteration was an odd-step (1) or even-step (0). Given the parity word w and
the final value T^k(n), the source is uniquely recoverable.

Without the parity word, T^k(n) is ambiguous — many source values collide to
the same scrambled value.

**The key insight** from your 2-adic determinism proof: the first k parity
bits of T(n) are determined entirely by n mod 2^k. So if your log agrees
with the target's log mod 2^k, the first k parity bits are identical
between you and the target. You can infer those bits from your own history
at zero cost. You only need bandwidth for the parity bits past your shared
prefix.

P-adic closeness = shared 2-adic structure = shared parity prefix = free
bandwidth.

## Log Encoding

A universe's log is a big integer n, constructed by appending event bits as
they are emitted:

```
append_event(log, event) -> log * 2^bits_per_event + event_bits
```

Log growth is monotone. Log values rapidly become astronomical — this is
fine, the protocol operates on arbitrary-precision integers.

**Interpretation layer** — the integer IS the log. Decoding it into discrete
events is a separate concern for display and search. The protocol only cares
about the integer value.

**Genesis prefix** — all universes fork from a shared genesis event. The
low-order bits of every universe's log are identical: the genesis bits.
Divergence happens at higher bits as histories differ.

## The Scrambling Function

The game's canonical scrambler is the Syracuse function:

```python
def syracuse(n):
    return (3*n + 1) // 2 if n % 2 else n // 2

def syracuse_k(n, k):
    parity = []
    for _ in range(k):
        parity.append(n % 2)
        n = syracuse(n)
    return n, parity
```

`syracuse_k(n, k)` returns the scrambled value T^k(n) and the parity word
w = [w_0, ..., w_{k-1}].

This is exactly `collatz/core.py` already in the repo — the scrambler is the
same dynamics you've been studying.

## Parity Words as Bandwidth

An observation transaction transmits three things:

1. The scrambled value s = T^k(n_source) — always transmitted (cheap, one integer)
2. The depth k — how many iterations were applied
3. Some number b of parity bits from the parity word w

**Bandwidth unit** — one parity bit is the atomic unit. 1 B = 1 bit of
decoded determinism into the source's log history.

**Observation cost** — scales with the number of parity bits transmitted.
The scrambled value itself is free (it's just a number, compressible by
standard means). The information content is in the parity word.

## Invertibility and Reconstruction

Given (s, k, w) the observer reconstructs n_source:

```python
def invert(scrambled, parity):
    n = scrambled
    for bit in reversed(parity):
        if bit == 1:    # odd step: n was odd, scrambled = (3n+1)/2
            n = (2 * n - 1) // 3
        else:            # even step: n was even, scrambled = n/2
            n = 2 * n
    return n
```

If the parity word is correct, this returns n_source exactly.

If the parity word is truncated (only first b < k bits), the observer gets
an **orbit family**: all integers n such that T^b(n) = s_{k-b} (the value
after k-b unknown iterations) with the known b bits as prefix. The size of
this family grows exponentially with k-b.

If the parity word has errors, the observer reconstructs a neighboring
integer in the same residue class mod 2^position — often wildly different
numerically, even with a single bit wrong.

## P-adic Bandwidth Savings

**Theorem (your 2-adic determinism result):** For the Syracuse function T,
the first k parity bits of T applied to n are determined by n mod 2^k.

**Corollary:** If n_observer and n_source agree mod 2^k, then:

```
parity(n_source, k) == parity(n_observer, k)  for the first k bits
```

So the observer can compute the first k parity bits from their own log at
zero bandwidth. The bandwidth is only needed for parity bits after the
shared prefix ends.

**Shared prefix depth:**

```python
def shared_prefix_depth(n_a, n_b):
    """Largest k such that n_a ≡ n_b (mod 2^k)"""
    if n_a == n_b:
        return ∞
    diff = n_a ^ n_b       # bitwise xor
    return bit_position_of_lowest_set_bit(diff)
```

This is exactly v₂(n_a - n_b), the 2-adic valuation of their difference.

**Bandwidth requirement for observation to depth k:**

```
bandwidth_needed(observer, source, k) = max(0, k - shared_prefix_depth(observer, source))
```

## Distance and Bandwidth

The game's two distances map directly onto the scrambling protocol:

### P-adic distance → parity prefix length (bandwidth efficiency)

Universe at hex (q_a, r_a), observer at (q_b, r_b):

- v₂(N(Δq, Δr)) where N is the Eisenstein norm governs how deep the shared
  log prefix goes
- Deep p-adic closeness = long shared parity prefix = cheap observation
- P-adic distant = short shared prefix = expensive observation

### Euclidean distance → propagation delay

- Grid distance × local time-per-hex = how many ticks ago the observed log
  state was emitted
- Far away on the grid = observing old news
- Close on the grid = observing recent history

These are independent: you can be Euclidean-far and p-adic-close (old news
that decodes cheaply) or Euclidean-close and p-adic-far (recent news that
costs a fortune to decode).

## Game Action Mapping

### Scan (cheap, shallow)

- Receives T^k(n_source) for small k (maybe k=3 to 5)
- Transmits only 1-2 parity bits
- Observer fills the rest from their own log's 2-adic structure
- Good intel only for p-adically close targets
- Classes p-adically-far targets as "noise" — you see the scrambled value
  but can't distinguish it from millions of other possible sources

### Probe (medium, one-shot)

- Requests depth k iterations
- Allocates bandwidth B to parity bits
- Receives min(k, shared_prefix + B) parity bits total
- Reconstructs orbit family if B < k - shared_prefix, else exact log
- Cost scales with k × B × distance_factor

### Entangle (expensive, persistent)

- Standing channel to target
- Each tick, transmits delta parity bits (new events since last tick)
- Observer maintains a rolling reconstruction of the target's log
- Can only be established where shared_prefix_depth ≥ minimum threshold
  (you can't entangle with a p-adically distant universe because the
  bandwidth would be prohibitive)

### Emit (cheap, always)

- Append to your own log
- If you're entangled with another universe, your emissions ripple through
  the channel — their observer sees your new events via their standing
  entanglement

### Compress (variable, produces energy)

- Run k iterations of T on your own log
- Produces energy proportional to log₂(log_before) - log₂(log_after)
- This is the stellar mechanic: stars are locally running T on your log to
  extract the compression differential
- After compression, your log is smaller (the T^k scrambled version) — you
  lose recent divergent history but retain the deep structure

## Conservation Law (In-Game)

Your conservation law `s · log₂(6) = T - log₂(n) + ε` governs the
fundamental game economy:

- **T** = observation depth (how many iterations you look through)
- **s** = number of odd-step parity bits in the window (information-bearing
  bits)
- **log₂(n)** = size of your log
- **log₂(6)** = the base-6 rate

Each observation/compression event must satisfy this law within its ε
slack. You can't observe more depth than your log size supports. You can't
compress faster than the 3-growth/2-decay balance allows.

This is not a soft constraint — it's the fundamental thermodynamics of the
multiverse. The game engine enforces it. Every action is validated against
this identity.

## Implementation Notes

### Existing code to reuse

- `collatz/core.py` — `orbit(n)`, `stopping_time(n)`, `dropping_time(n)`
  are the scrambler and its measurements
- `collatz/dropping.py` — `dropping_genus(n)` gives (s, M, I) signature
  which maps to (odd-step count, modulus, index) for bandwidth accounting
- `collatz/stopping.py` — stopping class computations
- `collatz/factorization.py` — for prime addressing and entanglement
  compatibility checks

### New code needed

- `emanon/engine/scrambler.py` — wraps `collatz.core` with the observation
  protocol: encode/decode/bandwidth calculation
- `emanon/engine/observation.py` — scan/probe/entangle action resolution
- `emanon/engine/conservation.py` — validate every cross-universe
  transaction against `s·log₂(6) = T - log₂(n) + ε`

### Performance

Logs grow to astronomical size quickly. The protocol uses Python's arbitrary
precision integers, which handle this natively but slow down.

Mitigation: at the game level, logs are periodically **compressed by stars**
— run k iterations of T, replacing the log with T^k(log). This bounds log
size. The observer's tradeoff: compress often (small logs, fast protocol,
shallow historical access) vs. compress rarely (deep history, expensive
observation).

## Worked Example

Universe A at hex (0, 0) — log value n_A = 127 (binary: 1111111)
Universe B at hex (-3, 3) — log value n_B = 127 + 3^3·δ for some small δ...

Actually let's use concrete numbers. Say:
- n_A = 27 (your Paper 1 example)
- n_B = 91 = 27 + 64 = 27 + 2^6

Then n_A XOR n_B = 64, lowest set bit at position 6.
shared_prefix_depth = 6.

If observer A wants to observe B to depth 10:
- bandwidth_needed = 10 - 6 = 4 bits
- Transmit: T^10(91) = [some integer], plus 4 parity bits (positions 6-9 of B's parity word)
- Observer fills positions 0-5 of the parity word from their own T(27) computation
- Reconstruction: exact log of B

If observer A wants to observe B to depth 20:
- bandwidth_needed = 20 - 6 = 14 bits
- Much more expensive

If universe C is at n_C = 27 + 2 = 29 (shared_prefix_depth = 1):
- Observing C to depth 10 costs 9 bits
- Nearly the full parity word has to be transmitted

This directly demonstrates p-adic bandwidth pricing.

## Open Questions

- What exactly counts as one "parity bit" of bandwidth in energy units?
  Linear, logarithmic, something else?
- How are observation errors (wrong parity bits) handled? Do they corrupt
  the observer's view or do they introduce uncertainty explicitly?
- Can players deliberately falsify parity bits to deceive observers?
  (Information warfare)
- How does the conservation law cap work — soft cost or hard limit?
- Should the encoding of events into log bits respect event boundaries
  (byte-aligned) or pack densely?
- When stars compress your log, do they destroy the parity word or preserve
  it for future re-derivation? (Affects depth of historical access)
- Entanglement persistence: does the shared prefix depth change over time
  as both universes accumulate new events, or is it locked at the moment of
  entanglement?
