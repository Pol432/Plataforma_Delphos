"""
FASE 11 Enterprise - Suite de Tests Robusta
REGLA DE ORO: Cero accesos a DB. Solo instancias en memoria + validaciones Pydantic.
Todas las funciones de clase llevan self.
"""
import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.models.enterprise import (
    FeedPost, PostLike, PostComment, SavedPost,
    Notification, NotificationPreference,
    SupportTicket, TicketMessage, GeneralFeedback,
    SubscriptionPlan, UserSubscription, PaymentTransaction,
    AdminDao, FraudAttempt,
)
from app.schemas.enterprise import (
    FeedPostCreate, PostLikeCreate, PostCommentCreate, SavedPostCreate,
    NotificationCreate, NotificationPreferenceCreate,
    SupportTicketCreate, TicketMessageCreate, GeneralFeedbackCreate,
    SubscriptionPlanCreate, UserSubscriptionCreate, PaymentTransactionCreate,
    AdminDaoCreate, FraudAttemptCreate,
)


# ==============================================================================
# BLOQUE A: Feed Social
# ==============================================================================

class TestFeedPost:
    def test_model_instancia_basica(self):
        post = FeedPost(user_id=1, contenido="Hola comunidad", esta_activo=True)
        assert post.contenido == "Hola comunidad"
        assert post.esta_activo is True

    def test_model_imagen_url_none_por_defecto(self):
        post = FeedPost(user_id=1, contenido="Sin imagen", esta_activo=True)
        assert post.imagen_url is None

    def test_model_con_imagen_url(self):
        post = FeedPost(user_id=2, contenido="Con imagen", imagen_url="https://cdn.delphos.io/img.png", esta_activo=True)
        assert post.imagen_url == "https://cdn.delphos.io/img.png"

    def test_schema_create_valido(self):
        data = FeedPostCreate(user_id=1, contenido="Post válido")
        assert data.user_id == 1
        assert data.contenido == "Post válido"

    def test_schema_contenido_vacio_rechazado(self):
        with pytest.raises(ValidationError):
            FeedPostCreate(user_id=1, contenido="")

    def test_schema_user_id_cero_rechazado(self):
        with pytest.raises(ValidationError):
            FeedPostCreate(user_id=0, contenido="Test")

    def test_schema_user_id_negativo_rechazado(self):
        with pytest.raises(ValidationError):
            FeedPostCreate(user_id=-5, contenido="Test")

    def test_schema_imagen_url_muy_larga_rechazada(self):
        with pytest.raises(ValidationError):
            FeedPostCreate(user_id=1, contenido="Test", imagen_url="x" * 501)


class TestPostLike:
    def test_model_instancia_en_memoria(self):
        like = PostLike(post_id=5, user_id=10)
        assert like.post_id == 5
        assert like.user_id == 10

    def test_schema_valido(self):
        data = PostLikeCreate(post_id=1, user_id=2)
        assert data.post_id == 1
        assert data.user_id == 2

    def test_schema_post_id_cero_rechazado(self):
        with pytest.raises(ValidationError):
            PostLikeCreate(post_id=0, user_id=1)

    def test_schema_user_id_negativo_rechazado(self):
        with pytest.raises(ValidationError):
            PostLikeCreate(post_id=1, user_id=-1)

    def test_schema_ambos_ids_negativos_rechazados(self):
        with pytest.raises(ValidationError):
            PostLikeCreate(post_id=-1, user_id=-1)


class TestPostComment:
    def test_model_instancia_en_memoria(self):
        comentario = PostComment(post_id=1, user_id=2, contenido="Gran aporte!")
        assert comentario.contenido == "Gran aporte!"

    def test_schema_valido(self):
        data = PostCommentCreate(post_id=1, user_id=2, contenido="Excelente")
        assert data.contenido == "Excelente"

    def test_schema_contenido_vacio_rechazado(self):
        with pytest.raises(ValidationError):
            PostCommentCreate(post_id=1, user_id=2, contenido="")

    def test_schema_post_id_invalido(self):
        with pytest.raises(ValidationError):
            PostCommentCreate(post_id=0, user_id=1, contenido="Test")


class TestSavedPost:
    def test_model_instancia_en_memoria(self):
        guardado = SavedPost(post_id=10, user_id=4)
        assert guardado.post_id == 10
        assert guardado.user_id == 4

    def test_schema_valido(self):
        data = SavedPostCreate(post_id=3, user_id=4)
        assert data.post_id == 3
        assert data.user_id == 4

    def test_schema_post_id_cero_rechazado(self):
        with pytest.raises(ValidationError):
            SavedPostCreate(post_id=0, user_id=1)

    def test_schema_user_id_negativo_rechazado(self):
        with pytest.raises(ValidationError):
            SavedPostCreate(post_id=1, user_id=-10)


