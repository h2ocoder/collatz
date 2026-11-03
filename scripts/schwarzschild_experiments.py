"""SCRUM-65: experiments for the information-theoretic Schwarzschild radius.

Run:  python -X utf8 scripts/schwarzschild_experiments.py [E1 E2 ...]
      (no arguments runs everything; E4 and E7 use one process per map or chunk)

Writes research/information-schwarzschild-radius/results/<experiment>.json

E1  rates: c, g, memory, sigma, Mach, theta and the extremal paths per map
E2  word horizons by kick count, exact DP over all first-contraction words
E3  Kesten tail of the random recursion, by solving its functional equation
E4  exhaustive integers: survival of lift, cut-off, reach, lifetimes, per map
E5  exact Page curves
E6  3-adic memory: erased bits against g
E7  coefficient stopping test on all n < 2^N and the certificate it implies
E8  phase sweep over (d, q) and the two-branch Mach curve
E9  cycles and captured integers across 3x + a, 5x + a and the family
E10 most compact integers of the classic map
E11 the capture law: captured integers of 3x + a against the mass a
"""

import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from collatz.schwarzschild import (  # noqa: E402
    COLLATZ, CollatzLike, capture_cross_section, certified_kicks, cheapest_climb,
    contraction_sums, contraction_word, contraction_words, cramer_exponent, drift,
    erased_bits, head_speed,
    horizon, largest_horizon, lift_tail, longest_fall, longest_hover, mach_number, memory_rate,
    page_curve, phase, place_exponents, reach_exponent, stagnation_radius, step_sigma,
    tail_constant, trapping_radius, weak_field_exponent,
)

from collatz.schwarzschild.rates import bisect_root  # noqa: E402

RESULTS = ROOT / "research" / "information-schwarzschild-radius" / "results"

# Name, multipliers per residue, exhaustive bit depth for E4.
FAMILY = [
    ("3x+1", (1, 3), 26),
    ("(1,4,4)/3", (1, 4, 4), 24),
    ("(1,1,7)/3", (1, 1, 7), 24),
    ("(1,3,5,7)/4", (1, 3, 5, 7), 24),
    ("(1,5,5,5)/4", (1, 5, 5, 5), 24),
    ("(1,6,6,6,6)/5", (1, 6, 6, 6, 6), 24),
    ("(1,2,4)/3", (1, 2, 4), 24),
    ("(1,2,5)/3", (1, 2, 5), 24),
    ("(1,4,4,6,6)/5", (1, 4, 4, 6, 6), 24),
    ("(1,2,7)/3", (1, 2, 7), 23),
    ("(1,4,5)/3", (1, 4, 5), 22),
    ("(1,5,5)/3", (1, 5, 5), 17),
]


def system_of(q):
    return CollatzLike.from_multipliers(q)


def save(name, payload):
    RESULTS.mkdir(parents=True, exist_ok=True)
    path = RESULTS / f"{name}.json"
    path.write_text(json.dumps(payload, indent=1, default=float, allow_nan=False) + "\n",
                    encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)}")


# ---- E1 ----

def finite(value):
    """JSON has no infinity, so an infinite rate is stored as null."""
    return None if math.isinf(value) else value


def describe(name, system):
    climb = cheapest_climb(system)
    hover = longest_hover(system)
    fall = longest_fall(system)
    theta = cramer_exponent(system)
    return {
        "map": name, "d": system.d, "q": system.q, "a": system.a, "phase": phase(system),
        "c": head_speed(system), "g": drift(system), "memory": memory_rate(system),
        "sigma": step_sigma(system), "mach": finite(mach_number(system)),
        "theta": finite(theta),
        "weak_field": finite(weak_field_exponent(system)),
        "reach": finite(reach_exponent(system)),
        "climb_speed": climb and climb.speed, "climb_cost": climb and climb.cost,
        "steps_per_bit_typical": 1 / drift(system) if drift(system) > 0 else None,
        "steps_per_bit_hover": 1 / hover.cost if hover else None,
        "steps_per_bit_fall": 1 / fall.cost if fall and fall.cost > 0 else None,
        "stagnation_radius": stagnation_radius(system),
        "trapping_radius": trapping_radius(system),
        "tail_constant": tail_constant(system),
        "places": {str(k): v for k, v in place_exponents(system).items()},
    }


