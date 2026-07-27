"""
urgency_calculator.py — Computes urgency multipliers for skill gaps.

Urgency reflects how blocking a skill gap is right now:
  - Critical skill with a gap  → 1.0  (must fix to be career-ready)
  - Non-critical with large gap → 0.7  (important but not blocking)
  - Non-critical with small gap → 0.5  (nice-to-have improvement)
  - Already met (gap == 0)     → 0.0  (skip entirely)

The urgency score is multiplied into the final priority formula:
    Priority = Gap × PageRank_Efficiency × Urgency
"""

import sys
import os
import logging
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from learning_path.engine.gap_analyzer import SkillGap

logger = logging.getLogger("lpo.urgency_calculator")


# ─────────────────────────────────────────────────────────────────────────────
#  Urgency thresholds (tunable via config)
# ─────────────────────────────────────────────────────────────────────────────

URGENCY_CRITICAL          = 1.0   # Critical skill, gap > 0
URGENCY_LARGE_GAP         = 0.75  # Non-critical, gap > LARGE_GAP_THRESHOLD
URGENCY_MEDIUM_GAP        = 0.50  # Non-critical, gap > MEDIUM_GAP_THRESHOLD
URGENCY_SMALL_GAP         = 0.30  # Non-critical, any gap > 0
URGENCY_MET               = 0.0   # No gap

LARGE_GAP_THRESHOLD  = 30.0  # gap points considered "large"
MEDIUM_GAP_THRESHOLD = 15.0  # gap points considered "medium"


def calculate_urgency(gap: SkillGap) -> float:
    """
    Return a 0.0–1.0 urgency multiplier for a single skill gap.
    """
    if gap.gap <= 0:
        return URGENCY_MET

    if gap.is_critical:
        return URGENCY_CRITICAL

    if gap.gap >= LARGE_GAP_THRESHOLD:
        return URGENCY_LARGE_GAP

    if gap.gap >= MEDIUM_GAP_THRESHOLD:
        return URGENCY_MEDIUM_GAP

    return URGENCY_SMALL_GAP


def calculate_all_urgencies(gaps: List[SkillGap]) -> Dict[int, float]:
    """
    Return {skill_id: urgency_score} for all gaps.
    Only skills with gap > 0 have urgency > 0.
    """
    return {g.skill_id: calculate_urgency(g) for g in gaps}


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    from learning_path.core.graph_schema import SkillGraph
    from learning_path.careers.career_database import get_career_requirements, get_critical_skills
    from learning_path.engine.gap_analyzer import calculate_gaps
    from config import SKILL_GRAPH_PATH

    print("\nDELPHOS LPO — Urgency Calculator\n")

    graph        = SkillGraph.load(SKILL_GRAPH_PATH)
    career_slug  = "ux-designer"
    requirements = get_career_requirements(career_slug)
    critical_ids = get_critical_skills(career_slug)

    maria_skills = {71: 72.0, 5: 76.0, 1: 65.0, 3: 74.0, 15: 60.0}
    gaps      = calculate_gaps(maria_skills, requirements, graph, critical_ids)
    urgencies = calculate_all_urgencies(gaps)

    header = f"  {'Skill':<28} {'Gap':>6} {'Urgency':>8}  Label"
    print(header)
    print("  " + "─" * 58)
    for g in gaps:
        u     = urgencies[g.skill_id]
        label = ("CRITICAL" if g.is_critical and g.gap > 0
                 else ("large" if g.gap >= LARGE_GAP_THRESHOLD
                       else ("medium" if g.gap >= MEDIUM_GAP_THRESHOLD
                             else ("small" if g.gap > 0 else "met"))))
        print(f"  {g.skill_name:<28} {g.gap:>6.1f} {u:>8.2f}  {label}")
    print()


if __name__ == "__main__":
    main()
