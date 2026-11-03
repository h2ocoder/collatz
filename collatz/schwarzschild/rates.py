"""Haar rates: the address-space face of the Schwarzschild analogy.

Under Haar measure on the d-adic integers the digits of an orbit are independent
and uniform (the digit bijection), so the scale factor Q / d^t is a random walk:

    c      = log2 d                  bits of address read per step, on every branch
    g      = log2 d - E[log2 q_r]    bits of size lost per step, independent of n
    memory = E[log2 q_r]             bits written into residues mod q per step

Radius is address depth and mass is lift, the bits an orbit climbs above its
start. The information radius

    r_s(M) = -log2 mu(lift >= M) = theta M + O(1)

is governed by the Cramer root theta of (1 / d) sum (q_r / d)^theta = 1, and the
Gaussian (weak-field) limit of theta is 2 g / (sigma^2 ln 2), the shape of
2 G M / c^2. Statements about Haar-typical points are exact. Applying them to an
integer past the point where its digits run out is a heuristic, and the vault
says so: research/information-schwarzschild-radius/Information Radius.md.
"""

import math
from dataclasses import dataclass

import numpy as np

from collatz.schwarzschild.system import COLLATZ, CollatzLike


def bisect_root(function, low: float, high: float) -> float:
    """A root of function on [low, high], given a sign change, to double precision."""
    low_is_positive = function(low) > 0
    for _ in range(300):
        middle = (low + high) / 2
        if middle in (low, high):
            break
        if (function(middle) > 0) == low_is_positive:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def _over_sigma(top: float, spread: float) -> float:
    """top / spread, with the signed infinity when the branches share one speed."""
    return top / spread if spread else math.copysign(math.inf, top)


def size_steps(system: CollatzLike = COLLATZ) -> list[float]:
    """log2(q_r / d) per residue: how many bits of size each branch adds at large n."""
    return [math.log2(q) - math.log2(system.d) for q in system.q]


def head_speed(system: CollatzLike = COLLATZ) -> float:
    """c = log2 d: bits of address consumed per step, the same on every branch."""
    return math.log2(system.d)


def memory_rate(system: CollatzLike = COLLATZ) -> float:
    """E[log2 q_r]: bits per step stored in residues modulo the multipliers."""
    return sum(math.log2(q) for q in system.q) / system.d


def drift(system: CollatzLike = COLLATZ) -> float:
    """g = c - memory: mean bits of size lost per step.

    Example: round(drift(), 4) = 0.2075 for the classic map
    """
    return head_speed(system) - memory_rate(system)


def step_sigma(system: CollatzLike = COLLATZ) -> float:
    """Standard deviation of the size step, in bits per sqrt(step).

    For a two-branch map this is half the gap between the two speeds, so it is
    also the fastest possible motion relative to the mean flow.
    """
    steps = size_steps(system)
    mean = sum(steps) / len(steps)
    return math.sqrt(sum((x - mean) ** 2 for x in steps) / len(steps))


def mach_number(system: CollatzLike = COLLATZ) -> float:
    """g / sigma: how fast the mean flow runs compared with the step speed.

    Infinite when every branch has the same multiplier, because then sigma = 0.
    """
    return _over_sigma(drift(system), step_sigma(system))


def place_exponents(system: CollatzLike = COLLATZ) -> dict:
    """Haar-mean log2 |T'|_v at each place v. The values sum to zero.

    Keys are "inf" and each prime dividing d or a multiplier. The zero sum is the
    product formula, so it holds for every map and carries no information about
    any particular one (docs/Conjectures/Proof Attempt - Adelic IFS Bridge.md).

    Example: for the classic map {"inf": -0.2075, 2: 1.0, 3: -0.7925}
    """
    exponents = {"inf": -drift(system)}
    for prime in sorted(_primes_of(system)):
        total = 0.0
        for q in system.q:
            total += (_valuation(system.d, prime) - _valuation(q, prime)) * math.log2(prime)
        exponents[prime] = total / system.d
    return exponents


def _primes_of(system: CollatzLike) -> set:
    primes = set()
    for value in (system.d, *system.q):
        p = 2
        while value > 1:
            if value % p == 0:
                primes.add(p)
                value //= p
            else:
                p += 1
    return primes


def _valuation(value: int, prime: int) -> int:
    count = 0
    while value % prime == 0:
        value //= prime
        count += 1
    return count


def cramer_exponent(system: CollatzLike = COLLATZ) -> float:
    """theta > 0 with (1 / d) sum (q_r / d)^theta = 1: the price of one bit of height.

    Returns 1.0 exactly when sum q_r = d^2, where E[T(n)] = n + const, so n is a
    martingale up to the offsets. Returns inf if no branch expands (q_r <= d for
    all r), because then no lift is possible at any price, and 0.0 if g <= 0,
    because then lift costs nothing.

    Example: cramer_exponent() = 1.0    -- (3/2)^1 + (1/2)^1 = 2
    """
    if max(system.q) <= system.d:
        return math.inf
    if drift(system) <= 0:
        return 0.0
    if sum(system.q) == system.d ** 2:
        return 1.0

    def excess(theta):
        return sum((q / system.d) ** theta for q in system.q) / system.d - 1

    high = 1.0
    while excess(high) < 0:
        high *= 2
    low = high / 2
    while excess(low) > 0:
        low /= 2
    return bisect_root(excess, low, high)


