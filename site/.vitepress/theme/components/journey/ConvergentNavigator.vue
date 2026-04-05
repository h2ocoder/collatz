<script setup lang="ts">
import { ref, computed } from 'vue'
import { LOG2_3 } from '../../utils/collatz'

// Convergents of log2(3) from its continued fraction [1; 1, 1, 2, 2, 3, 1, 5, 2, 23, ...]
const convergents = [
  { p: 1, q: 1, cf: 1 },
  { p: 2, q: 1, cf: 1 },
  { p: 3, q: 2, cf: 1 },
  { p: 8, q: 5, cf: 2 },
  { p: 19, q: 12, cf: 2 },
  { p: 65, q: 41, cf: 3 },
  { p: 84, q: 53, cf: 1 },
  { p: 485, q: 306, cf: 5 },
  { p: 1054, q: 665, cf: 2 },
  { p: 24727, q: 15601, cf: 23 },
]

const selectedIdx = ref(3) // default to (8,5)

const enriched = computed(() => {
  return convergents.map((c, i) => {
    const ratio = c.p / c.q
    const isAscending = ratio < LOG2_3 // p/q < log2(3) means 2^p < 3^q = ascending
    const error = Math.abs(ratio - LOG2_3)
    const K = c.p + c.q

    let status: string
    if (isAscending) {
      status = 'Ascending (auto-eliminated)'
    } else if (c.q <= 5) {
      status = 'Enumerated: no cycle'
    } else if (c.q <= 41) {
      status = 'MITM: no cycle'
    } else {
      status = 'Counting bound: words/gap → 0'
    }

    return {
      ...c,
      idx: i,
      ratio,
      isAscending,
      error,
      K,
      status,
      E: c.p,
      S: c.q,
    }
  })
})

const selected = computed(() => enriched.value[selectedIdx.value])

// For the number line visualization
const zoomLevel = ref(0) // 0 = wide, higher = zoomed in
const zoomCenter = computed(() => LOG2_3)
const zoomRange = computed(() => 0.5 / Math.pow(3, zoomLevel.value))
</script>

<template>
  <div class="conv-nav">
    <div class="number-line">
      <div class="nl-label">log₂3 ≈ {{ LOG2_3.toFixed(10) }}</div>
      <div class="nl-track">
        <div class="nl-target" :style="{ left: '50%' }" title="log₂(3)">
          <div class="nl-target-line"></div>
          <span class="nl-target-label">log₂3</span>
        </div>
        <div
          v-for="c in enriched"
          :key="c.idx"
          class="nl-point"
          :class="{
            ascending: c.isAscending,
            descending: !c.isAscending,
            selected: c.idx === selectedIdx
          }"
          :style="{
            left: Math.max(2, Math.min(98, 50 + (c.ratio - zoomCenter) / zoomRange * 50)) + '%'
          }"
          @click="selectedIdx = c.idx"
          :title="`${c.p}/${c.q} = ${c.ratio.toFixed(6)}`"
        >
          <span class="nl-point-label">{{ c.p }}/{{ c.q }}</span>
        </div>
      </div>
      <div class="nl-controls">
        <button @click="zoomLevel = Math.max(0, zoomLevel - 1)">Zoom Out</button>
        <span>Zoom: {{ zoomLevel }}</span>
        <button @click="zoomLevel = Math.min(6, zoomLevel + 1)">Zoom In</button>
      </div>
    </div>

    <div class="conv-table">
      <div
        v-for="c in enriched"
        :key="c.idx"
        class="conv-row"
        :class="{ selected: c.idx === selectedIdx, ascending: c.isAscending }"
        @click="selectedIdx = c.idx"
      >
        <span class="conv-frac">{{ c.p }}/{{ c.q }}</span>
        <span class="conv-k">K={{ c.K }}</span>
        <span class="conv-type" :class="c.isAscending ? 'asc' : 'desc'">
          {{ c.isAscending ? '↑' : '↓' }}
        </span>
        <span class="conv-status">{{ c.status }}</span>
      </div>
    </div>

    <div v-if="selected" class="detail">
      <h4>Convergent {{ selected.p }}/{{ selected.q }}</h4>
      <table>
        <tr><td>$E$ (even steps)</td><td>{{ selected.E }}</td></tr>
        <tr><td>$S$ (odd steps)</td><td>{{ selected.S }}</td></tr>
        <tr><td>$K = E + S$</td><td>{{ selected.K }}</td></tr>
        <tr><td>$E/S$</td><td>{{ selected.ratio.toFixed(8) }}</td></tr>
        <tr><td>$|\log_2 3 - E/S|$</td><td>{{ selected.error.toExponential(3) }}</td></tr>
        <tr>
          <td>Type</td>
          <td :class="selected.isAscending ? 'asc-text' : 'desc-text'">
            {{ selected.isAscending ? 'Ascending (3ˢ > 2ᴱ)' : 'Descending (2ᴱ > 3ˢ)' }}
          </td>
        </tr>
        <tr>
          <td>Status</td>
          <td><strong>{{ selected.status }}</strong></td>
        </tr>
      </table>
    </div>
  </div>
