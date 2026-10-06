// Reviewer check: dump what the PentagonWalk component's own functions return, for every control setting.
// Read by fp_math_04_component.py, which compares the dump with an independent Python implementation.
//
// Run:  node scripts/thirty_six/site_checks/fp_component_dump.mjs   (Node 22.18+ strips the TypeScript types)
import { writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import {
  HALF_PHI,
  MAX_STEPS,
  ROLES,
  distanceFromUniform,
  lucas,
  pentagonOrder,
  residueCounts,
  returnCount,
  walkCounts,
} from '../../../site/.vitepress/theme/utils/pentagon.ts'

const rows = []
for (const sign of [1, -1]) {
  const order = pentagonOrder(sign)
  for (let start = 0; start < 5; start++) {
    for (let k = 0; k <= MAX_STEPS; k++) {
      // exactly the component's computed values
      const startVertex = order.indexOf(start)
      const collatz = residueCounts(k, start, sign)
      const walk = walkCounts(k, startVertex)
      const mismatches = order.filter((residue, v) => collatz[residue] !== walk[v]).length
      const isApex = startVertex === 0
      const verdict = mismatches > 0 ? 'different' : isApex ? 'same' : 'unmoved'
      const total = 2 ** k
      const firstN = start === 0 ? 5 : start
      rows.push({
        sign, start, k, order, startVertex, collatz, walk, mismatches, verdict,
        firstN, lastN: firstN + 5 * (total - 1),
        distance: distanceFromUniform(collatz), rate: HALF_PHI ** k,
        lucas: lucas(k), returnCount: returnCount(k), lucasSign: k % 2 === 0 ? '+' : '-',
      })
    }
  }
}
const out = fileURLToPath(new URL('./fp_component_dump.json', import.meta.url))
writeFileSync(out, JSON.stringify({ MAX_STEPS, ROLES, HALF_PHI, rows }))
console.log(`wrote ${rows.length} rows to ${out}`)
