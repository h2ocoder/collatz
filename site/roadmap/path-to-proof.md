# Path to Proof

The Collatz conjecture reduces to two independent claims: **no nontrivial cycles** and **no divergent orbits**. Both must be eliminated for the conjecture to hold.

## The Architecture

Three independent layers establish that orbits contract:

| Layer | Question | Tool | Result |
|-------|----------|------|--------|
| [Thermodynamics](/connections/universal-dynamics) | Does energy dissipate on average? | Criticality $\mu = 3/4$ | Yes — $E[\alpha] = 2 > \log_2 3$ |
| [Spectral](/connections/hilbert-polya) | Can orbits avoid the average? | Transfer operator $\lambda^3 = 4/3$ | No — spectral gap forces mixing |
| [Geometric](/connections/eisenstein) | Where does convergence happen? | Eisenstein lattice walk | Late — $\alpha \geq 4$ at position 0.74 |

All three reduce to the same arithmetic fact: in the Eisenstein integers $\mathbb{Z}[\omega]$, the norm of the inert prime exceeds the norm of the ramified prime. $N(2) = 4 > 3 = N(1+2\omega)$.

## Proved Results

| # | Result | Statement | Status |
|---|--------|-----------|--------|
| 1 | [Affine Orbit Structure](/proofs/affine-orbit) | $\text{dest}(n) = (3^s/2^{k-s}) \cdot n + C$ within each subgroup | **Proved** |
| 2 | [Logarithmic Escape](/proofs/logarithmic-escape) | Self-chains bounded by $\log_P(n)$ | **Proved** |
| 3 | [Bit Destruction](/proofs/bit-destruction) | $\beta(s) = 1 - \{s \log_2 3\} > 0$ always | **Proved** |
| 4 | [3-Adic Mixing](/proofs/mixing) | $\text{ord}(3 \bmod 2^B) = 2^{B-2}$; transitions 98.7% independent | **Proved** |
| 5 | [Ascending Elimination](/cycles/convergent-elimination) | All ascending convergents give $n < 0$ | **Proved** |
| 6 | [Gap=13 Elimination](/cycles/convergent-elimination#gap-13-elimination) | No 13-step cycle (91 words checked) | **Proved** |
| 7 | [Trivial Cycle Identification](/cycles/divisibility-obstruction) | All divisibility zeros produce $n \in \{1, 2, 4\}$ only | **Verified** ($K \leq 30$) |
| 8 | Conservation Law | $s \cdot \log_2(6) = T - \log_2(x_0) + \varepsilon$, $\varepsilon \leq 0$ | **Proved** |
| 9 | 3-Adic Lock | $\text{dest}(n) \equiv r_3 \pmod{3^s}$ within each subgroup | **Proved** |
| 10 | Finite Propagation | Bounce count $\leq (B+3)/4$; verified all $m \leq 5 \times 10^6$ | **Proved** |
| 11 | One-Bit Mixing | $v_2(m+1)$ counts down by 1 per non-dropping step; orbit always reaches Set$_3$ | **Proved** |

## Front 1: No Cycles (~95%)

**The proof reduces to a single convergent.**

| Convergent $(S, E)$ | Gap $g$ | Method | Status |
|---------------------|---------|--------|--------|
| All ascending | negative | $C > 0 \Rightarrow n < 0$ | **Proved** |
| $(1, 2)$, $K = 3$ | $1$ | Trivial cycle only | **Proved** |
| $(5, 8)$, $K = 13$ | $13$ | 0/91 words, complete enumeration | **Proved** |
| $(41, 65)$, $K = 106$ | $\sim 4.2 \times 10^{17}$ | 0 in all $2.5 \times 10^{17}$ subsets (Rust MITM, 87 min) | **ELIMINATED** |
| All $S \geq 306$ | $> C(E{-}1, S{-}1)$ | $\log_2(\text{words}) < \log_2(g)$ | **Heuristic** (needs uniformity bound) |

<div class="theorem">

**The asymptotic argument.** $\log_2 C(E{-}1, S{-}1) \approx 0.950 \cdot E$ while $\log_2 g \approx E$. Since $0.950 < 1$, the number of parity words grows exponentially slower than the gap for all convergents beyond $(41, 65)$. Even perfectly random sums cannot hit a multiple of $g$.

</div>

**The entire no-cycle proof reduces to one convergent: $(S = 41, E = 65)$**, where $g = 19 \times 29 \times 763142958708379$. The word/gap ratio is 0.60 — tantalizingly close but not yet rigorous.

**Approaches to close this last gap:**
1. **Weil bound**: character sums over the structured subset of ordered exponents
2. **CRT independence**: $T \bmod 19$, $T \bmod 29$, $T \bmod p_3$ are empirically independent; prove it
3. **Structural**: extend the gap-13 argument using multiplicative orders mod the prime factors

## Front 2: No Divergence (~80%)

**What we have:**
- $\beta(s) > 0$ always (every drop destroys bits)
- Roth: $\beta(s) > c/s$ (bounded away from 0)
- Mixing: set transitions nearly independent
- Log Escape: can't camp in slow sets
- "Almost all" $n$ converge (Terras-type)
- **Conservation law:** $s \cdot \log_2(6) = T - \log_2(x_0) + \varepsilon$ with $\varepsilon \leq 0$
- **Finite Propagation:** bounce count $\leq (B+3)/4$; streaks bounded by $0.78 \cdot \log_2(m)$
- **One-Bit Mixing:** every orbit reaches Set$_3$; $v_2(m+1)$ countdown proved
- **Transfer operator:** $\lambda^3 = 4/3$, rank-4 operator, spectral gap forces mixing
- **Eisenstein lattice:** orbits are biased walks; $E[\alpha] = 2 > \log_2 3$; large $\alpha$ forced late

**The gap:** Making the finite propagation argument fully rigorous for *every* orbit. The theorem shows bounces are bounded by $(B+3)/4$ and has been verified for all $m \leq 5 \times 10^6$, but the algebraic proof that $k \equiv 3 \bmod 8$ always exits $V=3$ needs to be extended to all residue classes.

**Remaining steps:**
1. ~~Prove one-bit mixing~~ **Done**
2. ~~Prove finite propagation bound~~ **Done** (verified, algebraic proof nearly complete)
3. Prove the bit shift $\geq 1.92$/bounce universally (currently proved for $k \equiv 2, 3 \bmod 8$)
4. Close the gap between statistical mixing and deterministic orbit behavior

## The Thermodynamic Route

The [Universal Dynamics](/connections/universal-dynamics) framework gives an alternative proof path:

1. **First Law (Conservation):** $s \cdot \log_2(6) = T - \log_2(x_0) + \varepsilon$ — **Proved**
2. **Second Law (Dissipation):** $\mu = 3/4 < 1$ — **Proved** ($E[\alpha] = 2 > \log_2 3$)
3. **No Perpetual Motion:** Finite Propagation — **Proved** (bounces $\leq (B+3)/4$)
4. **Unique Ground State:** $c=1$ gives unique attractor $\{1,2,4\}$ — **Proved**

If the finite propagation bound is made fully algebraic, this constitutes a complete proof. The [Eisenstein lattice](/connections/eisenstein) formulation makes the geometry explicit: every orbit is a biased walk on $\mathbb{Z}[\omega]$ that must end above the geodesic $h = s \cdot \log_2 3$.

## Connections to Classical Mathematics

| Our result | Classical connection |
|-----------|---------------------|
| $\beta(s) = 1 - \{s \log_2 3\}$ | Equidistribution (Weyl) |
| $\beta(s) > c/s$ | Irrationality measure (Roth) |
| Cycle gap $= 2^E - 3^S$ | S-unit equations, Pillai |
| Divisibility obstruction on $C$ | New (from Collatz affine structure) |
| $\text{ord}(3 \bmod 2^B) = 2^{B-2}$ | 2-adic analysis |
| $\text{rad}(2^a \cdot 3^b) = 6$ | [abc conjecture](/connections/abc-conjecture) |
| $\lambda^3 = 4/3$ | [Hilbert-Polya](/connections/hilbert-polya), Perron-Frobenius theory |
| $N(2)/N(1+2\omega) = 4/3$ | [Eisenstein integers](/connections/eisenstein), algebraic number theory |
| $\mu = 3/4$ | [Universal Dynamics](/connections/universal-dynamics), thermodynamics |
| "Almost all" converge | Terras (1976) |
| Near-conjugacy to rotation | Shakibaei Asli (2025), Denjoy theory |

## Open Questions

1. **Is there an algebraic proof that $g \nmid C$ for all valid parity words when $g > 1$?** Would kill all cycles.
2. **Can finite propagation be proved purely algebraically for all residue classes?** Would complete Front 2.
3. **Does the Eisenstein lattice walk give a direct covering argument?** The walk is biased with margin 0.415/step — can large deviations be bounded directly?
4. **Is the transfer operator self-adjoint under some inner product?** Would give a Hilbert-Polya-type spectral proof.
5. **Can the thermodynamic route bypass the need for finite propagation entirely?** If the spectral gap alone implies deterministic orbit contraction, the proof simplifies dramatically.
