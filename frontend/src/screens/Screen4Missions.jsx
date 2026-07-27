import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import api from '../services/api' // Tu puente con el backend
import {
    Flame, Lock, Cloud, Handshake, Palette,
    ChevronRight, X, Clock, Layers, Building2,
    Star, Zap, Award, CheckCircle2, ArrowRight,
    Sparkles, Brain, Filter, Search, Grid, List,
    Cpu, Briefcase, Pen, Globe, Target, Shuffle,
    PlayCircle, BookOpen, MonitorPlay, ArrowLeft
} from 'lucide-react'

const TABS = ['Misiones Principales', 'Misiones Secundarias', 'Explorar catálogo']

// Mapa de iconos para asignar dinámicamente según la categoría de la DB
const ICON_MAP = {
    'Tecnología': Cpu,
    'Negocios': Briefcase,
    'Diseño': Pen,
    'Marketing': Flame,
    'Ciberseguridad': Target,
    'Cloud': Cloud,
};

const CATEGORIES = ['Todos', 'Tecnología', 'Negocios', 'Diseño', 'Marketing']
const DIFFICULTY_LABELS = { 1: 'Básico', 2: 'Básico', 3: 'Intermedio', 4: 'Avanzado' }

// AI indicator badge
function AIBadge({ active }) {
    return (
        <motion.div
            animate={{ opacity: active ? [0.7, 1, 0.7] : 1 }}
            transition={{ repeat: active ? Infinity : 0, duration: 2 }}
            style={{ display: 'flex', alignItems: 'center', gap: '7px', background: 'var(--accent-glow)', border: '1px solid var(--border-accent)', borderRadius: '8px', padding: '6px 14px' }}>
            <Brain size={13} color="var(--accent)" strokeWidth={2} />
            <span style={{ fontFamily: 'Inter', fontSize: '0.7rem', fontWeight: 600, color: 'var(--accent)' }}>
                {active ? 'IA actualizando preferencias...' : 'Catálogo inteligente'}
            </span>
            {active && (
                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.2, ease: 'linear' }}>
                    <Sparkles size={11} color="var(--accent)" strokeWidth={2} />
                </motion.div>
            )}
        </motion.div>
    )
}

