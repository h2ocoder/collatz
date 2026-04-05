<script setup lang="ts">
import { ref, computed } from 'vue'
import { v2, collatzStep, dropDepth } from '../../utils/collatz'

const inputN = ref(31)
const history = ref<{ m: number; v2plus: number; v2minus: number; depth: number; isSet3: boolean }[]>([])
const currentIndex = ref(0)

function init() {
  let m = Math.max(3, inputN.value)
  if (m % 2 === 0) m++
  const entries: typeof history.value = []
  for (let i = 0; i < 60 && m > 1; i++) {
    const vp = v2(m + 1)
    const vm = v2(m - 1)
    const d = dropDepth(m)
    const isSet3 = m % 4 === 1
    entries.push({ m, v2plus: vp, v2minus: vm, depth: d, isSet3 })
    // Syracuse step
    let next = 3 * m + 1
    while (next % 2 === 0) next >>= 1
    m = next
  }
  history.value = entries
  currentIndex.value = 0
}

function stepForward() {
  if (currentIndex.value < history.value.length - 1) currentIndex.value++
}
function stepBack() {
  if (currentIndex.value > 0) currentIndex.value--
}

const current = computed(() => history.value[currentIndex.value])
const countdownBars = computed(() => {
  return history.value.slice(0, currentIndex.value + 1).map((h, i) => ({
    ...h,
    index: i,
    isCurrent: i === currentIndex.value
  }))
})

init()
</script>

<template>
  <div class="countdown-viz">
    <div class="controls">
      <label>
        Start (odd):
        <input type="number" v-model.number="inputN" min="3" step="2" @keydown.enter="init" />
      </label>
      <button @click="init">Reset</button>
      <button @click="stepBack" :disabled="currentIndex === 0">←</button>
      <button @click="stepForward" :disabled="currentIndex >= history.length - 1">→</button>
    </div>

    <div v-if="current" class="current-info">
      <div class="info-row">
        <span class="label">m =</span>
        <span class="value mono">{{ current.m.toLocaleString() }}</span>
        <span class="badge" :class="current.isSet3 ? 'set3' : 'nonset3'">
          {{ current.isSet3 ? 'Set₃ (m≡1 mod 4)' : 'm≡3 mod 4' }}
        </span>
      </div>
      <div class="counters">
        <div class="counter">
          <div class="counter-label">v₂(m+1)</div>
          <div class="counter-value">{{ current.v2plus }}</div>
          <div class="counter-bar">
            <div class="bar-fill plus" :style="{ width: Math.min(current.v2plus * 12, 100) + '%' }"></div>
          </div>
          <div class="counter-hint">Counts down → forces Set₃</div>
        </div>
        <div class="counter">
          <div class="counter-label">v₂(m−1)</div>
          <div class="counter-value">{{ current.v2minus }}</div>
          <div class="counter-bar">
            <div class="bar-fill minus" :style="{ width: Math.min(current.v2minus * 12, 100) + '%' }"></div>
          </div>
          <div class="counter-hint">Counts down → forces deep drop</div>
        </div>
        <div class="counter">
          <div class="counter-label">Drop depth</div>
          <div class="counter-value" :class="{ deep: current.depth >= 3, weak: current.depth === 2 }">
            {{ current.depth }}
          </div>
          <div class="counter-bar">
            <div class="bar-fill depth" :style="{ width: Math.min(current.depth * 12, 100) + '%' }"
                 :class="{ deep: current.depth >= 3 }"></div>
          </div>
          <div class="counter-hint">= v₂(3m+1) = bits matching -1/3</div>
        </div>
      </div>
    </div>

    <div class="timeline">
      <div class="timeline-header">
        <span>Step</span><span>v₂(m+1)</span><span>Depth</span>
      </div>
      <div class="timeline-scroll">
        <div
          v-for="bar in countdownBars"
          :key="bar.index"
          class="timeline-row"
          :class="{ current: bar.isCurrent, set3: bar.isSet3 }"
          @click="currentIndex = bar.index"
        >
          <span class="tl-step">{{ bar.index }}</span>
          <div class="tl-bar-container">
            <div class="tl-bar v2p" :style="{ width: bar.v2plus * 8 + 'px' }"></div>
            <span class="tl-val">{{ bar.v2plus }}</span>
          </div>
          <div class="tl-depth" :class="{ deep: bar.depth >= 3, strong: bar.depth >= 4 }">
            {{ bar.depth }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.countdown-viz {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}

.controls {
  display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 16px;
}
.controls input { width: 100px; padding: 6px 10px; border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg); color: var(--vp-c-text-1); font-size: 14px; }
.controls button { padding: 6px 14px; border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg); color: var(--vp-c-text-1); cursor: pointer; font-size: 13px; }
.controls button:hover:not(:disabled) { background: var(--vp-c-brand-soft); }
.controls button:disabled { opacity: 0.4; }

