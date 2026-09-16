---
tags: [ternary, llm, quantization, survey, ml]
status: draft
created: 2026-09-16
---

# Ternary LLMs — State of the Art

A survey for a mathematician who has not worked in machine learning. Part 1 of the
[[00 Index]] investigation. Companion notes: [[Neural Networks and Collatz - Prior Work]],
[[Research Directions - Ternary Nets x Collatz]], [[Paper - Breaking the 1.58-bit Barrier]],
[[Trit Packing and log2(3)]].

Every arXiv identifier below was checked by fetching the abstract or PDF, except where the
note says "not independently verified".

## TL;DR

A *ternary* neural network stores every weight as one of three symbols `{-1, 0, +1}`.
Because the weights are no longer arbitrary real numbers, the dominant operation of a neural
network — the matrix-vector product — stops being multiplication and becomes *signed
addition*: add the input, subtract the input, or skip it. Information-theoretically each
weight costs log₂3 ≈ 1.585 bits, which is where the marketing name "1.58-bit LLM" comes
from [1]. Since 2024 this has gone from a curiosity to a deployed format: there are
open ternary models from 0.5B to 27B parameters, CPU/GPU kernels in `llama.cpp`, vLLM and
`bitnet.cpp`, FPGA accelerators, and as of 2026 ternary mixture-of-experts reasoning models
that run on a phone [2][3][4][5].

The headline claim of the field — that ternary weights cost you almost nothing in accuracy
if you *train* with them rather than rounding a finished model — is now well supported at
the ≤10B scale and increasingly at 27B [1][6][7][3].

## Glossary (for the non-specialist)

| Term | Meaning |
|---|---|
| **Weight** | One number in the network's parameter matrix. A 2B model has 2×10⁹ of them. |
| **Matmul / GEMM / GEMV** | Matrix-matrix / matrix-vector multiply. ~All of the compute. |
| **Activation** | The vector flowing between layers (the "input" to each matmul). |
| **Quantization** | Replacing high-precision weights (fp16 = 16 bits) with a small set of values. |
| **bpw** | Bits per weight, the storage cost after packing. Ternary's floor is log₂3 ≈ 1.585. |
| **PTQ** | *Post-training* quantization: take a finished model, round its weights, calibrate. Cheap. |
| **QAT** | *Quantization-aware training*: train with the rounding in the loop. Expensive, more accurate. |
| **STE** | Straight-through estimator: the trick that makes QAT differentiable (below) [8]. |
| **absmean quantizer** | BitNet's rule: scale a weight matrix by its mean absolute value, then round each entry to the nearest of {-1,0,+1} [1]. |
| **Perplexity** | How surprised the model is by held-out text. Lower is better; the standard accuracy proxy. |
| **MoE** | Mixture-of-experts: only a fraction of the weights are used per token (e.g. "20B-A1B" = 20B total, 1B active). |
| **KV cache** | Stored attention state; often the memory bottleneck at long context. |
| **Memory-bound decode** | Generating one token at a time reads the whole weight matrix but does little arithmetic, so *speed tracks bytes moved*, not FLOPs. This is why bpw matters so much [2]. |

## Why {-1, 0, +1}

Three reasons, in increasing order of importance:

1. **Arithmetic.** `y = Wx` with `W ∈ {-1,0,+1}` needs no multipliers: each term is `+x_i`,
   `-x_i`, or nothing. On CPUs this becomes masked adds; in silicon it removes the
   multiplier array entirely, which is where most of the energy goes. This is the oldest
   observation in the field — Ternary Weight Networks (Li, Liu, Zhang et al., 2016) already
   reported ~16× compression with "fewer multiplications" [9], and Trained Ternary
   Quantization (Zhu, Han, Mao, Dally, ICLR 2017) learned the scale factors too [10].
2. **The zero.** Binary `{-1,+1}` forces every input to contribute. The zero gives the
   network a *feature filter* — it can ignore an input — and empirically this is worth a
   lot of accuracy [1]. It also makes the weight matrix naturally sparse (see §"Zeros"),
   which is what [[Paper - Breaking the 1.58-bit Barrier]] exploits.
