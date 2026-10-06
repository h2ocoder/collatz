"""Skeptic check 4 (Q5.0, Q5.4-a..g, Q5.x) -- path side, independent code paths.

Three independent ways to get the counts:
  (W) brute-force enumeration of words (small s);
  (Z) Zarubin's inclusion-exclusion recursion (OEIS A100982, Theorem 1), generalised to an
      arbitrary boundary m_i:   c(k+1) = sum_{m=1..k} (-1)^(m-1) C(m_(k-m+1) + m - 1, m) c(k-m+1);
  (D) row DP on words: A(j,i) = [cond(j,i)] (A(j-1,i-1) + A(j-1,i)), c_s = sum_j A(j, s-1),
      with cond tested by exact integer comparison (2^j < 3^i, or j*b <= a*i / j*b < a*i).
Bizley values are checked against a direct 2-D lattice-path DP (never rise above / touch only
at the ends) and against Bizley's formula written as a sum over partitions of k.

Conventions: shortcut map; s = number of odd steps; N(s) = A100982(s) (offset 1).
'weak'  : prefix (j letters, i ones) allowed iff j*b <= a*i   (m_i = floor(i a/b))
'strict': allowed iff j*b <  a*i                               (m_i = ceil(i a/b) - 1)

Run: python -I -X utf8 v4_paths_independent.py    (reads ../oeis_data, data only; ~3-5 min)
"""
import os
import sys
import time
from fractions import Fraction
from math import comb, factorial, gcd

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v4_paths_independent.log"), "w", encoding="utf-8")
T0 = time.time()


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")
    LOG.flush()


# ------------------------------------------------------------------ boundaries
def true_bound(q):
    """i -> largest j with 2^j < q^i, found by stepping (no bit_length)."""
    cache = {0: 0}
    state = {"i": 0, "j": 0, "pw": 1}

    def f(i):
        while state["i"] < i:
            state["i"] += 1
            state["pw"] *= q
            j = state["j"]
            while (1 << (j + 1)) < state["pw"]:
                j += 1
            state["j"] = j
            cache[state["i"]] = j
        return cache[i]
    return f


def weak(a, b):
    return lambda i: (i * a) // b


def strict(a, b):
    return lambda i: (i * a - 1) // b          # largest j with j*b < a*i


# ------------------------------------------------------------------ three counters
def count_D(bound, S):
    res = [None, 1]
    prev = [1]
    for i in range(1, S):
        jm = bound(i)
        row = [0] * (jm + 1)
        run = 0
        lp = len(prev)
        for j in range(1, jm + 1):
            if j - 1 < lp:
                run += prev[j - 1]
            row[j] = run
        prev = row
        res.append(sum(row))
    return res


def count_Z(bound, S):
    c = [None, 1]
    for k in range(1, S):
        tot = 0
        for m in range(1, k + 1):
            term = comb(bound(k - m + 1) + m - 1, m) * c[k - m + 1]
            tot += term if m % 2 == 1 else -term
        c.append(tot)
    return c


def words_W(cond, s, q_final=None):
    """All words with s ones: every proper non-empty prefix satisfies cond, the word ends at the
    first failure of cond (which must happen right after a 0).  Returns the list of words."""
    res = []

    def rec(w, j, i):
        # w is an admissible prefix with j letters, i ones (every non-empty prefix satisfies cond)
        if i < s and cond(j + 1, i + 1):
            rec(w + "1", j + 1, i + 1)
        if cond(j + 1, i):
            rec(w + "0", j + 1, i)
        elif i == s:
            res.append(w + "0")          # first failure of cond, with all s ones used: a dropping word
    rec("", 0, 0)
    return res


