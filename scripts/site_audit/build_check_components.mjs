// Build stage: every component under site/.vitepress/theme/components is parsed and compiled in
// memory, and any identifier its template reads that the script does not define is reported
// (the production build does not warn about those). Writes nothing; not a site build.
// Run:  node scripts/site_audit/build_check_components.mjs
import { readFileSync, readdirSync, statSync } from 'node:fs'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'
import { join, relative } from 'node:path'

const sitePath = fileURLToPath(new URL('../../site/', import.meta.url))
const require = createRequire(join(sitePath, 'package.json'))
const { parse, compileScript, compileTemplate } = require('@vue/compiler-sfc')

const root = join(sitePath, '.vitepress/theme/components')
const files = []
const walk = (d) => {
  for (const f of readdirSync(d)) {
    const p = join(d, f)
    if (statSync(p).isDirectory()) walk(p)
    else if (f.endsWith('.vue')) files.push(p)
  }
}
walk(root)

// which components are actually placed on a page
const mdFiles = []
const walkMd = (d) => {
  for (const f of readdirSync(d)) {
    if (f === 'node_modules' || f === '.vitepress') continue
    const p = join(d, f)
    if (statSync(p).isDirectory()) walkMd(p)
    else if (f.endsWith('.md')) mdFiles.push(p)
  }
}
walkMd(sitePath)
const allMd = mdFiles.map((f) => readFileSync(f, 'utf8')).join('\n')
const onAPage = (name) => new RegExp(`<${name}[\\s/>]`).test(allMd)

let bad = 0
let unusedNotes = 0
for (const filename of files.sort()) {
  const source = readFileSync(filename, 'utf8')
  const { descriptor, errors } = parse(source, { filename })
  const errs = [...errors]
  let bindings
  try {
    bindings = compileScript(descriptor, { id: 'x' }).bindings
  } catch (e) {
    errs.push(e)
  }
  let missing = []
  let dollars = []
  if (descriptor.template) {
    const tpl = compileTemplate({
      source: descriptor.template.content,
      filename,
      id: 'x',
      compilerOptions: { bindingMetadata: bindings }
    })
    errs.push(...tpl.errors)
    missing = [...new Set([...tpl.code.matchAll(/_ctx\.([A-Za-z_$][\w$]*)/g)].map((m) => m[1]))]
      .filter((n) => !n.startsWith('$'))
    // TeX left in a template is shown raw: components are not passed through markdown
    const text = descriptor.template.content.replace(/\{\{[\s\S]*?\}\}/g, '').replace(/="[^"]*"/g, '')
    dollars = [...text.matchAll(/\$[^$\n<]{1,60}\$/g)].map((m) => m[0])
  }
  const name = filename.replace(/^.*[\\/]/, '').replace(/\.vue$/, '')
  const used = onAPage(name)
  // raw TeX only matters where a reader can see it: an unplaced component is noted, not counted
  const visibleDollars = used ? dollars : []
  const tag = errs.length || missing.length || visibleDollars.length ? 'PROBLEM' : (used ? 'ok' : 'unused')
  console.log(`${tag.padEnd(8)} ${relative(root, filename)}`)
  for (const e of errs) console.log('    error:', e.message || e)
  if (missing.length) console.log('    unresolved template identifiers:', missing.join(', '))
  if (dollars.length) {
    console.log(`    raw TeX in template${used ? '' : ' (component is not placed on any page, so nothing shows)'}:`, dollars.join('  '))
    if (!used) unusedNotes++
  }
  bad += errs.length + missing.length + visibleDollars.length
}
console.log(bad
  ? `\n${bad} problem(s)`
  : `\nall ${files.length} components compile; no unresolved identifiers; no raw TeX on any page` +
    (unusedNotes ? ` (${unusedNotes} unplaced component with raw TeX, see above)` : ''))
process.exit(bad ? 1 : 0)
