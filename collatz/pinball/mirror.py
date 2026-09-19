"""The mirror table: n -> n - |n/2| on even n, 3n+1 on odd n.

For n > 0 this is the Collatz map. For n < 0, n - |n/2| = 3n/2, so on
magnitudes m = |n| the map is

    m -> 3m - 1   (m odd),      m -> 3m / 2   (m even).

Every step raises the magnitude and the map is injective: instead of throwing
the factors of 2 away it converts them to factors of 3. Run backwards it is a
terminating 'divide by 3' process, which gives every negative integer an AGE
(steps back to a value with no preimage) determined by its residue mod 2*3^age
-- the 3-adic mirror of stopping classes, which are determined mod 2^k.
"""


def mirror_step(n: int) -> int:
    """One step of n -> 3n+1 (odd), n - |n/2| (even). Collatz for n > 0.

    Example: mirror_step(-2) = -3;  mirror_step(-3) = -8;  mirror_step(6) = 3
    """
    if n == 0:
        raise ValueError("n must be non-zero")
    return 3 * n + 1 if n % 2 else n - abs(n) // 2


def mirror_orbit(n: int, steps: int) -> list[int]:
    """The first `steps` iterates, including n.

    Example: mirror_orbit(-1, 6) = [-1, -2, -3, -8, -12, -18, -27]
    """
    seq = [n]
    for _ in range(steps):
        seq.append(mirror_step(seq[-1]))
    return seq


def mirror_back(m: int):
    """Unique predecessor of magnitude m, as (predecessor, branch), or None.

    Branch 'A': m = 3p/2 for even p   (needs 3 | m)           -> p = 2m/3
    Branch 'B': m = 3p - 1 for odd p  (needs m = 2 mod 6)     -> p = (m+1)/3
    Magnitudes m = 1 mod 3 or m = 5 mod 6 have no predecessor (density 1/2).

    Example: mirror_back(27) = (18, 'A');  mirror_back(8) = (3, 'B');  mirror_back(5) = None
    """
    if m % 3 == 0:
        return 2 * m // 3, "A"
    if m % 6 == 2:
        return (m + 1) // 3, "B"
    return None


def age_word(m: int) -> str:
    """Branches taken walking back from magnitude m to its seed, newest first.

    Never contains 'BB': branch B lands on an odd value, which branch B cannot
    leave. Age words are exactly the golden-mean shift.

    Example: age_word(27) = 'AAABAB'   -- 27 <- 18 <- 12 <- 8 <- 3 <- 2 <- 1
    """
    word = ""
    while (step := mirror_back(m)) is not None:
        m, branch = step
        word += branch
    return word


def age(m: int) -> int:
    """Steps back from magnitude m to a value with no predecessor.

    Example: age(27) = 6;  age(5) = 0
    """
    return len(age_word(m))


def seed(m: int) -> int:
    """The predecessor-free magnitude whose forward orbit contains m.

    (seed(m), age(m)) are unique coordinates for every positive magnitude.
    Example: seed(27) = 1   -- 27 lies on the orbit of -1
    """
    while (step := mirror_back(m)) is not None:
        m = step[0]
    return m


def age_tail(t: int) -> tuple[int, int]:
    """P(age >= t) as (numerator, denominator) = (Fibonacci(t+3), 2 * 3^t).

    Example: age_tail(1) = (3, 6);  age_tail(4) = (13, 162)
    """
    a, b = 0, 1
    for _ in range(t + 3):
        a, b = b, a + b
    return a, 2 * 3 ** t
