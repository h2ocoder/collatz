//! SCRUM-30 H3: survival of positive integers inside a forbidden-factor family.
//!
//! Generalises main.rs: instead of the single forbidden factor "00", take any list
//! of forbidden factors over the Terras parity alphabet (1 = odd step, 0 = halving).
//! Walk the tree of residues mod 2^j whose parity word avoids every factor, to depth
//! B, then finish each leaf by direct iteration until a forbidden factor appears.
//! An orbit that reaches 1 and is still alive 40 steps later is counted as absorbed
//! (the word of the trivial cycle, 1010..., is allowed in that family).
//!
//! Usage: family <B> <threads> <factor> [<factor> ...]     e.g.  family 40 32 000

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;

#[derive(Clone, Copy)]
struct Node { r: u64, x: u128, pow3: u128, hist: u32, depth: u32 }

const HIST: usize = 2048;
const LIMIT: u128 = 1u128 << 125;

#[derive(Clone)]
struct Family { pats: Vec<(u32, u32)> } // (bits, length), most recent symbol in bit 0

impl Family {
    /// True if the word whose most recent `depth` symbols are in `hist` now ends in a forbidden factor.
    #[inline(always)]
    fn dead(&self, hist: u32, depth: u32) -> bool {
        for &(bits, len) in &self.pats {
            if depth >= len && (hist & ((1u32 << len) - 1)) == bits { return true; }
        }
        false
    }
}

#[inline(always)]
fn children(n: Node, fam: &Family, out: &mut Vec<Node>) {
    for bit in 0..2u64 {
        let r2 = n.r + (bit << n.depth);
        let x2 = n.x + (bit as u128) * n.pow3;
        let odd = (x2 & 1) as u32;
        let hist = (n.hist << 1) | odd;
        if fam.dead(hist, n.depth + 1) { continue; }
        if odd == 1 {
            out.push(Node { r: r2, x: (3 * x2 + 1) >> 1, pow3: n.pow3 * 3, hist, depth: n.depth + 1 });
        } else {
            out.push(Node { r: r2, x: x2 >> 1, pow3: n.pow3, hist, depth: n.depth + 1 });
        }
    }
}

struct Tally { leaves: u64, absorbed: u64, overflow: u64, hist: Vec<u64>, best: Vec<(u64, u32)>,
               trials: Vec<u64>, succ: Vec<u64> }

/// Survival trials at levels B+2 .. B+14 are tallied by the bit length of the starting number.
const LEN_BUCKETS: usize = 65;

