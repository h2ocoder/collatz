/**
 * Counting logic for the PentagonWalk component (page: explore/folded-pentagon).
 *
 * Pure functions, no DOM access, erasable type annotations only, so the same
 * file is imported by the component and by the Node check
 * scripts/thirty_six/site_figures/check_pentagon_walk.mjs.
 *
 * Source of the mathematics: scripts/thirty_six/golden_kernel/README.md, Theorem A
 * and its corollary. Plain numbers are exact here: for k <= 16 every value stays
 * below 5 * 2^16 * (3/2)^16 < 2^28.
 */

/** The constant c of the rule (3n + c)/2: +1 for 3x+1, -1 for 3x-1. */
export type Sign = 1 | -1

export const MAX_STEPS = 16

/**
 * Residues mod 5 in pentagon order, apex first.
 * 3x+1: apex 1, neighbours 2 and 3, far pair 4 and 0, joined as 1-2-4-0-3.
 * 3x-1: the same pentagon with every residue negated (apex 4, neighbours 3 and 2,
 * far pair 1 and 0).
 */
export function pentagonOrder(sign: Sign): number[] {
  const plus = [1, 2, 4, 0, 3]
  return sign === 1 ? plus : plus.map((r) => (5 - r) % 5)
}

/** Role of each position of pentagonOrder(). */
export const ROLES = ['apex', 'near', 'far', 'far', 'near']

/** Shortcut map: n/2 for even n, (3n + sign)/2 for odd n. */
export function shortcutStep(n: number, sign: Sign): number {
  return n % 2 === 0 ? n / 2 : (3 * n + sign) / 2
}

/**
 * Iterate the shortcut map k times on each of the 2^k positive integers
 * n = start (mod 5) in one period of length 5 * 2^k, and count the residues of
 * the results mod 5. Returns counts indexed by residue 0..4; they sum to 2^k.
 */
export function residueCounts(k: number, start: number, sign: Sign): number[] {
  const counts = [0, 0, 0, 0, 0]
  const total = 2 ** k
  const first = start === 0 ? 5 : start
  for (let j = 0; j < total; j++) {
    let n = first + 5 * j
    for (let i = 0; i < k; i++) n = shortcutStep(n, sign)
    counts[n % 5]++
  }
  return counts
}

/**
 * Simple random walk on a 5-cycle, computed by stepping the walk: the number of
 * k-step walks from vertex `from` that end at each vertex 0..4. They sum to 2^k.
 */
export function walkCounts(k: number, from: number): number[] {
  let w = [0, 0, 0, 0, 0]
  w[from] = 1
  for (let i = 0; i < k; i++) {
    const next = [0, 0, 0, 0, 0]
    for (let v = 0; v < 5; v++) {
      next[(v + 1) % 5] += w[v]
      next[(v + 4) % 5] += w[v]
    }
    w = next
  }
  return w
}

/** Lucas numbers L_0 = 2, L_1 = 1, L_2 = 3, ... */
export function lucas(k: number): number {
  let a = 2
  let b = 1
  for (let i = 0; i < k; i++) [a, b] = [b, a + b]
  return a
}

/** Closed walks of length k on a pentagon (OEIS A054877): (2^k + 2(-1)^k L_k)/5. */
export function returnCount(k: number): number {
  return (2 ** k + 2 * (k % 2 === 0 ? 1 : -1) * lucas(k)) / 5
}

/** Total variation distance between the law counts/sum and the uniform law on 5 points. */
export function distanceFromUniform(counts: number[]): number {
  const total = counts.reduce((a, b) => a + b, 0)
  return counts.reduce((acc, c) => acc + Math.abs(c / total - 0.2), 0) / 2
}

/** cos 36 degrees = half the golden ratio. */
export const HALF_PHI = (1 + Math.sqrt(5)) / 4