def weak_field_exponent(system: CollatzLike = COLLATZ) -> float:
    """2 g / (sigma^2 ln 2): the Gaussian limit of theta, exact as g -> 0.

    With G = g and c = sigma this is r_s / M = 2 G / c^2, in bits of address per
    bit of lift. Measured in nats the ln 2 goes away.

    Example: round(weak_field_exponent(), 4) = 0.9534, against the exact 1
    """
    return _over_sigma(2 * drift(system) / math.log(2), step_sigma(system) ** 2)


def tail_constant(system: CollatzLike = COLLATZ) -> float | None:
    """Goldie's C in P(F > t) ~ C / t, available in closed form when theta = 1.

    The stationary law of the random recursion x -> (q_r x + a_r) / d has a
    Kesten tail of index theta. For theta = 1, Goldie's formula reduces to
    E[B] / E[A ln A] with A = q_r / d and B = a_r / d.

    Example: tail_constant() = 1 / ln(27/16) = 1.9111
    """
    if cramer_exponent(system) != 1.0:
        return None
    d = system.d
    mean_b = sum(system.a) / d ** 2
    moment = sum((q / d) * math.log(q / d) for q in system.q) / d
    return mean_b / moment


def tilted_law(eta: float, system: CollatzLike = COLLATZ) -> list[float]:
    """Digit law p_r proportional to q_r^eta: the extremal laws below all have this form."""
    logs = [eta * math.log(q) for q in system.q]
    top = max(logs)
    weights = [math.exp(x - top) for x in logs]
    total = sum(weights)
    return [w / total for w in weights]


def _entropy(law) -> float:
    return -sum(p * math.log2(p) for p in law if p > 0)


def _mean_log_q(law, system: CollatzLike) -> float:
    return sum(p * math.log2(q) for p, q in zip(law, system.q))


@dataclass(frozen=True)
class Path:
    """An extremal way to spend address bits.

    law: digit frequencies along the path. speed: bits of size per step, signed.
    cost: Kullback-Leibler distance from uniform digits, bits of address per step.
    """

    law: tuple[float, ...]
    speed: float
    cost: float


def _path(law, system: CollatzLike) -> Path:
    return Path(tuple(law), _mean_log_q(law, system) - head_speed(system),
                head_speed(system) - _entropy(law))


def cheapest_climb(system: CollatzLike = COLLATZ) -> Path | None:
    """The digit law that rises at the lowest address cost per bit of height.

    It is p_r = (q_r / d)^theta / d, and cost / speed = theta. None if the map
    cannot climb or climbing is free.

    Example: the classic map kicks with frequency 3/4 and rises 0.1887 bits per
    step, the slope Lagarias and Weiss predict for extremal orbits.
    """
    theta = cramer_exponent(system)
    if theta in (0.0, math.inf):
        return None
    return _path([(q / system.d) ** theta / system.d for q in system.q], system)


def reach_exponent(system: CollatzLike = COLLATZ) -> float:
    """1 + 1 / theta: log(peak) / log(n) once an integer has spent all its address.

    Inf when g <= 0. For the classic map this is the Lagarias-Weiss constant 2.
    Heuristic for integers: a first-moment count over 2^B candidates.
    """
    theta = cramer_exponent(system)
    return math.inf if theta == 0.0 else 1 + 1 / theta


def longest_hover(system: CollatzLike = COLLATZ) -> Path | None:
    """The cheapest digit law with zero size drift, or None if the map cannot hover.

    The stopping time of a B-bit integer is at most B / cost in the first-moment
    count. For the classic map cost = 1 - H(log_3 2) = 0.0500, about 20 B steps.
    """
    if max(system.q) <= system.d or drift(system) <= 0:
        return None

    def excess(eta):
        return _mean_log_q(tilted_law(eta, system), system) - head_speed(system)

    high = 1.0
    while excess(high) < 0:
        high *= 2
    return _path(tilted_law(bisect_root(excess, 0.0, high), system), system)


def longest_fall(system: CollatzLike = COLLATZ) -> Path | None:
    """The slowest sustainable descent, or None if orbits do not fall on average.

    A descent of B bits at speed v takes B / v steps and costs cost B / v address
    bits, so it is affordable while cost <= v. That reads H(p) >= E_p[log2 q]: the
    digit entropy must cover what the residues store. At the slowest descent the
    two are equal.

    Example: the classic map gives kick frequency 0.609090 and
    1 / (v ln 2) = 41.677648, the Lagarias-Weiss constant.
    """
    if drift(system) <= 0:
        return None
    if len(set(system.q)) == 1:
        return _path([1 / system.d] * system.d, system)

    def excess(eta):
        law = tilted_law(eta, system)
        return _entropy(law) - _mean_log_q(law, system)

    high = 1.0
    while excess(high) > 0 and high < 1e6:
        high *= 2
    if excess(high) > 0:
        return _path(tilted_law(high, system), system)
    return _path(tilted_law(bisect_root(excess, 0.0, high), system), system)


