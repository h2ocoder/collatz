# Kozyrev Orbital Spectrum of Collatz Dropping Sets — Design Spec

**Date:** 2026-06-01
**Status:** Locked. Implementation proceeds via writing-plans.

## Premise

Quantum-mechanical orbitals are eigenstates of a self-adjoint operator (the Hamiltonian); their "shapes" are level sets of those eigenfunctions. To ask "what is the shape of a Collatz dropping set in 2-adic space" is therefore to ask: in what eigenbasis of a natural 2-adic operator does the dropping-set indicator look simple?

The natural operator is **Vladimirov's $D^\alpha$**, the pseudo-differential 2-adic Laplacian. Its discrete eigenbasis on $\mathbb{Z}_2 / 2^K \mathbb{Z}_2$ is the **Kozyrev wavelet basis**, which for $p = 2$ coincides with the Haar wavelets on the dyadic tree. Decomposing the existing Sturmian sign field $\chi$, dropping-set indicators $\mathbf{1}_{D_k}$, and stopping time $T$ in this basis yields a literal "orbital spectrum" indexed by shell $j$ (principal quantum number) and offset $a$ (orientation).

The existing `scripts/collatz_2adic_potential.py` already builds the Sturmian-charge field and a Newton-style $4^{v_2}$ kernel. That is a static field. This spec extends to the eigenproblem.

## Why this approach

The repo's 2-adic substrate is already in place:

- $\chi(n)$ — Sturmian sign of the dropping class containing $n$ (proved in `Sturmian Bridge` Parts 5–6).
- Dropping classes $D_k$ — already exposed by `collatz.dropping`.
- Bit-split 2D imaging — already in `scripts/collatz_2adic_potential.py`, faithful pictorial encoding of $\mathbb{Z}_2 / 2^K \mathbb{Z}_2$.

Kozyrev wavelets are the *exact* operator-eigenfunction analogue of spherical harmonics × radial wavefunctions, with explicit closed form. The decomposition is computable in $O(N \log N)$ via the fast Haar transform. There is no parameter to tune (unlike a Schrödinger Hamiltonian with $\chi$-potential, which would introduce a coupling $\lambda$); this keeps falsifiability clean.

## Locked decisions

| Decision | Choice | Why |
|---|---|---|
| Operator | Vladimirov $D^\alpha$ on $\mathbb{Z}_2 / 2^K \mathbb{Z}_2$ | Canonical 2-adic Laplacian; eigenfunctions are Kozyrev wavelets |
| Basis realization | Dyadic Haar wavelets indexed by shell $j \in \{0,\dots,K{-}1\}$ and offset $a \in \{0,\dots,2^j{-}1\}$, plus constant mode | Kozyrev = Haar for $p=2$; admits $O(N\log N)$ FHT |
| Depth | $K = 11$ for headline, scalable up to $K = 16$ | Matches existing `collatz_2adic_potential.py`; reusable bit-split coords |
| Input fields | $\chi(n)$, $\mathbf{1}_{D_k}$ for $k \in \{1,2,4,5,7,8\}$, $T(n)$ | $\chi$ tests Sturmian claim; $D_k$ tests fingerprint claim; $T$ is control |
| Off-Beatty handling | $\chi = 0$ at off-Beatty values (existing convention) | Preserves Parseval; no special-case in the transform |
| Numeric type | `np.float64` throughout | Exact-`Fraction` adds nothing; Haar coefficients are inherently floating energies |
| Visualization output | Single PNG `data/collatz_kozyrev_spectrum.png` | Matches existing script convention |
| Coupling to embeddings | Standalone for now | Avoids dependency on v1–v8 `collatz/embeddings/` lens machinery until results justify it |

## Architecture

### Module layout

New module `collatz/wavelets.py` (no subpackage yet — promote later if it grows):

```
collatz/
  wavelets.py            # Fast Haar transform + Kozyrev basis access
scripts/
  collatz_kozyrev_spectrum.py   # Builds inputs, runs FHT, writes PNG
tests/
  test_wavelets.py
```

### Components

