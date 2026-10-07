# The Dropping Dictionary

A [dropping set](../foundations/definitions) collects every integer whose orbit first falls below its start after the same number of steps. The sets themselves are disjoint, but their destinations *overlap*, and you can run them **backwards** — from a destination value, reconstruct the numbers that drop onto it. This page is about the rules for doing that. They turn out to be a single dictionary, read in two opposite directions; and no finite machine translates between the two directions, for a reason that goes back to a 1969 theorem about bases 2 and 3. The objects here are classical, nothing is claimed as new, and none of it bears on the conjecture: the last section says why.

This is the companion to [The Wobble](./log6-wobble): that page dissected the $+1$ perturbation on a *single* orbit; this one is about the *combinatorics* of one dropping round and how the $\times 2$ and $\times 3$ structures interlock.

## One round is an affine map

By the [Affine Orbit Structure](../proofs/affine-orbit) theorem, the integers sharing one parity word over a dropping round of length $k$ form a class on which the destination map is **exactly affine**. Each class is pinned by a triple $(k, s, C)$, with $s$ its number of odd steps, and carries

$$\mathrm{dest}(n) = \frac{3^s\, n + C}{2^{\,k-s} }, \qquad C \in \mathbb{Z}\ \text{the integer } +1 \text{ accumulation.}$$

The collection of these triples is the **dictionary**. The whole story is that it is one table read two ways.

![The dictionary read two ways: forward by a 2-adic key, backward by a 3-adic key; the thinning 3-adic reach of destinations; the backward predecessor tree of 2](/data/collatz_nested_dropping.png)

**Forward** you key on $n \bmod 2^k$: the low bits pick the word, the word gives the destination. Pure 2-adic.

**Backward** you key on $d \bmod 3^s$: a destination $d$ has a candidate predecessor in class $(k,s,C)$ **iff** $2^{\,k-s} d \equiv C \pmod{3^s}$, and then the candidate is *unique*:

$$n = \frac{2^{\,k-s}\, d - C}{3^s}.$$

The candidate follows the class's parity word, and it is a true predecessor exactly when it is larger than $d$. At $d = 1$ the class $(3,1,1)$ offers $n = 1$, which is not; any other failure would be a counterexample to Terras's coefficient stopping time conjecture (see the [definitions](../foundations/definitions)), and there is none with $n \le 10^7$ (computed).

So "build a dropping set from its destination" is a literal lookup keyed by $d \bmod 3^s$. The same table — 2-adic key going forward, 3-adic key going backward. That asymmetry is concrete: the forward map reads $n$ modulo a power of 2, its inverse reads $d$ modulo a power of 3. Keying predecessors modulo $3^s$ is standard (Lagarias 1985; Wirsching 1998).

The **thinning** is the 3-adic part. Each class maps its whole $2^k$-residue class onto a *single* residue mod $3^s$ of the destination line, so as $s$ climbs, the destinations a depth-$s$ drop can reach are pinned into an exponentially thinner sliver — $\tfrac13, \tfrac19, \tfrac{2}{27}, \tfrac{3}{81}, \tfrac{7}{243}, \dots$ of the residues. The levels do not nest (level 1 reaches $d \equiv 1 \pmod 3$, level 2 reaches $d \equiv 2 \pmod 9$); their reaches thin out, and they **overlap** in the sense that one value (e.g. $d = 10 \leftarrow 11, 13, 15, 20$) is reached from several levels at once.

## The alphabet is a ballot language

Strip a letter to its parity word. Apart from the one-letter word `E` (the even numbers, level $s = 0$), a word is admissible **iff** it (1) starts with `O`, (2) has **no two adjacent `O`s** — because $3n+1$ is always even, every odd step forces a following halving — and (3) is **ballot-admissible**: $3^o > 2^e$ at every interior step, with the first drop $3^o < 2^e$ only at the end. The *only* arithmetic input is the comparison $3^o \gtrless 2^e$; no prime is privileged. Arithmetic (the 2) and multiplicity (the 3) are two readings of one lattice path.

The number of letters with $s$ odd steps, for $s = 0, 1, 2, \dots$, is

$$w_s = 1,\,1,\,1,\,2,\,3,\,7,\,12,\,30,\,85,\,173,\,476,\,961,\,2652,\,8045,\dots$$

