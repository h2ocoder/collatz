"""Prime factorisation vs the circuit's view (dropping class = n mod 2^b).

Facts tested here, all exact:
  A. Odd prime powers cannot bias the dropping class: among multiples of an odd p^a, the class
     distribution equals the overall one (CRT: n mod 2^b is equidistributed on multiples of p^a).
  B. Every odd square is = 1 (mod 8), hence in Set_3 (stopping time 3): even prime powers, and
     all odd squares, always drop in 3 steps.
  C. The class sequence of p, p^2, p^3, ... is periodic: p^a mod 2^b depends on a through the
     multiplicative order of p in (Z/2^b)^*; even a -> class 3 always.
  D. Class of a product q*n is a function of (q mod 2^b, n mod 2^b), so "class(pq) from
     class(p), class(q)" is a *distribution*, computable exactly: the multiplication table of
     dropping classes.
  E. Prime factors are reset at every odd step: gcd(3n+1, n) = 1.  For p | n the destination
     satisfies dest = C_r * 2^{-b} (mod p) with C_r the subgroup intercept, so whether p keeps
     dividing the orbit at its first drop is decided by the residue class r alone.
  F. The one prime-power-in-n quantity the circuit does see: v2(n+1) (trailing 1-bits) = the
     number k of consecutive odd steps = Charton's k.

Usage: .venv/Scripts/python.exe research/investigate-ternary-llms/scripts/primes_and_circuit.py
"""
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from collatz.core import stopping_time, stopping_destination  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
NMAX = 1 << 20
CLASSES = [3, 6, 8, 11, 13, 16, 19]


def cls(n):
    if n == 1:
        return 3  # 1 = 1 (mod 4): the residue class of Set_3
    k = stopping_time(n)
    return k if k <= 19 else 21


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


if __name__ == "__main__":
    out = {}
    odd = list(range(3, NMAX, 2))
    C = {n: cls(n) for n in odd}
    overall = Counter(C.values())
    tot = len(odd)
    print(f"class distribution over odd n < 2^20: " + ", ".join(f"{c}: {overall[c]/tot:.4f}" for c in CLASSES + [21]))

    # A. multiples of odd prime powers
    print("\nA. class distribution among odd multiples of p^a (should equal overall, by CRT):")
    devA = 0
    for pa in (5, 7, 25, 49, 121, 343):
        sub = Counter(C[n] for n in odd if n % pa == 0)
        s = sum(sub.values())
        dev = max(abs(sub[c] / s - overall[c] / tot) for c in CLASSES + [21])
        devA = max(devA, dev)
        print(f"   p^a={pa:4d}: n={s:6d}  " + ", ".join(f"{c}: {sub[c]/s:.4f}" for c in CLASSES + [21]) + f"   max |dev| = {dev:.4f}")
    out["A_max_dev"] = devA

    # B. odd squares and even prime powers
    sq = [m * m for m in range(3, 1024, 2)]
    print(f"\nB. odd squares m^2 (m odd, 3..1023): classes = {Counter(cls(n) for n in sq)}  (all = 3 since m^2 = 1 mod 8)")
    out["B_squares_all_class3"] = all(cls(n) == 3 for n in sq)

    # C. class sequence of prime powers
    print("\nC. class of p^a, a = 1..16 (period divides ord of p in (Z/4096)^*; even a -> 3):")
    seqs = {}
    for p in (3, 5, 7, 11, 13, 17, 19, 23, 31):
        seq = [cls(p**a) for a in range(1, 17)]
        seqs[p] = seq
        print(f"   p={p:2d}: {seq}")
    out["C_prime_power_classes"] = seqs

    # D. multiplication table of classes: P(class(q n) = c | class(q) = a, class(n) = b), residues mod 2^12
    M = 1 << 12
    R = {r: cls(r) for r in range(1, M, 2)}  # class by residue (89% decided; 21 = undecided/deep)
    byc = defaultdict(list)
    for r, c in R.items():
        byc[c].append(r)
    print("\nD. multiplication table: rows class(q) x class(n) -> distribution of class(q*n mod 2^12)")
    table = {}
    hdr = "        " + "".join(f"{c:>7}" for c in CLASSES + [21])
    print("   (a,b) " + hdr)
    for a in (3, 6, 8):
        for b in (3, 6, 8, 11):
            cnt = Counter()
            for q in byc[a]:
                for n in byc[b]:
                    cnt[R[(q * n) % M]] += 1
            s = sum(cnt.values())
            row = {c: cnt[c] / s for c in CLASSES + [21]}
            table[f"{a}x{b}"] = row
            print(f"   ({a:2d},{b:2d})      " + "".join(f"{row[c]:7.3f}" for c in CLASSES + [21]))
    out["D_table"] = table
    # the exact statement behind row (3, x): q = 1 mod 4 preserves n's class-3 membership? check 3x3 -> 3 always?
    print("   note: (3,3) -> 3 with probability", f"{table['3x3'][3]:.3f}", "(1 mod 4 times 1 mod 4 = 1 mod 4: always class 3)")

    # E. divisibility at the first drop is decided by the residue class
    print("\nE. for p | n: dest(n) mod p is constant on each dropping-set residue class (dest = (3^s n + C)/2^b):")
    bad = 0
    checks = 0
    for k, mod in ((8, 32), (13, 256)):
        s = {8: 3, 13: 5}[k]
        b = mod.bit_length() - 1
        for r in range(1, mod, 2):
            if cls(r) != k:
                continue
            for p in (5, 7, 11):
                vals = set()
                for n in range(r, r + mod * 400, mod):
                    if n % p == 0 and stopping_time(n) == k:
                        vals.add(stopping_destination(n) % p)
                if len(vals) > 1:
                    bad += 1
                checks += 1
    print(f"   residue classes x primes checked: {checks}; classes where dest mod p varied: {bad}")
    out["E_violations"] = bad
    # which residue classes of Set_8 keep divisibility by 5 / 7 at the drop?  (C_r = 0 mod p)
    keep = {}
    for p in (5, 7, 11, 13):
        kept = []
        for r in range(1, 32, 2):
            if cls(r) != 8:
                continue
            n = next(n for n in range(r, r + 32 * 2000, 32) if n % p == 0 and stopping_time(n) == 8)
            if stopping_destination(n) % p == 0:
                kept.append(r)
        keep[p] = kept
    print(f"   Set_8 residue classes (mod 32) at which p | n implies p | dest: {keep}   (3 never: 3-adic lock)")
    out["E_keep"] = keep

    # F. v2(n+1) = number of consecutive odd steps at the start
    def odd_run(n):
        k = 0
        while n % 2:
            n = (3 * n + 1) // 2
            k += 1
        return k
    okF = all(odd_run(n) == ((n + 1) & -(n + 1)).bit_length() - 1 for n in range(1, 200001, 2))
    print(f"\nF. consecutive odd Terras steps from odd n = v2(n+1) for all odd n < 200001: {okF}")
    out["F"] = okF
    json.dump(out, open(RESULTS / "primes_and_circuit.json", "w"), indent=1)
