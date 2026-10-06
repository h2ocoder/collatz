"""Shared exact tools for the golden_kernel thread (thread 3 of scripts/thirty_six).

CONVENTIONS (used by every script in this directory)
  * Shortcut (Terras) map T(n) = n/2 (n even), (3n+1)/2 (n odd).  On a residue ring Z/N with
    gcd(N, 6) = 1 the two branches are the affine bijections
        e(x) = x/2,      o(x) = (3x+1)/2      (division = multiplication by the inverse mod N).
  * Terras kernel (the Matthews-Watts matrix of the map mod N), acting on FUNCTIONS f : Z/N -> C:
        (K f)(x) = (1/2) f(e x) + (1/2) f(o x).
    We always work with the integer matrix  A = 2K = R_e + R_o,  A[x, e(x)] += 1, A[x, o(x)] += 1,
    a sum of two permutation matrices.  Eigenvalues of K are eigenvalues of A divided by 2.
  * A acts on measures (row vectors) by push-forward:  (mu A)(y) = mu(e^-1 y) + mu(o^-1 y).
    "Left eigenvector" = eigen-measure = eigenfunctional;  "right eigenvector" = eigenfunction.
  * Generalised pair (q, d):  e(x) = x/d,  o(x) = (qx+1)/d,  needs gcd(N, d) = 1.
  * Psi_m(x) = minimal polynomial over Q of 2cos(2 pi / m)  (degree phi(m)/2 for m >= 3;
    Psi_1 = x - 2, Psi_2 = x + 2).  Phi_k = k-th cyclotomic polynomial.
    Kronecker (1857): an algebraic integer all of whose conjugates are real and in [-2, 2] is
    2cos(2 pi j/m); one all of whose conjugates lie in the closed unit disc is 0 or a root of unity.

Everything here is exact integer arithmetic (multimodular + CRT with a proved coefficient bound).
"""
from __future__ import annotations

from math import gcd

import numpy as np

# ----------------------------------------------------------------------------- number theory


def primes_upto(n: int) -> list[int]:
    s = bytearray([1]) * (n + 1)
    s[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i :: i] = bytearray(len(s[i * i :: i]))
    return [i for i in range(n + 1) if s[i]]


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def order(a: int, n: int) -> int:
    """multiplicative order of a modulo n (gcd(a, n) = 1)."""
    a %= n
    k, x = 1, a
    while x != 1:
        x = x * a % n
        k += 1
    return k


def v2(n: int) -> int:
    return (n & -n).bit_length() - 1


def divisors(n: int) -> list[int]:
    return [d for d in range(1, n + 1) if n % d == 0]


def euler_phi(n: int) -> int:
    r, m, p = n, n, 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r


# ----------------------------------------------------------------------------- the kernel


def branches(N: int, q: int = 3, d: int = 2) -> tuple[list[int], list[int]]:
    """(e, o) as lists: e[x] = x/d, o[x] = (q x + 1)/d  in Z/N."""
    assert gcd(N, d) == 1
    inv = pow(d, -1, N)
    return [x * inv % N for x in range(N)], [(q * x + 1) * inv % N for x in range(N)]


def two_K(N: int, q: int = 3, d: int = 2, sign: int = 1) -> np.ndarray:
    """A = R_e + sign * R_o as an int64 matrix acting on functions (A f)(x) = f(e x) + sign f(o x)."""
    e, o = branches(N, q, d)
    A = np.zeros((N, N), dtype=np.int64)
    for x in range(N):
        A[x, e[x]] += 1
        A[x, o[x]] += sign
    return A


# ----------------------------------------------------------------------------- charpoly mod p

_MODS = [p for p in primes_upto(1 << 24) if p > (1 << 24) - 4000][::-1]   # ~250 primes just below 2^24


