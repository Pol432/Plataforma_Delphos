import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import api from '../services/api'
import {
    Target, Clock, Layers, Zap, CheckCircle2, ArrowLeft,
    FileText, Send, Sparkles, BookOpen, AlertCircle,
    ChevronRight, User2
} from 'lucide-react'

// ── Floating particle
function Particle({ delay, x, y, size, color }) {
    return (
        <motion.div
            style={{ position: 'absolute', width: size, height: size, borderRadius: '50%', background: color, left: x, top: y, pointerEvents: 'none' }}
            animate={{ y: [0, -18, 0], opacity: [0.15, 0.5, 0.15] }}
            transition={{ duration: 3 + Math.random() * 2, repeat: Infinity, delay, ease: 'easeInOut' }}
        />
    )
}

const PARTICLES = Array.from({ length: 14 }, (_, i) => ({
    id: i, delay: i * 0.4,
    x: `${5 + Math.random() * 90}%`, y: `${5 + Math.random() * 90}%`,
    size: 2 + Math.random() * 3,
    color: ['var(--primary)', 'var(--accent)', 'var(--gold)'][i % 3],
}))

// ── Step type pill
function StepTypePill({ type }) {
    const configs = {
        video: { label: 'VIDEO', color: 'var(--accent)', bg: 'var(--accent-glow)' },
        lectura: { label: 'LECTURA', color: 'var(--gold)', bg: 'rgba(255,167,38,0.1)' },
        tarea: { label: 'TAREA', color: 'var(--primary)', bg: 'var(--primary-glow)' },
    }
    const c = configs[type] || configs.tarea
    return (
        <span style={{
            display: 'inline-flex', alignItems: 'center', gap: '4px',
            background: c.bg, border: `1px solid ${c.color}44`,
            borderRadius: '5px', padding: '2px 8px',
            fontFamily: 'Inter', fontSize: '0.58rem', fontWeight: 700,
            color: c.color, letterSpacing: '0.1em',
        }}>
            {c.label}
        </span>
    )
}

// ── Empty state when no active mission
function EmptyWorkspace({ onNavigate }) {
    return (
        <div style={{
            height: '100vh', background: 'var(--bg)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexDirection: 'column', gap: '20px', padding: '40px',
            textAlign: 'center', position: 'relative', overflow: 'hidden',
        }}>
            {PARTICLES.map(p => <Particle key={p.id} {...p} />)}
            <div style={{ position: 'relative', zIndex: 1 }}>
                <motion.div
                    animate={{ rotate: [0, 360] }}
                    transition={{ repeat: Infinity, duration: 20, ease: 'linear' }}
                    style={{ width: '80px', height: '80px', margin: '0 auto 20px' }}
                >
                    <svg viewBox="0 0 100 100" width="80" height="80">
                        <polygon points="50,2 93.3,26 93.3,74 50,98 6.7,74 6.7,26"
                            fill="var(--primary-glow)" stroke="var(--primary)"
                            strokeWidth="1.5" strokeDasharray="10 5" opacity="0.6" />
                    </svg>
                </motion.div>
                <Target size={32} color="var(--primary)" strokeWidth={1.5}
                    style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -70%)' }} />
            </div>
            <div style={{ position: 'relative', zIndex: 1 }}>
                <span style={{ fontSize: '0.6rem', fontFamily: 'Inter', color: 'var(--primary)', letterSpacing: '0.18em', textTransform: 'uppercase', display: 'block', marginBottom: '8px' }}>// Workspace vacío</span>
                <h2 style={{ fontFamily: 'Inter', fontWeight: 900, fontSize: '1.4rem', color: 'var(--text-bright)', marginBottom: '10px' }}>
                    Sin misión activa
                </h2>
                <p style={{ fontFamily: 'Inter', fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.6, maxWidth: '320px', marginBottom: '24px' }}>
                    Selecciona una misión desde el tablón de operaciones para activar tu espacio de trabajo.
                </p>
                <motion.button
                    whileHover={{ background: 'var(--primary-dim)', boxShadow: '0 6px 24px var(--primary-glow)' }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => onNavigate(4)}
                    style={{
                        display: 'flex', alignItems: 'center', gap: '8px',
                        background: 'var(--primary)', color: '#fff', border: 'none',
                        borderRadius: '8px', padding: '12px 22px',
                        fontFamily: 'Inter', fontWeight: 700, fontSize: '0.8rem',
                        cursor: 'pointer', letterSpacing: '0.07em', textTransform: 'uppercase',
                        boxShadow: '0 4px 18px var(--primary-glow)',
                        margin: '0 auto',
                    }}
                >
                    Ver misiones <ChevronRight size={15} strokeWidth={2.5} />
                </motion.button>
            </div>
        </div>
    )
}

