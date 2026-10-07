// Tour audit: the base-6 circle.  How far does a real orbit drift from the exact rotation by log6(3),
// counting every Collatz step?  And is there a 44-step near-return in Collatz steps / in Syracuse steps?
const L6 = Math.log(6), A = Math.log(3) / L6
const frac = (x) => x - Math.floor(x)
const circ = (a, b) => { const d = Math.abs(frac(a) - frac(b)); return Math.min(d, 1 - d) }
let worst = 0, worstN = 0, sumTot = 0, cnt = 0
for (let n = 3; n <= 99999; n++) {
  let x = n, k = 0, W = 0
  while (x !== 1) { if (x % 2) { W += Math.log(1 + 1 / (3 * x)) / L6; x = 3 * x + 1 } else x = x / 2; k++ }
  sumTot += W; cnt++
  if (W > worst) { worst = W; worstN = n }
}
console.log(`3 <= n <= 99999: total drift from the exact rotation when the orbit reaches 1: max ${worst.toFixed(4)} of a turn (n = ${worstN}), mean ${(sumTot / cnt).toFixed(4)}`)

// near-return after q steps: mean circular distance between step k and step k+q
function meanReturn(seq, q) { let s = 0, c = 0; for (let k = 0; k + q < seq.length; k++) { s += circ(Math.log(seq[k]) / L6, Math.log(seq[k + q]) / L6); c++ } return c ? s / c : NaN }
for (const n of [77031, 97, 27, 6171]) {
  const full = [n], odd = [n]
  let x = n
  while (x !== 1) { x = x % 2 ? 3 * x + 1 : x / 2; full.push(x); if (x % 2) odd.push(x) }
  console.log(`n=${n}: ${full.length} points counting every step, ${odd.length} odd values`)
  console.log('   every step:  mean distance after q steps  ' + [13, 31, 44, 75, 106].map(q => `q=${q}: ${meanReturn(full, q).toFixed(3)}`).join('  '))
  console.log('   odd values:  mean distance after q steps  ' + [13, 31, 44, 75, 106].map(q => `q=${q}: ${meanReturn(odd, q).toFixed(3)}`).join('  '))
}
console.log('exact rotation: 44*alpha mod 1 =', frac(44 * A).toFixed(4), '(short of a full turn by', (1 - frac(44 * A)).toFixed(4) + ')', ' 31*alpha mod 1 =', frac(31 * A).toFixed(4))
// 3x-1 rotates the same way
{
  const x = 7; const y = 3 * x - 1
  console.log('3x-1 at x=7: advance', frac(Math.log(y) / L6 - Math.log(x) / L6).toFixed(4), ' vs log6(3) =', A.toFixed(4))
}
// Shakibaei Asli's coordinate {log6(x + 1/5)}: per-step error bound 0.2749
{
  let mx = 0
  for (let x = 1; x <= 200000; x++) { const y = x % 2 ? 3 * x + 1 : x / 2; let e = frac(Math.log(y + 0.2) / L6 - Math.log(x + 0.2) / L6 - A); if (e > 0.5) e -= 1; if (Math.abs(e) > mx) mx = Math.abs(e) }
  console.log('max |error| per step with T(x) = {log6(x+1/5)}, x <= 2e5:', mx.toFixed(4))
}
