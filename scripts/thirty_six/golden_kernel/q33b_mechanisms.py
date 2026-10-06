"""Q3.3 (mechanisms)  Why do irrational cosines appear for some (q, d, N), and where does Collatz mod 5 sit?

Reads q33_qd_survey.json (run q33_qd_survey.py first).  Branch multipliers mod N:  a = 1/d  (even branch x -> a x)
and  b = q/d  (odd branch x -> b x + 1/d).

  1. classify every irrational-cosine hit of the survey:
       A  both branches involutions (a^2 = 1 and b = -1): R_e + R_o is a symmetric matrix, all eigenvalues real (proved)
       B  reflection + translation (a = -1, b = 1): eigenvalues 0 and 2cos(2 pi s/N) (proved)
       C  odd branch a reflection (b = -1, i.e. N | q + d), even branch not an involution   <- Collatz mod 5 is here
       D  even branch an involution only;   E  neither
  2. check A and B on the whole survey range (every such triple must have an all-real primitive spectrum).
  3. for the 3x+1 kernel: the moduli N prime to 6 at which a branch is an involution.
  4. the one-parameter family that contains Collatz mod 5:   G_N = (1/2)(x -> -2x) + (1/2)(x -> -x - 2)  on Z/N,
     N odd  (this is the pair (d+1, d) reduced modulo N = 2d + 1; N = 5 is (3, 2)).  Every Kronecker factor at
     level N for odd 5 <= N <= G_MAX.
  5. all dilation + reflection kernels  (1/2)(x -> a x) + (1/2)(x -> 1 - x)  on Z/p, p <= 61: which a give an
     irrational cosine, and what a is algebraically.

Run:  python -X utf8 q33b_mechanisms.py [G_MAX=301]     (writes q33b_mechanisms.log / .json)
"""
from __future__ import annotations

import json
import sys
import time
from math import gcd
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gk_common import (charpoly_int, cyclotomic, divisors, euler_phi, kronecker_candidates, multiplicity, order,  # noqa: E402
                       pdivmod, peval_mod, primes_upto, psi, pstr, two_K)

G_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 301
HERE = Path(__file__).resolve().parent
T0 = time.time()
LOG: list[str] = []
RES: dict = {}


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


survey = json.loads((HERE / "q33_qd_survey.json").read_text(encoding="utf-8"))
hits = survey["irrational_cosine_hits"]

# ------------------------------------------------------------------------------- 1
say(f"=== 1. the {len(hits)} irrational-cosine hits of the (q, d, N) survey, by mechanism ===")
say("   even branch x -> a x is an involution iff a^2 = 1;  odd branch x -> b x + 1/d is an involution iff b = -1 (b^2 = 1 alone gives o^2 = a translation)")
KEYS = ["A: both branches involutions (a^2 = 1, b = -1): symmetric matrix",
        "B: reflection + translation (a = -1, b = 1)",
        "C: odd branch a reflection (b = -1), even branch not an involution",
        "D: even branch an involution (a^2 = 1), odd branch neither reflection nor translation",
        "E: neither branch an involution"]
classes: dict[str, list] = {k: [] for k in KEYS}


def klass(q: int, d: int, N: int) -> str:
    a = pow(d, -1, N)
    b = q * a % N
    if a * a % N == 1 and b == N - 1:
        return KEYS[0]
    if a == N - 1 and b == 1:
        return KEYS[1]
    if b == N - 1:
        return KEYS[2]
    if a * a % N == 1:
        return KEYS[3]
    return KEYS[4]


for h in hits:
    q, d, N = h["q"], h["d"], h["N"]
    irr = sorted(int(j) for j in h["psi"] if int(j) not in (1, 2, 3, 6))
    classes[klass(q, d, N)].append((q, d, N, irr))
for k, v in classes.items():
    say(f"   {k}: {len(v)}" + (f": {v}" if len(v) <= 45 else f", e.g. {v[:12]} ..."))
