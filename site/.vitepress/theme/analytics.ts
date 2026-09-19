// PostHog analytics for the site.
//
// Off unless VITE_POSTHOG_KEY is set at build time (the deploy workflow passes the
// repository variable POSTHOG_KEY). Local builds and dev servers send nothing.
//
// What is recorded:
//   $pageview       every page, including client-side navigation
//   $pageleave      with PostHog's built-in max scroll depth for the page
//   section_viewed  once per page visit, the first time an h2/h3 has been on screen
//                   for at least SECTION_DWELL_MS, with how many seconds into the visit
//   playground_used the first interaction with an interactive component on a page
//
// Privacy: no cookies (localStorage persistence), Do Not Track is respected, session
// recording and autocaptured element clicks are off.

import type { Router } from 'vitepress'

const KEY = import.meta.env.VITE_POSTHOG_KEY as string | undefined
const HOST = (import.meta.env.VITE_POSTHOG_HOST as string | undefined) || 'https://us.i.posthog.com'
const SECTION_DWELL_MS = 2000

type PostHog = typeof import('posthog-js').default
let posthog: PostHog | null = null
let observer: IntersectionObserver | null = null
let visitStart = 0

export async function setupAnalytics(router: Router) {
  if (typeof window === 'undefined' || !KEY) return
  posthog = (await import('posthog-js')).default
  posthog.init(KEY, {
    api_host: HOST,
    persistence: 'localStorage',
    respect_dnt: true,
    autocapture: false,
    disable_session_recording: true,
    capture_pageview: false,
    capture_pageleave: true,
  })

  const previous = router.onAfterRouteChanged
  router.onAfterRouteChanged = (to: string) => {
    previous?.(to)
    track(to)
  }
  track(window.location.pathname)
}

function track(path: string) {
  if (!posthog) return
  visitStart = performance.now()
  posthog.capture('$pageview', { $current_url: window.location.href, path })
  // wait for the new page's DOM before observing its headings and components
  window.setTimeout(() => {
    watchSections(path)
    watchPlaygrounds(path)
  }, 300)
}

function watchSections(path: string) {
  observer?.disconnect()
  const seen = new Set<string>()
  const timers = new Map<Element, number>()
  observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      const heading = entry.target as HTMLElement
      const id = heading.id || heading.textContent?.trim() || ''
      if (seen.has(id)) continue
      if (entry.isIntersecting) {
        timers.set(heading, window.setTimeout(() => {
          seen.add(id)
          posthog?.capture('section_viewed', {
            path,
            section_id: id,
            section_title: heading.textContent?.replace(/​|#$/g, '').trim(),
            level: heading.tagName.toLowerCase(),
            seconds_into_visit: Math.round((performance.now() - visitStart) / 1000),
          })
        }, SECTION_DWELL_MS))
      } else {
        window.clearTimeout(timers.get(heading))
        timers.delete(heading)
      }
    }
  }, { threshold: 0.6 })
  document.querySelectorAll('.vp-doc h2, .vp-doc h3').forEach((h) => observer!.observe(h))
}

function watchPlaygrounds(path: string) {
  // any interactive control inside the page body counts; report the first use per page visit
  const doc = document.querySelector('.vp-doc')
  if (!doc) return
  let reported = false
  const onUse = (event: Event) => {
    const target = event.target as HTMLElement
    if (reported || !target.closest('input, button, select, canvas, svg, [role="button"]')) return
    reported = true
    const section = nearestHeading(target)
    posthog?.capture('playground_used', { path, section, control: target.tagName.toLowerCase() })
  }
  doc.addEventListener('input', onUse, { capture: true })
  doc.addEventListener('click', onUse, { capture: true })
}

function nearestHeading(el: HTMLElement): string | undefined {
  const headings = Array.from(document.querySelectorAll('.vp-doc h2, .vp-doc h3'))
  let last: Element | undefined
  for (const h of headings) {
    if (h.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING) last = h
    else break
  }
  return last?.textContent?.replace(/​|#$/g, '').trim()
}
