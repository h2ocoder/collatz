<template>
  <div class="bridge">
    <div class="controls">
      <div class="row">
        <label>
          Slope α
          <input type="range" v-model.number="slope" min="1.0" max="4.5" step="0.0005" />
          <span class="value">{{ slope.toFixed(4) }}</span>
        </label>
        <span class="preset-row">
          <button :class="{ active: nearEq(slope, LOG2_3) }" @click="slope = LOG2_3">
            3x+1 (log₂3)
          </button>
          <button :class="{ active: nearEq(slope, LOG2_5) }" @click="slope = LOG2_5">
            5x+1 (log₂5)
          </button>
          <button :class="{ active: nearEq(slope, LOG2_7) }" @click="slope = LOG2_7">
            7x+1 (log₂7)
          </button>
          <button :class="{ active: nearEq(slope, LOG2_9) }" @click="slope = LOG2_9">
            9x+1 (log₂9)
          </button>
        </span>
        <span class="preset-row">
          <button :class="{ active: nearEq(slope, GOLDEN) }" @click="slope = GOLDEN">
            φ
          </button>
          <button :class="{ active: nearEq(slope, 1.5) }" @click="slope = 1.5">
            3/2
          </button>
          <button :class="{ active: nearEq(slope, 19/12) }" @click="slope = 19/12">
            19/12
          </button>
        </span>
      </div>
      <div class="row">
        <label>
          Steps shown (o = 1..N)
          <input type="range" v-model.number="oMax" min="6" max="60" step="1" />
          <span class="value">N = {{ oMax }}</span>
        </label>
        <label>
          Focus on o
          <input type="range" v-model.number="focusO" min="1" :max="oMax" step="1" />
          <span class="value">o = {{ focusO }}</span>
        </label>
      </div>
    </div>

    <div class="panels">
      <!-- Panel A: cutting sequence in the grid -->
      <div class="panel">
        <h4>A. The cutting line — symbolic dynamics of slope α</h4>
        <p class="caption">
          Walk along the line $y = \alpha x$ through a unit grid. Mark a
          <span class="dot-x"></span> at each vertical-line crossing,
          a <span class="dot-y"></span> at each horizontal-line crossing.
          The sequence of crossings <em>is</em> the Sturmian word.
        </p>
        <svg :viewBox="`0 0 ${gridW} ${gridH}`" class="grid-svg">
          <!-- grid lines -->
          <g class="grid-lines">
            <line v-for="i in xLines" :key="'v'+i"
                  :x1="xToPx(i)" :y1="0" :x2="xToPx(i)" :y2="gridH" />
            <line v-for="i in yLines" :key="'h'+i"
                  :x1="0" :y1="yToPx(i)" :x2="gridW" :y2="yToPx(i)" />
          </g>
          <!-- the slope line -->
          <line :x1="xToPx(0)" :y1="yToPx(0)"
                :x2="xToPx(gridXMax)" :y2="yToPx(gridXMax * slope)"
                class="cut-line" />
          <!-- horizontal crossings (the "gap" markers) -->
          <circle v-for="m in horizCrossings" :key="'h'+m.y"
                  :cx="xToPx(m.y / slope)" :cy="yToPx(m.y)" :r="3.5"
                  :class="m.highlight ? 'dot-y-marker hi' : 'dot-y-marker'" />
          <!-- vertical crossings (integer o values) -->
          <circle v-for="m in vertCrossings" :key="'v'+m.x"
                  :cx="xToPx(m.x)" :cy="yToPx(m.x * slope)" :r="4"
                  :class="m.highlight ? 'dot-x-marker hi' : 'dot-x-marker'" />
          <text v-for="m in vertCrossings.filter(v => v.x <= 8)" :key="'lbl'+m.x"
                :x="xToPx(m.x) + 5" :y="yToPx(m.x * slope) - 5"
                class="vert-label">o={{ m.x }}</text>
        </svg>
      </div>

      <!-- Panel B: Beatty sequence on a number line -->
      <div class="panel">
        <h4>B. The dropping schedule — Beatty sequence k_o = o + ⌊oα⌋ + 1</h4>
        <p class="caption">
          Dropping times marched out on the integers. Each interval between
          consecutive k_o is colored by its gap size:
          <span class="legend gap2"></span> shorter gap ({{ Math.floor(slope) + 1 }}),
          <span class="legend gap3"></span> longer gap ({{ Math.floor(slope) + 2 }}).
        </p>
        <svg :viewBox="`0 0 ${beattyW} ${beattyH}`" class="beatty-svg">
          <!-- baseline -->
          <line :x1="20" :y1="beattyH * 0.55" :x2="beattyW - 20"
                :y2="beattyH * 0.55" stroke="#888" stroke-width="1" />
          <!-- intervals (between k_{o-1} and k_o) -->
          <rect v-for="(seg, i) in beattySegments" :key="i"
                :x="kToPx(seg.from)" :y="beattyH * 0.55 - 6"
                :width="kToPx(seg.to) - kToPx(seg.from)" :height="12"
                :class="seg.gap === Math.floor(slope) + 2 ? 'gap3' : 'gap2'"
                :opacity="seg.highlight ? 1 : 0.55" />
          <!-- k_o markers -->
          <circle v-for="m in beattyPoints" :key="'k'+m.o"
                  :cx="kToPx(m.k)" :cy="beattyH * 0.55" :r="m.highlight ? 6 : 3.5"
                  :class="m.highlight ? 'k-marker hi' : 'k-marker'" />
          <!-- tick marks for selected k values -->
          <g class="k-labels">
            <text v-for="m in beattyPoints.filter((_, i) => i < 12)" :key="'lblk'+m.o"
                  :x="kToPx(m.k)" :y="beattyH * 0.85"
                  text-anchor="middle">k={{ m.k }}</text>
          </g>
        </svg>
      </div>

      <!-- Panel C: rotation on the unit interval -->
      <div class="panel">
        <h4>C. The rotation — {(o−1)α} on [0, 1)</h4>
        <p class="caption">
          For each o, compute the fractional part of (o−1)α and plot it on
          the unit interval. The threshold τ = ⌈α⌉ − α
          (<strong>{{ threshold.toFixed(4) }}</strong>) splits the points:
          <span class="legend gap2"></span> below τ ⟹ shorter gap,
          <span class="legend gap3"></span> above τ ⟹ longer gap.
        </p>
        <svg :viewBox="`0 0 ${rotW} ${rotH}`" class="rotation-svg">
          <line :x1="20" :y1="rotH * 0.5" :x2="rotW - 20" :y2="rotH * 0.5"
                stroke="#888" stroke-width="1" />
          <!-- threshold marker -->
          <line :x1="tToPx(threshold)" :y1="rotH * 0.2"
                :x2="tToPx(threshold)" :y2="rotH * 0.8"
                stroke="#e67e22" stroke-width="2" stroke-dasharray="4,3" />
          <text :x="tToPx(threshold)" :y="rotH * 0.16"
                text-anchor="middle" fill="#e67e22" font-size="11">
            τ = {{ threshold.toFixed(3) }}
          </text>
          <!-- 0 and 1 labels -->
          <text :x="20" :y="rotH * 0.78" font-size="11" fill="#666">0</text>
          <text :x="rotW - 20" :y="rotH * 0.78" font-size="11" fill="#666"
                text-anchor="end">1</text>
          <!-- rotation points -->
          <g>
            <circle v-for="p in rotationPoints" :key="'r'+p.o"
                    :cx="tToPx(p.frac)" :cy="rotH * 0.5"
                    :r="p.highlight ? 6 : 3.5"
                    :class="(p.frac >= threshold ? 'gap3-pt' : 'gap2-pt') + (p.highlight ? ' hi' : '')" />
          </g>
          <!-- highlighted o label -->
          <text :x="tToPx(rotationPoints.find(p => p.highlight)?.frac ?? 0)"
                :y="rotH * 0.28" text-anchor="middle" font-size="11"
                fill="var(--vp-c-text-1)">
            o = {{ focusO }}
          </text>
        </svg>
      </div>

      <!-- Panel D: Sturmian word strip -->
      <div class="panel">
        <h4>D. The Sturmian word — the gap sequence itself</h4>
        <p class="caption">
          One cell per o, colored by the gap value gap_o = k_o − k_{o−1}.
          This is the binary sequence rendered as the
          <a href="/explore/sturmian-fractals">fractal turtle</a> on the
          other page.
        </p>
        <div class="word-strip">
          <div v-for="(g, i) in gapSequence" :key="i"
               :class="['cell', g === Math.floor(slope) + 2 ? 'gap3' : 'gap2', { hi: i + 1 === focusO }]"
               :title="`o=${i+1}, gap=${g}`">
            {{ g }}
          </div>
        </div>
      </div>
    </div>

    <!-- Information panel tying everything to Collatz -->
    <div class="connect">
      <h4>
        At o = {{ focusO }}, every view points to the same datum
        <span v-if="qSystem !== null" class="badge">
          {{ qSystem }}x+1 system
        </span>
      </h4>
      <div class="connect-grid">
        <div class="connect-cell">
          <div class="cell-title">Rotation point</div>
          <div class="cell-val">{{ ((focusO - 1) * slope % 1).toFixed(4) }}</div>
          <div class="cell-sub">
            {{ (focusO - 1) * slope % 1 >= threshold ? 'above' : 'below' }} τ
          </div>
        </div>
        <div class="connect-cell">
          <div class="cell-title">Dropping time k_o</div>
          <div class="cell-val">{{ kFor(focusO) }}</div>
          <div class="cell-sub">k = o + ⌊oα⌋ + 1</div>
        </div>
        <div class="connect-cell">
          <div class="cell-title">Gap from previous</div>
          <div class="cell-val">{{ gapFor(focusO) }}</div>
          <div class="cell-sub">
            ⟹ Sturmian sign
            <strong>{{ gapFor(focusO) === Math.floor(slope) + 2 ? '+' : '−' }}</strong>
          </div>
        </div>
        <div class="connect-cell">
          <div class="cell-title">Dropping class size |R<sub>k</sub>|</div>
          <div class="cell-val">
            {{ knownRkSize(kFor(focusO), qSystem) ?? '—' }}
          </div>
          <div class="cell-sub">
            residues mod 2<sup>k</sup> that drop at step k
          </div>
        </div>
      </div>

      <div class="explain">
        <p v-if="qSystem === 3">
          <strong>3x+1 (Collatz):</strong> the cutting sequence of slope
          log₂3 is the Collatz dropping schedule. At each o, the sign
          {{ gapFor(focusO) === Math.floor(slope) + 2 ? '+1' : '−1' }} predicted by the
          gap is exactly the sign of the χ<sub>6</sub> L-function partial
          sum on <em>this</em> dropping class — by the
          <a href="/connections/sturmian-l-probe">closed-form theorem</a>.
          The dropping class itself contains
          {{ knownRkSize(kFor(focusO), qSystem) ? knownRkSize(kFor(focusO), qSystem)!.toLocaleString() : 'many' }}
          residues, every one of which traces a Collatz orbit that first
          drops below its starting value at exactly step k = {{ kFor(focusO) }}.
        </p>
        <p v-else-if="qSystem !== null">
          <strong>{{ qSystem }}x+1 cousin:</strong> the Sturmian schedule
          extends — same Beatty machinery, slope log₂{{ qSystem }}, gaps in
          {<strong>{{ Math.floor(slope) + 1 }}, {{ Math.floor(slope) + 2 }}</strong>}.
          What differs from Collatz is the Terras identity: for {{ qSystem }}x+1
          the sum Σ |R_k|/2^k falls short of 1, and the gap is the
          2-adic density of cycle-residues + divergent orbits. For 5x+1
          there are known cycles starting at 13 and 17; verified by
          <a href="https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Dropping%20Zeta%20Spectrum.md">Part 10</a>.
        </p>
        <p v-else-if="isRational(slope)">
          <strong>Rational slope</strong> ⟹ the gap sequence eventually
          repeats with period q. This is the Cobham-automatic regime from
          <a href="https://github.com/h2ocoder/collatz/blob/main/docs/Explorations/Dropping%20Zeta%20Spectrum.md">Part 9</a>
          — at q-th level the Beatty structure becomes finite-state.
          Compare with α = log₂3 for the irrational case.
        </p>
        <p v-else>
          <strong>This slope isn't directly Collatz</strong> — only α = log₂q
          for odd q corresponds to a qx+1 system. But the Sturmian structure
          is the same for every irrational slope. φ gives the Fibonacci word;
          log₂3 gives the Collatz dropping rule. Click a qx+1 preset above
          to snap to a Collatz-cousin slope.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const LOG2_3 = Math.log2(3)
