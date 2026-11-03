---
tags: [schwarzschild, information-theory, large-deviations, kesten]
status: verified
created: 2026-11-02
jira: SCRUM-65
---

# Information Radius

The address-space face of the dictionary. Code: `collatz/schwarzschild/rates.py`, `collatz/schwarzschild/tape.py`. Experiments: E1, E3, E4, E6.

Write S_t(x) = log₂(Q_t/d^t) for the scale walk of x, where Q_t is the product of the first t multipliers.

## 1. The speed of light — Proved, Verified

**Causal cone.** T^t(n) mod d^m depends only on n mod d^(m+t).

**Proof.** If n ≡ n′ mod d^(m+1) then they share a branch r and T(n) − T(n′) = q_r (n − n′)/d ≡ 0 mod d^m. Induct on t. ∎

**Sharpness.** Adding d^p to n leaves the first p digits of the word unchanged and always changes digit p, because it moves T^p(n) by Q_p, which is prime to d.

So every step reads exactly one address digit, whichever branch it takes. That is the semantic content of c: the same for every orbit, independent of how the size moves. The word of length t and n mod d^t are in bijection (Terras 1976 for 3x+1, Möller 1978 and Matthews–Watts 1984 for general maps), so under Haar measure the digits are independent and uniform.

    c = log₂ d    (1 bit per step for 3x+1)

Tested for nine maps.

## 2. Gravity, memory and the ledger — Proved, exact under Haar

Exact identity along any orbit with positive values:

    log₂ T^t(n) = log₂ n − t log₂ d + Σ log₂ q_{r_i} + Σ log₂(1 + a_{r_i}/(q_{r_i} n_i))

Under Haar measure the first two sums have rates that give

    c = g + m

| rate | meaning | 3x+1 |
|---|---|---|
| c = log₂ d | address read per step | 1 |
| g = c − m | size lost per step | 0.2075 |
| m = E[log₂ q_r] | written into residues mod q per step | 0.7925 |

g does not depend on n, apart from the last sum, which falls like 1/n. Every size falls at the same rate, and that is the content of the equivalence principle here.

**What the number holds.** Take n uniform over one period of d^B and t ≤ B. Given the word, n = r + d^t j and T^t(n) = (Q r + C)/d^t + Q j, an arithmetic progression of difference Q with d^(B−t) terms. So H(value | word) = (B − t) c exactly. Read as a split: the current value holds the unread address plus a record of the past in its residues mod 3^s, and T^t(n) mod 3^s is fixed by the word alone. That is the repo's 3-adic lock, now as a ledger.

**Places.** The three rates are the Lyapunov exponents at ∞, 2 and 3, and they sum to zero: −0.2075 + 1 − 0.7925 = 0. This is the product formula, so it holds for every map and says nothing about any particular one, as `docs/Conjectures/Proof Attempt - Adelic IFS Bridge.md` already warns.

**Two-branch speeds.** Up is +0.585 and down is −1. Write them as σ − g and −σ − g with σ = ½ log₂ 3. Each step is a null ray around a flow of speed g, and the ingoing ray has the speed of the head, σ + g = c.

## 3. The information radius — Classical, Verified

Define lift as sup_t S_t and

    r_s(M) := −log₂ μ(sup_t S_t ≥ M)

The Cramér root θ > 0 solves (1/d) Σ_r (q_r/d)^θ = 1. Under the tilted digit law p_r = (q_r/d)^θ/d the walk climbs, and the change of measure is exact:

    μ(τ_M < ∞) = 2^(−θM) E~[2^(−θ·overshoot)]

So r_s(M) = θM + ρ₀ + o(1) (Cramér–Lundberg, in the non-lattice case). `lift_tail` samples this identity, and a test checks it against exact first-passage dynamic programming.

| M | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| 2^M μ(lift ≥ M), 3x+1, exact DP | 0.855 | 0.814 | 0.852 | 0.830 | 0.837 | 0.833 |

**θ = 1 is exact** when Σ q_r = d². Then E[T(n)] = n + constant, so n is a martingale up to offsets, Doob's inequality gives μ(lift ≥ M) ≤ 2^(−M), and one bit of height costs one bit of address.