def charpoly_mod(A: np.ndarray, p: int) -> np.ndarray:
    """coefficients c[0..n] (c[k] = coefficient of x^k, monic) of det(xI - A) modulo the prime p.
    Hessenberg reduction + the Hessenberg recurrence; all intermediate values < 2^62 for n < 2^14."""
    H = (A % p).astype(np.int64)
    n = H.shape[0]
    for k in range(n - 2):
        col = H[k + 1 :, k]
        nz = np.nonzero(col)[0]
        if len(nz) == 0:
            continue
        i = k + 1 + int(nz[0])
        if i != k + 1:
            H[[k + 1, i], :] = H[[i, k + 1], :]
            H[:, [k + 1, i]] = H[:, [i, k + 1]]
        inv = pow(int(H[k + 1, k]), -1, p)
        c = (H[k + 2 :, k] * inv) % p
        if not c.any():
            continue
        H[k + 2 :, :] = (H[k + 2 :, :] - np.outer(c, H[k + 1, :])) % p
        H[:, k + 1] = (H[:, k + 1] + H[:, k + 2 :] @ c) % p
    # Hessenberg recurrence  p_k = (x - h_kk) p_{k-1} - sum_{j<k} h_{jk} (prod_{i=j+1..k} h_{i,i-1}) p_{j-1}
    P = np.zeros((n + 1, n + 1), dtype=np.int64)      # P[k] = coefficients of p_k
    P[0, 0] = 1
    for k in range(1, n + 1):
        pk = np.zeros(n + 1, dtype=np.int64)
        pk[1:] = P[k - 1, :-1]
        pk = (pk - int(H[k - 1, k - 1]) * P[k - 1]) % p
        if k >= 2:
            # weights w_j = h_{j,k} * prod_{i=j+1..k} h_{i,i-1}   (1-indexed j = 1..k-1)
            w = np.zeros(k - 1, dtype=np.int64)
            prod = 1
            for j in range(k - 1, 0, -1):
                prod = prod * int(H[j, j - 1]) % p          # h_{j+1, j} in 1-indexed terms
                w[j - 1] = int(H[j - 1, k - 1]) * prod % p
                if prod == 0:
                    break
            pk = (pk - w @ P[: k - 1]) % p
        P[k] = pk
    return P[n]


def crt_poly(residues: list[np.ndarray], mods: list[int]) -> list[int]:
    """symmetric-range CRT of coefficient vectors."""
    n = len(residues[0])
    M = 1
    out = [0] * n
    for r, m in zip(residues, mods):
        inv = pow(M % m, -1, m)
        for i in range(n):
            t = ((int(r[i]) - out[i]) * inv) % m
            out[i] += M * t
        M *= m
    half = M // 2
    return [c - M if c > half else c for c in out]


def charpoly_int(A: np.ndarray, radius: int = 2) -> list[int]:
    """exact integer characteristic polynomial det(xI - A), coefficient list c[k] of x^k.
    `radius` bounds the spectral radius (row sums of |A|), so |c_k| <= C(n,k) radius^(n-k) <= (1+radius)^n."""
    n = A.shape[0]
    bound = 2 * (1 + radius) ** n + 1
    mods, res, M = [], [], 1
    for p in _MODS:
        mods.append(p)
        res.append(charpoly_mod(A, p))
        M *= p
        if M > bound:
            break
    else:
        raise RuntimeError("not enough moduli")
    return crt_poly(res, mods)


# ----------------------------------------------------------------------------- integer polynomials (lists, c[k] ~ x^k)


def ptrim(a: list[int]) -> list[int]:
    a = list(a)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def pmul(a: list[int], b: list[int]) -> list[int]:
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return out


def pdivmod(a: list[int], b: list[int]) -> tuple[list[int], list[int]]:
    """division by a MONIC integer polynomial b."""
    a = list(a)
    b = ptrim(b)
    assert b[-1] == 1
    db = len(b) - 1
    if len(a) - 1 < db:
        return [0], ptrim(a)
    q = [0] * (len(a) - db)
    for i in range(len(a) - 1, db - 1, -1):
        c = a[i]
        if c:
            q[i - db] = c
            for j in range(db + 1):
                a[i - db + j] -= c * b[j]
    return ptrim(q), ptrim(a[:db] if db else [0])


def pdivides(b: list[int], a: list[int]) -> bool:
    return pdivmod(a, b)[1] == [0]


def multiplicity(b: list[int], a: list[int]) -> tuple[int, list[int]]:
    """largest k with b^k | a, and the cofactor."""
    k = 0
    while True:
        q, r = pdivmod(a, b)
        if r != [0]:
            return k, a
        a, k = q, k + 1


def peval_mod(a: list[int], x: int, m: int) -> int:
    r = 0
    for c in reversed(a):
        r = (r * x + c) % m
    return r