**`collatz/wavelets.py`** — Kozyrev/Haar machinery:
- `haar_forward(f: np.ndarray) -> tuple[float, np.ndarray]`: takes a length-$N$ vector ($N$ a power of 2), returns `(c0, coeffs)` where `c0 = ⟨f, φ⟩` is the constant-mode coefficient and `coeffs[idx(j,a)] = ⟨f, ψ_{j,a}⟩` for $j \in [0, K)$, $a \in [0, 2^j)$. Total length $N - 1$. Implementation: standard in-place dyadic averaging-and-differencing, $O(N \log N)$.
- `haar_inverse(c0: float, coeffs: np.ndarray, depth_cutoff: int | None = None) -> np.ndarray`: reconstruct $f$ from coefficients; if `depth_cutoff = J`, use only shells $j < J$ (partial reconstruction $f_J$).
- `shell_energies(coeffs: np.ndarray, K: int) -> np.ndarray`: returns shape `(K,)` with $E_j = \sum_a |c_{j,a}|^2$.
- `coefficient_grid(coeffs: np.ndarray, K: int) -> np.ndarray`: returns shape `(K, 2^{K-1})` ragged-padded array with `|c_{j,a}|^2` for triangle-plot rendering.
- `kozyrev_basis_vector(j: int, a: int, K: int) -> np.ndarray`: build single basis vector $\psi_{j,a}$ explicitly (testing aid + illustration plot).
- `idx(j: int, a: int) -> int`: flat index helper, `2^j - 1 + a`.

Normalization: $\psi_{j,a}$ has $\ell^2$ norm 1; $\phi \equiv 1/\sqrt{N}$. Parseval: $\|f\|_2^2 = c_0^2 + \sum_{j,a} c_{j,a}^2$.

**`scripts/collatz_kozyrev_spectrum.py`** — pipeline + figure:
1. Build $\chi(n)$ for $n \in [1, N]$ via the same logic as `collatz_2adic_potential.py` (factor into a helper there or duplicate; see Refactor below).
2. Build $\mathbf{1}_{D_k}(n)$ for each target $k$ via `collatz.dropping`.
3. Build $T(n)$ via `standard_stopping_time` (already factorable).
4. Run `haar_forward` on each.
5. Compose figure: shell-energy curves, bit-split partial reconstructions $f_J$ for $J \in \{2, 4, 6, 8, K\}$, dyadic spectrogram, shuffled-$\chi$ null overlay.
6. Save PNG.

**Refactor (in-scope, minimal):** lift `sturmian_sign`, `beatty_to_o`, and `bits_to_2d` from `scripts/collatz_2adic_potential.py` into `collatz/utils.py`, and update that script to import them. For stopping time, use the existing `collatz.stopping` API (or `collatz.core.orbit`) rather than the script-local `standard_stopping_time` — verify equivalence first and remove the duplicate. This is the targeted improvement justified by the new consumer.

### Data flow

```
inputs (N=2^K vectors)        Haar coeffs        derived
─────────────────────         ──────────────     ──────────────────
χ(n)            ──┐                              shell energies E_j
1_{D_k}(n)      ──┼── haar_forward ──► c_{j,a} ── shell heatmap |c_{j,a}|²
T(n)            ──┘                              partial reconstructions f_J
shuffled χ      ──┘ (null)                       null shell energies
```

## Falsifiable claims

- **H1 — Sturmian shell concentration.** Shell energies $E_j(\chi)$ deviate measurably from a shuffled-$\chi$ null at specific $j$. Specifically, the surplus energy localizes at shells related to the $\log_2 3$ Beatty rhythm. *Test:* compute $E_j(\chi) - E_j(\chi_{\text{shuffled}})$ averaged over $\ge 100$ shuffles; flag shells with $|z| > 3$.
- **H2 — Dropping-class fingerprint.** The normalized spectra $\hat E_j(\mathbf{1}_{D_k}) = E_j / \sum_j E_j$ differ across $k$ by more than the shuffle null spread. *Test:* pairwise $\ell^1$ distance between $\hat E_j$ vectors, compared to within-class shuffle distance.
- **H3 — $T$ is not Haar-sparse.** Stopping time $T(n)$ has wavelet entropy $H(\hat E_j(T))$ close to the maximum $\log_2 K$, distinguishing it from $\chi$ and $\mathbf{1}_{D_k}$.

