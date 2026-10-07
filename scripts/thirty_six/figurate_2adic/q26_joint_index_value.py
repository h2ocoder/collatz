"""Beyond the seed questions: is the dropping class of the INDEX n related to the dropping class of
the VALUE T_n?  (Both are residue data: T_n mod 2^K is a function of n mod 2^(K+1).)

Exact joint law of (cst(n), cst(T_n)) for n over one full period Z/2^(K+1), K = 16, for the rules
3x+1, 3x-1 and 5x+1; mutual information in bits; and the same for the hexagonal isometry H_n = n(2n-1).

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 q26_joint_index_value.py
Conventions: common.py.  k = Terras stopping time; k = 0 means cst > K (undetermined at this level).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import Tee, class_table

out = Tee(os.path.join(HERE, "q26_joint_index_value.log"))
res = {}
K = 16
M = 1 << K
n = np.arange(2 * M, dtype=np.int64)


def mutual_information(joint):
    tot = joint.sum()
    pi = joint.sum(axis=1) / tot
    pj = joint.sum(axis=0) / tot
    mi = 0.0
    for a in range(joint.shape[0]):
        for b in range(joint.shape[1]):
            if joint[a, b]:
                p = joint[a, b] / tot
                mi += p * math.log2(p / (pi[a] * pj[b]))
    return mi


def entropy(v):
    p = v[v > 0] / v.sum()
    return float(-(p * np.log2(p)).sum())


for (q, d) in ((3, 1), (3, -1), (5, 1)):
    lab, _ = class_table(K, q, d)
    lab = np.array(lab, dtype=np.int64)
    for fam, f in (("triangular T_n", (n * (n + 1) // 2) % M), ("hexagonal n(2n-1)", (n * (2 * n - 1)) % M)):
        a = lab[n % M]
        b = lab[f]
        joint = np.zeros((K + 1, K + 1), dtype=np.int64)
        np.add.at(joint, (a, b), 1)
        mi = mutual_information(joint)
        h = entropy(joint.sum(axis=1))
        out("=" * 96)
        out(f"rule {q}x{d:+d}, {fam}: joint counts of (class of index n, class of value), n in Z/2^{K + 1}")
        ks = [k for k in range(K + 1) if joint[k].sum()]
        show = [k for k in ks if k][:6] + [0]
        out("   index k \\ value k " + "".join(f"{('>' + str(K)) if k == 0 else k:>9}" for k in show) + "    other")
        for ka in show:
            row = joint[ka]
            other = row.sum() - sum(row[k] for k in show)
            out(f"        {('>' + str(K)) if ka == 0 else ka:>6}       " + "".join(f"{row[k]:9d}" for k in show)
                + f"{other:9d}")
        out(f"   mutual information I(class(n); class(value)) = {mi:.6f} bits   (entropy of one marginal {h:.4f} bits)")
        res[f"{q}x{d:+d} | {fam}"] = dict(mutual_information_bits=mi, marginal_entropy_bits=h)

out("=" * 96)
out("Exact low-level rules behind the table (any rule; they are statements about n mod 8):")
out("   T_n is even  <=>  n = 0 or 3 mod 4.   n = 1 mod 8  =>  T_n = 1 mod 4.   n = 5 mod 8  =>  T_n = 3 mod 4.")
ok = all(((x * (x + 1) // 2) % 2 == 0) == (x % 4 in (0, 3)) for x in range(4096))
ok &= all((x * (x + 1) // 2) % 4 == 1 for x in range(1, 4096, 8))
ok &= all((x * (x + 1) // 2) % 4 == 3 for x in range(5, 4096, 8))
out("   verified for n < 4096:", ok)
out("   Consequence for 3x+1: every index with Terras stopping time >= 4 (n = 3 mod 4) has an even T_n")
out("   (value in Set_1); an index in Set_3 (n = 1 mod 4) always has an odd T_n.")
res["low_level_rules_ok"] = ok

# ------------------------------------------------------------------ first-run law
out("=" * 96)
out("First-run law.  L1(n) = length of the first run of equal letters in the parity vector of n.")
out("   3x+1:  L1(n) = v2(n) + v2(n+1) = v2(T_n) + 1         (T_n = n(n+1)/2: branch fixed points 0 and -1)")
out("   3x-1:  L1(n) = v2(n) + v2(n-1) = v2(T_(n-1)) + 1     (fixed points 0 and +1)")
out("   5x+1:  L1(n) = v2(n) + v2(3n+1) = v2(n(3n+1)/2) + 1  (fixed points 0 and -1/3; second pentagonal)")
out("=" * 96)


def first_run(x, q, d, cap=200):
    p0 = x & 1
    L = 0
    while (x & 1) == p0 and L < cap:
        x = (q * x + d) >> 1 if x & 1 else x >> 1
        L += 1
    return L


def val2(x):
    c = 0
    while x % 2 == 0:
        x //= 2
        c += 1
    return c


law = {}
law["3x+1 vs T_n"] = all(first_run(x, 3, 1) == val2(x * (x + 1) // 2) + 1 for x in range(1, 200001))
law["3x-1 vs T_(n-1)"] = all(first_run(x, 3, -1) == val2(x * (x - 1) // 2) + 1 for x in range(2, 200001))
law["5x+1 vs n(3n+1)/2"] = all(first_run(x, 5, 1) == val2(x * (3 * x + 1) // 2) + 1 for x in range(1, 200001))
law["control: 5x+1 vs T_n (should fail)"] = all(first_run(x, 5, 1) == val2(x * (x + 1) // 2) + 1 for x in range(1, 200001))
law["control: 3x-1 vs T_n (should fail)"] = all(first_run(x, 3, -1) == val2(x * (x + 1) // 2) + 1 for x in range(2, 200001))
for name, v in law.items():
    out(f"   {v!s:5s}  {name}   (1 <= n <= 200000)")
res["first_run_law"] = law

# mutual information with the family matched to the rule
out("=" * 96)
out("Mutual information with the figurate family MATCHED to the rule (K = 16, n in Z/2^17):")
for (q, d, fam, f) in ((3, 1, "T_n = n(n+1)/2", (n * (n + 1) // 2) % M),
                        (3, -1, "T_(n-1) = n(n-1)/2", (n * (n - 1) // 2) % M),
                        (5, 1, "n(3n+1)/2", (n * (3 * n + 1) // 2) % M),
                        (5, -1, "n(3n-1)/2", (n * (3 * n - 1) // 2) % M)):
    lab, _ = class_table(K, q, d)
    lab = np.array(lab, dtype=np.int64)
    joint = np.zeros((K + 1, K + 1), dtype=np.int64)
    np.add.at(joint, (lab[n % M], lab[f]), 1)
    mi = mutual_information(joint)
    out(f"   rule {q}x{d:+d} with {fam:20s}: I = {mi:.6f} bits")
    res[f"matched {q}x{d:+d}"] = mi
out("   3x+-1: exactly 1/2 bit (theorem 6 of the README).  5x+-1: not 1/2.  The 3x value uses that the word")
out("   '10' is already a dropping word (3 < 4), so every odd n outside the class k = 2 has first run >= 2.")
with open(os.path.join(HERE, "q26_joint_index_value.json"), "w", encoding="utf-8") as fh:
    json.dump(res, fh, indent=1)
out.close()
