# VitePress Collatz Research Site — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a VitePress site at `site/` presenting proved Collatz conjecture results with KaTeX-rendered math, organized as a research monograph.

**Architecture:** VitePress 1.x with `@mdit/plugin-katex` for math rendering. Content in Markdown with LaTeX. Custom CSS for theorem/proof boxes. No interactive widgets in v1.

**Tech Stack:** VitePress, KaTeX, `@mdit/plugin-katex`, TypeScript config

**Spec:** `docs/plans/2026-04-02-vitepress-site-design.md`

---

## File Map

```
site/
├── package.json                          # CREATE — deps and scripts
├── .vitepress/
│   ├── config.mts                        # CREATE — nav, sidebar, KaTeX plugin
│   └── theme/
│       ├── index.ts                      # CREATE — KaTeX CSS import
│       └── custom.css                    # CREATE — theorem/proof box styles
├── index.md                              # CREATE — home page
├── foundations/
│   ├── definitions.md                    # CREATE — core math definitions
│   └── terminology.md                    # CREATE — Paper 1 vs Paper 2 table
├── proofs/
│   ├── affine-orbit.md                   # CREATE — Affine Orbit Structure proof
│   ├── logarithmic-escape.md             # CREATE — Logarithmic Escape proof
│   ├── bit-destruction.md                # CREATE — Bit Destruction Bound
│   └── mixing.md                         # CREATE — 3-Adic Mixing theorem
├── cycles/
│   ├── convergent-elimination.md         # CREATE — convergent elimination results
│   └── divisibility-obstruction.md       # CREATE — the conjecture + evidence
├── roadmap/
│   └── path-to-proof.md                  # CREATE — two fronts roadmap
├── connections/
│   ├── index.md                          # CREATE — connections landing page
│   └── abc-conjecture.md                 # CREATE — abc connection
└── public/
    └── two-fronts.svg                    # CREATE — roadmap diagram
```

Also modify:
- `.gitignore` — add `site/node_modules/`, `site/.vitepress/cache/`, `site/.vitepress/dist/`

---

### Task 1: Bootstrap VitePress + KaTeX

**Files:**
- Create: `site/package.json`
- Create: `site/.vitepress/config.mts`
- Create: `site/.vitepress/theme/index.ts`
- Create: `site/.vitepress/theme/custom.css`
- Create: `site/index.md`
- Modify: `.gitignore`

- [ ] **Step 1: Create site directory and package.json**

```bash
mkdir -p site
```

Write `site/package.json`:
```json
{
  "name": "collatz-research",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vitepress dev",
    "build": "vitepress build",
    "preview": "vitepress preview"
  }
}
```

- [ ] **Step 2: Install dependencies**

```bash
cd site && npm add -D vitepress @mdit/plugin-katex katex
```

Expected: `node_modules/` created, `package-lock.json` generated.

- [ ] **Step 3: Add site ignores to .gitignore**

Append to `.gitignore`:
```
# VitePress site
site/node_modules/
site/.vitepress/cache/
site/.vitepress/dist/
```

- [ ] **Step 4: Create VitePress config with KaTeX**

