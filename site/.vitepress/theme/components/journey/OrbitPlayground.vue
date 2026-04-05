<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { orbit, collatzStep } from '../../utils/collatz'

const inputValue = ref(27)
const currentOrbit = ref<number[]>([])
const displayedSteps = ref(0)
const isAnimating = ref(false)
let animTimer: ReturnType<typeof setTimeout> | null = null

const maxValue = computed(() => currentOrbit.value.length ? Math.max(...currentOrbit.value.slice(0, displayedSteps.value + 1)) : 0)
const bitLength = computed(() => {
  const val = currentOrbit.value[displayedSteps.value]
  return val ? Math.ceil(Math.log2(val + 1)) : 0
})
const currentValue = computed(() => currentOrbit.value[displayedSteps.value] ?? inputValue.value)
const isOdd = computed(() => (currentValue.value & 1) === 1)
const isDone = computed(() => displayedSteps.value >= currentOrbit.value.length - 1)

function startOrbit() {
  stopAnimation()
  const n = Math.max(2, Math.floor(Number(inputValue.value)))
  currentOrbit.value = orbit(n)
  displayedSteps.value = 0
  animate()
}

function animate() {
  isAnimating.value = true
  animTimer = setTimeout(() => {
    if (displayedSteps.value < currentOrbit.value.length - 1) {
      displayedSteps.value++
      animate()
    } else {
      isAnimating.value = false
    }
  }, Math.min(80, 3000 / currentOrbit.value.length))
}

function stopAnimation() {
  isAnimating.value = false
  if (animTimer) { clearTimeout(animTimer); animTimer = null }
}

function stepForward() {
  stopAnimation()
  if (displayedSteps.value < currentOrbit.value.length - 1) {
    displayedSteps.value++
  }
}

function reset() {
  stopAnimation()
  displayedSteps.value = 0
}

function randomNumber() {
  inputValue.value = Math.floor(Math.random() * 9999) + 2
  startOrbit()
}

// Initialize
startOrbit()
</script>

<template>
  <div class="orbit-playground">
    <div class="controls">
      <label>
        Start:
        <input
          type="number"
          v-model.number="inputValue"
          min="2"
          max="999999"
          @keydown.enter="startOrbit"
        />
      </label>
      <button @click="startOrbit">Go</button>
      <button @click="randomNumber">Random</button>
      <button @click="stepForward" :disabled="isDone">Step</button>
      <button @click="isAnimating ? stopAnimation() : animate()" :disabled="isDone">
        {{ isAnimating ? 'Pause' : 'Play' }}
      </button>
      <button @click="reset">Reset</button>
    </div>

    <div class="stats">
      <div class="stat">
        <span class="stat-label">Current</span>
        <span class="stat-value" :class="{ odd: isOdd, even: !isOdd }">{{ currentValue.toLocaleString() }}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Step</span>
        <span class="stat-value">{{ displayedSteps }} / {{ currentOrbit.length - 1 }}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Bits</span>
        <span class="stat-value">{{ bitLength }}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Peak</span>
        <span class="stat-value">{{ maxValue.toLocaleString() }}</span>
      </div>
    </div>

    <div class="orbit-display">
      <div
        v-for="(val, i) in currentOrbit.slice(0, displayedSteps + 1)"
        :key="i"
        class="orbit-step"
        :class="{
          current: i === displayedSteps,
          odd: val % 2 === 1,
          even: val % 2 === 0,
          reached1: val === 1
        }"
      >
        <span class="step-num">{{ i }}</span>
        <span class="step-val">{{ val.toLocaleString() }}</span>
        <span class="step-arrow" v-if="i < displayedSteps">
          {{ currentOrbit[i] % 2 === 1 ? '×3+1' : '÷2' }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.orbit-playground {
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
  width: 100px;
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
  transition: background 0.15s;
}

.controls button:hover:not(:disabled) {
  background: var(--vp-c-brand-soft);
}

.controls button:disabled {
  opacity: 0.4;
  cursor: default;
}

.stats {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 16px;
  padding: 12px;
  background: var(--vp-c-bg);
  border-radius: 8px;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--vp-c-text-3);
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  font-family: var(--vp-font-family-mono);
}

.stat-value.odd { color: var(--vp-c-brand-1); }
.stat-value.even { color: var(--vp-c-green-1); }

.orbit-display {
  max-height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.orbit-step {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 10px;
  border-radius: 4px;
  font-family: var(--vp-font-family-mono);
  font-size: 13px;
  transition: background 0.15s;
}

.orbit-step.current {
  background: var(--vp-c-brand-soft);
  font-weight: 600;
}

.orbit-step.reached1 {
  background: var(--vp-c-green-soft);
}

.step-num {
  width: 40px;
  text-align: right;
  color: var(--vp-c-text-3);
  font-size: 11px;
}

.step-val {
  min-width: 80px;
}

.orbit-step.odd .step-val { color: var(--vp-c-brand-1); }
.orbit-step.even .step-val { color: var(--vp-c-text-2); }

.step-arrow {
  font-size: 11px;
  color: var(--vp-c-text-3);
  margin-left: auto;
}
</style>
