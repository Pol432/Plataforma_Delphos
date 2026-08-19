import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, Lightbulb, Award, BookOpen, Clock } from 'lucide-react'
import api from '../services/api'

export default function Screen6Completion({ onNext, activeModule }) {
    const [registering, setRegistering] = useState(false)

    useEffect(() => {
        const registerCompletion = async () => {
            if (!activeModule) return
            setRegistering(true)
            try {
                const userRes = await api.get('/api/v1/users/me')
                const userId = userRes.data?.id
                if (!userId) return

                let progressId = null
                try {
                    const startRes = await api.post('/api/v1/progress/start', {
                        user_id: userId,
                        simulation_id: activeModule.id,
                    })
                    progressId = startRes.data?.id
                } catch (startErr) {
                    // 400 = ya estaba iniciado, que es lo normal: enviar una tarea
                    // desde el workspace ya crea el registro. Hay que recuperar su
                    // id, o el PATCH que lo marca completado no llega a ejecutarse.
                    if (startErr?.response?.status === 400) {
                        try {
                            const listRes = await api.get(`/api/v1/progress/user/${userId}`)
                            const existing = (listRes.data || []).find(
                                p => p.simulation_id === activeModule.id
                            )
                            progressId = existing?.id ?? null
                        } catch (listErr) {
                            console.warn('No se pudo recuperar el progreso existente:', listErr?.response?.status)
                        }
                    } else {
                        console.warn('Error al iniciar progreso:', startErr?.response?.status)
                    }
                }

                if (progressId) {
                    await api.patch(`/api/v1/progress/${progressId}`, {
                        status: 'completed',
                        completion_percentage: 100,
                    })
                }
            } catch (err) {
                console.error('Error al registrar módulo completado:', err)
            } finally {
                setRegistering(false)
            }
        }

        registerCompletion()
    }, [activeModule])

    const handleContinue = () => {
        localStorage.removeItem('activeModule')
        onNext()
    }

    return (
        <div style={{
            minHeight: '100vh', background: 'var(--bg)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            padding: '24px', position: 'relative', overflow: 'hidden',
        }}>
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', width: '700px', height: '500px', borderRadius: '50%', background: 'radial-gradient(circle, var(--primary-glow) 0%, transparent 70%)', pointerEvents: 'none' }} />

            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                style={{
                    maxWidth: '540px', width: '100%', padding: '44px 40px',
                    background: 'var(--card)',
                    border: '1px solid var(--border)',
                    borderTop: '3px solid var(--primary)',
                    boxShadow: 'var(--shadow-lg)',
                    position: 'relative', borderRadius: '16px',
                }}
            >
                <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                    <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', damping: 15, delay: 0.2 }}
                        style={{
                            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                            width: '72px', height: '72px', borderRadius: '50%',
                            background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.2)',
                        }}
                    >
                        <CheckCircle size={36} color="var(--primary)" strokeWidth={2} />
                    </motion.div>
                </div>

                <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                    <h1 style={{
                        fontSize: '1.6rem', fontFamily: 'Inter', fontWeight: 800,
                        color: 'var(--text-bright)',
                        letterSpacing: '0.04em'
                    }}>
                        Resumen de Progreso
                    </h1>
                </div>

                {activeModule && (
                    <p style={{ textAlign: 'center', fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '32px', fontFamily: 'Inter' }}>
                        Has completado con éxito el módulo <strong>{activeModule.title}</strong>
                    </p>
                )}

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '32px' }}>
                    <div style={{
                        background: 'var(--bg2)', border: '1px solid var(--border)',
                        borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '12px'
                    }}>
                        <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--bg)', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <Clock size={20} color="var(--primary)" />
                        </div>
                        <div>
                            <p style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-bright)' }}>{activeModule?.estimatedTime || '1h 30m'}</p>
                            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'Inter' }}>TIEMPO INVERTIDO</p>
                        </div>
                    </div>
                    <div style={{
                        background: 'var(--bg2)', border: '1px solid var(--border)',
                        borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '12px'
                    }}>
                        <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--bg)', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <Award size={20} color="var(--accent)" />
                        </div>
                        <div>
                            <p style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-bright)' }}>100%</p>
                            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'Inter' }}>PRECISIÓN</p>
                        </div>
                    </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '32px' }}>
                    <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>Feedback del Instructor IA</h3>
                    <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}
                        style={{ background: 'rgba(6, 182, 212, 0.05)', border: '1px solid rgba(6, 182, 212, 0.2)', borderLeft: '3px solid var(--accent)', borderRadius: '8px', padding: '16px', display: 'flex', gap: '12px', alignItems: 'flex-start' }}
                    >
                        <div style={{ width: '32px', height: '32px', flexShrink: 0, background: 'var(--bg)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--border)' }}>
                            <CheckCircle size={16} color="var(--accent)" strokeWidth={2.5} />
                        </div>
                        <div>
                            <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.75rem', color: 'var(--accent)', marginBottom: '6px', letterSpacing: '0.04em', textTransform: 'uppercase' }}>Ejecución Óptima</p>
                            <p style={{ fontSize: '0.85rem', color: 'var(--text)', lineHeight: '1.5', fontFamily: 'Inter' }}>Tu lógica fue impecable. La estructura mostrada fue clara y profesional.</p>
                        </div>
                    </motion.div>
                    <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }}
                        style={{ background: 'rgba(59, 130, 246, 0.05)', border: '1px solid rgba(59, 130, 246, 0.2)', borderLeft: '3px solid var(--primary)', borderRadius: '8px', padding: '16px', display: 'flex', gap: '12px', alignItems: 'flex-start' }}
                    >
                        <div style={{ width: '32px', height: '32px', flexShrink: 0, background: 'var(--bg)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--border)' }}>
                            <Lightbulb size={16} color="var(--primary)" strokeWidth={2.5} />
                        </div>
                        <div>
                            <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.75rem', color: 'var(--primary)', marginBottom: '6px', letterSpacing: '0.04em', textTransform: 'uppercase' }}>Área de Mejora Recomendada</p>
                            <p style={{ fontSize: '0.85rem', color: 'var(--text)', lineHeight: '1.5', fontFamily: 'Inter' }}>Intenta documentar tus próximos pasos para que el equipo pueda darte seguimiento más fácilmente.</p>
                        </div>
                    </motion.div>
                </div>

                <motion.button
                    style={{ width: '100%', padding: '16px', borderRadius: '10px', background: 'var(--primary)', color: '#fff', border: 'none', fontFamily: 'Inter', fontWeight: 700, fontSize: '0.9rem', cursor: registering ? 'wait' : 'pointer', letterSpacing: '0.05em' }}
                    whileHover={{ background: 'var(--primary-dim)' }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleContinue}
                    disabled={registering}
                >
                    {registering ? 'Guardando progreso...' : 'Continuar Aprendizaje'}
                </motion.button>
            </motion.div>
        </div>
    )
}
