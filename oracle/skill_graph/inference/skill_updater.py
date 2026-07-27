"""
inference/skill_updater.py
--------------------------
Merges skill signals from multiple sources into a user's DB profile
using Exponential Moving Average (EMA).

Main entry point:
    update_from_task(user_id, task_id, submission_text, time_spent_s)
    update_from_quiz(user_id, quiz_answers)
    update_from_transcript(user_id, transcript_text)

Fusion strategy (per skill):
    1. Run both text_inference and mindspore_model
    2. Fuse scores: 40% keyword signal + 60% model signal
    3. Apply EMA against current DB value
    4. Recalculate velocity and trend
    5. Write back to habilidades_usuario
"""

import time
import numpy as np
from datetime import datetime
from typing import Optional

from db.repositories  import (
    get_user_profile, upsert_skill, log_inference,
    get_task_skill_weights, save_onboarding_session,
)
from inference.text_inference  import infer_from_submission, extract_skills_from_text
from inference.mindspore_model import predict_skills, get_model
from inference.onboarding_quiz import score_quiz
from skill_taxonomy            import SKILL_INDEX, SKILL_DB_ID


# ── EMA configuration ──────────────────────────────────────────────────────
# α = how much we trust the NEW observation vs the existing value.
# α is higher when confidence is low (we know little → update faster).

def _alpha(current_confidence: float) -> float:
    """
    EMA weight for the new observation.
    confidence 0.0 → α 0.70  (big updates, we know nothing)
    confidence 0.5 → α 0.45
    confidence 0.9 → α 0.25  (small updates, we have strong evidence)
    """
    return 0.70 - (0.45 * current_confidence)


def _new_confidence(old_conf: float, source: str) -> float:
    """Increment confidence based on evidence quality."""
    increments = {
        "quiz":       0.15,
        "task":       0.12,
        "transcript": 0.08,
        "social":     0.06,
        "behavior":   0.04,
    }
    delta = increments.get(source, 0.05)
    return min(old_conf + delta, 0.95)


def _velocity(old_mastery: float, new_mastery: float,
               days_elapsed: float = 7.0) -> float:
    """Points gained per week."""
    if days_elapsed <= 0:
        return 0.0
    return (new_mastery - old_mastery) / days_elapsed * 7.0


def _trend(velocity: float) -> str:
    if velocity >  2.0: return "mejorando"
    if velocity < -2.0: return "declinando"
    return "estable"


# ── Fusion: combine keyword + model scores ─────────────────────────────────

def _fuse(
    keyword_scores: dict[str, float],
    model_scores:   dict[str, float],
    task_slugs:     Optional[list[str]] = None,
    kw_weight:      float = 0.40,
) -> dict[str, float]:
    """
    Fuse two signal sources into a single score per skill.
    Skills only in one source still contribute (treated as 0 in the other).
    Task-attached skills get a +15% boost on the fused score.
    """
    all_slugs = set(keyword_scores) | set(model_scores)
    fused: dict[str, float] = {}

    for slug in all_slugs:
        kw  = keyword_scores.get(slug, 0.0)
        mdl = model_scores.get(slug,   0.0)

        if kw > 0 and mdl > 0:
            score = kw_weight * kw + (1 - kw_weight) * mdl
        elif kw > 0:
            score = kw * 0.70        # keyword-only → lower confidence
        else:
            score = mdl * 0.85       # model-only   → slightly reduced

        fused[slug] = min(score, 100.0)

    # Task-slug boost
    if task_slugs:
        for slug in task_slugs:
            if slug in fused:
                fused[slug] = min(fused[slug] * 1.15, 100.0)

    return fused


# ── Core EMA update ────────────────────────────────────────────────────────

