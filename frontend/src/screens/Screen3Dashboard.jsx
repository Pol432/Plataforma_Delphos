import { useState, useEffect } from 'react'
import { motion, AnimatePresence, useMotionValue, useSpring } from 'framer-motion'
import { Map, Target, Users, User2, ChevronRight, UserCircle, MapPin, Zap, CheckCircle2, Clock, Layers, Star, Activity } from 'lucide-react'
import api from '../services/api' // Importamos la conexión centralizada

const NAV_ITEMS = [
    { icon: Map, label: 'Mapa', id: 3 },
    { icon: Target, label: 'Misiones', id: 4 },
    { icon: Users, label: 'Comunidad', id: 7 },
    { icon: User2, label: 'Perfil', id: 8 },
]

const EMPTY_STARTERS = [
    { label: 'Completa tu perfil', reward: '+30 XP', Icon: UserCircle, color: '#00E5FF' },
    { label: 'Explora el mapa de progreso', reward: '+20 XP', Icon: MapPin, color: '#FF4500' },
    { label: 'Acepta tu primera misión', reward: '+50 XP', Icon: Zap, color: '#FFA726' },
]

// Floating particle component
function Particle({ delay, x, y, size, color }) {
    return (
        <motion.div
            style={{ position: 'absolute', width: size, height: size, borderRadius: '50%', background: color, left: x, top: y, pointerEvents: 'none' }}
            animate={{ y: [0, -18, 0], opacity: [0.15, 0.5, 0.15] }}
            transition={{ duration: 3 + Math.random() * 2, repeat: Infinity, delay, ease: 'easeInOut' }}
        />
    )
}

// Animated number counter
function Counter({ value, suffix = '' }) {
    const mv = useMotionValue(0)
    const spring = useSpring(mv, { damping: 20, stiffness: 60 })
    const [display, setDisplay] = useState(0)
    useEffect(() => { mv.set(value) }, [value])
    useEffect(() => spring.on('change', v => setDisplay(Math.round(v))), [spring])
    return <span>{display}{suffix}</span>
}

// Hexagonal node for the path map
function HexNode({ x, y, i, total, isCompleted, isCurrent, isLocked, color, label, duration, MissionIcon, onClick }) {
    const HEX_R = 26
    const pts = Array.from({ length: 6 }, (_, k) => {
        const a = (Math.PI / 3) * k - Math.PI / 6
        return `${HEX_R * Math.cos(a)},${HEX_R * Math.sin(a)}`
    }).join(' ')

    return (
        <g transform={`translate(${x},${y})`} style={{ cursor: isCurrent ? 'pointer' : 'default' }} onClick={isCurrent ? onClick : undefined}>
            {isCurrent && (
                <motion.polygon points={pts} fill="none" stroke={color} strokeWidth="1.5"
                    animate={{ opacity: [0.3, 0.9, 0.3], scale: [1, 1.18, 1] }}
                    transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
                    style={{ transformOrigin: '0 0' }}
                />
            )}
            <polygon points={pts}
                fill={isCompleted ? color : isCurrent ? `${color}20` : '#1a1a1a'}
                stroke={isCompleted ? color : isCurrent ? color : '#2a2a2a'}
                strokeWidth="2"
            />
            {isCompleted
                ? <CheckCircle2 x={-9} y={-9} size={18} color="#111" strokeWidth={2.5} />
                : isCurrent
                    ? MissionIcon && <MissionIcon x={-9} y={-9} size={18} color={color} strokeWidth={2} />
                    : <text x="0" y="5" textAnchor="middle" fill="#444" fontSize="11" fontFamily="Inter" fontWeight="700">{i + 1}</text>
            }
        </g>
    )
}

