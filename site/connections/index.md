# Connections to Classical Mathematics

The Collatz conjecture sits at the intersection of 2-adic analysis, Diophantine approximation, and the abc conjecture. These pages explore those connections. Some are known mathematics, some are my own explorations and analogies; each page says which.

---

- **[abc Conjecture](/connections/abc-conjecture)** — Would constrain how close powers of 2 and 3 can be. The Collatz map involves only primes 2 and 3, the minimal-radical case. Connects to: cycles, bit destruction.

- **Baker's Theorem** — Effective lower bounds on linear forms in logarithms give $|E - S \log_2 3| > S^{-\kappa}$ for an effective constant $\kappa$ (Rhin: $\kappa \approx 13$). This is the tool behind the known lower bounds on cycle length. Connects to: [Convergent Elimination](/cycles/convergent-elimination), [Bit Destruction](/proofs/bit-destruction).

- **S-Unit Equations** (Evertse, 1984) — The equation $2^a - 3^b = g$ has finitely many solutions for each fixed $g$. Connects to: [Divisibility Obstruction](/cycles/divisibility-obstruction).

- **Terras's Theorem** (1976) — For almost all $n$ (density 1), the Collatz orbit eventually drops below $n$. Tao (2019) proved a much stronger "almost all" result. Connects to: [3-Adic Mixing](/proofs/mixing).

- **Weyl Equidistribution** — The sequence $\{s \cdot \log_2 3\}$ is equidistributed mod 1, so slow and fast sets are interleaved without pattern. Connects to: [Bit Destruction](/proofs/bit-destruction).

---

- **[Universal Dynamics](/connections/universal-dynamics)** — The "Collatz Zoo" of generalized $nx+c$, $x/y$ systems. Among the systems studied, 3x+1 is the only nontrivial one whose average drift is negative — a classical heuristic, since 3 is the only odd prime less than $y^2 = 4$. A thermodynamic analogy: conservation, dissipation, and no perpetual motion.

- **[The Transfer Operator](/connections/hilbert-polya)** — A Perron-Frobenius operator for a model of the dynamics has exactly 4 non-zero eigenvalues: $\{2, (4/3)^{1/3} \cdot \omega^k\}$. The non-trivial spectrum lies on a circle of radius $(4/3)^{1/3}$, which invites an analogy with the critical line in the Hilbert-Pólya picture.

- **[Eisenstein Lattice](/connections/eisenstein)** — The Eisenstein integers $\mathbb{Z}[\omega]$ as an algebraic setting for Collatz. The halving prime 2 is inert ($N=4$), the tripling prime 3 ramifies ($N=3$). Every orbit traces a walk on the triangular lattice. The eigenvalue equation $\lambda^3 = N(2)/N(1+2\omega) = 4/3$ is a ratio of Eisenstein norms. Large $\alpha$ steps cluster late in orbits (position 0.74).

- **[The Sturmian L-Probe](/connections/sturmian-l-probe)** — The Hecke L-probe $\chi_6$ on $\mathbb{Z}[\omega]$, restricted to a single Collatz dropping set, has an *exact* closed form: $D_{\chi_6}^{(k_o)}(N) = i\sqrt{3} \cdot \epsilon_o \cdot A_o \cdot N_{k_o}/|R_{k_o}|$, where the phase $\epsilon_o$ is the Sturmian cutting sequence of $\log_2 3$. Every $\alpha_k$ is a rational multiple of $\sqrt{3}/2$, and every phase is $\pm 90°$.
