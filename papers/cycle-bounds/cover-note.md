# Cover note (for circulating the paper)

Subject: A short, self-contained derivation of 3x+1 cycle lower bounds — and a $25 bounty on it

Hi —

Attached is a 5-page note, *How Large a 3x+1 Cycle Must Be*. I want to be upfront about its scope so I don't waste your time: **it does not prove that no nontrivial Collatz cycle exists** — that's open, and I make no claim on it. What it does is give a clean, elementary, self-contained derivation of *lower bounds* on any cycle that might exist.

The whole argument is two short lemmas:

1. A cycle is a "closed word": (2^K − 3^m)·n_min = S.
2. The product identity ∏(3 + 1/n_i) = 2^K gives the exact bound n_min ≤ 1/(2^{K/m} − 3) — with equality on the trivial cycle, which is the built-in check.

Combined with the standard verification (no cycle below 2^68), this forces K/m into an interval of width 2^−69 around log₂3, and a continued-fraction step gives: any nontrivial cycle has ≥ 7.2×10¹⁰ odd elements, period ≥ 1.86×10¹¹, least element ≥ 2^68.

These numbers reproduce the published bounds of Eliahou and Hercher exactly (the numerator is Hercher's figure) — so I'm not claiming novelty of the *result*. The point is the packaging: the derivation fits on two pages and exposes that the governing continued fraction of log₂3 is the same one behind the base-6 "rotation" picture of the map.

Because it's short and elementary, I'm confident it's correct — confident enough to put **$25** on it: I'll pay the first person who finds a genuine mathematical error (a bad inequality, a gap in the continued-fraction step, a miscomputed constant, a misuse of the verification). "Already known" doesn't count — the prior art is cited.

All constants are reproducible from a 120-digit script in the repo. I'd genuinely value a sharp read.

Thanks,
Darcy
