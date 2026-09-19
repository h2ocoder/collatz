---
tags: [proposals, ternary, collatz, machine-learning, experiments]
status: proposal
created: 2026-09-16
---

# Research Directions — Ternary Nets × Collatz

**Everything in this note is a proposal, not a result.** Part 3 of the [[00 Index]]
investigation. Background: [[Ternary LLMs - State of the Art]],
[[Neural Networks and Collatz - Prior Work]]. Related in-flight work:
[[Ternary Syracuse Circuit]] (exact hand-built ternary threshold RNN for the Syracuse map —
*not* proposed here, but extended in §E).

## The one idea that makes the pairing non-arbitrary

Ternary weights are a *signed-digit* representation: `{-1, 0, +1}` with a power-of-two scale
is exactly canonical signed digit / balanced ternary, and 3n+1 = (n≪1) + n + 1 is a
signed-digit constant multiplication. Meanwhile, this repo's central structural fact is that
Collatz behaviour is determined by *low binary digits* (2-adic determinism: mod 4 → Set₃,
mod 16 → Set₆, …), and Charton & Narayanan showed that transformers learning the long
Collatz step climb exactly that mod-2^p ladder [1]. So there is a real hypothesis available,
not just a pun:

> **H1.** A ternary-weight network is a *more natural hypothesis class* for Collatz structure
> than a full-precision one, because the target function is a signed-digit / residue-class
> computation, and because a ternary weight matrix is directly readable as a set of residue
> tests (+1 = "this bit must be 1", −1 = "must be 0", 0 = "don't care").

H1 is falsifiable, and every experiment below is an angle on it. The honest prior: H1 is
plausible for *interpretability* (readable weights) and weak for *accuracy* (ternary rarely
beats fp; it matches it). Design the experiments so the interpretability payoff survives even
if the accuracy claim dies.

## A. Ternary stopping-class classifier on binary digits

*(this is idea (a) from the brief — kept, sharpened)*

**Question.** Train a ternary-weight MLP to predict a number's dropping set from its low bits.
Do the learned ternary weights recover the known residue-class structure (mod 2^p), i.e. can
you *read the theorem off the weight matrix*?

**Setup.**
- Inputs: the low B bits of odd n, encoded as ±1 (B = 12, 16, 20). Optionally a second
  variant with base-6 digits for comparison with §B.
- Target: `collatz.dropping.dropping_set(n)` (equivalently `stopping.stopping_class(n)`),
  capped at classes 3, 6, 8, 11, 13, 16, 19 + "other" (the odd-n spectrum from `MEMORY.md`).
- Model: 2-layer MLP, width 64–256, `BitLinear`-style absmean ternarization + straight-through
  estimator [2][3]; matched full-precision baseline; matched *binary* `{-1,+1}` baseline to
  isolate the value of the zero.
- Analysis, and this is the actual deliverable: for each hidden unit, read the ternary weight
  vector as a partial pattern over bits and check whether its support is a prefix of the
  trailing bits, and whether the induced test matches a known modulus. Measure "support
  locality" = fraction of non-zero weights in the lowest p positions; measure agreement
  between each unit's induced partition and the partition by n mod 2^p.
