// Parses every $...$ and $$...$$ span of the five 'structure-cycles' pages with KaTeX
// (throwOnError), and scans for the Vue-template hazards. Not a site build: reads only.
// Run: node structure_cycles_katex_check.mjs   (from scripts/site_audit/)
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const here = dirname(fileURLToPath(import.meta.url))
const site = resolve(here, '../../site')
const require = createRequire(resolve(site, 'package.json'))
const katex = require('katex')

const pages = [
  'proofs/affine-orbit.md',
  'proofs/bit-destruction.md',
  'proofs/mixing.md',
  'cycles/convergent-elimination.md',
  'cycles/divisibility-obstruction.md',
]
let bad = 0
for (const p of pages) {
  const src = readFileSync(resolve(site, p), 'utf8')
  let spans = 0
  const rest = src.replace(/\$\$([\s\S]+?)\$\$/g, (_, tex) => {
    spans++
    try { katex.renderToString(tex, { displayMode: true, throwOnError: true }) }
    catch (e) { bad++; console.log(`${p}: display math error: ${e.message}\n   ${tex}`) }
    return ' '
  })
  rest.replace(/\$([^$\n]+?)\$/g, (_, tex) => {
    spans++
    try { katex.renderToString(tex, { throwOnError: true }) }
    catch (e) { bad++; console.log(`${p}: inline math error: ${e.message}\n   ${tex}`) }
    return ' '
  })
  const dollars = (rest.match(/\$/g) || []).length
  if (dollars % 2) { bad++; console.log(`${p}: odd number of single dollar signs`) }
  src.split('\n').forEach((line, i) => {
    if (/\{\{|\}\}/.test(line)) { bad++; console.log(`${p}:${i + 1}: consecutive braces`) }
    const prose = line.replace(/\$[^$]*\$/g, ' ')
    if (/<[A-Za-z]/.test(prose) && !/^<\/?div/.test(line.trim())) { bad++; console.log(`${p}:${i + 1}: raw < before a letter`) }
    if (/^\|/.test(line)) {
      for (const m of line.matchAll(/\$([^$]*)\$/g)) {
        if (m[1].includes('|')) { bad++; console.log(`${p}:${i + 1}: literal | inside table math`) }
      }
    }
    for (const m of line.matchAll(/\]\(([^)]+)\)/g)) {
      if (/\.md(#|$)/.test(m[1])) { bad++; console.log(`${p}:${i + 1}: link with .md: ${m[1]}`) }
    }
  })
  console.log(`${p}: ${spans} math spans parsed`)
}
console.log(bad ? `PROBLEMS: ${bad}` : 'all clean')