Write `site/.vitepress/config.mts`:
```ts
import { defineConfig } from 'vitepress'
import { katex } from '@mdit/plugin-katex'

export default defineConfig({
  title: 'Collatz Research',
  description: 'Toward a proof of the Collatz conjecture',

  markdown: {
    config: (md) => {
      md.use(katex, { mhchem: false })
    }
  },

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Foundations', link: '/foundations/definitions' },
      { text: 'Proofs', link: '/proofs/affine-orbit' },
      { text: 'Cycles', link: '/cycles/convergent-elimination' },
      { text: 'Roadmap', link: '/roadmap/path-to-proof' },
      { text: 'Connections', link: '/connections/' }
    ],

    sidebar: [
      {
        text: 'Foundations',
        items: [
          { text: 'Definitions', link: '/foundations/definitions' },
          { text: 'Terminology Map', link: '/foundations/terminology' }
        ]
      },
      {
        text: 'Proved Results',
        items: [
          { text: 'Affine Orbit Structure', link: '/proofs/affine-orbit' },
          { text: 'Logarithmic Escape', link: '/proofs/logarithmic-escape' },
          { text: 'Bit Destruction Bound', link: '/proofs/bit-destruction' },
          { text: '3-Adic Mixing', link: '/proofs/mixing' }
        ]
      },
      {
        text: 'Cycle Analysis',
        items: [
          { text: 'Convergent Elimination', link: '/cycles/convergent-elimination' },
          { text: 'Divisibility Obstruction', link: '/cycles/divisibility-obstruction' }
        ]
      },
      {
        text: 'Roadmap',
        items: [
          { text: 'Path to Proof', link: '/roadmap/path-to-proof' }
        ]
      },
      {
        text: 'Connections',
        items: [
          { text: 'Overview', link: '/connections/' },
          { text: 'abc Conjecture', link: '/connections/abc-conjecture' }
        ]
      }
    ],

    outline: { level: [2, 3] }
  }
})
```

- [ ] **Step 5: Create custom theme entry with KaTeX CSS**

Write `site/.vitepress/theme/index.ts`:
```ts
import DefaultTheme from 'vitepress/theme'
import 'katex/dist/katex.min.css'
import './custom.css'

export default DefaultTheme
```

- [ ] **Step 6: Create custom CSS for theorem/proof boxes**

Write `site/.vitepress/theme/custom.css`:
```css
.theorem {
  border-left: 4px solid var(--vp-c-brand-1);
  background: var(--vp-c-bg-soft);
  padding: 1rem 1.5rem;
  margin: 1.5rem 0;
  border-radius: 0 8px 8px 0;
}

.theorem strong:first-child {
  color: var(--vp-c-brand-1);
}

.proof {
  border-left: 2px solid var(--vp-c-divider);
  padding: 0.75rem 1.5rem;
  margin: 1rem 0;
}

.proof::after {
  content: '∎';
  display: block;
  text-align: right;
  margin-top: 0.5rem;
  color: var(--vp-c-text-2);
}

.corollary {
  border-left: 3px solid var(--vp-c-green-1);
  background: var(--vp-c-bg-soft);
  padding: 0.75rem 1.5rem;
  margin: 1rem 0;
  border-radius: 0 6px 6px 0;
}
```

- [ ] **Step 7: Create minimal home page to test**

Write `site/index.md`:
```markdown
---
layout: home
hero:
  name: Collatz Research
  text: Toward a Proof
  tagline: New structural results on the Collatz conjecture using affine orbit theory, modular arithmetic, and connections to the abc conjecture.
  actions:
    - theme: brand
      text: Read the Proofs
      link: /proofs/affine-orbit
    - theme: alt
      text: Path to Proof
      link: /roadmap/path-to-proof

features:
  - title: Affine Orbit Structure
    details: Every drop through a dropping set is an exact affine map. Proved by induction.
    link: /proofs/affine-orbit
  - title: Logarithmic Escape
    details: No orbit can stay in one dropping set for more than O(log n) steps.
    link: /proofs/logarithmic-escape
  - title: Bit Destruction Bound
    details: Every drop destroys β(s) = 1 − {s·log₂3} bits. Connected to Roth's theorem.
    link: /proofs/bit-destruction
  - title: Cycle Elimination
    details: Half of all convergents killed by sign. First non-trivial convergent (gap=13) eliminated.
    link: /cycles/convergent-elimination
---

::: tip What's New (April 2026)
Six new structural results proved, including the Affine Orbit Structure theorem, Logarithmic Escape bound, and the first computational elimination of a non-trivial cycle candidate (gap=13). See the [roadmap](/roadmap/path-to-proof) for the full picture.
:::

## The Research

This work approaches the Collatz conjecture through three complementary lenses:

1. **Dropping Sets, Pythagorean Triples & Riemann** (Paper 1) — Classification of integers by dropping time, orbital triples, complex multipliers
2. **Stopping Classes & Geometric Correspondence** (Paper 2) — Diophantine lines, stopping signatures, geometric structure
3. **Proportional Power Ratios** (Paper 3) — Base-6 lattice, polar structure, the log₂6 spectrum

The results on this site unify these perspectives through the **affine orbit framework**, revealing that every Collatz drop is a computable linear map whose properties connect to deep number theory (Roth's theorem, the abc conjecture, S-unit equations).
```

