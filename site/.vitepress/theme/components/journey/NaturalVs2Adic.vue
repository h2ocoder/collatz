<script setup lang="ts">
import { ref, computed } from 'vue'
import { orbit, syracuseStep } from '../../utils/collatz'

const naturalN = ref(27)

// Natural number orbit
const naturalOrbit = computed(() => {
  const orb = orbit(naturalN.value, 200)
  return orb.slice(0, 30)
})

// 2-adic "orbit" of -1/3 (the cycle ...010101 → ...010101)
// -1/3 in Collatz: 3*(-1/3)+1 = 0, but for display we show the pattern
// The 2-adic cycle of -1/3 under Syracuse: it maps to itself
// Actually the non-trivial 2-adic cycles are more complex.
// For simplicity, show the pattern: -1 → -1 → -1 (since 3(-1)+1=-2, -2/2=-1)
const twoadicCycle = computed(() => {
  // The simplest 2-adic cycle: -1 → -1 (since 3(-1)+1 = -2, -2/2 = -1)
  // In binary: ...11111111 = -1
  // Show this as the infinite-bit object
  return [
    { val: '…111111111', label: '-1', step: 0 },
    { val: '…111111110', label: '3(-1)+1 = -2', step: 1 },
    { val: '…111111111', label: '-2/2 = -1', step: 2 },
    { val: '…111111110', label: '3(-1)+1 = -2', step: 3 },
    { val: '…111111111', label: '-2/2 = -1', step: 4 },
  ]
})
</script>

<template>
  <div class="nat-vs-2adic">
    <div class="split">
      <div class="panel natural">
        <h4>Natural Number: {{ naturalN }}</h4>
        <div class="panel-subtitle">{{ naturalN.toString(2).length }} bits, then zeros forever</div>
        <div class="binary-display">
          <span class="bits finite">{{ naturalN.toString(2) }}</span><span class="bits zeros">00000000…</span>
        </div>
        <div class="orbit-mini">
          <span
            v-for="(v, i) in naturalOrbit"
            :key="i"
            class="orbit-val"
            :class="{ reached1: v === 1 }"
          >{{ v }}</span>
          <span v-if="naturalOrbit[naturalOrbit.length-1] === 1" class="converged">✓ Converged!</span>
        </div>
        <div class="verdict good">
          <strong>Finite fuel → bounces terminate → converges to 1</strong>
        </div>
      </div>

      <div class="panel twoadic">
        <h4>2-Adic Integer: -1</h4>
        <div class="panel-subtitle">Infinite 1-bits, never ends</div>
        <div class="binary-display">
          <span class="bits infinite">…111111111111111111111</span>
        </div>
        <div class="orbit-mini">
          <span
            v-for="entry in twoadicCycle"
            :key="entry.step"
            class="orbit-val cycle"
          >{{ entry.label }}</span>
          <span class="cycle-indicator">↺ cycles forever</span>
        </div>
        <div class="verdict bad">
          <strong>Infinite fuel → bounces never terminate → cycles forever</strong>
        </div>
      </div>
    </div>

    <div class="controls">
      <label>
        Natural number:
        <input type="number" v-model.number="naturalN" min="2" max="9999" />
      </label>
    </div>

    <div class="insight">
      <strong>The ONLY difference:</strong> natural numbers have <em>finitely many</em> 1-bits.
      2-adic integers can have <em>infinitely many</em>.
      The carry propagation reads bits at 1.92/bounce but only 0.51 new bits appear.
      Finite numbers run out. Infinite numbers don't.
    </div>
  </div>
</template>

<style scoped>
.nat-vs-2adic {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}

.split { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }

@media (max-width: 640px) {
  .split { grid-template-columns: 1fr; }
}

.panel {
  padding: 16px; border-radius: 8px;
}
.panel.natural { background: #f0fdf4; border: 2px solid #86efac; }
.panel.twoadic { background: #fef2f2; border: 2px solid #fca5a5; }

.panel h4 { margin: 0 0 4px; font-family: var(--vp-font-family-mono); font-size: 15px; }
.panel-subtitle { font-size: 12px; color: var(--vp-c-text-3); margin-bottom: 10px; }

.binary-display { margin-bottom: 10px; font-family: var(--vp-font-family-mono); font-size: 13px; overflow-x: auto; }
.bits.finite { color: var(--vp-c-brand-1); font-weight: 600; }
.bits.zeros { color: #d1d5db; }
.bits.infinite { color: #dc2626; font-weight: 600; }

.orbit-mini { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 10px; }
.orbit-val {
  padding: 2px 5px; border-radius: 3px; font-family: var(--vp-font-family-mono);
  font-size: 11px; background: var(--vp-c-bg); color: var(--vp-c-text-2);
}
.orbit-val.reached1 { background: #bbf7d0; color: #15803d; font-weight: 600; }
.orbit-val.cycle { background: #fee2e2; color: #b91c1c; }
.converged { font-size: 12px; color: #16a34a; font-weight: 600; }
.cycle-indicator { font-size: 12px; color: #dc2626; font-weight: 600; }

.verdict { padding: 8px 12px; border-radius: 6px; font-size: 13px; }
.verdict.good { background: #dcfce7; color: #15803d; }
.verdict.bad { background: #fee2e2; color: #b91c1c; }

.controls { margin-bottom: 12px; }
.controls input { width: 80px; padding: 6px 10px; border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg); color: var(--vp-c-text-1); }

.insight {
  padding: 14px; background: var(--vp-c-bg); border-radius: 8px; font-size: 14px;
  border-left: 4px solid var(--vp-c-brand-1);
}
</style>
