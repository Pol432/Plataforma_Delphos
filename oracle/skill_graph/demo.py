"""
demo.py
-------
Interactive end-to-end demo of the Temporal Skill Graph.
Simulates a complete student journey: onboarding → tasks → profile.

Run:
    python demo.py
    python demo.py --user-id 5   (use existing user)
    python demo.py --reset        (clear user data first)
"""

import sys
import time
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from sqlalchemy import text
from db.connection import engine
from inference.api import tsg


def banner(title: str):
    w = 58
    print("\n" + "─" * w)
    print(f"  {title}")
    print("─" * w)


def progress_bar(mastery: float, width: int = 25) -> str:
    filled = int(mastery / 100 * width)
    return "█" * filled + "░" * (width - filled) + f"  {mastery:.1f}"


def get_or_create_demo_user() -> int:
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id FROM usuarios WHERE email='demo@tsg.dev'")
        ).fetchone()
    if row:
        return row[0]
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO usuarios (email, nombre_completo)
            VALUES ('demo@tsg.dev', 'Estudiante Demo')
            ON CONFLICT (email) DO NOTHING
        """))
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id FROM usuarios WHERE email='demo@tsg.dev'")
        ).fetchone()
    return row[0]


def reset_user(user_id: int):
    with engine.begin() as conn:
        conn.execute(text(
            "DELETE FROM habilidades_usuario WHERE usuario_id=:uid"
        ), {"uid": user_id})
        conn.execute(text(
            "DELETE FROM sesiones_onboarding_habilidades WHERE usuario_id=:uid"
        ), {"uid": user_id})
        conn.execute(text(
            "DELETE FROM inferencias_habilidades WHERE usuario_id=:uid"
        ), {"uid": user_id})
        conn.execute(text(
            "UPDATE usuarios SET onboarding_completado=false WHERE id=:uid"
        ), {"uid": user_id})
    print(f"  ↺  User {user_id} data reset")


def run_demo(user_id: int):
    print("\n" + "=" * 58)
    print("  TEMPORAL SKILL GRAPH — Live Demo")
    print("  DELPHOS Vocational Platform")
    print("=" * 58)
    print(f"\n  Simulating journey for user_id={user_id}")

    # ── Step 1: Onboarding ─────────────────────────────────────────────────
    banner("Step 1 of 5 — Onboarding Quiz")
    print("  Sofia, 16 years old, high school student.")
    print("  No prior tech experience. Taking the 15-question quiz...\n")

    # Sofia's profile: analytical + some creativity
    quiz_answers = {
        "q1": "C",   # Research approach → analytical
        "q2": "A",   # Pattern recognition
        "q3": "A",   # Critical thinking
        "q4": "C",   # Systematic explanation
        "q5": "A",   # Planning + delegation
        "q6": "A",   # Enjoys puzzles
        "q7": "C",   # Listens before deciding
        "q8": "A",   # Looks for patterns in data
        "q9": "A",   # Reads docs first
        "q10": "C",  # Writes everything down
        "q11": "A",  # Loves technical problems
        "q12": "A",  # Reviews work carefully
        "q13": "A",  # Wants to build systems
        "q14": "A",  # Analyses criticism objectively
        "q15": "A",  # Wants to understand how things work
    }

    result = tsg.initialize_user(user_id, quiz_answers)
    time.sleep(0.3)

    print(f"  Quiz complete in {result['elapsed_ms']}ms")
    print(f"  Skills initialised: {result['skills_initialized']}")
    print(f"\n  Sofia's initial profile:")
    top = tsg.get_top_skills(user_id, n=8, min_confidence=0.0)
    for s in top:
        print(f"    {s['slug']:<35} {progress_bar(s['mastery'])}")

    # ── Step 2: First task ─────────────────────────────────────────────────
    banner("Step 2 of 5 — First Task: Data Analysis")
    print("  Sofia completes her first simulation task at JPMorgan:\n")
    print('  "Analicé datos de transacciones financieras con Excel')
    print('   avanzado. Identifiqué patrones de gasto, calculé')
    print('   promedios y creé gráficos de tendencias mensuales."\n')

    result2 = tsg.process_task(
        user_id, tarea_id=1,
        submission_text=(
            "Analicé datos de transacciones financieras usando Excel avanzado. "
            "Organicé la base de datos, apliqué tablas dinámicas para agrupar "
            "por categoría, calculé estadísticas descriptivas y creé gráficos "
            "de tendencias mensuales para presentar al equipo."
        ),
        time_spent_s=2700,
    )
    print(f"  Task processed in {result2['elapsed_ms']}ms")
    print(f"  Skills updated: {result2['skills_updated']}")
    print(f"\n  Top skills after Task 1:")
    top2 = tsg.get_top_skills(user_id, n=6)
    for s in top2:
        print(f"    {s['slug']:<35} {progress_bar(s['mastery'])}")

    # ── Step 3: Second task ────────────────────────────────────────────────
    banner("Step 3 of 5 — Second Task: Python Scripting")
    print("  Two days later, Sofia completes a Python task:\n")

    result3 = tsg.process_task(
        user_id, tarea_id=2,
        submission_text=(
            "Escribí mi primer script en Python para automatizar el análisis "
            "de datos de ventas. Usé pandas para leer el CSV, limpié valores "
            "nulos, agrupé por región y generé un reporte con matplotlib. "
            "Fue un reto pero lo resolví paso a paso."
        ),
        time_spent_s=3600,
    )
    print(f"  Skills updated: {result3['skills_updated']}")
    print(f"\n  Profile evolution — new skills appearing:")
    top3 = tsg.get_top_skills(user_id, n=8)
    for s in top3:
        trend_icon = {"mejorando": "↑", "estable": "→", "declinando": "↓"}.get(
            tsg.get_enriched_skills(user_id).get(s["slug"], {}).get("trend", ""), "·"
        )
        print(f"    {trend_icon} {s['slug']:<33} {progress_bar(s['mastery'])}")

    # ── Step 4: Wide&Deep output ───────────────────────────────────────────
    banner("Step 4 of 5 — Output: Wide&Deep Recommender")
    print("  Skill vector sent to Wide&Deep (non-zero excerpt):\n")
    vector = tsg.get_skill_vector(user_id)
    non_zero = sorted(
        [(k, v) for k, v in vector.items() if v > 0],
        key=lambda x: -x[1]
    )
    print(f"  Total vector dimension: {len(vector)}")
    print(f"  Non-zero skills:        {len(non_zero)}")
    print(f"\n  Top entries:")
    for slug, score in non_zero[:8]:
        print(f"    '{slug}': {score:.1f}")
    print(f"    ... ({len(non_zero) - 8} more non-zero)")

    # ── Step 5: Learning Path output ──────────────────────────────────────
    banner("Step 5 of 5 — Output: Learning Path Optimizer")
    print("  Enriched profile for Learning Path Optimizer:\n")
    enriched = tsg.get_enriched_skills(user_id)
    print(f"  Skills with evidence: {len(enriched)}")

    print(f"\n  Skill detail sample:")
    for slug in ["analisis_datos", "python", "pensamiento_analitico"]:
        if slug in enriched:
            s = enriched[slug]
            print(f"\n    [{slug}]")
            print(f"      Mastery    : {s['mastery']:.1f} / 100")
            print(f"      Confidence : {s['confidence']:.2f}")
            print(f"      Velocity   : {s['velocity']:+.2f} pts/week")
            print(f"      Trend      : {s['trend']}")

    print(f"\n  Skill gap analysis (recommended next skills):")
    gaps = tsg.get_skill_gaps(user_id, [
        "python", "machine_learning", "sql", "visualizacion_datos",
        "estadistica", "analisis_datos"
    ])
    for g in gaps[:4]:
        print(f"    {g['slug']:<30} gap: {g['gap']:.1f}  (mastery: {g['mastery']:.1f})")

    # ── Final summary ──────────────────────────────────────────────────────
    print("\n" + "=" * 58)
    print("  Demo Complete — System Summary")
    print("=" * 58)
    status = tsg.get_onboarding_status(user_id)
    print(f"\n  User {user_id} after full journey:")
    print(f"    Onboarding complete  : {status['onboarding_completado']}")
    print(f"    Skills with evidence : {status['skills_with_evidence']}")
    print(f"    Ready for recommender: {status['ready_for_recommender']}")
    print(f"\n  Cold-start problem solved:")
    print(f"    → Started with 0 skills")
    print(f"    → After quiz + 2 tasks: {status['skills_with_evidence']} skills profiled")
    print(f"    → Wide&Deep receives a {len(vector)}-dim input vector")
    print(f"    → Learning Path has mastery + confidence + velocity per skill")
    print("\n  ✓ Temporal Skill Graph working end-to-end\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", type=int, default=None)
    parser.add_argument("--reset",   action="store_true",
                        help="Clear user data before running demo")
    args = parser.parse_args()

    uid = args.user_id or get_or_create_demo_user()

    if args.reset:
        reset_user(uid)

    run_demo(uid)