const LOG2_5 = Math.log2(5)
const LOG2_7 = Math.log2(7)
const LOG2_9 = Math.log2(9)
const GOLDEN = (1 + Math.sqrt(5)) / 2

const slope = ref(LOG2_3)
const oMax = ref(18)
const focusO = ref(7)

// Generalised Sturmian threshold τ = ⌈α⌉ - α  (fractional complement)
const threshold = computed(() => Math.ceil(slope.value) - slope.value)

function nearEq(a: number, b: number, eps = 1e-4) { return Math.abs(a - b) < eps }
function isRational(x: number) {
  return nearEq(x, 1.5) || nearEq(x, 19 / 12) || nearEq(x, 8 / 5)
}

// Detect which qx+1 system this slope corresponds to, if any
function matchedQ(s: number): number | null {
  for (const q of [3, 5, 7, 9]) {
    if (nearEq(s, Math.log2(q))) return q
  }
  return null
}

function kFor(o: number): number {
  return o + Math.floor(o * slope.value) + 1
}
function gapFor(o: number): number {
  return o <= 1 ? kFor(1) - 1 : kFor(o) - kFor(o - 1)
}

// |R_k^{(q)}| for q ∈ {3, 5, 7, 9} (q=3 has deep precomputed tables; cousins from scripts/qx_systems_analysis.py)
const RK_TABLE: Record<number, Record<number, number>> = {
  3: {
    1: 1, 3: 2, 6: 4, 8: 16, 11: 48, 13: 224, 16: 768, 19: 3840,
    21: 21760, 24: 88576, 26: 487424, 29: 1968128,
    32: 10653696, 34: 50855936, 37: 261275648, 39: 1278242816,
    42: 6571913216, 44: 30811815936, 47: 154189103104,
    50: 755015057408, 52: 3445824487424, 55: 17035728519168,
  },
  5: { 1: 1, 4: 2, 7: 8, 10: 40, 14: 224, 17: 1792 },
  7: { 1: 1, 4: 2, 8: 8, 12: 56, 16: 480 },
  9: { 1: 1, 5: 2, 9: 12, 13: 96 },
}
function knownRkSize(k: number, q: number | null): number | null {
  if (q === null) return null
  return RK_TABLE[q]?.[k] ?? null
}

