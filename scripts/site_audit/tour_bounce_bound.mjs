// Tour audit: try to reproduce "bounce count <= (B+3)/4 for every odd m <= 5e6".
// The repo holds no code for this claim, so several candidate definitions of "bounce count" are tried.
//   D1  V=3 Set_3 visits (m = 9 mod 16) in the first weak streak (visits before the first depth >= 3 visit)
//   D1m the same, maximised over every weak streak of the orbit
//   D4  as D1 but only visits with k = (m-9)/16 = 2 or 3 mod 8
//   DW  the widget's BOUNCE rows (k = 2 mod 8) in the first weak streak
//   DWa the widget's BOUNCE rows over the whole orbit
const LIMIT = Number(process.argv[2] || 5e6)
const v2 = (n) => { let c = 0; while (n % 2 === 0) { n /= 2; c++ } return c }
const defs = ['D1', 'D1m', 'D4', 'DW', 'DWa']
const maxByBits = {}; const viol = {}; const firstAt = {}; const firstViol = {}
for (const d of defs) { maxByBits[d] = new Array(30).fill(0); viol[d] = 0; firstAt[d] = {}; firstViol[d] = null }
for (let m0 = 3; m0 <= LIMIT; m0 += 2) {
  let m = m0
  let d1 = 0, d4 = 0, dw = 0, dwa = 0, d1m = 0, cur = 0, first = true
  while (m > 1) {
    while (m % 4 === 3) m = (3 * m + 1) / 2
    if (m <= 1) break
    const t = 3 * m + 1
    const depth = v2(t)
    if (depth >= 3) { if (cur > d1m) d1m = cur; cur = 0; first = false }
    else if (m % 16 === 9) {
      const k8 = ((m - 9) / 16) % 8
      cur++
      if (first) { d1++; if (k8 === 2 || k8 === 3) d4++; if (k8 === 2) dw++ }
      if (k8 === 2) dwa++
    }
    m = t / 2 ** depth
  }
  if (cur > d1m) d1m = cur
  const B = Math.ceil(Math.log2(m0))       // the doc's B
  const bound = (B + 3) / 4
  const vals = { D1: d1, D1m: d1m, D4: d4, DW: dw, DWa: dwa }
  for (const d of defs) {
    const x = vals[d]
    if (x > maxByBits[d][B]) maxByBits[d][B] = x
    if (firstAt[d][x] === undefined) firstAt[d][x] = m0
    if (x > bound) { viol[d]++; if (firstViol[d] === null) firstViol[d] = m0 }
  }
}
console.log('odd m <=', LIMIT, ' B = ceil(log2 m), bound (B+3)/4')
for (const d of defs) {
  console.log(`\n${d}: violations ${viol[d]}` + (firstViol[d] ? ` (first at m = ${firstViol[d]})` : ''))
  console.log('  max by B (B=2..23): ' + maxByBits[d].slice(2, 24).join(' '))
  console.log('  first m reaching each count: ' + JSON.stringify(firstAt[d]))
}
