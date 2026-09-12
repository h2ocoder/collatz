# Density Exponent

**Date:** 2026-09-10
**Spec:** [design](../superpowers/specs/2026-09-10-density-exponent-design.md) · **Script:** `scripts/density_exponent_kl.py` · **Context:** [[2026-09-10-proof-direction-assessment]]

**Question.** How large a $\theta$ can be proved in $\pi_a(x) = \#\{n \le x : n \to a\} \ge x^{\theta}$? The record, $\theta = 0.84$, is Krasikov–Lagarias (2003), from a linear program $L_k^{NT}(\lambda)$ on residue classes mod $3^k$ that they solved up to $k=11$. Two things were tested: (A) does the repo's dropping-set alphabet give a stronger inequality system? (B) what happens to the *same* KL system for $k>11$?

## Result

| $k$ | classes $3^k$ | KL $\gamma_k$ (this run) | KL published | certified $\gamma'$ (exact) | DROP $\gamma_k$ |
|---:|---:|---:|---:|---:|---:|
| 2 | 9 | 0.436588 | 0.436588 | | — |
| 5 | 243 | 0.733580 | 0.733579 | | 0.645741 |
| 7 | 2,187 | 0.782569 | | | 0.749072 |
| 9 | 19,683 | 0.816831 | 0.816830 | | 0.796413 |
| 10 | 59,049 | 0.829546 | | | 0.813044 |
| 11 | 177,147 | 0.841757 | 0.841756 | 0.841676 | |
| 12 | 531,441 | **0.853136** | — | **0.853057** | |
| 13 | 1,594,323 | **0.863006** | — | **0.862927** | |
| 14 | 4,782,969 | **0.872452** | — | **0.872373** | |
| 15 | 14,348,907 | **0.881248** | — | **0.881170** | |
| 16 | 43,046,721 | **0.889267** | — | **0.889189** | |
| 17 | 129,140,163 | **0.896612** | — | **0.896535** | |
| 18 | 387,420,489 | **0.903289** | — | **0.903212** | |

