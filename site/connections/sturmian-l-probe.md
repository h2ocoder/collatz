# The Sturmian L-Probe

The Hecke L-function probe $\chi_6$ on $\mathbb{Z}[\omega]$, when restricted to a single Collatz dropping set, has an **exact closed form** — and that closed form's phase is the cutting sequence of $\log_2 3$.

Every quantity is explicit and every constant is algebraic. The closed form matches the computed sums shown in the table and plots below; the argument for it is given as an outline, with the lemmas in Step 5 stated rather than proved in full here.

## The Setup

Each odd integer $n$ lifts to an Eisenstein integer via the **orbit-pair lift**:

$$\iota_2(n) = n + \text{dest}(n) \cdot \omega \in \mathbb{Z}[\omega]$$

where $\text{dest}(n)$ is the first orbit value below $n$. The sextic residue character $\chi_6$ maps each lift to a sixth root of unity (or zero).

For odd-start dropping times $k_o = o + \lfloor o \log_2 3 \rfloor + 1$ and the corresponding dropping set $\text{Dset}_{k_o}$, define the **per-Dset twisted partial sum**:

$$D_{\chi_6}^{(k_o)}(N) = \sum_{\substack{n \le N \text{ odd} \\ T(n) = k_o}} \chi_6\bigl(\iota_2(n)\bigr)$$

## The Theorem

::: tip Sturmian L-Probe Closed Form (proof outlined below)
For all $o \ge 1$ except the unique singular case $o = 3$:

$$D_{\chi_6}^{(k_o)}(N) = i\sqrt{3} \cdot \epsilon_o \cdot A_o \cdot \frac{N_{k_o}}{|R_{k_o}|}$$

where:
- $\epsilon_o = +1$ if $\text{gap}_o = k_o - k_{o-1} = 3$, and $-1$ if $\text{gap}_o = 2$.
- $A_o$ is determined by the recursion $A_{o+1} = \tfrac{1}{2}(P_o + \sigma_o A_o)$ with $A_1 = 1$, $\sigma_o = (-1)^{\text{gap}_o}$.
- $P_o$ is the number of valid Syracuse $\alpha$-sequences for $\text{Dset}_{k_o}$.
- $N_{k_o}$ is the count of odd $n \le N$ with $T(n) = k_o$.

For $o = 3$ (i.e. $k = 8$): $D_{\chi_6}^{(8)}(N) = 0$ exactly.
:::

The phase $\epsilon_o$ is the **Sturmian cutting sequence of $\log_2 3$** — the canonical irrational-rotation signal.

![Per-Dset character magnitudes α_k and signed phases, with the √3/2, √3/6, √3/14 tier structure visible](/data/dropping_set_l_function.png)

## What the closed form looks like

| $o$ | $k_o$ | gap | $\arg$ | per-$n$ size | clean form |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 3 | 2 | $-90°$ | 0.8660 | $\sqrt{3}/2$ |
| 2 | 6 | 3 | $+90°$ | 0.8660 | $\sqrt{3}/2$ |
| 3 | 8 | 2 | — | 0 | exact cancellation |
| 4 | 11 | 3 | $+90°$ | 0.2887 | $\sqrt{3}/6$ |
| 5 | 13 | 2 | $-90°$ | 0.1237 | $\sqrt{3}/14$ |
| 6 | 16 | 3 | $+90°$ | 0.2887 | $\sqrt{3}/6$ |
| 7 | 19 | 3 | $+90°$ | 0.1155 | $(\sqrt{3}/2) \cdot 2/15$ |
| 8 | 21 | 2 | $-90°$ | 0.1325 | $(\sqrt{3}/2) \cdot 13/85$ |

Three universal facts visible immediately:

1. **Magnitudes are rational multiples of $\sqrt{3}/2$**, with the denominator equal to $|R_{k_o}|$.
2. **All phases are $\pm 90°$** — sums lie strictly on the imaginary axis.
3. **The sign pattern matches the gap parity** — exactly the Sturmian word of $\log_2 3$.

## The Sturmian Sign Rule

For the dropping-time sequence $k_o$, the gaps $\text{gap}_o = k_o - k_{o-1}$ form the binary sequence

$$(2, 3, 2, 3, 2, 3, 3, 2, 3, 2, 3, 3, 2, 3, 2, 3, 2, 3, 3, 2, \ldots)$$

This is the **cutting sequence** of the line $y = x \log_2 3$ — the canonical Sturmian word with irrational slope. The sign of the L-probe's per-Dset sum is:

