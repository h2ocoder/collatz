//! SCRUM-30 H3 follow-up: paired real-vs-lifted continuation for every surviving leaf.
//!
//! For each residue r < 2^B whose first B parities avoid the forbidden factor, run the
//! next K = 14 steps twice from the same automaton state:
//!   real    from x = T^B(r)                       (the digits the orbit makes itself)
//!   lifted  from x + 3^s * j, j pseudo-random     (T^B(r + 2^B j): genuinely fresh digits)
//! Both are tallied in the same bucket, keyed by the bit length of the REAL x. The
//! difference real - lifted per bucket measures non-freshness with the automaton-state
//! mix held fixed, which a plain comparison with lambda/2 cannot do.
//!
//! Trials are counted at levels B+2 .. B+14, the same window as the other analyses.
//! Usage: family_paired <B> <threads> <factor>     prints one JSON object

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;

#[derive(Clone, Copy)]
struct Node { r: u64, x: u128, pow3: u128, hist: u32, depth: u32 }

const BUCKETS: usize = 129;
const WINDOW: u32 = 14;

fn mix(mut z: u64) -> u64 {
    z = z.wrapping_add(0x9E3779B97F4A7C15);
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58476D1CE4E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D049BB133111EB);
    z ^ (z >> 31)
}

fn dead(pat: (u32, u32), hist: u32, depth: u32) -> bool {
    depth >= pat.1 && (hist & ((1u32 << pat.1) - 1)) == pat.0
}

fn children(n: Node, pat: (u32, u32), out: &mut Vec<Node>) {
    for bit in 0..2u64 {
        let r2 = n.r + (bit << n.depth);
        let x2 = n.x + (bit as u128) * n.pow3;
        let odd = (x2 & 1) as u32;
        let hist = (n.hist << 1) | odd;
        if dead(pat, hist, n.depth + 1) { continue; }
        if odd == 1 {
            out.push(Node { r: r2, x: (3 * x2 + 1) >> 1, pow3: n.pow3 * 3, hist, depth: n.depth + 1 });
        } else {
            out.push(Node { r: r2, x: x2 >> 1, pow3: n.pow3, hist, depth: n.depth + 1 });
        }
    }
}

/// Run WINDOW steps from value y with history `hist`; return (trials, successes) at levels B+2..B+14.
fn window(pat: (u32, u32), mut y: u128, mut hist: u32, bits: u32) -> (u64, u64) {
    let (mut trials, mut succ) = (0u64, 0u64);
    for step in bits..bits + WINDOW {
        let odd = (y & 1) as u32;
        hist = (hist << 1) | odd;
        let d = dead(pat, hist, step + 1);
        if step >= bits + 2 { trials += 1; if !d { succ += 1; } }
        if d { break; }
        y = if odd == 1 { (3 * y + 1) >> 1 } else { y >> 1 };
    }
    (trials, succ)
}

#[derive(Default, Clone)]
struct Tally { real_t: Vec<u64>, real_s: Vec<u64>, lift_t: Vec<u64>, lift_s: Vec<u64> }

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let bits: u32 = args[1].parse().unwrap();
    let threads: usize = args[2].parse().unwrap();
    let pat = {
        let mut v = 0u32;
        for ch in args[3].chars() { v = (v << 1) | if ch == '1' { 1 } else { 0 }; }
        (v, args[3].len() as u32)
    };
    let mut frontier = vec![Node { r: 1, x: 2, pow3: 3, hist: 1, depth: 1 }];
    while frontier[0].depth < bits.min(18) {
        let mut next = Vec::new();
        for n in &frontier { children(*n, pat, &mut next); }
        frontier = next;
    }
    let work = Arc::new(frontier);
    let cursor = Arc::new(AtomicUsize::new(0));
    let empty = Tally { real_t: vec![0; BUCKETS], real_s: vec![0; BUCKETS], lift_t: vec![0; BUCKETS], lift_s: vec![0; BUCKETS] };
    let total = Arc::new(Mutex::new(empty.clone()));
    let start = std::time::Instant::now();
    let handles: Vec<_> = (0..threads).map(|_| {
        let (work, cursor, total, mut t) = (work.clone(), cursor.clone(), total.clone(), empty.clone());
        thread::spawn(move || {
            let mut stack = Vec::with_capacity(256);
            loop {
                let i = cursor.fetch_add(1, Ordering::Relaxed);
                if i >= work.len() { break; }
                stack.push(work[i]);
                while let Some(n) = stack.pop() {
                    if n.depth < bits { children(n, pat, &mut stack); continue; }
                    let b = (128 - n.x.leading_zeros()) as usize;
                    let (rt, rs) = window(pat, n.x, n.hist, bits);
                    let j = (mix(n.r) >> 24) as u128 | 1;
                    let (lt, ls) = window(pat, n.x + n.pow3 * j, n.hist, bits);
                    t.real_t[b] += rt; t.real_s[b] += rs; t.lift_t[b] += lt; t.lift_s[b] += ls;
                }
            }
            let mut g = total.lock().unwrap();
            for b in 0..BUCKETS {
                g.real_t[b] += t.real_t[b]; g.real_s[b] += t.real_s[b];
                g.lift_t[b] += t.lift_t[b]; g.lift_s[b] += t.lift_s[b];
            }
        })
    }).collect();
    for h in handles { h.join().unwrap(); }
    let g = total.lock().unwrap();
    let rows: Vec<String> = (0..BUCKETS).filter(|b| g.real_t[*b] + g.lift_t[*b] > 0)
        .map(|b| format!("[{},{},{},{},{}]", b, g.real_s[b], g.real_t[b], g.lift_s[b], g.lift_t[b])).collect();
    println!("{{\"bits\":{},\"factor\":\"{}\",\"seconds\":{:.1},\"rows\":[{}]}}",
        bits, args[3], start.elapsed().as_secs_f64(), rows.join(","));
}
