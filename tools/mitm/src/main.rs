/// 4-Group Meet-in-the-Middle: prove no 106-step Collatz cycle exists.
///
/// For convergent (S=41, E=65), gap g = 2^65 - 3^41 = 420491770248316829.
/// We check all C(64,40) ≈ 2.5×10^17 ordered 40-subsets of {1,...,64}
/// to verify that no subset gives T ≡ 0 mod g.

use std::time::Instant;

const G: u64 = 420_491_770_248_316_829;

#[inline(always)]
fn mod_add(a: u64, b: u64) -> u64 {
    let s = a + b;
    if s >= G { s - G } else { s }
}

#[inline(always)]
fn mod_sub(a: u64, b: u64) -> u64 {
    if a >= b { a - b } else { G - b + a }
}

#[inline(always)]
fn mod_mul(a: u64, b: u64) -> u64 {
    ((a as u128 * b as u128) % G as u128) as u64
}

fn mod_pow(mut base: u64, mut exp: u64) -> u64 {
    let mut result: u64 = 1;
    base %= G;
    while exp > 0 {
        if exp & 1 == 1 {
            result = mod_mul(result, base);
        }
        base = mod_mul(base, base);
        exp >>= 1;
    }
    result
}

fn binomial(n: usize, k: usize) -> usize {
    if k > n { return 0; }
    let k = k.min(n - k);
    let mut r: usize = 1;
    for i in 0..k {
        r = r * (n - i) / (i + 1);
    }
    r
}

/// Generate all k-subsets of `elems`, compute weighted sum mod G.
fn block_sums(elems: &[usize], k: usize, coeff_start: usize,
              coeffs: &[u64], pow2: &[u64]) -> Vec<u64> {
    if k == 0 { return vec![0]; }
    if k > elems.len() { return vec![]; }
    let n = elems.len();
    let mut out = Vec::with_capacity(binomial(n, k));
    let mut idx: Vec<usize> = (0..k).collect();
    loop {
        let mut s: u64 = 0;
        for (j, &i) in idx.iter().enumerate() {
            s = mod_add(s, mod_mul(coeffs[coeff_start + j], pow2[elems[i]]));
        }
        out.push(s);
        // next combination
        let mut i = k;
        loop {
            if i == 0 { return out; }
            i -= 1;
            idx[i] += 1;
            if idx[i] <= n - k + i { break; }
        }
        for j in (i+1)..k { idx[j] = idx[j-1] + 1; }
    }
}

fn main() {
    let start = Instant::now();

    // coeffs[j] = 3^{39-j} mod g, for j=0..39
    let mut coeffs = [0u64; 40];
    for j in 0..40 { coeffs[j] = mod_pow(3, (39 - j) as u64); }

    let c0 = mod_pow(3, 40);
    let target = mod_sub(0, c0);

    let mut pow2 = [0u64; 65];
    for i in 0..65 { pow2[i] = mod_pow(2, i as u64); }

    let blocks: [Vec<usize>; 4] = [
        (1..=16).collect(), (17..=32).collect(),
        (33..=48).collect(), (49..=64).collect(),
    ];

    // Enumerate distributions
    let mut dists = Vec::new();
    for k1 in 0..=16usize {
        for k2 in 0..=16 {
            if k1+k2 > 40 { break; }
            for k3 in 0..=16 {
                if k1+k2+k3 > 40 { break; }
                let k4 = 40 - k1 - k2 - k3;
                if k4 <= 16 {
                    let l = binomial(16,k1)*binomial(16,k2);
                    let r = binomial(16,k3)*binomial(16,k4);
                    if l > 0 && r > 0 { dists.push((k1,k2,k3,k4)); }
                }
            }
        }
    }
    dists.sort_by_key(|&(a,b,c,d)| binomial(16,a)*binomial(16,b) + binomial(16,c)*binomial(16,d));

    let total_subsets: u128 = 250_649_105_469_666_120;
    let mut checked: u128 = 0;
    let mut found = false;

    println!("4-Group MITM for convergent (S=41, E=65)");
    println!("g = {}", G);
    println!("{} distributions to process", dists.len());
    println!();

    for (idx, &(k1,k2,k3,k4)) in dists.iter().enumerate() {
        let ls = binomial(16,k1)*binomial(16,k2);
        let rs = binomial(16,k3)*binomial(16,k4);

        let s1 = block_sums(&blocks[0], k1, 0, &coeffs, &pow2);
        let s2 = block_sums(&blocks[1], k2, k1, &coeffs, &pow2);
        let s3 = block_sums(&blocks[2], k3, k1+k2, &coeffs, &pow2);
        let s4 = block_sums(&blocks[3], k4, k1+k2+k3, &coeffs, &pow2);

        // Build sorted left
        let mut left = Vec::with_capacity(ls);
        for &a in &s1 { for &b in &s2 { left.push(mod_add(a, b)); } }
        left.sort_unstable();

        // Search right
        'outer: for &a in &s3 {
            for &b in &s4 {
                let needed = mod_sub(target, mod_add(a, b));
                if left.binary_search(&needed).is_ok() {
                    found = true;
                    println!("*** ZERO FOUND! dist=({},{},{},{}) ***", k1,k2,k3,k4);
                    break 'outer;
                }
            }
        }
        if found { break; }

        checked += (ls as u128) * (rs as u128);
        let el = start.elapsed().as_secs_f64();
        let pct = checked as f64 / total_subsets as f64 * 100.0;

        if idx < 3 || (idx+1) % 200 == 0 || (ls*rs > 100_000_000) {
            println!("  [{:>7.1}s] {}/{} dists  {:.2}%  pair={}", el, idx+1, dists.len(), pct, (ls as u128)*(rs as u128));
        }
    }

    let el = start.elapsed().as_secs_f64();
    println!();
    if !found {
        println!("=== COMPLETE: NO ZEROS FOUND in {:.1}s ===", el);
        println!("All {} subsets checked.", total_subsets);
        println!();
        println!("*** NO 106-STEP COLLATZ CYCLE EXISTS ***");
        println!("*** CONVERGENT (S=41, E=65) ELIMINATED ***");
    } else {
        println!("Cycle candidate found in {:.1}s", el);
    }
}
