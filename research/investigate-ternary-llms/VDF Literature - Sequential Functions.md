---
tags: [collatz, vdf, cryptography, sequential-functions, literature-survey, loop-L11]
status: survey
created: 2026-09-16
---

# VDF Literature — Sequential Functions

A literature survey written for a mathematician, not a cryptographer, to support [[VDF Feasibility - Collatz as a Delay Function]]. The question behind it: could the session's results — the 5-unit ternary Terras gate ([[Minimal Ternary Circuit]], [[Ternary Syracuse Circuit]]), the affine k-step structure and the trit-packing stopping-time formula ([[Collatz Bridge - Trits and Stopping Times]]) — found a verifiable delay function, a proof of sequential work, or a verifiable puzzle? This note only reports what the literature has established and what it would demand; the feasibility verdict lives in the sibling note. Index: [[00 Index]].

Every citation below was checked against the source (ePrint/arXiv page, publisher page, or the PDF text). Items I could not fully verify are marked **(unverified)**.

**Bottom line in five sentences.**
1. A VDF is not "a slow function"; it is a slow function whose output is *unique* and whose correctness can be checked in time polylogarithmic in the delay, against an adversary with polynomially many parallel processors and unbounded precomputation [1].
2. Every deployed VDF (Chia, and the paused Ethereum design) is repeated squaring in a group of unknown order, verified with a proof of exponentiation [5, 6, 17]; the "iterated low-degree map + SNARK" family (VeeDo, Sloth++, MinRoot) was broken in latency terms in 2023–24 and Ethereum put its VDF on hold [12, 13, 14, 16].
3. The literature contains half a dozen Collatz-based hash / proof-of-work / PRNG proposals (an abandoned Apple patent, two arXiv/ePrint preprints, a finance-journal proof-of-work, an IEEE conference paper, two PRNG papers); none has a security reduction, none has received public cryptanalysis, and none is a delay function [22–29].
4. Iterating the Collatz map is *not* known to be inherently sequential: Stérin–Woods proved that about half the bits of T^i(x) for i = O(log x) are computable in NC¹ (fast in parallel), and the rest are only known to be in P [30]; the k-step affine structure the repo proved is itself a parallel shortcut once the parity word is known [33].
5. The one Collatz-like map with a *proved* stopping-time bound is the F₂[x] analogue of Hicks–Mullen–Yucas–Zavislak: every polynomial reaches 1 in at most deg² + 2·deg steps [34], improved to O(deg^1.5) [35] with average ≈ 2·deg [36] — a proved, predictable delay, which is the property the integer map lacks.

---

## 1. Definitions

### 1.1 Verifiable delay functions (Boneh–Bonneau–Bünz–Fisch 2018)

Boneh, Bonneau, Bünz and Fisch [1] gave the first formal definition. A VDF is a triple of algorithms:

- **Setup(λ, t) → pp** — public parameters for security parameter λ and delay parameter t;
- **Eval(pp, x) → (y, π)** — the output y and a proof π; must take t sequential steps;
- **Verify(pp, x, y, π) → {accept, reject}**.

Three properties:

- **Sequentiality.** No adversary with poly(λ, t) parallel processors and a poly(λ, t) precomputation phase can output y in parallel time noticeably less than t (formally, (t, ε)-sequentiality: less than (1 − ε)·t parallel steps). The adversary is allowed *arbitrary* parallelism up to a polynomial and arbitrary precomputed tables; only wall-clock depth is bounded. This is the property that defeats time–memory trade-offs (§3.2) and hardware races.
- **Uniqueness / soundness.** For each x exactly one y verifies; no efficient adversary can produce (y′, π′) with y′ ≠ y that Verify accepts.
- **Efficiency.** Verify runs in time polylog(t)·poly(λ), and π is short. BBBF explicitly rejected Sloth (§2.3) as a VDF because its verification is only a constant factor faster than evaluation, not polylogarithmic [1].

A **weak VDF** relaxes the requirement that honest Eval be near-sequential: Eval may need O(t) processors itself, but the adversary still gains no further parallel speedup [1, §6].

### 1.2 Proofs of sequential work (PoSW) and how they differ

Mahmoody, Moran and Vadhan (ITCS 2013) [3] defined *publicly verifiable proofs of sequential work*: a prover convinces a verifier that N sequential hash evaluations were spent on a challenge, in the random-oracle model, via a labelling of a depth-robust graph. Cohen and Pietrzak (Eurocrypt 2018) [4] gave a simple construction with O(log N) prover space. BBBF state the relationship precisely: "VDFs can be seen as a special case of publicly verifiable proofs of sequential work with the additional guarantee of a unique output (hence the use of the term 'function' versus 'proof')" [1, §9]. A PoSW prover can produce many valid proofs for one challenge, so a PoSW cannot serve as a randomness beacon; a VDF can.

### 1.3 Time-lock puzzles (Rivest–Shamir–Wagner 1996)

