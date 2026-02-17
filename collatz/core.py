"""Core Collatz functions: step, orbit, stopping time, Syracuse map."""


def collatz_step(n):
    """Single step of the Collatz function f(n).

    f(n) = n/2 if n is even, 3n+1 if n is odd.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    return n // 2 if n % 2 == 0 else 3 * n + 1


def orbit(n):
    """Full Collatz orbit from n down to 1.

    Returns the sequence [n, f(n), f²(n), ..., 1].
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    seq = [n]
    while n != 1:
        n = collatz_step(n)
        seq.append(n)
    return seq


def total_stopping_time(n):
    """Number of steps to reach 1 from n."""
    if n <= 0:
        raise ValueError("n must be a positive integer")
    steps = 0
    while n != 1:
        n = collatz_step(n)
        steps += 1
    return steps


def stopping_time(n):
    """Steps to first value < n (called 'dropping time' in Paper 1).

    For n=5: 5→16→8→4, returns 3 (three steps to reach 4 < 5).
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    start = n
    steps = 0
    while True:
        n = collatz_step(n)
        steps += 1
        if n < start:
            return steps


def stopping_destination(n):
    """First value < n reached via the Collatz function.

    For n=5: returns 4 (since 5→16→8→4).
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    start = n
    while True:
        n = collatz_step(n)
        if n < start:
            return n


def stopping_orbit(n):
    """Orbit segment from n to first value < n.

    Returns [f(n), f²(n), ..., d] where d < n is the stopping destination.
    Excludes n, includes destination (Paper 2 convention).
    """
    if n <= 1:
        raise ValueError("n must be > 1")
    start = n
    seq = []
    while True:
        n = collatz_step(n)
        seq.append(n)
        if n < start:
            return seq


# ---------------------------------------------------------------------------
# Syracuse (odd-only) map
# ---------------------------------------------------------------------------

def v2(n):
    """2-adic valuation of n: the largest k such that 2^k divides n.

    Equivalently, the number of trailing zeros in binary.
    Example: v2(12) = 2  (12 = 4 × 3), v2(8) = 3, v2(7) = 0.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k


def syracuse_step(n):
    """Single step of the Syracuse (odd-only) map.

    S(n) = (3n + 1) / 2^v₂(3n+1)

    Takes an odd number directly to the next odd number in the Collatz orbit.
    The number of halvings skipped equals v₂(3n + 1), captured by alpha_value().

    Example: syracuse_step(3) = 5  (3→10→5, skipping one even step)
    Example: syracuse_step(5) = 1  (5→16→8→4→2→1, skipping four even steps)
    """
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")
    val = 3 * n + 1
    return val // (val & -val)  # divide by 2^v2 using bit trick


def syracuse_orbit(n):
    """Full Syracuse orbit from odd n down to 1.

    Returns the sequence of odd numbers visited: [n, S(n), S²(n), ..., 1].
    This is the Collatz orbit with all even numbers stripped out.

    Example: syracuse_orbit(7) = [7, 11, 17, 13, 5, 1]
    """
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")
    seq = [n]
    while n != 1:
        n = syracuse_step(n)
        seq.append(n)
    return seq


def syracuse_stopping_time(n):
    """Syracuse steps to first odd value < n.

    Example: syracuse_stopping_time(7) = 4  (7→11→17→13→5, four Syracuse steps)
    """
    if n <= 1:
        raise ValueError("n must be an odd integer > 1")
    if n % 2 == 0:
        raise ValueError("n must be odd")
    start = n
    steps = 0
    while True:
        n = syracuse_step(n)
        steps += 1
        if n < start:
            return steps


def alpha_value(n):
    """The 2-adic valuation of 3n+1 for odd n.

    This is the number of halvings that follow a 3n+1 step — it controls
    the "shape" of each Syracuse step. The sequence of alpha values along
    an orbit completely determines the orbit's structure.

    Example: alpha_value(3) = 1  (3→10, v₂(10) = 1)
    Example: alpha_value(5) = 4  (5→16, v₂(16) = 4)
    """
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")
    return v2(3 * n + 1)


def alpha_sequence(n):
    """Sequence of alpha (2-adic valuation) values along the Syracuse orbit.

    For each odd number visited, records how many halvings follow.
    The alpha sequence is a complete fingerprint of the orbit's branching pattern.
    The sum of all alpha values equals the total number of even steps in the orbit.

    Returns list of alpha values (one per Syracuse step, excludes the final 1).

    Example: alpha_sequence(3) = [1, 4]
             (3→5: alpha=1, 5→1: alpha=4, total even steps = 5)
    Example: alpha_sequence(7) = [1, 1, 1, 3, 4]
    """
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")
    alphas = []
    while n != 1:
        alphas.append(alpha_value(n))
        n = syracuse_step(n)
    return alphas