def e1():
    rows = [describe(name, system_of(q)) for name, q, _ in FAMILY]
    rows += [describe("5x+1", CollatzLike.qx_plus_a(5, 1)),
             describe("7x+1", CollatzLike.qx_plus_a(7, 1)),
             describe("(n+1)/2", system_of((1, 1))),
             describe("(1,2,2)/3", system_of((1, 2, 2)))]
    for row in rows:
        theta = row["theta"]
        print(f"  {row['map']:16s} {row['phase']:9s} g={row['g']:+.4f} sigma={row['sigma']:.4f} "
              f"theta={'inf' if theta is None else format(theta, '.4f')} weak={row['weak_field']}")
    classic = longest_fall(COLLATZ)
    print("  Lagarias-Weiss constant from saturation:", 1 / (classic.cost * math.log(2)))
    save("e1_rates", rows)


# ---- E2 ----

def e2(s_max=1500):
    table = []
    for s in range(0, 15):
        words = contraction_words(s)
        radii = [horizon(w) for w in words]
        k = len(words[0])
        table.append({
            "s": s, "k": k, "stopping_class": k + s, "subgroups": len(words),
            "beta": (3 ** s and (k - s * math.log2(3))),
            "F_min": float(min(radii)), "F_mean": float(sum(radii) / len(radii)),
            "F_max": float(max(radii)), "bound": float(largest_horizon(s)),
        })
    finished = contraction_sums(s_max)
    rows = []
    running = Fraction(0)
    for s in sorted(finished):
        k, count, total = finished[s]
        if s == 0:
            continue
        expected = Fraction(total, (2 ** k - 3 ** s) * 2 ** k)
        running += expected
        rows.append({"s": s, "k": k, "log2_subgroups": math.log2(count),
                     "measure": float(Fraction(count, 2 ** k)),
                     "mean_horizon": float(Fraction(total, count * (2 ** k - 3 ** s))),
                     "expected_captures": float(expected),
                     "running_total": float(running)})
    tail = {str(cut): float(sum(r["expected_captures"] for r in rows if r["s"] >= cut))
            for cut in (2, 5, 10, 20, 50, 100, 200, 500)}
    for row in table[:10]:
        print("  s", row["s"], "beta", round(row["beta"], 4), "F", round(row["F_min"], 2),
              round(row["F_mean"], 2), round(row["F_max"], 2), "bound", round(row["bound"], 2))
    print("  expected captures with s >= cut:", {k: round(v, 5) for k, v in tail.items()})
    save("e2_word_horizons", {"by_kicks": table, "dp": rows[:60] + rows[60::25], "tail": tail})


# ---- E3 ----

def stationary_tail(system, iterations=4000, points=24001, low=1e-8, high=1e24):
    """S(t) = P(x > t) for the stationary law of x -> (q_r x + a_r) / d, uniform r.

    Iterates S(t) = (1 / d) sum S((d t - a_r) / q_r) on a log grid. S(u) = 1 for
    u < 0. Past the top of the grid the known slope -theta extrapolates.
    """
    theta = cramer_exponent(system)
    d = system.d
    grid = np.geomspace(low, high, points)
    log_grid = np.log(grid)
    log_s = np.full(points, -600.0)
    for _ in range(iterations):
        total = np.zeros(points)
        for q, a in zip(system.q, system.a):
            u = (d * grid - a) / q
            value = np.ones(points)
            positive = u > 0
            log_u = np.log(u[positive])
            interior = np.interp(log_u, log_grid, log_s)
            beyond = log_u > log_grid[-1]
            interior[beyond] = log_s[-1] - theta * (log_u[beyond] - log_grid[-1])
            value[positive] = np.exp(interior)
            total += value
        new = np.log(np.minimum(np.maximum(total / d, 1e-300), 1.0))
        change = float(np.abs(new - log_s).max())
        log_s = new
        if change < 1e-12:
            break
    return grid, log_s