# ==============================================================================
# BLOQUE B: Notificaciones
# ==============================================================================

class TestNotification:
    def test_model_defaults(self):
        notif = Notification(
            user_id=1, titulo="Alerta", mensaje="Revisa tu perfil",
            tipo="sistema", leida=False
        )
        assert notif.leida is False
        assert notif.tipo == "sistema"

    def test_model_link_accion_none(self):
        notif = Notification(user_id=1, titulo="T", mensaje="M", tipo="social", leida=False)
        assert notif.link_accion is None

    def test_schema_tipo_sistema(self):
        data = NotificationCreate(user_id=1, titulo="T", mensaje="M", tipo="sistema")
        assert data.tipo == "sistema"

    def test_schema_tipo_social(self):
        data = NotificationCreate(user_id=1, titulo="T", mensaje="M", tipo="social")
        assert data.tipo == "social"

    def test_schema_tipo_simulacion(self):
        data = NotificationCreate(user_id=1, titulo="T", mensaje="M", tipo="simulacion")
        assert data.tipo == "simulacion"

    def test_schema_tipo_invalido_rechazado(self):
        with pytest.raises(ValidationError):
            NotificationCreate(user_id=1, titulo="T", mensaje="M", tipo="marketing")

    def test_schema_titulo_vacio_rechazado(self):
        with pytest.raises(ValidationError):
            NotificationCreate(user_id=1, titulo="", mensaje="M")

    def test_schema_mensaje_vacio_rechazado(self):
        with pytest.raises(ValidationError):
            NotificationCreate(user_id=1, titulo="T", mensaje="")

    def test_schema_titulo_max_length(self):
        with pytest.raises(ValidationError):
            NotificationCreate(user_id=1, titulo="x" * 201, mensaje="M")


class TestNotificationPreference:
    def test_model_instancia_con_push_desactivado(self):
        pref = NotificationPreference(
            user_id=2, email_marketing=True, email_alertas=True, push_social=False
        )
        assert pref.push_social is False
        assert pref.email_marketing is True

    def test_schema_todos_desactivados(self):
        data = NotificationPreferenceCreate(
            user_id=1, email_marketing=False, email_alertas=False, push_social=False
        )
        assert data.email_marketing is False
        assert data.email_alertas is False
        assert data.push_social is False

    def test_schema_defaults_todos_activos(self):
        data = NotificationPreferenceCreate(user_id=1)
        assert data.email_marketing is True
        assert data.email_alertas is True
        assert data.push_social is True

    def test_schema_user_id_invalido(self):
        with pytest.raises(ValidationError):
            NotificationPreferenceCreate(user_id=0)


# ==============================================================================
# BLOQUE C: Soporte y Feedback
# ==============================================================================

class TestSupportTicket:
    def test_model_estado_default_abierto(self):
        ticket = SupportTicket(
            user_id=1, asunto="Error en login",
            descripcion="No puedo entrar", estado="abierto", prioridad="alta"
        )
        assert ticket.estado == "abierto"
        assert ticket.prioridad == "alta"

    def test_schema_todas_las_prioridades(self):
        for prioridad in ["baja", "media", "alta", "critica"]:
            data = SupportTicketCreate(
                user_id=1, asunto="Asunto ok",
                descripcion="Descripcion larga ok", prioridad=prioridad
            )
            assert data.prioridad == prioridad

    def test_schema_prioridad_invalida_rechazada(self):
        with pytest.raises(ValidationError):
            SupportTicketCreate(
                user_id=1, asunto="Test",
                descripcion="Descripcion larga", prioridad="urgente"
            )

    def test_schema_asunto_muy_corto_rechazado(self):
        with pytest.raises(ValidationError):
            SupportTicketCreate(user_id=1, asunto="AB", descripcion="Descripcion larga ok")

    def test_schema_descripcion_muy_corta_rechazada(self):
        with pytest.raises(ValidationError):
            SupportTicketCreate(user_id=1, asunto="Asunto ok", descripcion="Corto")

    def test_schema_user_id_invalido(self):
        with pytest.raises(ValidationError):
            SupportTicketCreate(user_id=-1, asunto="Asunto ok", descripcion="Descripcion larga ok")