def stagnation_radius(system: CollatzLike = COLLATZ) -> float | None:
    """The n where the Haar-mean log step vanishes, offsets included, or None.

    Above it the mean flow is inward. For d = 2 this is the horizon a / (4 - q) of
    the typical word (1, 0), which is the trivial cycle for 3x + a. None if the
    mean flow never turns inward, or the offsets are all zero or include a negative.

    Example: stagnation_radius() = 1.0
    """
    if drift(system) <= 0 or not any(system.a) or min(system.a) < 0:
        return None

    def mean_step(log_n):
        n = math.exp(log_n)
        return sum(math.log2((q + a / n) / system.d) for q, a in zip(system.q, system.a)) / system.d

    low, high = -1.0, 1.0
    while mean_step(low) < 0:
        low *= 2
    while mean_step(high) > 0:
        high *= 2
    return math.exp(bisect_root(mean_step, low, high))


def trapping_radius(system: CollatzLike = COLLATZ) -> float | None:
    """max a_r / (d - q_r) if every q_r < d and every a_r >= 0, else None.

    This is a hard horizon, and it needs no statistics: above it T(n) < n on every
    branch, so all orbits enter [0, trapping_radius]. Each branch's own bound is
    the place where that branch's fastest outgoing motion stops, r_s = a / (d - q).
    A negative offset can throw an orbit below zero, which is why offsets must be
    non-negative: d = 3, q = (1, 2, 2), a = (0, -5, -1) sends 1 to -1.

    Example: CollatzLike.from_multipliers((1, 2, 2)) has trapping radius 2.0
    """
    if max(system.q) >= system.d or min(system.a) < 0:
        return None
    return max(a / (system.d - q) for q, a in zip(system.q, system.a))


def phase(system: CollatzLike = COLLATZ) -> str:
    """Where a map sits relative to the three critical lines.

    interior:   every q_r < d. All orbits fall into a hard horizon (a theorem).
    thin:       g > 0 and theta > 1. E[T(n)] contracts.
    critical:   theta = 1. n is a martingale up to offsets, as for 3x + 1.
    heavy:      g > 0 and theta < 1. Typical orbits fall but E[T(n)] grows.
    outflow:    g <= 0. Typical orbits rise.
    """
    theta = cramer_exponent(system)
    if theta == math.inf:
        return "interior"
    if theta == 0.0:
        return "outflow"
    if theta == 1.0:
        return "critical"
    return "thin" if theta > 1 else "heavy"


def _climb_steps(system: CollatzLike, theta: float) -> tuple[np.ndarray, np.ndarray]:
    steps = np.array(size_steps(system))
    law = np.array([(q / system.d) ** theta / system.d for q in system.q])
    return steps, law / law.sum()


def information_radius(lift: float, system: CollatzLike = COLLATZ, samples: int = 200_000,
                       seed: int = 0) -> float:
    """r_s(M) = -log2 mu(lift >= M): the address depth that can carry a lift of M bits.

    Uses the exact change of measure mu(tau < infinity) = E~[2^(-theta S_tau)],
    where E~ runs the walk under cheapest_climb's law, which always reaches the
    level. Sampling error is small because the overshoot is bounded by one step.
    It works in log space, so a large lift does not underflow. Returns 0.0 when
    g <= 0, since lift is then free, and inf when the map cannot climb.

    Example: information_radius(16) is about 16.26: theta = 1 plus a constant
    """
    theta = cramer_exponent(system)
    if theta == 0.0:
        return 0.0
    if theta == math.inf:
        return math.inf
    steps, law = _climb_steps(system, theta)
    rng = np.random.default_rng(seed)
    position = np.zeros(samples)
    active = np.ones(samples, dtype=bool)
    while active.any():
        count = int(active.sum())
        position[active] += rng.choice(steps, size=count, p=law)
        active[active] = position[active] < lift
    overshoot = position - lift
    return theta * lift - math.log2(float(np.mean(2.0 ** (-theta * overshoot))))


def lift_tail(lift: float, system: CollatzLike = COLLATZ, samples: int = 200_000,
              seed: int = 0) -> float:
    """mu(sup of the size walk >= lift) under Haar measure, for lift > 0.

    This is 2^(-information_radius(lift)). It is 1.0 when g <= 0 and 0.0 when the
    map cannot climb. A large enough lift underflows to 0.0, so use
    information_radius there.
    """
    return 2.0 ** -information_radius(lift, system, samples, seed)