# ------------------------------------------------------------------ helpers
def records(q, R):
    """strict record minima / maxima of {r log2 q}, exact."""
    tb = true_bound(q)
    lo, up = [], []
    bl = bu = None       # (q^r, m_r)
    pw = 1
    for r in range(1, R + 1):
        pw *= q
        m = tb(r)
        if bl is None or pw << bl[1] < bl[0] << m:
            bl = (pw, m)
            lo.append(r)
        if bu is None or pw << bu[1] > bu[0] << m:
            bu = (pw, m)
            up.append(r)
    return lo, up


def path_count(X, Y, strict_inside):
    """E/N lattice paths (0,0)->(X,Y) with y*X <= x*Y at every point; if strict_inside the
    line may be met only at the two ends."""
    col = [0] * (Y + 1)
    col[0] = 1
    for x in range(0, X + 1):
        new = [0] * (Y + 1)
        for y in range(0, Y + 1):
            if x == 0 and y == 0:
                new[0] = 1
                continue
            lhs, rhs = y * X, x * Y
            if lhs > rhs:
                break
            if strict_inside and lhs == rhs and (x, y) != (X, Y):
                continue
            v = col[y] if x > 0 else 0
            if y > 0:
                v += new[y - 1]
            new[y] = v
        col = new
    return col[Y]


def partitions(n, mx=None):
    if mx is None:
        mx = n
    if n == 0:
        yield []
        return
    for p in range(min(n, mx), 0, -1):
        for rest in partitions(n - p, p):
            yield [p] + rest


def bizley_partition(m, n, k, strict_inside):
    """Bizley 1954 via partitions of k: phi_k = sum prod F_j^{c_j}/c_j!,
    psi_k = sum (-1)^(sum c_j - 1) prod F_j^{c_j}/c_j!,  F_j = C(j(m+n), jm)/(j(m+n))."""
    F = {j: Fraction(comb(j * (m + n), j * m), j * (m + n)) for j in range(1, k + 1)}
    tot = Fraction(0)
    for part in partitions(k):
        mult = {}
        for p in part:
            mult[p] = mult.get(p, 0) + 1
        term = Fraction(1)
        for j, c in mult.items():
            term *= F[j] ** c / factorial(c)
        if strict_inside and (sum(mult.values()) - 1) % 2 == 1:
            term = -term
        tot += term
    assert tot.denominator == 1
    return int(tot)


def read_b(name):
    d = {}
    p = os.path.join(HERE, "..", "oeis_data", name)
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#"):
            a, b = line.split()[:2]
            d[int(a)] = int(b)
    return d


