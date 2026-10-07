"""Reviewer check 4 for site/explore/folded-pentagon.md: the PentagonWalk component.

Reads fp_component_dump.json (what the component's own TypeScript functions return for every setting of
its three controls: k = 0..16, start residue 0..4, rule 3x+1 / 3x-1) and compares it with an independent
Python implementation:
  - integer counts on a window of 5*2^k consecutive integers that STRADDLES ZERO (the component uses a
    positive window), Python big integers;
  - the pentagon-walk law from the closed form with exact arithmetic in Z[sqrt 5] (the component steps a walk);
  - the truth value of 'same law' decided here, independently of the component's verdict logic.

Run:  node fp_component_dump.mjs  &&  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 fp_math_04_component.py
"""
from __future__ import annotations

import itertools
import json
import math
from fractions import Fraction as Fr
from pathlib import Path

FAIL = 0


def check(ok: bool, label: str) -> None:
    global FAIL
    if not ok:
        FAIL += 1
    print(f"   [{'ok' if ok else 'FAIL'}] {label}")


dump = json.loads((Path(__file__).parent / "fp_component_dump.json").read_text())
ROWS = dump["rows"]
K_MAX = dump["MAX_STEPS"]
print(f"component dump: {len(ROWS)} settings, MAX_STEPS = {K_MAX}, ROLES = {dump['ROLES']}")


# ---------------------------------------------------------------- independent reference
def T(n: int, c: int) -> int:
    return n // 2 if n % 2 == 0 else (3 * n + c) // 2


def ref_counts(k: int, start: int, c: int) -> list[int]:
    lo = -(5 * 2**k) // 2 - 11
    counts = [0] * 5
    for n0 in range(lo, lo + 5 * 2**k):
        if n0 % 5 != start:
            continue
        n = n0
        for _ in range(k):
            n = T(n, c)
        counts[n % 5] += 1
    return counts


class Q5:
    """a + b sqrt5 with rational a, b."""

    def __init__(self, a, b=0):
        self.a, self.b = Fr(a), Fr(b)

    def __add__(self, o):
        return Q5(self.a + o.a, self.b + o.b)

    def __mul__(self, o):
        return Q5(self.a * o.a + 5 * self.b * o.b, self.a * o.b + self.b * o.a)

    def __pow__(self, n):
        r = Q5(1)
        for _ in range(n):
            r = r * self
        return r


C72 = Q5(Fr(-1, 4), Fr(1, 4))      # cos 72 = (sqrt5 - 1)/4
C144 = Q5(Fr(-1, 4), Fr(-1, 4))    # cos 144 = -(sqrt5 + 1)/4
COS = {0: Q5(1), 1: C72, 2: C144, 3: C144, 4: C72}       # cos(2 pi j/5);  cos(4 pi j/5) = COS[2j mod 5]


def ref_walk(k: int, frm: int) -> list[int]:
    """2^k x law of the simple random walk on the 5-cycle after k steps, closed form, exact."""
    out = []
    for v in range(5):
        j = (v - frm) % 5
        val = Q5(Fr(1, 5)) + Q5(Fr(2, 5)) * (C72**k * COS[j] + C144**k * COS[2 * j % 5])
        assert val.b == 0
        cnt = val.a * 2**k
        assert cnt.denominator == 1
        out.append(int(cnt))
    return out


def lucas(k: int) -> int:
    a, b = 2, 1
    for _ in range(k):
        a, b = b, a + b
    return a


# roles as the thread states them
ROLE = {1: {1: "apex", 2: "near", 3: "near", 0: "far", 4: "far"}, -1: {4: "apex", 2: "near", 3: "near", 0: "far", 1: "far"}}
APEX = {1: 1, -1: 4}
PERMS = list(itertools.permutations(range(5)))

# ---------------------------------------------------------------- 1. counts and walk
print("=== 1. the two columns of the table ===")
bad_c, bad_w, bad_tot = [], [], []
REF = {}
for r in ROWS:
    key = (r["sign"], r["start"], r["k"])
    REF[key] = ref_counts(r["k"], r["start"], r["sign"])
    if r["collatz"] != REF[key]:
        bad_c.append(key)
    if r["walk"] != ref_walk(r["k"], r["startVertex"]):
        bad_w.append(key)
    if sum(r["collatz"]) != 2 ** r["k"] or sum(r["walk"]) != 2 ** r["k"]:
        bad_tot.append(key)
check(not bad_c, f"T^k(n) column = independent count on a window straddling zero, all {len(ROWS)} settings {bad_c[:3]}")
check(not bad_w, f"Walk column = exact closed-form pentagon law from the start vertex, all settings {bad_w[:3]}")
check(not bad_tot, "both columns total 2^k")

# ---------------------------------------------------------------- 2. labels
print("=== 2. labels ===")
ok_roles = all(dump["ROLES"][v] == ROLE[r["sign"]][res] for r in ROWS for v, res in enumerate(r["order"]))
check(ok_roles, "apex / near / far labels: 3x+1 apex 1, near {2,3}, far {0,4};  3x-1 apex 4, near {2,3}, far {0,1}")
check(all(r["order"] == ([1, 2, 4, 0, 3] if r["sign"] == 1 else [4, 3, 1, 0, 2]) for r in ROWS), "pentagon drawn as 1-2-4-0-3, and 4-3-1-0-2 for 3x-1 (every residue negated)")
check(all((r["startVertex"] == 0) == (r["start"] == APEX[r["sign"]]) for r in ROWS), "the start is flagged as the apex exactly when it is residue 1 (3x+1) or 4 (3x-1)")
ok_n = True
for r in ROWS:
    ns = [n for n in range(1, 5 * 2 ** r["k"] + 5) if n % 5 == r["start"]][: 2 ** r["k"]]
    ok_n &= r["firstN"] == ns[0] and r["lastN"] == ns[-1] and r["lastN"] - r["firstN"] < 5 * 2 ** r["k"]
