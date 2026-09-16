---
tags: [log2-3, continued-fractions, three-distance, packing, information-theory]
status: complete
created: 2026-09-16
---

# Trit Packing and $\log_2 3$

The arithmetic underneath [[Paper - Breaking the 1.58-bit Barrier]]: which
$(t, b)$ pairs pack $t$ trits into $b$ bits efficiently, why the answer is the
continued fraction of $\log_2 3$, and where the same numbers already appear in
the Collatz work (`docs/Explorations/Dropping Zeta Spectrum.md` Part 6) and in
music (`docs/Conjectures/Eisenstein Factorization.md`, the Pythagorean comma).

Scripts: `research/investigate-ternary-llms/scripts/packing_records.py`
(exact integer / 120-digit mpmath; no float decides anything),
`research/investigate-ternary-llms/scripts/entropy_bitcos.py`.

## 1. The packing condition

$t$ trits fit in $b$ bits iff there is an injection $\{0,1,2\}^t \to \{0,1\}^b$,
i.e. iff

$$3^t \le 2^b \iff b \ge \lceil t \log_2 3 \rceil = \operatorname{bitlen}(3^t)$$

($3^t$ is never a power of two, so ceiling and bit-length agree for $t \ge 1$.)
Write $b(t) = \lceil t\log_2 3\rceil$ and the **waste**

$$w(t) = b(t) - t\log_2 3 = 1 - \{t \log_2 3\} \in (0, 1).$$

Rate $b(t)/t \to \log_2 3$; the whole design space is the Diophantine
approximation of $\log_2 3$ from **above**.

## 2. Continued fraction (verified)

$$\log_2 3 = 1.5849625007211561814537\ldots = [1; 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55, 1, 4, 3, 1, 1, \ldots]$$

confirming the expansion quoted in `docs/Explorations/Dropping Zeta Spectrum.md`.
Convergents alternate below/above:

| $k$ | $p/q$ | value | side |
|---|---|---|---|
| 0 | 1/1 | 1.0 | below |
| 1 | 2/1 | 2.0 | **above** |
| 2 | 3/2 | 1.5 | below |
| 3 | 8/5 | 1.6 | **above** |
| 4 | 19/12 | 1.58333 | below |
| 5 | 65/41 | 1.5853659 | **above** |
| 6 | 84/53 | 1.5849057 | below |
| 7 | 485/306 | 1.58496732 | **above** |
| 8 | 1054/665 | 1.584962406 | below |
| 9 | 24727/15601 | 1.5849625024 | **above** |

Only the **upper** ones are packings. Note in particular: $1054/665$ is *below*
$\log_2 3$, so 665 trits do **not** fit in 1054 bits ($3^{665}/2^{1054} =
1.0000437 > 1$). The musically famous denominators 12, 53, 665 are all *lower*
approximants — they are the **overflow** cases, not the packings.

## 3. Record-efficient packings (verified)

A pair $(t, b(t))$ is a *record* if $b(t)/t$ is strictly smaller than for every
smaller $t$. Computed exactly for $t \le 20\,000$:

