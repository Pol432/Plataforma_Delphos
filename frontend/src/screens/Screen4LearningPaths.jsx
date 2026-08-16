import { useState, useEffect } from 'react'
        import {motion, AnimatePresence} from 'framer-motion'
        import api from '../services/api'
        import {
            Flame, Lock, Cloud, Handshake, Palette,
            ChevronRight, X, Clock, Layers, Building2,
            Star, Zap, Award, CheckCircle2, ArrowRight,
            Sparkles, Brain, Filter, Search, Grid, List,
            Cpu, Briefcase, Pen, Globe, Target, Shuffle,
            PlayCircle, BookOpen, MonitorPlay, ArrowLeft
        } from 'lucide-react'

        const TABS = ['Rutas Principales', 'Módulos Secundarios', 'Explorar Catálogo']

        const ICON_MAP = {
            'Tecnología': Cpu,
        'Negocios': Briefcase,
        'Diseño': Pen,
        'Marketing': Flame,
        'Ciberseguridad': Target,
        'Cloud': Cloud,
};

        const DIFFICULTY_LABELS = {1: 'Básico', 2: 'Básico', 3: 'Intermedio', 4: 'Avanzado' }

        function AIBadge({active}) {
    return (
        <motion.div
            animate={{ opacity: active ? [0.7, 1, 0.7] : 1 }}
            transition={{ repeat: active ? Infinity : 0, duration: 2 }}
            style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '4px', padding: '8px 16px' }}>
            <Brain size={16} color="var(--primary)" strokeWidth={2} />
            <span style={{ fontFamily: 'Inter', fontSize: '0.85rem', fontWeight: 600, color: 'var(--primary)' }}>
                {active ? 'IA actualizando recomendaciones...' : 'Catálogo inteligente'}
            </span>
            {active && (
                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.2, ease: 'linear' }}>
                    <Sparkles size={14} color="var(--primary)" strokeWidth={2} />
                </motion.div>
            )}
        </motion.div>
        )
}

        function CatalogCard({module, onSelect}) {
    const CategoryIcon = module.categoryIcon || BookOpen
        return (
        <motion.div
            whileHover={{ y: -4, boxShadow: '0 12px 24px rgba(0,0,0,0.08)' }}
            onClick={() => onSelect(module)}
            style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: '8px', overflow: 'hidden', cursor: 'pointer', transition: 'all 0.2s', display: 'flex', flexDirection: 'column', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>

            <div style={{ height: '140px', background: `${module.color}15`, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
                    <module.Icon size={32} color={module.color} strokeWidth={1.5} />
                </div>
                {!module.unlocked && (
                    <div style={{ position: 'absolute', top: '12px', right: '12px', background: '#fff', borderRadius: '4px', padding: '4px 8px', display: 'flex', alignItems: 'center', gap: '4px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
                        <Lock size={12} color="var(--text-muted)" />
                        <span style={{ fontFamily: 'Inter', fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-muted)' }}>Pro</span>
                    </div>
                )}
                <div style={{ position: 'absolute', bottom: '12px', left: '12px', display: 'flex', alignItems: 'center', gap: '6px', background: '#fff', borderRadius: '4px', padding: '4px 10px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                    <CategoryIcon size={12} color={module.color} strokeWidth={2} />
                    <span style={{ fontFamily: 'Inter', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-bright)' }}>{module.category || 'General'}</span>
                </div>
            </div>

            <div style={{ padding: '20px', flex: 1, display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-bright)', lineHeight: 1.3 }}>{module.title}</h3>
                <p style={{ fontFamily: 'Inter', fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.5, flex: 1 }}>{module.subtitle}</p>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto', paddingTop: '16px', borderTop: '1px solid var(--border)' }}>
                    <span style={{ fontFamily: 'Inter', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>{DIFFICULTY_LABELS[module.difficulty]}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Clock size={14} color="var(--text-muted)" />
                        <span style={{ fontFamily: 'Inter', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>{module.estimatedTime}</span>
                    </div>
                </div>
            </div>
        </motion.div>
        )
}

        function SectionTitle({icon: Icon, label, color }) {
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <Icon size={18} color={color} />
            <span style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', color: 'var(--text-bright)' }}>{label}</span>
        </div>
        )
}

        export default function Screen4LearningPaths({onStartModule, onNavigate}) {
    const [activeTab, setActiveTab] = useState(0)
        const [centerCard, setCenterCard] = useState(0)
        const [selectedModule, setSelectedModule] = useState(null)
        const [catFilter, setCatFilter] = useState('Todos')
        const [search, setSearch] = useState('')
        const [aiActive, setAiActive] = useState(false)
        const [activeCourse, setActiveCourse] = useState(null)
        const [currentStep, setCurrentStep] = useState({modIndex: 0, stepIndex: 0 })
        const [dbModules, setDbModules] = useState([])
        const [aiPaths, setAiPaths] = useState([])
        const [aiRecs, setAiRecs] = useState([])
        const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchModules = async () => {
            try {
                const response = await api.get('/api/v1/simulaciones')
                const formatted = response.data.map((m, index) => {
            let themeColor = 'var(--primary)';
        if (m.color === '#00E5FF') themeColor = 'var(--accent)';
        if (m.color === '#FF4500') themeColor = 'var(--primary)';

        const TEMPLATES = [
        [
        {
            title: 'Fase 1: Contextualización', duration: '45m', steps: [
        {type: 'video', title: 'Introducción a ' + m.title, desc: `En este video repasaremos los fundamentos y conceptos críticos de ${m.title}.` },
        {type: 'lectura', title: 'Documentación técnica', desc: 'Revisa la documentación adjunta antes de proceder con la configuración.' }
        ]
                            },
        {
            title: 'Fase 2: Ejecución Práctica', duration: '1h 30m', steps: [
        {type: 'tarea', title: 'Laboratorio de Entrenamiento', desc: `Inicia la simulación para implementar los requerimientos de ${m.title} en un entorno controlado.` }
        ]
                            }
        ],
        [
        {
            title: 'Módulo A: Análisis del Caso', duration: '30m', steps: [
        {type: 'lectura', title: 'Requisitos del cliente', desc: `Briefing detallado del proyecto sobre ${m.title}.` },
        {type: 'video', title: 'Reunión de Kickoff', desc: 'Grabación de la toma de requerimientos iniciales con el stakeholder.' }
        ]
                            },
        {
            title: 'Módulo B: Desarrollo', duration: '2h', steps: [
        {type: 'video', title: 'Setup de herramientas', desc: 'Configuración del espacio de trabajo.' },
        {type: 'tarea', title: 'Armado de Propuesta', desc: 'Ingresa al workspace para construir la propuesta final.' }
        ]
                            }
        ],
        [
        {
            title: 'Etapa Única: Acción Inmediata', duration: '50m', steps: [
        {type: 'video', title: 'Brief del módulo', desc: `Video corto explicando tu objetivo en ${m.title}.` },
        {type: 'tarea', title: 'Despliegue de Tarea', desc: 'Accede a la terminal y ejecuta los comandos necesarios para resolver el ticket.' }
        ]
                            }
        ]
        ];
        const assignedModules = TEMPLATES[index % 3];
        return {
            ...m,
            color: themeColor,
        Icon: ICON_MAP[m.category] || BookOpen,
        categoryIcon: ICON_MAP[m.category] || BookOpen,
        unlocked: true,
        requiredLevel: 1,
        modules: m.modules?.length ? m.modules : assignedModules,
        skills: m.skills?.length ? m.skills : ['Habilidad Analítica', 'Resolución'],
        badge: m.badge || 'Certificado de Finalización'
                    }
                })
        setDbModules(formatted)

        // Load AI Data
        const savedPaths = localStorage.getItem('oracleLearningPaths')
        const savedRecs = localStorage.getItem('oracleRecommendations')

        if (savedPaths) {
            const parsedPaths = JSON.parse(savedPaths)
            setAiPaths(parsedPaths.map((p, i) => ({
                id: `ai-path-${i}`,
                title: p.name || p.title || 'Ruta Generada',
                subtitle: p.category || 'Recomendación de IA',
                category: p.category || 'General',
                color: 'var(--primary)',
                Icon: Sparkles,
                categoryIcon: Brain,
                unlocked: true,
                difficulty: p.difficulty_level ? 3 : 2,
                estimatedTime: p.duration_hours ? `${p.duration_hours}h` : '4h',
                modules: p.steps ? p.steps.map(s => ({
                    title: s.step_title || s.title,
                    duration: '1h',
                    steps: [
                        {type: 'video', title: 'Intro: ' + (s.step_title || s.title), desc: s.focus || '' },
                        {type: 'tarea', title: 'Práctica', desc: 'Aplica lo aprendido' }
                    ]
                })) : [
                    {
                        title: 'Fase 1: Contextualización', duration: '45m', steps: [
                            {type: 'video', title: 'Introducción', desc: 'Revisión de fundamentos.' },
                            {type: 'lectura', title: 'Documentación', desc: 'Revisa la documentación técnica.' }
                        ]
                    }
                ],
                skills: p.matched_skills && p.matched_skills.length > 0 ? p.matched_skills : ['IA Recomendada', p.name || 'Ruta'],
                description: p.description || `Ruta enfocada en ${p.category || 'aprendizaje'}`
            })))
        }

        if (savedRecs) {
                    const parsedRecs = JSON.parse(savedRecs)
                    setAiRecs(parsedRecs.map((r, i) => ({
            id: `ai-rec-${i}`,
        title: r.title,
        subtitle: r.motivo,
        category: r.categoria,
        color: 'var(--accent)',
        Icon: Target,
        categoryIcon: Target,
        unlocked: true,
        difficulty: 2,
        estimatedTime: '2h',
        modules: TEMPLATES[0],
        skills: ['Recomendado', r.categoria],
        description: r.motivo
                    })))
                }

            } catch (err) {
            console.error("Error cargando módulos:", err)
        } finally {
            setLoading(false)
        }
        }
        fetchModules()
    }, [])

    const handleCardClick = (module, idx) => {
            setCenterCard(idx)
        if (module.unlocked) setSelectedModule(module)
    }

    const handleCatalogInteract = () => {
            setAiActive(true)
        setTimeout(() => setAiActive(false), 3000)
    }

    const handleStartCourse = (module) => {
            setActiveCourse(module)
        setCurrentStep({modIndex: 0, stepIndex: 0 })
        setSelectedModule(null)
    }

        let displayedModules = dbModules;
    if (activeTab === 0 && aiPaths.length > 0) {
            displayedModules = aiPaths;
    } else if (activeTab === 1 && aiRecs.length > 0) {
            displayedModules = aiRecs;
    }

    const catalogModules = displayedModules.filter(m => {
        const matchCat = catFilter === 'Todos' || m.category === catFilter
        const matchSearch = !search || m.title.toLowerCase().includes(search.toLowerCase()) || m.subtitle?.toLowerCase().includes(search.toLowerCase())
        return matchCat && matchSearch
    })

        return (
        <div style={{ minHeight: '100vh', background: '#f8f9fa', padding: '48px 48px 120px 48px', position: 'relative' }}>
            <div style={{ marginBottom: '40px' }}>
                <h1 style={{ fontSize: '2.5rem', fontFamily: 'Outfit, sans-serif', fontWeight: 700, color: 'var(--text-bright)', marginBottom: '12px' }}>Catálogo de Aprendizaje</h1>
                <p style={{ fontFamily: 'Inter', fontSize: '1.1rem', color: 'var(--text-muted)' }}>Explora nuestras rutas formativas y comienza a desarrollar habilidades clave.</p>
            </div>

            <div style={{ display: 'flex', gap: '32px', marginBottom: '48px', borderBottom: '1px solid var(--border)' }}>
                {TABS.map((tab, i) => (
                    <div key={i} onClick={() => setActiveTab(i)}
                        style={{ padding: '12px 0', borderBottom: activeTab === i ? '2px solid var(--primary)' : '2px solid transparent', color: activeTab === i ? 'var(--primary)' : 'var(--text-muted)', fontFamily: 'Inter', fontWeight: 600, fontSize: '1rem', cursor: 'pointer', transition: 'all 0.2s ease', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {tab}
                    </div>
                ))}
            </div>

            <AnimatePresence mode="wait">
                {activeTab < 2 && (
                    <motion.div key="modules" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                        <div style={{ display: 'flex', gap: '32px', padding: '20px 0', overflowX: 'auto', paddingBottom: '40px' }}>
                            {loading ? (
                                <p style={{ color: 'var(--text-muted)', fontFamily: 'Inter', fontSize: '1.1rem' }}>Cargando rutas de aprendizaje...</p>
                            ) : displayedModules.length > 0 ? (
                                displayedModules.slice(0, 3).map((module, idx) => {
                                    const isCenter = idx === centerCard
                                    return (
                                        <motion.div key={module.id || idx} onClick={() => handleCardClick(module, idx)}
                                            animate={{ scale: isCenter ? 1.05 : 0.95, opacity: isCenter ? 1 : 0.7 }}
                                            whileHover={{ scale: isCenter ? 1.05 : 0.98 }}
                                            transition={{ duration: 0.3 }}
                                            style={{ width: '340px', flexShrink: 0, background: '#fff', borderRadius: '8px', overflow: 'hidden', cursor: 'pointer', border: '1px solid var(--border)', boxShadow: isCenter ? '0 12px 24px rgba(0,0,0,0.08)' : '0 4px 12px rgba(0,0,0,0.03)' }}>
                                            <div style={{ height: '160px', background: `${module.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                                <div style={{ width: '72px', height: '72px', borderRadius: '50%', background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
                                                    <module.Icon size={36} color={module.color} />
                                                </div>
                                            </div>
                                            <div style={{ padding: '24px' }}>
                                                <h3 style={{ fontSize: '1.2rem', marginBottom: '8px', lineHeight: 1.3, fontFamily: 'Inter', fontWeight: 700, color: 'var(--text-bright)' }}>{module.title}</h3>
                                                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px', lineHeight: 1.5 }}>{module.subtitle}</p>
                                                <motion.button style={{ width: '100%', padding: '14px', borderRadius: '4px', background: isCenter ? 'var(--primary)' : '#f0f2f5', color: isCenter ? '#fff' : 'var(--text-bright)', border: 'none', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.95rem', cursor: 'pointer', transition: 'background 0.2s' }}
                                                    whileHover={isCenter ? { background: 'var(--primary-dim)' } : {}} whileTap={{ scale: 0.98 }}
                                                    onClick={e => { e.stopPropagation(); if (isCenter) setSelectedModule(module) }}>
                                                    {isCenter ? 'Ver detalles del curso' : 'Seleccionar'}
                                                </motion.button>
                                            </div>
                                        </motion.div>
                                    )
                                })
                            ) : (
                                <p style={{ color: 'var(--text-muted)', fontFamily: 'Inter', fontSize: '1.1rem' }}>No hay rutas disponibles actualmente.</p>
                            )}
                        </div>
                    </motion.div>
                )}

                {activeTab === 2 && (
                    <motion.div key="catalog" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '24px', marginBottom: '32px', flexWrap: 'wrap' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: '#fff', border: '1px solid var(--border)', borderRadius: '4px', padding: '12px 16px', flex: 1, maxWidth: '600px', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
                                <Search size={20} color="var(--text-muted)" />
                                <input value={search} onChange={e => { setSearch(e.target.value); handleCatalogInteract() }} placeholder="Buscar cursos, habilidades o certificaciones..." style={{ background: 'transparent', border: 'none', outline: 'none', fontFamily: 'Inter', fontSize: '1rem', color: 'var(--text-bright)', flex: 1 }} />
                            </div>
                            <AIBadge active={aiActive} />
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '24px' }}>
                            {catalogModules.map(m => (
                                <CatalogCard key={m.id} module={m} onSelect={ms => { setSelectedModule(ms); handleCatalogInteract() }} />
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            <AnimatePresence>
                {selectedModule && (
                    <>
                        <motion.div key="backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setSelectedModule(null)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(4px)', zIndex: 100 }} />
                        <div style={{ position: 'fixed', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 101, pointerEvents: 'none' }}>
                            <motion.div initial={{ scale: 0.95, opacity: 0, y: 20 }} animate={{ scale: 1, opacity: 1, y: 0 }} exit={{ scale: 0.95, opacity: 0, y: 20 }}
                                style={{ width: '100%', maxWidth: '800px', maxHeight: '90vh', background: '#fff', borderRadius: '12px', display: 'flex', flexDirection: 'column', overflow: 'hidden', pointerEvents: 'all', boxShadow: '0 24px 48px rgba(0,0,0,0.15)' }}>

                                {/* Modal Header */}
                                <div style={{ padding: '32px 40px', background: '#fff', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <div style={{ display: 'flex', gap: '24px' }}>
                                        <div style={{ width: '80px', height: '80px', borderRadius: '8px', background: `${selectedModule.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                                            <selectedModule.Icon size={40} color={selectedModule.color} />
                                        </div>
                                        <div>
                                            <span style={{ fontFamily: 'Inter', fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600, display: 'block', marginBottom: '8px', textTransform: 'uppercase' }}>{selectedModule.category?.toUpperCase() || 'GENERAL'}</span>
                                            <h2 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '2rem', fontWeight: 700, color: 'var(--text-bright)', lineHeight: 1.2, marginBottom: '12px' }}>{selectedModule.title}</h2>
                                            <p style={{ fontFamily: 'Inter', fontSize: '1rem', color: 'var(--text-muted)' }}>{selectedModule.subtitle}</p>
                                        </div>
                                    </div>
                                    <button onClick={() => setSelectedModule(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: '8px' }}>
                                        <X size={24} />
                                    </button>
                                </div>

                                {/* Modal Body */}
                                <div style={{ overflowY: 'auto', flex: 1, padding: '40px' }}>
                                    <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: '48px' }}>
                                        <div>
                                            <SectionTitle icon={BookOpen} label="Acerca de este curso" color="var(--primary)" />
                                            <p style={{ fontFamily: 'Inter', fontSize: '1rem', color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: '32px' }}>{selectedModule.description}</p>

                                            <SectionTitle icon={Star} label="Lo que aprenderás" color="var(--primary)" />
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                                                {selectedModule.skills.map(s => (
                                                    <div key={s} style={{ fontFamily: 'Inter', fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-bright)', background: '#f0f2f5', padding: '8px 16px', borderRadius: '4px' }}>{s}</div>
                                                ))}
                                            </div>
                                        </div>

                                        <div>
                                            <SectionTitle icon={Layers} label="Temario del curso" color="var(--primary)" />
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                                                {selectedModule.modules.map((mod, i) => (
                                                    <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
                                                        <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#f8f9fa', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, border: '1px solid var(--border)' }}>
                                                            <span style={{ fontFamily: 'Inter', fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-muted)' }}>{i + 1}</span>
                                                        </div>
                                                        <div>
                                                            <p style={{ fontFamily: 'Inter', fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-bright)', marginBottom: '4px' }}>{mod.title}</p>
                                                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                                <Clock size={12} color="var(--text-muted)" />
                                                                <span style={{ fontFamily: 'Inter', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{mod.duration}</span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Modal Footer */}
                                <div style={{ padding: '24px 40px', background: '#f8f9fa', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'flex-end' }}>
                                    <motion.button style={{ padding: '16px 32px', borderRadius: '4px', background: 'var(--primary)', color: '#fff', border: 'none', fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', cursor: 'pointer', transition: 'background 0.2s' }}
                                        whileHover={{ background: 'var(--primary-dim)' }} whileTap={{ scale: 0.98 }}
                                        onClick={() => handleStartCourse(selectedModule)}>
                                        Inscribirse gratis
                                    </motion.button>
                                </div>
                            </motion.div>
                        </div>
                    </>
                )}
            </AnimatePresence>

            <AnimatePresence>
                {activeCourse && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }}
                        style={{ position: 'fixed', inset: 0, background: '#fff', zIndex: 200, display: 'flex', flexDirection: 'column' }}>

                        {/* Player Header */}
                        <div style={{ height: '72px', borderBottom: '1px solid var(--border)', background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 32px', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
                                <button onClick={() => setActiveCourse(null)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.95rem' }}>
                                    <ArrowLeft size={20} /> Volver
                                </button>
                                <div style={{ width: '1px', height: '32px', background: 'var(--border)' }} />
                                <h2 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.2rem', color: 'var(--text-bright)' }}>{activeCourse.title}</h2>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <span style={{ fontFamily: 'Inter', fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500 }}>Progreso del curso:</span>
                                <div style={{ width: '200px', height: '8px', background: '#f0f2f5', borderRadius: '4px', overflow: 'hidden' }}>
                                    <div style={{ width: `${Math.max(5, ((currentStep.modIndex + 1) / activeCourse.modules.length) * 100)}%`, height: '100%', background: 'var(--primary)', transition: 'width 0.4s ease' }} />
                                </div>
                            </div>
                        </div>

                        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
                            {/* Main Content Area */}
                            <div style={{ flex: 1, background: '#f8f9fa', padding: '48px', overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
                                {(() => {
                                    const step = activeCourse.modules[currentStep.modIndex].steps[currentStep.stepIndex];
                                    return (
                                        <div style={{ maxWidth: '900px', width: '100%', margin: '0 auto', flex: 1, display: 'flex', flexDirection: 'column' }}>
                                            <h1 style={{ fontFamily: 'Inter', fontWeight: 800, fontSize: '2rem', color: 'var(--text-bright)', marginBottom: '32px' }}>{step.title}</h1>
                                            <div style={{ flex: 1, background: '#fff', border: '1px solid var(--border)', borderRadius: '8px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '64px', textAlign: 'center', boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
                                                {step.type === 'video' && (
                                                    <>
                                                        <div style={{ width: '100px', height: '100px', borderRadius: '50%', background: 'rgba(59,130,246,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '32px' }}>
                                                            <MonitorPlay size={48} color="var(--primary)" />
                                                        </div>
                                                        <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.4rem', color: 'var(--text-bright)', marginBottom: '16px' }}>Reproductor Multimedia</h3>
                                                        <p style={{ color: 'var(--text-muted)', fontFamily: 'Inter', fontSize: '1.1rem', maxWidth: '600px', lineHeight: 1.6 }}>{step.desc}</p>
                                                    </>
                                                )}
                                                {step.type === 'lectura' && (
                                                    <>
                                                        <div style={{ width: '100px', height: '100px', borderRadius: '50%', background: 'rgba(16,185,129,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '32px' }}>
                                                            <BookOpen size={48} color="#10B981" />
                                                        </div>
                                                        <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.4rem', color: 'var(--text-bright)', marginBottom: '16px' }}>Material de Lectura</h3>
                                                        <p style={{ color: 'var(--text-muted)', fontFamily: 'Inter', fontSize: '1.1rem', maxWidth: '600px', lineHeight: 1.6 }}>{step.desc}</p>
                                                    </>
                                                )}
                                                {step.type === 'tarea' && (
                                                    <>
                                                        <div style={{ width: '100px', height: '100px', borderRadius: '50%', background: 'rgba(245,158,11,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '32px' }}>
                                                            <CheckCircle2 size={48} color="#F59E0B" />
                                                        </div>
                                                        <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.4rem', color: 'var(--text-bright)', marginBottom: '16px' }}>Laboratorio Práctico</h3>
                                                        <p style={{ color: 'var(--text-muted)', fontFamily: 'Inter', fontSize: '1.1rem', marginBottom: '40px', maxWidth: '600px', lineHeight: 1.6 }}>{step.desc}</p>
                                                        <motion.button onClick={() => { setActiveCourse(null); onStartModule(activeCourse); }}
                                                            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                                                            style={{ padding: '16px 32px', background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: '4px', fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '12px' }}>
                                                            <Sparkles size={20} /> Iniciar laboratorio
                                                        </motion.button>
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })()}
                            </div>

                            {/* Course Sidebar */}
                            <div style={{ width: '400px', background: '#fff', borderLeft: '1px solid var(--border)', display: 'flex', flexDirection: 'column' }}>
                                <div style={{ padding: '24px 32px', borderBottom: '1px solid var(--border)' }}>
                                    <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-bright)' }}>Contenido del Curso</h3>
                                </div>
                                <div style={{ overflowY: 'auto', flex: 1, padding: '24px 32px' }}>
                                    {activeCourse.modules.map((mod, mI) => (
                                        <div key={mI} style={{ marginBottom: '24px' }}>
                                            <div style={{ padding: '16px', background: '#f8f9fa', border: '1px solid var(--border)', borderRadius: '8px 8px 0 0', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                                <span style={{ fontFamily: 'Inter', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Sección {mI + 1}</span>
                                                <span style={{ fontFamily: 'Inter', fontSize: '1rem', fontWeight: 600, color: 'var(--text-bright)' }}>{mod.title}</span>
                                            </div>
                                            <div style={{ border: '1px solid var(--border)', borderTop: 'none', borderRadius: '0 0 8px 8px', overflow: 'hidden' }}>
                                                {mod.steps.map((step, sI) => {
                                                    const isActive = currentStep.modIndex === mI && currentStep.stepIndex === sI;
                                                    const StepIcon = step.type === 'video' ? PlayCircle : step.type === 'lectura' ? BookOpen : CheckCircle2;
                                                    return (
                                                        <div key={sI} onClick={() => setCurrentStep({ modIndex: mI, stepIndex: sI })}
                                                            style={{ padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', background: isActive ? 'rgba(59,130,246,0.05)' : '#fff', borderBottom: '1px solid var(--border)', cursor: 'pointer', transition: 'all 0.2s' }}>
                                                            <StepIcon size={20} color={isActive ? 'var(--primary)' : 'var(--text-muted)'} />
                                                            <span style={{ fontFamily: 'Inter', fontSize: '0.95rem', color: isActive ? 'var(--primary)' : 'var(--text-bright)', fontWeight: isActive ? 600 : 400 }}>{step.title}</span>
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

