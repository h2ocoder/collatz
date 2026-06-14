# Collatz as a Quasicrystal

**Question:** Are there physical manifestations of the Collatz dynamics — crystal-like ones? We have called the orbit a "quasicrystal" throughout [[Log-6 Rotation Duality]]; this note makes that *literal* by computing an actual diffraction pattern. Script: `scripts/collatz_quasicrystal_diffraction.py` → `data/collatz_quasicrystal_diffraction.png`.

## The construction is exact, not metaphorical

In base-6 log coordinates every Collatz step is a rigid rotation by $\alpha=\log_6 3$, so the orbit's phases $\theta_k=\{\log_6 x_k\}$ are the sequence $\{k\alpha + W_k\}$. The pure-rotation part $\{k\alpha\}$ is a **cut-and-project set** — the textbook construction of a 1D quasicrystal (project the points of $\mathbb{Z}^2$ lying in a strip of slope $\alpha$ onto a line). The $+1$ "wobble" $W_k$ is a small decoration on top.

So the orbit is not *like* a quasicrystal; in these coordinates it **is** one (plus a perturbation), and we can diffract it.

## The diffractogram

The cut-and-project chain has two tile lengths arranged in the Sturmian word of $\alpha$ (aperiodic but perfectly ordered). Its structure factor $S(q)=\frac1N|\sum_n e^{-iq x_n}|^2$ is **pure point** — sharp Bragg peaks — at $q = 2\pi(h+h'\alpha)/\|\cdot\|$, and the brightest sit exactly at the **continued-fraction convergents** of $\log_6 3$:

$$\frac{h'}{h} = \frac11,\ \frac12,\ \frac23,\ \frac35,\ \frac{8}{13},\ \frac{19}{31},\ \frac{84}{137},\ \dots$$

This is what a real quasicrystal diffraction experiment looks like, and it is the same $13/31/137$ hierarchy that appears as the rotation's near-return periods and the [[Nested Dropping Sets|dropping alphabet]]'s resonant levels. A long real Collatz orbit reproduces the same Bragg peaks in its internal-space spectrum $|\langle e^{2\pi i m\theta}\rangle|^2$ at $m=13,31,44,106,137$.

## The $+1$ is thermal disorder the crystal survives

Treating $W_k$ as phase disorder, the peak intensities are damped by the **Debye–Waller factor** $D(m)=|\langle e^{2\pi i m W_k}\rangle|$ — formally identical to how thermal vibration damps Bragg peaks in a real crystal. Because the wobble is *shot noise* (long plateaus, rare discrete kicks) rather than Gaussian jitter, $D(m)$ stays near 1 far longer than equal-variance Gaussian noise would (the [[Log-6 Rotation Duality|Mössbauer/recoil-free]] analogue). In the diffractogram the orbit's peaks sit essentially on top of the ideal-rotation peaks: **the $+1$ damps but does not melt the crystal.**

## Real physics with the same mathematics

These are *structural* correspondences — the same equations on a different substrate, not a claim that any material computes Collatz. But the substrates are real and measured:

| Collatz object | Measured physics | Shared mathematics |
|---|---|---|
| Rotation $\alpha=\log_6 3$; Bragg peaks at convergents | **Quasicrystals** (Shechtman); Fibonacci photonic/phononic superlattices | cut-and-project / Sturmian order |
| $13\to31\to137$ continued-fraction hierarchy | **Hofstadter butterfly** (moiré graphene, cold atoms) | self-similar gaps indexed by the CF of $\alpha$ |
| Quasiperiodic potential on a lattice | **Aubry–André / Harper model** (bichromatic optical lattices) — metal–insulator transition | $V_n=\cos(2\pi\alpha n)$ |
| Resonance at $r=1$ | **Arnold tongues / devil's staircase** (Josephson junctions, CDWs) | the circle map; Farey structure |
| Wobble coherence $D(m)$ | **Mössbauer / Debye–Waller** | $|\langle e^{imW}\rangle|$, shot noise |
| 2-adic/3-adic dropping tree | **Spin-glass ultrametricity** (Parisi); $p$-adic physics | tree-structured energy landscape |

The two strongest: **quasicrystals** (the cut-and-project identity is exact, and a "$\log_6 3$ superlattice" is buildable with existing Fibonacci-superlattice technology) and the **Hofstadter / Aubry–André** family, where *our* continued fraction literally indexes measured energy gaps and a real localization transition.

## Caveat

No known physical system has the Collatz map as its equations of motion — it is arithmetic/symbolic dynamics, not a Hamiltonian flow. What transfers is the *emergent* structure (quasiperiodicity, Sturmian order, mode-locking, ultrametricity). Same calibration as the earlier honest negative on the string-landscape idea: shared mathematics, yes; physical mechanism, no.

## Related

[[Log-6 Rotation Duality]], [[Nested Dropping Sets]], [[Why 27 Is Long]].
