import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowRight, CheckCircle2, ChevronRight, Users, Briefcase, Target } from 'lucide-react'

const QUESTIONS = [
    {
        text: 'El equipo no se pone de acuerdo sobre la fecha de entrega. ¿Cuál es tu plan de acción?',
        answers: ['Analizar datos y proponer una fecha basada en evidencia', 'Organizar una reunión de alineación con los stakeholders'],
        icon: Users,
    },
    {
        text: 'Un cliente clave solicita un cambio de alcance de último minuto. ¿Cuál es tu respuesta inicial?',
        answers: ['Evaluar el impacto técnico y proponer una solución', 'Escuchar al cliente y gestionar las expectativas del proyecto'],
        icon: Briefcase,
    },
    {
        text: 'Te asignan liderar un proyecto ambiguo sin instrucciones claras. ¿Cómo decides arrancar?',
        answers: ['Definir un alcance preliminar y solicitar validación', 'Explorar ideas y posibles enfoques con el equipo central'],
        icon: Target,
    },
]

const FEEDBACK = [
    ['Enfoque analítico sólido. Avanza al siguiente caso.', 'Excelente enfoque colaborativo. Sigue adelante.'],
    ['Buena priorización técnica. Un paso más cerca.', 'Gran manejo de relaciones. Tu perfil se define.'],
    ['Liderazgo estructurado. Estás listo.', 'Proactividad destacada. Excelente.'],
]

