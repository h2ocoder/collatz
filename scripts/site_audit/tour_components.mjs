// Tour audit: run the journey components' own logic (imported from the site's utils)
// and compare what they print with the truth.  Read-only; prints to stdout.
import {
  v2, collatzStep, orbit, syracuseStep, syracuseOrbit, stoppingTime, orbitalOddity,
  beta, cycleGap, dropDepth, parityWords, log6, frac, LOG6_3, LOG2_3,
} from '../../site/.vitepress/theme/utils/collatz.ts'

const hr = (t) => console.log('\n=== ' + t + ' ===')

// ---------------------------------------------------------------- CycleHunter
hr('CycleHunter: what the widget prints')
function cycleHunter(S, E) {
  const K = S + E
  const asc = S * Math.log2(3) > E
  const gap = cycleGap(S, E)
  if (asc) return { S, E, verdict: 'ASCENDING' }
  const words = K > 25 ? null : parityWords(K, S)
  if (!words) return { S, E, verdict: 'too large' }
  const g = Number(gap)
  let zero = 0
  for (const w of words) {
    let T = 0, pow2 = 1, pow3 = 1
    for (let i = 0; i < w.length; i++) {
      if (w[i] === 1) { T = (T + pow3 * pow2) % g; pow3 = (pow3 * 3) % g }
      pow2 = (pow2 * 2) % g
    }
    if (((T % g) + g) % g === 0) zero++
  }
  const sub = `C(${E - 1},${S - 1})`
  return { S, E, gap: g, wordsShown: words.length, subLabel: sub, zero,
           verdict: zero === 0 ? 'NO CYCLE OF THIS SHAPE' : 'CYCLE FOUND' }
}
for (const [S, E] of [[1, 2], [2, 4], [3, 6], [5, 8], [3, 5], [2, 3], [4, 7], [2, 5], [3, 7], [4, 8], [6, 10], [7, 12]]) {
  console.log(JSON.stringify(cycleHunter(S, E)))
}

// truth: 3x+1 map, S odd steps, E even steps, start at an odd element.
// word = composition (a_1..a_S) of E into S positive parts; n = c / (2^E - 3^S),
// c = sum_j 3^(S-1-j) 2^(a_1+...+a_j)   (j = 0..S-1, empty sum = 0)
hr('Truth: compositions of E into S parts, exact arithmetic')
function binom(n, k) { let r = 1n; for (let i = 0n; i < BigInt(k); i++) r = r * (BigInt(n) - i) / (i + 1n); return r }
function trueCycles(S, E) {
  const g = (1n << BigInt(E)) - 3n ** BigInt(S)
  let count = 0, hits = []
  const parts = []
  function rec(left, slots) {
    if (slots === 1) { parts.push(left); check(); parts.pop(); return }
    for (let a = 1; a <= left - (slots - 1); a++) { parts.push(a); rec(left - a, slots - 1); parts.pop() }
  }
  function check() {
    count++
    let c = 0n, pre = 0
    for (let j = 0; j < S; j++) { c += 3n ** BigInt(S - 1 - j) * (1n << BigInt(pre)); pre += parts[j] }
    if (g !== 0n && c % g === 0n) hits.push({ parts: [...parts], n: (c / g).toString() })
  }
  rec(E, S)
  return { S, E, gap: g.toString(), compositions: count, binom: binom(E - 1, S - 1).toString(), hits }
}
for (const [S, E] of [[1, 2], [2, 4], [3, 6], [5, 8], [3, 5], [2, 3], [4, 7], [2, 5], [3, 7], [4, 8], [6, 10], [7, 12]]) {
  console.log(JSON.stringify(trueCycles(S, E)))
}
console.log('3^3 =', 3 ** 3, ' 2^5 =', 2 ** 5, ' -> gap 2^5-3^3 =', 2 ** 5 - 3 ** 3, '(positive)')
console.log('3^2 =', 3 ** 2, ' 2^3 =', 2 ** 3, ' -> gap 2^3-3^2 =', 2 ** 3 - 3 ** 2, '(negative)')
console.log('C(13,5)=', binom(13, 5).toString(), ' C(12,4)=', binom(12, 4).toString(), ' C(8,5)=', binom(8, 5).toString(), ' C(7,4)=', binom(7, 4).toString(), ' C(14,2)=', binom(14, 2).toString())

// ---------------------------------------------------------------- BinaryStepVisualizer
hr('BinaryStepVisualizer: bit growth on a x3+1 step')
const bl = (n) => n.toString(2).length
let g1 = 0, g2 = 0, g0 = 0
for (let n = 1; n < 100000; n += 2) { const d = bl(3 * n + 1) - bl(n); if (d === 1) g1++; else if (d === 2) g2++; else g0++ }
console.log('odd n < 1e5: growth 1 bit:', g1, ' 2 bits:', g2, ' other:', g0)
console.log('27 ->', 82, ': bits', bl(27), '->', bl(82))
let h0 = 0, h1 = 0
for (let n = 1; n < 100000; n += 2) { const d = bl((3 * n + 1) / 2) - bl(n); if (d === 0) h0++; else if (d === 1) h1++ }
console.log('odd n < 1e5: (3n+1)/2 adds 0 bits:', h0, ' 1 bit:', h1)