.current-info { margin-bottom: 16px; padding: 14px; background: var(--vp-c-bg); border-radius: 8px; }

.info-row { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.label { color: var(--vp-c-text-3); font-size: 14px; }
.value.mono { font-family: var(--vp-font-family-mono); font-size: 18px; font-weight: 700; }
.badge { padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.badge.set3 { background: #dcfce7; color: #16a34a; }
.badge.nonset3 { background: #fee2e2; color: #dc2626; }

.counters { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.counter { text-align: center; }
.counter-label { font-size: 13px; font-weight: 600; margin-bottom: 4px; font-family: var(--vp-font-family-mono); }
.counter-value { font-size: 28px; font-weight: 700; font-family: var(--vp-font-family-mono); }
.counter-value.deep { color: #16a34a; }
.counter-value.weak { color: #d97706; }
.counter-bar { height: 6px; background: var(--vp-c-bg-soft); border-radius: 3px; margin: 6px 0; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
.bar-fill.plus { background: var(--vp-c-brand-1); }
.bar-fill.minus { background: #8b5cf6; }
.bar-fill.depth { background: #f59e0b; }
.bar-fill.depth.deep { background: #22c55e; }
.counter-hint { font-size: 11px; color: var(--vp-c-text-3); }

.timeline { margin-top: 16px; }
.timeline-header { display: flex; gap: 8px; font-size: 11px; color: var(--vp-c-text-3); text-transform: uppercase; padding: 0 8px 4px; }
.timeline-header span:first-child { width: 40px; }
.timeline-header span:nth-child(2) { flex: 1; }
.timeline-header span:last-child { width: 40px; text-align: center; }

.timeline-scroll { max-height: 250px; overflow-y: auto; }

.timeline-row {
  display: flex; align-items: center; gap: 8px; padding: 3px 8px; border-radius: 4px; cursor: pointer;
  transition: background 0.1s;
}
.timeline-row:hover { background: var(--vp-c-bg); }
.timeline-row.current { background: var(--vp-c-brand-soft); }
.timeline-row.set3 { border-left: 3px solid #22c55e; }

.tl-step { width: 40px; font-size: 11px; color: var(--vp-c-text-3); font-family: var(--vp-font-family-mono); }
.tl-bar-container { flex: 1; display: flex; align-items: center; gap: 6px; }
.tl-bar { height: 10px; border-radius: 3px; background: var(--vp-c-brand-1); transition: width 0.3s; }
.tl-val { font-size: 11px; font-family: var(--vp-font-family-mono); color: var(--vp-c-text-2); }
.tl-depth { width: 40px; text-align: center; font-family: var(--vp-font-family-mono); font-size: 13px; font-weight: 600; border-radius: 4px; padding: 2px; }
.tl-depth.deep { background: #dcfce7; color: #16a34a; }
.tl-depth.strong { background: #bbf7d0; color: #15803d; }
</style>
