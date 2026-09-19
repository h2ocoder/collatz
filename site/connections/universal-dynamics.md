# Universal Dynamics

## The Collatz Zoo

What happens when we change the rules? The classical Collatz map uses $3x+1$ for odd numbers and $x/2$ for even. But we can build a whole **zoo** of dynamical systems by varying the multiplier $n$, the divisor $y$, and the additive constant $c$:

$$f(x) = \begin{cases} x/y & \text{if } y \mid x \\ nx + c & \text{otherwise} \end{cases}$$

The classical conjecture is the special case $(n, y, c) = (3, 2, 1)$. Studying the full family shows why 3x+1 is *expected* to converge — and why most of its relatives are expected not to.

<ZooExplorer />

## Thermodynamic Framework

Each system in the zoo has measurable "physics." We treat the orbit as an energy transfer process:

| Quantity | Formula | Physical Analogue |
|----------|---------|-------------------|
| Potential energy | $\log_y(x)$ | Height above ground state |
| Energy input per kick | $\log_y(n)$ | Work done by the $nx+c$ step |
| Energy drain per step | $1$ | Dissipation from the $x/y$ step |
| Fundamental constant | $\log_y(ny)$ | The "speed of light" of the system |
| Criticality $\mu$ | $n / y^{E[v_y]}$ | Subcritical ($\mu < 1$) or supercritical ($\mu > 1$) |

### The Conservation Law

Every system obeys a conservation equation:

$$s \cdot \log_y(ny) = T - \log_y(x_{\text{final}}/x_{\text{initial}}) + \varepsilon$$

where $s$ is the number of kick steps (odd steps), $T$ is the total steps, and $\varepsilon$ captures the residual from the $+c$ corrections.

For classical 3x+1: $s \cdot \log_2(6) = T - \log_2(x_0) + \varepsilon$, with $\varepsilon \in [-0.33, 0]$.

This is the **first law** — energy is conserved up to a small dissipative residual.

### The Critical Threshold

The criticality parameter determines everything:

$$\mu = \frac{n}{y^{E[v_y]}}$$

where $E[v_y]$ is the expected $y$-adic valuation of $nx+c$ for random inputs. For $x/2$ systems, $E[v_2] = 2$ (each bit position is equally likely to end a run of zeros), giving:

$$\mu = \frac{n}{y^2} = \frac{n}{4}$$

The phase transition is at $\mu = 1$, i.e., $n = 4$:

| System | $\mu$ | Behavior in tests |
|--------|-------|----------|
| $3x+1, \; x/2$ | $3/4 = 0.75$ | **every tested orbit reaches 1** |
| $5x+1, \; x/2$ | $5/4 = 1.25$ | 84% divergent |
| $7x+1, \; x/2$ | $7/4 = 1.75$ | 98% divergent |
| $9x+1, \; x/2$ | $9/4 = 2.25$ | 97% divergent |

**3 is the only odd prime less than 4.** So among these systems $3x+1$ is the only nontrivial one whose average drift is downward. That is a classical heuristic, not a proof: an average says nothing certain about every orbit.

## The Three Laws

A thermodynamic analogy, in three "laws":

### First Law: Conservation

$$s \cdot \log_2(6) = T - \log_2(x_0) + \varepsilon$$

Energy input equals energy output plus residual. This holds for **all** $(n, y, c)$ systems — it's a counting identity. The fundamental constant $\log_2(6)$ arises because $6 = 2 \times 3 = y \times n$.

### Second Law: Dissipation

$$\mu = 3/4 < 1$$

The average energy drain exceeds the average energy input. Each kick-drain cycle produces a **net loss of 0.415 bits**. This is the arrow of time — orbits trend downward on average.

For $5x+1$: $\mu = 5/4 > 1$, so the arrow points *upward*, and most orbits appear to grow without bound.

### Third Law: No Perpetual Motion

Even though the average is contraction, individual orbits could in principle avoid the average — staying in "unlucky" residue classes that produce fewer drains per kick. The [finite fuel](/journey/finite-fuel) picture suggests this can't persist: staying unlucky imposes more and more constraints on the bits of the starting number. By computer, the number of such bounces is at most $(B+3)/4$ for every $m \leq 5 \times 10^6$, where $B$ is the bit-length.

This "law" is not proved — it is essentially the Collatz conjecture itself — and it's where the $+1$ in $3x+1$ enters critically. The conservation law doesn't depend on $c$, but the **tightness of modular constraints** does.

## The Role of $c$

Varying $c$ while keeping $n=3, y=2$ reveals a surprise:

| $c$ | $\mu$ | Tested orbits reaching 1 | Cycles found | Notes |
|-----|-------|-------------------|--------|-------|
| 1 | 0.75 | 100% | 0 | Unique attractor |
| 3 | 0.75 | 0% | 2 | $3 \mid c$: trapped |
| 5 | 0.75 | 13% | 21 | Multiple attractors |
| 7 | 0.75 | 69% | 6 | |
| 9 | 0.75 | 0% | 3 | $3 \mid c$: trapped |
| 11 | 0.75 | 19% | 20 | |
| 13 | 0.75 | 51% | 20 | |

**Criticality $\mu$ is identical for all values of $c$** — it depends only on $n$ and $y$. Every system with $n=3, y=2$ is subcritical, and in tests every orbit settles into *some* cycle. But $c$ determines the **ground state landscape**:

- **$c \equiv 0 \pmod{3}$**: The factor of 3 creates an invariant; orbits can never escape multiples of 3. Always cycles.
- **$c$ even**: Breaks the odd/even alternation structure.
- **$c = 1$**: 1 lies on the cycle $1 \to 4 \to 2 \to 1$, and every orbit tested ends there — a **unique vacuum**, a single ground state.

In physics terms: $n$ and $y$ determine the **thermodynamics** (does energy dissipate?). The constant $c$ determines the **ground state degeneracy** (how many stable configurations exist?). Among the systems in this zoo, classical Collatz is the one where both line up in the tests: subcritical dissipation with a single observed ground state.

## Related

- [Eisenstein Lattice](/connections/eisenstein) — orbits as walks on the triangular lattice
- [The Transfer Operator](/connections/hilbert-polya) — the spectrum of a model operator
- [abc Conjecture](/connections/abc-conjecture) — the Collatz map as the minimal-radical case
- [Finite Fuel](/journey/finite-fuel) — a heuristic for why individual orbits might not escape the average
- [Bit Destruction](/proofs/bit-destruction) — the size of each drop in bits
