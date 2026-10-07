"""Q5.1 / Q5.2 (beyond the seed): why 36 is a fixed point of tau_3, and which numbers play
the role of 36 for the k-fold divisor function tau_k (the "cousins" of F = tau_3).

tau_k(n) = number of ordered factorisations n = d_1 ... d_k = prod_i C(a_i + k - 1, a_i).
tau_k(p^2) = C(k+1, 2) = T_k for every prime p, hence for primes p != q

      tau_k(p^2 q^2) = T_k^2 = 1^3 + 2^3 + ... + k^3      (Nicomachus)

so the number of (k-1)-step multichains of the 3x3 divisor grid is the sum of the first k
cubes.  T_k^2 is a FIXED POINT of tau_k as soon as T_k itself is a product of two distinct
primes:  k = 3 gives 36.

Checks performed (all exact):
  [1] T_k^2 is fixed by tau_k  <=>  T_k is a squarefree semiprime, for 2 <= k <= 3000.
  [2] general form: if B = C(a+k-1, a) is squarefree with exactly a prime factors then B^a
      is a fixed point of tau_k.  List of (k, a) with k <= 60, a <= 10.
  [3] k and q = (k+1)/2 both prime  =>  tau_k has the fixed points k, q*k^2, (q*k)^2 and the
      2-cycle {q*k, k^2}; for k = 3 and k = 5 these (with 1) are ALL attractors (full lists
      come from q51_q52_tau3_dynamics.py).

Run: python -X utf8 q51b_tau_k_family.py     (seconds)
"""
import json
import os
from math import comb

from sympy import factorint, isprime

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "q51b_tau_k_family.log"), "w", encoding="utf-8")


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")


def tau_k(n, k):
    r = 1
    for a in factorint(n).values():
        r *= comb(a + k - 1, a)
    return r


def T(k):
    return k * (k + 1) // 2


def main():
    res = {}
    out("=" * 78)
    out("tau_k family: the role of 36 = T_3^2 = 1^3 + 2^3 + 3^3")
    out("=" * 78)

    ok = all(comb(k + 1, 2) ** 2 == sum(i ** 3 for i in range(1, k + 1)) for k in range(1, 500))
    out("[0] tau_k(p^2 q^2) = C(k+1,2)^2 = sum_{i<=k} i^3, k < 500:", ok)
    out("    direct: tau_3(36) =", tau_k(36, 3), "; tau_5(225) =", tau_k(225, 5), "; tau_4(100) =", tau_k(100, 4),
        "; tau_7(2^2*3^2) =", tau_k(36, 7), "= T_7^2 =", T(7) ** 2)

    # [1]
    fixed_k, semi_k = [], []
    for k in range(2, 3001):
        f = factorint(T(k))
        semi = (len(f) == 2 and all(e == 1 for e in f.values()))
        # tau_k(T_k^2) from the factorisation of T_k
        val = 1
        for e in f.values():
            val *= comb(2 * e + k - 1, 2 * e)
        fx = (val == T(k) ** 2)
        if fx:
            fixed_k.append(k)
        if semi:
            semi_k.append(k)
    out("\n[1] k in [2,3000] with tau_k(T_k^2) = T_k^2 :", fixed_k[:25], "...", len(fixed_k), "values")
    out("    k in [2,3000] with T_k a squarefree semiprime:", semi_k[:25], "...", len(semi_k), "values")
    out("    the two sets coincide:", fixed_k == semi_k)
    out("    the fixed points T_k^2 :", [T(k) ** 2 for k in fixed_k[:10]])
    res["Tk2_fixed_iff_semiprime_upto_3000"] = fixed_k == semi_k
    res["k_list"] = fixed_k[:40]

    # [2]
    out("\n[2] (k, a) with B = C(a+k-1, a) squarefree with exactly a prime factors (=> B^a fixed by tau_k)")
    fam = []
    for k in range(2, 61):
        for a in range(1, 11):
            B = comb(a + k - 1, a)
            f = factorint(B)
            if len(f) == a and all(e == 1 for e in f.values()):
                n = B ** a
                assert tau_k(n, k) == n
                fam.append((k, a, B, n))
    for k, a, B, n in fam:
        if k <= 12 or a >= 3:
            out(f"    k={k:>2} a={a}: B = {B} = {'*'.join(str(p) for p in sorted(factorint(B)))},  fixed point B^a = {n}")
    out(f"    ({len(fam)} pairs with k <= 60, a <= 10; a = 1 is 'k prime, fixed point k'; a = 2 is [1])")
    res["Ba_family"] = [[k, a, B, str(n)] for k, a, B, n in fam]

    # [3]
    out("\n[3] k and q = (k+1)/2 both prime: attractors k, q k^2, (q k)^2 and the 2-cycle {q k, k^2}")
    ks = [k for k in range(3, 400, 2) if isprime(k) and isprime((k + 1) // 2)]
    out("    such k < 400:", ks)
    for k in ks[:8]:
        q = (k + 1) // 2
        c1 = tau_k(k, k) == k
        c2 = tau_k(q * k * k, k) == q * k * k
        c3 = tau_k((q * k) ** 2, k) == (q * k) ** 2
        c4 = tau_k(q * k, k) == k * k and tau_k(k * k, k) == q * k
        out(f"    k={k:>3}, q={q:>3}: fixed {k}, {q*k*k}, {(q*k)**2}; cycle {{{q*k}, {k*k}}} : {c1 and c2 and c3 and c4}")
        assert c1 and c2 and c3 and c4
    out("    k = 3: {3, 18, 36, {6,9}};  k = 5: {5, 75, 225, {15,25}}  -- with 1, the complete lists (q51_q52 log).")
    out("    k = 13: {13, 1183, 8281, {91,169}} exist; completeness for k = 13 NOT computed (E_13 is huge).")
    res["k_with_q_prime"] = ks

    # the same statement in exponent coordinates for k = 3
    out("\n[4] k = 3 in exponent coordinates (the grid of 2^a 3^b):")
    for a in range(0, 9):
        row = []
        for b in range(0, 5):
            n = 2 ** a * 3 ** b
            f = T(a + 1) * T(b + 1)
            row.append("=" if f == n else (">" if f > n else "<"))
        out(f"    a={a}: " + " ".join(row) + "     (F(2^a 3^b) vs 2^a 3^b for b = 0..4)")
    json.dump(res, open(os.path.join(HERE, "q51b_tau_k_family.json"), "w"), indent=1)
    out("\nwrote q51b_tau_k_family.json")


if __name__ == "__main__":
    main()
    LOG.close()
