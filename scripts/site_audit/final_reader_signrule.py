# Class-level check of the Sturmian sign rule and the A_o recursion (sturmian-l-probe.md), by exact DP.
# M_i[e'] = number of non-dropped parity-word prefixes that reach the i-th odd step after e' halvings.
# dest mod 3 depends only on the parity of alpha_o = e_o - e' (halvings after the last odd step).
from fractions import Fraction
def fl(i):  # floor(i*log2 3), exact
    return (3 ** i).bit_length() - 1
OMAX = 400
M = {0: 1}
P = {}; D = {}
for i in range(1, OMAX + 1):
    e_i = fl(i) + 1
    P[i] = sum(M.values())
    D[i] = sum(v * (1 if (e_i - ep) % 2 == 1 else -1) for ep, v in M.items())   # c2 - c1
    # extend to the (i+1)-th odd step: e'' in (e', floor(i log2 3)]
    cap = fl(i)
    newM = {}
    run = 0
    keys = sorted(M)
    idx = 0
    for e2 in range(1, cap + 1):
        while idx < len(keys) and keys[idx] < e2:
            run += M[keys[idx]]; idx += 1
        if run: newM[e2] = run
    M = newM
k = lambda o: o + fl(o) + 1 if o > 0 else 1
print("P_1..12:", [P[i] for i in range(1, 13)])
A = {1: Fraction(1)}
bad_sign = []; bad_rec = []
for o in range(1, OMAX + 1):
    gap = k(o) - k(o - 1)
    eps = 1 if gap == 3 else -1
    if o < OMAX:
        A[o + 1] = (P[o] + (-1) ** gap * A[o]) / 2
    if D[o] != eps * A[o]: bad_rec.append(o)
    sgn = (D[o] > 0) - (D[o] < 0)
    if sgn != eps: bad_sign.append((o, gap, D[o] if o < 10 else '...'))
print("c2-c1, o=1..10:", [D[o] for o in range(1, 11)])
print(f"o <= {OMAX}: sign(c2-c1) != gap rule at:", bad_sign)
print(f"o <= {OMAX}: c2-c1 != eps_o*A_o (recursion) at:", bad_rec)
print("0 < A_o < P_o for 4 <= o <=", OMAX, ":", all(0 < A[o] < P[o] for o in range(4, OMAX + 1)))
