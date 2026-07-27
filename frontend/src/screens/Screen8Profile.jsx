import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import api from '../services/api'
import {
    Lock, Clock, Zap, Trophy, Flame, Star,
    Cloud, Handshake, Palette, Cpu, BarChart2,
    User2, Calendar, Hash, Layers, LogOut,
} from 'lucide-react'

// ── Skill tree nodes ──────────────────────────────────────────────────────────
const NODES = [
    { id: 'root', label: 'Inicio', x: 220, y: 20, locked: false, parents: [], color: 'var(--primary)', Icon: Zap },
    { id: 'cloud', label: 'Cloud\nBasics', x: 90, y: 100, locked: true, parents: ['root'], color: 'var(--accent)', Icon: Cloud },
    { id: 'aws', label: 'AWS\nCore', x: 50, y: 185, locked: true, parents: ['cloud'], color: 'var(--accent)', Icon: Cloud },
    { id: 'devops', label: 'DevOps', x: 110, y: 265, locked: true, parents: ['aws'], color: 'var(--accent)', Icon: Cpu },
    { id: 'security', label: 'SecOps', x: 60, y: 345, locked: true, parents: ['devops'], color: 'var(--primary)', Icon: Lock },
    { id: 'data', label: 'Data\nBasics', x: 185, y: 100, locked: true, parents: ['root'], color: 'var(--accent)', Icon: BarChart2 },
    { id: 'analysis', label: 'Data\nAnalysis', x: 165, y: 185, locked: true, parents: ['data'], color: 'var(--accent)', Icon: BarChart2 },
    { id: 'ml', label: 'Machine\nLearning', x: 180, y: 275, locked: true, parents: ['analysis'], color: 'var(--accent)', Icon: Star },
    { id: 'biz', label: 'Business\nBasics', x: 290, y: 100, locked: true, parents: ['root'], color: 'var(--primary)', Icon: Handshake },
    { id: 'nego', label: 'Nego-\nciación', x: 310, y: 185, locked: true, parents: ['biz'], color: 'var(--primary)', Icon: Handshake },
    { id: 'consult', label: 'Consul-\ntoría', x: 285, y: 275, locked: true, parents: ['nego'], color: 'var(--primary)', Icon: Trophy },
    { id: 'exec', label: 'Ejecutivo', x: 300, y: 355, locked: true, parents: ['consult'], color: 'var(--gold)', Icon: Trophy },
    { id: 'design', label: 'Design\nBasics', x: 380, y: 105, locked: true, parents: ['root'], color: 'var(--gold)', Icon: Palette },
    { id: 'brand', label: 'Branding', x: 400, y: 195, locked: true, parents: ['design'], color: 'var(--gold)', Icon: Palette },
    { id: 'ux', label: 'UX / UI', x: 385, y: 285, locked: true, parents: ['brand'], color: 'var(--gold)', Icon: Star },
]
const nodeMap = Object.fromEntries(NODES.map(n => [n.id, n]))

const BADGES = [
    { label: 'AWS', color: 'var(--accent)', Icon: Cloud },
    { label: 'Diseño', color: 'var(--gold)', Icon: Palette },
    { label: 'Datos', color: 'var(--accent)', Icon: BarChart2 },
    { label: 'Ventas', color: 'var(--primary)', Icon: Handshake },
    { label: 'Líder', color: 'var(--gold)', Icon: Trophy },
    { label: 'DevOps', color: 'var(--accent)', Icon: Cpu },
]

