---
tags: [schwarzschild, toy-models, analog-gravity, landauer]
status: analogy
created: 2026-11-02
jira: SCRUM-65
---

# Toy Physics Systems

Which physical toy models does a Collatz-like map actually resemble? Each entry says what matches exactly and what does not. All of this is **Analogy** unless a line says otherwise.

## 1. The two-dimensional dilaton black hole — the best fit

The string-inspired 1+1 dimensional black hole (Witten 1991, Mandal–Sengupta–Wadia 1991, Callan–Giddings–Harvey–Strominger 1992) has metric function

    f(r) = 1 − 2m e^(−Q r)

Put r = log₂ n. The value of Q is then a choice of units: Q = ln 2 per bit makes e^(Qr) = n, so f = 1 − 2m/n, and with F = 2m this is the lapse of a word, 1 − F/n ([[Word Horizons]] §1).

The factor alone cannot choose between 2D and 4D, since with r = n it is the 4D 1 − r_s/r. The null ray does choose. A word is exactly the time-1 map of

    dr/dt = −β f(r)    with r = log₂ n

([[Word Horizons]] §2). That is the ingoing ray dr/dt = −c f(r) only in the logarithmic coordinate. With r = n the speed would have to grow with n. So **a word is one ingoing null ray of the 2D geometry, with c = β bits per word**, and it stalls at the horizon.

Treat the integer itself as the object, with mass B = log₂ n, and the scaling laws side with 2D, not 4D:

| quantity | 4D Schwarzschild | 2D dilaton | integer of B bits |
|---|---|---|---|
| entropy | ∝ M² | ∝ M | B bits, ∝ M |
| temperature | ∝ 1/M | constant | drain law independent of n |
| lifetime | ∝ M³ | ∝ M | B/g steps, ∝ M |
| specific heat | negative | infinite | no analogue |

The density of states fits too. There are 2^B integers of B bits, so S(E) = E ln 2, a Hagedorn spectrum with T = 1/ln 2.

**Limits.** That table uses a third meaning of mass and compares scalings only. In the 2D theory the mass sets the horizon position, r_h = (1/Q) ln 2m, while an integer's B is not the horizon of any word. Hawking temperature needs a Euclidean continuation that has no counterpart here, and T = 1/ln 2 is the convention that a state of E bits has probability 2^(−E). The values do not match either: at Q = ln 2 the dilaton's T = Q/4π is 0.055, about 26 times smaller than 1.44. Only the independence from M carries over. There is no gravity, no field and no back-reaction.

## 2. An acoustic horizon

Unruh (1981) showed that sound in a moving fluid sees a black hole where the flow turns supersonic. The river model (Hamilton–Lisle 2008) writes the Schwarzschild geometry in the same language.

A two-branch walk has exactly this structure. Each step is a null ray of a flow:

    up = σ − g,    down = −σ − g

with sound speed σ = ½ log₂ q and flow speed g = 1 − ½ log₂ q, so the Mach number is 𝓜 = g/σ.

| regime | condition | map |
|---|---|---|
| supersonic, 𝓜 > 1 | q < 2 | everything falls, with a sonic point at a/(2 − q) |
| subsonic inward, 0 < 𝓜 < 1 | 2 < q < 4 | 3x+1, 𝓜 = 0.262 |
| still, 𝓜 = 0 | q = 4 | no integer map |
| outward, 𝓜 < 0 | q > 4 | 5x+1, a white hole by flow direction |

For q < d the sonic point is literal: `trapping_radius` is where the fastest upward ray stops, and it is a theorem. The flow speed also depends on position through the offset. For 3x+1 the mean step vanishes at n = 1, the stagnation point a/(4 − q), which is the horizon of the typical word 10 and the trivial cycle.

**Limits.** The walk has no persistence, so the Lorentz-like structure of a telegraph process is missing. There is no fluid. 3x+1 itself never goes supersonic, so it has no sonic horizon at any n.

## 3. A sedimenting atmosphere

Collatz dynamics are first order with drift and noise, which is overdamped sedimentation, the system behind Perrin's 1909 measurement. The exact law

    μ(height ≥ h) ≈ L 2^(−θ h)

is the barometric formula, with scale height 1/θ. Its Gaussian form, exp(−2 g h/σ²), is the Einstein relation between drift and diffusion. Integers obey it (L ≈ 0.83) up to a ceiling at h ≈ B set by the size of the sample. This is the most honest of the toys, because it is what the map statistically is.

**Limits.** There is no equilibrium with a floor unless the floor is the attractor, and the ceiling is a sampling effect.

## 4. The reversible tape: Landauer, Bennett and a Page-shaped curve

T is many-to-one, but `emit` and `absorb` show that n → (T^t(n), word) is one-to-one (**Proved**, tested on nine maps). "Bits destroyed" means bits moved to a tape, as in Bennett's reversible computation (1973), and only discarding the tape costs Landauer's price.

Take n uniform over one period of d^B. Then the word has min(t, B) c bits and the pair has B c bits, so

    I(value; word) = H(value) + min(t, B) c − B c

is exact. It rises until t = B, because the word is learning fresh address, and then falls, because the value is losing size while the word learns nothing new. The kink is pigeonhole. Past t = B the word is a function of its first B symbols, though it still looks random: that is the regime where no probabilistic argument has a hold.

Exact entropies, 3x+1 (E5):

| B | peak step | peak I (bits) | peak I / B | mean slope of H before | after |
|---|---|---|---|---|---|
| 12 | 12 | 10.08 | 0.840 | −0.160 | −0.157 |
| 16 | 16 | 13.41 | 0.838 | −0.162 | −0.170 |
| 20 | 20 | 16.72 | 0.836 | −0.164 | −0.177 |
| 24 | 24 | 20.01 | 0.834 | −0.166 | −0.182 |

![[figures/page_curve.png]]

The ledger's leading order is peak I/B = 0.7925 with slopes −g = −0.2075. **The measurements have not converged at B = 24.** Both move toward those values slowly. The upper bound H ≤ E[log₂ value] + O(log B) is rigorous for t ≤ B, and the O(√B) spread of log-size is the likely reason for the gap, but I have no matching lower bound for integers. The clean statement of the same rate is the 3-adic limit in [[Information Radius]] §8, which is proved.

**Limits.** This is classical mutual information. A real Page curve is about entanglement entropy of a pure state, and the Page time is a fraction near half the evaporation time. Here the ratio is g/c = 0.2075.

## 5. Not used

- **Cellular automata.** Multiplying by 2 or 3 is a local rule in base 6, so a true lattice speed of light exists there (Cloney–Goles–Vichniac 1987, Kari 2012). It measures a different thing from the head speed. A note for later.
- **Bekenstein-style bounds.** H(p) = E_p[log₂ q] ([[Information Radius]] §7) has the form of an entropy bound, but there is no area in it.
- **Rindler space.** The uniform field suggests it, but the local temperature in Rindler space varies with position, and here it does not.

## Related

[[The Schwarzschild Dictionary]] · [[Word Horizons]] · [[Information Radius]] · [[Audit]]
