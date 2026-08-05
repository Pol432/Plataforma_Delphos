import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Map, Target, Users, User2, ChevronRight, UserCircle, MapPin, Zap, CheckCircle2, Clock, Layers, Activity, BookOpen, ChevronDown } from 'lucide-react'
import api from '../services/api' 

const EMPTY_STARTERS = [
    { label: 'Completa tu perfil', reward: '+30 Puntos', Icon: UserCircle, color: 'var(--primary)' },
    { label: 'Explora el mapa de progreso', reward: '+20 Puntos', Icon: MapPin, color: 'var(--accent)' },
    { label: 'Acepta tu primer módulo', reward: '+50 Puntos', Icon: Zap, color: 'var(--primary)' },
]

function TimelineMap({ modules, activeIdx, color, onNodeClick }) {
    return (
        <div style={{ padding: '10px 0', display: 'flex', flexDirection: 'column', gap: '0' }}>
            {modules.map((mod, i) => {
                const isCompleted = i < activeIdx;
                const isCurrent = i === activeIdx;
                const isLocked = i > activeIdx;
                
                return (
                    <div key={i} style={{ display: 'flex', gap: '16px', position: 'relative' }}>
                        {/* Timeline Line */}
                        {i < modules.length - 1 && (
                            <div style={{ 
                                position: 'absolute', left: '15px', top: '30px', bottom: '-20px', 
                                width: '2px', background: isCompleted ? color : 'var(--border)', 
                                zIndex: 0 
                            }} />
                        )}
                        
                        {/* Timeline Node */}
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', zIndex: 1 }}>
                            <div 
                                onClick={isCurrent ? () => onNodeClick(5) : undefined}
                                style={{ 
                                    width: '32px', height: '32px', borderRadius: '50%', 
                                    background: isCompleted ? color : isCurrent ? 'var(--bg2)' : 'var(--bg)', 
                                    border: `2px solid ${isCompleted || isCurrent ? color : 'var(--border)'}`, 
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    cursor: isCurrent ? 'pointer' : 'default',
                                    transition: 'all 0.2s'
                                }}>
                                {isCompleted ? (
                                    <CheckCircle2 size={16} color="#fff" strokeWidth={3} />
                                ) : isCurrent ? (
                                    <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: color }} />
                                ) : (
                                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>{i + 1}</span>
                                )}
                            </div>
                        </div>

                        {/* Content Card */}
                        <div style={{ 
                            flex: 1, paddingBottom: '24px', 
                            opacity: isLocked ? 0.6 : 1 
                        }}>
                            <div style={{ 
                                background: isCurrent ? 'var(--card)' : 'transparent', 
                                border: isCurrent ? `1px solid ${color}` : '1px solid transparent', 
                                borderRadius: '8px', padding: '12px 16px',
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                            }}>
                                <div>
                                    <h4 style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-bright)', marginBottom: '4px' }}>
                                        {mod.title}
                                    </h4>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                        <Clock size={12} color="var(--text-muted)" />
                                        <span style={{ fontFamily: 'Inter', fontSize: '0.7rem', color: 'var(--text-muted)' }}>{mod.duration}</span>
                                    </div>
                                </div>
                                {isCurrent && (
                                    <button 
                                        onClick={() => onNodeClick(5)}
                                        style={{ 
                                            background: color, color: '#fff', border: 'none', 
                                            borderRadius: '6px', padding: '6px 14px', 
                                            fontFamily: 'Inter', fontSize: '0.7rem', fontWeight: 600, 
                                            cursor: 'pointer' 
                                        }}>
                                        Continuar
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    )
}

function StatCard({ value, label, color, Icon, delay = 0 }) {
    return (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}
            style={{ background: 'var(--card)', border: '1px solid var(--border)', borderLeft: `3px solid ${color}`, borderRadius: '8px', padding: '16px', flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: 'var(--bg)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon size={20} color={color} />
            </div>
            <div>
                <p style={{ fontFamily: 'Inter', fontWeight: 800, fontSize: '1.2rem', color: 'var(--text-bright)', lineHeight: 1 }}>
                    {value}
                </p>
                <span style={{ fontSize: '0.65rem', fontFamily: 'Inter', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '4px', display: 'block' }}>{label}</span>
            </div>
        </motion.div>
    )
}

export default function Screen3Dashboard({ onNavigate, activeModule }) {
    const [userData, setUserData] = useState({
        username: 'Cargando...',
        xp_total: 0,
        level_current: 0,
        streak_days: 0
    });

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const response = await api.get('/api/v1/users/me');
                setUserData(response.data);
            } catch (err) {
                console.error("No se pudo obtener el perfil del campus:", err);
            }
        };
        fetchUserData();
    }, []);

    return (
        <div style={{ height: '100vh', background: 'var(--bg)', display: 'flex', overflow: 'hidden' }}>

            {/* ── LEFT SIDEBAR */}
            <aside style={{ width: '240px', flexShrink: 0, background: 'var(--bg2)', borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '32px 20px', gap: '24px', overflow: 'hidden' }}>
                <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'var(--card)', border: '2px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <User2 size={32} color="var(--text-muted)" strokeWidth={1.5} />
                </div>

                <div style={{ textAlign: 'center', width: '100%' }}>
                    <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-bright)', fontFamily: 'Inter', marginBottom: '4px' }}>
                        {userData.username}
                    </h3>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'Inter' }}>
                        Estudiante Aurum
                    </span>
                </div>

                <div style={{ width: '100%', background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '8px', padding: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-muted)', fontFamily: 'Inter' }}>Progreso de Ruta</span>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-bright)', fontWeight: 700, fontFamily: 'Inter' }}>{userData.xp_total % 100}%</span>
                    </div>
                    <div style={{ background: 'var(--bg)', borderRadius: '4px', overflow: 'hidden', height: '6px', width: '100%' }}>
                        <div style={{ width: `${Math.min((userData.xp_total % 100), 100)}%`, height: '100%', background: 'var(--primary)', borderRadius: '4px', transition: 'width 0.5s ease' }} />
                    </div>
                </div>

                <div style={{ width: '100%', background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '8px', padding: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Activity size={20} color="var(--primary)" />
                    <div>
                        <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-bright)' }}>{userData.streak_days} Días</p>
                        <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontFamily: 'Inter' }}>Estudio constante</p>
                    </div>
                </div>
            </aside>

            {/* ── CENTER */}
            <main style={{
                flex: 1, overflow: 'auto', padding: '32px 40px', position: 'relative', background: 'var(--bg)'
            }}>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
                    <h2 style={{ fontSize: '1.4rem', fontFamily: 'Inter', fontWeight: 800, color: 'var(--text-bright)' }}>Mi Aprendizaje</h2>
                </div>

                {activeModule && (
                    <div style={{ display: 'flex', gap: '16px', marginBottom: '32px' }}>
                        <StatCard value={userData.xp_total} label="Puntos de Avance" color="var(--accent)" Icon={Zap} delay={0} />
                        <StatCard value={activeModule.modules.length} label="Módulos" color="var(--primary)" Icon={BookOpen} delay={0.08} />
                        <StatCard value={userData.streak_days} label="Días seguidos" color="var(--accent)" Icon={Activity} delay={0.16} />
                    </div>
                )}

                <AnimatePresence mode="wait">
                    {activeModule ? (
                        <motion.div key="active" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }}>
                            {/* Mission banner */}
                            <div style={{ background: 'var(--card)', border: `1px solid var(--border)`, borderLeft: `4px solid ${activeModule.color}`, borderRadius: '12px', padding: '20px 24px', display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
                                <div style={{ width: '48px', height: '48px', borderRadius: '8px', background: 'var(--bg)', border: `1px solid var(--border)`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                                    <activeModule.Icon size={24} color={activeModule.color} />
                                </div>
                                <div style={{ flex: 1 }}>
                                    <p style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>Módulo activo</p>
                                    <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-bright)' }}>{activeModule.title}</h3>
                                </div>
                                <div style={{ display: 'flex', gap: '12px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '6px', padding: '6px 12px' }}>
                                        <Clock size={12} color="var(--text-muted)" />
                                        <span style={{ fontFamily: 'Inter', fontSize: '0.75rem', color: 'var(--text-muted)' }}>{activeModule.estimatedTime}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Timeline map */}
                            <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '12px', padding: '24px 32px' }}>
                                <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', color: 'var(--text-bright)', marginBottom: '24px' }}>
                                    Hoja de Ruta del Curso
                                </h3>
                                <TimelineMap modules={activeModule.modules} activeIdx={0} color={activeModule.color} onNodeClick={() => onNavigate(5)} />
                            </div>
                        </motion.div>
                    ) : (
                        <motion.div key="empty" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }}
                            style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '12px', minHeight: '400px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', padding: '40px' }}>
                            <BookOpen size={48} color="var(--border)" strokeWidth={1} style={{ marginBottom: '16px' }} />
                            <div style={{ textAlign: 'center' }}>
                                <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-bright)', marginBottom: '8px' }}>Selecciona una ruta para empezar</h3>
                                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontFamily: 'Inter', maxWidth: '300px', lineHeight: '1.6' }}>Tu progreso aparecerá aquí cuando inicies tu primer curso.</p>
                            </div>
                            <button style={{ marginTop: '16px', background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: '8px', padding: '12px 24px', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}
                                onClick={() => onNavigate(4)}>
                                Explorar Catálogo
                            </button>
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>

            {/* ── RIGHT SIDEBAR */}
            <aside style={{ width: '280px', flexShrink: 0, background: 'var(--bg2)', padding: '32px 20px', borderLeft: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto' }}>
                <div>
                    <h3 style={{ fontSize: '0.9rem', fontFamily: 'Inter', fontWeight: 700, color: 'var(--text-bright)', marginBottom: '16px' }}>{activeModule ? 'Próximas Etapas' : 'Tareas Sugeridas'}</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {activeModule ? (
                            activeModule.modules.slice(1, 4).map((mod, i) => (
                                <div key={i} style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '8px', padding: '12px' }}>
                                    <h4 style={{ fontSize: '0.75rem', fontFamily: 'Inter', fontWeight: 600, color: 'var(--text-bright)', marginBottom: '6px' }}>{mod.title}</h4>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                        <Clock size={10} color="var(--text-muted)" />
                                        <span style={{ fontFamily: 'Inter', fontSize: '0.65rem', color: 'var(--text-muted)' }}>{mod.duration}</span>
                                    </div>
                                </div>
                            ))
                        ) : (
                            EMPTY_STARTERS.map((m, i) => (
                                <div key={i} onClick={() => onNavigate(4)}
                                    style={{ background: 'var(--card)', border: '1px solid var(--border)', borderLeft: `3px solid ${m.color}`, borderRadius: '8px', padding: '14px', cursor: 'pointer' }}>
                                    <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '8px' }}>
                                        <m.Icon size={16} color={m.color} />
                                        <p style={{ fontSize: '0.8rem', fontFamily: 'Inter', fontWeight: 500, color: 'var(--text-bright)' }}>{m.label}</p>
                                    </div>
                                    <span style={{ display: 'inline-block', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '4px', padding: '2px 8px', fontFamily: 'Inter', fontSize: '0.65rem', color: 'var(--text-muted)' }}>{m.reward}</span>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </aside>
        </div>
    )
}