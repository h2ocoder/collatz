"""Audit checks for site/connections/universal-dynamics.md and ZooExplorer.vue.

1. epsilon range in  s*log2(6) = T - log2(x0) + eps  for 3x+1 (page: eps in [-0.33, 0]).
2. Sign of the general conservation identity (page writes T - log_y(x_final/x_initial)).
3. 'Behavior in tests' table: share of starts that do not reach 1 / do not cycle, for 5x+1, 7x+1, 9x+1.
4. 'Role of c' table: share reaching 1 and number of DISTINCT cycles, vs the repo's own
   counter (collatz.zoo counts distinct first-repeated values, i.e. cycle entry points).
5. ZooExplorer survey replicated (starts 3..499 odd, cap 1e15, 2000 steps).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from collatz.zoo import CollatzSystem  # noqa: E402


def eps_3x1(x0):
    x, s, T = x0, 0, 0
    while x != 1:
        if x & 1:
            x = 3 * x + 1
            s += 1
        else:
            x >>= 1
        T += 1
    return s * math.log2(6) - T + math.log2(x0)


def check_eps():
    lo = (0.0, 1)
    for bound in (10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6):
        m = min(((eps_3x1(x), x) for x in range(1, bound)), key=lambda t: t[0])
        mx = max(((eps_3x1(x), x) for x in range(1, bound)), key=lambda t: t[0])
        print(f"   x0 < {bound}: min eps = {m[0]:.5f} at x0 = {m[1]};  max eps = {mx[0]:.2e} at x0 = {mx[1]}")
    for x in (3, 7, 9, 27, 31):
        print(f"   eps({x}) = {eps_3x1(x):.5f}")


def check_general_identity():
    # x -> x/y if y | x else n x + c ; run a few steps and compare both sign conventions
    for (n, y, c, x0, steps) in ((3, 2, 1, 27, 111), (5, 2, 1, 7, 40), (3, 2, 5, 11, 30), (4, 3, 1, 7, 25)):
        x, s, T = x0, 0, 0
        for _ in range(steps):
            if x % y == 0:
                x //= y
            else:
                x = n * x + c
                s += 1
            T += 1
        logy = lambda v: math.log(v) / math.log(y)
        lhs = s * logy(n * y)
        minus = T - logy(x / x0)   # the page's form, eps would be lhs - minus
        plus = T + logy(x / x0)
        print(f"   ({n}x+{c}, x/{y}) x0={x0}, {T} steps, x_final={x}: s*log_y(ny)={lhs:.4f}; "
              f"T - log_y(xf/x0)={minus:.4f} (eps={lhs - minus:+.4f});  T + log_y(xf/x0)={plus:.4f} (eps={lhs - plus:+.4f})")


def classify(n, y, c, x0, cap=None, max_steps=10_000):
    """Return ('one', None) if hits 1, ('cycle', frozenset(cycle)) or ('escape', None)."""
    x = x0
    seen = {x: 0}
    seq = [x]
    for _ in range(max_steps):
        x = x // y if x % y == 0 else n * x + c
        if x == 1:
            return 'one', None
        if cap is not None and x > cap:
            return 'escape', None
        if x in seen:
            cyc = seq[seen[x]:]
            return 'cycle', frozenset(cyc)
        seen[x] = len(seq)
        seq.append(x)
    return 'escape', None


def survey(n, y, c, starts, cap=None, max_steps=10_000):
    res = {'one': 0, 'cycle': 0, 'escape': 0}
    cycles = set()
    tot = 0
    for x0 in starts:
        if x0 % y == 0:
            continue
        tot += 1
        st, cyc = classify(n, y, c, x0, cap, max_steps)
        res[st] += 1
        if cyc:
            cycles.add(cyc)
    return res, cycles, tot


if __name__ == "__main__":
    print("1. epsilon range (3x+1)")
    check_eps()
    print("2. general identity, sign check")
    check_general_identity()

    print("3. 'Behavior in tests' table (page: 5x+1 84% divergent, 7x+1 98%, 9x+1 97%)")
    for n in (3, 5, 7, 9):
        for label, starts in (("odd 3..499", range(3, 500, 2)), ("odd 3..999", range(3, 1000, 2))):
            res, cycles, tot = survey(n, 2, 1, starts, cap=10 ** 60, max_steps=20_000)
            print(f"   {n}x+1 {label}: reach 1 {res['one']}/{tot} ({res['one'] / tot:.1%}), "
                  f"other cycle {res['cycle']}/{tot} ({res['cycle'] / tot:.1%}), "
                  f"passed 1e60 {res['escape']}/{tot} ({res['escape'] / tot:.1%}); "
                  f"distinct other cycles (min elements): {sorted(min(c) for c in cycles)}")
        # the repo's own survey (timeout after max_steps = 'divergent')
        for mx, rng in ((5000, range(3, 500, 2)), (10000, range(3, 1000, 2))):
            sv = CollatzSystem(n=n, y=2, c=1, max_steps=mx).survey(rng)
            o = sv['outcomes']
            tot = sv['sample_size']
            print(f"      collatz.zoo survey max_steps={mx} {rng}: {o}  timeout share="
                  f"{o.get('timeout', 0) / tot:.1%}  'cycles_found'={sv['cycles_found']}")

    print("4. 'Role of c' table (page: c=1 100%/0 cycles; 3: 0%/2; 5: 13%/21; 7: 69%/6; 9: 0%/3; 11: 19%/20; 13: 51%/20)")
    for c in (1, 3, 5, 7, 9, 11, 13, 15, 17, 19):
        for label, starts in (("odd 3..499", range(3, 500, 2)), ("odd 3..999", range(3, 1000, 2))):
            res, cycles, tot = survey(3, 2, c, starts, cap=None, max_steps=100_000)
            sv = CollatzSystem(n=3, y=2, c=c, max_steps=5000).survey(starts)
            print(f"   3x+{c:<2d} {label}: reach 1 {res['one'] / tot:.1%}; escape {res['escape']}; "
                  f"DISTINCT cycles not through 1: {len(cycles)} (min elements {sorted(min(cy) for cy in cycles)}); "
                  f"repo 'cycles_found' = {sv['cycles_found']}; repo outcomes {sv['outcomes']}")

    print("5. ZooExplorer survey replicated (cap 1e15, 2000 steps, starts 3..499 odd)")
    for (n, y, c) in ((3, 2, 1), (5, 2, 1), (7, 2, 1), (9, 2, 1)):
        res, cycles, tot = survey(n, y, c, range(3, 500, 2), cap=10 ** 15, max_steps=2000)
        print(f"   {n}x+{c}, x/{y}: converge {res['one'] / tot:.0%}  cycle {res['cycle'] / tot:.0%}  "
              f"'diverge' {res['escape'] / tot:.0%}")
