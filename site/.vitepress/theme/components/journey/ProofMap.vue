<script setup lang="ts">
import { ref } from 'vue'

const selectedNode = ref<string | null>(null)

const nodes = [
  { id: 'irr', label: 'log₂3 irrational', group: 'known', x: 10, y: 20,
    summary: 'Known. 2ᴱ ≠ 3ˢ for any positive integers, so no exact cancellation between halvings and triplings is possible. Baker’s theory of linear forms in logarithms says how close they can get.' },
  { id: 'beta', label: 'β(s) = 1 − {s·log₂3}', group: 'known', x: 30, y: 10,
    summary: 'Elementary as a bound on the multiplier: in a drop with s odd steps the multiplier 3ˢ/2^(k−s) removes at least β(s) bits, because it is below 1. It removes exactly β(s) in every case checked (n ≤ 10⁷); that it always does would follow from Terras’s coefficient stopping time conjecture, which is open. The number itself loses a little less, because of the +1s. A way to picture drops, not a step toward convergence.' },
  { id: 'affine', label: 'Affine orbit structure', group: 'known', x: 30, y: 35,
    summary: 'Known (Terras 1976, Everett 1977). Within each residue class of Set_k: dest(n) = (3ˢ/2^{k−s})·n + C.' },
  { id: 'nocycle', label: 'No cycles?', group: 'open', x: 10, y: 60,
    summary: 'Open. Small cases are ruled out (Steiner, Eliahou, Simons–de Weger, Hercher), and any nontrivial cycle must be enormous. Nobody has ruled out cycles in general.' },
  { id: 'countdown', label: 'v₂ countdowns', group: 'proved', x: 50, y: 20,
    summary: 'Elementary, shown on the Countdown page. v₂(m+1) counts down by 1 per step → every climb ends at a member of Set₃. v₂(m−1) falls by 2 per weak drop → every run of weak drops ends, in a deep drop if it started even and in a new climb if it started odd. Both are facts about the current value, not about the starting value.' },
  { id: 'depth', label: 'Depth = distance from −1/3', group: 'known', x: 50, y: 45,
    summary: 'Elementary. Drop depth v₂(3m+1) = number of lowest binary digits of m matching −1/3 = …010101₂.' },
  { id: 'bounce', label: 'Bounce statistics', group: 'verified', x: 70, y: 15,
    summary: 'Computed. Counting the Set₃ visits with m ≡ 41 (mod 128) before an orbit’s first deep drop, there are at most (B+3)/4 of them, B being the number of bits of m, for every odd m ≤ 5×10⁶. Over a whole orbit the count can exceed that (m = 2919). No bound is proved.' },
  { id: 'finite', label: 'Finite fuel', group: 'heuristic', x: 70, y: 40,
    summary: 'Heuristic. The picture charges each bounce 1.92 bits read against 0.51 bits of growth. These are bookkeeping constants, not measured averages, and whether any such accounting holds along every orbit is open.' },
  { id: 'converge', label: 'All reach 1?', group: 'open', x: 90, y: 30,
    summary: 'Open. This is the Collatz conjecture. Nothing on this site proves it.' },
]

const edges = [
  { from: 'irr', to: 'beta' },
  { from: 'irr', to: 'nocycle' },
  { from: 'beta', to: 'countdown' },
  { from: 'affine', to: 'countdown' },
  { from: 'affine', to: 'depth' },
  { from: 'countdown', to: 'bounce' },
  { from: 'depth', to: 'bounce' },
  { from: 'bounce', to: 'finite' },
  { from: 'finite', to: 'converge' },
  { from: 'nocycle', to: 'converge' },
]

function getNode(id: string) { return nodes.find(n => n.id === id) }

const groupColors: Record<string, string> = {
  known: '#6366f1',
  proved: '#22c55e',
  verified: '#3b82f6',
  heuristic: '#f59e0b',
  open: '#ef4444',
}
</script>

<template>
  <div class="proof-map">
    <svg viewBox="0 0 100 70" class="map-svg">
      <!-- Edges -->
      <line
        v-for="(e, i) in edges"
        :key="'e'+i"
        :x1="getNode(e.from)!.x" :y1="getNode(e.from)!.y"
        :x2="getNode(e.to)!.x" :y2="getNode(e.to)!.y"
        stroke="#d1d5db" stroke-width="0.3"
      />
      <!-- Nodes -->
      <g
        v-for="n in nodes"
        :key="n.id"
        :transform="`translate(${n.x}, ${n.y})`"
        @click="selectedNode = selectedNode === n.id ? null : n.id"
        style="cursor: pointer"
      >
        <circle
          r="3"
          :fill="groupColors[n.group]"
          :stroke="selectedNode === n.id ? '#000' : 'none'"
          stroke-width="0.4"
        />
        <text
          y="-4" text-anchor="middle"
          :font-size="n.id === 'converge' ? '2.6' : '2.2'"
          :font-weight="n.id === 'converge' ? 'bold' : 'normal'"
          :fill="groupColors[n.group]"
        >{{ n.label }}</text>
      </g>
    </svg>

    <div class="map-legend">
      <span><span class="dot" style="background: #6366f1"></span> Known mathematics</span>
      <span><span class="dot" style="background: #22c55e"></span> Proved here (elementary)</span>
      <span><span class="dot" style="background: #3b82f6"></span> Verified by computation</span>
      <span><span class="dot" style="background: #f59e0b"></span> Heuristic</span>
      <span><span class="dot" style="background: #ef4444"></span> Open</span>
    </div>

    <div v-if="selectedNode" class="node-detail">
      <h4>{{ getNode(selectedNode)?.label }}</h4>
      <p>{{ getNode(selectedNode)?.summary }}</p>
    </div>
    <div v-else class="node-detail hint">
      Click any node to see what it says and how solid it is.
    </div>
  </div>
</template>

<style scoped>
.proof-map {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}

.map-svg { width: 100%; max-height: 300px; background: var(--vp-c-bg); border-radius: 8px; }

.map-legend { display: flex; gap: 14px; flex-wrap: wrap; margin: 10px 0; font-size: 12px; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }

.node-detail { padding: 14px; background: var(--vp-c-bg); border-radius: 8px; }
.node-detail.hint { color: var(--vp-c-text-3); font-style: italic; font-size: 14px; }
.node-detail h4 { margin: 0 0 6px; font-family: var(--vp-font-family-mono); }
.node-detail p { margin: 0; font-size: 14px; line-height: 1.6; }
</style>