def pstr(a: list[int], var: str = "x") -> str:
    terms = []
    for k in range(len(a) - 1, -1, -1):
        c = a[k]
        if c == 0:
            continue
        mono = "" if k == 0 else (var if k == 1 else f"{var}^{k}")
        coef = abs(c)
        s = f"{coef}" if (coef != 1 or k == 0) else ""
        terms.append(("-" if c < 0 else "+") + " " + s + mono)
    if not terms:
        return "0"
    out = " ".join(terms)
    return out[2:] if out.startswith("+ ") else "-" + out[2:]


# ----------------------------------------------------------------------------- Psi_m and Phi_k

_psi_cache: dict[int, list[int]] = {}
_phi_cache: dict[int, list[int]] = {}


def cyclotomic(k: int) -> list[int]:
    """Phi_k as an integer coefficient list."""
    if k in _phi_cache:
        return _phi_cache[k]
    num = [-1] + [0] * (k - 1) + [1]          # x^k - 1
    for d in divisors(k):
        if d < k:
            num, r = pdivmod(num, cyclotomic(d))
            assert r == [0]
    _phi_cache[k] = num
    return num


def _chebyshev_C(n: int) -> list[int]:
    """C_n(x) with C_n(2cos t) = 2cos(n t):  C_0 = 2, C_1 = x, C_n = x C_{n-1} - C_{n-2}."""
    a, b = [2], [0, 1]
    if n == 0:
        return a
    for _ in range(n - 1):
        c = [0] + b
        for i, v in enumerate(a):
            c[i] -= v
        a, b = b, c
    return b


def psi(m: int) -> list[int]:
    """minimal polynomial of 2cos(2 pi/m) (monic, integer).  Uses  C_m(x) - 2 = prod_{d | m} Psi_d(x)^{e_d}
    with e_d = 1 for d in {1, 2} and 2 otherwise."""
    if m in _psi_cache:
        return _psi_cache[m]
    if m == 1:
        r = [-2, 1]
    elif m == 2:
        r = [2, 1]
    else:
        num = _chebyshev_C(m)
        num[0] -= 2
        for d in divisors(m):
            if d < m:
                e = 1 if d <= 2 else 2
                for _ in range(e):
                    num, rem = pdivmod(num, psi(d))
                    assert rem == [0], (m, d)
        # num = Psi_m^2
        r = _poly_sqrt(num)
    _psi_cache[m] = r
    return r


def _poly_sqrt(a: list[int]) -> list[int]:
    """exact square root of a monic integer polynomial of even degree that is a perfect square."""
    n = (len(a) - 1) // 2
    r = [0] * (n + 1)
    r[n] = 1
    for k in range(n - 1, -1, -1):
        # coefficient of x^(n+k) in r^2 = 2 r_k + sum_{i+j=n+k, k<i,j<n...}
        s = 0
        for i in range(k + 1, n + 1):
            j = n + k - i
            if k < j <= n:
                s += r[i] * r[j]
        num = a[n + k] - s
        assert num % 2 == 0
        r[k] = num // 2
    assert pmul(r, r) == list(a), "not a perfect square"
    return r


def kronecker_candidates(max_deg: int) -> tuple[list[int], list[int]]:
    """all m with deg Psi_m <= max_deg and all k with deg Phi_k <= max_deg (phi(n) > 2*max_deg for n > bound)."""
    ms, ks = [], []
    # phi(n) >= sqrt(n/2), so n <= 2 * (2*max_deg)^2 is a rigorous cap; in practice far smaller
    cap = 2 * (2 * max_deg) ** 2 + 8
    # sieve phi up to cap but stop early with the sharper bound phi(n) > n / (1.8 ln ln n + 3)  -- we simply sieve
    cap = min(cap, 20 * max_deg + 200)   # phi(n) >= n/ (e^gamma lnln n + 3/lnln n) > n/10 for n < 10^40
    ph = list(range(cap + 1))
    for i in range(2, cap + 1):
        if ph[i] == i:
            for j in range(i, cap + 1, i):
                ph[j] -= ph[j] // i
    for n in range(1, cap + 1):
        degpsi = 1 if n <= 2 else ph[n] // 2
        if degpsi <= max_deg:
            ms.append(n)
        if ph[n] <= max_deg:
            ks.append(n)
    return ms, ks
