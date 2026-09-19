//! SCRUM-30 E12 (fast): exhaustive search for positive integers whose Terras
//! parity word avoids two consecutive halvings ("00").
//!
//! Same algorithm as scripts/double_halving_search.py: walk the tree of residues
//! mod 2^j whose first j steps contain no "00" (Fibonacci(j+1) nodes per level),
//! then finish each depth-B leaf by direct iteration. Exhaustive for n < 2^B.
//!
//! Usage: double_halving <B> [threads] [k/K]      prints one JSON object
//! The optional k/K runs shard k of K (for splitting one search across machines);
//! merge the outputs with scripts/merge_search_shards.py.

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;

#[derive(Clone, Copy)]
struct Node {
    r: u64,
    x: u128,
    pow3: u128,
    halved: bool,
    depth: u32,
}

const HIST: usize = 1024;
const LIMIT: u128 = 1u128 << 125;

struct Tally {
    leaves: u64,
    hist: Vec<u64>,
    best: Vec<(u64, u32)>, // top survivors (n, steps)
    overflow: Vec<u64>,
}

impl Tally {
    fn new() -> Self {
        Tally { leaves: 0, hist: vec![0; HIST], best: Vec::new(), overflow: Vec::new() }
    }
    fn record(&mut self, n: u64, steps: u32) {
        self.hist[(steps as usize).min(HIST - 1)] += 1;
        if self.best.len() < 16 || steps > self.best.last().unwrap().1 {
            self.best.push((n, steps));
            self.best.sort_by(|a, b| b.1.cmp(&a.1));
            self.best.truncate(16);
        }
    }
}

#[inline(always)]
fn children(n: Node, out: &mut Vec<Node>) {
    for bit in 0..2u64 {
        let r2 = n.r + (bit << n.depth);
        let x2 = n.x + (bit as u128) * n.pow3;
        if x2 & 1 == 0 {
            if !n.halved {
                out.push(Node { r: r2, x: x2 >> 1, pow3: n.pow3, halved: true, depth: n.depth + 1 });
            }
        } else {
            out.push(Node { r: r2, x: (3 * x2 + 1) >> 1, pow3: n.pow3 * 3, halved: false, depth: n.depth + 1 });
        }
    }
}

fn finish(leaf: Node, t: &mut Tally) {
    t.leaves += 1;
    if leaf.r == 1 {
        return;
    }
    let (mut y, mut h, mut steps) = (leaf.x, leaf.halved, leaf.depth);
    loop {
        if y & 1 == 0 {
            if h {
                break;
            }
            y >>= 1;
            h = true;
        } else {
            if y > LIMIT {
                t.overflow.push(leaf.r);
                return;
            }
            y = (3 * y + 1) >> 1;
            h = false;
        }
        steps += 1;
    }
    t.record(leaf.r, steps);
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let bits: u32 = args.get(1).and_then(|s| s.parse().ok()).unwrap_or(40);
    let threads: usize = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(32);
    assert!(bits >= 2 && bits <= 63);
    let split = bits.min(20);

    // breadth-first to the split depth: these are the work items
    let mut frontier = vec![Node { r: 1, x: 2, pow3: 3, halved: false, depth: 1 }];
    while frontier[0].depth < split {
        let mut next = Vec::with_capacity(frontier.len() * 2);
        for n in &frontier {
            children(*n, &mut next);
        }
        frontier = next;
    }
    // optional sharding for multi-machine runs: "k/K" keeps work items with index % K == k
    let (shard, shards): (usize, usize) = args.get(3).map(|s| {
        let mut it = s.split('/');
        (it.next().unwrap().parse().unwrap(), it.next().unwrap().parse().unwrap())
    }).unwrap_or((0, 1));
    let frontier: Vec<Node> = frontier.into_iter().enumerate()
        .filter(|(i, _)| i % shards == shard).map(|(_, n)| n).collect();
    let work = Arc::new(frontier);
    let cursor = Arc::new(AtomicUsize::new(0));
    let total = Arc::new(Mutex::new(Tally::new()));
    let start = std::time::Instant::now();

    let handles: Vec<_> = (0..threads)
        .map(|_| {
            let (work, cursor, total) = (work.clone(), cursor.clone(), total.clone());
            thread::spawn(move || {
                let mut t = Tally::new();
                let mut stack: Vec<Node> = Vec::with_capacity(256);
                loop {
                    let i = cursor.fetch_add(1, Ordering::Relaxed);
                    if i >= work.len() {
                        break;
                    }
                    stack.push(work[i]);
                    while let Some(n) = stack.pop() {
                        if n.depth == bits {
                            finish(n, &mut t);
                        } else {
                            children(n, &mut stack);
                        }
                    }
                }
                let mut g = total.lock().unwrap();
                g.leaves += t.leaves;
                for (a, b) in g.hist.iter_mut().zip(t.hist.iter()) {
                    *a += b;
                }
                for (n, s) in t.best {
                    g.record_best(n, s);
                }
                g.overflow.extend(t.overflow);
            })
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }

    let g = total.lock().unwrap();
    let hist: Vec<String> = g.hist.iter().enumerate().filter(|(_, c)| **c > 0)
        .map(|(k, c)| format!("[{},{}]", k, c)).collect();
    let best: Vec<String> = g.best.iter().map(|(n, s)| format!("[{},{}]", n, s)).collect();
    let over: Vec<String> = g.overflow.iter().map(|n| n.to_string()).collect();
    println!(
        "{{\"bits\":{},\"shard\":\"{}/{}\",\"threads\":{},\"seconds\":{:.1},\"leaves\":{},\"best\":[{}],\"overflow\":[{}],\"histogram\":[{}]}}",
        bits, shard, shards, threads, start.elapsed().as_secs_f64(), g.leaves, best.join(","), over.join(","), hist.join(",")
    );
}

impl Tally {
    fn record_best(&mut self, n: u64, steps: u32) {
        self.best.push((n, steps));
        self.best.sort_by(|a, b| b.1.cmp(&a.1));
        self.best.truncate(16);
    }
}