// ── Skill Tree SVG ────────────────────────────────────────────────────────────
function SkillTree() {
    const W = 460, H = 400
    const R = 22
    return (
        <svg width="100%" height={H} viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" style={{ overflow: 'visible' }}>
            <defs>
                <filter id="aglow2"><feGaussianBlur stdDeviation="5" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
            </defs>
            {NODES.flatMap(n => n.parents.map(pid => {
                const p = nodeMap[pid]; if (!p) return null
                return <line key={`${pid}-${n.id}`} x1={p.x} y1={p.y} x2={n.x} y2={n.y} stroke="var(--border)" strokeWidth="1.5" strokeDasharray="4 3" />
            }))}
            {NODES.map(n => {
                const NIcon = n.Icon; const isRoot = n.id === 'root'
                return (
                    <g key={n.id} transform={`translate(${n.x},${n.y})`}>
                        <circle r={R + 5} fill="none" stroke={n.locked ? 'var(--border)' : n.color} strokeWidth="1" opacity={n.locked ? 0.35 : 0.5} strokeDasharray={n.locked ? '3 3' : 'none'} />
                        <circle r={R} fill={n.locked ? 'var(--card)' : `var(--accent-glow)`} stroke={n.locked ? 'var(--border)' : n.color} strokeWidth={isRoot ? 2.5 : 1.5} filter={isRoot ? 'url(#aglow2)' : 'none'} />
                        {n.locked
                            ? <Lock x={-9} y={-9} size={18} color="var(--text-muted)" strokeWidth={2} />
                            : <NIcon x={-10} y={-10} size={20} color={n.color} strokeWidth={2} />}
                        {n.label.split('\n').map((line, li) => (
                            <text
                                key={li}
                                x="0"
                                y={R + 12 + li * 11}
                                textAnchor="middle"
                                fill={n.locked ? 'var(--text-muted)' : n.color}
                                fontSize="8.5"
                                fontFamily="Inter"
                                fontWeight={n.locked ? '400' : '700'}
                                letterSpacing="0.02em"
                            >
                                {line}
                            </text>
                        ))}
                    </g>
                )
            })}
        </svg>
    )
}

