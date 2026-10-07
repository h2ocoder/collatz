// Tour fixer: independent recomputation of every number written into the tour pages
// (site/journey/*.md and the journey components).  Run: node tour_fix_checks.mjs
const hr = (t) => console.log('\n=== ' + t + ' ===')
const v2 = (n) => { let c = 0; while (n % 2 === 0) { n /= 2; c++ } return c }
const L23 = Math.log2(3)

// ---------------------------------------------------------------- 1. cycle equation, small cases (exact)
hr('1. Cycle equation, exact: n = (sum_j 3^(S-1-j) 2^(a_j)) / (2^E - 3^S), a_j = halvings before the j-th odd step')
function compositions(E, S) { // E as an ordered sum of S positive parts
  const out = []
  ;(function rec(left, parts) {
    if (parts.length === S - 1) { if (left >= 1) out.push([...parts, left]); return }
    for (let p = 1; p <= left - (S - 1 - parts.length); p++) rec(left - p, [...parts, p])
  })(E, [])
  return out
}
function smallCase(S, E) {
  const g = 2n ** BigInt(E) - 3n ** BigInt(S)
  const comps = compositions(E, S)
  const hits = []
  for (const parts of comps) {
    let num = 0n, a = 0n
    for (let j = 0; j < S; j++) { num += 3n ** BigInt(S - 1 - j) * 2n ** a; a += BigInt(parts[j]) }
    if (num % g === 0n) hits.push({ parts: parts.join(','), n: (num / g).toString() })
  }
  console.log(`(S=${S}, E=${E}): gap ${g}, odd-start words ${comps.length}, integer solutions: ${JSON.stringify(hits)}`)
}
smallCase(1, 2); smallCase(5, 8); smallCase(2, 3); smallCase(3, 5); smallCase(3, 6)
{ // cyclic words for (5,8): length 13, five 1s, no two cyclically adjacent
  let n = 0
  for (let mask = 0; mask < 1 << 13; mask++) {
    let ones = 0, ok = true
    for (let i = 0; i < 13; i++) { const b = (mask >> i) & 1, c = (mask >> ((i + 1) % 13)) & 1; ones += b; if (b && c) ok = false }
    if (ok && ones === 5) n++
  }
  console.log('(5,8): cyclic words (every starting point):', n)
}
{ // check -5 and -7 really loop with two odd and three even steps
  let x = -5; const seq = [x]
  do { x = (((x % 2) + 2) % 2) ? 3 * x + 1 : x / 2; seq.push(x) } while (x !== -5)
  console.log('negative loop from -5:', seq.join(' -> '))
}

// ---------------------------------------------------------------- 2. words / gap
hr('2. Naive expected count: words / gap, with words = C(E-1, S-1)')
const binom = (n, k) => { let r = 1n; for (let i = 1n; i <= BigInt(k); i++) r = r * (BigInt(n) - i + 1n) / i; return r }
const ratio = (a, b) => { // a/b as a float, a and b BigInt
  if (a === 0n) return 0
  const sh = 60n; const q = (a << (sh + 64n)) / b; return Number(q) / 2 ** 124
}
for (const [S, E] of [[5, 8], [41, 65], [306, 485]]) {
  const g = 2n ** BigInt(E) - 3n ** BigInt(S)
  console.log(`(S=${S}, E=${E}): words/gap = ${ratio(binom(E - 1, S - 1), g).toExponential(3)}`)
}
for (const S of [1, 2, 3, 5, 10, 20, 41, 60, 100, 200]) {
  let tot = 0
  for (let E = Math.ceil(S * L23); E <= 14 * S + 60; E++) {
    const g = 2n ** BigInt(E) - 3n ** BigInt(S)
    if (g <= 0n) continue
    tot += ratio(binom(E - 1, S - 1), g)
  }
  console.log(`S=${S}: sum over every E with positive gap = ${tot.toFixed(3)}`)
}
{ const p = 1 / L23; console.log('entropy at S/E = 1/log2 3:', (-(p * Math.log2(p) + (1 - p) * Math.log2(1 - p))).toFixed(4)) }
console.log('1/(3 ln 2) =', (1 / (3 * Math.LN2)).toFixed(4), '(so E/S - log2 3 < 0.481 / n_min < 2^-69 when n_min > 2^68)')