3. **Bandwidth.** Token-by-token generation is memory-bound: time per token ≈ (bytes of
   weights) / (memory bandwidth). Going fp16 → ternary is a ~10× reduction in bytes moved,
   which is why a 27B model can run on a laptop or phone [4][11].

### Historical detour: Setun and balanced ternary

The user will enjoy this: ternary computing predates the transistor era's binary
orthodoxy. The **Setun**, built in 1958 at Moscow State University by a team under
Nikolay Brusentsov, was a working *balanced ternary* computer — digits `{-1, 0, +1}`,
exactly the modern LLM alphabet — implemented with ferrite cores and diodes. About 50
machines were built between 1959 and 1965, most of them installed in universities [12].
Balanced ternary has genuinely nice properties: negation is digit-wise, rounding is
truncation, and no separate sign bit is needed.

The classical argument for radix 3 is **radix economy**: for a fixed representable range,
the product (number of digits × symbols per digit) is minimized at base *e* ≈ 2.718, and 3
is the nearest integer [13]. The argument is contested for actual circuits — a 2019 analysis
argues R=3 is not optimal once real gate costs are modelled [14] — and, honestly, modern
ternary LLMs are *not* motivated by radix economy at all. They are motivated by (1) and (3)
above. Worth knowing so you can spot the bad version of the argument when it appears in
blog posts.

## Timeline

| Year | Work | What it added |
|---|---|---|
| 1958 | Setun (Brusentsov) [12] | Balanced-ternary hardware, `{-1,0,+1}` digits |
| 2013 | Straight-through estimator (Bengio, Léonard, Courville) [8] | Makes training through a rounding step possible |
| 2016 | Ternary Weight Networks (Li, Liu, Zhang et al.) [9] | Threshold-based ternarization + scale; ~16× compression |
| 2016 | Trained Ternary Quantization (Zhu, Han, Mao, Dally) [10] | *Learned* asymmetric scales; ≈no loss on ResNet/AlexNet |
| 2023 | BitNet (Wang, Ma, Dong et al.) [15] | `BitLinear`: 1-bit weights trained from scratch *at LLM scale*; a scaling law |
| 2024 | BitNet b1.58 (Ma, Wang, Ma et al.) [1] | Ternary `{-1,0,+1}` + absmean; matches fp16 LLaMA at 3B; coins "1.58-bit" |
| 2024 | MatMul-free LM (Zhu et al.) [16] | Removes *all* matmuls (ternary weights + element-wise ops); FPGA at 13 W |
| 2024 | Spectra / TriLM (Kaushal et al.) [6] | First open suite, 99M–3.9B, trained 300B tokens; TriLM 3.9B ≈ FloatLM 3.9B |
| 2024 | BitNet a4.8 [17] | 4-bit *activations* via hybrid quantization + sparsification |
| 2025 | BitNet b1.58 2B4T [7] | First open native ternary model at 2B/4T tokens; 0.4 GB, 29 ms/token on a laptop CPU |
| 2025 | `bitnet.cpp` [2] | I2_S / TL1 / TL2 kernels; up to 6.25× over fp baselines on CPU |
| 2025 | BitNet v2 [18] | Hadamard rotation kills activation outliers → native 4-bit activations |
| 2025 | ParetoQ (Liu et al.) [19] | Unified 1/1.58/2/3/4-bit comparison; a sharp representation shift between 2 and 3 bits |
| 2025 | TerEffic [20], TeLLMe [21] | FPGA ternary accelerators (prefill + decode) |
| 2025 | Falcon-Edge / Falcon3-1.58bit (TII) [22] | Ternary *fine-tuning* from a bf16 checkpoint; `onebitllms` toolkit |
| 2026 | Sparse-BitNet [23] | ~42% of a trained BitNet's weights are already zero; adds N:M sparsity on top |
| 2026 | CAT-Q (Intel Labs) [24] | Ternary **PTQ** that beats BitNet-QAT with 512 calibration samples (~10⁵× fewer tokens) |
| 2026 | Bonsai 27B (PrismML) [4], Maple 20B-A1B (DeepGrove) [5], BitCPM-CANN (OpenBMB) [25] | Ternary at 20–27B; MoE reasoning; NPU-native ternary training |
| 2026 | BITCOS (Georganas, Heinecke, Dubey, Intel) [26] | Exploits the *zero density* to get below the 1.585-bit "barrier" |

