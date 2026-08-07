import { useState, useEffect } from 'react'
import api from '../services/api'
import {
    Clock, Trophy, BookOpen,
    Cloud, Handshake, Palette, Cpu, BarChart2,
    User2, Calendar, Hash, LogOut, Code, ShieldCheck
} from 'lucide-react'
import { motion } from 'framer-motion'

const COMPETENCIES = [
    { label: 'Cloud Architecture', category: 'Tecnología', progress: 80, color: 'var(--primary)', Icon: Cloud },
    { label: 'Desarrollo Frontend', category: 'Tecnología', progress: 65, color: 'var(--primary)', Icon: Code },
    { label: 'Análisis de Datos', category: 'Datos', progress: 40, color: 'var(--accent)', Icon: BarChart2 },
    { label: 'Diseño UX/UI', category: 'Diseño', progress: 90, color: 'var(--primary)', Icon: Palette },
    { label: 'Gestión de Proyectos', category: 'Negocios', progress: 50, color: 'var(--accent)', Icon: Handshake },
    { label: 'Ciberseguridad', category: 'Tecnología', progress: 30, color: 'var(--primary)', Icon: ShieldCheck },
]

export default function Screen8Profile({ onNavigate, onLogout }) {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)
    const [progressStats, setProgressStats] = useState({ completed: 0, totalHours: 0 })

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const response = await api.get('/api/v1/users/me')
                const userData = response.data
                setUser(userData)

                if (userData?.id) {
                    try {
                        const progressRes = await api.get(`/api/v1/progress/user/${userData.id}`)
                        const progressList = progressRes.data || []
                        const completed = progressList.filter(p => p.status === 'completed').length
                        const totalHours = completed * 2
                        setProgressStats({ completed, totalHours })
                    } catch (progressErr) {
                        console.warn('Endpoint de progreso no disponible:', progressErr?.response?.status)
                    }
                }
            } catch (err) {
                console.error("Error al sincronizar perfil:", err)
            } finally {
                setLoading(false)
            }
        }
        fetchUserData()
    }, [])

    const handleLogout = () => {
        localStorage.removeItem('token')
        if (onLogout) onLogout()
    }

    if (loading) return (
        <div style={{ height: '100vh', background: '#f8f9fa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <p style={{ color: 'var(--text-muted)', fontFamily: 'Inter', fontSize: '1rem' }}>Cargando perfil...</p>
        </div>
    )

    const STATS = [
        { label: 'Horas Invertidas', value: String(progressStats.totalHours), Icon: Clock },
        { label: 'Módulos Completados', value: String(progressStats.completed), Icon: BookOpen },
        { label: 'Nivel Profesional', value: user?.level_current || '1', Icon: Trophy },
    ]

    return (
        <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', background: '#f8f9fa' }}>
            
            {/* Header Profile */}
            <div style={{ flexShrink: 0, padding: '64px 48px 48px', borderBottom: '1px solid var(--border)', background: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
                <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
                    <div style={{ width: '120px', height: '120px', borderRadius: '50%', background: '#f0f2f5', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 8px 24px rgba(0,0,0,0.06)' }}>
                        <User2 size={64} color="var(--text-muted)" strokeWidth={1} />
                    </div>
                    <div>
                        <h1 style={{ fontFamily: 'Playfair Display', fontWeight: 700, fontSize: '2.5rem', color: 'var(--text-bright)', marginBottom: '8px' }}>
                            {user?.username || 'Estudiante'}
                        </h1>
                        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
                            <span style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1rem', color: 'var(--text-muted)', fontFamily: 'Inter' }}>
                                <Hash size={16} /> Estudiante #{user?.id || '000'}
                            </span>
                            <span style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1rem', color: 'var(--text-muted)', fontFamily: 'Inter' }}>
                                <Calendar size={16} /> {user?.created_at ? `Miembro desde ${new Date(user.created_at).getFullYear()}` : 'Nuevo miembro'}
                            </span>
                        </div>
                    </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '16px' }}>
                    <div style={{ background: 'rgba(59,130,246,0.05)', border: '1px solid rgba(59,130,246,0.2)', borderRadius: '8px', padding: '16px 32px', textAlign: 'center' }}>
                        <p style={{ fontFamily: 'Inter', fontSize: '0.85rem', color: 'var(--primary)', marginBottom: '4px', fontWeight: 600 }}>Rendimiento Global</p>
                        <p style={{ fontFamily: 'Inter', fontWeight: 800, fontSize: '2rem', color: 'var(--text-bright)', lineHeight: 1 }}>{user?.xp_total || 0}</p>
                    </div>
                    <button onClick={handleLogout} style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'transparent', border: 'none', fontSize: '0.95rem', color: 'var(--text-muted)', cursor: 'pointer', fontFamily: 'Inter', fontWeight: 500, padding: '8px 16px', borderRadius: '4px', transition: 'background 0.2s' }}
                        onMouseOver={e => e.currentTarget.style.background = '#f0f2f5'}
                        onMouseOut={e => e.currentTarget.style.background = 'transparent'}
                    >
                        <LogOut size={16} /> Cerrar sesión
                    </button>
                </div>
            </div>

            {/* Body */}
            <div style={{ flex: 1, overflow: 'auto', padding: '48px' }}>
                <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                    
                    {/* Stats Row */}
                    <div style={{ display: 'flex', gap: '24px', marginBottom: '48px' }}>
                        {STATS.map((s, i) => (
                            <motion.div whileHover={{ y: -4 }} key={i} style={{ flex: 1, background: '#fff', border: '1px solid var(--border)', borderRadius: '8px', padding: '32px', display: 'flex', alignItems: 'center', gap: '24px', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
                                <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: 'rgba(59,130,246,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <s.Icon size={32} color="var(--primary)" />
                                </div>
                                <div>
                                    <p style={{ fontWeight: 800, fontSize: '2rem', color: 'var(--text-bright)', marginBottom: '4px', fontFamily: 'Inter', lineHeight: 1.2 }}>{s.value}</p>
                                    <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontFamily: 'Inter', fontWeight: 500 }}>{s.label}</p>
                                </div>
                            </motion.div>
                        ))}
                    </div>

                    {/* Competencies Grid */}
                    <div style={{ marginBottom: '48px' }}>
                        <h2 style={{ fontFamily: 'Playfair Display', fontWeight: 700, fontSize: '1.8rem', color: 'var(--text-bright)', marginBottom: '24px' }}>
                            Desarrollo de Competencias
                        </h2>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '24px' }}>
                            {COMPETENCIES.map((comp, i) => (
                                <div key={i} style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: '8px', padding: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                            <div style={{ width: '48px', height: '48px', borderRadius: '8px', background: `${comp.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                                <comp.Icon size={24} color={comp.color} />
                                            </div>
                                            <div>
                                                <h4 style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: '1.05rem', color: 'var(--text-bright)', marginBottom: '4px' }}>{comp.label}</h4>
                                                <span style={{ fontFamily: 'Inter', fontSize: '0.85rem', color: 'var(--text-muted)' }}>{comp.category}</span>
                                            </div>
                                        </div>
                                        <span style={{ fontFamily: 'Inter', fontSize: '1rem', fontWeight: 700, color: comp.color }}>{comp.progress}%</span>
                                    </div>
                                    <div style={{ height: '8px', background: '#f0f2f5', borderRadius: '4px', overflow: 'hidden' }}>
                                        <div style={{ width: `${comp.progress}%`, height: '100%', background: comp.color, borderRadius: '4px', transition: 'width 1s ease-in-out' }} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}