check(ok_n, "'the 2^k integers n = start (mod 5) from firstN to lastN': the first 2^k positive ones, inside one period 5*2^k")
check(all(r["lucas"] == lucas(r["k"]) and r["lucasSign"] == ("+" if r["k"] % 2 == 0 else "-") and 5 * r["returnCount"] == 2 ** r["k"] + 2 * (-1) ** r["k"] * lucas(r["k"]) for r in ROWS),
      "Lucas row: L_k, the sign shown, and (2^k +- 2 L_k)/5")
check(all(r["returnCount"] == r["collatz"][r["start"]] for r in ROWS if r["startVertex"] == 0), "'Back at the apex' = Lucas formula whenever that table is shown (apex start), both rules")
check(all(abs(r["distance"] - float(sum(abs(Fr(c, 2 ** r["k"]) - Fr(1, 5)) for c in REF[(r["sign"], r["start"], r["k"])]) / 2)) < 1e-12 for r in ROWS), "'Distance from uniform' = total variation, as the caption says")
check(abs(dump["HALF_PHI"] - math.cos(math.radians(36))) < 1e-15 and all(abs(r["rate"] - math.cos(math.radians(36)) ** r["k"]) < 1e-12 for r in ROWS), "(phi/2)^k row")

# ---------------------------------------------------------------- 3. the verdict
print("=== 3. the agreement indicator ===")


def truly_same_law(sign: int, start: int, k: int) -> bool:
    """the statement the green box makes: counts on residues = k-step walk counts on the vertices, walk begun at the start's vertex."""
    order = [1, 2, 4, 0, 3] if sign == 1 else [4, 3, 1, 0, 2]
    w = ref_walk(k, order.index(start))
    return all(REF[(sign, start, k)][res] == w[v] for v, res in enumerate(order))


false_same = [(r["sign"], r["start"], r["k"]) for r in ROWS if r["verdict"] == "same" and not truly_same_law(r["sign"], r["start"], r["k"])]
false_diff = [(r["sign"], r["start"], r["k"]) for r in ROWS if r["verdict"] == "different" and truly_same_law(r["sign"], r["start"], r["k"])]
unmoved = sorted({(r["sign"], r["start"], r["k"]) for r in ROWS if r["verdict"] == "unmoved"})
same = [(r["sign"], r["start"], r["k"]) for r in ROWS if r["verdict"] == "same"]
check(not false_same, f"'Same law' is never shown falsely ({len(same)} settings show it)")
check(not false_diff, "'Different laws' is never shown when the laws agree")
check(sorted(same) == sorted((s, APEX[s], k) for s in (1, -1) for k in range(K_MAX + 1)), "'Same law' is shown for the apex start at every k = 0..16, both rules, and nowhere else")
check(all(k == 0 for _, _, k in unmoved) and len(unmoved) == 8, f"'Nothing has moved yet' appears only at k = 0 (non-apex starts): {unmoved}")
nonapex = [r for r in ROWS if r["startVertex"] != 0 and r["k"] >= 1]
check(all(r["verdict"] == "different" for r in nonapex), f"every non-apex start with k >= 1 shows 'Different laws' ({len(nonapex)} settings); fewest disagreeing vertices: {min(r['mismatches'] for r in nonapex)}")
by_m = {}
for r in nonapex:
    by_m[r["mismatches"]] = by_m.get(r["mismatches"], 0) + 1
print(f"   non-apex, k >= 1: number of settings by 'm of 5 vertices disagree': {dict(sorted(by_m.items()))}")
low = sorted((r["sign"], r["start"], r["k"], r["mismatches"]) for r in nonapex if r["mismatches"] <= 2)
print(f"   settings with only 1 or 2 disagreeing vertices: {low[:12]}{' ...' if len(low) > 12 else ''}")
# 'no relabelling of the residues repairs the others'
ok_relabel = True
for sign in (1, -1):
    for start in range(5):
        if start == APEX[sign]:
            continue
        laws = [REF[(sign, start, k)] for k in range(K_MAX + 1)]
        ok_relabel &= not any(all(laws[k] == [ref_walk(k, p[start])[p[res]] for res in range(5)] for k in range(K_MAX + 1)) for p in PERMS)
check(ok_relabel, "'no relabelling of the residues repairs the others': none of the 120 placements gives a pentagon law for k = 0..16, each non-apex start, both rules")
# the mirror toggle keeps the start on the same vertex
check(all([4, 3, 1, 0, 2].index((5 - s) % 5) == [1, 2, 4, 0, 3].index(s) for s in range(5)), "switching the rule maps start s to -s, which sits on the same vertex")
check(all(REF[(-1, (5 - s) % 5, k)] == [REF[(1, s, k)][(5 - res) % 5] for res in range(5)] for s in range(5) for k in range(K_MAX + 1)),
      "3x-1 from start -s is the 3x+1 law from s with every residue negated (all starts, k = 0..16)")

# ---------------------------------------------------------------- 4. the 'Ratio of the two' row
print("=== 4. 'Ratio of the two' (distance / (phi/2)^k) at k = 0, 4, 8, 12, 16, 3x+1 ===")
for start in range(5):
    vals = [next(r for r in ROWS if r["sign"] == 1 and r["start"] == start and r["k"] == k) for k in (0, 4, 8, 12, 16)]
    print(f"   start {start}: " + ", ".join(f"{r['distance'] / r['rate']:.4f}" for r in vals))

print(f"\n{FAIL} failures")
