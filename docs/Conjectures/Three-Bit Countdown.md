# The Three-Bit Countdown and the Unified Invariant Family

**Date:** 2026-07-28
**Status:** Structure PROVED; forcing bound reduced to a sharp conjecture with exact data.
**Scripts:** `scripts/three_bit_ledger.py`, `scripts/three_bit_avoidance_tree.py`, `scripts/three_bit_backward_law.py`, `scripts/three_bit_ansatz.py`
**Figure:** `data/collatz_three_bit_avoiders.png`

Task 3–4 of [[2026-04-04-countdown-hierarchy-plan]] asked for an invariant $I_4$ forcing strong drops ($v_2(3m+1)\ge 4$), and conjectured a pattern $I_k = v_2(m+a_k)/b_k$. **The pattern exists and is now explicit.**

---

## 1. The master identity (PROVED)

For odd $m$, let $d = v_2(3m+1)$ and $m_2 = (3m+1)/2^d$ be the Syracuse step. Define the **depth-$d$ form**

$$F_d(m) = (2^d - 3)\,m - 1, \qquad \text{fixed point } \tfrac{1}{2^d-3}.$$

Then, exactly and for every odd $m$:

$$F_d(m_2) = \frac{3\,F_d(m)}{2^d}.$$

*Proof.* $2^d F_d(m_2) = (2^d-3)(3m+1) - 2^d = 3(2^d-3)m - 3 = 3F_d(m)$. $\blacksquare$

Moreover $F_d(m) \equiv -(3m+1) \pmod{2^d}$, so $v_2(F_d(m)) \ge d$ automatically. Hence the **ledger**: each depth-$d$ step

* decreases $v_2(F_d)$ by exactly $d$, and
* increases $v_3(F_d)$ by exactly 1.

Verified exhaustively/randomly in `three_bit_ledger.py` (200K random 64-bit odd $m$, exact). Specializations:

| $d$ | form $F_d$ | ledger | known as |
|----|-----------|--------|----------|
| 1 (growth) | $-(m+1)$ | $m_2+1 = \tfrac32(m+1)$ | **One-Bit Countdown** |
| 2 (weak)   | $m-1$    | $m_2-1 = \tfrac34(m-1)$ | **Two-Bit Countdown** |
| 3 (medium) | $5m-1$   | $5m_2-1 = \tfrac38(5m-1)$ | **NEW: three-bit form** |
| 4 (strong) | $13m-1$  | $13m_2-1 = \tfrac{3}{16}(13m-1)$ | depth-4 form |

Every Syracuse step converts 2-adic capital of its own form into 3-adic capital, at exchange rate $d$ bits : 1 trit. The One-Bit and Two-Bit countdowns are the $d=1,2$ rows of one algebraic family — their previously separate proofs are the same one-line computation.

**Encounter classification in form language** (verified to $2^{18}$): at a Set$_3$ encounter,
weak $\iff v_2(m-1)\ge 3$; medium $\iff v_2(m-1)=2 \wedge v_2(5m-1)\ge 4$; strong $\iff v_2(m-1)=2 \wedge v_2(5m-1)=3$.

## 2. The backward tree is an explicit 3-adic-gated system (PROVED)

Preimage maps on avoiders (an *avoider* survives $n$ encounters with $d\in\{2,3\}$; `enc(m)` = its count):

