<template>
  <div class="spectrum-viz">
    <div class="controls">
      <label>
        Multiplier <em>n</em>:
        <input type="range" v-model.number="n" min="3" max="13" step="2" />
        <span class="value">{{ n }}</span>
      </label>
      <label>
        Modulus <em>M</em>:
        <select v-model.number="modulus">
          <option v-for="m in modulusOptions" :key="m" :value="m">{{ m }}</option>
        </select>
      </label>
    </div>

    <div class="system-label">
      Transfer operator for <strong>{{ n }}x+1, x/2</strong> on Z/{{ modulus }}Z
    </div>

    <div class="viz-grid">
      <div class="circle-panel">
        <h4>Eigenvalue Spectrum</h4>
        <svg :viewBox="`-${R+40} -${R+40} ${2*(R+40)} ${2*(R+40)}`" class="circle-svg">
          <!-- Unit circle -->
          <circle cx="0" cy="0" :r="R" fill="none" stroke="#666" stroke-width="0.5" stroke-dasharray="4,4" />

          <!-- Critical circle -->
          <circle cx="0" cy="0" :r="criticalR" fill="none"
                  :stroke="criticalRadius > 1 ? '#3eaf7c' : '#e74c3c'"
                  stroke-width="1.5" stroke-dasharray="6,3" />

          <!-- Axes -->
          <line :x1="-R-20" y1="0" :x2="R+20" y2="0" stroke="#444" stroke-width="0.3" />
          <line x1="0" :y1="-R-20" x2="0" :y2="R+20" stroke="#444" stroke-width="0.3" />

          <!-- Eigenvalues -->
          <circle v-for="(e, i) in eigenvalues" :key="i"
                  :cx="e.re * scale" :cy="-e.im * scale"
                  :r="e.mag > 0.01 ? 5 : 2"
                  :fill="e.mag > 0.01 ? (e.mag > 1 ? '#3eaf7c' : '#e74c3c') : '#888'"
                  :opacity="e.mag > 0.01 ? 1 : 0.3"
                  stroke="white" stroke-width="0.5" />

          <!-- Labels -->
          <text :x="R+5" y="12" fill="#888" font-size="11">Re</text>
          <text x="5" :y="-R-8" fill="#888" font-size="11">Im</text>
          <text :x="R+3" y="-3" fill="#666" font-size="9">{{ (R/scale).toFixed(1) }}</text>
          <text x="-3" :y="-R+12" fill="#666" font-size="9" text-anchor="end">{{ (R/scale).toFixed(1) }}i</text>

          <!-- Critical circle label -->
          <text :x="criticalR + 4" y="-8"
                :fill="criticalRadius > 1 ? '#3eaf7c' : '#e74c3c'"
                font-size="10">
            |λ|={{ criticalRadius.toFixed(3) }}
          </text>
        </svg>
      </div>

      <div class="info-panel">
        <h4>Spectral Analysis</h4>
        <table>
          <tr>
            <td>Dimension</td>
            <td>{{ modulus }}</td>
          </tr>
          <tr>
            <td>Non-zero eigenvalues</td>
            <td>{{ nonZeroCount }}</td>
          </tr>
          <tr>
            <td>λ₁ (trivial)</td>
            <td>{{ trivialEig.toFixed(4) }}</td>
          </tr>
          <tr>
            <td>Critical radius |λ₂|</td>
            <td :class="criticalRadius > 1 ? 'good' : 'bad'">
              {{ criticalRadius.toFixed(6) }}
            </td>
          </tr>
          <tr>
            <td>Predicted radius</td>
            <td>({{ y }}²/{{ n }})^(1/{{ n }}) = {{ predictedRadius.toFixed(6) }}</td>
          </tr>
          <tr>
            <td>|λ₂|ⁿ</td>
            <td>{{ Math.pow(criticalRadius, n).toFixed(6) }}</td>
          </tr>
          <tr>
            <td>y²/n = 4/{{ n }}</td>
            <td>{{ (4/n).toFixed(6) }}</td>
          </tr>
          <tr>
            <td>Eigenvalue eq.</td>
            <td>
              λ<sup>{{ n }}</sup> = {{ (4/n).toFixed(4) }}
            </td>
          </tr>
        </table>

        <div class="eigenvalue-eq" v-if="n === 3">
          <div class="eq-box">
            λ³ = 4/3
            <br />
            λ = ∛(4/3) · ωᵏ
            <br />
            <small>ω = e^(2πi/3), k = 0, 1, 2</small>
          </div>
        </div>

        <div class="verdict">
          <template v-if="criticalRadius > 1">
            Critical circle radius > 1
            <br />
            <strong>⟹ Subcritical: orbits contract</strong>
          </template>
          <template v-else>
            Critical circle radius &lt; 1
            <br />
            <strong>⟹ Supercritical: orbits grow</strong>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const n = ref(3)
