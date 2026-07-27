"""
Gamification Safe Tests - Fase 9
Tests en memoria (sin db.add()) para validar modelos y schemas
"""
import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.models.gamification import (
    UserModule, TaskSkill, XPTransaction,
    Achievement, UserAchievement,
    Mission, UserMission,
    VirtualMentor, MentorConversation, MentorMessage,
    OracleMessage,
    EstadoModuloEnum, TipoFuenteXPEnum, TipoLogroEnum,
    EstadoMisionEnum, EstadoConversacionEnum, RolMensajeEnum
)
from app.schemas.gamification import (
    XPTransactionCreate, AchievementCreate, MissionCreate,
    TaskSkillCreate, VirtualMentorCreate,
    MentorMessageCreate, OracleMessageCreate
)


class TestGamificationModelsSafe:
    """Tests de instanciación de modelos (en memoria)"""
    
    def test_user_module_instantiation(self):
        """Test: Instanciar UserModule en memoria"""
        user_module = UserModule(
            user_id=1,
            module_id=2,
            simulacion_usuario_id=3,
            estado=EstadoModuloEnum.EN_PROGRESO,
            porcentaje_completado=Decimal("45.50"),
            tiempo_dedicado_minutos=120
        )
        assert user_module.user_id == 1
        assert user_module.estado == EstadoModuloEnum.EN_PROGRESO
        assert user_module.porcentaje_completado == Decimal("45.50")
        assert user_module.tiempo_dedicado_minutos == 120
    
    def test_task_skill_instantiation(self):
        """Test: Instanciar TaskSkill con defaults"""
        task_skill = TaskSkill(
            task_id=10,
            skill_id=5,
            xp_ganado=25,
            peso=Decimal("1.5")
        )
        assert task_skill.task_id == 10
        assert task_skill.skill_id == 5
        assert task_skill.xp_ganado == 25
        assert task_skill.peso == Decimal("1.5")
    
    def test_xp_transaction_instantiation(self):
        """Test: Instanciar XPTransaction (puede ser negativo)"""
        xp_trans = XPTransaction(
            user_id=1,
            cantidad_xp=-50,  # Penalización
            tipo_fuente=TipoFuenteXPEnum.PENALIZACION,
            fuente_id=None,
            descripcion="Penalización por inactividad",
            xp_anterior=500,
            xp_nuevo=450
        )
        assert xp_trans.cantidad_xp == -50
        assert xp_trans.tipo_fuente == TipoFuenteXPEnum.PENALIZACION
        assert xp_trans.xp_nuevo == 450
    
    def test_achievement_instantiation(self):
        """Test: Instanciar Achievement con defaults"""
        achievement = Achievement(
            titulo="Primera Victoria",
            descripcion="Completa tu primera tarea",
            tipo_logro=TipoLogroEnum.BRONCE,
            recompensa_xp=100,
            is_active=True,
            is_hidden=False
        )
        assert achievement.titulo == "Primera Victoria"
        assert achievement.tipo_logro == TipoLogroEnum.BRONCE
        assert achievement.recompensa_xp == 100
        assert achievement.is_active is True
    
    def test_user_achievement_instantiation(self):
        """Test: Instanciar UserAchievement"""
        user_ach = UserAchievement(
            user_id=1,
            logro_id=5,
            desbloqueado=True,
            progreso_actual=10,
            progreso_requerido=10,
            notificado=False
        )
        assert user_ach.desbloqueado is True
        assert user_ach.progreso_actual == 10
        assert user_ach.notificado is False
    
    def test_mission_instantiation(self):
        """Test: Instanciar Mission"""
        mission = Mission(
            titulo="Racha Semanal",
            descripcion="Completa tareas 7 días seguidos",
            objetivo_tipo="racha_dias",
            objetivo_cantidad=7,
            recompensa_xp=500,
            is_active=True,
            es_semanal=True
        )
        assert mission.objetivo_tipo == "racha_dias"
        assert mission.objetivo_cantidad == 7
        assert mission.es_semanal is True
    
    def test_user_mission_instantiation(self):
        """Test: Instanciar UserMission"""
        user_mission = UserMission(
            user_id=1,
            mision_id=3,
            progreso_actual=5,
            estado=EstadoMisionEnum.EN_PROGRESO,
            recompensa_reclamada=False
        )
        assert user_mission.progreso_actual == 5
        assert user_mission.estado == EstadoMisionEnum.EN_PROGRESO
        assert user_mission.recompensa_reclamada is False
    
    def test_virtual_mentor_instantiation(self):
        """Test: Instanciar VirtualMentor"""
        mentor = VirtualMentor(
            empresa_id=1,
            nombre="Dr. Tech",
            personalidad="profesional",
            prompt_sistema="Eres un mentor experto en tecnología",
            modelo_ia="gpt-4",
            temperatura=Decimal("0.7"),
            max_tokens=500,
            is_active=True
        )
        assert mentor.nombre == "Dr. Tech"
        assert mentor.modelo_ia == "gpt-4"
        assert mentor.temperatura == Decimal("0.7")
    
    def test_mentor_conversation_instantiation(self):
        """Test: Instanciar MentorConversation"""
        conversation = MentorConversation(
            user_id=1,
            mentor_id=2,
            simulation_id=3,
            estado=EstadoConversacionEnum.ACTIVA,
            total_mensajes=0
        )
        assert conversation.estado == EstadoConversacionEnum.ACTIVA
        assert conversation.total_mensajes == 0
    
    def test_mentor_message_instantiation(self):
        """Test: Instanciar MentorMessage"""
        message = MentorMessage(
            conversacion_id=1,
            user_id=2,
            mentor_id=3,
            rol=RolMensajeEnum.ASSISTANT,
            contenido="Hola, ¿en qué puedo ayudarte?",
            modelo_usado="gpt-4",
            tokens_usados=15,
            tiempo_respuesta_ms=250
        )
        assert message.rol == RolMensajeEnum.ASSISTANT
        assert message.tokens_usados == 15
        assert message.tiempo_respuesta_ms == 250
    
    def test_oracle_message_instantiation(self):
        """Test: Instanciar OracleMessage"""
        oracle_msg = OracleMessage(
            sesion_id=1,
            rol=RolMensajeEnum.USER,
            contenido="Me gusta la programación",
            modelo_usado="gpt-4",
            tokens_usados=20,
            prompt_tokens=15,
            completion_tokens=5
        )
        assert oracle_msg.sesion_id == 1
        assert oracle_msg.rol == RolMensajeEnum.USER
        assert oracle_msg.tokens_usados == 20


