# Kozyrev Orbital Spectrum

**Spec:** [[../superpowers/specs/2026-06-01-kozyrev-orbital-spectrum-design]]
**Plan:** [[../superpowers/plans/2026-06-01-kozyrev-orbital-spectrum]]
**Figure:** `data/collatz_kozyrev_spectrum.png`

## What it shows

Decomposition of three fields on $\mathbb{Z} / 2^K \mathbb{Z}$ (with $K = 11$) in the orthonormal Kozyrev wavelet basis — the eigenbasis of the 2-adic Vladimirov operator $D^\alpha$, which for $p = 2$ coincides with dyadic Haar wavelets.

Fields:

- $\chi(n)$ — Sturmian sign of the dropping class containing $n$ (the proved sign rule from [[Sturmian Bridge]]).
- $\mathbf{1}_{D_k}(n)$ for selected dropping classes.
- $T(n)$ — standard stopping time, as a control.

For each field we plot:

- **Kozyrev shell-energy spectrum** $E_j = \sum_a |c_{j, a}|^2$ — the "radial probability distribution" in the QM-orbital analogy ($j$ = principal quantum number).
- **Walsh weight-energy spectrum** $W_w = \sum_{\text{popcount}(m) = w} |F[m]|^2$ — the dual "momentum-like" basis (2-adic Fourier).
- **Partial reconstructions** $\chi_J$ — bit-split images at increasing reconstruction depth.
- **Dyadic spectrogram** — heatmap of $|c_{j, a}|^2$ on the $(j, a)$ triangle.
- **Duality scatter** — each field as a point $(H_K, H_W)$ in Kozyrev-shell-entropy vs Walsh-weight-entropy space.

## Hypotheses (see spec for falsifiability)

- **H1 — Sturmian shell concentration.** Does $E_j(\chi)$ depart from the shuffled-$\chi$ null band at shells related to the $\log_2 3$ Beatty rhythm?
- **H2 — Dropping-class fingerprint.** Do different $\mathbf{1}_{D_k}$ have distinguishable normalized Kozyrev (and Walsh) spectra?
- **H3 — $T$ is not Haar-sparse.** Stopping time should spread energy across many shells.
- **H4 — Discrete wave–particle duality.** The probed fields sit *off* the maximum-entropy corner — they cannot be simultaneously sparse in both Kozyrev and Walsh bases. Dropping-set fields specifically should land in the "Kozyrev-localized" half-plane ($H_K < H_W$), making them "particle-like" in this discrete 2-adic phase space. A dropping set that saturates the lower bound on $H_K + H_W$ would be a "coherent state of Collatz".

## Notes on interpretation

- Kozyrev shell $j = 0$ is the coarsest wavelet (one wavelet, support of size $N$). Shell $j = K - 1$ is finest (support of size 2). The bit-split layout puts shell-$j$ structure as $2^j$-period stripes in either bit-half axis.
- Walsh weight $w$ counts the set bits of $m$ — i.e., how many "binary frequencies" the character $W_m = (-1)^{\langle m, \cdot \rangle_2}$ engages. Weight 0 is the constant; weight $K$ is the fully-alternating character.
- Off-Beatty values of $n$ get $\chi(n) = 0$. This adds energy to *no* specific shell or weight — it broadens any spectral peak in both bases.
- The probed dropping classes $\{1, 3, 6, 8, 11, 13, 16\}$ are exactly the non-empty Beatty rungs $k_o = o + \lfloor o \log_2 3 \rfloor + 1$ for $o = 0, 1, 2, 3, 4, 5, 6$. Other small $k$ (2, 4, 5, 7, …) are structurally empty under the standard Collatz map.
