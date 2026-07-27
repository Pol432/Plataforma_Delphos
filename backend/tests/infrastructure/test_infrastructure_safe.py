"""
FASE 12 Infrastructure - Suite de Tests Robusta
REGLA DE ORO: Cero accesos a DB. Solo instancias en memoria + Pydantic.
Todas las funciones dentro de clases llevan self.
"""
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from pydantic import ValidationError

from app.models.infrastructure import (
    SocialAuth, UserSession, AuthLog,
    RateLimit, SystemConfig,
    Level, Referral,
    MentorSimulation,
    AuditSimulation, AuditCompany, AuditUser,
)
from app.models.progress import SimulationSkill
from app.schemas.infrastructure import (
    SocialAuthCreate, UserSessionCreate, AuthLogCreate,
    RateLimitCreate, SystemConfigCreate,
    LevelCreate, ReferralCreate,
    MentorSimulationCreate, SimulationSkillCreate,
    AuditSimulationCreate, AuditCompanyCreate, AuditUserCreate,
)

# Fixture de datetime reutilizable
_NOW = datetime(2025, 8, 1, 12, 0, 0, tzinfo=timezone.utc)


# ==============================================================================
# BLOQUE A: Autenticación y Sesiones
# ==============================================================================

class TestSocialAuth:
    def test_model_instancia_google(self):
        sa = SocialAuth(
            usuario_id=1,
            proveedor="google",
            proveedor_usuario_id="google-uid-12345",
            email_proveedor="user@gmail.com",
            verificado=True,
            total_usos=3
        )
        assert sa.proveedor == "google"
        assert sa.verificado is True
        assert sa.total_usos == 3

    def test_model_instancia_linkedin(self):
        sa = SocialAuth(
            usuario_id=2,
            proveedor="linkedin",
            proveedor_usuario_id="li-uid-999",
            es_metodo_principal=True
        )
        assert sa.es_metodo_principal is True

    def test_model_metadata_json(self):
        sa = SocialAuth(
            usuario_id=1,
            proveedor="github",
            proveedor_usuario_id="gh-123",
            metadata_proveedor={"login": "matji", "public_repos": 42}
        )
        assert sa.metadata_proveedor["public_repos"] == 42

    def test_schema_proveedor_valido(self):
        for p in ["google", "linkedin", "github", "microsoft", "apple"]:
            data = SocialAuthCreate(
                usuario_id=1, proveedor=p,
                proveedor_usuario_id="uid-123"
            )
            assert data.proveedor == p

    def test_schema_proveedor_invalido(self):
        with pytest.raises(ValidationError):
            SocialAuthCreate(
                usuario_id=1, proveedor="facebook",
                proveedor_usuario_id="uid-123"
            )

    def test_schema_usuario_id_cero_rechazado(self):
        with pytest.raises(ValidationError):
            SocialAuthCreate(
                usuario_id=0, proveedor="google",
                proveedor_usuario_id="uid-123"
            )

    def test_schema_proveedor_uid_vacio_rechazado(self):
        with pytest.raises(ValidationError):
            SocialAuthCreate(
                usuario_id=1, proveedor="google",
                proveedor_usuario_id=""
            )


class TestUserSession:
    def test_model_sesion_activa(self):
        s = UserSession(
            usuario_id=1,
            token_sesion="jwt.token.aqui",
            expira_en=_NOW,
            revocado=False,
            plataforma="web"
        )
        assert s.revocado is False
        assert s.plataforma == "web"

    def test_model_sesion_revocada(self):
        s = UserSession(
            usuario_id=2,
            token_sesion="jwt.revocado",
            expira_en=_NOW,
            revocado=True,
            razon_revocacion="logout"
        )
        assert s.revocado is True
        assert s.razon_revocacion == "logout"

    def test_model_total_requests_default(self):
        s = UserSession(
            usuario_id=1,
            token_sesion="tok",
            expira_en=_NOW,
            total_requests=0
        )
        assert s.total_requests == 0

    def test_schema_plataforma_valida(self):
        for p in ["web", "ios", "android", "desktop"]:
            data = UserSessionCreate(
                usuario_id=1,
                token_sesion="a" * 20,
                expira_en=_NOW,
                plataforma=p
            )
            assert data.plataforma == p

    def test_schema_plataforma_invalida(self):
        with pytest.raises(ValidationError):
            UserSessionCreate(
                usuario_id=1,
                token_sesion="a" * 20,
                expira_en=_NOW,
                plataforma="smartwatch"
            )

    def test_schema_token_muy_corto(self):
        with pytest.raises(ValidationError):
            UserSessionCreate(
                usuario_id=1,
                token_sesion="corto",
                expira_en=_NOW
            )