- [ ] **Step 8: Verify the site boots with math rendering**

```bash
cd site && npm run dev
```

Expected: Site loads at `http://localhost:5173`. Home page shows hero and feature cards.

- [ ] **Step 9: Commit**

```bash
git add site/ .gitignore
git commit -m "feat: bootstrap VitePress site with KaTeX math rendering"
```

---

### Task 2: Foundations Pages

**Files:**
- Create: `site/foundations/definitions.md`
- Create: `site/foundations/terminology.md`

- [ ] **Step 1: Write definitions page**

Write `site/foundations/definitions.md`. Content source: `docs/Conjectures/` files and `CLAUDE.md`. Include formal definitions with examples for:

- Collatz step: $f(n) = n/2$ if even, $3n+1$ if odd
- Orbit: $[n, f(n), f^2(n), \ldots, 1]$
- Dropping time (= stopping time): steps to first value $< n$
- Dropping destination: first value $< n$
- Dropping orbit: $[n, f(n), \ldots, 2d]$ (includes $n$, excludes destination)
- Dropping set $\text{Dset}_k$: all $n$ with dropping time $k$
- Orbital oddity: count of odd numbers in the dropping orbit
- Syracuse map: $S(n) = (3n+1)/2^{v_2(3n+1)}$
- Alpha value / alpha sequence: $v_2(3n+1)$ along the Syracuse orbit

Each definition should use the `<div class="theorem">` box and include a worked example.

- [ ] **Step 2: Write terminology map page**

Write `site/foundations/terminology.md`. Content source: CLAUDE.md terminology table.

Include the full Paper 1 vs Paper 2 mapping table, plus a note explaining why both terminologies exist (two independent papers discovering the same structure).

- [ ] **Step 3: Verify pages render with correct math**

```bash
cd site && npm run dev
```

Navigate to `/foundations/definitions` and `/foundations/terminology`. Verify LaTeX renders and theorem boxes display.

- [ ] **Step 4: Commit**

```bash
git add site/foundations/
git commit -m "feat: add foundations pages (definitions, terminology map)"
```

---

### Task 3: Affine Orbit Structure Proof Page

**Files:**
- Create: `site/proofs/affine-orbit.md`

Content source: `docs/Conjectures/Affine Orbit Structure.md`

- [ ] **Step 1: Write the proof page**

Write `site/proofs/affine-orbit.md` following the page template:

1. **Statement** (theorem box): For any $\text{Dset}_k$ with orbital oddity $s$, within each residue subgroup mod $2^{k-s}$: $\text{dest}(n) = \frac{3^s}{2^{k-s}} \cdot n + C$
2. **Significance**: Links contraction ratio to stopping time spectrum. The slope is universal across all subgroups — only the intercept varies.
3. **Examples**: Table of slopes for $k = 1, 3, 6, 8, 11, 13$ with exact formulas. Include a worked example for Set$_3$: $n = 5 \Rightarrow \text{dest} = \frac{3}{4}(5) + \frac{1}{4} = 4$.
4. **Proof**: Full induction from the Obsidian source. Base case ($k=0$), even step case, odd step case. Include the key insight about bit consumption: even steps consume one bit, odd steps consume none.
5. **Corollaries**: (a) Orbital oddity is constant within $\text{Dset}_k$. (b) Orbit sum and max are affine in $n$. (c) Period of $\text{Dset}_k$ is $2^{k-s}$. (d) $3^s/2^{k-s} < 1$ iff $k > s \log_2 6$.
6. **Related**: Links to Logarithmic Escape, Bit Destruction, Odd Stopping Time Spectrum.

Use `<div class="theorem">`, `<div class="proof">`, and `<div class="corollary">` wrappers.

- [ ] **Step 2: Verify math renders correctly**

