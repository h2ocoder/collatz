"""SCRUM-30 H3 follow-up: where does the c/sqrt(N) correction to lambda/2 come from?

Runs the family search (scripts/double_halving_rs, binary `family`) twice per pattern and depth:
  real   the starting numbers r < 2^B themselves
  lift   r + 2^B * j with j pseudo-random: identical first B parities, genuinely fresh bits after
and reports survival over levels B+2..B+14 overall, excluding small starting numbers, and by
bit length of the starting number.

Run:  python -X utf8 scripts/family_correction_analysis.py
Writes research/investigate-pinball-analogy/results/family_correction.json
"""

import json
import math
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from family_survival_analysis import growth_rate  # noqa: E402

BINARY = ROOT / "scripts" / "double_halving_rs" / "target" / "release" / ("family.exe" if os.name == "nt" else "family")
OUT = ROOT / "research" / "investigate-pinball-analogy" / "results" / "family_correction.json"


def run(bits, pattern, lift):
    env = dict(os.environ, FAMILY_LIFT="1" if lift else "0")
    text = subprocess.run([str(BINARY), str(bits), "32", pattern], capture_output=True, text=True, env=env, check=True).stdout
    data = json.loads(text)
    return {b: (s, t) for b, s, t in data["by_len"]}


def rate(buckets, keep=lambda b: True):
    s = sum(v[0] for b, v in buckets.items() if keep(b))
    t = sum(v[1] for b, v in buckets.items() if keep(b))
    r = s / t
    return r, math.sqrt(r * (1 - r) / t), t


def fmt(r, se, pred):
    return f"{r - pred:+.2e} (z {(r - pred) / se:+6.1f})"


def main():
    results = {}
    for pattern in ("101", "1001", "000", "00"):
        pred = growth_rate(pattern) / 2
        for bits in (30, 34, 38):
            real, lifted = run(bits, pattern, False), run(bits, pattern, True)
            half = bits // 2
            row = {
                "pred": pred,
                "real_all": rate(real),
                "lift_all": rate(lifted),
                "real_large": rate(real, lambda b: b > half),
                "real_small": rate(real, lambda b: b <= half),
                "real_by_len": {b: rate(real, lambda c, b=b: c == b) for b in sorted(real) if real[b][1] > 0},
            }
            results[f"{pattern}@{bits}"] = row
            small_n = row["real_small"][2]
            print(f"{pattern:>5} B={bits}:  real {fmt(*row['real_all'][:2], pred)} | lifted {fmt(*row['lift_all'][:2], pred)}"
                  f" | real without r<2^{half} {fmt(*row['real_large'][:2], pred)} | small r only ({small_n:,} trials) "
                  f"{row['real_small'][0] - pred:+.3f}")
    OUT.write_text(json.dumps(results, indent=1, default=list))


if __name__ == "__main__":
    main()
