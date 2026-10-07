"""Skeptic check 3 (Q5.1-c, Theorem 3 and its two satellites), independent code path.

Theorem 3:  for k >= 2,  tau_k(T_k^2) = T_k^2   <=>   T_k = p*q with primes p != q.

Here tau_k is evaluated on the INTEGER T_k^2 through sympy.factorint(T_k**2) (the researcher
factors T_k and doubles the exponents), the range is k <= 20000 instead of 3000, and the edge
cases k = 1, 2 and prime-power / prime-cube T_k are printed explicitly.

Also:
  * the index set equals OEIS A164977 (terms copied from oeis.org on 2026-10-06);
  * 'B = C(a+k-1,a) squarefree with exactly a prime factors => B^a fixed'  -- and the converse
    question: among PERFECT POWERS m^a fixed by tau_k, are there others?  (brute force, small range)
  * 'k, q=(k+1)/2 both prime => fixed k, q k^2, (q k)^2 and 2-cycle {q k, k^2}'.
  * control: how special is 'the largest fixed point is T_k^2'?  (uses the lists of v2)

Run: python -X utf8 v3_theorem3_family.py   (about 1 min)
"""
import os
from math import comb

from sympy import factorint, isprime

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v3_theorem3_family.log"), "w", encoding="utf-8")


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")


def tau_k(n, k):
    r = 1
    for e in factorint(n).values():
        r *= comb(e + k - 1, e)
    return r


def T(k):
    return k * (k + 1) // 2


A164977 = [3, 4, 5, 6, 10, 13, 22, 37, 46, 58, 61, 73, 82, 106, 157, 166, 178, 193, 226, 262, 277,
           313, 346, 358, 382, 397, 421, 457, 466, 478, 502, 541, 562, 586, 613, 661, 673, 718,
           733, 757, 838, 862, 877, 886, 982, 997, 1018, 1093, 1153, 1186, 1201, 1213, 1237, 1282]

out("edge cases")
out("  k=1: tau_1 = 1 identically; T_1 = 1; tau_1(1) = 1 (fixed, trivially; the theorem is stated for k >= 2)")
out("  k=2: T_2 = 3, tau_2(9) =", tau_k(9, 2), "(not fixed; 3 is not a product of two distinct primes)")
K = 20000
fixed, semi, bad = [], [], []
for k in range(2, K + 1):
    t = T(k)
    fx = tau_k(t * t, k) == t * t
    f = factorint(t)
    sm = len(f) == 2 and all(e == 1 for e in f.values())
    if fx:
        fixed.append(k)
    if sm:
        semi.append(k)
    if fx != sm:
        bad.append(k)
out(f"Theorem 3 for 2 <= k <= {K}: counterexamples {bad}; #k = {len(fixed)}")
out("  first k:", fixed[:20])
out("  fixed points T_k^2:", [T(k) ** 2 for k in fixed[:10]])
out("  index list starts with all", len(A164977), "listed terms of OEIS A164977:", fixed[:len(A164977)] == A164977)
# T_k = p^2 never happens (so 'product of two primes' in A164977 means two DISTINCT primes)
out("  k <= 20000 with T_k a prime square:", [k for k in range(2, K + 1) if (lambda f: len(f) == 1 and list(f.values()) == [2])(factorint(T(k)))])
# omega(T_k) = 1 only for k = 2
out("  k <= 20000 with omega(T_k) = 1:", [k for k in range(2, K + 1) if len(factorint(T(k))) == 1])

out("\nall fixed points of tau_k that are perfect squares m^2, m <= 3000, k = 2..12 (brute force)")
for k in range(2, 13):
    hits = [m * m for m in range(1, 3001) if tau_k(m * m, k) == m * m]
    out(f"  k={k:>2}: {hits}   T_k^2 = {T(k)**2}  {'(T_k semiprime)' if k in fixed else ''}")

out("\nB = C(a+k-1,a) squarefree with exactly a prime factors => tau_k(B^a) = B^a   (k <= 80, a <= 12)")
cnt = 0
for k in range(2, 81):
    for a in range(1, 13):
        B = comb(a + k - 1, a)
        f = factorint(B)
        if len(f) == a and all(e == 1 for e in f.values()):
            assert tau_k(B ** a, k) == B ** a
            cnt += 1
            if a >= 3:
                out(f"  k={k}, a={a}: B={B} = {'*'.join(map(str, sorted(f)))}")
out("  pairs verified:", cnt, " (README examples (7,4)->210^4 and (9,3)->165^3:",
    tau_k(210 ** 4, 7) == 210 ** 4, tau_k(165 ** 3, 9) == 165 ** 3, ")")

out("\nk and q=(k+1)/2 both prime")
ks = [k for k in range(3, 2000, 2) if isprime(k) and isprime((k + 1) // 2)]
out("  k < 2000:", ks)
ok = True
for k in ks:
    q = (k + 1) // 2
    ok &= tau_k(k, k) == k and tau_k(q * k * k, k) == q * k * k and tau_k((q * k) ** 2, k) == (q * k) ** 2
    ok &= tau_k(q * k, k) == k * k and tau_k(k * k, k) == q * k
out("  fixed k, q k^2, (q k)^2 and cycle {q k, k^2} verified for all of them:", ok)
out("  note: 'k is a fixed point of tau_k' holds for EVERY prime k (tau_k(p) = k); only the other three need q prime")
out("  every prime k <= 200 fixed:", all(tau_k(k, k) == k for k in range(2, 200) if isprime(k)))

out("\ncontrol: is T_k^2 the LARGEST fixed point of tau_k?  (complete lists from v2_tauk_attractors.log)")
lists = {2: [1, 2], 3: [1, 3, 18, 36], 4: [1, 100, 200, 224, 560, 1344, 1920], 5: [1, 5, 75, 225],
         6: [1, 441, 19559232], 7: [1, 7, 72030, 133111440, 399334320, 1944810000],
         8: [1, 11859210000, 311203233792]}
for k, L in lists.items():
    out(f"  k={k}: T_k^2 = {T(k)**2:>5} in list: {T(k)**2 in L}; largest fixed point {L[-1]}; "
        f"T_k^2 largest: {T(k)**2 == L[-1]}; all fixed points {k}-smooth-ish? max prime {max(max(factorint(n)) if n > 1 else 1 for n in L)}")
LOG.close()
