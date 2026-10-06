"""Q3.5  Is the Terras kernel special at Pierpont primes p = 2^u 3^v + 1 (the primes whose totient is 3-smooth),
or at the primes 6^(2^j) + 1 (7, 37, 1297)?

Conventions: gk_common.py.  K_p = Terras kernel on Z/p.
  a = v2(ord_p 2),  b = v2(ord_p 3),  t = v2(p - 1),  rung = a - b,
  m = order of 2 modulo <3>,  idx = [(Z/p)^x : <2,3>].
The theorem (lattice form) gives the circle |lambda| = 1/2 exactly:  if b >= 1 there are (p-1)/ord_p(3) eigenvalues
on it (counted with multiplicity), namely (1/2) * {m-th roots of (-1)^(m+t')}, each idx times; they are primitive
2^(rung+1)-th roots of unity times mu_m when rung >= 1.  So the 'half-circle content' is a function of the pair
(<2>, <3>) alone, and 'extreme' means: large rung (needs t >= rung + 2) or large (p-1)/ord_p(3).

Part A (orders only, all primes < A_MAX): distribution of the rung and of the content, Pierpont against all
        primes with the same t = v2(p-1).
Part B (spectra, float): |lambda_2| and the measured content for every Pierpont prime <= B_MAX and its four nearest
        non-Pierpont neighbours (two below, two above).

Run:  python -X utf8 q35_pierpont.py [A_MAX=1000000] [B_MAX=1500]    (writes q35_pierpont.log / .json)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gk_common import order, primes_upto, v2  # noqa: E402

A_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
B_MAX = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
T0 = time.time()
LOG: list[str] = []


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def is_pierpont(p: int) -> bool:
    n = p - 1
    while n % 2 == 0:
        n //= 2
    while n % 3 == 0:
        n //= 3
    return n == 1


def two_part_of_order(g: int, p: int, t: int) -> int:
    """v2 of the multiplicative order of g mod p (t = v2(p-1))."""
    x = pow(g, (p - 1) >> t, p)
    a = 0
    while x != 1:
        x = x * x % p
        a += 1
    return a


# =============================================================================== Part A
say(f"=== A. orders only: all primes 5 <= p < {A_MAX} ===")
PR = [p for p in primes_upto(A_MAX - 1) if p >= 5]
recs = []
for p in PR:
    t = v2(p - 1)
    a = two_part_of_order(2, p, t)
    b = two_part_of_order(3, p, t)
    recs.append((p, t, a, b, is_pierpont(p)))
pier = [r for r in recs if r[4]]
say(f"   {len(recs)} primes, {len(pier)} Pierpont: {[r[0] for r in pier]}")
say("   rung = a - b when b >= 1 (ord_p 3 even), 'none' when b = 0 (no eigenvalue of modulus 1/2 is forced)")


def rung_label(a: int, b: int) -> str:
    if b == 0:
        return "none"
    r = a - b
    return "<0" if r < 0 else ("0" if r == 0 else ("1" if r == 1 else ">=2"))


labels = ["none", "<0", "0", "1", ">=2"]
say("   t = v2(p-1) | all primes: n and fractions [none, a<b (-1/2), a=b (+1/2), rung 1 (+-i/2), rung >= 2] | Pierpont primes with this t: p(rung)")
tableA = []
for t in sorted({r[1] for r in recs}):
    sel = [r for r in recs if r[1] == t]
    if len(sel) < 5 and not any(r[4] for r in sel):
        continue
    cnt = {lab: 0 for lab in labels}
    for r in sel:
        cnt[rung_label(r[2], r[3])] += 1
    pp = [(r[0], rung_label(r[2], r[3]) if r[3] == 0 else str(r[2] - r[3])) for r in sel if r[4]]
    tableA.append({"t": t, "n": len(sel), "fractions": {lab: cnt[lab] / len(sel) for lab in labels}, "pierpont": pp})
    say(f"   t = {t:>2} | n = {len(sel):>6}  " + "  ".join(f"{cnt[lab] / len(sel):.3f}" for lab in labels) + f" | {pp}")
# pooled test: is the Pierpont rung distribution different from primes with the same t?
obs = {lab: 0 for lab in labels}
exp = {lab: 0.0 for lab in labels}
for row in tableA:
    for pval, lab in row["pierpont"]:
        lab2 = lab if lab in ("none",) else ("<0" if int(lab) < 0 else ("0" if int(lab) == 0 else ("1" if int(lab) == 1 else ">=2")))
        obs[lab2] += 1
        for l2 in labels:
            exp[l2] += row["fractions"][l2]
chi2 = sum((obs[lab] - exp[lab]) ** 2 / exp[lab] for lab in labels if exp[lab] > 0)
say(f"   Pierpont primes, observed rung classes {obs}; expected from all primes with the same t: " + str({k: round(v, 2) for k, v in exp.items()}) + f"; chi^2 = {chi2:.2f} on 4 d.o.f. (5 % critical value 9.49)")
say("   first primes by rung (smallest five), with Pierpont flag:")
first = {}
for p, t, a, b, pi in recs:
    if b >= 1 and a - b >= 1:
        first.setdefault(a - b, [])
        if len(first[a - b]) < 5:
            first[a - b].append((p, "P" if pi else "-"))
for r in sorted(first):
    say(f"      rung {r} (eigenvalues (1/2) x primitive 2^{r + 1}-th roots of unity): {first[r]}")
say("   the three primes 6^(2^j) + 1:")
for p in (7, 37, 1297):
    t = v2(p - 1)
    a, b = two_part_of_order(2, p, t), two_part_of_order(3, p, t)
    say(f"      p = {p}: ord 6 = {order(6, p)}, ord 2 = {order(2, p)}, ord 3 = {order(3, p)}, t = {t}, a = {a}, b = {b}, rung = {a - b if b else 'none'}, content (p-1)/ord 3 = {(p - 1) // order(3, p) if b else 0}")
say("   6^(2^j) = -1 forces chi(2)^(2^j) chi(3)^(2^j) = -1 for the characters of exact 2-power order 2^(j+1): the 2-parts of ord 2 and ord 3 cannot both be < 2^(j+1);")
say("   that is a constraint on (a, b), not a coincidence of the kernel.")

# =============================================================================== Part B
say(f"\n=== B. spectra (float): Pierpont primes <= {B_MAX} against their four nearest non-Pierpont neighbours ===")
small = [p for p in primes_upto(B_MAX + 200) if p >= 5]
pset = [p for p in small if is_pierpont(p) and p <= B_MAX]


def kernel_stats(p: int) -> dict:
    inv2 = pow(2, -1, p)
    K = np.zeros((p, p))
    for x in range(p):
        K[x, x * inv2 % p] += 0.5
        K[x, (3 * x + 1) * inv2 % p] += 0.5
    ev = np.linalg.eigvals(K)
    mod = np.sort(np.abs(ev))[::-1]
    o3 = order(3, p)
    return {"p": p, "lambda2": float(mod[1]), "content_measured": int(np.sum(np.abs(np.abs(ev) - 0.5) < 1e-7)),
            "content_predicted": (p - 1) // o3 if o3 % 2 == 0 else 0, "ord2": order(2, p), "ord3": o3}


rowsB = []
for p in pset:
    i = small.index(p)
    below = [q for q in small[:i][::-1] if not is_pierpont(q)][:2]
    above = [q for q in small[i + 1 :] if not is_pierpont(q)][:2]
    sp_ = kernel_stats(p)
    nb = [kernel_stats(q) for q in below + above]
    rowsB.append({"pierpont": sp_, "neighbours": nb})
    say(f"   p = {p:>4} (ord2 {sp_['ord2']:>4}, ord3 {sp_['ord3']:>4}): |lambda_2| = {sp_['lambda2']:.4f}, content {sp_['content_measured']} (predicted {sp_['content_predicted']})"
        f" | neighbours {[(n['p'], round(n['lambda2'], 4), n['content_measured'], n['content_predicted']) for n in nb]}  [{time.time() - T0:.0f}s]")
lp = np.array([r["pierpont"]["lambda2"] for r in rowsB])
ln = np.array([np.mean([n["lambda2"] for n in r["neighbours"]]) for r in rowsB])
alln = np.array([n["lambda2"] for r in rowsB for n in r["neighbours"]])
diff = lp - ln
say(f"   |lambda_2|: Pierpont mean {lp.mean():.4f} (sd {lp.std(ddof=1):.4f}, n = {len(lp)}); neighbours mean {alln.mean():.4f} (sd {alln.std(ddof=1):.4f}, n = {len(alln)})")
say(f"   paired difference (Pierpont - mean of its 4 neighbours): mean {diff.mean():+.4f}, sd {diff.std(ddof=1):.4f}, t = {diff.mean() / (diff.std(ddof=1) / np.sqrt(len(diff))):+.2f} (n = {len(diff)}); Pierpont larger in {int((diff > 0).sum())} of {len(diff)}")
big = [r for r in rowsB if r["pierpont"]["p"] >= 97]
d2 = np.array([r["pierpont"]["lambda2"] - np.mean([n["lambda2"] for n in r["neighbours"]]) for r in big])
say(f"   same, p >= 97 only: mean {d2.mean():+.4f}, sd {d2.std(ddof=1):.4f}, t = {d2.mean() / (d2.std(ddof=1) / np.sqrt(len(d2))):+.2f} (n = {len(d2)})")
cm = [(r["pierpont"]["p"], r["pierpont"]["content_measured"], r["pierpont"]["content_predicted"]) for r in rowsB if r["pierpont"]["content_measured"] != r["pierpont"]["content_predicted"]]
cn = [(n["p"], n["content_measured"], n["content_predicted"]) for r in rowsB for n in r["neighbours"] if n["content_measured"] != n["content_predicted"]]
say(f"   measured content differs from the theorem's count at Pierpont primes {cm} and at neighbours {sorted(set(cn))}   (these are the sporadic primes 11, 31, 37)")
cp_ = np.array([r["pierpont"]["content_predicted"] / (r["pierpont"]["p"] - 1) for r in rowsB])
cnn = np.array([n["content_predicted"] / (n["p"] - 1) for r in rowsB for n in r["neighbours"]])
say(f"   content / (p - 1) = 1/ord_p(3) or 0: Pierpont mean {cp_.mean():.4f}, neighbours mean {cnn.mean():.4f}  (Pierpont primes have 3-smooth, hence often small, ord_p(3))")
say(f"total time {time.time() - T0:.0f} s")
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
Path(__file__).with_suffix(".json").write_text(json.dumps({"A_MAX": A_MAX, "B_MAX": B_MAX, "tableA": tableA, "first_by_rung": {str(k): v for k, v in first.items()}, "partB": rowsB}, indent=0), encoding="utf-8")
