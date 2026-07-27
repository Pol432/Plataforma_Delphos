import json
from datetime import datetime
from typing import Optional
from sqlalchemy import text
from db.connection import engine
from schemas import SkillState, UserSkillProfile, InferenceResult


# ──────────────────────────────────────────────
# Skill catalog
# ──────────────────────────────────────────────

def load_skill_index() -> dict[str, int]:
    """Returns {slug: habilidad_id} for every active skill in the catalog."""
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT id, slug FROM habilidades_catalogo WHERE esta_activo = true"
        )).fetchall()
    return {r.slug: r.id for r in rows}


def load_skill_catalog() -> list[dict]:
    """Returns full catalog rows (id, slug, nombre, categoria)."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT id, slug, nombre, categoria
            FROM habilidades_catalogo
            WHERE esta_activo = true
            ORDER BY id
        """)).fetchall()
    return [dict(r._mapping) for r in rows]


# ──────────────────────────────────────────────
# User skill profile
# ──────────────────────────────────────────────

def get_user_profile(usuario_id: int) -> UserSkillProfile:
    """Load all skill rows for a user and return a UserSkillProfile."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT
              hu.habilidad_id,
              hc.slug,
              hu.xp_total,
              hu.nivel,
              COALESCE(hu.confianza, 0)                  AS confianza,
              COALESCE(hu.velocidad, 0)                  AS velocidad,
              COALESCE(hu.tendencia_ia, 'unknown')       AS tendencia_ia,
              hu.aptitud_predicha,
              COALESCE(hu.fuentes_evidencia, '[]'::jsonb) AS fuentes_evidencia,
              hu.ultimo_inferido_en
            FROM habilidades_usuario hu
            JOIN habilidades_catalogo hc ON hc.id = hu.habilidad_id
            WHERE hu.usuario_id = :uid
        """), {"uid": usuario_id}).fetchall()

        onboarding = conn.execute(text("""
            SELECT onboarding_completado
            FROM usuarios WHERE id = :uid
        """), {"uid": usuario_id}).scalar()

    skills = {}
    for r in rows:
        m = r._mapping
        skills[m["slug"]] = SkillState(
            habilidad_id      = m["habilidad_id"],
            slug              = m["slug"],
            xp_total          = m["xp_total"] or 0,
            nivel             = m["nivel"] or 0,
            confianza         = float(m["confianza"]),
            velocidad         = float(m["velocidad"]),
            tendencia_ia      = m["tendencia_ia"],
            aptitud_predicha  = float(m["aptitud_predicha"]) if m["aptitud_predicha"] else None,
            fuentes_evidencia = m["fuentes_evidencia"] if isinstance(m["fuentes_evidencia"], list)
                                else json.loads(m["fuentes_evidencia"]),
            ultimo_inferido_en = m["ultimo_inferido_en"],
        )

    return UserSkillProfile(
        usuario_id=usuario_id,
        skills=skills,
        onboarding_completado=bool(onboarding),
    )


def upsert_skill(usuario_id: int, habilidad_id: int, updates: dict):
    """
    Insert or update one skill row with TSG fields.
    updates keys: xp_total, nivel, confianza, velocidad,
                  tendencia_ia, aptitud_predicha, fuentes_evidencia (list)
    """
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO habilidades_usuario
              (usuario_id, habilidad_id, xp_total, nivel,
               confianza, velocidad, tendencia_ia,
               aptitud_predicha, fuentes_evidencia, ultimo_inferido_en)
            VALUES
              (:uid, :hid, :xp, :nivel,
               :confianza, :velocidad, :tendencia,
               :aptitud, CAST(:fuentes AS jsonb), now())
            ON CONFLICT ON CONSTRAINT uq_habilidades_usuario_uid_hid DO UPDATE SET
              xp_total           = EXCLUDED.xp_total,
              nivel              = EXCLUDED.nivel,
              confianza          = EXCLUDED.confianza,
              velocidad          = EXCLUDED.velocidad,
              tendencia_ia       = EXCLUDED.tendencia_ia,
              aptitud_predicha   = EXCLUDED.aptitud_predicha,
              fuentes_evidencia  = EXCLUDED.fuentes_evidencia,
              ultimo_inferido_en = now()
        """), {
            "uid":       usuario_id,
            "hid":       habilidad_id,
            "xp":        updates.get("xp_total", 0),
            "nivel":     updates.get("nivel", 0),
            "confianza": updates.get("confianza", 0.0),
            "velocidad": updates.get("velocidad", 0.0),
            "tendencia": updates.get("tendencia_ia", "unknown"),
            "aptitud":   updates.get("aptitud_predicha"),
            "fuentes":   json.dumps(updates.get("fuentes_evidencia", [])),
        })


# ──────────────────────────────────────────────
# Onboarding
# ──────────────────────────────────────────────

def save_onboarding_session(usuario_id: int, respuestas: dict,
                            skills_inferidas: dict, confianza: float):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO sesiones_onboarding_habilidades
              (usuario_id, respuestas, habilidades_inferidas, confianza_global)
            VALUES
              (:uid, CAST(:resp AS jsonb), CAST(:skills AS jsonb), :conf)
        """), {
            "uid":    usuario_id,
            "resp":   json.dumps(respuestas),
            "skills": json.dumps(skills_inferidas),
            "conf":   confianza,
        })
        # Mark onboarding complete on the main user row
        conn.execute(text("""
            UPDATE usuarios SET onboarding_completado = true
            WHERE id = :uid
        """), {"uid": usuario_id})