— from $s = 1$ on this is [**OEIS A100982**](https://oeis.org/A100982), which begins $1, 1, 2, 3, 7, 12$: the *admissible Collatz sequences* of the stopping-time literature (Wagon 1985, Terras, Chamberland, Winkler, Roosendaal). The extra leading 1 is $w_0$, the word `E`. The object we reached by working backwards is classical, and so is the backward reading of it (Lagarias 1985; Wirsching 1998). Its growth rate, which follows from the binomial bounds of Winkler (arXiv:2609.22303, 2026), is the binomial entropy

$$\lambda = \frac{\beta^\beta}{(\beta-1)^{\beta-1} }, \qquad \beta = \log_2 3, \qquad \lambda \approx 2.8395.$$

![Alphabet growth at rate lambda; the two readings — 2-adic mass converging to 1 versus 3-adic mass to 1.69; the predecessor-multiplicity histogram](/data/collatz_dropping_alphabet.png)

Now the asymmetry can be put in numbers. Each letter of level $s$ carries its two keys at the **same scale**, because the number of halvings in it is $e_s = \lfloor s\log_2 3\rfloor + 1$, which puts $2^{e_s}$ in $(3^s,\, 2\cdot 3^s]$:

| reading | key | total mass | meaning |
|---|---|---:|---|
| **Forward** (2-adic) | $n \bmod 2^{e_s}$ | $\sum_s w_s/2^{e_s} = \mathbf{1}$ | the classes are disjoint and fill $\mathbb{Z}_2$ up to a set of measure zero (Terras 1976; the partial sum to $s = 200$ is 0.99999997). An integer has at most one dropping word; that every integer above 1 drops at all is equivalent to the Collatz conjecture |
| **Backward** (3-adic) | $d \bmod 3^s$ | $\sum_s w_s/3^s = \mathbf{1.690}$ (computed) | **overlap** — the map is *multivalued*; a destination has on average $1.69$ one-round predecessors (1.690 over $2 \le d \lt 10^6$, computed) |

The same alphabet, at the same resolution, tiles $\mathbb{Z}_2$ (up to a null set) under the 2-adic reading and covers $\mathbb{Z}_3$ 1.69 times over, on average, under the 3-adic reading. Forward, each $n$ has at most one image: disjoint preimages, total mass 1 by Terras's theorem. Backward, a $d$ has one source or several (exactly one when 3 divides $d$): overlapping images, mass 1.69. The excess $1.69 - 1 = 0.69$ over the trivial halving $n = 2d$ **is** the overlap of dropping orbits, quantified. (The predecessor histogram in the figure counts only letters of at most 22 steps, for $2 \le d \lt 3000$, and has mean 1.63; with every letter the mean over that range is 1.689, computed.) Per level the reach is $w_s$ of the $3^s$ residues (all distinct for $s \le 12$, computed), a share that shrinks roughly like $(\lambda/3)^s \approx 0.947^s$, while the classes of the 2-adic reading leave out only a null set.

## One continued fraction runs both sides

A letter is built from two blocks: $A = \texttt{OE}$ (altitude step $\log_2 3 - 1 \approx +0.585$) and $B = \texttt{E}$ (step $-1$). Climbing one level adds one $A$-block and **either 0 or 1** $B$-block, and that 0/1 schedule — the increments $e_{s+1} - e_s \in \{1,2\}$ — is *exactly the Beatty / Sturmian word of $\log_2 3$*:

$$e_{s+1} - e_s = 2,1,2,1,2,2,1,2,1,2,2,1,\dots \qquad (s = 1, 2, 3, \dots)$$

![The block schedule equals the Beatty word of log2 3; the shared continued fraction with the rotation, whose convergent denominators are 13, 31, 137](/data/collatz_alphabet_rotation.png)

And $\log_2 3$ is the same irrational that drives the [log-6 rotation](../journey/the-rotation): with $\alpha = \log_6 3 = \log_2 3/(1 + \log_2 3)$, the two share a continued-fraction tail, so the convergent denominators of $\alpha$,

$$1,1,2,3,5,\ \mathbf{13},\ \mathbf{31},\ 106,\ \mathbf{137},\ 791,\dots$$

are the rotation's near-return periods — the $13/31/137$ [parastichy arms](./log6-wobble), with 44 the $27/44$ semiconvergent. From 2 on, each is a sum $p + q$ over a convergent $p/q$ of $\log_2 3$: $13 = 8 + 5$, $31 = 19 + 12$, $137 = 84 + 53$. The denominators $q = 5, 12, 41, 53, \dots$ are the levels of the alphabet at which $s\log_2 3$ is nearest an integer, and a letter of level $q$ is $p + q$ or $p + q + 1$ steps long. The combinatorial alphabet and the harmonic rotation are **two faces of one number**.

## No finite machine: Cobham's theorem

If that forward-to-backward correspondence were a single finite-state machine reading $n$ in base 2 and writing $d$ in base 3, we would have an explicit device converting arithmetic into multiplicity. It does not exist, and the reason turns out to have little to do with Collatz.

![The forward letter-machine is infinite-state; emitting d in base 3 requires reading n in both bases](/data/collatz_dropping_transducer.png)

**The forward machine is infinite-state.** Reading $n$ LSB-first, the $j$-th parity is $\texttt{bit} \oplus \texttt{carry}$ — but the carry is the low-bit trajectory itself, an unbounded register: to go on writing parities, a machine must remember where $j$ steps of the shortcut map ($(3x+1)/2$ or $x/2$) have taken the bits read so far. The script counts $10, 28, 88, 295, 1024, 3626$ such values at depths $j = 4, 6, \dots, 14$ (computed), and the count cannot stay bounded, since $2^j - 1$ alone goes to $3^j - 1$. No finite automaton writes the parity sequence, of which the letter is the opening stretch.

**Emitting $d$ in base 3 entangles both bases of $n$.** Exactly, by one line of algebra ($2^{e_s} d = 3^s n + C$), and checked on 60,000 random odd $n$ below $10^7$:

$$d \bmod 3^M \ \text{is determined by}\ \big(\,\text{letter}(n),\ n \bmod 3^{M-s}\,\big).$$

The letter needs $e_s$ **base-2** digits of $n$; the remaining $M-s$ ternary digits of $d$ need $n \bmod 3^{M-s}$, i.e. **base-3** digits of $n$. The letter alone leaves $d \bmod 3^M$ spread over up to $3^{M-s}$ values. So $d$'s ternary expansion has a **seam at digit $s$**: the low $s$ digits — the dictionary key — come from reading $n$ in base 2; every digit above comes from reading $n$ in base 3.

A finite base-2→base-3 transducer cannot exist, for a reason that has nothing to do with the seam. On even numbers the dropping map is $n \mapsto n/2$, so such a machine would convert binary to ternary. Fed the powers of 2, a regular set of binary strings, it would have to produce a regular set of ternary strings (a finite transducer sends regular sets to regular sets): the expansions of the powers of 2. But by **Cobham's theorem** (1969) a set of integers recognisable by finite automata in two multiplicatively independent bases is ultimately periodic, and the powers of 2 are not. The same argument rules out a finite machine for the identity map: the obstruction is about bases 2 and 3, not about Collatz.

The dictionary works because it only ever matches the **key**: the low $s$ ternary digits, which the base-2 letter does determine. Push past the key and you must read $n$ modulo powers of 3.

## What it means

**The letter, read from the low binary digits of $n$, fixes the low $s$ ternary digits of $d$ and nothing above them; and no finite machine converts between the two bases at all.** The layers of this page, in order:

- the dictionary is finite *per letter*, never globally;
- the alphabet tiles $\mathbb{Z}_2$ up to a null set (Terras) but covers $\mathbb{Z}_3$ with overlaps;
- its length schedule is the Beatty word of $\log_2 3$;
- and no finite machine joins the two readings, by a theorem about bases 2 and 3 that does not involve Collatz.

None of this bears on the conjecture. The alphabet, the two masses, the seam and the Cobham obstruction are the same for $3x-1$ (its classes are the negatives of these), a map with cycles of its own, so nothing here can tell the two maps apart.

## Where this lives in the repo

- Research note: [Nested Dropping Sets](https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Nested%20Dropping%20Sets.md) (working notes)
- Scripts: `scripts/collatz_nested_dropping.py`, `collatz_dropping_alphabet.py`, `collatz_alphabet_rotation.py`, `collatz_dropping_transducer.py`
- Foundations: [Affine Orbit Structure](../proofs/affine-orbit), [The Hidden Rotation](../journey/the-rotation)
