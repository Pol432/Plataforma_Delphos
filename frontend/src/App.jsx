import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import './index.css'
import Screen1Register from './screens/Screen1Register'
import Screen2Onboarding from './screens/Screen2Onboarding'
import Screen2bCareerSelect from './screens/Screen2bCareerSelect'
import Screen3Dashboard from './screens/Screen3Dashboard'
import Screen4Missions from './screens/Screen4Missions'
import Screen5Workspace from './screens/Screen5Workspace'
import Screen6Victory from './screens/Screen6Victory'
import Screen7Community from './screens/Screen7Community'
import Screen8Profile from './screens/Screen8Profile'
import {
  LayoutDashboard, Target, Briefcase, Users, User2, Palette,
  Cpu, Pen, Flame, Cloud,
} from 'lucide-react'

const MISSION_ICON_MAP = {
  'Tecnología': Cpu,
  'Negocios': Briefcase,
  'Diseño': Pen,
  'Marketing': Flame,
  'Ciberseguridad': Target,
  'Cloud': Cloud,
}

// ── Color Themes ───────────────────────────────────────────────
const THEMES = [
  { id: '1', name: 'Soft Cyberpunk', primary: '#FF4500', accent: '#00E5FF', bg: '#111111' },
  { id: '2', name: 'Magenta Noir', primary: '#E5007D', accent: '#00A9CE', bg: '#050505' },
  { id: '3', name: 'Forest Neon', primary: '#22C55E', accent: '#EF4444', bg: '#020617' },
]

