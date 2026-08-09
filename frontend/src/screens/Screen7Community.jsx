import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import api from '../services/api'
import {
    Hash, Users, MessageSquare, ThumbsUp, Pin,
    Plus, Search, ChevronRight, Zap, Trophy,
    TrendingUp, Cpu, Briefcase, Palette, BookOpen,
    Sword, X, Send, Volume2, UserCircle
} from 'lucide-react'

// Mapeo de iconos para categorías reales
const ICON_MAP = { 'tech': Cpu, 'biz': Briefcase, 'design': Palette, 'resources': BookOpen, 'debates': Sword };

function ThreadCard({ thread, color, onClick }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            whileHover={{ boxShadow: '0 4px 12px rgba(0,0,0,0.05)', y: -2 }}
            onClick={onClick}
            style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: '8px', padding: '20px 24px', cursor: 'pointer', transition: 'all 0.2s', marginBottom: '16px' }}
        >
            <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                <div style={{ width: '48px', height: '48px', flexShrink: 0, borderRadius: '50%', background: `${color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', color: color }}>
                    {thread.initials || (thread.author && thread.author.substring(0, 2).toUpperCase())}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <h4 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.05rem', color: 'var(--text-bright)' }}>{thread.title}</h4>
                        <span style={{ fontFamily: 'Inter', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{thread.time}</span>
                    </div>
                    <p style={{ fontFamily: 'Inter', fontSize: '0.95rem', color: 'var(--text)', lineHeight: 1.6 }}>{thread.body}</p>
                </div>
            </div>
        </motion.div>
    )
}

export default function Screen7Community({ onNavigate }) {
    const [activeServer, setActiveServer] = useState(null)
    const [activeChannel, setActiveChannel] = useState(null)
    const [servers, setServers] = useState([])
    const [leaderboard, setLeaderboard] = useState([])
    const [loading, setLoading] = useState(true)
    
    // --- ESTADOS PARA LOS MENSAJES Y MODAL ---
    const [threads, setThreads] = useState([])
    const [showNewThread, setShowNewThread] = useState(false)
    const [draftTitle, setDraftTitle] = useState('')
    const [draft, setDraft] = useState('')
    const [search, setSearch] = useState('')

    // --- CARGA DE DATOS INICIALES ---
    useEffect(() => {
        const fetchCommunityData = async () => {
            try {
                // 1. Cargar Ranking (Usuarios de la DB)
                const resUsers = await api.get('/api/v1/users');
                const sorted = resUsers.data.sort((a, b) => b.xp_total - a.xp_total);
                setLeaderboard(sorted);

                // 2. Cargar Servidores (Categorías de la DB)
                const resCats = await api.get('/api/v1/categories');
                if (resCats.data.length > 0) {
                    const formatted = resCats.data.map(cat => {
                        let themeColor = cat.color || 'var(--primary)';
                        if (themeColor === '#00E5FF') themeColor = 'var(--accent)';
                        else if (themeColor === '#FF4500') themeColor = 'var(--primary)';
                        else if (themeColor === '#FFA726') themeColor = '#F59E0B';

                        return {
                            id: cat.id, label: cat.name, color: themeColor,
                            Icon: ICON_MAP[cat.slug] || BookOpen,
                            channels: [
                                { id: `gen-${cat.id}`, name: 'general', icon: Hash, unread: 0 },
                                { id: `ann-${cat.id}`, name: 'anuncios', icon: Volume2, unread: 0 },
                                { id: `ent-${cat.id}`, name: 'debates', icon: MessageSquare, unread: 0 }
                            ]
                        }
                    });
                    setServers(formatted);
                    setActiveServer(formatted[0]);
                    setActiveChannel(formatted[0].channels[0]);
                }
            } catch (err) {
                console.error("Modo offline: Backend vacío");
            } finally {
                setLoading(false);
            }
        };
        fetchCommunityData();
    }, []);

    const fetchMessages = async (channel) => {
        if (!channel) return;
        try {
            const response = await api.get(`/api/v1/community/messages/${channel.name}`);
            
            const formattedThreads = response.data.map(msg => {
                const emailName = msg.user_email.split('@')[0];
                return {
                    id: msg.id,
                    author: emailName,
                    initials: emailName.substring(0, 2).toUpperCase(),
                    time: new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
                    title: `Consulta de ${emailName}`,
                    body: msg.content,
                    likes: 0,
                    replies: 0,
                    pinned: false
                }
            });
            
            setThreads(formattedThreads.reverse());
        } catch (err) {
            console.error("No hay mensajes previos en este canal o hubo un error.");
            setThreads([]);
        }
    };

    useEffect(() => {
        fetchMessages(activeChannel);
    }, [activeChannel]);

    const handlePost = async () => {
        if (!draft.trim()) return;
        
        try {
            const fullContent = draftTitle.trim() ? `**${draftTitle.trim()}**\n${draft.trim()}` : draft.trim();
            
            await api.post(`/api/v1/community/messages/${activeChannel.name}?content=${encodeURIComponent(fullContent)}`);
            
            setShowNewThread(false);
            setDraftTitle('');
            setDraft('');
            
            await fetchMessages(activeChannel);
            
        } catch (err) {
            console.error("Error publicando el hilo:", err);
            alert("No se pudo publicar el mensaje. Verifica tu conexión.");
        }
    }

    const displayed = threads.filter(t =>
        !search || t.title.toLowerCase().includes(search.toLowerCase()) || t.body.toLowerCase().includes(search.toLowerCase())
    )

    return (
        <div style={{ height: '100vh', background: '#f8f9fa', display: 'flex', overflow: 'hidden' }}>

            {/* ── COMMUNITIES RAIL */}
            <div style={{ width: '80px', flexShrink: 0, background: '#fff', borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '24px 0', gap: '16px' }}>
                {servers.map(server => {
                    const Icon = server.Icon; const isActive = activeServer?.id === server.id;
                    return (
                        <motion.button key={server.id} onClick={() => { setActiveServer(server); setActiveChannel(server.channels[0]); }}
                            whileHover={{ scale: 1.05 }}
                            style={{ width: '56px', height: '56px', borderRadius: isActive ? '12px' : '28px', background: isActive ? `${server.color}15` : '#fff', border: isActive ? `2px solid ${server.color}` : '1px solid var(--border)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.2s ease', boxShadow: isActive ? '0 4px 12px rgba(0,0,0,0.05)' : 'none' }}>
                            <Icon size={24} color={isActive ? server.color : 'var(--text-muted)'} />
                        </motion.button>
                    )
                })}
                <div style={{ width: '40px', height: '1px', background: 'var(--border)', margin: '8px 0' }} />
                <motion.button whileHover={{ scale: 1.05 }} style={{ width: '56px', height: '56px', borderRadius: '28px', background: '#f0f2f5', border: '1px dashed var(--text-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                    <Plus size={24} color="var(--text-muted)" />
                </motion.button>
            </div>

            {/* ── CHANNELS SIDEBAR */}
            <div style={{ width: '260px', flexShrink: 0, background: '#fff', borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column' }}>
                <div style={{ padding: '24px', borderBottom: '1px solid var(--border)' }}>
                    <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-bright)' }}>{activeServer ? activeServer.label : 'Comunidades'}</h3>
                </div>
                <div style={{ flex: 1, padding: '16px 12px' }}>
                    <p style={{ fontFamily: 'Inter', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '12px', paddingLeft: '12px' }}>Canales</p>
                    {activeServer ? activeServer.channels.map(channel => (
                        <button key={channel.id} onClick={() => setActiveChannel(channel)}
                            style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 12px', borderRadius: '6px', border: 'none', background: activeChannel?.id === channel.id ? '#f0f2f5' : 'transparent', color: activeChannel?.id === channel.id ? 'var(--text-bright)' : 'var(--text-muted)', cursor: 'pointer', fontSize: '0.9rem', fontFamily: 'Inter', fontWeight: activeChannel?.id === channel.id ? 600 : 500, transition: 'background 0.2s' }}>
                            <channel.icon size={18} color={activeChannel?.id === channel.id ? activeServer.color : 'var(--text-muted)'} />
                            {channel.name}
                        </button>
                    )) : (
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', padding: '12px', fontFamily: 'Inter' }}>Selecciona una comunidad</p>
                    )}
                </div>
            </div>

            {/* ── THREADS FEED */}
            <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
                {/* Header */}
                <div style={{ padding: '20px 32px', borderBottom: '1px solid var(--border)', background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '24px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <Hash size={24} color={activeServer ? activeServer.color : 'var(--primary)'} />
                        <h2 style={{ fontFamily: 'Playfair Display', fontWeight: 700, fontSize: '1.5rem', color: 'var(--text-bright)' }}>{activeChannel ? activeChannel.name : 'Bienvenido'}</h2>
                    </div>
                    
                    {activeServer && (
                        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flex: 1, maxWidth: '500px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: '#f0f2f5', border: '1px solid transparent', borderRadius: '8px', padding: '10px 16px', flex: 1, transition: 'border-color 0.2s' }}>
                                <Search size={18} color="var(--text-muted)" />
                                <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Buscar discusiones..."
                                    style={{ background: 'transparent', border: 'none', outline: 'none', flex: 1, fontFamily: 'Inter', fontSize: '0.95rem', color: 'var(--text-bright)' }} />
                            </div>
                            <motion.button onClick={() => setShowNewThread(true)}
                                whileHover={{ background: 'var(--primary-dim)' }} whileTap={{ scale: 0.97 }}
                                style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--primary)', border: 'none', borderRadius: '6px', padding: '12px 20px', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.95rem', color: '#fff', cursor: 'pointer', whiteSpace: 'nowrap', transition: 'background 0.2s' }}>
                                <Plus size={18} /> Nueva publicación
                            </motion.button>
                        </div>
                    )}
                </div>

                <div style={{ flex: 1, overflowY: 'auto', padding: '32px' }}>
                    {!activeServer ? (
                        <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
                            <div style={{ width: '96px', height: '96px', borderRadius: '50%', background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '24px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
                                <Users size={48} color="var(--primary)" />
                            </div>
                            <h3 style={{ fontFamily: 'Playfair Display', fontWeight: 700, fontSize: '2rem', color: 'var(--text-bright)', marginBottom: '16px' }}>Bienvenido a la Comunidad</h3>
                            <p style={{ fontFamily: 'Inter', color: 'var(--text-muted)', fontSize: '1.1rem', maxWidth: '400px', lineHeight: 1.6 }}>Únete a nuestras comunidades para compartir conocimientos, resolver dudas y conectar con otros profesionales.</p>
                        </div>
                    ) : (
                        <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column' }}>
                            {displayed.length > 0 ? (
                                displayed.map((thread) => (
                                    <ThreadCard key={thread.id} thread={thread} color={activeServer.color} />
                                ))
                            ) : (
                                <div style={{ textAlign: 'center', padding: '64px 0' }}>
                                    <MessageSquare size={48} color="var(--border)" style={{ marginBottom: '16px' }} />
                                    <p style={{ fontFamily: 'Inter', color: 'var(--text-muted)', fontSize: '1.1rem' }}>No hay mensajes en este canal aún. ¡Sé el primero en iniciar una conversación!</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </main>

            {/* ── RIGHT PANEL: LEADERBOARD ── */}
            <aside style={{ width: '300px', flexShrink: 0, background: '#fff', borderLeft: '1px solid var(--border)', display: 'flex', flexDirection: 'column' }}>
                <div style={{ padding: '24px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Trophy size={20} color="#F59E0B" />
                    <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-bright)' }}>Top Estudiantes</h3>
                </div>
                <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
                    {leaderboard.length > 0 ? leaderboard.slice(0, 10).map((user, i) => (
                        <div key={user.id} style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
                            <span style={{ fontFamily: 'Inter', fontWeight: 800, color: i < 3 ? '#F59E0B' : 'var(--text-muted)', fontSize: '1rem', minWidth: '24px' }}>#{i + 1}</span>
                            <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: i < 3 ? 'rgba(245, 158, 11, 0.1)' : '#f0f2f5', display: 'flex', alignItems: 'center', justifyContent: 'center', color: i < 3 ? '#F59E0B' : 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 700 }}>
                                {user.username.substring(0, 2).toUpperCase()}
                            </div>
                            <div style={{ flex: 1, minWidth: 0 }}>
                                <p style={{ fontFamily: 'Inter', fontSize: '0.95rem', color: 'var(--text-bright)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontWeight: 600 }}>{user.username}</p>
                                <p style={{ fontFamily: 'Inter', fontSize: '0.8rem', color: 'var(--primary)', fontWeight: 500 }}>{user.xp_total} Puntos</p>
                            </div>
                        </div>
                    )) : <p style={{ fontFamily: 'Inter', color: 'var(--text-muted)', fontSize: '0.9rem' }}>Cargando ranking...</p>}
                </div>
            </aside>

            {/* ── NEW THREAD MODAL ── */}
            <AnimatePresence>
                {showNewThread && (
                    <>
                        <motion.div key="nt-backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                            onClick={() => { setShowNewThread(false); setDraft(''); setDraftTitle('') }}
                            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(4px)', zIndex: 100 }} />
                        <div style={{ position: 'fixed', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 101, pointerEvents: 'none' }}>
                            <motion.div key="nt-modal" initial={{ scale: 0.95, opacity: 0, y: 20 }} animate={{ scale: 1, opacity: 1, y: 0 }} exit={{ scale: 0.95, opacity: 0, y: 20 }}
                                style={{ width: '100%', maxWidth: '600px', background: '#fff', borderRadius: '12px', boxShadow: '0 24px 48px rgba(0,0,0,0.15)', overflow: 'hidden', pointerEvents: 'all' }}>
                                
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '24px 32px', borderBottom: '1px solid var(--border)', background: '#fff' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                        <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: `${activeServer.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                            <Hash size={20} color={activeServer.color} />
                                        </div>
                                        <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.2rem', color: 'var(--text-bright)' }}>Nueva discusión</h3>
                                    </div>
                                    <button onClick={() => { setShowNewThread(false); setDraft(''); setDraftTitle('') }}
                                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: '4px' }}>
                                        <X size={24} />
                                    </button>
                                </div>
                                
                                <div style={{ padding: '32px' }}>
                                    <label style={{ display: 'block', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-bright)', marginBottom: '8px' }}>Título (opcional)</label>
                                    <input value={draftTitle} onChange={e => setDraftTitle(e.target.value)} placeholder="Ej. Duda sobre el módulo 2..."
                                        style={{ width: '100%', background: '#f8f9fa', border: '1px solid var(--border)', borderRadius: '6px', padding: '14px 16px', fontFamily: 'Inter', fontSize: '1rem', color: 'var(--text-bright)', outline: 'none', marginBottom: '24px', boxSizing: 'border-box', transition: 'border-color 0.2s' }} 
                                        onFocus={e => e.target.style.borderColor = 'var(--primary)'}
                                        onBlur={e => e.target.style.borderColor = 'var(--border)'}
                                    />
                                    
                                    <label style={{ display: 'block', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-bright)', marginBottom: '8px' }}>Contenido de la discusión</label>
                                    <textarea value={draft} onChange={e => setDraft(e.target.value)} placeholder="Explica tu pregunta, comparte un recurso, abre un debate..." rows={6}
                                        style={{ width: '100%', background: '#f8f9fa', border: '1px solid var(--border)', borderRadius: '6px', padding: '16px', fontFamily: 'Inter', fontSize: '1rem', color: 'var(--text-bright)', outline: 'none', resize: 'vertical', lineHeight: 1.6, boxSizing: 'border-box', transition: 'border-color 0.2s' }} 
                                        onFocus={e => e.target.style.borderColor = 'var(--primary)'}
                                        onBlur={e => e.target.style.borderColor = 'var(--border)'}
                                    />
                                    
                                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '32px', gap: '16px' }}>
                                        <button onClick={() => { setShowNewThread(false); setDraft(''); setDraftTitle('') }}
                                            style={{ padding: '12px 24px', borderRadius: '6px', border: '1px solid var(--border)', background: '#fff', color: 'var(--text-bright)', fontFamily: 'Inter', fontWeight: 600, fontSize: '1rem', cursor: 'pointer', transition: 'background 0.2s' }}
                                            onMouseOver={e => e.currentTarget.style.background = '#f0f2f5'}
                                            onMouseOut={e => e.currentTarget.style.background = '#fff'}
                                        >
                                            Cancelar
                                        </button>
                                        <motion.button onClick={handlePost} disabled={!draft.trim()}
                                            whileHover={draft.trim() ? { background: 'var(--primary-dim)' } : {}} whileTap={draft.trim() ? { scale: 0.98 } : {}}
                                            style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 28px', borderRadius: '6px', border: 'none', background: draft.trim() ? 'var(--primary)' : '#f0f2f5', color: draft.trim() ? '#fff' : 'var(--text-muted)', fontFamily: 'Inter', fontWeight: 600, fontSize: '1rem', cursor: draft.trim() ? 'pointer' : 'not-allowed', transition: 'all 0.2s' }}>
                                            <Send size={18} /> Publicar
                                        </motion.button>
                                    </div>
                                </div>
                            </motion.div>
                        </div>
                    </>
                )}
            </AnimatePresence>
        </div>
    )
}