Rivest, Shamir and Wagner [2] introduced time-lock puzzles: encrypt under the key y = x^(2^t) mod N for an RSA modulus N. The puzzle-setter, knowing φ(N), computes y in one exponentiation; everyone else needs t sequential squarings. This is the ancestor of every modern VDF, but it is *privately* verifiable — only the setter can check quickly. Pietrzak's 2019 VDF [6] is literally "how the Rivest–Shamir–Wagner time-lock puzzle can be made publicly verifiable".

---

## 2. Known constructions and why they work

### 2.1 Repeated squaring in a group of unknown order (Wesolowski; Pietrzak)

Both 2019 VDFs [5, 6] compute y = g^(2^t) in a group G of unknown order (an RSA group Z/NZ with N of unknown factorisation, or the class group of an imaginary quadratic field, which needs no trusted setup).

*Why squaring is believed sequential.* Exponent 2^t has t bits; without knowing |G| the only known way to reduce the exponent is to perform the t squarings one after another. Parallelism helps only inside a single modular multiplication (constant-factor speedup), which is why the VDF Alliance built low-latency modular-squaring ASICs to fix that constant [15].

*How verification is fast.*
- **Wesolowski** [5]: the verifier sends a random prime ℓ; the prover returns π = g^⌊2^t/ℓ⌋; the verifier checks π^ℓ · g^(2^t mod ℓ) = y with two small exponentiations. Proof: one group element. Soundness rests on the *adaptive root assumption* in G.
- **Pietrzak** [6]: a halving protocol — the prover reveals the midpoint μ = g^(2^(t/2)), the verifier merges the two half-claims with a random challenge, and after log t rounds a single squaring remains. Proof: log t group elements; ~10 KB for t ≤ 2^40 and N = 2048 bits, verification ≈ three RSA exponentiations; soundness needs only that low-order elements be hard to find.

Chia's blockchain runs exactly this in production: repeated squaring in class groups with a fresh 1024-bit discriminant per challenge, and Wesolowski proofs [17]. Döttling, Garg, Malavolta and Vasudevan ("Tight VDFs", SCN 2020) showed how to shrink the evaluator's parallelism overhead to logarithmic [21].

### 2.2 Isogeny VDFs (De Feo–Masson–Petit–Sanso 2019)

The Asiacrypt 2019 paper [7] builds VDFs from walks of length T in supersingular isogeny graphs, verified with a pairing equation. Sequentiality rests on the assumption that a long isogeny walk cannot be shortcut; the trusted setup is heavy (one long walk per parameter set) but the output is unique and verification is a constant number of pairings. Not deployed; included because it is the one VDF family with a genuinely different sequential primitive.

### 2.3 Sloth (Lenstra–Wesolowski 2015): the asymmetry trick

Sloth [8] takes a prime p ≡ 3 (mod 4) and iterates a permutation ρ built from modular square roots: ρ(x) = +√x if x is a quadratic residue, −√(−x) otherwise, with the sign fixed by the parity of the canonical lift. Extracting a square root costs the exponent (p+1)/4, i.e. "at least log₂(p) − 2 unparallelizable modular squarings, whereas a single modular squaring suffices to verify the result" [8, §3.2]. This is the general *asymmetry trick*: choose a step whose inverse is cheap. Its limit, as BBBF observed, is that verification is only ≈ log p times faster than evaluation — a constant depending on p, not polylog(t) — so Sloth is a "time-asymmetric encoding" or pseudo-VDF, not a VDF [1]. The unicorn protocol in the same paper is a public-randomness beacon built on sloth.

### 2.4 Iterated low-degree maps plus a STARK/SNARK: VeeDo, Sloth++, MinRoot

The BBBF paper's generic construction [1, §5] is: take *any* iterated sequential function f = g∘g∘…∘g and attach an incrementally verifiable computation (IVC) proof [11] — a succinct proof that each step was computed correctly, updated in parallel with the computation. Then Verify checks only the succinct proof. This turns any sequential map into a VDF, with two costs: the proof system needs its own assumptions, and **the cost metric becomes the algebraic degree of g over the proof field**, because a SNARK/STARK prover's work is proportional to the arithmetic-circuit size of *checking* g, not of computing it.

That metric drove the three algebraic candidates. StarkWare's VeeDo (2020) [10] iterates a low-degree permutation over a prime field for ~3·10^8 steps and wraps it in a STARK. Sloth++ [1] is Sloth over F_{p²}. MinRoot (Khovratovich–Maller–Tiwari, ePrint 2022/1626) [9] iterates

  F_i(x, y) = ( (x + y)^{1/5},  x + i )  (mod p),

with p the scalar field of BLS12-381 or BN254: a fifth root costs ≈ log₂ p ≈ 254 sequential squarings to compute but only degree 5 to *check*, so the SNARK is cheap. The designers ran 2^30 rounds per second, claimed "128 bits of multitarget VDF security" (no adversary with 2^128 processors and shared memory halves the latency), and Supranational taped out a 12 nm ASIC at 257 cycles ≈ 230 ns per round [9, 13, 15].

