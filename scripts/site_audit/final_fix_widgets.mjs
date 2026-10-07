// Final-fixer check: up to which start do the 32-bit widgets show the true orbit?
// The functions below copy the widgets' arithmetic exactly (utils/collatz.ts and the
// loops inside BounceSimulator, CountdownVisualizer, DepthExplorer); the *Exact twins use BigInt.
// Run: node scripts/site_audit/final_fix_widgets.mjs

// ---- utils/collatz.ts, as shipped ----
function v2(n) { if (n === 0) return Infinity; let c = 0; while ((n & 1) === 0) { n >>= 1; c++ } return c }
function collatzStep(n) { return (n & 1) ? 3 * n + 1 : n >> 1 }
function orbit(n, maxSteps = 10000) { const seq = [n]; let steps = 0; while (n !== 1 && steps < maxSteps) { n = collatzStep(n); seq.push(n); steps++ } return seq }
function syracuseStep(m) { let val = 3 * m + 1; while ((val & 1) === 0) val >>= 1; return val }
function syracuseOrbit(m, maxSteps = 5000) { const seq = [m]; let steps = 0; while (m !== 1 && steps < maxSteps) { m = syracuseStep(m); seq.push(m); steps++ } return seq }
function stoppingTime(n) { const start = n; let steps = 0; while (n >= start && n !== 1) { n = collatzStep(n); steps++; if (steps > 100000) return -1 } return steps }
function stoppingDestination(n) { const start = n; let guard = 0; while (n >= start) { n = collatzStep(n); if (++guard > 100000) return NaN } return n }
function dropDepth(m) { return v2(3 * m + 1) }

// ---- exact twins ----
function orbitExact(n0) { let n = BigInt(n0); const seq = [n]; while (n !== 1n) { n = (n & 1n) ? 3n * n + 1n : n / 2n; seq.push(n) } return seq.map(Number) }
function syrExact(n0) { let m = BigInt(n0); const seq = [m]; while (m !== 1n) { let t = 3n * m + 1n; while ((t & 1n) === 0n) t /= 2n; m = t; seq.push(m) } return seq.map(Number) }
function dropExact(n0) { const n = BigInt(n0); let x = n, k = 0; do { x = (x & 1n) ? 3n * x + 1n : x / 2n; k++ } while (x >= n); return [k, Number(x)] }

// ---- widget loops ----
function bounceWidget(n0) { let m = Math.max(3, n0); if (m % 2 === 0) m++; const rows = [];
  for (let i = 0; i < 80 && m > 1; i++) { while (m > 1 && m % 4 === 3) { m = (3 * m + 1) / 2 } if (m <= 1) break
    const vm1 = v2(m - 1); const isBounce = vm1 === 3 && m % 16 === 9 && ((m - 9) / 16) % 8 === 2
    rows.push([m, dropDepth(m), isBounce]); let next = 3 * m + 1; while (next % 2 === 0) next >>= 1; m = next } return rows }
function bounceExact(n0) { let m = BigInt(Math.max(3, n0)); if (m % 2n === 0n) m++; const rows = [];
  for (let i = 0; i < 80 && m > 1n; i++) { while (m > 1n && m % 4n === 3n) { m = (3n * m + 1n) / 2n } if (m <= 1n) break
    let t = 3n * m + 1n, d = 0; while (t % 2n === 0n) { t /= 2n; d++ }
    rows.push([Number(m), d, m % 128n === 41n]); m = t } return rows }
