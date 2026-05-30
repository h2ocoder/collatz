<template>
  <div class="fractal-playground">
    <div class="controls">
      <div class="control-row">
        <label>
          Sequence {{ compare ? 'A' : '' }}
          <select v-model="sequenceType">
            <option value="log2_3">log₂3 Sturmian (Collatz dropping sign)</option>
            <option value="fibonacci">Fibonacci word (slope 1/φ)</option>
            <option value="stopping">Stopping-Class parity P_o mod 2</option>
            <option value="rational">Custom rational slope p/q</option>
          </select>
        </label>
        <label v-if="sequenceType === 'rational'">
          p
          <input type="number" v-model.number="customP" min="1" max="500" />
        </label>
        <label v-if="sequenceType === 'rational'">
          q
          <input type="number" v-model.number="customQ" min="1" max="500" />
        </label>
      </div>

      <div v-if="compare" class="control-row">
        <label>
          Sequence B
          <select v-model="sequenceType2">
            <option value="log2_3">log₂3 Sturmian</option>
            <option value="fibonacci">Fibonacci word</option>
            <option value="stopping">Stopping-Class parity</option>
            <option value="rational">Custom rational p/q</option>
          </select>
        </label>
        <label v-if="sequenceType2 === 'rational'">
          p
          <input type="number" v-model.number="customP2" min="1" max="500" />
        </label>
        <label v-if="sequenceType2 === 'rational'">
          q
          <input type="number" v-model.number="customQ2" min="1" max="500" />
        </label>
      </div>

      <div class="control-row">
        <label>
          Turn angle:
          <input type="range" v-model.number="angle" min="3" max="180" step="0.5" />
          <span class="value">{{ angle.toFixed(1) }}°</span>
          <span class="snap-row">
            <button v-for="a in [20, 30, 45, 60, 72, 90, 108, 120, 144]"
                    :key="a"
                    :class="{ 'active-snap': Math.abs(angle - a) < 0.01 }"
                    @click="angle = a">{{ a }}°</button>
          </span>
        </label>
      </div>

      <div class="control-row">
        <label>
          Length:
          <input type="range" v-model.number="logLength"
                 min="6" :max="maxLogLength" step="0.05" />
          <span class="value">{{ length.toLocaleString() }}</span>
          <span class="length-note" v-if="anyStopping">
            (max 16k for Stopping-Class — DP is O(N²))
          </span>
        </label>
      </div>

      <div class="control-row">
        <label>
          Recipe
          <select v-model="recipe">
            <option value="wikipedia">Wikipedia (turn on 0, alt L/R)</option>
            <option value="dragon">Dragon (left on 0, right on 1)</option>
          </select>
        </label>
        <label>
          Mode
          <select v-model="mode">
            <option value="2d">2D</option>
            <option value="3d">3D (drag to rotate)</option>
          </select>
        </label>
        <label>
          Color
          <select v-model="colorMode">
            <option value="time">Time direction</option>
            <option value="heading">Heading axis</option>
            <option value="distance">Distance from origin</option>
            <option value="solid">Solid</option>
          </select>
        </label>
      </div>

      <div class="control-row">
        <label class="toggle">
          <input type="checkbox" v-model="spin" :disabled="mode !== '3d'" />
          Auto-spin
        </label>
        <label class="toggle">
          <input type="checkbox" v-model="compare" />
          Compare A vs B
        </label>
        <button @click="resetView">Reset view</button>
        <button @click="exportPNG" :disabled="exporting">
          {{ exporting ? 'Exporting…' : 'Export PNG 4×' }}
        </button>
      </div>
    </div>

    <div class="canvas-grid" :class="{ comparing: compare }">
      <div class="canvas-wrap" ref="wrapRef">
        <canvas ref="canvasRef"
                @pointerdown="onPointerDown"
                @pointermove="onPointerMove"
                @pointerup="onPointerUp"
                @pointerleave="onPointerUp"
                @wheel.prevent="onWheel" />
        <div class="canvas-label">{{ sequenceLabel(sequenceType, customP, customQ) }}</div>
        <div class="hint" v-if="mode === '3d'">drag · scroll</div>
      </div>
      <div v-if="compare" class="canvas-wrap" ref="wrapRef2">
        <canvas ref="canvasRef2"
                @pointerdown="onPointerDown"
                @pointermove="onPointerMove"
                @pointerup="onPointerUp"
                @pointerleave="onPointerUp"
                @wheel.prevent="onWheel" />
        <div class="canvas-label">{{ sequenceLabel(sequenceType2, customP2, customQ2) }}</div>
        <div class="hint" v-if="mode === '3d'">linked rotation</div>
      </div>
    </div>

    <div class="stats">
      <div><strong>Length:</strong> {{ length.toLocaleString() }} symbols</div>
      <div><strong>+1 density (A):</strong> {{ plusDensity1.toFixed(4) }}</div>
      <div v-if="compare"><strong>+1 density (B):</strong> {{ plusDensity2.toFixed(4) }}</div>
      <div><strong>Bounds:</strong> {{ boundsLabel }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

const LOG2_3 = Math.log2(3)
const PHI_INV = 2 / (1 + Math.sqrt(5))

type SeqType = 'log2_3' | 'fibonacci' | 'stopping' | 'rational'
type Recipe = 'wikipedia' | 'dragon'
type Mode = '2d' | '3d'
type ColorMode = 'time' | 'heading' | 'distance' | 'solid'

// ---------- Reactive state ----------
const sequenceType = ref<SeqType>('log2_3')
const sequenceType2 = ref<SeqType>('stopping')
const customP = ref(19); const customQ = ref(12)
const customP2 = ref(8); const customQ2 = ref(5)
const angle = ref(120)
const logLength = ref(11.5)
const recipe = ref<Recipe>('wikipedia')
const mode = ref<Mode>('2d')
const colorMode = ref<ColorMode>('time')
const compare = ref(false)
const spin = ref(false)
const exporting = ref(false)

const anyStopping = computed(() =>
  sequenceType.value === 'stopping' || (compare.value && sequenceType2.value === 'stopping')
)
const maxLogLength = computed(() => (anyStopping.value ? 14 : 16))
const length = computed(() => Math.round(2 ** logLength.value))

watch(maxLogLength, (m) => { if (logLength.value > m) logLength.value = m })

function sequenceLabel(t: SeqType, p: number, q: number) {
  switch (t) {
    case 'log2_3':   return 'log₂3 Sturmian'
    case 'fibonacci': return 'Fibonacci word'
    case 'stopping':  return 'Stopping-Class parity'
    case 'rational':  return `Rational ${p}/${q}`
  }
  return ''
}

// ---------- Sequence generators ----------
function fibonacciWord(n: number): Int8Array {
  let s: number[] = [0]
  while (s.length < n) {
    const out: number[] = []
    for (const c of s) {
      if (c === 0) { out.push(0); out.push(1) }
      else out.push(0)
    }
    s = out
  }
  return Int8Array.from(s.slice(0, n))
}

function sturmianLog23(n: number): Int8Array {
  const out = new Int8Array(n)
  let prev = 0
  for (let j = 1; j <= n; j++) {
    const f = Math.floor(j * LOG2_3)
    out[j - 1] = f - prev - 1
    prev = f
  }
  return out
}

function sturmianRational(n: number, p: number, q: number): Int8Array {
  const out = new Int8Array(n)
  let prev = 0
  for (let j = 1; j <= n; j++) {
    const f = Math.floor((j * p) / q)
    const diff = f - prev
    // Map (0,1) → 0 and (2,3,...) → 1 for slopes > 1; otherwise keep as-is for slopes in (0,1)
    out[j - 1] = p > q ? Math.max(0, Math.min(1, diff - 1)) : diff
    prev = f
  }
  return out
}

const stoppingCache: { len: number; arr: Int8Array } = { len: 0, arr: new Int8Array() }

function stoppingClassParity(n: number): Int8Array {
  if (stoppingCache.len >= n) return stoppingCache.arr.subarray(0, n)
  const out = new Int8Array(n)
  out[0] = 1
  let f: Uint8Array = new Uint8Array([1])
  let BPrev = 0
  for (let j = 1; j < n; j++) {
    const Bj = Math.floor(j * LOG2_3)
    const cum = new Uint8Array(f.length + 1)
    let x = 0
    for (let i = 0; i < f.length; i++) { x ^= f[i]; cum[i + 1] = x }
    const newF = new Uint8Array(Bj + 1)
    const lo = j - 1
    if (lo <= BPrev) {
      for (let S = j; S <= Bj; S++) {
        const hi = Math.min(BPrev, S - 1)
        if (hi < lo) continue
        newF[S] = cum[hi + 1] ^ cum[lo]
      }
    }
    let parity = 0
    for (let i = 0; i < newF.length; i++) parity ^= newF[i]
    out[j] = parity
    f = newF
    BPrev = Bj
  }
  stoppingCache.len = n
  stoppingCache.arr = out
  return out
}

function generate(t: SeqType, n: number, p: number, q: number): Int8Array {
  switch (t) {
    case 'fibonacci': return fibonacciWord(n)
    case 'log2_3':    return sturmianLog23(n)
    case 'stopping':  return stoppingClassParity(n)
    case 'rational':  return sturmianRational(n, p, q)
  }
  return new Int8Array()
}

const sequence1 = computed(() => generate(sequenceType.value, length.value, customP.value, customQ.value))
const sequence2 = computed(() =>
  compare.value ? generate(sequenceType2.value, length.value, customP2.value, customQ2.value) : null
)

function densityOf(s: Int8Array | null): number {
  if (!s || s.length === 0) return 0
  let c = 0
  for (let i = 0; i < s.length; i++) if (s[i] === 1) c++
  return c / s.length
}
const plusDensity1 = computed(() => densityOf(sequence1.value))
const plusDensity2 = computed(() => densityOf(sequence2.value))

// ---------- Turtles ----------
interface Path { xs: Float32Array; ys: Float32Array; zs: Float32Array | null }

function wikipediaTurtle2D(s: Int8Array, angDeg: number): Path {
  const L = s.length
  const xs = new Float32Array(L + 1), ys = new Float32Array(L + 1)
  let x = 0, y = 0, h = 0
  const a = (angDeg * Math.PI) / 180
  for (let i = 0; i < L; i++) {
    x += Math.cos(h); y += Math.sin(h)
    xs[i + 1] = x; ys[i + 1] = y
    if (s[i] === 0) h += (i % 2 === 0 ? a : -a)
  }
  return { xs, ys, zs: null }
}
function dragonTurtle2D(s: Int8Array, angDeg: number): Path {
  const L = s.length
  const xs = new Float32Array(L + 1), ys = new Float32Array(L + 1)
  let x = 0, y = 0, h = 0
  const a = (angDeg * Math.PI) / 180
  for (let i = 0; i < L; i++) {
    x += Math.cos(h); y += Math.sin(h)
    xs[i + 1] = x; ys[i + 1] = y
    h += (s[i] === 0 ? a : -a)
  }
  return { xs, ys, zs: null }
}
function wikipediaTurtle3D(s: Int8Array, angDeg: number): Path {
  const L = s.length
  const xs = new Float32Array(L + 1), ys = new Float32Array(L + 1), zs = new Float32Array(L + 1)
  let Fx = 1, Fy = 0, Fz = 0
  let Ux = 0, Uy = 1, Uz = 0
  let Rx = 0, Ry = 0, Rz = -1
  const a = (angDeg * Math.PI) / 180
  let x = 0, y = 0, z = 0
  for (let i = 0; i < L; i++) {
    x += Fx; y += Fy; z += Fz
    xs[i + 1] = x; ys[i + 1] = y; zs[i + 1] = z
    if (s[i] === 0) {
      const m = i % 4
      const sign = (m === 0 || m === 1) ? 1 : -1
      const axisU = (m === 0 || m === 2)
      const c = Math.cos(sign * a), si = Math.sin(sign * a)
      if (axisU) {
        const Fx2 = Fx * c + Rx * si, Fy2 = Fy * c + Ry * si, Fz2 = Fz * c + Rz * si
        const Rx2 = -Fx * si + Rx * c, Ry2 = -Fy * si + Ry * c, Rz2 = -Fz * si + Rz * c
        Fx = Fx2; Fy = Fy2; Fz = Fz2; Rx = Rx2; Ry = Ry2; Rz = Rz2
      } else {
        const Fx2 = Fx * c + Ux * si, Fy2 = Fy * c + Uy * si, Fz2 = Fz * c + Uz * si
        const Ux2 = -Fx * si + Ux * c, Uy2 = -Fy * si + Uy * c, Uz2 = -Fz * si + Uz * c
        Fx = Fx2; Fy = Fy2; Fz = Fz2; Ux = Ux2; Uy = Uy2; Uz = Uz2
      }
    }
  }
  return { xs, ys, zs }
}
function dragonTurtle3D(s: Int8Array, angDeg: number): Path {
  const L = s.length
  const xs = new Float32Array(L + 1), ys = new Float32Array(L + 1), zs = new Float32Array(L + 1)
  let Fx = 1, Fy = 0, Fz = 0
  let Ux = 0, Uy = 1, Uz = 0
  let Rx = 0, Ry = 0, Rz = -1
  const a = (angDeg * Math.PI) / 180
  let x = 0, y = 0, z = 0
  for (let i = 0; i < L; i++) {
    x += Fx; y += Fy; z += Fz
    xs[i + 1] = x; ys[i + 1] = y; zs[i + 1] = z
    const sign = s[i] === 0 ? 1 : -1
    const axisU = i % 2 === 0
    const c = Math.cos(sign * a), si = Math.sin(sign * a)
    if (axisU) {
      const Fx2 = Fx * c + Rx * si, Fy2 = Fy * c + Ry * si, Fz2 = Fz * c + Rz * si
      const Rx2 = -Fx * si + Rx * c, Ry2 = -Fy * si + Ry * c, Rz2 = -Fz * si + Rz * c
      Fx = Fx2; Fy = Fy2; Fz = Fz2; Rx = Rx2; Ry = Ry2; Rz = Rz2
    } else {
      const Fx2 = Fx * c + Ux * si, Fy2 = Fy * c + Uy * si, Fz2 = Fz * c + Uz * si
      const Ux2 = -Fx * si + Ux * c, Uy2 = -Fy * si + Uy * c, Uz2 = -Fz * si + Uz * c
      Fx = Fx2; Fy = Fy2; Fz = Fz2; Ux = Ux2; Uy = Uy2; Uz = Uz2
    }
  }
  return { xs, ys, zs }
}

function computePath(s: Int8Array | null): Path | null {
  if (!s) return null
  if (mode.value === '2d') {
    return recipe.value === 'wikipedia' ? wikipediaTurtle2D(s, angle.value) : dragonTurtle2D(s, angle.value)
  }
  return recipe.value === 'wikipedia' ? wikipediaTurtle3D(s, angle.value) : dragonTurtle3D(s, angle.value)
}

const path1 = computed(() => computePath(sequence1.value))
const path2 = computed(() => computePath(sequence2.value))

// ---------- View state ----------
const rotX = ref(0.55)
const rotY = ref(0.55)
const zoom = ref(1.0)
let dragging = false; let lastX = 0; let lastY = 0

function onPointerDown(e: PointerEvent) {
  if (mode.value !== '3d') return
  dragging = true
  lastX = e.clientX; lastY = e.clientY
  ;(e.target as HTMLElement).setPointerCapture?.(e.pointerId)
  if (spin.value) spin.value = false
}
function onPointerMove(e: PointerEvent) {
  if (!dragging) return
  const dx = e.clientX - lastX
  const dy = e.clientY - lastY
  rotY.value += dx * 0.01
  rotX.value += dy * 0.01
  lastX = e.clientX; lastY = e.clientY
}
function onPointerUp() { dragging = false }
function onWheel(e: WheelEvent) {
  const factor = e.deltaY < 0 ? 1.1 : 1 / 1.1
  zoom.value = Math.min(20, Math.max(0.05, zoom.value * factor))
}
function resetView() { rotX.value = 0.55; rotY.value = 0.55; zoom.value = 1.0 }

// ---------- Drawing ----------
const canvasRef = ref<HTMLCanvasElement | null>(null)
const canvasRef2 = ref<HTMLCanvasElement | null>(null)
const wrapRef = ref<HTMLDivElement | null>(null)
const wrapRef2 = ref<HTMLDivElement | null>(null)
const boundsLabel = ref('')

function getCSSVar(name: string): string {
  if (typeof document === 'undefined') return '#888'
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || '#888'
}

function viridis(t: number): string {
  const r = Math.round(68 + (253 - 68) * t)
  const g = Math.round(1 + (231 - 1) * Math.sqrt(t))
  const b = Math.round(84 + (37 - 84) * t)
  return `rgb(${r},${g},${b})`
}
function magma(t: number): string {
  const r = Math.round(0 + 255 * Math.pow(t, 0.85))
  const g = Math.round(0 + 200 * Math.pow(t, 1.7))
  const b = Math.round(20 + 235 * Math.pow(t, 0.4) - 235 * t * t * 0.6)
  return `rgb(${Math.max(0, Math.min(255, r))},${Math.max(0, Math.min(255, g))},${Math.max(0, Math.min(255, b))})`
}
function hsl(h: number, s: number, l: number): string {
  return `hsl(${(h * 360).toFixed(0)}, ${(s * 100).toFixed(0)}%, ${(l * 100).toFixed(0)}%)`
}

function projectPath(p: Path): { px: Float32Array; py: Float32Array; pz: Float32Array | null } {
  const L = p.xs.length
  const px = new Float32Array(L), py = new Float32Array(L)
  let pz: Float32Array | null = null
  if (mode.value === '3d' && p.zs) {
    const cx = Math.cos(rotX.value), sx = Math.sin(rotX.value)
    const cy = Math.cos(rotY.value), sy = Math.sin(rotY.value)
    pz = new Float32Array(L)
    for (let i = 0; i < L; i++) {
      const x = p.xs[i], y = p.ys[i], z = p.zs[i]
      const x1 = x * cy + z * sy
      const z1 = -x * sy + z * cy
      const y2 = y * cx - z1 * sx
      const z2 = y * sx + z1 * cx
      px[i] = x1; py[i] = y2; pz[i] = z2
    }
  } else {
    for (let i = 0; i < L; i++) { px[i] = p.xs[i]; py[i] = p.ys[i] }
  }
  return { px, py, pz }
}

function renderPath(
  ctx: CanvasRenderingContext2D, W: number, H: number, p: Path,
  setBoundsLabel: boolean
) {
  const { px, py } = projectPath(p)
  const L = px.length
  if (L < 2) return
  let minx = Infinity, maxx = -Infinity, miny = Infinity, maxy = -Infinity
  for (let i = 0; i < L; i++) {
    const x = px[i], y = py[i]
    if (x < minx) minx = x; if (x > maxx) maxx = x
    if (y < miny) miny = y; if (y > maxy) maxy = y
  }
  const dx = maxx - minx || 1
  const dy = maxy - miny || 1
  const margin = 24
  const scale = Math.min((W - 2 * margin) / dx, (H - 2 * margin) / dy) * zoom.value
  const cxr = (minx + maxx) / 2
  const cyr = (miny + maxy) / 2
  if (setBoundsLabel) {
    boundsLabel.value =
      `[${minx.toFixed(0)}, ${maxx.toFixed(0)}] × [${miny.toFixed(0)}, ${maxy.toFixed(0)}]`
  }

  const sx = (x: number) => (x - cxr) * scale + W / 2
  const sy = (y: number) => -(y - cyr) * scale + H / 2

  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  ctx.lineWidth = mode.value === '3d' ? 1.0 : 0.8

  if (colorMode.value === 'solid') {
    ctx.strokeStyle = getCSSVar('--vp-c-brand-1') || '#3eaf7c'
    ctx.beginPath()
    ctx.moveTo(sx(px[0]), sy(py[0]))
    for (let i = 1; i < L; i++) ctx.lineTo(sx(px[i]), sy(py[i]))
    ctx.stroke()
  } else if (colorMode.value === 'time') {
    const chunkCount = 96
    const chunkSize = Math.max(1, Math.floor((L - 1) / chunkCount))
    for (let c = 0; c < chunkCount; c++) {
      const i0 = c * chunkSize
      const i1 = Math.min(L - 1, (c + 1) * chunkSize)
      if (i1 <= i0) continue
      ctx.strokeStyle = viridis(c / chunkCount)
      ctx.beginPath()
      ctx.moveTo(sx(px[i0]), sy(py[i0]))
      for (let i = i0 + 1; i <= i1; i++) ctx.lineTo(sx(px[i]), sy(py[i]))
      if (i1 < L - 1) ctx.lineTo(sx(px[i1 + 1]), sy(py[i1 + 1]))
      ctx.stroke()
    }
  } else if (colorMode.value === 'heading') {
    // Color each segment by its 2D direction (post-projection). Batch into 32 hue bins.
    const HUE_BINS = 32
    const buckets: Array<[number, number][]> = Array.from({ length: HUE_BINS }, () => [])
    for (let i = 1; i < L; i++) {
      const ddx = px[i] - px[i - 1]
      const ddy = py[i] - py[i - 1]
      const ang = Math.atan2(ddy, ddx)
      const hueBin = Math.floor(((ang + Math.PI) / (2 * Math.PI)) * HUE_BINS) % HUE_BINS
      buckets[hueBin].push([i - 1, i])
    }
    for (let b = 0; b < HUE_BINS; b++) {
      const list = buckets[b]
      if (list.length === 0) continue
      ctx.strokeStyle = hsl(b / HUE_BINS, 0.7, 0.55)
      ctx.beginPath()
      for (const [a, c] of list) {
        ctx.moveTo(sx(px[a]), sy(py[a]))
        ctx.lineTo(sx(px[c]), sy(py[c]))
      }
      ctx.stroke()
    }
  } else { // distance
    // Color by ||point - origin|| in 32 magma bins
    const HUE_BINS = 48
    const dists = new Float32Array(L)
    let dmin = Infinity, dmax = -Infinity
    for (let i = 0; i < L; i++) {
      const d = Math.hypot(p.xs[i], p.ys[i], p.zs ? p.zs[i] : 0)
      dists[i] = d
      if (d < dmin) dmin = d
      if (d > dmax) dmax = d
    }
    const dspan = dmax - dmin || 1
    const buckets: Array<[number, number][]> = Array.from({ length: HUE_BINS }, () => [])
    for (let i = 1; i < L; i++) {
      const t = (dists[i] - dmin) / dspan
      const b = Math.min(HUE_BINS - 1, Math.max(0, Math.floor(t * HUE_BINS)))
      buckets[b].push([i - 1, i])
    }
    for (let b = 0; b < HUE_BINS; b++) {
      const list = buckets[b]
      if (list.length === 0) continue
      ctx.strokeStyle = magma(b / (HUE_BINS - 1))
      ctx.beginPath()
      for (const [a, c] of list) {
        ctx.moveTo(sx(px[a]), sy(py[a]))
        ctx.lineTo(sx(px[c]), sy(py[c]))
      }
      ctx.stroke()
    }
  }

  // Endpoints
  ctx.fillStyle = '#9b59b6'
  ctx.strokeStyle = '#000'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.arc(sx(px[0]), sy(py[0]), 4, 0, Math.PI * 2)
  ctx.fill(); ctx.stroke()
  ctx.fillStyle = '#e67e22'
  ctx.beginPath()
  ctx.arc(sx(px[L - 1]), sy(py[L - 1]), 4, 0, Math.PI * 2)
  ctx.fill(); ctx.stroke()
}

function drawCanvas(
  canvas: HTMLCanvasElement | null, wrap: HTMLDivElement | null,
  p: Path | null, setBoundsLabel: boolean
) {
  if (!canvas || !p) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  const dpr = window.devicePixelRatio || 1
  const rect = wrap?.getBoundingClientRect()
  const W = rect?.width ?? 600
  const H = rect?.height || 540
  canvas.width = W * dpr
  canvas.height = H * dpr
  canvas.style.width = `${W}px`
  canvas.style.height = `${H}px`
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.fillStyle = getCSSVar('--vp-c-bg') || '#ffffff'
  ctx.fillRect(0, 0, W, H)
  renderPath(ctx, W, H, p, setBoundsLabel)
}

function drawAll() {
  drawCanvas(canvasRef.value, wrapRef.value, path1.value, true)
  if (compare.value) drawCanvas(canvasRef2.value, wrapRef2.value, path2.value, false)
}

let raf = 0
function scheduleDraw() {
  cancelAnimationFrame(raf)
  raf = requestAnimationFrame(drawAll)
}

// ---------- Auto-spin ----------
let spinRaf = 0
let spinLast = 0
function spinTick(ts: number) {
  if (!spin.value || mode.value !== '3d') { spinRaf = 0; return }
  if (spinLast === 0) spinLast = ts
  const dt = (ts - spinLast) / 1000
  spinLast = ts
  rotY.value += dt * 0.4
  spinRaf = requestAnimationFrame(spinTick)
}
watch([spin, mode], ([on, m]) => {
  cancelAnimationFrame(spinRaf); spinRaf = 0; spinLast = 0
  if (on && m === '3d') spinRaf = requestAnimationFrame(spinTick)
})

watch(compare, async (on) => { if (on) await nextTick(); scheduleDraw() })

watch(
  () => [
    sequenceType.value, sequenceType2.value, customP.value, customQ.value,
    customP2.value, customQ2.value, angle.value, length.value,
    recipe.value, mode.value, colorMode.value,
    compare.value, rotX.value, rotY.value, zoom.value,
  ],
  scheduleDraw,
  { flush: 'post' }
)

let resizeObs: ResizeObserver | null = null
onMounted(() => {
  scheduleDraw()
  if (typeof ResizeObserver !== 'undefined' && wrapRef.value) {
    resizeObs = new ResizeObserver(() => scheduleDraw())
    resizeObs.observe(wrapRef.value)
  }
})
onUnmounted(() => {
  resizeObs?.disconnect()
  cancelAnimationFrame(raf)
  cancelAnimationFrame(spinRaf)
})

// ---------- Export ----------
async function exportPNG() {
  if (!canvasRef.value) return
  exporting.value = true
  try {
    const baseW = canvasRef.value.clientWidth
    const baseH = canvasRef.value.clientHeight
    const EXPORT_SCALE = 4
    const W = baseW
    const H = baseH

    const renderOne = (p: Path | null, label: string): HTMLCanvasElement => {
      const tmp = document.createElement('canvas')
      tmp.width = W * EXPORT_SCALE
      tmp.height = H * EXPORT_SCALE
      const ctx = tmp.getContext('2d')!
      ctx.setTransform(EXPORT_SCALE, 0, 0, EXPORT_SCALE, 0, 0)
      ctx.fillStyle = '#ffffff'
      ctx.fillRect(0, 0, W, H)
      if (p) renderPath(ctx, W, H, p, false)
      // label
      ctx.setTransform(EXPORT_SCALE, 0, 0, EXPORT_SCALE, 0, 0)
      ctx.fillStyle = '#444'
      ctx.font = '14px sans-serif'
      ctx.fillText(label, 12, 20)
      return tmp
    }

    const c1 = renderOne(path1.value, sequenceLabel(sequenceType.value, customP.value, customQ.value))
    let combined: HTMLCanvasElement
    if (compare.value && path2.value) {
      const c2 = renderOne(path2.value, sequenceLabel(sequenceType2.value, customP2.value, customQ2.value))
      combined = document.createElement('canvas')
      combined.width = c1.width + c2.width
      combined.height = c1.height
      const cctx = combined.getContext('2d')!
      cctx.drawImage(c1, 0, 0)
      cctx.drawImage(c2, c1.width, 0)
    } else {
      combined = c1
    }

    const url: string = await new Promise((resolve, reject) => {
      combined.toBlob((blob) => {
        if (!blob) { reject(new Error('toBlob failed')); return }
        resolve(URL.createObjectURL(blob))
      }, 'image/png')
    })
    const a = document.createElement('a')
    a.href = url
    const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')
    a.download = `sturmian_fractal_${stamp}.png`
    document.body.appendChild(a); a.click(); document.body.removeChild(a)
    setTimeout(() => URL.revokeObjectURL(url), 5000)
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.fractal-playground {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}
.controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 14px;
}
.control-row {
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
.controls label.toggle { gap: 6px; }
.controls input[type="range"] { width: 240px; }
.controls input[type="number"] {
  width: 60px;
  padding: 3px 6px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
}
.controls select {
  padding: 4px 8px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
}
.controls button {
  padding: 4px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
  cursor: pointer;
  font-size: 13px;
}
.controls button:hover { background: var(--vp-c-bg-mute); }
.controls button:disabled { opacity: 0.6; cursor: not-allowed; }
.snap-row {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-left: 8px;
}
.snap-row button {
  padding: 2px 8px;
  font-size: 12px;
}
.snap-row .active-snap {
  background: var(--vp-c-brand-soft);
  border-color: var(--vp-c-brand-1);
}
.value {
  font-weight: bold;
  min-width: 60px;
  font-variant-numeric: tabular-nums;
}
.length-note {
  font-size: 12px;
  color: var(--vp-c-text-3);
  margin-left: 6px;
}
.canvas-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}
.canvas-grid.comparing {
  grid-template-columns: 1fr 1fr;
}
@media (max-width: 720px) {
  .canvas-grid.comparing { grid-template-columns: 1fr; }
}
.canvas-wrap {
  position: relative;
  width: 100%;
  height: 540px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  overflow: hidden;
  touch-action: none;
}
.canvas-wrap canvas { display: block; cursor: grab; }
.canvas-wrap canvas:active { cursor: grabbing; }
.canvas-label {
  position: absolute;
  left: 10px;
  top: 8px;
  font-size: 12px;
  font-weight: bold;
  color: var(--vp-c-text-2);
  background: var(--vp-c-bg-soft);
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid var(--vp-c-divider);
}
.hint {
  position: absolute;
  right: 10px;
  bottom: 10px;
  font-size: 11px;
  color: var(--vp-c-text-3);
  background: var(--vp-c-bg-soft);
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid var(--vp-c-divider);
}
.stats {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 12px;
  font-size: 13px;
  color: var(--vp-c-text-2);
}
</style>
