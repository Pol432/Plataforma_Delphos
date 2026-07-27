"""
gap_analyzer.py — Calculates skill gaps between a user's current mastery
and a target career's requirements.

Gap = max(0, required_mastery - current_mastery)
A gap of 0 means the skill is already at or above the required level.
"""

import sys
import os
import logging
from typing import Dict, List
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
logger = logging.getLogger("lpo.gap_analyzer")


@dataclass
class SkillGap:
    skill_id:         int
    skill_name:       str
    current_mastery:  float   # 0–100
    required_mastery: float   # 0–100
    gap:              float   # required - current (clamped to 0)
    is_critical:      bool    # if True, career is blocked until gap is closed
    category:         str


# ─────────────────────────────────────────────────────────────────────────────
#  Core calculation
# ─────────────────────────────────────────────────────────────────────────────

def calculate_gaps(
    user_skills:  Dict[int, float],   # {skill_id: current_mastery}
    career_requirements: Dict[int, float],  # {skill_id: required_mastery}
    graph,                             # SkillGraph (for names + categories)
    critical_skills: List[int] = None, # skill_ids that are blocking
) -> List[SkillGap]:
    """
    Compute skill gaps for a user vs a target career.

    Returns a list of SkillGap objects sorted by gap size (largest first).
    Skills already met (gap == 0) are included with gap=0 so the full
    picture is available to the priority scorer.
    """
    if critical_skills is None:
        critical_skills = []

    gaps = []
    for skill_id, required in career_requirements.items():
        current = user_skills.get(skill_id, 0.0)
        gap = max(0.0, required - current)

        node = graph.nodes.get(skill_id)
        skill_name = node.skill_name if node else f"skill_{skill_id}"
        category   = node.category   if node else "unknown"

        gaps.append(SkillGap(
            skill_id=skill_id,
            skill_name=skill_name,
            current_mastery=current,
            required_mastery=required,
            gap=gap,
            is_critical=(skill_id in critical_skills),
            category=category,
        ))

    # Sort: critical with gap first, then by gap size descending
    gaps.sort(key=lambda g: (not (g.is_critical and g.gap > 0), -g.gap))
    logger.debug("Gap analysis: %d skills, %d with gaps",
                 len(gaps), sum(1 for g in gaps if g.gap > 0))
    return gaps


def gaps_only(gaps: List[SkillGap]) -> List[SkillGap]:
    """Return only skills that still have a gap > 0."""
    return [g for g in gaps if g.gap > 0]


def is_career_ready(gaps: List[SkillGap]) -> bool:
    """True if all critical skills have gap == 0."""
    return all(g.gap == 0 for g in gaps if g.is_critical)


def career_readiness_pct(gaps: List[SkillGap]) -> float:
    """Percentage of total gap points already closed (0–100)."""
    total_required = sum(g.required_mastery for g in gaps)
    if total_required == 0:
        return 100.0
    total_current = sum(min(g.current_mastery, g.required_mastery) for g in gaps)
    return round((total_current / total_required) * 100, 1)


# ─────────────────────────────────────────────────────────────────────────────
#  DB helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_user_skills_from_db(user_id: int, conn) -> Dict[int, float]:
    """
    Load a user's current skill mastery scores from habilidades_usuario_maestria.
    Returns {skill_id: mastery_score}.
    """
    from db import get_cursor
    with get_cursor(conn) as cur:
        cur.execute("""
            SELECT habilidad_id, puntaje
            FROM habilidades_usuario_maestria
            WHERE usuario_id = %s
        """, (user_id,))
        return {row["habilidad_id"]: float(row["puntaje"]) for row in cur.fetchall()}


def get_career_requirements_from_db(career_slug: str, conn) -> tuple:
    """
    Load career skill requirements from DB.
    Returns ({skill_id: required_mastery}, [critical_skill_ids]).
    """
    from db import get_cursor
    with get_cursor(conn) as cur:
        cur.execute("""
            SELECT hc.habilidad_id, hc.maestria_requerida, hc.es_critica
            FROM habilidades_carrera hc
            JOIN carreras_catalogo cc ON cc.id = hc.carrera_id
            WHERE cc.slug = %s
        """, (career_slug,))
        rows = cur.fetchall()

    requirements = {row["habilidad_id"]: float(row["maestria_requerida"]) for row in rows}
    critical     = [row["habilidad_id"] for row in rows if row["es_critica"]]
    return requirements, critical


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point / self-test
# ─────────────────────────────────────────────────────────────────────────────

def main():
    from learning_path.core.graph_schema import SkillGraph
    from learning_path.careers.career_database import get_career_requirements, get_critical_skills
    from config import SKILL_GRAPH_PATH

    print("\nDELPHOS LPO — Gap Analyzer\n")

    graph = SkillGraph.load(SKILL_GRAPH_PATH)

    # Simulate Maria: wants to be a UX Designer
    career_slug = "ux-designer"
    requirements  = get_career_requirements(career_slug)
    critical_ids  = get_critical_skills(career_slug)

    maria_skills = {
        71: 72.0,   # visual_design (good)
        5:  76.0,   # creativity (good)
        1:  65.0,   # analytical_thinking (okay)
        3:  74.0,   # communication (good)
        15: 60.0,   # empathy (okay)
        # Missing: ux_design, user_research, prototyping, ui_design, figma
    }

    gaps = calculate_gaps(maria_skills, requirements, graph, critical_ids)

    print(f"  Career   : {career_slug}")
    print(f"  Readiness: {career_readiness_pct(gaps):.1f}%")
    print(f"  Ready?   : {is_career_ready(gaps)}\n")

    header = f"  {'Skill':<28} {'Current':>8} {'Required':>9} {'Gap':>6} {'Critical':>9}"
    print(header)
    print("  " + "─" * 64)
    for g in gaps:
        crit = "🔴 YES" if g.is_critical and g.gap > 0 else ("✓" if g.gap == 0 else "")
        print(f"  {g.skill_name:<28} {g.current_mastery:>8.1f} {g.required_mastery:>9.1f} "
              f"{g.gap:>6.1f} {crit:>9}")
    print()


if __name__ == "__main__":
    main()
