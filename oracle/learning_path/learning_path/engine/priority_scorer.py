"""
priority_scorer.py — Combines gap, efficiency, and urgency into one score.

Formula:
    Priority = Gap × PageRank_Efficiency × Urgency × 1000

The ×1000 factor scales the small PageRank floats into readable numbers.
Higher priority → learned first.
"""

import sys
import os
import logging
from dataclasses import dataclass
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from learning_path.engine.gap_analyzer import SkillGap

logger = logging.getLogger("lpo.priority_scorer")

SCORE_SCALE = 1000.0   # makes scores human-readable


@dataclass
class PriorityScore:
    skill_id:    int
    skill_name:  str
    gap:         float
    efficiency:  float
    urgency:     float
    priority:    float   # Gap × Efficiency × Urgency × SCORE_SCALE
    is_critical: bool
    category:    str


# ─────────────────────────────────────────────────────────────────────────────
#  Scoring
# ─────────────────────────────────────────────────────────────────────────────

def calculate_priorities(
    gaps:        List[SkillGap],
    efficiency:  Dict[int, float],  # {skill_id: pagerank_score}
    urgencies:   Dict[int, float],  # {skill_id: urgency_multiplier}
) -> List[PriorityScore]:
    """
    Score every skill gap and return a ranked list (highest priority first).
    Skills with gap == 0 get priority 0 and appear at the bottom.
    """
    scores = []
    for g in gaps:
        eff = efficiency.get(g.skill_id, 0.0)
        urg = urgencies.get(g.skill_id, 0.0)
        pri = g.gap * eff * urg * SCORE_SCALE

        scores.append(PriorityScore(
            skill_id=g.skill_id,
            skill_name=g.skill_name,
            gap=g.gap,
            efficiency=eff,
            urgency=urg,
            priority=pri,
            is_critical=g.is_critical,
            category=g.category,
        ))

    scores.sort(key=lambda s: (-s.priority, -s.gap))
    logger.debug("Priority scoring: %d skills ranked, top=%s (%.2f)",
                 len(scores),
                 scores[0].skill_name if scores else "none",
                 scores[0].priority   if scores else 0.0)
    return scores


def top_skills_to_learn(
    priorities: List[PriorityScore],
    n: int = 5,
) -> List[PriorityScore]:
    """Return the top-N skills to learn next (gap > 0 only)."""
    return [p for p in priorities if p.gap > 0][:n]


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
    from config import SKILL_GRAPH_PATH

    print("\nDELPHOS LPO — Priority Scorer\n")

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

    print(f"  Career: {career_slug}\n")
    header = (f"  {'#':>3}  {'Skill':<28} {'Gap':>6} {'Eff':>8} "
              f"{'Urg':>6} {'Priority':>10}  Flags")
    print(header)
    print("  " + "─" * 76)

    for rank, p in enumerate(priorities, 1):
        flags = "🔴 CRITICAL" if p.is_critical and p.gap > 0 else ("✓ met" if p.gap == 0 else "")
        print(f"  {rank:>3}. {p.skill_name:<28} {p.gap:>6.1f} {p.efficiency:>8.5f} "
              f"{p.urgency:>6.2f} {p.priority:>10.3f}  {flags}")

    print(f"\n  → Start with: {priorities[0].skill_name} (priority: {priorities[0].priority:.2f})")
    print()


if __name__ == "__main__":
    main()
