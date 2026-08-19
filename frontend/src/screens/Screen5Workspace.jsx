import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import api from '../services/api'
import {
    Target, Clock, Layers, Zap, CheckCircle2, ArrowLeft,
    FileText, Send, Sparkles, BookOpen, AlertCircle,
    ChevronRight, User2
} from 'lucide-react'

// ── Step type pill
function StepTypePill({ type }) {
    const configs = {
        video: { label: 'VIDEO', color: 'var(--primary)', bg: 'rgba(59, 130, 246, 0.1)' },
        lectura: { label: 'LECTURA', color: '#10B981', bg: 'rgba(16, 185, 129, 0.1)' },
        tarea: { label: 'LABORATORIO', color: '#F59E0B', bg: 'rgba(245, 158, 11, 0.1)' },
    }
    const c = configs[type] || configs.tarea
    return (
        <span style={{
            display: 'inline-flex', alignItems: 'center', gap: '6px',
            background: c.bg, borderRadius: '4px', padding: '4px 10px',
            fontFamily: 'Inter', fontSize: '0.75rem', fontWeight: 600,
            color: c.color, textTransform: 'uppercase'
        }}>
            {c.label}
        </span>
    )
}

// ── Empty state when no active mission
function EmptyWorkspace({ onNavigate }) {
    return (
        <div style={{
            height: '100vh', background: '#f8f9fa',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexDirection: 'column', gap: '24px', padding: '40px',
            textAlign: 'center'
        }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
                <Target size={40} color="var(--primary)" />
            </div>
            <div>
                <h2 style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 700, fontSize: '2rem', color: 'var(--text-bright)', marginBottom: '12px' }}>
                    Tu Espacio de Trabajo
                </h2>
                <p style={{ fontFamily: 'Inter', fontSize: '1.05rem', color: 'var(--text-muted)', lineHeight: 1.6, maxWidth: '400px', margin: '0 auto' }}>
                    Aún no has iniciado ninguna ruta. Selecciona un curso desde el catálogo para activar tu espacio de aprendizaje.
                </p>
            </div>
            <motion.button
                whileHover={{ background: 'var(--primary-dim)' }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onNavigate(4)}
                style={{
                    display: 'flex', alignItems: 'center', gap: '8px',
                    background: 'var(--primary)', color: '#fff', border: 'none',
                    borderRadius: '4px', padding: '14px 28px',
                    fontFamily: 'Inter', fontWeight: 600, fontSize: '1rem',
                    cursor: 'pointer', marginTop: '16px', transition: 'background 0.2s'
                }}
            >
                Explorar catálogo
            </motion.button>
        </div>
    )
}

