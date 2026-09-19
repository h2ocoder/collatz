---
tags: [ternary-llm, information-theory, paper-summary, log2-3]
status: complete
created: 2026-09-16
---

# Paper — Breaking the 1.58-bit Barrier for Ternary LLMs

Georganas, Heinecke & Dubey (Intel), arXiv:2609.16338v1 [1]. Structured summary,
plus the information theory the paper leaves implicit (computed here).

Siblings: [[00 Index]] · [[Trit Packing and log2(3)]] ·
[[Collatz Bridge - Trits and Stopping Times]] · [[Ternary LLMs - State of the Art]]

## 1. Problem

Ternary LLMs store every weight as a trit $w \in \{-1, 0, +1\}$ (BitNet b1.58 and
successors [4]). The paper is purely a *storage-layout and kernel* paper: no
training, no accuracy claims. It asks how few bits per weight a deployable layout
can use while keeping the unpack sequence cheap enough that GEMV stays
bandwidth-bound rather than instruction-bound.

## 2. The "1.58-bit barrier"

> "Three equiprobable symbols carry $\log_2 3 \approx 1.585$ bits of information"

so $\log_2 3$ is quoted as the floor. Two deployed layouts bracket it:

| layout | rate | note |
|---|---|---|
| 2-bit (`I2_S`, `TQ2_0`) | 2.000 bpw | one trit per 2-bit field, one state wasted |
| five-trit-per-byte (`TQ1_0`) | 8/5 = 1.600 bpw | "Five trits fit in a byte ($3^5 = 243 \le 256$)" |
| five-trit in a 128-block | 1.625 bpw | "128 is not a multiple of 5: a block needs $\lceil 128/5 \rceil = 26$ payload bytes, so the rate stored in practice is $26 \times 8/128 = 1.625$" |

The 1.625 number is the paper's real target: block-alignment padding, not the
packing itself, is what keeps deployed formats above $\log_2 3$. See
[[Trit Packing and log2(3)]] — **26 bytes is provably the best a byte-aligned
128-trit block can do**, so the paper's framing is fair.

## 3. BITCOS = BITmap + COmpacted Signs

Layout (§II-A):

> "a *presence bitmap* of one bit per weight, set where the weight is non-zero;
> and a *sign vector* of one bit per *non-zero* weight, in tensor order."

Cost, with zero density $z$:

$$B(z) = 1 + (1-z) = 2 - z \ \text{bits/weight}$$

- Beats the deployed five-trit rate once $2-z < 1.625$, i.e. $z > 0.375$.
- The sign stream is *variable-rate*: a column's sign bits start at a cursor that
  "the bitmap alone does not give away", recovered by popcount over preceding
  bitmap words; no explicit per-block offset metadata is stored.
