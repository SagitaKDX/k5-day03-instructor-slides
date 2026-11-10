/** Web Audio SFX + ambient bed for the instructor deck. Default: silent until user enables. */

export type SfxKind = 'whoosh' | 'chime' | 'warn' | 'tick' | 'kickoff' | 'zero'

type AmbientState = {
  master: GainNode | null
  filter: BiquadFilterNode | null
  oscillators: OscillatorNode[]
  lfo: OscillatorNode | null
  stepTimer: number | null
  fadeCleanupTimer: number | null
  generationId: number
  noise: AudioBufferSourceNode | null
}

const NOTES = [261.63, 293.66, 329.63, 392.0, 440.0, 523.25] // C major pent-ish calm

let ctx: AudioContext | null = null
let sfxMuted = true
let musicPlaying = false
let reducedMotion = false

const ambient: AmbientState = {
  master: null,
  filter: null,
  oscillators: [],
  lfo: null,
  stepTimer: null,
  fadeCleanupTimer: null,
  generationId: 0,
  noise: null,
}

function getCtx(): AudioContext | null {
  const AC = window.AudioContext || (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
  if (!AC) return null
  if (!ctx) ctx = new AC()
  if (ctx.state === 'suspended') void ctx.resume()
  return ctx
}

export function setReducedMotion(flag: boolean) {
  reducedMotion = flag
  if (flag && musicPlaying) stopMusic()
}

export function isSfxMuted() {
  return sfxMuted
}

export function isMusicPlaying() {
  return musicPlaying
}

export function setSfxMuted(muted: boolean) {
  sfxMuted = muted
  try {
    localStorage.setItem('deck_sfx_muted', muted ? 'true' : 'false')
  } catch {
    /* ignore */
  }
}

export function loadPrefs() {
  try {
    sfxMuted = localStorage.getItem('deck_sfx_muted') !== 'false'
    // music always starts off
  } catch {
    sfxMuted = true
  }
}

function tone(
  type: OscillatorType,
  freqStart: number,
  freqEnd: number,
  dur: number,
  peak: number,
  when = 0,
) {
  const c = getCtx()
  if (!c || sfxMuted || reducedMotion) return
  const now = c.currentTime + when
  const osc = c.createOscillator()
  const gain = c.createGain()
  const filter = c.createBiquadFilter()
  osc.type = type
  osc.frequency.setValueAtTime(freqStart, now)
  osc.frequency.exponentialRampToValueAtTime(Math.max(40, freqEnd), now + dur)
  filter.type = 'lowpass'
  filter.frequency.setValueAtTime(1800, now)
  gain.gain.setValueAtTime(0.0001, now)
  gain.gain.linearRampToValueAtTime(peak, now + 0.02)
  gain.gain.exponentialRampToValueAtTime(0.0001, now + dur)
  osc.connect(filter)
  filter.connect(gain)
  gain.connect(c.destination)
  osc.start(now)
  osc.stop(now + dur + 0.02)
}

export function playSfx(kind: SfxKind) {
  if (sfxMuted || reducedMotion) return
  switch (kind) {
    case 'whoosh':
      tone('sine', 240, 520, 0.14, 0.07)
      tone('triangle', 180, 90, 0.18, 0.035, 0.01)
      break
    case 'chime':
      tone('sine', 523.25, 523.25, 0.35, 0.06)
      tone('sine', 659.25, 659.25, 0.4, 0.04, 0.04)
      break
    case 'warn':
      tone('triangle', 440, 330, 0.22, 0.05)
      break
    case 'tick':
      tone('square', 880, 660, 0.05, 0.02)
      break
    case 'kickoff':
      tone('sine', 392, 523.25, 0.2, 0.07)
      tone('sine', 523.25, 783.99, 0.28, 0.05, 0.08)
      break
    case 'zero':
      tone('sawtooth', 220, 110, 0.35, 0.04)
      tone('sine', 330, 165, 0.4, 0.045, 0.05)
      break
  }
}

function clearStepTimer() {
  if (ambient.stepTimer != null) {
    window.clearTimeout(ambient.stepTimer)
    ambient.stepTimer = null
  }
}

function clearFadeCleanup() {
  if (ambient.fadeCleanupTimer != null) {
    window.clearTimeout(ambient.fadeCleanupTimer)
    ambient.fadeCleanupTimer = null
  }
}

function destroyAmbientNodes() {
  clearStepTimer()
  try {
    ambient.oscillators.forEach((o) => o.stop())
    ambient.lfo?.stop()
    ambient.noise?.stop()
  } catch {
    /* ignore */
  }
  ambient.oscillators = []
  ambient.lfo = null
  ambient.filter = null
  ambient.master = null
  ambient.noise = null
}

function scheduleArpeggio(c: AudioContext, gen: number) {
  if (!musicPlaying || ambient.generationId !== gen || !ambient.master) return
  try {
    const t = c.currentTime
    const osc = c.createOscillator()
    const g = c.createGain()
    const f = c.createBiquadFilter()
    const freq = NOTES[Math.floor(Math.random() * NOTES.length)] * (Math.random() > 0.7 ? 0.5 : 1)
    osc.type = 'sine'
    osc.frequency.setValueAtTime(freq, t)
    f.type = 'lowpass'
    f.frequency.setValueAtTime(900, t)
    g.gain.setValueAtTime(0.0001, t)
    g.gain.linearRampToValueAtTime(0.028, t + 0.12)
    g.gain.exponentialRampToValueAtTime(0.0001, t + 2.4)
    osc.connect(f)
    f.connect(g)
    g.connect(ambient.master)
    osc.start(t)
    osc.stop(t + 2.5)
  } catch {
    /* ignore */
  }
  ambient.stepTimer = window.setTimeout(
    () => scheduleArpeggio(c, gen),
    1600 + Math.random() * 1400,
  )
}

function createNoiseBuffer(c: AudioContext) {
  const len = c.sampleRate * 2
  const buf = c.createBuffer(1, len, c.sampleRate)
  const data = buf.getChannelData(0)
  for (let i = 0; i < len; i++) data[i] = (Math.random() * 2 - 1) * 0.15
  return buf
}

export function startMusic() {
  if (reducedMotion) return
  const c = getCtx()
  if (!c) return

  clearFadeCleanup()

  // Resume during fade-out
  if (ambient.master) {
    const now = c.currentTime
    ambient.master.gain.cancelScheduledValues(now)
    ambient.master.gain.setValueAtTime(ambient.master.gain.value, now)
    ambient.master.gain.linearRampToValueAtTime(0.055, now + 0.8)
    musicPlaying = true
    if (ambient.stepTimer == null) scheduleArpeggio(c, ambient.generationId)
    return
  }

  ambient.generationId += 1
  const gen = ambient.generationId
  const now = c.currentTime
  const master = c.createGain()
  master.gain.setValueAtTime(0.0001, now)
  master.gain.linearRampToValueAtTime(0.055, now + 0.9)
  master.connect(c.destination)
  ambient.master = master

  const filter = c.createBiquadFilter()
  filter.type = 'lowpass'
  filter.frequency.setValueAtTime(420, now)
  filter.Q.setValueAtTime(0.9, now)
  filter.connect(master)
  ambient.filter = filter

  const lfo = c.createOscillator()
  const lfoGain = c.createGain()
  lfo.type = 'sine'
  lfo.frequency.setValueAtTime(0.07, now)
  lfoGain.gain.setValueAtTime(140, now)
  lfo.connect(lfoGain)
  lfoGain.connect(filter.frequency)
  lfo.start(now)
  ambient.lfo = lfo

  // Warm pad stack
  const padFreqs = [98.0, 146.83, 196.0, 246.94]
  ambient.oscillators = []
  padFreqs.forEach((f, i) => {
    const osc = c.createOscillator()
    const g = c.createGain()
    osc.type = i % 2 === 0 ? 'triangle' : 'sine'
    osc.frequency.setValueAtTime(f, now)
    g.gain.setValueAtTime(0.22 - i * 0.03, now)
    osc.connect(g)
    g.connect(filter)
    osc.start(now)
    ambient.oscillators.push(osc)
  })

  // Soft noise bed
  try {
    const noise = c.createBufferSource()
    const ng = c.createGain()
    const nf = c.createBiquadFilter()
    noise.buffer = createNoiseBuffer(c)
    noise.loop = true
    nf.type = 'lowpass'
    nf.frequency.setValueAtTime(280, now)
    ng.gain.setValueAtTime(0.018, now)
    noise.connect(nf)
    nf.connect(ng)
    ng.connect(master)
    noise.start(now)
    ambient.noise = noise
  } catch {
    ambient.noise = null
  }

  musicPlaying = true
  scheduleArpeggio(c, gen)
}

export function stopMusic() {
  if (!musicPlaying && !ambient.master) return
  musicPlaying = false
  clearStepTimer()
  const c = ctx
  if (!c || !ambient.master) {
    destroyAmbientNodes()
    return
  }
  const now = c.currentTime
  const gen = ambient.generationId
  ambient.master.gain.cancelScheduledValues(now)
  ambient.master.gain.setValueAtTime(ambient.master.gain.value, now)
  ambient.master.gain.linearRampToValueAtTime(0.0001, now + 0.8)
  clearFadeCleanup()
  ambient.fadeCleanupTimer = window.setTimeout(() => {
    if (ambient.generationId === gen && !musicPlaying) destroyAmbientNodes()
  }, 850)
}

export function toggleMusic() {
  if (musicPlaying) stopMusic()
  else startMusic()
}

export function onVisibilityChange() {
  if (!ambient.master || !ctx) return
  const now = ctx.currentTime
  if (document.hidden) {
    if (musicPlaying) {
      clearStepTimer()
      ambient.master.gain.cancelScheduledValues(now)
      ambient.master.gain.setValueAtTime(ambient.master.gain.value, now)
      ambient.master.gain.linearRampToValueAtTime(0.0001, now + 0.4)
    }
  } else if (musicPlaying) {
    ambient.master.gain.cancelScheduledValues(now)
    ambient.master.gain.setValueAtTime(ambient.master.gain.value, now)
    ambient.master.gain.linearRampToValueAtTime(0.055, now + 0.5)
    if (ambient.stepTimer == null) scheduleArpeggio(ctx, ambient.generationId)
  }
}