### 2.5 What killed the algebraic candidates

- **The 2023 EF-commissioned report** (Leurent, Mennink, Pietrzak, Rijmen, "Analysis of MinRoot", April 2023 workshop, published Sept 2023) [13] found that the exponentiation inside each round can be parallelised: with precomputed tables (Pohlig–Hellman-style tables of roots modulo factors of p − 1, and baby-step/giant-step tables) an attacker trades memory for latency, contradicting assumption 1 of the security claim ("the round function itself is sequential").
- **The Ethereum Foundation statement** (ethresear.ch, 18 September 2023, signed by Herold, Kadianakis, Khovratovich, Maller, Simkin, Sanso, Zapico, Zhang) [12] says: "the exponentiation part of the round function can be parallelized"; "At present we do not recommend using VDFs within Ethereum"; and, tellingly, "we have few tried and tested design patterns for building concretely efficient VDFs". (The task brief dated this statement 2024; the statement is from 2023. The 2024 item is the CRYPTO paper below.)
- **CRYPTO 2024, Biryukov, Fisch, Herold, Khovratovich, Leurent, Naya-Plasencia, Wesolowski, "Cryptanalysis of Algebraic Verifiable Delay Functions" (ePrint 2024/873)** [14] turned this into algorithms. Their Table 1, for a 256-bit prime as in MinRoot, lists latency (in sequential multiplications) versus resources for computing a fifth root, naive = 256: baby-step/giant-step, latency 8 with 2^128 processors and 2^128 memory (32× speedup); a *smoothness* method, latency 6 with 2^54.5 processors and no memory (42×); smoothness with medium-size factors, latency 13 with 2^48 processors and 2^59.5 memory (20×); down to latency 68 with 2^25 processors and 2^40 memory (3.7×). Their conclusion: "computing roots is not a sequential operation, breaking an assumption used in several VDF constructions. In particular, MinRoot is a VDF candidate that was proposed as a randomness beacon in the core layer of the Proof-of-Stake Ethereum protocol, but this project has been put on hold following our results." They also show (their §6) that even a *low-degree* round function admits parallel latency reductions, so simply swapping the root for a small power does not restore sequentiality.
- **Ethereum's current position**, per Edgington's *Upgrading Ethereum* [16]: "there is no active plan to implement one in Ethereum at this time. If anything, recent results on the difficulty of constructing VDF functions suggest that the prospect of an in-protocol VDF is receding." (Quoted from a search excerpt; the page fetch was rate-limited — **wording unverified against the live page**.)

The moral for any new candidate: the adversary model that matters is *latency with 2^100+ processors and large precomputed tables*, and the historical failure mode is that a step believed to be "inherently sequential" (a root, a low-degree map) turned out to have a shallow parallel circuit once memory was allowed.

### 2.6 Impossibility results that bound the design space

- Mahmoody, Smith and Wu (ICALP 2020) [18]: perfectly unique VDFs cannot be built from a random oracle alone in a black-box way. A hash chain is a fine *delay* function but cannot be made a *verifiable* delay function without extra structure.
- Hall-Andersen and Nielsen (ePrint 2022/542) [19]: incrementally verifiable computation itself cannot be built from random oracles alone, confirming Valiant's conjecture; so the "any sequential function + IVC" recipe always imports a non-black-box assumption from the proof system.

---

## 3. Iterated maps as delay functions

### 3.1 Parallel speedup of iterating a generic map

Iterating a *random* function is sequential in the random-oracle model: a sequential composition of hash functions "when modeled as random oracles, is provably a delay function" [14, §1, citing 18]; BBBF's and Cohen–Pietrzak's proofs rest on the same fact [1, 4]. But that guarantee vanishes the moment the map has algebraic structure: every algebraic VDF candidate above was proposed precisely because structure makes verification cheap, and was then attacked through the same structure. The Collatz map's structure — affine on residue classes, 2-adically determined parity words — is exactly the kind exploited in §3.2.

### 3.2 Time–memory trade-offs and why sequentiality is defined against them

Hellman's 1980 time–memory trade-off [20] showed that a one-time precomputation of N operations lets later inversions run in N^(2/3) time with N^(2/3) memory (TM² = N²). VDF sequentiality [1] is therefore defined against an adversary who has *already* done polynomial precomputation and has polynomially many processors: a delay function whose t-step evaluation can be shortened by a lookup table is broken by definition. BBBF themselves note a precomputation attack on their own permutation-polynomial candidate that yields a factor-s speedup after a bounded number of challenges [1, §8]. The CRYPTO 2024 tables (§2.5) are this attack model made concrete.