/// splitmix64: a deterministic pseudo-random lift for the FAMILY_LIFT control
fn mix(mut z: u64) -> u64 {
    z = z.wrapping_add(0x9E3779B97F4A7C15);
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58476D1CE4E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D049BB133111EB);
    z ^ (z >> 31)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let bits: u32 = args[1].parse().unwrap();
    let threads: usize = args[2].parse().unwrap();
    let pats: Vec<(u32, u32)> = args[3..].iter().map(|s| {
        // the string is written oldest symbol first; store with most recent symbol in bit 0
        let mut v = 0u32;
        for ch in s.chars() { v = (v << 1) | if ch == '1' { 1 } else { 0 }; }
        (v, s.len() as u32)
    }).collect();
    let fam = Family { pats };
    let lift = std::env::var("FAMILY_LIFT").map(|v| v == "1").unwrap_or(false);
    // FAMILY_BUCKET=value tallies by the bit length of T^B(n) instead of n
    let by_value = std::env::var("FAMILY_BUCKET").map(|v| v == "value").unwrap_or(false);
    let split = bits.min(18);

    // odd starting numbers only: the first symbol is 1
    let mut frontier = vec![Node { r: 1, x: 2, pow3: 3, hist: 1, depth: 1 }];
    while !frontier.is_empty() && frontier[0].depth < split {
        let mut next = Vec::with_capacity(frontier.len() * 2);
        for n in &frontier { children(*n, &fam, &mut next); }
        frontier = next;
    }
    // optional sharding via env FAMILY_SHARD="k/K": keep work items with index % K == k
    let (shard, shards): (usize, usize) = std::env::var("FAMILY_SHARD").ok().map(|s| {
        let mut it = s.split('/');
        (it.next().unwrap().parse().unwrap(), it.next().unwrap().parse().unwrap())
    }).unwrap_or((0, 1));
    let frontier: Vec<Node> = frontier.into_iter().enumerate()
        .filter(|(i, _)| i % shards == shard).map(|(_, n)| n).collect();
    let work = Arc::new(frontier);
    let cursor = Arc::new(AtomicUsize::new(0));
    let total = Arc::new(Mutex::new(Tally { leaves: 0, absorbed: 0, overflow: 0, hist: vec![0; HIST], best: vec![], trials: vec![0; LEN_BUCKETS], succ: vec![0; LEN_BUCKETS] }));
    let start = std::time::Instant::now();

    let handles: Vec<_> = (0..threads).map(|_| {
        let (work, cursor, total, fam) = (work.clone(), cursor.clone(), total.clone(), fam.clone());
        let (lift, by_value) = (lift, by_value);
        thread::spawn(move || {
            let mut t = Tally { leaves: 0, absorbed: 0, overflow: 0, hist: vec![0; HIST], best: vec![], trials: vec![0; LEN_BUCKETS], succ: vec![0; LEN_BUCKETS] };
            let mut stack: Vec<Node> = Vec::with_capacity(256);
            loop {
                let i = cursor.fetch_add(1, Ordering::Relaxed);
                if i >= work.len() { break; }
                stack.push(work[i]);
                while let Some(n) = stack.pop() {
                    if n.depth < bits { children(n, &fam, &mut stack); continue; }
                    t.leaves += 1;
                    let mut y = n.x;
                    if lift {
                        // T^B(r + 2^B j) = T^B(r) + 3^s j : first B parities unchanged, later ones fresh
                        let j = (mix(n.r) >> 24) as u128 | 1;
                        y = n.x + n.pow3 * j;
                    }
                    let y_leaf = y;   // the value after B steps
                    let (mut hist, mut steps) = (n.hist, n.depth);
                    let mut since_one: u32 = if n.r == 1 && !lift { 1 } else { 0 };
                    let mut outcome = 0u8; // 0 died, 1 absorbed, 2 overflow
                    loop {
                        if y == 1 && since_one == 0 { since_one = 1; }
                        if since_one > 0 { since_one += 1; if since_one > 40 { outcome = 1; break; } }
                        let odd = (y & 1) as u32;
                        hist = (hist << 1) | odd;
                        let dead = fam.dead(hist, steps + 1);
                        // trials at levels B+2 .. B+14, by bit length of the starting number
                        if steps >= bits + 2 && steps < bits + 15 {
                            let b = if by_value { (128 - y_leaf.leading_zeros()).min(64) as usize }
                                    else { (64 - n.r.leading_zeros()) as usize };
                            t.trials[b] += 1;
                            if !dead { t.succ[b] += 1; }
                        }
                        if dead { break; }
                        if odd == 1 {
                            if y > LIMIT { outcome = 2; break; }
                            y = (3 * y + 1) >> 1;
                        } else { y >>= 1; }
                        steps += 1;
                    }
                    match outcome {
                        1 => t.absorbed += 1,
                        2 => t.overflow += 1,
                        _ => {
                            t.hist[(steps as usize).min(HIST - 1)] += 1;
                            if t.best.len() < 8 || steps > t.best.last().unwrap().1 {
                                t.best.push((n.r, steps));
                                t.best.sort_by(|a, b| b.1.cmp(&a.1));
                                t.best.truncate(8);
                            }
                        }
                    }
                }
            }
            let mut g = total.lock().unwrap();
            g.leaves += t.leaves; g.absorbed += t.absorbed; g.overflow += t.overflow;
            for b in 0..LEN_BUCKETS { g.trials[b] += t.trials[b]; g.succ[b] += t.succ[b]; }
            for (a, b) in g.hist.iter_mut().zip(t.hist.iter()) { *a += b; }
            g.best.extend(t.best);
            g.best.sort_by(|a, b| b.1.cmp(&a.1));
            g.best.truncate(8);
        })
    }).collect();
    for h in handles { h.join().unwrap(); }

    let g = total.lock().unwrap();
    let hist: Vec<String> = g.hist.iter().enumerate().filter(|(_, c)| **c > 0).map(|(k, c)| format!("[{},{}]", k, c)).collect();
    let by_len: Vec<String> = (0..LEN_BUCKETS).filter(|b| g.trials[*b] > 0)
        .map(|b| format!("[{},{},{}]", b, g.succ[b], g.trials[b])).collect();
    let best: Vec<String> = g.best.iter().map(|(n, s)| format!("[{},{}]", n, s)).collect();
    println!("{{\"bits\":{},\"factors\":{:?},\"seconds\":{:.1},\"leaves\":{},\"absorbed\":{},\"overflow\":{},\"lift\":{},\"bucket\":\"{}\",\"by_len\":[{}],\"best\":[{}],\"histogram\":[{}]}}",
        bits, &args[3..], start.elapsed().as_secs_f64(), g.leaves, g.absorbed, g.overflow, lift, if by_value { "value" } else { "start" }, by_len.join(","), best.join(","), hist.join(","));
}
