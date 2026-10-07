// Fixer's syntax check for the 'explore' section (no site build):
//  1. SturmianBridge.vue parses and its template compiles with @vue/compiler-sfc;
//  2. every $...$ / $$...$$ in the six explore pages renders with KaTeX;
//  3. the prose outside math and code has no double braces and no "<letter" other than known tags.
// Run from the site directory:  node ../scripts/site_audit/explore_fix_compile_check.mjs
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import path from 'node:path'

const site = process.cwd()
const require = createRequire(path.join(site, 'package.json'))
const sfc = require('@vue/compiler-sfc')

const file = path.join(site, '.vitepress/theme/components/SturmianBridge.vue')
const src = readFileSync(file, 'utf8')
const { descriptor, errors } = sfc.parse(src, { filename: file })
console.log('SFC parse errors:', errors.length)
const script = sfc.compileScript(descriptor, { id: 'x' })
const tpl = sfc.compileTemplate({
  source: descriptor.template.content,
  filename: file,
  id: 'x',
  compilerOptions: { bindingMetadata: script.bindings },
})
console.log('template errors:', tpl.errors.length, tpl.errors.map(e => String(e.message || e)).slice(0, 3))
console.log('template tips:', tpl.tips.length)

let katex
try {
  katex = require('katex')
} catch {
  const r2 = createRequire(require.resolve('@mdit/plugin-katex'))
  katex = r2('katex')
}
const pages = ['log6-wobble', 'dropping-dictionary', 'sturmian-bridge', 'sturmian-fractals', 'alpha-sequence', 'binary-shortcut']
for (const p of pages) {
  const text = readFileSync(path.join(site, 'explore', p + '.md'), 'utf8')
  let bad = 0
  let n = 0
  // strip fenced/inline code first
  const noCode = text.replace(/```[\s\S]*?```/g, '').replace(/`[^`\n]*`/g, '')
  const re = /\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$/g
  let m
  while ((m = re.exec(noCode))) {
    n++
    // inside a table row an escaped bar \| reaches KaTeX as |
    const tex = (m[1] ?? m[2]).replace(/\\\|/g, '|')
    try {
      katex.renderToString(tex, { displayMode: m[1] !== undefined, throwOnError: true, strict: false })
    } catch (e) {
      bad++
      console.log(`  ${p}: KaTeX error in "${tex.slice(0, 60)}": ${String(e.message).slice(0, 90)}`)
    }
  }
  const prose = noCode.replace(re, '')
  const tags = (prose.match(/<[A-Za-z][^\s>/]*/g) || []).filter(t => !['<SturmianBridge', '<SturmianFractal', '<AlphaExplorer', '<BinaryShortcut', '<div'].includes(t))
  console.log(`${p}: ${n} formulas, ${bad} KaTeX errors; double braces in prose: ${/\{\{|\}\}/.test(prose)}; stray "<letter": ${JSON.stringify(tags)}`)
}