class TestAuthLog:
    def test_model_login_exitoso(self):
        log = AuthLog(
            usuario_id=1,
            tipo_evento="login_exitoso",
            metodo="email_password",
            exitoso=True,
            ip_address="192.168.1.1"
        )
        assert log.exitoso is True
        assert log.tipo_evento == "login_exitoso"

    def test_model_login_fallido_anonimo(self):
        log = AuthLog(
            usuario_id=None,
            tipo_evento="login_fallido",
            exitoso=False,
            razon_fallo="password_incorrecto"
        )
        assert log.usuario_id is None
        assert log.razon_fallo == "password_incorrecto"

    def test_schema_evento_valido(self):
        data = AuthLogCreate(
            tipo_evento="logout",
            exitoso=True
        )
        assert data.tipo_evento == "logout"

    def test_schema_evento_muy_corto(self):
        with pytest.raises(ValidationError):
            AuthLogCreate(tipo_evento="ab", exitoso=True)

    def test_schema_usuario_id_opcional(self):
        data = AuthLogCreate(tipo_evento="login_fallido", exitoso=False)
        assert data.usuario_id is None


# ==============================================================================
# BLOQUE B: Seguridad y Sistema
# ==============================================================================

class TestRateLimit:
    def test_model_no_bloqueado(self):
        rl = RateLimit(
            tipo_accion="login",
            contador=3,
            limite_max=10,
            ventana_inicio=_NOW,
            ventana_fin=_NOW,
            bloqueado=False
        )
        assert rl.bloqueado is False
        assert rl.contador == 3

    def test_model_bloqueado(self):
        rl = RateLimit(
            tipo_accion="api_call",
            contador=100,
            limite_max=100,
            ventana_inicio=_NOW,
            ventana_fin=_NOW,
            bloqueado=True
        )
        assert rl.bloqueado is True

    def test_model_usuario_anonimo(self):
        rl = RateLimit(
            usuario_id=None,
            ip_address="10.0.0.1",
            tipo_accion="login",
            contador=5,
            limite_max=20,
            ventana_inicio=_NOW,
            ventana_fin=_NOW
        )
        assert rl.usuario_id is None
        assert rl.ip_address == "10.0.0.1"

    def test_schema_limite_max_cero_rechazado(self):
        with pytest.raises(ValidationError):
            RateLimitCreate(
                tipo_accion="login",
                limite_max=0,
                ventana_inicio=_NOW,
                ventana_fin=_NOW
            )

    def test_schema_tipo_accion_corto(self):
        with pytest.raises(ValidationError):
            RateLimitCreate(
                tipo_accion="ab",
                limite_max=10,
                ventana_inicio=_NOW,
                ventana_fin=_NOW
            )


class TestSystemConfig:
    def test_model_config_string(self):
        cfg = SystemConfig(
            clave="site_name",
            valor="Delphos",
            tipo_dato="string",
            es_publico=True
        )
        assert cfg.clave == "site_name"
        assert cfg.es_publico is True

    def test_model_config_json(self):
        cfg = SystemConfig(
            clave="features_habilitadas",
            valor='{"dark_mode": true, "beta": false}',
            tipo_dato="json",
            categoria="integracion"
        )
        assert cfg.tipo_dato == "json"
        assert cfg.categoria == "integracion"

    def test_model_no_modificable(self):
        cfg = SystemConfig(
            clave="max_users",
            valor="10000",
            tipo_dato="integer",
            es_modificable=False
        )
        assert cfg.es_modificable is False

    def test_schema_tipos_validos(self):
        for tipo in ["string", "integer", "decimal", "boolean", "json"]:
            data = SystemConfigCreate(
                clave="mi_clave",
                valor="mi_valor",
                tipo_dato=tipo
            )
            assert data.tipo_dato == tipo

    def test_schema_tipo_invalido(self):
        with pytest.raises(ValidationError):
            SystemConfigCreate(
                clave="mi_clave",
                valor="mi_valor",
                tipo_dato="array"
            )

    def test_schema_clave_muy_corta(self):
        with pytest.raises(ValidationError):
            SystemConfigCreate(clave="x", valor="valor")

    def test_schema_valor_vacio_rechazado(self):
        with pytest.raises(ValidationError):
            SystemConfigCreate(clave="clave_ok", valor="")