def e3():
    rows = []
    for name, q, iterations in (("3x+1", (1, 3), 6000), ("(1,4,4)/3", (1, 4, 4), 4000),
                                ("(1,1,7)/3", (1, 1, 7), 4000), ("(1,3,5,7)/4", (1, 3, 5, 7), 4000),
                                ("(1,2,4)/3", (1, 2, 4), 2000), ("(1,2,5)/3", (1, 2, 5), 3000),
                                ("(1,2,7)/3", (1, 2, 7), 8000), ("(1,4,5)/3", (1, 4, 5), 12000)):
        system = system_of(q)
        grid, log_s = stationary_tail(system, iterations)
        theta = cramer_exponent(system)
        samples = {}
        for exponent in (2, 4, 6, 8, 10, 12):
            t = 10.0 ** exponent
            at = float(np.interp(math.log(t), np.log(grid), log_s))
            near = float(np.interp(math.log(t) + 0.5, np.log(grid), log_s))
            samples[exponent] = {"t_theta_S": math.exp(at + theta * math.log(t)),
                                 "local_slope": (near - at) / 0.5}
        rows.append({"map": name, "theta": theta, "goldie": tail_constant(system), "samples": samples})
        last = samples[12]
        print(f"  {name:14s} theta={theta:.4f} slope@1e12={last['local_slope']:.4f} "
              f"t^theta S={last['t_theta_S']:.4f} goldie={tail_constant(system)}")
    save("e3_kesten_tail", rows)


# ---- E4 ----

def scan(q, bits, step_cap=3000, hard_cap=2_000_000):
    """Every n in [1, 2^bits): log2 of the orbit peak, total steps, first-drop steps.

    Blocks [2^b, 2^(b+1)) run vectorised until each orbit falls below the block,
    where the table already knows the answer. Orbits that near 64 bits, or outlast
    step_cap, finish in exact Python integers. Lifetimes count steps to the first
    repeated value, so cycle elements have lifetime 0.
    """
    system = system_of(q)
    d = system.d
    Q = np.array(system.q, dtype=np.int64)
    A = np.array(system.a, dtype=np.int64)
    limit = (1 << 62) // max(system.q)
    size = 1 << bits
    log_peak = np.zeros(size)
    life = np.zeros(size, dtype=np.int64)
    first = np.full(size, -1, dtype=np.int64)
    cycles = set()
    unresolved = []

    for b in range(bits):
        lo, hi = 1 << b, 1 << (b + 1)
        n = np.arange(lo, hi, dtype=np.int64)
        peak = n.astype(np.float64)
        drop = np.full(hi - lo, -1, dtype=np.int64)
        end_value = np.zeros(hi - lo, dtype=np.int64)
        end_step = np.zeros(hi - lo, dtype=np.int64)
        index = np.arange(hi - lo)
        x = n.copy()
        slow = []
        for t in range(1, step_cap + 1):
            r = x % d
            x = (Q[r] * x + A[r]) // d
            peak[index] = np.maximum(peak[index], x.astype(np.float64))
            newly = (x < n[index]) & (drop[index] < 0)
            drop[index[newly]] = t
            done = x < lo
            end_value[index[done]] = x[done]
            end_step[index[done]] = t
            big = ~done & (x >= limit)
            if big.any():
                slow.extend(zip(index[big].tolist(), x[big].tolist(), [t] * int(big.sum())))
            keep = ~done & ~big
            index, x = index[keep], x[keep]
            if index.size == 0:
                break
        if index.size:
            slow.extend((i, lo + i, 0) for i in index.tolist())   # restart, counting from n
        final = end_value > 0
        log_peak[lo:hi] = np.log2(peak)
        log_peak[lo:hi][final] = np.maximum(log_peak[lo:hi][final], log_peak[end_value[final]])
        below = life[end_value[final]]
        life[lo:hi][final] = np.where(below < 0, -1, end_step[final] + below)   # unknown stays unknown
        first[lo:hi] = drop

        for i, value, t in slow:
            start = lo + i
            value = int(value)
            top = float(log_peak[start])
            mark = int(drop[i])
            seen = {}
            while True:
                if value < lo:
                    life[start] = t + life[value] if life[value] >= 0 else -1
                    top = max(top, float(log_peak[value]))
                    break
                if value in seen:
                    orbit = [v for v, at in seen.items() if at >= seen[value]]
                    cycles.add(min(orbit))
                    life[start] = seen[value]
                    break
                if t >= hard_cap:
                    unresolved.append(start)
                    life[start] = -1
                    break
                seen[value] = t
                value = system.step(value)
                t += 1
                top = max(top, math.log2(value))
                if mark < 0 and value < start:
                    mark = t
            log_peak[start] = top
            first[start] = mark
    return log_peak, life, first, sorted(cycles), unresolved


