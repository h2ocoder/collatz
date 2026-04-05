import { ref, onUnmounted } from 'vue'

/**
 * Composable for requestAnimationFrame-based animation loops.
 * Automatically cleans up on component unmount.
 */
export function useAnimation(callback: (dt: number) => void) {
  const isRunning = ref(false)
  let rafId: number | null = null
  let lastTime = 0

  function loop(time: number) {
    if (!isRunning.value) return
    const dt = lastTime ? (time - lastTime) / 1000 : 0
    lastTime = time
    callback(dt)
    rafId = requestAnimationFrame(loop)
  }

  function start() {
    if (isRunning.value) return
    isRunning.value = true
    lastTime = 0
    rafId = requestAnimationFrame(loop)
  }

  function stop() {
    isRunning.value = false
    if (rafId !== null) {
      cancelAnimationFrame(rafId)
      rafId = null
    }
  }

  onUnmounted(stop)

  return { start, stop, isRunning }
}
