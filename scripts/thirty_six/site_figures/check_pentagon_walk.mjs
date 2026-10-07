// Check of the arithmetic behind the PentagonWalk component on the site page
// site/explore/folded-pentagon.md.
//
// It imports the very functions the component uses
// (site/.vitepress/theme/utils/pentagon.ts) and compares them with an independent
// reference written here: BigInt arithmetic, a window of 5 * 2^k consecutive
// integers that contains negatives, and the closed-form pentagon law.
// Reference values are those of scripts/thirty_six/golden_kernel/README.md
// (Theorem A, corollary) and its logs.
//
// Run from anywhere (Node 22.18+ or 23.6+, which strip TypeScript types on import):
//     node scripts/thirty_six/site_figures/check_pentagon_walk.mjs

import {
  HALF_PHI,
  MAX_STEPS,
  distanceFromUniform,
  lucas,
  pentagonOrder,
  residueCounts,
  returnCount,
  walkCounts,
} from '../../../site/.vitepress/theme/utils/pentagon.ts'

let failures = 0
function check(ok, label) {
  if (!ok) failures++
  console.log(`   [${ok ? 'ok' : 'FAIL'}] ${label}`)
}
const same = (a, b) => a.length === b.length && a.every((x, i) => x === b[i])

// ---------------------------------------------------------------- independent reference
const mod5 = (x) => Number(((x % 5n) + 5n) % 5n)

/** Counts of T^k(n) mod 5 over the n = start (mod 5) in a window of 5 * 2^k consecutive integers. */
function referenceCounts(k, start, sign, windowStart) {
  const counts = [0, 0, 0, 0, 0]
  const len = 5n * 2n ** BigInt(k)
  for (let n0 = windowStart; n0 < windowStart + len; n0++) {
    if (mod5(n0) !== start) continue
    let n = n0
    for (let i = 0; i < k; i++) n = n % 2n === 0n ? n / 2n : (3n * n + BigInt(sign)) / 2n
    counts[mod5(n)]++
  }
  return counts
}

/** Pentagon-walk law in closed form (eigenvalues cos 72 and cos 144), times 2^k, rounded. */
function closedFormWalk(k) {
  const c1 = Math.cos((2 * Math.PI) / 5)
  const c2 = Math.cos((4 * Math.PI) / 5)
  return [0, 1, 2, 3, 4].map((j) =>
    Math.round(2 ** k * (0.2 + 0.4 * (c1 ** k * Math.cos((2 * Math.PI * j) / 5) + c2 ** k * Math.cos((4 * Math.PI * j) / 5)))),
  )
}

/** The component's comparison: walk counts re-indexed by residue, walk started at the vertex of `start`. */
function walkByResidue(k, start, sign) {
  const order = pentagonOrder(sign)
  const w = walkCounts(k, order.indexOf(start))
  const out = [0, 0, 0, 0, 0]
  order.forEach((r, v) => (out[r] = w[v]))
  return out
}

// ---------------------------------------------------------------- 1. the corollary, start 1
console.log('=== 1. 3x+1, start n = 1 (mod 5): counts of T^k(n) mod 5 by residue 0..4 ===')
const README = {
  0: [0, 1, 0, 0, 0],
  1: [0, 0, 1, 1, 0],
  2: [1, 2, 0, 0, 1],
  8: [57, 70, 36, 36, 57],
  16: [13380, 13990, 12393, 12393, 13380],
}
let allAgree = true
let allRef = true
for (let k = 0; k <= MAX_STEPS; k++) {
  const c = residueCounts(k, 1, 1)
  const w = walkByResidue(k, 1, 1)
  const ref = k <= 13 ? referenceCounts(k, 1, 1, -(5n * 2n ** BigInt(k)) / 2n) : null
  allAgree &&= same(c, w)
  if (ref) allRef &&= same(c, ref)
  if (k <= 10 || k === 16) {
    console.log(`   k = ${String(k).padStart(2)}: Collatz ${JSON.stringify(c)}   pentagon walk ${JSON.stringify(w)}   ${same(c, w) ? 'equal' : 'DIFFERENT'}`)
  }
  if (README[k]) check(same(c, README[k]), `k = ${k} matches the README value ${JSON.stringify(README[k])}`)
}
check(allAgree, `k = 0..${MAX_STEPS}: Collatz counts = pentagon-walk counts at every vertex`)
check(allRef, 'k = 0..13: component counts = BigInt reference on a window containing negatives')
check([...Array(MAX_STEPS + 1).keys()].every((k) => same(walkCounts(k, 0), closedFormWalk(k))), `k = 0..${MAX_STEPS}: stepped walk = closed-form pentagon law`)

