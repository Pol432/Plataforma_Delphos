import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, Lightbulb, Trophy, Zap, Award } from 'lucide-react'
import ReactConfetti from 'react-confetti'
import api from '../services/api'

export default function Screen6Victory({ onNext, activeMission }) {
    const [windowSize, setWindowSize] = useState({ width: window.innerWidth, height: window.innerHeight })
    const [confettiDone, setConfettiDone] = useState(false)
    const [glitch, setGlitch] = useState(false)
    const [registering, setRegistering] = useState(false)

    // XP real de la misión o fallback a 150
    const xpReward = activeMission?.xp
        ? (typeof activeMission.xp === 'string' ? parseInt(activeMission.xp.replace(/\D/g, '')) || 150 : activeMission.xp)
        : 150

    useEffect(() => {
        const handle = () => setWindowSize({ width: window.innerWidth, height: window.innerHeight })
        window.addEventListener('resize', handle)
        const t = setTimeout(() => setConfettiDone(true), 5000)
        const g = setInterval(() => { setGlitch(true); setTimeout(() => setGlitch(false), 180) }, 3800)

        // B-02: Registrar la misión completada en el backend al entrar a esta pantalla
        const registerCompletion = async () => {
            if (!activeMission) return
            setRegistering(true)
            try {
                const userRes = await api.get('/api/v1/users/me')
                const userId = userRes.data?.id
                if (!userId) return

                // Intentar iniciar progreso y marcarlo como completado
                let progressId = null
                try {
                    const startRes = await api.post('/api/v1/progress/start', {
                        user_id: userId,
                        simulation_id: activeMission.id,
                    })
                    progressId = startRes.data?.id
                } catch (startErr) {
                    // Si ya existía, ignoramos el error 400
                    console.warn('Progreso ya iniciado o error al iniciar:', startErr?.response?.status)
                }

                if (progressId) {
                    await api.patch(`/api/v1/progress/${progressId}`, {
                        status: 'completed',
                        completion_percentage: 100,
                    })
                }
            } catch (err) {
                console.error('Error al registrar misión completada:', err)
            } finally {
                setRegistering(false)
            }
        }

        registerCompletion()

        return () => { window.removeEventListener('resize', handle); clearTimeout(t); clearInterval(g) }
    }, [])

    const handleContinue = () => {
        // Limpiar misión activa del localStorage al continuar
        localStorage.removeItem('activeMission')
        onNext()
    }

    return (
        <div style={{
            minHeight: '100vh', background: 'var(--bg)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            padding: '24px', position: 'relative', overflow: 'hidden',
        }}>
            {/* Radial glows */}
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', width: '700px', height: '500px', borderRadius: '50%', background: 'radial-gradient(circle, var(--primary-glow) 0%, var(--accent-glow) 50%, transparent 70%)', pointerEvents: 'none' }} />

            {/* Floating particles */}
            {Array.from({ length: 18 }).map((_, i) => (
                <motion.div key={i}
                    animate={{ y: [0, -28, 0], opacity: [0.3, 0.7, 0.3] }}
                    transition={{ duration: 2 + (i % 4), repeat: Infinity, delay: i * 0.25 }}
                    style={{
                        position: 'absolute',
                        width: (i % 3 === 0 ? 4 : 2) + 'px', height: (i % 3 === 0 ? 4 : 2) + 'px',
                        borderRadius: '50%',
                        background: i % 2 === 0 ? 'var(--primary)' : 'var(--accent)',
                        boxShadow: i % 2 === 0 ? '0 0 4px var(--primary)' : '0 0 4px var(--accent)',
                        top: (15 + (i * 4.5)) + '%', left: (5 + (i * 5.2)) + '%',
                    }}
                />
            ))}

            {!confettiDone && (
                <div className="confetti-overlay">
                    <ReactConfetti width={windowSize.width} height={windowSize.height}
                        numberOfPieces={220} recycle={false}
                        colors={['var(--primary)', 'var(--accent)', 'var(--gold)', 'var(--text-bright)']}
                    />
                </div>
            )}

            <motion.div
                initial={{ opacity: 0, scale: 0.8, y: 40 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
                style={{
                    maxWidth: '540px', width: '100%', padding: '44px 40px',
                    background: 'var(--card)',
                    border: '1px solid var(--border)',
                    borderTop: '2px solid var(--primary)',
                    boxShadow: '0 0 40px var(--primary-glow), 0 24px 64px rgba(0,0,0,0.7)',
                    position: 'relative', borderRadius: '12px',
                }}
            >
                {/* Corner lines */}
                <div style={{ position: 'absolute', top: 0, right: 0, width: '80px', height: '2px', background: 'var(--accent)', borderRadius: '0 0 0 2px' }} />
                <div style={{ position: 'absolute', top: 0, right: 0, width: '2px', height: '80px', background: 'var(--accent)' }} />

                {/* Trophy icon */}
                <div style={{ textAlign: 'center', marginBottom: '14px' }}>
                    <motion.div animate={{ rotate: [0, -8, 8, -5, 0] }} transition={{ duration: 1.2, delay: 0.4 }}
                        style={{
                            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                            width: '72px', height: '72px', borderRadius: '18px',
                            background: 'var(--primary-glow)', border: '1.5px solid var(--border)',
                            boxShadow: '0 0 20px var(--primary-glow)',
                        }}
                    >
                        <Trophy size={36} color="var(--primary)" strokeWidth={1.8} />
                    </motion.div>
                </div>

                {/* Glitch title */}
                <div style={{ textAlign: 'center', marginBottom: '6px', position: 'relative' }}>
                    <h1 style={{
                        fontSize: '1.8rem', fontFamily: 'Inter', fontWeight: 900,
                        color: 'var(--primary)',
                        textShadow: '0 0 18px var(--primary-glow)',
                        letterSpacing: '0.08em', position: 'relative'
                    }}>
                        MÓDULO COMPLETADO
                        {glitch && (
                            <>
                                <span style={{ position: 'absolute', inset: 0, color: 'var(--accent)', clipPath: 'inset(30% 0 50% 0)', transform: 'translate(-3px, 0)' }}>MÓDULO COMPLETADO</span>
                                <span style={{ position: 'absolute', inset: 0, color: 'var(--gold)', clipPath: 'inset(70% 0 0% 0)', transform: 'translate(3px, 0)' }}>MÓDULO COMPLETADO</span>
                            </>
                        )}
                    </h1>
                </div>
                {activeMission && (
                    <p style={{ textAlign: 'center', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '6px', fontFamily: 'Inter', fontStyle: 'italic' }}>
                        {activeMission.title}
                    </p>
                )}
                <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: '28px', fontSize: '0.82rem', fontFamily: 'Inter', letterSpacing: '0.05em' }}>
                    &gt; Has demostrado tu habilidad. Recompensas desbloqueadas:
                </p>

                {/* Loot widgets */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '22px' }}>
                    <motion.div initial={{ x: -30, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.4 }}
                        style={{
                            background: 'var(--primary-glow)', border: '1px solid var(--border)',
                            borderTop: '2px solid var(--primary)',
                            borderRadius: '10px', padding: '20px', textAlign: 'center',
                        }}
                    >
                        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '10px' }}>
                            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--bg)', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <Zap size={20} color="var(--primary)" strokeWidth={2} />
                            </div>
                        </div>
                        {/* B-02: XP real de la misión */}
                        <span style={{ fontFamily: 'Inter', fontWeight: 900, fontSize: '1.5rem', color: 'var(--primary)' }}>
                            +{xpReward} XP
                        </span>
                        <p style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '4px', fontFamily: 'Inter' }}>PUNTOS DE EXPERIENCIA</p>
                    </motion.div>
                    <motion.div initial={{ x: 30, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.5 }}
                        style={{
                            background: 'var(--accent-glow)', border: '1px solid var(--border)',
                            borderTop: '2px solid var(--accent)',
                            borderRadius: '10px', padding: '20px', textAlign: 'center',
                        }}
                    >
                        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '10px' }}>
                            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--bg)', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <Award size={20} color="var(--accent)" strokeWidth={2} />
                            </div>
                        </div>
                        <span style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.9rem', color: 'var(--accent)' }}>
                            {activeMission?.badge || 'PRIMEROS PASOS'}
                        </span>
                        <p style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '4px', fontFamily: 'Inter' }}>LOGRO DESBLOQUEADO</p>
                    </motion.div>
                </div>

                {/* Feedback */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '28px' }}>
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}
                        style={{ background: 'var(--accent-glow)', border: '1px solid var(--border)', borderLeft: '3px solid var(--accent)', borderRadius: '8px', padding: '14px', display: 'flex', gap: '12px', alignItems: 'flex-start' }}
                    >
                        <div style={{ width: '32px', height: '32px', flexShrink: 0, background: 'var(--bg)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--border)' }}>
                            <CheckCircle size={16} color="var(--accent)" strokeWidth={2.5} />
                        </div>
                        <div>
                            <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.72rem', color: 'var(--accent)', marginBottom: '4px', letterSpacing: '0.06em', textTransform: 'uppercase' }}>EJECUCIÓN ÓPTIMA</p>
                            <p style={{ fontSize: '0.8rem', color: 'var(--text-bright)', lineHeight: '1.5', fontFamily: 'Inter' }}>Tu lógica fue impecable. La estructura del contrato fue clara y profesional.</p>
                        </div>
                    </motion.div>
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}
                        style={{ background: 'var(--primary-glow)', border: '1px solid var(--border)', borderLeft: '3px solid var(--gold)', borderRadius: '8px', padding: '14px', display: 'flex', gap: '12px', alignItems: 'flex-start' }}
                    >
                        <div style={{ width: '32px', height: '32px', flexShrink: 0, background: 'var(--bg)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--border)' }}>
                            <Lightbulb size={16} color="var(--gold)" strokeWidth={2.5} />
                        </div>
                        <div>
                            <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.72rem', color: 'var(--gold)', marginBottom: '4px', letterSpacing: '0.06em', textTransform: 'uppercase' }}>ÁREA DE MEJORA</p>
                            <p style={{ fontSize: '0.8rem', color: 'var(--text-bright)', lineHeight: '1.5', fontFamily: 'Inter' }}>Intenta estructurar mejor el documento con secciones más definidas.</p>
                        </div>
                    </motion.div>
                </div>

                <motion.button
                    style={{ width: '100%', padding: '16px', borderRadius: '10px', background: 'var(--primary)', color: '#fff', border: 'none', fontFamily: 'Inter', fontWeight: 700, fontSize: '0.9rem', cursor: registering ? 'wait' : 'pointer', letterSpacing: '0.1em', textTransform: 'uppercase', boxShadow: '0 4px 20px var(--primary-glow)' }}
                    whileHover={{ background: 'var(--primary-dim)', boxShadow: '0 6px 28px var(--primary-glow)' }}
                    whileTap={{ scale: 0.97 }}
                    onClick={handleContinue}
                    disabled={registering}
                >
                    {registering ? '⏳ REGISTRANDO...' : '⚡ CONTINUAR AVENTURA'}
                </motion.button>
            </motion.div>
        </div>
    )
}