def survival(lift):
    """Thresholds and exact counts for a block's lifts."""
    top = float(lift.max())
    thresholds = np.linspace(0.25, max(top, 0.5), 40)
    return [(float(h), int((lift >= h).sum())) for h in thresholds]


def fit_slope(rows, total, minimum=30, skip=1.0):
    """Weighted least squares slope of -log2 survival against lift, in bits per bit."""
    usable = [(h, c) for h, c in rows if c >= minimum and h >= skip]
    if len(usable) < 4:
        return None
    h = np.array([u[0] for u in usable])
    y = -np.log2(np.array([u[1] for u in usable]) / total)
    w = np.sqrt(np.array([u[1] for u in usable], dtype=float))
    return float(np.polyfit(h, y, 1, w=w)[0])


def e4_one(entry):
    name, q, bits = entry
    start = time.time()
    system = system_of(q)
    log_peak, life, first, cycles, unresolved = scan(q, bits)
    theta = cramer_exponent(system)
    climb = cheapest_climb(system)
    depth_bits = math.log2(system.d)
    blocks = []
    for b in range(8, bits):
        lo, hi = 1 << b, 1 << (b + 1)
        n = np.arange(lo, hi, dtype=np.float64)
        bit_size = np.log2(n)
        lift = log_peak[lo:hi] - bit_size
        rows = survival(lift)
        good = life[lo:hi] >= 0
        stopped = first[lo:hi] > 0
        blocks.append({
            "bits": b + 1, "max_lift": float(lift.max()), "argmax": int(lo + lift.argmax()),
            "max_reach": float((log_peak[lo:hi] / bit_size).max()),
            "mean_lift": float(lift.mean()),
            "slope": fit_slope(rows, hi - lo),
            "mean_life_per_bit": float((life[lo:hi][good] / bit_size[good]).mean()),
            "max_life_per_bit": float((life[lo:hi][good] / bit_size[good]).max()),
            "max_stop_per_bit": float((first[lo:hi][stopped] / bit_size[stopped]).max()),
            "survival": rows,
        })
    top = blocks[-1]
    constant = lift_tail(12 / max(theta, 0.25), system, samples=100_000) * 2 ** (theta * 12 / max(theta, 0.25))
    predicted = [{"lift": h, "count": c,
                  "ratio": c / ((1 << (bits - 1)) * lift_tail(h, system, samples=40_000))}
                 for h, c in top["survival"] if c >= 30 and h >= 1]
    window = (climb.speed * (bits / depth_bits)) if climb else None
    result = {
        "map": name, "bits": bits, "theta": theta, "reach_predicted": reach_exponent(system),
        "lundberg_constant": constant, "exact_window_lift": window,
        "cutoff_predicted": (bits - 1 + math.log2(constant)) / theta,   # 2^(B-1) numbers in the block
        "steps_per_bit_typical": 1 / drift(system),
        "steps_per_bit_hover": 1 / longest_hover(system).cost,
        "steps_per_bit_fall": 1 / longest_fall(system).cost,
        "cycle_minima": cycles, "unresolved": len(unresolved), "blocks": blocks,
        "ratio_to_haar": predicted, "seconds": time.time() - start,
    }
    return result


def e4():
    with ProcessPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(e4_one, FAMILY))
    for r in results:
        last = r["blocks"][-1]
        ratios = [x["ratio"] for x in r["ratio_to_haar"]]
        print(f"  {r['map']:14s} B={r['bits']:2d} theta={r['theta']:.4f} slope={last['slope']} "
              f"maxlift={last['max_lift']:.2f} cutoff~{r['cutoff_predicted']:.2f} "
              f"reach={last['max_reach']:.3f}/{r['reach_predicted']:.3f} "
              f"ratio {min(ratios):.2f}..{max(ratios):.2f} "
              f"life {last['mean_life_per_bit']:.2f}/{r['steps_per_bit_typical']:.2f} "
              f"maxlife {last['max_life_per_bit']:.1f}/{r['steps_per_bit_fall']:.1f} "
              f"maxstop {last['max_stop_per_bit']:.1f}/{r['steps_per_bit_hover']:.1f} "
              f"unresolved {r['unresolved']} t={r['seconds']:.0f}s")
    save("e4_family_scan", results)