def _apply_ema_updates(
    user_id:        int,
    fused_scores:   dict[str, float],
    source:         str,
    min_score_gate: float = 8.0,
) -> dict[str, float]:
    """
    Load current profile, apply EMA for each skill in fused_scores,
    write back to DB.

    Returns:
        {slug: new_mastery} for all skills that were updated.
    """
    profile  = get_user_profile(user_id)
    # profile.skills is already {slug: SkillState}
    existing = {}
    for slug, skill in profile.skills.items():
        existing[slug] = {
            "xp_total":  skill.xp_total,
            "confianza": skill.confianza,
            "velocidad": skill.velocidad,
        }
    updated  = {}

    for slug, new_obs in fused_scores.items():
        if new_obs < min_score_gate:
            continue                  # filter noise

        habilidad_id = SKILL_DB_ID.get(slug)
        if habilidad_id is None:
            continue                  # unknown slug

        current = existing.get(slug, {})
        old_mastery    = float(current.get("xp_total", 0) or 0) / 10.0
        old_confidence = float(current.get("confianza", 0.0) or 0.0)
        old_velocity   = float(current.get("velocidad", 0.0) or 0.0)

        # EMA
        α           = _alpha(old_confidence)
        new_mastery = α * new_obs + (1 - α) * old_mastery
        new_mastery = max(0.0, min(new_mastery, 100.0))

        new_conf     = _new_confidence(old_confidence, source)
        vel          = _velocity(old_mastery, new_mastery)
        # Smooth velocity too
        smooth_vel   = 0.5 * vel + 0.5 * old_velocity
        trend        = _trend(smooth_vel)

        upsert_skill(user_id, habilidad_id, {
            "xp_total":      int(new_mastery * 10),
            "confianza":     round(new_conf, 4),
            "velocidad":     round(smooth_vel, 4),
            "tendencia_ia":  trend,
            "ultimo_inferido_en": datetime.utcnow(),
        })

        updated[slug] = new_mastery

    return updated


# ── Public entry points ────────────────────────────────────────────────────

def update_from_task(
    user_id:      int,
    tarea_id:     int,
    submission_text: str,
    time_spent_s: int = 0,
) -> dict[str, float]:
    """
    Process a task submission:
    1. Fetch task's skill weights from DB
    2. Run text_inference + mindspore_model
    3. Fuse, EMA-update, persist

    Returns updated {slug: mastery}.
    """
    t_start = time.time()

    # Task-associated skills (from habilidades_tarea)
    task_weights = get_task_skill_weights(tarea_id)   # [{slug, peso, xp_ganado}]
    task_slugs   = [w["slug"] for w in task_weights]

    # Signals
    kw_scores  = infer_from_submission(submission_text, task_slugs)
    mdl_scores = predict_skills(submission_text, threshold=5.0)

    # Fuse
    fused = _fuse(kw_scores, mdl_scores, task_slugs)

    # EMA update
    updated = _apply_ema_updates(user_id, fused, source="task")

    elapsed_ms = int((time.time() - t_start) * 1000)

    # Audit log
    log_inference({
        "usuario_id":      user_id,
        "tipo_fuente":     "task",
        "referencia_id":   tarea_id,
        "habilidades_raw": fused,
        "confianza":       0.70 if len(updated) > 3 else 0.40,
        "modelo_version":  "mindspore_v1",
        "tiempo_ms":       elapsed_ms,
    })

    print(f"  task→skills: {len(updated)} updated in {elapsed_ms}ms")
    return updated


def update_from_quiz(
    user_id:     int,
    quiz_answers: dict[str, str],
) -> dict[str, float]:
    """
    Process onboarding quiz results and initialise the user's skill profile.
    Also runs aptitude prediction for unlearned skills via skill_taxonomy.
    """
    t_start = time.time()

    # Score quiz
    quiz_scores = score_quiz(quiz_answers)

    # Aptitude prediction using transfer learning
    aptitude_scores = _predict_aptitudes(quiz_scores)

    # Merge: quiz scores for observed skills, aptitude for unlearned
    fused = {**aptitude_scores, **quiz_scores}   # quiz wins on conflict

    # EMA update (lower gate — quiz signals are coarser)
    updated = _apply_ema_updates(user_id, fused, source="quiz", min_score_gate=5.0)

    elapsed_ms = int((time.time() - t_start) * 1000)

    # Persist onboarding session
    save_onboarding_session(user_id, quiz_answers, updated,
                             confianza=0.30)

    log_inference({
        "usuario_id":      user_id,
        "tipo_fuente":     "quiz",
        "referencia_id":   None,
        "habilidades_raw": fused,
        "confianza":       0.30,
        "modelo_version":  "quiz_v1",
        "tiempo_ms":       elapsed_ms,
    })

    print(f"  quiz→skills: {len(updated)} initialised in {elapsed_ms}ms")
    return updated


