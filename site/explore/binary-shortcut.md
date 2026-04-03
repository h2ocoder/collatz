# The Binary Shortcut

## The Discovery

There's a shortcut for computing Collatz steps using binary arithmetic, discovered through pattern exploration:

1. Take an odd number $n$ and write it in binary
2. Count the **trailing 1-bits** (from the right). Call this $m$.
3. Split the binary string: $S_0$ = the left part, $S_1$ = the trailing 1s
4. Compute: $k = \text{decimal}(S_0) + 1$
5. **Result** = $k \times 3^m - 1$

This gives you the value after $m$ applications of the shortcut map $(3n+1)/2$, **skipping all the intermediate steps**.

## Worked Example: n = 27

$27 = 11011_2$

Trailing 1-bits: **11** (two 1s, so $m = 2$)

Split: $S_0 = $ "110" (decimal 6), $S_1 = $ "11"

$k = 6 + 1 = 7$

**Result** $= 7 \times 3^2 - 1 = 7 \times 9 - 1 = 62$

Verify with step-by-step $(3x+1)/2$:
- $27 \to (3 \times 27 + 1)/2 = 82/2 = 41$
- $41 \to (3 \times 41 + 1)/2 = 124/2 = 62$ ✓

The shortcut jumped from 27 straight to 62, skipping 41 entirely.

## More Examples

| $n$ | Binary | Trailing 1s | $k$ | Formula | Result | Verification |
|-----|--------|-------------|-----|---------|--------|-------------|
| 3 | 11 | 2 | 1 | $1 \times 9 - 1$ | **8** | $3 \to 5 \to 8$ ✓ |
| 7 | 111 | 3 | 1 | $1 \times 27 - 1$ | **26** | $7 \to 11 \to 17 \to 26$ ✓ |
| 15 | 1111 | 4 | 1 | $1 \times 81 - 1$ | **80** | $15 \to 23 \to 35 \to 53 \to 80$ ✓ |
| 27 | 11011 | 2 | 7 | $7 \times 9 - 1$ | **62** | $27 \to 41 \to 62$ ✓ |
| 31 | 11111 | 5 | 1 | $1 \times 243 - 1$ | **242** | $31 \to 47 \to \cdots \to 242$ ✓ |

Notice the all-1s numbers ($3, 7, 15, 31, \ldots = 2^k - 1$): they always give $k = 1$, so the result is $3^m - 1$.

## Why It Works: The Algebra

The formula has a clean algebraic form. If $n$ has $m$ trailing 1-bits, then:

$$n = 2^m \cdot q + (2^m - 1)$$

where $q = \lfloor n / 2^m \rfloor$ (the bits to the left of the trailing 1s, i.e., $S_0$).

Each application of $(3x+1)/2$ to an odd number $x$ gives $(3x+1)/2$. After $m$ applications:

$$\text{result} = (q + 1) \times 3^m - 1 = \frac{n + 1}{2^m} \times 3^m - 1 = (n+1) \times \left(\frac{3}{2}\right)^m - 1$$

<div class="proof">

**Proof by induction on $m$.**

**Base** ($m = 1$): $n = 2q + 1$ (one trailing 1).
$(3(2q+1)+1)/2 = (6q+4)/2 = 3q+2 = 3(q+1) - 1$. ✓

**Step** ($m \to m+1$): $n = 2^{m+1}q + (2^{m+1} - 1)$ has $m+1$ trailing 1s.

After one $(3x+1)/2$: $(3n+1)/2 = 3 \cdot 2^m(q+1) - 1$

This equals $2^m \cdot [3(q+1)] + (2^m - 1) - 2^m$... more cleanly, it has $m$ trailing 1s with left part $q' = 3(q+1) - 1$.

By the inductive hypothesis, $m$ more steps give: $(q'+1) \times 3^m - 1 = 3(q+1) \times 3^m - 1 = (q+1) \times 3^{m+1} - 1$. ✓

</div>

## Connection to the Affine Orbit Structure

This shortcut is a **special case** of the [Affine Orbit Structure](/proofs/affine-orbit) theorem:

$$\text{dest}(n) = \frac{3^s}{2^{k-s}} \cdot n + C$$

The shortcut handles the case where $s = m$ (odd steps) and $k - s = m$ (even steps), i.e., $k = 2m$. Each odd step has alpha value $\alpha = 1$ (exactly one halving), so the contraction ratio is $(3/2)^m$.

The general theorem allows *any* sequence of alpha values — some steps might halve once ($\alpha = 1$), others might halve many times ($\alpha = 4, 5, \ldots$). The binary shortcut handles the specific case where all the halvings are singles.

## Why Trailing 1s Matter

The trailing 1-bits in binary encode the **2-adic structure** of $n$:

- Each trailing 1 means "the next $(3x+1)/2$ gives an odd result" (so we continue)
- The first 0 means "the result will be even" (so we stop and halve)

This is the **bit consumption** property from the affine orbit proof: the last $m$ bits of $n$ determine the first $m$ steps of the orbit. Trailing 1s = consecutive odd steps = consecutive $\alpha = 1$ values in the [alpha sequence](/explore/alpha-sequence).

| Trailing bits | Orbit behavior | Alpha values |
|--------------|----------------|--------------|
| ...0**1** | One odd step, then even | $[\alpha_1]$ where $\alpha_1 \geq 1$ |
| ...0**11** | Two odd steps, then even | $[1, \alpha_2]$ where $\alpha_2 \geq 1$ |
| ...0**111** | Three odd steps, then even | $[1, 1, \alpha_3]$ where $\alpha_3 \geq 1$ |
| ...0**1111** | Four odd steps, then even | $[1, 1, 1, \alpha_4]$ |

The binary shortcut processes the entire run of $\alpha = 1$ values in one shot. The general [affine structure](/proofs/affine-orbit) handles arbitrary alpha sequences.

## Try It

Enter an odd number to see the binary shortcut in action:

<BinaryShortcut />
