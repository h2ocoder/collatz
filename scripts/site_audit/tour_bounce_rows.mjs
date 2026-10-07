// Tour audit: print the Set_3 visits the BounceSimulator lists, with v2(m-1), for the page's examples.
const v2 = (n) => { let c = 0; while (n % 2 === 0) { n /= 2; c++ } return c }
function rows(start, cap = 200) {
  let m = start; if (m % 2 === 0) m++
  const out = []
  for (let i = 0; i < cap && m > 1; i++) {
    let climb = 0
    while (m > 1 && m % 4 === 3) { m = (3 * m + 1) / 2; climb++ }
    if (m <= 1) break
    const V = v2(m - 1), depth = v2(3 * m + 1)
    const k8 = m % 16 === 9 ? ((m - 9) / 16) % 8 : -1
    const isBounce = V === 3 && k8 === 2
    out.push({ m, climb, V, depth, k8, isBounce, bits: m.toString(2).length })
    let nx = 3 * m + 1; while (nx % 2 === 0) nx /= 2
    m = nx
  }
  return out
}
for (const n of [76827, 1227079, 27]) {
  const r = rows(n)
  console.log(`\nstart ${n} (${n.toString(2).length} bits): ${r.length} Set_3 visits before reaching 1`)
  console.log(r.slice(0, 30).map((x, i) => `${i}:${x.isBounce ? 'B' : x.depth >= 4 ? 'S' : x.depth >= 3 ? 'm' : 'w'}[climb${x.climb},V${x.V},d${x.depth},k8=${x.k8},${x.bits}b]`).join('\n'))
  console.log('total rows flagged BOUNCE in whole orbit:', r.filter(x => x.isBounce).length,
    '| V=3 visits:', r.filter(x => x.V === 3).length,
    '| leading run of visits before first depth>=3:', r.findIndex(x => x.depth >= 3))
}