// ---------------------------------------------------------------- 2. Lucas formula, OEIS A054877
console.log('=== 2. returns to the apex: (2^k + 2(-1)^k L_k)/5, OEIS A054877 ===')
const A054877 = [1, 0, 2, 0, 6, 2, 20, 14, 70]
const returns = [...Array(MAX_STEPS + 1).keys()].map((k) => residueCounts(k, 1, 1)[1])
console.log(`   returns, k = 0..${MAX_STEPS}: ${returns.join(', ')}`)
console.log(`   Lucas numbers L_0..L_10: ${[...Array(11).keys()].map(lucas).join(', ')}`)
check(same(returns.slice(0, A054877.length), A054877), 'first terms are 1, 0, 2, 0, 6, 2, 20, 14, 70')
check(returns.every((r, k) => r === returnCount(k)), `Lucas formula gives the return count for k = 0..${MAX_STEPS}`)

// ---------------------------------------------------------------- 3. the mirror 3x-1
console.log('=== 3. 3x-1: apex 4, neighbours 2 and 3, far pair 0 and 1 ===')
console.log(`   pentagon order for 3x-1: ${pentagonOrder(-1).join('-')}`)
let mirrorOk = true
let mirrorRef = true
for (let k = 0; k <= MAX_STEPS; k++) {
  const c = residueCounts(k, 4, -1)
  mirrorOk &&= same(c, walkByResidue(k, 4, -1))
  if (k <= 12) mirrorRef &&= same(c, referenceCounts(k, 4, -1, -(5n * 2n ** BigInt(k)) / 2n))
  // the 3x-1 counts are the 3x+1 counts with residues negated
  mirrorOk &&= same(c, [0, 1, 2, 3, 4].map((r) => residueCounts(k, 1, 1)[(5 - r) % 5]))
}
console.log(`   k = 8: ${JSON.stringify(residueCounts(8, 4, -1))}`)
check(mirrorOk, `k = 0..${MAX_STEPS}: start 4 gives the pentagon law, and equals the 3x+1 law with residues negated`)
check(mirrorRef, 'k = 0..12: agrees with the BigInt reference')

// ---------------------------------------------------------------- 4. the other starts
console.log('=== 4. starts other than the apex ===')
function permutations(xs) {
  if (xs.length <= 1) return [xs]
  return xs.flatMap((x, i) => permutations([...xs.slice(0, i), ...xs.slice(i + 1)]).map((p) => [x, ...p]))
}
const PERMS = permutations([0, 1, 2, 3, 4])
for (const sign of [1, -1]) {
  const apex = pentagonOrder(sign)[0]
  for (const start of [0, 1, 2, 3, 4]) {
    if (start === apex) continue
    const laws = [...Array(MAX_STEPS + 1).keys()].map((k) => residueCounts(k, start, sign))
    const differs = laws.map((c, k) => !same(c, walkByResidue(k, start, sign)))
    // is there ANY placement of the residues on the pentagon giving a pentagon law for all k?
    const someLabelling = PERMS.some((p) => laws.every((c, k) => same(c, [0, 1, 2, 3, 4].map((r) => walkCounts(k, p[start])[p[r]]))))
    console.log(`   3x${sign === 1 ? '+' : '-'}1, start ${start}: k = 1 Collatz ${JSON.stringify(laws[1])}  walk ${JSON.stringify(walkByResidue(1, start, sign))}`)
    check(!differs[0] && differs.slice(1).every(Boolean), `start ${start}: equal at k = 0 only, different for every k = 1..${MAX_STEPS}`)
    check(!someLabelling, `start ${start}: no relabelling of the residues gives a pentagon law (k = 0..${MAX_STEPS}, 120 labellings)`)
  }
}
check(same(residueCounts(1, 2, 1), [0, 2, 0, 0, 0]), 'README: from n = 2 (mod 5) every integer lands on residue 1 after one step')

// ---------------------------------------------------------------- 5. distance from uniform
console.log('=== 5. total variation distance from uniform against (phi/2)^k, start 1 ===')
check(Math.abs(HALF_PHI - Math.cos(Math.PI / 5)) < 1e-15, `phi/2 = cos 36 degrees = ${HALF_PHI.toFixed(6)}`)
for (let k = 0; k <= MAX_STEPS; k += 2) {
  const d = distanceFromUniform(residueCounts(k, 1, 1))
  console.log(`   k = ${String(k).padStart(2)}: distance ${d.toFixed(6)}   (phi/2)^k ${(HALF_PHI ** k).toFixed(6)}   ratio ${(d / HALF_PHI ** k).toFixed(4)}`)
}
const ratios = [0, 1, 2, 3, 4].map((s) => distanceFromUniform(residueCounts(16, s, 1)) / HALF_PHI ** 16)
console.log(`   ratio at k = 16 for starts 0..4: ${ratios.map((r) => r.toFixed(4)).join(', ')}`)

// ---------------------------------------------------------------- 6. size of the numbers
let big = 0
for (let j = 0; j < 2 ** MAX_STEPS; j++) {
  let n = 4 + 5 * j
  for (let i = 0; i < MAX_STEPS; i++) {
    n = n % 2 === 0 ? n / 2 : (3 * n + 1) / 2
    if (n > big) big = n
  }
}
check(3 * big + 1 < Number.MAX_SAFE_INTEGER, `largest value met at k = ${MAX_STEPS} is ${big} (far below 2^53)`)

console.log(`\n${failures} failures`)
process.exit(failures ? 1 : 0)
