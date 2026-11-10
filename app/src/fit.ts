// Auto-fit: scale each slide so body text reaches a projector-readable size.
//
// Slide content is authored at a 17px body (BASE_BODY_PX). On screens 961px wide and up, each
// .slide-inner is laid out at a design width and scaled with CSS zoom so body text approaches
// targetBodyPx(): about 24px at 1280 wide, 25px at 1440, 29px at 1920 (18pt on a 1280 slide is
// 24px). If the content would overflow at that size, the slide backs off only as far as needed.

export const BASE_BODY_PX = 17
const MIN_ZOOM = 0.85
const MOBILE_MAX = 960

export function targetBodyPx(viewportWidth: number) {
  return Math.min(30, Math.max(18, 0.009 * viewportWidth + 12))
}

export type FitResult = { zoom: number; bodyPx: number }

/** Fit one slide. `slide` is the scroll container, `inner` the content box. */
export function fitSlide(slide: HTMLElement, inner: HTMLElement): FitResult {
  if (window.innerWidth <= MOBILE_MAX) {
    inner.style.zoom = ''
    inner.style.width = ''
    return { zoom: 1, bodyPx: BASE_BODY_PX }
  }
  const availW = slide.clientWidth
  const availH = slide.clientHeight
  const target = targetBodyPx(window.innerWidth) / BASE_BODY_PX
  let z = target
  for (let k = 0; k < 6; k++) {
    inner.style.zoom = '1'
    inner.style.width = `${availW / z}px`
    const h = inner.scrollHeight
    const fitZ = availH / h
    if (fitZ >= z) break
    z = Math.max(MIN_ZOOM, fitZ)
    if (z === MIN_ZOOM) break
  }
  inner.style.width = `${availW / z}px`
  inner.style.zoom = String(z)
  return { zoom: z, bodyPx: Math.round(BASE_BODY_PX * z * 10) / 10 }
}

export function fitAll(root: ParentNode = document) {
  const out: FitResult[] = []
  root.querySelectorAll<HTMLElement>('.slide').forEach((slide) => {
    const inner = slide.querySelector<HTMLElement>('.slide-inner')
    if (inner) out.push(fitSlide(slide, inner))
  })
  return out
}
