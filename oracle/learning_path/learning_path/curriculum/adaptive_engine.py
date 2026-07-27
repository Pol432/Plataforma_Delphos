"""
adaptive_engine.py — Real-time path adaptation based on task performance.

Rules:
  score >= SKIP_THRESHOLD (85)  → skip next task, accelerated gain
  score  < REINFORCE_THRESHOLD (60) → insert refresher before next task
  60 <= score < 85              → normal progression

Also handles:
  - Phase completion detection
  - XP award calculation
  - Mastery update
"""

import sys
import os
import logging
from dataclasses import dataclass
from typing import Optional, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from learning_path.curriculum.task_schema import LearningPath, LearningPhase, TaskItem
from config import SKIP_THRESHOLD, REINFORCE_THRESHOLD

logger = logging.getLogger("lpo.adaptive_engine")


# ─────────────────────────────────────────────────────────────────────────────
#  Result type
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CompletionResult:
    action:        str           # 'normal' | 'saltar' | 'refuerzo'
    skill_gain:    float         # mastery points added
    xp_earned:     int           # XP for the DELPHOS gamification system
    message:       str           # user-facing feedback
    next_task:     Optional[TaskItem] = None
    phase_complete: bool = False


# ─────────────────────────────────────────────────────────────────────────────
#  Adaptive logic (pure, no DB)
# ─────────────────────────────────────────────────────────────────────────────

def _determine_action(score: float) -> str:
    if score >= SKIP_THRESHOLD:
        return "saltar"
    if score < REINFORCE_THRESHOLD:
        return "refuerzo"
    return "normal"


def _adjusted_gain(base_gain: float, score: float, action: str) -> float:
    """Adjust skill gain based on performance."""
    if action == "saltar":
        return round(base_gain * 1.2, 2)   # excel → 20% bonus
    if action == "refuerzo":
        return round(base_gain * 0.5, 2)   # struggle → half gain
    return base_gain


def _calculate_xp(score: float, duration_minutes: int) -> int:
    """
    XP = base score reward + time bonus.
    Scales 0–60 XP based on performance, +10 for completing quickly.
    """
    base = int(score * 0.5)                     # 0–50 XP
    time_bonus = 10 if duration_minutes <= 30 else 0
    return base + time_bonus


def _build_message(action: str, score: float, skill_name: str, gain: float) -> str:
    if action == "saltar":
        return (f"Excellent work! {score:.0f}/100 on {skill_name}. "
                f"You're ahead — skipping to the next challenge. +{gain:.1f} mastery points!")
    if action == "refuerzo":
        return (f"Good effort! {score:.0f}/100 on {skill_name}. "
                f"Let's reinforce this topic before moving on. +{gain:.1f} mastery points.")
    return (f"Nice! {score:.0f}/100 on {skill_name}. "
            f"Progressing as planned. +{gain:.1f} mastery points.")


# ─────────────────────────────────────────────────────────────────────────────
#  Handle task completion (in-memory path)
# ─────────────────────────────────────────────────────────────────────────────