- **Reproduction.** The power-iteration/bisection solver matches the published Table 2 to six decimals at $k = 2, 5, 9, 11$, so the system implemented is theirs.
- **(A) DROP is weaker.** At every $k \ge 3$ the dropping-word system gives a smaller exponent than KL at the same modulus (0.813 vs 0.830 at $k=10$, words with $s \le 9$). This was predicted: KL's nested min-of-sums dominates DROP's sum-of-mins. The one structural advantage of DROP — no advanced terms, so the induction on height is direct — does not translate into a better exponent. **Negative result; the dropping-set basis does not help here.**
- **(B) Pushing $k$ works.** The KL system is a monotone homogeneous map, so its feasibility threshold is a nonlinear Perron root and costs $O(3^k)$ per iteration instead of an LP. $k=12$ to $18$ each add about $0.01$ ($k=18$: 387M classes, 48 min with the memory-lean `kl_system_lean`, ~6 GB; the eigenvector file is 1.5 GB). Each new level has an **exact certificate**: a positive integer vector $C$ with $C \le M_{\lambda'}(C)$ verified in `int64` arithmetic with floored 60-digit lower bounds for the coefficients, at $\lambda' = \lambda_k - 10^{-4}$. By KL Theorem 2.2, feasibility of $L_k^{NT}(\lambda')$ gives $\pi_a(x) \ge x^{\log_2\lambda'}$ for $a \not\equiv 0 \pmod 3$ and $x \ge x_0(a)$.

**Consequently (subject to the correctness of KL Theorem 2.2 as applied to its own system at larger $k$):**
$$\pi_a(x) \ \ge\ x^{0.903} \quad\text{for all sufficiently large } x,\ a \not\equiv 0 \pmod 3,$$
improving $x^{0.84}$. The increments $\gamma_{k+1}-\gamma_k$ are $0.0114, 0.0099, 0.0094, 0.0088, 0.0080, 0.0073, 0.0067$ for $k = 11\to 18$.

## The geometric law

The gap to $\lambda=2$ shrinks by a constant factor per level:

| $k$ | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
|---|---|---|---|---|---|---|---|---|---|---|
| $(2-\lambda_k)/(2-\lambda_{k-1})$ | 0.935 | 0.935 | 0.932 | 0.932 | 0.936 | 0.934 | 0.934 | 0.935 | 0.936 | 0.938 |

Fit on $k=11..16$: $2-\lambda_k \approx 0.439\cdot 0.9342^k$, which **predicted $\lambda_{17} = 1.86202$ before the $k=17$ run; observed $1.86169$** (the residual $3\times10^{-4}$ is a slow drift of the ratio, not a break). If the law holds, $\lambda_k \to 2$ geometrically and $\gamma_k \to 1$: predicted $\gamma_{20} \approx 0.917$, $\gamma_{30} \approx 0.958$, $\gamma_{50} \approx 0.989$. **Conjecture:** $\lim_k \lambda_k = 2$, hence $\pi_a(x) \ge x^{1-\varepsilon}$ for every $\varepsilon>0$. Krasikov–Lagarias state this consequence and leave the limit open.

*Monotonicity is easy:* lifting a feasible level-$k$ solution to level $k+1$ as a function constant on the three lifts of each class turns every min-over-lifts into the value itself, so every right-hand side can only increase; hence $\lambda_{k+1} \ge \lambda_k$. The open content is the *rate*. A geometric rate suggests each extra 3-adic digit recovers a fixed fraction of the remaining loss on the odd branch; a construction of near-feasible solutions with $2-\lambda \le C\rho^k$ would be a theorem.

## Why nobody did this since 2003

KL solved $L_k^{NT}$ as a linear program (2·3^{k-1} principal variables plus auxiliaries), and their eliminated system $L_k^{EL}$ was infeasible beyond $k=5$. The NT system at $k=11$ has 118,098 variables; that was the practical LP limit at the time and the paper gives no reason for stopping there beyond size. The observation used here — that the LP's feasibility is exactly "nonlinear Perron root $\ge 1$" for the min-plus/linear map, computable by power iteration in $O(3^k)$ memory — makes $k=16$ a laptop computation. The exact certificate makes the result checkable without trusting floating point.

## Honest caveats

1. The claim rests on Theorem 2.2 of Krasikov–Lagarias. Its proof (their §3–5: back-substitution eliminates the advanced term $y+\alpha-1$ into a retarded system $\mathcal{I}_k(EL)$ by Theorems 3.1–3.2; Theorem 4.1 transfers LP feasibility with the auxiliaries set to the min over lifts, which is exactly the choice used here; Theorem 5.1 then gives $\phi \ge \Delta c\lambda^y$ by induction on $y$) is generic in $k$ and uses no numerical input — the only computation in the paper is the LP itself, for $k\le 11$. So the certificate at level $k$ inherits precisely the paper's rigor. I have not independently re-verified their §3–5.
2. $x_0(a)$ is ineffective in the same way as in KL.
3. This is progress on the density side, not on convergence of every $n$; it sits below Tao's "almost all" result in strength but is a different statement (integers reaching $1$, not "almost bounded values").

## Reproduce

```bash
.venv/bin/python scripts/density_exponent_kl.py 10 9          # KL vs DROP table to k=10
.venv/bin/python scripts/density_exponent_kl.py certify 13 1.818824   # exact certificate at k=13
```
Eigenvectors for the certified levels are in `data/kl_eigvec_k{k}.npy`.

## Related

[[Nested Dropping Sets]] (the alphabet that DROP uses) · [[Affine Orbit Structure]] · [[Lens C - Implication Catalog]] (#9, "density refinement", previously marked *do not pursue*: it is the one that moved)

## Mechanism (attack on the rate, 2026-09-10 evening)

**Scripts:** `scripts/kl_mechanism.py`, `scripts/kl_annealed.py`. The only pessimism in $L_k^{NT}$ is the min over the three lifts of the unknown top 3-adic digit; that digit decides an odd-branching only after $k$ odd steps down every path. So $2-\lambda_k$ is governed by how much the growth potential $c$ depends on its top digit. Findings:

1. **Both moments are critical at $\lambda=2$.** The annealed step operator (mean over lifts) has Perron root exactly 1 per odd generation, and because $2^{\alpha}=3$ the *squared-weight* operator does too: $(3/4)^2+(3/2)^2 = 3(1-1/16)$. A critical second moment rules out the naive CLT argument (which would give geometric decay of the lift-spread); it suggests polynomial decay instead.
2. **The annealed eigenvector's mean lift-spread decays like $3.5/k$** ($k\cdot$spread $= 3.4$–$3.6$ for $k=7..13$), and re-reading the $\lambda_k$ table the same way gives $k(2-\lambda_k) = 2.29, 2.32, 2.36, 2.37, 2.37, 2.36, 2.35$ for $k=11..17$. So **two laws fit**: geometric $0.437\cdot0.9345^k$ (residuals $\sim10^{-4}$) and $2.53/k - 2.57/k^2$ (residuals $\sim10^{-3}$). They predicted $\lambda_{18} = 1.87092$ vs $1.86716$; **the $k=18$ run gave $1.87033$: the $1/k$ law is rejected** (off by $3\times10^{-3}$), the geometric law holds to $6\times10^{-4}$, with the ratio drifting up slowly ($0.932\to0.938$ over $k=12..18$). The asymptotic rate is therefore geometric-or-slightly-slower; a pure power law is excluded in this range.
3. **The max lift-spread does not decay at all** (1.12 at every level). The worst classes are digits $222\ldots2$ (the 3-adic integer $-1$, fixed point of the odd route $(2a-1)/3$, i.e. the trivial *negative* cycle), and the periodic expansions $2020\ldots$, $2100\,2100\ldots$, $1212\ldots$ — the 3-adic points of the other negative cycles $(-5,\ldots)$, $(-17,\ldots)$. Near those points the backward tree has a long spine of odd steps each of weight $3/2>1$, the spine dominates the potential (the eigenvector's dynamic range grows like $1.5^k$), and the top digit decides whether the spine continues, so it controls an $O(1)$ fraction. **The loss in the Krasikov–Lagarias system is concentrated on 3-adic neighbourhoods of the negative Collatz cycles.**
4. Consequently the naive reduction "annealed eigenvector $\Rightarrow$ certificate" only reaches $\lambda\approx1.43$: it is killed by the spine classes. The true min-eigenvector accommodates them by lowering their own potential self-consistently. A proof of $\lambda_k\to2$ has to treat the spine classes separately (their fraction is $3^{-j}$ for spine length $j$) and show the *regular* classes' digit influence decays; measured on regular classes the per-digit ratio is $0.85$–$0.91$ in mid-range, not yet a clean constant.
5. The annealed operator's spectrum is $\{1, 1/4, 1/4, \ldots\}$ (the $1/4$ from the $\times4$ permutation), so the spectral gap is *not* what sets the digit-influence rate; the rate lives in the level-to-level renormalisation $c_k \leftarrow \bar c_{k-1}$ (the level-$k$ eigenvector is determined by the lift-averages at level $k-1$ through $c(m)=\sum_n 4^{-n}(O\bar c)(4^n m)$), which is the object to analyse next.

**Status:** $\lambda_k\to2$ remains a conjecture with two candidate rates; the structural cause of the loss (negative cycles in $\mathbb{Z}_3$) is identified and is the natural starting point for a proof.
