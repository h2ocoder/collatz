# Density Exponent via Difference Inequalities — Design

**Date:** 2026-09-10
**Goal:** Execute the direction recommended in `docs/plans/2026-09-10-proof-direction-assessment.md`: attack the density exponent $\theta$ in $\#\{n\le x : n\to 1\}\ge x^{\theta}$ using Krasikov–Lagarias difference inequalities, (a) reproducing the published $x^{0.84}$ and (b) testing whether the repo's dropping-set alphabet gives a stronger system.

## Objects

For $a \not\equiv 0 \pmod 3$ let $\pi_a(x) = \#\{n \le x : T^{j}(n) = a \text{ for some } j\}$ (nodes of the backward tree of $a$ up to $x$). Krasikov–Lagarias (Acta Arith. 109, 2003) define, for principal classes $m \bmod 3^k$ ($m \equiv 2 \bmod 3$),
$$\phi_k^m(y) = \inf\{\pi_a^*(2^y a) : a \equiv m \pmod{3^k}\},$$
so $y$ is height in bits above the target. The inequalities, with $\alpha=\log_2 3$ and $d_{k-1}^{m'} = \min$ over the three lifts of $m'$ to level $k$:

| $m \bmod 9$ | inequality |
|---|---|
| 2 | $\phi_k^m(y) \ge \phi_k^{4m}(y-2) + d_{k-1}^{(4m-2)/3}(y+\alpha-2)$ |
| 5 | $\phi_k^m(y) \ge \phi_k^{4m}(y-2)$ |
| 8 | $\phi_k^m(y) \ge \phi_k^{4m}(y-2) + d_{k-1}^{(2m-1)/3}(y+\alpha-1)$ |

The 5-case is the branch whose odd preimage is $\equiv 0 \pmod 3$ (a dead chain). The min is where a 3-adic digit is lost on division by 3; it is the *only* pessimism in the system. **Theorem 2.2 (KL):** if the linear program $L_k^{NT}(\lambda)$ — the ansatz $\phi \ge c\,\lambda^y$ substituted into the table, with $1 \le c \le C_{\max}$ and $d = \min$ of lifts — is feasible for $\lambda \in [1,2]$, then $\pi_a(x) \ge C x^{\log_2 \lambda}$.

## Method

Instead of an LP, view the right-hand side as a **monotone, positively homogeneous map** $M_\lambda$ on $\mathbb{R}_{\ge 0}^{3^k}$. Feasibility of $c \le M_\lambda(c)$ with $c>0$ is equivalent to the nonlinear Perron root $r(\lambda) \ge 1$; $r$ is decreasing in $\lambda$. So: power iteration for $r(\lambda)$, bisection for $\lambda^\ast$ with $r=1$, exponent $\gamma_k = \log_2 \lambda^\ast$. Cost $O(3^k)$ per iteration, which reaches $k = 16$ on a laptop where the 2003 LP stopped at $k=11$.

**Certificate.** For $\lambda' = \lambda^\ast - 10^{-4}$, iterate $M_{\lambda'}$ to convergence, round $c$ to integers $C = \lfloor c\, 2^{30}\rfloor$, replace the coefficients $\lambda'^{-2}, \lambda'^{\alpha-2}, \lambda'^{\alpha-1}$ by integer *lower* bounds (mpmath, 60 digits, floored), and check $C \le M(C)$ in exact `int64` arithmetic. Monotonicity in the coefficients makes success a proof of feasibility of $L_k^{NT}(\lambda')$, hence of the exponent $\log_2 \lambda'$ by Theorem 2.2.

## The dropping-set system (DROP)

Same tree, expanded along first-return (dropping) $T$-words $w$ with $s$ ones, length $L$, constant $C_w$: the preimage $n_w(a) = (2^L a - C_w)/3^s$ exists iff $a \equiv \rho_w \pmod{3^s}$, sits at height $y - (L - s\alpha)$ (always retarded), and is known only mod $3^{k-s}$, so it enters through the min over $3^s$ lifts:
$$c^m \le \lambda^{-1} c^{2m} + \sum_{w:\, m \equiv \rho_w (3^{s_w})} \lambda^{-(L_w - s_w\alpha)}\, d_{k-s_w}^{\,n_w(m)}.$$
Attractive feature: no advanced terms, so the induction on $y$ is direct. Expected weakness (predicted before running): KL's nested min-of-sums dominates DROP's sum-of-mins, so DROP cannot exceed KL at equal $k$.

## Files

- `scripts/density_exponent_kl.py` — `kl_system`, `drop_system`, `perron_root`, `best_lambda`, `certify_kl_exact`, CLI (`compare` and `certify`).
- `data/kl_eigvec_k{k}.npy` — certified eigenvectors.
- Results: `docs/Explorations/Density Exponent.md`.
