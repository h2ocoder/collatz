// Tour audit: check that every quoted string in tour_findings.json occurs verbatim in its file.
import { readFileSync } from 'node:fs'
const root = new URL('../../', import.meta.url)
const items = JSON.parse(readFileSync(new URL('./tour_findings.json', import.meta.url), 'utf8'))
let bad = 0
for (const it of items) {
  const text = readFileSync(new URL(it.file, root), 'utf8').replace(/\r\n/g, '\n')
  const n = text.split(it.quote).length - 1
  if (n !== 1) { bad++; console.log(`[${n} matches] ${it.file}\n    ${it.quote.slice(0, 110)}`) }
}
console.log(`${items.length} quotes checked, ${bad} not matching exactly once`)