# ==============================================================================
# BLOQUE C: Gamificación y Referidos
# ==============================================================================

class TestLevel:
    def test_model_nivel_basico(self):
        lvl = Level(
            nivel=1,
            xp_requerida=0,
            nombre_nivel="Novato",
            recompensa_xp_bonus=0
        )
        assert lvl.nivel == 1
        assert lvl.nombre_nivel == "Novato"

    def test_model_nivel_avanzado_con_recompensas(self):
        lvl = Level(
            nivel=10,
            xp_requerida=5000,
            nombre_nivel="Experto",
            recompensa_xp_bonus=200,
            recompensas_items=["avatar_especial", "badge_oro"],
            color="#FFD700"
        )
        assert lvl.nivel == 10
        assert lvl.xp_requerida == 5000
        assert lvl.recompensa_xp_bonus == 200

    def test_schema_nivel_cero_rechazado(self):
        with pytest.raises(ValidationError):
            LevelCreate(nivel=0, xp_requerida=0)

    def test_schema_xp_negativa_rechazada(self):
        with pytest.raises(ValidationError):
            LevelCreate(nivel=1, xp_requerida=-100)

    def test_schema_nivel_valido(self):
        data = LevelCreate(nivel=5, xp_requerida=2500, nombre_nivel="Avanzado")
        assert data.nombre_nivel == "Avanzado"
        assert data.recompensa_xp_bonus == 0


class TestReferral:
    def test_model_referral_pendiente(self):
        ref = Referral(
            usuario_referidor_id=1,
            usuario_referido_id=2,
            codigo_referido="DELPHOS2025",
            estado="pendiente",
            recompensa_referidor_xp=500,
            recompensa_referido_xp=200,
            recompensa_reclamada=False
        )
        assert ref.estado == "pendiente"
        assert ref.recompensa_reclamada is False

    def test_model_referral_completado(self):
        ref = Referral(
            usuario_referidor_id=1,
            usuario_referido_id=3,
            codigo_referido="PROMO100",
            estado="completado",
            recompensa_reclamada=True,
            simulaciones_completadas=1
        )
        assert ref.estado == "completado"
        assert ref.simulaciones_completadas == 1

    def test_schema_codigo_muy_corto(self):
        with pytest.raises(ValidationError):
            ReferralCreate(
                usuario_referidor_id=1,
                usuario_referido_id=2,
                codigo_referido="AB"
            )

    def test_schema_ids_iguales_tecnicamente_valido(self):
        # Pydantic no valida lógica de negocio, solo tipos
        data = ReferralCreate(
            usuario_referidor_id=1,
            usuario_referido_id=1,
            codigo_referido="CODIGO123"
        )
        assert data.usuario_referidor_id == data.usuario_referido_id

    def test_schema_id_cero_rechazado(self):
        with pytest.raises(ValidationError):
            ReferralCreate(
                usuario_referidor_id=0,
                usuario_referido_id=2,
                codigo_referido="CODIGO123"
            )


# ==============================================================================
# BLOQUE D: Tablas Puente
# ==============================================================================

class TestMentorSimulation:
    def test_model_mentor_principal(self):
        ms = MentorSimulation(
            simulacion_id=5,
            mentor_id=2,
            rol_en_simulacion="mentor_principal",
            disponible_chat_global=True,
            orden_presentacion=1
        )
        assert ms.rol_en_simulacion == "mentor_principal"
        assert ms.disponible_chat_global is True

    def test_model_experto_invitado(self):
        ms = MentorSimulation(
            simulacion_id=3,
            mentor_id=7,
            rol_en_simulacion="experto_invitado",
            disponible_chat_global=False,
            mensaje_bienvenida="Hola, soy experto en finanzas"
        )
        assert ms.rol_en_simulacion == "experto_invitado"
        assert ms.disponible_chat_global is False

    def test_schema_roles_validos(self):
        for rol in ["mentor_principal", "supervisor", "colega", "experto_invitado"]:
            data = MentorSimulationCreate(
                simulacion_id=1,
                mentor_id=1,
                rol_en_simulacion=rol
            )
            assert data.rol_en_simulacion == rol

    def test_schema_rol_invalido(self):
        with pytest.raises(ValidationError):
            MentorSimulationCreate(
                simulacion_id=1,
                mentor_id=1,
                rol_en_simulacion="jefe"
            )

    def test_schema_orden_cero_rechazado(self):
        with pytest.raises(ValidationError):
            MentorSimulationCreate(
                simulacion_id=1,
                mentor_id=1,
                orden_presentacion=0
            )


