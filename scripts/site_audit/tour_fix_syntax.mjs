// Tour fixer: cheap syntax checks on the edited files (no site build).
//  - the data arrays edited in ProofMap.vue and PhysicsAnalogy.vue still parse as JavaScript
//  - no markdown page in site/journey has two consecutive curly braces, or a raw "<" followed by a letter
//    outside the known HTML tags / component tags
//  - no literal "|" inside inline math within a table row
//  - every relative link in site/journey resolves to a page
import { readFileSync, existsSync, readdirSync } from 'node:fs'
const root = new URL('../../site/', import.meta.url)
const comp = (n) => readFileSync(new URL(`.vitepress/theme/components/journey/${n}.vue`, root), 'utf8')
let bad = 0
for (const [file, name] of [['ProofMap', 'nodes'], ['PhysicsAnalogy', 'rows']]) {
  const src = comp(file)
  const m = src.match(new RegExp(`const ${name} = (\\[[\\s\\S]*?\\n\\])`))
  if (!m) { console.log(`${file}: array ${name} not found`); bad++; continue }
  try { const arr = (0, eval)(m[1]); console.log(`${file}: ${name} parses, ${arr.length} entries`) } catch (e) { console.log(`${file}: PARSE ERROR ${e.message}`); bad++ }
}
// template sanity for the edited components: balanced interpolation braces, tags still paired
for (const file of ['Base6Circle', 'BinaryStepVisualizer', 'BounceSimulator', 'CountdownVisualizer', 'HailstoneChart', 'NaturalVs2Adic', 'PhysicsAnalogy', 'ProofMap']) {
  const src = comp(file)
  const tpl = src.slice(src.indexOf('<template>'), src.lastIndexOf('</template>') + '</template>'.length)
  const open = (tpl.match(/\{\{/g) || []).length, close = (tpl.match(/\}\}/g) || []).length
  const tags = {}
  for (const t of tpl.matchAll(/<(\/?)([a-zA-Z][a-zA-Z0-9-]*)([^>]*)>/g)) {
    if (t[3].trim().endsWith('/')) continue
    if (['br', 'input', 'canvas', 'line', 'circle'].includes(t[2]) && !t[1]) { if (!new RegExp(`</${t[2]}>`).test(tpl)) continue }
    tags[t[2]] = (tags[t[2]] || 0) + (t[1] ? -1 : 1)
  }
  const unbalanced = Object.entries(tags).filter(([, v]) => v !== 0)
  console.log(`${file}: interpolations ${open}/${close}${open !== close ? ' MISMATCH' : ''}; unbalanced tags: ${unbalanced.length ? JSON.stringify(unbalanced) : 'none'}`)
  if (open !== close || unbalanced.length) bad++
}
const dir = new URL('journey/', root)
for (const f of readdirSync(dir).filter(f => f.endsWith('.md'))) {
  const text = readFileSync(new URL(f, dir), 'utf8').replace(/\r\n/g, '\n')
  const issues = []
  if (/\{\{|\}\}/.test(text)) issues.push('double curly brace')
  text.split('\n').forEach((line, i) => {
    const stripped = line.replace(/<\/?(div|a|br|span|em|strong|sub|sup)\b[^>]*>/g, '').replace(/<[A-Z][A-Za-z0-9]* \/>/g, '')
    if (/<[A-Za-z]/.test(stripped)) issues.push(`line ${i + 1}: "<" followed by a letter`)
    if (line.startsWith('|')) for (const m of line.matchAll(/\$[^$]*\$/g)) if (m[0].includes('|')) issues.push(`line ${i + 1}: "|" inside math in a table`)
    for (const m of line.matchAll(/\]\((\.{1,2}\/[^)#]+|\/[^)#]+)(#[^)]*)?\)/g)) {
      const target = m[1].startsWith('/') ? new URL('.' + m[1], root) : new URL(m[1], dir)
      if (m[1].startsWith('/data/')) { if (!existsSync(new URL('public' + m[1], root))) issues.push(`line ${i + 1}: missing asset ${m[1]}`); continue }
      if (!existsSync(new URL(target.href + '.md')) && !existsSync(new URL(target.href.replace(/\/?$/, '/index.md')))) issues.push(`line ${i + 1}: dead link ${m[1]}`)
    }
    for (const m of line.matchAll(/href="(\.\/[^"]+|\/[^"]*)"/g)) {
      if (m[1] === '/') continue
      const target = m[1].startsWith('/') ? new URL('.' + m[1], root) : new URL(m[1], dir)
      if (!existsSync(new URL(target.href + '.md'))) issues.push(`line ${i + 1}: dead href ${m[1]}`)
    }
  })
  const comps = [...text.matchAll(/<([A-Z][A-Za-z0-9]*) \/>/g)].map(m => m[1])
  for (const c of comps) if (!existsSync(new URL(`.vitepress/theme/components/journey/${c}.vue`, root))) issues.push(`unknown component ${c}`)
  console.log(`${f}: components [${comps.join(', ')}] ${issues.length ? 'ISSUES: ' + issues.join('; ') : 'ok'}`)
  bad += issues.length
}
console.log(bad ? `\n${bad} problem(s)` : '\nall checks passed')