- Unpack uses `pdep` semantics ("pdep takes the low bits of its source in order
  and drops them at the positions the mask selects"): AVX-512 uses mask registers
  (17 instructions/iteration, 3 for unpacking); AVX2 materialises byte masks;
  the Xe2 GPU kernel uses a 256-entry SLM lookup table indexed by
  $(m, s)$ = 4 presence bits + 4 sign bits, each entry holding four fp16 constants.

## 4. Zero densities (Table I, 29 models)

Measured $z$ ranges **29.66 %** (Bonsai 27B) to **51.48 %** (CAT-Q Qwen3-1.7B);
mean over the 29 models ≈ **40.5 %**. The table's "Symbols" column is exactly
$2 - z$; "+Scale" adds group-scale metadata (16-bit scale per group; 0.125 bpw at
group size 128, as little as 0.003 bpw for near-per-tensor groups). BITCOS stores
more compactly than five-trit packing in **26 of 29** models — the three
exceptions are the three models with $z < 0.375$ (Bonsai 27B 29.66 %,
CAT-Q Qwen3-30B-A3B 32.88 %, CAT-Q Qwen3-235B-A22B 34.07 %).

## 5. Results and limits

- GEMV vs the 2-bit baseline: 1.14–1.28× (Emerald Rapids), 1.13–1.27× (Arrow
  Lake), 1.04–1.14× (Arc 140V), 1.01–1.12× (Arc Pro B70).
- End-to-end decode: up to 1.18× (CPU), 1.27× (GPU).
- Negative result worth keeping: on Lunar Lake the kernel is *instruction-bound*
  and BITCOS loses to the 2-bit reference at every density. Smaller payload only
  pays when the pipeline is bandwidth-bound — the roofline crossover is the
  paper's honest boundary condition.

## 6. What the paper does not do

No entropy coding, arithmetic coding, Huffman, rANS, or any information-theoretic
bound beyond quoting $\log_2 3$. No mention of balanced-ternary hardware history,
of the $3^t \le 2^b$ packing family beyond $t=5$, or of why 128 (it is inherited
from quantisation group size, not derived). It also does not compare against
`TL2` (bitnet.cpp), which already packs 3 trits in 5 bits = 1.667 bpw [5].

## 7. The implicit information theory (computed here)

Script: `research/investigate-ternary-llms/scripts/entropy_bitcos.py`.

For the i.i.d. ternary source $P(0)=z$, $P(\pm 1) = (1-z)/2$:

$$H(z) = h(z) + (1-z), \qquad h(z) = -z\log_2 z - (1-z)\log_2(1-z)$$

**Verified facts.**

1. $H(z) \le H(1/3) = \log_2 3$ with equality **only** at $z = 1/3$. So for any
   real model the "1.58-bit barrier" is not the bound — $\log_2 3$ is the
   *maximum* of the true bound over $z$. Every measured model has
   $H(z) < \log_2 3$, and $\max_z H(z) = 1.58496 < 1.625$: **the deployed rate
   exceeds the entropy bound for every possible zero density**, uniform included.
2. $B(z) - H(z) = 1 - h(z)$ exactly. The whole BITCOS overhead is the entropy
   deficit of the *presence bitmap*, which is stored raw at 1 bit/weight when it
   only carries $h(z)$ bits. The sign stream is already optimal (signs are
   equiprobable given non-zero).
3. $B(z) = 2 - z$ is exactly the expected length of a **single-symbol Huffman
   code** for this source whenever $z \ge 1/3$ (codeword lengths $1,2,2$).
   BITCOS is therefore Huffman coding, stream-separated so it can be decoded
   with `pdep` instead of a bit-serial tree walk. For $z < 1/3$ Huffman gives
   $(3+z)/2$ (short code to a signed symbol) — better than $2-z$ — which is why
   BITCOS degrades for the three low-$z$ models.
4. Break-even points: $B(z) = 1.625 \iff z = 3/8$ (the paper's threshold), and
   $B(z) = \log_2 3 \iff z = 2 - \log_2 3 = \log_2(4/3) = 0.41504$. Eight of the
   29 models are above the second threshold (BitNet b1.58 2B4T, CAT-Q
   Qwen3-1.7B/8B/32B, ParetoQ 350M/600M/1B/1.5B) — those genuinely store below the
   uniform-ternary information content.

**Overhead table** (bits/weight; full 29-model table in the script output):

| model | $z$ | $H(z)$ | BITCOS $2-z$ | gap $1-h(z)$ |
|---|---|---|---|---|
| CAT-Q Qwen3-1.7B | 0.5148 | 1.4846 | 1.4852 | 0.0006 |
| CAT-Q Qwen3-32B | 0.4711 | 1.5265 | 1.5289 | 0.0024 |
| ParetoQ 1.5B | 0.4710 | 1.5266 | 1.5290 | 0.0024 |
| BitNet b1.58 2B4T | 0.4219 | 1.5604 | 1.5781 | 0.0177 |
| TriLM 1.5B | 0.4021 | 1.5701 | 1.5979 | 0.0278 |
| BitCPM-CANN 0.5B | 0.3767 | 1.5790 | 1.6233 | 0.0443 |
| CAT-Q Qwen3-30B-A3B | 0.3288 | 1.5849 | 1.6712 | 0.0863 |
| Bonsai 27B | 0.2966 | 1.5805 | 1.7034 | 0.1229 |

At $z = 1/2$ the source is dyadic ($\tfrac12, \tfrac14, \tfrac14$) and BITCOS is
**exactly** entropy-optimal — CAT-Q Qwen3-1.7B at $z = 0.5148$ is within
0.0006 bits/weight of the Shannon bound. Mean gap over the 29 models: 0.026
bits/weight (1.7 %).

**What an arithmetic coder would buy.** Block-Huffman rates converge to $H(z)$
from above (computed for blocks of $m = 1 \dots 8$ trits): at $z = 0.4219$,
$m{=}1$ gives 1.578, $m{=}5$ gives 1.567, $m{=}8$ gives 1.564, vs $H = 1.5604$.
For a 2 B-weight model that is ~4 MB saved out of 395 MB — and it costs
sequential decode, which destroys the random access the kernels need. **Verdict:
entropy coding is correctly absent from this paper.** BITCOS sits within 1–2 % of
the Shannon bound while staying `pdep`-decodable; the remaining headroom is not
worth the decode. The only real headroom is for the $z < 3/8$ models, where
swapping the roles of the streams (Huffman order) recovers up to 0.1 bpw.

## 8. What transfers to the Collatz work

Only the mathematics of $3^t \le 2^b$, not the LLM content. See
[[Trit Packing and log2(3)]] and [[Collatz Bridge - Trits and Stopping Times]].

## Sources

1. E. Georganas, A. Heinecke, P. Dubey, "Breaking the 1.58-bit Barrier for Ternary LLMs", arXiv:2609.16338v1 — https://arxiv.org/html/2609.16338v1
2. llama.cpp `ggml-common.h`, `block_tq1_0` (1.6875 bpw) and `block_tq2_0` (2.0625 bpw) — https://raw.githubusercontent.com/ggml-org/llama.cpp/master/ggml/src/ggml-common.h
3. ggml-org/llama.cpp PR #22836, "ggml-cpu: add STQ1_0 ternary quantization" — https://github.com/ggml-org/llama.cpp/pull/22836
4. S. Ma et al., "The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits" (cited as [1] by the paper).
5. J. Wang et al., "Bitnet.cpp: Efficient Edge Inference for Ternary LLMs", arXiv:2502.11880 — https://arxiv.org/html/2502.11880v1
