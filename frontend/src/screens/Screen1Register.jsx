import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import api from '../services/api'
import { Eye, EyeOff, CheckCircle2, Lock } from 'lucide-react'

const HERO_IMAGES = [
    'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&w=1200&q=80',
    'https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&w=1200&q=80'
]

// ── Reusable styled input ──────────────────────────────────────────────────────
function Field({ label, type = 'text', placeholder, value, onChange, rightEl }) {
    const [focused, setFocused] = useState(false)
    return (
        <div style={{ marginBottom: '16px' }}>
            {label && <label style={{ display: 'block', fontFamily: 'Inter', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-bright)', marginBottom: '8px' }}>{label}</label>}
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                <input type={type} placeholder={placeholder} value={value} onChange={onChange}
                    onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
                    style={{
                        width: '100%', background: '#fff',
                        border: `1px solid ${focused ? 'var(--primary)' : 'var(--border)'}`,
                        borderRadius: '4px', padding: '14px 16px',
                        fontFamily: 'Inter', fontSize: '0.95rem', color: 'var(--text-bright)', outline: 'none',
                        transition: 'border-color 0.2s', boxShadow: focused ? '0 0 0 3px var(--primary-glow)' : 'none',
                    }}
                />
                {rightEl && <div style={{ position: 'absolute', right: '12px' }}>{rightEl}</div>}
            </div>
        </div>
    )
}

// ── Select field ──────────────────────────────────────────────────────────────
function SelectField({ label, value, onChange, options }) {
    const [focused, setFocused] = useState(false)
    return (
        <div style={{ marginBottom: '16px' }}>
            {label && <label style={{ display: 'block', fontFamily: 'Inter', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-bright)', marginBottom: '8px' }}>{label}</label>}
            <div style={{ position: 'relative' }}>
                <select value={value} onChange={onChange} onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
                    style={{
                        width: '100%', appearance: 'none', background: '#fff',
                        border: `1px solid ${focused ? 'var(--primary)' : 'var(--border)'}`, borderRadius: '4px',
                        padding: '14px 16px', fontFamily: 'Inter', fontSize: '0.95rem',
                        color: value ? 'var(--text-bright)' : 'var(--text-muted)', outline: 'none', cursor: 'pointer',
                        boxShadow: focused ? '0 0 0 3px var(--primary-glow)' : 'none', transition: 'all 0.2s',
                    }}>
                    {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
                <div style={{ position: 'absolute', right: '16px', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', borderLeft: '5px solid transparent', borderRight: '5px solid transparent', borderTop: '5px solid var(--text-muted)' }} />
            </div>
        </div>
    )
}

const COUNTRIES = [
    '', 'Argentina', 'Bolivia', 'Chile', 'Colombia', 'Costa Rica', 'Cuba',
    'Ecuador', 'El Salvador', 'Guatemala', 'Honduras', 'México', 'Nicaragua',
    'Panamá', 'Paraguay', 'Perú', 'República Dominicana', 'Uruguay', 'Venezuela',
    'España', 'Estados Unidos', 'Otro',
].map(c => ({ value: c, label: c || 'Selecciona tu país' }))

const ROLES = [
    { value: '', label: 'Selecciona tu rol' },
    { value: 'student', label: 'Estudiante universitario' },
    { value: 'graduate', label: 'Recién graduado' },
    { value: 'professional', label: 'Profesional en activo' },
    { value: 'career_change', label: 'En transición de carrera' },
    { value: 'teacher', label: 'Docente / Académico' },
    { value: 'entrepreneur', label: 'Emprendedor' },
    { value: 'other', label: 'Otro' },
]

const GDPR_TEXT = 'Acepto los Términos de servicio y la Política de privacidad.'

// ── Password input with toggle ────────────────────────────────────────────────
function PasswordField({ label, placeholder, value, onChange }) {
    const [show, setShow] = useState(false)
    return (
        <Field label={label} type={show ? 'text' : 'password'} placeholder={placeholder} value={value} onChange={onChange}
            rightEl={
                <button type="button" onClick={() => setShow(s => !s)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, color: 'var(--text-muted)', display: 'flex' }}>
                    {show ? <EyeOff size={18} strokeWidth={2} /> : <Eye size={18} strokeWidth={2} />}
                </button>
            }
        />
    )
}

// ── Password strength meter ───────────────────────────────────────────────────
function PasswordStrength({ password }) {
    const score = [/.{8,}/, /[A-Z]/, /[0-9]/, /[^A-Za-z0-9]/].filter(r => r.test(password)).length
    const colors = ['var(--border)', 'var(--warm)', 'var(--accent)', 'var(--primary)', '#10B981']
    if (!password) return null
    return (
        <div style={{ marginTop: '-8px', marginBottom: '16px' }}>
            <div style={{ display: 'flex', gap: '4px' }}>
                {[1, 2, 3, 4].map(i => (
                    <div key={i} style={{ flex: 1, height: '4px', borderRadius: '2px', background: i <= score ? colors[score] : 'var(--border)', transition: 'background 0.3s' }} />
                ))}
            </div>
        </div>
    )
}

// ── Google Button Component ───────────────────────────────────────────────────
function GoogleButton({ disabled }) {
    return (
        <button disabled={disabled} style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', background: '#fff', border: '1px solid var(--border)', borderRadius: '4px', padding: '14px', fontFamily: 'Inter', fontWeight: 600, fontSize: '1rem', color: 'var(--text-bright)', cursor: disabled ? 'not-allowed' : 'pointer', marginBottom: '24px', opacity: disabled ? 0.6 : 1, transition: 'background 0.2s' }}>
            <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" /><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" /><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" /><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" /></svg>
            Continuar con Google
        </button>
    )
}

// ══════════════════════════════════════════════════════════════════════════════
// ── LOGIN PANEL ───────────────────────────────────────────────────────────────
function LoginPanel({ onNext, onGoRegister }) {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const [showForgotModal, setShowForgotModal] = useState(false)

    const handleLogin = async () => {
        if (!email || !password) return;
        setLoading(true);
        try {
            const params = new URLSearchParams();
            params.append('username', email);
            params.append('password', password);

            const response = await api.post('/api/v1/token', params, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });

            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                onNext();
            }
        } catch (err) {
            alert(err.response?.data?.detail || "Credenciales incorrectas");
        } finally {
            setLoading(false);
        }
    }

    return (
        <motion.div key="login" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} style={{ width: '100%', maxWidth: '420px', margin: '0 auto' }}>
            <h2 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '2rem', fontWeight: 700, color: 'var(--text-bright)', marginBottom: '32px', textAlign: 'center' }}>Inicia sesión en tu cuenta</h2>

            <div title="Próximamente">
                <GoogleButton disabled={true} />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
                <div style={{ flex: 1, height: '1px', background: 'var(--border)' }} />
                <span style={{ fontFamily: 'Inter', fontSize: '0.85rem', color: 'var(--text-muted)' }}>o ingresa con tu email</span>
                <div style={{ flex: 1, height: '1px', background: 'var(--border)' }} />
            </div>

            <Field label="Correo electrónico" placeholder="correo@ejemplo.com" value={email} onChange={e => setEmail(e.target.value)} />
            <PasswordField label="Contraseña" placeholder="Mínimo 8 caracteres" value={password} onChange={e => setPassword(e.target.value)} />

            <div style={{ textAlign: 'right', marginTop: '-8px', marginBottom: '24px' }}>
                <span onClick={() => setShowForgotModal(true)} style={{ fontFamily: 'Inter', fontSize: '0.85rem', color: 'var(--primary)', fontWeight: 600, cursor: 'pointer' }}>¿Olvidaste tu contraseña?</span>
            </div>

            <motion.button whileHover={{ background: 'var(--primary-dim)' }} whileTap={{ scale: 0.98 }}
                onClick={handleLogin} disabled={loading}
                style={{ width: '100%', background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: '4px', padding: '16px', fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', cursor: loading ? 'not-allowed' : 'pointer', transition: 'background 0.2s', marginBottom: '24px' }}>
                {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
            </motion.button>

            <p style={{ textAlign: 'center', fontFamily: 'Inter', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                ¿No tienes cuenta? <span onClick={onGoRegister} style={{ color: 'var(--primary)', fontWeight: 600, cursor: 'pointer' }}>Regístrate gratis</span>
            </p>

            <AnimatePresence>
                {showForgotModal && (
                    <>
                        <motion.div key="backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setShowForgotModal(false)} style={{ position: 'fixed', inset: 0, background: 'rgba(255,255,255,0.85)', backdropFilter: 'blur(8px)', zIndex: 100 }} />
                        <motion.div key="modal" initial={{ scale: 0.95, opacity: 0, y: 10 }} animate={{ scale: 1, opacity: 1, y: 0 }} exit={{ scale: 0.95, opacity: 0, y: 10 }}
                            style={{ position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', zIndex: 101, width: 'min(400px, 90vw)', background: '#fff', borderRadius: '8px', padding: '32px', boxShadow: 'var(--shadow-lg)', textAlign: 'center' }}>
                            <div style={{ width: '56px', height: '56px', margin: '0 auto 16px', background: 'var(--primary-glow)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <Lock size={24} color="var(--primary)" />
                            </div>
                            <h3 style={{ fontFamily: 'Inter', fontWeight: 700, fontSize: '1.25rem', color: 'var(--text-bright)', marginBottom: '12px' }}>Recuperación de cuenta</h3>
                            <p style={{ fontFamily: 'Inter', fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: '24px' }}>
                                Esta funcionalidad estará disponible próximamente.<br />Contacta a <span style={{ color: 'var(--primary)', fontWeight: 600 }}>soporte@delphos.com</span>
                            </p>
                            <button onClick={() => setShowForgotModal(false)} style={{ width: '100%', padding: '12px', background: 'var(--primary)', border: 'none', borderRadius: '4px', fontFamily: 'Inter', fontWeight: 600, color: '#fff', cursor: 'pointer' }}>Entendido</button>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </motion.div>
    )
}

// ══════════════════════════════════════════════════════════════════════════════
// ── REGISTER PANEL ────────────────────────────────────────────────────────────
function RegisterPanel({ onNext, onGoLogin }) {
    const [form, setForm] = useState({ firstName: '', lastName: '', email: '', password: '', confirm: '', country: '', role: '', birthYear: '', terms: false })
    const [step, setStep] = useState(1)
    const [loading, setLoading] = useState(false)

    const set = (key) => (e) => setForm(f => ({ ...f, [key]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }))

    const passwordMatch = form.password && form.confirm && form.password === form.confirm
    const step1Valid = form.firstName && form.lastName && form.role && form.country
    const step2Valid = form.email && form.password.length >= 8 && passwordMatch && form.terms

    const handleSubmit = async () => {
        if (!step2Valid) return;
        setLoading(true);
        try {
            // TEMPORAL: `role` y `country` se recogen en el paso 1 pero no se envían.
            // El backend (UserCreate, `extra="forbid"`) los rechaza con 422 porque
            // todavía no existen como columnas. NO volver a añadirlos aquí hasta que
            // esté hecha la migración descrita en TODO_MATIAS_SCHEMA.md.
            // `birth_year` sí se manda: el backend ya lo mapea a `birth_date`.
            const payload = {
                email: form.email,
                password: form.password,
                full_name: `${form.firstName} ${form.lastName}`.trim(),
                username: form.email.split('@')[0],
                birth_year: parseInt(form.birthYear) || 2000
            };
            await api.post('/api/v1/register', payload);

            // El paso 3 lleva directo al onboarding, y `POST /oracle/full_profile`
            // exige `get_current_user`. Sin este login automático el usuario recién
            // registrado llega al oráculo sin token y la recomendación muere en un
            // 401 que el frontend se traga en silencio.
            const params = new URLSearchParams();
            params.append('username', form.email);
            params.append('password', form.password);
            const { data } = await api.post('/api/v1/token', params, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            if (!data.access_token) throw new Error('El backend no devolvió access_token');
            localStorage.setItem('token', data.access_token);

            setStep(3);
        } catch (err) {
            // Si la cuenta se creó pero el login falló, mandamos a iniciar sesión:
            // entrar al onboarding sin token daría un perfil sin recomendaciones.
            if (err.response?.status === 401 || err.message?.includes('access_token')) {
                alert("Tu cuenta se creó, pero no pudimos iniciar sesión automáticamente. Entra con tus credenciales.");
                onGoLogin();
                return;
            }
            alert(err.response?.data?.detail || "Error al crear la cuenta");
        } finally {
            setLoading(false);
        }
    }

    const years = Array.from({ length: 60 }, (_, i) => 2010 - i)

    return (
        <motion.div key="register" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} style={{ width: '100%', maxWidth: step === 3 ? '420px' : '480px', margin: '0 auto' }}>
            <AnimatePresence mode="wait">
                {step === 1 && (
                    <motion.div key="step1" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                        <h2 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '2rem', fontWeight: 700, color: 'var(--text-bright)', marginBottom: '8px', textAlign: 'center' }}>Crea tu cuenta</h2>
                        <p style={{ fontFamily: 'Inter', fontSize: '0.95rem', color: 'var(--text-muted)', marginBottom: '32px', textAlign: 'center' }}>Paso 1 de 2: Cuéntanos sobre ti</p>

                        <div style={{ display: 'flex', gap: '16px' }}>
                            <div style={{ flex: 1 }}><Field label="Nombre" placeholder="María" value={form.firstName} onChange={set('firstName')} /></div>
                            <div style={{ flex: 1 }}><Field label="Apellido" placeholder="García" value={form.lastName} onChange={set('lastName')} /></div>
                        </div>

                        <div style={{ display: 'flex', gap: '16px' }}>
                            <div style={{ flex: 1 }}>
                                <SelectField label="Rol actual" value={form.role} onChange={set('role')} options={ROLES} />
                            </div>
                            <div style={{ flex: 1 }}>
                                <SelectField label="Año de nacimiento" value={form.birthYear} onChange={set('birthYear')} options={[{ value: '', label: 'Año' }, ...years.map(y => ({ value: y, label: String(y) }))]} />
                            </div>
                        </div>

                        <SelectField label="País" value={form.country} onChange={set('country')} options={COUNTRIES} />

                        <motion.button onClick={() => step1Valid && setStep(2)}
                            whileHover={step1Valid ? { background: 'var(--primary-dim)' } : {}} whileTap={step1Valid ? { scale: 0.98 } : {}}
                            style={{ width: '100%', background: step1Valid ? 'var(--primary)' : 'var(--secondary)', color: step1Valid ? '#fff' : 'var(--text-muted)', border: 'none', borderRadius: '4px', padding: '16px', fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', cursor: step1Valid ? 'pointer' : 'not-allowed', marginTop: '8px', marginBottom: '24px', transition: 'background 0.2s' }}>
                            Siguiente paso
                        </motion.button>

                        <p style={{ textAlign: 'center', fontFamily: 'Inter', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                            ¿Ya tienes cuenta? <span onClick={onGoLogin} style={{ color: 'var(--primary)', fontWeight: 600, cursor: 'pointer' }}>Inicia sesión</span>
                        </p>
                    </motion.div>
                )}

                {step === 2 && (
                    <motion.div key="step2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
                        <div style={{ marginBottom: '24px' }}>
                            <span onClick={() => setStep(1)} style={{ fontFamily: 'Inter', fontSize: '0.85rem', color: 'var(--primary)', fontWeight: 600, cursor: 'pointer' }}>← Volver al paso 1</span>
                        </div>
                        <h2 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '2rem', fontWeight: 700, color: 'var(--text-bright)', marginBottom: '8px', textAlign: 'center' }}>Configura tu acceso</h2>
                        <p style={{ fontFamily: 'Inter', fontSize: '0.95rem', color: 'var(--text-muted)', marginBottom: '32px', textAlign: 'center' }}>Paso 2 de 2: Credenciales de seguridad</p>

                        <Field label="Correo electrónico" type="email" placeholder="correo@ejemplo.com" value={form.email} onChange={set('email')} />

                        <PasswordField label="Contraseña" placeholder="Mínimo 8 caracteres" value={form.password} onChange={set('password')} />
                        <PasswordStrength password={form.password} />

                        <PasswordField label="Confirmar contraseña" placeholder="Repite tu contraseña" value={form.confirm} onChange={set('confirm')} />

                        <label style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', cursor: 'pointer', marginTop: '24px', marginBottom: '24px' }}>
                            <div onClick={() => setForm(f => ({ ...f, terms: !f.terms }))}
                                style={{ width: '20px', height: '20px', flexShrink: 0, borderRadius: '4px', border: `1px solid ${form.terms ? 'var(--primary)' : 'var(--border)'}`, background: form.terms ? 'var(--primary)' : '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.2s' }}>
                                {form.terms && <CheckCircle2 size={14} color="#fff" strokeWidth={3} />}
                            </div>
                            <span style={{ fontFamily: 'Inter', fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                                Acepto los <span style={{ color: 'var(--primary)', fontWeight: 600 }}>Términos de servicio</span> y la <span style={{ color: 'var(--primary)', fontWeight: 600 }}>Política de privacidad</span>.
                            </span>
                        </label>

                        <motion.button onClick={handleSubmit} disabled={!step2Valid || loading}
                            whileHover={step2Valid ? { background: 'var(--primary-dim)' } : {}} whileTap={step2Valid ? { scale: 0.98 } : {}}
                            style={{ width: '100%', background: step2Valid ? 'var(--primary)' : 'var(--secondary)', color: step2Valid ? '#fff' : 'var(--text-muted)', border: 'none', borderRadius: '4px', padding: '16px', fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', cursor: step2Valid ? 'pointer' : 'not-allowed', transition: 'background 0.2s' }}>
                            {loading ? 'Creando cuenta...' : 'Crear mi cuenta'}
                        </motion.button>
                    </motion.div>
                )}

                {step === 3 && (
                    <motion.div key="step3" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} style={{ textAlign: 'center', padding: '40px 0' }}>
                        <div style={{ width: '80px', height: '80px', margin: '0 auto 24px', borderRadius: '50%', background: 'rgba(16, 185, 129, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <CheckCircle2 size={40} color="#10B981" />
                        </div>
                        <h2 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '2.5rem', fontWeight: 700, color: 'var(--text-bright)', marginBottom: '16px' }}>¡Bienvenido!</h2>
                        <p style={{ fontFamily: 'Inter', fontSize: '1rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: '32px' }}>
                            Hola, <strong style={{ color: 'var(--text-bright)' }}>{form.firstName}</strong>. Tu perfil ha sido creado exitosamente. Comienza tu aprendizaje hoy mismo.
                        </p>
                        <motion.button onClick={onNext}
                            whileHover={{ background: 'var(--primary-dim)' }} whileTap={{ scale: 0.98 }}
                            style={{ width: '100%', background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: '4px', padding: '16px', fontFamily: 'Inter', fontWeight: 700, fontSize: '1rem', cursor: 'pointer' }}>
                            Comenzar aventura
                        </motion.button>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    )
}

// ══════════════════════════════════════════════════════════════════════════════
// ── MAIN COMPONENT (SPLIT SCREEN LAYOUT) ──────────────────────────────────────
export default function Screen1Register({ onNext }) {
    const [mode, setMode] = useState('login')
    const [currentImage, setCurrentImage] = useState(0)

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentImage(prev => (prev + 1) % HERO_IMAGES.length)
        }, 5000)
        return () => clearInterval(timer)
    }, [])

    return (
        <div style={{ minHeight: '100vh', display: 'flex', background: '#fff' }}>
            {/* Left Side: Hero Section (Hidden on small screens) */}
            <div style={{ flex: 1, position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '60px', color: '#fff' }} className="hero-section">

                {/* Image Carousel Background */}
                <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
                    <AnimatePresence>
                        <motion.div
                            key={currentImage}
                            initial={{ opacity: 0, scale: 1.05 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 1.5 }}
                            style={{
                                position: 'absolute', inset: 0,
                                backgroundImage: `url(${HERO_IMAGES[currentImage]})`,
                                backgroundSize: 'cover',
                                backgroundPosition: 'center',
                            }}
                        />
                    </AnimatePresence>
                </div>

                {/* Dark Overlay for Text Readability */}
                <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to right, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 100%)', zIndex: 0 }} />

                <div style={{ position: 'relative', zIndex: 1, maxWidth: '500px' }}>
                    <AnimatePresence mode="wait">
                        {mode === 'login' ? (
                            <motion.div key="hero-login" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.4 }}>
                                <h1 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '3.5rem', fontWeight: 700, lineHeight: 1.15, marginBottom: '24px', textShadow: '0 4px 16px rgba(0,0,0,0.6)', color: '#F59E0B' }}>
                                    Desarrolla tus<br />habilidades
                                </h1>
                                <p style={{ fontFamily: 'Inter', fontSize: '1.15rem', opacity: 0.95, lineHeight: 1.6, maxWidth: '420px', textShadow: '0 2px 8px rgba(0,0,0,0.6)' }}>
                                    Únete a nuestra plataforma y accede a contenido de primer nivel impartido por expertos de la industria.
                                </p>
                            </motion.div>
                        ) : (
                            <motion.div key="hero-register" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.4 }}>
                                <h1 style={{ fontFamily: 'Outfit, sans-serif', fontSize: '3.5rem', fontWeight: 700, lineHeight: 1.15, marginBottom: '24px', textShadow: '0 4px 16px rgba(0,0,0,0.6)', color: '#F59E0B' }}>
                                    Impulsa tu<br />carrera.
                                </h1>
                                <p style={{ fontFamily: 'Inter', fontSize: '1.15rem', opacity: 0.95, lineHeight: 1.6, maxWidth: '420px', textShadow: '0 2px 8px rgba(0,0,0,0.6)' }}>
                                    Crea tu cuenta gratuita hoy y comienza a construir tu futuro profesional con rutas de aprendizaje personalizadas.
                                </p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>

            {/* Right Side: Form Container */}
            <div style={{ width: '100%', maxWidth: '600px', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px', background: 'var(--bg2)', position: 'relative' }}>
                <AnimatePresence mode="wait">
                    {mode === 'login'
                        ? <LoginPanel key="login" onNext={onNext} onGoRegister={() => setMode('register')} />
                        : <RegisterPanel key="register" onNext={onNext} onGoLogin={() => setMode('login')} />
                    }
                </AnimatePresence>
            </div>

            {/* Inline CSS for hiding hero on mobile */}
            <style>{`
                @media (max-width: 900px) {
                    .hero-section {
                        display: none !important;
                    }
                }
            `}</style>
        </div>
    )
}
