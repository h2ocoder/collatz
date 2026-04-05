<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { cycleGap, parityWords } from '../../utils/collatz'

const S = ref(5)
const E = ref(8)

const K = computed(() => S.value + E.value)
const isAscending = computed(() => {
  // 3^S > 2^E means ascending
  return S.value * Math.log2(3) > E.value
})

const gap = computed(() => {
  try {
    return cycleGap(S.value, E.value)
  } catch { return 0n }
})

const gapLog2 = computed(() => {
  const g = gap.value
  if (g === 0n) return 0
  return Math.log2(Number(g))
})

const words = computed(() => {
  if (K.value > 25) return null // too many
  return parityWords(K.value, S.value)
})

const wordCount = computed(() => {
  if (words.value) return words.value.length
  // Approximate with binomial
  const n = E.value - 1
  const k = S.value - 1
  if (k < 0 || k > n) return 0
  return Math.round(Math.exp(logBinom(n, k)))
})

function logBinom(n: number, k: number): number {
  let s = 0
  for (let i = 0; i < k; i++) s += Math.log(n - i) - Math.log(i + 1)
  return s
}

// For small K: compute the T values and their remainders mod gap
const remainders = computed(() => {
  if (!words.value || gap.value === 0n || gap.value > 1000000000n) return null
  const g = Number(gap.value)
  const results: { word: string; T: number; remainder: number }[] = []

  for (const w of words.value) {
    // T = sum over odd positions of 2^E * C_i where C_i is the affine constant
    // Simplified: compute T mod g for the word
    let T = 0
    let pow2 = 1
    let pow3 = 1
    for (let i = 0; i < w.length; i++) {
      if (w[i] === 1) { // odd step
        T = (T + pow3 * pow2) % g
        pow3 = (pow3 * 3) % g
      }
      pow2 = (pow2 * 2) % g
    }
    const remainder = ((T % g) + g) % g
    results.push({
      word: w.join(''),
      T,
      remainder
    })
  }
  return results
})

const histogramData = computed(() => {
  if (!remainders.value) return null
  const g = Number(gap.value)
  const bins = Math.min(g, 50)
  const binWidth = g / bins
  const counts = new Array(bins).fill(0)

  for (const { remainder } of remainders.value) {
    const bin = Math.min(Math.floor(remainder / binWidth), bins - 1)
    counts[bin]++
  }

  const zeroCount = remainders.value.filter(r => r.remainder === 0).length
  return { counts, bins, binWidth, zeroCount, total: remainders.value.length }
})

const wordsPerGap = computed(() => {
  if (gap.value === 0n) return Infinity
  return wordCount.value / Number(gap.value)
})
</script>

<template>
  <div class="cycle-hunter">
    <div class="controls">
      <label>
        S (odd steps):
        <input type="number" v-model.number="S" min="1" max="50" />
      </label>
      <label>
        E (even steps):
        <input type="number" v-model.number="E" min="1" max="100" />
      </label>
      <span class="k-display">K = {{ K }}</span>
    </div>

    <div class="result-panel" :class="{ ascending: isAscending }">
      <div v-if="isAscending" class="verdict ascending">
        <strong>ASCENDING</strong> — $3^{{ '{' + S + '}' }} > 2^{{ '{' + E + '}' }}$.
        The gap is negative. Any cycle solution gives $n &lt; 0$.
        <br/><strong>Eliminated automatically.</strong>
      </div>
      <div v-else class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Gap $g = 2^{{ '{' + E + '}' }} - 3^{{ '{' + S + '}' }}$</div>
          <div class="stat-val">{{ gap.toLocaleString() }}</div>
          <div class="stat-sub">≈ 2^{{ gapLog2.toFixed(1) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Parity words</div>
          <div class="stat-val">{{ wordCount.toLocaleString() }}</div>
          <div class="stat-sub">$C({{ E-1 }}, {{ S-1 }})$</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Words / Gap</div>
          <div class="stat-val" :class="{ danger: wordsPerGap > 1, safe: wordsPerGap < 1 }">
            {{ wordsPerGap < 0.001 ? wordsPerGap.toExponential(1) : wordsPerGap.toFixed(3) }}
          </div>
          <div class="stat-sub">{{ wordsPerGap < 1 ? 'Too few words for a cycle' : 'Needs closer inspection' }}</div>
        </div>
      </div>

      <div v-if="histogramData && !isAscending" class="histogram-section">
        <h4>Remainder distribution (T mod {{ Number(gap).toLocaleString() }})</h4>
        <div class="histogram">
          <div
            v-for="(count, i) in histogramData.counts"
            :key="i"
            class="hist-bar"
            :style="{
              height: count / Math.max(...histogramData.counts) * 100 + '%',
              background: i === 0 ? (histogramData.zeroCount > 0 ? '#ef4444' : '#22c55e') : 'var(--vp-c-brand-1)'
            }"
          />
        </div>
        <div class="hist-labels">
          <span>0</span>
          <span>{{ Math.floor(Number(gap) / 2).toLocaleString() }}</span>
          <span>{{ Number(gap).toLocaleString() }}</span>
        </div>
        <div class="verdict" :class="histogramData.zeroCount === 0 ? 'safe' : 'danger'">
          <strong>{{ histogramData.zeroCount === 0 ? 'NO CYCLES' : 'CYCLE FOUND' }}</strong>
          — {{ histogramData.zeroCount }} of {{ histogramData.total }} words have remainder 0.
          {{ histogramData.zeroCount === 0 ? 'The gap never divides T.' : '' }}
        </div>
      </div>

      <div v-if="K > 25 && !isAscending" class="too-large">
        <p>K = {{ K }} is too large to enumerate words directly.
        For $(S, E) = (41, 65)$: eliminated by MITM computation (87 min in Rust).
        For $S \geq 306$: the second moment bound proves words/gap $\to 0$ exponentially.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cycle-hunter {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}

.controls {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 16px;
}

.controls input {
  width: 70px;
  padding: 6px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
}

.controls label { display: flex; align-items: center; gap: 8px; font-size: 14px; }

.k-display {
  font-family: var(--vp-font-family-mono);
  font-weight: 600;
  color: var(--vp-c-brand-1);
}

.result-panel { padding: 16px; background: var(--vp-c-bg); border-radius: 8px; }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 16px; }

.stat-card {
  padding: 12px;
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
}

.stat-label { font-size: 12px; color: var(--vp-c-text-3); margin-bottom: 4px; }
.stat-val { font-size: 20px; font-weight: 700; font-family: var(--vp-font-family-mono); }
.stat-val.danger { color: #ef4444; }
.stat-val.safe { color: #22c55e; }
.stat-sub { font-size: 12px; color: var(--vp-c-text-3); margin-top: 2px; }

.histogram-section h4 { margin: 12px 0 8px; font-size: 14px; }

.histogram {
  display: flex;
  align-items: flex-end;
  height: 120px;
  gap: 1px;
  background: var(--vp-c-bg-soft);
  border-radius: 6px;
  padding: 4px;
}

.hist-bar { flex: 1; min-width: 3px; border-radius: 2px 2px 0 0; transition: height 0.3s; }

.hist-labels { display: flex; justify-content: space-between; font-size: 11px; color: var(--vp-c-text-3); margin-top: 4px; }

.verdict {
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
}

.verdict.safe { background: #dcfce7; color: #15803d; }
.verdict.danger { background: #fee2e2; color: #b91c1c; }
.verdict.ascending { background: #dbeafe; color: #1d4ed8; }

.too-large { font-size: 14px; color: var(--vp-c-text-2); padding: 12px; }
</style>