</template>

<style scoped>
.conv-nav {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}

.number-line { margin-bottom: 16px; }
.nl-label { font-size: 12px; color: var(--vp-c-text-3); margin-bottom: 4px; text-align: center; }

.nl-track {
  position: relative;
  height: 60px;
  background: var(--vp-c-bg);
  border-radius: 8px;
  margin-bottom: 8px;
}

.nl-target { position: absolute; top: 0; height: 100%; transform: translateX(-50%); }
.nl-target-line { width: 2px; height: 100%; background: var(--vp-c-text-1); margin: 0 auto; }
.nl-target-label { position: absolute; bottom: -16px; left: 50%; transform: translateX(-50%); font-size: 10px; font-weight: 600; white-space: nowrap; }

.nl-point {
  position: absolute; top: 50%; transform: translate(-50%, -50%);
  width: 10px; height: 10px; border-radius: 50%; cursor: pointer;
  transition: transform 0.15s;
}
.nl-point:hover { transform: translate(-50%, -50%) scale(1.5); }
.nl-point.ascending { background: #3b82f6; }
.nl-point.descending { background: #ef4444; }
.nl-point.selected { transform: translate(-50%, -50%) scale(2); box-shadow: 0 0 0 3px var(--vp-c-brand-1); }

.nl-point-label {
  position: absolute; bottom: 14px; left: 50%; transform: translateX(-50%);
  font-size: 9px; font-family: var(--vp-font-family-mono); white-space: nowrap;
  display: none;
}
.nl-point:hover .nl-point-label,
.nl-point.selected .nl-point-label { display: block; }

.nl-controls { display: flex; justify-content: center; gap: 12px; align-items: center; }
.nl-controls button { padding: 4px 10px; border: 1px solid var(--vp-c-divider); border-radius: 4px; background: var(--vp-c-bg); cursor: pointer; font-size: 12px; }
.nl-controls span { font-size: 12px; color: var(--vp-c-text-3); }

.conv-table { margin-bottom: 16px; max-height: 200px; overflow-y: auto; }
.conv-row {
  display: flex; gap: 10px; align-items: center; padding: 6px 10px;
  border-radius: 4px; cursor: pointer; font-size: 13px;
}
.conv-row:hover { background: var(--vp-c-bg); }
.conv-row.selected { background: var(--vp-c-brand-soft); }
.conv-row.ascending { opacity: 0.7; }

.conv-frac { font-family: var(--vp-font-family-mono); font-weight: 600; width: 80px; }
.conv-k { font-family: var(--vp-font-family-mono); width: 60px; color: var(--vp-c-text-3); font-size: 12px; }
.conv-type { width: 20px; font-size: 16px; }
.conv-type.asc { color: #3b82f6; }
.conv-type.desc { color: #ef4444; }
.conv-status { font-size: 12px; color: var(--vp-c-text-2); }

.detail { padding: 14px; background: var(--vp-c-bg); border-radius: 8px; }
.detail h4 { margin: 0 0 8px; font-family: var(--vp-font-family-mono); }
.detail table { width: 100%; border-collapse: collapse; }
.detail td { padding: 4px 8px; border-bottom: 1px solid var(--vp-c-divider); font-size: 13px; }
.detail td:first-child { color: var(--vp-c-text-3); width: 45%; }
.detail td:last-child { font-family: var(--vp-font-family-mono); }

.asc-text { color: #3b82f6; }
.desc-text { color: #ef4444; }
</style>
