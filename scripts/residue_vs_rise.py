"""Is the residue r_v of a parity word correlated with how much the word rises?

For every T-word v of length K starting with 1, the integers following v form one residue
class r_v mod 2^K (Terras).  Compute height(v) = s*log2(3) - K (log2 of the ratio after K
steps) and the max excursion, and look at r_v / 2^K conditional on height.  Under the i.i.d.
model r_v/2^K would be independent of the word; any dependence is the size–residue coupling.
"""
import sys, math, numpy as np
K = int(sys.argv[1]) if len(sys.argv) > 1 else 20
M = 1 << K
a = math.log2(3) - 1
# residue r_v: n ≡ r mod 2^K follows word v.  Enumerate by n = odd residues mod 2^K and
# computing their word (bijection), which is cheaper than inverting words.
r = np.arange(1, M, 2, dtype=np.int64)
x = r + 3 * M   # large representative avoids small-n artefacts; word depends only on r mod 2^K
height = np.zeros(len(r)); maxexc = np.zeros(len(r)); ones = np.zeros(len(r), dtype=np.int64)
for j in range(K):
    odd = (x & 1) == 1
    x = np.where(odd, (3 * x + 1) // 2, x >> 1)
    height += np.where(odd, a, -1.0); ones += odd
    maxexc = np.maximum(maxexc, height)
rel = r / M
print(f"K={K}: {len(r)} words.  corr(height, r/2^K) = {np.corrcoef(height, rel)[0,1]:+.4f};  corr(max excursion, r/2^K) = {np.corrcoef(maxexc, rel)[0,1]:+.4f}")
print("| height bin (bits after K steps) | #words | mean r/2^K | P(r/2^K < 0.01) | P(r/2^K < 0.1) |"); print("|---|---|---|---|---|")
edges = [-20, -8, -4, -2, 0, 2, 4, 6, 8, 12]
for lo, hi in zip(edges[:-1], edges[1:]):
    m = (height >= lo) & (height < hi)
    if m.sum() == 0: continue
    print(f"| [{lo},{hi}) | {m.sum()} | {rel[m].mean():.4f} | {np.mean(rel[m]<0.01):.5f} | {np.mean(rel[m]<0.1):.4f} |")
# strongest rising words: those never dropping (ratio >= 1 at every step)
print(f"P(r/2^K < 0.01) overall = {np.mean(rel<0.01):.5f} (uniform: 0.01)")