// ---------------------------------------------------------------- 3. the site's 32-bit orbit
hr('3. OrbitPlayground: utils/collatz.ts halves with a 32-bit shift')
{
  const LIM = 2 ** 31
  let first = 0, count = 0, maxPeak = 0, maxAt = 0, maxBelow1e5 = 0
  for (let n = 2; n <= 999999; n++) {
    let x = n, peak = n
    while (x !== 1) { x = x % 2 ? 3 * x + 1 : x / 2; if (x > peak) peak = x }
    if (peak >= LIM) { count++; if (!first) first = n }
    if (peak > maxPeak) { maxPeak = peak; maxAt = n }
    if (n <= 100000 && peak > maxBelow1e5) maxBelow1e5 = peak
  }
  console.log(`starts <= 999999 whose true peak is >= 2^31: ${count}; first ${first}; largest peak ${maxPeak} at ${maxAt}`)
  console.log(`largest peak for a start <= 100000: ${maxBelow1e5} (< 2^31 = ${LIM}: ${maxBelow1e5 < LIM})`)
  const siteStep = (n) => (n & 1) ? 3 * n + 1 : n >> 1
  let n = 113383, steps = 0
  while (n !== 1 && steps < 10000) { n = siteStep(n); steps++ }
  console.log(`site orbit(113383): stopped after ${steps} steps at ${n}`)
  let x = 113383, t = 0, pk = x
  while (x !== 1) { x = x % 2 ? 3 * x + 1 : x / 2; t++; if (x > pk) pk = x }
  console.log(`true orbit of 113383: ${t} steps, peak ${pk}`)
}

// ---------------------------------------------------------------- 4. the puzzle page
hr('4. The Puzzle: 27, and the slider range 2..1000')
{
  let x = 27, t = 0, pk = 27, at = 0
  while (x !== 1) { x = x % 2 ? 3 * x + 1 : x / 2; t++; if (x > pk) { pk = x; at = t } }
  console.log(`27: ${t} steps, peak ${pk} at step ${at}; log2 start ${Math.log2(27).toFixed(2)}, log2 peak ${Math.log2(pk).toFixed(2)}, gain ${(Math.log2(pk / 27)).toFixed(2)} bits; bit lengths ${(27).toString(2).length} -> ${pk.toString(2).length}`)
  let rise = 0, all1 = true
  for (let n = 2; n <= 1000; n++) { let y = n, up = false, k = 0; while (y !== 1 && k < 1e5) { y = y % 2 ? 3 * y + 1 : y / 2; k++; if (y > n) up = true } if (y !== 1) all1 = false; if (up) rise++ }
  console.log(`n = 2..1000: all reach 1: ${all1}; orbits that go above their start: ${rise} of 999`)
  console.log('log2(3) =', L23.toFixed(4))
}

// ---------------------------------------------------------------- 5. bits
hr('5. Binary Engine: bit growth, coefficient stopping time, mean beta')
{
  let one = 0, two = 0, other = 0
  for (let n = 1; n < 1e5; n += 2) { const d = (3 * n + 1).toString(2).length - n.toString(2).length; if (d === 1) one++; else if (d === 2) two++; else other++ }
  console.log(`odd n < 1e5: 3n+1 adds 1 bit ${one} times, 2 bits ${two} times, anything else ${other} times`)
  const LIMIT = 1e7
  let bad = 0, sum = 0, cnt = 0
  for (let n = 2; n <= LIMIT; n++) {
    let x = n, s = 0, e = 0
    while (x >= n) { if (x % 2) { x = 3 * x + 1; s++ } else { x /= 2; e++ } }
    if (e !== (s === 0 ? 1 : Math.ceil(s * L23))) bad++
    if (n % 2) { sum += e - s * L23; cnt++ }
  }
  console.log(`n = 2..${LIMIT}: drops whose halving count is not ceil(s log2 3) (s >= 1; one halving for s = 0): ${bad}`)
  console.log(`odd n <= ${LIMIT}: mean of (halvings - s log2 3) over drops = ${(sum / cnt).toFixed(4)}`)
  const rec = []; let low = 2
  for (let s = 1; s <= 320; s++) { const b = Math.ceil(s * L23) - s * L23; if (b < low) { low = b; rec.push(`${Math.ceil(s * L23)}/${s}`) } }
  console.log('record-low beta at E/s =', rec.join(' '), ' (convergents of log2 3: 1/1 2/1 3/2 8/5 19/12 65/41 84/53 485/306)')
}