RES["hit_classes"] = {k: [list(t) for t in v] for k, v in classes.items()}
say("   class E hits and the orders of (a, b) modulo each prime power of N:")
for q, d, N, irr in classes[KEYS[4]]:
    parts = []
    for pp, ee in sp.factorint(N).items():
        M = pp ** ee
        a = pow(d, -1, M)
        b = q * a % M
        parts.append(f"mod {M}: a = {a} (ord {order(a, M)}), b = {b} (ord {order(b, M)})")
    say(f"      (q,d,N) = ({q},{d},{N}) cosines j = {irr}: " + "; ".join(parts))

# ------------------------------------------------------------------------------- 2
say("\n=== 2. the two proved all-cosine mechanisms, checked on the whole survey range ===")
real_set = {(r["q"], r["d"], r["N"]) for r in survey["all_real"]}
cnt = {k: [0, 0] for k in KEYS}
for d in range(2, survey["QD_MAX"] + 1):
    for q in range(2, survey["QD_MAX"] + 1):
        if q == d:
            continue
        for N in range(3, survey["N_MAX"] + 1):
            if gcd(N, q * d) != 1:
                continue
            k = klass(q, d, N)
            cnt[k][0] += 1
            cnt[k][1] += (q, d, N) in real_set
for k in KEYS:
    say(f"   {k}: {cnt[k][0]} triples, primitive spectrum all real in {cnt[k][1]}")
assert cnt[KEYS[0]][0] == cnt[KEYS[0]][1] and cnt[KEYS[1]][0] == cnt[KEYS[1]][1]
cE = [t for t in sorted(real_set) if t[2] >= 3 and klass(*t) in (KEYS[2], KEYS[3], KEYS[4])]
say(f"   all-real levels NOT explained by A or B: {cE}")
RES["mechanism_counts"] = {k: v for k, v in cnt.items()}
RES["all_real_unexplained_by_A_B"] = [list(t) for t in cE]

# ------------------------------------------------------------------------------- 3
say("\n=== 3. the 3x+1 kernel: moduli N prime to 6 with an involutive branch ===")
inv = []
for N in range(5, 2000):
    if N % 2 and N % 3:
        a = pow(2, -1, N)
        b = 3 * a % N
        if a * a % N == 1 or b * b % N == 1:
            inv.append((N, "e" if a * a % N == 1 else "o"))
say(f"   N < 2000: {inv}    (o^2 = id  <=>  (3/2)^2 = 1  <=>  N | 3^2 - 2^2 = 5;  e^2 = id  <=>  N | 3)")
say("   so 5 = 3^2 - 2^2 = 3 + 2 is the only modulus at which a branch of the 3x+1 map is an involution: there 3/2 = -1, the odd branch is a reflection,")
say("   and the word 'oo' (the cell (k, s) = (2, 2) of the exponent lattice, 2^2 - 3^2 = -5) is the identity.")

# ------------------------------------------------------------------------------- 4
say(f"\n=== 4. the family G_N = (1/2)(x -> -2x) + (1/2)(x -> -x - 2) on Z/N, N odd, 5 <= N <= {G_MAX}  [(d+1, d) mod 2d+1] ===")
PR = primes_upto(60000)
_pts: dict = {}


