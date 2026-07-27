import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import api from '../services/api' // Tu puente con el backend
import {
    Hash, Users, MessageSquare, ThumbsUp, Pin,
    Plus, Search, ChevronRight, Zap, Trophy,
    TrendingUp, Cpu, Briefcase, Palette, BookOpen,
    Sword, X, Send, Volume2,
} from 'lucide-react'

// Mapeo de iconos para categorías reales
const ICON_MAP = { 'tech': Cpu, 'biz': Briefcase, 'design': Palette, 'resources': BookOpen, 'debates': Sword };

function ThreadCard({ thread, color, onClick }) {
    const [liked, setLiked] = useState(false)
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            whileHover={{ boxShadow: `0 0 18px var(--accent-glow)`, x: 2 }}
            onClick={onClick}
            style={{ background: 'var(--card)', border: '1px solid var(--border)', borderLeft: `3px solid ${thread.pinned ? color : 'var(--border)'}`, borderRadius: '10px', padding: '16px 18px', cursor: 'pointer', transition: 'all 0.2s', marginBottom: '10px' }}
        >
            <div style={{ display: 'flex', gap: '11px', alignItems: 'flex-start' }}>
                <div style={{ width: '36px', height: '36px', flexShrink: 0, borderRadius: '9px', background: 'var(--bg2)', border: `1.5px solid var(--border)`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Inter', fontWeight: 800, fontSize: '0.68rem', color: color }}>
                    {thread.initials || (thread.author && thread.author.substring(0, 2).toUpperCase())}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                        <h4 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-bright)' }}>{thread.title}</h4>
                        <span style={{ fontFamily: 'Inter', fontSize: '0.62rem', color: 'var(--text-muted)' }}>{thread.time}</span>
                    </div>
                    <p style={{ fontFamily: 'Inter', fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{thread.body}</p>
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
                        let themeColor = cat.color || '#00E5FF';
                        if (themeColor === '#00E5FF') themeColor = 'var(--accent)';
                        else if (themeColor === '#FF4500') themeColor = 'var(--primary)';
                        else if (themeColor === '#FFA726') themeColor = 'var(--gold)';

                        return {
                            id: cat.id, label: cat.name, color: themeColor,
                            Icon: ICON_MAP[cat.slug] || Cpu,
                            channels: [
                                { id: `gen-${cat.id}`, name: 'general', icon: Hash, unread: 0 },
                                { id: `ann-${cat.id}`, name: 'anuncios', icon: Volume2, unread: 0 },
                                { id: `ent-${cat.id}`, name: 'entrevistas-tech', icon: MessageSquare, unread: 0 } // Aseguramos que exista el canal del seeder
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

    // B-12: fetchMessages extraído como función del componente para poder llamarla directamente
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
                    title: `Mensaje de ${emailName}`,
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

    // Recargar mensajes cuando cambia el canal activo
    useEffect(() => {
        fetchMessages(activeChannel);
    }, [activeChannel]);

    // --- FUNCIÓN PARA PUBLICAR MENSAJES ---
    const handlePost = async () => {
        if (!draft.trim()) return;
        
        try {
            const fullContent = draftTitle.trim() ? `**${draftTitle.trim()}**\n${draft.trim()}` : draft.trim();
            
            // Enviamos el post al backend
            await api.post(`/api/v1/community/messages/${activeChannel.name}?content=${encodeURIComponent(fullContent)}`);
            
            setShowNewThread(false);
            setDraftTitle('');
            setDraft('');
            
            // B-12: Recargar mensajes directamente, sin hack de setTimeout
            await fetchMessages(activeChannel);
            
        } catch (err) {
            console.error("Error publicando el hilo:", err);
            alert("No se pudo publicar el mensaje. Verifica tu conexión.");
        }
    }

    // Buscador
    const displayed = threads.filter(t =>
        !search || t.title.toLowerCase().includes(search.toLowerCase()) || t.body.toLowerCase().includes(search.toLowerCase())
    )

    return (
        <div style={{ height: '100vh', background: 'var(--bg)', display: 'flex', overflow: 'hidden' }}>

            {/* ── SERVERS RAIL */}
            <div style={{ width: '64px', flexShrink: 0, background: 'var(--bg2)', borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '16px 0', gap: '8px' }}>
                {servers.map(server => {
                    const Icon = server.Icon; const isActive = activeServer?.id === server.id;
                    return (
                        <motion.button key={server.id} onClick={() => { setActiveServer(server); setActiveChannel(server.channels[0]); }}
                            whileHover={{ scale: 1.1 }}
                            style={{ width: '44px', height: '44px', borderRadius: isActive ? '12px' : '22px', background: isActive ? 'var(--accent-glow)' : 'var(--card)', border: `1.5px solid ${isActive ? server.color : 'var(--border)'}`, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.25s' }}>
                            <Icon size={20} color={isActive ? server.color : 'var(--text-muted)'} />
                        </motion.button>
                    )
                })}
                <div style={{ width: '32px', height: '1px', background: 'var(--border)', margin: '4px 0' }} />
                <motion.button style={{ width: '44px', height: '44px', borderRadius: '22px', background: 'var(--card)', border: '1.5px dashed var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                    <Plus size={18} color="var(--text-muted)" />
                </motion.button>
            </div>

            {/* ── CHANNELS SIDEBAR */}
            <div style={{ width: '200px', flexShrink: 0, background: 'var(--bg2)', borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column' }}>
                <div style={{ padding: '16px 14px', borderBottom: '1px solid var(--border)', background: 'var(--bg2)' }}>
                    <h3 style={{ fontWeight: 800, fontSize: '0.8rem', color: 'var(--text-bright)' }}>{activeServer ? activeServer.label : 'CANALES'}</h3>
                </div>
                <div style={{ flex: 1, padding: '12px 8px' }}>
                    {activeServer ? activeServer.channels.map(channel => (
                        <button key={channel.id} onClick={() => setActiveChannel(channel)}
                            style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '7px', padding: '8px', borderRadius: '6px', border: 'none', background: activeChannel?.id === channel.id ? 'var(--accent-glow)' : 'transparent', color: activeChannel?.id === channel.id ? 'var(--text-bright)' : 'var(--text-muted)', cursor: 'pointer', fontSize: '0.78rem' }}>
                            <channel.icon size={14} color={activeChannel?.id === channel.id ? activeServer.color : 'var(--text-muted)'} />
                            {channel.name}
                        </button>
                    )) : (
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.7rem', padding: '10px' }}>Sin canales activos</p>
                    )}
                </div>
            </div>

            {/* ── THREADS FEED */}
            <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
                {/* Cabecera con Buscador y Botón */}
                <div style={{ padding: '14px 22px', borderBottom: '1px solid var(--border)', background: 'var(--bg)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '14px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
                        <Hash size={18} color={activeServer ? activeServer.color : 'var(--primary)'} />
                        <h2 style={{ fontWeight: 800, fontSize: '0.95rem', color: 'var(--text-bright)' }}>{activeChannel ? activeChannel.name : 'lobby'}</h2>
                    </div>
                    
                    {activeServer && (
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flex: 1, maxWidth: '340px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '7px', padding: '7px 12px', flex: 1 }}>
                                <Search size={13} color="var(--text-muted)" strokeWidth={2} />
                                <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Buscar en el canal..."
                                    style={{ background: 'transparent', border: 'none', outline: 'none', flex: 1, fontFamily: 'Inter', fontSize: '0.75rem', color: 'var(--text-bright)' }} />
                            </div>
                            <motion.button onClick={() => setShowNewThread(true)}
                                whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
                                style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'var(--primary)', border: 'none', borderRadius: '7px', padding: '8px 14px', fontFamily: 'Inter', fontWeight: 700, fontSize: '0.72rem', color: '#fff', cursor: 'pointer', whiteSpace: 'nowrap' }}>
                                <Plus size={13} strokeWidth={2.5} /> Nuevo hilo
                            </motion.button>
                        </div>
                    )}
                </div>

                <div style={{ flex: 1, overflowY: 'auto', padding: '20px 22px' }}>
                    {!activeServer ? (
                        <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
                            <Zap size={40} color="var(--primary)" strokeWidth={1} style={{ marginBottom: '16px', opacity: 0.5 }} />
                            <h3 style={{ color: 'var(--text-bright)', marginBottom: '8px' }}>¡Bienvenido al Campus Estudiantil!</h3>
                            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', maxWidth: '300px' }}>Parece que aún no te has unido a ninguna comunidad profesional.</p>
                            <button onClick={() => onNavigate(4)} style={{ marginTop: '20px', background: 'var(--primary)', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: '8px', fontWeight: 700, cursor: 'pointer' }}>Explorar Comunidades</button>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                            {displayed.length > 0 ? (
                                displayed.map((thread) => (
                                    <ThreadCard key={thread.id} thread={thread} color={activeServer.color} />
                                ))
                            ) : (
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center', marginTop: '20px' }}>No hay mensajes aquí aún. ¡Sé el primero en escribir!</p>
                            )}
                        </div>
                    )}
                </div>
            </main>

            {/* ── RIGHT PANEL: LEADERBOARD REAL */}
            <aside style={{ width: '236px', flexShrink: 0, background: 'var(--bg2)', borderLeft: '1px solid var(--border)', padding: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '16px' }}>
                    <Trophy size={14} color="var(--gold)" />
                    <h4 style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Top Estudiantes</h4>
                </div>
                {leaderboard.length > 0 ? leaderboard.slice(0, 8).map((user, i) => (
                    <div key={user.id} style={{ display: 'flex', alignItems: 'center', gap: '9px', marginBottom: '10px' }}>
                        <span style={{ fontWeight: 900, color: i === 0 ? 'var(--gold)' : 'var(--border)', fontSize: '0.7rem', minWidth: '16px' }}>#{i + 1}</span>
                        <div style={{ width: '26px', height: '26px', borderRadius: '6px', background: 'var(--bg)', border: `1px solid ${i === 0 ? 'var(--gold)' : 'var(--border)'}`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-bright)', fontSize: '0.6rem', fontWeight: 700 }}>
                            {user.username.substring(0, 2).toUpperCase()}
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                            <p style={{ fontSize: '0.75rem', color: 'var(--text)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontWeight: 600 }}>{user.username}</p>
                            <p style={{ fontSize: '0.6rem', color: 'var(--accent)' }}>{user.xp_total} XP</p>
                        </div>
                    </div>
                )) : <p style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>Cargando ranking...</p>}
            </aside>

            {/* ── NEW THREAD MODAL ── */}
            <AnimatePresence>
                {showNewThread && (
                    <>
                        <motion.div key="nt-backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                            onClick={() => { setShowNewThread(false); setDraft(''); setDraftTitle('') }}
                            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(6px)', zIndex: 100 }} />
                        <div style={{ position: 'fixed', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 101, pointerEvents: 'none' }}>
                            <motion.div key="nt-modal" initial={{ scale: 0.9, opacity: 0, y: 20 }} animate={{ scale: 1, opacity: 1, y: 0 }} exit={{ scale: 0.9, opacity: 0, y: 20 }} transition={{ type: 'spring', damping: 26, stiffness: 300 }}
                                style={{ width: 'min(560px, 94vw)', background: 'var(--bg2)', border: `1px solid var(--border)`, borderTop: `2px solid ${activeServer.color}`, borderRadius: '16px', boxShadow: `0 0 60px rgba(0,0,0,0.9)`, overflow: 'hidden', pointerEvents: 'all' }}>
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 22px', borderBottom: '1px solid var(--border)', background: 'var(--card)' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <Hash size={15} color={activeServer.color} strokeWidth={2.5} />
                                        <h3 style={{ fontFamily: 'Inter', fontWeight: 800, fontSize: '0.88rem', color: 'var(--text-bright)' }}>Nuevo hilo en #{activeChannel?.name}</h3>
                                    </div>
                                    <button onClick={() => { setShowNewThread(false); setDraft(''); setDraftTitle('') }}
                                        style={{ background: 'transparent', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                                        <X size={18} strokeWidth={2.5} />
                                    </button>
                                </div>
                                <div style={{ padding: '18px 22px' }}>
                                    <input value={draftTitle} onChange={e => setDraftTitle(e.target.value)} placeholder="Título del hilo (opcional)..."
                                        style={{ width: '100%', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '8px', padding: '10px 14px', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.88rem', color: 'var(--text-bright)', outline: 'none', marginBottom: '10px', boxSizing: 'border-box' }} />
                                    <textarea value={draft} onChange={e => setDraft(e.target.value)} placeholder="Explica tu pregunta, comparte un recurso, abre un debate..." rows={5}
                                        style={{ width: '100%', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '8px', padding: '10px 14px', fontFamily: 'Inter', fontSize: '0.84rem', color: 'var(--text)', outline: 'none', resize: 'none', lineHeight: 1.6, boxSizing: 'border-box' }} />
                                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '14px', gap: '10px' }}>
                                        <button onClick={() => { setShowNewThread(false); setDraft(''); setDraftTitle('') }}
                                            style={{ padding: '10px 18px', borderRadius: '8px', border: '1px solid var(--border)', background: 'transparent', color: 'var(--text-muted)', fontFamily: 'Inter', fontWeight: 600, fontSize: '0.78rem', cursor: 'pointer' }}>Cancelar</button>
                                        <motion.button onClick={handlePost} disabled={!draft.trim()}
                                            whileHover={draft.trim() ? { scale: 1.02 } : {}} whileTap={draft.trim() ? { scale: 0.97 } : {}}
                                            style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '10px 20px', borderRadius: '8px', border: 'none', background: draft.trim() ? 'var(--primary)' : 'var(--bg2)', color: draft.trim() ? '#fff' : 'var(--text-muted)', fontFamily: 'Inter', fontWeight: 700, fontSize: '0.78rem', cursor: draft.trim() ? 'pointer' : 'not-allowed', transition: 'all 0.2s' }}>
                                            <Send size={13} strokeWidth={2.5} /> Publicar hilo
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