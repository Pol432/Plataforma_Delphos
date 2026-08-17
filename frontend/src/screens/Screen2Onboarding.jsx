import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowRight, CheckCircle2, ChevronRight, Brain, RotateCcw } from 'lucide-react'
import { questionBank, shuffleQuestions } from '../data/questionBank'

export default function Screen2Onboarding({ onNext }) {
    const [allQuestions, setAllQuestions] = useState([])
    const [activeQuestions, setActiveQuestions] = useState([])
    const [currentIndex, setCurrentIndex] = useState(0)
    
    // Scores
    const [scores, setScores] = useState({
        analytical: 0,
        creative: 0,
        social: 0,
        linguistic: 0,
        hands_on: 0
    })

    const [disabled, setDisabled] = useState(false)
    const [exitDirection, setExitDirection] = useState(0)

    // On mount, shuffle and pick the first 10
    useEffect(() => {
        const shuffled = shuffleQuestions(questionBank)
        setAllQuestions(shuffled)
        setActiveQuestions(shuffled.slice(0, 10))
    }, [])

    const handleAnswer = (option) => {
        if (disabled) return
        setDisabled(true)
        setExitDirection(-1)

        // Add weights to scores
        const newScores = { ...scores }
        for (const [trait, weight] of Object.entries(option.weights || {})) {
            newScores[trait] += weight
        }
        setScores(newScores)

        setTimeout(() => {
            setCurrentIndex(prev => prev + 1)
            setExitDirection(0)
            setDisabled(false)
        }, 500)
    }

    const handleRefine = () => {
        // Load 5 more questions
        const currentCount = activeQuestions.length
        const nextQuestions = allQuestions.slice(currentCount, currentCount + 5)
        
        if (nextQuestions.length === 0) {
            alert("Has respondido todas las preguntas disponibles.")
            return
        }

        setActiveQuestions(prev => [...prev, ...nextQuestions])
    }

    const handleAccept = () => {
        // Normalize scores to 0-100 based on max possible or relative to max
        // To normalize properly without knowing max possible easily, we can find the max score achieved,
        // and scale so that the highest is 95, or we can just scale by total points.
        // Let's do a relative scaling: the highest trait gets 95, others proportional.
        // If all 0, default to 50.
        const maxScore = Math.max(...Object.values(scores), 1)
        const normalized = {
            analytical_score: Math.round((scores.analytical / maxScore) * 95) || 10,
            creative_score: Math.round((scores.creative / maxScore) * 95) || 10,
            social_score: Math.round((scores.social / maxScore) * 95) || 10,
            linguistic_score: Math.round((scores.linguistic / maxScore) * 95) || 10,
            hands_on_score: Math.round((scores.hands_on / maxScore) * 95) || 10,
        }

        onNext({ normalizedScores: normalized })
    }

    // --- RENDER PROFILE REVIEW ---
    if (currentIndex >= activeQuestions.length && activeQuestions.length > 0) {
        // Find top traits for display
        const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1])
        const maxScore = sorted[0][1] || 1

        const labels = {
            analytical: 'Analítico & Lógico',
            creative: 'Creativo & Diseño',
            social: 'Social & Liderazgo',
            linguistic: 'Lingüístico & Comunicación',
            hands_on: 'Práctico & Físico'
        }

        return (
            <div style={{ minHeight: '100vh', background: 'var(--bg)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 24px' }}>
                <div style={{ width: '100%', maxWidth: '600px', background: '#fff', padding: '40px', borderRadius: '16px', boxShadow: 'var(--shadow-md)', border: '1px solid var(--border)' }}>
                    <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                        <Brain size={48} color="var(--primary)" style={{ marginBottom: '16px' }} />
                        <h1 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '2rem', fontWeight: 700, color: 'var(--text-bright)' }}>Tu Perfil Delphos</h1>
                        <p style={{ fontFamily: 'Inter, sans-serif', color: 'var(--text-muted)', marginTop: '8px' }}>Basado en tus respuestas, este es tu mapa de afinidad profesional.</p>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginBottom: '40px' }}>
                        {sorted.map(([key, val]) => {
                            const pct = Math.round((val / maxScore) * 100)
                            return (
                                <div key={key}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontFamily: 'Inter', fontSize: '0.9rem', fontWeight: 600, color: 'var(--text)' }}>
                                        <span>{labels[key]}</span>
                                        <span>{pct}%</span>
                                    </div>
                                    <div style={{ height: '8px', background: 'var(--border)', borderRadius: '4px', overflow: 'hidden' }}>
                                        <motion.div 
                                            initial={{ width: 0 }} 
                                            animate={{ width: `${pct}%` }} 
                                            transition={{ duration: 1, ease: 'easeOut' }}
                                            style={{ height: '100%', background: 'var(--primary)', borderRadius: '4px' }} 
                                        />
                                    </div>
                                </div>
                            )
                        })}
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <button onClick={handleAccept} style={{ width: '100%', padding: '16px', background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: '8px', fontFamily: 'Inter', fontWeight: 600, fontSize: '1.1rem', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', transition: 'background 0.2s' }}>
                            Continuar a selección de carreras <ArrowRight size={20} />
                        </button>
                        
                        {activeQuestions.length < allQuestions.length && (
                            <button onClick={handleRefine} style={{ width: '100%', padding: '16px', background: 'transparent', color: 'var(--primary)', border: '1px solid var(--primary)', borderRadius: '8px', fontFamily: 'Inter', fontWeight: 600, fontSize: '1rem', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', transition: 'background 0.2s' }}>
                                <RotateCcw size={18} /> No estoy conforme, quiero refinar mi perfil
                            </button>
                        )}
                    </div>
                </div>
            </div>
        )
    }

    // --- RENDER TEST QUESTIONS ---
    const q = activeQuestions[currentIndex]
    if (!q) return null // loading state

    const progress = Math.round((currentIndex / activeQuestions.length) * 100)

    return (
        <div style={{
            minHeight: '100vh', background: 'var(--bg)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            padding: '40px 24px', position: 'relative', overflowX: 'hidden'
        }}>
            {/* Header & Progress */}
            <div style={{ width: '100%', maxWidth: '800px', marginBottom: '40px' }}>
                <h1 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '2.5rem', fontWeight: 700, color: 'var(--text-bright)', textAlign: 'center', marginBottom: '12px' }}>
                    Evaluación de Competencias
                </h1>
                <p style={{ fontFamily: 'Inter, sans-serif', fontSize: '1.1rem', color: 'var(--text-muted)', textAlign: 'center', marginBottom: '32px' }}>
                    Pregunta {currentIndex + 1} de {activeQuestions.length}
                </p>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <span style={{ fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: '0.8rem', color: 'var(--text-muted)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>PROGRESO</span>
                    <span style={{ fontFamily: 'Inter, sans-serif', color: 'var(--primary)', fontSize: '1rem', fontWeight: 700 }}>{progress}%</span>
                </div>
                <div style={{ background: 'var(--border)', borderRadius: '9999px', overflow: 'hidden', height: '8px' }}>
                    <motion.div
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.6, ease: 'easeOut' }}
                        style={{ height: '100%', borderRadius: '9999px', background: 'var(--primary)' }}
                    />
                </div>
            </div>

            {/* Main Content Area */}
            <div style={{ width: '100%', maxWidth: '800px', display: 'flex', flexDirection: 'column', gap: '32px' }}>
                
                {/* Question Text */}
                <div style={{ position: 'relative', minHeight: '180px' }}>
                    <AnimatePresence mode="wait">
                        <motion.div key={currentIndex}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: exitDirection > 0 ? 50 : -50 }}
                            transition={{ duration: 0.3, ease: "easeInOut" }}
                            style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                        >
                            <h2 style={{ fontSize: '1.8rem', lineHeight: '1.4', color: 'var(--text-bright)', fontFamily: 'Inter, sans-serif', fontWeight: 600, textAlign: 'center' }}>
                                {q.text}
                            </h2>
                        </motion.div>
                    </AnimatePresence>
                </div>

                {/* Answer Buttons */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', width: '100%' }}>
                    {q.options.map((option, i) => (
                        <motion.button key={i}
                            style={{
                                background: '#fff', color: 'var(--text-bright)', border: '1px solid var(--border)', borderRadius: '12px', padding: '20px 24px',
                                fontFamily: 'Inter, sans-serif', fontWeight: 500, fontSize: '1.1rem', textAlign: 'left', lineHeight: '1.5',
                                cursor: disabled ? 'default' : 'pointer', boxShadow: 'var(--shadow-sm)', opacity: disabled ? 0.6 : 1,
                                display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px',
                            }}
                            whileHover={disabled ? {} : { scale: 1.01, borderColor: 'var(--primary)', backgroundColor: 'var(--bg2)' }}
                            whileTap={disabled ? {} : { scale: 0.99 }}
                            onClick={() => handleAnswer(option)}
                        >
                            <span style={{ flex: 1 }}>{option.text}</span>
                            <div style={{ width: '32px', height: '32px', background: 'var(--bg)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                                <ChevronRight size={18} color="var(--primary)" strokeWidth={2.5} />
                            </div>
                        </motion.button>
                    ))}
                </div>
            </div>
        </div>
    )
}