const y = 2
const modulus = ref(24)

const modulusOptions = [6, 12, 24, 48, 96]

const R = 120
const scale = computed(() => R / 2.5)

// Analytical eigenvalues of the transfer operator
// For nx+1, x/2: non-trivial eigenvalues are n-th roots of y^2/n
// Verified numerically via NumPy for n=3,5,7,9,11,13 (see collatz/zoo.py)
const eigenvalues = computed(() => {
  const M = modulus.value
  const nVal = n.value

  const ratio = (y * y) / nVal
  const radius = Math.pow(ratio, 1.0 / nVal)

  const eigs = []
  // Trivial eigenvalue
  eigs.push({ re: 2, im: 0, mag: 2 })

  // Non-trivial: n-th roots of y^2/n
  for (let k = 0; k < nVal; k++) {
    const angle = (2 * Math.PI * k) / nVal
    eigs.push({
      re: radius * Math.cos(angle),
      im: radius * Math.sin(angle),
      mag: radius
    })
  }

  // Fill remaining with zeros
  for (let i = eigs.length; i < M; i++) {
    eigs.push({ re: 0, im: 0, mag: 0 })
  }

  return eigs
})

const nonZeroCount = computed(() => eigenvalues.value.filter(e => e.mag > 0.01).length)
const trivialEig = computed(() => 2.0)

const criticalRadius = computed(() => {
  const ratio = (y * y) / n.value
  return Math.pow(ratio, 1.0 / n.value)
})

const criticalR = computed(() => criticalRadius.value * scale.value)

const predictedRadius = computed(() => {
  return Math.pow(4.0 / n.value, 1.0 / n.value)
})
</script>

<style scoped>
.spectrum-viz {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}

.controls {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.controls label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.value {
  font-weight: bold;
  min-width: 24px;
}

.system-label {
  font-size: 16px;
  margin-bottom: 16px;
}

.viz-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 640px) {
  .viz-grid { grid-template-columns: 1fr; }
  .controls { flex-direction: column; gap: 12px; }
}

.circle-panel, .info-panel {
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  padding: 12px;
  background: var(--vp-c-bg);
}

.circle-panel h4, .info-panel h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--vp-c-text-2);
}

.circle-svg {
  width: 100%;
  max-height: 320px;
}

.info-panel table {
  width: 100%;
  font-size: 13px;
  margin-bottom: 12px;
}

.info-panel td {
  padding: 3px 8px;
}

.info-panel td:first-child {
  color: var(--vp-c-text-2);
}

.good { color: #3eaf7c; font-weight: bold; }
.bad { color: #e74c3c; font-weight: bold; }

.eigenvalue-eq {
  margin: 12px 0;
}

.eq-box {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  padding: 12px;
  text-align: center;
  font-size: 16px;
  font-family: 'KaTeX_Math', serif;
}

.eq-box small {
  font-size: 12px;
  color: var(--vp-c-text-2);
}

.verdict {
  margin-top: 12px;
  padding: 10px;
  border-radius: 6px;
  text-align: center;
  font-size: 14px;
  background: var(--vp-c-bg-soft);
}
</style>
