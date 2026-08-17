import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import './index.css'
import api from './services/api'
import Screen1Register from './screens/Screen1Register'
import Screen2Onboarding from './screens/Screen2Onboarding'
import Screen2bCareerSelect from './screens/Screen2bCareerSelect'
import Screen3Dashboard from './screens/Screen3Dashboard'
import Screen4LearningPaths from './screens/Screen4LearningPaths'
import Screen5Workspace from './screens/Screen5Workspace'
import Screen6Completion from './screens/Screen6Completion'
import Screen7Community from './screens/Screen7Community'
import Screen8Profile from './screens/Screen8Profile'
import {
  LayoutDashboard, BookOpen, Briefcase, Users, User2, Palette,
  Cpu, Pen, Flame, Cloud,
} from 'lucide-react'

const MODULE_ICON_MAP = {
  'Tecnología': Cpu,
  'Negocios': Briefcase,
  'Diseño': Pen,
  'Marketing': Flame,
  'Ciberseguridad': BookOpen,
  'Cloud': Cloud,
}

// ── Nav items (only visible after login) ─────────────────────────────────────
const NAV_ITEMS = [
  { id: 3, label: 'Dashboard', Icon: LayoutDashboard },
  { id: 4, label: 'Rutas', Icon: BookOpen },
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
        borderRadius: '24px',
        padding: '8px 12px',
        display: 'flex', gap: '4px',
        boxShadow: 'var(--shadow-lg)',
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
  const [activeModule, setActiveModule] = useState(() => {
    try {
      const saved = localStorage.getItem('activeModule')
      if (!saved) return null
      const parsed = JSON.parse(saved)
      parsed.Icon = MODULE_ICON_MAP[parsed.category] || BookOpen
      return parsed
    } catch { return null }
  })
  // El perfil del oráculo vive aquí, pero NO sólo aquí: un refresh entre el
  // onboarding y la selección de carrera lo perdía y `Screen2bCareerSelect`
  // caía al fallback de 50s sin avisar. Se rehidrata de localStorage al
  // arrancar y, si no hay nada, del backend (`inferred_skills`).
  const [oracleAnswers, setOracleAnswers] = useState(() => {
    try {
      const saved = localStorage.getItem('oracleProfile')
      return saved ? JSON.parse(saved) : []
    } catch { return [] }
  })

  useEffect(() => {
    if (activeModule) {
      const { Icon, ...serializableModule } = activeModule
      localStorage.setItem('activeModule', JSON.stringify(serializableModule))
    } else {
      localStorage.removeItem('activeModule')
    }
  }, [activeModule])

  useEffect(() => {
    if (oracleAnswers?.normalizedScores) {
      localStorage.setItem('oracleProfile', JSON.stringify(oracleAnswers))
    } else {
      localStorage.removeItem('oracleProfile')
    }
  }, [oracleAnswers])

  // Si el usuario vuelve con sesión abierta pero sin perfil en local, lo
  // recuperamos del backend en vez de rehacerle el test.
  useEffect(() => {
    if (oracleAnswers?.normalizedScores) return
    if (!localStorage.getItem('token')) return

    let cancelled = false
    api.get('/api/v1/users/me')
      .then(({ data }) => {
        const stored = data?.inferred_skills
        if (!cancelled && stored && Object.keys(stored).length > 0) {
          setOracleAnswers({ normalizedScores: stored })
        }
      })
      .catch(() => { /* sin perfil guardado: el onboarding lo generará */ })

    return () => { cancelled = true }
  }, [])

  const navigate = (screenId) => setCurrentScreen(screenId)

  const handleLogout = () => {
    setActiveModule(null)
    localStorage.removeItem('activeModule')
    localStorage.removeItem('token')
    localStorage.removeItem('oracleProfile')
    setOracleAnswers([])
    setCurrentScreen(1)
  }

  const handleStartModule = (module) => {
    setActiveModule(module)
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
          onConfirm={(picks) => navigate(3)}
          onBackToOracle={() => { setOracleAnswers([]); navigate(2) }}
        />
      )
      case 3: return <Screen3Dashboard onNavigate={navigate} activeModule={activeModule} />
      case 4: return <Screen4LearningPaths onStartModule={handleStartModule} onNavigate={navigate} />
      case 5: return <Screen5Workspace onNext={() => navigate(6)} onNavigate={navigate} activeModule={activeModule} />
      case 6: return <Screen6Completion onNext={() => { setActiveModule(null); navigate(3) }} activeModule={activeModule} />
      case 7: return <Screen7Community onNavigate={navigate} />
      case 8: return <Screen8Profile onNavigate={navigate} onLogout={handleLogout} />
      default: return <Screen1Register onNext={() => navigate(2)} />
    }
  }

  const showNav = !PRE_LOGIN_SCREENS.has(currentScreen)

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', position: 'relative', paddingBottom: showNav ? '88px' : '0' }}>
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