// ── Theme Switcher ────────────────────────────────────────────
function ThemeSwitcher({ activeTheme, onThemeChange }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  // Close on outside click
  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const active = THEMES.find(t => t.id === activeTheme) || THEMES[0]

  return (
    <div ref={ref} style={{ position: 'fixed', top: '14px', right: '16px', zIndex: 9999 }}>
      {/* Trigger button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setOpen(o => !o)}
        title="Cambiar tema de colores"
        style={{
          display: 'flex', alignItems: 'center', gap: '7px',
          background: 'var(--bg2)',
          backdropFilter: 'blur(14px)',
          border: `1px solid var(--border)`,
          borderRadius: '12px',
          padding: '7px 13px',
          cursor: 'pointer',
          boxShadow: `0 0 14px var(--primary-glow), 0 4px 16px rgba(0,0,0,0.5)`,
          transition: 'box-shadow 0.3s ease, border-color 0.3s ease',
        }}
      >
        <Palette size={15} color="var(--primary)" />
        <span style={{
          fontFamily: 'Inter, sans-serif', fontSize: '0.62rem', fontWeight: 600,
          letterSpacing: '0.06em', textTransform: 'uppercase',
          color: 'var(--primary)',
        }}>
          {active.name}
        </span>
        {/* Color swatches preview */}
        <div style={{ display: 'flex', gap: '3px', marginLeft: '2px' }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--primary)' }} />
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--accent)' }} />
        </div>
      </motion.button>

      {/* Dropdown */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.95 }}
            transition={{ duration: 0.18, ease: 'easeOut' }}
            style={{
              position: 'absolute', top: 'calc(100% + 8px)', right: 0,
              background: 'rgba(18,18,18,0.97)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: '14px',
              padding: '8px',
              minWidth: '196px',
              boxShadow: '0 16px 40px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.04) inset',
              display: 'flex', flexDirection: 'column', gap: '4px',
            }}
          >
            <p style={{
              fontFamily: 'Inter, sans-serif', fontSize: '0.55rem', fontWeight: 700,
              letterSpacing: '0.1em', textTransform: 'uppercase',
              color: '#555', padding: '4px 8px 6px 8px',
            }}>Tema de colores</p>

            {THEMES.map(theme => {
              const isActive = theme.id === activeTheme
              return (
                <motion.button
                  key={theme.id}
                  whileHover={{ x: 3 }}
                  onClick={() => { onThemeChange(theme.id); setOpen(false) }}
                  style={{
                    display: 'flex', alignItems: 'center', gap: '10px',
                    background: isActive ? `${theme.primary}18` : 'transparent',
                    border: isActive ? `1px solid ${theme.primary}44` : '1px solid transparent',
                    borderRadius: '9px',
                    padding: '9px 11px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'background 0.15s ease',
                  }}
                >
                  {/* Mini palette preview */}
                  <div style={{ display: 'flex', gap: '3px', flexShrink: 0 }}>
                    <div style={{ width: 14, height: 24, borderRadius: '4px 0 0 4px', background: theme.bg, border: '1px solid rgba(255,255,255,0.1)' }} />
                    <div style={{ width: 14, height: 24, background: theme.primary }} />
                    <div style={{ width: 14, height: 24, borderRadius: '0 4px 4px 0', background: theme.accent }} />
                  </div>
                  <div>
                    <p style={{
                      fontFamily: 'Inter, sans-serif', fontSize: '0.72rem', fontWeight: 600,
                      color: isActive ? theme.primary : '#ccc',
                      margin: 0, lineHeight: 1.2,
                    }}>{theme.name}</p>
                    <p style={{
                      fontFamily: 'Inter, sans-serif', fontSize: '0.58rem',
                      color: '#555', margin: 0, marginTop: '1px',
                    }}>Tema {theme.id}</p>
                  </div>
                  <div style={{
                      marginLeft: 'auto', width: 6, height: 6, borderRadius: '50%',
                      background: theme.primary,
                      boxShadow: `0 0 6px ${theme.primary}aa`,
                    }} />
                </motion.button>
              )
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ── Nav items (only visible after login) ─────────────────────────────────────
const NAV_ITEMS = [
  { id: 3, label: 'Dashboard', Icon: LayoutDashboard },
  { id: 4, label: 'Misiones', Icon: Target },
  { id: 5, label: 'Workspace', Icon: Briefcase },
  { id: 7, label: 'Comunidad', Icon: Users },
  { id: 8, label: 'Perfil', Icon: User2 },
]

// screens that should NOT show the nav bar
const PRE_LOGIN_SCREENS = new Set([1, 2, 9])

// ── Bottom dock nav ───────────────────────────────────────────────────────────
function BottomNav({ current, onNavigate }) {
  return (
    <motion.div
      initial={{ y: 80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ type: 'spring', damping: 22, stiffness: 260, delay: 0.1 }}
      style={{
        position: 'fixed', bottom: '18px', left: 0, right: 0,
        zIndex: 1000,
        display: 'flex', justifyContent: 'center',
        pointerEvents: 'none',
      }}
    >
      <div style={{
        background: 'var(--bg2)',
        backdropFilter: 'blur(16px)',
        border: '1px solid var(--border)',
        borderRadius: '20px',
        padding: '6px 10px',
        display: 'flex', gap: '2px',
        boxShadow: '0 8px 32px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.04) inset',
        pointerEvents: 'auto',
      }}>
        {NAV_ITEMS.map(({ id, label, Icon }) => {
          const active = current === id
          return (
            <motion.button
              key={id}
              onClick={() => onNavigate(id)}
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.92 }}
              style={{
                display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '3px',
                padding: '8px 18px', borderRadius: '14px', border: 'none', cursor: 'pointer',
                background: active ? 'var(--primary-glow)' : 'transparent',
                position: 'relative', transition: 'background 0.2s',
              }}
            >
              {active && (
                <motion.div
                  layoutId="nav-dot"
                  style={{
                    position: 'absolute', top: '5px',
                    width: '4px', height: '4px', borderRadius: '50%',
                    background: 'var(--primary)',
                    boxShadow: '0 0 6px var(--primary-glow)',
                  }}
                />
              )}
              <Icon
                size={18}
                strokeWidth={active ? 2.5 : 1.8}
                color={active ? 'var(--primary)' : 'var(--text-muted)'}
                style={{ transition: 'color 0.2s' }}
              />
              <span style={{
                fontFamily: 'Inter, sans-serif', fontSize: '0.58rem', fontWeight: active ? 700 : 500,
                color: active ? 'var(--primary)' : 'var(--text-muted)', letterSpacing: '0.04em',
                transition: 'color 0.2s',
              }}>
                {label}
              </span>
            </motion.button>
          )
        })}
      </div>
    </motion.div>
  )
}

// ════════════════════════════════════════════════════════════════════════════════
function App() {
  const [currentScreen, setCurrentScreen] = useState(1)
  // B-03: Leer activeMission desde localStorage para persistir entre recargas
  const [activeMission, setActiveMission] = useState(() => {
    try {
      const saved = localStorage.getItem('activeMission')
      if (!saved) return null
      const parsed = JSON.parse(saved)
      parsed.Icon = MISSION_ICON_MAP[parsed.category] || Target
      return parsed
    } catch { return null }
  })
  const [oracleAnswers, setOracleAnswers] = useState([])
  const [theme, setTheme] = useState(() => localStorage.getItem('dao-theme') || '1')

  // Apply theme to <html> so CSS [data-theme] selectors work globally
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('dao-theme', theme)
  }, [theme])

  // B-03: Guardar activeMission en localStorage cada vez que cambia
  useEffect(() => {
    if (activeMission) {
      // Serializar solo los datos primitivos (sin funciones ni componentes React)
      const { Icon, ...serializableMission } = activeMission
      localStorage.setItem('activeMission', JSON.stringify(serializableMission))
    } else {
      localStorage.removeItem('activeMission')
    }
  }, [activeMission])

  const navigate = (screenId) => setCurrentScreen(screenId)

  const handleLogout = () => {
    setActiveMission(null)
    localStorage.removeItem('activeMission')
    localStorage.removeItem('token')
    setOracleAnswers([])
    setCurrentScreen(1)
  }

  const handleStartMission = (mission) => {
    setActiveMission(mission)
    navigate(5)
  }

  const renderScreen = () => {
    switch (currentScreen) {
      case 1: return <Screen1Register onNext={() => navigate(2)} />
      case 2: return (
        <Screen2Onboarding
          onNext={(answers) => { setOracleAnswers(answers); navigate(9) }}
        />
      )
      case 9: return (
        <Screen2bCareerSelect
          oracleAnswers={oracleAnswers}
          // B-04: El guardado de picks ocurre dentro de Screen2bCareerSelect
          onConfirm={(picks) => navigate(3)}
          onBackToOracle={() => { setOracleAnswers([]); navigate(2) }}
        />
      )
      case 3: return <Screen3Dashboard onNavigate={navigate} activeMission={activeMission} />
      case 4: return <Screen4Missions onStartMission={handleStartMission} onNavigate={navigate} />
      case 5: return <Screen5Workspace onNext={() => navigate(6)} onNavigate={navigate} activeMission={activeMission} />
      // B-02: Pasar activeMission a Screen6Victory para XP real y registro en backend
      case 6: return <Screen6Victory onNext={() => { setActiveMission(null); navigate(3) }} activeMission={activeMission} />
      case 7: return <Screen7Community onNavigate={navigate} />
      case 8: return <Screen8Profile onNavigate={navigate} onLogout={handleLogout} />
      default: return <Screen1Register onNext={() => navigate(2)} />
    }
  }

  const showNav = !PRE_LOGIN_SCREENS.has(currentScreen)

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', position: 'relative', paddingBottom: showNav ? '88px' : '0' }}>

      {/* Theme switcher — always visible, top-right corner */}
      <ThemeSwitcher activeTheme={theme} onThemeChange={setTheme} />

      {renderScreen()}

      <AnimatePresence>
        {showNav && (
          <BottomNav current={currentScreen} onNavigate={navigate} />
        )}
      </AnimatePresence>
    </div>
  )
}

export default App;