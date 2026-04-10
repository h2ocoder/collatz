/**
 * Shared Collatz computation utilities.
 * All functions work with standard numbers for small values
 * and BigInt where overflow is possible.
 */

/** 2-adic valuation: largest power of 2 dividing n */
export function v2(n: number): number {
  if (n === 0) return Infinity
  let c = 0
  while ((n & 1) === 0) { n >>= 1; c++ }
  return c
}

/** Single Collatz step: n/2 if even, 3n+1 if odd */
export function collatzStep(n: number): number {
  return (n & 1) ? 3 * n + 1 : n >> 1
}

/** Full Collatz orbit from n down to 1 */
export function orbit(n: number, maxSteps = 10000): number[] {
  const seq = [n]
  let steps = 0
  while (n !== 1 && steps < maxSteps) {
    n = collatzStep(n)
    seq.push(n)
    steps++
  }
  return seq
}

/** Syracuse step: odd → odd (skip even steps) */
export function syracuseStep(m: number): number {
  let val = 3 * m + 1
  while ((val & 1) === 0) val >>= 1
  return val
}

/** Syracuse orbit: sequence of odd values */
export function syracuseOrbit(m: number, maxSteps = 5000): number[] {
  const seq = [m]
  let steps = 0
  while (m !== 1 && steps < maxSteps) {
    m = syracuseStep(m)
    seq.push(m)
    steps++
  }
  return seq
}

/** Stopping time: steps to first value < n */
export function stoppingTime(n: number): number {
  const start = n
  let steps = 0
  while (n >= start && n !== 1) {
    n = collatzStep(n)
    steps++
    if (steps > 100000) return -1 // safety
  }
  return steps
}

/** Dropping time (= stopping time): alias for clarity */
export function droppingTime(n: number): number {
  return stoppingTime(n)
}

/** First value < n in the orbit */
export function stoppingDestination(n: number): number {
  const start = n
  while (n >= start) {
    n = collatzStep(n)
  }
  return n
}

/** Orbital oddity: count of odd values in the dropping orbit */
export function orbitalOddity(n: number): number {
  const start = n
  let count = 0
  let current = n
  while (current >= start) {
    if (current & 1) count++
    current = collatzStep(current)
  }
  return count
}

/** Bit destruction rate β(s) = ceil(s·log₂3) - s·log₂3 */
export function beta(s: number): number {
  const sl3 = s * Math.log2(3)
  return Math.ceil(sl3) - sl3
}

/** Cycle gap |2^E - 3^S| using BigInt for precision */
export function cycleGap(S: number, E: number): bigint {
  const pow2 = 1n << BigInt(E)
  let pow3 = 1n
  for (let i = 0; i < S; i++) pow3 *= 3n
  const diff = pow2 - pow3
  return diff < 0n ? -diff : diff
}

/** Count trailing 1-bits in binary representation */
export function trailingOnes(n: number): number {
  let c = 0
  while (n & 1) { c++; n >>= 1 }
  return c
}

/** Drop depth = v2(3m+1) for odd m */
export function dropDepth(m: number): number {
  return v2(3 * m + 1)
}

/**
 * Enumerate valid parity words for cycle (S, E) with K = S + E.
 * A parity word is a binary string of length K with exactly S ones,
 * starting with 1 (odd step first).
 * Returns array of words (as arrays of 0s and 1s).
 * Only feasible for small K (≤ ~20).
 */
export function parityWords(K: number, S: number): number[][] {
  if (S < 1 || S > K - 1 || K > 25) return []
  const words: number[][] = []

  // First bit is always 1 (start with odd step)
  // Need S-1 more ones in remaining K-1 positions
  function generate(pos: number, ones: number, current: number[]) {
    if (pos === K) {
      if (ones === S) words.push([...current])
      return
    }
    const remaining = K - pos
    const onesNeeded = S - ones
    // Try placing 1
    if (onesNeeded > 0 && onesNeeded <= remaining) {
      current.push(1)
      generate(pos + 1, ones + 1, current)
      current.pop()
    }
    // Try placing 0
    if (remaining - 1 >= onesNeeded) {
      current.push(0)
      generate(pos + 1, ones, current)
      current.pop()
    }
  }

  generate(1, 1, [1]) // first bit = 1
  return words
}

/** log base 6 */
export function log6(n: number): number {
  return Math.log(n) / Math.log(6)
}

/** Fractional part */
export function frac(x: number): number {
  return x - Math.floor(x)
}

/** Alpha sequence: v2(3m+1) at each Syracuse step */
export function alphaSequence(n: number, maxSteps = 5000): number[] {
  const alphas: number[] = []
  let m = n
  let steps = 0
  while (m !== 1 && steps < maxSteps) {
    alphas.push(v2(3 * m + 1))
    m = syracuseStep(m)
    steps++
  }
  return alphas
}

/** Eisenstein norm: N(a + b*omega) = a^2 - ab + b^2 */
export function eisensteinNorm(a: number, b: number): number {
  return a * a - a * b + b * b
}

/** The rotation constant */
export const LOG6_3 = Math.log(3) / Math.log(6) // ≈ 0.6131
export const LOG2_3 = Math.log2(3) // ≈ 1.5850
export const LOG2_6 = Math.log2(6) // ≈ 2.5850