export default function Screen2Onboarding({ onNext }) {
    const [cardIndex, setCardIndex] = useState(0)
    const [feedback, setFeedback] = useState(null)
    const [exitDirection, setExitDirection] = useState(0)
    const [progress, setProgress] = useState(33)
    const [disabled, setDisabled] = useState(false)
    const [answers, setAnswers] = useState([])

    const handleAnswer = (answerIdx, dir) => {
        if (disabled) return
        setDisabled(true)
        setExitDirection(dir)
        setFeedback({ text: FEEDBACK[cardIndex][answerIdx] })
        const newAnswers = [...answers, answerIdx]
        setAnswers(newAnswers)

        setTimeout(() => {
            setFeedback(null)
            if (cardIndex < QUESTIONS.length - 1) {
                setCardIndex(prev => prev + 1)
                setProgress(prev => Math.min(100, prev + 33))
                setExitDirection(0)
                setDisabled(false)
            } else {
                onNext(newAnswers)
            }
        }, 1600)
    }

    const q = QUESTIONS[cardIndex]
    const QuestionIcon = q.icon

    return (
        <div style={{
            minHeight: '100vh', background: 'var(--bg)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            padding: '40px 24px', position: 'relative',
        }}>
            {/* Inline feedback banner */}
            <AnimatePresence>
                {feedback && (
                    <motion.div
                        key="feedback"
                        initial={{ opacity: 0, y: -20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -20, scale: 0.95 }}
                        transition={{ duration: 0.3 }}
                        style={{
                            position: 'fixed', top: '40px', left: '50%',
                            transform: 'translateX(-50%)',
                            zIndex: 9999,
                            background: '#fff',
                            border: '1px solid var(--border)',
                            borderLeft: '4px solid var(--primary)',
                            borderRadius: '8px',
                            padding: '16px 24px',
                            display: 'flex', alignItems: 'center', gap: '12px',
                            boxShadow: 'var(--shadow-md)',
                            whiteSpace: 'nowrap',
                        }}
                    >
                        <CheckCircle2 size={20} color="var(--primary)" strokeWidth={2.5} />
                        <span style={{
                            fontFamily: 'Inter, sans-serif', fontWeight: 600,
                            fontSize: '1rem', color: 'var(--text-bright)',
                        }}>
                            {feedback.text}
                        </span>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Header & Progress */}
            <div style={{ width: '100%', maxWidth: '800px', marginBottom: '40px' }}>
                <h1 style={{ 
                    fontFamily: 'Outfit, sans-serif', 
                    fontSize: '2.5rem', 
                    fontWeight: 700, 
                    color: 'var(--text-bright)', 
                    textAlign: 'center', 
                    marginBottom: '12px' 
                }}>
                    Evaluación de Competencias
                </h1>
                <p style={{
                    fontFamily: 'Inter, sans-serif', 
                    fontSize: '1.1rem', 
                    color: 'var(--text-muted)', 
                    textAlign: 'center', 
                    marginBottom: '32px'
                }}>
                    Paso {cardIndex + 1} de {QUESTIONS.length} — Analizando tu perfil profesional
                </p>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <span style={{
                        fontFamily: 'Inter, sans-serif', fontWeight: 700,
                        fontSize: '0.8rem', color: 'var(--text-muted)', letterSpacing: '0.1em', textTransform: 'uppercase'
                    }}>PROGRESO</span>
                    <span style={{ fontFamily: 'Inter, sans-serif', color: 'var(--primary)', fontSize: '1rem', fontWeight: 700 }}>{progress}%</span>
                </div>
                <div style={{ background: 'var(--border)', borderRadius: '9999px', overflow: 'hidden', height: '8px' }}>
                    <motion.div
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.6, ease: 'easeOut' }}
                        style={{
                            height: '100%', borderRadius: '9999px',
                            background: 'var(--primary)'
                        }}
                    />
                </div>
            </div>

            {/* Main Content Area */}
            <div style={{ width: '100%', maxWidth: '800px', display: 'flex', flexDirection: 'column', gap: '32px' }}>
                
                {/* Question Card */}
                <div style={{ position: 'relative', minHeight: '280px' }}>
                    <AnimatePresence mode="wait">
                        <motion.div key={cardIndex}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: exitDirection > 0 ? 50 : -50 }}
                            transition={{ duration: 0.4, ease: "easeInOut" }}
                            style={{
                                position: 'absolute', inset: 0,
                                background: '#fff',
                                border: '1px solid var(--border)',
                                borderRadius: '16px',
                                boxShadow: 'var(--shadow-md)',
                                display: 'flex', flexDirection: 'column',
                                overflow: 'hidden'
                            }}
                        >
                            {/* Accent Top Bar */}
                            <div style={{ height: '6px', background: 'var(--primary)', width: '100%' }} />
                            
                            <div style={{ padding: '48px', flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '24px' }}>
                                <div style={{ 
                                    width: '64px', height: '64px', 
                                    background: '#F0F4FF', 
                                    borderRadius: '16px', 
                                    display: 'flex', alignItems: 'center', justifyContent: 'center' 
                                }}>
                                    <QuestionIcon size={32} color="var(--primary)" strokeWidth={2} />
                                </div>
                                <h2 style={{ 
                                    fontSize: '1.6rem', 
                                    lineHeight: '1.4', 
                                    color: 'var(--text-bright)', 
                                    fontFamily: 'Inter, sans-serif', 
                                    fontWeight: 600,
                                    textAlign: 'center',
                                    maxWidth: '600px'
                                }}>
                                    {q.text}
                                </h2>
                            </div>
                        </motion.div>
                    </AnimatePresence>
                </div>

                {/* Answer Buttons */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', width: '100%' }}>
                    {[
                        { color: '#fff', bg: 'var(--text-bright)', border: 'var(--text-bright)', hoverBg: 'var(--text)', dir: -1 },
                        { color: '#fff', bg: 'var(--primary)', border: 'var(--primary)', hoverBg: 'var(--primary-dim)', dir: 1 }
                    ].map(({ color, bg, border, hoverBg, dir }, i) => (
                        <motion.button key={i}
                            style={{
                                background: bg, 
                                color: color,
                                border: `1px solid ${border}`,
                                borderRadius: '12px', 
                                padding: '24px 32px',
                                fontFamily: 'Inter, sans-serif', 
                                fontWeight: 600,
                                fontSize: '1.1rem', 
                                textAlign: 'left', 
                                lineHeight: '1.5',
                                cursor: disabled ? 'default' : 'pointer',
                                boxShadow: 'var(--shadow-sm)',
                                opacity: disabled ? 0.6 : 1,
                                display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px',
                                transition: 'background-color 0.2s'
                            }}
                            whileHover={disabled ? {} : { scale: 1.02, backgroundColor: hoverBg }}
                            whileTap={disabled ? {} : { scale: 0.98 }}
                            onClick={() => handleAnswer(i, dir)}
                        >
                            <span style={{ flex: 1 }}>{q.answers[i]}</span>
                            <div style={{ 
                                width: '32px', height: '32px', 
                                background: 'rgba(255,255,255,0.2)', 
                                borderRadius: '50%', 
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                flexShrink: 0
                            }}>
                                <ChevronRight size={18} strokeWidth={2.5} />
                            </div>
                        </motion.button>
                    ))}
                </div>
            </div>
        </div>
    )
}
