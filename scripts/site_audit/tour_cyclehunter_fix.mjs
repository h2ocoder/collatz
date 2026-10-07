// Tour audit: check a corrected CycleHunter computation (valid words + the true cycle constant),
// and the BounceSimulator rows for m = 2919.
// Valid word for the 3n+1 map, started at an odd value: length K = S + E, S ones, first entry 1,
// no two ones adjacent, last entry 0.  There are C(E-1, S-1) of them.
// Constant: run the word, c <- 3c + 2^e on an odd step, e <- e + 1 on an even step; cycle iff (2^E - 3^S) | c.
function validWords(K, S) {
  const out = []
  const cur = [1]
  ;(function gen(pos, ones) {
    if (pos === K) { if (ones === S && cur[K - 1] === 0) out.push([...cur]); return }
    const remaining = K - pos, need = S - ones
    if (need > 0 && need <= remaining && cur[pos - 1] === 0) { cur.push(1); gen(pos + 1, ones + 1); cur.pop() }
    if (remaining - 1 >= need) { cur.push(0); gen(pos + 1, ones); cur.pop() }
  })(1, 1)
  return out
}
function check(S, E) {
  const g = 2 ** E - 3 ** S
  if (g <= 0) return { S, E, verdict: 'ASCENDING' }
  const words = validWords(S + E, S)
  let zero = 0; const hits = []
  for (const w of words) {
    let c = 0, pow2 = 1 % g, cExact = 0n, p2 = 1n
    for (const b of w) { if (b === 1) { c = (3 * c + pow2) % g; cExact = 3n * cExact + p2 } else { pow2 = (pow2 * 2) % g; p2 *= 2n } }
    if (c === 0) { zero++; hits.push((cExact / BigInt(g)).toString()) }
  }
  return { S, E, gap: g, words: words.length, zero, n: hits }
}
for (const [S, E] of [[1, 2], [2, 4], [3, 6], [4, 8], [5, 8], [3, 5], [2, 3], [4, 7], [5, 9], [5, 10], [6, 10], [7, 12], [8, 13], [9, 15], [10, 16]]) console.log(JSON.stringify(check(S, E)))

// all 91 cyclic words for (5,8) (any starting point): none gives an integer
{
  const K = 13, S = 5, g = 13; let n91 = 0, z = 0
  for (let mask = 0; mask < 1 << K; mask++) {
    const w = []; for (let i = 0; i < K; i++) w.push((mask >> i) & 1)
    if (w.reduce((a, b) => a + b, 0) !== S) continue
    let ok = true; for (let i = 0; i < K; i++) if (w[i] && w[(i + 1) % K]) ok = false
    if (!ok) continue
    n91++
    let c = 0, pow2 = 1
    for (const b of w) { if (b) c = (3 * c + pow2) % g; else pow2 = (pow2 * 2) % g }
    if (c === 0) z++
  }
  console.log('(5,8): cyclic words with no two adjacent odd steps:', n91, ' with gap | c:', z)
}

// BounceSimulator rows for 2919, as the widget computes them (80-row cap)
{
  const v2 = (n) => { let c = 0; while (n % 2 === 0) { n /= 2; c++ } return c }
  for (const start of [2919, 27]) {
    let m = start, rows = 0, b = 0, firstStreak = true, bFirst = 0
    for (let i = 0; i < 80 && m > 1; i++) {
      while (m > 1 && m % 4 === 3) m = (3 * m + 1) / 2
      if (m <= 1) break
      const depth = v2(3 * m + 1)
      const isB = v2(m - 1) === 3 && m % 16 === 9 && ((m - 9) / 16) % 8 === 2
      if (depth >= 3) firstStreak = false
      if (isB) { b++; if (firstStreak) bFirst++ }
      rows++
      m = (3 * m + 1) / 2 ** depth
    }
    const B = Math.ceil(Math.log2(start + 1))
    console.log(`BounceSimulator(${start}): bit budget ${B}, rows ${rows}, rows marked BOUNCE ${b} (before the first deep drop: ${bFirst}); (B+3)/4 = ${(B + 3) / 4}`)
  }
}