// ---------------------------------------------------------------- 6. countdowns
hr('6. The Countdown')
{
  let viol = 0, above = 0, tot = 0
  for (let m = 3; m < 200000; m += 4) {
    let x = m, v = v2(m + 1)
    while (x % 4 === 3) { const y = (3 * x + 1) / 2; if (v2(y + 1) !== v2(x + 1) - 1) viol++; x = y }
    const t = 3 * x + 1; const nxt = t / 2 ** v2(t)
    if (!(nxt < x)) viol++
    tot++; if (nxt > m) above++
    void v
  }
  console.log(`m = 3 mod 4 below 200000: ${tot} values; rule violations ${viol}; value after the step down still above m: ${above} (${(100 * above / tot).toFixed(1)}%)`)
  let v2viol = 0, endDeep = [0, 0], endClimb = [0, 0], oddW = 0, n8 = 0
  for (let m = 9; m < 400000; m += 8) {
    const w = v2(m - 1); n8++; if (w % 2) oddW++
    let x = m
    while (x % 8 === 1) { const y = (3 * x + 1) / 4; if (v2(y - 1) !== v2(x - 1) - 2) v2viol++; x = y }
    if (x % 8 === 5) endDeep[w % 2]++; else if (x % 4 === 3) endClimb[w % 2]++; else v2viol++
  }
  console.log(`m = 1 mod 8 below 400000: ${n8} values; "falls by exactly 2" violations ${v2viol}; v2(m-1) even -> deep ${endDeep[0]}, climb ${endClimb[0]}; odd -> deep ${endDeep[1]}, climb ${endClimb[1]}; share with odd v2(m-1): ${(oddW / n8).toFixed(4)}`)
  console.log('example: 9 ->', (3 * 9 + 1) / 4, ' 17 ->', (3 * 17 + 1) / 4)
  let s = 0, c = 0
  for (let m = 1; m < 1e6; m += 2) { s += v2(3 * m + 1); c++ }
  console.log(`odd m < 1e6: mean v2(3m+1) = ${(s / c).toFixed(4)} (geometric-mean factor per odd step 3/2^2 = 3/4)`)
}

// ---------------------------------------------------------------- 7. bounces
hr('7. Finite Fuel: the BOUNCE rows of the simulator (Set_3 visits with m = 41 mod 128)')
{
  let bad = 0, minG = 1e9, n = 0
  for (let m = 41; m < 1e6; m += 128) {
    const y = (3 * m + 1) / 4
    if (v2(3 * m + 1) !== 2 || y % 32 !== 31) bad++
    let x = y, climbs = 0
    while (x % 4 === 3) { x = (3 * x + 1) / 2; climbs++ }
    if (climbs < 4) bad++
    let z = y; for (let i = 0; i < 4; i++) z = (3 * z + 1) / 2
    const g = Math.log2(z / m); if (g < minG) minG = g
    n++
  }
  console.log(`m = 41 mod 128 below 1e6: ${n} values; not (weak drop to 31 mod 32, then >= 4 climbing steps): ${bad}; least growth after four climbing steps ${minG.toFixed(4)} bits; log2(243/64) = ${Math.log2(243 / 64).toFixed(4)}; 3 log2(9/8) = ${(3 * Math.log2(9 / 8)).toFixed(4)}`)
  function rows(start) { // as BounceSimulator.vue builds them (80-row cap), exact arithmetic
    let m = Math.max(3, start); if (m % 2 === 0) m++
    const out = []; let acc = 0, big = false
    for (let i = 0; i < 80 && m > 1; i++) {
      while (m > 1 && m % 4 === 3) m = (3 * m + 1) / 2
      if (m <= 1) break
      const depth = v2(3 * m + 1)
      const isB = v2(m - 1) === 3 && m % 16 === 9 && ((m - 9) / 16) % 8 === 2
      acc += isB ? 1.92 : 0.5
      if (3 * m + 1 >= 2 ** 31) big = true
      out.push({ t: isB ? 'B' : depth >= 4 ? 'S' : depth >= 3 ? 'm' : 'w', acc, depth })
      m = (3 * m + 1) / 2 ** depth
    }
    return { out, big }
  }
  for (const s of [76827, 1227079, 27, 2919]) {
    const { out, big } = rows(s)
    const B = Math.ceil(Math.log2(s + 1))
    const bIdx = out.map((r, i) => r.t === 'B' ? i : -1).filter(i => i >= 0)
    const firstDeep = out.findIndex(r => r.depth >= 3)
    const pass = out.findIndex(r => r.acc > B)
    console.log(`start ${s}: budget ${B}; ${out.length} rows; BOUNCE at rows ${bIdx.join(',')}; first deep drop at row ${firstDeep} (${out[firstDeep]?.t}); tally first exceeds budget at row ${pass} (${out[pass]?.acc.toFixed(2)}); final tally ${out[out.length - 1].acc.toFixed(1)}; first rows ${out.slice(0, 10).map(r => r.t).join(' ')}; any value >= 2^31: ${big}`)
  }
  // bound (B+3)/4, B = ceil(log2 m)
  let violFirst = 0, violAll = 0, firstAll = 0
  for (let m0 = 3; m0 <= 5e6; m0 += 2) {
    let m = m0, bFirst = 0, bAll = 0, first = true
    while (m > 1) {
      while (m % 4 === 3) m = (3 * m + 1) / 2
      if (m <= 1) break
      const depth = v2(3 * m + 1)
      if (depth >= 3) first = false
      else if (m % 128 === 41) { bAll++; if (first) bFirst++ }
      m = (3 * m + 1) / 2 ** depth
    }
    const bound = (Math.ceil(Math.log2(m0)) + 3) / 4
    if (bFirst > bound) violFirst++
    if (bAll > bound) { violAll++; if (!firstAll) firstAll = m0 }
  }
  console.log(`odd m <= 5e6, bound (B+3)/4 with B = ceil(log2 m): BOUNCE visits before the first deep drop exceed it ${violFirst} times; over the whole orbit ${violAll} times (first m = ${firstAll})`)
}

