import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Folder, Radio, FlaskConical, ArrowRight, CheckCircle2, ChevronRight } from 'lucide-react'

const QUESTIONS = [
    {
        text: 'El equipo no se pone de acuerdo sobre la fecha. ¿Qué haces?',
        answers: ['Analizar datos y proponer fechas', 'Organizar una reunión para alinear al equipo'],
        icon: Folder,
        color: 'var(--accent)',
        glow: 'var(--accent-glow)',
    },
    {
        text: 'Un cliente pide un cambio de último minuto. ¿Cuál es tu respuesta?',
        answers: ['Evaluar el impacto y proponer solución', 'Escuchar al cliente y gestionar expectativas'],
        icon: Radio,
        color: 'var(--primary)',
        glow: 'var(--primary-glow)',
    },
    {
        text: 'Te asignan un proyecto ambiguo sin instrucciones claras. ¿Cómo arrancas?',
        answers: ['Definir alcance y pedir claridad', 'Explorar ideas con el equipo'],
        icon: FlaskConical,
        color: 'var(--gold)',
        glow: 'var(--primary-glow)', // fallback to primary glow or similar
    },
]

const FEEDBACK = [
    ['¡Buen criterio! Avanza con confianza.', '¡Interesante perspectiva! Sigue adelante.'],
    ['¡Excelente enfoque! Un paso más cerca.', '¡Buena elección! Tu camino se despeja.'],
    ['¡Último desafío superado! Estás listo.', '¡Gran instinto profesional! Vamos.'],
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
            padding: '24px', position: 'relative',
        }}>
            {/* Warm glow */}
            <div style={{
                position: 'absolute', top: '40%', left: '50%', transform: 'translate(-50%,-50%)',
                width: '600px', height: '400px', borderRadius: '50%',
                background: 'radial-gradient(circle, var(--primary-glow) 0%, transparent 70%)',
                pointerEvents: 'none'
            }} />

            {/* Inline feedback banner — replaces XP toast */}
            <AnimatePresence>
                {feedback && (
                    <motion.div
                        key="feedback"
                        initial={{ opacity: 0, y: -14, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -14, scale: 0.95 }}
                        transition={{ duration: 0.3 }}
                        style={{
                            position: 'fixed', top: '28px', left: '50%',
                            transform: 'translateX(-50%)',
                            zIndex: 9999,
                            background: 'var(--card)',
                            border: '1px solid var(--border-accent)',
                            borderLeft: '3px solid var(--accent)',
                            borderRadius: '10px',
                            padding: '12px 22px',
                            display: 'flex', alignItems: 'center', gap: '10px',
                            boxShadow: '0 4px 24px var(--accent-glow), 0 8px 32px rgba(0,0,0,0.5)',
                            whiteSpace: 'nowrap',
                        }}
                    >
                        <CheckCircle2 size={16} color="var(--accent)" strokeWidth={2.5} />
                        <span style={{
                            fontFamily: 'Inter, sans-serif', fontWeight: 600,
                            fontSize: '0.85rem', color: 'var(--text)',
                        }}>
                            {feedback.text}
                        </span>
                        <ArrowRight size={14} color="var(--accent)" strokeWidth={2.5} />
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Progress header */}
            <div style={{ width: '100%', maxWidth: '480px', marginBottom: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <span style={{
                        fontFamily: 'Inter, sans-serif', fontWeight: 700,
                        fontSize: '0.65rem', color: 'var(--accent)', letterSpacing: '0.14em', textTransform: 'uppercase'
                    }}>&gt; ENERGÍA DEL ORÁCULO</span>
                    <span style={{ fontFamily: 'Inter, sans-serif', color: 'var(--primary)', fontSize: '0.9rem', fontWeight: 700 }}>{progress}%</span>
                </div>
                <div style={{ background: 'var(--bg2)', borderRadius: '9999px', overflow: 'hidden', height: '7px', border: '1px solid var(--border)' }}>
                    <motion.div
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.6, ease: 'easeOut' }}
                        style={{
                            height: '7px', borderRadius: '9999px',
                            background: 'linear-gradient(90deg, var(--primary), var(--accent))',
                            boxShadow: '0 0 8px var(--accent-glow)'
                        }}
                    />
                </div>
                <p style={{
                    textAlign: 'center', marginTop: '12px',
                    fontFamily: 'Inter, sans-serif', fontWeight: 600,
                    fontSize: '0.72rem', color: 'var(--text-muted)', letterSpacing: '0.06em', textTransform: 'uppercase'
                }}>
                    Pregunta {cardIndex + 1} / {QUESTIONS.length} — El Oráculo te evalúa
                </p>
            </div>

            {/* Card */}
            <div style={{ width: '100%', maxWidth: '440px', position: 'relative', height: '300px' }}>
                <AnimatePresence mode="wait">
                    <motion.div key={cardIndex}
                        initial={{ opacity: 0, y: 40, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, x: exitDirection > 0 ? 300 : -300, rotate: exitDirection > 0 ? 10 : -10, scale: 0.87 }}
                        transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
                        style={{
                            position: 'absolute', inset: 0,
                            background: 'var(--card)',
                            border: '1px solid var(--border)',
                            borderTop: `2px solid ${q.color}`,
                            borderRadius: '12px',
                            boxShadow: `0 0 24px ${q.glow}, 0 12px 40px rgba(0,0,0,0.6)`,
                            overflow: 'hidden',
                            display: 'flex', flexDirection: 'column',
                        }}
                    >
                        {/* Illustration area — icon instead of emoji */}
                        <div style={{
                            flex: '1', margin: '18px 18px 0',
                            border: '1px solid var(--border)', borderRadius: '8px',
                            background: q.glow,
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            position: 'relative', overflow: 'hidden'
                        }}>
                            <div style={{
                                position: 'absolute', inset: 0,
                                backgroundImage: `linear-gradient(${q.glow} 1px, transparent 1px), linear-gradient(90deg, ${q.glow} 1px, transparent 1px)`,
                                backgroundSize: '20px 20px'
                            }} />
                            {/* Soft glow ring */}
                            <div style={{
                                position: 'absolute',
                                width: '90px', height: '90px', borderRadius: '50%',
                                background: `radial-gradient(circle, ${q.glow} 0%, transparent 70%)`,
                                pointerEvents: 'none'
                            }} />
                            <div style={{
                                width: '52px', height: '52px', borderRadius: '14px',
                                background: q.glow,
                                border: `1.5px solid ${q.glow}`,
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                position: 'relative', zIndex: 1,
                            }}>
                                <QuestionIcon size={26} color={q.color} strokeWidth={1.8} />
                            </div>
                        </div>
                        {/* Question */}
                        <div style={{ padding: '16px 22px 20px', textAlign: 'center' }}>
                            <p style={{ fontSize: '0.9rem', lineHeight: '1.6', color: 'var(--text)', fontFamily: 'Inter, sans-serif', fontWeight: 500 }}>
                                {q.text}
                            </p>
                        </div>
                    </motion.div>
                </AnimatePresence>
            </div>

            {/* Answer Buttons */}
            <div style={{ width: '100%', maxWidth: '440px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginTop: '22px' }}>
                {[
                    { color: 'var(--accent)', bg: 'var(--accent-glow)', shadow: 'var(--accent-glow)', dir: -1 },
                    { color: 'var(--primary)', bg: 'var(--primary-glow)', shadow: 'var(--primary-glow)', dir: 1 }
                ].map(({ color, bg, shadow, dir }, i) => (
                    <motion.button key={i}
                        style={{
                            background: bg, color: color,
                            border: `1px solid ${color}`,
                            borderRadius: '10px', padding: '16px 14px',
                            fontFamily: 'Inter, sans-serif', fontWeight: 600,
                            fontSize: '0.8rem', textAlign: 'center', lineHeight: '1.5',
                            cursor: disabled ? 'default' : 'pointer',
                            boxShadow: `0 0 10px ${shadow}`,
                            opacity: disabled ? 0.5 : 1,
                            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
                        }}
                        whileHover={disabled ? {} : { boxShadow: `0 0 18px ${shadow}`, scale: 1.03 }}
                        whileTap={disabled ? {} : { scale: 0.95 }}
                        onClick={() => handleAnswer(i, dir)}
                    >
                        {q.answers[i]}
                        <ChevronRight size={14} strokeWidth={2.5} style={{ flexShrink: 0, opacity: 0.7 }} />
                    </motion.button>
                ))}
            </div>
        </div>
    )
}