# ==============================================================================
# BLOQUE E: Auditoría
# ==============================================================================

class TestAuditSimulation:
    def test_model_auditoria_publicar(self):
        audit = AuditSimulation(
            simulacion_id=10,
            usuario_empresa_id=3,
            accion="publicar",
            ip_address="192.168.0.1"
        )
        assert audit.accion == "publicar"
        assert audit.ip_address == "192.168.0.1"

    def test_model_sin_usuario_empresa(self):
        audit = AuditSimulation(
            simulacion_id=5,
            usuario_empresa_id=None,
            accion="archivar"
        )
        assert audit.usuario_empresa_id is None

    def test_model_campos_modificados_json(self):
        audit = AuditSimulation(
            simulacion_id=1,
            accion="editar",
            campos_modificados={
                "titulo": {"antes": "Viejo", "despues": "Nuevo"},
                "estado": {"antes": "draft", "despues": "published"}
            }
        )
        assert audit.campos_modificados["titulo"]["despues"] == "Nuevo"

    def test_schema_accion_muy_corta(self):
        with pytest.raises(ValidationError):
            AuditSimulationCreate(simulacion_id=1, accion="ab")

    def test_schema_simulacion_id_invalido(self):
        with pytest.raises(ValidationError):
            AuditSimulationCreate(simulacion_id=0, accion="editar")


class TestAuditCompany:
    def test_model_verificar_empresa(self):
        audit = AuditCompany(
            empresa_id=2,
            admin_dao_id=1,
            accion="verificar",
            detalles="RUC válido confirmado"
        )
        assert audit.accion == "verificar"
        assert audit.detalles == "RUC válido confirmado"

    def test_model_sin_admin(self):
        audit = AuditCompany(
            empresa_id=3,
            admin_dao_id=None,
            accion="crear"
        )
        assert audit.admin_dao_id is None

    def test_schema_empresa_id_cero_rechazado(self):
        with pytest.raises(ValidationError):
            AuditCompanyCreate(empresa_id=0, accion="editar")

    def test_schema_accion_valida(self):
        data = AuditCompanyCreate(empresa_id=1, accion="cambiar_plan")
        assert data.accion == "cambiar_plan"

    def test_schema_campos_modificados_dict(self):
        data = AuditCompanyCreate(
            empresa_id=1,
            accion="editar",
            campos_modificados={"tipo_partnership": {"antes": "basico", "despues": "premium"}}
        )
        assert data.campos_modificados["tipo_partnership"]["despues"] == "premium"


class TestAuditUser:
    def test_model_bloqueo_usuario(self):
        audit = AuditUser(
            usuario_id=50,
            admin_dao_id=1,
            accion="bloquear",
            razon="Comportamiento sospechoso detectado"
        )
        assert audit.accion == "bloquear"
        assert audit.razon == "Comportamiento sospechoso detectado"

    def test_model_reset_password(self):
        audit = AuditUser(
            usuario_id=20,
            admin_dao_id=2,
            accion="resetear_password",
            ip_address="10.0.0.5"
        )
        assert audit.ip_address == "10.0.0.5"

    def test_model_sin_admin_dao(self):
        audit = AuditUser(
            usuario_id=1,
            admin_dao_id=None,
            accion="editar_perfil"
        )
        assert audit.admin_dao_id is None

    def test_schema_usuario_id_negativo_rechazado(self):
        with pytest.raises(ValidationError):
            AuditUserCreate(usuario_id=-1, accion="bloquear")

    def test_schema_accion_muy_larga_rechazada(self):
        with pytest.raises(ValidationError):
            AuditUserCreate(usuario_id=1, accion="x" * 51)

    def test_schema_accion_muy_corta_rechazada(self):
        with pytest.raises(ValidationError):
            AuditUserCreate(usuario_id=1, accion="ab")