**Integers.** Exhaustive survival curves for every n up to 2²⁶ follow the Haar law with the same constant, about 0.83, far past the exact window. They end near M = B, but that is a statistical edge and not a wall. Over the blocks from 14 to 26 bits, B − max lift runs from 0.88 to 5.24 bits, and larger seeds go past it: n = 319,804,831 has log₂ n = 28.25 and lift 31.04. For the 26-bit block the exact window ends near lift 4.9, because the cheapest climb of M bits takes M/0.1887 steps. Everything beyond that is measured, not guaranteed.

![[figures/survival.png]]

## 4. The derivation in one line

Fuel is B bits and the price is θ bits per bit, so the largest lift among B-bit integers sits near (B − ρ₀)/θ, where r_s(M) = B. The count is a first-moment count over 2^B candidates, so this is a **Heuristic** for integers and not a bound: n = 27 lifts 7.42 bits on 4.75 bits of size. For 3x+1 the resulting constant, peak ≈ n^(1 + 1/θ) = n², is Lagarias–Weiss (1992, Theorem 2.3 in their random model) and Conjecture 4.2 of Kontorovich–Lagarias.

## 5. The weak-field limit — Proved, Verified

Expand ln E[2^(θX)] = 0 in cumulants of the size step X, with mean −g and variance σ²:

    −θ g ln 2 + ½ θ² σ² (ln 2)² + … = 0    so    θ ln 2 → 2 g / σ²

In nats of address per bit of lift this has the form **r_s = 2GM/c²** with G = g and c = σ. More drift raises r_s, more spread lowers it, and more mass raises it.

The c in this formula is the step spread σ, the local speed of §2. It is not the head speed log₂ d. For two branches σ + g = log₂ d, so the two meet only as g → 0, and for other maps they differ even then.

The exact equation is the strong-field theory. For a two-branch walk it depends on the Mach number 𝓜 = g/σ alone. With y = θ σ ln 2:

    𝓜 y = ln cosh y

Then y → 2𝓜 as 𝓜 → 0, and y → ln 2/(1 − 𝓜) as 𝓜 → 1. **Lift is free at Mach 0 and impossible at Mach 1**, where the fastest outgoing step stops. For 3x+1, 𝓜 = 0.2619, y = ½ ln 3, and the cheapest climb moves at half the local speed relative to the flow.

![[figures/mach.png]]

| map | g | θ exact | weak field | error |
|---|---|---|---|---|
| (1,5,5)/3 | 0.037 | 0.0907 | 0.0891 | −2% |
| (1,4,5)/3 | 0.144 | 0.427 | 0.395 | −8% |
| 3x+1 | 0.208 | 1 | 0.953 | −5% |
| (1,4,4)/3 | 0.252 | 1 | 0.817 | −18% |
| (1,6,6,6,6)/5 | 0.254 | 1 | 0.685 | −32% |
| (1,5,5,5)/4 | 0.259 | 1 | 0.738 | −26% |
| (1,2,7)/3 | 0.316 | 0.662 | 0.675 | +2% |
| (1,3,5,7)/4 | 0.321 | 1 | 0.822 | −18% |
| (1,2,5)/3 | 0.478 | 1.652 | 1.524 | −8% |
| (1,4,4,6,6)/5 | 0.488 | 4.056 | 1.548 | −62% |
| (1,2,4)/3 | 0.585 | 3.499 | 2.532 | −28% |
| (1,1,7)/3 | 0.649 | 1 | 1.070 | +7% |

The Gaussian form is close when g is small, and otherwise it depends on the skew of the step law. 3x+1's −5% benefits from a two-point step with zero third cumulant.

## 6. The bridge: horizons have the same exponent — Proved given Goldie, Verified

For Haar-random digits, F(w_k) → b as Q/d^k → 0, where b = A_{w_k}(0). Reversing the digits shows b has the law of the stationary solution x of

    x = (q_r x + a_r) / d    with r uniform

So the random affine recursion carries the law of horizons. It has E[log(q_r/d)] < 0 and E[(q_r/d)^θ] = 1, so Kesten (1973) and Goldie (1991) give a tail μ(F > t) ~ C t^(−θ). When θ = 1, Goldie's constant is closed form:

    C = E[B] / E[A ln A]    with A = q_r/d, B = a_r/d

For 3x+1, A is 1/2 or 3/2 and B is 0 or 1/2, so

    μ(F > t) ~ 1 / (t ln(27/16))    C = 1.91114

E3 solves S(t) = (1/d) Σ S((d t − a_r)/q_r) on a log grid, which tests this with no sampling noise:

