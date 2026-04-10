<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { syracuseOrbit, alphaSequence, eisensteinNorm, v2, LOG2_3 } from '../../utils/collatz'
import { getCSSVar } from '../../utils/canvas'

const startN = ref(27)
const showVectors = ref(false)
const showGrid = ref(true)
const canvasRef = ref<HTMLCanvasElement | null>(null)

// Eisenstein basis: e1 = (1, 0), e2 = (-1/2, sqrt(3)/2)
// Lattice point (h, s) -> pixel: x = h - s/2, y = s * sqrt(3)/2
const SQRT3_2 = Math.sqrt(3) / 2

function toPixel(h: number, s: number, scale: number, ox: number, oy: number): [number, number] {
  const x = ox + (h - s * 0.5) * scale
  const y = oy - s * SQRT3_2 * scale
  return [x, y]
}

function draw() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const rect = canvas.getBoundingClientRect()
  const dpr = window.devicePixelRatio || 1
  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr
  ctx.scale(dpr, dpr)
  const W = rect.width
  const H = rect.height

  ctx.clearRect(0, 0, W, H)

  const n = Math.max(3, startN.value | 0)
  if (n % 2 === 0) return // need odd

  const alphas = alphaSequence(n)
  const s_total = alphas.length
  const h_total = alphas.reduce((a, b) => a + b, 0)

  // Build walk points
  const walkPoints: Array<{ h: number; s: number; alpha: number }> = [{ h: 0, s: 0, alpha: 0 }]
  let h = 0, s = 0
  for (const a of alphas) {
    s += 1
    h += a
    walkPoints.push({ h, s, alpha: a })
  }

  // Compute scale to fit
  const maxH = Math.max(h_total, 10)
  const maxS = Math.max(s_total, 5)
  // In pixel coords, x range ~ [-maxS/2, maxH], y range ~ [0, maxS * sqrt3/2]
  const xRange = maxH + maxS * 0.5 + 4
  const yRange = maxS * SQRT3_2 + 4
  const pad = 50
  const scaleX = (W - pad * 2) / xRange
  const scaleY = (H - pad * 2) / yRange
  const scale = Math.min(scaleX, scaleY)

  // Origin: bottom-left area
  const ox = pad + maxS * 0.5 * scale + 2 * scale
  const oy = H - pad

  const dividerColor = getCSSVar('--vp-c-divider') || '#e0e0e0'
  const textColor = getCSSVar('--vp-c-text-3') || '#999'
  const brandColor = getCSSVar('--vp-c-brand-1') || '#5b8def'

  // Draw triangular grid (faint)
  if (showGrid.value && scale > 3) {
    ctx.strokeStyle = dividerColor
    ctx.lineWidth = 0.3
    ctx.globalAlpha = 0.4

    const gridStep = scale < 8 ? 5 : (scale < 15 ? 2 : 1)
    const gridMaxH = Math.ceil(maxH / gridStep) * gridStep + gridStep
    const gridMaxS = Math.ceil(maxS / gridStep) * gridStep + gridStep

    // Lines along h direction (constant s)
    for (let si = 0; si <= gridMaxS; si += gridStep) {
      const [x0, y0] = toPixel(0, si, scale, ox, oy)
      const [x1, y1] = toPixel(gridMaxH, si, scale, ox, oy)
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke()
    }
    // Lines along s direction (constant h)
    for (let hi = 0; hi <= gridMaxH; hi += gridStep) {
      const [x0, y0] = toPixel(hi, 0, scale, ox, oy)
      const [x1, y1] = toPixel(hi, gridMaxS, scale, ox, oy)
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke()
    }
    // Diagonal lines (constant h-s)
    for (let d = -gridMaxS; d <= gridMaxH; d += gridStep) {
      const s0 = Math.max(0, -d)
      const s1 = Math.min(gridMaxS, gridMaxH - d)
      if (s0 < s1) {
        const [x0, y0] = toPixel(d + s0, s0, scale, ox, oy)
        const [x1, y1] = toPixel(d + s1, s1, scale, ox, oy)
        ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke()
      }
    }
    ctx.globalAlpha = 1
  }

  // Draw geodesic line: h = s * log_2(3)
  const geoS = maxS + 2
  const geoH = geoS * LOG2_3
  const [gx0, gy0] = toPixel(0, 0, scale, ox, oy)
  const [gx1, gy1] = toPixel(geoH, geoS, scale, ox, oy)
  ctx.strokeStyle = '#94a3b8'
  ctx.lineWidth = 1.5
  ctx.setLineDash([6, 4])
  ctx.beginPath(); ctx.moveTo(gx0, gy0); ctx.lineTo(gx1, gy1); ctx.stroke()
  ctx.setLineDash([])

  // Label geodesic
  ctx.fillStyle = '#94a3b8'
  ctx.font = '11px sans-serif'
  ctx.textAlign = 'left'
  const [glx, gly] = toPixel(geoH * 0.7, geoS * 0.7, scale, ox, oy)
  ctx.save()
  const geoAngle = -Math.atan2(geoS * SQRT3_2, geoH - geoS * 0.5)
  ctx.translate(glx, gly)
  ctx.rotate(geoAngle)
  ctx.fillText('h = s \u00B7 log\u2082(3)  [geodesic]', 5, -6)
  ctx.restore()

  // Draw walk path segments
  for (let i = 1; i < walkPoints.length; i++) {
    const prev = walkPoints[i - 1]
    const curr = walkPoints[i]
    const [px, py] = toPixel(prev.h, prev.s, scale, ox, oy)
    const [cx2, cy2] = toPixel(curr.h, curr.s, scale, ox, oy)

    // Color: green if above geodesic, red if below
    const aboveGeo = curr.h - curr.s * LOG2_3
    ctx.strokeStyle = aboveGeo > 0 ? '#22c55e' : '#ef4444'
    ctx.lineWidth = 1.8
    ctx.globalAlpha = 0.3 + 0.7 * (i / walkPoints.length)
    ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(cx2, cy2); ctx.stroke()
  }
  ctx.globalAlpha = 1

  // Draw displacement vectors if enabled
  if (showVectors.value) {
    for (let i = 1; i < walkPoints.length; i++) {
      const prev = walkPoints[i - 1]
      const curr = walkPoints[i]
      const [px, py] = toPixel(prev.h, prev.s, scale, ox, oy)

      // Draw the tripling component (vertical in Eisenstein coords)
      const [tx, ty] = toPixel(prev.h, prev.s + 1, scale, ox, oy)
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.3)'
      ctx.lineWidth = 1
      ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(tx, ty); ctx.stroke()

      // Draw the halving component (horizontal)
      const [hx, hy] = toPixel(curr.h, curr.s, scale, ox, oy)
      ctx.strokeStyle = 'rgba(34, 197, 94, 0.3)'
      ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(hx, hy); ctx.stroke()
    }
  }

  // Draw walk points
  for (let i = 0; i < walkPoints.length; i++) {
    const p = walkPoints[i]
    const [px, py] = toPixel(p.h, p.s, scale, ox, oy)
    const isStart = i === 0
    const isEnd = i === walkPoints.length - 1

    const r = isStart ? 5 : isEnd ? 5 : Math.min(2 + p.alpha * 0.8, 6)
    const color = isStart ? '#ef4444' : isEnd ? '#22c55e' : brandColor
    ctx.globalAlpha = isStart || isEnd ? 1 : 0.3 + 0.7 * (i / walkPoints.length)

    ctx.fillStyle = color
    ctx.beginPath(); ctx.arc(px, py, r, 0, Math.PI * 2); ctx.fill()
  }
  ctx.globalAlpha = 1

  // Labels
  const [sx, sy] = toPixel(0, 0, scale, ox, oy)
  ctx.fillStyle = '#ef4444'
  ctx.font = 'bold 11px sans-serif'
  ctx.textAlign = 'left'
  ctx.fillText('(0, 0)', sx + 8, sy + 4)

  const [ex, ey] = toPixel(h_total, s_total, scale, ox, oy)
  ctx.fillStyle = '#22c55e'
  ctx.fillText(`(${h_total}, ${s_total})`, ex + 8, ey - 4)

  // Axis labels
  ctx.fillStyle = textColor
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText('h (halvings) \u2192', W / 2, H - 8)

  ctx.save()
  ctx.translate(12, H / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.fillText('s (triplings) \u2192', 0, 0)
  ctx.restore()
}

