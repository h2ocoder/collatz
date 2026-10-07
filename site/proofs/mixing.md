# Mixing Modulo Powers of Two

This page collects two elementary facts about how drops spread numbers over residue classes, and one measurement. The facts are classical; the measurement is mine. None of it says what an individual orbit must do.

## Destinations cover every residue class

From the [Affine Orbit Structure](/proofs/affine-orbit), within one residue class of $\text{Dset}_k$ (period $P = 2^{k-s}$):

$$\text{dest}(n_0 + P j) = \text{dest}(n_0) + 3^s j$$

Since $3^s$ is odd, it is invertible mod $2^B$. So as $j$ runs through $2^B$ consecutive values, the destinations run through **every** residue class mod $2^B$ exactly once. Starting points that agree on their low bits can land anywhere.

## The order of 3 modulo $2^B$

<div class="theorem">

**Theorem (classical).** For $B \geq 3$: $\text{ord}(3 \bmod 2^B) = 2^{B-2}$.

</div>

| $B$ | $2^B$ | $\text{ord}(3 \bmod 2^B)$ | Ratio |
|-----|-------|---------------------------|-------|
| 2 | 4 | 2 | 1/2 |
| 3 | 8 | 2 | 1/4 |
| 4 | 16 | 4 | 1/4 |
| 5 | 32 | 8 | 1/4 |
| 6 | 64 | 16 | 1/4 |
| 8 | 256 | 64 | 1/4 |
| 10 | 1024 | 256 | 1/4 |
| 12 | 4096 | 1024 | 1/4 |
| 16 | 65536 | 16384 | 1/4 |
| 20 | 1048576 | 262144 | 1/4 |

The ratio stabilizes at exactly $1/4$ for all $B \geq 3$: the powers of 3 reach exactly half of the odd residues mod $2^B$.

<div class="proof">

By lifting the exponent, for $j \geq 1$: $v_2(3^{2^j} - 1) = v_2(3 - 1) + v_2(3 + 1) + v_2(2^j) - 1 = 1 + 2 + j - 1 = j + 2$.

So $v_2(3^{2^{B-2} } - 1) = (B-2) + 2 = B$, confirming $3^{2^{B-2} } \equiv 1 \pmod{2^B}$.
And for $B \geq 4$, $v_2(3^{2^{B-3} } - 1) = (B-3) + 2 = B-1 < B$, so $3^{2^{B-3} } \not\equiv 1 \pmod{2^B}$; for $B = 3$ this is just $3 \not\equiv 1 \pmod 8$.

Since the order divides $2^{B-1}$ (the size of the group of odd residues), it is $2^{B-2}$.

</div>

### Powers of $3^s$

For **odd** $s$, $3^s$ has the same order as 3, so its powers reach the same half of the odd residues. For **even** $s$, the order drops by a factor $2^{v_2(s)}$:

| Set$_k$ | $s$ | $v_2(s)$ | Share of the powers of 3 reached by powers of $3^s$ |
|---------|-----|----------|----------------|
| 3 | 1 | 0 | 100% |
| 6 | 2 | 1 | 50% |
| 8 | 3 | 0 | 100% |
| 11 | 4 | 2 | 25% |
| 13 | 5 | 0 | 100% |
| 16 | 6 | 1 | 50% |
| 19 | 7 | 0 | 100% |
| 21 | 8 | 3 | 12.5% |

## Consecutive sets: independent in density

The covering fact has an exact consequence. Take one residue class of $\text{Dset}_k$ and any residue class $b \bmod 2^B$. Among the members $n_0 + Pj$ of the first class, the destination $\text{dest}(n_0) + 3^s j$ lands in $b \bmod 2^B$ for exactly one $j$ in every $2^B$. So the natural density of starting values that lie in the first class and whose destination lies in the second is the product of the two densities. Each dropping set agrees with a union of such classes apart from at most finitely many integers (see [Affine Orbit Structure](/proofs/affine-orbit)), so in the sense of density the dropping set of the destination is independent of the dropping set of the start.

A finite sample shows this only approximately. For $3 \le n < N$, I measured the mutual information between the dropping set of $n$ and the dropping set of its destination:

| $N$ | $H(\text{Set}_\text{next})$ | $H(\text{Set}_\text{next} \mid \text{Set}_\text{current})$ | $I(\text{Set}_\text{next}; \text{Set}_\text{current})$ |
|-----|-----|-----|-----|
| $5 \times 10^4$ | 2.356 bits | 2.343 bits | 0.013 bits |
| $5 \times 10^5$ | 2.361 bits | 2.358 bits | 0.003 bits |
| $5 \times 10^6$ | 2.362 bits | 2.361 bits | 0.0006 bits |

The measured value is not a constant of the map: it keeps shrinking as the sample grows, as sampling noise around zero would.

## What this does not show

These are statements about **averages over residue classes**. They do not stop a particular orbit from landing in slow sets many times in a row — for example, 294583 → 248555 → 209719 → 176951 → 149303 → 125975 → 106292 is six consecutive drops, every one of them through Set₈. And the same residue-class facts hold for the negative integers, where the rule has cycles. The classical "almost all" results are proved by other, more careful arguments, and they stop short of "almost every orbit reaches 1": Terras (1976) showed that almost every $n$ (natural density 1) eventually falls below its starting value, and Tao (2019) that almost every orbit (in logarithmic density) attains almost bounded values.

## Related

- [Affine Orbit Structure](/proofs/affine-orbit) — where the $3^s j$ shift comes from
- [Bit Destruction](/proofs/bit-destruction) — the size of each drop
