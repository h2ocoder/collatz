# The Dropping Dictionary

A [dropping set](../foundations/definitions) collects every integer whose orbit first falls below its start after the same number of steps. These sets *overlap*, and you can run them **backwards** — from a destination value, reconstruct the numbers that drop onto it. This page is about the rules for doing that. They turn out to be a single finite dictionary, read in two opposite directions, and the gap between the two directions is exactly the boundary between arithmetic and multiplicity — closed, in the end, by a 1969 theorem.

This is the companion to [The Wobble](./log6-wobble): that page dissected the $+1$ perturbation on a *single* orbit; this one is about the *combinatorics* of one dropping round and how the $\times 2$ and $\times 3$ structures interlock.

## One round is an affine map

By the [Affine Orbit Structure](../proofs/affine-orbit) theorem, the integers sharing one parity word over a dropping round of length $k$ form a class on which the destination map is **exactly affine**. Within a populated dropping set the odd-step count $s$ is constant, so each class is pinned by a triple $(k, s, C)$ and carries

$$\mathrm{dest}(n) = \frac{3^s\, n + C}{2^{\,k-s}}, \qquad C \in \mathbb{Z}\ \text{the integer } +1 \text{ accumulation.}$$

The collection of these triples is the **dictionary**. The whole story is that it is one table read two ways.

![The dictionary read two ways: forward by a 2-adic key, backward by a 3-adic key; the 3-adic nesting of destination reach; the backward predecessor tree of 2](/data/collatz_nested_dropping.png)

**Forward** you key on $n \bmod 2^k$: the low bits pick the word, the word gives the destination. Pure 2-adic.

**Backward** you key on $d \bmod 3^s$: a destination $d$ has a predecessor in class $(k,s,C)$ **iff** $2^{\,k-s} d \equiv C \pmod{3^s}$, and then it is *unique*:

$$n = \frac{2^{\,k-s}\, d - C}{3^s}.$$

So "build a dropping set from its destination" is a literal lookup keyed by $d \bmod 3^s$. The same table — 2-adic key going forward, 3-adic key going backward. That asymmetry is the [2-adic / 3-adic complementarity](../connections/) made concrete: the forward map reads the additive 2-adic structure, its inverse reads the additive 3-adic structure.

The **nesting** is the 3-adic part. Each class maps its whole $2^k$-residue class onto a *single* residue mod $3^s$ of the destination line, so as $s$ climbs, the destinations a depth-$s$ drop can reach are pinned into an exponentially thinner sliver — $\tfrac13, \tfrac19, \tfrac{2}{27}, \tfrac{3}{81}, \tfrac{7}{243}, \dots$ of the residues. The dropping sets nest 3-adically by destination reach, and **overlap** because one value (e.g. $d = 10 \leftarrow 11, 13, 15, 20$) is reached from several levels at once.

## The alphabet is a ballot language

Strip a letter to its parity word. It is admissible **iff** it (1) starts with `O`, (2) has **no two adjacent `O`s** — because $3n+1$ is always even, every odd step forces a following halving — and (3) is **ballot-admissible**: $3^o > 2^e$ at every interior step, with the first drop $3^o < 2^e$ only at the end. The *only* arithmetic input is the comparison $3^o \gtrless 2^e$; no prime is privileged. Arithmetic (the 2) and multiplicity (the 3) are two readings of one lattice path.

The number of letters with $s$ odd steps is

$$w_s = 1,\,1,\,1,\,2,\,3,\,7,\,12,\,30,\,85,\,173,\,476,\,961,\,2652,\,8045,\dots$$

