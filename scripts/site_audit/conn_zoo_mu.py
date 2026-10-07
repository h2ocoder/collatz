"""Audit check: ZooExplorer's criticality estimate over its slider ranges.

mu = n / y^avgDrains, avgDrains estimated as in ZooExplorer.vue (x = 1..499, y not dividing x).
Counts how many (n, y) pairs with c = 1 show mu < 1 ('Subcritical'), and shows that
(n, y, c) = (2, 3, 1) is 'Subcritical' while every start x = 2 mod 3 provably runs to infinity.
"""


def avg_drains(n, y, c):
    tot = cnt = 0
    for x in range(1, 500):
        if x % y == 0:
            continue
        v = n * x + c
        d = 0
        while v > 0 and v % y == 0:
            v //= y
            d += 1
        tot += d
        cnt += 1
    return tot / cnt


def run(n, y, c, x0, cap=10 ** 15, max_steps=2000):
    x = x0
    seen = {x}
    for _ in range(max_steps):
        x = x // y if x % y == 0 else n * x + c
        if x == 1:
            return 'reach 1'
        if x > cap:
            return 'pass cap'
        if x in seen:
            return 'cycle'
        seen.add(x)
    return 'pass cap'


if __name__ == "__main__":
    sub = []
    for y in range(2, 7):
        for n in range(2, 16):
            mu = n / y ** avg_drains(n, y, 1)
            if mu < 1:
                sub.append((n, y, round(mu, 3)))
    print("(n, y, mu) with c = 1 and mu < 1 in the widget's ranges:", sub)

    n, y, c = 2, 3, 1
    mu = n / y ** avg_drains(n, y, c)
    res = {}
    for x0 in range(3, 500, 2):
        if x0 % y == 0:
            continue
        r = run(n, y, c, x0)
        res[r] = res.get(r, 0) + 1
    print(f"(2x+1, x/3): mu = {mu:.3f}; survey of odd starts 3..499 not divisible by 3: {res}")
    print("   starts = 2 mod 3 among them that reach 1 or cycle:",
          sum(1 for x0 in range(5, 500, 6) if run(n, y, c, x0) != 'pass cap'),
          "(2x+1 = 2 mod 3 whenever x = 2 mod 3, so such a start is never divided again)")
