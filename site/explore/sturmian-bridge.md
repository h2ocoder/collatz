# The Sturmian Bridge — log₂3 as Collatz's Hidden Skeleton

> One mathematical object underlies four different pictures: the cutting sequence of a line, a list of dropping times, a rotation on the unit interval, and a binary word over $\{2, 3\}$. They are all *the same thing*, and they are what makes the Collatz dropping classification work.

This page is the hub that ties the rest of the repo's research together. Every other concept — dropping orbits, dropping classes, the χ_6 L-probe, the Sturmian sign rule, the CF tower of 12-TET / 53-TET characters, the fractals on the [Sturmian Fractals](/explore/sturmian-fractals) page — lives downstream of one fact: **the dropping schedule of the Collatz map is the Sturmian cutting sequence of slope $\log_2 3$.**

Adjust the slope, change the highlighted index, watch how all four views move together. That same lockstep is exactly the structural lockstep that lets Parts 4 through 9 of the [Dropping Zeta Spectrum](https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Dropping%20Zeta%20Spectrum.md) thread work.

## The four views

<SturmianBridge />

::: tip Why each view is "the same thing"
- **A. Cutting line** — the geometric picture. Walk along $y = \alpha x$ through a square grid. The order of crossings (vertical vs horizontal) is the Sturmian word.
- **B. Beatty sequence** — the same data as cumulative crossing positions. Each $k_o$ is the total number of crossings before the $o$-th vertical one. For Collatz that's a dropping time.
- **C. Rotation** — instead of cumulative crossings, just record where the line "is" relative to the next horizontal grid line. That's $\{(o-1)\alpha\} \in [0, 1)$. The cutoff $\tau = 2 - \alpha$ determines whether the next interval contains an extra horizontal crossing.
- **D. Word** — strip away the geometry and just write down the gap pattern as a binary sequence over $\{2, 3\}$. This is the input to the [turtle fractals](/explore/sturmian-fractals).
:::

## Why log₂3 is the right slope for Collatz

The Collatz map is a tug-of-war:

- Each **odd step** does $n \to (3n+1)/2$ — multiplies by $\approx 3/2$.
- Each **even step** does $n \to n/2$ — divides by 2.

If a trajectory has $o$ odd steps and $e$ even steps total, the value is multiplied by roughly $3^o / 2^e$. For it to **drop** below the starting value (which is what defines a dropping time), the divisions must win:

$$2^e > 3^o \quad \Longleftrightarrow \quad e > o \cdot \log_2 3.$$

So $\log_2 3 \approx 1.585$ is the **exchange rate** of the dynamics: every odd step "owes" $\log_2 3$ even steps. Because $e$ is an integer, the minimum legal $e$ for $o$ odd steps is $\lfloor o \log_2 3 \rfloor + 1$. Adding it to $o$ itself gives the $o$-th dropping time:

$$\boxed{k_o = o + \lfloor o \log_2 3 \rfloor + 1.}$$

The gaps $k_o - k_{o-1}$ are exactly $1 + (\lfloor o \log_2 3 \rfloor - \lfloor (o-1) \log_2 3 \rfloor)$, which is **2 or 3** depending on whether the line $y = x \log_2 3$ crossed an extra horizontal grid line between $o-1$ and $o$. That's the Sturmian gap-sequence.

In one sentence: **the irrationality of $\log_2 3$ is *why* the Collatz dropping schedule never repeats periodically, and the structural rigidity of irrational rotation is *why* the schedule has the strong combinatorial properties that the rest of the repo's work exploits.**

## How each view connects to each Collatz concept

### Dropping orbits → the cutting picture

Any individual Collatz orbit $n \to T(n) \to T^2(n) \to \ldots$ runs through *some* sequence of odd and even steps. The number of odd steps until the orbit first drops below $n$ is the orbit's odd-step count $o$. Its stopping time is $k_o$. So every Collatz orbit "lives at" one rung of the Beatty ladder shown in **Panel B** — and the entire set of orbits that share a stopping time is a single rung of that ladder.

### Dropping classes $R_k$ → the Beatty ladder

The **dropping class $R_k$** is the set of residues mod $2^k$ whose Collatz orbits first drop below the starting value at exactly step $k$. By the Affine Orbit Structure, these residues come in families of exactly $2^o$ (where $o$ is the corresponding odd-step count). The dropping classes are nonempty *exactly* for $k$ on the Beatty list $\{3, 6, 8, 11, 13, 16, 19, \ldots\}$ shown in **Panel B**. There is no dropping class for $k = 4, 5, 7, 9, 10, \ldots$ — those gaps in the integer number line are the missing Beatty rungs.

Try focusing $o = 7$: you'll see $k_7 = 19$, and the panel shows there are $|R_{19}| = 3{,}840$ residues mod $2^{19}$ in this class. Every one of those 3,840 numbers traces a Collatz orbit that drops at exactly step 19.

### The sign rule (Parts 4–7) → the rotation threshold

For each dropping class $R_{k_o}$, the χ_6 Hecke L-function partial sum has a **sign** $\epsilon_o \in \{+1, -1\}$. The proved closed form (Part 5) says

