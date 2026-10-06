"""Reviewer check (lens: honesty): Theorem 2' on site/explore/thirty-six.md says 'dropping sets',
the thread README (figurate_2adic, row T2') says 'dropping classes'.

For the rule n -> n/2 (n even), (q n + d)/2 (n odd) with q = 3, d = 1 mod 4 the README criterion
holds, so the squares meet exactly two CLASSES.  Count the distinct ACTUAL stopping times of the
squares n^2, 2 <= n <= 2000, for a few such d.

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 honesty_theorem2prime_sets_vs_classes.py
"""
from __future__ import annotations


def stop(n: int, q: int, d: int, cap: int = 10000):
    x, k = n, 0
    while k < cap:
        x = (q * x + d) // 2 if x & 1 else x // 2
        k += 1
        if x < n:
            return k
    return None


for q, d in ((3, 1), (3, 5), (3, 37), (3, 101), (7, 1), (7, 9), (5, 3)):
    crit = (q == 3 and d % 4 == 1) or (q in (5, 7) and (q + d) % 8 == 0)
    times: dict = {}
    for n in range(2, 2001):
        t = stop(n * n, q, d)
        times.setdefault(t, []).append(n * n)
    summary = ", ".join(f"k={t}: {len(v)} squares (first {v[0]})" for t, v in sorted(times.items(), key=lambda kv: (kv[0] is None, kv[0])))
    print(f"rule ({q}n{d:+d})/2  criterion {'holds' if crit else 'fails'}: {len(times)} distinct actual stopping times -> {summary[:230]}")
