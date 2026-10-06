"""Pierpont points on the exponent lattice of 3-smooth numbers.

A Pierpont prime is a prime p = 2^i 3^j + 1.  We call (i, j) a *Pierpont point*.
For p > 3 one always has i >= 1 (p odd) and (i, j) != (1, 0).

Primality here is PROVED, not probable: p - 1 = 2^i 3^j is completely factored, so
Lucas' converse of Fermat applies (Lehmer's form):

    N is prime  <=>  for every prime q | N - 1 there is a_q with
                     a_q^(N-1) = 1 (mod N)  and  a_q^((N-1)/q) != 1 (mod N).

Proof of (<=): the order of a_q is divisible by the full power of q in N - 1, so the
group (Z/N)^* has order divisible by N - 1, hence phi(N) = N - 1.

The witness search is over small a; if N is prime a witness for q = 2 is any quadratic
non-residue (density 1/2) and for q = 3 any cubic non-residue (density 2/3), so a
failure to find one among the first 60 primes after N passed a Fermat test would be
astronomically unlikely -- and is reported as an error rather than silently accepted.
"""
from __future__ import annotations

SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
                73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
                157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233,
                239, 241, 251, 257, 263, 269, 271, 277, 281]


def lucas_certificate(i: int, j: int):
    """Return a primality certificate {q: a_q} for N = 2^i 3^j + 1, or None if composite.

    Raises RuntimeError if N passes Fermat tests but no witness is found (never observed).
    """
    N = (1 << i) * 3 ** j + 1
    if N < 2:
        return None
    if N in (2, 3):
        return {"trivial": N}
    if N % 2 == 0:
        return None
    # trial division by small primes (cheap composite filter)
    for p in SMALL_PRIMES:
        if N == p:
            break
        if N % p == 0:
            return None
    qs = [q for q, e in ((2, i), (3, j)) if e > 0]
    cert = {}
    for q in qs:
        found = None
        for a in SMALL_PRIMES:
            if a >= N:
                break
            if pow(a, N - 1, N) != 1:
                return None  # Fermat witness of compositeness
            if pow(a, (N - 1) // q, N) != 1:
                found = a
                break
        if found is None:
            if N <= SMALL_PRIMES[-1] ** 2:
                # tiny N: fall back to trial division (complete, since we divided above)
                found = 0
            else:
                raise RuntimeError(f"no Lucas witness for q={q}, N=2^{i}*3^{j}+1")
        cert[q] = found
    return cert


def pierpont_points(amax: int, bmax: int, with_cert: bool = False):
    """All (i, j), 1 <= i <= amax, 0 <= j <= bmax, (i, j) != (1, 0), with 2^i 3^j + 1 prime.

    These are exactly the Pierpont primes > 3 inside the box.
    """
    out = []
    for i in range(1, amax + 1):
        for j in range(0, bmax + 1):
            if (i, j) == (1, 0):
                continue
            c = lucas_certificate(i, j)
            if c is not None:
                out.append((i, j, c) if with_cert else (i, j))
    return out


if __name__ == "__main__":
    import sympy
    pts = pierpont_points(40, 40, with_cert=True)
    print("Pierpont points (i,j) with i,j <= 40:", len(pts))
    bad = 0
    for i, j, c in pts:
        if not sympy.isprime((1 << i) * 3 ** j + 1):
            bad += 1
    # and the converse: nothing sympy calls prime was rejected
    S = {(i, j) for i, j, _ in pts}
    miss = 0
    for i in range(1, 41):
        for j in range(0, 41):
            if (i, j) != (1, 0) and sympy.isprime((1 << i) * 3 ** j + 1) and (i, j) not in S:
                miss += 1
    print("disagreements with sympy.isprime (BPSW): false-accept", bad, "false-reject", miss)
    print("first few primes:", sorted((1 << i) * 3 ** j + 1 for i, j, _ in pts)[:25])
