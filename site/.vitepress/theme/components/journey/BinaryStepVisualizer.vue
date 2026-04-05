<script setup lang="ts">
import { ref, computed } from 'vue'
import { collatzStep, v2 } from '../../utils/collatz'

const inputN = ref(27)
const history = ref<{ value: number; op: string }[]>([])
const currentIndex = ref(0)

function init() {
  const n = Math.max(2, Math.floor(Number(inputN.value)))
  history.value = [{ value: n, op: 'start' }]
  currentIndex.value = 0
}

function stepForward() {
  const current = history.value[currentIndex.value].value
  if (current <= 1) return
  const next = collatzStep(current)
  const op = current % 2 === 1 ? '×3+1' : '÷2'
  if (currentIndex.value < history.value.length - 1) {
    currentIndex.value++
  } else {
    history.value.push({ value: next, op })
    currentIndex.value = history.value.length - 1
  }
}

function stepBack() {
  if (currentIndex.value > 0) currentIndex.value--
}

function toBits(n: number): { bit: number; pos: number }[] {
  if (n <= 0) return [{ bit: 0, pos: 0 }]
  const bits: { bit: number; pos: number }[] = []
  let pos = 0
  let val = n
  while (val > 0) {
    bits.push({ bit: val & 1, pos })
    val >>= 1
    pos++
  }
  return bits.reverse() // MSB first
}

const currentValue = computed(() => history.value[currentIndex.value]?.value ?? 0)
const currentOp = computed(() => history.value[currentIndex.value]?.op ?? '')
const bits = computed(() => toBits(currentValue.value))
const bitLength = computed(() => bits.value.length)
const isOdd = computed(() => (currentValue.value & 1) === 1)
const isDone = computed(() => currentValue.value <= 1)

const prevValue = computed(() => {
  if (currentIndex.value === 0) return null
  return history.value[currentIndex.value - 1].value
})

// For ×3+1: show the carry chain
const carryPositions = computed(() => {
  if (currentOp.value !== '×3+1' || !prevValue.value) return new Set<number>()
  // The carry from 3n+1: compute 3*prev+1 and find which bit positions had carries
  const prev = prevValue.value
  const result = 3 * prev + 1
  // Simple heuristic: bits that differ between prev and result (shifted)
  const prevBits = toBits(prev)
  const resultBits = toBits(result)
  const carries = new Set<number>()
  // Mark positions where the result has more bits or different bits
  for (let i = 0; i < resultBits.length; i++) {
    const prevIdx = i - (resultBits.length - prevBits.length)
    if (prevIdx < 0 || prevIdx >= prevBits.length || resultBits[i].bit !== prevBits[prevIdx].bit) {
      carries.add(i)
    }
  }
  return carries
})

// For ÷2: highlight the bit being removed
const removedBitPos = computed(() => {
  if (currentOp.value !== '÷2') return -1
  return bits.value.length // last position of previous value
})

init()
</script>