For Collatz specifically the trade-off is already standard practice, not an attack: the repo's own result that the parity word of the first k Terras steps is a function of n mod 2^k (Terras 1976 [42]) means a table of 2^m entries lets an evaluator jump m steps per lookup (dest = 3^s·n/2^(k−s) + C), and this "sieve" is how the convergence-verification projects reach 2^71 [44]. In VDF terms: a k-step Collatz delay has a memory shortcut of m steps per lookup for any m, with the same 2^m table serving every input.

### 3.3 Hash chains: sequential but not verifiable

A hash chain h^t(x) is the textbook sequential function [3, 4], but verifying it costs t hash evaluations — no better than recomputing — and Mahmoody–Smith–Wu [18] prove that no black-box use of the hash can fix this. Verifiability has to come from a proof system (IVC/SNARK, §2.4) or from algebraic structure with a cheap inverse (§2.1, §2.3).

### 3.4 Collatz / 3x+1 as a cryptographic primitive: what exists

| Proposal | Type | Venue / status | Security argument | Cryptanalysis? |
|---|---|---|---|---|
| Ciet, Farrugia, Icart (Apple Inc.), "System and method for a Collatz based hash function", US 2013/0108038 A1, filed 30 Nov 2011 [23] | hash | patent application, **abandoned**, not granted | iterate n → n/2 or (3n+1) mod p for r rounds; "conditional branching" | none |
| Vuckovac, "One Way Function Candidate based on the Collatz Problem", arXiv:1801.05079 (2018) [22] | one-way function | arXiv preprint, 10 pp. | heuristic: exponential dependence of cost on branching | none |
| Bocart, "Inflation Propensity of Collatz Orbits: A New Proof-of-Work for Blockchain Applications", *J. Risk and Financial Management* 11(4):83 (2018) [25] | proof-of-work | finance journal | empirical: number of new orbit maxima is ≈ geometric with parameter ≈ 0.714 | none |
| Aljassas & Sasi, "Performance Evaluation of Proof-of-Work and Collatz Conjecture Consensus Algorithms", IEEE ICCAIS 2019 [26] | consensus puzzle | IEEE conference | none (a performance comparison; the Collatz variant runs ~1000× faster than hash PoW) | none |
| Xu & Tamir, "Pseudo-random number generators based on the Collatz conjecture", *Int. J. Information Technology* (2019) [28] | PRNG | Springer journal | NIST SP 800-22 statistical tests only | none |
| Działa, "Collatz-Weyl Generators", arXiv:2312.17043 (2023, rev. 2024) [29] | PRNG | arXiv preprint | statistical test suites; "potential of support of cryptographic applications" (author's phrasing) | none |
| Singh, Singh, Mishra (DRDO), "Collatz Hash: Hash Algorithm Using 3x+1 Conjecture", ePrint 2025/1606 (Sept 2025, rev. June 2026) [24] | hash, 256/384/512-bit | ePrint preprint (not peer reviewed) | "no quantum speedup against Collatz is known, so no structural attack should exist" | none |
| Doãn, "Collatz-PoW: A Novel Proof-of-Work System Based on the Collatz Conjecture", ResearchHub 2025, DOI 10.55277/researchhub.vzqyp4nb.1 [27] | proof-of-work | ResearchHub preprint | Python prototype; ASIC-resistance claim | none **(only the Crossref record was checked)** |

Assessment. Every item is a *proposal*; none states a security definition, gives a reduction, or has been cryptanalysed in print. Nothing in this list is a delay function: the hashes and PoWs are *search* puzzles (§5), and the PRNGs make no sequentiality claim. Searches for "Collatz verifiable delay" and "3x+1 VDF" returned nothing — no Collatz VDF proposal exists in the literature. The one serious cryptographer's blog on the topic (Soatok, Jan 2025) uses Collatz only as an analogy for carry propagation in ARX ciphers and proposes nothing.

### 3.5 Complexity of iterating T: P-complete or in NC?

- **Generalised Collatz maps are undecidable.** Conway (1972, "Unpredictable iterations") [31] showed that "Collatzian" fraction games simulate any register machine (later FRACTRAN); Kurtz and Simon (TAMC 2007) [32] sharpened this: the generalised Collatz problem is Π⁰₂-complete. This says nothing about the fixed 3x+1 map, whose orbit lengths are believed finite but unproved.
- **The fixed map is partially parallelisable.** Stérin and Woods (RP 2020; arXiv:2007.06979) [30] built a quasi-cellular automaton for 3x+1 running base 2 horizontally and base 3 vertically, and proved that "predicting about half of the bits of the iterates T^i(x), for i = O(log x), is in the complexity class NC¹ but outside AC⁰." Their accompanying page says of the other half: "Beyond saying that they are in P, we just don't know ... yet", and raises P-completeness only as the worst case. **No published result shows Collatz iteration to be P-complete, and none shows it in NC**; the question is open in both directions.
- **Once the parity word is known, the rest is TC⁰.** T^k(n) = 3^s·n/2^(k−s) + C(parity word); iterated multiplication and division are in uniform TC⁰ (Hesse–Allender–Barrington, JCSS 2002) [33], so the entire sequential content of k Collatz steps is in the parity word, which depends on n mod 2^k only [42]. For k ≤ log₂ n the parity word is computable from the low k bits *independently of the high bits* — a k-bit sub-computation, which is what Stérin–Woods's NC¹ result exploits. For k ≫ log₂ n the parity word depends on bits produced by earlier steps, and no shortcut is known — but none is ruled out.

Consequence for the 5-unit gate: a minimal *gate count* per bit says nothing about sequential *depth* over k steps, which is the only quantity a VDF cares about (§2.5, "latency" columns); the minimality result is a statement about circuit size, not about the depth of T^k.

---

## 4. Polynomial analogues with provable stopping times

Hicks, Mullen, Yucas and Zavislak, "A Polynomial Analogue of the 3n+1 Problem", *Amer. Math. Monthly* 115(7):615–622 (2008) [34] define on F₂[x]:

  T(f) = f/x if f(0) = 0 ("even"),   T(f) = (1 + x)·f + 1 if f(0) = 1 ("odd"),

i.e. x plays 2 and 1 + x plays 3. They prove that every non-zero f reaches 1, with stopping time at most deg(f)² + 2·deg(f). (The same works over any field; the arithmetic that makes the integer problem hard — carries — is absent.)

Follow-ups:
- Alon, Behajaina and Paran, "On the stopping time of the Collatz map in F₂[x]", arXiv:2401.03210 (2024) [35]: stopping time ≤ (2·deg f)^1.5 + deg f, i.e. O(deg^1.5); arithmetic progressions of unbounded length occur among stopping times; they ask whether the truth is linear or deg·log deg.
- Inselmann, "On the average stopping time of the Collatz map in F₂[x]", arXiv:2401.12781 (2024) [36]: the average stopping time over degree-n polynomials satisfies ρ(n)/n → 2, confirming Alon–Behajaina–Paran's conjecture.
- The same group has a more general treatment, "The Collatz map analogue in polynomial rings and in completions", arXiv:2312.00390 (2023, rev. 2024) [36a], and there is an earlier "Analogues of the 3x+1 Problem in Polynomial Rings of Characteristic 2", arXiv:1610.02545 [36b] **(authors not verified; titles from arXiv listings)**.

*Why a proved orbit length matters for a delay function.* Setup(λ, t) must produce a challenge whose honest evaluation takes t steps, and sequentiality is a statement about *that* t. For the integer map the stopping time of a random odd n has mean 9.478 (Wagon's constant; [[Collatz Bridge - Trits and Stopping Times]]) but no proved upper bound — it is not even proved finite — so "iterate until the orbit drops" has no Setup that can name t, and "iterate exactly k steps" abandons the orbit structure entirely and is just a k-step affine-with-branching map. The F₂[x] map has both a proved bound (so t is well-defined and Setup can certify it) and a linear-in-degree average (so t is *predictable*, not just bounded). It is also over F₂, so each step is a shift or a shift-and-XOR — the natural home for a bit-serial ternary-weight gate. That does not make it sequential (§3.5 applies with even more force: multiplication by (1 + x) has no carries, so k steps are k XOR-shifts, a depth-O(log k) linear map given the parity word), but it removes the *unpredictability of t* obstacle that the integer map cannot.

---

## 5. Verifiable puzzles versus delay functions

### 5.1 Proof-of-work and client puzzles are parallel by design

Dwork and Naor (CRYPTO 1992) [37] introduced "pricing functions": moderately hard, easily checked computations to price email. Back's Hashcash (1997; write-up 2002) [38] made it a hash-preimage search — find a nonce so that H(header ∥ nonce) has k leading zero bits — and Bitcoin inherited it. These are *search* puzzles: the expected work is 2^k trials, but the trials are independent, so p processors finish p times faster. A search puzzle therefore certifies *energy*, not *elapsed time*; BBBF's opening contrast is exactly this ("proofs of work … are parallelizable") [1]. Any Collatz puzzle of the form "find n with stopping time ≥ k" or "find a nonce whose Collatz-hash has property P" (this is what [25, 26, 27] propose) is a search puzzle and cannot be a VDF, whatever the per-trial cost.

### 5.2 "Find the smallest circuit": the Minimum Circuit Size Problem

The complexity home for an "optimal-circuit puzzle" is MCSP: given the 2^n-bit truth table of a Boolean function and a size bound s, decide whether a circuit of size ≤ s computes it. Kabanets and Cai (STOC 2000) [39] showed that MCSP is in NP and that proving it NP-hard under natural reductions would imply circuit lower bounds and break pseudorandom generators — i.e. its hardness is tied to the deepest open questions. Recent progress: Hirahara (FOCS 2022) [40] proved the *partial-function* version of MCSP NP-hard under randomised reductions, and Ilango (SIAM J. Comput. 2024) [41] showed SAT reduces to MCSP relative to a random oracle. Ilango's earlier work gives NP-completeness for AC⁰-formula minimisation and ETH-hardness for formula minimisation [41a].

Relevance to the session's exhaustive 5-unit result: "the Terras step needs exactly 5 ternary threshold units" is an *instance* of (a threshold-circuit variant of) MCSP solved by brute force at n = 5 inputs. As a puzzle it has the search-puzzle defect of §5.1 (a solver with p processors searches p times faster) and a worse one: the solution is a fixed public fact, so it can be posed once. MCSP is a hardness *source* for one-way functions and PRGs [40, 41], not a template for delay functions.

### 5.3 Proofs of useful work

The proof-of-useful-work literature replaces hash search with optimisation instances (SNARK proving marketplaces [45], minimal dominating sets [46], HEP simulations, matrix multiplication). I found no proposal that uses circuit minimisation as the useful task, and every PoUW is a search puzzle with the §5.1 property; the survey "Challenges of Proof-of-Useful-Work" (arXiv:2209.03865) [47] lists the standard obstacles (verifiability of the useful output, instance-choice attacks).

---

## 6. Checklist: what a Collatz-based candidate would have to satisfy

| # | Property | Why it is required (source) | Status for Collatz |
|---|---|---|---|
| 1 | A Setup that names the delay t for every challenge | VDF definition: sequentiality is relative to t [1] | Orbit length unproved for integers; proved ≤ deg² + 2 deg over F₂[x] [34, 35] |
| 2 | Sequentiality against poly(t) processors **and** polynomial precomputation/memory | BBBF definition [1]; Hellman trade-off [20]; the CRYPTO 2024 attack tables allow 2^25–2^128 processors and 2^40–2^128 memory [14] | Parity word is a function of n mod 2^k [42], so an m-step lookup table exists for every m; half the bits of O(log x) iterates are in NC¹ [30] |
| 3 | No shallow parallel circuit for one step **or** for the composition of steps | Both assumptions were stated separately for MinRoot and the first fell [13, 14] | One Terras step is depth-O(log B) (the bit-serial 5-unit gate is size-minimal, not depth-minimal); k steps reduce to one TC⁰ multiplication given the parity word [33] |
| 4 | Uniqueness of output | The line between a VDF and a PoSW [1, 3] | Trivially true for a deterministic map; the hard part is 5 |
| 5 | Verification in polylog(t) with a short proof | BBBF efficiency requirement; Sloth rejected for constant-factor asymmetry [1, 8] | Requires either a cheap inverse step (none: T is 2-to-1 and its "inverse" is the Collatz tree) or an IVC/SNARK wrapper [11], whose cost is the algebraic degree of a step over the proof field [9, 14] |
| 6 | A security reduction to a stated assumption, and public cryptanalysis | The EF's stated reason for pausing: "few tried and tested design patterns" [12] | No Collatz primitive in the literature has either [22–29] |
| 7 | Not a search puzzle | Search puzzles certify work, not time [1, 37, 38] | All existing Collatz PoW proposals are search puzzles [25, 26, 27] |
| 8 | The proof system's own assumption is acknowledged | IVC and unique VDFs are impossible from random oracles alone [18, 19] | Any "SNARK over the Collatz circuit" design inherits a SNARK assumption; the Collatz part contributes no hardness of its own |

---

## Sources

1. D. Boneh, J. Bonneau, B. Bünz, B. Fisch, "Verifiable Delay Functions", CRYPTO 2018; ePrint 2018/601. https://eprint.iacr.org/2018/601
2. R. L. Rivest, A. Shamir, D. A. Wagner, "Time-lock puzzles and timed-release crypto", MIT/LCS/TR-684, 1996. https://dspace.mit.edu/bitstream/handle/1721.1/149822/MIT-LCS-TR-684.pdf
3. M. Mahmoody, T. Moran, S. Vadhan, "Publicly verifiable proofs of sequential work", ITCS 2013. https://scholar.harvard.edu/files/salil/files/moody.pdf
4. B. Cohen, K. Pietrzak, "Simple Proofs of Sequential Work", Eurocrypt 2018; ePrint 2018/183. https://eprint.iacr.org/2018/183
5. B. Wesolowski, "Efficient verifiable delay functions", Eurocrypt 2019, J. Cryptology 2020; ePrint 2018/623. https://eprint.iacr.org/2018/623
6. K. Pietrzak, "Simple Verifiable Delay Functions", ITCS 2019; ePrint 2018/627. https://eprint.iacr.org/2018/627
7. L. De Feo, S. Masson, C. Petit, A. Sanso, "Verifiable Delay Functions from Supersingular Isogenies and Pairings", Asiacrypt 2019; ePrint 2019/166. https://eprint.iacr.org/2019/166
8. A. K. Lenstra, B. Wesolowski, "A random zoo: sloth, unicorn, and trx", ePrint 2015/366. https://eprint.iacr.org/2015/366
9. D. Khovratovich, M. Maller, P. R. Tiwari, "MinRoot: Candidate Sequential Function for Ethereum VDF", Stanford Blockchain Conf. 2022; ePrint 2022/1626. https://eprint.iacr.org/2022/1626
10. StarkWare, "Presenting: VeeDo, a STARK-based VDF Service", June 2020; code at https://github.com/starkware-libs/veedo. https://medium.com/starkware/presenting-veedo-e4bbff77c7ae
11. P. Valiant, "Incrementally Verifiable Computation or Proofs of Knowledge Imply Time/Space Efficiency", TCC 2008. https://link.springer.com/chapter/10.1007/978-3-540-78524-8_1
12. Ethereum Foundation Cryptography Research Team (G. Herold, G. Kadianakis, D. Khovratovich, M. Maller, M. Simkin, A. Sanso, A. Zapico, Z. Zhang), "Statement regarding the public report on the analysis of MinRoot", ethresear.ch, 18 Sept 2023. https://ethresear.ch/t/statement-regarding-the-public-report-on-the-analysis-of-minroot/16670
13. G. Leurent, B. Mennink, K. Pietrzak, V. Rijmen, "Analysis of MinRoot: Public report (requested by Ethereum Foundation)", Sept 2023. https://crypto.ethereum.org/events/minrootanalysis2023.pdf
14. A. Biryukov, B. Fisch, G. Herold, D. Khovratovich, G. Leurent, M. Naya-Plasencia, B. Wesolowski, "Cryptanalysis of Algebraic Verifiable Delay Functions", CRYPTO 2024, LNCS 14924; ePrint 2024/873. https://eprint.iacr.org/2024/873 (code: https://github.com/Cryptosaurus/VDF_cryptanalysis_code)
15. Protocol Labs, "Collaboration with the Ethereum Foundation on VDFs" (2019), https://filecoin.io/blog/posts/collaboration-with-the-ethereum-foundation-on-vdfs/ ; VDF Alliance wiki, https://supranational.atlassian.net/wiki/spaces/VA/overview ; Supranational, MinRoot VDF hardware engine, https://github.com/supranational/minroot_hardware
16. B. Edgington, *Upgrading Ethereum*, §2.9.3 "Randomness". https://eth2book.info/latest/part2/building_blocks/randomness/
17. Chia Network, "Proof of Time (VDFs)" and the Chia Green Paper (Oct 2024). https://docs.chia.net/proof-of-time/ ; https://docs.chia.net/files/ChiaGreenPaper_20241008.pdf
18. M. Mahmoody, C. Smith, D. J. Wu, "Can Verifiable Delay Functions Be Based on Random Oracles?", ICALP 2020; ePrint 2019/663. https://eprint.iacr.org/2019/663
19. M. Hall-Andersen, J. B. Nielsen, "On Valiant's Conjecture: Impossibility of Incrementally Verifiable Computation from Random Oracles", ePrint 2022/542. https://eprint.iacr.org/2022/542
20. M. E. Hellman, "A cryptanalytic time-memory trade-off", IEEE Trans. Inf. Theory 26(4):401–406, 1980. https://dl.acm.org/doi/10.1109/TIT.1980.1056220
21. N. Döttling, S. Garg, G. Malavolta, P. N. Vasudevan, "Tight Verifiable Delay Functions", SCN 2020; ePrint 2019/659. https://eprint.iacr.org/2019/659
22. R. Vuckovac, "One Way Function Candidate based on the Collatz Problem", arXiv:1801.05079 (2018). https://arxiv.org/abs/1801.05079
23. M. Ciet, A. J. Farrugia, T. Icart (Apple Inc.), "System and method for a Collatz based hash function", US 2013/0108038 A1, filed 30 Nov 2011, published 2 May 2013, abandoned. https://patents.google.com/patent/US20130108038
24. S. P. Singh, B. Singh, A. Mishra, "Collatz Hash: Hash Algorithm Using 3x+1 Conjecture", ePrint 2025/1606 (2025, rev. 2026). https://eprint.iacr.org/2025/1606
25. F. Bocart, "Inflation Propensity of Collatz Orbits: A New Proof-of-Work for Blockchain Applications", J. Risk and Financial Management 11(4):83, 2018. https://www.mdpi.com/1911-8074/11/4/83
26. H. M. A. Aljassas, S. Sasi, "Performance Evaluation of Proof-of-Work and Collatz Conjecture Consensus Algorithms", 2nd Int. Conf. on Computer Applications & Information Security (ICCAIS), 2019, DOI 10.1109/CAIS.2019.8769514. https://ieeexplore.ieee.org/document/8769514
27. K. Doãn, "Collatz-PoW: A Novel Proof-of-Work System Based on the Collatz Conjecture", ResearchHub, 2025, DOI 10.55277/researchhub.vzqyp4nb.1 (Crossref record only).
28. Xu, Tamir, "Pseudo-random number generators based on the Collatz conjecture", Int. J. Information Technology (Springer), 2019, DOI 10.1007/s41870-019-00307-9. https://link.springer.com/article/10.1007/s41870-019-00307-9
29. T. R. Działa, "Collatz-Weyl Generators: High Quality and High Throughput Parameterized Pseudorandom Number Generators", arXiv:2312.17043 (2023, rev. 2024). https://arxiv.org/abs/2312.17043
30. T. Stérin, D. Woods, "The Collatz process embeds a base conversion algorithm", Reachability Problems (RP) 2020, LNCS 12448; arXiv:2007.06979. https://arxiv.org/abs/2007.06979 ; summary page https://dna.hamilton.ie/2020-09-01-Collatz2.html
31. J. H. Conway, "Unpredictable iterations", Proc. 1972 Number Theory Conference, Univ. of Colorado, Boulder, pp. 49–52. (Reprinted in Lagarias (ed.), *The Ultimate Challenge: The 3x+1 Problem*, AMS 2010.)
32. S. A. Kurtz, J. Simon, "The Undecidability of the Generalized Collatz Problem", TAMC 2007, LNCS 4484. https://doi.org/10.1007/978-3-540-72504-6_49
33. W. Hesse, E. Allender, D. A. M. Barrington, "Uniform constant-depth threshold circuits for division and iterated multiplication", J. Comput. System Sci. 65(4):695–716, 2002. https://www.sciencedirect.com/science/article/pii/S0022000002000259
34. K. Hicks, G. L. Mullen, J. L. Yucas, R. Zavislak, "A Polynomial Analogue of the 3n+1 Problem", Amer. Math. Monthly 115(7):615–622, 2008. https://www.jstor.org/stable/27642557
35. G. Alon, A. Behajaina, E. Paran, "On the stopping time of the Collatz map in F₂[x]", arXiv:2401.03210 (2024). https://arxiv.org/abs/2401.03210
36. M. Inselmann, "On the average stopping time of the Collatz map in F₂[x]", arXiv:2401.12781 (2024). https://arxiv.org/abs/2401.12781
36a. "The Collatz map analogue in polynomial rings and in completions", arXiv:2312.00390 (2023, rev. Sept 2024). https://arxiv.org/abs/2312.00390 — authors not verified here.
36b. "Analogues of the 3x+1 Problem in Polynomial Rings of Characteristic 2", arXiv:1610.02545. https://arxiv.org/abs/1610.02545 — authors not verified here.
37. C. Dwork, M. Naor, "Pricing via Processing or Combatting Junk Mail", CRYPTO 1992. https://link.springer.com/chapter/10.1007/3-540-48071-4_10
38. A. Back, "Hashcash – A Denial of Service Counter-Measure", 2002. http://www.hashcash.org/papers/hashcash.pdf
39. V. Kabanets, J.-Y. Cai, "Circuit minimization problem", STOC 2000. https://dl.acm.org/doi/10.1145/335305.335314
40. S. Hirahara, "NP-Hardness of Learning Programs and Partial MCSP", FOCS 2022, pp. 968–979. https://eccc.weizmann.ac.il/report/2022/119/
41. R. Ilango, "SAT Reduces to the Minimum Circuit Size Problem with a Random Oracle", SIAM J. Comput., 2024, DOI 10.1137/24M1652568. https://doi.org/10.1137/24M1652568
41a. R. Ilango, "Constant Depth Formula and Partial Function Versions of MCSP Are Hard", SIAM J. Comput. (2023), DOI 10.1137/20M1383562. https://epubs.siam.org/doi/10.1137/20M1383562
42. R. Terras, "A stopping time problem on the positive integers", Acta Arithmetica 30 (1976), 241–252. (Used throughout the repo; see [[Collatz Bridge - Trits and Stopping Times]].)
44. "Improved verification limit for the convergence of the Collatz conjecture", J. Supercomputing (2025). https://link.springer.com/article/10.1007/s11227-025-07337-0 — cited only for the existence of table-driven sieving; author not verified here.
45. "SNARKChain: Proof-of-Useful-Work Blockchain Consensus with General-Purpose SNARK Marketplace", arXiv:2510.09729. https://arxiv.org/abs/2510.09729
46. "Chrisimos: A useful Proof-of-Work for finding Minimal Dominating Set of a graph", arXiv:2308.04407. https://arxiv.org/abs/2308.04407
47. "Challenges of Proof-of-Useful-Work (PoUW)", arXiv:2209.03865. https://arxiv.org/abs/2209.03865

Not cited: Soatok, "Collatzeral Damage: Bitwise and Proof Foolish" (Jan 2025, https://soatok.blog/2025/01/06/collatzeral-damage-bitwise-and-proof-foolish/) — checked; it proposes no primitive.
