"""Nested dropping sets — the dropping map as a finite dictionary read two ways.

Every populated dropping set D_k factors into a handful of WORD-CLASSES.  A
word-class is the set of n sharing one parity word over the k dropping steps;
within a single populated D_k the odd-step count s is constant, so the whole
class shares one exact affine destination map

    dest(n) = (3^s * n + C) / 2^(k-s)            (C the integer +1 accumulation)

The class is pinned by the triple (k, s, C).  The collection of these triples
is the DICTIONARY, and the whole point of this script is that it is one finite
table read in two opposite directions:

  FORWARD  (2-adic key).  n mod 2^k picks the word; the word gives the
           destination.  dest is an affine image of the residue class
           r + 2^k Z, an arithmetic progression of step 3^s.

  BACKWARD (3-adic key).  A destination value d has a predecessor in word
           class (k,s,C) iff  2^(k-s) d ≡ C (mod 3^s); when it does, the
           predecessor is unique:  n = (2^(k-s) d - C) / 3^s.  So d mod 3^s
           decides which words can have produced d.

Same table, 2-adic key going forward, 3-adic key going backward — the
2-adic / 3-adic complementarity realized as the forward/backward asymmetry of
a single map.

NESTING.  Forward, each word-class maps its 2^k-residue onto a SINGLE residue
mod 3^s of the destination line.  As s climbs the reachable destinations are
pinned into an exponentially thinner 3-adic sliver: the fraction of residues
mod 3^s a depth-s drop can reach is (#words at level s)/3^s = 1/3, 1/9, 2/27,
3/81, 7/243, ...  The dropping sets nest 3-adically by destination reach.

OVERLAP.  A single destination is reachable from several levels at once (e.g.
d=10 <- 11,13,15,20 from D_8,D_3,D_11,D_1), one predecessor per compatible
word.  Backing up round by round through the dictionary builds the inverse
Collatz tree, factored into single dropping rounds.

Three views:
  1. The dictionary table, annotated with the 2-adic forward key (n mod 2^k)
     and the 3-adic backward key (d mod 3^s) for each word-class.
  2. 3-adic nesting — destinations reachable at each level s drawn as nested
     slivers on the unit interval (the 3-adic worm's-eye view), with the
     coverage (#words)/3^s collapsing toward zero.
  3. The backward predecessor tree of a small destination, built purely by
     dictionary lookup, showing nesting (rounds) and overlap (branching).

Outputs:
    data/collatz_nested_dropping.png
"""

from __future__ import annotations

from fractions import Fraction
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from collatz.dropping import dropping_destination, dropping_time
from collatz.residues import dropping_set_residues


# --------------------------------------------------------------------------
# Build the dictionary: distinct word-classes (k, s, C) up to k_max.
# --------------------------------------------------------------------------
def word_class(k: int, r: int) -> tuple[int, int, int]:
    """(s, C, word) for residue r mod 2^k, derived from a representative."""
    M = 1 << k
    n0 = r if r >= 2 else r + M
    mult, add = Fraction(1), Fraction(0)
    x, s, word = n0, 0, []
    for _ in range(k):
        if x % 2 == 1:
            word.append("O")
            x = 3 * x + 1
            mult, add = 3 * mult, 3 * add + 1
            s += 1
        else:
            word.append("E")
            x //= 2
            mult, add = mult / 2, add / 2
    C = int(add * (1 << (k - s)))
    return s, C, "".join(word)


def build_dictionary(k_max: int) -> list[dict]:
    """One entry per distinct (k, s, C); records the 2-adic and 3-adic keys."""
    entries = []
    for k in range(1, k_max + 1):
        R = sorted(dropping_set_residues(k))
        if not R:
            continue
        by_class = defaultdict(list)
        for r in R:
            s, C, word = word_class(k, r)
            by_class[(s, C, word)].append(r)
        for (s, C, word), residues in by_class.items():
            mod3 = 3 ** s
            dres = None if s == 0 else (C * pow(1 << (k - s), -1, mod3)) % mod3
            entries.append({
                "k": k, "s": s, "C": C, "word": word,
                "residues_2k": sorted(residues),   # 2-adic forward key (mod 2^k)
                "dres_3s": dres,                    # 3-adic backward key (mod 3^s)
            })
    return entries