# ---- E5 ----

def e5():
    curves = {}
    for digits in (12, 16, 20, 24):
        table = page_curve(digits, 7 * digits)
        peak = int(table.mutual_information.idxmax())
        early = table.value_entropy.iloc[digits]
        curves[str(digits)] = {
            "peak_step": peak, "peak_information": float(table.mutual_information.iloc[peak]),
            "peak_share": float(table.mutual_information.iloc[peak] / digits),
            "slope_before": float((early - digits) / digits),
            "slope_after": float((table.value_entropy.iloc[3 * digits] - early) / (2 * digits)),
            "t": table.t.tolist()[:: max(1, digits // 8)],
            "value_entropy": table.value_entropy.round(5).tolist()[:: max(1, digits // 8)],
            "mutual_information": table.mutual_information.round(5).tolist()[:: max(1, digits // 8)],
        }
        print(f"  B={digits} peak at t={peak}, I={curves[str(digits)]['peak_information']:.3f}, "
              f"slopes {curves[str(digits)]['slope_before']:.4f} {curves[str(digits)]['slope_after']:.4f}")
    system = system_of((1, 4, 4))
    table = page_curve(13, 90, system)
    curves["base3_13"] = {"peak_step": int(table.mutual_information.idxmax()),
                          "peak_information": float(table.mutual_information.max()),
                          "address_bits": 13 * math.log2(3)}
    print("  base 3:", curves["base3_13"])
    save("e5_page_curve", curves)


# ---- E6 ----

def e6(levels=13):
    rows = []
    for m in range(1, levels + 1):
        result = erased_bits(m)
        rows.append({"trits": m, "entropy": result["entropy"], "erased": result["erased"],
                     "identity_gap": result["identity_gap"],
                     "capacity_deficit": m * math.log2(3) - result["entropy"]})
        print(f"  m={m:2d} erased={result['erased']:.6f} deficit={rows[-1]['capacity_deficit']:.4f}")
    print("  g =", drift())
    save("e6_three_adic_memory", {"g": drift(), "levels": rows})


# ---- E7 ----

def e7_chunk(args):
    """All n = 3 mod 4 in [start, stop): is T^tau(n) < n at the first contraction?

    n = 1 mod 4 contracts at (3n + 1) / 4 < n and even n at n / 2, so they pass.
    Values stay below 2^64 for n < 2^30, the largest Terras peak there being under 2^62.
    """
    start, stop = args
    n = np.arange(start | 3, stop, 4, dtype=np.uint64)
    x = n.copy()
    kicks = np.zeros(n.size, dtype=np.int64)
    logged = math.log2(3)
    failures = []
    t = 0
    longest = 0
    while n.size:
        t += 1
        odd = (x & np.uint64(1)).astype(bool)
        half = x >> np.uint64(1)
        x = half + odd * (x + np.uint64(1))     # (3x + 1) / 2 = x + (x + 1) / 2 for odd x
        kicks += odd
        contracted = kicks * logged < t
        if contracted.any():
            bad = x[contracted] >= n[contracted]
            if bad.any():
                failures.extend(n[contracted][bad].tolist())
            longest = max(longest, int(kicks[contracted].max()))
            keep = ~contracted
            n, x, kicks = n[keep], x[keep], kicks[keep]
    return failures, longest


def e7(bits=30):
    start = time.time()
    size = 1 << 22
    chunks = [(lo, lo + size) for lo in range(0, 1 << bits, size)]
    with ProcessPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(e7_chunk, chunks))
    failures = sorted(n for bad, _ in results for n in bad)
    longest = max(most for _, most in results)
    verified = (1 << bits) - 1
    certificate = certified_kicks(verified, s_limit=400_000)
    next_bound = largest_horizon(certificate + 1)
    print(f"  n < 2^{bits}: failures {failures[:10]}, most kicks {longest}, "
          f"certified s <= {certificate}, next bound {float(next_bound):.4g}, "
          f"{time.time() - start:.0f}s")
    save("e7_coefficient_stopping", {
        "bits": bits, "failures": failures, "most_kicks": longest,
        "certified_kicks": certificate, "next_horizon_bound": float(next_bound)})


# ---- E8 ----

def two_branch_theta(q):
    """theta for a real multiplier q in (2, 4) of the two-branch walk."""
    if q >= 4 or q <= 2:
        return None
    excess = lambda t: ((q / 2) ** t + 0.5 ** t) / 2 - 1
    high = 1.0
    while excess(high) < 0:
        high *= 2
    low = high / 2
    while excess(low) > 0:
        low /= 2
    return bisect_root(excess, low, high)


def e8():
    sweep = []
    for d in range(2, 9):
        for q in range(1, 3 * d + 2):
            if math.gcd(q, d) != 1:
                continue
            system = CollatzLike.from_multipliers((1, *([q] * (d - 1))))
            theta = cramer_exponent(system)
            sweep.append({"d": d, "q": q, "phase": phase(system), "g": drift(system),
                          "mach": finite(mach_number(system)), "theta": finite(theta)})
    curve = []
    for q in np.linspace(2.05, 3.99, 98):
        sigma = math.log2(q) / 2
        g = 1 - sigma
        theta = two_branch_theta(float(q))
        curve.append({"q": float(q), "mach": g / sigma, "theta": theta,
                      "weak": 2 * g / (sigma ** 2 * math.log(2))})
    boundary = {}
    for row in sweep:
        boundary.setdefault(row["d"], {})[row["q"]] = row["phase"]
    for d, phases in boundary.items():
        print(" ", d, {q: p[:3] for q, p in phases.items()})
    save("e8_phase_sweep", {"sweep": sweep, "curve": curve})


# ---- E9 ----

def cycles_of(system, limit, max_steps=20_000):
    found = {}
    for n in range(1, limit):
        cycle = system.cycle_through(n, max_steps)
        if cycle is not None:
            found[cycle[0]] = cycle
    return found


def e9():
    systems = [(f"3x{a:+d}", CollatzLike.qx_plus_a(3, a)) for a in (1, -1, 5, -5, 7, -7, 11, 13)]
    systems += [("5x+1", CollatzLike.qx_plus_a(5, 1)), ("5x-1", CollatzLike.qx_plus_a(5, -1)),
                ("7x+1", CollatzLike.qx_plus_a(7, 1))]
    systems += [(name, system_of(q)) for name, q, _ in FAMILY[1:9]]
    rows = []
    for name, system in systems:
        limit = 1 << 11
        cycles = cycles_of(system, limit, max_steps=3000)
        details = []
        for start, cycle in sorted(cycles.items()):
            word = system.word(start, len(cycle))
            Q, _, k = system.word_map(word)
            details.append({"min": start, "length": len(cycle), "horizon": str(horizon(word, system)),
                            "on_horizon": horizon(word, system) == start,
                            "contracting": Q < system.d ** k,
                            "beta": k * math.log2(system.d) - math.log2(Q)})
        scan_limit = 1 << 14
        positive_offsets = min(system.a) >= 0
        inside = []
        if positive_offsets:
            inside = [n for n in range(1, scan_limit) if captured_safely(n, system)]
        periodic = {x for c in cycles.values() for x in c}
        rows.append({"map": name, "cycles": details, "captured": inside[:60],
                     "captured_count": len(inside),
                     "captured_not_periodic": [n for n in inside if n not in periodic][:30]})
        print(f"  {name:14s} cycles {[c['min'] for c in details][:8]} all on horizon "
              f"{all(c['on_horizon'] for c in details)} contracting {sum(c['contracting'] for c in details)}/"
              f"{len(details)} captured {len(inside)} {inside[:8]}")
    save("e9_cycles_and_captures", rows)


def captured_safely(n, system):
    word = contraction_word(n, system, max_steps=2000)
    return word is not None and horizon(word, system) >= n


# ---- E10 ----

def e10(bits=22):
    top = []
    block_max = {}
    for n in range(2, 1 << bits):
        word = contraction_word(n)
        radius = horizon(word)
        c = radius / n
        size = n.bit_length()
        if c > block_max.get(size, (Fraction(-1), 0))[0]:
            block_max[size] = (c, n)
        if len(top) < 25 or c > top[-1][0]:
            top.append((c, n, len(word), sum(word), radius))
            top.sort(key=lambda row: -row[0])
            del top[25:]
    rows = [{"n": n, "compactness": float(c), "k": k, "s": s, "horizon": float(radius)}
            for c, n, k, s, radius in top]
    blocks = {str(b): {"compactness": float(v[0]), "n": v[1], "horizon": float(v[0] * v[1])}
              for b, v in sorted(block_max.items())}
    print("  top:", [(r["n"], round(r["compactness"], 4)) for r in rows[:8]])
    print("  by bits:", {b: (v["n"], round(v["compactness"], 5)) for b, v in list(blocks.items())[-6:]})
    save("e10_compactness", {"top": rows, "by_bits": blocks})


# ---- E11 ----

def e11_one(args):
    """Captured integers of 3x + a: the first contraction word has T^k(n) >= n."""
    a, reach = args
    n = np.arange(1, a * reach + 2, 2, dtype=np.int64)     # even n contract at n / 2
    x = n.copy()
    kicks = np.zeros(n.size, dtype=np.int64)
    logged = math.log2(3)
    caught = []
    t = 0
    while n.size:
        t += 1
        odd = (x & 1).astype(bool)
        x = np.where(odd, (3 * x + a) >> 1, x >> 1)
        kicks += odd
        contracted = kicks * logged < t
        if contracted.any():
            caught.extend(n[contracted & (x >= n)].tolist())
            keep = ~contracted
            n, x, kicks = n[keep], x[keep], kicks[keep]
    system = CollatzLike.qx_plus_a(3, a)
    genuine = periodic = minima = 0
    for start in caught:
        value, seen, dropped = start, set(), False
        while True:
            value = system.step(value)
            dropped = dropped or value < start
            if value == start:      # on a cycle, whether or not it is the cycle's minimum
                periodic += 1
                break
            if value in seen:       # entered a cycle that does not contain start
                if dropped:
                    genuine += 1
                else:
                    minima += 1
                break
            seen.add(value)
    return {"a": a, "captured": len(caught), "genuine": genuine, "periodic": periodic,
            "orbit_minima": minima, "largest": max(caught)}


def exact_mean_horizon(q, steps):
    """E[F(w)] at the first contraction, by exact sums over words sharing (Q, length).

    C is additive over words with the same Q and length, so each cell keeps a word
    count and a sum of C. Returns the sum so far and the measure still uncontracted.
    """
    system = system_of(q)
    d = system.d
    alive = {1: (1, 0)}
    total = 0.0
    power = 1
    for _ in range(steps):
        grown = {}
        next_power = power * d
        for Q, (count, c_sum) in alive.items():
            for q_r, a_r in zip(system.q, system.a):
                new_q = Q * q_r
                new_sum = q_r * c_sum + a_r * power * count
                if new_q < next_power:
                    total += float(Fraction(new_sum, (next_power - new_q) * next_power))
                else:
                    held = grown.get(new_q, (0, 0))
                    grown[new_q] = (held[0] + count, held[1] + new_sum)
        alive = grown
        power = next_power
    return total, float(Fraction(sum(c for c, _ in alive.values()), power))


def sampled_mean_horizon(args):
    """Monte Carlo over first contraction words.

    Returns E[F], E[min(F, cap)] and 2 E[number of odd n in [3, F]]. For the classic
    map the last is the expected number of integers n >= 3 captured, since a word's
    class is one odd residue, uniform among the odd residues mod 2^k.
    """
    q, samples, seed, cap = args
    system = system_of(q)
    rng = np.random.default_rng(seed)
    d = system.d
    total, truncated, integers, count = 0.0, 0.0, 0, 0
    for _ in range(samples):
        Q, C, power = 1, 0, 1
        for digit in rng.integers(0, d, 3000):
            r = int(digit)
            Q, C = system.q[r] * Q, system.q[r] * C + system.a[r] * power
            power *= d
            if Q < power:
                exact = Fraction(C, power - Q)
                radius = float(exact)
                total += radius
                truncated += min(radius, cap)
                integers += 2 * max(0, (int(exact) - 1) // 2)
                count += 1
                break
    return total / count, truncated / count, integers / count


def scaled_captures(args):
    """Count captured n for the map with multipliers q scaled by mass m."""
    q, m = args
    scaled = system_of(q).scaled(m)
    count = 0
    for n in range(1, max(4000, 1500 * m)):
        word = contraction_word(n, scaled, max_steps=1500)
        count += word is not None and horizon(word, scaled) >= n
    return {"m": m, "captured": count, "ratio": count / m}


def e11():
    cross_section = capture_cross_section()
    print(f"  Sigma = {cross_section:.10f}")
    values = list(range(1, 1402, 2))
    # 1500 clears the largest horizon among classic words of real weight (s = 41).
    with ProcessPoolExecutor(max_workers=10) as pool:
        rows = list(pool.map(e11_one, [(a, 1500) for a in values]))
        for row in rows:
            row["ratio"] = row["captured"] / row["a"]
        bands = []
        for low, high in ((1, 25), (25, 75), (75, 200), (200, 500), (500, 1000), (1000, 1402)):
            band = [r for r in rows if low <= r["a"] < high]
            ratios = np.array([r["ratio"] for r in band])

            def mean_share(key):
                return float(np.mean([r[key] / r["a"] for r in band]))

            bands.append({"from": low, "to": high, "maps": len(band),
                          "mean_ratio": float(ratios.mean()), "std_ratio": float(ratios.std()),
                          "genuine": mean_share("genuine"), "periodic": mean_share("periodic"),
                          "orbit_minima": mean_share("orbit_minima")})
            print(f"  a in [{low},{high}): captured / a = {ratios.mean():.4f} +- {ratios.std():.4f}, "
                  f"genuine {bands[-1]['genuine']:.4f} periodic {bands[-1]['periodic']:.4f} "
                  f"minima {bands[-1]['orbit_minima']:.4f}")
        clean = [r["a"] for r in rows if r["genuine"] == 0]
        print("  odd a with no genuine failure:", clean[:30], "fewest above that:",
              min(r["genuine"] for r in rows if r["a"] > 1))
        first = np.array(list(pool.map(sampled_mean_horizon,
                                       [((1, 3), 400_000, seed, 1500.0) for seed in range(10)])))
        moment = float(first[:, 2].mean())
        moment_error = float(first[:, 2].std(ddof=1) / math.sqrt(len(first)))
        print(f"  integers n >= 3 expected captured at a = 1: {moment:.4f} +- {moment_error:.4f}, "
              f"Poisson chance of none {math.exp(-moment):.3f}")
        family = []
        for name, q, masses, steps in (
                ("(1,4,4)/3", (1, 4, 4), (101, 202, 401, 802, 1201), 1200),
                ("(1,2,5)/3", (1, 2, 5), (101, 202, 401, 802, 1201), 260),
                ("(1,3,5,7)/4", (1, 3, 5, 7), (101, 201, 401, 801, 1201), 240)):
            exact, leftover = exact_mean_horizon(q, steps)
            # The scan stops at n = 1500 m, so it can only see horizons up to 1500 m.
            means = np.array(list(pool.map(sampled_mean_horizon,
                                           [(q, 1_000_000, seed, 1500.0) for seed in range(10)])))
            truncated = float(means[:, 1].mean())
            truncated_error = float(means[:, 1].std(ddof=1) / math.sqrt(len(means)))
            counts = list(pool.map(scaled_captures, [(q, m) for m in masses]))
            family.append({"map": name, "cross_section": exact, "uncontracted_measure": leftover,
                           "truncated": truncated, "truncated_error": truncated_error,
                           "by_mass": counts})
            print(f"  {name}: Sigma = {exact:.4f} (left {leftover:.1e}), truncated "
                  f"{truncated:.4f} +- {truncated_error:.4f}, captured / m = "
                  f"{[round(c['ratio'], 3) for c in counts]}")
    save("e11_capture_law", {"cross_section": cross_section, "bands": bands, "clean": clean[:60],
                             "integer_first_moment": moment, "integer_first_moment_error": moment_error,
                             "family": family, "maps": rows})


EXPERIMENTS = {"E1": e1, "E2": e2, "E3": e3, "E4": e4, "E5": e5, "E6": e6, "E7": e7,
               "E8": e8, "E9": e9, "E10": e10, "E11": e11}


def main():
    chosen = [a.upper() for a in sys.argv[1:]] or list(EXPERIMENTS)
    for name in chosen:
        print(name)
        start = time.time()
        EXPERIMENTS[name]()
        print(f"  {name} took {time.time() - start:.1f}s")


if __name__ == "__main__":
    main()