def handle_task_completion(
    path:             LearningPath,
    completed_task:   TaskItem,
    score:            float,        # 0–100
    time_spent_min:   int,
    user_skills:      Dict[int, float],
) -> CompletionResult:
    """
    Process a completed task and update the in-memory LearningPath.

    Returns a CompletionResult with the adaptive action, message, and next task.
    """
    action     = _determine_action(score)
    gain       = _adjusted_gain(completed_task.skill_gain, score, action)
    xp         = _calculate_xp(score, time_spent_min)
    message    = _build_message(action, score, completed_task.skill_name
                                if hasattr(completed_task, "skill_name")
                                else f"skill {completed_task.skill_id}", gain)

    # Update in-memory mastery
    prev = user_skills.get(completed_task.skill_id, 0.0)
    user_skills[completed_task.skill_id] = min(100.0, prev + gain)

    # Find the current phase
    current_phase = next(
        (ph for ph in path.phases if ph.skill_id == completed_task.skill_id and ph.unlocked),
        None,
    )

    phase_complete = False
    next_task: Optional[TaskItem] = None

    if current_phase:
        # Update phase mastery
        current_phase.current_mastery = user_skills[completed_task.skill_id]

        # Find the next pending task in this phase
        task_ids = [t.task_id for t in current_phase.tasks]
        if completed_task.task_id in task_ids:
            idx = task_ids.index(completed_task.task_id)

            if action == "saltar":
                # Skip the immediate next task
                skip_to = idx + 2
            else:
                skip_to = idx + 1

            if skip_to < len(current_phase.tasks):
                next_task = current_phase.tasks[skip_to]
            else:
                # Phase complete — check mastery
                if current_phase.current_mastery >= current_phase.target_mastery:
                    phase_complete = True
                    current_phase.unlocked = False   # mark done
                    # Unlock next phase
                    from learning_path.curriculum.curriculum_generator import unlock_next_phase
                    next_phase = unlock_next_phase(path, current_phase.order)
                    if next_phase and next_phase.tasks:
                        next_task = next_phase.tasks[0]

    logger.info("Task completed — score=%.0f action=%s gain=+%.1f xp=%d",
                score, action, gain, xp)

    return CompletionResult(
        action=action,
        skill_gain=gain,
        xp_earned=xp,
        message=message,
        next_task=next_task,
        phase_complete=phase_complete,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  DB version (updates PostgreSQL)
# ─────────────────────────────────────────────────────────────────────────────

def handle_task_completion_db(
    user_id:         int,
    microtarea_id:   int,
    fase_id:         int,
    score:           float,
    time_minutes:    int,
    conn,
) -> dict:
    """
    Persist task completion to PostgreSQL and update mastery + XP.
    Returns a dict compatible with CompletionResult fields.
    """
    from db import get_cursor

    with get_cursor(conn, dict_cursor=False) as cur:
        # 1. Get task metadata
        cur.execute(
            "SELECT ganancia_maestria, habilidad_id, titulo FROM microtareas_lpo WHERE id = %s",
            (microtarea_id,)
        )
        row = cur.fetchone()
        if not row:
            raise ValueError(f"microtarea_id {microtarea_id} not found")
        base_gain, habilidad_id, titulo = row

        action = _determine_action(score)
        gain   = _adjusted_gain(float(base_gain), score, action)
        xp     = _calculate_xp(score, time_minutes)

        # 2. Mark task complete
        cur.execute("""
            UPDATE progreso_microtarea_usuario
               SET estado='completada', puntaje=%s, tiempo_minutos=%s,
                   accion_adaptativa=%s, completada_en=NOW()
             WHERE usuario_id=%s AND microtarea_id=%s AND fase_id=%s
        """, (score, time_minutes, action, user_id, microtarea_id, fase_id))

        # 3. Update user mastery (INSERT OR increment)
        cur.execute("""
            INSERT INTO habilidades_usuario_maestria
                (usuario_id, habilidad_id, puntaje, fuente)
            VALUES (%s, %s, %s, 'lpo')
            ON CONFLICT (usuario_id, habilidad_id) DO UPDATE
                SET puntaje = LEAST(100, habilidades_usuario_maestria.puntaje + %s),
                    fuente  = 'lpo',
                    actualizado_en = NOW()
        """, (user_id, habilidad_id, gain, gain))

        # 4. Award XP in usuarios table
        cur.execute("""
            UPDATE usuarios
               SET xp_total = xp_total + %s,
                   fecha_ultima_actividad = NOW()
             WHERE id = %s
        """, (xp, user_id))

        # 5. Update phase progress counter
        cur.execute("""
            UPDATE fases_ruta_aprendizaje
               SET microtareas_completadas = microtareas_completadas + 1
             WHERE id = %s
        """, (fase_id,))

    logger.info("DB task completion — user=%d task=%d score=%.0f gain=+%.1f xp=%d",
                user_id, microtarea_id, score, gain, xp)

    return {
        "action":    action,
        "skill_gain": gain,
        "xp_earned":  xp,
        "message":   _build_message(action, score, str(titulo), gain),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point — simulate a few task completions
# ─────────────────────────────────────────────────────────────────────────────

def main():
    from learning_path.core.graph_schema import SkillGraph
    from learning_path.core.graph_converter import to_networkx
    from learning_path.careers.career_database import get_career_requirements, get_critical_skills
    from learning_path.engine.gap_analyzer import calculate_gaps
    from learning_path.engine.urgency_calculator import calculate_all_urgencies
    from learning_path.engine.efficiency_ranker import calculate_efficiency
    from learning_path.engine.priority_scorer import calculate_priorities
    from learning_path.curriculum.curriculum_generator import generate_curriculum
    from config import SKILL_GRAPH_PATH

    print("\nDELPHOS LPO — Adaptive Engine Simulation\n")

    graph        = SkillGraph.load(SKILL_GRAPH_PATH)
    nx_graph     = to_networkx(graph)
    career_slug  = "ux-designer"
    requirements = get_career_requirements(career_slug)
    critical_ids = get_critical_skills(career_slug)
    maria_skills = {71: 72.0, 5: 76.0, 1: 65.0, 3: 74.0, 15: 60.0}

    gaps       = calculate_gaps(maria_skills, requirements, graph, critical_ids)
    urgencies  = calculate_all_urgencies(gaps)
    efficiency = calculate_efficiency(graph, maria_skills, nx_graph)
    priorities = calculate_priorities(gaps, efficiency, urgencies)
    path       = generate_curriculum(priorities, maria_skills, graph)
    path.user_id     = "maria"
    path.career_slug = career_slug

    # Simulate 3 task completions
    scenarios = [
        (78, "Week 1 — Normal score"),
        (92, "Week 2 — Excellent! Should skip"),
        (48, "Week 3 — Struggled. Should reinforce"),
    ]

    phase = path.phases[0] if path.phases else None
    if not phase or not phase.tasks:
        print("  No tasks available for simulation")
        return

    task = phase.tasks[0]
    task.task_id = 1  # simulate an ID

    for score, label in scenarios:
        print(f"  {label}")
        result = handle_task_completion(path, task, score, 30, maria_skills)
        print(f"    Score  : {score}/100")
        print(f"    Action : {result.action}")
        print(f"    Message: {result.message}")
        print(f"    XP     : +{result.xp_earned}")
        print()


if __name__ == "__main__":
    main()
