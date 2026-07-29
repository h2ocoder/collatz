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

## 2b. The interaction identity and the two-tank machine (PROVED, 2026-07-28 continuation)

The whole calculus compresses into one formula. For **any** two depths $d, d'$ and odd $m$ with step depth $d = v_2(3m+1)$:

$$F_{d'}(m_2) \;=\; \frac{3\,F_{d'}(m) + 2^{d'} - 2^{d}}{2^{d}}.$$

*Proof.* $2^d F_{d'}(m_2) = (2^{d'}-3)(3m+1) - 2^d = 3F_{d'}(m) + (2^{d'}-3) + 3 - 2^d$. $\blacksquare$ (Verified 300K × 6 depths, exact.)

$d'=d$ recovers the master ledger; $d' \neq d$ gives every cross-refill, with an **escape hatch** exactly when $v_2(3F_{d'}(m)) = \min(d,d')$ (2-adic cancellation). Writing $V = v_2(m-1)$, $W = v_2(5m-1)$, the encounter state collapses to a *single active tank* — weak $(V\ge3, W=2)$, medium $(V=2, W\ge4)$, strong $(V=2, W=3)$ — with exact rules (all measured exhaustively to $2\times10^6$, zero exceptions, and provable from the identity via $15(m-1)+16$ and $3(5m-1)-32$):

| drop | own ledger | cross-refill | hatch |
|------|-----------|--------------|-------|
| weak $V{=}3$ | $V'{=}1$ (→ growth phase) | $W'{=}1$ | — |
| weak $V{=}4$ | $V'{=}2$ | $W' \ge 3$ **geometric** | **yes**: $W'{=}3$ ⟹ next is STRONG |
| weak $V{\ge}5$ | $V'{=}V{-}2$ (stays weak) | $W'{=}2$ | — |
| medium $W{=}4$ | $V'{=}1$ (→ growth phase) | $W'{=}1$ | — |
| medium $W{=}5$ | $W'{=}2$ | $V' \ge 3$ **geometric** | **yes** (re-enters weak mode) |
| medium $W{\ge}6$ | $W'{=}W{-}3$ | $V'{=}2$ | $W'{=}3$ ⟹ next is STRONG |

The deterministic branches drain fuel toward the critical levels $V{=}4$, $W{=}5$ ($=2^{d+2}$ in the proofs); only at hatches and growth-phase exits do fresh bits of $m$ enter. Avoiding strong forever means threading every hatch. Next-encounter type given $(d, V, W)$: 2/3 predictable, $H = 0.92$ bits — the residual entropy is exactly the hatch/growth-exit freedom.

## 3. The minimal-avoider function $A(n)$ (exact data)

$$A(n) = \min\{m \equiv 1 \bmod 4,\ m>1 : \mathrm{enc}(m) \ge n\}.$$

A depth-3 countdown theorem is **equivalent** to a lower bound $A(n) \ge c\,\gamma^n$ with $\gamma > 1$: it gives the pointwise bound $\mathrm{enc}(m) \le \log_\gamma(m/c)$, i.e. *every orbit meets a strong drop within $O(\log m)$ encounters*.

Exact values (sieve to $2\times 10^8$, `three_bit_avoidance_tree.py`): $A(1..59)$ = 9, 9, 9, 25, 33, 41, …, 199 327 233. Observed structure:

* Minimizers propagate by **L1** (ratio $4/3$; runs visible as v$_2(m-1)$ climbing 3,5,7,9 — L1 adds 2 bits there per step) and **L2** (ratio $8/3$), and die at $\equiv 0 \bmod 3$, spawning jump families (41, 257, 825, 34041, …).
* Upper bound (proved): the class of $1$ shadows the trivial cycle at 2 bits/encounter, so $A(n) \le C\cdot 4^n$.
* **Growth-rate caution.** Fitting $n \le 43$ gave $\gamma = 1.539 \approx (4/3)^{3/2}$ — but extending to $n = 59$ drops the overall fit to $\gamma = 1.377$, and the tail segment $n = 44..59$ grows at only $\approx 1.14$/encounter, *below* $4/3$. Deeper record families keep finding cheaper backward chains. The $(4/3)^{3/2}$ pattern was a window artifact; the true $\liminf A(n)^{1/n}$ is unresolved by this data and possibly approaches a limit set by the extremal cycles of the two-tank machine.

**Conjecture (Three-Bit Countdown, revised).** $A(n) \ge c\,\gamma^n$ for some $\gamma > 1$ — the countdown needs any exponential rate, not $4/3$ specifically. The candidate value of $\gamma$ is the min-mean-cycle growth of the gated two-tank machine of §2b (a *finite computation*, see §5b), which the backward L-chains realize.

**Census check** (`three_bit_census.py`): the exact telescoping $\log_2 m = \log_2 z + (2-\log_2 3)a + (3-\log_2 3)b - (\log_2 3 - 1)c + \varepsilon$ holds with $|\varepsilon| < 0.23$ on all minimizers ($a,b,c$ = weak/medium/growth step counts, $z$ = strong root), so $A(n) \ge c\gamma^n$ is equivalent to the **step-census bound** $c \le (b + \log_2 z)/(\log_2 3 - 1) - \delta n$. Minimizers run at slack $\approx 11$–$13$ from the $\delta = 0$ line at $n \le 43$.

## 4. Why soft arguments cannot close this

* **Archimedean counting fails:** along an avoidance streak, $\log_2 m_n = \log_2 m + 0.585\,G - (\ge 0.415)\,n$ with $G$ = total growth steps. Since heuristically $E[G] \approx n$ and $0.585 > 0.415$, positivity of orbit values yields **no** bound — avoidance streaks grow on average (the known 9/8 problem). The countdown must come from the 2-adic side.
* **Measure counting fails pointwise:** under Haar measure the avoidance density per encounter is exactly $3/4$; this gives "almost all" yet again, not "all".

## 5. Where the difficulty now concentrates (sharp open problem)

The cross-term. Under a *medium* drop the tank $v_2(5m-1)$ empties by exactly 3 (ledger). But under a **weak** drop, with $u = (5m-1)/4$ (odd at weak encounters):

$$5m_2 - 1 = \frac{3(5m-1)+4}{4} = 3u+1 \quad\Longrightarrow\quad v_2(5m_2-1) = v_2(3u+1).$$

The refill of the medium tank is itself a $3x+1$ valuation of an auxiliary odd variable. The recursion is Collatz-like one level down — this is the precise algebraic face of "depends on higher bits" from the old plan, and the exact spot a proof of §3's conjecture must control.

## 5b. The concrete proof path: min-mean-cycle of the gated machine

The two-tank machine (§2b) plus the mod-3 gates (§2) is a finite-state over-approximation of all avoidance words once fuel is capped (high fuel acts uniformly) and the 3-adic state is truncated to $m \bmod 3^j$. Its minimum mean value-growth per encounter, over all cycles (Karp's algorithm), is a **rigorous lower bound** on $\liminf A(n)^{1/n}$: an over-approximation admits more words, so its minimum can only be smaller. The program:

1. Measure/derive the growth-phase exit rule (the $(V,W)$ distribution when a growth phase ends) — the last unmodelled transition.
2. Build the product graph (mode, capped fuel, $m \bmod 3^j$); edge weights $\log_2(\text{backward factor}) \in \{\log_2\frac43, \log_2\frac83, \log_2\frac23\}$.
3. Compute min-mean-cycle. If $> 0$: exponential lower bound on $A(n)$ **proved** modulo the (bounded-ratio telescoping) value-tracking lemma, which handles the $\pm1$ corrections via each step's exact linearity in its own coordinate.
4. If $\le 0$ at every truncation $j$: the obstruction is genuinely 3-adic-deep, and the offending cycles name it precisely.

## 6. Status

| Claim | Status |
|-------|--------|
| Master identity + ledger, all $d$ | **PROVED** (one line; 200K exact checks) |
| One-Bit, Two-Bit as $d=1,2$ of one family | **PROVED** |
| Encounter classification via $v_2(m-1), v_2(5m-1)$ | **PROVED** (easy; verified to $2^{18}$) |
| Backward tree = L1/L2/L3 gated by mod 3; death at $0 \bmod 3$ | **PROVED** |
| Chain gas $=$ $v_3(m\mp1)$ | **PROVED** (affine conjugation) |
| $A(n) \le C\cdot4^n$ | **PROVED** (trivial-class shadow) |
| Interaction identity $F_{d'}(m_2) = [3F_{d'}(m) + 2^{d'} - 2^d]/2^d$ | **PROVED** (one line; 300K × 6 depths exact) |
| Two-tank refill rules + hatch structure | **PROVED** (from identity; exhaustive to $2\times10^6$) |
| $A(n)$ exact to $n=59$; tail growth $\approx 1.14 <$ overall fit $1.38$ | **COMPUTED** (rate unresolved; $(4/3)^{3/2}$ retracted) |
| $A(n) \ge c\,\gamma^n$, some $\gamma>1$ (⟹ strong drop within $O(\log m)$ encounters) | **OPEN** — the Three-Bit Countdown |
| Min-mean-cycle of gated machine $> 0$ | **OPEN** — finite computation, §5b |
| Ansatz $v_2(m-a)$ monotone along streaks | **REFUTED** ($v_2(m-1)$ double-increases 2954× once medium drops interleave) |