```bash
cd site && npm run dev
```

Check that all display math, inline math, fractions, and the QED marker render correctly on `/proofs/affine-orbit`.

- [ ] **Step 3: Commit**

```bash
git add site/proofs/affine-orbit.md
git commit -m "feat: add Affine Orbit Structure proof page"
```

---

### Task 4: Logarithmic Escape Proof Page

**Files:**
- Create: `site/proofs/logarithmic-escape.md`

Content source: `docs/Conjectures/Logarithmic Escape Theorem.md`

- [ ] **Step 1: Write the proof page**

Write `site/proofs/logarithmic-escape.md`:

1. **Statement**: For any $\text{Dset}_k$ with period $P = 2^{k-s}$, max consecutive self-transitions from $n$ is $m \leq \log_P(n) - 1$.
2. **Significance**: Much stronger than contraction ratio bounds. Forces orbits to change sets frequently.
3. **Examples**: Table showing bounds for Set$_3$ ($P=4$), Set$_6$ ($P=16$), Set$_8$ ($P=32$), Set$_{13}$ ($P=256$). Verified chain table for Set$_3$: $m=1$ through $m=7$ with smallest $n$ and chains.
4. **Proof**: Modular tightening induction. Base: membership requires $n \equiv r \pmod{P}$. Step: self-transition tightens to $P^{m+2}$ via coprimality of $3^s$ and $P$. Bound: $n \geq P^{m+1}$.
5. **Corollaries**: (a) No orbit camps in slow-contracting sets. (b) Combined with bit destruction, gives progress guarantees.
6. **Related**: Links to Affine Orbit Structure (prerequisite).

- [ ] **Step 2: Verify and commit**

```bash
cd site && npm run dev
```

Check `/proofs/logarithmic-escape`. Then:

```bash
git add site/proofs/logarithmic-escape.md
git commit -m "feat: add Logarithmic Escape Theorem proof page"
```

---

### Task 5: Bit Destruction Bound Page

**Files:**
- Create: `site/proofs/bit-destruction.md`

Content source: `docs/Conjectures/Bit Destruction Bound.md`

- [ ] **Step 1: Write the page**

Write `site/proofs/bit-destruction.md`:

1. **Statement**: $\beta(s) = \lceil s \cdot \log_2 3 \rceil - s \cdot \log_2 3 = 1 - \{s \cdot \log_2 3\}$, always $> 0$.
2. **Significance**: Every drop destroys bits. Connects to Diophantine approximation.
3. **Examples**: Table of $\beta(s)$ for $s = 0$ through $s = 29$, marking slow sets. Show the pattern: slow sets occur when $s \cdot \log_2 3$ is close to an integer from below.
4. **Proof of identity**: Direct from the contraction ratio $3^s/2^{k-s}$ where $k = s + \lceil s \log_2 3 \rceil$.
5. **Roth's theorem connection**: Best rational approximations to $\log_2 3$ give slowest sets. Table of convergents with their $\beta$ values. Roth gives $\beta(s) > c/s$, yielding $O(\log^2 n)$ conditional convergence bound.
6. **Numerical verification**: Table of bit budgets for $B = 64, 128, 256, 1024$.
7. **Related**: Links to convergents of $\log_2 3$, Affine Orbit Structure, Logarithmic Escape.

- [ ] **Step 2: Verify and commit**

```bash
cd site && npm run dev
```

Check `/proofs/bit-destruction`. Then:

```bash
git add site/proofs/bit-destruction.md
git commit -m "feat: add Bit Destruction Bound page"
```

---

### Task 6: 3-Adic Mixing Page

**Files:**
- Create: `site/proofs/mixing.md`

Content source: `docs/Conjectures/Bit Destruction Bound.md` (sections "Unconditional Mixing Theorem" and "Combined Picture"). The mixing theorem is documented within the Bit Destruction Bound file — extract the mixing-specific content into this standalone page and expand with the entropy measurement details and ord(3 mod 2^B) proof.

- [ ] **Step 1: Write the page**

Write `site/proofs/mixing.md`:

