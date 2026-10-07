# The Sturmian Bridge — log₂3 as Collatz's Hidden Skeleton

> One mathematical object underlies four different pictures: the cutting sequence of a line, a list of dropping times, a rotation on the unit interval, and a binary word over $\{2, 3\}$. They are all *the same thing*, and they are what makes the Collatz dropping classification work.

This page is the hub that ties the rest of the repo's research together. Every other concept — dropping orbits, dropping classes, the χ_6 L-probe, the Sturmian sign rule, the conjectured tower of characters at the 12-TET / 53-TET denominators, the fractals on the [Sturmian Fractals](/explore/sturmian-fractals) page — lives downstream of one fact: **the dropping times that the residue classes allow, $k_o = o + \lfloor o \log_2 3 \rfloor + 1$, are spaced by the Sturmian cutting sequence of slope $\log_2 3$.** It is a statement about which dropping times the classes allow. That no integer above 1 drops at any other time would follow from Terras's coefficient stopping time conjecture, which is open (no exception to it among $2 \le n \le 2.8 \times 10^{19}$: Rozier and Terracol, 2026). The map $3x-1$ has the same schedule and every $qx+1$ has one of the same kind, so it says nothing about whether every orbit drops.

Adjust the slope, change the highlighted index, watch how all four views move together. That same lockstep is what Parts 4 through 9 of the [Dropping Zeta Spectrum](https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Dropping%20Zeta%20Spectrum.md) working notes rely on. (They are working notes: for how firmly each result is established, go by this site.)

## The four views

<SturmianBridge />

::: tip Why each view is "the same thing"
- **A. Cutting line** — the geometric picture. Walk along $y = \alpha x$ through a square grid. The order of crossings (vertical vs horizontal) is the Sturmian word.
- **B. Beatty sequence** — the same data as cumulative crossing positions. Each $k_o$ is one more than the number of crossings up to and including the $o$-th vertical one ($o$ vertical and $\lfloor o\alpha \rfloor$ horizontal). For Collatz that's an allowed dropping time.
- **C. Rotation** — instead of cumulative crossings, just record where the line "is" relative to the next horizontal grid line. That's $\{(o-1)\alpha\} \in [0, 1)$. The cutoff $\tau = 2 - \alpha$ determines whether the next interval contains an extra horizontal crossing.
- **D. Word** — strip away the geometry and just write down the gap pattern as a binary sequence over $\{2, 3\}$. This is the input to the [turtle fractals](/explore/sturmian-fractals).
:::

## Why log₂3 is the right slope for Collatz

The Collatz map is a tug-of-war:

- Each **odd step** does $n \to 3n+1$ — multiplies by $\approx 3$.
- Each **even step** does $n \to n/2$ — divides by 2.

If a trajectory has $o$ odd steps and $e$ even steps total, the value is multiplied by roughly $3^o / 2^e$. For it to **drop** below the starting value (which is what defines a dropping time), the divisions must win:

$$2^e > 3^o \quad \Longleftrightarrow \quad e > o \cdot \log_2 3.$$

So $\log_2 3 \approx 1.585$ is the **exchange rate** of the dynamics: every odd step "owes" $\log_2 3$ even steps. Because $e$ is an integer, the minimum legal $e$ for $o$ odd steps is $\lfloor o \log_2 3 \rfloor + 1$. Adding it to $o$ itself gives the $o$-th allowed dropping time:

$$\boxed{k_o = o + \lfloor o \log_2 3 \rfloor + 1.}$$

The gaps $k_o - k_{o-1}$ are exactly $1 + (\lfloor o \log_2 3 \rfloor - \lfloor (o-1) \log_2 3 \rfloor)$, which is **2 or 3** depending on whether the line $y = x \log_2 3$ crossed an extra horizontal grid line between $o-1$ and $o$. That's the Sturmian gap-sequence.

In one sentence: **the irrationality of $\log_2 3$ is *why* the Collatz dropping schedule never repeats periodically, and the structural rigidity of irrational rotation is *why* the schedule has the strong combinatorial properties that the rest of the repo's work exploits.**

## How each view connects to each Collatz concept

### Dropping orbits → the cutting picture

