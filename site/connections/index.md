# Connections to Classical Mathematics

The Collatz problem touches 2-adic analysis and Diophantine approximation, and its cycle equation asks how close powers of 2 and 3 can be, a question the abc conjecture also speaks to. These pages explore those connections. Some are known mathematics, some are my own explorations and analogies; each page says which.

---

- **[abc Conjecture](/connections/abc-conjecture)** — Would force the gap between a power of 2 and a power of 3 to have a large radical. For the size of the gap, Baker's theorem (below) already proves more. The Collatz map involves only primes 2 and 3, the minimal-radical case. Connects to: cycles, bit destruction.

- **Baker's Theorem** — Effective lower bounds on linear forms in logarithms give $|E - S \log_2 3| > S^{-\kappa}$ up to a constant factor, for an effective constant $\kappa$ (Rhin: $\kappa \approx 13.3$). This is the tool behind the results on $m$-cycles (Steiner 1977; Simons and de Weger 2005; Hercher 2023). Connects to: [The Cycle Equation: Small Cases](/cycles/convergent-elimination), [Bit Destruction](/proofs/bit-destruction).

- **S-Unit Equations** — The equation $2^a - 3^b = g$ has finitely many solutions for each fixed $g$ (Pólya 1918, Pillai 1931; Evertse 1984 bounded their number). Connects to: [Cycles as a Divisibility Question](/cycles/divisibility-obstruction).

- **Terras's Theorem** (1976) — For almost all $n$ (density 1), the Collatz orbit eventually drops below $n$. Tao (2019) proved that almost all orbits, in the sense of logarithmic density, attain almost bounded values. Neither statement says that almost all orbits reach 1. Connects to: [Mixing Modulo Powers of Two](/proofs/mixing).

- **Weyl Equidistribution** — The sequence $\{s \cdot \log_2 3\}$ is equidistributed mod 1, so small and large values of the bit destruction $\beta(s)$ occur in fixed proportions. The order in which they occur is far from random: it is the orbit of a rotation, the same one behind the Sturmian patterns on this site. Connects to: [Bit Destruction](/proofs/bit-destruction).

---

- **[The Collatz Zoo](/connections/universal-dynamics)** — The generalized $nx+c$, $x/y$ systems. Among the $nx+1$, $x/2$ systems with odd $n > 1$, $3x+1$ is the only one whose average drift is negative — a classical heuristic, since 3 is the only odd number between 1 and 4. A thermodynamic analogy: conservation, dissipation, and a conjectural "no perpetual motion".

- **[The Transfer Operator](/connections/hilbert-polya)** — A weighted matrix for the map cut off at a modulus $M$ has, for the moduli tried ($M = 6, 12, 24, 48, 96$), exactly four non-zero eigenvalues: 2, from the fixed point 0, and the three cube roots of $4/3$, from the trivial cycle $1 \to 4 \to 2 \to 1$. The page also draws a loose analogy with the Hilbert-Pólya picture and says why it is only an analogy.

- **[Eisenstein Lattice](/connections/eisenstein)** — The Eisenstein integers $\mathbb{Z}[\omega]$ as a way of drawing Collatz orbits. The prime 2 is inert ($N(2)=4$); 3 ramifies as $-(1+2\omega)^2$, with $N(1+2\omega) = 3$. Every orbit is drawn as a walk on the triangular lattice. The $4/3$ of the transfer-matrix page can be written $N(2)/N(1+2\omega)$, a ratio of Eisenstein norms; that is a relabelling, not a derivation. In a sample of orbits, steps with $\alpha \geq 4$ sit late on average (mean relative position 0.70 for odd starts below 6000), partly because the last step into 1 always has $\alpha \geq 4$.

- **[The Sturmian L-Probe](/connections/sturmian-l-probe)** — A sum of the sextic character $\chi_6$ of $\mathbb{Z}[\omega]$ over a single Collatz dropping set has a closed form, exact over whole periods: a rational multiple of $i/\sqrt{3}$ times the number of terms, whose sign follows the Sturmian cutting sequence of $\log_2 3$. Per non-zero term the size is a rational multiple of $\sqrt{3}/2$, and the phase is $\pm 90°$. No L-function is evaluated, and the proof is given in outline.
