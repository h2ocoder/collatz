/**
 * Shared Canvas 2D drawing helpers.
 * Lightweight — no external dependencies.
 */

export interface AxisOpts {
  xLabel?: string
  yLabel?: string
  xMin: number
  xMax: number
  yMin: number
  yMax: number
  padding?: number
  gridLines?: boolean
  tickCount?: number
}

/** Get CSS variable value from the document */
export function getCSSVar(name: string): string {
  if (typeof document === 'undefined') return '#888'
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || '#888'
}

/** Clear canvas and return dimensions */
export function clearCanvas(ctx: CanvasRenderingContext2D): { w: number; h: number } {
  const w = ctx.canvas.width
  const h = ctx.canvas.height
  ctx.clearRect(0, 0, w, h)
  return { w, h }
}

/** Map data coordinates to canvas pixel coordinates */
export function mapCoords(
  x: number, y: number,
  opts: AxisOpts,
  canvasW: number, canvasH: number
): [number, number] {
  const pad = opts.padding ?? 50
  const plotW = canvasW - pad * 2
  const plotH = canvasH - pad * 2
  const px = pad + ((x - opts.xMin) / (opts.xMax - opts.xMin)) * plotW
  const py = pad + ((opts.yMax - y) / (opts.yMax - opts.yMin)) * plotH
  return [px, py]
}

/** Draw axes with optional grid lines */
export function drawAxes(ctx: CanvasRenderingContext2D, opts: AxisOpts) {
  const { w, h } = { w: ctx.canvas.width, h: ctx.canvas.height }
  const pad = opts.padding ?? 50
  const textColor = getCSSVar('--vp-c-text-1') || '#333'
  const gridColor = getCSSVar('--vp-c-divider') || '#e0e0e0'

  ctx.strokeStyle = textColor
  ctx.lineWidth = 1.5
  ctx.font = '12px sans-serif'
  ctx.fillStyle = textColor

  // X axis
  ctx.beginPath()
  ctx.moveTo(pad, h - pad)
  ctx.lineTo(w - pad, h - pad)
  ctx.stroke()

  // Y axis
  ctx.beginPath()
  ctx.moveTo(pad, pad)
  ctx.lineTo(pad, h - pad)
  ctx.stroke()

  // Grid lines and tick labels
  const tickCount = opts.tickCount ?? 5
  if (opts.gridLines !== false) {
    ctx.strokeStyle = gridColor
    ctx.lineWidth = 0.5

    for (let i = 0; i <= tickCount; i++) {
      const t = i / tickCount
      // Horizontal grid
      const gy = pad + t * (h - 2 * pad)
      ctx.beginPath()
      ctx.moveTo(pad, gy)
      ctx.lineTo(w - pad, gy)
      ctx.stroke()

      const yVal = opts.yMax - t * (opts.yMax - opts.yMin)
      ctx.fillStyle = textColor
      ctx.textAlign = 'right'
      ctx.fillText(yVal.toFixed(yVal > 100 ? 0 : 1), pad - 8, gy + 4)

      // Vertical grid
      const gx = pad + t * (w - 2 * pad)
      ctx.beginPath()
      ctx.moveTo(gx, pad)
      ctx.lineTo(gx, h - pad)
      ctx.stroke()

      const xVal = opts.xMin + t * (opts.xMax - opts.xMin)
      ctx.fillStyle = textColor
      ctx.textAlign = 'center'
      ctx.fillText(xVal.toFixed(xVal > 100 ? 0 : 1), gx, h - pad + 18)
    }
  }

  // Axis labels
  if (opts.xLabel) {
    ctx.fillStyle = textColor
    ctx.textAlign = 'center'
    ctx.font = '13px sans-serif'
    ctx.fillText(opts.xLabel, w / 2, h - 8)
  }
  if (opts.yLabel) {
    ctx.save()
    ctx.fillStyle = textColor
    ctx.textAlign = 'center'
    ctx.font = '13px sans-serif'
    ctx.translate(14, h / 2)
    ctx.rotate(-Math.PI / 2)
    ctx.fillText(opts.yLabel, 0, 0)
    ctx.restore()
  }
}

/** Draw a polyline */
export function drawLine(
  ctx: CanvasRenderingContext2D,
  points: [number, number][],
  color: string,
  lineWidth = 1.5
) {
  if (points.length < 2) return
  ctx.strokeStyle = color
  ctx.lineWidth = lineWidth
  ctx.beginPath()
  ctx.moveTo(points[0][0], points[0][1])
  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i][0], points[i][1])
  }
  ctx.stroke()
}

/** Draw a filled circle */
export function drawDot(
  ctx: CanvasRenderingContext2D,
  x: number, y: number,
  radius: number,
  color: string
) {
  ctx.fillStyle = color
  ctx.beginPath()
  ctx.arc(x, y, radius, 0, Math.PI * 2)
  ctx.fill()
}

/** Draw a filled rectangle */
export function drawBar(
  ctx: CanvasRenderingContext2D,
  x: number, y: number,
  w: number, h: number,
  color: string
) {
  ctx.fillStyle = color
  ctx.fillRect(x, y, w, h)
}

/** Draw text with options */
export function drawText(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number, y: number,
  opts?: { align?: CanvasTextAlign; font?: string; color?: string }
) {
  ctx.fillStyle = opts?.color ?? getCSSVar('--vp-c-text-1') || '#333'
  ctx.font = opts?.font ?? '12px sans-serif'
  ctx.textAlign = opts?.align ?? 'left'
  ctx.fillText(text, x, y)
}