- Sweep: accuracy vs B (expect a staircase — 50% at B = 2, ~62.5% at B = 4, … tracking the
  repo's mod-2^p coverage table), and accuracy vs class rank.

**Positive result.** Ternary weights concentrate on trailing bits, zeros mark the
"don't care" high bits, and units implement recognisable residue tests. That is a clean
interpretability claim: *the zero in `{-1,0,+1}` is literally the "don't care" of the 2-adic
structure*, and a ternary net trained on Collatz is a self-documenting decision list. It also
gives a non-trivial ML-side claim (ternary as a good inductive bias for p-adic targets) that
generalises beyond Collatz.

**Negative result.** Weights look like dense noise with matching accuracy — then ternary buys
nothing interpretability-wise, and the honest conclusion is "ternarization is orthogonal to
2-adic structure". Still worth writing down; it kills H1 cheaply.

**Cost.** Laptop, CPU-only, minutes per run. Data generation via `collatz.dropping` for
n < 10⁶ is seconds. **This is the cheapest experiment in the note and should be first.**

**Gotcha.** The task is *trivially* solvable by memorising a lookup table on B bits when
2^B ≪ dataset size. Control for this: train on n < 10⁶, test on n ∈ [10⁹, 10⁹ + 10⁶], and
report *weight structure*, not just accuracy.

## B. Does the base matter the way Charton found — and is base 6 special?

*(idea (b), first half)*

**Question.** Charton found accuracy on the long Collatz step ranges from 99.7% (bases 24,
16, 32) to 25% (base 3) [1]; Gomezjurado Gonzalez found the opposite polarity on one-step
Collatz, with binary collapsing and "factorization-aligned" bases at 99.8% [4]. This repo's
whole Paper 3 / conservation-law story says **base 6** is the natural lattice. So: for
*repo-native* targets (dropping set k, Syracuse step count s, α-sequence), does base 6 beat
base 2, 8, 16, 24 at equal information budget?

**Setup.** Fix a small encoder-decoder or decoder-only transformer (Charton's scale is
already laptop-adjacent: 4 encoder layers, dim 512). Targets, in increasing difficulty:
(i) dropping set of n; (ii) s = number of Syracuse steps to drop (`len(alpha_sequence(n))`);
(iii) κ(n) regression as in [1]. Bases B ∈ {2, 3, 6, 8, 10, 16, 24}, digit budget equalised
(same maximum n, so sequence lengths differ — report both per-base and per-token-budget).

**Positive result.** Base 6 outperforms bases with the same "even-ness" advantage (8, 16, 24)
on targets (i)/(ii). That would be evidence that the repo's base-6 lattice is a *learnable*
inductive bias and not just an accounting identity — and it directly extends Kari's base-6
Collatz cellular automaton [5] into the learned setting.

**Negative result — and I expect this one.** Base 6 lands between base 2 and base 8 exactly
where its factor 2 predicts, because k and k′ are *binary* suffix properties (Charton's
Theorem 2) and the factor 3 contributes nothing to reading them. Predicting this in advance
and then confirming it is still a result: it says the base-6 structure lives in the
*dynamics* (growth/contraction balance) and not in the *digit representation* — which
sharpens the repo's conservation-law claim rather than weakening it.

**Cost.** This is the expensive one: 7 bases × ~1 GPU-day each at Charton's scale. Scale down
(dim 256, 2 layers, n < 10⁸, 20M examples) to fit a laptop GPU overnight, and treat the
absolute accuracies as incomparable to [1].

## C. Probing for the affine map and the hidden intercept C

*(idea (b), second half — the interpretability core)*

**Question.** When a transformer learns the long Collatz step, does it internally represent
the *affine* parameters — slope 3^k/2^(k+k′) and intercept C = (3^k − 2^k)/2^(k+k′) — or only
a suffix-matching rule? The repo's Complementarity note treats C as the hidden variable that
encodes all mod-p correlations; if C is linearly decodable from the residual stream, that
claim gets a mechanistic counterpart.

**Setup.** Train (or reuse from §B) a model on κ(n). Then linear probes on the residual
stream at each layer for: k, k′, subgroup id (k, k′), log₂ slope, and C. Compare against
a control probe for a quantity the model *cannot* need (e.g. n mod 7, or the Eisenstein
sector of n). Ablate: patch the k′ representation from a different input and see whether the
output changes by the predicted power of two — Charton's power-of-two error mode [1] predicts
exactly this intervention should produce p = 2^δ·κ(n).

**Positive result.** A causal, quantitative account: "the model computes κ by estimating
(k, k′) and then applying the affine map", verified by activation patching. That is a genuine
mechanistic-interpretability contribution, and it is stated in the repo's own vocabulary
(subgroups, slope, intercept) which nobody in the ML literature uses.

**Negative result.** Probes find k and k′ but no representation of the slope/intercept — the
model does digit-wise arithmetic instead. Also informative, and consistent with the "carry
transducer" picture that [[Ternary Syracuse Circuit]] builds by hand.

**Cost.** Needs a trained model from §B (reuse!), then probes are minutes. Activation patching
needs a bit of plumbing; `TransformerLens`-style tooling or a hand-rolled hook is fine at this
scale.

## D. CollatzBench: Collatz as a probe of quantization damage

*(idea (c) — kept, and I think it is the most publishable)*

**Question.** Does ternary quantization damage *arithmetic* ability in a structured way?
Specifically: is the damage concentrated in carry propagation / control flow (the k′ loop),
which is what Charton showed is the hard part?

**Setup.** No training. Evaluate off-the-shelf models on a Collatz task suite:
- Models: ternary — BitNet b1.58 2B4T [6], TriLM 3.9B [7], Falcon-Edge 1.58-bit [8],
  Bonsai/Maple if runnable [9][10]; full-precision controls of matched size — Qwen2.5-1.5B,
  LLaMA-3.2-1B, Gemma-3-1B; plus PTQ controls (INT4/INT2 of the same fp models) to separate
  "low-bit" from "ternary".
- Tasks, all exactly checkable with `collatz.core`: one Syracuse step; κ(n) (long step);
  number of trailing 1-bits k; stopping time; "is n in dropping set 3".
- Report accuracy **stratified by (k, k′)** — Charton's classes — and by digit length.
  The stratification is the novelty: aggregate accuracy tells you nothing, the profile does.

**Positive result.** Ternary models lose accuracy specifically at large k′ (deep carry chains)
while matching on small classes → "low-bit quantization preferentially destroys control-flow
depth, not arithmetic". That is a claim the quantization literature currently has no clean
instrument for, and Collatz is the instrument: exactly known, unbounded difficulty, one
parameter (k + k′) that grades it.

**Negative result.** Ternary and fp degrade identically (both collapse past k + k′ ≈ 4).
Then the conclusion is "these models don't do multi-step integer arithmetic at all, at any
precision" — still a usable negative benchmark result, and cheap.

**Cost.** Laptop. `bitnet.cpp` [11] / `llama.cpp` run all of these on CPU; the whole suite is
a few thousand prompts per model. Half a day of engineering, mostly harness.

**Gotcha.** Prompt-format sensitivity will dominate unless controlled. Use the same few-shot
template for all models, and report both greedy and self-consistency; check tokenizer digit
splitting (a model that tokenizes "12345" as one token is playing a different game).

## E. Follow-ups on the exact ternary Syracuse circuit

*(the main agent is hand-building this; these are extensions, not a rebuild)*

**Literature it should cite.** 3n = (n≪1) + n means one Syracuse step is a single
carry-propagating addition, whose minimal signed-digit form is the canonical signed digit /
non-adjacent-form recoding — the constant-multiplication literature (Bernstein's shift-add
sequences [12]; multiplierless MCM [13]). For the "how deep/how wide must the threshold
network be" question, the right frame is threshold-circuit complexity: iterated addition and
multiplication in DLOGTIME-uniform TC⁰ [14], depth-size tradeoffs for arithmetic in threshold
circuits [15], and — for the transformer version — Merrill & Sabharwal's result that
log-precision transformers live in uniform TC⁰ [16], which implies the iteration must come
from autoregression rather than depth. Kari's base-6 cellular automaton for ×3 and ×3/2 [5] is
the CA-shaped cousin of the same construction and the natural base-6 baseline.

**Three follow-up experiments.**
1. **Recoverability.** Take the hand-built exact circuit as ground truth; train a same-shape
   ternary network by QAT on (bit-string, bit-string) pairs; measure sign agreement and
   weight-space distance to the exact solution. Question: *does gradient descent find the
   circuit a human designed, or a different one?* Positive = a rare exact-solution grokking
   study with a known target. Cost: laptop hours.
2. **Initialization / lottery ticket.** Initialize at the exact circuit ± noise and measure
   the basin of attraction; initialize a *larger* net with the exact circuit embedded and
   see whether training preserves or destroys it. Relevance to ternary LLMs: whether
   discrete-weight training can preserve a known algorithm is precisely the QAT-stability
   question [17].
3. **Minimality.** Empirically search (SAT/ILP, or exhaustive at tiny widths) for the
   smallest ternary threshold circuit computing one Syracuse step on B bits, and compare to
   the hand-built one and to the CSD lower bound. A crisp, checkable number — the kind of
   thing that makes the note citable.

## F. The zero-density question, evaluated skeptically

*(idea (d) — mostly rejected, one salvageable version)*

**Reject:** "51.5% zeros in ternary LLMs [18] is Collatz-y" and "1.58 = log₂3 is the same 3 as
in 3n+1". These are numerology. The zero density is a property of the absmean quantizer
applied to a zero-peaked latent weight distribution — Sparse-BitNet shows the same ~42% from
the "quantization valley" [19] — and has no dynamical content. log₂3 appearing in trit packing
is an *encoding-efficiency* constant; log₂6 = 1 + log₂3 in the repo's conservation law is a
*growth-rate* constant. Same number, unrelated roles. [[Trit Packing and log2(3)]] should say
this explicitly so the coincidence stops being tempting.

**Keep, in bounded form:** in a network trained on a *Collatz* task (§A), do the zeros
localise on the high-order bits — the bits that provably cannot affect the answer? That is a
real, falsifiable question about whether "zero = don't care" is learned rather than assumed.
Metric: mutual information between zero-position and bit significance, against a shuffled
baseline. If yes, it is a one-paragraph result supporting H1; if no, drop the thread entirely.

**Cost.** Free — it is an analysis rider on §A.

## Ranking

| # | Experiment | Cost | Payoff if positive | Risk |
|---|---|---|---|---|
| A | Ternary dropping-set classifier | hours, CPU | Readable weights = readable theorem | memorisation confound |
| D | CollatzBench quantization probe | half a day, CPU | New instrument for quantization damage | all models may be at floor |
| C | Affine/intercept probing | needs §B model | Mechanistic version of the affine law | probes may find nothing |
| E | Circuit follow-ups | hours–days | Exact-target grokking study | narrow audience |
| B | Base sweep incl. base 6 | GPU-days | Base-6 as learnable bias | expected negative |
| F | Zero-localisation rider | free | supports H1 | trivially null |

**Do A first** (cheapest, tests H1 directly, and its analysis code is reused by F and E).
**Do D second** (no training at all, and it is the one outsiders would cite).

## Sources

1. Charton, F., Narayanan, A. — *Transformers know more than they can tell: Learning the Collatz sequence* (2025). https://arxiv.org/abs/2511.10811
2. Ma, S. et al. — *The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits* (2024). https://arxiv.org/abs/2402.17764
3. Bengio, Y., Léonard, N., Courville, A. — *Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation* (2013). https://arxiv.org/abs/1308.3432
4. Gomezjurado Gonzalez, L. — *The Long Delay to Arithmetic Generalization* (2026). https://arxiv.org/abs/2604.13082
5. Kari, J. — *Cellular Automata, the Collatz Conjecture and Powers of 3/2*, DLT 2012. https://link.springer.com/chapter/10.1007/978-3-642-31653-1_5
6. Ma, S. et al. — *BitNet b1.58 2B4T Technical Report* (2025). https://arxiv.org/abs/2504.12285
7. Kaushal, A. et al. — *Spectra: Pretraining Ternary Language Models at Scale* (2024). https://arxiv.org/abs/2407.12327
8. TII — *Falcon-Edge: 1.58-bit language models* (2025). https://huggingface.co/blog/tiiuae/falcon-edge
9. PrismML — *Bonsai 27B* (2026). https://huggingface.co/prism-ml/Ternary-Bonsai-27B-gguf
10. DeepGrove — *Maple-Preview 20B-A1B ternary MoE* (2026). https://huggingface.co/deepgrove/maple-preview
11. Wang, J. et al. — *Bitnet.cpp: Efficient Edge Inference for Ternary LLMs*, ACL 2025. https://arxiv.org/abs/2502.11880
12. Bernstein, R. — *Multiplication by integer constants*, Software: Practice and Experience 16(7):641–652, 1986. https://onlinelibrary.wiley.com/doi/abs/10.1002/spe.4380160704
13. Voronenko, Y., Püschel, M. — *Multiplierless multiple constant multiplication*, ACM TALG 3(2):11, 2007. https://dl.acm.org/doi/10.1145/1240233.1240234
14. Hesse, W., Allender, E., Barrington, D. A. M. — *Uniform constant-depth threshold circuits for division and iterated multiplication*, JCSS 65(4):695–716, 2002. https://www.sciencedirect.com/science/article/pii/S0022000002000259
15. Siu, K.-Y., Roychowdhury, V., Kailath, T. — *Depth-size tradeoffs for neural computation*, IEEE Trans. Computers 40(12):1402–1412, 1991.
16. Merrill, W., Sabharwal, A. — *The Parallelism Tradeoff: Limitations of Log-Precision Transformers*, TACL 2023. https://arxiv.org/abs/2207.00729
17. Huang, J. et al. — *Tequila: Trapping-free ternary quantization for LLMs* (2025), arXiv:2509.23809 — *cited in [18]; not independently verified.*
18. Georganas, E., Heinecke, A., Dubey, P. — *Breaking the 1.58-bit Barrier for Ternary LLMs* (2026). https://arxiv.org/abs/2609.16338
19. Zhang, D. et al. — *Sparse-BitNet: 1.58-bit LLMs are Naturally Friendly to Semi-Structured Sparsity* (2026). https://arxiv.org/abs/2603.05168
