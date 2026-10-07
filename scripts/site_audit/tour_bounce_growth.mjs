// Tour audit: are "1.92 bits read per bounce" and "0.51 bits of growth per bounce" measured averages?
// Measures the actual change of log2(value) across bounces, for odd m <= LIMIT.
const LIMIT = Number(process.argv[2] || 1e6)
const v2 = (n) => { let c = 0; while (n % 2 === 0) { n /= 2; c++ } return c }
console.log('log2(243/64) =', Math.log2(243 / 64).toFixed(4), '  3*log2(9/8) =', (3 * Math.log2(9 / 8)).toFixed(4), '  5*log2(3)-6 =', (5 * Math.log2(3) - 6).toFixed(4))

// (a) every widget BOUNCE visit (m = 41 mod 128): growth from that visit to the next Set_3 visit
let nA = 0, sumA = 0, minA = 1e9
// (b) first weak streak, visits with m = 9 mod 16 and k = 2 or 3 mod 8 (the count that gives 4 for 76827 and 5 for 1227079):
//     growth of log2(value) from the first such visit to the end of the streak, per bounce
let nB = 0, sumB = 0, streaks = 0
for (let m0 = 3; m0 <= LIMIT; m0 += 2) {
  let m = m0, first = true, startVal = 0, cnt = 0, pendingBounce = 0
  while (m > 1) {
    while (m % 4 === 3) m = (3 * m + 1) / 2
    if (m <= 1) break
    if (pendingBounce) { const g = Math.log2(m / pendingBounce); nA++; sumA += g; if (g < minA) minA = g; pendingBounce = 0 }
    const t = 3 * m + 1, depth = v2(t)
    if (depth >= 3) {
      if (first && cnt > 0) { sumB += Math.log2(m / startVal); nB += cnt; streaks++ }
      first = false
    } else if (m % 16 === 9) {
      const k8 = ((m - 9) / 16) % 8
      if (k8 === 2) pendingBounce = m
      if (first && (k8 === 2 || k8 === 3)) { if (cnt === 0) startVal = m; cnt++ }
    }
    m = t / 2 ** depth
  }
}
console.log(`odd m <= ${LIMIT}`)
console.log(`(a) widget BOUNCE visits: ${nA}; mean growth to the next Set_3 visit = ${(sumA / nA).toFixed(3)} bits; minimum = ${minA.toFixed(4)} bits`)
console.log(`(b) first weak streaks holding a bounce: ${streaks}; bounces ${nB}; mean growth of log2(value) per bounce, first bounce to the deep drop = ${(sumB / nB).toFixed(3)} bits`)
for (const n of [76827, 1227079]) {
  let m = n; const vis = []
  while (m > 1 && vis.length < 16) { while (m % 4 === 3) m = (3 * m + 1) / 2; const t = 3 * m + 1, d = v2(t); vis.push([m, d]); m = t / 2 ** d }
  console.log(n, 'log2 at Set_3 visits:', vis.map(x => Math.log2(x[0]).toFixed(1) + (x[1] >= 3 ? '*' : '')).join(' '))
}