Any individual Collatz orbit $n \to T(n) \to T^2(n) \to \ldots$ runs through *some* sequence of odd and even steps. The number of odd steps until the orbit first drops below $n$ is the orbit's odd-step count $o$. A drop with $o$ odd steps needs at least $\lfloor o \log_2 3 \rfloor + 1$ halvings, so the stopping time is at least $k_o$, and it equals $k_o$ for all but finitely many members of each residue class on the ladder (Terras 1976). That it equals $k_o$ for every $n > 1$ would follow from his coefficient stopping time conjecture, which is open; no exception exists among $2 \le n \le 10^7$ (computed). So, as far as anyone knows, every Collatz orbit that drops "lives at" one rung of the Beatty ladder shown in **Panel B**, and the orbits that share a stopping time share a rung.

### Dropping classes $R_k$ → the Beatty ladder

The **dropping class $R_k$** is the set of residues mod $2^k$ whose Collatz orbits first drop below the starting value at exactly step $k$. By the Affine Orbit Structure, these residues come in families of exactly $2^o$ (where $o$ is the corresponding odd-step count). The dropping classes are nonempty *exactly* for $k$ on the Beatty list $\{3, 6, 8, 11, 13, 16, 19, \ldots\}$ shown in **Panel B** (OEIS A122437; the numbers of residue families in the classes are OEIS A100982). There is no dropping class for $k = 4, 5, 7, 9, 10, \ldots$ — those gaps in the integer number line are the missing Beatty rungs.

Try focusing $o = 7$: you'll see $k_7 = 19$, and the panel shows there are $|R_{19}| = 3{,}840$ residues mod $2^{19}$ in this class. Every one of those 3,840 numbers traces a Collatz orbit that drops at exactly step 19.

### The sign rule (Parts 4–7) → the rotation threshold

For each dropping class $R_{k_o}$ with $o \ne 3$, the χ_6 character sum over the class, taken over whole periods, has a **sign** $\epsilon_o \in \{+1, -1\}$ (at $o = 3$ the sum is exactly 0). No L-function is involved: the sum is a count of destinations by residue modulo 3. The closed form (Part 5 of the working notes; outlined on [the L-probe page](/connections/sturmian-l-probe)) says

$$\epsilon_o = \begin{cases} +1 & \text{if } \{(o-1)\log_2 3\} \ge \tau \\ -1 & \text{if } \{(o-1)\log_2 3\} < \tau \end{cases}$$

where $\tau = 2 - \log_2 3 \approx 0.4150$. That threshold $\tau$ is the orange dashed line in **Panel C**. The rotation point's position relative to $\tau$ is the sign. The sign is the gap value. It is a property of the class total, not of each orbit in it.

### The Sturmian fractal → the gap sequence

**Panel D** is the binary word fed into the turtle program on the [Sturmian Fractals](/explore/sturmian-fractals) page. The same gap-2-or-gap-3 sequence that's encoded in the Beatty ladder *is* what the turtle reads symbol by symbol to draw fractal shapes. The triangular grid you see there at 120° comes from the angle (any word drawn with 120° turns stays on a triangular lattice); what the Beatty schedule decides is which edges are drawn.

### The continued fraction of log₂3 (Part 6) → musical scales

The continued fraction of $\log_2 3 = [1; 1, 1, 2, 2, 3, 1, 5, 2, 23, \ldots]$ produces convergents:

| Convergent | Decimal | Famous as |
|---|---|---|
| $\frac{3}{2}$ | $1.5000$ | Pythagorean fifth |
| $\frac{8}{5}$ | $1.6000$ | rough cf bound |
| $\frac{19}{12}$ | $1.5833$ | **12-tone equal temperament** |
| $\frac{84}{53}$ | $1.5849$ | **53-tone Holdrian comma** |

That 12-TET and 53-TET come from convergents of $\log_2 3$ is classical: twelve fifths nearly make seven octaves, and fifty-three nearly make thirty-one. Part 6 guesses that the same denominators index a family of finer characters; none has been built. Switch the slope above to $19/12$ and the word repeats with period 12: for a rational slope $p/q$ the gaps repeat every $q$ steps, by arithmetic alone. A periodic word is finite-state; the word of $\log_2 3$ never repeats.

### The Part 8 dichotomy → not everything is Sturmian