1. **Statement**: $\text{ord}(3 \bmod 2^B) = 2^{B-2}$ for $B \geq 3$. Post-drop destinations are equidistributed mod $2^B$.
2. **Significance**: The Collatz map scrambles 2-adic information via multiplication by odd powers of 3.
3. **Examples**: Table of $\text{ord}(3 \bmod 2^B)$ for $B = 2$ through $20$. Show the ratio is always $1/4$.
4. **Proof**: Classical result. For $B \geq 3$: $3 = 1 + 2$, so $3^{2^{B-2}} = (1+2)^{2^{B-2}} \equiv 1 \pmod{2^B}$ by the binomial theorem / lifting the exponent.
5. **Entropy measurement**: $I(\text{Set}_\text{next}; \text{Set}_\text{current}) \approx 0.03$ bits. TV distance $< 0.003$. Transition probabilities match natural densities within 1.3%.
6. **Implications**: Set transitions are 98.7% independent. Mixing quality by oddity parity: odd $s$ gives full mixing (100%), even $s$ gives reduced mixing ($50\%$ or less).
7. **Related**: Links to Bit Destruction, Logarithmic Escape.

- [ ] **Step 2: Verify and commit**

```bash
cd site && npm run dev
```

Check `/proofs/mixing`. Then:

```bash
git add site/proofs/mixing.md
git commit -m "feat: add 3-Adic Mixing theorem page"
```

---

### Task 7: Cycle Analysis Pages

**Files:**
- Create: `site/cycles/convergent-elimination.md`
- Create: `site/cycles/divisibility-obstruction.md`

Content source: `docs/plans/path-to-proof.md`, conversation results

- [ ] **Step 1: Write convergent elimination page**

Write `site/cycles/convergent-elimination.md`:

1. **The cycle equation**: From affine structure, a cycle visiting sets $k_1, \ldots, k_m$ requires $n = C_\text{total} \cdot 2^E / (2^E - 3^S)$ where $S = \sum s_i$, $E = \sum(k_i - s_i)$.
2. **Ascending elimination**: $C > 0$ always (sum of positive affine corrections). When $3^S > 2^E$, the denominator is negative, forcing $n < 0$. Theorem box + proof.
3. **Convergent table**: All convergents of $\log_2 3$ up to $(S, E) = (190537, 301994)$ with status: ascending = eliminated, descending = need checking.
4. **Gap=13 elimination**: For $(S=5, E=8)$: 91 valid parity words (circular binary strings, no adjacent 1s). Computed $C \cdot 2^8 \bmod 13$ for each. Distribution histogram over $\{1, \ldots, 12\}$ — zero never appears. Theorem: no 13-step cycle exists.
5. **The trivial cycle recovered**: $(S=1, E=2)$ with gap=1 produces $n = 1, 2, 4$ — the known 4→2→1 cycle.

- [ ] **Step 2: Write divisibility obstruction page**

Write `site/cycles/divisibility-obstruction.md`:

1. **The conjecture**: For gap $g = 2^E - 3^S > 1$, no valid parity word has $g \mid 2^E \cdot C$.
2. **Evidence**: Gap=13 verified exhaustively. Distribution of $C \bmod 13$ is roughly uniform over non-zero residues.
3. **Why it matters**: Would prove no non-trivial cycles exist (combined with ascending elimination).
4. **Structural hints**: $\text{ord}(3 \bmod 13) = 3$, $\text{ord}(2 \bmod 13) = 12$. The affine contributions are constrained to a restricted set of residues mod $g$.
5. **Next convergent**: $(S=41, E=65)$ has $\sim 10^{17}$ parity words — infeasible to enumerate, needs algebraic approach.

- [ ] **Step 3: Verify and commit**

```bash
cd site && npm run dev
```

Check both pages. Then:

```bash
git add site/cycles/
git commit -m "feat: add cycle analysis pages (convergent elimination, divisibility obstruction)"
```

---

### Task 8: Roadmap Page

**Files:**
- Create: `site/roadmap/path-to-proof.md`
- Create: `site/public/two-fronts.svg`

Content source: `docs/plans/path-to-proof.md`

