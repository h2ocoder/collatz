<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { orbit } from '../../utils/collatz'

const startN = ref(27)
const useLog = ref(false)
const canvasRef = ref<HTMLCanvasElement | null>(null)

function draw() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // HiDPI
  const rect = canvas.getBoundingClientRect()
  const dpr = window.devicePixelRatio || 1
  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr
  ctx.scale(dpr, dpr)
  const w = rect.width
  const h = rect.height

  ctx.clearRect(0, 0, w, h)

  const orb = orbit(Math.max(2, startN.value), 10000)
  const values = useLog.value ? orb.map(v => Math.log2(Math.max(v, 1))) : orb

  const maxVal = Math.max(...values)
  const minVal = Math.min(...values)
  const range = maxVal - minVal || 1
  const pad = 50

  // Background
  const bg = getComputedStyle(canvas).getPropertyValue('--vp-c-bg').trim() || '#fff'
  ctx.fillStyle = bg
  ctx.fillRect(0, 0, w, h)

  // Grid
  const gridColor = getComputedStyle(canvas).getPropertyValue('--vp-c-divider').trim() || '#e5e5e5'
  const textColor = getComputedStyle(canvas).getPropertyValue('--vp-c-text-2').trim() || '#666'
  ctx.strokeStyle = gridColor
  ctx.lineWidth = 0.5

  for (let i = 0; i <= 4; i++) {
    const y = pad + (i / 4) * (h - 2 * pad)
    ctx.beginPath(); ctx.moveTo(pad, y); ctx.lineTo(w - 10, y); ctx.stroke()
    const label = (maxVal - (i / 4) * range).toFixed(useLog.value ? 1 : 0)
    ctx.fillStyle = textColor
    ctx.font = '11px sans-serif'
    ctx.textAlign = 'right'
    ctx.fillText(label, pad - 8, y + 4)
  }

  // Y-axis label
  ctx.save()
  ctx.fillStyle = textColor
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'center'
  ctx.translate(12, h / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.fillText(useLog.value ? 'log\u2082(value)' : 'value', 0, 0)
  ctx.restore()

  // X-axis label
  ctx.fillStyle = textColor
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText('step', w / 2, h - 6)

  // Plot
  const brandColor = getComputedStyle(canvas).getPropertyValue('--vp-c-brand-1').trim() || '#5b8def'
  ctx.strokeStyle = brandColor
  ctx.lineWidth = 1.5
  ctx.beginPath()

  for (let i = 0; i < values.length; i++) {
    const x = pad + (i / Math.max(values.length - 1, 1)) * (w - pad - 10)
    const y = pad + ((maxVal - values[i]) / range) * (h - 2 * pad)
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  }
  ctx.stroke()

  // Title
  ctx.fillStyle = textColor
  ctx.font = 'bold 13px sans-serif'
  ctx.textAlign = 'left'
  ctx.fillText(`n = ${startN.value} (${orb.length - 1} steps, peak ${Math.max(...orb).toLocaleString()})`, pad, 20)
}

watch([startN, useLog], draw)
onMounted(() => {
  draw()
  window.addEventListener('resize', draw)
})
onUnmounted(() => window.removeEventListener('resize', draw))
</script>

<template>
  <div class="hailstone-chart">
    <div class="controls">
      <label>
        n =
        <input type="range" min="2" max="1000" v-model.number="startN" />
        <span class="range-val">{{ startN }}</span>
      </label>
      <label class="toggle">
        <input type="checkbox" v-model="useLog" />
        log₂ scale
      </label>
    </div>
    <canvas ref="canvasRef" style="width: 100%; height: 300px;" />
    <p class="hint" v-if="!useLog">
      <em>Try toggling log₂ scale — the chaos becomes a steady descent.</em>
    </p>
    <p class="hint" v-else>
      <em>In log scale, the orbit trends downward. The bits are shrinking.</em>
    </p>
  </div>
</template>

<style scoped>
.hailstone-chart {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
  background: var(--vp-c-bg-soft);
}

.controls {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.controls label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.range-val {
  font-family: var(--vp-font-family-mono);
  font-weight: 600;
  min-width: 40px;
}

.toggle {
  cursor: pointer;
}

.toggle input {
  cursor: pointer;
}

canvas {
  border-radius: 8px;
  background: var(--vp-c-bg);
}

.hint {
  font-size: 13px;
  color: var(--vp-c-text-3);
  margin: 8px 0 0;
}
</style>
