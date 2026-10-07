# Final-reader independent checks (read-only audit of site numbers).
from fractions import Fraction
from math import log2, comb, floor, log, sqrt
import numpy as np

L = log2(3)
print("== transfer matrix (hilbert-polya.md) ==")
def cutoff_cycles(M, n=3, sign=1):
    f = lambda x: x // 2 if x % 2 == 0 else (n * x + sign) % M
    w = lambda x: Fraction(2) if x % 2 == 0 else Fraction(1, n)
    seen = {}; cycles = []
    for x0 in range(M):
        path = []; x = x0
        while x not in seen:
            seen[x] = x0; path.append(x); x = f(x)
        if seen[x] == x0 and x in path:
            cyc = path[path.index(x):]
            prod = Fraction(1)
            for y in cyc: prod *= w(y)
            cycles.append((cyc, prod))
    return cycles
bad = []
for M in range(6, 114, 6):
    cyc = cutoff_cycles(M)
    desc = sorted((len(c), p) for c, p in cyc)
    if desc != [(1, Fraction(2)), (3, Fraction(4, 3))]:
        bad.append((M, [(c, str(p)) for c, p in cyc]))
print("multiples of 6 below 114 whose loops are not exactly {0} and {1,4,2}:", bad)
print("M=114 loops:", [(c, str(p), float(p) ** (1 / len(c))) for c, p in cutoff_cycles(114)])
for M in (24, 96):
    A = np.zeros((M, M))
    for x in range(M):
        if x % 2 == 0: A[x // 2, x] = 2
        else: A[(3 * x + 1) % M, x] = 1 / 3
    ev = np.linalg.eigvals(A)
    nz = sorted([abs(e) for e in ev if abs(e) > 1e-6], reverse=True)
    print(f"M={M}: nonzero |eig| = {[round(v,4) for v in nz]}, rank = {np.linalg.matrix_rank(A)}, ||A-A^T||_F/||A||_F = {np.linalg.norm(A-A.T)/np.linalg.norm(A):.3f}")
for n in (5, 7):
    print(f"{n}x+1 at M=24 loops:", [(c, str(p), round(float(p) ** (1 / len(c)), 4)) for c, p in cutoff_cycles(24, n)])
print("3x-1 at M=24 loops:", [(c, str(p), round(float(p) ** (1 / len(c)), 4)) for c, p in cutoff_cycles(24, 3, -1)])

print("\n== cycle heuristic (no-loops.md) ==")
for S, E in ((5, 8), (41, 65), (306, 485)):
    g = 2 ** E - 3 ** S
    words_odd = comb(E - 1, S - 1)
    print(f"(S,E)=({S},{E}): words starting odd = C(E-1,S-1) ~ 2^{log2(words_odd):.1f}; gap ~ 2^{log2(g):.1f}; words/gap = {Fraction(words_odd, g).__float__():.3g}; C(E,S)/gap = {Fraction(comb(E,S), g).__float__():.3g}")
for S in (5, 20, 60):
    tot = Fraction(0)
    for E in range(floor(S * L) + 1, 40 * S):
        tot += Fraction(comb(E - 1, S - 1), 2 ** E - 3 ** S)
    print(f"sum over E of C(E-1,S-1)/gap for S={S}: {float(tot):.3f}")
print("E/S - log2 3 bound: 1/(3*2^68*ln2) = 2^%.3f" % log2(1 / (3 * 2 ** 68 * log(2))))

print("\n== dropping words: A100982, masses, sign rule at class level ==")
# enumerate dropping words level by level, tracking (e, C mod 3^big not needed): keep C exactly as int for s<=15
def levels(smax):
    # state after an odd step count: list of (e, C) for prefixes that have not dropped; word in f-steps
    out = {}
    # level 0: word E
    out[0] = [(1, 0)]
    # start: O then mandatory E  => s=1,e=1, C: (3n+1)/2 -> numerator const 1 with e=1
    frontier = [(1, 1, 1)]  # (s, e, C) meaning value = (3^s n + C)/2^e, last step was a halving after an odd step
    for s in range(1, smax + 1):
        done = []; nxt = []
        stack = list(frontier)
        while stack:
            s_, e, C = stack.pop()
            if 2 ** e > 3 ** s_:
                done.append((e, C)); continue
            # not dropped: either halve again or take an odd step (then mandatory halving)
            stack.append((s_, e + 1, C))
            nxt.append((s_ + 1, e + 1, 3 * C + 2 ** e))
        out[s] = done; frontier = nxt
    return out
lv = levels(17)
P = {s: len(v) for s, v in lv.items()}
print("w_s, s=0..17:", [P[s] for s in range(18)])
e_of = lambda s: floor(s * L) + 1
print("all e equal floor(s log2 3)+1:", all(all(e == e_of(s) for e, C in lv[s]) for s in lv))
print("sum w_s/2^e_s to s=17:", float(sum(Fraction(P[s], 2 ** e_of(s)) for s in lv)), " sum w_s/3^s to s=17:", float(sum(Fraction(P[s], 3 ** s) for s in lv)))
print("distinct residues d mod 3^s per level (s<=12):", all(len({(C * pow(2 ** e, -1, 3 ** s)) % 3 ** s for e, C in lv[s]}) == P[s] for s in range(1, 13)))
A = {1: 1}
k = lambda o: o + e_of(o)
for o in range(1, 17):
    gap = k(o) - k(o - 1)  # sigma_o uses gap_o = k_o - k_{o-1}
    A[o + 1] = Fraction(P[o] + (-1) ** gap * A[o], 2)
rows = []
ok = True
for o in range(1, 18):
    c1 = c2 = 0
    for e, C in lv[o]:
        r = (C * pow(2 ** e, -1, 3)) % 3
        if r == 1: c1 += 1
        elif r == 2: c2 += 1
        else: ok = False
    gap = k(o) - k(o - 1)
    eps = 1 if gap == 3 else -1
    rows.append((o, k(o), gap, c2 - c1, eps * A[o]))
    if c2 - c1 != eps * A[o]: ok = False
print("o, k_o, gap, c2-c1 (classes), eps*A_o (recursion):")
for r in rows: print("  ", r[0], r[1], r[2], r[3], r[4])
print("class-level closed form c2-c1 = eps_o*A_o holds for o=1..17:", ok)

print("\n== misc ==")
a = log(3) / log(6)
print("log6 3 =", a, " 44a =", 44 * a, " 31a =", 31 * a)
beta = L; lam = beta ** beta / (beta - 1) ** (beta - 1)
print("lambda =", lam, " lambda/3 =", lam / 3)
# average beta over odd n: exact from class densities
tot = Fraction(0); wsum = Fraction(0)
for s in range(1, 18):
    wt = Fraction(2 * P[s], 2 ** e_of(s)); wsum += wt
    tot += wt * Fraction(e_of(s) - s * L).limit_denominator(10 ** 12)
print("mean beta over odd n from class densities, s<=17: %.4f (weight covered %.4f)" % (float(tot), float(wsum)))