| $t$ | $b$ | bits/trit | waste $w(t)$ | note |
|---|---|---|---|---|
| 1 | 2 | 2.0 | 0.4150 | the 2-bit format (`I2_S`, `TQ2_0`) |
| 3 | 5 | 1.6667 | 0.2451 | **bitnet.cpp `TL2`**: 3 weights → 5 bits [4] |
| 5 | 8 | 1.6 | 0.07519 | five trits per byte (`TQ1_0`, the paper's baseline) |
| 17 | 27 | 1.58824 | 0.05564 | |
| 29 | 46 | 1.58621 | 0.03609 | |
| 41 | 65 | 1.585366 | 0.016537 | |
| 94 | 149 | 1.585106 | 0.013525 | |
| 147 | 233 | 1.585034 | 0.010512 | |
| 200 | 317 | 1.585 | 0.0075 | |
| 253 | 401 | 1.584980 | 0.004487 | |
| 306 | 485 | 1.5849673 | 0.0014748 | |
| 971 | 1539 | 1.5849640 | 0.0014118 | |
| … | | | | then 1636, 2301, 2966, … (step 665) |
| 15601 | 24727 | 1.58496250 | 2.62e-5 | |

**Theorem (verified numerically for $t \le 20\,000$, and standard in
one-sided-approximation theory).** The record pairs are *exactly* the upper best
approximations of $\log_2 3$: the upper convergents together with the
semiconvergents $\frac{p_{k-1}+jp_k}{q_{k-1}+jq_k}$ lying above $\log_2 3$. The
script checks set equality in both directions — no record fails to be an upper
semiconvergent and no upper semiconvergent fails to be a record.

The record denominators $1, 3, 5, 17, 29, 41, 94, 147, 200, 253, 306, 971, \ldots$
are a sub-sequence of **OEIS A206788**, "denominators of semiconvergents to
$\log_2 3$", whose own gloss is *"equal divisions of the octave that have good
approximations of the 3rd harmonic"* [5]. Packing trits into bits and choosing an
equal-tempered scale are the same optimisation.

### Three Distance / Sturmian reading

$w(t) = 1 - \{t\alpha\}$, $\alpha = \log_2 3$. Record packings are exactly the
$t$ at which $\{t\alpha\}$ sets a record *close to 1 from below* — the left
endpoint neighbours of 0 in the Three Distance Theorem partition of the circle by
$\{\alpha\}, \{2\alpha\}, \ldots, \{N\alpha\}$ (the same machinery as
`docs/Explorations/Dropping Zeta Spectrum.md` Part 6). Consequently:

- The increments $b(t+1) - b(t) \in \{1, 2\}$ form the **Sturmian cutting
  sequence** of slope $\log_2 3$:
  $2,1,2,1,2,2,1,2,1,2,2,1,2,1,2,1,2,2,1,\ldots$ (OEIS A022921 territory), i.e.
  *"how many bits the next trit costs"* is a Sturmian word. It is the same word
  that governs the dropping-set sign rule in Part 4 of the Dropping Zeta note.
- Waste is never $\ge 1$ (trivially) and record waste decays like $1/t$ along
  best approximants, so there is no finite packing that reaches $\log_2 3$ —
  the barrier is approached but never attained by any fixed-size block code.

## 4. Fixed registers and fixed blocks

What hardware actually faces: either a $b$-bit register (maximise $t$) or an
$n$-weight block (minimise bytes).

| register | max trits | bits/weight | slack |
|---|---|---|---|
| 8 | 5 | 1.6 | 0.075 bits |
| 16 | 10 | 1.6 | 0.150 |
| 32 | 20 | 1.6 | 0.301 |
| 64 | 40 | 1.6 | 0.602 |
| 128 | 80 | 1.6 | 1.203 |
| 256 | 161 | 1.5901 | 0.821 |
| 512 | 323 | 1.58514 | 0.057 |

Byte-sized registers are stuck at 1.6 up to 128 bits because $5 | 80$; a 512-bit
vector register (AVX-512, one `zmm`) holds **323 trits at 1.58514 bpw**, within
0.06 bits of a whole 512-bit word of the $\log_2 3$ bound. That is the natural
"SIMD-native" packing nobody in the surveyed formats uses.

Block side (the paper's case):

| $n$ | min bits | min bytes | 5-trit bytes | bpw (optimal) | bpw (byte-aligned) | bpw (5-trit) |
|---|---|---|---|---|---|---|
| 32 | 51 | 7 | 7 | 1.59375 | 1.7500 | 1.7500 |
| 64 | 102 | 13 | 13 | 1.59375 | 1.6250 | 1.6250 |
| **128** | **203** | **26** | **26** | 1.58594 | **1.6250** | **1.6250** |
| 256 | 406 | 51 | 52 | 1.58594 | 1.5938 | 1.6250 |
| 512 | 812 | 102 | 103 | 1.58594 | 1.5938 | 1.6094 |
| 1024 | 1624 | 203 | 205 | 1.58594 | 1.5859 | 1.6016 |

**Verified:** for $n = 128$, $\lceil 128\log_2 3\rceil = 203$ bits $= 25.375$
bytes $\to 26$ bytes. The five-trit packing's 26 bytes is therefore *optimal
among byte-aligned layouts*; the paper's 1.625 bpw baseline cannot be improved by
any cleverer trit packing at that block size. The excess over $\log_2 3$ at 128 is
$5.1$ bits per block, of which only $0.13$ bits is packing waste and $5.0$ bits is
byte padding. At $n = 256$ optimal-byte-aligned (51 bytes) finally beats five-trit
(52 bytes) — a free 0.031 bpw nobody collects.

## 5. Deployed formats, rated

| format | packing | bpw | comment |
|---|---|---|---|
| `I2_S` (bitnet.cpp) | 1 trit / 2 bits | 2.0 | record pair $(1,2)$ |
| `TL1` (bitnet.cpp) | 2 trits / 4-bit LUT index | 2.0 | $3^2 = 9 \le 16$, not a record |
| `TL2` (bitnet.cpp) | 3 trits / 5 bits (1 sign + 4 index, mirror-folded $3^3/2 = 13.5 \le 16$) | 1.667 | record pair $(3,5)$ [4] |
| `TQ2_0` (llama.cpp) | 2-bit + fp16 per 256 | 2.0625 | |
| `TQ1_0` (llama.cpp) | 240 trits at 5/byte + 16 trits at 4/byte + fp16 | 1.6875 | see below [2] |
| `STQ1_0` (PR #22836) | 4-bit codebook + 1-bit signs, power-of-two groups | between the two | SIMD-friendlier than `TQ1_0` [3] |
| BITCOS | bitmap + compacted signs | $2 - z$ | data-dependent, not a fixed packing |
| Setun (1958) | 2 ferrite cores / trit | 2.0 | historical: the $(1,2)$ packing in hardware [6] |

`TQ1_0` arithmetic (verified from `ggml-common.h`): `qs[(256 - 16)/5] = 48` bytes
hold 240 trits at 5/byte, `qh[4]` holds the remaining 16 trits at only **4 per
byte** ($3^4 = 81 \le 256$, wasting 2 bits/trit), plus a 16-bit scale:
$(48 \cdot 8 + 4\cdot 8 + 16)/256 = 432/256 = 1.6875$ bpw — matching the comment
in the header. The remainder handling, not the packing, costs 0.09 bpw.

## 6. The same integers, in music (verified)

$3^t$ vs $2^b$ *is* the comma problem: a stack of $t$ fifths against $b$ octaves.

| $t$ | $b$ | $3^t/2^b$ | packing verdict | musical name |
|---|---|---|---|---|
| 5 | 8 | 0.94921875 | fits (1.6 bpw) | inverse of the **Pythagorean limma** 256/243 |
| 12 | 19 | 1.0136433 | **overflows** | the **Pythagorean comma** |
| 41 | 65 | 0.9886025 | fits (1.58537) | 41-EDO |
| 53 | 84 | 1.0020903 | **overflows** | **Mercator's comma** |
| 306 | 485 | 0.9989783 | fits (1.5849673) | 306-EDO |
| 665 | 1054 | 1.0000437 | **overflows** | 665-EDO (the classic "almost exact" one) |

So the Pythagorean comma is precisely the statement *"12 trits do not fit in 19
bits"*, and the five-trit byte is precisely *"the limma is the slack left when 5
fifths are folded into 8 octaves"*. The repo's period-12 Eisenstein structure and
the comma $3^{12}/2^{19}$ are therefore on the *overflow* side of this ledger —
worth keeping straight when reading the analogy in
[[Collatz Bridge - Trits and Stopping Times]].

## 7. Known-results check

- Trit packing itself is folklore/engineering, not a research literature: the
  $3^5 \le 2^8$ fact is stated in the llama.cpp source comment [2] and in the
  BITCOS paper [1]; `TL2`'s $(3,5)$ packing in [4]; the Setun used two cores per
  trit, i.e. the $(1,2)$ packing, despite balanced ternary's $\log_2 3$ argument
  [6].
- The *mathematics* is classical one-sided Diophantine approximation plus the
  Three Distance Theorem; A206788 [5] already records the semiconvergent
  denominators with the musical gloss.
- No source found that states the "records = upper semiconvergents" fact in the
  trit-packing language, nor that computes the 512-bit/323-trit packing. Neither
  is deep, but neither is written down in the ML-systems literature.

## Sources

1. E. Georganas, A. Heinecke, P. Dubey, "Breaking the 1.58-bit Barrier for Ternary LLMs", arXiv:2609.16338v1 — https://arxiv.org/html/2609.16338v1
2. llama.cpp `ggml/src/ggml-common.h` (`block_tq1_0`, `block_tq2_0`) — https://raw.githubusercontent.com/ggml-org/llama.cpp/master/ggml/src/ggml-common.h
3. ggml-org/llama.cpp PR #22836, "add STQ1_0 ternary quantization" — https://github.com/ggml-org/llama.cpp/pull/22836
4. J. Wang et al., "Bitnet.cpp: Efficient Edge Inference for Ternary LLMs", arXiv:2502.11880 — https://arxiv.org/html/2502.11880v1
5. OEIS A206788, "Denominators of semiconvergents to log_2(3)" — https://oeis.org/A206788
6. Russian Virtual Computer Museum, "Development of ternary computers at Moscow State University" (Setun; two ferrite cores per trit) — https://www.computer-museum.ru/english/setun.htm
7. OEIS A020914, "Number of digits in base-2 representation of 3^n" ($=\lceil n\log_2 3\rceil$) — https://oeis.org/A020914