$$\text{sgn}\bigl(D_{\chi_6}^{(k_o)}\bigr) = \begin{cases} +i & \text{if } \text{gap}_o = 3 \\ -i & \text{if } \text{gap}_o = 2 \end{cases}$$

Equivalently, by the Beatty fractional-part characterization:

$$\text{gap}_o = 3 \iff \{(o-1) \log_2 3\} \ge 2 - \log_2 3 \approx 0.4150$$

The probe's phase pattern *is* the irrational rotation of $\log_2 3$, made arithmetic-visible.

![Empirical signs (open circles) sit exactly on the Sturmian-rule prediction (filled green for gap=3, red for gap=2). Bottom panel shows the Beatty fractional part vs the threshold 0.4150 — green points above, red below](/data/sturmian_sign_pattern.png)

## Proof outline

The argument is a chain of explicit calculations:

**Step 1 — Eisenstein column collapse.** The 9-cell lookup of $\chi_6$ on $\mathbb{Z}[\omega]/3$ has column sums
$\sum_i \chi_6(i + 0 \cdot \omega) = 0$, $\sum_i \chi_6(i + 1 \cdot \omega) = -i\sqrt{3}$, $\sum_i \chi_6(i + 2 \cdot \omega) = +i\sqrt{3}$.

**Step 2 — dest mod 3 lemma.** Using the affine recurrence $n_k = (3^o n + \Delta)/2^e$ and tracking $\Delta \bmod 3$, one shows $\text{dest}(n) \bmod 3 \in \{1, 2\}$, with $\text{dest} \equiv 2 \pmod 3$ iff $j^* + k_o$ is even (where $j^*$ is the position of the last odd Collatz step).

**Step 3 — α-parity reduction.** Combining Steps 1 and 2: the sign of the per-Dset sum depends on the parity of $\alpha_o = k_o - 1 - j^*$, the last Syracuse-step halving count.

**Step 4 — alternating-sum recursion.** Tracking $A_o = $ (paths with $\alpha_o$ odd) $-$ (paths with $\alpha_o$ even) over valid Beatty-bounded lattice paths gives
$$A_{o+1} = \tfrac{1}{2}(P_o + \sigma_o A_o), \quad \sigma_o = (-1)^{\text{gap}_o}.$$

**Step 5 — three lemmas:**
- **Parity:** $A_o \equiv P_o \pmod 2$ (so the recursion is always integer-valued).
- **Monotonicity:** $P_{o+1} > P_o$ for $o \ge 2$ (so path counts grow strictly).
- **Bounds:** $0 < A_o < P_o$ for $o \ge 4$, with $A_3 = 0$ the unique zero.

**Step 6 — induction.** From the three lemmas, the recursion produces $A_{o+1} \ge 1$ for $o \ge 3$, with $A_{o+1} \le P_o - 1 < P_{o+1}$ preserved. The bound $A_o < P_o$ for $o \ge 3$ rules out any second cancellation: $o = 3$ is structurally unique.

## What this is *not*

The closed form is not RH for any classical L-function. The Hecke L-function $L(s, \chi_6)$ on $\mathbb{Z}[\omega]$ has its own zeros. The closed form is about the **orbit-twisted partial sum**, which is a different object: a character sum restricted to the *Collatz-orbit-pair image* in $\mathbb{Z}[\omega]$, not over all ideals.

The natural full L-function for Collatz would be

$$L_{\text{Collatz}}(s, \chi_6) = \sum_{n \text{ odd}} \frac{\chi_6(\iota_2(n))}{n^s}$$

with the closed form describing its partial sums one dropping set at a time. Its zeros, if it has interesting ones, would not be the zeros of the classical $L(s, \chi_6)$. I have not studied them.

## Implications

**The character $\chi_6$ is not blind to Collatz.** Restricted to a dropping set, the character sum is far from random: it has an explicit size and a phase fixed by the Sturmian word of $\log_2 3$.

**The structure is combinatorial.** The closed form depends only on the Beatty boundary $B_j = \lfloor j \log_2 3 \rfloor$ and counts of lattice paths below it (the admissible parity words of OEIS A100982).

**It says nothing about convergence.** The formula is stated in terms of the numbers that *do* drop, so it is equally consistent with the conjecture being true or false.

## Related

- [The Transfer Operator](/connections/hilbert-polya) — the critical circle $(4/3)^{1/3}$ and where the eigenvalue equation comes from
- [Eisenstein Lattice](/connections/eisenstein) — why $\mathbb{Z}[\omega]$ is the right number ring for the Collatz dynamics
- [The Hidden Rotation](/journey/the-rotation) — Sturmian dynamics of $\log_2 3$, the same irrational that appears here