| map | θ | local slope at t = 10¹² | t^θ S(t) | Goldie C |
|---|---|---|---|---|
| 3x+1 | 1 | −1.00000 | 1.91113 | 1.91114 |
| (1,4,4)/3 | 1 | −1.00000 | 2.49408 | 2.49409 |
| (1,1,7)/3 | 1 | −0.99981 | 0.80337 | 0.80346 |
| (1,3,5,7)/4 | 1 | −1.00000 | 2.15541 | 2.15541 |
| (1,2,4)/3 | 3.49943 | −3.49944 | 7.09752 | none |
| (1,2,5)/3 | 1.65196 | −1.65196 | 2.58535 | none |
| (1,2,7)/3 | 0.66188 | −0.66188 | 0.82782 | none |
| (1,4,5)/3 | 0.42699 | −0.42699 | 1.49225 | none |

A value-space horizon of M bits therefore costs θM bits of address. At θ = 1 the stationary mean is infinite, because E[T(x)] = x + constant. That is why q = 3 sits on the edge: for q < 3 this mean is finite and for q > 3 the tail is heavier.

Caution: this tail is for long Haar-typical words. The horizon of a *first* contraction word is different: its tail is thin, since a large F there needs a near-critical s with exponentially small measure, and that is why Σ converges.

## 7. Spending the budget — Classical for 3x+1, new form, Verified

A path with digit law p moves at speed v(p) = E_p[log₂ q] − c and costs D(p) = c − H(p) address bits per step. Three extremal paths follow, all with p_r ∝ q_r^η.

| path | condition | 3x+1 |
|---|---|---|
| cheapest climb | minimise D/v, which equals θ | kick share 3/4, speed 0.1887 bits/step |
| longest hover | v = 0, minimise D | kick share log₃ 2, 19.98 steps per bit |
| longest fall | slowest v with D ≤ |v| | kick share 0.609090, 28.89 steps per bit |

The climb speed is Kontorovich–Lagarias's slope (¾) ln 3 − ln 2 = 0.1308 nats per step. The longest fall is their constant: saturation gives 1/(|v| ln 2) = **41.677648**, and they quote 41.677647 with ones-ratio about 0.609091.

The saturation condition D = |v| is the same as

    H(p) = E_p[log₂ q]

the digit entropy equals what the residues can store. It is a Bekenstein-like bound in form. A descent is sustainable only while the word's entropy covers the memory it writes. This is Lagarias–Weiss's fixed-point equation in other words, and it extends to any map.

## 8. The memory is used at full capacity — Proved given Tao, Verified

Take the stationary law on Z/3^m and let H_m be its entropy. Branch 0 is a bijection mod 3^m, and branch 1 sees x only mod 3^(m−1). So the bits one step erases satisfy the exact identity

    H(coin | y mod 3^m) = 1 − (H_m − H_(m−1)) / 2

The left side falls with m, since more conditioning cannot raise entropy, so it has a limit. Tao's fine-scale mixing (2022, Proposition 1.14) bounds Osc(m, n), the L¹ distance between the level-n law and its average over the fibres above level m, by O(m^(−A)) for every n ≥ m. Applying a Fannes-type entropy bound on each fibre gives

    H_n ≥ H_m + (n − m) log₂ 3 (1 − Osc(m, n)/2) − 1

so H_n/n → log₂ 3. The differences H_m − H_(m−1) then average to log₂ 3, and that forces the limit to be

    1 − ½ log₂ 3 = g

So **the bits erased per step, given the value's full 3-adic expansion, equal the drift g exactly.** Tao's Syracuse variable is the same object: conditioning on the last kick gives y = (3x+1)/2^a with a geometric, which is his recursion, and the level-1 law (0, 1/3, 2/3) agrees with the value he quotes.

| m | 1 | 3 | 5 | 7 | 9 | 11 | 13 | limit |
|---|---|---|---|---|---|---|---|---|
| erased bits | 0.5409 | 0.2883 | 0.2522 | 0.2365 | 0.2280 | 0.2227 | 0.2191 | 0.2075 |
| capacity deficit, bits | 0.667 | 1.071 | 1.278 | 1.407 | 1.496 | 1.562 | 1.611 | |

## Related

[[The Schwarzschild Dictionary]] · [[Word Horizons]] · [[Collatz-like Maps in General]] · [[Toy Physics Systems]]