$$\epsilon_o = \begin{cases} +1 & \text{if } \{(o-1)\log_2 3\} \ge \tau \\ -1 & \text{if } \{(o-1)\log_2 3\} < \tau \end{cases}$$

where $\tau = 2 - \log_2 3 \approx 0.4150$. That threshold $\tau$ is the orange dashed line in **Panel C**. The rotation point's position relative to $\tau$ is the sign. The sign is the gap value. Every Collatz orbit in $R_{k_o}$ contributes to the same sign because they all share the dropping-class-level data.

### The Sturmian fractal → the gap sequence

**Panel D** is the binary word fed into the turtle program on the [Sturmian Fractals](/explore/sturmian-fractals) page. The same gap-2-or-gap-3 sequence that's encoded in the Beatty ladder *is* what the turtle reads symbol by symbol to draw fractal shapes. The triangular tiling at 120° you see there isn't a coincidence — it's the geometric externalization of the Beatty schedule.

### The CF tower (Part 6) → musical scales as Collatz characters

The continued fraction of $\log_2 3 = [1; 1, 1, 2, 2, 3, 1, 5, 2, 23, \ldots]$ produces convergents:

| Convergent | Decimal | Famous as |
|---|---|---|
| $\frac{3}{2}$ | $1.5000$ | Pythagorean fifth |
| $\frac{8}{5}$ | $1.6000$ | rough cf bound |
| $\frac{19}{12}$ | $1.5833$ | **12-tone equal temperament** |
| $\frac{84}{53}$ | $1.5849$ | **53-tone Holdrian comma** |

The fact that 12-TET and 53-TET both arise as deep convergents of $\log_2 3$ is the same Diophantine fact that organizes the Collatz character tower. Switch the slope above to $19/12$ — you'll see the Sturmian word eventually become periodic (period 12). That's *Cobham's theorem* showing: rational slope ⟹ $q$-automatic sequence ⟹ finite-state structure.

### The Part 8 dichotomy → not everything is Sturmian

The cutting picture predicts the **sign** of the χ_6 sum for each dropping class. It does *not* predict the **magnitude**. [Part 8](https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Dropping%20Zeta%20Spectrum.md) showed that the magnitude's mod-2 reduction — the Stopping-Class parity $P_o \bmod 2$ — is full-entropy Bernoulli, the *opposite* complexity class. So inside the same closed form, one factor is the lowest-complexity infinite binary sequence (the Sturmian sign) and the other is the highest. The bridge picture above is the *sign* side of that dichotomy.

### The qx+1 cousins → universal Sturmian skeleton, varying cycles

Try clicking **5x+1**, **7x+1**, or **9x+1** in the slope presets. The same four-panel picture appears, just at a different slope $\log_2 q$. [Part 10](https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Dropping%20Zeta%20Spectrum.md) verifies empirically:

- **Beatty match holds for every q.** The dropping classes $|R_k^{(q)}|$ are nonzero exactly on the predicted Beatty list $k_o = o + \lfloor o \log_2 q \rfloor + 1$.
- **Sturmian fingerprint holds for every q.** Factor complexity $p(n) = n+1$ for $n = 1, \ldots, 30$ across $q \in \{3, 5, 7, 9\}$.
- **What changes is the Terras identity, not the Sturmian schedule.** For $q = 3$ (Collatz), $\sum |R_k|/2^k \to 1$ (conjecturally). For $q \ge 5$, the sum stops short of 1 — the gap is the 2-adic density of cycle-residues plus divergent orbits.

So the Sturmian skeleton is **universal across $qx+1$ cousins**, and what makes Collatz the conjecturally-hard case is the precise equality $\sum |R_k|/2^k = 1$, not the Sturmian schedule itself. For $5x+1$ there are two well-known cycles (starting at 13 and 17), and that's exactly the kind of cyclical failure the Terras gap measures. The script `scripts/qx_systems_analysis.py` runs all of this and saves `data/qx_systems_analysis.png`.

## In one paragraph

The Collatz tug-of-war between $\times 3$ and $\div 2$ makes $\log_2 3$ the natural exchange rate. Its irrationality makes the dropping schedule a Sturmian cutting sequence. That Sturmian-ness propagates through the affine orbit structure and Eisenstein factorization into the χ_6 sign rule, where it becomes a proved closed form. The rational approximations of $\log_2 3$ (which double as the musical scales 12-TET and 53-TET) index a tower of finer characters yet to be built. The turtle program from the [Sturmian Fractals](/explore/sturmian-fractals) page is the visual rendering of the same gap sequence, and the dichotomy of [Part 8](https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Dropping%20Zeta%20Spectrum.md) is what lies beyond it.

## See also

- [The Sturmian L-Probe](/connections/sturmian-l-probe) — the closed-form theorem in full formality
- [Sturmian Fractals](/explore/sturmian-fractals) — turtle visualizations of the same sequence
- [Affine Orbit Structure](/proofs/affine-orbit) — why each dropping class has size $2^o$
- [Eisenstein Lattice](/connections/eisenstein) — where the χ_6 character comes from
