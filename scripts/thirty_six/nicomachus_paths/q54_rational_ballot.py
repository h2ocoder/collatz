"""Q5.4  Rational-slope ballot numbers along the (semi)convergents of log2 3.

CONVENTIONS (stated once, used everywhere in this file)
  * Shortcut (Terras) map T(n) = n/2 (n even), (3n+1)/2 (n odd).
  * A dropping word of order s is a 0/1 word (1 = odd step) with exactly s ones such
    that every proper prefix with j letters and s_j ones has 2^j < 3^(s_j) and the
    whole word of length L has 2^L > 3^s.  Then L = floor(s*log2 3) + 1 = A020914(s).
    Paper-1 dropping time (3n+1 and n/2 counted separately) is k = L + s = A122437.
  * N(s) = number of dropping words of order s = OEIS A100982(s), offset 1.
  * Winkler / Beatty form:  N(s) = #{1 <= t_1 < ... < t_(s-1) : t_i <= floor(i*alpha)},
    alpha = log2 3, where t_i = number of letters before the (i+1)-th one.
  * For a rational slope a/b we use two boundaries:
        weak    m_i = floor(i*a/b)        (a lattice point ON the rational line is allowed)
        strict  m_i = ceil(i*a/b) - 1     (a lattice point ON the rational line is forbidden)
  * c_s(boundary) = #{1 <= t_1 < ... < t_(s-1) : t_i <= m_i}.

Everything is exact integer / Fraction arithmetic.  floor(i*log2 q) is computed as
(q**i).bit_length() - 1, which is exact because q**i is never a power of two.

Run:  python -I -X utf8 q54_rational_ballot.py     (about 1 minute)
Output: q54_rational_ballot.log, q54_rational_ballot.json
"""
import json
import os
import sys
from fractions import Fraction
from math import comb, gcd

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "q54_rational_ballot.log"), "w", encoding="utf-8")


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")


# ---------------------------------------------------------------- boundaries
def beatty(q, i):
    """floor(i*log2 q), exact (q odd >= 3)."""
    return (q ** i).bit_length() - 1


def weak(a, b, i):
    return (i * a) // b


