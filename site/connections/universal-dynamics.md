# The Collatz Zoo

What happens when we change the rules? The classical Collatz map uses $3x+1$ for odd numbers and $x/2$ for even. But we can build a whole **zoo** of dynamical systems by varying the multiplier $n$, the divisor $y$, and the additive constant $c$:

$$f(x) = \begin{cases} x/y & \text{if } y \mid x \\ nx + c & \text{otherwise} \end{cases}$$

The classical conjecture is the special case $(n, y, c) = (3, 2, 1)$. Studying the full family shows why 3x+1 is *expected* to converge — and why most of its relatives are expected not to. Everything on this page is a heuristic, an analogy, or a computation over a stated range. None of it is a proof.

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

$$s \cdot \log_y(ny) = T - \log_y(x_{\text{initial} }/x_{\text{final} }) + \varepsilon$$

where $s$ is the number of kick steps (odd steps), $T$ is the total steps, and $\varepsilon \le 0$ captures the residual from the $+c$ corrections.

For classical 3x+1, on an orbit followed down to 1: $s \cdot \log_2(6) = T - \log_2(x_0) + \varepsilon$, with $\varepsilon \le 0$ always, and $\varepsilon \ge -0.33$ for every start below $10^6$ (computed; the minimum, $-0.326$, is at $x_0 = 993$).

This is the **first law** — energy is conserved up to the residual $\varepsilon$.

### The Critical Threshold

The criticality parameter measures the average drift, and nothing more:

$$\mu = \frac{n}{y^{E[v_y]} }$$

where $E[v_y]$ is the expected $y$-adic valuation of $nx+c$ for random inputs. For $x/2$ systems with $n$ and $c$ odd, $E[v_2] = 2$ (each bit position is equally likely to end a run of zeros), giving:

$$\mu = \frac{n}{y^2} = \frac{n}{4}$$

The average drift changes sign at $\mu = 1$, i.e., $n = 4$:

| System | $\mu$ | Odd starts 3 to 499 (computed) |
|--------|-------|----------|
| $3x+1, \; x/2$ | $3/4 = 0.75$ | **all reach 1** |
| $5x+1, \; x/2$ | $5/4 = 1.25$ | 84% pass $10^{15}$; the rest reach 1 or the cycles through 13 and 17 |
| $7x+1, \; x/2$ | $7/4 = 1.75$ | 98% pass $10^{15}$ |
| $9x+1, \; x/2$ | $9/4 = 2.25$ | 97% pass $10^{15}$ |

Passing $10^{15}$ is not divergence: no orbit of $5x+1$ has been proved to diverge.

**3 is the only odd number between 1 and 4.** So among the $nx+1$, $x/2$ systems with odd $n > 1$, $3x+1$ is the only one whose average drift is downward. That is a classical heuristic, not a proof: an average says nothing certain about every orbit. The explorer above has a blunt example: for $2x+1$, $x/3$ it reports $\mu \approx 0.87$, yet every start that is 2 modulo 3 is never divided at all ($2x+1$ is again 2 modulo 3) and runs off to infinity.

## The Three Laws

A thermodynamic analogy, in three "laws":

### First Law: Conservation

$$s \cdot \log_2(6) = T - \log_2(x_0) + \varepsilon$$

Energy input equals energy output plus residual. This holds for **all** $(n, y, c)$ systems — it's a counting identity. The fundamental constant $\log_2(6)$ arises because $6 = 2 \times 3 = y \times n$.

### Second Law: Dissipation

$$\mu = 3/4 < 1$$

The average energy drain exceeds the average energy input. On average, a kick-drain cycle loses **0.415 bits**. This is the arrow of time — orbits trend downward on average.

For $5x+1$: $\mu = 5/4 > 1$, so the arrow points *upward*, and most orbits appear to grow without bound.

### Third "Law" (conjectural): No Perpetual Motion

Even though the average is contraction, individual orbits could in principle avoid the average — staying in "unlucky" residue classes that produce fewer drains per kick. The [finite fuel](/journey/finite-fuel) picture is a heuristic for why this might not persist: staying unlucky imposes more and more constraints on the bits of the starting number.

This "law" is not proved — it is essentially the Collatz conjecture itself — and it's where the $+1$ in $3x+1$ enters critically. The average drift doesn't depend on which odd $c$ is used, but which cycles exist does, as the next section shows.

## The Role of $c$

Varying $c$ while keeping $n=3, y=2$ reveals a surprise:

| $c$ | $\mu$ | Starts that pass through 1 | Distinct cycles reached | Notes |
|-----|-------|-------------------|--------|-------|
| 1 | 0.75 | 100% | 1 | Only $1 \to 4 \to 2 \to 1$ seen |
| 3 | 0.75 | 0% | 1 | $3 \mid c$: the $3x+1$ map on multiples of 3 |
| 5 | 0.75 | 13% | 6 | Several cycles |
| 7 | 0.75 | 69% | 2 | 1 is not on a cycle: $1 \to 10 \to 5 \to 22 \to \dots \to 5$ |
| 9 | 0.75 | 0% | 1 | $3 \mid c$: the $3x+1$ map on multiples of 9 |
| 11 | 0.75 | 19% | 3 | |
| 13 | 0.75 | 47% | 10 | |

(Computed for the odd starts from 3 to 499; every one ended in a cycle.)

**Criticality $\mu$ is identical for all odd values of $c$** — it depends only on $n$ and $y$. Every such system with $n=3, y=2$ is subcritical, and for every odd $c$ from 1 to 19 every odd start from 3 to 999 settles into *some* cycle (computed). But $c$ determines the **ground state landscape**:

- **$c \equiv 0 \pmod{3}$**: after its first odd step an orbit stays among multiples of 3 for good ($3x + c$ is then a multiple of 3, and halving keeps the factor), so it never comes back to 1. Every orbit tested ends in a cycle. For $c = 3$ the map on multiples of 3, and for $c = 9$ the map on multiples of 9, is the $3x+1$ map in disguise, so "always cycles" there is the Collatz conjecture again.
- **$c$ even**: $3x + c$ is odd whenever $x$ is, so an odd number is never halved again and its orbit grows forever.
- **$c = 1$**: 1 lies on the cycle $1 \to 4 \to 2 \to 1$, and every orbit tested ends there — a single observed ground state.

In physics terms: $n$ and $y$ determine the **thermodynamics** (does energy dissipate on average?). The constant $c$ determines the **ground state degeneracy** (how many stable configurations exist?). Among the systems tabulated here, classical Collatz and its two disguises ($c = 3$ and $c = 9$) are the ones with a single observed cycle; only for $c = 1$ does that cycle pass through 1.

## Related

- [Eisenstein Lattice](/connections/eisenstein) — orbits as walks on the triangular lattice
- [The Transfer Operator](/connections/hilbert-polya) — the spectrum of the map cut off at a modulus
- [abc Conjecture](/connections/abc-conjecture) — how close powers of 2 and 3 can be
- [Finite Fuel](/journey/finite-fuel) — a heuristic for why individual orbits might not escape the average
- [Bit Destruction](/proofs/bit-destruction) — the size of each drop in bits