// ---------------------------------------------------------------- OrbitPlayground overflow
hr('OrbitPlayground / utils.orbit: 32-bit shift overflow')
function trueOrbitLen(n) { let s = 0, peak = n; while (n !== 1) { n = n % 2 ? 3 * n + 1 : n / 2; if (n > peak) peak = n; s++ } return { s, peak } }
let firstBad = null, badCount = 0
for (let n = 2; n <= 999999; n++) {
  const t = trueOrbitLen(n)
  if (t.peak >= 2 ** 31) { badCount++; if (firstBad === null) firstBad = n }
}
console.log('n <= 999999 whose true peak >= 2^31:', badCount, ' first:', firstBad)
if (firstBad) {
  const o = orbit(firstBad)
  const t = trueOrbitLen(firstBad)
  console.log('utils.orbit(', firstBad, ') length-1 =', o.length - 1, ' last =', o[o.length - 1], ' min =', Math.min(...o), ' | true steps', t.s, 'true peak', t.peak)
}
for (const n of [27, 703, 77671, 99999]) { const t = trueOrbitLen(n); const o = orbit(n); console.log(n, 'widget steps', o.length - 1, 'true', t.s, 'peak', t.peak) }
let maxPeak1e5 = 0; for (let n = 2; n < 100000; n++) { const t = trueOrbitLen(n); if (t.peak > maxPeak1e5) maxPeak1e5 = t.peak }
console.log('max peak for n < 1e5:', maxPeak1e5, ' < 2^31?', maxPeak1e5 < 2 ** 31)

// ---------------------------------------------------------------- HailstoneChart
hr('HailstoneChart: is the log-scale picture a steady descent?')
{
  const o = orbit(27); const pk = Math.max(...o)
  console.log('27: steps', o.length - 1, 'peak', pk, 'at step', o.indexOf(pk), 'log2 start', Math.log2(27).toFixed(2), 'log2 peak', Math.log2(pk).toFixed(2))
  let climbers = 0, big = 0
  for (let n = 2; n <= 1000; n++) { const oo = orbit(n); const p = Math.max(...oo); if (p > n) climbers++; if (Math.log2(p) - Math.log2(n) >= 3) big++ }
  console.log('n in 2..1000: orbits that rise above their start:', climbers, ' of 999; rising by 3 or more bits:', big)
}

// ---------------------------------------------------------------- Base6Circle
hr('Base6Circle: coloured dots (Syracuse orbit) vs grey dots (i * log6 3)')
const circ = (a, b) => { let d = Math.abs(frac(a) - frac(b)); return Math.min(d, 1 - d) }
for (const n of [27, 97, 703, 6171, 77031]) {
  const orb = syracuseOrbit(n, 510)
  let sum = 0, cnt = 0, close = 0
  for (let i = 1; i < orb.length; i++) {
    const d = circ(log6(orb[i]), log6(n) + i * LOG6_3)
    sum += d; cnt++; if (d < 0.02) close++
  }
  // same comparison against every Collatz step
  const full = orbit(n)
  let sum2 = 0, cnt2 = 0, maxd2 = 0
  for (let i = 1; i < full.length; i++) { const d = circ(log6(full[i]), log6(n) + i * LOG6_3); sum2 += d; cnt2++; if (d > maxd2) maxd2 = d }
  console.log(`n=${n}: Syracuse points ${orb.length}; mean circular distance coloured_i vs grey_i = ${(sum / cnt).toFixed(3)} (random = 0.250), within 0.02: ${close}/${cnt}` +
    ` | all Collatz steps: mean ${(sum2 / cnt2).toFixed(3)}, max ${maxd2.toFixed(3)} over ${cnt2} steps`)
}
{
  // rotation per Syracuse step
  const m = 27, s = syracuseStep(m)
  console.log('27 -> 41: advance on circle =', frac(log6(s) - log6(m)).toFixed(4), ' log6(3) =', LOG6_3.toFixed(4), ' 2*log6(3) mod 1 =', frac(2 * LOG6_3).toFixed(4))
  console.log('halving: -log6(2) mod 1 =', frac(-Math.log(2) / Math.log(6)).toFixed(4), '= log6(3)')
  // advance per Syracuse step as a function of a = v2(3m+1)
  for (let a = 1; a <= 4; a++) console.log(' a =', a, ': (1+a)*log6(3) mod 1 =', frac((1 + a) * LOG6_3).toFixed(4))
  let maxSyr = 0, arg = 0
  for (let n = 3; n <= 99999; n += 2) { const L = syracuseOrbit(n, 5000).length; if (L > maxSyr) { maxSyr = L; arg = n } }
  console.log('longest Syracuse orbit for odd n <= 99999:', maxSyr, 'points, at n =', arg)
}
{
  console.log('44*log6(3) =', (44 * LOG6_3).toFixed(4), ' 31*log6(3) =', (31 * LOG6_3).toFixed(4), ' 13*log6(3) =', (13 * LOG6_3).toFixed(4), ' 106*log6(3)=', (106 * LOG6_3).toFixed(4))
}

