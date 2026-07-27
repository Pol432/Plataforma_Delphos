"""
demo.py — Interactive demo: Maria wants to become a UX Designer.

Run:
    python learning_path/demo.py
    python scripts/lpo.py demo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning_path.api import generate_path, get_current_task, complete_task

# ── colours ──────────────────────────────────────────────────────────────────
G = "\033[92m"; Y = "\033[93m"; B = "\033[94m"; BOLD = "\033[1m"; R = "\033[0m"


def divider(char="─", width=58):
    print(f"  {char * width}")


def run_demo():
    print(f"\n{BOLD}{'='*60}{R}")
    print(f"{BOLD}  DELPHOS · Learning Path Optimizer — Live Demo{R}")
    print(f"{BOLD}{'='*60}{R}\n")

    # ── Scenario ─────────────────────────────────────────────────────────────
    print(f"  {BOLD}Scenario:{R} Maria (22) wants to become a UX Designer.\n")
    print(f"  {B}Maria's current skills:{R}")

    maria_skills = {
        71: 72.0,   # visual_design   (good)
        5:  76.0,   # creativity      (good)
        1:  65.0,   # analytical_thinking (okay)
        3:  74.0,   # communication   (good)
        15: 60.0,   # empathy         (okay)
    }
    skill_names = {
        71: "visual_design", 5: "creativity", 1: "analytical_thinking",
        3: "communication", 15: "empathy",
    }
    for sid, mastery in maria_skills.items():
        bar = "█" * int(mastery // 10) + "░" * (10 - int(mastery // 10))
        print(f"    {skill_names[sid]:<24} [{B}{bar}{R}] {mastery:.0f}/100")

    print(f"\n  Missing: ui_design, ux_design, user_research, prototyping, figma\n")

    # ── Generate path ─────────────────────────────────────────────────────────
    print(f"  {Y}⚙  Generating learning path...{R}")
    path = generate_path("maria", "ux-designer", maria_skills.copy())
    user_skills = maria_skills.copy()

    print(f"\n  {G}✓  Learning path created!{R}\n")
    print(f"  {BOLD}Summary:{R}")
    print(f"    Phases : {len(path.phases)}")
    print(f"    Tasks  : {path.total_tasks}")
    print(f"    Est.   : {path.total_estimated_hours:.1f} hours  "
          f"(~{path.total_estimated_hours/2:.0f} days at 2h/day)\n")

    divider()
    print(f"  {BOLD}Learning Plan:{R}\n")
    for phase in path.phases:
        lock  = f"{G}🔓{R}" if phase.unlocked else f"🔒"
        gap   = phase.target_mastery - phase.current_mastery
        print(f"  {lock}  Phase {phase.order}: {BOLD}{phase.skill_name}{R}")
        print(f"       Gap    : {phase.current_mastery:.0f} → {phase.target_mastery:.0f}  (+{gap:.0f} pts)")
        print(f"       Tasks  : {len(phase.tasks)}  (~{phase.estimated_total_time}min)")
        if phase.tasks:
            print(f"       First  : {phase.tasks[0].title[:52]}")
        print()

    # ── Simulate task completions ─────────────────────────────────────────────
    divider()
    print(f"\n  {BOLD}Simulating task completions:{R}\n")

    simulations = [
        (78, 30, "Week 1 — Maria scores well, normal progression"),
        (92, 25, "Week 2 — Maria excels! System skips next task"),
        (48, 45, "Week 3 — Maria struggles. Refresher inserted"),
        (88, 35, "Week 4 — Back on track, strong performance"),
    ]

    task = get_current_task(path)
    if not task:
        print("  No tasks available.")
        return

    for score, mins, label in simulations:
        print(f"  {B}→ {label}{R}")

        # Give the task a fake ID so the engine can track it
        task.task_id = getattr(task, "task_id", 0) or 1

        result = complete_task(path, task, score, mins, user_skills)

        score_bar = "█" * int(score // 10) + "░" * (10 - int(score // 10))
        print(f"    Score   : [{B}{score_bar}{R}] {score}/100")
        print(f"    Action  : {BOLD}{result.action}{R}")
        print(f"    Gain    : +{result.skill_gain:.1f} mastery pts")
        print(f"    XP      : +{result.xp_earned} ⭐")
        print(f"    Message : {result.message[:70]}")

        if result.phase_complete:
            print(f"    {G}🎉 Phase complete! Next phase unlocked.{R}")

        if result.next_task:
            print(f"    Next    : {result.next_task.title[:52]}")
            task = result.next_task
            task.task_id = task.task_id or 1
        print()

    # ── Final state ───────────────────────────────────────────────────────────
    divider()
    print(f"\n  {BOLD}Maria's updated skill scores:{R}\n")
    for sid, mastery in sorted(user_skills.items(),
                                key=lambda x: -x[1]):
        from learning_path.core.graph_schema import SkillGraph
        from config import SKILL_GRAPH_PATH
        g = SkillGraph.load(SKILL_GRAPH_PATH)
        name = g.nodes[sid].skill_name if sid in g.nodes else f"skill_{sid}"
        bar  = "█" * int(mastery // 10) + "░" * (10 - int(mastery // 10))
        print(f"    {name:<24} [{G}{bar}{R}] {mastery:.1f}/100")

    print(f"\n{BOLD}{G}{'='*60}{R}")
    print(f"{BOLD}{G}  Demo complete — LPO is working end-to-end!{R}")
    print(f"{BOLD}{G}{'='*60}{R}\n")


if __name__ == "__main__":
    run_demo()
