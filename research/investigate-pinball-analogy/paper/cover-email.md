# Cover email — draft

**To:** Manuel-Alejandro Reyes Jiménez (address: from the arXiv listing of 2606.02621)
**Subject:** Your Open Question 1 (orbits meeting 4 mod 6): verified for n < 2^56, and a backward companion to your Fibonacci theorem (the "mirror map")

Dear Dr. Reyes Jiménez,

I read your paper "A Fibonacci theorem for Collatz trajectories via modular graph structure" (arXiv:2606.02621) with great interest. I am an independent researcher, not a professional mathematician, and I am writing because some computations I have been doing bear directly on the first open question in your Section 5. I would value your view on whether any of it is already known.

Three things, in order of how sure I am that they are useful to you:

1. **Your open question, verified for every n < 2^56.** Avoiding 4 (mod 6) at levels 2..m is the same as the parity word of n containing no two consecutive halvings (after an odd step the value is 2 mod 3; halving gives 1 mod 3; a value is 4 mod 6 exactly when it was just produced by a halving and is about to be halved again). Because your theorem says only F(m+1) residues survive m levels, one can search the tree of surviving residues instead of all integers: the cost is about φ^B rather than 2^B. Every n > 1 below 2^56 meets 4 (mod 6). The longest survival is 173 steps, at n = 66,107,737,450,688,865. Records follow 3.27·log2(n), which is what a model with survival probability φ/2 per level predicts, so m0(n) ≤ 4·log2(n) looks like a reasonable conjectural form for the bound f(n) you ask about.

2. **A measurement you may find interesting.** Among the 3.65·10^11 integers that survive their own 56 binary digits, the probability of surviving one further level is 0.809017, 0.809017, 0.809012, 0.809021 at levels 56, 64, 72, 80 — and φ/2 = 0.809017. Past level B the parity is no longer read from the digits of n but from digits the iteration creates, and they leave H4 at exactly the rate free digits would.

   Two small remarks that I did not see in the paper: the 3x+1 conjecture implies a positive answer (the only odd predecessors of 1 other than 1 are (4^j − 1)/3, reached with exponent at least 4); and the statement is false for negative integers (−1, and the cycle −5, −7), so any proof has to use positivity.

3. **A backward, 3-adic companion to your theorem.** Consider m → 3m − 1 (m odd), m → 3m/2 (m even) — what the Collatz map becomes on negative integers if halving is replaced by n → n − |n/2|. I have been calling it the *mirror map*: it is the Collatz map reflected through zero, and where Collatz discards a factor 2 it exchanges it for a factor 3. It is injective, so its inverse is a terminating process and every integer has an "age". The number of residues mod 2·3^t with age ≥ t is exactly F(t+3), and the same holds with 3 replaced by any odd q. The proof is short: a backward odd-type step always lands on an odd number and can only leave an even one, so it never occurs twice in a row, and each backward step reads one base-q digit. It is your count with the roles of 2 and 3 exchanged and time reversed.

One more connection, which also concerns Mike Winkler's recent revision of arXiv:1412.0519 (v3, August 2026), where your paper is cited. His Proposition 5.1 says that any finite-state condition on parity words gives a transfer-matrix count of residues mod 2^k, and he remarks that your theorem is "not a direct corollary" of it because your states are residues mod 6. But the observation in point 1 shows that avoiding 4 (mod 6) *is* a parity-word condition — the forbidden factor 00 — so your Theorem 4.7 does follow directly from his principle. You may both find that worth knowing. I am copying him for that reason. [Delete this sentence if not copying him.]

A short note with proofs, the algorithm and tables is attached. I have searched Lagarias's annotated bibliographies and the OEIS without finding the backward law or the map, and I have read Winkler's v3, which is forward and mod 2^k throughout. I have only seen summaries of Wirsching's book, so I am not claiming the backward law is new. If you know of a prior statement I would be grateful for the reference.

The code is a few hundred lines (Python, and Rust for the large runs) and I am happy to share it. The computations and much of the drafting were done with the assistance of an AI system (Claude); every statement in the note was checked by computation.

Thank you for an enjoyable paper.

With best regards,
Darcy Thomas

---

## Before sending

- [ ] Replace 2^56 by 2^60 (and the record) if that run has finished — see `results/double_halving_rs_60.json`.
- [x] Winkler arXiv:1412.0519v3 read (pp. 1–3, 6–9): forward, mod 2^k, forbidden factor 11; no backward or 3-adic count. His address is on the paper: mike.winkler@ruhr-uni-bochum.de.
- [ ] If obtainable, read Wirsching LNM 1681 ch. II. If it contains the backward law, rewrite point 3 as "I noticed that the law in [ref] is the companion of your theorem".
- [ ] Decide whether to copy Winkler (recommended: the bridge between the two papers concerns him directly).
- [ ] Find the author's address on the arXiv abstract page. I did not look it up.
- [ ] Attach `fibonacci-age-law.pdf`.
- [ ] Optional first step instead of email: a MathOverflow question, "Is this Fibonacci count for the inverse of m → 3m−1, 3m/2 known?"