// ---------------------------------------------------------------- 8. rotation
hr('8. The Hidden Rotation')
{
  const L6 = Math.log(6), A = Math.log(3) / L6
  const frac = (x) => x - Math.floor(x)
  const circ = (a, b) => { const d = Math.abs(frac(a) - frac(b)); return Math.min(d, 1 - d) }
  console.log(`log6 3 = ${A.toFixed(4)}; log6 2 = ${(Math.log(2) / L6).toFixed(4)}; 27/44 = ${(27 / 44).toFixed(4)}; 44*log6 3 = ${(44 * A).toFixed(4)}; 31*log6 3 = ${(31 * A).toFixed(4)}`)
  let worst = 0, at = 0
  for (let n = 3; n <= 99999; n++) {
    let x = n, W = 0
    while (x !== 1) { if (x % 2) { W += Math.log(1 + 1 / (3 * x)) / L6; x = 3 * x + 1 } else x /= 2 }
    if (W > worst) { worst = W; at = n }
  }
  console.log(`3 <= n <= 99999: largest total drift from the exact rotation by the time the orbit reaches 1: ${worst.toFixed(4)} of a turn (n = ${at})`)
  for (const n of [27, 97, 703, 6171, 77031]) {
    const full = [n], odd = [n]; let x = n
    while (x !== 1) { x = x % 2 ? 3 * x + 1 : x / 2; full.push(x); if (x % 2) odd.push(x) }
    const th0 = Math.log(n) / L6
    let dOdd = 0; for (let i = 1; i < odd.length; i++) dOdd += circ(Math.log(odd[i]) / L6, th0 + i * A)
    let dFull = 0; for (let i = 1; i < full.length; i++) dFull += circ(Math.log(full[i]) / L6, th0 + i * A)
    let r44 = 0, c44 = 0; for (let k = 0; k + 44 < full.length; k++) { r44 += circ(Math.log(full[k]) / L6, Math.log(full[k + 44]) / L6); c44++ }
    // star discrepancy of the first k odd-value points, k = 10, 20, 40, all
    const disc = (pts) => { const s = [...pts].sort((a, b) => a - b); let D = 0; for (let i = 0; i < s.length; i++) D = Math.max(D, Math.abs((i + 1) / s.length - s[i]), Math.abs(i / s.length - s[i])); return D }
    const pos = odd.map(v => frac(Math.log(v) / L6))
    const ds = [10, 20, 40, 80, pos.length].filter((k, i, a) => k <= pos.length && a.indexOf(k) === i).map(k => `${k}:${disc(pos.slice(0, k)).toFixed(3)}`)
    console.log(`n=${n}: ${full.length} values, ${odd.length} odd; widget pairing (odd value i vs grey dot i): mean distance ${(dOdd / (odd.length - 1)).toFixed(3)}; every step vs rotation: mean ${(dFull / (full.length - 1)).toFixed(3)}; mean distance after 44 steps ${c44 ? (r44 / c44).toFixed(3) : 'n/a'}; discrepancy of first k odd-value points ${ds.join(' ')}`)
  }
  let maxOdd = 0, maxAt = 0
  for (let n = 3; n <= 99999; n += 2) { let x = n, c = 1; while (x !== 1) { x = x % 2 ? 3 * x + 1 : x / 2; if (x % 2) c++ } if (c > maxOdd) { maxOdd = c; maxAt = n } }
  console.log(`most odd values in an orbit, odd start <= 99999: ${maxOdd} (n = ${maxAt})`)
  // 3x-1 cycles
  for (const s of [5, 17]) { let x = s; const seq = [x]; do { x = x % 2 ? 3 * x - 1 : x / 2; seq.push(x) } while (x !== s && seq.length < 60); console.log(`3x-1 from ${s}: returns after ${seq.length - 1} steps: ${x === s}`) }
}