watch([startN, showVectors, showGrid], draw)
onMounted(() => { draw(); window.addEventListener('resize', draw) })
onUnmounted(() => window.removeEventListener('resize', draw))

// Computed stats for display
function getStats() {
  const n = Math.max(3, startN.value | 0)
  if (n % 2 === 0) return null
  const alphas = alphaSequence(n)
  const s = alphas.length
  const h = alphas.reduce((a, b) => a + b, 0)
  const T = h + s
  const norm = eisensteinNorm(h, s)
  const ratio = s > 0 ? h / s : 0
  const excess = h - s * LOG2_3
  return { h, s, T, norm, ratio, excess }
}
</script>

<template>
  <div class="eisenstein-walk">
    <div class="controls">
      <label>
        n =
        <input type="number" v-model.number="startN" min="3" max="99999" step="2" @keyup.enter="draw" />
      </label>
      <label class="toggle">
        <input type="checkbox" v-model="showGrid" /> Grid
      </label>
      <label class="toggle">
        <input type="checkbox" v-model="showVectors" /> Vectors
      </label>
    </div>
    <canvas ref="canvasRef" style="width: 100%; height: 420px;" />
    <div class="stats" v-if="getStats()">
      <span>h = <strong>{{ getStats()!.h }}</strong></span>
      <span>s = <strong>{{ getStats()!.s }}</strong></span>
      <span>h/s = <strong>{{ getStats()!.ratio.toFixed(4) }}</strong></span>
      <span>N(h,s) = <strong>{{ getStats()!.norm }}</strong></span>
      <span :class="getStats()!.excess > 0 ? 'above' : 'below'">
        {{ getStats()!.excess > 0 ? 'above' : 'below' }} geodesic by {{ Math.abs(getStats()!.excess).toFixed(3) }}
      </span>
    </div>
    <p class="caption">
      Each Syracuse step adds a vector $\alpha_i + \omega$ to the lattice walk.
      <span style="color: #22c55e;">Green</span> segments are above the geodesic (contracting);
      <span style="color: #ef4444;">red</span> segments are below (growing).
      Dot size reflects $\alpha$ (halvings per tripling).
    </p>
  </div>
</template>

<style scoped>
.eisenstein-walk {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}

.controls {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 8px;
}

.controls input[type="number"] {
  width: 80px;
  padding: 6px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
}

.controls label { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.toggle { cursor: pointer; }

canvas { border-radius: 8px; background: var(--vp-c-bg); }

.stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 13px;
  margin-top: 8px;
  color: var(--vp-c-text-2);
}

.stats .above { color: #22c55e; }
.stats .below { color: #ef4444; }

.caption { font-size: 13px; color: var(--vp-c-text-3); margin: 8px 0 0; }
</style>
