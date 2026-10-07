// Compile-only syntax check of the four components the connections pages embed.
// Reads the .vue files and compiles script + template in memory. Writes nothing; not a site build.
// Run from site/:  node ../scripts/site_audit/conn_fixer_sfc_check.mjs
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { resolve } from 'node:path'

const require = createRequire(resolve(process.cwd(), 'package.json'))
const { parse, compileScript, compileTemplate } = require('@vue/compiler-sfc')

const dir = resolve(process.cwd(), '.vitepress/theme/components/journey')
let bad = 0
for (const name of ['AlphaPositionChart.vue', 'EisensteinWalk.vue', 'SpectrumVisualizer.vue', 'ZooExplorer.vue']) {
  const filename = resolve(dir, name)
  const source = readFileSync(filename, 'utf8')
  const { descriptor, errors } = parse(source, { filename })
  const errs = [...errors]
  let bindings
  try {
    const script = compileScript(descriptor, { id: name })
    bindings = script.bindings
  } catch (e) {
    errs.push(e)
  }
  const tpl = compileTemplate({
    source: descriptor.template.content,
    filename,
    id: name,
    compilerOptions: { bindingMetadata: bindings }
  })
  errs.push(...tpl.errors)
  // identifiers the template reads that the script does not define
  const used = new Set()
  for (const m of tpl.code.matchAll(/\$setup\.([A-Za-z_$][\w$]*)/g)) used.add(m[1])
  const missing = [...(tpl.code.matchAll(/_ctx\.([A-Za-z_$][\w$]*)/g))].map(m => m[1])
  console.log(name, errs.length ? 'ERRORS' : 'ok',
    '| template bindings:', [...used].sort().join(', ') || '(none inline)',
    missing.length ? '| UNRESOLVED (_ctx): ' + [...new Set(missing)].join(', ') : '')
  for (const e of errs) { bad++; console.log('   ', e.message || e) }
  if (missing.length) bad++
}
process.exit(bad ? 1 : 0)