The cutting picture predicts the **sign** of the χ_6 sum for each dropping class. It does *not* predict the **magnitude**. [Part 8](https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Dropping%20Zeta%20Spectrum.md) of the working notes computed the first 20,000 terms of the magnitude's mod-2 reduction, the Stopping-Class parity $P_o \bmod 2$ (the counts $P_o$ are OEIS A100982). Every binary block of length up to 11 occurs, as it would for coin flips, though the share of 1s is 0.476, about seven standard errors from the 1/2 of a fair coin. So inside the same closed form the sign is a Sturmian word, the lowest-complexity aperiodic sequence there is, and the magnitude's parity looks, as far as computed, close to random. Nothing is proved about the parity sequence. The bridge picture above is the *sign* side of that dichotomy.

### The qx+1 cousins → the same Sturmian skeleton, a different Terras sum

Try clicking **5x+1**, **7x+1**, or **9x+1** in the slope presets. The same four-panel picture appears, just at a different slope $\log_2 q$. [Part 10](https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Dropping%20Zeta%20Spectrum.md) of the working notes checks this by computation:

- **Beatty match for each q tested.** For $q \in \{3, 5, 7, 9\}$ the dropping classes $|R_k^{(q)}|$ are nonzero exactly on the Beatty list $k_o = o + \lfloor o \log_2 q \rfloor + 1$ (computed for $k$ up to 29, 18, 17 and 15). The reason is the same for every odd $q$: a drop needs $2^e > q^o$.
- **Sturmian fingerprint for every q.** The gap word has factor complexity $p(n) = n+1$, as the word of any irrational slope must (Morse and Hedlund); checked for $n = 1, \ldots, 30$ with $q \in \{3, 5, 7, 9\}$.
- **What changes is the Terras sum, not the Sturmian schedule.** For $q = 3$, $\sum |R_k|/2^k = 1$: this is Terras's theorem (1976) that almost every integer has a finite stopping time. For $q = 5, 7, 9$ the sum stops short of 1 (computed: about 0.824, 0.699 and 0.614): a positive share of the residue classes never meets the dropping condition.

So the Sturmian skeleton is shared by all the $qx+1$ cousins, and by $3x-1$ as well: it cannot tell these maps apart, and it says nothing about whether every orbit falls. The Terras sum does separate $3x+1$ from $5x+1$, but it is a statement about almost all integers, while the conjecture is about every one of them: $3x-1$ also has sum 1, and has cycles through 5 and 17. Nor do the two known nontrivial cycles of $5x+1$ (through 13 and 17) account for its shortfall: a cycle is finitely many integers and weighs nothing in such a sum. Of the integers below $2^{16}$, 17.5% had not dropped below their start after 2000 steps of $5x+1$ (computed), and only two of those, 13 and 17, lie on the cycles; whether any of the rest grows without bound has not been proved for a single orbit. The script `scripts/qx_systems_analysis.py` runs the Part 10 computations and saves `data/qx_systems_analysis.png`.

## In one paragraph

The Collatz tug-of-war between $\times 3$ and $\div 2$ makes $\log_2 3$ the natural exchange rate. Its irrationality makes the schedule of allowed dropping times a Sturmian cutting sequence. That Sturmian-ness propagates through the affine orbit structure and Eisenstein factorization into the χ_6 sign rule, where it becomes an explicit closed form (supported by computation; its proof is so far an outline). The rational approximations of $\log_2 3$ (which double as the musical scales 12-TET and 53-TET) may index a tower of finer characters; none has been built. The turtle program from the [Sturmian Fractals](/explore/sturmian-fractals) page is the visual rendering of the same gap sequence, and the dichotomy of [Part 8](https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Dropping%20Zeta%20Spectrum.md) of the working notes is what lies beyond it.

## See also

- [The Sturmian L-Probe](/connections/sturmian-l-probe) — the closed form, with an outline of the argument
- [Sturmian Fractals](/explore/sturmian-fractals) — turtle visualizations of the same sequence
- [Affine Orbit Structure](/proofs/affine-orbit) — why the residues of a dropping class come in families of $2^o$
- [Eisenstein Lattice](/connections/eisenstein) — where the χ_6 character comes from
