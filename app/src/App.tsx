import {
  useCallback,
  useLayoutEffect,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'
import rawSlides from './slides/content.json'
import { Maximize, Minimize, Music, NotebookText, Volume2, VolumeX } from 'lucide-react'
import logoUrl from './assets/logo-vingroup-vinuni.png'
import { fitAll } from './fit'
import {
  SESSION_LABEL,
  clearSessionInUrl,
  localize,
  pinSessionInUrl,
  sessionFromClock,
  sessionFromUrl,
  type Session,
} from './session'
import {
  isSfxMuted,
  loadPrefs,
  onVisibilityChange,
  playSfx,
  setReducedMotion,
  setSfxMuted,
  startMusic,
  stopMusic,
} from './audio/engine'

type SlideData = {
  index: number
  title: string
  html: string
  notes: string
  activeCp: string | null
  timerMin: number | null
  timerLabel: string | null
  completedThrough: number | null
}

const rawSlideData = rawSlides as SlideData[]
const CP_LIST = ['1', '2', '3', '4', '5'] as const
const CP_NAMES: Record<string, string> = {
  '1': 'Setup và v0',
  '2': 'v1 đến v3',
  '3': 'Tool và test',
  '4': 'Eval 10 case',
  '5': 'UI và report',
}

function formatTime(totalSec: number) {
  const neg = totalSec < 0
  const abs = Math.abs(totalSec)
  const m = Math.floor(abs / 60)
  const s = abs % 60
  return `${neg ? '-' : ''}${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(false)
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    const apply = () => setReduced(mq.matches)
    apply()
    mq.addEventListener('change', apply)
    return () => mq.removeEventListener('change', apply)
  }, [])
  return reduced
}

export default function App() {
  // Decided once when the deck opens; never flips mid-class.
  const [session, setSession] = useState<Session>(() => sessionFromUrl() ?? sessionFromClock())
  const [sessionPinned, setSessionPinned] = useState(() => sessionFromUrl() !== null)
  const slides = useMemo(
    () =>
      rawSlideData.map((s) => ({
        ...s,
        title: localize(s.title, session),
        html: localize(s.html, session),
        notes: localize(s.notes, session),
      })),
    [session],
  )
  useEffect(() => {
    document.documentElement.dataset.session = session
  }, [session])
  const switchSession = () => {
    const next: Session = session === 'morning' ? 'afternoon' : 'morning'
    if (next === sessionFromClock()) {
      clearSessionInUrl()
      setSessionPinned(false)
    } else {
      pinSessionInUrl(next)
      setSessionPinned(true)
    }
    setSession(next)
  }
  const [index, setIndex] = useState(0)
  const [notesOpen, setNotesOpen] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  useEffect(() => {
    const onFs = () => setIsFullscreen(Boolean(document.fullscreenElement))
    document.addEventListener('fullscreenchange', onFs)
    return () => document.removeEventListener('fullscreenchange', onFs)
  }, [])
  const [sfxOn, setSfxOn] = useState(false)
  const [musicOn, setMusicOn] = useState(false)
    const [remainSec, setRemainSec] = useState(0)
  const [timerRunning, setTimerRunning] = useState(false)
  const [timerLabel, setTimerLabel] = useState('Chưa bắt đầu')
  const [timerCp, setTimerCp] = useState<string | null>(null)
  const [totalSec, setTotalSec] = useState(0)
  const reduced = usePrefersReducedMotion()
  const touchStart = useRef<{ x: number; y: number } | null>(null)
  const warnedRef = useRef(false)
  const zeroedRef = useRef(false)
  const prevIndex = useRef(0)

  // Scale every slide toward a projector-readable text size; refit on resize and once fonts load.
  useLayoutEffect(() => {
    let timer = 0
    const fitNow = () => {
      ;(window as unknown as { __deckFit?: unknown }).__deckFit = fitAll()
    }
    const later = () => {
      window.clearTimeout(timer)
      timer = window.setTimeout(fitNow, 60)
    }
    fitNow()
    void document.fonts?.ready.then(fitNow)
    window.addEventListener('resize', later)
    return () => {
      window.clearTimeout(timer)
      window.removeEventListener('resize', later)
    }
  }, [slides])

  const current = slides[index]
  const total = slides.length

  useEffect(() => {
    loadPrefs()
    setSfxOn(!isSfxMuted())
  }, [])

  useEffect(() => {
    setReducedMotion(reduced)
    if (reduced) {
      stopMusic()
      setMusicOn(false)
    }
  }, [reduced])

  useEffect(() => {
    const onVis = () => onVisibilityChange()
    document.addEventListener('visibilitychange', onVis)
    return () => document.removeEventListener('visibilitychange', onVis)
  }, [])

  const go = useCallback(
    (next: number) => {
      setIndex(Math.max(0, Math.min(total - 1, next)))
    },
    [total],
  )

  const goToCp = useCallback(
    (cp: string | number) => {
      const key = String(cp)
      const idx = slides.findIndex((s) => s.activeCp === key)
      if (idx >= 0) go(idx)
    },
    [go, slides],
  )

  const startCpTimer = useCallback((cp: string, minutes: number, label: string) => {
    setTimerCp(cp)
    setTotalSec(minutes * 60)
    setRemainSec(minutes * 60)
    setTimerLabel(label)
    setTimerRunning(true)
    warnedRef.current = false
    zeroedRef.current = false
    playSfx('chime')
  }, [])

  const kickoffLab = useCallback(() => {
    playSfx('kickoff')
    goToCp('1')
  }, [goToCp])

  useEffect(() => {
    if (index !== prevIndex.current) {
      playSfx('whoosh')
      prevIndex.current = index
    }
  }, [index])

  useEffect(() => {
    const slide = slides[index]
    if (slide?.activeCp && slide.timerMin && slide.activeCp !== timerCp) {
      startCpTimer(
        slide.activeCp,
        slide.timerMin,
        slide.timerLabel || `CP${slide.activeCp}`,
      )
    }
  }, [index, slides, startCpTimer, timerCp])

  useEffect(() => {
    if (!timerRunning) return
    const id = window.setInterval(() => setRemainSec((s) => s - 1), 1000)
    return () => window.clearInterval(id)
  }, [timerRunning])

  useEffect(() => {
    if (remainSec === 120 && timerRunning && !warnedRef.current) {
      warnedRef.current = true
      playSfx('warn')
    }
    if (remainSec === 0 && timerRunning && !zeroedRef.current) {
      zeroedRef.current = true
      playSfx('zero')
    }
  }, [remainSec, timerRunning])

  const handleToggleSfx = () => {
    const next = !sfxOn
    setSfxOn(next)
    setSfxMuted(!next)
    if (next) playSfx('tick')
  }

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return
      const tag = (e.target as HTMLElement)?.tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA') return
      switch (e.key) {
        case 'ArrowRight':
        case ' ':
        case 'PageDown':
          e.preventDefault()
          go(index + 1)
          break
        case 'ArrowLeft':
        case 'PageUp':
          e.preventDefault()
          go(index - 1)
          break
        case 'Home':
          e.preventDefault()
          go(0)
          break
        case 'End':
          e.preventDefault()
          go(total - 1)
          break
        case 'n':
        case 'N':
          e.preventDefault()
          setNotesOpen((v) => !v)
          break
        case 'm':
        case 'M':
          e.preventDefault()
          handleToggleSfx()
          break
        case 'b':
        case 'B':
          e.preventDefault()
          if (reduced) return
          if (musicOn) {
            stopMusic()
            setMusicOn(false)
          } else {
            startMusic()
            setMusicOn(true)
          }
          break
        case 'p':
        case 'P':
          e.preventDefault()
          setTimerRunning((v) => !v)
          break
        case 'r':
        case 'R':
          e.preventDefault()
          setRemainSec(totalSec)
          warnedRef.current = false
          zeroedRef.current = false
          break
        case 'f':
        case 'F':
          e.preventDefault()
          if (!document.fullscreenElement) {
            void document.documentElement.requestFullscreen?.()
          } else {
            void document.exitFullscreen?.()
          }
          break
        default:
          break
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional key handler deps
  }, [go, index, total, totalSec, musicOn, reduced, sfxOn])

  useEffect(() => {
    ;(window as unknown as { kickoffLab?: () => void }).kickoffLab = kickoffLab
    ;(window as unknown as { goToCP?: (cp: number | string) => void }).goToCP = goToCp
    return () => {
      delete (window as unknown as { kickoffLab?: () => void }).kickoffLab
      delete (window as unknown as { goToCP?: (cp: number | string) => void }).goToCP
    }
  }, [kickoffLab, goToCp])

  const activeCp = current?.activeCp
  const completedThrough = useMemo(() => {
    if (current?.completedThrough != null) return current.completedThrough
    if (index >= total - 2) return 5
    if (activeCp != null) return Math.max(0, Number(activeCp) - 1)
    return null
  }, [activeCp, current, index, total])

  const timerClass = [
    'cp-timer-panel',
    timerRunning ? 'running' : remainSec < totalSec && remainSec > 0 ? 'paused' : '',
    remainSec < 0 ? 'overtime' : '',
    remainSec <= 120 && remainSec >= 0 && timerRunning ? 'warn' : '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <>
      <a className="skip-link" href="#deck">
        Bỏ qua thanh điều khiển
      </a>
      <header className="deck-header">
        <div className="brand">
          <img
            className="brand-logo"
            src={logoUrl}
            alt="Vingroup và VinUniversity"
            width={353}
            height={91}
          />
          <div className="brand-text">
            <span className="brand-course">AI Thực Chiến, K5 Level 3</span>
            <span className="brand-day">Day 03: Prompt Engineering và Tool Calling</span>
          </div>
        </div>

        <nav className="cp-rail" aria-label="Checkpoint">
          {CP_LIST.map((cp) => {
            const n = Number(cp)
            const state =
              activeCp === cp
                ? 'is-active'
                : (completedThrough != null && n <= completedThrough) ||
                    (activeCp != null && n < Number(activeCp))
                  ? 'is-done'
                  : ''
            return (
              <button
                key={cp}
                type="button"
                className={`cp-node ${state}`}
                aria-current={activeCp === cp ? 'step' : undefined}
                onClick={() => goToCp(cp)}
              >
                <span className="cp-id">CP{cp}</span>
                <span className="cp-name">{CP_NAMES[cp]}</span>
              </button>
            )
          })}
        </nav>

        <button
          type="button"
          className="session-switch"
          onClick={switchSession}
          title="Đổi giữa lớp sáng và lớp chiều"
        >
          <span className="session-name">{SESSION_LABEL[session]}</span>
          <span className="session-how">{sessionPinned ? 'Chọn tay' : 'Theo giờ máy'}</span>
        </button>

        <div className={timerClass} role="timer" aria-live="off">
          <span className="timer-label">{timerLabel}</span>
          <span className="timer-display">{formatTime(remainSec)}</span>
          <span className="timer-status">
            {remainSec < 0 ? 'Quá giờ' : timerRunning ? 'Đang chạy' : 'Tạm dừng'}
          </span>
          <div className="timer-actions">
            <button type="button" className="btn-ghost" onClick={() => setTimerRunning((v) => !v)}>
              {timerRunning ? 'Dừng' : 'Chạy'} <kbd>P</kbd>
            </button>
            <button
              type="button"
              className="btn-ghost"
              onClick={() => {
                setRemainSec(totalSec)
                warnedRef.current = false
                zeroedRef.current = false
              }}
            >
              Đặt lại <kbd>R</kbd>
            </button>
          </div>
        </div>

        <div className="header-actions">
          <button
            type="button"
            className="btn-icon"
            aria-pressed={sfxOn}
            aria-label="Âm báo (M)"
            title="Âm báo (M)"
            onClick={handleToggleSfx}
          >
            {sfxOn ? <Volume2 aria-hidden="true" /> : <VolumeX aria-hidden="true" />}
          </button>
          <button
            type="button"
            className="btn-icon"
            aria-pressed={musicOn}
            aria-label="Nhạc nền (B)"
            title={reduced ? 'Nhạc nền tắt khi hệ thống giảm chuyển động' : 'Nhạc nền (B)'}
            disabled={reduced}
            onClick={() => {
              if (reduced) return
              if (musicOn) {
                stopMusic()
                setMusicOn(false)
              } else {
                startMusic()
                setMusicOn(true)
              }
            }}
          >
            <Music aria-hidden="true" />
          </button>
          <button
            type="button"
            className="btn-icon"
            aria-pressed={notesOpen}
            aria-controls="speaker-notes"
            aria-label="Ghi chú giảng viên (N)"
            title="Ghi chú giảng viên (N)"
            onClick={() => setNotesOpen((v) => !v)}
          >
            <NotebookText aria-hidden="true" />
          </button>
          <button
            type="button"
            className="btn-icon"
            aria-label={isFullscreen ? 'Thoát toàn màn hình (F)' : 'Toàn màn hình (F)'}
            title={isFullscreen ? 'Thoát toàn màn hình (F)' : 'Toàn màn hình (F)'}
            onClick={() => {
              if (!document.fullscreenElement) void document.documentElement.requestFullscreen?.()
              else void document.exitFullscreen?.()
            }}
          >
            {isFullscreen ? <Minimize aria-hidden="true" /> : <Maximize aria-hidden="true" />}
          </button>
        </div>
      </header>

      <main
        id="deck"
        tabIndex={-1}
        onTouchStart={(e) => {
          const t = e.changedTouches[0]
          touchStart.current = { x: t.screenX, y: t.screenY }
        }}
        onTouchEnd={(e) => {
          if (!touchStart.current) return
          const t = e.changedTouches[0]
          const dx = t.screenX - touchStart.current.x
          const dy = t.screenY - touchStart.current.y
          if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) {
            if (dx < 0) go(index + 1)
            else go(index - 1)
          }
          touchStart.current = null
        }}
      >
        {slides.map((slide, i) => (
          <section
            key={slide.index}
            className={`slide${i === index ? ' active' : ''}`}
            aria-hidden={i !== index}
            aria-label={slide.title}
            data-index={slide.index}
          >
            <div className="slide-inner" dangerouslySetInnerHTML={{ __html: slide.html }} />
          </section>
        ))}
      </main>

      <footer className="deck-footer">
        <span className="slide-counter">
          {index + 1} / {total}
        </span>
        <div className="progress" role="tablist" aria-label="Danh sách slide">
          {slides.map((s) => (
            <button
              key={s.index}
              type="button"
              role="tab"
              aria-selected={s.index === index}
              aria-label={`Slide ${s.index + 1}: ${s.title}`}
              className={`progress-tick${s.index === index ? ' is-active' : ''}${s.index < index ? ' is-past' : ''}`}
              onClick={() => go(s.index)}
            />
          ))}
        </div>
        <div className="nav-buttons">
          <button type="button" className="btn-nav" disabled={index === 0} onClick={() => go(index - 1)}>
            Trước
          </button>
          <button
            type="button"
            className="btn-nav btn-nav--next"
            disabled={index === total - 1}
            onClick={() => go(index + 1)}
          >
            Tiếp
          </button>
        </div>
      </footer>

      <aside id="speaker-notes" className={notesOpen ? 'is-open' : ''} aria-label="Ghi chú giảng viên" aria-hidden={!notesOpen}>
        <div className="notes-header">
          <h2 className="notes-title">Ghi chú giảng viên</h2>
          <button type="button" className="btn-ghost" onClick={() => setNotesOpen(false)}>
            Đóng
          </button>
        </div>
        <p className="notes-slide">{current?.title}</p>
        <div
          className="notes-content"
          dangerouslySetInnerHTML={{
            __html: current?.notes || '<p>Slide này không có ghi chú.</p>',
          }}
        />
      </aside>
    </>
  )
}
