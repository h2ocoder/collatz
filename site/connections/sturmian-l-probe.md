# The Sturmian L-Probe

A sum of the sextic character $\chi_6$ of $\mathbb{Z}[\omega]$ over a single Collatz dropping set has a **closed form**, exact over whole periods, and its sign follows the cutting sequence of $\log_2 3$.

Despite the name, no L-function is evaluated on this page: $\chi_6(n + \text{dest}(n)\,\omega)$ depends only on $n \bmod 3$ and $\text{dest}(n) \bmod 3$, so the sum is a weighted count of destinations by their residue modulo 3. The ingredients are known: reading destinations modulo powers of 3 is standard (Lagarias 1985; Wirsching 1998), and the path counts $P_o$ below are OEIS A100982.

Every quantity is explicit and every constant is algebraic. The closed form matches the computed sums shown in the table and plots below (checked by direct summation over whole periods for $o \le 8$); the argument for it is given as an outline, with the lemmas in Step 5 stated rather than proved in full here.

## The Setup

Each odd integer $n$ lifts to an Eisenstein integer via the **orbit-pair lift**:

$$\iota_2(n) = n + \text{dest}(n) \cdot \omega \in \mathbb{Z}[\omega]$$

where $\text{dest}(n)$ is the first orbit value below $n$. The sextic residue character $\chi_6$ maps each lift to a sixth root of unity (or zero). It has conductor 3, so its value depends only on the lift modulo 3.

For odd-start dropping times $k_o = o + \lfloor o \log_2 3 \rfloor + 1$ and the corresponding dropping set $\text{Dset}_{k_o}$, define the **per-Dset twisted partial sum**:

$$D_{\chi_6}^{(k_o)}(N) = \sum_{\substack{n \le N \text{ odd} \\ T(n) = k_o} } \chi_6\bigl(\iota_2(n)\bigr)$$

## The Closed Form

::: tip Sturmian L-Probe Closed Form (proof outlined below; checked by direct summation for o ≤ 8)
For all $o \ge 1$ except the unique singular case $o = 3$, when the sum runs over a whole number of periods (a period is $3 \cdot 2^{k_o}$ consecutive integers, all greater than 1):

$$D_{\chi_6}^{(k_o)} = \frac{i}{\sqrt 3} \cdot \epsilon_o \cdot \frac{A_o}{P_o} \cdot N_{k_o}$$

where:
- $\epsilon_o = +1$ if $\text{gap}_o = k_o - k_{o-1} = 3$, and $-1$ if $\text{gap}_o = 2$.
- $A_o$ is determined by the recursion $A_{o+1} = \tfrac{1}{2}(P_o + \sigma_o A_o)$ with $A_1 = 1$, $\sigma_o = (-1)^{\text{gap}_o}$.
- $P_o$ is the number of valid Syracuse $\alpha$-sequences for $\text{Dset}_{k_o}$: $1, 1, 2, 3, 7, 12, 30, 85, \dots$
- $N_{k_o}$ is the number of terms: the odd $n$ in the range with $T(n) = k_o$.

For a general cut-off $N$, the partial sum $D_{\chi_6}^{(k_o)}(N)$ differs from this by a bounded amount, the contribution of an incomplete period.

For $o = 3$ (i.e. $k = 8$): the sum over every whole period is exactly 0, and the partial sums stay bounded. They are not always 0: $D_{\chi_6}^{(8)}(23)$ has modulus 1.
:::

The sign $\epsilon_o$ is the **Sturmian cutting sequence of $\log_2 3$** — the canonical irrational-rotation signal.

