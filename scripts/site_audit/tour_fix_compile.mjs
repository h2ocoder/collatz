// Tour fixer: in-memory compile check, no site build and no files written.
//  1. each edited journey component is parsed and its template compiled with @vue/compiler-sfc
//  2. each journey page is rendered with VitePress's own markdown renderer (+ the KaTeX plugin from the
//     site config) and the resulting HTML is compiled as a Vue template, which is what VitePress does.
import { readFileSync, readdirSync } from 'node:fs'
import { createRequire } from 'node:module'
import { pathToFileURL, fileURLToPath } from 'node:url'
const siteUrl = new URL('../../site/', import.meta.url)
const sitePath = fileURLToPath(siteUrl)
const require = createRequire(new URL('package.json', siteUrl))
const sfc = require('@vue/compiler-sfc')
let bad = 0

const compDir = new URL('.vitepress/theme/components/journey/', siteUrl)
for (const name of ['Base6Circle', 'BinaryStepVisualizer', 'BounceSimulator', 'CountdownVisualizer', 'HailstoneChart', 'NaturalVs2Adic', 'PhysicsAnalogy', 'ProofMap']) {
  const source = readFileSync(new URL(name + '.vue', compDir), 'utf8')
  const { descriptor, errors } = sfc.parse(source, { filename: name + '.vue' })
  const errs = [...errors]
  try {
    const script = sfc.compileScript(descriptor, { id: name })
    const tpl = sfc.compileTemplate({ source: descriptor.template.content, filename: name + '.vue', id: name, compilerOptions: { bindingMetadata: script.bindings } })
    errs.push(...tpl.errors)
  } catch (e) { errs.push(e) }
  console.log(`${name}.vue: ${errs.length ? 'ERRORS ' + errs.map(e => e.message || e).join(' | ') : 'compiles'}`)
  bad += errs.length
}

const vp = await import(pathToFileURL(require.resolve('vitepress')).href)
const { katex } = await import(pathToFileURL(require.resolve('@mdit/plugin-katex')).href)
const md = await vp.createMarkdownRenderer(sitePath, { config: (m) => { m.use(katex, { mhchem: false }) } }, '/')
const dom = require('@vue/compiler-dom')
const pageDir = new URL('journey/', siteUrl)
for (const f of readdirSync(pageDir).filter(f => f.endsWith('.md'))) {
  const src = readFileSync(new URL(f, pageDir), 'utf8')
  const errs = []
  let html = ''
  try { html = md.render(src, { path: fileURLToPath(new URL(f, pageDir)), relativePath: 'journey/' + f, cleanUrls: false }) } catch (e) { errs.push(e) }
  try { dom.compile(`<div>${html}</div>`, { onError: (e) => errs.push(e) }) } catch (e) { errs.push(e) }
  const katexErr = (html.match(/katex-error/g) || []).length
  console.log(`${f}: ${html.length} chars of HTML; KaTeX errors ${katexErr}; ${errs.length ? 'TEMPLATE ERRORS ' + errs.map(e => e.message || e).join(' | ') : 'compiles as a Vue template'}`)
  bad += errs.length + katexErr
}
console.log(bad ? `\n${bad} problem(s)` : '\nall compile checks passed')