// Zigzag SVG map
function HexPathMap({ modules, activeIdx, color, MissionIcon, onNodeClick }) {
    const W = 420
    const ROW_H = 86
    const COLS = [90, W - 90]
    const totalH = modules.length * ROW_H + 40

    return (
        <div style={{ position: 'relative', width: '100%' }}>
            <svg width="100%" height={totalH} viewBox={`0 0 ${W} ${totalH}`} preserveAspectRatio="xMidYMid meet" style={{ overflow: 'visible' }}>
                <defs>
                    <filter id="glow2"><feGaussianBlur stdDeviation="4" result="blur" /><feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
                    <filter id="nodeglow"><feGaussianBlur stdDeviation="6" result="blur" /><feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
                </defs>
                {modules.map((_, i) => {
                    if (i >= modules.length - 1) return null
                    const x1 = COLS[i % 2], y1 = i * ROW_H + 36
                    const x2 = COLS[(i + 1) % 2], y2 = (i + 1) * ROW_H + 36
                    const done = i < activeIdx
                    return <path key={i} d={`M${x1} ${y1} C${x1} ${y1 + 35},${x2} ${y2 - 35},${x2} ${y2}`}
                        fill="none" stroke={done ? color : '#252525'} strokeWidth={done ? 2.5 : 1.5}
                        strokeDasharray={done ? 'none' : '6 4'} opacity={done ? 0.9 : 0.5}
                        filter={done ? 'url(#glow2)' : 'none'} />
                })}
                {modules.map((mod, i) => (
                    <HexNode key={i} x={COLS[i % 2]} y={i * ROW_H + 36} i={i} total={modules.length}
                        isCompleted={i < activeIdx} isCurrent={i === activeIdx} isLocked={i > activeIdx}
                        color={color} label={mod.title} duration={mod.duration} MissionIcon={MissionIcon}
                        onClick={onNodeClick}
                    />
                ))}
                {modules.map((mod, i) => {
                    const isLeft = i % 2 === 0
                    const x = COLS[i % 2] + (isLeft ? 36 : -36)
                    const y = i * ROW_H + 36
                    const isCurrent = i === activeIdx
                    const isCompleted = i < activeIdx
                    return (
                        <g key={`label-${i}`} transform={`translate(${x},${y})`}>
                            <foreignObject x={isLeft ? 0 : -150} y={-24} width="150" height="52">
                                <div style={{ fontFamily: 'Inter', fontSize: '0.72rem', fontWeight: isCurrent ? 700 : 400, color: isCurrent ? '#f5f5f5' : isCompleted ? '#777' : '#444', lineHeight: 1.35, textDecoration: isCompleted ? 'line-through' : 'none', paddingLeft: isLeft ? '6px' : 0, paddingRight: isLeft ? 0 : '6px', textAlign: isLeft ? 'left' : 'right' }}>
                                    {mod.title}
                                    <div style={{ fontSize: '0.6rem', marginTop: '3px', color: isCurrent ? color : '#444', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '3px', justifyContent: isLeft ? 'flex-start' : 'flex-end' }}>
                                        <Clock size={9} strokeWidth={2} /> {mod.duration}
                                        {isCurrent && <span style={{ marginLeft: '4px', color, letterSpacing: '0.06em' }}>EN CURSO</span>}
                                    </div>
                                </div>
                            </foreignObject>
                        </g>
                    )
                })}
            </svg>
        </div>
    )
}

