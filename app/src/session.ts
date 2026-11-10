// Morning / afternoon class handling.
//
// The lab README gives the afternoon schedule (13:30 to 17:30, checkpoints at 15:00, 15:30,
// 16:00, 16:30, 17:30). The morning class runs the same 240 minutes, shifted by
// MORNING_SHIFT_HOURS. Change that one number if the morning class starts at another time.
//
// Slide content is written in afternoon times. localize() shifts every HH:MM between 13:00 and
// 18:59 for the morning class, and fills the {{SESSION}} / {{SESSION_RANGE}} tokens.

export type Session = 'morning' | 'afternoon'

/** Hour (local time) from which the deck opens as the afternoon class. */
export const AFTERNOON_FROM_HOUR = 13

/** Morning class = afternoon schedule moved this many hours earlier (13:30 to 08:30). */
export const MORNING_SHIFT_HOURS = -5

const AFTERNOON_START = '13:30'
const AFTERNOON_END = '17:30'

export const SESSION_LABEL: Record<Session, string> = {
  morning: 'Lớp sáng',
  afternoon: 'Lớp chiều',
}

const PARAM = 'ca'
const PARAM_VALUE: Record<Session, string> = { morning: 'sang', afternoon: 'chieu' }

/** Session forced by the URL (?ca=sang or ?ca=chieu), if any. */
export function sessionFromUrl(): Session | null {
  const v = new URLSearchParams(window.location.search).get(PARAM)
  if (v === PARAM_VALUE.morning) return 'morning'
  if (v === PARAM_VALUE.afternoon) return 'afternoon'
  return null
}

/** Session from the clock at the moment the deck opens. */
export function sessionFromClock(now: Date = new Date()): Session {
  return now.getHours() < AFTERNOON_FROM_HOUR ? 'morning' : 'afternoon'
}

/** Write the chosen session into the URL so a reload or a shared link keeps it. */
export function pinSessionInUrl(session: Session) {
  const url = new URL(window.location.href)
  url.searchParams.set(PARAM, PARAM_VALUE[session])
  window.history.replaceState(null, '', url)
}

export function clearSessionInUrl() {
  const url = new URL(window.location.href)
  url.searchParams.delete(PARAM)
  window.history.replaceState(null, '', url)
}

function shiftTime(hhmm: string, hours: number) {
  const [h, m] = hhmm.split(':').map(Number)
  return `${String(h + hours).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

const TIME_RE = /\b(1[3-8]):([0-5]\d)\b/g

/** Localize slide HTML or a title for a session. */
export function localize(text: string, session: Session): string {
  const shift = session === 'morning' ? MORNING_SHIFT_HOURS : 0
  const range = `${shiftTime(AFTERNOON_START, shift)} đến ${shiftTime(AFTERNOON_END, shift)}`
  let out = text
    .replaceAll('{{SESSION}}', SESSION_LABEL[session])
    .replaceAll('{{SESSION_RANGE}}', range)
  if (shift !== 0) {
    out = out.replace(TIME_RE, (_, h: string, m: string) => shiftTime(`${h}:${m}`, shift))
  }
  return out
}