class TestTicketMessage:
    def test_model_mensaje_usuario(self):
        msg = TicketMessage(ticket_id=1, user_id=5, mensaje="Mi pregunta", es_staff=False)
        assert msg.es_staff is False
        assert msg.mensaje == "Mi pregunta"

    def test_model_mensaje_staff(self):
        msg = TicketMessage(ticket_id=1, user_id=99, mensaje="Respuesta del equipo", es_staff=True)
        assert msg.es_staff is True

    def test_schema_valido(self):
        data = TicketMessageCreate(ticket_id=1, user_id=1, mensaje="Hola", es_staff=False)
        assert data.mensaje == "Hola"

    def test_schema_mensaje_vacio_rechazado(self):
        with pytest.raises(ValidationError):
            TicketMessageCreate(ticket_id=1, user_id=1, mensaje="")

    def test_schema_ticket_id_cero_rechazado(self):
        with pytest.raises(ValidationError):
            TicketMessageCreate(ticket_id=0, user_id=1, mensaje="Test")


class TestGeneralFeedback:
    def test_model_anonimo(self):
        fb = GeneralFeedback(user_id=None, tipo="bug", mensaje="Falla el botón", calificacion=2)
        assert fb.user_id is None
        assert fb.tipo == "bug"

    def test_model_con_usuario(self):
        fb = GeneralFeedback(user_id=5, tipo="idea", mensaje="Agregar dark mode", calificacion=5)
        assert fb.calificacion == 5

    def test_schema_tipo_bug(self):
        data = GeneralFeedbackCreate(tipo="bug", mensaje="Error encontrado aqui")
        assert data.tipo == "bug"

    def test_schema_tipo_idea(self):
        data = GeneralFeedbackCreate(tipo="idea", mensaje="Una idea muy buena")
        assert data.tipo == "idea"

    def test_schema_tipo_invalido_rechazado(self):
        with pytest.raises(ValidationError):
            GeneralFeedbackCreate(tipo="queja", mensaje="Mensaje largo ok")

    def test_schema_calificacion_maxima_valida(self):
        data = GeneralFeedbackCreate(tipo="idea", mensaje="Mensaje largo", calificacion=5)
        assert data.calificacion == 5

    def test_schema_calificacion_minima_valida(self):
        data = GeneralFeedbackCreate(tipo="bug", mensaje="Mensaje largo", calificacion=1)
        assert data.calificacion == 1

    def test_schema_calificacion_sobre_5_rechazada(self):
        with pytest.raises(ValidationError):
            GeneralFeedbackCreate(tipo="idea", mensaje="Mensaje largo", calificacion=6)

    def test_schema_calificacion_cero_rechazada(self):
        with pytest.raises(ValidationError):
            GeneralFeedbackCreate(tipo="idea", mensaje="Mensaje largo", calificacion=0)

    def test_schema_mensaje_muy_corto_rechazado(self):
        with pytest.raises(ValidationError):
            GeneralFeedbackCreate(tipo="bug", mensaje="Cor")


# ==============================================================================
# BLOQUE D: Monetización y Seguridad
# ==============================================================================

class TestSubscriptionPlan:
    def test_model_con_caracteristicas_json(self):
        plan = SubscriptionPlan(
            nombre="Pro",
            precio_mensual=Decimal("29.99"),
            es_activo=True,
            caracteristicas={"simulaciones_ilimitadas": True, "certificados": True}
        )
        assert plan.nombre == "Pro"
        assert plan.caracteristicas["certificados"] is True

    def test_model_plan_gratuito(self):
        plan = SubscriptionPlan(nombre="Free", precio_mensual=Decimal("0.00"), es_activo=True)
        assert plan.precio_mensual == Decimal("0.00")

    def test_schema_precio_cero_valido(self):
        data = SubscriptionPlanCreate(nombre="Free", precio_mensual=Decimal("0.00"))
        assert data.precio_mensual == Decimal("0.00")

    def test_schema_precio_negativo_rechazado(self):
        with pytest.raises(ValidationError):
            SubscriptionPlanCreate(nombre="Plan", precio_mensual=Decimal("-1.00"))

    def test_schema_nombre_muy_corto_rechazado(self):
        with pytest.raises(ValidationError):
            SubscriptionPlanCreate(nombre="X", precio_mensual=Decimal("9.99"))

    def test_schema_nombre_max_length_rechazado(self):
        with pytest.raises(ValidationError):
            SubscriptionPlanCreate(nombre="N" * 101, precio_mensual=Decimal("9.99"))


