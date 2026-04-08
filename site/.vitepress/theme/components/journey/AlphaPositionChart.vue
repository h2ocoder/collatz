<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { syracuseOrbit, v2 } from '../../utils/collatz'
import { getCSSVar } from '../../utils/canvas'

const canvasRef = ref<HTMLCanvasElement | null>(null)

const BINS = 20
const ALPHA_GROUPS = [
  { label: '\u03B1 = 1 (neutral)', key: 1, color: '#94a3b8' },
  { label: '\u03B1 = 2', key: 2, color: '#6366f1' },
  { label: '\u03B1 = 3', key: 3, color: '#3b82f6' },
  { label: '\u03B1 \u2265 4', key: 4, color: '#ef4444' },
]

function computeData() {
  // For each alpha group, compute histogram of relative positions
  const histograms: Record<number, number[]> = {}
  for (const g of ALPHA_GROUPS) histograms[g.key] = new Array(BINS).fill(0)

  for (let n = 3; n < 6000; n += 2) {
    const orb = syracuseOrbit(n)
    const s = orb.length - 1 // number of Syracuse steps
    if (s < 5) continue

    for (let i = 0; i < s; i++) {
      const m = orb[i]
      const alpha = v2(3 * m + 1)
      const relPos = i / (s - 1)
      const bin = Math.min(Math.floor(relPos * BINS), BINS - 1)

      if (alpha >= 4) histograms[4][bin]++
      else if (alpha === 3) histograms[3][bin]++
      else if (alpha === 2) histograms[2][bin]++
      else histograms[1][bin]++
    }
  }

  // Normalize each group to get density
  for (const g of ALPHA_GROUPS) {
    const total = histograms[g.key].reduce((a, b) => a + b, 0)
    if (total > 0) {
      histograms[g.key] = histograms[g.key].map(v => v / total)
    }
  }

  return histograms
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

  const histograms = computeData()

  const pad = { left: 50, right: 20, top: 20, bottom: 50 }
  const plotW = W - pad.left - pad.right
  const plotH = H - pad.top - pad.bottom

  const textColor = getCSSVar('--vp-c-text-1') || '#333'
  const dividerColor = getCSSVar('--vp-c-divider') || '#e0e0e0'

  // Find max density for scaling
  let maxDensity = 0
  for (const g of ALPHA_GROUPS) {
    for (const v of histograms[g.key]) {
      if (v > maxDensity) maxDensity = v
    }
  }
  maxDensity *= 1.1

  // Draw axes
  ctx.strokeStyle = textColor
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.moveTo(pad.left, pad.top)
  ctx.lineTo(pad.left, H - pad.bottom)
  ctx.lineTo(W - pad.right, H - pad.bottom)
  ctx.stroke()

  // X axis labels
  ctx.fillStyle = textColor
  ctx.font = '11px sans-serif'
  ctx.textAlign = 'center'
  for (let i = 0; i <= 4; i++) {
    const frac = i / 4
    const x = pad.left + frac * plotW
    ctx.fillText(frac.toFixed(2), x, H - pad.bottom + 16)

    // Grid line
    ctx.strokeStyle = dividerColor
    ctx.lineWidth = 0.5
    ctx.beginPath(); ctx.moveTo(x, pad.top); ctx.lineTo(x, H - pad.bottom); ctx.stroke()
  }
  ctx.fillStyle = textColor
  ctx.font = '12px sans-serif'
  ctx.fillText('Relative position in orbit (0 = start, 1 = end)', W / 2, H - 6)

  // Y axis label
  ctx.save()
  ctx.translate(12, (pad.top + H - pad.bottom) / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.textAlign = 'center'
  ctx.fillText('Density', 0, 0)
  ctx.restore()

  // Draw bars for each group (overlaid, semi-transparent)
  const barW = plotW / BINS
  const groups = [...ALPHA_GROUPS].reverse() // draw alpha>=4 first (behind)

  for (const g of groups) {
    const hist = histograms[g.key]
    ctx.fillStyle = g.color
    ctx.globalAlpha = 0.55

    for (let b = 0; b < BINS; b++) {
      const x = pad.left + b * barW + 1
      const barH = (hist[b] / maxDensity) * plotH
      const y = H - pad.bottom - barH
      ctx.fillRect(x, y, barW - 2, barH)
    }
  }
  ctx.globalAlpha = 1

  // Draw mean position markers
  for (const g of ALPHA_GROUPS) {
    const hist = histograms[g.key]
    let weightedSum = 0
    let totalWeight = 0
    for (let b = 0; b < BINS; b++) {
      const center = (b + 0.5) / BINS
      weightedSum += center * hist[b]
      totalWeight += hist[b]
    }
    const mean = totalWeight > 0 ? weightedSum / totalWeight : 0.5
    const mx = pad.left + mean * plotW

    // Draw triangle marker
    ctx.fillStyle = g.color
    ctx.beginPath()
    ctx.moveTo(mx, H - pad.bottom + 2)
    ctx.lineTo(mx - 5, H - pad.bottom + 10)
    ctx.lineTo(mx + 5, H - pad.bottom + 10)
    ctx.closePath()
    ctx.fill()
  }

  // Legend
  const legendX = W - pad.right - 140
  const legendY = pad.top + 10
  ctx.font = '11px sans-serif'
  for (let i = 0; i < ALPHA_GROUPS.length; i++) {
    const g = ALPHA_GROUPS[i]
    const y = legendY + i * 18
    ctx.fillStyle = g.color
    ctx.globalAlpha = 0.7
    ctx.fillRect(legendX, y, 12, 12)
    ctx.globalAlpha = 1
    ctx.fillStyle = textColor
    ctx.textAlign = 'left'
    ctx.fillText(g.label, legendX + 18, y + 10)
  }

  // Uniform reference line
  const uniformY = H - pad.bottom - ((1 / BINS) / maxDensity) * plotH
  ctx.strokeStyle = '#94a3b8'
  ctx.lineWidth = 1
  ctx.setLineDash([4, 4])
  ctx.beginPath(); ctx.moveTo(pad.left, uniformY); ctx.lineTo(W - pad.right, uniformY); ctx.stroke()
  ctx.setLineDash([])
  ctx.fillStyle = '#94a3b8'
  ctx.font = '10px sans-serif'
  ctx.textAlign = 'left'
  ctx.fillText('uniform', pad.left + 4, uniformY - 4)
}

onMounted(() => { draw(); window.addEventListener('resize', draw) })
onUnmounted(() => window.removeEventListener('resize', draw))
</script>

<template>
  <div class="alpha-position">
    <canvas ref="canvasRef" style="width: 100%; height: 300px;" />
    <p class="caption">
      Where each $\alpha$ value appears in orbits (odd numbers 3&ndash;5999).
      <span style="color: #ef4444;">&alpha; &ge; 4</span> clusters at position 0.73 &mdash;
      large contractive steps are forced to appear <strong>late</strong> in the orbit.
      Triangles mark the mean position of each group.
    </p>
  </div>
</template>

<style scoped>
.alpha-position {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}

canvas { border-radius: 8px; background: var(--vp-c-bg); }

.caption { font-size: 13px; color: var(--vp-c-text-3); margin: 8px 0 0; }
</style>
