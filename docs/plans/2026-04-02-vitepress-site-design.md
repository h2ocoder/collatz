# VitePress Site Design

**Date:** 2026-04-02
**Status:** Approved

## Purpose

A public-facing website presenting the Collatz conjecture research: proved results with full LaTeX-rendered proofs, the path-to-proof roadmap, and connections to classical mathematics. Aimed at mathematicians for feedback. Architecture supports future interactive widgets (phase B).

## Bootstrap

Requires Node 18+.

```bash
cd site
npm init -y
npm add -D vitepress @mdit/plugin-katex katex
```

`package.json` scripts:
```json
{
  "scripts": {
    "dev": "vitepress dev",
    "build": "vitepress build",
    "preview": "vitepress preview"
  }
}
```

## Architecture

- **Location:** `site/` at project root (separate from `docs/` Obsidian vault and `collatz/` Python package)
- **Framework:** VitePress 1.x
- **Math rendering:** KaTeX via `@mdit/plugin-katex` (actively maintained, ESM-compatible with VitePress 1.x). KaTeX CSS imported in `.vitepress/theme/index.ts`.
- **No other dependencies for v1**

## Directory Structure

```
site/
├── package.json             # Node dependencies and dev/build scripts
├── .vitepress/
│   ├── config.mts           # VitePress config (nav, sidebar, KaTeX plugin)
│   └── theme/
│       └── index.ts         # Custom theme entry: imports KaTeX CSS
├── index.md                 # Home page (hero + overview)
├── foundations/
│   ├── definitions.md       # Collatz step, orbit, dropping time, Syracuse map
│   └── terminology.md       # Paper 1 vs Paper 2 correspondence table
├── proofs/
│   ├── affine-orbit.md      # Affine Orbit Structure (full induction proof)
│   ├── logarithmic-escape.md # Logarithmic Escape Theorem
│   ├── bit-destruction.md   # Bit Destruction Bound + Roth connection
│   └── mixing.md            # 3-Adic Mixing theorem
├── cycles/
│   ├── convergent-elimination.md  # Ascending + gap=13 elimination
│   └── divisibility-obstruction.md # The conjecture + evidence
├── roadmap/
│   └── path-to-proof.md     # Two fronts, progress, open questions
├── connections/
│   ├── index.md             # Overview of connections to classical math
│   └── abc-conjecture.md    # The minimal radical case
└── public/
    └── (static assets if needed)
```

## Page Content Plan

### Home (`index.md`)
- Hero: title, one-line summary, "what's new" callout
- Brief overview of the three research papers
- Quick links to key results

### Foundations
- **Definitions:** Collatz step $f(n)$, orbit, dropping time, dropping destination, dropping set, orbital oddity, Syracuse map, alpha sequence. Each with formal definition + example.
- **Terminology Map:** Table mapping Paper 1 ↔ Paper 2 terms (from CLAUDE.md).

### Proved Results (the core of the site)
Each page follows the structure:
1. Statement (boxed theorem)
2. Significance (why it matters, 2-3 sentences)
3. Examples (concrete numbers)
4. Proof (full, with LaTeX)
5. Corollaries
6. Related results (links)

**Affine Orbit Structure:**
- Theorem: $\text{dest}(n) = \frac{3^s}{2^{k-s}} \cdot n + C$
- Induction proof (base case, even step, odd step)
- Table of slopes by Set$_k$
- Corollaries: orbital oddity, affine orbit sums, period $= 2^{k-s}$
- *Proof source: proved in conversation 2026-04-02; written up in `docs/Conjectures/Affine Orbit Structure.md`*

**Logarithmic Escape:**
- Theorem: self-chains bounded by $\log_P(n)$
- Modular tightening proof
- Verified table (Set$_3$ chains)
- *Proof source: proved in conversation 2026-04-02; written up in `docs/Conjectures/Logarithmic Escape Theorem.md`*

**Bit Destruction Bound:**
- Identity: $\beta(s) = 1 - \{s \cdot \log_2 3\}$
- Connection to convergents of $\log_2 3$
- Roth's theorem application: $\beta > c/s$
- Conditional convergence: $O(\log^2 n)$ drops
- Table of slow sets
- *Proof source: proved in conversation 2026-04-02; written up in `docs/Conjectures/Bit Destruction Bound.md`*

**3-Adic Mixing:**
- $\text{ord}(3 \bmod 2^B) = 2^{B-2}$
- Entropy measurement: $I \approx 0.03$ bits
- Implications for orbit randomness
- *Proof source: ord result is classical number theory; entropy measurement from conversation 2026-04-02; documented in `docs/Conjectures/Bit Destruction Bound.md`*

### Cycle Analysis
**Convergent Elimination:**
- Ascending convergents: sign argument (C > 0, ratio > 1 → n < 0)
- Gap=13 computation: all 91 parity words, distribution of $C \bmod 13$
- Table of convergent status

**Divisibility Obstruction:**
- The conjecture: $g \nmid 2^E \cdot C$ for gap $g > 1$
- Evidence from gap=13
- Why this would prove no non-trivial cycles

### Path to Proof
- Two fronts diagram as a static SVG in `public/` (no Mermaid dependency)
- Progress percentages
- Open questions as clear targets
- *Content source: `docs/plans/path-to-proof.md`*

### Connections
- abc conjecture: $\text{rad}(2^a \cdot 3^b) = 6$
- S-unit equations
- Hierarchy of bounds table

## VitePress Configuration

### Navigation
Top nav: Home | Foundations | Proofs | Cycles | Roadmap | Connections

### Sidebar
Grouped by section with all pages listed.

### Theme
Default VitePress theme. Minor customization:
- Custom CSS for theorem boxes (bordered callouts)
- Proof QED markers

### KaTeX Setup
- `@mdit/plugin-katex` registered in `config.mts` via `markdown.config` hook
- KaTeX CSS imported in `.vitepress/theme/index.ts`: `import 'katex/dist/katex.min.css'`
- Supports inline `$...$` and display `$$...$$`

## Future-Ready (Phase B)

- Vue components can be embedded in any Markdown page via `<ComponentName />`
- Interactive widgets planned: orbit explorer, binary trie visualizer, affine map calculator, cycle pattern checker
- Python computation results exportable as JSON for client-side use

## What's NOT in v1

- No interactive widgets
- No CI/CD or deploy pipeline
- No custom theme beyond theorem box CSS
- No search (VitePress built-in is fine for now)