# ──────────────────────────────────────────────
# Inference log
# ──────────────────────────────────────────────

def log_inference(result):
    """
    Accepts either an InferenceResult dataclass or a plain dict.
    Dict keys: usuario_id, tipo_fuente, referencia_id,
               habilidades_raw, confianza, tiempo_ms
    """
    if isinstance(result, dict):
        uid  = result["usuario_id"]
        tipo = result["tipo_fuente"]
        ref  = result.get("referencia_id")
        raw  = json.dumps(result.get("habilidades_raw", {}))
        conf = result.get("confianza", 0.5)
        ms   = result.get("tiempo_ms", 0)
    else:
        uid  = result.usuario_id
        tipo = result.tipo_fuente
        ref  = result.referencia_id
        raw  = json.dumps(result.skills_raw)
        conf = result.confianza
        ms   = result.tiempo_ms

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO inferencias_habilidades
              (usuario_id, tipo_fuente, referencia_id,
               habilidades_raw, confianza, modelo_version, tiempo_ms)
            VALUES
              (:uid, :tipo, :ref,
               CAST(:raw AS jsonb), :conf, 'v1.0', :ms)
        """), {
            "uid":  uid,
            "tipo": tipo,
            "ref":  ref,
            "raw":  raw,
            "conf": conf,
            "ms":   ms,
        })


# ──────────────────────────────────────────────
# Aptitude predictions
# ──────────────────────────────────────────────

def upsert_aptitude(usuario_id: int, habilidad_id: int,
                    aptitud: float, base_skills: dict, confianza: float):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO aptitudes_predichas
              (usuario_id, habilidad_id, aptitud, habilidades_base, confianza)
            VALUES
              (:uid, :hid, :apt, CAST(:base AS jsonb), :conf)
            ON CONFLICT ON CONSTRAINT uq_aptitud_usuario_habilidad DO UPDATE SET
              aptitud          = EXCLUDED.aptitud,
              habilidades_base = EXCLUDED.habilidades_base,
              confianza        = EXCLUDED.confianza,
              creado_en        = now()
        """), {
            "uid":  usuario_id,
            "hid":  habilidad_id,
            "apt":  aptitud,
            "base": json.dumps(base_skills),
            "conf": confianza,
        })


# ──────────────────────────────────────────────
# Task context (read from existing DELPHOS tables)
# ──────────────────────────────────────────────

def get_tarea_usuario(tarea_usuario_id: int) -> Optional[dict]:
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT tu.*, tm.duracion_estimada_minutos
            FROM tareas_usuario tu
            JOIN tareas_modulo tm ON tm.id = tu.tarea_id
            WHERE tu.id = :id
        """), {"id": tarea_usuario_id}).fetchone()
    return dict(row._mapping) if row else None


def get_task_skill_weights(tarea_id: int) -> list[dict]:
    """Returns skills attached to a task with their weights."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT ht.habilidad_id, ht.peso, ht.xp_ganado,
                   hc.slug, hc.nombre
            FROM habilidades_tarea ht
            JOIN habilidades_catalogo hc ON hc.id = ht.habilidad_id
            WHERE ht.tarea_id = :tid
        """), {"tid": tarea_id}).fetchall()
    return [dict(r._mapping) for r in rows]
