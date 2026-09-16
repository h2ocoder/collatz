---
tags: [collatz, machine-learning, transformers, prior-work, survey]
status: draft
created: 2026-09-16
---

# Neural Networks and Collatz — Prior Work

Part 2 of the [[00 Index]] investigation: what has already been done at the intersection of
neural networks and the Collatz map, plus the computability/circuit-complexity background
that constrains what "a network that runs Collatz" can mean. Companions:
[[Ternary LLMs - State of the Art]], [[Research Directions - Ternary Nets x Collatz]],
[[Ternary Syracuse Circuit]].

Repo-internal prior art (different vault, referenced by path): `docs/Explorations/Collatz
Embeddings.md` (eight versions of Collatz-as-embedding experiments) and
`docs/Explorations/Machine Learning.md` (the originating idea).

## 1. The central paper: transformers learning the Collatz sequence

**Charton & Narayanan, *Transformers know more than they can tell — Learning the Collatz
sequence*, arXiv:2511.10811 (Nov 2025)** [1]. This is the most relevant piece of prior work
in existence, and it is unusually well matched to this repo's framework.

**Task.** They do *not* train on a single Collatz step. They define the **long Collatz step**
κ: odd → odd. Write the compressed map c ↦ (3c+1)/2 for odd c and c ↦ c/2 for even c. For odd
n, let k = number of trailing 1-bits of n (so n = 2^k·m − 1), apply k up-steps, then k′
down-steps until odd again:

$$\kappa(n) = \frac{(3/2)^k (n+1) - 1}{2^{k'}}$$

So κ is "one Syracuse-style excursion", with **two loops of input-dependent length**. That is
the whole point: the arithmetic is easy, the *control flow* is hard.

**Setup.** Sequence-to-sequence transformer (4-layer bidirectional encoder, dim 512, 8 heads;
1-layer decoder), integers written as digit sequences in base B, one model per base for all
B = 2…57, ~300M training pairs with n odd and uniform in [1, 10¹²], test set 100k pairs.

**Results by base** (Table 1 of [1]):

| Accuracy | Bases |
|---|---|
| 99.5%+ | 24, 16, 32, 36, 12, 48, 8 |
| 95–99% | 6, 20, 28, 2, 52, 10, 44, 54 |
| 88–89% | 26, 46, 33 |
| 70–71% | 49, 47, 21, 27, 51, 39, 31, 41, 23, 7, 25 |
| 55–56% | 13, 37, 19, 55, 29, 53, 35, 5 |
| 25–37% | 11 (37%), 3 (25%) |

All even bases reach ≥88%; most odd bases stay below 80%. Base 3 is the *worst* base tested.

**What the models actually learn.** Accuracy jumps in discrete steps, and the *same* step
levels (25, 37, 55, 71, 81, 88, 92, 99.7%) appear for every base. Models in different bases
succeed and fail on the *same inputs* (base-15 and base-17 models agree on 98% of a test
sample). The explanation: for p large enough, each residue class mod 2^p is either predicted
with >95% accuracy or <1%. The classes are learned in a fixed order, identified by binary
suffix:

`…001₂`, then `…1011₂`, `…1101₂`, then `…00111₂`, `…10011₂`, …

Their Theorem 2 shows why: k and k′ can be read off the binary representation of n by matching
its suffix against the sequences H_l built from the parities of 2^{-p}(3^l − 1) mod 3^l
(H₁ = 10, H₂ = 111000, H₃ = 111101101000010010). Each learned class is exactly one pair
(k, k′), and the classes are learned in increasing order of k + k′. Corollary 3: over odd n,
P(k = a) = 2^{-a}, P(k′ = b | k = a) = 2^{-b}, and k ⟂ k′.

**Failure modes** (the "know more than they can tell" part). Hallucination essentially never
occurs. In over 90% of failures the model performs the *correct* computation but uses the
wrong loop length: in odd bases ~70% of errors have p/t exactly equal to a small power of two
(k′ under-estimated to the largest value the model has learned); in even bases most errors are
"near power-of-two errors" p = 2^l κ(n) + ε with small odd ε. So the models know more than
their accuracy suggests — they have the arithmetic, they lack the control structure.

### Why this matters for *this* repo

The map κ is **exactly the repo's affine orbit law**, in Charton's notation. Within a fixed
(k, k′) class,

$$\kappa(n) = \frac{3^k}{2^{k+k'}}\,n + \frac{3^k - 2^k}{2^{k+k'}}$$

which is `dest(n) = (3^s / 2^(k−s))·n + C` with s = k up-steps and k + k′ total halvings.
Verified numerically here for all odd n < 20000: zero violations, and the classes land on the
residues the repo would predict — (k,k′) = (1,1) ⇒ n ≡ 1 (mod 8), (2,1) ⇒ 11 (mod 16),
(1,2) ⇒ 13 (mod 16), (3,1) ⇒ 7 (mod 32), (1,3) ⇒ 5 (mod 32). These are precisely the binary
suffixes Charton lists as the learning order.

Three concrete correspondences worth stating out loud:

1. **Charton's "class mod 2^p" = the repo's 2-adic determinism table.** `MEMORY.md` records
   mod 4 → class 3, mod 16 → class 6, mod 32 → class 8, …, 89% classified by mod 4096.
   Charton's models climb the same ladder, one rung per accuracy jump.
2. **Charton's k (trailing 1-bits of n) = the repo's v₂(m+1) countdown** from the One-Bit
   Mixing result. He writes n = 2^k·m − 1; the repo writes the same structure as a 2-adic
   valuation counting down one bit per non-dropping step.
3. **The learning pattern is subgroup-by-subgroup.** A transformer trained on κ learns one
   affine map (one subgroup of a dropping set) at a time, in order of k + k′. That is a
   statement about *this repo's* decomposition, discovered independently by an ML experiment.

None of the three is claimed by [1] in this language — the repo vocabulary (dropping set,
subgroup, affine law) is not used there. Which is exactly the opening for new work.

## 2. Grokking a single Collatz step

**Gomezjurado Gonzalez, *The Long Delay to Arithmetic Generalization: When Learned
Representations Outrun Behavior*, arXiv:2604.13082 (2026)** [2]. Studies delayed
generalization ("grokking") on **one-step** Collatz prediction. Findings: the encoder learns
parity and residue organization within a few thousand steps while the decoder takes tens of
thousands more to use it; transplanting a trained encoder into a fresh model gives 2.75×
faster learning, transplanting a decoder *hurts*; freezing the encoder and retraining only
the decoder removes the plateau entirely. Numeral base again acts as an inductive bias —
bases whose factorization aligns with Collatz arithmetic reach 99.8%, while *binary
representations collapse and do not recover* on their setup.

Note the tension with [1], where binary-friendly (even, power-of-two) bases were best. The two
tasks differ (one step vs a long step; classification-ish vs regression), so this is a real
open question rather than a contradiction — and a cheap one to probe, see
[[Research Directions - Ternary Nets x Collatz]] §2.

## 3. Base representation and transformer arithmetic more generally

- **Charton, *Learning the greatest common divisor: explaining transformer predictions*,
  arXiv:2308.15594** [3]. Same methodology, simpler target. Models learn "products of divisors
  of the base and small primes" and predict the largest such number dividing both inputs.
  Accuracy depends strongly on base: 61.8% (base 11) → 96.8% (base 420), with composite
  bases (30, 60, 210, 420) best. Training distribution matters enormously: log-uniform
  *outcomes* raise correct GCDs ≤100 from 38 to 91. Charton reports the distribution trick
  does **not** transfer to the Collatz task [1, §6.3].
- **McLeish et al., *Transformers Can Do Arithmetic with the Right Embeddings*, NeurIPS 2024,
  arXiv:2405.17399** [4]. Abacus positional embeddings (encode each digit's position relative
  to the start of its number) plus input injection/recurrence: trained on ≤20-digit addition,
  up to 99% on 100-digit addition. Establishes that failure on arithmetic is often a
  *positional-encoding* problem, not a capacity problem.
- **Kaiser & Sutskever, *Neural GPUs Learn Algorithms*, arXiv:1511.08228** [5]. A
  convolutional-GRU architecture that learns long binary addition *and long binary
  multiplication* from short examples and generalizes to long ones — the first neural model
  to learn an algorithm with superlinear runtime. Price, Zaremba & Sutskever's follow-up
  *Extensions and Limitations of the Neural GPU* (2016) documents how fragile that
  generalization is [6].
- **Liu, Ash, Goel, Krishnamurthy, Zhang, *Transformers Learn Shortcuts to Automata*,
  arXiv:2210.10749** [7]. A shallow transformer can simulate any finite automaton with far
  fewer layers than steps, via the algebraic structure of its transformation semigroup:
  O(log T) depth in general, O(1) depth when the group is solvable. Directly relevant: the
  binary carry structure of 3n+1 *is* a finite transducer, so "can a transformer learn the
  carry transducer in constant depth" has a theoretical answer, and the parity/carry
  automaton is solvable.

## 4. Circuit and computability background

This matters for the hand-built [[Ternary Syracuse Circuit]] and for knowing what is
*provably* impossible.

- **Multiplication by the constant 3 is add-and-shift.** 3n = (n ≪ 1) + n, so 3n+1 is one
  carry-propagating addition — an operation whose signed-digit form uses digits {-1, 0, +1}.
  The relevant classical literature is *constant multiplication*: canonical signed digit /
  non-adjacent form recoding, Bernstein's shift-add sequences [8], and the multiple constant
  multiplication (MCM) problem [9]. Any exact ternary-weight construction for 3n+1 is
  rediscovering CSD recoding, and should cite it.
- **Threshold circuits.** Iterated addition, multiplication and even division sit in
  DLOGTIME-uniform TC⁰ (constant-depth threshold circuits) [10]; depth-size tradeoffs for
  arithmetic in threshold circuits are classical [11]. A ternary-weight threshold unit *is*
  a threshold gate with weights in {-1,0,+1}, so the question "how many trits and how much
  depth for one Syracuse step" is a small-constants instance of a well-studied problem.
- **Transformers are in TC⁰.** Merrill & Sabharwal, *The Parallelism Tradeoff: Limitations of
  Log-Precision Transformers*, TACL 2023 [12]: a log-precision transformer can be simulated
  by constant-depth logspace-uniform threshold circuits. So a fixed-depth transformer cannot
  iterate the Collatz map an unbounded number of times — the loop must come from
  autoregression/chain-of-thought, not depth. This is the formal version of Charton's
  finding that "the hard part is the loop lengths".
- **Recurrent nets are Turing-complete.** Siegelmann & Sontag, *On the computational power of
  neural nets*, JCSS 50(1):132–150, 1995 [13]: rational-weight recurrent nets simulate
  arbitrary Turing machines in real time. So a *recurrent* ternary network running Collatz is
  not prohibited by anything.
- **Generalized Collatz is undecidable.** Conway's *Unpredictable iterations* (1972) [14]
  encodes Minsky machines into generalized Collatz maps (later FRACTRAN); Kurtz & Simon,
  *The Undecidability of the Generalized Collatz Problem*, TAMC 2007 [15], show the natural
  generalization is Π⁰₂-complete/recursively undecidable. Consequence for this project: no
  network can be expected to *decide* Collatz-like halting in general. A network can compute
  the step function exactly (that is finite-state per digit); predicting stopping time in
  closed form is the part with a hardness barrier.

## 5. Cellular automata and the base-6 lattice

**Kari, *Cellular Automata, the Collatz Conjecture and Powers of 3/2*, DLT 2012** [16]
constructs one-dimensional reversible CA F×3 and F×3/2 that multiply by 3 and by 3/2 **in
base 6**, shows F×3 can be modified to simulate the Collatz function, and connects F×3/2 to
Mahler's Z-number problem. This is a direct, citable precedent for the repo's base-6 theme
(`MEMORY.md`: conservation law s·log₂6, spectral gap → 5/6, λ₂ = 1/6 from rad(6)). A CA is a
weight-shared local network — i.e. a convolutional network with a hand-set kernel — so Kari's
construction is also the natural "exact neural" model of the Collatz map in base 6, and a
sensible baseline for the [[Ternary Syracuse Circuit]] work (binary carry transducer vs base-6
local rule).

## 6. Statistical / ML models of stopping times

- **Bayesian Modeling of Collatz Stopping Times: A Probabilistic Machine Learning
  Perspective**, arXiv:2603.04479 (2026) [17]. Hierarchical negative-binomial regression for
  total stopping time τ(n) over n ≤ 10⁷ from just log n and n mod 8, versus a mechanistic
  "odd-block" generative model. The GLM wins on held-out predictive likelihood. Useful as a
  **baseline to beat**: any learned model of stopping time should be compared against
  "log n + n mod 8" regression, which is close to free.
- **Chang, *Exploring Collatz Dynamics with Human-LLM Collaboration*, arXiv:2603.11066
  (2026)** [18]. ~10¹⁴ computational experiments, 630 formal results, modular scrambling
  lemma and burst–gap decomposition; explicitly not a proof. Same author as the "one-bit
  orbit mixing" reduction already in `MEMORY.md`. Relevant mainly as evidence that
  LLM-assisted Collatz exploration is now a publishable genre, and as a methodological
  cautionary tale about the volume-of-results-to-insight ratio.
- Lowry-Duda's work on transformers and the Möbius function, cited in [1], is the closest
  analogue for "learn a multiplicative/number-theoretic function" [1, §2].

## 7. The gap

Searched and **not found** (as of 2026-09-16):

- Any work training a **ternary / low-bit** network on a Collatz task, or asking whether
  ternary weights are a natural basis for 2-adic residue structure.
- Any work probing a Collatz-trained network for the **affine subgroup structure**
  (slope 3^s/2^(k−s), intercept C) rather than for output accuracy.
- Any use of Collatz as a **benchmark for quantization damage** (does ternarization break
  carry propagation specifically?).
- Any connection between the repo's dropping-set / Eisenstein-sector machinery and learned
  representations, beyond the repo's own `docs/Explorations/Collatz Embeddings.md`.

All four are cheap to attempt; see [[Research Directions - Ternary Nets x Collatz]].

## Sources

1. Charton, F., Narayanan, A. — *Transformers know more than they can tell: Learning the Collatz sequence* (13 Nov 2025). https://arxiv.org/abs/2511.10811
2. Gomezjurado Gonzalez, L. — *The Long Delay to Arithmetic Generalization: When Learned Representations Outrun Behavior* (Mar 2026, rev. Jun 2026). https://arxiv.org/abs/2604.13082
3. Charton, F. — *Learning the greatest common divisor: explaining transformer predictions*, ICLR 2024 (2023). https://arxiv.org/abs/2308.15594
4. McLeish, S., Bansal, A., Stein, A., Jain, N., Kirchenbauer, J., Bartoldson, B. R., Kailkhura, B., Bhatele, A., Geiping, J., Schwarzschild, A., Goldstein, T. — *Transformers Can Do Arithmetic with the Right Embeddings*, NeurIPS 2024. https://arxiv.org/abs/2405.17399
5. Kaiser, Ł., Sutskever, I. — *Neural GPUs Learn Algorithms*, ICLR 2016. https://arxiv.org/abs/1511.08228
6. Price, E., Zaremba, W., Sutskever, I. — *Extensions and Limitations of the Neural GPU* (2016). *arXiv identifier not independently verified; record exists via ResearchGate/ICLR 2017 workshop track.*
7. Liu, B., Ash, J. T., Goel, S., Krishnamurthy, A., Zhang, C. — *Transformers Learn Shortcuts to Automata*, ICLR 2023. https://arxiv.org/abs/2210.10749
8. Bernstein, R. — *Multiplication by integer constants*, Software: Practice and Experience 16(7):641–652, 1986. https://onlinelibrary.wiley.com/doi/abs/10.1002/spe.4380160704
9. Voronenko, Y., Püschel, M. — *Multiplierless multiple constant multiplication*, ACM Transactions on Algorithms 3(2), art. 11, 2007. https://dl.acm.org/doi/10.1145/1240233.1240234
10. Hesse, W., Allender, E., Barrington, D. A. M. — *Uniform constant-depth threshold circuits for division and iterated multiplication*, JCSS 65(4):695–716, 2002. https://www.sciencedirect.com/science/article/pii/S0022000002000259
11. Siu, K.-Y., Roychowdhury, V., Kailath, T. — *Depth-size tradeoffs for neural computation*, IEEE Transactions on Computers 40(12):1402–1412, 1991. https://www.semanticscholar.org/paper/1cda5453eeb2c759cc1a7abf4f13b0ca3cb11c0d
12. Merrill, W., Sabharwal, A. — *The Parallelism Tradeoff: Limitations of Log-Precision Transformers*, TACL 2023. https://arxiv.org/abs/2207.00729
13. Siegelmann, H. T., Sontag, E. D. — *On the computational power of neural nets*, Journal of Computer and System Sciences 50(1):132–150, 1995. https://www.sciencedirect.com/science/article/pii/S0022000085710136
14. Conway, J. H. — *Unpredictable iterations*, Proc. 1972 Number Theory Conference, Univ. of Colorado, pp. 49–52. *Primary text not fetched; verified via secondary sources incl. [15].*
15. Kurtz, S. A., Simon, J. — *The Undecidability of the Generalized Collatz Problem*, TAMC 2007, LNCS 4484:542–553. https://people.cs.uchicago.edu/~simon/RES/collatz.pdf
16. Kari, J. — *Cellular Automata, the Collatz Conjecture and Powers of 3/2*, DLT 2012, LNCS 7410:40–49. https://link.springer.com/chapter/10.1007/978-3-642-31653-1_5
17. *Bayesian Modeling of Collatz Stopping Times: A Probabilistic Machine Learning Perspective* (4 Mar 2026). https://arxiv.org/abs/2603.04479
18. Chang, E. Y. — *Exploring Collatz Dynamics with Human-LLM Collaboration* (2026). https://arxiv.org/abs/2603.11066