- [ ] **Step 1: Create the two-fronts diagram SVG**

Create `site/public/two-fronts.svg` — a simple static diagram showing:
- "Collatz Conjecture" at top
- Two branches: "No Cycles (~70%)" and "No Divergence (~30%)"
- Under each: bullet list of proved results and remaining gaps
- Use clean black/white/brand-color styling, no external fonts

- [ ] **Step 2: Write the roadmap page**

Write `site/roadmap/path-to-proof.md`. Adapt the content from the Obsidian source, converting `[[wikilinks]]` to VitePress links. Include:

Include the diagram: `<img src="/two-fronts.svg" alt="Two fronts toward proving the Collatz conjecture" style="max-width: 600px; margin: 1rem auto; display: block;" />`

1. **Overview**: The conjecture reduces to no cycles + no divergence.
2. **Proved results summary**: Compact list of all 6 results with one-line statements and links to full proof pages.
3. **Front 1: No Cycles (~70%)**: What we have, what's missing, the key conjecture, next steps.
4. **Front 2: No Divergence (~30%)**: What we have, the gap, possible approaches.
5. **Connections table**: Our results mapped to classical mathematics.
6. **Open questions**: Numbered list of the 4 sharpest targets.

- [ ] **Step 2: Verify and commit**

```bash
cd site && npm run dev
```

Check `/roadmap/path-to-proof`. Then:

```bash
git add site/roadmap/
git commit -m "feat: add path-to-proof roadmap page"
```

---

### Task 9: Connections Pages

**Files:**
- Create: `site/connections/index.md`
- Create: `site/connections/abc-conjecture.md`

- [ ] **Step 1: Write connections landing page**

Write `site/connections/index.md`:

Brief overview of how this research connects to established mathematics. Links to:
- abc conjecture (detailed page)
- Mentions of: Roth's theorem, Baker's theorem, Pillai conjecture, S-unit equations, Terras's theorem, Weyl equidistribution. Each with a one-sentence description and which of our results it connects to.

- [ ] **Step 2: Write abc conjecture page**

Write `site/connections/abc-conjecture.md`:

1. **Statement of abc**: For coprime $a + b = c$, $c < K(\varepsilon) \cdot \text{rad}(abc)^{1+\varepsilon}$.
2. **The minimal radical**: $\text{rad}(2^a \cdot 3^b) = 6$ regardless of exponents. The Collatz map involves only primes 2 and 3 — the smallest possible radical.
3. **Application to cycles**: The cycle equation $3^S \cdot n + C = 2^E \cdot n$ involves terms with $\text{rad} = 6$. abc constrains how close $3^S$ and $2^E$ can be, bounding cycle length.
4. **Hierarchy of bounds**: Table comparing Trivial / Roth / Baker / Pillai / abc bounds on $\beta(s)$ and cycle constraints.
5. **S-unit equations**: The equation $|2^E - 3^S| = g$ is a solved problem (Evertse, 1984 — finitely many solutions for each $g$). Connection to our gap analysis.

- [ ] **Step 3: Verify and commit**

```bash
cd site && npm run dev
```

Check `/connections/` and `/connections/abc-conjecture`. Then:

```bash
git add site/connections/
git commit -m "feat: add connections pages (overview, abc conjecture)"
```

---

### Task 10: Create public dir + final build verification

**Files:**
- Create: `site/public/.gitkeep`

- [ ] **Step 1: Create public directory**

```bash
mkdir -p site/public
touch site/public/.gitkeep
```

- [ ] **Step 2: Run full build**

```bash
cd site && npm run build
```

Expected: Clean build with no errors. Output in `site/.vitepress/dist/`.

- [ ] **Step 3: Preview built site**

```bash
cd site && npm run preview
```

Navigate through all pages. Verify:
- All math renders (inline and display)
- Theorem/proof/corollary boxes display correctly
- Navigation and sidebar work
- All internal links resolve
- No console errors

- [ ] **Step 4: Final commit**

```bash
git add site/public/.gitkeep
git commit -m "feat: complete VitePress site v1 with all proof pages"
```
