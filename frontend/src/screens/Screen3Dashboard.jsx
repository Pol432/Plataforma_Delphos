import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { UserCircle, MapPin, Zap, CheckCircle2, Clock, Activity, BookOpen, ChevronRight } from 'lucide-react'
import api from '../services/api' 

const EMPTY_STARTERS = [
    { label: 'Completa tu perfil', reward: '+30 Puntos', Icon: UserCircle, color: 'var(--primary)' },
    { label: 'Explora el mapa de progreso', reward: '+20 Puntos', Icon: MapPin, color: 'var(--accent)' },
    { label: 'Acepta tu primer módulo', reward: '+50 Puntos', Icon: Zap, color: 'var(--primary)' },
]

function TimelineMap({ modules, activeIdx, color, onNodeClick }) {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
            {modules.map((mod, i) => {
                const isCompleted = i < activeIdx;
                const isCurrent = i === activeIdx;
                const isLocked = i > activeIdx;
                
                return (
                    <div key={i} style={{ display: 'flex', gap: '20px', position: 'relative' }}>
                        {/* Timeline Line */}
                        {i < modules.length - 1 && (
                            <div style={{ 
                                position: 'absolute', left: '15px', top: '32px', bottom: '-8px', 
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
                                    background: isCompleted ? color : '#fff', 
                                    border: `2px solid ${isCompleted || isCurrent ? color : 'var(--border)'}`, 
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    cursor: isCurrent ? 'pointer' : 'default',
                                    boxShadow: isCurrent ? `0 0 0 4px ${color}20` : 'none',
                                    transition: 'all 0.2s'
                                }}>
                                {isCompleted ? (
                                    <CheckCircle2 size={16} color="#fff" strokeWidth={3} />
                                ) : isCurrent ? (
                                    <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: color }} />
                                ) : (
                                    <span style={{ fontFamily: 'Inter', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>{i + 1}</span>
                                )}
                            </div>
                        </div>

                        {/* Content Card */}
                        <div style={{ flex: 1, paddingBottom: '32px', opacity: isLocked ? 0.6 : 1 }}>
                            <div style={{ 
                                background: '#fff', 
                                border: isCurrent ? `1px solid ${color}` : '1px solid var(--border)', 
                                borderRadius: '8px', padding: '16px 20px',
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                boxShadow: isCurrent ? '0 4px 12px rgba(0,0,0,0.05)' : 'none',
                                cursor: isCurrent ? 'pointer' : 'default'
                            }}
                            onClick={isCurrent ? () => onNodeClick(5) : undefined}
                            >
                                <div>
                                    <h4 style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-bright)', marginBottom: '6px' }}>
                                        {mod.title}
                                    </h4>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                        <Clock size={14} color="var(--text-muted)" />
                                        <span style={{ fontFamily: 'Inter', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{mod.duration}</span>
                                    </div>
                                </div>
                                {isCurrent && (
                                    <button 
                                        style={{ 
                                            background: color, color: '#fff', border: 'none', 
                                            borderRadius: '4px', padding: '8px 16px', 
                                            fontFamily: 'Inter', fontSize: '0.85rem', fontWeight: 600, 
                                            cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px'
                                        }}>
                                        Continuar <ChevronRight size={16} />
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
            style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: '8px', padding: '20px', flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
            <div style={{ width: '48px', height: '48px', borderRadius: '8px', background: `${color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon size={24} color={color} />
            </div>
            <div>
                <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.4rem', color: 'var(--text-bright)', lineHeight: 1, marginBottom: '6px' }}>
                    {value}
                </p>
                <span style={{ fontSize: '0.8rem', fontFamily: 'Inter', color: 'var(--text-muted)' }}>{label}</span>
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
    const [recommendations, setRecommendations] = useState([]);

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

        try {
            const savedRecs = localStorage.getItem('oracleRecommendations');
            if (savedRecs) {
                setRecommendations(JSON.parse(savedRecs));
            }
        } catch (e) {
            console.error(e);
        }
    }, []);

    return (
        <div style={{ height: '100vh', background: '#f8f9fa', display: 'flex', overflow: 'hidden' }}>

            {/* ── LEFT SIDEBAR */}
            <aside style={{ width: '260px', flexShrink: 0, background: '#fff', borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '40px 24px', gap: '32px', overflow: 'hidden' }}>
                <div style={{ textAlign: 'center', width: '100%' }}>
                    <div style={{ width: '88px', height: '88px', borderRadius: '50%', background: '#f0f2f5', margin: '0 auto 16px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <UserCircle size={40} color="var(--text-muted)" strokeWidth={1.5} />
                    </div>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-bright)', fontFamily: 'Inter', marginBottom: '6px' }}>
                        {userData.username}
                    </h3>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontFamily: 'Inter' }}>
                        Estudiante Activo
                    </span>
                </div>

                <div style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', fontFamily: 'Inter' }}>Horas de Práctica</span>
                        <span style={{ fontSize: '0.85rem', color: 'var(--primary)', fontWeight: 700, fontFamily: 'Inter' }}>12h</span>
                    </div>
                </div>

                <div style={{ width: '100%', borderTop: '1px solid var(--border)', paddingTop: '24px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                        <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <Activity size={20} color="#10B981" />
                        </div>
                        <div>
                            <p style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', color: 'var(--text-bright)', marginBottom: '2px' }}>3 Módulos</p>
                            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'Inter' }}>Completados</p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* ── CENTER */}
            <main style={{
                flex: 1, overflow: 'auto', padding: '48px', position: 'relative'
            }}>

                <div style={{ marginBottom: '40px' }}>
                    <h2 style={{ fontSize: '2.5rem', fontFamily: 'Outfit, sans-serif', fontWeight: 700, color: 'var(--text-bright)', marginBottom: '8px' }}>Mi Aprendizaje</h2>
                    <p style={{ fontFamily: 'Inter', fontSize: '1rem', color: 'var(--text-muted)' }}>Continúa donde lo dejaste y alcanza tus metas profesionales.</p>
                </div>

                {activeModule && (
                    <div style={{ display: 'flex', gap: '24px', marginBottom: '48px' }}>
                        <StatCard value={"3"} label="Simulaciones" color="var(--primary)" Icon={Zap} delay={0} />
                        <StatCard value={activeModule.modules.length} label="Módulos Totales" color="var(--accent)" Icon={BookOpen} delay={0.1} />
                        <StatCard value={"12h"} label="Práctica" color="#10B981" Icon={Clock} delay={0.2} />
                    </div>
                )}

                <AnimatePresence mode="wait">
                    {activeModule ? (
                        <motion.div key="active" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }}>
                            
                            <h3 style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 700, fontSize: '1.8rem', color: 'var(--text-bright)', marginBottom: '24px' }}>
                                Curso Actual
                            </h3>
                            
                            {/* Mission banner */}
                            <div style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: '8px', padding: '24px 32px', display: 'flex', alignItems: 'center', gap: '24px', marginBottom: '32px', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
                                <div style={{ width: '64px', height: '64px', borderRadius: '8px', background: `${activeModule.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                                    <activeModule.Icon size={32} color={activeModule.color} />
                                </div>
                                <div style={{ flex: 1 }}>
                                    <p style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: '0.85rem', color: 'var(--primary)', marginBottom: '8px' }}>MÓDULO ACTIVO</p>
                                    <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.4rem', color: 'var(--text-bright)' }}>{activeModule.title}</h3>
                                </div>
                                <div style={{ display: 'flex', gap: '12px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#f8f9fa', borderRadius: '4px', padding: '8px 16px' }}>
                                        <Clock size={16} color="var(--text-muted)" />
                                        <span style={{ fontFamily: 'Inter', fontSize: '0.9rem', color: 'var(--text-bright)', fontWeight: 500 }}>{activeModule.estimatedTime} restantes</span>
                                    </div>
                                </div>
                            </div>

                            {/* Timeline map */}
                            <div style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: '8px', padding: '32px 40px', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
                                <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.2rem', color: 'var(--text-bright)', marginBottom: '32px' }}>
                                    Contenido del curso
                                </h3>
                                <TimelineMap modules={activeModule.modules} activeIdx={0} color={activeModule.color} onNodeClick={() => onNavigate(5)} />
                            </div>
                        </motion.div>
                    ) : (
                        <motion.div key="empty" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }}
                            style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: '8px', minHeight: '400px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '20px', padding: '40px', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
                            <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: '#f0f2f5', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '8px' }}>
                                <BookOpen size={40} color="var(--text-muted)" strokeWidth={1.5} />
                            </div>
                            <div style={{ textAlign: 'center' }}>
                                <h3 style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 700, fontSize: '1.8rem', color: 'var(--text-bright)', marginBottom: '12px' }}>Ningún curso en progreso</h3>
                                <p style={{ fontSize: '1rem', color: 'var(--text-muted)', fontFamily: 'Inter', maxWidth: '400px', lineHeight: '1.6' }}>Explora nuestro catálogo para encontrar la ruta de aprendizaje que mejor se adapte a tus metas.</p>
                            </div>
                            <button style={{ marginTop: '24px', background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: '4px', padding: '14px 28px', fontFamily: 'Inter', fontWeight: 600, fontSize: '1rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', transition: 'background 0.2s' }}
                                onClick={() => onNavigate(4)}
                                onMouseOver={(e) => e.currentTarget.style.background = 'var(--primary-dim)'}
                                onMouseOut={(e) => e.currentTarget.style.background = 'var(--primary)'}
                            >
                                Explorar Catálogo
                            </button>
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>

            {/* ── RIGHT SIDEBAR */}
            <aside style={{ width: '320px', flexShrink: 0, background: '#fff', padding: '40px 24px', borderLeft: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto' }}>
                <div>
                    <h3 style={{ fontSize: '1.1rem', fontFamily: 'Inter', fontWeight: 700, color: 'var(--text-bright)', marginBottom: '24px' }}>{activeModule ? 'Próximas Clases' : 'Simulaciones Recomendadas'}</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {activeModule ? (
                            activeModule.modules.slice(1, 4).map((mod, i) => (
                                <div key={i} style={{ background: '#f8f9fa', border: '1px solid var(--border)', borderRadius: '8px', padding: '16px' }}>
                                    <h4 style={{ fontSize: '0.9rem', fontFamily: 'Inter', fontWeight: 600, color: 'var(--text-bright)', marginBottom: '8px', lineHeight: 1.4 }}>{mod.title}</h4>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                        <Clock size={14} color="var(--text-muted)" />
                                        <span style={{ fontFamily: 'Inter', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{mod.duration}</span>
                                    </div>
                                </div>
                            ))
                        ) : (
                            recommendations.length > 0 ? (
                                recommendations.slice(0, 3).map((rec, i) => (
                                    <div key={i} onClick={() => onNavigate(4)}
                                        style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: '8px', padding: '16px', cursor: 'pointer', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '12px' }}>
                                            <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: `rgba(59,130,246,0.1)`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                                <Zap size={18} color="var(--primary)" />
                                            </div>
                                            <span style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-bright)' }}>{rec.title}</span>
                                        </div>
                                        <div style={{ display: 'inline-block', background: '#f0f2f5', color: 'var(--text-muted)', padding: '4px 10px', borderRadius: '4px', fontSize: '0.75rem', fontFamily: 'Inter', fontWeight: 600 }}>
                                            {rec.categoria}
                                        </div>
                                    </div>
                                ))
                            ) : (
                                EMPTY_STARTERS.map((m, i) => (
                                    <div key={i} onClick={() => onNavigate(4)}
                                        style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: '8px', padding: '16px', cursor: 'pointer', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '12px' }}>
                                            <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: `${m.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                                <m.Icon size={18} color={m.color} />
                                            </div>
                                            <span style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-bright)' }}>{m.label}</span>
                                        </div>
                                        <div style={{ display: 'inline-block', background: '#f0f2f5', color: 'var(--text-muted)', padding: '4px 10px', borderRadius: '4px', fontSize: '0.75rem', fontFamily: 'Inter', fontWeight: 600 }}>
                                            Completar
                                        </div>
                                    </div>
                                ))
                            )
                        )}
                    </div>
                </div>
            </aside>
        </div>
    )
}
