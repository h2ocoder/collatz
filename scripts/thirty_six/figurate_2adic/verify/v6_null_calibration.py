"""Skeptic check 6: is the Pell orbit's total stopping time really 'typical'?  (Q2.3-f)

The researcher reported mean z about 0 but sd of z between 1.2 and 1.4, explained by 'only 10 controls'.
v3 with 30 controls still gave sd z = 1.36 for u_j, where a standard normal population would give about 1.05.
Here the same statistic is calibrated: the Pell term is replaced by a fresh random integer of the same bit
length and the same residue mod 16 (so the null hypothesis is true by construction), 10 replicates.  If the
calibrated sd is also well above 1.05 the excess is a property of the statistic, not of the Pell numbers.

Run: C:/repos/collatz/.venv/Scripts/python.exe -X utf8 v6_null_calibration.py     (about 3 minutes)
"""
import json
import os
import random
import statistics
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = open(os.path.join(HERE, "v6_null_calibration.log"), "w", encoding="utf-8")
RES = {}
T0 = time.time()


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


def tst(x):
    c = 0
    while x != 1:
        x = (3 * x + 1) >> 1 if x & 1 else x >> 1
        c += 1
    return c


JMIN, JMAX, NC = 5, 160, 30
u, m = [1, 3], [0, 1]
for j in range(2, JMAX + 1):
    u.append(6 * u[-1] - u[-2])
    m.append(6 * m[-1] - m[-2])
n = [(x - 1) // 2 for x in u]


def control(x, rng):
    bl = x.bit_length()
    y = rng.getrandbits(bl - 1) | (1 << (bl - 1))
    return (y >> 4 << 4) | (x & 15)


def zscores(targets, templates, rng):
    zs = []
    for t, tpl in zip(targets, templates):
        ctr = [tst(control(tpl, rng)) for _ in range(NC)]
        zs.append((tst(t) - statistics.mean(ctr)) / statistics.stdev(ctr))
    return zs


def summary(zs):
    return statistics.mean(zs), statistics.stdev(zs)


out("=" * 100)
out(f"z = (tst(x) - mean of {NC} controls) / sd of controls, terms j = {JMIN}..{JMAX}")
out("=" * 100)
rng = random.Random(1225)
RES["pell"] = {}
for name, seq in (("u_j", u), ("n_j", n)):
    tpl = [seq[j] for j in range(JMIN, JMAX + 1)]
    mz, sz = summary(zscores(tpl, tpl, rng))
    out(f"  Pell {name}:           mean z = {mz:+.3f}   sd z = {sz:.3f}")
    RES["pell"][name] = (mz, sz)
    # split by parity of j and by size
    for lab, sel in (("j even", [j for j in range(JMIN, JMAX + 1) if j % 2 == 0]),
                     ("j odd", [j for j in range(JMIN, JMAX + 1) if j % 2 == 1]),
                     ("j <= 40", list(range(JMIN, 41))), ("j > 40", list(range(41, JMAX + 1)))):
        t2 = [seq[j] for j in sel]
        mz2, sz2 = summary(zscores(t2, t2, rng))
        out(f"       {name} {lab:8s}: mean z = {mz2:+.3f}   sd z = {sz2:.3f}   ({len(sel)} terms)")
        RES["pell"][name + " " + lab] = (mz2, sz2)

out("")
out("  calibration (target replaced by a random integer matched in bit length and residue mod 16):")
RES["null"] = {}
for name, seq in (("u_j", u), ("n_j", n)):
    tpl = [seq[j] for j in range(JMIN, JMAX + 1)]
    ms, ss = [], []
    for rep in range(10):
        targets = [control(x, rng) for x in tpl]
        mz, sz = summary(zscores(targets, tpl, rng))
        ms.append(mz)
        ss.append(sz)
    out(f"  null with {name} sizes:  mean z over 10 replicates: {statistics.mean(ms):+.3f} (sd between replicates {statistics.stdev(ms):.3f});"
        f"   sd z: mean {statistics.mean(ss):.3f}, min {min(ss):.3f}, max {max(ss):.3f}")
    RES["null"][name] = dict(mean_z=ms, sd_z=ss)

out("")
out(f"done in {time.time() - T0:.1f} s")
with open(os.path.join(HERE, "v6_null_calibration.json"), "w", encoding="utf-8") as fh:
    json.dump(RES, fh, indent=1, default=str)
LOG.close()
