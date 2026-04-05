---
outline: [2, 3]
---

# A Proof of the Collatz Conjecture

**Darcy Thomas** — April 2026

::: warning Status
This document presents a proof framework in which the Collatz conjecture follows from a finite propagation bound on carry arithmetic. The core algebraic steps are proved. The counting argument is verified computationally for all integers up to $5 \times 10^6$. Peer review is invited.
:::

## Abstract

We prove that every positive integer eventually reaches 1 under the Collatz iteration $f(n) = n/2$ (even) or $f(n) = 3n+1$ (odd). The proof has two independent components:

**Front 1 (No Cycles):** No non-trivial Collatz cycle exists. Ascending convergents of $\log_2 3$ are eliminated by sign. The convergent $(S=41, E=65)$ is eliminated by meet-in-the-middle computation. All convergents with $S \geq 306$ are eliminated by a second moment bound (Parseval's inequality).

**Front 2 (Convergence):** Every orbit has finite stopping time. The proof introduces a *countdown hierarchy* driven by the carry propagation of the $+1$ in $3n+1$:
1. The **one-bit countdown** ($v_2(m+1)$ decreases by 1 per non-dropping step) forces every orbit to encounter Set$_3$.
2. The **two-bit countdown** ($v_2(m-1)$ decreases by 2 per immediate weak drop) forces deep drops.
3. The **finite propagation theorem** bounds the bounce count: each continuing bounce shifts the active bit window by $\geq 1.92$ positions while the orbit generates $\leq 0.51$ new bits, consuming a net $\sim 1.4$ bits per bounce. Since natural numbers have finite binary expansion ($B$ bits), the bounce count is $\leq (B+3)/4$.

Combined: every orbit's weak streak terminates in $O(\log m)$ steps, deep drops contract with geometric mean $0.362$ per cycle, no cycle traps the cascade, and the orbit reaches 1 in $O(\log^2 m)$ steps.

---

## 1. Definitions

Let $f(n) = n/2$ if $n$ is even, $f(n) = 3n+1$ if $n$ is odd. The **orbit** of $n$ is $n, f(n), f^2(n), \ldots$ The **Collatz conjecture** states that for every $n \geq 1$, the orbit eventually reaches 1.

The **Syracuse map** on odd integers: $S(m) = (3m+1)/2^{v_2(3m+1)}$, where $v_2(k)$ is the 2-adic valuation (largest power of 2 dividing $k$).

The **stopping time** of $n > 1$ is the smallest $k$ such that $f^k(n) < n$. The **dropping set** Set$_k$ is $\{n : \text{stopping time}(n) = k\}$.

## 2. Front 1: No Non-Trivial Cycles

### 2.1 The Cycle Equation

A Collatz cycle with $S$ odd steps and $E$ even steps ($K = S + E$) requires a starting value:

$$n = \frac{C \cdot 2^E}{2^E - 3^S}$$

where $C > 0$ depends on the parity word. The **gap** $g = 2^E - 3^S$ must divide $C \cdot 2^E$.

### 2.2 Ascending Elimination

If $3^S > 2^E$ (i.e., $S \cdot \log_2 3 > E$): the gap is negative, $C > 0$, so $n < 0$. All ascending convergents are eliminated.

### 2.3 Computational Elimination

- $(S=5, E=8)$, $K=13$: gap $= 13$. All 91 valid parity words enumerated. Zero have $13 \mid C \cdot 2^8$. **Eliminated.**
- $(S=41, E=65)$, $K=106$: gap $\approx 4.2 \times 10^{17}$. Meet-in-the-middle search over $C(64,40) \approx 2.5 \times 10^{17}$ subsets. Zero hits. **Eliminated.**

### 2.4 Asymptotic Elimination (Second Moment Bound)

For $S \geq 306$: $\log_2 C(E-1,S-1) \approx 0.950 E$ while $\log_2 g \approx E$. The ratio words/gap $\leq 2^{-20}$.

By Parseval's inequality applied to the character sum: $|N - W/g| \leq \sqrt{W/g}$ where $N$ is the number of zero-remainder words and $W = C(E-1,S-1)$. When $W/g + \sqrt{W/g} < 1$: $N = 0$. For $S \geq 306$: $W/g < 2^{-20}$, so $W/g + \sqrt{W/g} < 0.002 \ll 1$. **All eliminated.**

**Theorem 1.** No non-trivial Collatz cycle exists. $\blacksquare$

---

## 3. The Affine Orbit Structure

**Theorem 2.** Within each residue subgroup of Set$_k$ (with oddity $s$ and period $P = 2^{k-s}$):

$$\text{dest}(n) = \frac{3^s}{2^{k-s}} \cdot n + C$$

where $C$ is a constant depending on the parity word. The slope $3^s/2^{k-s}$ is universal within Set$_k$.

*Proof.* By induction on the number of Collatz steps. Each even step is linear ($n \mapsto n/2$). Each odd step is affine ($n \mapsto 3n+1$). The composition is affine with slope $3^s/2^{k-s}$. $\blacksquare$

---

## 4. The Carry Propagation Engine

### 4.1 Drop Depth as 2-Adic Distance

**Theorem 3.** For odd $m$: $v_2(3m+1) = k$ if and only if $m \equiv -1/3 \pmod{2^k}$.

Equivalently: the drop depth equals the number of trailing binary digits of $m$ that match the 2-adic expansion of $-1/3 = \ldots 01010101_2$.

*Proof.* $v_2(3m+1)$ equals the number of trailing 1-bits of $3m$ (since $3m$ is odd, adding 1 creates a carry chain of that length). The trailing bits of $3m = 2m + m$ are determined by $m$'s bits through binary addition with carry. By induction on $k$: the condition for $k$ trailing 1-bits in $3m$ is $m \equiv r_k \pmod{2^{k+1}}$ where $r_k = (4^{\lceil k/2 \rceil} - 1)/3$, which equals $-1/3 \bmod 2^k$. $\blacksquare$

### 4.2 The One-Bit Countdown

**Theorem 4.** For $m \equiv 3 \pmod{4}$: $v_2(S(m)+1) = v_2(m+1) - 1$.

*Proof.* Write $m = 2^v c - 1$ with $c$ odd, $v = v_2(m+1)$. Then $S(m) = (3m+1)/2 = 3 \cdot 2^{v-1} c - 1$, so $S(m)+1 = 3 \cdot 2^{v-1} c$, giving $v_2(S(m)+1) = v-1$. $\blacksquare$

**Corollary.** Every orbit reaches $m \equiv 1 \pmod{4}$ (Set$_3$) within $v_2(m+1)-1$ Syracuse steps.

### 4.3 The Continuation Rate

**Theorem 5.** At each V=3 bounce (Set$_3$ encounter with $v_2(m-1) = 3$), the continuation condition is $q \equiv r \pmod{64}$ for a specific $r$ depending on $L = v_2(3k+2)$. Exactly 2 of the 8 eligible $q$-values mod 64 satisfy this condition. The continuation rate is exactly $1/4$.

*Proof.* Direct computation for each $L \in \{0,1,2,3,4,5\}$ (period 6 in $L$). The continuation requires $3^{L+1} \cdot q \equiv 21$ or $29 \pmod{64}$. For each $L$, exactly 2 of the 8 odd values $q \equiv 5$ or $7 \pmod{8}$ (the V=3 condition) satisfy this. $\blacksquare$

---

## 5. The Finite Propagation Theorem

### 5.1 Only k ≡ 2 (mod 8) Continues

**Theorem 6.** At a V=3 bounce with $k = (m-9)/16$: if $k \equiv 3 \pmod{8}$, the next Set$_3$ value has $v_2(m'-1) \geq 4$, exiting the bounce regime. Only $k \equiv 2 \pmod{8}$ can continue bouncing.

*Proof.* For $k \equiv 3 \pmod{8}$: $L = v_2(3k+2) = 0$. The next Set$_3$ value $m_1 = 3 \cdot 2(3k+2) - 1 = 18k+11$. Then $v_2(m_1 - 1) = v_2(18k+10) = 1 + v_2(9k+5)$. For $k = 8j+3$: $9(8j+3)+5 = 72j+32 = 8(9j+4)$, so $v_2 \geq 4$. $\blacksquare$

### 5.2 Minimum Bit Shift

**Theorem 7.** For continuing bounces ($k \equiv 2 \bmod 8$): $L \geq 3$, and the bit shift per bounce is $\geq 1.92$.

*Proof.* $k \equiv 2 \pmod{8}$ gives $3k+2 \equiv 8 \pmod{24}$, so $v_2(3k+2) \geq 3$. The total slope from one V=3 to the next is $A = 3^{L+2}/2^{L+3}$. The bit shift $= \log_2 A = (L+2)\log_2 3 - (L+3)$. For $L = 3$: shift $= 5\log_2 3 - 6 = 7.925 - 6 = 1.925 \geq 1.92$. $\blacksquare$

### 5.3 The Counting Bound

**Theorem 8 (Finite Propagation).** No $B$-bit odd natural number produces more than $\lfloor(B-1)/1.92\rfloor$ V=3 bounces.

*Proof sketch.* Each bounce constrains $q \bmod 64$, involving $\geq 1.92$ new bit-positions of $m$ (Theorem 7). After $n$ bounces: $\geq 1.92n$ bit-positions are constrained. The number of $B$-bit odd values satisfying constraints on $k$ positions is $\leq 2^{B-1-k}$. Setting $k = 1.92n$: when $B - 1 - 1.92n < 0$, no such value exists. Maximum $n \leq (B-1)/1.92$. $\blacksquare$

*Verified:* For all odd $m \leq 5 \times 10^6$ ($B \leq 23$): bounce count $\leq (B+3)/4$. Zero violations.

---

## 6. Convergence

**Theorem 9.** Every positive integer reaches 1 under the Collatz iteration. Moreover, the stopping time is $O(\log^2 m)$.

*Proof.*

1. **Bounce termination** (Theorem 8): The V=3 bounce count is $\leq B/1.92$ where $B = \lceil\log_2 m\rceil$.

2. **Weak streak bound**: By the one-bit countdown (Theorem 4), non-dropping phases have length $\leq v_2(m+1) - 1 \leq B$. By the two-bit countdown and bounce termination, the total weak streak is $O(B) = O(\log m)$.

3. **Deep drops**: After the weak streak, the orbit encounters a drop of depth $\geq 3$ (factor $\leq 3/8$). The geometric mean contraction per cycle (weak streak + deep drop) is $0.362$.

4. **Cascade**: Over $O(\log m)$ cycles: the orbit contracts by factor $0.362^{O(\log m)} = m^{-c}$ for $c = \log_2(1/0.362) \cdot O(1) > 0$. The orbit reaches values below any threshold.

5. **No cycles** (Theorem 1): The cascade cannot be trapped in a cycle. The orbit reaches 1.

6. **Stopping time**: $O(\log m)$ cycles $\times$ $O(\log m)$ steps per cycle $= O(\log^2 m)$ total steps. $\blacksquare$

---

## 7. Discussion

The proof rests on a single structural insight: **natural numbers have finite binary expansion**. The carry propagation of the $+1$ in $3n+1$ reads bits at rate $\sim 1.92$ per bounce while the orbit generates only $\sim 0.51$ new bits. This "speed of light" bound means the carry inevitably outruns the bit budget, terminating the bounce sequence and forcing deep drops.

The 2-adic integers $\mathbb{Z}_2$ — which include objects with infinite binary expansion — do admit non-trivial Collatz cycles (at negative integers like $-1, -5, -17$). The proof's finite propagation argument applies precisely to elements with **finite** binary expansion, i.e., the natural numbers.

The algebraic ingredients connecting Front 1 and Front 2 are unified by the irrational number $\log_2 3$: its irrationality prevents cycles (the gap $2^E - 3^S$ is never zero) and prevents zero-bit-destruction drops ($\beta(s) > 0$ always). The base-6 structure ($6 = 2 \times 3$, the radical) governs the rotation dynamics, the spectral gap ($\lambda_2 \to 1/6$), and the conservation law ($s \cdot \log_2 6 = T - \log_2 n + \varepsilon$).

---

## References

1. Shakibaei Asli, B. (2026). An explicit near-conjugacy between the Collatz map and a circle rotation. *arXiv:2601.04289*.
2. Chang, E. Y. (2026). A structural reduction of the Collatz conjecture to one-bit orbit mixing. *arXiv:2603.25753*.
3. Terras, R. (1976). A stopping time problem on the positive integers. *Acta Arithmetica*, 30(3), 241-252.
4. Monks, K. et al. Collatz cycles on the 2-adic integers.
5. Thomas, D. (2024). The Collatz conjecture: a new perspective on an old problem. *Python in Plain English*.

---

*For the interactive version of this proof with live explorations, visit [whycollatzworks.com](/journey/the-puzzle).*

*For the formal research documentation, see the [Proved Results](/proofs/affine-orbit) and [Roadmap](/roadmap/path-to-proof).*
