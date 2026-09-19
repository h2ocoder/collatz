"""L7 analysis: stratify one-step model accuracy by v2(3n+1) and classify the wrong answers.

Runs on CPU against the checkpoints written by base_polarity.py, so it can be used while the
sweep is still on the GPU.  Usage:
  CUDA_VISIBLE_DEVICES= .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/stratify_by_valuation.py [bases]
Writes results/stratify_by_valuation.json
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base_polarity as bp  # noqa: E402

bp.DEV = "cpu"
HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"


def analyse(base, task_name="one"):
    ck = torch.load(RESULTS / "checkpoints" / f"{task_name}_b{base}.pt", map_location="cpu")
    task = bp.Task(task_name, base)
    model = bp.TF(task.V, task.T, d=ck["d"], L=ck["L"])
    model.load_state_dict(ck["state"])
    model.eval()
    ns = bp.sample_odd(np.random.default_rng(12345), 4096)
    toks, meta = task.batch(ns)
    Lp = task.Lin + 1
    seq = toks[:, :Lp].clone()
    with torch.no_grad():
        for _ in range(task.Lout + 1):
            seq = torch.cat([seq, model(seq)[:, -1].argmax(-1, keepdim=True)], 1)
    out, tgt = seq[:, Lp:].numpy(), toks[:, Lp:].numpy()

    def decode(row):
        val = 0
        for i, d in enumerate(row):
            if d >= base:
                break
            val += int(d) * base**i
        return val

    by = defaultdict(lambda: [0, 0])
    what = Counter()
    for n, o, t in zip(ns, out, tgt):
        n = int(n)
        v = bp.v2(3 * n + 1)
        ok = bool((o == t).all())
        by[v][0] += ok
        by[v][1] += 1
        if not ok:
            pred, m = decode(o), 3 * n + 1
            if pred == m // 2:
                what["(3n+1)/2 halved once only"] += 1
            elif v >= 2 and pred in {m >> j for j in range(1, v)}:
                what["halved too few times"] += 1
            elif pred == m:
                what["3n+1 no halving"] += 1
            else:
                what["other"] += 1
    return dict(base=base, task=task_name, layers=ck["L"], overall=sum(a for a, _ in by.values()) / len(ns),
                by_v={v: dict(acc=a / b, n=b) for v, (a, b) in sorted(by.items())}, wrong=dict(what))


if __name__ == "__main__":
    bases = [int(b) for b in sys.argv[1].split(",")] if len(sys.argv) > 1 else [2, 3, 6, 16, 24]
    res = []
    for b in bases:
        try:
            r = analyse(b)
        except FileNotFoundError:
            print(f"base {b}: no checkpoint yet")
            continue
        res.append(r)
        print(f"base {b} ({r['layers']} layers): overall {r['overall']:.4f}; wrong answers {r['wrong']}")
        print("   " + "  ".join(f"v={v}:{d['acc']:.2f}" for v, d in r["by_v"].items() if d["n"] >= 8))
    json.dump(res, open(RESULTS / "stratify_by_valuation.json", "w"), indent=1)
