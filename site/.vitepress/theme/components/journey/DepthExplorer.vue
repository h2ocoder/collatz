<script setup lang="ts">
import { ref, computed } from 'vue'
import { dropDepth, syracuseStep } from '../../utils/collatz'

const inputN = ref(85)
const history = ref<{ m: number; depth: number; bits: string; matchBits: string }[]>([])
const currentIndex = ref(0)

// -1/3 mod 2^20 in binary (the alternating pattern ...010101)
const NEG_THIRD_BITS = '01010101010101010101' // 20 bits of ...010101

function toBin(n: number, width: number): string {
  return n.toString(2).padStart(width, '0')
}

function init() {
  let m = Math.max(3, inputN.value)
  if (m % 2 === 0) m++
  const entries: typeof history.value = []

  for (let i = 0; i < 40 && m > 1; i++) {
    const depth = dropDepth(m)
    const bits = toBin(m, 20)
    // Highlight matching bits with -1/3 pattern (from LSB)
    const bitsRev = bits.split('').reverse()
    const patRev = NEG_THIRD_BITS.split('').reverse()
    let matchCount = 0
    for (let j = 0; j < bitsRev.length; j++) {
      if (bitsRev[j] === patRev[j]) matchCount++
      else break
    }
    const matchBits = bits.split('').map((b, idx) => {
      const fromRight = bits.length - 1 - idx
      return fromRight < matchCount ? 'match' : 'no'
    }).join(',')

    entries.push({ m, depth, bits, matchBits })
    m = syracuseStep(m)
  }
  history.value = entries
  currentIndex.value = 0
}

const current = computed(() => history.value[currentIndex.value])

const matchInfo = computed(() => {
  if (!current.value) return null
  const matches = current.value.matchBits.split(',').filter(x => x === 'match').length
  return { matches, depth: current.value.depth }
})

init()
</script>

<template>
  <div class="depth-explorer">
    <div class="controls">
      <label>
        Start (odd):
        <input type="number" v-model.number="inputN" min="3" step="2" @keydown.enter="init" />
      </label>
      <button @click="init">Reset</button>
      <button @click="currentIndex > 0 && currentIndex--">←</button>
      <button @click="currentIndex < history.length - 1 && currentIndex++">→</button>
    </div>

    <div v-if="current" class="comparison">
      <div class="bit-row">
        <span class="row-label">m =</span>
        <span class="row-value">{{ current.m.toLocaleString() }}</span>
        <div class="bits">
          <span
            v-for="(b, i) in current.bits.split('')"
            :key="'m'+i"
            class="bit"
            :class="{
              match: current.matchBits.split(',')[i] === 'match',
              one: b === '1',
              zero: b === '0'
            }"
          >{{ b }}</span>
        </div>
      </div>
      <div class="bit-row pattern">
        <span class="row-label">−1/3 =</span>
        <span class="row-value">…010101</span>
        <div class="bits">
          <span
            v-for="(b, i) in NEG_THIRD_BITS.split('')"
            :key="'p'+i"
            class="bit pattern-bit"
            :class="{ match: current.matchBits.split(',')[i] === 'match' }"
          >{{ b }}</span>
        </div>
      </div>

      <div class="match-info">
        <div class="match-count">
          <span class="big-num">{{ matchInfo?.matches }}</span>
          <span class="match-label">matching digits (from LSB)</span>
        </div>
        <div class="depth-display">
          <span class="big-num" :class="{ deep: current.depth >= 3, strong: current.depth >= 4 }">
            {{ current.depth }}
          </span>
          <span class="match-label">drop depth = v₂(3m+1)</span>
        </div>
      </div>
    </div>

    <div class="timeline">
      <div
        v-for="(h, i) in history.slice(0, Math.min(history.length, 30))"
        :key="i"
        class="tl-item"
        :class="{ current: i === currentIndex, deep: h.depth >= 3 }"
        @click="currentIndex = i"
      >
        <span class="tl-depth" :class="{ deep: h.depth >= 3, strong: h.depth >= 4 }">{{ h.depth }}</span>
      </div>
    </div>
    <p class="caption">
      Click the depth numbers above to step through the orbit.
      <strong>Deep drops</strong> (green) = more digits matching −1/3.
    </p>
  </div>
</template>

<style scoped>
.depth-explorer {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}
.controls { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 16px; }
.controls input { width: 90px; padding: 6px 10px; border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg); color: var(--vp-c-text-1); }
.controls button { padding: 6px 14px; border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg); cursor: pointer; }
.controls button:hover { background: var(--vp-c-brand-soft); }

.comparison { padding: 14px; background: var(--vp-c-bg); border-radius: 8px; margin-bottom: 12px; }
.bit-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
.row-label { font-size: 13px; color: var(--vp-c-text-3); width: 50px; }
.row-value { font-family: var(--vp-font-family-mono); font-size: 13px; width: 90px; }
.bits { display: flex; gap: 1px; }
.bit {
  width: 16px; height: 22px; display: flex; align-items: center; justify-content: center;
  font-family: var(--vp-font-family-mono); font-size: 12px; border-radius: 2px;
}
.bit.one { background: var(--vp-c-brand-soft); color: var(--vp-c-brand-1); }
.bit.zero { background: var(--vp-c-bg-soft); color: var(--vp-c-text-3); }
.bit.match { background: #bbf7d0 !important; color: #15803d !important; font-weight: 700; }
.bit.pattern-bit { background: var(--vp-c-bg-soft); color: var(--vp-c-text-3); }
.bit.pattern-bit.match { background: #bbf7d0 !important; color: #15803d !important; }

.match-info { display: flex; gap: 30px; margin-top: 12px; }
.match-count, .depth-display { text-align: center; }
.big-num { font-size: 32px; font-weight: 700; font-family: var(--vp-font-family-mono); display: block; }
.big-num.deep { color: #16a34a; }
.big-num.strong { color: #15803d; }
.match-label { font-size: 12px; color: var(--vp-c-text-3); }

.timeline { display: flex; gap: 3px; flex-wrap: wrap; margin-bottom: 8px; }
.tl-item {
  width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;
  border-radius: 4px; cursor: pointer; background: var(--vp-c-bg); transition: transform 0.1s;
}
.tl-item:hover { transform: scale(1.2); }
.tl-item.current { box-shadow: 0 0 0 2px var(--vp-c-brand-1); }
.tl-item.deep { background: #dcfce7; }
.tl-depth { font-family: var(--vp-font-family-mono); font-size: 12px; font-weight: 600; }
.tl-depth.deep { color: #16a34a; }
.tl-depth.strong { color: #15803d; }

.caption { font-size: 12px; color: var(--vp-c-text-3); }
</style>
