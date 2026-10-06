"""Q2.4  The mirror: bitwise NOT, the triangular coordinate, and the cycles of T on Z.

NOT(x) = -1 - x  (2-adic bitwise complement).  T = shortcut Collatz map on Z (all signs).

Run:  C:/repos/collatz/.venv/Scripts/python.exe -X utf8 q24_mirror.py
Writes q24_mirror.log / .json.
"""
import json
import os
import sys
import time
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import Tee, tri, v2

out = Tee(os.path.join(HERE, "q24_mirror.log"))
res = {}
t0 = time.time()


def NOT(x):
    return -1 - x


def C(x):                      # un-shortcut odd step
    return 3 * x + 1


def T(x):                      # shortcut map, any integer (Python // and % are floor-based: exact here)
    return x // 2 if x % 2 == 0 else (3 * x + 1) // 2


def Tminus(y):                 # 3x-1 shortcut map
    return y // 2 if y % 2 == 0 else (3 * y - 1) // 2


def TN(m):                     # claimed NOT-conjugate of T
    return 3 * m // 2 if m % 2 == 0 else (m - 1) // 2


# ------------------------------------------------------------------ A. conjugacy identities
out("=" * 100)
out("A. Identities, checked for every integer -20000 <= n <= 20000")
out("=" * 100)
R = range(-20000, 20001)
chk = {}
chk["NOT(3n+1) = 3 NOT(n) + 1            (3x+1 commutes with NOT)"] = all(NOT(C(n)) == C(NOT(n)) for n in R)
chk["NOT(NOT(m)/2) = (m-1)/2, m odd       (halving does NOT commute)"] = all(
    NOT(NOT(m) // 2) == (m - 1) // 2 for m in R if m % 2)
chk["NOT o T o NOT = TN: m -> 3m/2 (m even), (m-1)/2 (m odd)"] = all(NOT(T(NOT(m))) == TN(m) for m in R)
chk["TN(m) = Tminus(m+1) - 1              (TN is 3x-1 shifted by one)"] = all(TN(m) == Tminus(m + 1) - 1 for m in R)
chk["-T(-y) = Tminus(y)                   (negation: 3x+1 on Z_<0 = 3x-1 on Z_>0)"] = all(-T(-y) == Tminus(y) for y in R)
chk["T_NOT(n) = T_n                       (triangular number is NOT-invariant)"] = all(tri(NOT(n)) == tri(n) for n in R)
chk["T_(3n+1) = 9 T_n + 1                 (the odd step descends to t -> 9t+1)"] = all(tri(C(n)) == 9 * tri(n) + 1 for n in R)
chk["u(3n+1) = 3 u(n),  u = 2n+1"] = all(2 * C(n) + 1 == 3 * (2 * n + 1) for n in R)
chk["u(n/2) = v(n) = n+1 for n even"] = all(2 * (n // 2) + 1 == n + 1 for n in R if n % 2 == 0)
chk["v(T(n)) = 3v/2 (v even), (v+1)/2 (v odd),  v = n+1"] = all(
    T(n) + 1 == (3 * (n + 1) // 2 if (n + 1) % 2 == 0 else (n + 2) // 2) for n in R)
chk["T(NOT(e)) = NOT(3e/2) for e even     (mirror branch of an even point)"] = all(
    T(NOT(e)) == NOT(3 * e // 2) for e in R if e % 2 == 0)
for name, ok in chk.items():
    out(f"  {ok!s:5s}  {name}")
res["A_identities"] = chk

# halving does not descend to the T-coordinate: explicit witness
out("  halving has no image in the t = T_n coordinate: T_n = T_NOT(n), but only one of n, NOT(n) is even.")
out("  The two branches at the even representative e of the pair {e, NOT(e)} are  e -> e/2  (3x+1 side)")
out("  and  e -> 3e/2  (mirror side): the quotient by NOT is a 2-valued correspondence, not a map.")

# ------------------------------------------------------------------ B. cycles of T on Z
out("")
out("=" * 100)
out("B. Cycles of the shortcut map T on Z, exhaustive over starts -200000 <= n <= 200000")
out("=" * 100)
cyc_of = {}
cycles = []
for start in range(-200000, 200001):
    path = []
    seen = {}
    x = start
    while x not in cyc_of and x not in seen:
        seen[x] = len(path)
        path.append(x)
        x = T(x)
    if x in cyc_of:
        cid = cyc_of[x]
    else:
        cyc = path[seen[x]:]
        cid = len(cycles)
        cycles.append(cyc)
    for y in path:
        cyc_of[y] = cid


def rotate_to_min_abs(c):
    i = min(range(len(c)), key=lambda t: (abs(c[t]), c[t]))
    return c[i:] + c[:i]


cycles = sorted((rotate_to_min_abs(c) for c in cycles), key=lambda c: (len(c), abs(c[0])))
basin = {}
for x, cid in cyc_of.items():
    pass
table = []
out("  coordinates:  n ;  v = n+1 ;  u = 2n+1 ;  NOT(n) = -1-n = -v ;  t = T_n = (u^2-1)/8")
for c in cycles:
    word = "".join("1" if x % 2 else "0" for x in c)
    k, s = len(c), word.count("1")
    cell = 2 ** k - 3 ** s
    # word constant: n0 * (2^k - 3^s)
    const = c[0] * cell
    runs = [r for r in word.split("0") if r]
    if word[0] == "1" and word[-1] == "1" and "0" in word:
        runs = runs[:-1]
        runs[0] = word.rsplit("0", 1)[1] + runs[0] if False else runs[0]
    row = dict(cycle=c, word=word, k=k, s=s, cell=cell, word_constant=const,
               v=[x + 1 for x in c], u=[2 * x + 1 for x in c], NOT=[NOT(x) for x in c],
               tri=[tri(x) for x in c])
    table.append(row)
    out(f"  --- cycle with min |n| = {c[0]}:  length k={k}, odd steps s={s}, word {word},"
        f" 2^k-3^s = {cell}, word constant n0*(2^k-3^s) = {const}")
    out(f"      n   : {c}")
    out(f"      v   : {row['v']}")
    out(f"      u   : {row['u']}")
    out(f"      NOT : {row['NOT']}")
    out(f"      T_n : {row['tri']}")
res["B_cycles"] = table
res["B_num_cycles"] = len(cycles)
out(f"  number of cycles met from |n| <= 200000: {len(cycles)}  (the five known ones)")

out("")
out("  minimal elements in each coordinate:")
out("     n0    v0=n0+1   NOT(n0)   u0=2n0+1   T_n0   v2(v0)   v0/2^v2   3-smooth |v| along the cycle")


def smooth3(x):
    x = abs(x)
    if x == 0:
        return False
    for p in (2, 3):
        while x % p == 0:
            x //= p
    return x == 1


mins = []
for row in table:
    n0 = row["cycle"][0]
    v0 = n0 + 1
    j = v2(v0) if v0 else None
    c0 = (v0 >> j) if v0 else 0
    sm = [abs(v) for v in row["v"] if smooth3(v)]
    mins.append(dict(n0=n0, v0=v0, NOT=NOT(n0), u0=2 * n0 + 1, tri=tri(n0), j=j, c=c0, smooth_v=sm))
    out(f"   {n0:5d}   {v0:6d}   {NOT(n0):6d}   {2 * n0 + 1:6d}   {tri(n0):6d}    {j!s:5s}   {c0:5d}     {sm}")
res["B_minima"] = mins

# decomposition into runs ("scaled anti-diagonals of the 3-smooth lattice")
out("")
out("  v-coordinate run decomposition (a run of j odd steps is v = c*2^j -> c*2^(j-1)*3 -> ... -> c*3^j):")
for row in table:
    c = row["cycle"]
    vs = row["v"]
    word = row["word"]
    k = len(c)
    # start at a position preceded by a 0 (or anywhere if the word is all ones / all zeros)
    starts = [i for i in range(k) if word[i] == "1" and word[i - 1] == "0"]
    desc = []
    for i in starts:
        j = 0
        while word[(i + j) % k] == "1" and j < k:
            j += 1
        cc = vs[i] // 2 ** j
        desc.append(f"{cc}*antidiag({j}) = {[vs[(i + t) % k] for t in range(j)] + [cc * 3 ** j]}")
    if not starts:
        desc.append("no proper run (word " + word + ")")
    out(f"     n0={c[0]:4d}: " + " ; ".join(desc))

# ------------------------------------------------------------------ C. unit cells and Levi ben Gerson pairs
out("")
out("=" * 100)
out("C. Unit cells |2^k - 3^s| = 1 (k >= 1, s >= 0; searched s <= 3000)  <->  consecutive 3-smooth pairs")
out("   <->  3-smooth triangular numbers  <->  integer cycles forced by the cell")
out("=" * 100)
units = []
for s in range(0, 3001):
    p = 3 ** s
    for cand in (p - 1, p + 1):
        if cand > 1 and cand & (cand - 1) == 0:
            k = cand.bit_length() - 1
            units.append((k, s, 2 ** k - 3 ** s))
units.sort()
for (k, s, val) in units:
    lo, hi = sorted((2 ** k, 3 ** s))
    t = lo * hi // 2
    cyc = [row["cycle"] for row in table if row["k"] == k and row["s"] == s]
    out(f"   (k,s)=({k},{s})  2^k-3^s = {val:+d}   pair ({lo},{hi})   T_{lo} = {t}   cycle(s) in this cell: {cyc}")
res["C_unit_cells"] = units
out("   the remaining cycle (min -17) sits in the non-unit cell (11,7): 2^11 - 3^7 = -139 and 139 | word constant.")

# family: word 1^j 0  ->  n0 = 3^j - 2^j is a cycle minimum of 3x + d_j with d_j = 2^(j+1) - 3^j, and n0 + d_j = 2^j
out("")
out("   family 'one anti-diagonal + one halving' (word 1^j 0): rule 3x + d_j, d_j = 2^(j+1) - 3^j,")
out("   cycle minimum n0 = 3^j - 2^j, v0 = n0 + d_j = 2^j.  It is a 3x+-1 cycle iff |d_j| = 1.")
fam = []
for j in range(0, 9):
    d = 2 ** (j + 1) - 3 ** j
    n0 = 3 ** j - 2 ** j
    x = n0
    orb = []
    for _ in range(j + 1):
        orb.append(x)
        x = x // 2 if x % 2 == 0 else (3 * x + d) // 2
    ok = (x == n0)
    fam.append((j, d, n0, ok))
    out(f"      j={j}: d_j = {d:+6d}   n0 = {n0:5d}   closes after j+1 steps: {ok}   orbit {orb}"
        f"{'   <-- 3x+1' if d == 1 else ''}{'   <-- 3x-1 (mirror)' if d == -1 else ''}")
res["C_family"] = fam

# 1-circuits: c = (2^e - 1)/(2^(j+e) - 3^j) integral?
sol = []
for j in range(1, 200):
    for e in range(1, 200):
        den = 2 ** (j + e) - 3 ** j
        num = 2 ** e - 1
        if num % den == 0:
            cc = num // den
            sol.append((j, e, cc, cc * 2 ** j - 1))
out(f"   1-circuits (j odd steps then e extra halvings), integer solutions for 1 <= j,e < 200: (j, e, c, n0) = {sol}")
res["C_one_circuits"] = sol

# ------------------------------------------------------------------ D. TN on the positive integers; where is 36?
out("")
out("=" * 100)
out("D. The mirror map TN (m -> 3m/2 | (m-1)/2) on m >= 0; m = NOT(n) = -(n+1) for n <= -1")
out("=" * 100)
for m0 in (0, 4, 16):
    x = m0
    orb = [x]
    while True:
        x = TN(x)
        if x == m0:
            break
        orb.append(x)
    fac = []
    for y in orb:
        if y and smooth3(y):
            a = v2(y)
            b = 0
            z = y >> a
            while z > 1:
                z //= 3
                b += 1
            fac.append(f"{y}=2^{a}3^{b}")
    out(f"   cycle through {m0}: {orb}")
    out(f"       3-smooth members: {fac}")
out("   36 = 2^2 3^2 is the midpoint of the anti-diagonal a+b=4 inside the 11-cycle; NOT(36) = -37,")
out("   i.e. 37 = 36 + 1 lies on the 3x-1 cycle of 17.  35 (v = 36 for 3x+1) is not on a cycle.")
x = 37
orb = [x]
while True:
    x = Tminus(x)
    if x == 37:
        break
    orb.append(x)
out(f"   3x-1 orbit of 37: {orb}")
res["D_37_on_3x-1_cycle"] = orb

# ------------------------------------------------------------------ E. census: is 'v0 = power of two' common?
out("")
out("=" * 100)
out("E. Base rate.  For the rules 3x+d (d odd, 3 !| d, |d| <= 499) list the primitive positive cycles")
out("   (gcd(min, d) = 1), minimum n0 <= 100|d| + 2000.  v0 = n0 + d is the coordinate in which an odd")
out("   step is v -> 3v/2.  How often is v0 = 2^j exactly (c = 1), as for 1, 5 and 17?")
out("=" * 100)


def cycle_min_scan(d, nmax, cap=200000):
    """n0 is a cycle minimum iff its orbit returns to n0 before going below n0.
    Starts that flow into a cycle with a LARGER minimum neither drop nor return; they are
    recognised with Brent's cycle detection and counted as 'captured' (not as cycles)."""
    found = []
    captured = 0
    unresolved = 0
    for n0 in range(1, nmax + 1, 2):          # a cycle minimum is odd (an even minimum would halve below)
        x = n0
        k = s = 0
        word = []
        saved, nxt = None, 64
        while True:
            if x & 1:
                x = (3 * x + d) >> 1
                s += 1
                word.append("1")
            else:
                x >>= 1
                word.append("0")
            k += 1
            if x < n0:
                break
            if x == n0:
                found.append((n0, k, s, "".join(word)))
                break
            if x == saved:
                captured += 1
                break
            if k == nxt:
                saved, nxt = x, nxt * 2
            if k >= cap:
                unresolved += 1
                break
    return found, captured, unresolved


census = []
unres_total = 0
capt_total = 0
for d in range(-499, 500, 2):
    if d % 3 == 0:
        continue
    f, cap_, un = cycle_min_scan(d, 100 * abs(d) + 2000)
    unres_total += un
    capt_total += cap_
    for (n0, k, s, word) in f:
        if gcd(n0, abs(d)) != 1:
            continue
        v0 = n0 + d
        runs = len([r for r in (word + word).split("0") if r]) // 2 if "0" in word else 1
        ncirc = sum(1 for i in range(k) if word[i] == "1" and word[i - 1] == "0") or 1
        if v0 == 0:
            j, c = None, 0
        else:
            j = v2(v0)
            c = v0 >> j
        census.append(dict(d=d, n0=n0, k=k, s=s, circuits=ncirc, v0=v0, j=j, c=c))
tot = len(census)
pure = [r for r in census if r["c"] in (1, -1)]
out(f"   primitive positive cycles found: {tot}   starts captured by a cycle with larger minimum: {capt_total}"
    f"   unresolved starts (step cap hit): {unres_total}")
out(f"   with v0 = +-2^j (c = +-1): {len(pure)}  = {len(pure) / tot:.3f}")
bycirc = {}
for r in census:
    a = bycirc.setdefault(r["circuits"], [0, 0])
    a[0] += 1
    a[1] += r["c"] in (1, -1)
out("   by number of circuits (runs of odd steps):  circuits: (cycles, with c=+-1, fraction)")
for cnum in sorted(bycirc):
    a = bycirc[cnum]
    out(f"      {cnum:2d}: ({a[0]:4d}, {a[1]:3d}, {a[1] / a[0]:.3f})")
small = [r for r in census if r["n0"] <= 17 * abs(r["d"])]
sp = [r for r in small if r["c"] in (1, -1)]
out(f"   restricted to n0 <= 17|d| (the size range of 1, 5, 17): {len(sp)} of {len(small)} = {len(sp) / max(1, len(small)):.3f}")
two = [r for r in census if r["circuits"] == 2]
out("   all 2-circuit cycles with c = +-1 (the type of the 17-cycle):")
for r in two:
    if r["c"] in (1, -1):
        out(f"      d={r['d']:+5d}  n0={r['n0']:6d}  (k,s)=({r['k']},{r['s']})  v0={r['v0']} = {r['c']:+d}*2^{r['j']}")
dm1 = [r for r in census if r["d"] in (1, -1)]
out(f"   rows for d = +-1: {dm1}")
# distribution of |c| for comparison
cs = {}
for r in census:
    cs[abs(r["c"])] = cs.get(abs(r["c"]), 0) + 1
top = sorted(cs.items(), key=lambda t: -t[1])[:10]
out(f"   most common |c| = |v0|/2^v2(v0): {top}")
out("   every cycle with c = +-1:")
for r in pure:
    out(f"      d={r['d']:+5d}  n0={r['n0']:6d}  (k,s)=({r['k']},{r['s']})  circuits={r['circuits']:2d}"
        f"  v0={r['v0']} = {r['c']:+d}*2^{r['j']}")
# size-matched base rate: among cycles with |v0| <= B, how many have |v0| a power of two,
# against the share of powers of two among the even numbers 2..B
size_matched = {}
for B in (16, 32, 64, 128, 256):
    inb = [r for r in census if 0 < abs(r["v0"]) <= B]
    hit = [r for r in inb if r["c"] in (1, -1)]
    naive = (B.bit_length() - 1) / (B // 2)
    size_matched[B] = (len(hit), len(inb), naive)
    out(f"   size-matched: |v0| <= {B:3d}: {len(hit):2d} of {len(inb):3d} cycles have |v0| = 2^j"
        f"  ({len(hit) / max(1, len(inb)):.3f});  share of powers of two among even numbers <= {B}: {naive:.3f}")
res["E_census"] = dict(total=tot, pure_power_of_two=len(pure), by_circuits=bycirc,
                       small_total=len(small), small_pure=len(sp), d_pm1=dm1, top_c=top,
                       captured=capt_total, unresolved=unres_total, pure_rows=pure,
                       size_matched=size_matched)

# ------------------------------------------------------------------ F. the 2-circuit equations for the 17-cycle
out("")
out("=" * 100)
out("F. Two-circuit cycles of 3x-1 (positive y, v = y-1): runs (j1,e1,j2,e2), v = c1 2^j1 and c2 2^j2")
out("     3^j1 c1 + 1 = 2^e1 (2^j2 c2 + 1),   3^j2 c2 + 1 = 2^e2 (2^j1 c1 + 1)")
out("   => c1 = [(2^e1-1) 3^j2 + (2^e2-1) 2^(e1+j2)] / (3^(j1+j2) - 2^(j1+j2+e1+e2))")
out("=" * 100)
from fractions import Fraction  # noqa: E402

j1, e1, j2, e2 = 4, 1, 3, 3
num1 = (2 ** e1 - 1) * 3 ** j2 + (2 ** e2 - 1) * 2 ** (e1 + j2)
num2 = (2 ** e2 - 1) * 3 ** j1 + (2 ** e1 - 1) * 2 ** (e2 + j1)
den = 3 ** (j1 + j2) - 2 ** (j1 + j2 + e1 + e2)
out(f"   17-cycle: (j1,e1,j2,e2) = (4,1,3,3): c1 = {num1}/{den} = {Fraction(num1, den)},"
    f" c2 = {num2}/{den} = {Fraction(num2, den)}")
sols = []
for a1 in range(1, 25):
    for b1 in range(1, 25):
        for a2 in range(1, 25):
            for b2 in range(1, 25):
                dd = 3 ** (a1 + a2) - 2 ** (a1 + a2 + b1 + b2)
                n1 = (2 ** b1 - 1) * 3 ** a2 + (2 ** b2 - 1) * 2 ** (b1 + a2)
                n2 = (2 ** b2 - 1) * 3 ** a1 + (2 ** b1 - 1) * 2 ** (b2 + a1)
                if n1 % dd == 0 and n2 % dd == 0:
                    c1, c2 = n1 // dd, n2 // dd
                    if c1 % 2 and c2 % 2:      # run lengths exact: c odd
                        sols.append((a1, b1, a2, b2, c1, c2, c1 * 2 ** a1 + 1, c2 * 2 ** a2 + 1))
out(f"   all integer solutions with odd c1, c2 and 1 <= j,e <= 24 (j1,e1,j2,e2,c1,c2,y1,y2): {sols}")
out("   (positive c: 3x-1 on positive integers; negative c: 3x+1 on positive integers, y = -(c 2^j + 1))")
res["F_two_circuit_solutions"] = sols

# ------------------------------------------------------------------ G. anti-diagonals of the 3-smooth lattice
out("")
out("=" * 100)
out("G. Anti-diagonal j of the 3-smooth lattice: {2^j, 2^(j-1) 3, ..., 3^j}.  In v = n+1 the Collatz map")
out("   walks it (v -> 3v/2) and leaves at 3^j by v -> (v+1)/2; the mirror leaves by m -> (m-1)/2.")
out("   The anti-diagonal closes into a cycle iff the exit lands on 2^j: 3^j + 1 = 2^(j+1) (Collatz)")
out("   or 3^j - 1 = 2^(j+1) (mirror).")
out("=" * 100)
for j in range(0, 9):
    diag = [2 ** (j - i) * 3 ** i for i in range(j + 1)]
    plus_exit = (3 ** j + 1) // 2
    minus_exit = (3 ** j - 1) // 2
    out(f"   j={j}: {diag}   Collatz exit (3^j+1)/2 = {plus_exit}{'  = 2^j: CYCLE' if plus_exit == 2 ** j else ''}"
        f"   mirror exit (3^j-1)/2 = {minus_exit}{'  = 2^j: CYCLE' if minus_exit == 2 ** j else ''}")
out("   36 = 2^2 3^2 is on anti-diagonal 4.  Collatz: v = 36 -> 54 -> 81 -> 41 -> 21 -> 11 -> 6 -> 9 -> 5 -> 3 -> 2")
out("   (n = 35 -> ... -> 1).  Mirror: m = 36 -> 54 -> 81 -> 40 -> 60 -> 90 -> 135 -> 67 -> 33 -> 16 -> 24 -> 36.")

out("")
out(f"done in {time.time() - t0:.1f} s")
with open(os.path.join(HERE, "q24_mirror.json"), "w", encoding="utf-8") as fh:
    json.dump(res, fh, indent=1, default=str)
out.close()
