<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  HALF_PHI,
  MAX_STEPS,
  ROLES,
  distanceFromUniform,
  lucas,
  pentagonOrder,
  residueCounts,
  returnCount,
  walkCounts,
  type Sign,
} from '../utils/pentagon'

const steps = ref(8)
const start = ref(1)
const sign = ref<Sign>(1)

// Switching the rule negates every residue, so keep the start on the same vertex.
watch(sign, () => { start.value = (5 - start.value) % 5 })

const k = computed(() => Math.min(MAX_STEPS, Math.max(0, Math.round(steps.value) || 0)))
const total = computed(() => 2 ** k.value)
const order = computed(() => pentagonOrder(sign.value))
const startVertex = computed(() => order.value.indexOf(start.value))
const isApex = computed(() => startVertex.value === 0)

// The two computations, kept apart: integers pushed through the map, and a walk stepped on a 5-cycle.
const collatz = computed(() => residueCounts(k.value, start.value, sign.value))
const walk = computed(() => walkCounts(k.value, startVertex.value))

const rows = computed(() => order.value.map((residue, v) => ({
  v,
  residue,
  role: ROLES[v],
  isStart: v === startVertex.value,
  count: collatz.value[residue],
  walk: walk.value[v],
  share: collatz.value[residue] / total.value,
  walkShare: walk.value[v] / total.value,
  same: collatz.value[residue] === walk.value[v],
})))

const mismatches = computed(() => rows.value.filter((r) => !r.same).length)
// At k = 0 every start agrees trivially, so nothing is confirmed until a step is taken.
// For k >= 1 the counts agree only from the apex (checked for every start, both rules, k <= 16).
const verdict = computed(() => (k.value === 0 ? 'unmoved' : mismatches.value > 0 ? 'different' : 'same'))

const distance = computed(() => distanceFromUniform(collatz.value))
const rate = computed(() => HALF_PHI ** k.value)

const firstN = computed(() => (start.value === 0 ? 5 : start.value))
const lastN = computed(() => firstN.value + 5 * (total.value - 1))
const ruleName = computed(() => (sign.value === 1 ? '3x+1' : '3x−1'))
const oddBranch = computed(() => (sign.value === 1 ? '(3n+1)/2' : '(3n−1)/2'))

// ---- drawing: a regular pentagon, apex at the top, vertices counter-clockwise ----
const CX = 160
const CY = 156
const R = 100
const RMAX = 30 // disc radius for a share of 1; disc area is proportional to the share
const fix = (x: number) => Number(x.toFixed(1))

const vertices = [0, 1, 2, 3, 4].map((i) => {
  const a = Math.PI / 2 + (2 * Math.PI * i) / 5
  const x = CX + R * Math.cos(a)
  const y = CY - R * Math.sin(a)
  // outer label: residue and role on one line above or below, stacked beside the two side vertices
  const label =
    i === 0 ? { x, y: y - RMAX - 8, anchor: 'middle', stack: false }
    : i === 1 ? { x: x - RMAX - 6, y: y + 2, anchor: 'end', stack: true }
    : i === 4 ? { x: x + RMAX + 6, y: y + 2, anchor: 'start', stack: true }
    : { x, y: y + RMAX + 18, anchor: 'middle', stack: false }
  return {
    x: fix(x),
    y: fix(y),
    lx: fix(label.x),
    ly: fix(label.y),
    anchor: label.anchor,
    stack: label.stack,
    ix: fix(CX + 48 * Math.cos(a)),
    iy: fix(CY - 48 * Math.sin(a)),
  }
})
const outline = vertices.map((p) => `${p.x},${p.y}`).join(' ')
const radius = (share: number) => Number((RMAX * Math.sqrt(share)).toFixed(2))
const diamond = (p: { x: number; y: number }) => `${p.x},${p.y - 6} ${p.x + 6},${p.y} ${p.x},${p.y + 6} ${p.x - 6},${p.y}`

const num = (n: number) => n.toLocaleString('en-US')
const pct = (x: number) => `${(100 * x).toFixed(1)}%`

const summary = computed(() =>
  `Pentagon with residues ${order.value.join(', ')} at its vertices. After ${k.value} steps of ${ruleName.value} from residue ${start.value}: `
  + rows.value.map((r) => `residue ${r.residue} holds ${r.count} of ${total.value} integers, the pentagon walk ${r.walk}`).join('; ') + '.')
</script>

