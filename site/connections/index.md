# Connections to Classical Mathematics

The structural results on this site connect to deep areas of number theory. The Collatz conjecture sits at the intersection of 2-adic analysis, Diophantine approximation, and the abc conjecture.

---

- **[abc Conjecture](/connections/abc-conjecture)** — Constrains how close powers of 2 and 3 can be. The Collatz map involves only primes 2 and 3, making it the minimal-radical case. Connects to: cycle elimination, bit destruction.

- **Roth's Theorem** — Bounds the irrationality measure of $\log_2 3$, giving $\beta(s) > c/s$. Connects to: [Bit Destruction Bound](/proofs/bit-destruction).

- **Baker's Theorem** — Effective lower bounds on linear forms in logarithms: $|k \log 2 - s \log 3| > \exp(-c \cdot \log k \cdot \log \log k)$. Gives the strongest unconditional bound on cycle length. Connects to: [Convergent Elimination](/cycles/convergent-elimination).

- **Pillai's Conjecture** — $|2^m - 3^n| \to \infty$ as $m + n \to \infty$. Would give $\beta(s) > c$ (constant), upgrading convergence to $O(\log n)$ drops. Connects to: [Bit Destruction Bound](/proofs/bit-destruction).

- **S-Unit Equations** (Evertse, 1984) — The equation $2^a - 3^b = g$ has finitely many solutions for each fixed $g$. Connects to: [Divisibility Obstruction](/cycles/divisibility-obstruction).

- **Terras's Theorem** (1976) — For almost all $n$ (density 1), the Collatz orbit eventually drops below $n$. Our mixing results give a cleaner proof. Connects to: [3-Adic Mixing](/proofs/mixing).

- **Weyl Equidistribution** — The sequence $\{s \cdot \log_2 3\}$ is equidistributed mod 1, meaning slow and fast sets are interleaved without pattern. Connects to: [Bit Destruction Bound](/proofs/bit-destruction).

---

- **[Universal Dynamics](/connections/universal-dynamics)** — The "Collatz Zoo" of generalized $nx+c$, $x/y$ systems. 3x+1 is the *only* nontrivial convergent system because 3 is the only odd prime less than $y^2 = 4$. Thermodynamic framework: conservation, dissipation, and no perpetual motion.

- **[The Transfer Operator](/connections/hilbert-polya)** — The Perron-Frobenius operator has exactly 4 non-zero eigenvalues: $\{2, (4/3)^{1/3} \cdot \omega^k\}$. The non-trivial spectrum lies on a critical circle of radius $(4/3)^{1/3}$, analogous to the critical line in the Hilbert-Polya conjecture. Convergence reduces to: $4 > 3$.

- **[Eisenstein Lattice](/connections/eisenstein)** — The Eisenstein integers $\mathbb{Z}[\omega]$ are the natural algebraic home for Collatz. The halving prime 2 is inert ($N=4$), the tripling prime 3 ramifies ($N=3$). Every orbit traces a walk on the triangular lattice. The eigenvalue equation $\lambda^3 = N(2)/N(1+2\omega) = 4/3$ is a ratio of Eisenstein norms. Large $\alpha$ steps cluster late in orbits (position 0.74), forced by modular tightening.

- **[The Sturmian L-Probe](/connections/sturmian-l-probe)** — The Hecke L-probe $\chi_6$ on $\mathbb{Z}[\omega]$, restricted to a single Collatz dropping set, has an *exact* closed form: $D_{\chi_6}^{(k_o)}(N) = i\sqrt{3} \cdot \epsilon_o \cdot A_o \cdot N_{k_o}/|R_{k_o}|$, where the phase $\epsilon_o$ is the Sturmian cutting sequence of $\log_2 3$. Proved: every $\alpha_k$ is a rational multiple of $\sqrt{3}/2$, every phase is $\pm 90°$. The proof reduces to a parity-bound induction on Beatty-bounded lattice paths.
