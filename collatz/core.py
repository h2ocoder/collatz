"""Core Collatz functions: step, orbit, stopping time."""


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
