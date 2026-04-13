<template>
  <div class="zoo-explorer">
    <div class="controls">
      <label>
        Multiplier <em>n</em>:
        <input type="range" v-model.number="n" min="2" max="15" step="1" />
        <span class="value">{{ n }}</span>
      </label>
      <label>
        Divisor <em>y</em>:
        <input type="range" v-model.number="y" min="2" max="6" step="1" />
        <span class="value">{{ y }}</span>
      </label>
      <label>
        Constant <em>c</em>:
        <input type="range" v-model.number="c" min="1" max="19" step="2" />
        <span class="value">{{ c }}</span>
      </label>
    </div>

    <div class="system-label">
      System: <strong>{{ n }}x+{{ c }}, x/{{ y }}</strong>
      <span :class="['badge', muClass]">
        μ = {{ mu.toFixed(3) }} — {{ muLabel }}
      </span>
    </div>

    <div class="results-grid">
      <div class="physics-panel">
        <h4>Thermodynamics</h4>
        <table>
          <tr><td>Criticality μ</td><td>{{ mu.toFixed(4) }}</td></tr>
          <tr><td>Energy input/kick</td><td>{{ energyInput.toFixed(3) }} bits</td></tr>
          <tr><td>Avg drains/kick</td><td>{{ avgDrains.toFixed(3) }}</td></tr>
          <tr><td>Net per cycle</td><td :class="netPerCycle < 0 ? 'good' : 'bad'">{{ netPerCycle.toFixed(3) }} bits</td></tr>
          <tr><td>Fundamental const</td><td>log{{ y === 2 ? '₂' : '_' + y }}({{ n * y }}) = {{ fundamentalConst.toFixed(4) }}</td></tr>
        </table>
      </div>

      <div class="survey-panel">
        <h4>Survey (n=3..499, odd)</h4>
        <div class="bar-chart">
          <div class="bar converged" :style="{ width: convPct + '%' }">
            <span v-if="convPct > 10">{{ convPct.toFixed(0) }}% converge</span>
          </div>
          <div class="bar cycled" :style="{ width: cycPct + '%' }">
            <span v-if="cycPct > 10">{{ cycPct.toFixed(0) }}% cycle</span>
          </div>
          <div class="bar diverged" :style="{ width: divPct + '%' }">
            <span v-if="divPct > 10">{{ divPct.toFixed(0) }}% diverge</span>
          </div>
        </div>
        <div class="bar-labels">
          <span class="converged-label">Conv: {{ surveyResults.converged }}</span>
          <span class="cycled-label">Cycle: {{ surveyResults.cycled }}</span>
          <span class="diverged-label">Div: {{ surveyResults.diverged }}</span>
        </div>
      </div>
    </div>

    <div class="orbit-panel">
      <h4>Sample orbit: x = {{ sampleStart }}</h4>
      <div class="orbit-display">
        <svg :viewBox="`0 0 ${orbitWidth} ${orbitHeight}`" class="orbit-svg">
          <polyline
            :points="orbitPoints"
            fill="none"
            :stroke="mu < 1 ? '#3eaf7c' : '#e74c3c'"
            stroke-width="1.5"
          />
          <line x1="0" :y1="baselineY" :x2="orbitWidth" :y2="baselineY"
                stroke="#666" stroke-width="0.5" stroke-dasharray="4,4" />
        </svg>
        <div class="orbit-info">
          {{ sampleOrbit.length }} steps, peak {{ samplePeak.toLocaleString() }},
          {{ sampleStatus }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const n = ref(3)
const y = ref(2)
const c = ref(1)
const MAX_STEPS = 2000

const energyInput = computed(() => Math.log(n.value) / Math.log(y.value))

const avgDrains = computed(() => {
  // Estimate avg y-adic valuation of nx+c for random x not divisible by y
  let totalDrains = 0
  let count = 0
  for (let x = 1; x < 500; x++) {
    if (x % y.value === 0) continue
    let val = n.value * x + c.value
    let d = 0
    while (val > 0 && val % y.value === 0) {
      val = Math.floor(val / y.value)
      d++
    }
    totalDrains += d
    count++
  }
  return count > 0 ? totalDrains / count : 1
})

const mu = computed(() => n.value / Math.pow(y.value, avgDrains.value))
const netPerCycle = computed(() => energyInput.value - avgDrains.value)
const fundamentalConst = computed(() => Math.log(n.value * y.value) / Math.log(y.value))

const muClass = computed(() => mu.value < 1 ? 'subcritical' : 'supercritical')
const muLabel = computed(() => mu.value < 1 ? 'Subcritical' : 'Supercritical')

function step(x) {
  if (x % y.value === 0) return Math.floor(x / y.value)
  return n.value * x + c.value
}

function runOrbit(x0) {
  const seq = [x0]
  const seen = new Set([x0])
  let status = 'timeout'
  for (let i = 0; i < MAX_STEPS; i++) {
    const next = step(seq[seq.length - 1])
    seq.push(next)
    if (next === 1) { status = 'converged'; break }
    if (next <= 0 || next > 1e15) { status = 'diverged'; break }
    if (seen.has(next)) { status = 'cycle'; break }
    seen.add(next)
  }
  return { seq, status }
}

const surveyResults = computed(() => {
  let converged = 0, cycled = 0, diverged = 0
  for (let x = 3; x < 500; x += 2) {
    if (x % y.value === 0) continue
    const { status } = runOrbit(x)
    if (status === 'converged') converged++
    else if (status === 'cycle') cycled++
    else diverged++
  }
  return { converged, cycled, diverged }
})

const total = computed(() => {
  const s = surveyResults.value
  return s.converged + s.cycled + s.diverged || 1
})
const convPct = computed(() => surveyResults.value.converged / total.value * 100)
const cycPct = computed(() => surveyResults.value.cycled / total.value * 100)
const divPct = computed(() => surveyResults.value.diverged / total.value * 100)

const sampleStart = computed(() => {
  // Pick an interesting starting value
  for (const x of [27, 31, 47, 73, 97, 127]) {
    if (x % y.value !== 0) return x
  }
  return 3
})

const sampleOrbitData = computed(() => runOrbit(sampleStart.value))
const sampleOrbit = computed(() => sampleOrbitData.value.seq)
const sampleStatus = computed(() => sampleOrbitData.value.status)
const samplePeak = computed(() => Math.max(...sampleOrbit.value))

const orbitWidth = 600
const orbitHeight = 150

const orbitPoints = computed(() => {
  const seq = sampleOrbit.value
  if (seq.length < 2) return ''
  const maxVal = Math.max(...seq, 2)
  const logMax = Math.log2(maxVal)
  return seq.map((v, i) => {
    const x = (i / (seq.length - 1)) * orbitWidth
    const ly = v > 0 ? Math.log2(v) : 0
    const plotY = orbitHeight - 10 - (ly / logMax) * (orbitHeight - 20)
    return `${x},${plotY}`
  }).join(' ')
})

const baselineY = computed(() => {
  const maxVal = Math.max(...sampleOrbit.value, 2)
  const logMax = Math.log2(maxVal)
  const logStart = Math.log2(sampleStart.value)
  return orbitHeight - 10 - (logStart / logMax) * (orbitHeight - 20)
})
</script>

<style scoped>
.zoo-explorer {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}

.controls {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.controls label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.controls input[type="range"] {
  width: 120px;
}

.value {
  font-weight: bold;
  min-width: 24px;
  text-align: center;
}

.system-label {
  font-size: 16px;
  margin-bottom: 16px;
}

.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 13px;
  margin-left: 12px;
}

.badge.subcritical {
  background: #d4edda;
  color: #155724;
}

.badge.supercritical {
  background: #f8d7da;
  color: #721c24;
}

.results-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

@media (max-width: 640px) {
  .results-grid { grid-template-columns: 1fr; }
  .controls { flex-direction: column; gap: 12px; }
}

.physics-panel, .survey-panel {
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  padding: 12px;
  background: var(--vp-c-bg);
}

.physics-panel h4, .survey-panel h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--vp-c-text-2);
}

.physics-panel table {
  width: 100%;
  font-size: 13px;
}

.physics-panel td {
  padding: 2px 8px;
}

.physics-panel td:first-child {
  color: var(--vp-c-text-2);
}

.physics-panel td.good { color: #3eaf7c; font-weight: bold; }
.physics-panel td.bad { color: #e74c3c; font-weight: bold; }

.bar-chart {
  display: flex;
  height: 32px;
  border-radius: 4px;
  overflow: hidden;
  background: var(--vp-c-divider);
}

.bar {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: bold;
  color: white;
  min-width: 0;
  transition: width 0.3s ease;
}

.bar.converged { background: #3eaf7c; }
.bar.cycled { background: #e2b93d; }
.bar.diverged { background: #e74c3c; }

.bar-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-top: 4px;
}

.converged-label { color: #3eaf7c; }
.cycled-label { color: #e2b93d; }
.diverged-label { color: #e74c3c; }

.orbit-panel {
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  padding: 12px;
  background: var(--vp-c-bg);
}

.orbit-panel h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--vp-c-text-2);
}

.orbit-svg {
  width: 100%;
  height: 150px;
}

.orbit-info {
  font-size: 12px;
  color: var(--vp-c-text-2);
  margin-top: 4px;
}
</style>