<template>
  <div class="binary-viz">
    <div class="controls">
      <label>
        Start:
        <input type="number" v-model.number="inputN" min="2" max="99999" @keydown.enter="init" />
      </label>
      <button @click="init">Reset</button>
      <button @click="stepBack" :disabled="currentIndex === 0">← Back</button>
      <button @click="stepForward" :disabled="isDone">Step →</button>
    </div>

    <div class="step-info">
      <span class="step-count">Step {{ currentIndex }}</span>
      <span class="op-badge" :class="currentOp">{{ currentOp || 'start' }}</span>
      <span class="value">{{ currentValue.toLocaleString() }}</span>
      <span class="bit-count">{{ bitLength }} bits</span>
    </div>

    <div class="bit-display">
      <div
        v-for="(b, i) in bits"
        :key="i"
        class="bit-cell"
        :class="{
          one: b.bit === 1,
          zero: b.bit === 0,
          carry: carryPositions.has(i),
          lsb: i === bits.length - 1
        }"
      >
        <span class="bit-value">{{ b.bit }}</span>
        <span class="bit-pos">{{ bits.length - 1 - i }}</span>
      </div>
    </div>

    <div class="explanation">
      <template v-if="currentOp === '÷2'">
        <div class="explain-box even">
          <strong>÷2</strong>: Right-shift. The rightmost bit (0) falls off.
          Bit length: {{ bitLength }} → the number <strong>loses a bit</strong>.
        </div>
      </template>
      <template v-else-if="currentOp === '×3+1'">
        <div class="explain-box odd">
          <strong>×3+1</strong>: Multiply by 3 (= shift left + add), then +1.
          The carry chain propagates through consecutive 1-bits.
          Bit length: {{ bitLength }} — grew by at most 1 bit.
        </div>
      </template>
      <template v-else-if="currentOp === 'start'">
        <div class="explain-box start">
          Starting value: <strong>{{ currentValue }}</strong> in binary.
          Click <strong>Step →</strong> to apply the Collatz rule.
        </div>
      </template>
    </div>

    <div class="history-strip">
      <span
        v-for="(h, i) in history.slice(0, currentIndex + 1)"
        :key="i"
        class="history-item"
        :class="{ current: i === currentIndex, odd: h.value % 2 === 1 }"
        @click="currentIndex = i"
      >
        {{ h.value }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.binary-viz {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}

.controls {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 16px;
}

.controls input {
  width: 90px;
  padding: 6px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
}

.controls button {
  padding: 6px 14px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  cursor: pointer;
  font-size: 13px;
}

.controls button:hover:not(:disabled) { background: var(--vp-c-brand-soft); }
.controls button:disabled { opacity: 0.4; cursor: default; }

.step-info {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
  font-family: var(--vp-font-family-mono);
}

.step-count { font-size: 12px; color: var(--vp-c-text-3); }

.op-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.op-badge.×3\+1, .op-badge.\×3\+1 { background: #fee2e2; color: #dc2626; }
.op-badge.÷2 { background: #dcfce7; color: #16a34a; }
.op-badge.start { background: var(--vp-c-brand-soft); color: var(--vp-c-brand-1); }

.value { font-size: 18px; font-weight: 600; }
.bit-count { font-size: 13px; color: var(--vp-c-text-3); }

.bit-display {
  display: flex;
  gap: 2px;
  flex-wrap: wrap;
  margin-bottom: 12px;
  overflow-x: auto;
  padding: 8px 0;
}

.bit-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 28px;
  padding: 6px 4px;
  border-radius: 4px;
  transition: background 0.2s, transform 0.2s;
}

.bit-cell.one {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  font-weight: 700;
}

.bit-cell.zero {
  background: var(--vp-c-bg);
  color: var(--vp-c-text-3);
}

.bit-cell.carry {
  background: #fef3c7;
  transform: scale(1.1);
  box-shadow: 0 0 8px rgba(234, 179, 8, 0.4);
}

.bit-cell.lsb {
  border-bottom: 2px solid var(--vp-c-brand-1);
}

.bit-value {
  font-family: var(--vp-font-family-mono);
  font-size: 16px;
}

.bit-pos {
  font-size: 9px;
  color: var(--vp-c-text-3);
  margin-top: 2px;
}

.explain-box {
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 12px;
}

.explain-box.even { background: #dcfce7; color: #15803d; }
.explain-box.odd { background: #fee2e2; color: #b91c1c; }
.explain-box.start { background: var(--vp-c-bg); color: var(--vp-c-text-2); }

.history-strip {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  padding-top: 8px;
  border-top: 1px solid var(--vp-c-divider);
}

.history-item {
  padding: 2px 6px;
  border-radius: 3px;
  font-family: var(--vp-font-family-mono);
  font-size: 11px;
  cursor: pointer;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-3);
}

.history-item.current {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  font-weight: 600;
}

.history-item.odd { border-left: 2px solid var(--vp-c-brand-1); }
</style>
