# The +1 Perturbation

**Status:** Open — this is the core remaining obstacle for Front 2

## The Observation

The Collatz map 3n+1 decomposes into two fundamentally different operations:

1. **×3** — purely multiplicative, stays within the 2-3 adic scaffold
2. **+1** — additive perturbation that completely destroys the prime factorization

Since gcd(n, 3n+1) = 1 always, the +1 replaces every prime factor of n with an entirely new set. The only surviving structure is the 2-adic valuation v₂(3n+1), which lives in the scaffold.

## The Scaffold

The 2-adic and 3-adic structure forms a rigid scaffold:
- **2-adic**: n mod 2^(k-s) determines dropping set membership (period, subgroup)
- **3-adic**: dest(n) mod 3^s is locked to a single residue per subgroup
- **Combined**: modulus 2^(k-2s) · 6^s (the base-6 lattice)

This scaffold is proved ([[Affine Orbit Structure]], [[3-adic lock]]). Within it:
- The slope 3^s/2^(k-s) is universal per Set_k (proved)
- The spectral gap → 5/6, Cheeger h ≥ 0.44 (verified)
- No absorbing subsets exist on the lattice (verified up to 1.5M points)

## The Question

**Does the +1 perturbation, acting within the 2-3 scaffold, guarantee that every orbit eventually drops?**

Equivalently: does the complete reshuffling of non-{2,3} prime factors at each odd step prevent any orbit from being permanently "non-dropping"?

## Why This Is Hard

The +1 is the *interaction between additive and multiplicative structure*. This touches:

- **The abc conjecture**: 3n + 1 = c with rad(3n · (3n+1)) involving all primes. The Collatz case has rad = 6 on the scaffold (minimal radical), making it the hardest case of abc.
- **The Erdős–Kac theorem**: the prime factorization of 3n+1 is "effectively random" — but "effectively" hides the difficulty.
- **Schinzel's hypothesis / Bunyakovsky conjecture**: predicting prime factors of n+1 from n is a central open problem.

## Physical Analogy

The +1 acts like a **perturbation that breaks integrability**:

| Physics | Collatz |
|---------|---------|
| Integrable system | Pure multiplicative map 3n/2^k |
| Perturbation | The +1 in 3n+1 |
| KAM tori | Periodic 2-adic patterns (cycles) |
| Torus destruction | Front 1: no non-trivial cycles |
| Ergodicity after destruction | Front 2: mixing / spectral gap |
| Dissipation | β(s) > 0 at every drop |

In KAM theory: if a perturbation destroys ALL invariant tori, the system is ergodic.
We proved the +1 destroys all tori (= no cycles, Front 1).
The remaining claim: this implies ergodicity (= mixing, Front 2).

## The Hilbert Curve Connection

On a Hilbert curve, the 2-adic scaffold creates self-similar spatial patterns. The +1 perturbation creates non-local jumps (53% cross half the grid). The Hilbert curve is a "map" of the scaffold, and every prime has a specific location within it.

The "almost symmetries" visible on the Hilbert curve are the quasi-periodic structure of the dropping classes (governed by the three-distance theorem for log₂3). The +1 breaks these symmetries just enough to prevent trapping, but preserves enough structure for the scaffold to constrain the dynamics.

## Possible Proof Routes

1. **KAM-to-ergodic bridge**: Prove that the destruction of all cycles (Front 1) implies mixing (Front 2). In smooth dynamics, this follows from the Oxtoby-Ulam theorem. Need a discrete analogue.

2. **Relative compactness**: Prove the +1 perturbation is "relatively compact" in the sense of Kato-Birman scattering theory. This would give completeness of the "wave operators" — every orbit reaches an asymptotic state.

3. **Entropy production**: The +1 destroys all prime factors (= maximizes entropy of the factorization). Combined with the scaffold's dissipation (β > 0), entropy production should drive convergence.

4. **Direct scaffold argument**: Use the fact that the 2-3 scaffold covers all odd residues (verified) and the +1 ensures the orbit can't stay in any uncovered gap. The three-distance theorem bounds the gap sizes.

## Related

- [[Affine Orbit Structure]] — the scaffold
- [[Spectral Mixing Theorem]] — the mixing evidence  
- [[Bit Destruction Bound]] — the dissipation
- [[Logarithmic Escape Theorem]] — can't camp in slow sets