// ════════════════════════════════════════════════════════════════
export default function Screen5Workspace({ onNext, onNavigate, activeModule }) {
    const [submission, setSubmission] = useState('')
    const [submitting, setSubmitting] = useState(false)
    const [submitError, setSubmitError] = useState(null)
    const [activeStep, setActiveStep] = useState(0)
    const [userData, setUserData] = useState(null)
    // Módulos y tareas reales del backend. `null` = todavía cargando; `[]` =
    // esta simulación no tiene contenido propio y se usa el temario de relleno.
    const [dbModules, setDbModules] = useState(null)

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

    // `GET /simulaciones` no devuelve módulos (SimulationOut no tiene ese
    // campo), así que hay que pedirlos aparte. Sin esto los pasos vienen del
    // temario de relleno, que no trae `task_id` y no se puede enviar nada.
    useEffect(() => {
        const simId = activeModule?.id
        if (!simId) return
        let cancelled = false

        const fetchContent = async () => {
            try {
                const modRes = await api.get('/api/v1/modules', { params: { simulation_id: simId } })
                const mods = modRes.data || []
                const withTasks = await Promise.all(
                    mods.map(async (m) => {
                        const taskRes = await api.get('/api/v1/tasks', { params: { module_id: m.id } })
                        return { ...m, tasks: taskRes.data || [] }
                    })
                )
                if (!cancelled) setDbModules(withTasks)
            } catch (e) {
                console.error('Error cargando módulos/tareas de la simulación:', e)
                if (!cancelled) setDbModules([])
            }
        }
        fetchContent()

        return () => { cancelled = true }
    }, [activeModule?.id])

    // Cada paso lleva su propia respuesta: al cambiar de paso se limpia el
    // textarea y el error, si no el texto de una tarea se arrastra a la siguiente.
    useEffect(() => {
        setSubmission('')
        setSubmitError(null)
    }, [activeStep])

    if (!activeModule) return <EmptyWorkspace onNavigate={onNavigate} />

    // Los módulos reales mandan sobre el temario de relleno: son los únicos que
    // traen `task_id`, que es lo que permite enviar la respuesta. La descripción
    // del módulo se muestra como lectura previa y cada tarea es un paso enviable.
    const realModules = (dbModules || []).length
        ? dbModules.map(m => ({
            title: m.title,
            duration: m.duration || '1h',
            steps: [
                { type: 'lectura', title: m.title, desc: m.description },
                ...(m.tasks || []).map(t => ({
                    type: 'tarea',
                    title: t.title,
                    desc: t.description,
                    taskId: t.id,
                })),
            ],
        }))
        : null

    const displayModules = realModules || activeModule.modules || []

    // Flatten all steps across all modules
    const allSteps = displayModules.flatMap((mod, mIdx) =>
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

    // Envía la respuesta de la tarea actual. Devuelve true si se puede avanzar.
    // Los pasos sin `taskId` (temario de relleno) no tienen nada que enviar.
    const submitCurrentTask = async () => {
        if (!isTareaStep || !currentStep?.taskId) return true
        try {
            await api.post(
                `/api/v1/simulaciones/${activeModule.id}/tasks/${currentStep.taskId}/submit`,
                { response: submission }
            )
            setSubmitError(null)
            return true
        } catch (err) {
            console.error('Error al enviar la respuesta:', err)
            setSubmitError(
                'No pudimos guardar tu respuesta. Revisa tu conexión y vuelve a intentarlo.'
            )
            return false
        }
    }

    const goToNextStep = () => setActiveStep(s => Math.min(allSteps.length - 1, s + 1))

    // Avanzar de paso también envía: si sólo enviara el último, las tareas
    // intermedias se perderían igual que antes.
    const handleAdvance = async () => {
        if (isTareaStep && !submission.trim()) return
        setSubmitting(true)
        const ok = await submitCurrentTask()
        setSubmitting(false)
        if (ok) goToNextStep()
    }

    const handleComplete = async () => {
        if (isTareaStep && !submission.trim()) return
        setSubmitting(true)
        const ok = await submitCurrentTask()
        setSubmitting(false)
        if (ok) onNext()
    }

    // Salida de emergencia: si el envío falla, el estudiante no se queda
    // atrapado en la pantalla, pero sólo tras haberlo intentado y con el aviso
    // delante — nunca en silencio.
    const handleSkipAfterError = () => {
        setSubmitError(null)
        if (isLastStep) onNext()
        else goToNextStep()
    }

    const missionColor = 'var(--primary)'
    const totalModules = activeModule.modules?.length || 1
    const progress = Math.round(((activeStep + 1) / Math.max(allSteps.length, 1)) * 100)

    return (
        <div style={{ height: '100vh', background: '#f8f9fa', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

            {/* ── TOP NAV ── */}
            <div style={{
                height: '72px', flexShrink: 0,
                background: '#fff', borderBottom: '1px solid var(--border)',
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '0 32px', gap: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
                    <motion.button
                        whileHover={{ color: 'var(--primary)' }}
                        onClick={() => onNavigate(4)}
                        style={{
                            background: 'transparent', border: 'none', cursor: 'pointer',
                            display: 'flex', alignItems: 'center', gap: '8px',
                            color: 'var(--text-muted)', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.95rem',
                        }}
                    >
                        <ArrowLeft size={18} /> Volver
                    </motion.button>
                    <div style={{ width: '1px', height: '32px', background: 'var(--border)' }} />
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        {activeModule.Icon && <activeModule.Icon size={20} color={missionColor} strokeWidth={1.5} />}
                        <span style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-bright)' }}>
                            {activeModule.title}
                        </span>
                    </div>
                </div>

                {/* Progress bar */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: 1, maxWidth: '400px' }}>
                    <span style={{ fontFamily: 'Inter', fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                        Progreso del curso
                    </span>
                    <div style={{ flex: 1, height: '8px', background: '#f0f2f5', borderRadius: '4px', overflow: 'hidden' }}>
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
                            style={{ height: '100%', background: missionColor }}
                        />
                    </div>
                    <span style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: '0.9rem', color: missionColor }}>
                        {progress}%
                    </span>
                </div>

                {/* User chip */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: '#f8f9fa', border: '1px solid var(--border)', borderRadius: '4px', padding: '8px 16px' }}>
                    <User2 size={16} color="var(--text-muted)" />
                    <span style={{ fontFamily: 'Inter', fontSize: '0.9rem', color: 'var(--text-bright)', fontWeight: 600 }}>
                        {userData?.username || 'Estudiante'}
                    </span>
                </div>
            </div>

            {/* ── BODY ── */}
            <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>

                {/* ── LEFT SIDEBAR: Steps index ── */}
                <div style={{
                    width: '320px', flexShrink: 0,
                    background: '#fff', borderRight: '1px solid var(--border)',
                    display: 'flex', flexDirection: 'column', overflow: 'hidden',
                }}>
                    <div style={{ padding: '24px', borderBottom: '1px solid var(--border)' }}>
                        <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', color: 'var(--text-bright)', marginBottom: '8px' }}>
                            Contenido
                        </h3>
                        <p style={{ fontFamily: 'Inter', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                            {totalModules} sección{totalModules !== 1 ? 'es' : ''} · {allSteps.length} lecciones
                        </p>
                    </div>
                    <div style={{ flex: 1, overflowY: 'auto', padding: '16px 24px' }}>
                        {activeModule.modules?.map((mod, mIdx) => (
                            <div key={mIdx} style={{ marginBottom: '24px' }}>
                                {/* Module header */}
                                <div style={{ marginBottom: '12px' }}>
                                    <span style={{ fontFamily: 'Inter', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                                        Sección {mIdx + 1}
                                    </span>
                                    <h4 style={{ fontFamily: 'Inter', fontSize: '1rem', fontWeight: 600, color: 'var(--text-bright)', marginTop: '4px' }}>
                                        {mod.title}
                                    </h4>
                                </div>
                                {/* Steps */}
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                    {(mod.steps || []).map((step, sIdx) => {
                                        const globalIdx = allSteps.findIndex(s => s.modIdx === mIdx && s.sIdx === sIdx)
                                        const isActive = globalIdx === activeStep
                                        const isDone = globalIdx < activeStep
                                        const StepIcon = step.type === 'video' ? BookOpen : step.type === 'lectura' ? FileText : CheckCircle2
                                        
                                        return (
                                            <motion.div
                                                key={sIdx}
                                                onClick={() => setActiveStep(globalIdx)}
                                                style={{
                                                    display: 'flex', alignItems: 'center', gap: '12px',
                                                    padding: '12px 16px', borderRadius: '4px', cursor: 'pointer',
                                                    background: isActive ? 'rgba(59, 130, 246, 0.05)' : '#f8f9fa',
                                                    border: isActive ? `1px solid var(--primary)` : '1px solid var(--border)',
                                                    transition: 'all 0.2s',
                                                }}
                                            >
                                                <div style={{
                                                    width: '24px', height: '24px', flexShrink: 0, borderRadius: '50%',
                                                    background: isDone ? missionColor : '#fff',
                                                    border: `1px solid ${isDone ? missionColor : 'var(--border)'}`,
                                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                }}>
                                                    {isDone
                                                        ? <CheckCircle2 size={14} color="#fff" strokeWidth={2.5} />
                                                        : <StepIcon size={12} color={isActive ? missionColor : 'var(--text-muted)'} strokeWidth={2} />
                                                    }
                                                </div>
                                                <span style={{
                                                    fontFamily: 'Inter', fontSize: '0.9rem',
                                                    fontWeight: isActive ? 600 : 500,
                                                    color: isActive ? 'var(--text-bright)' : 'var(--text-muted)',
                                                    flex: 1, lineHeight: 1.3,
                                                }}>
                                                    {step.title}
                                                </span>
                                            </motion.div>
                                        )
                                    })}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* ── MAIN CONTENT ── */}
                <div style={{ flex: 1, overflowY: 'auto', position: 'relative', background: '#f8f9fa' }}>
                    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '48px', position: 'relative', zIndex: 1 }}>

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
                                    <div style={{ marginBottom: '32px' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
                                            <StepTypePill type={currentStep.type} />
                                            <span style={{ fontFamily: 'Inter', fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                                                Lección {activeStep + 1} de {allSteps.length}
                                            </span>
                                        </div>
                                        <h1 style={{
                                            fontFamily: 'Outfit, sans-serif', fontWeight: 700, fontSize: '2.5rem',
                                            color: 'var(--text-bright)', marginBottom: '12px', lineHeight: 1.2,
                                        }}>
                                            {currentStep.title}
                                        </h1>
                                        <p style={{ fontFamily: 'Inter', fontSize: '1.1rem', color: 'var(--text-muted)' }}>
                                            {currentStep.moduleTitle}
                                        </p>
                                    </div>

                                    {/* Step content card */}
                                    <div style={{
                                        background: '#fff', border: '1px solid var(--border)',
                                        borderRadius: '8px', padding: '48px', marginBottom: '32px',
                                        boxShadow: '0 4px 12px rgba(0,0,0,0.02)',
                                    }}>
                                        {currentStep.type === 'video' && (
                                            <div style={{ textAlign: 'center' }}>
                                                <div style={{
                                                    width: '96px', height: '96px', margin: '0 auto 24px',
                                                    borderRadius: '50%', background: 'rgba(59, 130, 246, 0.1)',
                                                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                                                }}>
                                                    <BookOpen size={40} color="var(--primary)" />
                                                </div>
                                                <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.4rem', color: 'var(--text-bright)', marginBottom: '16px' }}>
                                                    Recurso Multimedia
                                                </h3>
                                                <p style={{ fontFamily: 'Inter', fontSize: '1.1rem', color: 'var(--text-muted)', lineHeight: 1.6, maxWidth: '600px', margin: '0 auto 32px' }}>
                                                    {currentStep.desc || 'Revisa el material multimedia de esta sección antes de avanzar al siguiente paso.'}
                                                </p>
                                                <div style={{
                                                    background: '#f8f9fa', border: '1px solid var(--border)',
                                                    borderRadius: '4px', padding: '24px',
                                                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px',
                                                }}>
                                                    <AlertCircle size={20} color="var(--text-muted)" />
                                                    <span style={{ fontFamily: 'Inter', fontSize: '1rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                                                        El reproductor de video estará disponible próximamente.
                                                    </span>
                                                </div>
                                            </div>
                                        )}

                                        {currentStep.type === 'lectura' && (
                                            <div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
                                                    <div style={{
                                                        width: '56px', height: '56px', flexShrink: 0, borderRadius: '50%',
                                                        background: 'rgba(16, 185, 129, 0.1)',
                                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                    }}>
                                                        <FileText size={28} color="#10B981" />
                                                    </div>
                                                    <div>
                                                        <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.9rem', color: '#10B981', textTransform: 'uppercase', marginBottom: '4px' }}>
                                                            Material de lectura
                                                        </p>
                                                        <p style={{ fontFamily: 'Inter', fontSize: '1.2rem', color: 'var(--text-bright)', fontWeight: 600 }}>
                                                            {activeModule.title}
                                                        </p>
                                                    </div>
                                                </div>
                                                <p style={{ fontFamily: 'Inter', fontSize: '1.1rem', color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '32px' }}>
                                                    {currentStep.desc || `Lee detenidamente la documentación técnica y el caso de estudio provisto para esta etapa de la simulación. Comprende el contexto antes de proceder con la ejecución práctica.`}
                                                </p>
                                                <div style={{
                                                    background: '#f8f9fa', borderLeft: '4px solid #10B981',
                                                    borderRadius: '4px', padding: '20px 24px',
                                                }}>
                                                    <p style={{ fontFamily: 'Inter', fontSize: '1rem', color: 'var(--text-bright)', lineHeight: 1.6 }}>
                                                        <strong>Nota importante:</strong> Toma apuntes de los conceptos clave, ya que serán evaluados en el laboratorio práctico.
                                                    </p>
                                                </div>
                                            </div>
                                        )}

                                        {currentStep.type === 'tarea' && (
                                            <div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
                                                    <div style={{
                                                        width: '56px', height: '56px', flexShrink: 0, borderRadius: '50%',
                                                        background: 'rgba(245, 158, 11, 0.1)',
                                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                    }}>
                                                        <Zap size={28} color="#F59E0B" />
                                                    </div>
                                                    <div>
                                                        <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.9rem', color: '#F59E0B', textTransform: 'uppercase', marginBottom: '4px' }}>
                                                            Laboratorio
                                                        </p>
                                                        <p style={{ fontFamily: 'Inter', fontSize: '1.2rem', color: 'var(--text-bright)', fontWeight: 600 }}>
                                                            Evaluación práctica
                                                        </p>
                                                    </div>
                                                </div>

                                                <p style={{ fontFamily: 'Inter', fontSize: '1.1rem', color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '32px' }}>
                                                    {currentStep.desc || `Aplica lo aprendido en esta lección. Desarrolla tu entrega explicando el proceso y la solución al desafío planteado.`}
                                                </p>

                                                {/* Submission area */}
                                                <div>
                                                    <label style={{ display: 'block', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-bright)', marginBottom: '12px' }}>
                                                        Tu respuesta
                                                    </label>
                                                    <textarea
                                                        value={submission}
                                                        onChange={e => setSubmission(e.target.value)}
                                                        placeholder="Escribe tu solución detallada aquí..."
                                                        rows={8}
                                                        style={{
                                                            width: '100%', background: '#fff',
                                                            border: `1px solid ${submission.trim() ? 'var(--primary)' : 'var(--border)'}`,
                                                            borderRadius: '4px', padding: '20px',
                                                            fontFamily: 'Inter', fontSize: '1rem',
                                                            color: 'var(--text-bright)', outline: 'none',
                                                            resize: 'vertical', lineHeight: 1.6,
                                                            boxSizing: 'border-box',
                                                            transition: 'border-color 0.2s',
                                                        }}
                                                    />
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* Aviso de fallo de envío: el botón principal reintenta,
                                        y hay una salida explícita para no bloquear al estudiante. */}
                                    {submitError && (
                                        <div style={{
                                            display: 'flex', alignItems: 'flex-start', gap: '12px',
                                            background: 'rgba(239, 68, 68, 0.08)',
                                            border: '1px solid rgba(239, 68, 68, 0.3)',
                                            borderRadius: '4px', padding: '16px 20px', marginBottom: '20px',
                                        }}>
                                            <AlertCircle size={20} color="#EF4444" style={{ flexShrink: 0, marginTop: '2px' }} />
                                            <div>
                                                <p style={{ fontFamily: 'Inter', fontSize: '0.95rem', color: 'var(--text-bright)', lineHeight: 1.5 }}>
                                                    {submitError}
                                                </p>
                                                <button
                                                    onClick={handleSkipAfterError}
                                                    style={{
                                                        marginTop: '8px', background: 'none', border: 'none', padding: 0,
                                                        fontFamily: 'Inter', fontSize: '0.9rem', fontWeight: 600,
                                                        color: '#EF4444', cursor: 'pointer', textDecoration: 'underline',
                                                    }}
                                                >
                                                    Continuar sin guardar esta respuesta
                                                </button>
                                            </div>
                                        </div>
                                    )}

                                    {/* Navigation buttons */}
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <motion.button
                                            onClick={() => setActiveStep(s => Math.max(0, s - 1))}
                                            disabled={activeStep === 0}
                                            whileHover={activeStep > 0 ? { background: '#f0f2f5' } : {}}
                                            whileTap={{ scale: 0.98 }}
                                            style={{
                                                padding: '12px 24px', borderRadius: '4px',
                                                border: '1px solid var(--border)', background: '#fff',
                                                fontFamily: 'Inter', fontWeight: 600, fontSize: '0.95rem',
                                                color: activeStep === 0 ? 'var(--text-muted)' : 'var(--text-bright)',
                                                cursor: activeStep === 0 ? 'not-allowed' : 'pointer',
                                                transition: 'all 0.2s',
                                                opacity: activeStep === 0 ? 0.5 : 1
                                            }}
                                        >
                                            Anterior
                                        </motion.button>

                                        {isLastStep ? (
                                            <motion.button
                                                onClick={handleComplete}
                                                disabled={submitting || (isTareaStep && !submission.trim())}
                                                whileHover={!submitting && (!isTareaStep || submission.trim()) ? { background: 'var(--primary-dim)' } : {}}
                                                whileTap={{ scale: 0.98 }}
                                                style={{
                                                    display: 'flex', alignItems: 'center', gap: '8px',
                                                    padding: '14px 32px', borderRadius: '4px',
                                                    background: (!isTareaStep || submission.trim()) && !submitting ? 'var(--primary)' : '#f0f2f5',
                                                    color: (!isTareaStep || submission.trim()) && !submitting ? '#fff' : 'var(--text-muted)',
                                                    border: 'none',
                                                    fontFamily: 'Inter', fontWeight: 600, fontSize: '1rem',
                                                    cursor: submitting || (isTareaStep && !submission.trim()) ? 'not-allowed' : 'pointer',
                                                    transition: 'all 0.2s',
                                                }}
                                            >
                                                {submitting ? 'Enviando...' : 'Completar curso'}
                                            </motion.button>
                                        ) : (
                                            <motion.button
                                                onClick={handleAdvance}
                                                disabled={submitting || (isTareaStep && !submission.trim())}
                                                whileHover={!submitting && (!isTareaStep || submission.trim()) ? { background: 'var(--primary-dim)' } : {}}
                                                whileTap={{ scale: 0.98 }}
                                                style={{
                                                    display: 'flex', alignItems: 'center', gap: '8px',
                                                    padding: '14px 32px', borderRadius: '4px',
                                                    background: (!isTareaStep || submission.trim()) && !submitting ? 'var(--primary)' : '#f0f2f5',
                                                    color: (!isTareaStep || submission.trim()) && !submitting ? '#fff' : 'var(--text-muted)',
                                                    border: 'none',
                                                    fontFamily: 'Inter', fontWeight: 600, fontSize: '1rem',
                                                    cursor: submitting || (isTareaStep && !submission.trim()) ? 'not-allowed' : 'pointer',
                                                    transition: 'all 0.2s'
                                                }}
                                            >
                                                {submitting ? 'Enviando...' : <>Siguiente lección <ChevronRight size={18} /></>}
                                            </motion.button>
                                        )}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </div>
        </div>
    )
}
