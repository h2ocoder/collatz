---
tags: [collatz, literature, 3x+k, rational-cycles, cycle-bounds, diophantine, 5x+1, divergence, log2-3, oeis]
status: literature-survey
created: 2026-09-17
---

# Literature — 3x+k Cycles and Divergence

**Question.** The repo found (verified) that every residue class of the 3x+1 stopping-time sets has an affine intercept $r(v)$ that is the smallest element of a primitive cycle of $T_k(x) = x/2 \mid (3x+k)/2$ with $k = 2^b - 3^s$ (OEIS A226607, [[Primes and the Circuit]] §6). What does the literature say about (a) why $3x+1$ is special, (b) why other $3x+k$ have cycles, (c) why some maps blow up? This note is the source base for [[Why 3x+1 is Special]].

Every citation below was checked against the source (primary text, or Lagarias's own annotated bibliographies [3][5] where the primary is paywalled or bot-walled). Where I could not read the primary, I say so inline. Three claims were also re-derived numerically here (marked **Verified here**): scripts are inline in the text, results quoted.

**Bottom line in one paragraph.** For a parity word $v$ of length $b$ with $s$ odd steps, the cycle equation is $x_0 = k\,\varphi(v)/(2^b - 3^s)$ with $\varphi(v)$ a positive integer built from $v$ [1][10][11]. A $3x+k$ cycle of type $(b,s)$ exists iff $(2^b - 3^s) \mid k\,\varphi(v)$. For $k = 2^b - 3^s$ (or a small divisor of it) *every* necklace of type $(b,s)$ is a cycle — this is exactly why A226613 record-holders are numbers $2^b - 3^s$ [9][21], and it is the mechanism behind the repo's intercept correspondence. For $k = 1$ the only Diophantine freebie is $2^2 - 3^1 = 1$ (the trivial cycle); any other cycle needs $2^b - 3^s$ to divide $\varphi(v)$, which forces $b/s$ to be a continued-fraction-quality approximation to $\log_2 3$, and the verification bound $2^{71}$ [17] then pushes any cycle past $10^{11}$ steps [14][16]. Divergence is a different question with a different answer: the drift per Terras step is $\tfrac12\log_2 p - 1$, negative for $p=3$ and positive for every $p \ge 5$; $k$ does not enter [12][18]. So: no divergence expected for any $3x+k$ (Lagarias's $3x+k$ conjecture [1][4]); divergence expected for every $px+1$, $p \ge 5$ (Crandall's conjecture [12]); the only thing that is "special" about $k=1$ is that its cycle count is conjecturally minimal, and that is a Diophantine fact about $2^b - 3^s = 1$.

---

## 0. Setup and the cycle equation (Böhm–Sontacchi 1978; Lagarias 1990)

Write $T_k(x) = x/2$ if $x$ even, $(3x+k)/2$ if $x$ odd, for odd $k$ with $\gcd(k,6)=1$ (the "3x+k function" $T_{3,k}$ in Lagarias's notation [4]). A parity word $v = (v_1,\dots,v_b) \in \{0,1\}^b$ with $s = \sum v_j$ ones composes to an affine map [10, Lemma 2, attributed to Lagarias [1]]:

$$\phi_v(x) = \frac{3^s x + \varphi(v)}{2^b}, \qquad \varphi(v) = \sum_{j=1}^{b} v_j\, 3^{\,v_{j+1}+\dots+v_b}\, 2^{\,j-1},$$

so the unique fixed point (for $k=1$; multiply by $k$ for $T_k$) is

$$x_0 = \frac{k\,\varphi(v)}{2^b - 3^s}.$$

Böhm–Sontacchi [11] wrote the same thing as "a rational number $x$ in a cycle of period $n$ has the form $x = \sum_{k=0}^{m-1} 3^{m-k-1}2^{v_k} / (2^n - 3^m)$" and deduced that every integer in a cycle of length $n$ has $|x| < 3^n$ and that there are at most $2^n$ cycles of period $n$ [3, #26]. This is the whole algebra; everything below is number theory applied to it.

**Verified here.** For all 80 values $k < 234$ with $\gcd(k,6)=1$, I found every primitive $T_k$ cycle with minimum below $2\times10^5$, read off its word $(b,s)$, and checked $(2^b-3^s) \mid k\,\varphi(v)$ and $\min = k\,\varphi_{\min}/(2^b-3^s)$: 0 violations across all cycles (e.g. $k=5$: words $(3,1),(5,3),(5,3),(27,17),(27,17)$ with $2^b-3^s = 5,5,5,5077565,5077565$; $k=233$: 19 cycles, matching A226613). The $5x+1$ cycle $\{13,33,83,208,104,52,26\}$ has $(b,s)=(7,3)$ and $2^7 - 5^3 = 3$, exactly Crandall's remark [12, §8].

In the repo's language: $r(v) = \varphi_{\min}(v)$, and the intercept correspondence of [[Primes and the Circuit]] is the statement that the affine intercept of a residue class *is* the Lagarias numerator of its parity word.

---

## 1. Lagarias 1990 — the set of rational cycles [1]

I could not read the full text (IMPAN/EUDML/matwbn all serve a bot wall to non-browser fetches). What follows is Lagarias's own annotation of the paper [3, #108] plus his 2010 restatement [4, §4]; both are by the author, so I treat them as authoritative summaries.

**Correspondence.** "This paper studies the sets of those integer cycles of $T_k(x)$ ... for positive $k \equiv \pm1 \pmod 6$ which have $(x,k)=1$. These correspond to rational cycles $x/k$ of the $3x+1$ function $T$" [3, #108]. In [4, §4]: "the $3x+1$ function $T(x)$ can be extended to be well defined on the set of all rational numbers having odd denominator, and a rescaling of any $T$-orbit of such a rational number $r = n/k$ to clear its denominator $k$ will give an orbit of the map $T_{3,k}$. Thus, integer cycles of the $3x+k$ function correspond to rational cycles of the $3x+1$ function having denominator $k$." A $T_k$-cycle is **primitive** if its elements are all coprime to $k$, "or, equivalently, if its elements are not a common multiple of the elements of another cycle" [21, A226607 quoting [1]]. The non-primitive cycles of $T_{k}$ are just the cycles of $T_{k/d}$ scaled by $d$; $S(3t) = S(1)$ in Simons–de Weger's invariant [5, #100].

**Theorems (as annotated by the author) [3, #108].**
- "It shows that infinitely many $k$ have at least $k^{1-\epsilon}$ distinct such cycles of period at most $\log k$" — so the cycle count is unbounded in $k$, and it is achieved with *short* words, i.e. by $k \mid 2^b - 3^s$ with small $b$ (see §6).
- "and infinitely many $k$ have no such cycles having period length less than $k^{1/3}$" — so cycles can also be forced to be long.
- "Estimates are given for the counting function $C(k,y)$ counting the number of such cycles of $T_k$ of period $\le y$, for all $k \le x$ with $y = \beta\log x$. In particular $C(k, 1.01k) \le 5k(\log k)^5$."

**Conjectures.** "It conjectures that every $T_k$ has such an integer cycle" [3, #108] (i.e. $\ge 1$ primitive cycle for every $k$ coprime to 6). And the two-part "$3x+k$ conjecture" [4, §4]: "The generalization of the $3x+1$ conjecture to this situation is twofold: first, that under iteration every orbit becomes eventually periodic, and second, that there are only a finite number of cycles (periodic orbits)." **No divergent orbits for any $3x+k$** is therefore an explicit Lagarias conjecture, and Lagarias calls $3x+k$ "the correct level of generality for studying rational cycles of the $3x+1$ function" [4, §6.2].

**1985 survey [2].** The Monthly survey contains the 3/4 heuristic (§2.1: "this heuristic argument suggests that on average the iterates in a trajectory tend to shrink in size, so that divergent trajectories should not exist"; attributed to Crandall [12]), the Böhm–Sontacchi cycle equation, Steiner's circuit theorem, Crandall's cycle bound, and a "periodically linear functions" generalization framework in §3 (Conway's class). I read the section pages node3/node8/node9/node11 at cecm.sfu.ca; the 5x+1 material in the 1985 paper is thinner than in [12] and [18], which I use instead.

---

## 2. Belaga & Mignotte — the 3x+d programme [6][7][8][9]

**[6] Belaga & Mignotte, "Embedding the 3x+1 conjecture in a 3x+d context", Experimental Math. 7 (1998) 145–151.** Lagarias's annotation [3, #18] (he dates it 1999; the journal issue is 1998): "It proves that there is an absolute constant $c$ such that there are at most $dk^c$ periodic orbits which contain at most $k$ odd integers. Furthermore $c$ is effectively computable. This follows using a transcendence result of Baker and Wüstholz [J. reine Angew. 442 (1993), 19–62]." This is the first *polynomial-in-$d$* bound on the number of $3x+d$ cycles of bounded odd-length, and the first place Baker's method is applied to $3x+d$ for general $d$. I could not access the Experimental Math. full text (Project Euclid returned the adjacent article; tandfonline 403).

**[8] Belaga, "Effective polynomial upper bounds to perigees and numbers of (3x+d)-cycles of a given oddlength", Acta Arith. 106 (2003) 197–206.** Annotation [5, #11]: for any cycle $C$ of the $3x+d$ map of length $l$ with $k$ odd elements, the smallest element ("perigee") satisfies
$$\operatorname{prg}(C) \le \frac{d}{2^{l/k} - 3}, \qquad\text{hence}\qquad \log_2 3 < \frac{\text{length}(C)}{\text{oddlength}(C)} \le \log_2(d+3),$$
the upper bound sharp; the number $U_{d,k}$ of cycles of odd-length $k$ is at most $dk^{c_0}$ with $c_0 = 32$ admissible (linear forms in logarithms), and the largest element is $< dk^{c_0}(3/2)^k$. The perigee bound is the $3x+d$ form of the Diophantine mechanism in §3: a cycle with small perigee needs $2^{l/k}$ close to 3, i.e. $l/k$ close to $\log_2 3$.

**[7] Belaga & Mignotte, "Cyclic structure of dynamical systems associated with 3x+d extensions of Collatz problem", U. Strasbourg preprint 2000-18 (hal-00129656), 57 pp.** Annotation [5, #10]: "a theoretical and experimental study of the distribution of number and lengths of finite cycles to the $3x+d$ map, for $d \equiv \pm1 \pmod 6$. It contains much data and a wealth of interesting results and conjectures." From the HAL abstract as quoted in search results (the HAL page itself is Anubis-walled): they computed "the complete list of primitive cycles" for "every one of 6667 systems $D_d$ with $1 \le d \le 19999$", state that "the calculations confirm two long-standing conjectures of Lagarias from 1990" (every $d$ has a primitive cycle; finitely many), and formulate the **$3x+d$ hypothesis**: "$D_d$ has a finite number of cycles and no divergent trajectories." (Wording from the HAL abstract via search; I did not read the 57-page PDF.)

**[9] Belaga & Mignotte 2006.** (a) "Walking cautiously into the Collatz wilderness", DMTCS Proc. AG (2006) 249–260 — open questions and new conjectures; (b) "The Collatz problem and its generalizations: Experimental data. Table 1. Primitive cycles of 3x+d mappings", Strasbourg preprint 2006-015 — tables for $1 < d < 20000$, "the authors conjecture they obtain the complete list"; (c) "Table 2. Factorization of Collatz numbers $2^l - 3^k$", preprint 2006-018 — "known divisors of numbers of form $D = 2^l - 3^k$ for $l \le 114$. Numbers $D$ of this form give $3x+D$ problems having many primitive cycles" [5, #12–14]. That last sentence is the literature's statement of the mechanism in §6.

---

## 3. Cycle impossibility for 3x+1 — the Diophantine argument [11][12][13][14][10][15][16][17]

### 3.1 The mechanism, cleanly

Let $C$ be a nontrivial positive cycle of $T = T_1$ with word $(b,s)$ and minimum $m$. From §0, $m = \varphi_{\min}/(2^b - 3^s)$ with $2^b > 3^s$. Two inequalities [14][10]:

1. Every odd step multiplies by $\tfrac{3x+1}{2x} \le \tfrac{3 + 1/m}{2}$ and every even step by $\tfrac12$; around the cycle the product is 1, so $2^b \le (3+1/m)^s$, i.e.
$$\log_2 3 < \frac{b}{s} \le \log_2\!\Big(3 + \frac1m\Big) = \log_2 3 + O\!\Big(\frac{1}{m}\Big).$$
(Chamberland's summary of Eliahou [23]: $\log_2(3 + 1/M) \le |C|/|C_{\text{odd}}| \le \log_2(3 + 1/m)$ with $M$ the maximum.)
2. The verification bound: $m > X_0$ where the conjecture is checked up to $X_0$.

Together: $b/s$ lies in an interval of width $\approx 1/(3 X_0 \ln 2)$ just above $\log_2 3$. By the theory of continued fractions, a fraction in an interval that narrow must have denominator at least that of the appropriate convergent/intermediate fraction of $\log_2 3$. The continued fraction of $\log_2 3$ is $[1;1,1,2,2,3,1,5,2,23,2,2,1,1,55,1,\dots]$ with convergents $1/1, 2/1, 3/2, 8/5, 19/12, 65/41, 84/53, 485/306, 1054/665, 24727/15601, 50508/31867, 125743/79335, 176251/111202, 301994/190537, 16785921/10590737, 17087915/10781274, \dots$ (the same expansion that drives [[Trit Packing and log2(3)]] and the odd stopping-time spectrum in [[Collatz Bridge - Trits and Stopping Times]]).

**Verified here.** Taking the smallest-denominator fraction in $(\log_2 3, \log_2(3+1/X_0))$ (Stern–Brocot search, 80-digit arithmetic):

| $X_0$ | minimal $s$ (odd steps) | minimal $b$ (T-steps) | literature |
|---|---|---|---|
| $2^{40}$ | 10,781,274 | **17,087,915** | Eliahou 1993 [14]: exactly 17,087,915 |
| $3\cdot 2^{50}$ | 118,212,940 | **187,363,077** | Tempkin–Arteaga 1997 as quoted in [23]: 187,363,077 |
| $704\cdot 2^{60}$ | **72,057,431,991** | 114,208,327,604 | Hercher [16]: "the current $K > 7.2\cdot10^{10}$" odd steps |
| $2^{71}$ (Barina 2025) | 72,057,431,991 | 114,208,327,604 | plateau until the next convergent |

So the crude criterion reproduces the published numbers to the digit, and the reason the numbers jump in discrete steps is that they *are* denominators of convergents/intermediate fractions of $\log_2 3$. That is the sense in which "$3x+1$ needs a Diophantine miracle": a nontrivial cycle would exhibit a rational approximation $b/s$ to $\log_2 3$ with error $< 10^{-22}$, which exists only at $s \gtrsim 7\times10^{10}$.

### 3.2 The results, in order

- **Böhm–Sontacchi 1978 [11]** — cycle equation and $|x| < 3^n$; at most $2^n$ cycles of period $n$ [3, #26].
- **Crandall 1978 [12]** — Theorem 7.3: "Assume $m > 1$ and $C^k(m) = m$. Then $k > 17985$" (here $k$ counts *odd* steps of the accelerated map, using verification to $10^9$ and convergents $q_{10}=31867$, $q_{11}=79335$). He also "establishes a connection between the validity of the conjecture and the diophantine equation $2^x - 3^y = p$" (abstract). Lagarias 1985 [2, node8] restates this as: nontrivial cycles have period $> 275{,}000$ using convergents of $\log_2 3$ (note the 1985 figure uses $T$-steps and a later verification bound).
- **Steiner 1977/78 [13]** — "the only circuit on the positive integers that is a cycle is $\{1,2\}$", via the exponential Diophantine equation $(2^{k+l} - 3^k)h = 2^l - 1$ [3, #158], solved with Baker's method; the first transcendence-theory result on the problem. His $Qx+1$ sequels [22] show the only circuit-cycle for $Q=5$ is $\{13,208\}$ and none exists for $Q=7$.
- **Eliahou 1993 [14]** — exact statement [3, #53]: "any nontrivial cycle on $\mathbb Z^+$ of the $3x+1$ function $T(x)$ has period $p = 301994A + 17087915B + 85137581C$ with $A,B,C$ nonnegative integers where $B \ge 1$, and at least one of $A$ or $C$ is zero. Hence the minimal possible period length is at least 17087915. The method uses the continued fraction expansion of $\log_2 3$, and the truth of the $3x+1$ Conjecture for all $n < 2^{40}$." The three generators are numerators of a convergent and two neighbouring semiconvergents of $\log_2 3$: $301994/190537$ (convergent), $17087915/10781274 = (16785921 + 301994)/(10590737 + 190537)$ (convergent), and $85137581/53715833 = (5\cdot17087915 - 301994)/(5\cdot10781274 - 190537)$ (semiconvergent) — **verified here**. Any fraction $b/s$ in the narrow admissible interval is a nonnegative integer combination of the Farey neighbours bounding it, which is exactly the "$A,B,C$ with $B \ge 1$, $AC = 0$" form.
- **Halbeisen–Hungerbühler 1997 [10]** — optimal bound on the minimum of a rational cycle of type $(b,s)$ in terms of the extremal word $\tilde s(l,n)$ (the "most balanced" word, $\tilde s_i = \lfloor in/l\rfloor - \lfloor (i-1)n/l\rfloor$); improved Eliahou's criterion so that verification to $2.1\times10^{14}$ gives cycle length $\ge 102{,}225{,}496$. Their closing remark (their (A')): the $3x+1$ cycle conjecture fails iff there is a non-periodic word $s$ with $\gcd\{\varphi(t) : t \in \sigma(s)\} = 2^{l(s)} - 3^{n(s)}$ — i.e. iff $2^b - 3^s$ divides *all* rotations' numerators. This is the $k=1$ case of the §6 criterion.
- **Simons–de Weger 2005 [15]** — an **$m$-cycle** is a cycle with $m$ local minima ($m$ blocks of consecutive odd steps). Main results [5, #101]: for each fixed $m$ there are finitely many $m$-cycles (Brox 2000 earlier); no nontrivial $m$-cycles for $1 \le m \le 68$ (later 74, then 76 with new $X_0$ [16]). Method: a transcendence result of G. Rhin (a lower bound for linear forms in the logarithms of 2 and 3, Progress in Math. 71 (1987) 155–164, per [5, #101]) plus computational Diophantine approximation and extensive computation.
- **Hercher 2023 [16]** — "There are no Collatz $m$-cycles with $m \le 91$", J. Integer Sequences 26 (2023), Art. 23.3.5 (arXiv:2201.00406). Abstract: "Simons and de Weger proved that $m \ge 76$. With newer bounds on the range of starting values for which the Collatz conjecture has been checked, one gets $m \ge 83$. In this paper, we prove $m \ge 92$." Also: "to raise the number of odd members a nontrivial cycle has to have to the next bound — that is, to at least $K \ge 1.375\cdot10^{11}$ ... it suffices to show that, for every integer smaller than or equal to $1536\cdot2^{60} = 3\cdot2^{69}$, the respective Collatz sequence enters the trivial cycle." He used $X_0 = 704\cdot2^{60}$ and quotes the then-current $K > 7.2\cdot10^{10}$ (Hercher–Puchert).
- **Barina 2020/2025 [17]** — verification to $2^{68}$ (J. Supercomputing 77 (2021) 2681–2688) and to **$2^{71} \approx 2.36\times10^{21}$** as of 15 Jan 2025 (J. Supercomputing 81 (2025) 810; project page pcbarina.fit.vutbr.cz). Since $2^{71} > 3\cdot2^{69}$, Hercher's sufficiency condition is met, so **any nontrivial cycle now has $\ge 1.375\times10^{11}$ odd steps** — this consequence is implied by [16]+[17]; I have not found a paper stating it explicitly, so treat it as "follows from published theorems" rather than "published".

### 3.3 What is and is not proved

Proved: no cycles of length $< 1.1\times10^{11}$ (T-steps), none with $\le 91$ local minima, finitely many $m$-cycles for each $m$. **Not proved:** finitely many cycles in total (Lagarias's Finite Cycles Conjecture (C1) in [4, §7]); and the $m$-cycle results depend on Baker's bounds, which are effective but not strong enough to close the problem without computation. The Diophantine argument rules out *short* cycles absolutely and *all* cycles only if one could show the cycle minimum is bounded, which is the conjecture itself.

---

## 4. Divergence and the multiplier [12][18][19][20][22]

### 4.1 The drift is $\tfrac12\log_2 p - 1$, independent of $k$

Kontorovich–Lagarias [18, §3.2 eq. (3.5) and §8.2] set up the same **biased random walk** for both maps: after logarithmic rescaling, one Terras step adds $-\log 2 + \delta\log p$ with $\delta$ a fair Bernoulli, so the drift is
$$\mu_3 = -\log 2 + \tfrac12\log 3 = \tfrac12\log\tfrac34 \approx -0.14384, \qquad \mu_5 = -\log 2 + \tfrac12\log 5 = \tfrac12\log\tfrac54 \approx +0.11157.$$
In bits per Terras step this is $\tfrac12\log_2 p - 1$: $-0.2075$ ($p=3$), $+0.1610$ ($p=5$), $+0.4037$ ($p=7$). The additive constant $k$ only enters through $e_k = \log(1 + k/(p x_k))$, "small as long as $|x_k|$ is large" [18, eq. (8.4) with $k=1$]. Their Theorem 8.2: "For the $5x+1$ BRW model, with probability one, a trajectory diverges to $+\infty$." Their 5x+1 summary [18, §1.2]: "It is conjectured that a density one set of integers belong to divergent trajectories ... It is also conjectured that there are a finite number of periodic orbits, which include the orbits $\{1,3,8,4,2\}$ and $\{13,33,83,208,104,52,26\}$ on the positive integers and the orbit $\{-1,-2\}$ on the negative integers." And [18, §7.3]: "It is an open problem to prove that even a single trajectory (such as that emanating from the starting seed $n_0 = 7$) is divergent!" Lagarias 2010 [4, §3.3] repeats: "similar stochastic models predict that almost all orbits should 'escape to infinity' ... but it remains an unsolved problem to prove that there exists even one trajectory for the $5x+1$ problem that 'escapes to infinity'."

So the answer to "why do some blow up" is: the geometric mean of $\{p/2, 1/2\}$ is $\sqrt p/2$, which is $<1$ iff $p < 4$. Among odd $p$ that is $p=3$ alone. The repo's $\lambda_2 \to 1/6$ and the "$p$ vs 4" threshold are the same fact: $\sqrt{3}/2 < 1 < \sqrt 5/2$. In [[Winkler Tail Bound]] terms, the fraction of words of length $b$ with $3^s > 2^b$ is exponentially small ($2^{b(H(\theta)-1)}$ with $H(0.631) = 0.95$), whereas for $p=5$ the fraction with $5^s < 2^b$ is exponentially small — the exact rigorous version is Theorem 2.2 of [18] (density of $\lambda$-stopping times $\to 1$) versus its mirror Theorem 7.2 ($\lambda^+$-stopping times $\to 1$ for $5x+1$).

### 4.2 Crandall's $qx+r$ conjecture [12, §8]

Primary text, verbatim: "Conjecture (8.1). In the '$qx+r$' problem, with $q, r \in D^+$ and $q > 1$, some $m \in D^+$ fails to satisfy an equation $C^k(m) = 1$; except in the case $(q,r) = (3,1)$." Proved trivially for $r > 1$ ($m \equiv 0 \pmod r$ stays $\equiv 0 \pmod r$), and "It is known that the conjecture is true for $q = 5, 181$, and 1093; but all other cases remain elusive." The three cases: $q=5$ via the cycle through 13, "traced back to the diophantine equation $2^7 - 5^3 = 3$"; $q = 181$ via $m = 21$, cycle $\{611, 27, \dots\}$, "arising from the diophantine equation $2^{15} - 181^2 = 7$"; $q = 1093$ because $2^{q-1} \equiv 1 \pmod{q^2}$ (Wieferich) makes height 2 impossible, so "all other $m$ have infinite height ... This case is the only one for which it is known that almost all $m$ have infinite height" (Lagarias notes the same argument works for the other Wieferich prime 3511 [3, #47]). Crandall's stated reason for the general case is the heuristic drift: "a heuristic probabilistic argument suggests that for each $q \ge 5$ the '$qx+1$' problem should have a divergent trajectory" [3, #47].

Note the shape of Crandall's conjecture: it says $qx+1$ has *some* orbit missing 1 — by a cycle or by divergence. The cycle route is again a Diophantine coincidence ($2^7 - 5^3 = 3$, $2^{15} - 181^2 = 7$); the divergence route is the drift. For $q \ge 5$ both routes are open at once, which is why $5x+1$ is expected to have both finitely many cycles *and* density-one divergence.

### 4.3 Undecidability (why no general theorem should be expected)

Conway 1972 [19] shows that for functions $g(n) = a_j n$ if $n \equiv j \pmod N$ (rational $a_j$, "periodically linear" with no constant term), the question "does some iterate of $2^n$ reach a power of 2" is undecidable, by encoding Minsky register machines in the exponents of the prime factorisation [3, #43]; FRACTRAN (1987) is the same construction. Kurtz–Simon 2007 [20] sharpen this: the generalized Collatz problem ("does every orbit reach 1") is $\Pi^0_2$-complete for the class of Conway-type functions. Consequence for this note: no argument of the form "$px+k$ maps behave like this for all $(p,k)$" can be a decision procedure; what one can hope for is the *drift dichotomy* (§4.1) as a heuristic and Baker-type bounds for specific cycles.

### 4.4 A caution

arXiv:2104.10681 (Tremblay, math.GM) claims to "prove that there are trajectories ... of the $5x+1$ problem which are divergent" and that ">17% of all positive integers start divergent trajectories." It is an unrefereed general-mathematics posting whose method is a counting of residue-class growth; it does not establish divergence of any specific orbit, and it contradicts the open-problem status stated by Lagarias in 2010 and 2021 [4][18]. Do not cite it as a result.

---

## 5. Morley's OEIS sequences [21]

All by Geoffrey H. Morley, June 2013, all "conjecturally complete" (trajectories below $10^8$; for $k < 158195$ no primitive cycle with minimal element above 28,306,063 was found). Definition used: $T_k(x) = x/2$ if even, $(3x+k)/2$ if odd; primitive iff elements coprime to $k$.

| Sequence | Records |
|---|---|
| A226607 | irregular array: smallest element of each primitive $3x+k$ cycle, rows indexed by $k$ with $\gcd(k,6)=1$ (row $k=5$: 1, 19, 23, 187, 347) |
| A226608 | largest element of the same cycle |
| A226609 | cycle length $b$ (row $k=5$: 3, 5, 5, 27, 27) |
| A226610 | number of odd elements $s$ |
| A226611 | smallest starting value whose trajectory enters the cycle |
| A226612 | row start indices |
| A226613 | number of primitive cycles for $k$ ($n = \lfloor k/3\rfloor + 1$): 1, 5, 1, 2, 9, 2, 1, 3, 2, 4, 1, 2, 3, 1, 1, 7, ...; references Belaga–Mignotte 2000 Table for the first 500 terms |
| A226663 / A226664 | record numbers of primitive cycles and the $k$ achieving them: counts 1, 5, 9, 19, 20, 23, 52, 53, 97, 142, 534, 944, 950, 3806, 4782 at $k$ = 1, 5, 13, 233, 355, 431, 499, 1319, 1631, 6005, 6487, 14303, 45853, 71515, 186793 |
| A226623–A226630, A226681–A226682 | the same programme for $3x-k$ |

Morley cites Lagarias 1990 and Belaga–Mignotte 2000/2006 (including "Table 2. Factorization of Collatz numbers $2^l - 3^k$") in A226607 [21]. The OEIS pages themselves do not spell out the $2^b - 3^s$ mechanism; §6 does.

---

## 6. Counting cycles by words — why $k = 2^b - 3^s$ is rich and $k=1$ is poor

**Criterion.** From §0: a word $v$ of type $(b,s)$ gives an integer $T_k$-cycle iff $(2^b - 3^s) \mid k\,\varphi(v)$. Distinct necklaces (rotation classes) give distinct cycles; the number of necklaces of type $(b,s)$ is $\tfrac1b\binom{b}{s}$ when $\gcd(b,s)=1$ (the necklace/cycle-lemma count, cf. the lattice-path count in [[Winkler Tail Bound]]).

**Consequence.** If $k = (2^b - 3^s)/c$, the criterion for type $(b,s)$ reads $c \mid \varphi(v)$. For $c = 1$ *every* necklace of type $(b,s)$ is a cycle; for small $c$ roughly a $1/c$ fraction is. This is the content of Belaga–Mignotte's sentence "Numbers $D$ of this form give $3x+D$ problems having many primitive cycles" [5, #14] and of Lagarias's "infinitely many $k$ have at least $k^{1-\epsilon}$ cycles of period at most $\log k$" [3, #108] (take $k = 2^b - 3^s \approx 2^b$; then $\tfrac1b\binom{b}{s}$ with $s \approx b/\log_2 3$ is $2^{b H(0.631) - O(\log b)} = k^{0.95 - o(1)}$; Lagarias's $k^{1-\epsilon}$ presumably uses a range of nearby $(b,s)$ or divisors — I have not seen his proof).

**Verified here.** Every A226664 record-holder is $2^b - 3^s$ or a small-cofactor divisor of one:

| $k$ | $= (2^b - 3^s)/c$ | necklaces of type $(b,s)$ | integral cycles from this word | primitive | A226613 total |
|---|---|---|---|---|---|
| 431 | $(2^9 - 3^4)/1$ | 14 | 14 | 14 | 23 |
| 1319 | $(2^{11} - 3^6)/1$ | 42 | 42 | 42 | 53 |
| 1631 | $(2^{13} - 3^8)/1$ | 99 | 99 | 84 | 97 |
| 6005 | $(2^{13} - 3^7)/1$ | 132 | 132 | 111 | 142 |
| 6487 | $(2^{16} - 3^{10})/1$ | 504 | 504 | 456 | 534 |
| 45853 | $(2^{16} - 3^9)/1$ | 715 | 715 | 715 | 950 |
| 233 | $(2^{13} - 3^8)/7$ | 99 | 15 | 15 | 19 |
| 14303 | $(2^{27} - 3^{17})/355$ | 312,455 | (not enumerated) | — | 944 |
| 71515 | $(2^{27} - 3^{17})/71$ | 312,455 | (not enumerated) | — | 3806 |
| 186793 | $(2^{24} - 3^{15})/13$ | $\approx 54{,}480$ | (not enumerated) | — | 4782 |

The single word $(b,s)$ with $2^b - 3^s = k$ accounts for the bulk of every record; the remainder come from other $(b',s')$ with $k \mid 2^{b'} - 3^{s'}$ (e.g. $2^{26} - 3^{16} = 7\cdot233\cdot103271$), and non-primitive ones are those whose elements share a factor with $k$ (for $1631 = 7\cdot233$, the 15 non-primitive cycles are the $k=233$ cycles scaled by 7). For the estimate rows, $312455/355 \approx 880$ and $312455/71 \approx 4400$ bracket the observed 944 and 3806.

**The $k=1$ case.** $2^b - 3^s = 1$ has the single solution $(b,s) = (2,1)$ in positive integers (Gersonides 1342; a special case of Catalan/Mihăilescu), giving the trivial cycle $\{1,2\}$ from the one necklace of type $(2,1)$. Every other cycle would need $2^b - 3^s \mid \varphi(v)$ with $\varphi(v)$ of size about $m(2^b - 3^s)$ — and §3 shows that with $m > 2^{71}$ this forces $s > 7\times10^{10}$. So "$3x+1$ has the fewest cycles" is, literally, "1 is the number with the fewest representations as a divisor of $2^b - 3^s$ (one, at $(2,1)$), and all its other candidate cycles are pushed past the verification horizon by the continued fraction of $\log_2 3$." Nothing here proves finiteness; it makes $k=1$ the *tightest* case of a uniform Diophantine constraint. The same reasoning says $k = 2^b - 3^s$ with $b \le 16$ have hundreds of cycles, which is what A226663 shows. $3x-1$ ($k=-1$) is instructive in the other direction (**verified here**): $3^s - 2^b = 1$ has the solutions $(b,s) = (1,1)$ and $(3,2)$, giving the cycles $\{1\}$ and $\{5,7,10\}$ for free, while the third known cycle $\{17,25,37,55,82,41,61,91,136,68,34\}$ has $(b,s) = (11,7)$ with $3^7 - 2^{11} = 139$ dividing its numerator — a genuine divisibility coincidence of the kind $k=1$ never gets. Morley's A226623 row $k=1$ of $3x-k$ lists exactly 1, 5, 17, consistent with Lagarias's list of negative-integer cycles of $3x+1$: $\{-1\}, \{-5,-7,-10\}, \{-17,\dots,-34\}$ [18, §1.1]. That $3x-1$ has two Diophantine freebies to $3x+1$'s one is the cleanest small illustration of the whole story.

---

## 7. Synthesis — what the literature supports, and how strongly

**(a) Why $3x+1$ is special.**
*Proved:* the cycle equation $x_0 = k\varphi(v)/(2^b - 3^s)$ [11][1]; $2^b - 3^s = 1$ only at $(2,1)$; any nontrivial $3x+1$ cycle has $b/s$ within $\sim 10^{-22}$ of $\log_2 3$ and hence $> 1.1\times10^{11}$ steps and $\ge 92$ local minima [14][16][17]. *Conjectured:* finitely many cycles (C1), no divergence (C2) [4]. *The honest statement:* $3x+1$ is special only in that $k=1$ is the value with **no Diophantine slack** — its cycles must be manufactured by $2^b - 3^s$ dividing a number of the same size, which continued fractions forbid up to astronomically large $b$. Every other $k$ has slack proportional to the number of small $(b,s)$ with $k \mid 2^b - 3^s$. This is a statement about the *cycle count*, not about the dynamics; the dynamics (drift, 2-adic structure, Terras densities) are identical for all $3x+k$ ([[Primes and the Circuit]] §1 — odd primes are invisible to the circuit, and $k$ is just such an odd number).

**(b) Why other $3x+k$ have cycles.**
*Proved:* $T_k$ has a cycle of type $(b,s)$ iff $(2^b - 3^s) \mid k\varphi(v)$ (§0, [10, Lemma 2]); infinitely many $k$ have $\ge k^{1-\epsilon}$ cycles [1]; number of cycles of odd-length $\le K$ is $\le kK^{32}$ [8]. *Verified here:* the A226663 record-holders are $2^b - 3^s$ (or small-cofactor divisors), and the necklaces of that one word account for the bulk of their cycles. *Conjectured:* every $k$ has $\ge 1$ primitive cycle and finitely many [1], confirmed for $k < 20000$ by exhaustive search [7][9][21].

**(c) Why $px+1$ diverges for $p \ge 5$ but no $3x+k$ should.**
*Heuristic, rigorous in the model:* the log-drift per Terras step is $\tfrac12\log_2 p - 1$, so the biased random walk diverges a.s. iff $p > 4$ [18, Thm 8.2 vs eq. (3.5)]; $k$ affects only the $O(1/x)$ correction. *Rigorous for the true map:* the density of integers whose orbit drops below $\lambda n$ ($p=3$) or exceeds $\lambda n$ ($p=5$) tends to 1 [18, Thms 2.2 and 7.2]. *Open:* not one divergent $5x+1$ orbit is known [4][18]; Crandall's conjecture that $qx+1$ misses 1 for some $m$ is proved only for $q = 5, 181, 1093$ — and in the first two cases by *cycles*, not divergence [12]. *Impossible in general:* Conway/Kurtz–Simon undecidability for the wider class [19][20]. *Lagarias's explicit conjecture:* every $3x+k$ orbit is eventually periodic — no divergence for any $k$ [1][4]; Belaga–Mignotte's $3x+d$ hypothesis says the same [7].

**Where the repo's picture differs from the literature.** Nowhere in substance. The two novelties the repo can claim are (i) the identification of the affine intercepts $r(v)$ of stopping-time residue classes with Lagarias numerators $\varphi_{\min}(v)$, i.e. with A226607 entries for $k = 2^b - 3^s$ (this is a re-reading of Lagarias's correspondence through the Terras/affine-orbit lens, not a new theorem), and (ii) the observation that $\lambda_2 = 1/6$ and the $\sqrt p / 2$ threshold are the same fact. The "why cycles for other $k$" answer — necklace counting against divisors of $2^b - 3^s$ — is explicit in Belaga–Mignotte's tables and implicit in Lagarias's $k^{1-\epsilon}$ theorem, and should be cited to them.

---

## Sources

1. J. C. Lagarias, *The set of rational cycles for the 3x+1 problem*, Acta Arithmetica 56 (1990) 33–53. DOI 10.4064/aa-56-1-33-53. https://eudml.org/doc/206298 — full text not readable here (bot wall); theorems taken from the author's annotation [3, #108] and restatement [4, §4].
2. J. C. Lagarias, *The 3x+1 problem and its generalizations*, Amer. Math. Monthly 92 (1985) 3–23. DOI 10.1080/00029890.1985.11971528. HTML: http://www.cecm.sfu.ca/organics/papers/lagarias/ (sections node3, node8, node9, node11 read).
3. J. C. Lagarias, *The 3x+1 problem: An annotated bibliography (1963–1999)*, arXiv:math/0309224 (v7, 2006). https://arxiv.org/abs/math/0309224 — entries #18 (Belaga–Mignotte 1998), #26 (Böhm–Sontacchi), #43 (Conway), #47 (Crandall), #53 (Eliahou), #80 (Halbeisen–Hungerbühler), #108 (Lagarias 1990), #158–160 (Steiner).
4. J. C. Lagarias, *The 3x+1 problem: An overview*, in *The Ultimate Challenge: The 3x+1 Problem* (AMS, 2010) 3–29; arXiv:2111.02635. https://arxiv.org/abs/2111.02635
5. J. C. Lagarias, *The 3x+1 problem: An annotated bibliography, II (2000–2009)*, arXiv:math/0608208. https://arxiv.org/abs/math/0608208 — entries #10–14 (Belaga, Belaga–Mignotte 2000–2006), #100–101 (Simons–de Weger).
6. E. G. Belaga, M. Mignotte, *Embedding the 3x+1 conjecture in a 3x+d context*, Experimental Mathematics 7 (1998) no. 2, 145–151. (Full text not accessed; content from [3, #18].)
7. E. G. Belaga, M. Mignotte, *Cyclic structure of dynamical systems associated with 3x+d extensions of Collatz problem*, Université Louis Pasteur, Strasbourg, preprint 2000-18 (57 pp.), HAL hal-00129656. https://hal.science/hal-00129656 (HAL page bot-walled; abstract via search snippets and [5, #10].)
8. E. G. Belaga, *Effective polynomial upper bounds to perigees and numbers of (3x+d)-cycles of a given oddlength*, Acta Arithmetica 106 (2003) no. 2, 197–206. https://www.impan.pl/en/publishing-house/journals-and-series/acta-arithmetica/all/106/2/82606/
9. E. G. Belaga, M. Mignotte, *Walking cautiously into the Collatz wilderness: algorithmically, number theoretically, randomly*, DMTCS Proceedings AG (Fourth Colloquium on Mathematics and Computer Science, 2006) 249–260; and *The Collatz problem and its generalizations: Experimental data. Table 1. Primitive cycles of 3x+d mappings* (Strasbourg preprint 2006-015) and *Table 2. Factorization of Collatz numbers 2^l − 3^k* (preprint 2006-018). Per [5, #12–14].
10. L. Halbeisen, N. Hungerbühler, *Optimal bounds for the length of rational Collatz cycles*, Acta Arithmetica 78 (1997) no. 3, 227–239. PDF: https://www.math.ch/norbert.hungerbuehler/publications/Optimal_bounds_for_the_length_of_rational_Collatz_cycles.pdf (read in full).
11. C. Böhm, G. Sontacchi, *On the existence of cycles of given length in integer sequences like x_{n+1} = x_n/2 if x_n even, and x_{n+1} = 3x_n+1 otherwise*, Atti Accad. Naz. Lincei Rend. Cl. Sci. Fis. Mat. Natur. (8) 64 (1978) no. 3, 260–264. https://eudml.org/doc/290184
12. R. E. Crandall, *On the "3x+1" problem*, Mathematics of Computation 32 (1978) no. 144, 1281–1292. https://www.ams.org/journals/mcom/1978-32-144/S0025-5718-1978-0480321-3/ (read in full).
13. R. P. Steiner, *A theorem on the Syracuse problem*, Proc. 7th Manitoba Conference on Numerical Mathematics and Computing (Winnipeg 1977), Congressus Numerantium XX, Utilitas Math., Winnipeg 1978, 553–559. (Content from [3, #158].)
14. S. Eliahou, *The 3x+1 problem: new lower bounds on nontrivial cycle lengths*, Discrete Mathematics 118 (1993) 45–56. DOI 10.1016/0012-365X(93)90052-U. https://archive-ouverte.unige.ch/unige:12087 (abstract; theorem statement from [3, #53] and [10, §4.2]; bound reproduced numerically here).
15. J. L. Simons, B. M. M. de Weger, *Theoretical and computational bounds for m-cycles of the 3n+1 problem*, Acta Arithmetica 117 (2005) no. 1, 51–70. DOI 10.4064/aa117-1-3. https://eudml.org/doc/278746
16. C. Hercher, *There are no Collatz m-cycles with m ≤ 91*, Journal of Integer Sequences 26 (2023), Article 23.3.5; arXiv:2201.00406. https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.html (read in full).
17. D. Barina, *Convergence verification of the Collatz problem*, J. Supercomputing 77 (2021) 2681–2688, DOI 10.1007/s11227-020-03368-x; D. Barina, *Improved verification limit for the convergence of the Collatz conjecture*, J. Supercomputing 81 (2025) 810, DOI 10.1007/s11227-025-07337-0; project page https://pcbarina.fit.vutbr.cz/ (all $n < 2^{71}$ as of 2025-01-15).
18. A. V. Kontorovich, J. C. Lagarias, *Stochastic models for the 3x+1 and 5x+1 problems*, arXiv:0910.1944 (2009); in *The Ultimate Challenge* (AMS 2010). https://arxiv.org/abs/0910.1944 (read in full).
19. J. H. Conway, *Unpredictable iterations*, Proc. 1972 Number Theory Conference, University of Colorado, Boulder, 1972, 49–52. Scan: https://gwern.net/doc/cs/computable/1972-conway.pdf (content from [3, #43]).
20. S. A. Kurtz, J. Simon, *The undecidability of the generalized Collatz problem*, Theory and Applications of Models of Computation (TAMC 2007), Lecture Notes in Computer Science 4484, Springer, 2007. https://link.springer.com/chapter/10.1007/978-3-540-72504-6_49 (page range not verified).
21. G. H. Morley, OEIS A226607–A226613, A226623, A226663, A226664, A226681 (all June 2013). https://oeis.org/A226607, https://oeis.org/A226613, https://oeis.org/A226663, https://oeis.org/A226664
22. R. P. Steiner, *On the "Qx+1" problem, Q odd*, Fibonacci Quarterly 19 (1981) 285–288, and *II*, ibid. 293–296. (Content from [3, #159–160].)
23. M. Chamberland, *An update on the 3x+1 problem* (survey; English version of the 2003 Butl. Soc. Catalana Mat. article), PDF https://chamberland.math.grinnell.edu/papers/3x_survey_eng.pdf — used for the Eliahou inequality and the Tempkin–Arteaga 1997 figure 187,363,077.
