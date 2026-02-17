"""Stopping Time / Class / Point / Signature / Modulus (Paper 2 terminology).

Paper 2: "The Geometric Collatz Correspondence"

Key definitions:
- Stopping Time: steps to first value < n (same as dropping time)
- Stopping Destination: first value < n (same as dropping destination)
- Stopping Orbit: [f(n), ..., d] (excludes n, includes destination)
- Stopping Point: (Sdest - n, Sdest) — a point in the plane
- Stopping Class_k: all n with stopping time = k
- Stopping Modulus_k: number of distinct offset lines for class k
- Stopping Page: which "page" n falls on (1-indexed)
- Stopping Offset: which line within the page (0-indexed)
- Stopping Signature: (time, page, offset) — unique identifier in Collatz Address Space
"""

from fractions import Fraction

import pandas as pd

from .core import collatz_step, stopping_time as _core_stopping_time
from .core import stopping_destination as _core_stopping_dest
from .core import stopping_orbit as _core_stopping_orbit


def stopping_time(n):
    """Number of steps to first reach a value < n.

    Example: stopping_time(5) = 3, stopping_time(27) = 96.
    """
    return _core_stopping_time(n)


def stopping_destination(n):
    """First value < n reached via iteration.

    Example: stopping_destination(19) = 11.
    """
    return _core_stopping_dest(n)


def stopping_orbit(n):
    """Orbit from f(n) to the stopping destination.

    Paper 2 convention: excludes n, includes destination.
    Example: stopping_orbit(19) = [58, 29, 88, 44, 22, 11]
    """
    return _core_stopping_orbit(n)


def stopping_point(n):
    """Stopping Point = (Sdest - n, Sdest).

    Maps each integer to a point in the plane.
    Example: stopping_point(19) = (-8, 11)
    """
    d = stopping_destination(n)
    return (d - n, d)


def stopping_class(n):
    """Which Stopping Class does n belong to? Returns the stopping time k.

    Stopping Class_k = {n : stopping_time(n) = k}.
    """
    return stopping_time(n)


def stopping_modulus_for_class(k, search_limit=None):
    """Number of distinct offset lines for Stopping Class_k.

    Examines the pattern of stopping points to determine how many
    parallel lines the points fall on.

    Example: stopping_modulus_for_class(3) = 1
    Example: stopping_modulus_for_class(8) = 2
    """
    if search_limit is None:
        search_limit = max(500, k * 100)
    members = sorted(
        n for n in range(2, search_limit) if stopping_time(n) == k
    )
    if len(members) < 4:
        return 1
    # Compute x-values of stopping points
    x_vals = [stopping_destination(n) - n for n in members]
    # Find period in differences
    diffs = [x_vals[i + 1] - x_vals[i] for i in range(len(x_vals) - 1)]
    for period in range(1, len(diffs) // 2 + 1):
        pattern = diffs[:period]
        if all(
            diffs[i] == pattern[i % period]
            for i in range(min(len(diffs), period * 3))
        ):
            return period
    return 1


def stopping_page(n):
    """Stopping Page of n (1-indexed).

    Analogous to a memory page. Numbers with the same stopping page
    tend to be located in the same geometric area.

    Example: For class 8: n=11 → page 1, n=43 → page 2, n=75 → page 3.
    """
    k = stopping_class(n)
    mod = stopping_modulus_for_class(k)
    idx = _class_index(n, k)
    return idx // mod + 1


def stopping_offset(n):
    """Stopping Offset of n (0-indexed).

    Distance from the lower Stopping Page boundary.
    Example: For class 8: n=11 → offset 0, n=23 → offset 1.
    """
    k = stopping_class(n)
    mod = stopping_modulus_for_class(k)
    idx = _class_index(n, k)
    return idx % mod


def stopping_signature(n):
    """Stopping Signature = (Stopping Time, Stopping Page, Stopping Offset).

    Uniquely identifies an orbit by its location in Collatz Address Space.
    Example: stopping_signature(11) = (8, 1, 0)
    Example: stopping_signature(23) = (8, 1, 1)
    """
    return (stopping_time(n), stopping_page(n), stopping_offset(n))


def stopping_line_slope(k, search_limit=None):
    """Slope of the Diophantine line for Stopping Class_k.

    All stopping points in a class share the same slope (across all offset lines).
    Returns a Fraction for exact representation.

    Example: stopping_line_slope(3) = Fraction(-3, 1)
    Example: stopping_line_slope(6) = Fraction(-9, 7)
    """
    if search_limit is None:
        search_limit = max(500, k * 100)
    members = sorted(
        n for n in range(2, search_limit) if stopping_time(n) == k
    )
    if len(members) < 2:
        raise ValueError(f"Not enough members found for class {k}")
    p1 = stopping_point(members[0])
    p2 = stopping_point(members[1])
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if dx == 0:
        raise ValueError("Vertical line — undefined slope")
    return Fraction(dy, dx)


def classify_range(start, end):
    """Classify all integers in [start, end) with stopping properties.

    Returns a DataFrame with columns:
    n, stopping_time, stopping_destination, stopping_point_x, stopping_point_y,
    stopping_class, stopping_page, stopping_offset
    """
    rows = []
    for n in range(start, end):
        if n <= 1:
            continue
        st = stopping_time(n)
        sd = stopping_destination(n)
        sp = stopping_point(n)
        rows.append({
            "n": n,
            "stopping_time": st,
            "stopping_destination": sd,
            "stopping_point_x": sp[0],
            "stopping_point_y": sp[1],
            "stopping_class": st,
        })
    df = pd.DataFrame(rows)
    return df


def _class_index(n, k, search_limit=None):
    """0-based index of n within Stopping Class_k (sorted by magnitude)."""
    if search_limit is None:
        search_limit = n + 1
    members = sorted(m for m in range(2, search_limit) if stopping_time(m) == k)
    return members.index(n)
