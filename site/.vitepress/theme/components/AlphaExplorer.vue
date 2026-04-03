<script setup>
import { ref, computed } from 'vue'

const inputN = ref(27)

function computeAlphaSteps(n) {
  if (n < 1 || !Number.isInteger(n)) return { steps: [], alphas: [] }

  const steps = []
  const alphas = []

  while (n > 1) {
    if (n % 2 === 1) {
      const product = 3 * n + 1
      let val = product
      let halvings = 0
      while (val % 2 === 0) {
        val = val / 2
        halvings++
      }
      steps.push({
        type: 'odd',
        from: n,
        product: product,
        halvings: halvings,
        to: val,
        alpha: halvings
      })
      alphas.push(halvings)
      n = val
    } else {
      const to = n / 2
      steps.push({
        type: 'even',
        from: n,
        to: to
      })
      n = to
    }
  }

  return { steps, alphas }
}

const result = computed(() => {
  const n = Number(inputN.value)
  if (n < 2 || !Number.isInteger(n)) return null

  const { steps, alphas } = computeAlphaSteps(n)
  const distinct = [...new Set(alphas)].sort((a, b) => a - b)
  const radical = distinct.reduce((a, b) => a * b, 1)
  const bits = Math.log2(n)
  const quality = radical > 1 ? bits / Math.log2(radical) : Infinity
  const totalHalvings = alphas.reduce((a, b) => a + b, 0)

  return {
    n,
    steps,
    alphas,
    distinct,
    radical,
    quality,
    bits,
    totalOddSteps: alphas.length,
    totalHalvings,
    totalSteps: steps.length
  }
})
</script>

<template>
  <div class="alpha-explorer">
    <div class="input-row">
      <label>Enter an odd number: </label>
      <input
        v-model.number="inputN"
        type="number"
        min="3"
        step="2"
        class="num-input"
      />
    </div>

    <div v-if="result" class="results">
      <h3>Alpha Sequence of {{ result.n }}</h3>

      <div class="step-trace">
        <div
          v-for="(step, i) in result.steps"
          :key="i"
          :class="['step', step.type]"
        >
          <template v-if="step.type === 'odd'">
            <span class="num">{{ step.from }}</span>
            <span class="arrow">→</span>
            <span class="calc">3×{{ step.from }}+1 = {{ step.product }}</span>
            <span class="arrow">→</span>
            <span class="calc">÷2<sup>{{ step.halvings }}</sup></span>
            <span class="arrow">→</span>
            <span class="num">{{ step.to }}</span>
            <span class="alpha-badge">α = {{ step.alpha }}</span>
          </template>
          <template v-else>
            <span class="num even-num">{{ step.from }}</span>
            <span class="arrow">→</span>
            <span class="calc">÷2</span>
            <span class="arrow">→</span>
            <span class="num">{{ step.to }}</span>
          </template>
        </div>
      </div>

      <h3>Summary</h3>
      <table class="summary-table">
        <tr>
          <td>Alpha sequence</td>
          <td><strong>[{{ result.alphas.join(', ') }}]</strong></td>
        </tr>
        <tr>
          <td>Distinct alphas</td>
          <td>{{ '{' + result.distinct.join(', ') + '}' }}</td>
        </tr>
        <tr>
          <td>Collatz radical</td>
          <td>{{ result.distinct.join(' × ') }} = <strong>{{ result.radical }}</strong></td>
        </tr>
        <tr>
          <td>Collatz quality</td>
          <td>log₂({{ result.n }}) / log₂({{ result.radical }}) = <strong>{{ result.quality === Infinity ? '∞' : result.quality.toFixed(3) }}</strong></td>
        </tr>
        <tr><td colspan="2" style="border-top: 1px solid var(--vp-c-divider)"></td></tr>
        <tr>
          <td>Odd steps (3n+1)</td>
          <td>{{ result.totalOddSteps }}</td>
        </tr>
        <tr>
          <td>Total halvings</td>
          <td>{{ result.totalHalvings }}</td>
        </tr>
        <tr>
          <td>Total Collatz steps</td>
          <td>{{ result.totalSteps }}</td>
        </tr>
        <tr>
          <td>Bits of n</td>
          <td>{{ result.bits.toFixed(1) }}</td>
        </tr>
      </table>

      <div v-if="result.quality > 3" class="high-quality-note">
        ⚡ <strong>High quality orbit!</strong> This number uses very few distinct alpha values relative to its size —
        its orbit is exceptionally "smooth."
      </div>
    </div>
  </div>
</template>

<style scoped>
.alpha-explorer {
  margin: 1.5rem 0;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.num-input {
  font-size: 1.1rem;
  padding: 0.4rem 0.8rem;
  border: 2px solid var(--vp-c-brand-1);
  border-radius: 6px;
  width: 150px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
}

.step-trace {
  font-family: var(--vp-font-family-mono);
  font-size: 0.85rem;
  line-height: 1.8;
  margin: 1rem 0;
  padding: 1rem;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.step {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.step.odd {
  margin: 0.2rem 0;
}

.step.even {
  opacity: 0.5;
  margin: 0.1rem 0;
}

.num {
  font-weight: bold;
  color: var(--vp-c-brand-1);
}

.even-num {
  color: var(--vp-c-text-2);
}

.arrow {
  color: var(--vp-c-text-3);
}

.calc {
  color: var(--vp-c-text-2);
}

.alpha-badge {
  background: var(--vp-c-brand-1);
  color: white;
  padding: 0.1rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  margin-left: 0.5rem;
}

.summary-table {
  width: 100%;
  max-width: 500px;
  border-collapse: collapse;
  margin: 1rem 0;
}

.summary-table td {
  padding: 0.4rem 0.8rem;
}

.summary-table td:first-child {
  color: var(--vp-c-text-2);
  white-space: nowrap;
}

.high-quality-note {
  background: var(--vp-c-brand-soft);
  border-left: 4px solid var(--vp-c-brand-1);
  padding: 0.75rem 1rem;
  border-radius: 0 6px 6px 0;
  margin-top: 1rem;
}
</style>
