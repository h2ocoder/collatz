# Chain vs Stochastic Model

**Date:** 2026-09-10 · **Scripts:** `scripts/chain_vs_stochastic_model.py`, `scripts/dropping_tail_vs_ballot.py`, `scripts/residue_vs_rise.py`
**Question:** The word sequence along the drop chain is an exact renewal process *over residue classes* (consecutive dropping words are independent, because dest runs over a full coset as $n$ runs over its class). So the only structure a chain can have is the **size–residue coupling**: what happens once the chain runs longer than $\log_2 n$ steps and is "using" residue digits $n$ does not have. Is that coupling measurable?

## Method

Compare integers in $[N/2, N]$ against the Lagarias–Weiss random walk (fair parity bits; odd step $+\log_2 3 - 1$ and 2 standard steps, even step $-1$ and 1 step; stop at log-size 0), with three refinements: (1) first-drop tail against the *exact* ballot count, which has no endgame; (2) the residue $r_v$ of every word of length 20 against the word's rise; (3) a hybrid model that follows the random walk down to a cutoff size and then adds the *true* total stopping time of an integer of that size, to remove the model's inaccuracy at small values.

## Results

**First drop (T-map dropping time $L$), $N = 2\times10^7$, 5M integers:**

| $K$ | 30 | 40 | 60 | 80 | 100 | 120 | 150 |
|---|---|---|---|---|---|---|---|
| empirical / ballot | 0.999 | 0.998 | 0.985 | 1.020 | 1.036 | 1.125 | 1.047 |

Exactly 1.000 for $K \le \log_2 N$ (Terras), and 1 within noise beyond it. A 5–17% deficit seen at $N = 2\times10^6$ for $K=40$–$120$ did not survive the 10× larger sample: finite-size.

**Residue vs rise, all $2^{19}$ words of length 20:** corr(height, $r_v/2^K$) $= +0.0006$; $P(r_v/2^K < 0.01)$ is $0.0100 \pm 0.0002$ in every height bin with more than 1000 words. Only the nearly-all-ones bin (191 words, height $\ge 8$ bits) skews large ($P(<0.1) = 0.052$), for the classical reason that $k$ leading ones force $n \equiv -1 \pmod{2^k}$.

**Total stopping time per bit $H$, tail ratio empirical / model:**

| model | $H>12$ | $H>15$ | $H>18$ | $H>21$ |
|---|---|---|---|---|
| pure random walk, $N=2\times10^6$ | 0.83 | 0.54 | 0.29 | 0.14 |
| walk to 12 bits + exact endgame | 1.06 | 0.96 | 0.67 | 0.41 |
| walk to 16 bits + exact endgame | 1.16 | 1.23 | 1.03 | 0.69 |
| walk to 18 bits + exact endgame | 1.17 | 1.28 | 1.29 | 1.03 |
| walk to 16 bits, $N = 2\times10^7$ | 1.18 | 1.20 | 1.00 | 0.92 |

The apparent factor-7 suppression of hard numbers is entirely the random walk's inaccuracy for small values; as the cutoff rises toward $\log_2 N$ the tail ratio goes to 1 (the mild excess at moderate $H$ is the $+C_w$ terms making real values slightly larger than the model's). Max $H$ observed: 26.8 at $N=2\times10^6$; Lagarias–Weiss predict $\limsup H = 41.677\ln 2 = 28.9$.

## Conclusion

Within reach ($n \le 2\times10^7$), **no size–residue coupling is measurable**: hard numbers occur exactly as often as the i.i.d. parity model predicts, in the first drop, in the whole chain, and in the residues of rising words. Combined with today's other nulls ([[Prime Factorization and Dropping Rate]], [[Periodic Point Proximity]]), every statistic tried says the stochastic model is exact at every accessible scale. That is the standard picture (Lagarias–Weiss 1992; Kontorovich–Lagarias 2009), re-verified here with a proper endgame correction — the correction matters: without it one would report a spurious factor-7 suppression.

**Consequence for strategy.** Statistical exploration of orbits has no remaining signal to find; the conjecture is the statement that the model has *no exceptions*, and exceptions of density zero are invisible to any experiment. Rigorous progress has to come from the non-random side: the 3-adic determinism of the backward tree (the density exponent, [[Density Exponent]]), Diophantine bounds (cycles), or measure-theoretic arguments (Tao).

## Related

[[Density Exponent]] · [[Periodic Point Proximity]] · [[Prime Factorization and Dropping Rate]] · [[Three-Bit Countdown]] (its $A(n)$ is the minimal-survivor object $M(K)$ restricted to Set$_3$)
