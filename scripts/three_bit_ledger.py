"""Verify the conservation-ledger identities behind the countdown hierarchy.

For odd m, one Syracuse step m2 = (3m+1)/2^d acts LINEARLY on the form
F_d(m) = (2^d - 3)m - 1, whose fixed point is 1/(2^d - 3):

    F_d(m2) = 3 * F_d(m) / 2^d          ... (exact identity, all odd m)

so each step of depth d trades exactly d bits of v2(F_d) for one 3-adic digit
of v3(F_d).  Specializations:
    d=1 (growth): m2+1 = 3(m+1)/2        [F_1 = -(m+1); One-Bit Countdown]
    d=2 (weak):   m2-1 = 3(m-1)/4        [F_2 = m-1;    Two-Bit Countdown]
    d=3 (medium): 5m2-1 = 3(5m-1)/8      [F_3 = 5m-1;   Three-Bit form]
    d=4 (strong): 13m2-1 = 3(13m-1)/16   [F_4 = 13m-1]

Also verifies the encounter classification in v2(F) terms and the backward-
chain gate duality: consecutive backward steps of type d are gated by
v3(F_d) >= 1, and an L-chain of length k needs v3(F_d) >= k.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collatz.core import v2 as _v2  # noqa: E402


def v2(n: int) -> int:
    return _v2(abs(n))


def v3(n: int) -> int:
    n = abs(n)
    k = 0
    while n % 3 == 0:
        n //= 3
        k += 1
    return k


def main() -> None:
    rng = random.Random(20260728)

    # 1. The master identity F_d(m2) = 3 F_d(m) / 2^d, exact, for the actual
    #    step depth d = v2(3m+1) of each m.
    for _ in range(200_000):
        m = rng.randrange(3, 1 << 64) | 1
        t = 3 * m + 1
        d = v2(t)
        m2 = t >> d
        c = (1 << d) - 3
        assert (c * m2 - 1) * (1 << d) == 3 * (c * m - 1), (m, d)
    print("master identity F_d(m2) = 3 F_d(m)/2^d: 200K random 64-bit odd m, exact")

    # 2. Ledger: v2 down by d, v3 up by 1 (needs v2(F_d(m)) >= d, v3 exact)
    for _ in range(200_000):
        m = rng.randrange(3, 1 << 64) | 1
        t = 3 * m + 1
        d = v2(t)
        m2 = t >> d
        c = (1 << d) - 3
        f, f2 = c * m - 1, c * m2 - 1
        assert v2(f2) == v2(f) - d, (m, d)
        assert v3(f2) == v3(f) + 1, (m, d)
    print("ledger: v2(F_d) -= d and v3(F_d) += 1 per depth-d step: 200K cases, exact")

    # 3. Depth classification at encounters, in v2-of-form terms
    for m in range(5, 1 << 18, 4):
        d = v2(3 * m + 1)
        if d == 2:
            assert v2(m - 1) >= 3
        elif d == 3:
            assert v2(m - 1) == 2 and v2(5 * m - 1) >= 4
        else:
            assert v2(m - 1) == 2 and v2(5 * m - 1) == 3
    print("classification: weak <=> v2(m-1)>=3; medium <=> v2(5m-1)>=4; "
          "strong <=> v2(5m-1)=3  (given encounter)")

    # 4. Backward-chain gas: k consecutive growth-preimages from m exist
    #    iff v3(m+1) >= k, and the chain divides |m+1|'s 3-part exactly.
    for _ in range(20_000):
        m = rng.randrange(3, 1 << 40) | 1
        k = v3(m + 1)
        x = m
        for i in range(k):
            assert x % 3 == 2, (m, i)
            x = (2 * x - 1) // 3
        assert x % 3 != 2 or v3(x + 1) == 0, m
        assert (x + 1) * 3**k == (m + 1) << k or k == 0, m
    print("backward gas: growth-preimage chain length = v3(m+1), exact")

    # 5. Weak-preimage chains gated by v3(m-1)
    for _ in range(20_000):
        m = rng.randrange(5, 1 << 40) | 1
        k = v3(m - 1)
        x = m
        for i in range(k):
            assert x % 3 == 1, (m, i)
            x = (4 * x - 1) // 3
        assert x % 3 != 1
    print("backward gas: weak-preimage chain length = v3(m-1), exact")


if __name__ == "__main__":
    main()