function countdownWidget(n0) { let m = Math.max(3, n0); if (m % 2 === 0) m++; const out = []; for (let i = 0; i < 60 && m > 1; i++) { out.push([m, v2(m + 1), v2(m - 1), dropDepth(m)]); let next = 3 * m + 1; while (next % 2 === 0) next >>= 1; m = next } return out }
function v2big(x) { let c = 0; while (x % 2n === 0n) { x /= 2n; c++ } return c }
function countdownExact(n0) { let m = BigInt(Math.max(3, n0)); if (m % 2n === 0n) m++; const out = []; for (let i = 0; i < 60 && m > 1n; i++) { out.push([Number(m), v2big(m + 1n), m === 1n ? Infinity : v2big(m - 1n), v2big(3n * m + 1n)]); let t = 3n * m + 1n; while (t % 2n === 0n) t /= 2n; m = t } return out }
function depthWidget(n0) { let m = Math.max(3, n0); if (m % 2 === 0) m++; const out = []; for (let i = 0; i < 40 && m > 1; i++) { out.push([m, dropDepth(m)]); m = syracuseStep(m) } return out }
function depthExact(n0) { let m = BigInt(Math.max(3, n0)); if (m % 2n === 0n) m++; const out = []; for (let i = 0; i < 40 && m > 1n; i++) { out.push([Number(m), v2big(3n * m + 1n)]); let t = 3n * m + 1n; while (t % 2n === 0n) t /= 2n; m = t } return out }

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b)
function firstBad(lo, hi, step, w, e) { for (let n = lo; n < hi; n += step) { if (!same(w(n), e(n))) return n } return null }
let ok = true
function check(label, cond, detail = '') { ok = ok && cond; console.log(`  [${cond ? 'OK' : 'FAIL'}] ${label}${detail ? ' -- ' + detail : ''}`) }

const LIM = 100000
console.log('1. Widgets against exact arithmetic, every start below 100,000')
check('OrbitPlayground / BinaryStepVisualizer (orbit, every n from 2)', firstBad(2, LIM, 1, n => orbit(n), orbitExact) === null)
check('Base6Circle / EisensteinWalk / AlphaPositionChart (Syracuse orbit, odd n from 3)', firstBad(3, LIM, 2, n => syracuseOrbit(n), syrExact) === null)
check('BounceSimulator rows (value, depth, BOUNCE flag)', firstBad(3, LIM, 1, bounceWidget, bounceExact) === null)
check('CountdownVisualizer rows', firstBad(3, LIM, 1, countdownWidget, countdownExact) === null)
check('DepthExplorer rows', firstBad(3, LIM, 1, depthWidget, depthExact) === null)
check('DroppingSetExplorer (dropping time and destination, n from 2 to 100,100)',
  firstBad(2, 100101, 1, n => [stoppingTime(n), stoppingDestination(n)], dropExact) === null)

console.log('2. First start at which each goes wrong (searched up to 400,000)')
const HI = 400000
const fb = {
  orbit: firstBad(LIM, HI, 1, n => orbit(n, 3000), orbitExact),
  syracuse: firstBad(LIM + 1, HI, 2, n => syracuseOrbit(n, 3000), syrExact),
  bounce: firstBad(LIM + 1, HI, 2, bounceWidget, bounceExact),
  countdown: firstBad(LIM + 1, HI, 2, countdownWidget, countdownExact),
  depth: firstBad(LIM + 1, HI, 2, depthWidget, depthExact),
  dropping: firstBad(LIM, HI, 1, n => [stoppingTime(n), stoppingDestination(n)], dropExact),
}
console.log('   ', JSON.stringify(fb))
check('nothing goes wrong below 113,000; the full-orbit widgets first fail at 113,383',
  Object.values(fb).every(v => v === null || v >= 113000) && fb.orbit === 113383 && fb.syracuse === 113383,
  `peak of 113383 is ${Math.max(...orbitExact(113383)).toLocaleString('en-US')}, 2^31 = ${(2 ** 31).toLocaleString('en-US')}`)
check('BounceSimulator shows 15 rows for 113383 where the true list has 39',
  bounceWidget(113383).length === 15 && bounceExact(113383).length === 39)

console.log('3. The examples named on Finite Fuel')
for (const n of [27, 76827, 1227079]) {
  const w = bounceWidget(n), e = bounceExact(n)
  const b = e.map((r, i) => r[2] ? i : -1).filter(i => i >= 0)
  const firstDeep = e.findIndex(r => r[1] >= 3)
  check(`${n}: widget rows equal the exact rows`, same(w, e), `BOUNCE rows ${JSON.stringify(b)}, first depth>=3 at row ${firstDeep}, ${e.length} rows`)
}

console.log('4. NaturalVs2Adic: first 30 values, n up to 9,999')
check('first 30 orbit values exact for every n from 2 to 9,999',
  firstBad(2, 10000, 1, n => orbit(n, 200).slice(0, 30), n => orbitExact(n).slice(0, 30)) === null)

console.log(ok ? '\nALL OK' : '\nSOME CHECKS FAILED')
