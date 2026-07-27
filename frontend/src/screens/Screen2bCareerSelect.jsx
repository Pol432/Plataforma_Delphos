import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import api from '../services/api'
import {
    CheckCircle2, ArrowRight, RotateCcw, Sparkles,
    Cloud, Handshake, Palette, Cpu, BarChart2, Globe,
    Megaphone, ShieldCheck, Lightbulb, FlaskConical, Brain,
    Heart, Stethoscope, Pill, Activity, Eye, Smile,
    Scale, BookOpen, Building, Landmark, Leaf, Zap,
    Camera, Music, PenTool, Code2, Database, Wifi,
    TrendingUp, DollarSign, Users, Truck, Plane, Home,
    Microscope, Atom, Dna, X,
} from 'lucide-react'

// ── Full career catalog ───────────────────────────────────────────────────────
const CAREERS = [
    // Tecnología
    { id: 'cloud', label: 'Cloud & DevOps', icon: Cloud, color: 'var(--accent)', cat: 'Tecnología', affinity: [2, 1, 2] },
    { id: 'software', label: 'Desarrollo de Software', icon: Code2, color: 'var(--accent)', cat: 'Tecnología', affinity: [2, 0, 2] },
    { id: 'data', label: 'Data Analytics', icon: BarChart2, color: 'var(--accent)', cat: 'Tecnología', affinity: [2, 1, 2] },
    { id: 'ai', label: 'Inteligencia Artificial', icon: Brain, color: 'var(--primary)', cat: 'Tecnología', affinity: [2, 0, 2] },
    { id: 'cybersec', label: 'Ciberseguridad', icon: ShieldCheck, color: 'var(--accent)', cat: 'Tecnología', affinity: [2, 1, 1] },
    { id: 'databases', label: 'Bases de Datos', icon: Database, color: 'var(--accent)', cat: 'Tecnología', affinity: [2, 0, 1] },
    { id: 'iot', label: 'IoT & Redes', icon: Wifi, color: 'var(--primary)', cat: 'Tecnología', affinity: [2, 0, 2] },
    { id: 'research', label: 'Investigación & I+D', icon: FlaskConical, color: 'var(--primary)', cat: 'Tecnología', affinity: [1, 1, 2] },
    // Negocios
    { id: 'product', label: 'Product Management', icon: Lightbulb, color: 'var(--gold)', cat: 'Negocios', affinity: [1, 2, 2] },
    { id: 'biz', label: 'Consultoría de Negocios', icon: Handshake, color: 'var(--primary)', cat: 'Negocios', affinity: [0, 2, 1] },
    { id: 'finance', label: 'Finanzas Corporativas', icon: DollarSign, color: 'var(--gold)', cat: 'Negocios', affinity: [2, 1, 0] },
    { id: 'marketing', label: 'Growth & Marketing', icon: Megaphone, color: 'var(--primary)', cat: 'Negocios', affinity: [1, 2, 1] },
    { id: 'intl', label: 'Negocios Internacionales', icon: Globe, color: 'var(--accent)', cat: 'Negocios', affinity: [0, 2, 0] },
    { id: 'hr', label: 'Recursos Humanos', icon: Users, color: 'var(--primary)', cat: 'Negocios', affinity: [0, 2, 1] },
    { id: 'logistics', label: 'Logística & Supply Chain', icon: Truck, color: 'var(--gold)', cat: 'Negocios', affinity: [1, 1, 1] },
    { id: 'ecommerce', label: 'E-commerce & Retail', icon: TrendingUp, color: 'var(--primary)', cat: 'Negocios', affinity: [1, 2, 1] },
    { id: 'banking', label: 'Banca & Inversiones', icon: Landmark, color: 'var(--accent)', cat: 'Negocios', affinity: [2, 1, 0] },
    { id: 'startup', label: 'Emprendimiento', icon: Zap, color: 'var(--gold)', cat: 'Negocios', affinity: [1, 2, 2] },
    // Diseño & Creatividad
    { id: 'ux', label: 'UX / Product Design', icon: Palette, color: 'var(--gold)', cat: 'Diseño', affinity: [0, 1, 2] },
    { id: 'graphic', label: 'Diseño Gráfico', icon: PenTool, color: 'var(--accent)', cat: 'Diseño', affinity: [0, 0, 2] },
    { id: 'architecture', label: 'Arquitectura', icon: Building, color: 'var(--gold)', cat: 'Diseño', affinity: [1, 1, 2] },
    { id: 'interior', label: 'Diseño de Interiores', icon: Home, color: 'var(--primary)', cat: 'Diseño', affinity: [0, 1, 2] },
    { id: 'photo', label: 'Fotografía & Audiovisual', icon: Camera, color: 'var(--accent)', cat: 'Diseño', affinity: [0, 0, 2] },
    { id: 'music', label: 'Producción Musical', icon: Music, color: 'var(--primary)', cat: 'Diseño', affinity: [0, 0, 2] },
    // Salud
    { id: 'medicine', label: 'Medicina', icon: Stethoscope, color: 'var(--primary)', cat: 'Salud', affinity: [2, 1, 1] },
    { id: 'nursing', label: 'Enfermería', icon: Heart, color: 'var(--primary)', cat: 'Salud', affinity: [0, 2, 1] },
    { id: 'pharmacy', label: 'Farmacia', icon: Pill, color: 'var(--accent)', cat: 'Salud', affinity: [2, 1, 1] },
    { id: 'psychology', label: 'Psicología', icon: Smile, color: 'var(--gold)', cat: 'Salud', affinity: [0, 2, 1] },
    { id: 'nutrition', label: 'Nutrición & Dietética', icon: Leaf, color: 'var(--primary)', cat: 'Salud', affinity: [1, 1, 1] },
    { id: 'physio', label: 'Fisioterapia', icon: Activity, color: 'var(--accent)', cat: 'Salud', affinity: [0, 2, 1] },
    { id: 'optometry', label: 'Optometría', icon: Eye, color: 'var(--accent)', cat: 'Salud', affinity: [2, 1, 1] },
    { id: 'biomedical', label: 'Ingeniería Biomédica', icon: Dna, color: 'var(--primary)', cat: 'Salud', affinity: [2, 1, 2] },
    { id: 'publichealth', label: 'Salud Pública', icon: Heart, color: 'var(--primary)', cat: 'Salud', affinity: [0, 2, 1] },
    // Ciencias
    { id: 'bio', label: 'Biología', icon: Microscope, color: 'var(--primary)', cat: 'Ciencias', affinity: [2, 0, 1] },
    { id: 'chem', label: 'Química', icon: FlaskConical, color: 'var(--accent)', cat: 'Ciencias', affinity: [2, 0, 2] },
    { id: 'physics', label: 'Física', icon: Atom, color: 'var(--accent)', cat: 'Ciencias', affinity: [2, 0, 2] },
    { id: 'env', label: 'Ciencias Ambientales', icon: Leaf, color: 'var(--primary)', cat: 'Ciencias', affinity: [1, 1, 2] },
    { id: 'astro', label: 'Astronomía', icon: Sparkles, color: 'var(--accent)', cat: 'Ciencias', affinity: [2, 0, 2] },
    // Ingeniería
    { id: 'civil', label: 'Ingeniería Civil', icon: Building, color: 'var(--gold)', cat: 'Ingeniería', affinity: [2, 1, 1] },
    { id: 'electro', label: 'Ing. Electrónica', icon: Cpu, color: 'var(--accent)', cat: 'Ingeniería', affinity: [2, 0, 2] },
    { id: 'mech', label: 'Ing. Mecánica', icon: Zap, color: 'var(--primary)', cat: 'Ingeniería', affinity: [2, 0, 1] },
    { id: 'aero', label: 'Ing. Aeronáutica', icon: Plane, color: 'var(--accent)', cat: 'Ingeniería', affinity: [2, 0, 2] },
    { id: 'industrial', label: 'Ing. Industrial', icon: TrendingUp, color: 'var(--gold)', cat: 'Ingeniería', affinity: [2, 1, 1] },
    { id: 'energy', label: 'Ing. de Energía', icon: Zap, color: 'var(--primary)', cat: 'Ingeniería', affinity: [2, 0, 2] },
    // Sociales & Humanidades
    { id: 'law', label: 'Derecho', icon: Scale, color: 'var(--gold)', cat: 'Social', affinity: [1, 2, 1] },
    { id: 'journalism', label: 'Periodismo & Comunicación', icon: Megaphone, color: 'var(--primary)', cat: 'Social', affinity: [0, 2, 1] },
    { id: 'education', label: 'Educación & Pedagogía', icon: BookOpen, color: 'var(--primary)', cat: 'Social', affinity: [0, 2, 1] },
    { id: 'polisci', label: 'Ciencias Políticas', icon: Globe, color: 'var(--accent)', cat: 'Social', affinity: [0, 2, 1] },
    { id: 'socialwork', label: 'Trabajo Social', icon: Heart, color: 'var(--primary)', cat: 'Social', affinity: [0, 2, 0] },
    { id: 'tourism', label: 'Turismo & Hotelería', icon: Plane, color: 'var(--gold)', cat: 'Social', affinity: [0, 2, 1] },
]

