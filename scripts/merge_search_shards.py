"""Merge the JSON outputs of sharded double_halving runs (double_halving <B> <threads> k/K).

Usage:  python scripts/merge_search_shards.py shard0.json shard1.json ... > merged.json
Checks that every shard 0..K-1 is present exactly once and that the merged leaf
count is the Fibonacci number F(B+1).
"""

import json
import sys


def fib(k):
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a


def main(paths):
    shards = [json.load(open(p)) for p in paths]
    bits = {s["bits"] for s in shards}
    assert len(bits) == 1, f"mixed depths: {bits}"
    total = int(shards[0]["shard"].split("/")[1])
    seen = sorted(int(s["shard"].split("/")[0]) for s in shards)
    assert seen == list(range(total)), f"expected shards 0..{total - 1}, got {seen}"
    hist = {}
    for s in shards:
        for k, c in s["histogram"]:
            hist[k] = hist.get(k, 0) + c
    merged = {
        "bits": bits.pop(),
        "shards": total,
        "seconds_max": max(s["seconds"] for s in shards),
        "seconds_sum": sum(s["seconds"] for s in shards),
        "leaves": sum(s["leaves"] for s in shards),
        "best": sorted((b for s in shards for b in s["best"]), key=lambda t: -t[1])[:16],
        "overflow": [n for s in shards for n in s["overflow"]],
        "histogram": sorted(hist.items()),
    }
    assert merged["leaves"] == fib(merged["bits"] + 1), "leaf count is not F(B+1): a shard is wrong or missing"
    json.dump(merged, sys.stdout)


if __name__ == "__main__":
    main(sys.argv[1:])
