# Site rewrite: from "proof journey" to honest field notes

Date: 2026-09-19 · Source: read-only audit of `site/` (28 pages, ~20,100 words) plus the shape-of-proof audit.

## Goal

whycollatzworks.com becomes a jumping-off place for four kinds of visitor, and every page says which kind of page it is: **known mathematics**, **proved here**, **verified by computation**, **conjecture / heuristic**, **exploration / analogy**, **retracted**. No proof is claimed anywhere. The playgrounds stay front and centre.

## Personas and their paths

| Persona | Path from the home page |
|---|---|
| Curious layperson | Tour ch. 1–2 → playgrounds → "why is this hard?" → mirror-map playground |
| Maths student | How to read → Known mathematics in order → Fibonacci age law (a complete short proof) → retractions as exercises in finding the gap |
| Number theorist | How to read (one page, the whole claim) → Results → code and PDF |
| Fellow Collatz hobbyist | Retractions → the "must fail for −1" barrier → explorations → GitHub |

## What the audit found (all verified against the files)

1. Metadata and navigation said "an interactive proof"; pages stated "Theorem: every orbit converges" and "Front 1: Complete".
2. No-cycles: a heuristic expected-count argument presented as rigorous, on the false premise that a cycle's (S, E) must be a convergent of log₂3.
3. **Logarithmic Escape is false.** 294583 makes six consecutive Set₈ drops; the bound allows 2.63. The proof assumes one residue subgroup; the chain alternates 23, 11 mod 32. (Re-verified 2026-09-19.)
4. Roth's theorem misapplied in seven places (log₂3 is transcendental).
5. "Bit destruction β > 0" is a restatement of "a drop is a decrease".
6. Finite Propagation cited as proved; no page proves it; an average is applied to every n.
7. No prior art cited: Terras 1976, Everett 1977, OEIS A100982 and A122437, Steiner, Simons–de Weger, Eliahou, Hercher, Shakibaei Asli.
8. Nothing from `research/investigate-pinball-analogy/` is on the site.

## Work items

Done on 2026-09-19 (branch `feature/SCRUM-30_InvestigatePinballAnalogy`, not deployed):

- [x] **1. Metadata and nav labels** — `site/.vitepress/config.mts`: description, og tags, "Proof Journey" → "The Tour", "Proved Results" → "Structure (mostly known mathematics)", roadmap → Archive, new "Start Here".
- [x] **2. Home page reframed** — `site/index.md`: hero, tagline, six cards, status box, "What this site is", "Where to start" by persona.
- [x] **3a. `site/about/how-to-read.md`** — claims policy, label legend, the list of errors with the counterexample, the −1 test, what is worth reading.
- [x] **3b. Warning banners** on the eleven pages that overclaim or lack attribution (marker `<!-- audit-banner -->`). A stopgap until each page is rewritten.
- [x] Site builds (`npx vitepress build`).

To do, in order:

- [ ] **4. Rewrite the cycles material (M)** — `journey/no-loops.md`, `cycles/convergent-elimination.md`, `journey/the-picture.md`: remove "Theorem"/"Complete"; explain the cycle equation and what Steiner, Simons–de Weger, Eliahou, Hercher actually prove; keep CycleHunter and ConvergentNavigator as demos.
- [ ] **5. Demote Finite Fuel and The Complete Picture (M)** — turn `ProofMap.vue` into a *status map* coloured by label; fix the dangling "Finite Propagation Theorem" links in `connections/eisenstein.md`, `connections/universal-dynamics.md`, `journey/the-countdown.md`.
- [ ] **6. Fix the Roth error in the text (S)** — `binary-engine.md`, `the-rotation.md`, `bit-destruction.md`, `abc-conjecture.md`, `connections/index.md`, `path-to-proof.md`. State the Baker–Rhin bound instead.
- [ ] **7. Badge system (M)** — `StatusBadge.vue`, `status:` frontmatter on every page, rendered through a layout slot in `theme/index.ts`. Then remove the stopgap banners page by page.
- [ ] **8. Author page (S, needs Darcy)** — `site/about/author.md`: background, how long, why. Fix the wording in `publications.md`.
- [ ] **9. Prior-art citations (S/M)** — definitions, affine-orbit, sturmian-bridge, sturmian-l-probe, binary-shortcut ("the discovery" is classical).
- [ ] **10. Soften the Connections pages (M)** — hilbert-polya ("reduces to 4 > 3"), universal-dynamics ("why 3x+1 converges"), eisenstein ("unifies three proof strategies"), sturmian-l-probe ("every claim is proven").
- [ ] **11. New page: the mirror map and the Fibonacci age law (M)** — from the LaTeX note; link the PDF; embed the walk-back playground.
- [ ] **12. New page: the 2⁶⁰ verification and the Banerji dual (S/M)** — with the tree-search explainer.
- [ ] **13. New page: nesting, the never-drain fractal, the −1 barrier, the exchange-family transition (M)** — reuse `NaturalVs2Adic.vue`.
- [ ] **14. Mirror-map playground as a Vue component (L)** — port the two published explainer pages into `theme/components/`.
- [ ] **15. Archive section (M)** — move Logarithmic Escape, the old roadmap, and one paragraph each on the adelic-IFS and Denjoy-bridge claims: what was claimed, why it fails, the lesson.
- [ ] **16. Restructure the sidebar** to: Start Here · Play · Known Mathematics · Results From This Project · Explorations · Archive · References.

## Deployment note

`.github/workflows/deploy.yml` deploys on push to `main`. Nothing here is live until this branch is merged. Items 1–3 are a small, safe first merge and remove the most misleading statements from the public site.