def test_points(k: int, cosine: bool):
    key = (k, cosine)
    if key not in _pts:
        out = []
        for r in PR:
            if r % k == 1:
                z = next(z for z in (pow(h, (r - 1) // k, r) for h in range(2, r)) if order(z, r) == k)
                out.append((r, (z + pow(z, -1, r)) % r if cosine else z))
                if len(out) == 2:
                    break
        _pts[key] = out
    return _pts[key]


def kron(p_: list[int]):
    deg = len(p_) - 1
    rest = p_
    z, rest = multiplicity([0, 1], rest)
    ms, ks = kronecker_candidates(deg)
    ps, ph = {}, {}
    for j in ms:
        if j == 4:
            continue
        if j <= 2 or all(peval_mod(rest, pt, r) == 0 for r, pt in test_points(j, True)):
            mult, rest2 = multiplicity(psi(j), rest)
            if mult:
                ps[j], rest = mult, rest2
    for k in ks:
        if k <= 2:
            continue
        if all(peval_mod(rest, pt, r) == 0 for r, pt in test_points(k, False)):
            mult, rest2 = multiplicity(cyclotomic(k), rest)
            if mult:
                ph[k], rest = mult, rest2
    return z, ps, ph, len(rest) - 1


prim: dict[int, list[int]] = {1: [-2, 1]}
fam = []
for N in range(3, G_MAX + 1, 2):
    A = np.zeros((N, N), dtype=np.int64)
    for x in range(N):
        A[x, (-2 * x) % N] += 1
        A[x, (-x - 2) % N] += 1
    p_ = charpoly_int(A)
    for dd in divisors(N):
        if dd < N:
            p_, r = pdivmod(p_, prim[dd])
            assert r == [0]
    prim[N] = p_
    if N < 5:
        continue
    z, ps, ph, rest = kron(p_)
    irr = {j: v for j, v in ps.items() if j not in (1, 2, 3, 6)}
    fam.append({"N": N, "ord(-2)": order(N - 2, N), "zero": z, "psi": {str(k): v for k, v in ps.items()}, "phi": {str(k): v for k, v in ph.items()}, "non_kronecker_deg": rest})
    if irr:
        say(f"   N = {N:>3} (ord(-2) = {order(N - 2, N):>3}): irrational cosines j = {irr}" + (f"   prim = {sp.factor(sp.Poly(p_[::-1], sp.Symbol('x')).as_expr())}" if len(p_) <= 13 else ""))
gold = [f["N"] for f in fam if "5" in f["psi"] or "10" in f["psi"]]
octa = [f["N"] for f in fam if "8" in f["psi"]]
other = sorted({int(j) for f in fam for j in f["psi"] if int(j) not in (1, 2, 3, 5, 6, 8, 10)})
say(f"   golden (j = 5 or 10) at N = {gold}")
say(f"   octagon (j = 8, sqrt2) at N = {octa}")
say(f"   other irrational j seen: {other}")
say(f"   levels with all eigenvalues real: {[f['N'] for f in fam if f['non_kronecker_deg'] == 0 and not f['phi']]}")
RES["family_G"] = fam

# ------------------------------------------------------------------------------- 5
say("\n=== 5. all kernels (1/2)(x -> a x) + (1/2)(x -> 1 - x) on Z/p, 5 <= p <= 61: the a with an irrational cosine ===")
xs = sp.Symbol("x")
refl = []
for p in [q for q in primes_upto(61) if q >= 5]:
    found: dict[int, list] = {}
    for a in range(2, p - 1):
        A = np.zeros((p, p), dtype=np.int64)
        for t in range(p):
            A[t, a * t % p] += 1
            A[t, (1 - t) % p] += 1
        cp = charpoly_int(A)
        q_, r = pdivmod(cp, [-2, 1])
        js = []
        for j in (5, 10, 8, 12, 7, 14, 9, 18, 16, 20, 24, 15, 30, 11, 22, 13, 26):
            if len(psi(j)) - 1 <= len(q_) - 1:
                mult, _ = multiplicity(psi(j), q_)
                if mult:
                    js.append(j)
        if js:
            found[a] = js
    tags = {}
    for a in found:
        t = []
        if (a + 2) % p == 0:
            t.append("-2")
        if (2 * a + 1) % p == 0:
            t.append("-1/2")
        if (a * a + a - 1) % p == 0:
            t.append("root of a^2+a-1")
        if (a * a - a - 1) % p == 0:
            t.append("root of a^2-a-1")
        if (a * a - 2) % p == 0:
            t.append("sqrt2")
        if (2 * a * a - 1) % p == 0:
            t.append("1/sqrt2")
        if (a + 4) % p == 0:
            t.append("-4")
        if (4 * a + 1) % p == 0:
            t.append("-1/4")
        tags[a] = t
    refl.append({"p": p, "a": {str(a): {"cosines_j": js, "ord": order(a, p), "is": tags[a]} for a, js in found.items()}})
    say(f"   p = {p:>2}: " + (", ".join(f"a = {a} (ord {order(a, p)}; j = {js}; {'/'.join(tags[a]) or '?'})" for a, js in found.items()) or "none"))
RES["reflection_kernels"] = refl
say("   a = -2 and a = -1/2 are the family G_p and its transpose.  Kernels with a and 1/a have the same spectrum (transpose).")
say(f"total time {time.time() - T0:.0f} s")
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
Path(__file__).with_suffix(".json").write_text(json.dumps(RES, indent=0, default=str), encoding="utf-8")
