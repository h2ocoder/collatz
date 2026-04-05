<script setup lang="ts">
import { ref, computed } from 'vue'
import { droppingTime, stoppingDestination, orbitalOddity, beta } from '../../utils/collatz'

const rangeStart = ref(2)
const rangeSize = ref(100)
const selectedN = ref<number | null>(null)

const SET_COLORS: Record<number, string> = {
  1: '#94a3b8',  // even (grey)
  3: '#22c55e',  // Set_3 (green - fast)
  6: '#3b82f6',  // Set_6 (blue)
  8: '#8b5cf6',  // Set_8 (purple)
  11: '#f59e0b', // Set_11 (amber)
  13: '#ef4444', // Set_13 (red - slow)
  16: '#06b6d4', // Set_16 (cyan)
  19: '#ec4899', // Set_19 (pink)
}

function getSetColor(k: number): string {
  return SET_COLORS[k] || '#6b7280'
}

const numbers = computed(() => {
  const start = Math.max(2, rangeStart.value)
  const result: { n: number; k: number; color: string }[] = []
  for (let n = start; n < start + rangeSize.value && n < start + 200; n++) {
    const k = n % 2 === 0 ? 1 : droppingTime(n)
    result.push({ n, k, color: getSetColor(k) })
  }
  return result
})

const selectedInfo = computed(() => {
  if (!selectedN.value || selectedN.value < 2) return null
  const n = selectedN.value
  const k = n % 2 === 0 ? 1 : droppingTime(n)
  const dest = n % 2 === 0 ? n / 2 : stoppingDestination(n)
  const s = n % 2 === 0 ? 0 : orbitalOddity(n)
  const b = s > 0 ? beta(s) : 1
  const slope = s > 0 ? Math.pow(3, s) / Math.pow(2, k - s) : 0.5
  return { n, k, s, dest, beta: b, slope, isEven: n % 2 === 0 }
})

const setDistribution = computed(() => {
  const counts: Record<number, number> = {}
  let total = 0
  for (const { k } of numbers.value) {
    counts[k] = (counts[k] || 0) + 1
    total++
  }
  return Object.entries(counts)
    .map(([k, count]) => ({ k: Number(k), count, pct: (count / total * 100).toFixed(1) }))
    .sort((a, b) => a.k - b.k)
})
</script>

<template>
  <div class="drop-explorer">
    <div class="controls">
      <label>
        From:
        <input type="number" v-model.number="rangeStart" min="2" max="99900" />
      </label>
      <label>
        Show:
        <input type="range" v-model.number="rangeSize" min="20" max="200" />
        {{ rangeSize }} numbers
      </label>
    </div>

    <div class="number-grid">
      <div
        v-for="item in numbers"
        :key="item.n"
        class="num-cell"
        :style="{ background: item.color + '30', borderColor: item.color }"
        :class="{ selected: selectedN === item.n }"
        @click="selectedN = item.n"
      >
        <span class="num-val">{{ item.n }}</span>
      </div>
    </div>

    <div class="legend">
      <span v-for="{ k, count, pct } in setDistribution" :key="k" class="legend-item">
        <span class="legend-dot" :style="{ background: getSetColor(k) }"></span>
        Set {{ k }} ({{ pct }}%)
      </span>
    </div>

    <div v-if="selectedInfo" class="detail-panel">
      <h4>n = {{ selectedInfo.n }}</h4>
      <template v-if="selectedInfo.isEven">
        <p>Even number. One step: {{ selectedInfo.n }} ÷ 2 = {{ selectedInfo.dest }}.</p>
      </template>
      <template v-else>
        <table>
          <tr><td>Dropping Set</td><td><strong>Set {{ selectedInfo.k }}</strong></td></tr>
          <tr><td>Dropping Time</td><td>{{ selectedInfo.k }} steps</td></tr>
          <tr><td>Odd Steps (s)</td><td>{{ selectedInfo.s }}</td></tr>
          <tr><td>Destination</td><td>{{ selectedInfo.dest }}</td></tr>
          <tr>
            <td>Contraction</td>
            <td>
              3<sup>{{ selectedInfo.s }}</sup>/2<sup>{{ selectedInfo.k - selectedInfo.s }}</sup>
              = {{ selectedInfo.slope.toFixed(4) }}
              <span :style="{ color: selectedInfo.slope < 0.5 ? '#16a34a' : selectedInfo.slope > 0.9 ? '#dc2626' : '#d97706' }">
                ({{ selectedInfo.slope < 0.5 ? 'fast' : selectedInfo.slope > 0.9 ? 'slow!' : 'moderate' }})
              </span>
            </td>
          </tr>
          <tr>
            <td>Bits destroyed (β)</td>
            <td>{{ selectedInfo.beta.toFixed(4) }}</td>
          </tr>
        </table>
      </template>
    </div>
    <div v-else class="detail-panel hint">
      Click any number to see its dropping set properties.
    </div>
  </div>
</template>

<style scoped>
.drop-explorer {
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

.controls input[type="number"] {
  width: 80px;
  padding: 6px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
}

.controls label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.number-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
  margin-bottom: 12px;
}

.num-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 30px;
  border-radius: 4px;
  border: 1.5px solid;
  cursor: pointer;
  transition: transform 0.1s, box-shadow 0.1s;
}

.num-cell:hover {
  transform: scale(1.15);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 1;
}

.num-cell.selected {
  transform: scale(1.2);
  box-shadow: 0 0 0 2px var(--vp-c-brand-1);
}

.num-val {
  font-family: var(--vp-font-family-mono);
  font-size: 11px;
}

.legend {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
  font-size: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

.detail-panel {
  padding: 14px;
  background: var(--vp-c-bg);
  border-radius: 8px;
  font-size: 14px;
}

.detail-panel.hint {
  color: var(--vp-c-text-3);
  font-style: italic;
}

.detail-panel h4 {
  margin: 0 0 8px;
  font-family: var(--vp-font-family-mono);
}

.detail-panel table {
  width: 100%;
  border-collapse: collapse;
}

.detail-panel td {
  padding: 4px 8px;
  border-bottom: 1px solid var(--vp-c-divider);
}

.detail-panel td:first-child {
  color: var(--vp-c-text-3);
  font-size: 13px;
  width: 40%;
}

.detail-panel td:last-child {
  font-family: var(--vp-font-family-mono);
  font-size: 13px;
}
</style>
