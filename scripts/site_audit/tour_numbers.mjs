// Tour audit: numbers quoted on the journey pages.
const L23 = Math.log2(3)
const v2 = (n) => { let c = 0; while (n % 2 === 0) { n /= 2; c++ } return c }
const hr = (t) => console.log('\n=== ' + t + ' ===')

// ------------------------------------------------ dropping words: s, e for every n; CST check; mean beta
hr('Drops: is the number of halvings always ceil(s log2 3)?  (Terras coefficient stopping time)')
{
  const LIMIT = Number(process.argv[2] || 1e7)
  let bad = 0, firstBad = null
  let sumBetaOdd = 0, nOdd = 0, sumBetaAll = 0, nAll = 0
  const setOf = {}
  for (let n = 2; n <= LIMIT; n++) {
    let x = n, s = 0, e = 0
    while (x >= n) { if (x % 2) { x = 3 * x + 1; s++ } else { x = x / 2; e++ } }
    const need = s === 0 ? 1 : Math.ceil(s * L23)
    if (e !== need) { bad++; if (firstBad === null) firstBad = n }
    const removed = e - s * L23            // bits removed beyond break-even, exact for this n
    if (n % 2) { sumBetaOdd += removed; nOdd++ }
    sumBetaAll += removed; nAll++
    if (n <= 1 << 16) { const k = s + e; setOf[k] = setOf[k] || new Set(); setOf[k].add(s) }
  }
  console.log(`2 <= n <= ${LIMIT}: drops whose halving count differs from ceil(s log2 3): ${bad}` + (firstBad ? ` (first ${firstBad})` : ''))
  console.log(`mean bits removed beyond break-even, e - s log2 3:  odd n: ${(sumBetaOdd / nOdd).toFixed(4)}   all n: ${(sumBetaAll / nAll).toFixed(4)}`)
  console.log('dropping times seen for n <= 65536 and their s:', Object.keys(setOf).map(Number).sort((a, b) => a - b).slice(0, 12).map(k => `${k}:{${[...setOf[k]].join(',')}}`).join(' '))
}

// ------------------------------------------------ density-weighted mean beta from class counts (A100982)
hr('Density-weighted mean of beta(s) over dropping classes')
{
  // N(s) = number of residue classes mod 2^e(s) with s odd steps, e(s) = ceil(s log2 3); count by brute force over residues
  let tot = 0, wsum = 0
  const out = []
  for (let s = 1; s <= 12; s++) {
    const e = Math.ceil(s * L23)
    // count residues r mod 2^e whose coefficient stopping time has exactly s odd steps and e halvings
    let cnt = 0
    const M = 2 ** e
    for (let r = 1; r < M; r += 2) {
      // follow parity of r + M*t symbolically: track (a, b) with value = a*t + b ; a = M*3^i/2^j
      let b = r, i = 0, j = 0, ok = false
      // use BigInt-free: b stays < 2^53 for e <= 20
      while (j < e) {
        if (b % 2) { b = 3 * b + 1; i++ } else { b = b / 2; j++ }
        if (j > 0 && i * L23 < j) { ok = (i === s && j === e); break }
      }
      if (ok) cnt++
    }
    const dens = cnt / M
    const beta = e - s * L23
    tot += dens; wsum += dens * beta
    out.push(`s=${s}:N=${cnt},e=${e},beta=${beta.toFixed(3)}`)
  }
  console.log(out.join('  '))
  console.log(`density of odd n covered (s<=12): ${tot.toFixed(4)} of 0.5;  mean beta over those odd n: ${(wsum / tot).toFixed(4)};  with evens (beta=1, density 1/2): ${((wsum + 0.5) / (tot + 0.5)).toFixed(4)}`)
}

// ------------------------------------------------ naive expected cycle count
hr('Naive expected number of cycle words: sum over E of C(E-1,S-1) / (2^E - 3^S)')
{
  const lgamma = (x) => { // Lanczos
    const g = 7, c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7]
    x -= 1; let a = c[0]; const t = x + g + 0.5
    for (let i = 1; i < 9; i++) a += c[i] / (x + i)
    return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a)
  }
  const lbin = (n, k) => lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)
  let cum = 0
  for (const S of [1, 2, 3, 5, 10, 20, 41, 100, 306, 1000]) {
    let tot = 0, near = 0
    const E0 = Math.ceil(S * L23)
    for (let E = E0; E <= 12 * S + 40; E++) {
      const lg = E * Math.LN2 + Math.log1p(-Math.exp(S * Math.log(3) - E * Math.LN2))
      const term = Math.exp(lbin(E - 1, S - 1) - lg)
      tot += term; if (E === E0) near = term
    }
    console.log(`S=${S}: smallest E=${E0}: words/gap = ${near.toExponential(3)};  summed over all E with positive gap = ${tot.toFixed(3)}`)
  }
  console.log('(5,8): 35/13 =', (35 / 13).toFixed(2), '  (41,65): C(64,40)/gap =', Math.exp(lbin(64, 40) - Math.log(2 ** 65 - 3 ** 41)).toFixed(3))
  console.log('entropy at S/E = 1/log2(3):', (() => { const p = 1 / L23; return -(p * Math.log2(p) + (1 - p) * Math.log2(1 - p)) })().toFixed(4))
}

// ------------------------------------------------ misc facts
hr('Misc')
console.log('76827 =', (76827).toString(2), `(${(76827).toString(2).length} bits)`, ' 1227079 bits:', (1227079).toString(2).length, ' 27 =', (27).toString(2))
console.log('beta(5) =', (8 - 5 * L23).toFixed(4), ' beta(41) =', (65 - 41 * L23).toFixed(4), ' 243/256 =', (243 / 256).toFixed(4), ' 27/32 =', 27 / 32, ' 9/16 =', 9 / 16)
console.log('2^19 < 3^12 ?', 2 ** 19 < 3 ** 12, ' 2^65 > 3^41 ?', 2n ** 65n > 3n ** 41n, ' 2^84 < 3^53 ?', 2n ** 84n < 3n ** 53n, ' 2^485 > 3^306 ?', 2n ** 485n > 3n ** 306n, ' 2^1054 < 3^665 ?', 2n ** 1054n < 3n ** 665n, ' 2^24727 > 3^15601 ?', 2n ** 24727n > 3n ** 15601n)
{
  // continued fraction of log2 3 and of log6 3
  const cf = (x, n) => { const a = []; for (let i = 0; i < n; i++) { const f = Math.floor(x); a.push(f); x = 1 / (x - f) } return a }
  console.log('cf log2 3:', cf(L23, 10).join(','), '  cf log6 3:', cf(Math.log(3) / Math.log(6), 10).join(','))
}
{
  // depth table
  for (let k = 2; k <= 6; k++) { const M = 2 ** (k + 1); const res = []; for (let m = 1; m < M; m += 2) if (v2(3 * m + 1) === k) res.push(m); console.log(`depth exactly ${k}: m = ${res.join(',')} mod ${M}`) }
}
{
  // Set_3, Set_6 residues
  const st = (n) => { let x = n, k = 0; while (x >= n) { x = x % 2 ? 3 * x + 1 : x / 2; k++ } return k }
  let ok3 = true, ok6 = true
  for (let n = 2; n < 100000; n++) { const k = st(n); if ((k === 3) !== (n % 4 === 1)) ok3 = false; if ((k === 6) !== (n % 16 === 3)) ok6 = false }
  console.log('Set_3 = {n = 1 mod 4} for 2<=n<1e5:', ok3, '  Set_6 = {n = 3 mod 16}:', ok6)
}