def predecessors(d: int, dic: list[dict]) -> list[tuple[int, int]]:
    """All (n, k) that drop to value d in one round, via the backward rule.

    Filtered to genuine predecessors (the congruence can hit for a word the
    orbit does not actually follow at small d; we confirm against the map).
    """
    out = []
    for e in dic:
        k, s, C = e["k"], e["s"], e["C"]
        num = (1 << (k - s)) * d - C
        if num > 0 and num % (3 ** s) == 0:
            n = num // (3 ** s)
            if n > 1 and dropping_time(n) == k and dropping_destination(n) == d:
                out.append((n, k))
    return out


# --------------------------------------------------------------------------
# View 3: backward predecessor tree, built purely by dictionary lookup.
# --------------------------------------------------------------------------
def predecessor_tree(root: int, dic: list[dict], depth: int) -> list:
    """Layered list; each node = (value, k_used_to_reach_parent, parent_idx)."""
    layers = [[(root, None, None)]]
    for _ in range(depth):
        prev = layers[-1]
        nxt = []
        for pi, (val, _, _) in enumerate(prev):
            for (n, k) in sorted(predecessors(val, dic)):
                nxt.append((n, k, pi))
        if not nxt:
            break
        layers.append(nxt)
    return layers


def main() -> None:
    K_MAX = 13
    dic = build_dictionary(K_MAX)
    dic.sort(key=lambda e: (e["s"], e["k"], e["C"]))
    print(f"dictionary: {len(dic)} word-classes up to k={K_MAX}")
    for e in dic:
        print(f"  k={e['k']:2d} s={e['s']} C={e['C']:3d} word={e['word']:<13} "
              f"2-adic n mod {1<<e['k']:5d} in {e['residues_2k'][:4]}"
              f"{'...' if len(e['residues_2k'])>4 else '':<3}  "
              f"3-adic d mod {3**e['s']:3d} = {e['dres_3s']}")

    fig = plt.figure(figsize=(16, 5.4))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.0, 1.25], wspace=0.28)

    # ---- View 1: the dictionary table, two keys ---------------------------
    ax0 = fig.add_subplot(gs[0, 0])
    ax0.axis("off")
    ax0.set_title("1. The dropping dictionary\n"
                  r"forward key $n\,\mathrm{mod}\,2^k$  ·  "
                  r"backward key $d\,\mathrm{mod}\,3^s$",
                  fontsize=10)
    header = ["$k$", "$s$", "$C$", "word",
              r"$n\,\mathrm{mod}\,2^k$", r"$d\,\mathrm{mod}\,3^s$"]
    rows = []
    for e in dic:
        twoadic = ",".join(str(r) for r in e["residues_2k"][:2])
        if len(e["residues_2k"]) > 2:
            twoadic += ",…"
        three = "—" if e["dres_3s"] is None else f"{e['dres_3s']} (3^{e['s']})"
        rows.append([str(e["k"]), str(e["s"]), str(e["C"]), e["word"],
                     f"{twoadic} (2^{e['k']})", three])
    tab = ax0.table(cellText=rows, colLabels=header, loc="center",
                    cellLoc="center", colWidths=[.07, .07, .09, .30, .27, .20])
    tab.auto_set_font_size(False)
    tab.set_fontsize(7.0)
    tab.scale(1, 1.18)
    # tint by level s
    cmap = plt.colormaps["viridis"]
    for i, e in enumerate(dic):
        c = cmap(e["s"] / 5)
        for j in range(len(header)):
            cell = tab[i + 1, j]
            cell.set_facecolor((c[0], c[1], c[2], 0.14))
            cell.set_edgecolor("0.8")

    # ---- View 2: 3-adic nesting -------------------------------------------
    ax1 = fig.add_subplot(gs[0, 1])
    # for each level s, draw the reachable destinations as slivers on [0,1)
    # at 3-adic resolution 3^s.  A class reaching residue a mod 3^s occupies
    # the interval [a/3^s, (a+1)/3^s).
    levels = defaultdict(list)
    for e in dic:
        if e["s"] >= 1:
            levels[e["s"]].append(e["dres_3s"])
    smax = max(levels)
    for s in range(1, smax + 1):
        mod = 3 ** s
        y = smax + 1 - s
        ax1.add_patch(plt.Rectangle((0, y - 0.34), 1, 0.68,
                                    facecolor="0.93", edgecolor="0.8", lw=0.5))
        for a in levels.get(s, []):
            ax1.add_patch(plt.Rectangle((a / mod, y - 0.34), 1 / mod, 0.68,
                                        facecolor=cmap(s / 5), edgecolor="none"))
        frac = len(levels.get(s, [])) / mod
        ax1.text(1.02, y, rf"$s={s}$: {len(levels.get(s,[]))}/{mod}"
                 rf"$={frac:.3f}$", va="center", fontsize=8)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0.4, smax + 0.8)
    ax1.set_yticks([])
    ax1.set_xlabel(r"destination position on $\mathbb{Z}_3$  "
                   r"($d\,\mathrm{mod}\,3^s$)")
    ax1.set_title("2. 3-adic nesting of destination reach\n"
                  "each deeper drop pins $d$ into a thinner sliver",
                  fontsize=10)

    # ---- View 3: backward predecessor tree --------------------------------
    ax2 = fig.add_subplot(gs[0, 2])
    ROOT, DEPTH = 2, 5
    layers = predecessor_tree(ROOT, dic, DEPTH)
    # x positions: spread each layer evenly; connect to parent
    pos = []
    for li, layer in enumerate(layers):
        xs = np.linspace(0, 1, len(layer) + 2)[1:-1]
        pos.append(xs)
    for li in range(1, len(layers)):
        for ni, (val, k, pi) in enumerate(layers[li]):
            x0, y0 = pos[li - 1][pi], len(layers) - li
            x1, y1 = pos[li][ni], len(layers) - li - 1
            ax2.plot([x0, x1], [y0, y1], "-", color="0.7", lw=0.7, zorder=1)
            ax2.text((x0 + x1) / 2, (y0 + y1) / 2, f"{k}", fontsize=6,
                     color="darkred", ha="center", va="center", zorder=3,
                     bbox=dict(boxstyle="round,pad=0.05", fc="white",
                               ec="none", alpha=0.7))
    for li, layer in enumerate(layers):
        y = len(layers) - li - 1
        for ni, (val, k, pi) in enumerate(layer):
            ax2.scatter(pos[li][ni], y, s=170, zorder=2,
                        color="darkslateblue" if li == 0 else "steelblue",
                        edgecolor="white", lw=0.8)
            ax2.text(pos[li][ni], y, str(val), fontsize=6.5, color="white",
                     ha="center", va="center", zorder=4, fontweight="bold")
    ax2.set_xlim(-0.05, 1.05)
    ax2.set_ylim(-0.6, len(layers) - 0.4)
    ax2.axis("off")
    ax2.set_title(f"3. Backward tree from destination {ROOT}\n"
                  "edge label = dropping time $k$ of that round",
                  fontsize=10)

    fig.suptitle("Nested dropping sets: one dictionary, 2-adic forward / "
                 "3-adic backward", fontsize=12, y=1.02)
    fig.savefig("data/collatz_nested_dropping.png", dpi=150,
                bbox_inches="tight")
    plt.close(fig)
    print("wrote data/collatz_nested_dropping.png")

    # ---- console: the nesting fractions and a worked backward lookup ------
    print("\n3-adic destination reach by level s:")
    for s in range(1, smax + 1):
        mod = 3 ** s
        res = sorted(levels.get(s, []))
        print(f"  s={s}: d ≡ {res} (mod {mod})   coverage {len(res)}/{mod}"
              f" = {len(res)/mod:.4f}")
    print("\nworked backward lookup (predecessors by dictionary):")
    for d in (1, 2, 4, 5, 10, 16):
        print(f"  d={d:3d} <- {sorted(predecessors(d, dic))}")


if __name__ == "__main__":
    main()