def update_from_transcript(
    user_id:         int,
    transcript_text: str,
) -> dict[str, float]:
    """
    Process academic transcript or CV text.
    Uses keyword inference only (no model — text is too different from tasks).
    """
    t_start = time.time()

    kw_scores = extract_skills_from_text(transcript_text)
    # Transcripts → softer signals
    scaled = {slug: score * 0.75 for slug, score in kw_scores.items()}

    updated = _apply_ema_updates(user_id, scaled, source="transcript",
                                  min_score_gate=10.0)

    elapsed_ms = int((time.time() - t_start) * 1000)

    log_inference({
        "usuario_id":      user_id,
        "tipo_fuente":     "transcript",
        "referencia_id":   None,
        "habilidades_raw": scaled,
        "confianza":       0.20,
        "modelo_version":  "keyword_v1",
        "tiempo_ms":       elapsed_ms,
    })

    print(f"  transcript→skills: {len(updated)} updated in {elapsed_ms}ms")
    return updated


# ── Aptitude prediction ────────────────────────────────────────────────────

def _predict_aptitudes(quiz_scores: dict[str, float]) -> dict[str, float]:
    """
    Use transfer learning rules from skill_taxonomy to predict
    aptitude scores for skills the user hasn't yet demonstrated.
    These are stored as predicted_aptitude, not mastery.
    """
    from skill_taxonomy import get_transfer_targets

    aptitudes: dict[str, float] = {}
    rng = np.random.default_rng()

    for slug, score in quiz_scores.items():
        if score < 40:
            continue     # only transfer from reasonably strong signals
        targets = get_transfer_targets(slug)
        for target_slug, weight in targets.items():
            if target_slug in quiz_scores:
                continue   # user already has direct evidence, skip
            predicted = score * weight + rng.normal(0, 3)
            predicted = max(0.0, min(predicted, 85.0))
            # Keep best prediction if multiple sources point here
            aptitudes[target_slug] = max(aptitudes.get(target_slug, 0), predicted)

    # Aptitude scores are weaker than observed scores
    return {slug: score * 0.65 for slug, score in aptitudes.items()}


# ── Smoke test ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from db.connection import check_connection

    try:
        check_connection()
    except Exception as e:
        print(f"✗ DB not reachable: {e}")
        sys.exit(1)

    # Use user_id=1 if it exists, else skip DB writes
    from sqlalchemy import text
    from db.connection import engine

    with engine.connect() as conn:
        row = conn.execute(text("SELECT id FROM usuarios LIMIT 1")).fetchone()

    if row is None:
        print("⚠ No users in DB — creating test user")
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO usuarios (email, nombre_completo)
                VALUES ('test@tsg.dev', 'Test TSG User')
                ON CONFLICT (email) DO NOTHING
            """))
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT id FROM usuarios WHERE email='test@tsg.dev'")
            ).fetchone()

    uid = row[0]
    print(f"✓ Using user_id={uid}")

    # Test quiz update
    print("\n── Test 1: Quiz update ───────────────────────")
    quiz_ans = {
        "q1": "C", "q2": "A", "q3": "A", "q4": "C",
        "q5": "A", "q6": "A", "q7": "C", "q8": "A",
        "q9": "A", "q10": "C", "q11": "A", "q12": "A",
        "q13": "A", "q14": "A", "q15": "A",
    }
    quiz_updated = update_from_quiz(uid, quiz_ans)
    top = sorted(quiz_updated.items(), key=lambda x: -x[1])[:5]
    print(f"  Top 5 after quiz:")
    for s, sc in top:
        print(f"    {s}: {sc:.1f}")

    # Test task update
    print("\n── Test 2: Task submission update ───────────")
    submission = (
        "Analicé un dataset de clientes con Python y pandas. "
        "Construí un modelo de clustering con scikit-learn para "
        "segmentar clientes por comportamiento de compra. "
        "Visualicé los resultados con matplotlib y presenté los "
        "hallazgos al equipo de marketing."
    )
    task_updated = update_from_task(uid, tarea_id=1,
                                     submission_text=submission)
    top2 = sorted(task_updated.items(), key=lambda x: -x[1])[:5]
    print(f"  Top 5 after task:")
    for s, sc in top2:
        print(f"    {s}: {sc:.1f}")

    # Test transcript update
    print("\n── Test 3: Transcript update ────────────────")
    transcript = (
        "Matemáticas: A+. Inglés: B+. Computación: A. "
        "Participé en el club de robótica y gané el concurso "
        "de diseño de pósters del colegio."
    )
    tr_updated = update_from_transcript(uid, transcript)
    print(f"  Skills updated from transcript: {len(tr_updated)}")

    print("\n✓ skill_updater smoke test passed")
