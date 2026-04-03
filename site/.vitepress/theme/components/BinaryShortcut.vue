<script setup>
import { ref, computed } from 'vue'

const inputN = ref(27)

const result = computed(() => {
  let n = Number(inputN.value)
  if (n < 3 || n % 2 === 0 || !Number.isInteger(n)) return null

  const binary = n.toString(2)

  // Count trailing 1s
  let m = 0
  for (let i = binary.length - 1; i >= 0; i--) {
    if (binary[i] === '1') m++
    else break
  }

  const s0 = binary.slice(0, binary.length - m)
  const s1 = binary.slice(binary.length - m)
  const q = s0 ? parseInt(s0, 2) : 0
  const k = q + 1
  const shortcutResult = k * Math.pow(3, m) - 1

  // Verify with step-by-step
  const path = [n]
  let val = n
  for (let i = 0; i < m; i++) {
    val = (3 * val + 1) / 2
    path.push(val)
  }

  return {
    n,
    binary,
    m,
    s0: s0 || '(empty)',
    s1,
    q,
    k,
    pow3m: Math.pow(3, m),
    shortcutResult,
    path,
    match: shortcutResult === path[m]
  }
})
</script>

<template>
  <div class="binary-shortcut">
    <div class="input-row">
      <label>Enter an odd number: </label>
      <input v-model.number="inputN" type="number" min="3" step="2" class="num-input" />
    </div>

    <div v-if="result" class="results">
      <h3>Binary Shortcut for {{ result.n }}</h3>

      <div class="binary-display">
        <span class="s0-bits">{{ result.s0 === '(empty)' ? '' : result.s0 }}</span><span class="s1-bits">{{ result.s1 }}</span>
        <div class="labels">
          <span v-if="result.s0 !== '(empty)'" class="s0-label">S₀ = "{{ result.s0 }}" (decimal {{ result.q }})</span>
          <span class="s1-label">S₁ = "{{ result.s1 }}" ({{ result.m }} trailing 1{{ result.m > 1 ? 's' : '' }})</span>
        </div>
      </div>

      <div class="formula">
        <div>k = {{ result.q }} + 1 = <strong>{{ result.k }}</strong></div>
        <div>Result = {{ result.k }} × 3<sup>{{ result.m }}</sup> − 1 = {{ result.k }} × {{ result.pow3m }} − 1 = <strong>{{ result.shortcutResult }}</strong></div>
      </div>

      <h4>Verification: {{ result.m }} steps of (3x+1)/2</h4>
      <div class="path">
        <span v-for="(val, i) in result.path" :key="i">
          <span :class="{ 'highlight': i === result.m }">{{ val }}</span>
          <span v-if="i < result.path.length - 1" class="arrow"> → </span>
        </span>
      </div>
      <div class="match" :class="{ ok: result.match, fail: !result.match }">
        {{ result.match ? '✓ Match!' : '✗ Mismatch' }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.binary-shortcut { margin: 1.5rem 0; }

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

.binary-display {
  font-family: var(--vp-font-family-mono);
  font-size: 1.4rem;
  margin: 1rem 0;
  padding: 1rem;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
}

.s0-bits { color: var(--vp-c-text-2); }
.s1-bits { color: var(--vp-c-brand-1); font-weight: bold; text-decoration: underline; }

.labels {
  font-size: 0.8rem;
  margin-top: 0.5rem;
  display: flex;
  gap: 1.5rem;
}
.s0-label { color: var(--vp-c-text-3); }
.s1-label { color: var(--vp-c-brand-1); }

.formula {
  background: var(--vp-c-bg-soft);
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin: 1rem 0;
  font-size: 1rem;
  line-height: 1.8;
}

.path {
  font-family: var(--vp-font-family-mono);
  font-size: 0.95rem;
  margin: 0.5rem 0;
}

.highlight {
  background: var(--vp-c-brand-soft);
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
  font-weight: bold;
}

.arrow { color: var(--vp-c-text-3); }

.match {
  margin-top: 0.5rem;
  font-weight: bold;
}
.match.ok { color: var(--vp-c-green-1); }
.match.fail { color: var(--vp-c-red-1); }
</style>