// ════════════════════════════════════════════════════════════════
export default function Screen5Workspace({ onNext, onNavigate, activeMission }) {
    const [submission, setSubmission] = useState('')
    const [submitting, setSubmitting] = useState(false)
    const [submitted, setSubmitted] = useState(false)
    const [activeStep, setActiveStep] = useState(0)
    const [userData, setUserData] = useState(null)

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const res = await api.get('/api/v1/users/me')
                setUserData(res.data)
            } catch (e) {
                console.error('Error cargando usuario en workspace:', e)
            }
        }
        fetchUser()
    }, [])

    if (!activeMission) return <EmptyWorkspace onNavigate={onNavigate} />

    // Flatten all steps across all modules
    const allSteps = activeMission.modules?.flatMap((mod, mIdx) =>
        (mod.steps || []).map((step, sIdx) => ({
            ...step,
            moduleTitle: mod.title,
            moduleDuration: mod.duration,
            modIdx: mIdx,
            sIdx,
        }))
    ) || []

    const currentStep = allSteps[activeStep] || null
    const isLastStep = activeStep === allSteps.length - 1
    const isTareaStep = currentStep?.type === 'tarea'

    const handleComplete = async () => {
        if (isTareaStep && !submission.trim()) return
        setSubmitting(true)
        try {
            // Navigate to Victory screen (which will handle backend calls)
            setTimeout(() => {
                setSubmitting(false)
                onNext()
            }, 800)
        } catch (err) {
            console.error('Error al completar paso:', err)
            setSubmitting(false)
        }
    }

    const missionColor = activeMission.color || 'var(--primary)'
    const totalModules = activeMission.modules?.length || 1
    const progress = Math.round(((activeStep + 1) / Math.max(allSteps.length, 1)) * 100)

    return (
        <div style={{ height: '100vh', background: 'var(--bg)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

            {/* ── TOP NAV ── */}
            <div style={{
                height: '60px', flexShrink: 0,
                background: 'var(--bg2)', borderBottom: '1px solid var(--border)',
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '0 24px', gap: '16px',
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <motion.button
                        whileHover={{ color: 'var(--primary)' }}
                        onClick={() => onNavigate(4)}
                        style={{
                            background: 'transparent', border: 'none', cursor: 'pointer',
                            display: 'flex', alignItems: 'center', gap: '6px',
                            color: 'var(--text-muted)', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.75rem',
                        }}
                    >
                        <ArrowLeft size={15} strokeWidth={2} /> Misiones
                    </motion.button>
                    <div style={{ width: '1px', height: '20px', background: 'var(--border)' }} />
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {activeMission.Icon && <activeMission.Icon size={16} color={missionColor} strokeWidth={2} />}
                        <span style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-bright)' }}>
                            {activeMission.title}
                        </span>
                    </div>
                </div>

                {/* Progress bar */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, maxWidth: '320px' }}>
                    <span style={{ fontFamily: 'Inter', fontSize: '0.65rem', color: 'var(--text-muted)', flexShrink: 0 }}>
                        Progreso
                    </span>
                    <div style={{ flex: 1, height: '6px', background: 'var(--bg)', borderRadius: '9999px', overflow: 'hidden', border: '1px solid var(--border)' }}>
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
                            style={{ height: '100%', borderRadius: '9999px', background: `linear-gradient(90deg, ${missionColor}, var(--accent))` }}
                        />
                    </div>
                    <span style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.65rem', color: missionColor, flexShrink: 0 }}>
                        {progress}%
                    </span>
                </div>

                {/* User chip */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '8px', padding: '5px 12px' }}>
                    <User2 size={13} color="var(--text-muted)" strokeWidth={2} />
                    <span style={{ fontFamily: 'Inter', fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                        {userData?.username || '...'}
                    </span>
                    <span style={{ fontFamily: 'Inter', fontSize: '0.62rem', color: 'var(--accent)', fontWeight: 700 }}>
                        · {userData?.xp_total || 0} XP
                    </span>
                </div>
            </div>

            {/* ── BODY ── */}
            <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>

                {/* ── LEFT SIDEBAR: Steps index ── */}
                <div style={{
                    width: '280px', flexShrink: 0,
                    background: 'var(--bg2)', borderRight: '1px solid var(--border)',
                    display: 'flex', flexDirection: 'column', overflow: 'hidden',
                }}>
                    <div style={{ padding: '16px 16px 12px', borderBottom: '1px solid var(--border)' }}>
                        <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.6rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.12em' }}>
                            Contenido de la misión
                        </p>
                        <p style={{ fontFamily: 'Inter', fontSize: '0.72rem', color: 'var(--text)', marginTop: '4px' }}>
                            {totalModules} módulo{totalModules !== 1 ? 's' : ''} · {allSteps.length} pasos
                        </p>
                    </div>
                    <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
                        {activeMission.modules?.map((mod, mIdx) => (
                            <div key={mIdx} style={{ marginBottom: '8px' }}>
                                {/* Module header */}
                                <div style={{ padding: '8px 10px 6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <div style={{ width: '2px', height: '12px', background: missionColor, borderRadius: '2px', flexShrink: 0 }} />
                                    <span style={{ fontFamily: 'Inter', fontSize: '0.65rem', fontWeight: 700, color: missionColor, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                                        {mod.title}
                                    </span>
                                </div>
                                {/* Steps */}
                                {(mod.steps || []).map((step, sIdx) => {
                                    const globalIdx = allSteps.findIndex(s => s.modIdx === mIdx && s.sIdx === sIdx)
                                    const isActive = globalIdx === activeStep
                                    const isDone = globalIdx < activeStep
                                    const StepIcon = step.type === 'video' ? BookOpen : step.type === 'lectura' ? FileText : CheckCircle2
                                    return (
                                        <motion.div
                                            key={sIdx}
                                            onClick={() => setActiveStep(globalIdx)}
                                            whileHover={{ x: 2 }}
                                            style={{
                                                display: 'flex', alignItems: 'center', gap: '10px',
                                                padding: '9px 10px', borderRadius: '8px', cursor: 'pointer',
                                                background: isActive ? 'var(--primary-glow)' : 'transparent',
                                                border: isActive ? `1px solid ${missionColor}44` : '1px solid transparent',
                                                marginBottom: '2px', transition: 'all 0.15s',
                                            }}
                                        >
                                            <div style={{
                                                width: '22px', height: '22px', flexShrink: 0, borderRadius: '6px',
                                                background: isDone ? missionColor : isActive ? 'var(--bg)' : 'var(--bg)',
                                                border: `1px solid ${isDone ? missionColor : isActive ? missionColor : 'var(--border)'}`,
                                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                            }}>
                                                {isDone
                                                    ? <CheckCircle2 size={13} color="#111" strokeWidth={2.5} />
                                                    : <StepIcon size={11} color={isActive ? missionColor : 'var(--text-muted)'} strokeWidth={2} />
                                                }
                                            </div>
                                            <span style={{
                                                fontFamily: 'Inter', fontSize: '0.72rem',
                                                fontWeight: isActive ? 600 : 400,
                                                color: isActive ? 'var(--text-bright)' : isDone ? 'var(--text-muted)' : 'var(--text)',
                                                flex: 1, lineHeight: 1.3,
                                                textDecoration: isDone ? 'line-through' : 'none',
                                            }}>
                                                {step.title}
                                            </span>
                                            {isActive && (
                                                <motion.div
                                                    animate={{ opacity: [1, 0.4, 1] }}
                                                    transition={{ repeat: Infinity, duration: 1.8 }}
                                                    style={{ width: '5px', height: '5px', borderRadius: '50%', background: missionColor, flexShrink: 0 }}
                                                />
                                            )}
                                        </motion.div>
                                    )
                                })}
                            </div>
                        ))}
                    </div>
                </div>

                {/* ── MAIN CONTENT ── */}
                <div style={{ flex: 1, overflowY: 'auto', position: 'relative', background: 'var(--bg)' }}>
                    {/* BG particles */}
                    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden' }}>
                        {PARTICLES.map(p => <Particle key={p.id} {...p} />)}
                    </div>

                    <div style={{ maxWidth: '760px', margin: '0 auto', padding: '32px 28px 120px', position: 'relative', zIndex: 1 }}>

                        <AnimatePresence mode="wait">
                            {currentStep && (
                                <motion.div
                                    key={activeStep}
                                    initial={{ opacity: 0, y: 16 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -16 }}
                                    transition={{ duration: 0.25 }}
                                >
                                    {/* Step header */}
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                                        <StepTypePill type={currentStep.type} />
                                        <span style={{ fontFamily: 'Inter', fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                                            Paso {activeStep + 1} de {allSteps.length}
                                        </span>
                                    </div>
                                    <h1 style={{
                                        fontFamily: 'Inter', fontWeight: 900, fontSize: '1.5rem',
                                        color: 'var(--text-bright)', marginBottom: '6px', lineHeight: 1.2,
                                    }}>
                                        {currentStep.title}
                                    </h1>
                                    <p style={{ fontFamily: 'Inter', fontSize: '0.72rem', color: missionColor, fontWeight: 600, marginBottom: '24px' }}>
                                        {currentStep.moduleTitle}
                                    </p>

                                    {/* Step content card */}
                                    <div style={{
                                        background: 'var(--card)', border: '1px solid var(--border)',
                                        borderTop: `2px solid ${missionColor}`,
                                        borderRadius: '12px', padding: '28px', marginBottom: '20px',
                                        boxShadow: `0 0 30px ${missionColor}10`,
                                    }}>
                                        {currentStep.type === 'video' && (
                                            <div style={{ textAlign: 'center' }}>
                                                <div style={{
                                                    width: '80px', height: '80px', margin: '0 auto 18px',
                                                    borderRadius: '20px', background: 'var(--bg2)',
                                                    border: `1.5px solid var(--border)`,
                                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                    boxShadow: `0 0 20px ${missionColor}20`,
                                                }}>
                                                    <BookOpen size={36} color={missionColor} strokeWidth={1.5} />
                                                </div>
                                                <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', color: 'var(--text-bright)', marginBottom: '10px' }}>
                                                    Recurso Multimedia
                                                </h3>
                                                <p style={{ fontFamily: 'Inter', fontSize: '0.84rem', color: 'var(--text-muted)', lineHeight: 1.7, maxWidth: '480px', margin: '0 auto 20px' }}>
                                                    {currentStep.desc || 'Revisa el material multimedia de esta sección antes de avanzar al siguiente paso.'}
                                                </p>
                                                <div style={{
                                                    background: 'var(--bg)', border: '1px dashed var(--border)',
                                                    borderRadius: '10px', padding: '20px',
                                                    display: 'flex', alignItems: 'center', gap: '12px',
                                                }}>
                                                    <AlertCircle size={18} color="var(--text-muted)" strokeWidth={1.5} />
                                                    <span style={{ fontFamily: 'Inter', fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                                                        El reproductor de video estará disponible cuando el instructor cargue el contenido multimedia.
                                                    </span>
                                                </div>
                                            </div>
                                        )}

                                        {currentStep.type === 'lectura' && (
                                            <div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '18px' }}>
                                                    <div style={{
                                                        width: '48px', height: '48px', flexShrink: 0, borderRadius: '12px',
                                                        background: 'rgba(255,167,38,0.1)', border: '1px solid rgba(255,167,38,0.3)',
                                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                    }}>
                                                        <FileText size={22} color="var(--gold)" strokeWidth={1.5} />
                                                    </div>
                                                    <div>
                                                        <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.65rem', color: 'var(--gold)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '2px' }}>
                                                            Material de lectura
                                                        </p>
                                                        <p style={{ fontFamily: 'Inter', fontSize: '0.8rem', color: 'var(--text)', fontWeight: 600 }}>
                                                            {activeMission.title}
                                                        </p>
                                                    </div>
                                                </div>
                                                <p style={{ fontFamily: 'Inter', fontSize: '0.85rem', color: 'var(--text)', lineHeight: 1.8, marginBottom: '16px' }}>
                                                    {currentStep.desc || `Lee detenidamente la documentación técnica y el caso de estudio provisto para esta etapa de la simulación. Comprende el contexto antes de proceder con la ejecución práctica.`}
                                                </p>
                                                <div style={{
                                                    background: 'var(--bg)', border: '1px solid rgba(255,167,38,0.2)',
                                                    borderLeft: '3px solid var(--gold)',
                                                    borderRadius: '8px', padding: '14px 16px',
                                                }}>
                                                    <p style={{ fontFamily: 'Inter', fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                                                        💡 <strong style={{ color: 'var(--text)' }}>Consejo:</strong> Toma nota de los puntos clave. Los necesitarás en la tarea práctica.
                                                    </p>
                                                </div>
                                            </div>
                                        )}

                                        {currentStep.type === 'tarea' && (
                                            <div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                                                    <div style={{
                                                        width: '48px', height: '48px', flexShrink: 0, borderRadius: '12px',
                                                        background: 'var(--primary-glow)', border: '1px solid var(--border-accent)',
                                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                        boxShadow: '0 0 14px var(--primary-glow)',
                                                    }}>
                                                        <Zap size={22} color="var(--primary)" strokeWidth={2} />
                                                    </div>
                                                    <div>
                                                        <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.65rem', color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '2px' }}>
                                                            Misión práctica
                                                        </p>
                                                        <p style={{ fontFamily: 'Inter', fontSize: '0.82rem', color: 'var(--text)', fontWeight: 700 }}>
                                                            Tarea de entrega
                                                        </p>
                                                    </div>
                                                </div>

                                                <p style={{ fontFamily: 'Inter', fontSize: '0.85rem', color: 'var(--text)', lineHeight: 1.8, marginBottom: '20px' }}>
                                                    {currentStep.desc || `Aplica lo aprendido en esta simulación. Desarrolla tu entrega, explica tu proceso y solución al desafío planteado.`}
                                                </p>

                                                {/* Submission area */}
                                                <div style={{ marginTop: '4px' }}>
                                                    <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px' }}>
                                                        Tu entrega
                                                    </p>
                                                    <textarea
                                                        value={submission}
                                                        onChange={e => setSubmission(e.target.value)}
                                                        placeholder="Describe tu solución, proceso, decisiones tomadas y resultados obtenidos..."
                                                        rows={6}
                                                        style={{
                                                            width: '100%', background: 'var(--bg)',
                                                            border: `1px solid ${submission.trim() ? 'var(--primary)' : 'var(--border)'}`,
                                                            borderRadius: '8px', padding: '14px',
                                                            fontFamily: 'Inter', fontSize: '0.84rem',
                                                            color: 'var(--text-bright)', outline: 'none',
                                                            resize: 'vertical', lineHeight: 1.7,
                                                            boxSizing: 'border-box',
                                                            transition: 'border-color 0.2s',
                                                            boxShadow: submission.trim() ? '0 0 0 3px var(--primary-glow)' : 'none',
                                                        }}
                                                    />
                                                    <p style={{ fontFamily: 'Inter', fontSize: '0.6rem', color: 'var(--text-muted)', marginTop: '5px', textAlign: 'right' }}>
                                                        {submission.length} caracteres
                                                    </p>
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* Navigation buttons */}
                                    <div style={{ display: 'flex', gap: '10px', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <motion.button
                                            onClick={() => setActiveStep(s => Math.max(0, s - 1))}
                                            disabled={activeStep === 0}
                                            whileHover={activeStep > 0 ? { borderColor: 'var(--primary)', color: 'var(--primary)' } : {}}
                                            whileTap={{ scale: 0.97 }}
                                            style={{
                                                padding: '10px 18px', borderRadius: '8px',
                                                border: '1px solid var(--border)', background: 'transparent',
                                                fontFamily: 'Inter', fontWeight: 600, fontSize: '0.75rem',
                                                color: activeStep === 0 ? 'var(--border)' : 'var(--text-muted)',
                                                cursor: activeStep === 0 ? 'not-allowed' : 'pointer',
                                                transition: 'all 0.2s',
                                            }}
                                        >
                                            ← Anterior
                                        </motion.button>

                                        {isLastStep ? (
                                            <motion.button
                                                onClick={handleComplete}
                                                disabled={submitting || (isTareaStep && !submission.trim())}
                                                whileHover={!submitting && (!isTareaStep || submission.trim()) ? { background: 'var(--primary-dim)', boxShadow: '0 6px 28px var(--primary-glow)' } : {}}
                                                whileTap={{ scale: 0.97 }}
                                                style={{
                                                    display: 'flex', alignItems: 'center', gap: '8px',
                                                    padding: '12px 28px', borderRadius: '8px',
                                                    background: (!isTareaStep || submission.trim()) && !submitting ? 'var(--primary)' : 'var(--bg2)',
                                                    color: (!isTareaStep || submission.trim()) && !submitting ? '#fff' : 'var(--text-muted)',
                                                    border: 'none',
                                                    fontFamily: 'Inter', fontWeight: 700, fontSize: '0.82rem',
                                                    cursor: submitting || (isTareaStep && !submission.trim()) ? 'not-allowed' : 'pointer',
                                                    letterSpacing: '0.07em', textTransform: 'uppercase',
                                                    boxShadow: (!isTareaStep || submission.trim()) ? '0 4px 20px var(--primary-glow)' : 'none',
                                                    transition: 'all 0.2s',
                                                }}
                                            >
                                                {submitting
                                                    ? <><Sparkles size={15} /> Entregando...</>
                                                    : <><Send size={15} /> Completar Misión</>
                                                }
                                            </motion.button>
                                        ) : (
                                            <motion.button
                                                onClick={() => setActiveStep(s => Math.min(allSteps.length - 1, s + 1))}
                                                whileHover={{ background: 'var(--primary-dim)', boxShadow: '0 4px 18px var(--primary-glow)' }}
                                                whileTap={{ scale: 0.97 }}
                                                style={{
                                                    display: 'flex', alignItems: 'center', gap: '8px',
                                                    padding: '10px 22px', borderRadius: '8px',
                                                    background: 'var(--primary)', color: '#fff', border: 'none',
                                                    fontFamily: 'Inter', fontWeight: 700, fontSize: '0.78rem',
                                                    cursor: 'pointer', letterSpacing: '0.07em', textTransform: 'uppercase',
                                                    boxShadow: '0 4px 16px var(--primary-glow)',
                                                }}
                                            >
                                                Siguiente <ChevronRight size={14} strokeWidth={2.5} />
                                            </motion.button>
                                        )}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>

                {/* ── RIGHT SIDEBAR: Mission info ── */}
                <div style={{
                    width: '240px', flexShrink: 0,
                    background: 'var(--bg2)', borderLeft: '1px solid var(--border)',
                    padding: '20px 14px', display: 'flex', flexDirection: 'column', gap: '12px', overflowY: 'auto',
                }}>
                    {/* Mission card */}
                    <div style={{
                        background: 'var(--card)', border: `1px solid var(--border)`,
                        borderTop: `2px solid ${missionColor}`,
                        borderRadius: '10px', padding: '14px',
                    }}>
                        <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.6rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '10px' }}>
                            Misión activa
                        </p>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                            <div style={{
                                width: '36px', height: '36px', flexShrink: 0, borderRadius: '9px',
                                background: 'var(--bg)', border: `1.5px solid ${missionColor}44`,
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                            }}>
                                {activeMission.Icon && <activeMission.Icon size={18} color={missionColor} strokeWidth={1.8} />}
                            </div>
                            <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.75rem', color: 'var(--text-bright)', lineHeight: 1.3, flex: 1 }}>
                                {activeMission.title}
                            </p>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                            {[
                                [Clock, activeMission.estimatedTime || 'N/A'],
                                [Layers, `${totalModules} módulo${totalModules !== 1 ? 's' : ''}`],
                                [Zap, activeMission.xp || '+XP'],
                            ].map(([Icon, label], i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
                                    <Icon size={11} color="var(--text-muted)" strokeWidth={2} />
                                    <span style={{ fontFamily: 'Inter', fontSize: '0.68rem', color: 'var(--text-muted)' }}>{label}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Skills */}
                    {activeMission.skills?.length > 0 && (
                        <div style={{
                            background: 'var(--card)', border: '1px solid var(--border)',
                            borderRadius: '10px', padding: '14px',
                        }}>
                            <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.6rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '10px' }}>
                                Habilidades
                            </p>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                                {activeMission.skills.map((skill, i) => (
                                    <span key={i} style={{
                                        fontFamily: 'Inter', fontSize: '0.62rem', fontWeight: 600,
                                        color: missionColor, background: 'var(--bg)',
                                        border: '1px solid var(--border)', borderRadius: '5px', padding: '3px 8px',
                                    }}>
                                        {skill}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* XP reward */}
                    <div style={{
                        background: 'var(--primary-glow)', border: '1px solid var(--border)',
                        borderTop: '2px solid var(--primary)',
                        borderRadius: '10px', padding: '14px', textAlign: 'center',
                    }}>
                        <motion.div animate={{ scale: [1, 1.1, 1] }} transition={{ repeat: Infinity, duration: 2.5, ease: 'easeInOut' }}>
                            <Zap size={20} color="var(--primary)" strokeWidth={2} style={{ marginBottom: '6px' }} />
                        </motion.div>
                        <p style={{ fontFamily: 'Inter', fontWeight: 900, fontSize: '1.2rem', color: 'var(--primary)' }}>
                            {activeMission.xp || '+150 XP'}
                        </p>
                        <p style={{ fontFamily: 'Inter', fontSize: '0.6rem', color: 'var(--text-muted)', marginTop: '3px', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                            Al completar
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}