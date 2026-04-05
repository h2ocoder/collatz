<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { beta, LOG2_3 } from '../../utils/collatz'

const maxS = ref(40)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const hoveredS = ref<number | null>(null)

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
  const w = rect.width
  const h = rect.height
  const pad = 50

  ctx.clearRect(0, 0, w, h)

  const textColor = getComputedStyle(canvas).getPropertyValue('--vp-c-text-2').trim() || '#666'
  const gridColor = getComputedStyle(canvas).getPropertyValue('--vp-c-divider').trim() || '#e5e5e5'

  // Axes
  ctx.strokeStyle = textColor
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.moveTo(pad, h - pad)
  ctx.lineTo(w - 10, h - pad)
  ctx.moveTo(pad, 10)
  ctx.lineTo(pad, h - pad)
  ctx.stroke()

  ctx.fillStyle = textColor
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText('s (odd steps)', w / 2, h - 8)

  ctx.save()
  ctx.translate(12, h / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.fillText('\u03B2(s) bits destroyed', 0, 0)
  ctx.restore()

  // Y-axis: 0 to 1
  ctx.strokeStyle = gridColor
  ctx.lineWidth = 0.5
  for (let y = 0; y <= 1; y += 0.25) {
    const py = h - pad - y * (h - pad - 10)
    ctx.beginPath(); ctx.moveTo(pad, py); ctx.lineTo(w - 10, py); ctx.stroke()
    ctx.fillStyle = textColor; ctx.textAlign = 'right'; ctx.font = '11px sans-serif'
    ctx.fillText(y.toFixed(2), pad - 6, py + 4)
  }

  // Bars
  const barW = Math.max(2, (w - pad - 20) / maxS.value - 2)
  const convergentS = new Set([1, 2, 5, 12, 29, 41]) // denominators of convergents of log2(3)

  for (let s = 1; s <= maxS.value; s++) {
    const b = beta(s)
    const x = pad + (s - 0.5) / maxS.value * (w - pad - 20)
    const barH = b * (h - pad - 10)
    const y = h - pad - barH

    // Color: green for fast (high beta), red for slow (low beta), gold for convergents
    let color: string
    if (convergentS.has(s)) {
      color = '#ef4444' // convergent = slow set
    } else if (b > 0.5) {
      color = '#22c55e'
    } else if (b > 0.2) {
      color = '#3b82f6'
    } else {
      color = '#f59e0b'
    }

    if (hoveredS.value === s) {
      color = '#8b5cf6'
    }

    ctx.fillStyle = color
    ctx.fillRect(x - barW / 2, y, barW, barH)
  }

  // Hover info
  if (hoveredS.value !== null && hoveredS.value >= 1) {
    const s = hoveredS.value
    const b = beta(s)
    const sl3 = s * LOG2_3
    const k = Math.ceil(s * Math.log2(6))

    ctx.fillStyle = 'rgba(0,0,0,0.8)'
    ctx.fillRect(w - 240, 10, 230, 80)
    ctx.fillStyle = '#fff'
    ctx.font = '12px monospace'
    ctx.textAlign = 'left'
    ctx.fillText(`s = ${s}  (Set ${k})`, w - 232, 28)
    ctx.fillText(`\u03B2(${s}) = ${b.toFixed(6)}`, w - 232, 44)
    ctx.fillText(`s\u00B7log\u2082(3) = ${sl3.toFixed(4)}`, w - 232, 60)
    ctx.fillText(`Factor: 3^${s}/2^${k - s} = ${(Math.pow(3, s) / Math.pow(2, k - s)).toFixed(4)}`, w - 232, 76)
  }

  // X tick labels
  ctx.fillStyle = textColor; ctx.textAlign = 'center'; ctx.font = '10px sans-serif'
  for (let s = 5; s <= maxS.value; s += 5) {
    const x = pad + (s - 0.5) / maxS.value * (w - pad - 20)
    ctx.fillText(String(s), x, h - pad + 14)
  }
}

function handleMouseMove(e: MouseEvent) {
  const canvas = canvasRef.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  const x = e.clientX - rect.left
  const pad = 50
  const s = Math.round(((x - pad) / (rect.width - pad - 20)) * maxS.value + 0.5)
  hoveredS.value = s >= 1 && s <= maxS.value ? s : null
  draw()
}

watch(maxS, draw)
onMounted(() => { draw(); window.addEventListener('resize', draw) })
onUnmounted(() => window.removeEventListener('resize', draw))
</script>

<template>
  <div class="bit-landscape">
    <div class="controls">
      <label>
        Max s:
        <input type="range" v-model.number="maxS" min="10" max="80" />
        {{ maxS }}
      </label>
    </div>
    <canvas
      ref="canvasRef"
      style="width: 100%; height: 280px; cursor: crosshair;"
      @mousemove="handleMouseMove"
      @mouseleave="hoveredS = null; draw()"
    />
    <div class="legend">
      <span><span class="dot" style="background: #22c55e"></span> Fast (β > 0.5)</span>
      <span><span class="dot" style="background: #3b82f6"></span> Moderate</span>
      <span><span class="dot" style="background: #f59e0b"></span> Slow (β < 0.2)</span>
      <span><span class="dot" style="background: #ef4444"></span> Convergent (slowest)</span>
    </div>
  </div>
</template>

<style scoped>
.bit-landscape {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}
.controls { margin-bottom: 8px; }
.controls label { display: flex; align-items: center; gap: 8px; font-size: 14px; }
canvas { border-radius: 8px; background: var(--vp-c-bg); }
.legend { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 8px; font-size: 12px; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 4px; vertical-align: middle; }
</style>
