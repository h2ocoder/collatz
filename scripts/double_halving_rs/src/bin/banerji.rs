//! SCRUM-30 E14 (fast): Banerji's backward conjecture, exhaustive for odd n < 2*3^t.
//! Same algorithm as scripts/banerji_backward_search.py.  Usage: banerji <t> [threads]

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;

#[derive(Clone, Copy)]
struct Node { r: u128, x: u128, mult: u128, level: u32 }

const HIST: usize = 512;

fn children(n: Node, pow3: &[u128], out: &mut Vec<Node>) {
    let modulus = 2 * pow3[n.level as usize];
    for d in 0..3u128 {
        let (r2, x2) = (n.r + modulus * d, n.x + n.mult * d);
        match x2 % 3 {
            2 => out.push(Node { r: r2, x: (2 * x2 - 1) / 3, mult: n.mult * 2, level: n.level + 1 }),
            1 => out.push(Node { r: r2, x: (4 * x2 - 1) / 3, mult: n.mult * 4, level: n.level + 1 }),
            _ => {}
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let depth: u32 = args.get(1).and_then(|s| s.parse().ok()).unwrap_or(22);
    let threads: usize = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(32);
    assert!(depth <= 38, "x*4 must stay below 2^127");
    let pow3: Arc<Vec<u128>> = Arc::new((0..=depth).map(|i| 3u128.pow(i)).collect());
    let split = depth.min(14);

    let mut frontier = vec![Node { r: 1, x: 1, mult: 2, level: 0 }];
    while frontier[0].level < split {
        let mut next = Vec::new();
        for n in &frontier { children(*n, &pow3, &mut next); }
        frontier = next;
    }
    let work = Arc::new(frontier);
    let cursor = Arc::new(AtomicUsize::new(0));
    // (leaves, histogram, best list, overflow list)
    let total = Arc::new(Mutex::new((0u64, vec![0u64; HIST], Vec::<(u128, u32)>::new(), Vec::<u128>::new())));
    let start = std::time::Instant::now();

    let handles: Vec<_> = (0..threads).map(|_| {
        let (work, cursor, total, pow3) = (work.clone(), cursor.clone(), total.clone(), pow3.clone());
        thread::spawn(move || {
            let (mut leaves, mut hist, mut best, mut over) = (0u64, vec![0u64; HIST], Vec::<(u128, u32)>::new(), Vec::<u128>::new());
            let mut stack: Vec<Node> = Vec::with_capacity(256);
            loop {
                let i = cursor.fetch_add(1, Ordering::Relaxed);
                if i >= work.len() { break; }
                stack.push(work[i]);
                while let Some(n) = stack.pop() {
                    if n.level < depth { children(n, &pow3, &mut stack); continue; }
                    leaves += 1;
                    if n.r == 1 { continue; }
                    let (mut y, mut steps, mut ok) = (n.x, n.level, true);
                    while y % 3 != 0 {
                        if y == 1 || y > (1u128 << 124) { ok = false; break; }
                        y = if y % 3 == 2 { (2 * y - 1) / 3 } else { (4 * y - 1) / 3 };
                        steps += 1;
                    }
                    if !ok { over.push(n.r); continue; }
                    hist[(steps as usize).min(HIST - 1)] += 1;
                    if best.len() < 12 || steps > best.last().unwrap().1 {
                        best.push((n.r, steps));
                        best.sort_by(|a, b| b.1.cmp(&a.1));
                        best.truncate(12);
                    }
                }
            }
            let mut g = total.lock().unwrap();
            g.0 += leaves;
            for (a, b) in g.1.iter_mut().zip(hist.iter()) { *a += b; }
            g.2.extend(best);
            g.2.sort_by(|a, b| b.1.cmp(&a.1));
            g.2.truncate(12);
            g.3.extend(over);
        })
    }).collect();
    for h in handles { h.join().unwrap(); }

    let g = total.lock().unwrap();
    let hist: Vec<String> = g.1.iter().enumerate().filter(|(_, c)| **c > 0).map(|(k, c)| format!("[{},{}]", k, c)).collect();
    let best: Vec<String> = g.2.iter().map(|(n, s)| format!("[\"{}\",{}]", n, s)).collect();
    let over: Vec<String> = g.3.iter().map(|n| format!("\"{}\"", n)).collect();
    println!("{{\"depth\":{},\"seconds\":{:.1},\"leaves\":{},\"best\":[{}],\"stuck_or_overflow\":[{}],\"histogram\":[{}]}}",
        depth, start.elapsed().as_secs_f64(), g.0, best.join(","), over.join(","), hist.join(","));
}