— exactly [**OEIS A100982**](https://oeis.org/A100982), the *admissible Collatz sequences* of the stopping-time literature (Wagon 1985, Terras, Chamberland, Winkler, Roosendaal). The object we reached by working backwards is classical; what is new is reading it through the forward/backward lens. Its growth rate is the binomial entropy

$$\lambda = \frac{\beta^\beta}{(\beta-1)^{\beta-1}}, \qquad \beta = \log_2 3, \qquad \lambda \approx 2.8395.$$

![Alphabet growth at rate lambda; the two readings — 2-adic mass converging to 1 versus 3-adic mass to 1.69; the predecessor-multiplicity histogram](/data/collatz_dropping_alphabet.png)

Now the asymmetry sharpens into two exact identities. Each letter of level $s$ carries its two keys at the **same scale**, because $e_s = \lceil s\log_2 3\rceil$ forces $2^{e_s} \in [3^s,\, 2\cdot 3^s)$:

| reading | key | total mass | meaning |
|---|---|---:|---|
| **Forward** (2-adic) | $n \bmod 2^{e_s}$ | $\sum_s w_s/2^{e_s} = \mathbf{1.000000}$ | **partition** of $\mathbb{Z}_2$ — the map is a *function*; every integer has exactly one dropping word |
| **Backward** (3-adic) | $d \bmod 3^s$ | $\sum_s w_s/3^s = \mathbf{1.690}$ | **overlap** — the map is *multivalued*; a destination has $\approx 1.69$ one-round predecessors |

The same alphabet, at the same resolution, is a **partition** under the 2-adic reading and a **1.69-fold overlap** under the 3-adic reading. Forward, each $n$ has one image — disjoint preimages, mass exactly 1. Backward, each $d$ has many sources — overlapping images, mass 1.69. The excess $1.69 - 1 = 0.69$ over the trivial halving $n = 2d$ **is** the overlap of dropping orbits, quantified; it is the mean of the predecessor histogram. Per level the 3-adic reach is a Cantor dust of dimension $\log_3 \lambda \approx 0.95$, while the 2-adic reading is full (dimension 1).

## One continued fraction runs both sides

A letter is built from two blocks: $A = \texttt{OE}$ (altitude step $\log_2 3 - 1 \approx +0.585$) and $B = \texttt{E}$ (step $-1$). Climbing one level adds one $A$-block and **either 0 or 1** $B$-block, and that 0/1 schedule — the increments $e_{s+1} - e_s \in \{1,2\}$ — is *exactly the Beatty / Sturmian word of $\log_2 3$*:

$$e_{s+1} - e_s = 2,1,2,1,2,2,1,2,1,2,2,1,\dots$$

![The block schedule equals the Beatty word of log2 3; the shared continued fraction with the rotation, whose convergent denominators are 13, 31, 137](/data/collatz_alphabet_rotation.png)

And $\log_2 3$ is the same irrational that drives the [log-6 rotation](../journey/the-rotation): with $\alpha = \log_6 3 = \log_2 3/(1 + \log_2 3)$, the two share a continued-fraction tail, so the convergent denominators of $\alpha$,

$$1,1,2,3,5,\ \mathbf{13},\ \mathbf{31},\ 106,\ \mathbf{137},\ 791,\dots$$

are simultaneously the rotation's near-return periods — the $13/31/137$ [parastichy arms](./log6-wobble), with 44 the $27/44$ semiconvergent — *and* the resonant levels of the alphabet, where $s\log_2 3$ is nearest an integer and the letters are tightest. The combinatorial alphabet and the harmonic rotation are **two faces of one number**.

## The wall is Cobham's theorem

If that forward-to-backward correspondence were a single finite-state machine reading $n$ in base 2 and writing $d$ in base 3, we would have an explicit device converting arithmetic into multiplicity. It does not exist — for a precise reason.

![The forward letter-machine is infinite-state; emitting d in base 3 requires reading n in both bases — the Cobham obstruction](/data/collatz_dropping_transducer.png)

**The forward letter-machine is infinite-state.** Reading $n$ LSB-first, the $j$-th parity is $\texttt{bit} \oplus \texttt{carry}$ — but the carry is the low-bit trajectory itself, an unbounded register. The Myhill–Nerode classes grow $10, 28, 88, 295, 1024, 3626, \dots$ without bound. No finite automaton assigns the letter.

**Emitting $d$ in base 3 entangles both bases of $n$.** Exactly, and verified with zero violations:

$$d \bmod 3^M \ \text{is determined by}\ \big(\,\text{letter}(n),\ n \bmod 3^{M-s}\,\big).$$

The letter needs $e_s$ **base-2** digits of $n$; the remaining $M-s$ ternary digits of $d$ need $n \bmod 3^{M-s}$, i.e. **base-3** digits of $n$. The letter alone leaves $d \bmod 3^M$ spread over up to $3^{M-s}$ values. So $d$'s ternary expansion has a **seam at digit $s$**: the low $s$ digits — the dictionary key — come from reading $n$ in base 2; every digit above comes from reading $n$ in base 3.

A finite base-2→base-3 transducer cannot straddle that seam. It would make the dropping relation automatic in two multiplicatively independent bases, and by **Cobham's theorem** (1969) the only such relations are ultimately periodic. The dropping map — infinitely many affine pieces with a non-periodic Beatty schedule — is not. Hence no finite machine.

The dictionary survives because it only ever matches the **key**: the low $s$ ternary digits, which the base-2 letter does determine — a finite correspondence at exactly the granularity Cobham permits. Push past the key and you must read $n$ in the other base.

## What it means

**Arithmetic (base 2) and multiplicity (base 3) meet precisely at the letter, and by Cobham nowhere further.** Every layer of this page is the same statement at a different magnification:

- the dictionary is finite *per letter*, never globally;
- the alphabet partitions $\mathbb{Z}_2$ but only overlaps $\mathbb{Z}_3$;
- its growth schedule is the Beatty word of the rotation constant;
- and the obstruction to unifying the two readings is a named theorem about bases 2 and 3.

It is the same wall that [The Wobble](./log6-wobble) met as the irrationality of $\log_6 3$ and that [The Countdown](../journey/the-countdown) meets as the $\varepsilon$ in the conservation law — here it wears its 2-adic / 3-adic face, and that face has a name.

## Where this lives in the repo

- Research note: [Nested Dropping Sets](https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Nested%20Dropping%20Sets.md)
- Scripts: `scripts/collatz_nested_dropping.py`, `collatz_dropping_alphabet.py`, `collatz_alphabet_rotation.py`, `collatz_dropping_transducer.py`
- Foundations: [Affine Orbit Structure](../proofs/affine-orbit), [The Hidden Rotation](../journey/the-rotation)
