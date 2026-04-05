<script setup lang="ts">
import { ref, computed } from 'vue'
import { v2, dropDepth } from '../../utils/collatz'

const inputN = ref(76827)
const steps = ref<{ m: number; bitLen: number; constraintBits: number; depth: number; isBounce: boolean }[]>([])
const currentStep = ref(0)

function init() {
  let m = Math.max(3, inputN.value)
  if (m % 2 === 0) m++
  const B = Math.ceil(Math.log2(m + 1))
  const entries: typeof steps.value = []
  let constraintAccum = 0

  for (let i = 0; i < 80 && m > 1; i++) {
    // Run to Set_3
    while (m > 1 && m % 4 === 3) {
      m = (3 * m + 1) / 2
    }
    if (m <= 1) break

    const depth = dropDepth(m)
    const vm1 = v2(m - 1)
    const isBounce = vm1 === 3 && m % 16 === 9 && ((m - 9) / 16) % 8 === 2
    const bitLen = Math.ceil(Math.log2(m + 1))

    // Each bounce consumes ~1.92 bits of constraint
    if (isBounce) constraintAccum += 1.92
    else constraintAccum += 0.5 // non-bounce Set_3 still uses some

    entries.push({ m, bitLen, constraintBits: constraintAccum, depth, isBounce })

    // Syracuse step
    let next = 3 * m + 1
    while (next % 2 === 0) next >>= 1
    m = next
  }
  steps.value = entries
  currentStep.value = 0
}

const initialBits = computed(() => {
  const n = Math.max(3, inputN.value)
  return Math.ceil(Math.log2(n + 1))
})

const visibleSteps = computed(() => steps.value.slice(0, currentStep.value + 1))

const currentEntry = computed(() => steps.value[currentStep.value])

function stepAll() { currentStep.value = steps.value.length - 1 }

init()
</script>

<template>
  <div class="bounce-sim">
    <div class="controls">
      <label>
        Start (try 76827):
        <input type="number" v-model.number="inputN" min="3" @keydown.enter="init" />
      </label>
      <button @click="init">Reset</button>
      <button @click="currentStep > 0 && currentStep--">←</button>
      <button @click="currentStep < steps.length - 1 && currentStep++">→</button>
      <button @click="stepAll">Show All</button>
    </div>

    <div class="fuel-gauge">
      <div class="gauge-label">
        <span>Bit Budget: <strong>{{ initialBits }}</strong> bits</span>
        <span v-if="currentEntry">
          Consumed: <strong>{{ currentEntry.constraintBits.toFixed(1) }}</strong> bits
        </span>
      </div>
      <div class="gauge-bar">
        <div class="gauge-fill budget" :style="{ width: '100%' }"></div>
        <div
          class="gauge-fill consumed"
          :style="{ width: Math.min((currentEntry?.constraintBits ?? 0) / initialBits * 100, 100) + '%' }"
        ></div>
        <div
          class="event-horizon"
          :style="{ left: '100%' }"
          title="Event horizon: bits end here"
        >
          <span class="horizon-label">event horizon</span>
        </div>
      </div>
      <div class="gauge-legend">
        <span><span class="dot budget-dot"></span> Available ({{ initialBits }} bits)</span>
        <span><span class="dot consumed-dot"></span> Consumed (~1.92/bounce)</span>
      </div>
    </div>

    <div class="step-list">
      <div
        v-for="(s, i) in visibleSteps"
        :key="i"
        class="step-row"
        :class="{
          current: i === currentStep,
          bounce: s.isBounce,
          deep: s.depth >= 3,
          strong: s.depth >= 4
        }"
        @click="currentStep = i"
      >
        <span class="s-idx">{{ i }}</span>
        <span class="s-bits">{{ s.bitLen }}b</span>
        <span class="s-depth" :class="{ deep: s.depth >= 3, strong: s.depth >= 4 }">
          d={{ s.depth }}
        </span>
        <span class="s-type">
          {{ s.isBounce ? 'BOUNCE' : s.depth >= 4 ? 'STRONG' : s.depth >= 3 ? 'medium' : 'weak' }}
        </span>
        <div class="s-bar-container">
          <div class="s-bar consumed" :style="{ width: Math.min(s.constraintBits / initialBits * 100, 100) + '%' }"></div>
        </div>
      </div>
    </div>

    <div class="insight" v-if="currentEntry && currentEntry.constraintBits > initialBits * 0.8">
      <strong>Fuel running low!</strong> The constraint bits ({{ currentEntry.constraintBits.toFixed(1) }})
      are approaching the bit budget ({{ initialBits }}). The event horizon is near.
      Beyond it: all bits are zero, and the bounce sequence must terminate.
    </div>
  </div>