<template>
  <div class="pentagon-walk">
    <div class="controls">
      <label>
        <span>Steps <em>k</em>:</span>
        <input type="range" v-model.number="steps" min="0" :max="MAX_STEPS" step="1" />
        <span class="value">{{ k }}</span>
      </label>
      <label>
        Start residue:
        <select v-model.number="start">
          <option v-for="r in 5" :key="r - 1" :value="r - 1">
            {{ r - 1 }} ({{ ROLES[order.indexOf(r - 1)] }})
          </option>
        </select>
      </label>
      <fieldset class="rule">
        <legend>Rule:</legend>
        <label><input type="radio" name="pentagon-walk-rule" :value="1" v-model="sign" /> 3x+1</label>
        <label><input type="radio" name="pentagon-walk-rule" :value="-1" v-model="sign" /> 3x−1</label>
      </fieldset>
    </div>

    <p class="system-label">
      <template v-if="k === 0">The single integer n = {{ firstN }}, before any step</template>
      <template v-else>
        The <strong>{{ num(total) }}</strong> integers n ≡ {{ start }} (mod 5) from {{ num(firstN) }} to {{ num(lastN) }},
        each pushed through <strong>{{ k }}</strong> {{ k === 1 ? 'step' : 'steps' }}
      </template>
      of T(n) = n/2 or {{ oddBranch }}.
    </p>

    <div class="viz-grid">
      <div class="panel">
        <h4>Where the integers land, mod 5</h4>
        <svg viewBox="0 0 320 296" class="pentagon-svg" role="img" :aria-label="summary">
          <polygon :points="outline" class="side" />
          <g v-for="row in rows" :key="row.v">
            <title>residue {{ row.residue }} ({{ row.role }}): {{ num(row.count) }} of {{ num(total) }} integers, {{ pct(row.share) }}; pentagon walk: {{ num(row.walk) }}</title>
            <circle v-if="row.count > 0" :cx="vertices[row.v].x" :cy="vertices[row.v].y" :r="radius(row.share)" class="disc" />
            <circle v-if="row.walk > 0" :cx="vertices[row.v].x" :cy="vertices[row.v].y" :r="radius(row.walkShare)" class="ring" />
            <polygon v-if="row.isStart" :points="diamond(vertices[row.v])" class="start-pin" />
            <text :x="vertices[row.v].lx" :y="vertices[row.v].ly" :text-anchor="vertices[row.v].anchor">
              <tspan class="residue">{{ row.residue }}</tspan>
              <tspan
                class="role"
                :x="vertices[row.v].stack ? vertices[row.v].lx : undefined"
                :dy="vertices[row.v].stack ? 15 : undefined"
                :dx="vertices[row.v].stack ? undefined : 5"
              >{{ row.role }}</tspan>
            </text>
            <text :x="vertices[row.v].ix" :y="vertices[row.v].iy - 2" text-anchor="middle" class="count">{{ num(row.count) }}</text>
            <text :x="vertices[row.v].ix" :y="vertices[row.v].iy + 12" text-anchor="middle" class="share">{{ pct(row.share) }}</text>
          </g>
        </svg>
        <ul class="legend">
          <li>
            <svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6" class="disc" /></svg>
            <span>T<sup>k</sup>(n) mod 5 (area = share)</span>
          </li>
          <li>
            <svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6" class="ring" /></svg>
            <span>pentagon walk</span>
          </li>
          <li>
            <svg viewBox="0 0 16 16" aria-hidden="true"><polygon points="8,2 14,8 8,14 2,8" class="start-pin" /></svg>
            <span>start</span>
          </li>
        </ul>

        <table class="stats">
          <tbody>
            <tr>
              <td>Distance from uniform</td>
              <td class="n">{{ distance.toFixed(5) }}</td>
            </tr>
            <tr>
              <td>(φ/2)<sup>k</sup> = cos<sup>k</sup> 36°</td>
              <td class="n">{{ rate.toFixed(5) }}</td>
            </tr>
            <tr>
              <td>Ratio of the two (levels off as k grows)</td>
              <td class="n">{{ (distance / rate).toFixed(4) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="panel">
        <h4>Counted two ways</h4>
        <table>
          <thead>
            <tr>
              <th scope="col">Vertex</th>
              <th scope="col">Residue</th>
              <th scope="col" class="n">T<sup>k</sup>(n)</th>
              <th scope="col" class="n">Walk</th>
              <th scope="col"><span class="visually-hidden">Agree?</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.v" :class="{ off: !row.same }">
              <td>{{ row.role }}<span v-if="row.isStart" class="start-tag"> ◆<span class="visually-hidden"> start</span></span></td>
              <td>{{ row.residue }}</td>
              <td class="n">{{ num(row.count) }}</td>
              <td class="n">{{ num(row.walk) }}</td>
              <td class="mark">{{ row.same ? '=' : '≠' }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td colspan="2">total</td>
              <td class="n">{{ num(total) }}</td>
              <td class="n">{{ num(total) }}</td>
              <td></td>
            </tr>
          </tfoot>
        </table>

        <div class="verdict" :class="verdict" role="status" aria-live="polite">
          <template v-if="verdict === 'same'">
            <strong>✓ Same law.</strong>
            After {{ k }} {{ k === 1 ? 'step' : 'steps' }} the integers sit on the residues exactly as a walk on the
            pentagon sits on its vertices, {{ k }} {{ k === 1 ? 'step' : 'steps' }} out from the apex.
          </template>
          <template v-else-if="verdict === 'unmoved'">
            <strong>Nothing has moved yet.</strong>
            At k = 0 both sit on the start. Take one step.
          </template>
          <template v-else>
            <strong>≠ Different laws.</strong>
            From residue {{ start }} the integers do not follow a walk begun on that vertex
            ({{ mismatches }} of 5 vertices disagree). Only the apex start gives the pentagon law, and no
            relabelling of the residues repairs the others.
          </template>
        </div>

        <table v-if="isApex" class="stats">
          <tbody>
            <tr>
              <td>Back at the apex</td>
              <td class="n">{{ num(collatz[start]) }}</td>
            </tr>
            <tr>
              <td>Lucas formula (2<sup>k</sup> {{ k % 2 === 0 ? '+' : '−' }} 2·L<sub>k</sub>)/5, with L<sub>{{ k }}</sub> = {{ num(lucas(k)) }}</td>
              <td class="n">{{ num(returnCount(k)) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <p class="caption">
      Every integer is iterated in your browser; the walk is computed separately, by stepping a five-cycle
      {{ k }} {{ k === 1 ? 'time' : 'times' }} from the start vertex. Distance from uniform is total variation:
      half the sum of |share − 1/5| over the five residues. Its ratio to (φ/2)<sup>k</sup> levels off as k grows,
      from any start; that levelling off is what decay at rate φ/2 means.
    </p>
  </div>
</template>

<style scoped>
.pentagon-walk {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}

.controls {
  display: flex;
  gap: 12px 24px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 12px;
}

.controls label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.controls select {
  padding: 4px 8px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
}

.controls input[type='range'],
.controls input[type='radio'] { accent-color: var(--vp-c-brand-1); }

.value {
  font-weight: bold;
  min-width: 20px;
  font-variant-numeric: tabular-nums;
}

.rule {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 0;
  margin: 0;
  padding: 0;
}

.rule legend {
  float: left;
  padding: 0;
  margin-right: 12px;
  font-size: 14px;
}

.rule label { cursor: pointer; gap: 4px; }

.system-label {
  font-size: 15px;
  line-height: 1.5;
  margin: 0 0 16px;
}

.viz-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 640px) {
  .viz-grid { grid-template-columns: 1fr; }
}

.panel {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 12px;
  background: var(--vp-c-bg);
  min-width: 0;
}

.panel h4 {
  margin: 0 0 8px;
  font-size: 14px;
  color: var(--vp-c-text-2);
}

.pentagon-svg {
  display: block;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.side {
  fill: none;
  stroke: var(--vp-c-divider);
  stroke-width: 1.5;
}

.disc { fill: var(--vp-c-brand-1); }

.ring {
  fill: none;
  stroke: var(--vp-c-text-1);
  stroke-width: 1.5;
}

.start-pin {
  fill: var(--vp-c-text-1);
  stroke: var(--vp-c-bg);
  stroke-width: 1.5;
}

.pentagon-svg text { fill: var(--vp-c-text-1); }
.residue { font-size: 17px; font-weight: 700; }
.role { font-size: 12px; fill: var(--vp-c-text-2); }
.count { font-size: 13px; font-weight: 600; font-variant-numeric: tabular-nums; }
.share { font-size: 11px; fill: var(--vp-c-text-2); font-variant-numeric: tabular-nums; }

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 16px;
  list-style: none;
  margin: 8px 0 0;
  padding: 0;
  font-size: 12px;
  color: var(--vp-c-text-2);
}

.legend li {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
}

.legend svg { width: 16px; height: 16px; flex: none; }

.panel table {
  display: table;
  width: 100%;
  margin: 0 0 12px;
  border-collapse: collapse;
  font-size: 13px;
}

.panel tr {
  background: none;
  border: 0;
  border-top: 1px solid var(--vp-c-divider);
}

.panel thead tr { border-top: 0; }

.panel th,
.panel td {
  border: 0;
  padding: 4px 8px;
  text-align: left;
  background: none;
}

.panel th {
  font-weight: 600;
  color: var(--vp-c-text-2);
}

.panel .n {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.panel tfoot td { color: var(--vp-c-text-2); }
.mark { width: 1.5em; text-align: center; color: var(--vp-c-text-2); }
.off .mark { color: var(--vp-c-text-1); font-weight: 700; }
.off td { background: var(--vp-c-warning-soft); }
.start-tag { color: var(--vp-c-text-1); }

.stats td:first-child { color: var(--vp-c-text-2); }
.panel table.stats { margin: 12px 0 0; }

.verdict {
  margin: 0;
  padding: 10px 12px;
  border-left: 4px solid var(--vp-c-divider);
  border-radius: 0 6px 6px 0;
  font-size: 14px;
  line-height: 1.5;
  background: var(--vp-c-default-soft);
}

.verdict.same {
  border-left-color: var(--vp-c-success-1);
  background: var(--vp-c-success-soft);
}

.verdict.same strong { color: var(--vp-c-success-1); }

.verdict.different {
  border-left-color: var(--vp-c-warning-1);
  background: var(--vp-c-warning-soft);
}

.verdict.different strong { color: var(--vp-c-warning-1); }

.caption {
  font-size: 13px;
  line-height: 1.5;
  color: var(--vp-c-text-2);
  margin: 12px 0 0;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}
</style>