## How they are trained

The mechanical problem: rounding has zero gradient almost everywhere, so you cannot
backpropagate through it. The standard fix is the **straight-through estimator** [8]: keep a
shadow copy of high-precision "latent" weights, quantize them in the forward pass, and in
the backward pass pretend the quantizer was the identity function. Gradients accumulate in
the latent weights; the discrete weights follow.

BitNet b1.58's quantizer is deliberately simple [1][7]:

```
scale γ = mean(|W|)                  # per weight matrix (or per group of 128)
W_ternary = clip(round(W / γ), -1, +1)
```

Activations are quantized separately, to 8-bit integers with a per-token absmax scale in
b1.58 [7]; a4.8 [17] and v2 [18] push activations to 4 bits, v2 by first applying an online
Hadamard transform so the outlier-heavy activation distribution becomes roughly Gaussian.

Two regimes now coexist:

- **QAT / native training** (BitNet, TriLM, Bonsai, Maple, BitCPM): highest quality, but you
  pay full pretraining cost. Known instability — "deadzone-trapped" weights that never
  leave 0 — is addressed by Tequila [27, *not independently verified*].
- **PTQ** (CAT-Q [24], TWLA [28, *not independently verified*]): quantize a finished model
  with a small calibration set. Until 2026 PTQ below ~2 bits lost badly; CAT-Q reports
  ternary PTQ of 1.7B–8B models beating BitNet b1.58 v1/v2 trained on 100B tokens, and
  quantizing 14B–235B models in 8–60 GPU-hours [24]. If this holds up it removes the main
  practical objection to ternary (you no longer need to pretrain from scratch).

## Accuracy versus full precision

- **BitNet b1.58 2B4T** (2B params, 4T tokens) scores an average of 54.19 across a standard
  benchmark suite vs 55.23 for fp Qwen2.5-1.5B, 44.90 for LLaMA-3.2-1B and 43.74 for
  Gemma-3-1B — i.e. competitive with full-precision peers of its size, at 0.4 GB
  non-embedding memory, 29 ms/token on a 13th-gen Intel i7 and ~0.028 J/token [7].
- **Spectra/TriLM** [6]: above ~1B parameters, ternary models trained from scratch beat both
  post-training-quantized and float models *at equal bit budget*; TriLM 3.9B matches
  FloatLM 3.9B on their benchmarks while having fewer bits than FloatLM 830M.
- **ParetoQ** [19]: a careful controlled comparison finds a qualitative transition between
  2 and 3 bits — at ≥3 bits a fine-tuned model stays near its pretrained distribution, at
  ≤2 bits the representation is rebuilt. Ternary/2-bit/3-bit sit on roughly the same
  accuracy-per-byte frontier and beat both binary and 4-bit.
- **2026 scale-up**: Bonsai 27B (a ternary build of Qwen3.6-27B) reports retaining ~95% of
  full-precision quality at 5.9 GB [4]; Maple-Preview is a 20B-A1B ternary MoE reasoning
  model reporting AIME-2026 87.5% and running 200+ tok/s on a Mac mini M4 [5]. These are
  vendor numbers from model cards and press, not peer-reviewed results — treat with the
  usual caution, but they are independently listed as deployed checkpoints in [26].

## Efficiency: how the trits are actually stored

This is the subject of the paper that started this investigation, so it is worth being
precise. Ternary's information-theoretic floor is log₂3 = 1.585 bpw. Real formats:

| Format | bpw | Idea |
|---|---|---|
| 2-bit (I2_S, `Q2_0`, LIBXSMM/XeTLA int2) | 2.0 | One trit per 2-bit field; simple, vectorizes well |
| Five-trit packing (`TQ1_0` in `llama.cpp`) | 1.6 → 1.625 deployed | 3⁵ = 243 ≤ 256, so five trits fit in a byte; but a 128-weight block needs ⌈128/5⌉ = 26 bytes → 1.625 bpw [26] |
| `TQ2_0` (`llama.cpp`) | 2.0625 | 2 bits per weight + block scale |
| BITCOS [26] | **2 − z** | Presence bitmap (1 bit/weight) + compacted sign vector (1 bit per *non-zero*) |

**The zeros are the point.** Georganas, Heinecke and Dubey measured the symbol distribution
of 29 state-of-the-art ternary checkpoints (BitNet, Bonsai, CAT-Q-Qwen3, ParetoQ, TriLM,
Maple, BitCPM-CANN) and found zero density z ranging from **29.7% to 51.5%** — the three
symbols are *not* equiprobable [26]. Their BITCOS layout costs 2 − z bits per weight, which
beats five-trit packing whenever z > 0.375 (26 of the 29 models) and reaches 1.485 bpw on
the sparsest. Measured end to end inside vLLM, decode throughput improves 1.10–1.18× on a
64-core Emerald Rapids CPU, 1.02–1.15× on a 24-core client CPU, and 1.02–1.27× on Intel Xe2
GPUs. See [[Paper - Breaking the 1.58-bit Barrier]] for the detailed reading.

Why are the zeros there at all? Sparse-BitNet observes the same phenomenon (~42% zeros in a
pretrained BitNet) and calls the weight histogram a "quantization valley": the absmean
threshold sends everything small to 0, and the latent weight distribution is peaked at 0
[23]. So "up to 51.5% zeros" is a fact about the *quantizer plus the weight distribution*,
not a deep property of language.

**Kernels and runtimes.** `bitnet.cpp` [2] introduced I2_S (int2 + scale, lossless) and the
Ternary Lookup Table kernels TL1/TL2, reporting up to 6.25× over full-precision and 2.32×
over other low-bit baselines on CPU. Table-lookup GEMM has its own lineage (T-MAC, LUT-NN,
TernGEMM, TABv2 [29–32, *cited in [26], not independently verified*]). `llama.cpp` ships
TQ1_0/TQ2_0 [33], and 2026 pull requests add CUDA TQ2_0 and further ternary formats. Intel's
LIBXSMM/XeTLA int2 kernels are the strongest published CPU/GPU baseline [26].

**Hardware.** Ternary is a natural ASIC/FPGA target because the multiplier array disappears.
TerEffic [20] deploys a 1.3B ternary model on an Alveo U280 at ~1400 tok/s; TeLLMe [21] and
TeLLMe v2 [34] do prefill *and* decode on a low-power edge FPGA (AMD KV260) with table-lookup
ternary matmul; the MatMul-free LM paper [16] runs a billion-parameter model at 13 W on
custom FPGA logic. No commercial ternary-native ASIC exists yet, which is the field's
standing "if this format survives, the silicon follows" bet.

## Open problems (as of September 2026)

1. **Does ternary hold at frontier scale?** Everything published is ≤27B, mostly ≤8B.
   No ternary model competes with a frontier full-precision model.
2. **PTQ vs QAT.** If CAT-Q-style PTQ [24] really matches QAT, ternary becomes a deployment
   choice rather than a pretraining commitment. Independent replication is the open question.
3. **Activations, not weights, are now the bottleneck.** Weights are at ~1.5 bpw; activations
   are at 8 or 4 bits and full of outliers. BitNet v2's Hadamard trick [18] is the current
   answer; whether 4-bit (or lower) activations are stable at scale is open.
4. **Structured vs unstructured zeros.** BITCOS exploits the zeros a trained model *already
   has* [26]; Sparse-BitNet [23] and Sherry [35, *not independently verified*] instead *force*
   a sparsity pattern (N:M, or exactly one zero per block of four) and pay 0.17–3.8 points of
   accuracy for hardware-friendliness. Which side wins is unsettled.
5. **Training instability / dead zones.** Weights trapped at 0 by the absmean threshold;
   partially addressed [27] but not solved.
