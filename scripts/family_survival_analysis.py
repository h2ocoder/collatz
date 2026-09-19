"""SCRUM-30 H3: does survival past an integer's own bits equal lambda/2 for every forbidden-factor family?

Reads research/investigate-pinball-analogy/results/family_<factor>.json (written by
scripts/double_halving_rs/src/bin/family.rs) and compares the measured per-step
survival rate beyond level B with lambda(F)/2, where lambda is the growth rate of
the number of binary words avoiding the factor.

Run:  python -X utf8 scripts/family_survival_analysis.py
"""

import json
import math
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "research" / "investigate-pinball-analogy" / "results"


def growth_rate(factor: str, length: int = 400) -> float:
    """Perron root of the language avoiding `factor`: ratio of successive word counts (exact integers)."""
    k = len(factor)
    counts = {"": 1}                      # suffix (up to k-1 symbols) -> number of words
    totals = []
    for _ in range(length):
        step = {}
        for suffix, c in counts.items():
            for ch in "01":
                word = suffix + ch
                if word.endswith(factor):
                    continue
                key = word[-(k - 1):] if k > 1 else ""
                step[key] = step.get(key, 0) + c
        counts = step
        totals.append(sum(counts.values()))
    return totals[-1] / totals[-2]


def main():
    rows = []
    for path in sorted(RESULTS.glob("family_*.json")):
        d = json.loads(path.read_text())
        factor, bits = d["factors"][0], d["bits"]
        hist = dict(map(tuple, d["histogram"]))
        # absorbed orbits (reached the cycle at 1 inside the family) survive every level
        tail, run = {}, d["absorbed"]
        for k in sorted(hist, reverse=True):
            run += hist[k]
            tail[k] = run
        lam = growth_rate(factor)
        # pooled survival over levels B+2 .. B+14, away from the boundary and with large counts
        levels = [L for L in range(bits + 2, bits + 15) if tail.get(L + 1) and tail[L] > 10 ** 6]
        num = sum(tail[L + 1] for L in levels)
        den = sum(tail[L] for L in levels)
        measured = num / den if den else float("nan")
        sigma = math.sqrt(measured * (1 - measured) / den) if den else float("nan")
        best_n, best_steps = d["best"][0] if d["best"] else (0, 0)
        rows.append({"factor": factor, "bits": bits, "leaves": d["leaves"], "absorbed": d["absorbed"],
                     "overflow": d["overflow"], "lambda": lam, "predicted": lam / 2, "measured": measured,
                     "sigma": sigma, "z": (measured - lam / 2) / sigma if sigma else float("nan"),
                     "record_steps": best_steps, "record_n": best_n, "seconds": d["seconds"]})
    print(f"{'forbid':>7} {'leaves':>15} {'absorbed':>10} {'lambda/2':>10} {'measured':>10} {'z':>7} {'record':>7}")
    for r in rows:
        print(f"{r['factor']:>7} {r['leaves']:>15,} {r['absorbed']:>10,} {r['predicted']:>10.6f} "
              f"{r['measured']:>10.6f} {r['z']:>+7.2f} {r['record_steps']:>7}")
    (RESULTS / "family_survival_summary.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
