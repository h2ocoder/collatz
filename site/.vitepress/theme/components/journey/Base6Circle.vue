<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { syracuseOrbit, log6, frac, LOG6_3 } from '../../utils/collatz'

const startN = ref(27)
const maxPoints = ref(100)
const showIdeal = ref(false)
const canvasRef = ref<HTMLCanvasElement | null>(null)

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
  const size = Math.min(rect.width, rect.height)
  const cx = rect.width / 2
  const cy = rect.height / 2
  const radius = size * 0.38

  // Background
  ctx.clearRect(0, 0, rect.width, rect.height)

  // Circle outline
  ctx.strokeStyle = getComputedStyle(canvas).getPropertyValue('--vp-c-divider').trim() || '#e0e0e0'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.arc(cx, cy, radius, 0, Math.PI * 2)
  ctx.stroke()

  // Tick marks at 0, 0.25, 0.5, 0.75
  const textColor = getComputedStyle(canvas).getPropertyValue('--vp-c-text-3').trim() || '#999'
  ctx.fillStyle = textColor
  ctx.font = '11px sans-serif'
  ctx.textAlign = 'center'

  for (let i = 0; i < 4; i++) {
    const angle = (i / 4) * Math.PI * 2 - Math.PI / 2
    const tx = cx + (radius + 18) * Math.cos(angle)
    const ty = cy + (radius + 18) * Math.sin(angle)
    ctx.fillText((i * 0.25).toFixed(2), tx, ty + 4)

    ctx.beginPath()
    ctx.moveTo(cx + radius * Math.cos(angle), cy + radius * Math.sin(angle))
    ctx.lineTo(cx + (radius + 8) * Math.cos(angle), cy + (radius + 8) * Math.sin(angle))
    ctx.strokeStyle = textColor
    ctx.lineWidth = 1
    ctx.stroke()
  }

  // Compute orbit points on the circle
  const n = Math.max(3, startN.value)
  const orb = syracuseOrbit(n, maxPoints.value + 10)
  const points = orb.slice(0, maxPoints.value).map((v, i) => {
    const theta = frac(log6(v)) * Math.PI * 2 - Math.PI / 2
    return { x: cx + radius * Math.cos(theta), y: cy + radius * Math.sin(theta), v, i }
  })

  // Ideal rotation points
  if (showIdeal.value) {
    const theta0 = frac(log6(n)) * Math.PI * 2 - Math.PI / 2
    ctx.strokeStyle = '#94a3b8'
    ctx.lineWidth = 0.5
    for (let i = 0; i < Math.min(maxPoints.value, orb.length); i++) {
      const theta = (frac(log6(n)) + i * LOG6_3) * Math.PI * 2 - Math.PI / 2
      const ix = cx + (radius - 4) * Math.cos(theta)
      const iy = cy + (radius - 4) * Math.sin(theta)
      ctx.fillStyle = 'rgba(148, 163, 184, 0.4)'
      ctx.beginPath()
      ctx.arc(ix, iy, 2.5, 0, Math.PI * 2)
      ctx.fill()
    }
  }

  // Draw connecting lines (faint)
  if (points.length > 1) {
    ctx.strokeStyle = 'rgba(99, 102, 241, 0.15)'
    ctx.lineWidth = 0.8
    ctx.beginPath()
    ctx.moveTo(points[0].x, points[0].y)
    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(points[i].x, points[i].y)
    }
    ctx.stroke()
  }

  // Draw actual orbit points
  const brandColor = getComputedStyle(canvas).getPropertyValue('--vp-c-brand-1').trim() || '#5b8def'
  for (let i = 0; i < points.length; i++) {
    const p = points[i]
    const alpha = 0.3 + 0.7 * (i / points.length) // fade in
    const r = i === 0 ? 5 : i === points.length - 1 ? 4 : 3
    ctx.fillStyle = i === 0 ? '#ef4444' : brandColor
    ctx.globalAlpha = alpha
    ctx.beginPath()
    ctx.arc(p.x, p.y, r, 0, Math.PI * 2)
    ctx.fill()
  }
  ctx.globalAlpha = 1

  // Labels
  ctx.fillStyle = '#ef4444'
  ctx.font = 'bold 12px sans-serif'
  ctx.textAlign = 'left'
  if (points.length > 0) {
    ctx.fillText(`start: ${n}`, points[0].x + 8, points[0].y - 8)
  }

  // Center label
  ctx.fillStyle = textColor
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText(`${points.length} points`, cx, cy - 6)
  ctx.fillText(`log₆ circle`, cx, cy + 10)
}

watch([startN, maxPoints, showIdeal], draw)
onMounted(() => { draw(); window.addEventListener('resize', draw) })
onUnmounted(() => window.removeEventListener('resize', draw))
</script>

<template>
  <div class="base6-circle">
    <div class="controls">
      <label>
        n =
        <input type="number" v-model.number="startN" min="3" max="99999" />
      </label>
      <label>
        Points:
        <input type="range" v-model.number="maxPoints" min="10" max="500" />
        {{ maxPoints }}
      </label>
      <label class="toggle">
        <input type="checkbox" v-model="showIdeal" />
        Show ideal rotation
      </label>
    </div>
    <canvas ref="canvasRef" style="width: 100%; height: 400px;" />
    <p class="caption">
      Each Syracuse step maps to a point on the circle at position $\lbrace \log_6(\text{value}) \rbrace$.
      <template v-if="showIdeal">
        <br/>Gray dots: ideal rotation by $\log_6 3 \approx 0.613$. Colored dots: actual orbit.
        They're close — Collatz is a <strong>perturbed irrational rotation</strong>.
      </template>
    </p>
  </div>
</template>

<style scoped>
.base6-circle {
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

.caption { font-size: 13px; color: var(--vp-c-text-3); margin: 8px 0 0; }
</style>