const CATS = ['Todas', 'Tecnología', 'Negocios', 'Diseño', 'Salud', 'Ciencias', 'Ingeniería', 'Social']

const CAT_COLORS = {
    'Tecnología': 'var(--accent)', 'Negocios': 'var(--primary)', 'Diseño': 'var(--gold)',
    'Salud': 'var(--primary)', 'Ciencias': 'var(--accent)', 'Ingeniería': 'var(--gold)', 'Social': 'var(--primary)',
}

function computeScores(answers) {
    return CAREERS.map(c => {
        let score = 0
        answers.forEach((ans, qi) => { score += ans === 0 ? c.affinity[qi] : (2 - c.affinity[qi]) })
        return { ...c, score }
    }).sort((a, b) => b.score - a.score)
}

// ── Compact career pill ───────────────────────────────────────────────────────
function CareerPill({ career, selected, onToggle, rank }) {
    const Icon = career.icon
    return (
        <motion.button
            onClick={() => onToggle(career.id)}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '9px 12px', borderRadius: '10px', cursor: 'pointer',
                background: selected ? 'var(--card2)' : 'var(--card)',
                border: `1px solid ${selected ? career.color : 'var(--border)'}`,
                transition: 'all 0.18s', textAlign: 'left', width: '100%',
                boxShadow: selected ? `0 0 12px var(--primary-glow)` : 'none',
            }}
        >
            <div style={{ width: '28px', height: '28px', flexShrink: 0, borderRadius: '7px', background: 'var(--bg2)', border: `1px solid var(--border)`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon size={14} color={career.color} strokeWidth={1.8} />
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ fontFamily: 'Inter', fontWeight: selected ? 700 : 500, fontSize: '0.75rem', color: selected ? career.color : 'var(--text)', lineHeight: 1.2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{career.label}</p>
                {rank <= 3 && <p style={{ fontFamily: 'Inter', fontSize: '0.57rem', color: 'var(--gold)', fontWeight: 600, marginTop: '1px' }}>#{rank} afinidad</p>}
            </div>
            {selected && <CheckCircle2 size={13} color={career.color} strokeWidth={2.5} style={{ flexShrink: 0 }} />}
        </motion.button>
    )
}

// ── Main Component ────────────────────────────────────────────────────────────
export default function Screen2bCareerSelect({ oracleAnswers = [], onConfirm, onBackToOracle }) {
    const ranked = useMemo(() => computeScores(oracleAnswers), [oracleAnswers])
    const [selected, setSelected] = useState(new Set())
    const [activecat, setActiveCat] = useState('Todas')
    const [search, setSearch] = useState('')
    const [saving, setSaving] = useState(false)

    const toggle = (id) => setSelected(prev => {
        const next = new Set(prev)
        next.has(id) ? next.delete(id) : next.add(id)
        return next
    })

    // B-04: Guardar carreras en localStorage y enviar al backend
    const handleConfirm = async () => {
        if (selected.size === 0) return
        setSaving(true)
        const careerIds = selectedList.map(c => c.id)
        const careerLabels = selectedList.map(c => c.label)

        // Guardar localmente siempre
        localStorage.setItem('userCareers', JSON.stringify(careerIds))
        localStorage.setItem('userCareerLabels', JSON.stringify(careerLabels))

        try {
            // Intentar persistir en el backend
            await api.patch('/api/v1/users/me', { careers: careerIds })
        } catch (err) {
            // No bloquear el flujo si falla (campo puede no existir aún en el schema)
            console.warn('No se pudo guardar carreras en backend:', err?.response?.status)
        } finally {
            setSaving(false)
            onConfirm(selectedList)
        }
    }

    const visible = useMemo(() => ranked.filter(c => {
        const inCat = activecat === 'Todas' || c.cat === activecat
        const inSearch = !search || c.label.toLowerCase().includes(search.toLowerCase()) || c.cat.toLowerCase().includes(search.toLowerCase())
        return inCat && inSearch
    }), [ranked, activecat, search])

    const selectedList = ranked.filter(c => selected.has(c.id))

    return (
        <div style={{ height: '100vh', background: 'var(--bg)', display: 'flex', flexDirection: 'column' }}>

            {/* ── HEADER */}
            <div style={{ flexShrink: 0, padding: '20px 28px 16px', borderBottom: '1px solid var(--border)', background: 'var(--bg2)' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px', flexWrap: 'wrap' }}>
                    <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '7px', marginBottom: '4px' }}>
                            <div style={{ width: '3px', height: '16px', background: 'var(--primary)', borderRadius: '2px' }} />
                            <span style={{ fontFamily: 'Inter', fontSize: '0.58rem', fontWeight: 700, color: 'var(--primary)', letterSpacing: '0.14em', textTransform: 'uppercase' }}>El Oráculo ha hablado</span>
                        </div>
                        <h1 style={{ fontFamily: 'Inter', fontWeight: 900, fontSize: '1.3rem', color: 'var(--text-bright)', marginBottom: '2px' }}>Elige tus áreas de interés</h1>
                        <p style={{ fontFamily: 'Inter', fontSize: '0.74rem', color: 'var(--text-muted)' }}>Selecciona las que más te llamen la atención — sin límite</p>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
                        <motion.div animate={{ opacity: [0.65, 1, 0.65] }} transition={{ repeat: Infinity, duration: 2.5 }}
                            style={{ display: 'flex', alignItems: 'center', gap: '5px', border: '1px solid var(--border)', background: 'var(--card)', borderRadius: '7px', padding: '6px 12px' }}>
                            <Sparkles size={11} color="var(--accent)" strokeWidth={2} />
                            <span style={{ fontFamily: 'Inter', fontSize: '0.65rem', color: 'var(--accent)', fontWeight: 600 }}>Ordenado por afinidad con el Oráculo</span>
                        </motion.div>
                        <motion.button onClick={onBackToOracle} whileHover={{ background: 'var(--primary-glow)' }} whileTap={{ scale: 0.96 }}
                            style={{ display: 'flex', alignItems: 'center', gap: '6px', border: '1px solid var(--border)', background: 'transparent', borderRadius: '7px', padding: '6px 12px', fontFamily: 'Inter', fontSize: '0.65rem', fontWeight: 600, color: 'var(--primary)', cursor: 'pointer' }}>
                            <RotateCcw size={11} strokeWidth={2.5} /> Más preguntas al Oráculo
                        </motion.button>
                    </div>
                </div>

                {/* Category filters + Search */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '14px', flexWrap: 'wrap' }}>
                    {CATS.map(cat => {
                        const active = activecat === cat
                        const col = cat === 'Todas' ? 'var(--primary)' : CAT_COLORS[cat]
                        return (
                            <motion.button key={cat} onClick={() => setActiveCat(cat)} whileTap={{ scale: 0.95 }}
                                style={{ padding: '5px 13px', borderRadius: '20px', border: `1px solid ${active ? col : 'var(--border)'}`, background: active ? 'var(--bg2)' : 'transparent', color: active ? col : 'var(--text-muted)', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.65rem', cursor: 'pointer', transition: 'all 0.18s' }}>
                                {cat}
                            </motion.button>
                        )
                    })}
                    <div style={{ flex: 1, minWidth: '140px', maxWidth: '220px', position: 'relative' }}>
                        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Buscar carrera..."
                            style={{ width: '100%', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '7px', padding: '5px 30px 5px 11px', fontFamily: 'Inter', fontSize: '0.72rem', color: 'var(--text)', outline: 'none' }} />
                        {search && (
                            <button onClick={() => setSearch('')} style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', padding: 0, color: 'var(--text-muted)', display: 'flex' }}>
                                <X size={12} strokeWidth={2} />
                            </button>
                        )}
                    </div>
                    <span style={{ fontFamily: 'Inter', fontSize: '0.65rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>{visible.length} carreras</span>
                </div>
            </div>

            {/* ── BODY */}
            <div style={{ flex: 1, overflow: 'auto', padding: '16px 28px' }}>
                {visible.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
                        <p style={{ fontFamily: 'Inter', fontSize: '0.85rem' }}>Sin resultados para "<strong style={{ color: 'var(--text)' }}>{search}</strong>"</p>
                    </div>
                ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '8px' }}>
                        {visible.map((career, i) => {
                            const rank = ranked.findIndex(c => c.id === career.id) + 1
                            return <CareerPill key={career.id} career={career} selected={selected.has(career.id)} onToggle={toggle} rank={rank} />
                        })}
                    </div>
                )}
            </div>

            {/* ── FOOTER */}
            <div style={{ flexShrink: 0, background: 'var(--bg2)', borderTop: '1px solid var(--border)', padding: '12px 28px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1, minWidth: 0 }}>
                    {selected.size > 0 ? (
                        <>
                            <CheckCircle2 size={13} color="var(--accent)" strokeWidth={2.5} />
                            <span style={{ fontFamily: 'Inter', fontWeight: 600, fontSize: '0.75rem', color: 'var(--accent)', flexShrink: 0 }}>
                                {selected.size} seleccionada{selected.size !== 1 ? 's' : ''}
                            </span>
                            <div style={{ display: 'flex', gap: '4px', overflow: 'hidden', flex: 1 }}>
                                <AnimatePresence>
                                    {selectedList.slice(0, 4).map(c => (
                                        <motion.span key={c.id} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.8 }}
                                            style={{ fontFamily: 'Inter', fontSize: '0.62rem', fontWeight: 600, color: c.color, background: 'var(--bg)', border: `1px solid var(--border)`, borderRadius: '5px', padding: '2px 8px', whiteSpace: 'nowrap' }}>
                                            {c.label}
                                        </motion.span>
                                    ))}
                                    {selected.size > 4 && (
                                        <span style={{ fontFamily: 'Inter', fontSize: '0.62rem', color: 'var(--text-muted)', padding: '2px 6px' }}>+{selected.size - 4} más</span>
                                    )}
                                </AnimatePresence>
                            </div>
                        </>
                    ) : (
                        <span style={{ fontFamily: 'Inter', fontSize: '0.74rem', color: 'var(--text-muted)' }}>Selecciona al menos un área para continuar</span>
                    )}
                </div>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexShrink: 0 }}>
                    <motion.button onClick={onBackToOracle} whileHover={{ color: 'var(--text)' }} whileTap={{ scale: 0.96 }}
                        style={{ padding: '9px 16px', border: '1px solid var(--border)', background: 'transparent', borderRadius: '7px', fontFamily: 'Inter', fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-muted)', cursor: 'pointer' }}>
                        Continuar con el Oráculo
                    </motion.button>
                    <motion.button disabled={selected.size === 0 || saving} onClick={handleConfirm}
                        whileHover={selected.size > 0 ? { background: 'var(--primary-dim)', boxShadow: '0 4px 18px var(--primary-glow)' } : {}} whileTap={{ scale: 0.97 }}
                        style={{ display: 'flex', alignItems: 'center', gap: '7px', padding: '9px 20px', border: 'none', borderRadius: '8px', background: selected.size > 0 ? 'var(--primary)' : 'var(--bg2)', color: selected.size > 0 ? '#fff' : 'var(--text-muted)', fontFamily: 'Inter', fontWeight: 700, fontSize: '0.78rem', cursor: selected.size > 0 && !saving ? 'pointer' : 'not-allowed', boxShadow: selected.size > 0 ? '0 4px 16px var(--primary-glow)' : 'none', transition: 'all 0.2s' }}>
                        {saving ? 'Guardando...' : <>Ir al Campus <ArrowRight size={14} strokeWidth={2.5} /></>}
                    </motion.button>
                </div>
            </div>
        </div>
    )
}
