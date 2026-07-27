"""
api.py — Main public API for the Learning Path Optimizer.

Three core methods:
    generate_path(user_id, career_slug, user_skills) → LearningPath
    get_current_task(user_id, path)                  → TaskItem | None
    handle_task_completion(...)                      → CompletionResult
"""

import sys
import os
import logging
from typing import Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning_path.core.graph_schema import SkillGraph
from learning_path.core.graph_converter import to_networkx
from learning_path.careers.career_database import get_career_requirements, get_critical_skills
from learning_path.engine.gap_analyzer import calculate_gaps
from learning_path.engine.urgency_calculator import calculate_all_urgencies
from learning_path.engine.efficiency_ranker import calculate_efficiency
from learning_path.engine.priority_scorer import calculate_priorities
from learning_path.curriculum.curriculum_generator import generate_curriculum
from learning_path.curriculum.adaptive_engine import handle_task_completion, CompletionResult
from learning_path.curriculum.task_schema import LearningPath, TaskItem
from learning_path.monitoring import timer
from config import SKILL_GRAPH_PATH

logger = logging.getLogger("lpo.api")

# ─────────────────────────────────────────────────────────────────────────────
#  Module-level singletons (loaded once at startup)
# ─────────────────────────────────────────────────────────────────────────────

_graph    = None
_nx_graph = None

def _load_graph():
    global _graph, _nx_graph
    if _graph is None:
        _graph    = SkillGraph.load(SKILL_GRAPH_PATH)
        _nx_graph = to_networkx(_graph)
        logger.info("Skill graph loaded — %d nodes, %d edges",
                    len(_graph.nodes), len(_graph.edges))
    return _graph, _nx_graph


# ─────────────────────────────────────────────────────────────────────────────
#  API
# ─────────────────────────────────────────────────────────────────────────────

def generate_path(
    user_id:     str,
    career_slug: str,
    user_skills: Dict[int, float],   # {skill_id: mastery 0-100}
    max_phases:  int = 8,
) -> LearningPath:
    """
    Generate a personalized learning path.

    Args:
        user_id     : DELPHOS usuario.id (or username for dev)
        career_slug : e.g. 'ux-designer', 'ml-engineer'
        user_skills : current mastery scores from TSG or self-assessment
        max_phases  : cap on learning phases (default 8)

    Returns:
        LearningPath with ordered phases and task sequences.
    """
    with timer("generate_path"):
        graph, nx_graph = _load_graph()

        requirements = get_career_requirements(career_slug)
        critical_ids = get_critical_skills(career_slug)

        gaps       = calculate_gaps(user_skills, requirements, graph, critical_ids)
        urgencies  = calculate_all_urgencies(gaps)
        efficiency = calculate_efficiency(graph, user_skills, nx_graph)
        priorities = calculate_priorities(gaps, efficiency, urgencies)
        path       = generate_curriculum(priorities, user_skills, graph, max_phases)

        path.user_id     = str(user_id)
        path.career_slug = career_slug

    logger.info("Path generated for user=%s career=%s — %d phases, %.1fh",
                user_id, career_slug, len(path.phases), path.total_estimated_hours)
    return path


def get_current_task(path: LearningPath) -> Optional[TaskItem]:
    """
    Return the next task the user should work on.
    Returns None if the path is complete.
    """
    return path.get_first_task()


def complete_task(
    path:           LearningPath,
    task:           TaskItem,
    score:          float,        # 0–100
    time_spent_min: int,
    user_skills:    Dict[int, float],
) -> CompletionResult:
    """
    Record a task completion and get the adaptive response.

    Updates user_skills in-place (the dict you pass is mutated).
    Returns a CompletionResult with next task and feedback message.
    """
    with timer("complete_task"):
        result = handle_task_completion(path, task, score, time_spent_min, user_skills)

    return result


# ─────────────────────────────────────────────────────────────────────────────
#  TSG / Wide&Deep integration shims
# ─────────────────────────────────────────────────────────────────────────────

def generate_path_from_db(user_id: int, career_slug: str, conn) -> LearningPath:
    """
    Full integration: reads user skills from DB (TSG source of truth),
    generates path, and persists it back.
    """
    from learning_path.engine.gap_analyzer import get_user_skills_from_db
    from learning_path.curriculum.curriculum_generator import save_path_to_db

    user_skills = get_user_skills_from_db(user_id, conn)
    path        = generate_path(user_id, career_slug, user_skills)
    ruta_id     = save_path_to_db(user_id, career_slug, path, conn)
    logger.info("Path persisted — ruta_id=%d", ruta_id)
    return path