// ---------- Panel A: cutting line ----------
const gridW = 360
const gridH = 460
const gridXMax = computed(() => Math.min(12, oMax.value))
const gridYMax = computed(() => Math.floor(gridXMax.value * slope.value) + 2)

function xToPx(x: number) {
  const pad = 20
  return pad + (x / gridXMax.value) * (gridW - 2 * pad)
}
function yToPx(y: number) {
  const pad = 20
  return gridH - pad - (y / gridYMax.value) * (gridH - 2 * pad)
}

const xLines = computed(() => Array.from({ length: gridXMax.value + 1 }, (_, i) => i))
const yLines = computed(() => Array.from({ length: gridYMax.value + 1 }, (_, i) => i))

const vertCrossings = computed(() => {
  const out: { x: number; highlight: boolean }[] = []
  for (let x = 1; x <= gridXMax.value; x++) {
    out.push({ x, highlight: x === focusO.value })
  }
  return out
})
const horizCrossings = computed(() => {
  const out: { y: number; highlight: boolean }[] = []
  for (let y = 1; y <= gridYMax.value; y++) {
    // x where line y = αx hits this horizontal line
    const xAt = y / slope.value
    if (xAt > gridXMax.value) break
    // highlight if this horizontal crossing happens in the interval (focusO-1, focusO]
    const inWindow = xAt > focusO.value - 1 && xAt <= focusO.value
    out.push({ y, highlight: inWindow })
  }
  return out
})