function StatCard({ value, label, suffix, color, Icon, delay = 0 }) {
    return (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}
            style={{ background: 'var(--card)', border: `1px solid ${color}22`, borderTop: `2px solid ${color}`, borderRadius: '10px', padding: '14px 16px', flex: 1, minWidth: 0, position: 'relative', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', top: -10, right: -10, width: 50, height: 50, borderRadius: '50%', background: `${color}10`, filter: 'blur(10px)', pointerEvents: 'none' }} />
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <Icon size={14} color={color} strokeWidth={2} />
                <span style={{ fontSize: '0.6rem', fontFamily: 'Inter', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>{label}</span>
            </div>
            <p style={{ fontFamily: 'Inter', fontWeight: 900, fontSize: '1.4rem', color, lineHeight: 1 }}>
                <Counter value={value} suffix={suffix} />
            </p>
        </motion.div>
    )
}

const PARTICLES = Array.from({ length: 18 }, (_, i) => ({
    id: i, delay: i * 0.4,
    x: `${5 + Math.random() * 90}%`, y: `${5 + Math.random() * 90}%`,
    size: 2 + Math.random() * 3,
    color: ['var(--primary)', 'var(--accent)', 'var(--gold)'][i % 3],
}))

export default function Screen3Dashboard({ onNavigate, activeMission }) {
    const [activeNav, setActiveNav] = useState('Mapa')

    // --- LÓGICA DE INTEGRACIÓN BACKEND ---
    const [userData, setUserData] = useState({
        username: 'Cargando...',
        xp_total: 0,
        level_current: 0,
        streak_days: 0
    });

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                // El interceptor de api.js se encargará de adjuntar el Bearer Token
                const response = await api.get('/api/v1/users/me');
                setUserData(response.data);
            } catch (err) {
                console.error("No se pudo obtener el perfil del campus:", err);
            }
        };
        fetchUserData();
    }, []);

    const handleNav = (item) => { setActiveNav(item.label); onNavigate(item.id) }

    return (
        <div style={{ height: '100vh', background: 'var(--bg)', display: 'flex', overflow: 'hidden' }}>

            {/* ── LEFT SIDEBAR */}
            <aside style={{ width: '220px', flexShrink: 0, background: 'var(--bg2)', borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '24px 16px', gap: '16px', overflow: 'hidden' }}>
                <div style={{ width: '90px', height: '90px', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <motion.svg viewBox="0 0 100 100" width="90" height="90" style={{ position: 'absolute' }}
                        animate={{ opacity: [0.6, 1, 0.6] }} transition={{ repeat: Infinity, duration: 3, ease: 'easeInOut' }}>
                        <polygon points="50,2 93.3,26 93.3,74 50,98 6.7,74 6.7,26" fill="none" stroke="var(--primary)" strokeWidth="2.5" />
                    </motion.svg>
                    <motion.svg viewBox="0 0 100 100" width="72" height="72" style={{ position: 'absolute' }}
                        animate={{ rotate: [0, 360] }} transition={{ repeat: Infinity, duration: 20, ease: 'linear' }}>
                        <polygon points="50,2 93.3,26 93.3,74 50,98 6.7,74 6.7,26" fill="none" stroke="var(--primary)" strokeWidth="0.8" strokeDasharray="12 8" opacity="0.3" />
                    </motion.svg>
                    <User2 size={30} color="var(--text-muted)" strokeWidth={1.5} />
                </div>

                <div style={{ textAlign: 'center' }}>
                    {/* NOMBRE DINÁMICO */}
                    <h3 style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-bright)', fontFamily: 'Inter', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '4px' }}>
                        {userData.username}
                    </h3>
                    <motion.span animate={{ opacity: [0.7, 1, 0.7] }} transition={{ repeat: Infinity, duration: 2.5 }}
                        style={{ fontSize: '0.65rem', color: 'var(--primary)', fontFamily: 'Inter', fontWeight: 600, background: 'var(--primary-glow)', border: '1px solid var(--border)', borderRadius: '5px', padding: '2px 10px', display: 'inline-block' }}>
                        {activeMission ? '⚡ En misión' : 'Explorador Aurum'}
                    </motion.span>
                </div>

                <div style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                        {/* NIVEL DINÁMICO */}
                        <span style={{ fontSize: '0.65rem', fontWeight: 600, color: 'var(--text-muted)', fontFamily: 'Inter' }}>Nivel {userData.level_current}</span>
                        <span style={{ fontSize: '0.65rem', color: 'var(--accent)', fontWeight: 600, fontFamily: 'Inter' }}>{userData.xp_total} / 100 XP</span>
                    </div>
                    <div style={{ background: 'var(--bg)', borderRadius: '9999px', overflow: 'hidden', height: '6px', border: '1px solid var(--border)', position: 'relative' }}>
                            <motion.div initial={{ width: 0 }}
                                animate={{ width: `${Math.min((userData.xp_total % 100), 100)}%` }}
                                transition={{ duration: 1.2, ease: [0.4, 0, 0.2, 1] }}
                                style={{ height: '6px', borderRadius: '9999px', background: 'linear-gradient(90deg, var(--primary), var(--accent))', position: 'relative' }}>
                            <motion.div animate={{ opacity: [0, 1, 0], x: ['0%', '100%'] }} transition={{ repeat: Infinity, duration: 1.8, ease: 'linear' }}
                                style={{ position: 'absolute', top: 0, left: 0, width: '40px', height: '100%', background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent)', borderRadius: '9999px' }} />
                        </motion.div>
                    </div>
                </div>

                <div style={{ background: 'var(--primary-glow)', border: '1px solid var(--border)', borderRadius: '10px', padding: '12px 14px', width: '100%', textAlign: 'center' }}>
                    <motion.div animate={userData.streak_days > 0 ? { scale: [1, 1.15, 1] } : {}} transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}>
                        <Zap size={20} color={userData.streak_days > 0 ? 'var(--primary)' : 'var(--text-muted)'} strokeWidth={2} style={{ display: 'block', margin: '0 auto 4px' }} />
                    </motion.div>
                    {/* RACHA DINÁMICA */}
                    <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', color: userData.streak_days > 0 ? 'var(--primary)' : 'var(--text-muted)' }}>{userData.streak_days} Días</p>
                    <p style={{ fontSize: '0.6rem', color: 'var(--text-muted)', fontFamily: 'Inter', letterSpacing: '0.08em', marginTop: '2px' }}>{userData.streak_days > 0 ? 'RACHA ACTIVA' : 'SIN RACHA AÚN'}</p>
                </div>

            </aside>

            {/* ── CENTER */}
            <main style={{
                flex: 1, overflow: 'auto', padding: '24px', position: 'relative',
            }}>

                {/* Floating particles */}
                <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden' }}>
                    {PARTICLES.map(p => <Particle key={p.id} {...p} />)}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', position: 'relative', zIndex: 1 }}>
                    <h2 style={{ fontSize: '1.4rem', fontFamily: 'Inter', fontWeight: 900 }}>Mapa de progreso</h2>
                    {activeMission && (
                        <motion.div initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
                            style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'var(--accent-glow)', border: '1px solid var(--border-accent)', borderRadius: '8px', padding: '5px 12px' }}>
                            <motion.div animate={{ scale: [1, 1.4, 1] }} transition={{ repeat: Infinity, duration: 1.2 }}
                                style={{ width: '7px', height: '7px', borderRadius: '50%', background: 'var(--accent)' }} />
                            <span style={{ fontFamily: 'Inter', fontSize: '0.65rem', fontWeight: 700, color: 'var(--accent)', letterSpacing: '0.08em' }}>EN VIVO</span>
                        </motion.div>
                    )}
                </div>

                {/* Stat cards row */}
                {activeMission && (
                    <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', position: 'relative', zIndex: 1 }}>
                        <StatCard value={userData.xp_total} label="XP Total" suffix="" color="var(--accent)" Icon={Zap} delay={0} />
                        <StatCard value={activeMission.modules.length} label="Módulos" suffix="" color="var(--primary)" Icon={Layers} delay={0.08} />
                        <StatCard value={userData.streak_days} label="Racha" suffix=" días" color="var(--gold)" Icon={Activity} delay={0.16} />
                    </div>
                )}

                <AnimatePresence mode="wait">
                    {activeMission ? (
                        <motion.div key="active" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }} style={{ position: 'relative', zIndex: 1 }}>
                            {/* Mission banner */}
                            <motion.div
                                initial={{ borderColor: `${activeMission.color}00` }}
                                animate={{ boxShadow: [`0 0 0px ${activeMission.color}00`, `0 0 24px ${activeMission.color}30`, `0 0 0px ${activeMission.color}00`] }}
                                transition={{ repeat: Infinity, duration: 3, ease: 'easeInOut' }}
                                style={{ background: '#1c1c1c', border: `1px solid ${activeMission.color}44`, borderTop: `2px solid ${activeMission.color}`, borderRadius: '12px', padding: '15px 20px', display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '20px' }}>
                                <div style={{ width: '42px', height: '42px', borderRadius: '10px', background: `${activeMission.color}14`, border: `1.5px solid ${activeMission.color}44`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                                    <activeMission.Icon size={22} color={activeMission.color} strokeWidth={1.8} />
                                </div>
                                <div style={{ flex: 1 }}>
                                    <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.65rem', color: activeMission.color, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '2px' }}>Misión activa</p>
                                    <h3 style={{ fontFamily: 'Inter', fontWeight: 800, fontSize: '0.88rem', color: 'var(--text-bright)' }}>{activeMission.title}</h3>
                                </div>
                                <div style={{ display: 'flex', gap: '6px' }}>
                                    {[[Clock, activeMission.estimatedTime], [Layers, `${activeMission.modules.length} mód.`]].map(([Icon, label], i) => (
                                        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '4px', background: 'var(--bg2)', borderRadius: '6px', padding: '4px 9px' }}>
                                            <Icon size={10} color="var(--text-muted)" strokeWidth={2} /><span style={{ fontFamily: 'Inter', fontSize: '0.65rem', color: 'var(--text-muted)' }}>{label}</span>
                                        </div>
                                    ))}
                                </div>
                            </motion.div>

                            {/* Hex path map */}
                            <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '12px', padding: '24px 20px 16px', position: 'relative', overflow: 'hidden' }}>
                                <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }} />
                                <div style={{ position: 'absolute', inset: 0, background: `radial-gradient(ellipse at 50% 20%, ${activeMission.color}07 0%, transparent 60%)`, pointerEvents: 'none' }} />
                                <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.6rem', color: 'var(--text-muted)', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: '18px', position: 'relative', zIndex: 1 }}>
                                    HOJA DE RUTA — {activeMission.modules.length} ETAPAS
                                </p>
                                <HexPathMap modules={activeMission.modules} activeIdx={0} color={activeMission.color} MissionIcon={activeMission.Icon} onNodeClick={() => onNavigate(5)} />
                        <motion.button
                                    style={{ marginTop: '18px', width: '100%', background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: '8px', padding: '12px', fontFamily: 'Inter', fontWeight: 700, fontSize: '0.8rem', cursor: 'pointer', letterSpacing: '0.07em', textTransform: 'uppercase', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', boxShadow: '0 4px 18px var(--primary-glow)', position: 'relative', zIndex: 1 }}
                                    whileHover={{ background: 'var(--primary-dim)', scale: 1.01, boxShadow: '0 6px 24px var(--primary-glow)' }} whileTap={{ scale: 0.97 }}
                                    onClick={() => onNavigate(5)}>
                                    <Zap size={14} strokeWidth={2.5} /> Continuar misión
                                </motion.button>
                            </div>
                        </motion.div>
                    ) : (
                        <motion.div key="empty" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }}
                            style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '12px', minHeight: '420px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', padding: '40px', position: 'relative', overflow: 'hidden', zIndex: 1 }}>
                            <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }} />
                            <motion.svg viewBox="0 0 100 100" width="88" height="88" animate={{ rotate: [0, 360] }} transition={{ repeat: Infinity, duration: 24, ease: 'linear' }}>
                                <polygon points="50,4 93.3,27 93.3,73 50,96 6.7,73 6.7,27" fill="var(--primary-glow)" stroke="var(--primary)" strokeWidth="1.5" strokeDasharray="10 5" opacity="0.5" />
                            </motion.svg>
                            <Map size={32} color="var(--secondary)" strokeWidth={1.5} style={{ position: 'absolute' }} />
                            <div style={{ textAlign: 'center', position: 'relative', zIndex: 1, marginTop: '60px' }}>
                                <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', color: 'var(--text-bright)', marginBottom: '8px' }}>Selecciona una misión para empezar</h3>
                                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'Inter', maxWidth: '260px', lineHeight: '1.6' }}>Tu mapa de progreso aparecerá aquí cuando inicies tu primera misión.</p>
                            </div>
                            <motion.button style={{ marginTop: '8px', background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: '8px', padding: '11px 22px', fontFamily: 'Inter', fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer', boxShadow: '0 4px 16px var(--primary-glow)', position: 'relative', zIndex: 1, display: 'flex', alignItems: 'center', gap: '8px' }}
                                whileHover={{ background: 'var(--primary-dim)', scale: 1.02 }} whileTap={{ scale: 0.97 }}
                                onClick={() => onNavigate(4)}>
                                Ver misiones <ChevronRight size={15} />
                            </motion.button>
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>

            {/* ── RIGHT SIDEBAR */}
            <aside style={{ width: '256px', flexShrink: 0, padding: '20px 14px', display: 'flex', flexDirection: 'column', gap: '10px', overflowY: 'auto', borderLeft: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <div style={{ width: '3px', height: '15px', background: 'var(--primary)', borderRadius: '2px' }} />
                    <h3 style={{ fontSize: '0.78rem', fontFamily: 'Inter', fontWeight: 700, color: 'var(--text-bright)' }}>{activeMission ? 'Módulos' : 'Para empezar'}</h3>
                </div>

                {activeMission ? (
                    <>
                        {activeMission.modules.slice(0, 5).map((mod, i) => (
                            <motion.div key={i} initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.07 }}
                                style={{ background: 'var(--card)', border: '1px solid var(--border)', borderLeft: `3px solid ${i === 0 ? activeMission.color : 'var(--bg2)'}`, borderRadius: '9px', padding: '10px 13px' }}>
                                <div style={{ display: 'flex', gap: '9px', alignItems: 'center' }}>
                                    <div style={{ width: '20px', height: '20px', borderRadius: '50%', flexShrink: 0, background: i === 0 ? `${activeMission.color}18` : 'var(--bg2)', border: `1px solid ${i === 0 ? activeMission.color + '44' : 'var(--border)'}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Inter', fontWeight: 700, fontSize: '0.58rem', color: i === 0 ? activeMission.color : 'var(--text-muted)' }}>{i + 1}</div>
                                    <p style={{ fontSize: '0.76rem', fontFamily: 'Inter', fontWeight: i === 0 ? 600 : 400, color: i === 0 ? 'var(--text-bright)' : 'var(--text-muted)', lineHeight: 1.35, flex: 1 }}>{mod.title}</p>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '7px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '3px' }}><Clock size={9} color="var(--text-muted)" strokeWidth={2} /><span style={{ fontFamily: 'Inter', fontSize: '0.62rem', color: 'var(--text-muted)' }}>{mod.duration}</span></div>
                                    {i === 0 && <motion.span animate={{ opacity: [1, 0.5, 1] }} transition={{ repeat: Infinity, duration: 1.5 }} style={{ fontFamily: 'Inter', fontSize: '0.58rem', color: activeMission.color, fontWeight: 700, letterSpacing: '0.08em' }}>ACTUAL</motion.span>}
                                </div>
                            </motion.div>
                        ))}
                        <motion.button style={{ marginTop: '4px', fontSize: '0.78rem', padding: '11px', width: '100%', background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: '9px', fontFamily: 'Inter', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 14px var(--primary-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
                            whileHover={{ background: 'var(--primary-dim)' }} whileTap={{ scale: 0.97 }} onClick={() => onNavigate(5)}>
                            <Zap size={13} strokeWidth={2.5} /> Continuar
                        </motion.button>
                    </>
                ) : (
                    <>
                        {EMPTY_STARTERS.map((m, i) => (
                            <motion.div key={i} initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.09 }}
                                whileHover={{ boxShadow: `0 0 14px ${m.color}20`, x: 2 }} onClick={() => onNavigate(4)}
                                style={{ background: 'var(--card)', border: '1px solid var(--border)', borderLeft: `3px solid ${m.color}`, borderRadius: '9px', padding: '13px', cursor: 'pointer', transition: 'all 0.2s' }}>
                                <div style={{ display: 'flex', gap: '9px', alignItems: 'center', marginBottom: '9px' }}>
                                    <div style={{ width: '28px', height: '28px', flexShrink: 0, borderRadius: '7px', background: `${m.color}14`, border: `1px solid ${m.color}33`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <m.Icon size={14} color={m.color} strokeWidth={2} />
                                    </div>
                                    <p style={{ fontSize: '0.77rem', fontFamily: 'Inter', fontWeight: 500, color: 'var(--text-muted)', lineHeight: 1.35 }}>{m.label}</p>
                                </div>
                                <div style={{ background: 'var(--bg)', borderRadius: '9999px', height: '4px', border: '1px solid var(--border)', marginBottom: '7px', overflow: 'hidden' }}>
                                    <div style={{ height: '4px', width: '0%', borderRadius: '9999px', background: 'linear-gradient(90deg, var(--primary), var(--accent))' }} />
                                </div>
                                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'rgba(255,167,38,0.1)', border: '1px solid rgba(255,167,38,0.3)', borderRadius: '5px', padding: '2px 9px', fontFamily: 'Inter', fontSize: '0.62rem', fontWeight: 700, color: '#FFA726', letterSpacing: '0.04em' }}>{m.reward}</span>
                            </motion.div>
                        ))}
                        <motion.button style={{ marginTop: '4px', fontSize: '0.8rem', padding: '12px', width: '100%', background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: '9px', fontFamily: 'Inter', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 14px var(--primary-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
                            whileHover={{ background: 'var(--primary-dim)', scale: 1.01 }} whileTap={{ scale: 0.97 }} onClick={() => onNavigate(4)}>
                            Ver misiones <ChevronRight size={14} />
                        </motion.button>
                    </>
                )}
            </aside>
        </div>
    )
}