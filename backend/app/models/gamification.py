"""
Gamification Models - Fase 9
Progreso Profundo, Economía XP, Logros, Misiones y Mentores IA
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum


# ============================================
# ENUMS
# ============================================

class EstadoModuloEnum(str, enum.Enum):
    NO_INICIADO = "no_iniciado"
    EN_PROGRESO = "en_progreso"
    COMPLETADO = "completado"


class TipoFuenteXPEnum(str, enum.Enum):
    TAREA = "tarea"
    LOGRO = "logro"
    MISION = "mision"
    BONUS = "bonus"
    PENALIZACION = "penalizacion"


class TipoLogroEnum(str, enum.Enum):
    BRONCE = "bronce"
    PLATA = "plata"
    ORO = "oro"
    PLATINO = "platino"


class EstadoMisionEnum(str, enum.Enum):
    ACTIVA = "activa"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    EXPIRADA = "expirada"


class EstadoConversacionEnum(str, enum.Enum):
    ACTIVA = "activa"
    PAUSADA = "pausada"
    FINALIZADA = "finalizada"


class RolMensajeEnum(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ============================================
# BLOQUE A: PROGRESO Y ECONOMÍA
# ============================================

class UserModule(Base):
    """
    Progreso del usuario en módulos de simulación
    Rastrea completitud, tiempo dedicado y estado
    """
    __tablename__ = "modulos_usuario"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("simulation_modules.id"), nullable=False, index=True)
    simulacion_usuario_id = Column(Integer, ForeignKey("user_simulation_progress.id"), nullable=True, index=True)
    
    # Estado y Progreso
    estado = Column(Enum(EstadoModuloEnum), nullable=False, default=EstadoModuloEnum.NO_INICIADO, index=True)
    porcentaje_completado = Column(Numeric(5, 2), default=0.0, nullable=False)  # 0-100
    tiempo_dedicado_minutos = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now())
    fecha_completado = Column(DateTime(timezone=True), nullable=True)
    ultima_actividad = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="user_modules")
    module = relationship("SimulationModule", backref="user_progress")
    
    def __repr__(self):
        return f"<UserModule user={self.user_id} module={self.module_id} estado={self.estado}>"


class TaskSkill(Base):
    """
    Habilidades asociadas a tareas con XP ganado
    Permite vincular skills específicas a tareas y ponderar su importancia
    """
    __tablename__ = "habilidades_tarea"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    task_id = Column(Integer, ForeignKey("module_tasks.id"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills_catalog.id"), nullable=False, index=True)
    
    # Gamificación
    xp_ganado = Column(Integer, default=10, nullable=False)
    peso = Column(Numeric(3, 2), default=1.0, nullable=False)  # Factor de importancia 0.0-2.0
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    task = relationship("ModuleTask", backref="task_skills")
    skill = relationship("SkillCatalog", backref="associated_tasks")
    
    def __repr__(self):
        return f"<TaskSkill task={self.task_id} skill={self.skill_id} xp={self.xp_ganado}>"


class XPTransaction(Base):
    """
    Registro de transacciones de XP
    Auditoría completa de ganancias/pérdidas de experiencia
    """
    __tablename__ = "transacciones_xp"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Transacción
    cantidad_xp = Column(Integer, nullable=False)  # Puede ser negativo (penalización)
    tipo_fuente = Column(Enum(TipoFuenteXPEnum), nullable=False, index=True)
    fuente_id = Column(Integer, nullable=True)  # ID de la tarea/logro/misión origen
    descripcion = Column(Text, nullable=False)
    
    # Balance
    xp_anterior = Column(Integer, default=0)
    xp_nuevo = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", backref="xp_transactions")
    
    def __repr__(self):
        return f"<XPTransaction user={self.user_id} cantidad={self.cantidad_xp} tipo={self.tipo_fuente}>"


# ============================================
# BLOQUE B: GAMIFICACIÓN
# ============================================

class Achievement(Base):
    """
    Logros desbloqueables del sistema
    Catálogo global de achievements disponibles
    """
    __tablename__ = "logros"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Info
    titulo = Column(String(200), nullable=False, unique=True)
    descripcion = Column(Text, nullable=False)
    icono_url = Column(String(500), nullable=True)
    
    # Clasificación
    tipo_logro = Column(Enum(TipoLogroEnum), nullable=False, default=TipoLogroEnum.BRONCE, index=True)
    categoria = Column(String(100), nullable=True)  # 'progreso', 'social', 'maestria', etc.
    
    # Recompensa
    recompensa_xp = Column(Integer, default=0, nullable=False)
    recompensa_badge = Column(String(100), nullable=True)
    
    # Condiciones (JSON para flexibilidad)
    condiciones = Column(Text, nullable=True)  # JSON serializado con criterios
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)  # Logros secretos
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Achievement {self.titulo} tipo={self.tipo_logro}>"


class UserAchievement(Base):
    """
    Logros desbloqueados por usuarios
    Registro de achievements obtenidos
    """
    __tablename__ = "logros_usuario"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    logro_id = Column(Integer, ForeignKey("logros.id"), nullable=False, index=True)
    
    # Estado
    desbloqueado = Column(Boolean, default=True, nullable=False)
    progreso_actual = Column(Integer, default=0)  # Para logros incrementales
    progreso_requerido = Column(Integer, default=1)
    
    # Metadata
    fecha_desbloqueo = Column(DateTime(timezone=True), server_default=func.now())
    notificado = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", backref="achievements")
    achievement = relationship("Achievement", backref="unlocked_by")
    
    def __repr__(self):
        return f"<UserAchievement user={self.user_id} logro={self.logro_id} desbloqueado={self.desbloqueado}>"


class Mission(Base):
    """
    Misiones del sistema
    Desafíos temporales con objetivos específicos
    """
    __tablename__ = "misiones"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Info
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    icono_url = Column(String(500), nullable=True)
    
    # Objetivo
    objetivo_tipo = Column(String(100), nullable=False)  # 'completar_tareas', 'ganar_xp', 'racha', etc.
    objetivo_cantidad = Column(Integer, nullable=False)
    objetivo_metadata = Column(Text, nullable=True)  # JSON con detalles adicionales
    
    # Recompensa
    recompensa_xp = Column(Integer, default=0, nullable=False)
    recompensa_items = Column(Text, nullable=True)  # JSON con items especiales
    
    # Temporalidad
    fecha_inicio = Column(DateTime(timezone=True), nullable=True)
    fecha_fin = Column(DateTime(timezone=True), nullable=True)
    duracion_dias = Column(Integer, nullable=True)  # Alternativa a fecha_fin
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    es_diaria = Column(Boolean, default=False)
    es_semanal = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Mission {self.titulo} objetivo={self.objetivo_tipo}>"


class UserMission(Base):
    """
    Progreso del usuario en misiones
    Rastrea avance en desafíos activos
    """
    __tablename__ = "misiones_usuario"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mision_id = Column(Integer, ForeignKey("misiones.id"), nullable=False, index=True)
    
    # Progreso
    progreso_actual = Column(Integer, default=0, nullable=False)
    estado = Column(Enum(EstadoMisionEnum), nullable=False, default=EstadoMisionEnum.ACTIVA, index=True)
    
    # Metadata
    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now())
    fecha_completado = Column(DateTime(timezone=True), nullable=True)
    recompensa_reclamada = Column(Boolean, default=False)
    
    # Timestamps
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="missions")
    mission = relationship("Mission", backref="user_progress")
    
    def __repr__(self):
        return f"<UserMission user={self.user_id} mision={self.mision_id} estado={self.estado}>"


# ============================================
# BLOQUE C: IA E INTERACCIÓN
# ============================================

class VirtualMentor(Base):
    """
    Mentores virtuales basados en IA
    Personalidades configurables por empresa
    """
    __tablename__ = "mentores_virtuales"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Ownership
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    
    # Identidad
    nombre = Column(String(200), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    titulo = Column(String(200), nullable=True)  # "Senior Data Scientist", "HR Manager"
    bio = Column(Text, nullable=True)
    
    # Personalidad IA
    personalidad = Column(String(100), default="profesional")  # 'profesional', 'motivador', 'técnico'
    prompt_sistema = Column(Text, nullable=False)  # System prompt para el LLM
    modelo_ia = Column(String(100), default="gpt-4")  # Modelo LLM a usar
    temperatura = Column(Numeric(2, 1), default=0.7)
    max_tokens = Column(Integer, default=500)
    
    # Especialización
    areas_experiencia = Column(Text, nullable=True)  # JSON con tags de expertise
    idiomas = Column(String(100), default="es")
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    empresa = relationship("Empresa", backref="virtual_mentors")
    
    def __repr__(self):
        return f"<VirtualMentor {self.nombre} empresa={self.empresa_id}>"


class MentorConversation(Base):
    """
    Sesiones de conversación con mentores IA
    Agrupa mensajes en contextos de simulación
    """
    __tablename__ = "conversaciones_mentor"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mentor_id = Column(Integer, ForeignKey("mentores_virtuales.id"), nullable=False, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=True, index=True)
    
    # Estado
    estado = Column(Enum(EstadoConversacionEnum), nullable=False, default=EstadoConversacionEnum.ACTIVA, index=True)
    total_mensajes = Column(Integer, default=0, nullable=False)
    
    # Metadata
    titulo_conversacion = Column(String(300), nullable=True)
    contexto_inicial = Column(Text, nullable=True)  # Contexto de la simulación
    
    # Timestamps
    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now())
    fecha_ultimo_mensaje = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    fecha_finalizacion = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="mentor_conversations")
    mentor = relationship("VirtualMentor", backref="conversations")
    simulation = relationship("Simulation", backref="mentor_conversations")
    
    def __repr__(self):
        return f"<MentorConversation user={self.user_id} mentor={self.mentor_id} estado={self.estado}>"


class MentorMessage(Base):
    """
    Mensajes individuales en conversaciones con mentores
    Registro completo de interacciones IA
    """
    __tablename__ = "mensajes_mentor"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    conversacion_id = Column(Integer, ForeignKey("conversaciones_mentor.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mentor_id = Column(Integer, ForeignKey("mentores_virtuales.id"), nullable=False, index=True)
    
    # Mensaje
    rol = Column(Enum(RolMensajeEnum), nullable=False, index=True)
    contenido = Column(Text, nullable=False)
    
    # Metadata IA
    modelo_usado = Column(String(100), nullable=True)
    tokens_usados = Column(Integer, default=0)
    tiempo_respuesta_ms = Column(Integer, nullable=True)
    
    # Contexto
    mensaje_padre_id = Column(Integer, ForeignKey("mensajes_mentor.id"), nullable=True)
    
    # Feedback
    util = Column(Boolean, nullable=True)  # Rating del usuario
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    conversation = relationship("MentorConversation", backref="messages")
    user = relationship("User", backref="mentor_messages")
    mentor = relationship("VirtualMentor", backref="messages")
    parent_message = relationship("MentorMessage", remote_side=[id], backref="replies")
    
    def __repr__(self):
        return f"<MentorMessage conversacion={self.conversacion_id} rol={self.rol}>"


class OracleMessage(Base):
    """
    Mensajes del sistema Oráculo
    Interacciones con el asistente de orientación vocacional
    """
    __tablename__ = "mensajes_oraculo"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    sesion_id = Column(Integer, ForeignKey("sesiones_oraculo.id"), nullable=False, index=True)
    
    # Mensaje
    rol = Column(Enum(RolMensajeEnum), nullable=False, index=True)
    contenido = Column(Text, nullable=False)
    
    # Metadata IA
    modelo_usado = Column(String(100), nullable=True)
    tokens_usados = Column(Integer, default=0)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    
    # Contexto
    pregunta_id = Column(Integer, nullable=True)  # Referencia a OracleQuestion si aplica
    respuesta_usuario = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    session = relationship("OracleSession", backref="messages")
    
    def __repr__(self):
        return f"<OracleMessage sesion={self.sesion_id} rol={self.rol} tokens={self.tokens_usados}>"