// ---------- Panel B: Beatty number line ----------
const beattyW = 720
const beattyH = 130
const kMax = computed(() => kFor(oMax.value) + 1)

function kToPx(k: number) {
  const pad = 20
  return pad + (k / kMax.value) * (beattyW - 2 * pad)
}

const beattyPoints = computed(() => {
  const out = []
  for (let o = 1; o <= oMax.value; o++) {
    out.push({ o, k: kFor(o), highlight: o === focusO.value })
  }
  return out
})

const beattySegments = computed(() => {
  const out = []
  let prevK = 1  // convention: k_0 = 1
  for (let o = 1; o <= oMax.value; o++) {
    const k = kFor(o)
    out.push({
      from: prevK, to: k, gap: k - prevK,
      highlight: o === focusO.value,
    })
    prevK = k
  }
  return out
})

// ---------- Panel C: rotation ----------
const rotW = 720
const rotH = 130

function tToPx(t: number) {
  const pad = 20
  return pad + t * (rotW - 2 * pad)
}

const rotationPoints = computed(() => {
  const out = []
  for (let o = 1; o <= oMax.value; o++) {
    const frac = ((o - 1) * slope.value) % 1
    out.push({ o, frac, highlight: o === focusO.value })
  }
  return out
})

// ---------- Panel D: word strip ----------
const gapSequence = computed(() => {
  const out: number[] = []
  for (let o = 1; o <= oMax.value; o++) out.push(gapFor(o))
  return out
})