![Per-Dset character-sum sizes per non-zero term, and the same signed by phase, for partial sums up to N = 300,000 and dropping times up to 88. Reference lines at √3/2, √3/6 and 1/8; the closed form's value at o = 5 is √3/14 ≈ 0.124](/data/dropping_set_l_function.png)

## What the closed form looks like

| $o$ | $k_o$ | gap | $\arg$ | size per non-zero term | clean form |
|---:|---:|---:|---:|---:|---|
| 1 | 3 | 2 | $-90°$ | 0.8660 | $\sqrt{3}/2$ |
| 2 | 6 | 3 | $+90°$ | 0.8660 | $\sqrt{3}/2$ |
| 3 | 8 | 2 | — | 0 | exact cancellation |
| 4 | 11 | 3 | $+90°$ | 0.2887 | $\sqrt{3}/6$ |
| 5 | 13 | 2 | $-90°$ | 0.1237 | $\sqrt{3}/14$ |
| 6 | 16 | 3 | $+90°$ | 0.2887 | $\sqrt{3}/6$ |
| 7 | 19 | 3 | $+90°$ | 0.1155 | $(\sqrt{3}/2) \cdot 2/15$ |
| 8 | 21 | 2 | $-90°$ | 0.1325 | $(\sqrt{3}/2) \cdot 13/85$ |

Three facts visible in the table, all consequences of the closed form:

1. **Per non-zero term, the size is $\tfrac{\sqrt3}{2} \cdot A_o/P_o$**, a rational multiple of $\sqrt{3}/2$. (One term in three is zero, because $\chi_6$ vanishes there.)
2. **All phases are $\pm 90°$** — over whole periods the sums lie exactly on the imaginary axis (for other $N$, within a bounded distance of it).
3. **The sign pattern matches the gap parity** — exactly the Sturmian word of $\log_2 3$.

## The Sturmian Sign Rule

For the dropping-time sequence $k_o$, the gaps $\text{gap}_o = k_o - k_{o-1}$ form the binary sequence

$$(2, 3, 2, 3, 2, 3, 3, 2, 3, 2, 3, 3, 2, 3, 2, 3, 2, 3, 3, 2, \ldots)$$

This is the **cutting sequence** of the line $y = x \log_2 3$ — the canonical Sturmian word with irrational slope. The sign of the per-Dset sum, over whole periods, is:

$$\text{sgn}\bigl(D_{\chi_6}^{(k_o)}\bigr) = \begin{cases} +i & \text{if } \text{gap}_o = 3 \\ -i & \text{if } \text{gap}_o = 2 \end{cases}$$

Equivalently, by the Beatty fractional-part characterization:

$$\text{gap}_o = 3 \iff \{(o-1) \log_2 3\} \ge 2 - \log_2 3 \approx 0.4150$$

That the gaps form a Sturmian word is immediate from the definition of $k_o$. The content of the rule is that the sign of the character sum is the parity of the gap.

![Empirical signs (open circles, shown for dropping times up to 60) sit on the Sturmian-rule prediction (filled green for gap=3, red for gap=2) everywhere except k = 8 (o = 3), where the sum is 0. Bottom panel shows the Beatty fractional part vs the threshold 0.4150 — green points above, red below](/data/sturmian_sign_pattern.png)

In the figure's axis label, $c_1$ and $c_2$ are the numbers of residue classes of the dropping set whose destinations are 1 and 2 modulo 3. Over a whole period the sum is $i\sqrt{3} \cdot 2^o\,(c_2 - c_1)$, so its sign is the sign of $c_2 - c_1$, and the closed form says $c_2 - c_1 = \epsilon_o A_o$. Counted exactly, class by class, $c_2 - c_1$ has the predicted sign for every $o \le 400$ except $o = 3$, where it is 0 (computed).

## Proof outline

The argument is a chain of explicit calculations:

**Step 1 — Eisenstein column collapse.** The 9-cell lookup of $\chi_6$ on $\mathbb{Z}[\omega]/3$ has column sums
$\sum_i \chi_6(i + 0 \cdot \omega) = 0$, $\sum_i \chi_6(i + 1 \cdot \omega) = -i\sqrt{3}$, $\sum_i \chi_6(i + 2 \cdot \omega) = +i\sqrt{3}$.

**Step 2 — dest mod 3 lemma.** Using the affine recurrence $n_k = (3^o n + \Delta)/2^e$ and tracking $\Delta \bmod 3$, one shows $\text{dest}(n) \bmod 3 \in \{1, 2\}$, with $\text{dest} \equiv 2 \pmod 3$ iff $j^* + k_o$ is even (where $j^*$ is the position of the last odd Collatz step).

**Step 3 — α-parity reduction.** Combining Steps 1 and 2: the sign of the per-Dset sum depends on the parity of $\alpha_o = k_o - 1 - j^*$, the last Syracuse-step halving count.

**Step 4 — alternating-sum recursion.** Tracking $A_o =$ (paths with $\alpha_o$ odd) $-$ (paths with $\alpha_o$ even) over valid Beatty-bounded lattice paths gives
$$A_{o+1} = \tfrac{1}{2}(P_o + \sigma_o A_o), \quad \sigma_o = (-1)^{\text{gap}_o}.$$

**Step 5 — three lemmas:**
- **Parity:** $A_o \equiv P_o \pmod 2$ (so the recursion is always integer-valued).
- **Monotonicity:** $P_{o+1} > P_o$ for $o \ge 2$ (so path counts grow strictly).
- **Bounds:** $0 < A_o < P_o$ for $o \ge 4$, with $A_3 = 0$ the unique zero.

**Step 6 — induction.** From the three lemmas, the recursion produces $A_{o+1} \ge 1$ for $o \ge 3$, with $A_{o+1} \le P_o - 1 < P_{o+1}$ preserved. The bound $A_o < P_o$ for $o \ge 3$ rules out any second cancellation: $o = 3$ is the only zero.

**What the outline assumes.** It treats each dropping set as a union of residue classes modulo a power of 2, which is why the equality is exact only over whole periods. That description is Terras's (1976) for all sufficiently large members of each class. Whether every member above 1 complies is his coefficient stopping time conjecture, open in general and true throughout the range of the sums computed here.

## What this is *not*

The closed form has nothing to do with the Riemann hypothesis for any classical L-function. The Hecke L-function $L(s, \chi_6)$ on $\mathbb{Z}[\omega]$ has its own zeros. The closed form is about the **orbit-twisted partial sum**, which is a different object: a character sum restricted to the *Collatz-orbit-pair image* in $\mathbb{Z}[\omega]$, not over all ideals.

One could go on to form the Dirichlet series

$$L_{\text{Collatz} }(s, \chi_6) = \sum_{n \text{ odd} } \frac{\chi_6(\iota_2(n))}{n^s}$$

with the closed form describing its partial sums one dropping set at a time. Its zeros, if it has interesting ones, would not be the zeros of the classical $L(s, \chi_6)$. I have not studied them.

## Implications

**The sum is not random.** Restricted to a dropping set, the character sum does not behave like a random sum. Except at $o = 3$, where it cancels exactly over whole periods, it grows in proportion to the number of terms, with an explicit constant and a sign fixed by the Sturmian word of $\log_2 3$.

**The structure is combinatorial.** The closed form depends only on the Beatty boundary $B_j = \lfloor j \log_2 3 \rfloor$ and counts of lattice paths below it (the admissible parity words of OEIS A100982).

**It says nothing about convergence.** The formula is stated in terms of the numbers that *do* drop, so it is equally consistent with the conjecture being true or false.

## Related

- [The Transfer Operator](/connections/hilbert-polya) — a small matrix whose spectrum turns out to be the trivial cycle
- [Eisenstein Lattice](/connections/eisenstein) — the ring $\mathbb{Z}[\omega]$ and its primes 2 and 3
- [The Hidden Rotation](/journey/the-rotation) — the base-6 circle: an irrational rotation plus a small perturbation
