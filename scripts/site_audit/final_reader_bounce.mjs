// (B+3)/4 bound on bounces (m = 41 mod 128 visits to Set3) before the first deep drop, odd starts up to 5e6. BigInt-free: values stay < 2^53?
let worstRatio = 0, viol = 0, maxVal = 0, checked = 0;
for (let n = 3; n <= 5000000; n += 2) {
  let m = n, bounces = 0, guard = 0;
  const B = Math.floor(Math.log2(n)) + 1;
  while (true) {
    while (m % 4 === 3) m = (3 * m + 1) / 2;
    if (m > maxVal) maxVal = m;
    if (m === 1) break;
    let t = 3 * m + 1, d = 0; while (t % 2 === 0) { t /= 2; d++; }
    if (d >= 3) break;
    if (m % 128 === 41) bounces++;
    m = t;
    if (++guard > 100000) { console.log('guard', n); break; }
  }
  checked++;
  if (bounces > (B + 3) / 4) { viol++; if (viol < 5) console.log('violation', n, bounces, B); }
  const r = bounces / ((B + 3) / 4); if (r > worstRatio) worstRatio = r;
}
console.log(`checked ${checked} odd starts; violations ${viol}; max bounces/((B+3)/4) = ${worstRatio.toFixed(3)}; max value seen ${maxVal} (2^53 = ${2**53})`);