def strict(a, b, i):
    return -((-i * a) // b) - 1


def counts(bound, R):
    """c_s for s = 1..R where bound(i) = m_i.  Returns list indexed by s (index 0 unused).

    DP over i: g[x] = number of increasing sequences t_1<...<t_i with t_i = x.
    c_(i+1) = sum_x g[x].
    """
    res = [None, 1]
    if R == 1:
        return res
    m1 = bound(1)
    g = [0] * (m1 + 2)
    for x in range(1, m1 + 1):
        g[x] = 1
    res.append(sum(g))
    for i in range(2, R):
        mi = bound(i)
        ng = [0] * (mi + 2)
        run = 0
        top = len(g) - 1
        for x in range(1, mi + 1):
            # ng[x] = sum_{y < x} g[y]
            if x - 1 <= top:
                run += g[x - 1]
            ng[x] = run
        g = ng
        res.append(sum(g))
    return res


# ---------------------------------------------------------------- continued fractions
def cf_log2(q, nterms):
    """Continued fraction of log2 q by exact integer comparisons of q^b vs 2^a."""
    # Use the Euclid-like algorithm on (log q, log 2) with exact tests: maintain
    # pairs (x, y) = (2^a1 / q^b1 ...) is awkward; instead use Stern-Brocot descent,
    # deciding a/b < log2 q  <=>  2^a < q^b  exactly.
    terms = []
    lo = (0, 1)   # lo < alpha   (as fractions a/b)
    hi = (1, 0)   # hi > alpha
    side = None
    run = 0
    while len(terms) < nterms:
        med = (lo[0] + hi[0], lo[1] + hi[1])
        below = (1 << med[0]) < q ** med[1]      # med < alpha
        this = "L" if below else "R"
        if below:
            lo = med
        else:
            hi = med
        if side is None:
            side, run = this, 1
        elif this == side:
            run += 1
        else:
            terms.append(run)
            side, run = this, 1
    # Stern-Brocot path R^a0 L^a1 R^a2 ... ; "below" means go right.  First run is of
    # 'L' type in our labelling (med < alpha -> lo moves), giving a0.
    return terms


def convergents(cf):
    P = [1, cf[0]]
    Q = [0, 1]
    for a in cf[1:]:
        P.append(a * P[-1] + P[-2])
        Q.append(a * Q[-1] + Q[-2])
    return P[1:], Q[1:]          # P_0/Q_0, P_1/Q_1, ...


def one_sided_best(q, maxden):
    """Strict record minima / maxima of the fractional part {r*log2 q}, r = 1..maxden.

    Exact: {r*alpha} < {j*alpha}  <=>  q^r / 2^m_r < q^j / 2^m_j.
    Returns (lower_orders, upper_orders) = Winkler's L_q and U_q.
    """
    lower, upper = [], []
    best_lo = None    # Fraction of the smallest mantissa so far
    best_hi = None
    for r in range(1, maxden + 1):
        mant = Fraction(q ** r, 1 << beatty(q, r))     # in (1,2);  = 2^{frac}
        if best_lo is None or mant < best_lo:
            best_lo = mant
            lower.append(r)
        if best_hi is None or mant > best_hi:
            best_hi = mant
            upper.append(r)
    return lower, upper


# ---------------------------------------------------------------- Bizley
def bizley(m, n, K):
    """Bizley (1954).  gcd(m,n)=1.  Returns (phi, psi), lists indexed 0..K.

    phi[k] = number of lattice paths (0,0)->(km,kn) that never rise above the line
             joining the endpoints (touching allowed).
    psi[k] = number of such paths that touch the line only at the two endpoints.
    sum phi_k t^k = exp(sum_j F_j t^j),  F_j = C(j(m+n), jm) / (j(m+n)),
    sum psi_k t^k = 1 - exp(-sum_j F_j t^j).
    """
    assert gcd(m, n) == 1
    F = [Fraction(0)] + [Fraction(comb(j * (m + n), j * m), j * (m + n)) for j in range(1, K + 1)]

    def exp_series(G):
        E = [Fraction(1)] + [Fraction(0)] * K
        for k in range(1, K + 1):
            E[k] = sum(j * G[j] * E[k - j] for j in range(1, k + 1)) / k
        return E

    phi = exp_series(F)
    neg = exp_series([-x for x in F])
    psi = [Fraction(0)] + [-neg[k] for k in range(1, K + 1)]
    assert all(x.denominator == 1 for x in phi + psi)
    return [int(x) for x in phi], [int(x) for x in psi]


def brute_paths(m, n, k, strict_inside):
    """Brute-force check of bizley(): count N/E paths (0,0)->(km,kn) below the diagonal."""
    X, Y = k * m, k * n            # x = east total, y = north total; stay with y*X <= x*Y
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def go(x, y):
        if (x, y) == (X, Y):
            return 1
        tot = 0
        for nx, ny in ((x + 1, y), (x, y + 1)):
            if nx > X or ny > Y:
                continue
            lhs, rhs = ny * X, nx * Y
            if lhs > rhs:
                continue
            if strict_inside and lhs == rhs and (nx, ny) != (X, Y):
                continue
            tot += go(nx, ny)
        return tot

    return go(0, 0)


# ---------------------------------------------------------------- main
def main():
    results = {}
    R = 1000
    out("=" * 78)
    out("Q5.4  rational-slope ballot numbers vs A100982")
    out("convention: shortcut map; order s = number of odd steps; N(s) = A100982(s)")
    out("=" * 78)

    # ---- (0) exact N(s) and comparison with the OEIS b-file
    N = counts(lambda i: beatty(3, i), R)
    out("\n[0] N(s), s = 1..20:", N[1:21])
    bpath = os.path.join(HERE, "oeis_data", "b100982.txt")
    if os.path.exists(bpath):
        b = {}
        for line in open(bpath, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            k, v = line.split()[:2]
            b[int(k)] = int(v)
        bad = [s for s in range(1, R + 1) if b.get(s) != N[s]]
        out(f"    compared with OEIS b100982.txt (downloaded 2026-10-06, {len(b)} terms): "
            f"s = 1..{R}: {'ALL AGREE' if not bad else 'MISMATCH at ' + str(bad[:5])}")
        results["bfile_agree_upto"] = R if not bad else bad[0] - 1
    else:
        out("    (b-file not present; skipped)")

    # ---- (1) continued fraction, convergents, one-sided best approximations
    cf = cf_log2(3, 12)
    P, Q = convergents(cf)
    out("\n[1] log2 3 = [", "; ".join(str(x) for x in cf), "...]")
    out("    convergents P_n/Q_n:", ", ".join(f"{p}/{q}" for p, q in zip(P, Q)))
    for p, q in zip(P, Q):
        assert ((1 << p) < 3 ** q) or ((1 << p) > 3 ** q)
    lower, upper = one_sided_best(3, R)
    out("    lower equality orders L_3 (strict record minima of {s*log2 3}), s <= 1000:", lower)
    out("    upper equality orders U_3 (strict record maxima), s <= 1000:", upper)
    results["L3"] = lower
    results["U3"] = upper

    # ---- (2) Winkler's sandwich and its equality set (independent re-verification)
    out("\n[2] Winkler sandwich  C(m-1,s-1)/s <= N(s) <= C(m,s-1)/s,  m = floor(s log2 3)")
    lo_eq, up_eq, viol = [], [], []
    for s in range(1, R + 1):
        m = beatty(3, s)
        lo = Fraction(comb(m - 1, s - 1), s)
        up = Fraction(comb(m, s - 1), s)
        if not (lo <= N[s] <= up):
            viol.append(s)
        if N[s] == lo:
            lo_eq.append(s)
        if N[s] == up:
            up_eq.append(s)
    out("    violations for s <= 1000:", viol)
    out("    lower equality at s =", lo_eq)
    out("    upper equality at s =", up_eq)
    out("    lower equality set == L_3 :", lo_eq == lower)
    out("    upper equality set == U_3 :", up_eq == upper)
    results["sandwich_violations"] = viol
    results["lower_eq_matches_L3"] = lo_eq == lower
    results["upper_eq_matches_U3"] = up_eq == upper

    # ---- (3) agreement windows for the slopes named in the task, both conventions
    out("\n[3] Agreement windows.  For slope a/b:  c_s(a/b) = N(s) exactly for s <= W.")
    out("    predicted W for a one-sided best approximation in its natural convention")
    out("    (lower: weak, upper: strict) = next order on the same side in L_3 / U_3;")
    out("    in the other convention W = b.")
    slopes = [(1, 1), (2, 1), (3, 2), (5, 3), (8, 5), (11, 7), (19, 12), (27, 17), (46, 29),
              (65, 41), (84, 53), (149, 94), (485, 306), (7, 4), (13, 8), (30, 19), (49, 31)]
    out(f"    {'a/b':>8} {'side':>6} {'best?':>6} {'W weak':>7} {'W strict':>8} {'predicted (natural)':>20} {'ok':>4}")
    win = {}
    allok = True
    for a, b in slopes:
        side = "lower" if (1 << a) < 3 ** b else "upper"
        cw = counts(lambda i: weak(a, b, i), R)
        cs = counts(lambda i: strict(a, b, i), R)
        Ww = next((s - 1 for s in range(1, R + 1) if cw[s] != N[s]), None)
        Ws = next((s - 1 for s in range(1, R + 1) if cs[s] != N[s]), None)
        lst = lower if side == "lower" else upper
        is_best = b in lst and ((side == "lower" and a == beatty(3, b)) or
                                (side == "upper" and a == beatty(3, b) + 1))
        pred = None
        if is_best:
            idx = lst.index(b)
            # for b = 1 the list contains 1 once; the successor is the next entry
            pred = lst[idx + 1] if idx + 1 < len(lst) else None
        natural = Ww if side == "lower" else Ws
        other = Ws if side == "lower" else Ww
        ok = ""
        if is_best and pred is not None:
            ok = "yes" if (natural == pred and other == b) else "NO"
            if ok == "NO":
                # b = 1 lower (slope 1/1, strict boundary is empty) is a degenerate case
                allok = False
        out(f"    {a:>4}/{b:<3} {side:>6} {str(is_best):>6} {str(Ww):>7} {str(Ws):>8} {str(pred):>20} {ok:>4}")
        win[f"{a}/{b}"] = {"side": side, "best": is_best, "W_weak": Ww, "W_strict": Ws, "pred": pred}
        # check: beyond the window the counts differ for EVERY later s (one-sidedness)
        if natural is not None:
            c = cw if side == "lower" else cs
            assert all(c[s] != N[s] for s in range(natural + 1, R + 1))
            if side == "lower":
                assert all(c[s] < N[s] for s in range(natural + 1, R + 1))
            else:
                assert all(c[s] > N[s] for s in range(natural + 1, R + 1))
    out("    all predictions for one-sided best approximations confirmed:", allok)
    results["windows"] = win
    results["windows_all_predicted"] = allok

    # ---- (3b) the same for EVERY one-sided best approximation with denominator <= 400
    chk = []
    for lst, side in ((lower, "lower"), (upper, "upper")):
        for idx, b in enumerate(lst[:-1]):
            if b > 400:
                break
            a = beatty(3, b) + (0 if side == "lower" else 1)
            bd = (lambda i, a=a, b=b: weak(a, b, i)) if side == "lower" else (lambda i, a=a, b=b: strict(a, b, i))
            c = counts(bd, R)
            W = next((s - 1 for s in range(1, R + 1) if c[s] != N[s]), None)
            chk.append((side, f"{a}/{b}", W, lst[idx + 1], W == lst[idx + 1]))
    out("\n[3b] every one-sided best approximation with denominator <= 400:")
    for row in chk:
        out("     ", row)
    out("     all windows equal the next same-side order:", all(r[4] for r in chk))
    results["windows_every_best_approx"] = all(r[4] for r in chk)

    # ---- (4) Bizley closed forms inside the windows, at multiples of convergent denominators
    out("\n[4] Bizley closed forms at s = k*Q_n, k <= 1 + floor(Q_(n+1)/Q_n)")
    out("    lower convergent P/Q: N(kQ) = phi_k(P-Q, Q)   (paths may touch the line)")
    out("    upper convergent P/Q: N(kQ) = psi_k(P-Q, Q)   (paths touch only at the ends)")
    # sanity check of the Bizley implementation against brute force
    for (m, n) in ((1, 2), (3, 5), (2, 3), (1, 1)):
        phi, psi = bizley(m, n, 4)
        for k in range(1, 5):
            assert phi[k] == brute_paths(m, n, k, False), (m, n, k)
            assert psi[k] == brute_paths(m, n, k, True), (m, n, k)
    out("    (bizley() checked against brute-force path enumeration for (1,2),(3,5),(2,3),(1,1), k<=4)")
    biz_rows = []
    allb = True
    new_orders = []
    for n_idx in range(0, len(Q) - 1):
        p, q = P[n_idx], Q[n_idx]
        if q > R:
            break
        qn1 = Q[n_idx + 1]
        side = "lower" if (1 << p) < 3 ** q else "upper"
        kmax = 1 + qn1 // q
        kmax_eff = min(kmax, R // q)
        if p - q == 0:
            # slope 1/1: degenerate rectangle (no east steps); N(k) = 1 trivially
            for k in range(1, kmax_eff + 1):
                ok = N[k * q] == 1
                allb &= ok
                biz_rows.append((f"{p}/{q}", side, k, k * q, "1 (degenerate)", ok))
            continue
        phi, psi = bizley(p - q, q, kmax_eff + 1)
        for k in range(1, kmax_eff + 2):
            if k * q > R:
                break
            val = phi[k] if side == "lower" else psi[k]
            ok = N[k * q] == val
            inside = k <= kmax
            if inside:
                allb &= ok
                if (k * q) not in lower and (k * q) not in upper:
                    new_orders.append(k * q)
            biz_rows.append((f"{p}/{q}", side, k, k * q,
                             str(val) if val < 10 ** 30 else f"{str(val)[:12]}...({len(str(val))} digits)",
                             ok if inside else f"outside window: {ok}"))
    for row in biz_rows:
        out("     ", row)
    out("    all in-window Bizley identities hold:", allb)
    new_orders = sorted(set(new_orders))
    out("    orders s <= 1000 with a Bizley closed form that are NOT Winkler equality orders:", new_orders)
    results["bizley_all_hold"] = allb
    results["bizley_new_orders"] = new_orders

    # explicit small ones, spelled out
    F = lambda m, n, j: Fraction(comb(j * (m + n), j * m), j * (m + n))
    out("\n    spelled out, with F_j = C(j(m+n), jm) / (j(m+n)):")
    f1, f2, f3 = F(3, 5, 1), F(3, 5, 2), F(3, 5, 3)
    out(f"      (m,n)=(3,5)  [8/5, upper]: F1={f1}, F2={f2}, F3={f3}")
    out(f"        N(10) = F2 - F1^2/2            = {f2 - f1**2/2}   (A100982(10) = {N[10]})")
    out(f"        N(15) = F3 - F1*F2 + F1^3/6    = {f3 - f1*f2 + f1**3/6}   (A100982(15) = {N[15]})")
    g1, g2, g3, g4 = (F(7, 12, j) for j in (1, 2, 3, 4))
    v24 = g2 + g1 ** 2 / 2
    v36 = g3 + g1 * g2 + g1 ** 3 / 6
    v48 = g4 + g1 * g3 + g2 ** 2 / 2 + g1 ** 2 * g2 / 2 + g1 ** 4 / 24
    out(f"      (m,n)=(7,12) [19/12, lower]: F1={g1}")
    out(f"        N(24) = F2 + F1^2/2                         = {v24}   ok={v24 == N[24]}")
    out(f"        N(36) = F3 + F1*F2 + F1^3/6                 = {v36}   ok={v36 == N[36]}")
    out(f"        N(48) = F4 + F1*F3 + F2^2/2 + F1^2*F2/2 + F1^4/24 = {v48}   ok={v48 == N[48]}")
    results["N36"] = str(N[36])
    results["N36_bizley_ok"] = (v36 == N[36])

    # ---- (5) first terms of each rational sequence (for OEIS identification)
    out("\n[5] first 22 terms of c_s(a/b) (natural convention) -- for OEIS lookup")
    seqs = {}
    for a, b, conv in ((1, 1, "weak"), (2, 1, "strict"), (2, 1, "weak"), (3, 2, "weak"), (3, 2, "strict"),
                       (5, 3, "strict"), (5, 3, "weak"), (8, 5, "strict"), (8, 5, "weak"),
                       (11, 7, "weak"), (19, 12, "weak")):
        bd = (lambda i: weak(a, b, i)) if conv == "weak" else (lambda i: strict(a, b, i))
        c = counts(bd, 60)
        seqs[f"{a}/{b} {conv}"] = [str(x) for x in c[1:31]]
        out(f"    {a}/{b} {conv:>6}: {c[1:23]}")
    c85 = counts(lambda i: strict(8, 5, i), 60)
    out("    8/5 strict, s = 16..24:", c85[16:25])
    out("    A100982,    s = 16..24:", N[16:25])
    results["rational_sequences"] = seqs

    # 3/2 weak == A047749 (shifted by 2)?
    def A047749(n):
        m = n // 2
        return comb(3 * m, m) // (2 * m + 1) if n % 2 == 0 else comb(3 * m + 1, m + 1) // (2 * m + 1)
    c32 = counts(lambda i: weak(3, 2, i), 400)
    ok32 = all(c32[s] == A047749(s) for s in range(1, 401))
    out(f"\n    c_s(3/2 weak) == A047749(s) for s = 1..400: {ok32}")
    out("      i.e. N(s) = C(3m,m)/(2m+1) for s = 2m and C(3m+1,m+1)/(2m+1) for s = 2m+1, valid for s <= 7")
    c32s = counts(lambda i: strict(3, 2, i), 400)
    ok32s = all(c32s[s] == A047749(s - 1) for s in range(1, 401))
    out(f"    c_s(3/2 strict) == A047749(s-1) for s = 1..400: {ok32s}")
    c21 = counts(lambda i: strict(2, 1, i), 200)
    cat = lambda n: comb(2 * n, n) // (n + 1)
    out("    c_s(2/1 strict) == Catalan(s-1) for s = 1..200:", all(c21[s] == cat(s - 1) for s in range(1, 201)))
    c21w = counts(lambda i: weak(2, 1, i), 200)
    out("    c_s(2/1 weak)   == Catalan(s)   for s = 1..200:", all(c21w[s] == cat(s) for s in range(1, 201)))
    results["A047749_match"] = ok32
    # classical ballot theorem with INTEGER slope mu = 2 (the excess slope 1/2 of 3/2 is 1/mu):
    # paths to (x, y), x east / y north, with x' >= mu*y' throughout:  (x - mu*y + 1)/(x + y + 1) * C(x+y+1, y)
    def ballot2(s):
        x, y = s, s // 2
        return Fraction((x - 2 * y + 1) * comb(x + y + 1, y), x + y + 1)
    okb = all(c32[s] == ballot2(s) for s in range(1, 401))
    out(f"    c_s(3/2 weak) == (s - 2h + 1)/(s + h + 1) * C(s+h+1, h), h = floor(s/2), s = 1..400: {okb}")
    out("      => closed form for EVERY s <= 7:", [int(ballot2(s)) for s in range(1, 8)], "= A100982(1..7);",
        "s = 8 gives", int(ballot2(8)), "!= 85")
    results["ballot_slope2_match"] = okb
    # the sequences attached to slope 5/3 in OEIS
    c53w = counts(lambda i: weak(5, 3, i), 40)
    c53s = counts(lambda i: strict(5, 3, i), 40)
    phi23, psi23 = bizley(2, 3, 8)
    out("    c_(3k)(5/3 weak)   k=1..6:", [c53w[3 * k] for k in range(1, 7)], " = Duchon numbers A060941 (phi_k(2,3)):",
        [c53w[3 * k] for k in range(1, 7)] == phi23[1:7])
    out("    c_(3k)(5/3 strict) k=1..6:", [c53s[3 * k] for k in range(1, 7)], " = A293946 (psi_k(2,3)):",
        [c53s[3 * k] for k in range(1, 7)] == psi23[1:7])
    out("      (slope 5/3 is an upper semiconvergent; its strict count agrees with A100982 only for s <= 5,")
    out("       so the only Duchon-type value that is a value of A100982 at the same order is c_3 = 2.)")

    # ---- (6) mirror: 5x+1 and 7x+1 (the same theorem with log2 5, log2 7)
    out("\n[6] cousins qx+1: c_s(log2 q)")
    for qq, bname in ((5, "b174795.txt"), (7, "b174796.txt")):
        cq = counts(lambda i: beatty(qq, i), 400)
        out(f"    q={qq}: first terms {cq[1:11]}")
        bp = os.path.join(HERE, "oeis_data", bname)
        if os.path.exists(bp):
            bb = {}
            for line in open(bp, encoding="utf-8"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                k, v = line.split()[:2]
                bb[int(k)] = int(v)
            bad = [s for s in sorted(bb) if s <= 400 and bb[s] != cq[s]]
            out(f"      OEIS {bname}: {len(bb)} terms, mismatches: {bad}")
        lo5, up5 = one_sided_best(qq, 400)
        cfq = cf_log2(qq, 8)
        out(f"      log2 {qq} = {cfq}; L_{qq} = {lo5[:12]}, U_{qq} = {up5[:12]}")
        loeq = [s for s in range(1, 401) if Fraction(comb(beatty(qq, s) - 1, s - 1), s) == cq[s]]
        upeq = [s for s in range(1, 401) if Fraction(comb(beatty(qq, s), s - 1), s) == cq[s]]
        out(f"      sandwich equality sets match L/U: {loeq == lo5}, {upeq == up5}")
        # window check for each best approx
        okw = True
        for lst, side in ((lo5, "lower"), (up5, "upper")):
            for idx, b in enumerate(lst[:-1]):
                if b > 150:
                    break
                a = beatty(qq, b) + (0 if side == "lower" else 1)
                bd = (lambda i, a=a, b=b: weak(a, b, i)) if side == "lower" else (lambda i, a=a, b=b: strict(a, b, i))
                c = counts(bd, 400)
                W = next((s - 1 for s in range(1, 401) if c[s] != cq[s]), None)
                okw &= (W == lst[idx + 1])
        out(f"      window = next same-side order, all best approximations with b <= 150: {okw}")
        results[f"q{qq}_windows_ok"] = okw

    # ---- (7) where do the unit cells (Gersonides pairs) sit?
    out("\n[7] Gersonides pairs and the first three convergents")
    for p, q in zip(P[:5], Q[:5]):
        out(f"    {p}/{q}: 2^{p} = {1 << p}, 3^{q} = {3 ** q}, difference 2^p - 3^q = {(1 << p) - 3 ** q}")
    out("    |2^P - 3^Q| = 1 exactly for the convergents 1/1, 2/1, 3/2 (pairs (2,3), (3,4), (8,9)).")
    out("    Their rational counts leave A100982 after s = 2, 3, 7; the lattice point that")
    out("    separates the lines is the next same-side semiconvergent: 3/2, 5/3, 11/7.")

    json.dump(results, open(os.path.join(HERE, "q54_rational_ballot.json"), "w"), indent=1)
    out("\nwrote q54_rational_ballot.json")


if __name__ == "__main__":
    main()
    LOG.close()