* **L1 (weak-pre):** $x \mapsto \tfrac{4x-1}{3}$, i.e. $(x-1)\mapsto\tfrac43(x-1)$. Exists iff $3\mid m-1$; always lands on a weak encounter (never strong, since $v_2(3x'+1)=v_2(4m)=2$ exactly); `enc` $+1$.
* **L2 (medium-pre):** $x \mapsto \tfrac{8x-1}{3}$, i.e. $(5x-1)\mapsto\tfrac83(5x-1)$. Exists iff $3\mid m+1$; never strong ($v_2 = 3$ exactly); `enc` $+1$.
* **L3 (growth-pre):** $x \mapsto \tfrac{2x-1}{3}$, i.e. $(x+1)\mapsto\tfrac23(x+1)$. Exists iff $3\mid m+1$; `enc` unchanged; **shrinks by $2/3$**.
* $m \equiv 0 \pmod 3$: **no Syracuse preimage exists** (family death).

Verified with 0 violations across ~50K cases each (`three_bit_backward_law.py`); each is a one-line affine conjugation, so all are proved. Every avoider arises from its successor by one L1/L2 composed with L3's, so the avoider tree is *exactly* this gated system — no hidden branches.

**Chain gas is 3-adic valuation:** consecutive L3-chains have length exactly $v_3(m+1)$; consecutive L1-chains exactly $v_3(m-1)$ (both verified exact). The 2-adic/3-adic duality of the framework is literal here: forward orbits spend $v_2$ and earn $v_3$ per form; backward chains spend the $v_3$.

## 3. The minimal-avoider function $A(n)$ (exact data)

$$A(n) = \min\{m \equiv 1 \bmod 4,\ m>1 : \mathrm{enc}(m) \ge n\}.$$

A depth-3 countdown theorem is **equivalent** to a lower bound $A(n) \ge c\,\gamma^n$ with $\gamma > 1$: it gives the pointwise bound $\mathrm{enc}(m) \le \log_\gamma(m/c)$, i.e. *every orbit meets a strong drop within $O(\log m)$ encounters*.

Exact values (sieve to $3\times 10^7$, `three_bit_avoidance_tree.py`): $A(1..43)$ = 9, 9, 9, 25, 33, 41, …, 24 381 193. Observed structure:

* Minimizers propagate by **L1** (ratio $4/3$; runs visible as v$_2(m-1)$ climbing 3,5,7,9 — L1 adds 2 bits there per step) and **L2** (ratio $8/3$), and die at $\equiv 0 \bmod 3$, spawning jump families (41, 257, 825, 34041, …).
* Fitted growth: $\gamma = 1.5387$ ($0.622$ bits/encounter), strikingly close to $(4/3)^{3/2} = 1.5396$ — the rate of a chain averaging one L1 + one L2 + one L3 per two encounters, factor $\tfrac43\cdot\tfrac83\cdot\tfrac23 = (4/3)^3$.
* Upper bound (proved): the class of $1$ shadows the trivial cycle at 2 bits/encounter, so $A(n) \le C\cdot 4^n$.

**Conjecture (Three-Bit Countdown).** $A(n) \ge c\,(4/3)^n$ for some $c>0$; empirically the truth is $\approx (4/3)^{3n/2}$.

## 4. Why soft arguments cannot close this

* **Archimedean counting fails:** along an avoidance streak, $\log_2 m_n = \log_2 m + 0.585\,G - (\ge 0.415)\,n$ with $G$ = total growth steps. Since heuristically $E[G] \approx n$ and $0.585 > 0.415$, positivity of orbit values yields **no** bound — avoidance streaks grow on average (the known 9/8 problem). The countdown must come from the 2-adic side.
* **Measure counting fails pointwise:** under Haar measure the avoidance density per encounter is exactly $3/4$; this gives "almost all" yet again, not "all".

## 5. Where the difficulty now concentrates (sharp open problem)

The cross-term. Under a *medium* drop the tank $v_2(5m-1)$ empties by exactly 3 (ledger). But under a **weak** drop, with $u = (5m-1)/4$ (odd at weak encounters):

$$5m_2 - 1 = \frac{3(5m-1)+4}{4} = 3u+1 \quad\Longrightarrow\quad v_2(5m_2-1) = v_2(3u+1).$$

The refill of the medium tank is itself a $3x+1$ valuation of an auxiliary odd variable. The recursion is Collatz-like one level down — this is the precise algebraic face of "depends on higher bits" from the old plan, and the exact spot a proof of §3's conjecture must control.

## 6. Status

| Claim | Status |
|-------|--------|
| Master identity + ledger, all $d$ | **PROVED** (one line; 200K exact checks) |
| One-Bit, Two-Bit as $d=1,2$ of one family | **PROVED** |
| Encounter classification via $v_2(m-1), v_2(5m-1)$ | **PROVED** (easy; verified to $2^{18}$) |
| Backward tree = L1/L2/L3 gated by mod 3; death at $0 \bmod 3$ | **PROVED** |
| Chain gas $=$ $v_3(m\mp1)$ | **PROVED** (affine conjugation) |
| $A(n) \le C\cdot4^n$ | **PROVED** (trivial-class shadow) |
| $A(n)$ exact to $n=43$; $\gamma \approx (4/3)^{3/2}$ | **COMPUTED** |
| $A(n) \ge c\,(4/3)^n$ (⟹ strong drop within $O(\log m)$ encounters) | **OPEN** — the Three-Bit Countdown |
| Ansatz $v_2(m-a)$ monotone along streaks | **REFUTED** ($v_2(m-1)$ double-increases 2954× once medium drops interleave) |