const qSystem = computed(() => matchedQ(slope.value))
</script>

<style scoped>
.bridge {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 16px;
  background: var(--vp-c-bg-soft);
  margin: 16px 0;
}
.controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 14px;
}
.row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
}
.controls label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}
.controls input[type="range"] { width: 220px; }
.value {
  font-weight: bold;
  min-width: 70px;
  font-variant-numeric: tabular-nums;
}
.preset-row {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-left: 8px;
}
.preset-row button {
  padding: 3px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
  font-size: 12px;
  cursor: pointer;
}
.preset-row button.active {
  background: var(--vp-c-brand-soft);
  border-color: var(--vp-c-brand-1);
}

.panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
@media (max-width: 820px) {
  .panels { grid-template-columns: 1fr; }
}

.panel {
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  padding: 10px 12px;
  background: var(--vp-c-bg);
}
.panel h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
}
.caption {
  font-size: 12px;
  color: var(--vp-c-text-2);
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.grid-svg {
  width: 100%;
  max-height: 420px;
  display: block;
}
.grid-lines line {
  stroke: var(--vp-c-divider);
  stroke-width: 0.5;
}
.cut-line {
  stroke: #2c3e50;
  stroke-width: 1.5;
}
.dot-x-marker {
  fill: #3498db;
  stroke: white;
  stroke-width: 0.5;
}
.dot-y-marker {
  fill: #e67e22;
  stroke: white;
  stroke-width: 0.5;
}
.dot-x-marker.hi, .dot-y-marker.hi {
  stroke: #000;
  stroke-width: 2;
  r: 6;
}
.vert-label {
  font-size: 9px;
  fill: var(--vp-c-text-2);
}

.dot-x {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #3498db;
  vertical-align: middle;
}
.dot-y {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e67e22;
  vertical-align: middle;
}

.beatty-svg, .rotation-svg {
  width: 100%;
  height: 130px;
  display: block;
}
rect.gap3 { fill: #3eaf7c; }
rect.gap2 { fill: #e67e22; }
.k-marker {
  fill: #2c3e50;
  stroke: white;
  stroke-width: 1;
}
.k-marker.hi {
  fill: #d62728;
  stroke: #000;
  stroke-width: 2;
}
.k-labels text {
  font-size: 9px;
  fill: var(--vp-c-text-2);
}

.gap3-pt { fill: #3eaf7c; stroke: white; stroke-width: 0.5; }
.gap2-pt { fill: #e67e22; stroke: white; stroke-width: 0.5; }
.gap3-pt.hi, .gap2-pt.hi {
  stroke: #000;
  stroke-width: 2;
  r: 6;
}

.word-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  padding: 4px 0;
}
.cell {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 28px;
  font-size: 12px;
  font-weight: bold;
  color: white;
  border-radius: 3px;
}
.cell.gap3 { background: #3eaf7c; }
.cell.gap2 { background: #e67e22; }
.cell.hi {
  outline: 2px solid #000;
  outline-offset: 1px;
}

.legend {
  display: inline-block;
  width: 14px;
  height: 12px;
  vertical-align: middle;
  border-radius: 2px;
  margin: 0 2px;
}
.legend.gap2 { background: #e67e22; }
.legend.gap3 { background: #3eaf7c; }

.connect {
  margin-top: 14px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  padding: 12px 14px;
  background: var(--vp-c-bg);
}
.connect h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
}
.badge {
  display: inline-block;
  margin-left: 8px;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: normal;
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  border-radius: 10px;
}
.connect-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}
@media (max-width: 820px) {
  .connect-grid { grid-template-columns: 1fr 1fr; }
}
.connect-cell {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 5px;
  padding: 8px 10px;
  text-align: center;
}
.cell-title {
  font-size: 11px;
  color: var(--vp-c-text-3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.cell-val {
  font-size: 20px;
  font-weight: bold;
  font-variant-numeric: tabular-nums;
  color: var(--vp-c-text-1);
  margin: 2px 0;
}
.cell-sub {
  font-size: 11px;
  color: var(--vp-c-text-2);
}

.explain {
  margin-top: 10px;
  font-size: 13px;
  line-height: 1.55;
  color: var(--vp-c-text-1);
}
.explain p { margin: 0; }
.explain a { color: var(--vp-c-brand-1); }
</style>
