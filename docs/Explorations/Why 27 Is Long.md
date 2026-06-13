# Why 27 Is Long

**Question:** $27$ takes $111$ Collatz steps and climbs to $9232$ — famously long for so small a number. Is there a shortcut to its length, or a way to guess it? And is the long orbit a fact about $27 = 3^3$ (its factorisation / $3$-adic form), or something else?

**Answer:** It is a **2-adic accident of $27$'s binary expansion**, not a fact about $3^3$. The forward Collatz map is blind to factorisation; $27$ is simply the *smallest* integer whose low bits encode a record-long climb. Script: `scripts/collatz_27_anatomy.py` → `data/collatz_27_anatomy.png`.

## The anatomy: one long letter

$27$'s orbit is **86% a single ascending dropping round**. Its [dropping time](Nested%20Dropping%20Sets.md) is $96$: it climbs for $96$ steps to the peak $9232 = 2^{13.17}$ before first falling below itself (to $23$), then finishes in $15$ steps. Decomposed into the [dropping dictionary](Nested%20Dropping%20Sets.md)'s letter chain,

$$\sigma(27) = \underbrace{96}_{27\to23} + 8 + 1 + 1 + 3 + 1 + 1 = 111,$$

the first letter dwarfs the rest. So "why is $27$ long?" is "why does $27$ sit in a $96$-step climbing letter?"

And the sharp fact: **$27$ is the smallest integer with dropping time $\ge 96$.** Its $96$-step word is itself a record-length climbing word, and $27$ is the least number whose binary digits realise it. The "big UPs" are a sustained run of odd values $x \equiv 3 \pmod 4$ — each gives $v_2(3x+1)=1$, so $x \mapsto (3x+1)/2 \approx 1.5x$, a climb. $57\%$ of $27$'s odd values are $\equiv 3 \pmod 4$.

## It is *not* the factorisation or the 3-adics

The forward map's move-sequence is a **function of $n$'s binary digits only**: every $n \equiv 27 \pmod{32}$ ($59, 91, 155, \dots$) shares $27$'s opening moves. The dynamics never read $n$'s factorisation. Concretely:

- **Powers of $3$ are not special.** Over $3^3,\dots,3^{33}$, the length z-score against same-size random odds averages $\mathbf{-0.10 \pm 0.18}$ — indistinguishable from generic. $3^4=81$, $3^6=729$, $3^9=19683$ are all *below* average. Being $3^k$ predicts nothing.
- **$27$ itself is only a $\sim\!2\sigma$ outlier** among numbers its size: the local mean of $\sigma$ near $27$ is $\approx 35$ with standard deviation $\approx 36$ — the variance is as large as the mean. $111$ is $z=+2.1$. Notable, not extraordinary.

So $27$'s fame is a *size illusion*: we expect a number as small as $27$ to be short, but $\sigma$ has enormous spread even at small $n$. $27$ is the smallest number to break $100$ steps and the first to visibly climb into the thousands — a dramatic record jump (the previous record, $25$, took $23$ steps).

This is the [forward dynamics = 2-adic](Nested%20Dropping%20Sets.md) principle in miniature: the trajectory (length, climb, peak) lives entirely on $\mathbb{Z}_2$; the multiplicative/$3$-adic structure that makes $27 = 3^3$ "feel" special is exactly the structure the forward map cannot see. (It is the *backward* map — reconstructing predecessors — that is $3$-adic; see [[Nested Dropping Sets]].)

## Shortcuts and statistical guesses

- **Exact shortcut.** $\sigma(n) = \mathrm{drop}(n) + \sigma(\mathrm{dest}(n))$ with $\mathrm{dest}(n) < n$: the letter-chain recursion, memoised, computes all lengths bottom-up. Block/residue acceleration (jump $2^B$ steps via a table keyed on $n \bmod 2^B$) is the same idea at the bit level. No closed form is known or expected.
- **Statistical guess.** $\sigma(n) \approx c\,\log_2 n$ on average ($c \approx 7$–$8$ empirically near these sizes), but with variance comparable to the mean, so any point estimate is weak. The *excess* over the mean tracks the orbit's expansion: $\sigma(n) - \overline{\sigma} \approx 15.5\,\log_2(\mathrm{peak}/n)$. For $27$ the expansion is $\log_2(9232/27) = 8.4$ bits — a big climb for a small number — which is the whole story. But the peak is not knowable without (essentially) running the orbit: the length is computationally irreducible.

## The takeaway

$27$ is the canonical lesson that **Collatz length is a 2-adic quantity**. It is long because its binary expansion happens to encode a record-length climbing word, lifting it to $9232$; $27 = 3^3$ is a coincidence the dynamics never use. The famous numbers (records, "feeders" like $54, 73, 97$ that drop straight into $27$'s basin) are organised entirely by the $2$-adic letter structure of [[Nested Dropping Sets]], not by arithmetic of their factors.

## Related

[[Nested Dropping Sets]], [[Log-6 Rotation Duality]], [[Affine Orbit Structure]].
