"""Q3.4 / Q3.2 extension: scan of ALL primes 5 <= p <= P_MAX for Kronecker-type eigenvalues beyond the theorem,
for both the Terras kernel (A^+ = R_e + R_o) and the sign-twisted kernel (A^- = R_e - R_o).

Method (sound for the 'nothing else' direction).  The characteristic polynomial is computed modulo two 24-bit
primes r1, r2 (Hessenberg).  Over Z we know the forced factors:
     A^+ : (x - 2) * x^z+ * (x^m - (-1)^(m+t))^idx          (the last one only if ord_p(3) is even),
     A^- : x * x^z- * (x^m - (-1)^m)^idx                      (always: -1 is an eigenvalue of A^- on every block),
with m = order of 2 modulo <3>, 2^m = 3^t, idx = [(Z/p)^x : <2,3>], z+ = number of even cycles of y -> 3y + 1/2,
z- = (p-1)/ord_p(3).  After dividing these out modulo r, the cofactor is tested for every further Kronecker factor:
     x,  x -+ 1,  Phi_k (3 <= k <= KMAX),  Psi_j (5 <= j <= KMAX, j != 6),  and x^m - c (2 <= |c| <= CMAX).
If a polynomial F divides the cofactor over Z then it divides it modulo every prime, so 'no hit modulo r1'
PROVES there is no such factor.  A hit modulo both r1 and r2 is reported as a sporadic event (and is confirmed
exactly by the census q32 for p <= 400).

Run:  python -X utf8 q34b_sporadic_scan.py [P_MAX=800] [KMAX=60]    (writes q34b_sporadic_scan.log / .json)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gk_common import charpoly_mod, cyclotomic, order, primes_upto, psi, two_K  # noqa: E402

P_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 800
KMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 60
CMAX = 400
RS = (16777213, 16777199)
T0 = time.time()
LOG: list[str] = []


def say(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def pdivmod_mod(a: np.ndarray, b: list[int], r: int) -> tuple[np.ndarray, np.ndarray]:
    """a / b modulo r for a MONIC b (coefficient lists ascending); returns (quotient, remainder)."""
    a = a.copy() % r
    bb = np.array(b, dtype=np.int64) % r
    db = len(bb) - 1
    da = len(a) - 1
    if da < db:
        return np.zeros(1, dtype=np.int64), a
    q = np.zeros(da - db + 1, dtype=np.int64)
    for i in range(da, db - 1, -1):
        c = int(a[i])
        if c:
            q[i - db] = c
            a[i - db : i + 1] = (a[i - db : i + 1] - c * bb) % r
    return q, a[:db] if db else np.zeros(1, dtype=np.int64)


def mult_mod(a: np.ndarray, b: list[int], r: int) -> tuple[int, np.ndarray]:
    k = 0
    while len(a) - 1 >= len(b) - 1:
        q, rem = pdivmod_mod(a, b, r)
        if rem.any():
            break
        a, k = q, k + 1
    return k, a


def binom_poly(m: int, c: int) -> list[int]:
    return [-c] + [0] * (m - 1) + [1]


CANDS: list[tuple[str, list[int]]] = [("x", [0, 1]), ("x-1", [-1, 1]), ("x+1", [1, 1])]
CANDS += [(f"Phi_{k}", cyclotomic(k)) for k in range(3, KMAX + 1)]
CANDS += [(f"Psi_{j}", psi(j)) for j in range(5, KMAX + 1) if j != 6]

events = []
rows = []
PRIMES = [q for q in primes_upto(P_MAX) if q >= 5]
for p in PRIMES:
    tp = time.time()
    o3 = order(3, p)
    pw, xx = {}, 1
    for t in range(o3):
        pw[xx] = t
        xx = xx * 3 % p
    m_, yy = 1, 2
    while yy not in pw:
        yy = yy * 2 % p
        m_ += 1
    t_ = pw[yy]
    idx = (p - 1) // (o3 * m_)
    z_plus = (p - 1) // o3 if o3 % 2 == 0 else 0
    z_minus = (p - 1) // o3
    row = {"p": p, "m": m_, "t": t_, "idx": idx, "ord3": o3}
    for sign in (1, -1):
        A = two_K(p, sign=sign)
        hits_by_r = []
        for r in RS:
            cp = charpoly_mod(A, r)
            # forced factors
            q, rem = pdivmod_mod(cp, [-2, 1] if sign == 1 else [0, 1], r)
            assert not rem.any()
            cof = q
            z = z_plus if sign == 1 else z_minus
            for _ in range(z):
                cof, rem = pdivmod_mod(cof, [0, 1], r)
                assert not rem.any(), (p, sign, "zero multiplicity below the geometric one")
            if sign == 1 and o3 % 2 == 0:
                forced = binom_poly(m_, (-1) ** (m_ + t_))
            elif sign == -1:
                forced = binom_poly(m_, (-1) ** m_)
            else:
                forced = None
            if forced is not None:
                for _ in range(idx):
                    cof, rem = pdivmod_mod(cof, forced, r)
                    assert not rem.any(), (p, sign, "theorem factor missing")
            hits = {}
            for name, pol in CANDS:
                if len(pol) - 1 <= len(cof) - 1:
                    k, _ = mult_mod(cof, pol, r)
                    if k:
                        hits[name] = k
            # binomial x^m - c, |c| >= 2: cof is a polynomial in x^m times a power of x (check on its support)
            sup = np.nonzero(cof)[0]
            if len(sup) and all((int(i) - int(sup[0])) % m_ == 0 for i in sup):
                gy = cof[int(sup[0]) :: m_]
                lim = min(2 ** m_ - 1, CMAX)
                if lim >= 2:
                    cs = np.array([c for c in range(-lim, lim + 1) if abs(c) >= 2], dtype=np.int64)
                    val = np.zeros(len(cs), dtype=np.int64)
                    for coef in gy[::-1]:
                        val = (val * cs + int(coef)) % r
                    for c in cs[val == 0].tolist():
                        hits[f"x^{m_}={c}"] = 1
            hits_by_r.append(hits)
        common = {k: min(hits_by_r[0][k], hits_by_r[1][k]) for k in hits_by_r[0] if k in hits_by_r[1]}
        row["plus" if sign == 1 else "minus"] = common
        if common:
            events.append((p, sign, common))
    rows.append(row)
    msg = f"p = {p:>3} (m,t,idx) = ({m_},{t_},{idx}) ord3 {o3:>3} | K: {row['plus'] or '-'} | K^-: {row['minus'] or '-'}  [{time.time() - tp:.1f}s, total {time.time() - T0:.0f}s]"
    if row["plus"] or row["minus"] or p % 50 < 4:
        say(msg)

say("\n================ SUMMARY ================")
say(f"primes 5 <= p <= {P_MAX}: {len(PRIMES)}; candidates beyond the forced factors: x, x-+1, Phi_k (k <= {KMAX}), Psi_j (j <= {KMAX}), x^m = c (2 <= |c| <= min(2^m - 1, {CMAX}))")
say("events for the Terras kernel K   (p, extra factors of charpoly(2K)): " + str([(p, c) for p, s, c in events if s == 1]))
say("events for the signed kernel K^- (p, extra factors of charpoly(2K^-)): " + str([(p, c) for p, s, c in events if s == -1]))
say("   (for ord_p(3) even, K^- is a character twist of K, spec K = chi(2) spec K^-, so its events are the same ones rotated; new information only for ord_p(3) odd)")
odd3 = [(p, c) for p, s, c in events if s == -1 and order(3, p) % 2 == 1]
say(f"   K^- events at primes with ord_p(3) odd: {odd3}")
last = max([p for p, s, c in events], default=None)
say(f"largest prime with any event: {last};  primes above it scanned without any event: {sum(1 for q in PRIMES if last is not None and q > last)}")
say(f"total time {time.time() - T0:.0f} s")
Path(__file__).with_suffix(".log").write_text("\n".join(LOG) + "\n", encoding="utf-8")
Path(__file__).with_suffix(".json").write_text(json.dumps({"P_MAX": P_MAX, "KMAX": KMAX, "events": [{"p": p, "sign": s, "factors": c} for p, s, c in events], "rows": rows}, indent=0), encoding="utf-8")