class TestUserSubscription:
    def test_model_instancia_activa(self):
        sub = UserSubscription(user_id=1, plan_id=2, estado="activa", metodo_pago="stripe")
        assert sub.estado == "activa"
        assert sub.metodo_pago == "stripe"

    def test_schema_estado_activa(self):
        data = UserSubscriptionCreate(user_id=1, plan_id=1, estado="activa")
        assert data.estado == "activa"

    def test_schema_estado_cancelada(self):
        data = UserSubscriptionCreate(user_id=1, plan_id=1, estado="cancelada")
        assert data.estado == "cancelada"

    def test_schema_estado_vencida(self):
        data = UserSubscriptionCreate(user_id=1, plan_id=1, estado="vencida")
        assert data.estado == "vencida"

    def test_schema_estado_trial(self):
        data = UserSubscriptionCreate(user_id=1, plan_id=1, estado="trial")
        assert data.estado == "trial"

    def test_schema_estado_invalido_rechazado(self):
        with pytest.raises(ValidationError):
            UserSubscriptionCreate(user_id=1, plan_id=1, estado="suspendida")

    def test_schema_plan_id_cero_rechazado(self):
        with pytest.raises(ValidationError):
            UserSubscriptionCreate(user_id=1, plan_id=0)


class TestPaymentTransaction:
    def test_model_instancia_completada(self):
        tx = PaymentTransaction(
            user_id=1, plan_id=2, monto=Decimal("29.99"),
            estado="completado", id_transaccion_pasarela="stripe_pi_abc123"
        )
        assert tx.estado == "completado"
        assert tx.id_transaccion_pasarela == "stripe_pi_abc123"

    def test_schema_estado_pendiente(self):
        data = PaymentTransactionCreate(user_id=1, plan_id=1, monto=Decimal("9.99"), estado="pendiente")
        assert data.estado == "pendiente"

    def test_schema_estado_fallido(self):
        data = PaymentTransactionCreate(user_id=1, plan_id=1, monto=Decimal("9.99"), estado="fallido")
        assert data.estado == "fallido"

    def test_schema_estado_reembolsado(self):
        data = PaymentTransactionCreate(user_id=1, plan_id=1, monto=Decimal("9.99"), estado="reembolsado")
        assert data.estado == "reembolsado"

    def test_schema_monto_cero_rechazado(self):
        with pytest.raises(ValidationError):
            PaymentTransactionCreate(user_id=1, plan_id=1, monto=Decimal("0.00"))

    def test_schema_monto_negativo_rechazado(self):
        with pytest.raises(ValidationError):
            PaymentTransactionCreate(user_id=1, plan_id=1, monto=Decimal("-5.00"))

    def test_schema_estado_invalido_rechazado(self):
        with pytest.raises(ValidationError):
            PaymentTransactionCreate(user_id=1, plan_id=1, monto=Decimal("10"), estado="procesando")


class TestAdminDao:
    def test_model_superadmin(self):
        admin = AdminDao(user_id=1, rol="superadmin", esta_activo=True)
        assert admin.rol == "superadmin"
        assert admin.esta_activo is True

    def test_model_moderador(self):
        admin = AdminDao(user_id=2, rol="moderador", esta_activo=True)
        assert admin.rol == "moderador"

    def test_schema_rol_superadmin(self):
        data = AdminDaoCreate(user_id=1, rol="superadmin")
        assert data.rol == "superadmin"

    def test_schema_rol_moderador(self):
        data = AdminDaoCreate(user_id=1, rol="moderador")
        assert data.rol == "moderador"

    def test_schema_rol_invalido_rechazado(self):
        with pytest.raises(ValidationError):
            AdminDaoCreate(user_id=1, rol="editor")

    def test_schema_user_id_cero_rechazado(self):
        with pytest.raises(ValidationError):
            AdminDaoCreate(user_id=0, rol="moderador")


class TestFraudAttempt:
    def test_model_anonimo(self):
        intento = FraudAttempt(
            user_id=None, ip_address="192.168.1.100",
            tipo_intento="brute_force", descripcion="10 intentos en 60s"
        )
        assert intento.user_id is None
        assert intento.ip_address == "192.168.1.100"

    def test_model_con_usuario(self):
        intento = FraudAttempt(user_id=42, ip_address="10.0.0.1", tipo_intento="token_invalido")
        assert intento.user_id == 42

    def test_schema_ip_valida(self):
        data = FraudAttemptCreate(ip_address="192.168.1.1", tipo_intento="brute_force")
        assert data.ip_address == "192.168.1.1"

    def test_schema_ip_muy_corta_rechazada(self):
        with pytest.raises(ValidationError):
            FraudAttemptCreate(ip_address="1.1", tipo_intento="hack")

    def test_schema_ip_muy_larga_rechazada(self):
        with pytest.raises(ValidationError):
            FraudAttemptCreate(ip_address="x" * 46, tipo_intento="brute_force")

    def test_schema_tipo_muy_corto_rechazado(self):
        with pytest.raises(ValidationError):
            FraudAttemptCreate(ip_address="192.168.1.1", tipo_intento="AB")

    def test_schema_descripcion_opcional(self):
        data = FraudAttemptCreate(ip_address="192.168.1.1", tipo_intento="brute_force")
        assert data.descripcion is None
