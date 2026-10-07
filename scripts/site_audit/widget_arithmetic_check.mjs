// Checks the widgets' shared arithmetic after the 32-bit operators were removed.
// Run with Node 22.18+ (it imports a .ts file):  node scripts/site_audit/widget_arithmetic_check.mjs
import { collatzStep, orbit, syracuseStep, v2, trailingOnes, stoppingTime } from '../../site/.vitepress/theme/utils/collatz.ts'

let failures = 0
const check = (ok, msg) => { if (!ok) { failures++; console.log('FAIL', msg) } }

// 1. Against BigInt: every start up to 300,000 and the classic path records beyond.
function bigOrbit(n) {
  let x = BigInt(n); const seq = [x]
  while (x !== 1n) { x = x % 2n === 0n ? x / 2n : 3n * x + 1n; seq.push(x) }
  return seq
}
const records = [113383, 138367, 159487, 270271, 665215, 704511, 1042431, 1212415, 1441407, 1875711,
  1988859, 2643183, 2684647, 3041127, 3873535, 4637979, 5656191, 6416623, 6631675, 19638399,
  38595583, 80049391, 120080895, 210964383]
const starts = []
for (let n = 1; n <= 300000; n++) starts.push(n)
starts.push(...records, 999999, 1227079, 319804830)
let compared = 0
for (const n of starts) {
  const a = orbit(n, 100000), b = bigOrbit(n)
  let same = a.length === b.length
  for (let i = 0; same && i < a.length; i++) same = BigInt(a[i]) === b[i]
  check(same, 'orbit differs from BigInt at start ' + n)
  compared++
}
console.log('1. orbit() equals the BigInt orbit for', compared, 'starts (all n <= 300,000 and', records.length, 'path records up to 210,964,383)')
console.log('   113383: length', orbit(113383).length, 'max', Math.max(...orbit(113383)), '(reaches 1:', orbit(113383).at(-1) === 1, ')')

// 2. Small helpers against definitions, including values above 2^31.
for (const n of [1, 2, 3, 12, 2 ** 31, 2 ** 31 + 2, 3 * 2 ** 40, 2 ** 52]) {
  let c = 0, x = BigInt(n); while (x % 2n === 0n) { x /= 2n; c++ }
  check(v2(n) === c, 'v2 ' + n)
}
for (const n of [1, 3, 7, 2 ** 33 - 1, 2 ** 40 + 7]) {
  let c = 0, x = BigInt(n); while (x % 2n === 1n) { x = (x - 1n) / 2n; c++ }
  check(trailingOnes(n) === c, 'trailingOnes ' + n)
}
for (const m of [1, 3, 27, 2 ** 33 + 1, 2643183]) {
  let x = 3n * BigInt(m) + 1n; while (x % 2n === 0n) x /= 2n
  check(BigInt(syracuseStep(m)) === x, 'syracuseStep ' + m)
}
check(collatzStep(2 ** 40) === 2 ** 39 && collatzStep(2 ** 40 + 1) === 3 * (2 ** 40 + 1) + 1, 'collatzStep above 2^31')
check(stoppingTime(27) === 96 && stoppingTime(3) === 6, 'stoppingTime')
console.log('2. v2, trailingOnes, syracuseStep, collatzStep, stoppingTime agree with their definitions above 2^31')

// 3. Where does exactness end?  Plain numbers are exact while 3n + 1 <= 2^53 - 1.
//    Induction: if n falls below itself with every value in range, and every smaller start is in range, so is n.
const LIMIT = (Number.MAX_SAFE_INTEGER - 1) / 3   // odd values must stay at or below this
let first = null
const t0 = process.hrtime.bigint()
for (let n = 3; n < 330000000 && first === null; n += 2) {     // even starts fall at once
  let x = n
  while (x >= n) {
    if (x % 2 !== 0) { if (x > LIMIT) { first = n; break } x = 3 * x + 1 } else x /= 2
  }
}
const secs = Number(process.hrtime.bigint() - t0) / 1e9
console.log('3. first start whose orbit leaves the exact range (some odd value above (2^53 - 2)/3):', first, '(' + secs.toFixed(1) + ' s)')
check(first === 319804831, 'expected 319804831')
if (first !== null) {
  const m = bigOrbit(first).reduce((a, b) => (a > b ? a : b))
  console.log('   its largest value is', m.toString(), '; 2^53 =', (2n ** 53n).toString())
}
console.log(failures === 0 ? '\n0 failures' : '\n' + failures + ' FAILURES')
process.exit(failures === 0 ? 0 : 1)
