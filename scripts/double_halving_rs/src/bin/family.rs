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

struct Tally { leaves: u64, absorbed: u64, overflow: u64, hist: Vec<u64>, best: Vec<(u64, u32)> }

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
    let split = bits.min(18);

    // odd starting numbers only: the first symbol is 1
    let mut frontier = vec![Node { r: 1, x: 2, pow3: 3, hist: 1, depth: 1 }];
    while !frontier.is_empty() && frontier[0].depth < split {
        let mut next = Vec::with_capacity(frontier.len() * 2);
        for n in &frontier { children(*n, &fam, &mut next); }
        frontier = next;
    }
    let work = Arc::new(frontier);
    let cursor = Arc::new(AtomicUsize::new(0));
    let total = Arc::new(Mutex::new(Tally { leaves: 0, absorbed: 0, overflow: 0, hist: vec![0; HIST], best: vec![] }));
    let start = std::time::Instant::now();

    let handles: Vec<_> = (0..threads).map(|_| {
        let (work, cursor, total, fam) = (work.clone(), cursor.clone(), total.clone(), fam.clone());
        thread::spawn(move || {
            let mut t = Tally { leaves: 0, absorbed: 0, overflow: 0, hist: vec![0; HIST], best: vec![] };
            let mut stack: Vec<Node> = Vec::with_capacity(256);
            loop {
                let i = cursor.fetch_add(1, Ordering::Relaxed);
                if i >= work.len() { break; }
                stack.push(work[i]);
                while let Some(n) = stack.pop() {
                    if n.depth < bits { children(n, &fam, &mut stack); continue; }
                    t.leaves += 1;
                    let (mut y, mut hist, mut steps) = (n.x, n.hist, n.depth);
                    let mut since_one: u32 = if n.r == 1 { 1 } else { 0 };
                    let mut outcome = 0u8; // 0 died, 1 absorbed, 2 overflow
                    loop {
                        if y == 1 && since_one == 0 { since_one = 1; }
                        if since_one > 0 { since_one += 1; if since_one > 40 { outcome = 1; break; } }
                        let odd = (y & 1) as u32;
                        hist = (hist << 1) | odd;
                        if fam.dead(hist, steps + 1) { break; }
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
            for (a, b) in g.hist.iter_mut().zip(t.hist.iter()) { *a += b; }
            g.best.extend(t.best);
            g.best.sort_by(|a, b| b.1.cmp(&a.1));
            g.best.truncate(8);
        })
    }).collect();
    for h in handles { h.join().unwrap(); }

    let g = total.lock().unwrap();
    let hist: Vec<String> = g.hist.iter().enumerate().filter(|(_, c)| **c > 0).map(|(k, c)| format!("[{},{}]", k, c)).collect();
    let best: Vec<String> = g.best.iter().map(|(n, s)| format!("[{},{}]", n, s)).collect();
    println!("{{\"bits\":{},\"factors\":{:?},\"seconds\":{:.1},\"leaves\":{},\"absorbed\":{},\"overflow\":{},\"best\":[{}],\"histogram\":[{}]}}",
        bits, &args[3..], start.elapsed().as_secs_f64(), g.leaves, g.absorbed, g.overflow, best.join(","), hist.join(","));
}