export default function Screen8Profile({ onNavigate, onLogout }) {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)
    // B-08: Estadísticas reales del progreso
    const [progressStats, setProgressStats] = useState({ completed: 0, totalHours: 0 })

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const response = await api.get('/api/v1/users/me')
                const userData = response.data
                setUser(userData)

                // B-08: Intentar cargar estadísticas de progreso
                if (userData?.id) {
                    try {
                        const progressRes = await api.get(`/api/v1/progress/user/${userData.id}`)
                        const progressList = progressRes.data || []
                        const completed = progressList.filter(p => p.status === 'completed').length
                        // Estimación: 2h por misión completada (puede refinarse con duración real)
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
            <p style={{ color: 'var(--primary)', fontFamily: 'monospace', letterSpacing: '0.2em' }}>ACCEDIENDO A PASAPORTE...</p>
        </div>
    )

    const STATS = [
        // B-08: Datos reales de progreso
        { label: 'Horas Invertidas', value: String(progressStats.totalHours), color: 'var(--accent)', Icon: Clock },
        { label: 'Misiones Completadas', value: String(progressStats.completed), color: 'var(--primary)', Icon: Flame },
        { label: 'Nivel Actual', value: user?.level_current || '0', color: 'var(--gold)', Icon: Trophy },
    ]

    const AREAS = [
        { label: 'Tecnología', pct: 0, color: 'var(--accent)' },
        { label: 'Negocios', pct: 0, color: 'var(--primary)' },
        { label: 'Diseño', pct: 0, color: 'var(--gold)' },
        { label: 'Datos', pct: 0, color: 'var(--accent)' },
    ]

    return (
        <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--bg)' }}>
            {/* Banner */}
            <div style={{ flexShrink: 0, position: 'relative' }}>
                <div style={{ height: '110px', background: 'var(--bg2)', position: 'relative', overflow: 'hidden' }}>
                    <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: '1px', background: 'linear-gradient(90deg, transparent, var(--primary), var(--accent), transparent)' }} />
                    <div style={{ position: 'absolute', top: '14px', right: '22px', background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(8px)', border: '1px solid var(--border)', borderRadius: '7px', padding: '5px 13px' }}>
                        <span style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.6rem', color: 'var(--primary)', letterSpacing: '0.14em', textTransform: 'uppercase' }}>PASAPORTE PROFESIONAL</span>
                    </div>
                </div>

                {/* Avatar */}
                <div style={{ position: 'absolute', bottom: -44, left: '30px', zIndex: 10 }}>
                    <div style={{ width: '90px', height: '90px', borderRadius: '50%', background: 'var(--card)', border: '3px solid var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <User2 size={38} color={user?.streak_days > 0 ? "var(--primary)" : "var(--text-muted)"} strokeWidth={1.5} />
                    </div>
                    <div style={{ position: 'absolute', bottom: 4, right: 4, width: '16px', height: '16px', borderRadius: '50%', background: 'var(--accent)', border: '3px solid var(--bg)' }} />
                </div>
            </div>

            {/* Name Row */}
            <div style={{ flexShrink: 0, display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', padding: '40px 24px 12px', borderBottom: '1px solid var(--border)' }}>
                <div style={{ paddingLeft: '110px' }}>
                    <h1 style={{ fontFamily: 'Inter', fontWeight: 900, fontSize: '1.45rem', color: 'var(--text-bright)', letterSpacing: '0.04em', marginBottom: '8px' }}>
                        {user?.username?.toUpperCase() || 'USUARIO_RED'}
                    </h1>
                    <div style={{ display: 'flex', gap: '6px' }}>
                        {[
                            { Icon: Hash, label: `ID: #${user?.id || '000'}`, color: 'var(--accent)' },
                            { Icon: Calendar, label: user?.created_at ? `Desde ${new Date(user.created_at).toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })}` : 'Nuevo miembro', color: 'var(--gold)' },
                            { Icon: Flame, label: `${user?.streak_days || 0} días de racha`, color: 'var(--primary)' },
                        ].map(({ Icon, label, color }, i) => (
                            <div key={i} style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', background: 'var(--bg2)', border: `1px solid var(--border)`, borderRadius: '6px', padding: '4px 11px' }}>
                                <Icon size={11} color={color} strokeWidth={2.5} />
                                <span style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: '0.68rem', color }}>{label}</span>
                            </div>
                        ))}
                    </div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end' }}>
                    <div style={{ background: 'var(--primary-glow)', border: '1px solid var(--border)', borderTop: '2px solid var(--primary)', borderRadius: '10px', padding: '12px 22px', textAlign: 'center', minWidth: '150px' }}>
                        <p style={{ fontFamily: 'Inter', fontWeight: 900, fontSize: '1.4rem', color: 'var(--primary)', lineHeight: 1 }}>NIVEL {user?.level_current || 0}</p>
                        <p style={{ fontFamily: 'Inter', fontSize: '0.62rem', color: 'var(--text-muted)', marginTop: '6px' }}>{user?.xp_total || 0} / 100 XP</p>
                    </div>
                    <button onClick={handleLogout} style={{ background: 'transparent', border: '1px solid var(--border)', borderRadius: '8px', padding: '7px 14px', fontSize: '0.7rem', color: 'var(--text-muted)', cursor: 'pointer' }}>
                        <LogOut size={13} /> Cerrar sesión
                    </button>
                </div>
            </div>

            {/* Body */}
            <div style={{ flex: 1, overflow: 'auto', padding: '18px 24px 20px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr 220px', gap: '14px', height: '100%' }}>
                    <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '12px', padding: '14px' }}>
                        <p style={{ fontWeight: 700, fontSize: '0.6rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '10px' }}>// Estadísticas</p>
                        {STATS.map((s, i) => (
                            <div key={i} style={{ background: 'var(--bg)', borderLeft: `3px solid ${s.color}`, borderRadius: '7px', padding: '9px 12px', display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                                <s.Icon size={13} color={s.color} />
                                <div>
                                    <p style={{ fontWeight: 900, color: s.color }}>{s.value}</p>
                                    <p style={{ fontSize: '0.58rem', color: 'var(--text-muted)' }}>{s.label}</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '12px', padding: '16px', position: 'relative' }}>
                        <SkillTree />
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderTop: '2px solid var(--gold)', borderRadius: '12px', padding: '14px' }}>
                            <p style={{ fontWeight: 700, fontSize: '0.6rem', color: 'var(--gold)', textTransform: 'uppercase', marginBottom: '12px' }}>Insignias</p>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '7px' }}>
                                {BADGES.map((b, i) => (
                                    <div key={i} style={{ aspectRatio: '1', background: 'var(--bg)', borderRadius: '9px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <b.Icon size={18} color="var(--border)" />
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}