Negative outcomes are publishable: H1 failing means the Sturmian rule's geometric content is not 2-adic-radial; H2 failing means dropping classes are wavelet-equivalent and the "orbital" framing was wrong.

## Visualization layout

Single figure `data/collatz_kozyrev_spectrum.png` with a 3×3 grid:

| | Col 0 | Col 1 | Col 2 |
|---|---|---|---|
| **Row 0** | $E_j(\chi)$ overlaid with null band | $E_j(\mathbf{1}_{D_k})$ for selected $k$ | $E_j(T)$ |
| **Row 1** | Bit-split image of $\chi$ (input) | Bit-split image of $\chi_{J=4}$ partial recon | Bit-split image of $\chi_{J=8}$ partial recon |
| **Row 2** | Dyadic spectrogram (triangle) of $\chi$ | Dyadic spectrogram of $\mathbf{1}_{D_1}$ | Dyadic spectrogram of $T$ |

DPI 120, figsize ≈ (16, 13), `RdBu_r` for signed quantities, `viridis` for energies.

## Testing strategy

`tests/test_wavelets.py`:

- **Parseval round-trip.** For random $f$, assert $\|f\|_2^2 \approx c_0^2 + \sum c_{j,a}^2$ to `rtol = 1e-12`.
- **Inverse round-trip.** `haar_inverse(*haar_forward(f)) ≈ f` to `rtol = 1e-12`.
- **Single-ball indicator.** For $f = \mathbf{1}_B$ where $B$ is the 2-adic ball of radius $2^{K-j_0}$ around $a_0$, assert exactly one nonzero coefficient at index `idx(j_0, a_0)` (within tolerance).
- **Orthonormality.** For $K = 5$ ($N = 32$), assert all pairwise inner products of `kozyrev_basis_vector` outputs equal $\delta_{(j,a),(j',a')}$.
- **Partial-reconstruction monotonicity.** As $J$ increases, $\|f - f_J\|_2$ decreases monotonically.

## Edge cases

- **N not a power of 2.** Not supported; the script generates exactly $N = 2^K$ inputs.
- **Off-Beatty $\chi = 0$ values.** Handled implicitly — zero contribution to every coefficient; Parseval holds.
- **Empty dropping classes.** Some $D_k$ may be empty for small $K$ (notably large $k$); script skips those with a logged warning.
- **Stopping time non-droppers ($T = 0$).** Treated as zero in $T(n)$ field; documented in script header.

## Out of scope

- **Approach B** — discrete Schrödinger on dyadic tree with $\chi$ as potential. Deferred; revisit if H1 is positive.
- **Approach C** — heat-kernel smoothing for "electron cloud" pictures. Deferred; visually pretty but not eigen-decomposition.
- **$p \neq 2$.** Generalization to $p$-adic Kozyrev for other primes. Deferred until binary case settles H1/H2.
- **Interactive site visualization.** Static PNG first; site integration only if results are surprising.
- **Embedding-framework integration.** Keep `collatz/wavelets.py` standalone; do not register as a `collatz/embeddings/` lens yet.
- **Beyond Haar.** No Daubechies / Meyer / other wavelet families — they are not eigenfunctions of $D^\alpha$ and break the QM analogy.

## Success criteria

1. Test suite passes (Parseval, round-trip, single-ball, orthonormality, monotonicity).
2. `scripts/collatz_kozyrev_spectrum.py` runs end-to-end at $K = 11$ in under 60 s on a laptop.
3. The headline shell-energy plot $E_j(\chi)$ either visibly departs from the null band (H1 positive) or visibly tracks it (H1 negative). Either outcome is a result.
4. Exploration note drafted in `docs/Explorations/Kozyrev Orbital Spectrum.md` summarizing what the spectra show.
