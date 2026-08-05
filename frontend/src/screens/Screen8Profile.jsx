import { useState, useEffect } from 'react'
import api from '../services/api'
import {
    Clock, Trophy, BookOpen,
    Cloud, Handshake, Palette, Cpu, BarChart2,
    User2, Calendar, Hash, LogOut, Code, Globe, ShieldCheck
} from 'lucide-react'

const COMPETENCIES = [
    { label: 'Cloud Architecture', category: 'Tecnología', progress: 80, color: 'var(--accent)', Icon: Cloud },
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
        <div style={{ height: '100vh', background: 'var(--bg)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <p style={{ color: 'var(--text-muted)', fontFamily: 'Inter', fontSize: '0.9rem' }}>Cargando perfil...</p>
        </div>
    )

    const STATS = [
        { label: 'Horas Invertidas', value: String(progressStats.totalHours), color: 'var(--text-bright)', Icon: Clock },
        { label: 'Módulos Completados', value: String(progressStats.completed), color: 'var(--text-bright)', Icon: BookOpen },
        { label: 'Nivel Profesional', value: user?.level_current || '1', color: 'var(--text-bright)', Icon: Trophy },
    ]

    return (
        <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--bg)' }}>
            
            {/* Header Profile */}
            <div style={{ flexShrink: 0, padding: '48px 48px 32px', borderBottom: '1px solid var(--border)', background: 'var(--bg2)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
                    <div style={{ width: '80px', height: '80px', borderRadius: '12px', background: 'var(--card)', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <User2 size={40} color="var(--text-muted)" strokeWidth={1.5} />
                    </div>
                    <div>
                        <h1 style={{ fontFamily: 'Inter', fontWeight: 800, fontSize: '1.8rem', color: 'var(--text-bright)', marginBottom: '8px' }}>
                            {user?.username || 'Estudiante'}
                        </h1>
                        <div style={{ display: 'flex', gap: '16px' }}>
                            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                <Hash size={14} /> ID: {user?.id || '000'}
                            </span>
                            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                <Calendar size={14} /> {user?.created_at ? `Miembro desde ${new Date(user.created_at).getFullYear()}` : 'Nuevo miembro'}
                            </span>
                        </div>
                    </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '16px' }}>
                    <div style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '8px', padding: '16px 24px', textAlign: 'right' }}>
                        <p style={{ fontFamily: 'Inter', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>Rendimiento Global</p>
                        <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.4rem', color: 'var(--primary)', lineHeight: 1 }}>{user?.xp_total || 0} PUNTOS</p>
                    </div>
                    <button onClick={handleLogout} style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'transparent', border: 'none', fontSize: '0.8rem', color: 'var(--text-muted)', cursor: 'pointer' }}>
                        <LogOut size={14} /> Cerrar sesión
                    </button>
                </div>
            </div>

            {/* Body */}
            <div style={{ flex: 1, overflow: 'auto', padding: '32px 48px' }}>
                
                {/* Stats Row */}
                <div style={{ display: 'flex', gap: '16px', marginBottom: '32px' }}>
                    {STATS.map((s, i) => (
                        <div key={i} style={{ flex: 1, background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '8px', padding: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
                            <div style={{ width: '48px', height: '48px', borderRadius: '8px', background: 'var(--bg)', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <s.Icon size={20} color="var(--primary)" />
                            </div>
                            <div>
                                <p style={{ fontWeight: 800, fontSize: '1.4rem', color: s.color, marginBottom: '4px' }}>{s.value}</p>
                                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'Inter', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{s.label}</p>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Competencies Grid */}
                <div style={{ marginBottom: '32px' }}>
                    <h2 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-bright)', marginBottom: '16px' }}>
                        Desarrollo de Competencias
                    </h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px' }}>
                        {COMPETENCIES.map((comp, i) => (
                            <div key={i} style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '8px', padding: '20px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                        <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--bg)', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                            <comp.Icon size={18} color={comp.color} />
                                        </div>
                                        <div>
                                            <h4 style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-bright)', marginBottom: '2px' }}>{comp.label}</h4>
                                            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{comp.category}</span>
                                        </div>
                                    </div>
                                    <span style={{ fontSize: '0.8rem', fontWeight: 700, color: comp.color }}>{comp.progress}%</span>
                                </div>
                                <div style={{ height: '6px', background: 'var(--bg)', borderRadius: '3px', overflow: 'hidden' }}>
                                    <div style={{ width: `${comp.progress}%`, height: '100%', background: comp.color, borderRadius: '3px' }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

            </div>
        </div>
    )
}