// ---------------------------------------------------------------- beta records
hr('BitDestructionLandscape: record-low beta(s)')
{
  let rec = 2; const out = []
  for (let s = 1; s <= 400; s++) { const b = beta(s); if (b < rec) { rec = b; out.push(`${s}:${b.toFixed(4)}(E=${Math.ceil(s * LOG2_3)})`) } }
  console.log(out.join('  '))
}

// ---------------------------------------------------------------- Countdown
hr('Countdowns')
{
  // one-bit: for m = 3 mod 4, v2(S(m)+1) = v2(m+1)-1
  let bad = 0
  for (let m = 3; m < 200000; m += 4) { const s = (3 * m + 1) / 2; if (v2(s + 1) !== v2(m + 1) - 1) bad++ }
  console.log('one-bit countdown violations (m = 3 mod 4, m < 2e5):', bad)
  // net change over one climb + the Set_3 step
  let up = 0, tot = 0
  for (let m = 3; m < 200000; m += 4) { let x = m; while (x % 4 === 3) x = (3 * x + 1) / 2; const y = syracuseStep(x); tot++; if (y > m) up++ }
  console.log('m = 3 mod 4, m < 2e5: after the countdown and the Set_3 step the orbit is still ABOVE m in', up, 'of', tot, 'cases')
  // two-bit: m = 1 mod 8, w = v2(m-1): next = (3m+1)/4 has v2(next-1) = w-2
  let bad2 = 0, deepAfter = { even: [0, 0], odd: [0, 0] }
  for (let m = 9; m < 400000; m += 8) {
    const w = v2(m - 1); const nx = (3 * m + 1) / 4
    if (w - 2 >= 1 && v2(nx - 1) !== w - 2) bad2++
    // follow the run of weak drops to its end
    let x = m
    while (x % 8 === 1) x = (3 * x + 1) / 4
    const endsDeep = x % 8 === 5, endsClimb = x % 4 === 3
    const key = w % 2 === 0 ? 'even' : 'odd'
    if (endsDeep) deepAfter[key][0]++; else if (endsClimb) deepAfter[key][1]++
  }
  console.log('two-bit step violations:', bad2)
  console.log('run of weak drops from m = 1 mod 8 ends in [deep drop, climb]:  w even ->', deepAfter.even, '  w odd ->', deepAfter.odd)
  console.log('example 9 -> ', syracuseStep(9), '(mod 4 =', syracuseStep(9) % 4, ')')
}

// ---------------------------------------------------------------- BounceSimulator
hr('BounceSimulator: what the widget prints')
function bounceSim(start) {
  let m = Math.max(3, start); if (m % 2 === 0) m++
  const entries = []; let acc = 0
  for (let i = 0; i < 80 && m > 1; i++) {
    while (m > 1 && m % 4 === 3) m = (3 * m + 1) / 2
    if (m <= 1) break
    const depth = dropDepth(m); const vm1 = v2(m - 1)
    const isBounce = vm1 === 3 && m % 16 === 9 && ((m - 9) / 16) % 8 === 2
    const bitLen = Math.ceil(Math.log2(m + 1))
    acc += isBounce ? 1.92 : 0.5
    entries.push({ m, bitLen, acc, depth, isBounce })
    let next = 3 * m + 1
    while (next % 2 === 0) next >>= 1
    m = next
  }
  return entries
}
for (const n of [76827, 1227079, 27]) {
  const e = bounceSim(n)
  const B = Math.ceil(Math.log2(n + 1))
  const bounces = e.filter(x => x.isBounce).length
  const firstWarn = e.findIndex(x => x.acc > B * 0.8)
  console.log(`start ${n}: budget ${B} bits; rows ${e.length}; BOUNCE rows ${bounces}; rows: ` +
    e.slice(0, 14).map(x => (x.isBounce ? 'B' : x.depth >= 4 ? 'S' : x.depth >= 3 ? 'm' : 'w') + x.bitLen).join(' ') +
    `; "Consumed" at last row ${e[e.length - 1].acc.toFixed(1)}; warning box first shows at row ${firstWarn}; any negative/garbage m: ${e.some(x => x.m < 0 || !Number.isInteger(x.m))}; max m ${Math.max(...e.map(x => x.m))}`)
}
