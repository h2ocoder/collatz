# Twin Primes in Dropping Orbits

**Question:** Can two twin primes $(p, p+2)$ both appear inside a single Collatz
[[Dropping Sets|dropping orbit]], and if so, is there a signature that explains
which pairs do?

**Answer (this note):** Yes, but the set is almost empty. Searched exhaustively
to $10^9$, the *only* twin primes that share a dropping orbit are $(3,5)$ and
$(11,13)$. The 1-step and 2-step cases are **proved** to be the only short-path
sources of these, and longer paths produce nothing up to the search bound.

---

## The co-occurrence criterion

A dropping orbit of $n$ is the trajectory $[n, f(n), \dots, 2d]$ until the first
value $d < n$ (the *destination*, which is **excluded**). So two values share a
dropping orbit iff they lie on one forward trajectory, both $\ge$ the seed, with
neither being the excluded destination.

For twins this collapses to a one-directional condition:

> **$p$ and $p+2$ share a dropping orbit $\iff$ $p$ reaches $p+2$ under the
> Collatz map with every intermediate value $\ge p$.**

Then $p+2$ sits *inside* $\text{dropping\_orbit}(p)$ (it is reached before the
first drop below $p$). The **descending** direction does *not* count: if $p+2$
falls to $p$, then $p$ is the orbit's excluded destination. Concretely, $7 \to
22 \to 11 \to 34 \to 17 \to 52 \to 26 \to 13 \to 40 \to 20 \to 10 \to 5$ reaches
$5$, but $5$ is $7$'s destination, so $5$ and $7$ do **not** co-occur. (This
false lead was caught by cross-checking against direct `dropping_orbit`
membership.)

The two real pairs:

- $(3,5)$:  $3 \to 10 \to 5$ — odd path $3 \to 5$ (**1 odd step**)
- $(11,13)$: $11 \to 34 \to 17 \to 52 \to 26 \to 13$ — odd path $11 \to 17 \to 13$ (**2 odd steps**)

---

## The path-length theorem (proved for $k \le 2$)

Write the **Syracuse map** on odds as $T(m) = (3m+1)/2^{a}$, where
$a = v_2(3m+1) \ge 1$. We ask when $T^{k}(m) = m+2$.

**$k=1$.** $3m+1 = 2^a(m+2)$.
- $a=1$: $3m+1 = 2m+4 \Rightarrow m = 3$.
- $a \ge 2$: $m(3-2^a) = 2^{a+1}-1$ has a negative coefficient on a positive
  right side, so $m<0$.

  $\boxed{m=3 \text{ only}}$ — i.e. the **only** adjacent odd pair differing by
  $+2$ anywhere in any Collatz orbit is $3 \to 5$.

**$k=2$.** With $m \to q \to m+2$, $q=(3m+1)/2^{a}$, $m+2=(3q+1)/2^{b}$,
eliminating $q$ gives
$$m\,(2^{a+b} - 9) = 2^{a} + 3 - 2^{a+b+1}.$$
If $a+b \ge 4$ the left coefficient is positive, so we would need $2^{a}+3 >
2^{a+b+1}$; but $b \ge 1$ forces $2^{a+b+1} \ge 4\cdot 2^{a} > 2^{a}+3$,
impossible. Hence $a+b \le 3$, leaving $(a,b) \in \{(1,1),(1,2),(2,1)\}$:
- $(1,1)$: $-5m = -3 \Rightarrow m = 3/5$ — none.
- $(1,2)$: $-m = -11 \Rightarrow m = 11$ — the path $11\to17\to13$. ✓
- $(2,1)$: $-m = -9 \Rightarrow m = 9$ — the path $9 \to 7 \to 11$.

  $\boxed{m \in \{9, 11\}}$. But $9 \to 7$ **dips below $9$**, so $9$ never
  reaches $11$ within its dropping orbit; only $m=11$ keeps the path $\ge m$.

**Selecting twins.** Requiring $m, m+2$ both prime kills $m=9$ (composite, and
it dips anyway), leaving exactly $m=3$ ($k=1$) and $m=11$ ($k=2$). These are
$(3,5)$ and $(11,13)$.

**$k \ge 3$.** $T^{k}(m)=m+2$ has *no* solutions for $k=3,4$ up to $10^7$, and
the full search below finds no twin co-occurrence beyond the two. Heuristic for
why none should exist: a length-$k$ return to $m+2$ needs $2^{\sum a_i}$ within a
factor $1+O(1/m)$ of $3^{k}$; Baker-type lower bounds on
$|\sum a_i \log 2 - k \log 3|$ make such near-coincidences rare, the admissible
$m$ bounded and sparse, and the count over twin primes a convergent sum — so
**finitely many overall**, empirically just two.

---

## Empirical confirmation

`scripts/twin_dropping_orbit_search.py` (segmented sieve + exact Collatz walk,
staying $\ge p$) to $N = 10^9$:

```
      (p, p+2)   steps  p mod 8
        (3, 5)       2        3
      (11, 13)       5        3
Total co-occurring twin pairs up to 1000000000: 2
```

Cross-checked against direct `dropping_orbit(n)` membership for all seeds
$n \le 2\times10^5$: same two pairs, no others (this is what exposed the
descending false positive $(5,7)$).

**A curiosity:** both sources have $p \equiv 3 \pmod 8$. With two data points
this is a thread, not a claim — but $3$ and $11$ are the two smallest
$3 \bmod 8$ values, and they are precisely the $k=1$ and $k=2$ solutions.

---

## Relation to the dropping *set* restriction

The companion question — which primes appear in a dropping **set** $D_k$ — has a
clean residue answer from [[Prime Dropping Residues]]: primes in $D_k$ are
exactly the primes whose residue mod $2^k$ lies in the coprime residue set
$R_k$. E.g. the only prime in $D_1$ is $2$, and the primes in $D_3$ are
*precisely* the primes $\equiv 1 \pmod 4$. That is a statement about *membership
in a class*; this note is about *co-occurrence on one trajectory* — a strictly
finer relation.

---

## Conjecture and status

> **Conjecture.** The only twin primes that share a Collatz dropping orbit are
> $(3,5)$ and $(11,13)$.

- **Proved:** these are the *only* pairs arising from odd-paths of length
  $\le 2$ (the theorem above).
- **Verified:** no other pair up to $10^9$; no length-3 or length-4 path source
  up to $10^7$.
- **Open:** ruling out all longer paths is entangled with $2^x$ vs $3^y$
  separation (linear forms in logarithms) and is not settled here.

**Related:** [[Prime Dropping Residues]], [[Prime Constellation Signatures]],
[[Collatz as a Quasicrystal]], [[Dropping Zeta Spectrum]].