class TestGamificationSchemasSafe:
    """Tests de validación Pydantic (en memoria)"""
    
    def test_xp_transaction_create_valid(self):
        """Test: Schema XPTransactionCreate válido"""
        schema = XPTransactionCreate(
            user_id=1,
            cantidad_xp=100,
            tipo_fuente="tarea",
            fuente_id=5,
            descripcion="Tarea completada exitosamente"
        )
        assert schema.cantidad_xp == 100
        assert schema.tipo_fuente == "tarea"
    
    def test_xp_transaction_create_negative(self):
        """Test: XP negativo (penalización) es válido"""
        schema = XPTransactionCreate(
            user_id=1,
            cantidad_xp=-50,
            tipo_fuente="penalizacion",
            descripcion="Penalización"
        )
        assert schema.cantidad_xp == -50
    
    def test_xp_transaction_invalid_tipo(self):
        """Test: Tipo de fuente inválido rechazado"""
        with pytest.raises(ValidationError):
            XPTransactionCreate(
                user_id=1,
                cantidad_xp=100,
                tipo_fuente="invalido",
                descripcion="Test"
            )
    
    def test_achievement_create_valid(self):
        """Test: Schema AchievementCreate válido"""
        schema = AchievementCreate(
            titulo="Maestro",
            descripcion="Completa 100 tareas",
            tipo_logro="oro",
            recompensa_xp=1000
        )
        assert schema.tipo_logro == "oro"
        assert schema.recompensa_xp == 1000
    
    def test_achievement_invalid_tipo(self):
        """Test: Tipo de logro inválido rechazado"""
        with pytest.raises(ValidationError):
            AchievementCreate(
                titulo="Test",
                descripcion="Test",
                tipo_logro="diamante",  # No existe
                recompensa_xp=100
            )
    
    def test_mission_create_valid(self):
        """Test: Schema MissionCreate válido"""
        schema = MissionCreate(
            titulo="Desafío Semanal",
            descripcion="Completa 10 tareas esta semana",
            objetivo_tipo="completar_tareas",
            objetivo_cantidad=10,
            recompensa_xp=500
        )
        assert schema.objetivo_cantidad == 10
        assert schema.recompensa_xp == 500
    
    def test_mission_invalid_objetivo_cantidad(self):
        """Test: Cantidad de objetivo inválida (negativa)"""
        with pytest.raises(ValidationError):
            MissionCreate(
                titulo="Test",
                descripcion="Test",
                objetivo_tipo="test",
                objetivo_cantidad=-5,  # Debe ser >= 1
                recompensa_xp=100
            )
    
    def test_task_skill_create_valid(self):
        """Test: Schema TaskSkillCreate válido"""
        schema = TaskSkillCreate(
            task_id=10,
            skill_id=5,
            xp_ganado=25,
            peso=Decimal("1.5")
        )
        assert schema.peso == Decimal("1.5")
        assert schema.xp_ganado == 25
    
    def test_task_skill_invalid_peso(self):
        """Test: Peso fuera de rango (>2.0) rechazado"""
        with pytest.raises(ValidationError):
            TaskSkillCreate(
                task_id=1,
                skill_id=1,
                xp_ganado=10,
                peso=Decimal("3.0")  # Max es 2.0
            )
    
    def test_virtual_mentor_create_valid(self):
        """Test: Schema VirtualMentorCreate válido"""
        schema = VirtualMentorCreate(
            empresa_id=1,
            nombre="AI Mentor",
            personalidad="motivador",
            prompt_sistema="Eres un mentor motivador",
            modelo_ia="gpt-4"
        )
        assert schema.nombre == "AI Mentor"
        assert schema.modelo_ia == "gpt-4"
    
    def test_mentor_message_create_valid(self):
        """Test: Schema MentorMessageCreate válido"""
        schema = MentorMessageCreate(
            conversacion_id=1,
            rol="assistant",
            contenido="¿Cómo puedo ayudarte?"
        )
        assert schema.rol == "assistant"
        assert len(schema.contenido) > 0
    
    def test_mentor_message_invalid_rol(self):
        """Test: Rol inválido rechazado"""
        with pytest.raises(ValidationError):
            MentorMessageCreate(
                conversacion_id=1,
                rol="admin",  # No existe
                contenido="Test"
            )
    
    def test_oracle_message_create_valid(self):
        """Test: Schema OracleMessageCreate válido"""
        schema = OracleMessageCreate(
            sesion_id=1,
            rol="user",
            contenido="Me interesa la ciencia"
        )
        assert schema.sesion_id == 1
        assert schema.rol == "user"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