// Catalog card (grid view)
function CatalogCard({ mission, onSelect }) {
    const CategoryIcon = mission.categoryIcon || Target
    return (
        <motion.div
            whileHover={{ y: -4, boxShadow: `0 12px 36px var(--primary-glow)` }}
            onClick={() => onSelect(mission)}
            style={{ background: 'var(--card)', border: '1px solid var(--border)', borderTop: `2px solid ${mission.color}`, borderRadius: '12px', overflow: 'hidden', cursor: 'pointer', transition: 'all 0.2s', display: 'flex', flexDirection: 'column' }}>
            <div style={{ height: '90px', background: `linear-gradient(135deg, var(--bg2) 0%, var(--bg) 100%)`, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', borderBottom: `1px solid var(--border)` }}>
                <div style={{ position: 'absolute', width: '70px', height: '70px', borderRadius: '50%', background: `radial-gradient(circle, ${mission.glow} 0%, transparent 70%)`, pointerEvents: 'none' }} />
                <div style={{ width: '46px', height: '46px', borderRadius: '12px', background: 'var(--bg2)', border: `1.5px solid var(--border)`, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', zIndex: 1 }}>
                    <mission.Icon size={22} color={mission.color} strokeWidth={1.8} />
                </div>
                {!mission.unlocked && (
                    <div style={{ position: 'absolute', inset: 0, backdropFilter: 'blur(4px)', background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
                        <Lock size={16} color="var(--text-muted)" strokeWidth={2} />
                        <span style={{ fontFamily: 'Inter', fontSize: '0.62rem', fontWeight: 600, color: 'var(--text-muted)' }}>Niv. {mission.requiredLevel}</span>
                    </div>
                )}
                <div style={{ position: 'absolute', top: '8px', left: '8px', display: 'flex', alignItems: 'center', gap: '4px', background: 'var(--bg2)', border: `1px solid var(--border)`, borderRadius: '5px', padding: '2px 8px' }}>
                    <CategoryIcon size={9} color={mission.color} strokeWidth={2.5} />
                    <span style={{ fontFamily: 'Inter', fontSize: '0.58rem', fontWeight: 700, color: mission.color, letterSpacing: '0.06em' }}>{mission.category?.toUpperCase() || 'GENERAL'}</span>
                </div>
            </div>
            <div style={{ padding: '14px', flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.78rem', color: 'var(--text-bright)', lineHeight: 1.35, letterSpacing: '0.02em' }}>{mission.title}</h3>
                <p style={{ fontFamily: 'Inter', fontSize: '0.73rem', color: 'var(--text-muted)', lineHeight: 1.45, flex: 1 }}>{mission.subtitle}</p>
                <div style={{ display: 'flex', gap: '4px', alignItems: 'center', marginTop: 'auto' }}>
                    {Array.from({ length: 4 }).map((_, f) => (
                        <Flame key={f} size={11} color={f < mission.difficulty ? 'var(--primary)' : 'var(--border)'} fill={f < mission.difficulty ? 'var(--primary)' : 'none'} strokeWidth={2} />
                    ))}
                    <span style={{ fontFamily: 'Inter', fontSize: '0.62rem', color: 'var(--text-muted)', marginLeft: '4px' }}>{DIFFICULTY_LABELS[mission.difficulty]}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Clock size={10} color="var(--text-muted)" strokeWidth={2} />
                        <span style={{ fontFamily: 'Inter', fontSize: '0.65rem', color: 'var(--text-muted)' }}>{mission.estimatedTime}</span>
                    </div>
                    <span style={{ fontFamily: 'Inter', fontSize: '0.65rem', fontWeight: 700, color: 'var(--accent)' }}>{mission.xp}</span>
                </div>
            </div>
        </motion.div>
    )
}

function SectionTitle({ icon: Icon, label, color }) {
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '7px', marginBottom: '12px' }}>
            <Icon size={13} color={color} strokeWidth={2.5} />
            <span style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.65rem', color, letterSpacing: '0.12em', textTransform: 'uppercase' }}>{label}</span>
        </div>
    )
}

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

const PARTICLES = Array.from({ length: 18 }, (_, i) => ({
    id: i, delay: i * 0.4,
    x: `${5 + Math.random() * 90}%`, y: `${5 + Math.random() * 90}%`,
    size: 2 + Math.random() * 3,
    color: ['var(--primary)', 'var(--accent)', 'var(--gold)'][i % 3],
}))

export default function Screen4Missions({ onStartMission, onNavigate }) {
    const [activeTab, setActiveTab] = useState(0)
    const [centerCard, setCenterCard] = useState(0)
    const [selectedMission, setSelectedMission] = useState(null)
    const [catFilter, setCatFilter] = useState('Todos')
    const [search, setSearch] = useState('')
    const [aiActive, setAiActive] = useState(false)

    // ESTADO PARA EL REPRODUCTOR ESTILO COURSERA/UDEMY
    const [activeCourse, setActiveCourse] = useState(null)
    const [currentStep, setCurrentStep] = useState({ modIndex: 0, stepIndex: 0 })

    // ── LÓGICA DE DATOS REALES ──────────────────────────
    const [dbMissions, setDbMissions] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchMissions = async () => {
            try {
                const response = await api.get('/api/v1/simulaciones')

                // Formateamos los datos asignando plantillas dinámicas
                const formatted = response.data.map((m, index) => {
                    let themeColor = m.color || 'var(--primary)';
                    let themeGlow = `${themeColor}44`;

                    if (m.color === '#00E5FF') { themeColor = 'var(--accent)'; themeGlow = 'var(--accent-glow)'; } 
                    else if (m.color === '#FF4500') { themeColor = 'var(--primary)'; themeGlow = 'var(--primary-glow)'; } 
                    else if (m.color === '#FFA726') { themeColor = 'var(--gold)'; themeGlow = 'var(--primary-glow)'; }

                    // PLANTILLAS DIFERENTES PARA LOS 3 RESULTADOS
                    const TEMPLATES = [
                        // Plantilla 1 (Típicamente IA / Tech)
                        [
                            {
                                title: 'Fase 1: Contextualización', duration: '45m', steps: [
                                    { type: 'video', title: 'Introducción a ' + m.title, desc: `En este video repasaremos los fundamentos y conceptos críticos de ${m.title}.` },
                                    { type: 'lectura', title: 'Documentación técnica', desc: 'Revisa la documentación adjunta antes de proceder con la configuración.' }
                                ]
                            },
                            {
                                title: 'Fase 2: Ejecución Práctica', duration: '1h 30m', steps: [
                                    { type: 'tarea', title: 'Laboratorio de Entrenamiento', desc: `Inicia la simulación para implementar los requerimientos de ${m.title} en un entorno controlado.` }
                                ]
                            }
                        ],
                        // Plantilla 2 (Típicamente Negocios / Diseño)
                        [
                            {
                                title: 'Módulo A: Análisis del Caso', duration: '30m', steps: [
                                    { type: 'lectura', title: 'Requisitos del cliente', desc: `Briefing detallado del proyecto sobre ${m.title}.` },
                                    { type: 'video', title: 'Reunión de Kickoff', desc: 'Grabación de la toma de requerimientos iniciales con el stakeholder.' }
                                ]
                            },
                            {
                                title: 'Módulo B: Desarrollo', duration: '2h', steps: [
                                    { type: 'video', title: 'Setup de herramientas', desc: 'Configuración del espacio de trabajo.' },
                                    { type: 'tarea', title: 'Armado de Propuesta', desc: 'Ingresa al workspace para construir la propuesta final.' }
                                ]
                            }
                        ],
                        // Plantilla 3 (Genérica / Tareas rápidas)
                        [
                            {
                                title: 'Etapa Única: Acción Inmediata', duration: '50m', steps: [
                                    { type: 'video', title: 'Brief de la misión', desc: `Video corto explicando tu objetivo en ${m.title}.` },
                                    { type: 'tarea', title: 'Despliegue de Tarea', desc: 'Accede a la terminal y ejecuta los comandos necesarios para resolver el ticket.' }
                                ]
                            }
                        ]
                    ];

                    // Le asigna una plantilla distinta usando el índice (0, 1, o 2)
                    const assignedModules = TEMPLATES[index % 3];

                    return {
                        ...m,
                        color: themeColor,
                        Icon: ICON_MAP[m.category] || Target,
                        categoryIcon: ICON_MAP[m.category] || Target,
                        glow: themeGlow,
                        unlocked: true, 
                        requiredLevel: 1,
                        // Si la DB ya trae módulos los usa, si no, usa la plantilla dinámica generada arriba
                        modules: m.modules?.length ? m.modules : assignedModules,
                        skills: m.skills?.length ? m.skills : ['Habilidad Analítica', 'Resolución'],
                        xp: m.xp || `+${Math.floor(Math.random() * 200 + 100)} XP`,
                        badge: m.badge || 'Insignia de Operador'
                    }
                })

                setDbMissions(formatted)
            } catch (err) {
                console.error("Error cargando misiones del campus:", err)
            } finally {
                setLoading(false)
            }
        }
        fetchMissions()
    }, [])

    const handleCardClick = (mission, idx) => {
        setCenterCard(idx)
        if (mission.unlocked) setSelectedMission(mission)
    }

    const handleCatalogInteract = () => {
        setAiActive(true)
        setTimeout(() => setAiActive(false), 3000)
    }

    // Abre el reproductor en lugar de ir directo al workspace
    const handleStartCourse = (mission) => {
        setActiveCourse(mission)
        setCurrentStep({ modIndex: 0, stepIndex: 0 })
        setSelectedMission(null)
    }

    const catalogMissions = dbMissions.filter(m => {
        const matchCat = catFilter === 'Todos' || m.category === catFilter
        const matchSearch = !search || m.title.toLowerCase().includes(search.toLowerCase()) || m.subtitle.toLowerCase().includes(search.toLowerCase())
        return matchCat && matchSearch
    })

    return (
        <div style={{
            minHeight: '100vh', background: 'var(--bg)',
            padding: '28px 24px 100px 24px', position: 'relative',
        }}>
            {/* Floating particles */}
            <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden' }}>
                {PARTICLES.map(p => <Particle key={p.id} {...p} />)}
            </div>

            {/* Header */}
            <div style={{ textAlign: 'center', marginBottom: '22px' }}>
                <span style={{ fontSize: '0.65rem', fontFamily: 'Inter', color: 'var(--primary)', letterSpacing: '0.18em', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>// Tablón de operaciones</span>
                <h1 style={{ fontSize: '1.8rem', fontFamily: 'Inter', fontWeight: 900, color: 'var(--text-bright)' }}>MISIONES ACTIVAS</h1>
            </div>

            {/* Tabs */}
            <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginBottom: '28px', flexWrap: 'wrap' }}>
                {TABS.map((tab, i) => (
                    <motion.button key={i} onClick={() => setActiveTab(i)}
                        whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                        style={{ padding: '8px 18px', borderRadius: '8px', background: activeTab === i ? 'var(--primary)' : 'var(--card)', color: activeTab === i ? '#fff' : 'var(--text-muted)', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.65rem', cursor: 'pointer', letterSpacing: '0.07em', textTransform: 'uppercase', border: activeTab === i ? 'none' : '1px solid var(--border)', boxShadow: activeTab === i ? '0 4px 16px var(--primary-glow)' : 'none', transition: 'all 0.25s ease', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        {i === 2 && <Brain size={12} strokeWidth={2.5} />}{tab}
                    </motion.button>
                ))}
            </div>

            <AnimatePresence mode="wait">
                {/* CAROUSEL DINÁMICO */}
                {activeTab < 2 && (
                    <motion.div key="missions" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '20px', padding: '10px 0 40px', flexWrap: 'wrap' }}>
                            {loading ? (
                                <p style={{ color: '#444', fontFamily: 'monospace' }}>ESCANEANDO RED DE SIMULACIONES...</p>
                            ) : dbMissions.length > 0 ? (
                                dbMissions.slice(0, 3).map((mission, idx) => {
                                    const isCenter = idx === centerCard
                                    return (
                                        <motion.div key={mission.id || idx} onClick={() => handleCardClick(mission, idx)}
                                            animate={{ scale: isCenter ? 1.05 : 0.92, y: isCenter ? -8 : 0, opacity: isCenter ? 1 : 0.65 }}
                                            whileHover={{ scale: isCenter ? 1.07 : 0.96 }}
                                            transition={{ duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
                                            style={{ width: '300px', flexShrink: 0, background: 'var(--card)', borderRadius: '12px', overflow: 'hidden', cursor: 'pointer', border: `1px solid ${isCenter ? mission.color : 'var(--border)'}`, borderTop: `2px solid ${mission.color}`, boxShadow: isCenter ? `0 0 24px ${mission.glow}, 0 20px 48px rgba(0,0,0,0.6)` : '0 8px 24px rgba(0,0,0,0.5)' }}>
                                            <div style={{ height: '130px', background: `linear-gradient(135deg, var(--bg2) 0%, var(--bg) 100%)`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '8px', position: 'relative', borderBottom: `1px solid var(--border)` }}>
                                                <div style={{ position: 'absolute', width: '90px', height: '90px', borderRadius: '50%', background: `radial-gradient(circle, ${mission.glow} 0%, transparent 70%)`, pointerEvents: 'none' }} />
                                                <div style={{ width: '52px', height: '52px', borderRadius: '14px', background: 'var(--bg2)', border: `1.5px solid var(--border)`, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', zIndex: 1 }}>
                                                    <mission.Icon size={26} color={mission.color} strokeWidth={1.8} />
                                                </div>
                                            </div>
                                            <div style={{ padding: '16px' }}>
                                                <h3 style={{ fontSize: '0.8rem', marginBottom: '5px', lineHeight: 1.35, fontFamily: 'Inter', fontWeight: 700, color: isCenter ? mission.color : 'var(--text-bright)' }}>{mission.title}</h3>
                                                <p style={{ color: 'var(--text-muted)', fontSize: '0.77rem', marginBottom: '12px', lineHeight: 1.5 }}>{mission.subtitle}</p>
                                                <div style={{ display: 'flex', gap: '6px', marginBottom: '14px', flexWrap: 'wrap' }}>
                                                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'var(--accent-glow)', border: '1px solid var(--border-accent)', borderRadius: '5px', padding: '3px 9px', fontFamily: 'Inter', fontSize: '0.63rem', fontWeight: 700, color: 'var(--accent)' }}><Zap size={10} strokeWidth={2.5} /> {mission.xp}</span>
                                                </div>
                                                <motion.button style={{ width: '100%', padding: '11px', borderRadius: '8px', background: isCenter ? 'var(--primary)' : 'var(--card)', color: isCenter ? '#fff' : 'var(--text-muted)', border: isCenter ? 'none' : '1px solid var(--border)', fontFamily: 'Inter', fontWeight: 700, fontSize: '0.7rem', cursor: 'pointer', textTransform: 'uppercase' }}
                                                    whileHover={isCenter ? { background: 'var(--primary-dim)' } : {}} whileTap={{ scale: 0.97 }}
                                                    onClick={e => { e.stopPropagation(); if (isCenter) setSelectedMission(mission) }}>
                                                    {isCenter ? 'VER DETALLES' : 'SELECCIONAR'}
                                                </motion.button>
                                            </div>
                                        </motion.div>
                                    )
                                })
                            ) : (
                                <p style={{ color: '#555' }}>No hay misiones disponibles actualmente.</p>
                            )}
                        </div>
                    </motion.div>
                )}

                {/* CATÁLOGO DINÁMICO */}
                {activeTab === 2 && (
                    <motion.div key="catalog" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '18px', flexWrap: 'wrap' }}>
                            <AIBadge active={aiActive} />
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '8px', padding: '7px 13px', flex: 1, maxWidth: '600px' }}>
                                <Search size={13} color="var(--text-muted)" />
                                <input value={search} onChange={e => { setSearch(e.target.value); handleCatalogInteract() }} placeholder="Buscar en el catálogo..." style={{ background: 'transparent', border: 'none', outline: 'none', fontFamily: 'Inter', fontSize: '0.78rem', color: 'var(--text-bright)', flex: 1 }} />
                            </div>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '14px' }}>
                            {catalogMissions.map(m => (
                                <CatalogCard key={m.id} mission={m} onSelect={ms => { setSelectedMission(ms); handleCatalogInteract() }} />
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* DETALLE MODAL */}
            <AnimatePresence>
                {selectedMission && (
                    <>
                        <motion.div key="backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setSelectedMission(null)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(6px)', zIndex: 100 }} />
                        <div style={{ position: 'fixed', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 101, pointerEvents: 'none' }}>
                            <motion.div initial={{ scale: 0.88, opacity: 0, y: 20 }} animate={{ scale: 1, opacity: 1, y: 0 }} exit={{ scale: 0.88, opacity: 0, y: 20 }}
                                style={{ width: 'min(720px, 94vw)', maxHeight: '86vh', background: 'var(--bg2)', border: `1px solid var(--border)`, borderTop: `2px solid ${selectedMission.color}`, borderRadius: '16px', display: 'flex', flexDirection: 'column', overflow: 'hidden', pointerEvents: 'all' }}>

                                <div style={{ padding: '20px 26px 16px', borderBottom: `1px solid var(--border)`, background: 'var(--card)' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '13px' }}>
                                            <div style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'var(--bg)', border: `1.5px solid var(--border)`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                                <selectedMission.Icon size={24} color={selectedMission.color} />
                                            </div>
                                            <div>
                                                <span style={{ fontSize: '0.6rem', color: selectedMission.color, fontWeight: 700 }}>{selectedMission.category?.toUpperCase()}</span>
                                                <h2 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-bright)' }}>{selectedMission.title}</h2>
                                            </div>
                                        </div>
                                        <button onClick={() => setSelectedMission(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}><X size={20} /></button>
                                    </div>
                                </div>

                                <div style={{ overflowY: 'auto', flex: 1, padding: '22px 26px' }}>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '22px' }}>
                                        <div>
                                            <SectionTitle icon={ChevronRight} label="Descripción" color={selectedMission.color} />
                                            <p style={{ fontSize: '0.82rem', color: 'var(--text)', lineHeight: 1.7 }}>{selectedMission.description}</p>

                                            <div style={{ marginTop: '20px' }}>
                                                <SectionTitle icon={Star} label="Habilidades" color={selectedMission.color} />
                                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                                    {selectedMission.skills.map(s => <div key={s} style={{ fontSize: '0.7rem', color: selectedMission.color, background: 'var(--bg)', border: '1px solid var(--border)', padding: '4px 10px', borderRadius: '5px' }}>{s}</div>)}
                                                </div>
                                            </div>
                                        </div>
                                        <div>
                                            <SectionTitle icon={Layers} label="Hoja de ruta" color={selectedMission.color} />
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
                                                {selectedMission.modules.map((mod, i) => (
                                                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '7px', padding: '10px' }}>
                                                        <span style={{ fontSize: '0.7rem', fontWeight: 700, color: selectedMission.color }}>{i + 1}</span>
                                                        <p style={{ fontSize: '0.8rem', color: 'var(--text)', flex: 1 }}>{mod.title}</p>
                                                        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{mod.duration}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div style={{ padding: '16px 26px', background: 'var(--card)', borderTop: `1px solid var(--border)`, display: 'flex', gap: '14px' }}>
                                    <motion.button style={{ flex: 1, padding: '13px', borderRadius: '9px', background: 'var(--primary)', color: '#fff', border: 'none', fontWeight: 700, cursor: 'pointer', textTransform: 'uppercase' }}
                                        whileHover={{ background: 'var(--primary-dim)' }} whileTap={{ scale: 0.97 }}
                                        onClick={() => handleStartCourse(selectedMission)}>
                                        INICIAR MISIÓN
                                    </motion.button>
                                </div>
                            </motion.div>
                        </div>
                    </>
                )}
            </AnimatePresence>

            {/* REPRODUCTOR DE CURSO (Estilo Coursera/Udemy) */}
            <AnimatePresence>
                {activeCourse && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }}
                        style={{ position: 'fixed', inset: 0, background: 'var(--bg)', zIndex: 200, display: 'flex', flexDirection: 'column' }}>

                        {/* Navbar de navegación */}
                        <div style={{ height: '64px', borderBottom: '1px solid var(--border)', background: 'var(--bg2)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 24px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                <button onClick={() => setActiveCourse(null)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.8rem' }}>
                                    <ArrowLeft size={16} /> Volver al catálogo
                                </button>
                                <div style={{ width: '1px', height: '24px', background: 'var(--border)' }} />
                                <h2 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-bright)' }}>{activeCourse.title}</h2>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'Inter' }}>Progreso:</span>
                                <div style={{ width: '120px', height: '6px', background: 'var(--bg)', borderRadius: '3px', overflow: 'hidden' }}>
                                    <div style={{ width: `${Math.max(10, ((currentStep.modIndex + 1) / activeCourse.modules.length) * 100)}%`, height: '100%', background: activeCourse.color, transition: 'width 0.4s ease' }} />
                                </div>
                            </div>
                        </div>

                        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
                            {/* Panel Principal */}
                            <div style={{ flex: 1, background: 'var(--bg)', padding: '32px', overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
                                {(() => {
                                    const step = activeCourse.modules[currentStep.modIndex].steps[currentStep.stepIndex];
                                    return (
                                        <div style={{ maxWidth: '800px', width: '100%', margin: '0 auto', flex: 1, display: 'flex', flexDirection: 'column' }}>
                                            <h1 style={{ fontFamily: 'Inter', fontWeight: 800, fontSize: '1.5rem', color: 'var(--text-bright)', marginBottom: '24px' }}>{step.title}</h1>

                                            <div style={{ flex: 1, background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '12px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px', textAlign: 'center' }}>
                                                {step.type === 'video' && (
                                                    <>
                                                        <MonitorPlay size={64} color={activeCourse.color} strokeWidth={1} style={{ marginBottom: '20px', opacity: 0.8 }} />
                                                        <h3 style={{ fontFamily: 'Inter', fontSize: '1.1rem', color: 'var(--text-bright)', marginBottom: '8px' }}>Reproductor Multimedia</h3>
                                                        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', maxWidth: '500px' }}>{step.desc}</p>
                                                    </>
                                                )}
                                                {step.type === 'lectura' && (
                                                    <>
                                                        <BookOpen size={64} color={activeCourse.color} strokeWidth={1} style={{ marginBottom: '20px', opacity: 0.8 }} />
                                                        <h3 style={{ fontFamily: 'Inter', fontSize: '1.1rem', color: 'var(--text-bright)', marginBottom: '8px' }}>Material de Lectura</h3>
                                                        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', maxWidth: '500px' }}>{step.desc}</p>
                                                    </>
                                                )}
                                                {step.type === 'tarea' && (
                                                    <>
                                                        <CheckCircle2 size={64} color="var(--primary)" strokeWidth={1} style={{ marginBottom: '20px', opacity: 0.8 }} />
                                                        <h3 style={{ fontFamily: 'Inter', fontSize: '1.1rem', color: 'var(--text-bright)', marginBottom: '8px' }}>Misión Práctica</h3>
                                                        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '24px', maxWidth: '500px' }}>{step.desc}</p>
                                                        <motion.button onClick={() => { setActiveCourse(null); onStartMission(activeCourse); }}
                                                            whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                                                            style={{ padding: '14px 24px', background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: '8px', fontFamily: 'Inter', fontWeight: 700, fontSize: '0.8rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', textTransform: 'uppercase', boxShadow: '0 4px 20px var(--primary-glow)' }}>
                                                            <Sparkles size={16} /> Abrir Workspace de Tareas
                                                        </motion.button>
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })()}
                            </div>

                            {/* Sidebar del Temario */}
                            <div style={{ width: '340px', background: 'var(--bg2)', borderLeft: '1px solid var(--border)', display: 'flex', flexDirection: 'column' }}>
                                <div style={{ padding: '20px', borderBottom: '1px solid var(--border)' }}>
                                    <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-bright)' }}>Contenido del Curso</h3>
                                </div>
                                <div style={{ overflowY: 'auto', flex: 1, padding: '16px' }}>
                                    {activeCourse.modules.map((mod, mI) => (
                                        <div key={mI} style={{ marginBottom: '16px' }}>
                                            <div style={{ padding: '12px 14px', background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '8px 8px 0 0', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                                <span style={{ fontSize: '0.65rem', fontWeight: 700, color: activeCourse.color, textTransform: 'uppercase' }}>Sección {mI + 1}</span>
                                                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-bright)' }}>{mod.title}</span>
                                            </div>
                                            <div style={{ border: '1px solid var(--border)', borderTop: 'none', borderRadius: '0 0 8px 8px', overflow: 'hidden' }}>
                                                {mod.steps.map((step, sI) => {
                                                    const isActive = currentStep.modIndex === mI && currentStep.stepIndex === sI;
                                                    const StepIcon = step.type === 'video' ? PlayCircle : step.type === 'lectura' ? BookOpen : CheckCircle2;
                                                    return (
                                                        <div key={sI} onClick={() => setCurrentStep({ modIndex: mI, stepIndex: sI })}
                                                            style={{ padding: '12px 14px', display: 'flex', alignItems: 'center', gap: '12px', background: isActive ? 'var(--primary-glow)' : 'var(--bg)', borderBottom: '1px solid var(--border)', cursor: 'pointer', transition: 'all 0.2s' }}>
                                                            <StepIcon size={14} color={isActive ? 'var(--primary)' : 'var(--text-muted)'} />
                                                            <span style={{ fontSize: '0.75rem', fontFamily: 'Inter', color: isActive ? 'var(--primary)' : 'var(--text)', fontWeight: isActive ? 600 : 400 }}>{step.title}</span>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}