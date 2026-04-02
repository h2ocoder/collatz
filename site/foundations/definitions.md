# Core Definitions

This page collects the formal definitions used throughout the site. Each definition includes a worked example. The notation follows Paper 1 (dropping) conventions; see the [Terminology Map](./terminology) for equivalences with Paper 2 (stopping).

## Collatz Step

<div class="theorem">

**Definition 1 (Collatz Step).** The Collatz function $f : \mathbb{Z}^+ \to \mathbb{Z}^+$ is defined by

$$
f(n) = \begin{cases} n/2 & \text{if } n \text{ is even} \\ 3n+1 & \text{if } n \text{ is odd} \end{cases}
$$

</div>

**Example.** $f(7) = 3(7)+1 = 22$ (odd rule), then $f(22) = 22/2 = 11$ (even rule).

## Orbit

<div class="theorem">

**Definition 2 (Orbit).** The *orbit* of $n$ is the sequence obtained by iterating $f$ until reaching 1:

$$
\text{orbit}(n) = [n,\; f(n),\; f^2(n),\; \ldots,\; 1]
$$

</div>

**Example.** The orbit of 6 is $[6, 3, 10, 5, 16, 8, 4, 2, 1]$.

## Dropping Time

<div class="theorem">

**Definition 3 (Dropping Time).** The *dropping time* of $n > 1$ is the smallest $k \geq 1$ such that $f^k(n) < n$:

$$
\text{drop}(n) = \min\{k \geq 1 : f^k(n) < n\}
$$

This is identical to the *stopping time* in Paper 2.

</div>

**Example.** For $n = 5$: $f(5) = 16$, $f^2(5) = 8$, $f^3(5) = 4$. Since $4 < 5$ and this is the first value below 5, the dropping time is 3.

## Dropping Destination

<div class="theorem">

**Definition 4 (Dropping Destination).** The *dropping destination* of $n$ is the first iterate that falls below $n$:

$$
\text{dest}(n) = f^{\text{drop}(n)}(n)
$$

</div>

**Example.** The dropping destination of 5 is $f^3(5) = 4$.

## Dropping Orbit

<div class="theorem">

**Definition 5 (Dropping Orbit).** The *dropping orbit* of $n$ is the segment of the orbit from $n$ up to (but not including) the dropping destination $d$:

$$
\text{dorbit}(n) = [n,\; f(n),\; \ldots,\; 2d]
$$

It includes $n$ and excludes the destination. Its length equals the dropping time.

</div>

**Example.** The dropping orbit of 5 is $[5, 16, 8]$ (length 3). The destination $4$ is excluded.

For $n = 3$: orbit proceeds $3 \to 10 \to 5 \to 16 \to 8 \to 4$, and the destination is $2 < 3$. The dropping orbit is $[3, 10, 5, 16, 8, 4]$ (length 6).

## Dropping Set

<div class="theorem">

**Definition 6 (Dropping Set).** The *dropping set* $\text{Dset}_k$ is the set of all positive integers with dropping time $k$:

$$
\text{Dset}_k = \{n \in \mathbb{Z}^+ : \text{drop}(n) = k\}
$$

Each dropping set is a union of arithmetic progressions.

</div>

**Example.**
- $\text{Dset}_1$ = all even numbers $\{2, 4, 6, 8, \ldots\}$, since one halving gives $n/2 < n$.
- $\text{Dset}_3 = \{5, 9, 13, 17, \ldots\} = \{n : n \equiv 1 \pmod{4}\}$.

## Orbital Oddity

<div class="theorem">

**Definition 7 (Orbital Oddity).** The *orbital oddity* of $n$ is the count of odd numbers in its dropping orbit. All members of $\text{Dset}_k$ share the same orbital oddity $s$.

</div>

**Example.** The orbital oddity of 3 is 2. Its dropping orbit is $[3, 10, 5, 16, 8, 4]$, which contains two odd values: 3 and 5.

## Syracuse Map

<div class="theorem">

**Definition 8 (Syracuse Map).** The *Syracuse map* $S : \mathbb{Z}_{\text{odd}}^+ \to \mathbb{Z}_{\text{odd}}^+$ compresses each $3n+1$ step and all subsequent halvings into a single operation:

$$
S(n) = \frac{3n+1}{2^{v_2(3n+1)}}
$$

where $v_2(m)$ is the 2-adic valuation of $m$ (the largest power of 2 dividing $m$).

</div>

**Example.** $S(7) = \frac{3(7)+1}{2^{v_2(22)}} = \frac{22}{2^1} = 11$, since $22 = 2 \cdot 11$.

## Alpha Value

<div class="theorem">

**Definition 9 (Alpha Value).** For odd $n$, the *alpha value* is the 2-adic valuation of $3n+1$:

$$
\alpha(n) = v_2(3n+1)
$$

This counts how many halvings follow the $3n+1$ step in the Syracuse map.

</div>

**Example.** $\alpha(5) = v_2(16) = 4$, since $3(5)+1 = 16 = 2^4$.

## Alpha Sequence

<div class="theorem">

**Definition 10 (Alpha Sequence).** The *alpha sequence* of an odd number $n$ is the sequence of alpha values along its Syracuse orbit until reaching 1:

$$
\alpha\text{-seq}(n) = [\alpha(n),\; \alpha(S(n)),\; \alpha(S^2(n)),\; \ldots]
$$

The sequence terminates when the Syracuse orbit reaches 1.

</div>

**Example.** The alpha sequence of 3 is $[1, 4]$:
- $S(3) = (3 \cdot 3 + 1)/2^1 = 5$, so $\alpha(3) = 1$
- $S(5) = (3 \cdot 5 + 1)/2^4 = 1$, so $\alpha(5) = 4$

The alpha sequence of 7 is $[1, 1, 1, 3, 4]$.
