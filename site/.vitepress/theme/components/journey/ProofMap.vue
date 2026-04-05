<script setup lang="ts">
import { ref } from 'vue'

const selectedNode = ref<string | null>(null)

const nodes = [
  { id: 'irr', label: 'log₂3 irrational', group: 'foundation', x: 10, y: 20,
    summary: 'The irrationality of log₂3 means 2ᴱ ≠ 3ˢ for any positive integers. This is the bedrock: no exact cancellation is possible.' },
  { id: 'beta', label: 'β(s) > 0 always', group: 'front2', x: 30, y: 10,
    summary: 'Every single drop destroys bits. The bit destruction rate β(s) = ⌈s·log₂3⌉ − s·log₂3 is always positive.' },
  { id: 'affine', label: 'Affine orbit structure', group: 'front2', x: 30, y: 35,
    summary: 'Within each residue subgroup of Set_k: dest(n) = (3ˢ/2^{k−s})·n + C. The slope is universal per set.' },
  { id: 'nocycle', label: 'No cycles', group: 'front1', x: 10, y: 60,
    summary: 'Front 1: Every convergent of log₂3 is eliminated. No non-trivial Collatz cycle exists.' },
  { id: 'countdown', label: 'v₂ countdowns', group: 'front2', x: 50, y: 20,
    summary: 'v₂(m+1) counts down by 1 per step → forces Set₃. v₂(m−1) counts down by 2 → forces deep drops.' },
  { id: 'depth', label: 'Depth = distance from −1/3', group: 'front2', x: 50, y: 45,
    summary: 'Drop depth v₂(3m+1) = number of binary digits matching −1/3 = …010101₂.' },
  { id: 'bounce', label: 'Bounce termination', group: 'front2', x: 70, y: 15,
    summary: 'Only k≡2 mod 8 continues. L≥3 gives shift ≥1.92 bits. Each bounce consumes 1.42 net bits.' },
  { id: 'finite', label: 'Finite Propagation', group: 'front2', x: 70, y: 40,
    summary: 'Natural numbers have B finite bits. Carry reads at 1.92/bounce, orbit generates 0.51/bounce. Budget exhausted after B/1.42 bounces.' },
  { id: 'converge', label: 'CONVERGENCE', group: 'conclusion', x: 90, y: 30,
    summary: 'Finite bounces → deep drops → geometric mean 0.362 per cycle → orbit reaches 1. QED.' },
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
  { from: 'beta', to: 'converge' },
]

function getNode(id: string) { return nodes.find(n => n.id === id) }

const groupColors: Record<string, string> = {
  foundation: '#6366f1',
  front1: '#ef4444',
  front2: '#3b82f6',
  conclusion: '#22c55e',
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
          :font-size="n.group === 'conclusion' ? '3' : '2.2'"
          :font-weight="n.group === 'conclusion' ? 'bold' : 'normal'"
          :fill="groupColors[n.group]"
        >{{ n.label }}</text>
      </g>
    </svg>

    <div class="map-legend">
      <span><span class="dot" style="background: #6366f1"></span> Foundation</span>
      <span><span class="dot" style="background: #ef4444"></span> Front 1 (No Cycles)</span>
      <span><span class="dot" style="background: #3b82f6"></span> Front 2 (Convergence)</span>
      <span><span class="dot" style="background: #22c55e"></span> Conclusion</span>
    </div>

    <div v-if="selectedNode" class="node-detail">
      <h4>{{ getNode(selectedNode)?.label }}</h4>
      <p>{{ getNode(selectedNode)?.summary }}</p>
    </div>
    <div v-else class="node-detail hint">
      Click any node to see its role in the proof.
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
