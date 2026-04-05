<script setup lang="ts">
import { ref } from 'vue'

const expandedRow = ref<number | null>(null)

const rows = [
  {
    physics: 'Speed of light c',
    collatz: 'Carry propagation: 1.92 bits/bounce',
    detail: 'The ×3 operation propagates carries through the binary representation at rate log₂(3) ≈ 1.58 bits per multiplication. Over a bounce cycle (~4 multiplications): the active bit window shifts by ≥ 1.92 positions. Nothing can outrun this speed.'
  },
  {
    physics: 'Particle velocity v < c',
    collatz: 'Orbit growth: 0.51 bits/bounce',
    detail: 'The orbit grows at rate 9/8 per weak drop, adding ~0.17 bits per step. Over a bounce cycle: ~0.51 new bits. This is the "velocity" of information generation — always less than the "speed of light" (1.92).'
  },
  {
    physics: 'Finite energy E = mc²',
    collatz: 'Finite binary expansion: B bits',
    detail: 'A natural number like 76,827 has exactly 17 bits of information. Beyond bit 17: all zeros. This finite "energy" is what distinguishes natural numbers from 2-adic integers (which have infinite bits).'
  },
  {
    physics: 'Event horizon',
    collatz: 'Position B: all zeros beyond',
    detail: 'At the edge of the number\'s binary expansion, all bits are 0. When the carry propagation\'s reading window crosses this boundary, it encounters only zeros. The bounce condition (which needs specific nonzero patterns) fails.'
  },
  {
    physics: 'Hawking radiation',
    collatz: '~0.51 new bits per bounce from growth',
    detail: 'The orbit\'s growth generates a trickle of new bits — like Hawking radiation slowly leaking from a black hole. But the rate (0.51) is too slow to prevent the eventual exhaustion of the bit budget.'
  },
  {
    physics: 'Heat death of universe',
    collatz: 'Bit budget exhausted → orbit collapses',
    detail: 'When the reading window has consumed all B bits and the growth can\'t keep up: the bounce sequence terminates, a deep drop occurs, and the orbit begins its final descent to 1. Inevitable thermodynamic collapse.'
  },
  {
    physics: 'Trivial zeros of ζ(s)',
    collatz: '2-adic cycles at negative integers',
    detail: 'The 2-adic Collatz cycles (at -1, -1/3, etc.) are "trivial" solutions — they exist in the infinite-precision world of Z₂ but not among natural numbers. Like the trivial zeros of the Riemann zeta function at negative even integers, they\'re structurally forced by symmetry.'
  },
]
</script>

<template>
  <div class="physics-analogy">
    <div
      v-for="(row, i) in rows"
      :key="i"
      class="analogy-row"
      :class="{ expanded: expandedRow === i }"
      @click="expandedRow = expandedRow === i ? null : i"
    >
      <div class="row-header">
        <div class="col physics">{{ row.physics }}</div>
        <div class="col arrow">↔</div>
        <div class="col collatz">{{ row.collatz }}</div>
        <div class="col expand">{{ expandedRow === i ? '−' : '+' }}</div>
      </div>
      <div v-if="expandedRow === i" class="row-detail">
        {{ row.detail }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.physics-analogy {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  margin: 16px 0;
  overflow: hidden;
}

.analogy-row {
  border-bottom: 1px solid var(--vp-c-divider);
  cursor: pointer;
  transition: background 0.15s;
}
.analogy-row:last-child { border-bottom: none; }
.analogy-row:hover { background: var(--vp-c-bg-soft); }
.analogy-row.expanded { background: var(--vp-c-bg-soft); }

.row-header {
  display: flex; align-items: center; padding: 12px 16px; gap: 12px;
}

.col { font-size: 14px; }
.col.physics { flex: 1; font-weight: 600; color: var(--vp-c-brand-1); }
.col.arrow { color: var(--vp-c-text-3); font-size: 16px; }
.col.collatz { flex: 1; color: var(--vp-c-text-1); }
.col.expand { width: 20px; text-align: center; font-size: 18px; color: var(--vp-c-text-3); }

.row-detail {
  padding: 0 16px 14px 16px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--vp-c-text-2);
}
</style>
