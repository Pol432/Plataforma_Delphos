"""
curriculum_generator.py — Builds the ordered task curriculum from ranked priorities.

Takes the priority-scored skill list and assembles:
  1. LearningPhases (one per skill to learn)
  2. TaskItems within each phase (from task_database, difficulty-matched)
  3. LearningPath wrapping all phases

First phase is always unlocked; subsequent phases unlock when the previous
phase's target mastery is reached.
"""

import sys
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from learning_path.curriculum.task_schema import TaskItem, LearningPhase, LearningPath
from learning_path.engine.priority_scorer import PriorityScore

logger = logging.getLogger("lpo.curriculum_generator")

MAX_TASKS_PER_PHASE = 7
MIN_TASKS_PER_PHASE = 2


def _build_task_item(task_tuple: tuple, db_id: int = 0) -> TaskItem:
    """Convert a task_database tuple to a TaskItem dataclass."""
    skill_id, title, tipo, diff, mins, gain, url = task_tuple
    return TaskItem(
        task_id=db_id,
        skill_id=skill_id,
        title=title,
        task_type=tipo,
        difficulty=diff,
        estimated_minutes=mins,
        skill_gain=gain,
        resource_url=url,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Core generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_curriculum(
    priorities:   List[PriorityScore],
    user_skills:  Dict[int, float],
    graph,
    max_phases:   int = 8,
) -> LearningPath:
    """
    Build a LearningPath from a ranked priority list.

    Args:
        priorities  : output of priority_scorer.calculate_priorities()
        user_skills : {skill_id: current_mastery}
        graph       : SkillGraph (for skill metadata)
        max_phases  : cap on phases (default 8; keeps path under 90 days)

    Returns:
        LearningPath with ordered phases, first phase unlocked.
    """
    from learning_path.curriculum.task_database import get_tasks_for_skill

    # Only build phases for skills that have a gap AND have tasks available
    actionable = [p for p in priorities if p.gap > 0][:max_phases]

    phases: List[LearningPhase] = []

    for order, p in enumerate(actionable, start=1):
        current = user_skills.get(p.skill_id, 0.0)
        target  = current + p.gap   # = required mastery

        # Get tasks matched to current mastery level
        raw_tasks = get_tasks_for_skill(p.skill_id, current, limit=MAX_TASKS_PER_PHASE)

        if len(raw_tasks) < MIN_TASKS_PER_PHASE:
            # Not enough tasks — skip this skill (will be populated later)
            logger.warning("Skipping phase for %s — only %d tasks available",
                           p.skill_name, len(raw_tasks))
            continue

        task_items = [_build_task_item(t) for t in raw_tasks]

        phase = LearningPhase(
            phase_id=0,          # will be set after DB insert
            skill_id=p.skill_id,
            skill_name=p.skill_name,
            order=order,
            current_mastery=current,
            target_mastery=target,
            priority_score=p.priority,
            tasks=task_items,
            unlocked=(order == 1),  # only first phase starts unlocked
        )
        phases.append(phase)

    if not phases:
        logger.error("No phases generated — check task coverage for skills")
        return LearningPath(user_id="?", career_slug="?", phases=[])

    # Re-number phases in case some were skipped
    for i, ph in enumerate(phases, start=1):
        ph.order = i

    # Infer user_id from context (will be set by api.py)
    path = LearningPath(
        user_id="",
        career_slug="",
        phases=phases,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )

    logger.info("Curriculum generated: %d phases, %d total tasks, %.1f hrs",
                len(phases), path.total_tasks, path.total_estimated_hours)
    return path


def unlock_next_phase(path: LearningPath, completed_phase_order: int) -> Optional[LearningPhase]:
    """
    Unlock the phase after the completed one.
    Returns the newly unlocked phase, or None if already at the end.
    """
    for phase in path.phases:
        if phase.order == completed_phase_order + 1:
            phase.unlocked = True
            logger.info("Phase %d (%s) unlocked", phase.order, phase.skill_name)
            return phase
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  DB persistence
# ─────────────────────────────────────────────────────────────────────────────

def save_path_to_db(
    user_id:     int,
    career_slug: str,
    path:        LearningPath,
    conn,
) -> int:
    """
    Persist a generated LearningPath to PostgreSQL.
    Returns the ruta_id.
    """
    from db import get_cursor
    with get_cursor(conn, dict_cursor=False) as cur:
        # ── Get career DB id ───────────────────────────────────────────────
        cur.execute("SELECT id FROM carreras_catalogo WHERE slug = %s", (career_slug,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Career slug '{career_slug}' not found in DB")
        career_id = row[0]

        # ── Upsert ruta_aprendizaje ────────────────────────────────────────
        cur.execute("""
            INSERT INTO rutas_aprendizaje
                (usuario_id, carrera_id, total_fases, total_horas_estimadas,
                 fecha_objetivo, estado)
            VALUES (%s, %s, %s, %s, NOW() + INTERVAL '90 days', 'activa')
            ON CONFLICT (usuario_id, carrera_id) DO UPDATE
                SET estado               = 'activa',
                    total_fases          = EXCLUDED.total_fases,
                    total_horas_estimadas = EXCLUDED.total_horas_estimadas,
                    actualizado_en       = NOW()
            RETURNING id
        """, (user_id, career_id, len(path.phases), path.total_estimated_hours))
        ruta_id = cur.fetchone()[0]

        for phase in path.phases:
            # ── Insert/update phase ────────────────────────────────────────
            cur.execute("""
                INSERT INTO fases_ruta_aprendizaje
                    (ruta_id, habilidad_id, orden, maestria_inicial,
                     maestria_objetivo, puntuacion_prioridad,
                     estado, total_microtareas)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                ruta_id, phase.skill_id, phase.order,
                phase.current_mastery, phase.target_mastery,
                phase.priority_score,
                'activa' if phase.unlocked else 'bloqueada',
                len(phase.tasks),
            ))
            fase_id = cur.fetchone()[0]
            phase.phase_id = fase_id

            for task in phase.tasks:
                # ── Link task to phase ─────────────────────────────────────
                # task_id may be 0 if we're using in-memory tasks
                if task.task_id > 0:
                    cur.execute("""
                        INSERT INTO progreso_microtarea_usuario
                            (usuario_id, fase_id, microtarea_id, estado)
                        VALUES (%s, %s, %s, 'pendiente')
                        ON CONFLICT DO NOTHING
                    """, (user_id, fase_id, task.task_id))

    logger.info("Path saved to DB — ruta_id=%d, %d phases", ruta_id, len(path.phases))
    return ruta_id


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    from learning_path.core.graph_schema import SkillGraph
    from learning_path.core.graph_converter import to_networkx
    from learning_path.careers.career_database import get_career_requirements, get_critical_skills
    from learning_path.engine.gap_analyzer import calculate_gaps
    from learning_path.engine.urgency_calculator import calculate_all_urgencies
    from learning_path.engine.efficiency_ranker import calculate_efficiency
    from learning_path.engine.priority_scorer import calculate_priorities
    from config import SKILL_GRAPH_PATH

    print("\nDELPHOS LPO — Curriculum Generator\n")

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

    print(f"  Career : {career_slug}")
    print(f"  Phases : {len(path.phases)}")
    print(f"  Tasks  : {path.total_tasks}")
    print(f"  Hours  : {path.total_estimated_hours:.1f}")
    print(f"  Generated: {path.generated_at}\n")

    for phase in path.phases:
        lock = "🔓" if phase.unlocked else "🔒"
        print(f"  {lock} Phase {phase.order}: {phase.skill_name}")
        print(f"     Mastery : {phase.current_mastery:.0f} → {phase.target_mastery:.0f}")
        print(f"     Tasks   : {len(phase.tasks)}  (~{phase.estimated_total_time}min)")
        if phase.tasks:
            print(f"     First   : {phase.tasks[0].title[:55]}")
        print()


if __name__ == "__main__":
    main()