</template>

<style scoped>
.bounce-sim {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}

.controls { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 16px; }
.controls input { width: 100px; padding: 6px 10px; border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg); color: var(--vp-c-text-1); font-size: 14px; }
.controls button { padding: 6px 14px; border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg); color: var(--vp-c-text-1); cursor: pointer; font-size: 13px; }
.controls button:hover { background: var(--vp-c-brand-soft); }

.fuel-gauge { margin-bottom: 16px; padding: 14px; background: var(--vp-c-bg); border-radius: 8px; }
.gauge-label { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 8px; }
.gauge-bar { position: relative; height: 24px; border-radius: 12px; background: var(--vp-c-bg-soft); overflow: visible; }
.gauge-fill { position: absolute; top: 0; left: 0; height: 100%; border-radius: 12px; transition: width 0.3s; }
.gauge-fill.budget { background: #dbeafe; }
.gauge-fill.consumed { background: linear-gradient(90deg, #f59e0b, #ef4444); opacity: 0.8; }
.event-horizon { position: absolute; top: -4px; height: 32px; width: 2px; background: #ef4444; }
.horizon-label { position: absolute; top: -18px; left: -30px; font-size: 10px; color: #ef4444; white-space: nowrap; }
.gauge-legend { display: flex; gap: 16px; margin-top: 6px; font-size: 11px; color: var(--vp-c-text-3); }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 2px; margin-right: 4px; }
.budget-dot { background: #93c5fd; }
.consumed-dot { background: #f59e0b; }

.step-list { max-height: 300px; overflow-y: auto; }
.step-row {
  display: flex; align-items: center; gap: 8px; padding: 4px 8px;
  border-radius: 4px; cursor: pointer; font-family: var(--vp-font-family-mono); font-size: 12px;
}
.step-row:hover { background: var(--vp-c-bg); }
.step-row.current { background: var(--vp-c-brand-soft); }
.step-row.bounce { border-left: 3px solid #f59e0b; }
.step-row.deep { border-left: 3px solid #22c55e; }
.step-row.strong { border-left: 3px solid #16a34a; }

.s-idx { width: 24px; color: var(--vp-c-text-3); font-size: 11px; }
.s-bits { width: 36px; }
.s-depth { width: 36px; }
.s-depth.deep { color: #16a34a; font-weight: 600; }
.s-depth.strong { color: #15803d; font-weight: 700; }
.s-type { width: 60px; font-size: 11px; }
.step-row.bounce .s-type { color: #d97706; font-weight: 600; }
.step-row.deep .s-type { color: #16a34a; }
.step-row.strong .s-type { color: #15803d; font-weight: 600; }

.s-bar-container { flex: 1; height: 6px; background: var(--vp-c-bg-soft); border-radius: 3px; }
.s-bar { height: 100%; border-radius: 3px; transition: width 0.3s; }
.s-bar.consumed { background: linear-gradient(90deg, #fbbf24, #ef4444); }

.insight { margin-top: 12px; padding: 12px; background: #fef3c7; border-radius: 8px; color: #92400e; font-size: 14px; }
</style>
