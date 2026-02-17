"""Shared helpers: caching, batch computation."""

from functools import lru_cache


@lru_cache(maxsize=None)
def _collatz_step_cached(n):
    """Cached single Collatz step."""
    return n // 2 if n % 2 == 0 else 3 * n + 1


def batch_apply(func, start, end):
    """Apply a classification function to a range of integers.

    Returns a list of (n, result) tuples for n in [start, end).
    """
    return [(n, func(n)) for n in range(start, end)]


def members_of_class(class_func, class_value, limit):
    """Find all integers n in [2, limit) belonging to a given class.

    Args:
        class_func: function that maps n -> class value (e.g., dropping_set)
        class_value: the target class value
        limit: upper bound (exclusive)

    Returns:
        Sorted list of integers belonging to that class.
    """
    return [n for n in range(2, limit) if class_func(n) == class_value]