def main():
    R = 2218
    # ---------------------------------------------------------------- [0] N(s) three ways
    out("[0] N(s) three ways")
    tb3 = true_bound(3)
    ND = count_D(tb3, R)
    out(f"    DP to s = {R} done ({time.time()-T0:.0f}s); N(1..14) = {ND[1:15]}")
    NZ = count_Z(tb3, 700)
    out(f"    Zarubin recursion to s = 700 agrees with DP: {NZ[1:] == ND[1:701]}  ({time.time()-T0:.0f}s)")
    okW = True
    allwords = {}
    for s in range(1, 15):
        ws = words_W(lambda j, i: (1 << j) < 3 ** i, s)
        allwords[s] = ws
        okW &= len(ws) == ND[s] and all(len(w) == tb3(s) + 1 for w in ws)
    out("    brute-force word enumeration s = 1..14 agrees (count and length L = floor(s log2 3)+1):", okW)
    b = read_b("b100982.txt")
    bad = [s for s in range(1, R + 1) if b.get(s) != ND[s]]
    out(f"    researcher's copy of the OEIS b-file ({len(b)} terms): mismatches for s <= {R}: {bad[:5]}")
    oeis_page = [1, 1, 2, 3, 7, 12, 30, 85, 173, 476, 961, 2652, 8045, 17637, 51033, 108950, 312455, 663535,
                 1900470, 5936673, 13472296, 39993895, 87986917, 257978502, 820236724, 1899474678, 5723030586,
                 12809477536, 38036848410, 84141805077, 248369601964, 794919136728]
    out("    32 data terms read by the skeptic from oeis.org/A100982 on 2026-10-06 agree:", ND[1:33] == oeis_page)

    # ---------------------------------------------------------------- [1] sandwich / equality sets
    lo3, up3 = records(3, R)
    out("\n[1] record orders: L_3 =", lo3, " U_3 =", up3)
    viol, loeq, upeq = [], [], []
    for s in range(1, R + 1):
        m = tb3(s)
        if not (comb(m - 1, s - 1) <= s * ND[s] <= comb(m, s - 1)):
            viol.append(s)
        if comb(m - 1, s - 1) == s * ND[s]:
            loeq.append(s)
        if comb(m, s - 1) == s * ND[s]:
            upeq.append(s)
    out(f"    sandwich violations s <= {R}: {viol}; lower-equality set == L_3: {loeq == lo3}; upper == U_3: {upeq == up3}")
    # rational Catalan values at equality orders (Winkler Thm 8)
    okc = all(ND[s] * tb3(s) == comb(tb3(s), s) for s in lo3 if s >= 2) and \
        all(ND[s] * (tb3(s) + 1) == comb(tb3(s) + 1, s) for s in up3 if s >= 2)
    out("    N(s) = C(m,s)/m on L_3 and C(m+1,s)/(m+1) on U_3 (s >= 2):", okc)

    # ---------------------------------------------------------------- [2] windows
    out("\n[2] windows: first s with c_s(a/b) != N(s), minus 1")
    out("    cross-check of the three counters on rational boundaries (s <= 60 for Z, s <= 11 for W):")
    okx = True
    for a, bb in ((3, 2), (8, 5), (5, 3), (2, 1), (11, 7), (19, 12), (1, 1), (7, 4), (6, 4)):
        for nm, bd, cond in (("weak", weak(a, bb), lambda j, i, a=a, bb=bb: j * bb <= a * i),
                             ("strict", strict(a, bb), lambda j, i, a=a, bb=bb: j * bb < a * i)):
            d = count_D(bd, 60)
            z = count_Z(bd, 60)
            okx &= d == z
            if not (a == bb and nm == "strict"):
                for s in range(1, 12):
                    # words: admissible prefixes with s-1 ones = c_s ; enumerate them directly
                    cnt = 0

                    def rec(j, i):
                        nonlocal cnt
                        if i == s - 1:
                            cnt += 1
                        if i < s - 1 and cond(j + 1, i + 1):
                            rec(j + 1, i + 1)
                        if j >= 1 and cond(j + 1, i):
                            rec(j + 1, i)
                    rec(0, 0)
                    okx &= cnt == d[s]
    out("      D == Z == W on 9 slopes x 2 conventions:", okx)

    rows = []
    allok = True
    for lst, side in ((lo3, "lower"), (up3, "upper")):
        for idx, bden in enumerate(lst):
            if bden > 1000:
                break
            a = tb3(bden) + (0 if side == "lower" else 1)
            assert gcd(a, bden) == 1
            cw = count_D(weak(a, bden), R)
            cs = count_D(strict(a, bden), R)
            Ww = next((s - 1 for s in range(1, R + 1) if cw[s] != ND[s]), None)
            Ws = next((s - 1 for s in range(1, R + 1) if cs[s] != ND[s]), None)
            nat, oth = (Ww, Ws) if side == "lower" else (Ws, Ww)
            pred = lst[idx + 1] if idx + 1 < len(lst) else None
            c = cw if side == "lower" else cs
            # one-sidedness beyond the window
            if nat is not None:
                if side == "lower":
                    mono = all(c[s] < ND[s] for s in range(nat + 1, R + 1))
                else:
                    mono = all(c[s] > ND[s] for s in range(nat + 1, R + 1))
            else:
                mono = True
            # the floor statement of Theorem 4 itself
            bd = weak(a, bden) if side == "lower" else strict(a, bden)
            first_diff = next((i for i in range(1, R + 1) if bd(i) != tb3(i)), None)
            ok = (nat == pred or (pred is None or pred > R) and nat is None) and (oth == bden) and mono \
                and (first_diff == pred or (first_diff is None and (pred is None or pred > R)))
            allok &= ok
            rows.append((f"{a}/{bden}", side, nat, oth, pred, first_diff, ok))
    for r in rows:
        out("     slope %-9s %-5s natural W = %-5s other W = %-5s predicted b+ = %-5s first floor mismatch = %-5s ok=%s" % r)
    out(f"    all one-sided best approximations with b <= 1000, s <= {R}: {allok}   ({time.time()-T0:.0f}s)")
    # not-best slopes and a non-reduced slope
    for a, bb in ((7, 4), (13, 8), (30, 19), (49, 31), (6, 4), (16, 10)):
        cw = count_D(weak(a, bb), 400)
        cs = count_D(strict(a, bb), 400)
        Ww = next((s - 1 for s in range(1, 401) if cw[s] != ND[s]), None)
        Ws = next((s - 1 for s in range(1, 401) if cs[s] != ND[s]), None)
        out(f"     control slope {a}/{bb}: W weak = {Ww}, W strict = {Ws}")

    # Winkler Prop. 9 reading: c_s(beta) = N(s) for EVERY real beta in the cell
    #   [max_{i<s} floor(i alpha)/i , min_{i<s} (floor(i alpha)+1)/i ),  weak convention;
    # check the cell end points are the best lower / upper approximations with denominator < s.
    okcell = True
    for s in range(2, 400):
        left = max(Fraction(tb3(i), i) for i in range(1, s))
        right = min(Fraction(tb3(i) + 1, i) for i in range(1, s))
        bl = max(x for x in lo3 if x < s)
        bu = max(x for x in up3 if x < s)
        okcell &= left == Fraction(tb3(bl), bl) and right == Fraction(tb3(bu) + 1, bu)
    out("    cell of alpha for prefix length s-1 is [best lower approx with b < s, best upper approx with b < s), s < 400:", okcell)

    # ---------------------------------------------------------------- [3] Bizley
    out("\n[3] Bizley values N(kQ), k <= 1 + floor(Q'/Q)")
    conv = [(1, 1), (2, 1), (3, 2), (8, 5), (19, 12), (65, 41), (84, 53), (485, 306), (1054, 665), (24727, 15601)]
    # verify these are the convergents (continued fraction recomputed from exact comparisons)
    for (p0, q0), (p1, q1) in zip(conv, conv[1:]):
        assert abs(p0 * q1 - p1 * q0) == 1
    okb = True
    newords = []
    for n in range(1, len(conv) - 1):
        P, Q = conv[n]
        Qn = conv[n + 1][1]
        lower = (1 << P) < 3 ** Q
        kmax = 1 + Qn // Q
        for k in range(1, kmax + 2):
            s = k * Q
            if s > R:
                break
            X, Y = k * Q, k * (P - Q)
            direct = path_count(X, Y, strict_inside=not lower)
            formula = bizley_partition(P - Q, Q, k, strict_inside=not lower) if k <= 8 else None
            inside = k <= kmax
            eq = direct == ND[s]
            okb &= (eq == inside) and (formula is None or formula == direct)
            if inside and s not in lo3 and s not in up3:
                newords.append(s)
            v = str(direct)
            out(f"     {P}/{Q} {'lower' if lower else 'upper'} k={k} s={s}: paths = {v if len(v) < 26 else v[:12] + '...(' + str(len(v)) + ' digits)'}"
                f"  == N(s): {eq}  formula==paths: {formula == direct if formula is not None else 'n/a'}  inside window: {inside}")
    out("    in-window identities all hold and the first k outside each window fails:", okb, f"({time.time()-T0:.0f}s)")
    out("    orders gaining a value (not equality orders), s <= 2218:", sorted(newords))
    F1, F2, F3 = (Fraction(comb(8 * j, 3 * j), 8 * j) for j in (1, 2, 3))
    out("    N(10) = F2 - F1^2/2 =", F2 - F1 ** 2 / 2, "; N(15) = F3 - F1F2 + F1^3/6 =", F3 - F1 * F2 + F1 ** 3 / 6,
        "; DP:", ND[10], ND[15])
    G = [None] + [Fraction(comb(19 * j, 7 * j), 19 * j) for j in (1, 2, 3, 4)]
    out("    N(24), N(36), N(48) from the spelled-out formulas:",
        G[2] + G[1] ** 2 / 2 == ND[24], G[3] + G[1] * G[2] + G[1] ** 3 / 6 == ND[36],
        G[4] + G[1] * G[3] + G[2] ** 2 / 2 + G[1] ** 2 * G[2] / 2 + G[1] ** 4 / 24 == ND[48], "; N(36) =", ND[36])

    # ---------------------------------------------------------------- [4] slope 3/2 and A047749
    out("\n[4] slope 3/2")
    c32 = count_D(weak(3, 2), 1001)

    def a047749(n):
        m = n // 2
        return comb(3 * m, m) // (2 * m + 1) if n % 2 == 0 else comb(3 * m + 1, m + 1) // (2 * m + 1)
    b47 = read_b("b047749.txt")
    out("    c_s(3/2 weak) == A047749(s) (formula) s <= 1000:", all(c32[s] == a047749(s) for s in range(1, 1001)),
        "; formula == b-file:", all(b47[s] == a047749(s) for s in b47 if s <= 1000))
    out("    ballot form (s-2h+1)/(s+h+1) C(s+h+1,h):",
        all(c32[s] * (s + s // 2 + 1) == (s - 2 * (s // 2) + 1) * comb(s + s // 2 + 1, s // 2) for s in range(1, 1001)))
    out("    N(s) == A047749(s) exactly for s in", [s for s in range(1, 300) if ND[s] == a047749(s)])
    out("    of these, Winkler equality orders:", [s for s in range(1, 8) if s in lo3 or s in up3],
        " -> the extra orders are", [s for s in range(1, 8) if s not in lo3 and s not in up3])

    # ---------------------------------------------------------------- [5] cousins and mirror
    out("\n[5] cousins qx+1")
    for q, bn in ((5, "b174795.txt"), (7, "b174796.txt")):
        tbq = true_bound(q)
        cq = count_D(tbq, 600)
        bq = read_b(bn)
        lq, uq = records(q, 600)
        le = [s for s in range(1, 601) if comb(tbq(s) - 1, s - 1) == s * cq[s]]
        ue = [s for s in range(1, 601) if comb(tbq(s), s - 1) == s * cq[s]]
        okw = True
        for lst, side in ((lq, "lower"), (uq, "upper")):
            for idx, bden in enumerate(lst[:-1]):
                if bden > 200:
                    break
                a = tbq(bden) + (0 if side == "lower" else 1)
                c = count_D(weak(a, bden) if side == "lower" else strict(a, bden), 600)
                W = next((s - 1 for s in range(1, 601) if c[s] != cq[s]), None)
                okw &= W == lst[idx + 1]
        out(f"    q={q}: first terms {cq[1:9]}; b-file mismatches {[s for s in bq if s <= 600 and bq[s] != cq[s]]};"
            f" equality sets == records: {le == lq and ue == uq}; windows == next record: {okw}")
    out("    A100982 vs 5x+1 vs 7x+1 at s = 1..8:", ND[1:9], count_D(true_bound(5), 9)[1:], count_D(true_bound(7), 9)[1:])

    out("\n[6] actual residue classes (own dropping-time code, not the repo's)")

    def paper1_time(n, a=3, c=1):
        x, t = n, 0
        while True:
            x = x // 2 if x % 2 == 0 else a * x + c
            t += 1
            if x < n:
                return t
            if t > 10 ** 4:
                return None

    def shortcut(n, a=3, c=1, cap=5000):
        x, t, o = n, 0, 0
        while t < cap:
            if x % 2:
                x = (a * x + c) // 2
                o += 1
            else:
                x //= 2
            t += 1
            if x < n:
                return t, o
        return None

    cls3 = {}
    okcls = True
    exc = []
    for s in range(1, 12):
        L = tb3(s) + 1
        k = L + s
        mod = 1 << L
        cl = [r for r in range(mod) if paper1_time(r + 3 * mod) == k and paper1_time(r + 11 * mod) == k]
        cls3[s] = cl
        okcls &= len(cl) == ND[s]
        # small representatives: does every member n >= 2 of the class drop at exactly k?
        for r in cl:
            for n in (r, r + mod, r + 2 * mod):
                if n >= 2 and paper1_time(n) != k:
                    exc.append((s, n, paper1_time(n)))
    out("    3x+1: #classes mod 2^L with Paper-1 dropping time L+s equals N(s), s = 1..11:", okcls,
        [len(cls3[s]) for s in range(1, 12)])
    out("    members n >= 2 (three smallest per class) that do NOT drop at L+s:", exc[:10], "(count", len(exc), ")")
    try:
        sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..")))
        from collatz.dropping import dropping_time
        okrepo = all(dropping_time(n) == paper1_time(n) for n in range(2, 20000))
        out("    own paper1_time == collatz.dropping.dropping_time for 2 <= n < 20000:", okrepo,
            "; dropping_time(3) =", dropping_time(3))
    except Exception as e:      # run with -I: the package may not be importable
        out("    (repo package not importable in this run:", repr(e), ")")

    okm = True
    for s in range(1, 11):
        L = tb3(s) + 1
        mod = 1 << L
        cm = [r for r in range(mod) if shortcut(r + 5 * mod, 3, -1) == (L, s) and shortcut(r + 9 * mod, 3, -1) == (L, s)]
        okm &= sorted(cm) == sorted((-r) % mod for r in cls3[s])
    out("    3x-1: classes (shortcut stopping (L,s) on two large representatives) == negatives of the 3x+1 classes, s <= 10:", okm)
    c5 = count_D(true_bound(5), 9)
    tb5 = true_bound(5)
    ok5 = True
    got = []
    for s in range(1, 7):
        L = tb5(s) + 1
        mod = 1 << L
        cl = [r for r in range(mod) if shortcut(r + 3 * mod, 5, 1) == (L, s) and shortcut(r + 7 * mod, 5, 1) == (L, s)]
        got.append(len(cl))
        ok5 &= len(cl) == c5[s]
    out("    5x+1: class counts", got, "== path counts:", ok5, "; A100982 would be", ND[1:7])

    # ---------------------------------------------------------------- [7] forced cells
    out("\n[7] forced cells (Q5.x)")
    for q in (3, 5, 7):
        tq = true_bound(q)
        forced = None
        for s in range(3, 9):
            ws = words_W(lambda j, i, q=q: (1 << j) < q ** i, s)
            for w in ws:
                cells = set()
                j = i = 0
                for ch in w[:-1]:
                    j += 1
                    i += ch == "1"
                    cells.add((j, i))
                forced = cells if forced is None else forced & cells
        out(f"    q={q}: cells (j, s_j) visited by EVERY dropping word of order 3..8: {sorted(forced)}")
    out("    q=3: every word with s >= 2 starts with 11:", all(w.startswith("11") for s in range(2, 15) for w in allwords[s]))
    out(f"\ntotal {time.time()-T0:.0f}s")
    LOG.close()


if __name__ == "__main__":
    main()