6. **No theory of why ternary suffices.** There is no account of *which* computations survive
   ternarization and which do not. This is the gap that makes the Collatz proposals in
   [[Research Directions - Ternary Nets x Collatz]] interesting: an exactly-known arithmetic
   target is a place where the question can actually be answered.

## Sources

1. Ma, S., Wang, H., Ma, L., Wang, L., Wang, W., Huang, S., Dong, L., Wang, R., Xue, J., Wei, F. — *The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits* (2024). https://arxiv.org/abs/2402.17764
2. Wang, J., Zhou, T., Song, S., Xia, T., Cao, T., Wei, S., Ma, S., Wang, H., Wei, F. — *Bitnet.cpp: Efficient Edge Inference for Ternary LLMs*, ACL 2025 (2025). https://arxiv.org/abs/2502.11880
3. Microsoft BitNet repository — https://github.com/microsoft/BitNet
4. PrismML — *Bonsai 27B: 1-bit and ternary builds of Qwen3.6-27B* (2026). https://prismml.com/news/prismml-releases-bonsai-27b and https://huggingface.co/prism-ml/Ternary-Bonsai-27B-gguf
5. DeepGrove — *Maple-Preview: a 20B-A1B ternary-weight reasoning MoE* (2026). https://huggingface.co/deepgrove/maple-preview
6. Kaushal, A., Vaidhya, T., Mondal, A. K., Pandey, T., Bhagat, A., Rish, I. — *Spectra: Surprising Effectiveness of Pretraining Ternary Language Models at Scale*, ICLR 2025 (2024). https://arxiv.org/abs/2407.12327
7. Ma, S., Wang, H., Huang, S., Zhang, X., Hu, Y., Song, T., Xia, Y., Wei, F. — *BitNet b1.58 2B4T Technical Report* (2025). https://arxiv.org/abs/2504.12285
8. Bengio, Y., Léonard, N., Courville, A. — *Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation* (2013). https://arxiv.org/abs/1308.3432
9. Li, F., Liu, B., Wang, X., Zhang, B., Yan, J. — *Ternary Weight Networks* (2016; later revisions add authors). https://arxiv.org/abs/1605.04711
10. Zhu, C., Han, S., Mao, H., Dally, W. J. — *Trained Ternary Quantization*, ICLR 2017 (2016). https://arxiv.org/abs/1612.01064
11. Belcak, P., Heinrich, G., Diao, S., Fu, Y., Dong, X., Muralidharan, S., Lin, Y. C., Molchanov, P. — *Small Language Models are the Future of Agentic AI* (2025). https://arxiv.org/abs/2506.02153
12. *Setun* (balanced ternary computer, Brusentsov, Moscow State University, 1958). https://en.wikipedia.org/wiki/Setun and https://www.computer-museum.ru/english/setun.htm
13. Georgiou, H. V. — *On the optimality of ternary arithmetic for compactness and hardware design* (2016). https://arxiv.org/abs/1611.03715
14. *Ternary circuits: why R=3 is not the Optimal Radix for Computation* (2019). https://arxiv.org/abs/1908.06841
15. Wang, H., Ma, S., Dong, L., Huang, S., Wang, H., Ma, L., Yang, F., Wang, R., Wu, Y., Wei, F. — *BitNet: Scaling 1-bit Transformers for Large Language Models* (2023). https://arxiv.org/abs/2310.11453
16. Zhu, R.-J., Zhang, Y., Sifferman, E., Sheaves, T., Wang, Y., Richmond, D., Zhou, P., Eshraghian, J. K. — *Scalable MatMul-free Language Modeling* (2024). https://arxiv.org/abs/2406.02528
17. Wang, H., Ma, S., Wei, F. — *BitNet a4.8: 4-bit Activations for 1-bit LLMs* (2024). https://arxiv.org/abs/2411.04965
18. Wang, H., Ma, S., Wei, F. — *BitNet v2: Native 4-bit Activations with Hadamard Transformation for 1-bit LLMs* (2025). https://arxiv.org/abs/2504.18415
19. Liu, Z., Zhao, C., Huang, R., Chen, S., Zhang, J., Zhao, S., Li, R., Xiong, Y. et al. — *ParetoQ: Improving Scaling Laws in Extremely Low-bit LLM Quantization* (2025). https://arxiv.org/abs/2502.02631
20. *TerEffic: Highly Efficient Ternary LLM Inference on FPGA* (2025). https://arxiv.org/abs/2502.16473
21. Qiao et al. — *TeLLMe: An Energy-Efficient Ternary LLM Accelerator for Prefilling and Decoding on Edge FPGAs* (2025). https://arxiv.org/abs/2504.16266
22. TII — *Falcon-Edge: powerful, universal, fine-tunable 1.58-bit language models* (2025). https://huggingface.co/blog/tiiuae/falcon-edge
23. Zhang, D., Wu, X., Huang, S., Wang, Y., Hao, H., Shao, Y., Chi, Z., Dong, L., Song, T., Xia, Y., Sui, Z., Wei, F. — *Sparse-BitNet: 1.58-bit LLMs are Naturally Friendly to Semi-Structured Sparsity* (2026). https://arxiv.org/abs/2603.05168
24. Wang, S., Li, C., Kang, Y., Fan, J., Yao, A. — *CAT-Q: Cost-efficient and Accurate Ternary Quantization for LLMs*, ICML 2026 (2026). https://arxiv.org/abs/2606.26650
25. OpenBMB — *BitCPM-CANN: full-pipeline ternary quantized models trained on CANN* (2025–26). https://huggingface.co/collections/openbmb/bitcpm-cann
26. Georganas, E., Heinecke, A., Dubey, P. — *Breaking the 1.58-bit Barrier for Ternary LLMs* (Intel, 14 Sep 2026). https://arxiv.org/abs/2609.16338
27. Huang, J., Wu, D., Wu, R., Cen, G., Yu, Z., Li, X., Liu, J., Zhou, P., Chen, X., Liu, D. Wu — *Tequila: Trapping-free ternary quantization for large language models* (2025), arXiv:2509.23809 — *cited in [26]; not independently verified.*
28. Zhao, Z., Xu, Z., Chen, X., Hu, Z., Jiang, D., Yang, D. — *TWLA: Achieving ternary weights and low-bit activations for LLMs via post-training quantization*, ICML 2026, arXiv:2606.13054 — *cited in [26]; not independently verified.*
29. Wei, J., Cao, S., Cao, T., Ma, L., Wang, L., Zhang, Y., Yang, M. — *T-MAC: CPU renaissance via table lookup for low-bit LLM deployment on edge*, EuroSys 2025 — *cited in [26]; not independently verified.*
30. Tang, X. et al. — *LUT-NN: Empower efficient neural network inference with centroid learning and table lookup*, MobiCom 2023 — *cited in [26]; not independently verified.*
31. Choi, S., Shim, K., Choi, J., Sung, W., Shim, B. — *TernGEMM: General matrix multiply library with ternary weights for fast DNN inference*, SiPS 2021 — *cited in [26]; not independently verified.*
32. Fu, G., Fischer, O., Zhu, S., Alonso, G. — *TABv2: A faster ternary and binary neural network inference library on the edge*, IEEE TVLSI 2026 — *cited in [26]; not independently verified.*
33. `llama.cpp` quantization formats TQ1_0 (1.6875 bpw, five trits/byte) and TQ2_0 (2.0625 bpw). https://github.com/ggml-org/llama.cpp
34. *TeLLMe v2: An Efficient End-to-End Ternary LLM Prefill and Decode Accelerator with Table-Lookup Matmul on Edge FPGAs* (2025). https://arxiv.org/abs/2510.15926
35. Huang, H., Wu, D., Hu, Q., Yu, G., Yang, J., Zhu, J., Liu, X., Wu, D. — *Sherry: Hardware-efficient 1.25-bit ternary quantization via fine-grained sparsification*, arXiv:2601.07892 — *cited in [26]; not independently verified.*
