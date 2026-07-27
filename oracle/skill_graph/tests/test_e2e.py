"""
tests/test_e2e.py
-----------------
End-to-end test: full user journey from onboarding through
multiple task submissions, verifying skill accumulation,
API outputs, and DB persistence at each step.

Run:
    python tests/test_e2e.py
"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from db.connection import engine, check_connection
from inference.api import tsg

# ── Helpers ────────────────────────────────────────────────────────────────

PASS = "✓"
FAIL = "✗"
results: list[tuple[str, bool, str]] = []

def check(name: str, condition: bool, detail: str = ""):
    symbol = PASS if condition else FAIL
    results.append((name, condition, detail))
    print(f"  {symbol} {name}" + (f" — {detail}" if detail else ""))
    return condition


def get_or_create_test_user(email: str = "e2e_test@tsg.dev") -> int:
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id FROM usuarios WHERE email=:e"), {"e": email}
        ).fetchone()
    if row:
        return row[0]
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO usuarios (email, nombre_completo)
            VALUES (:e, 'E2E Test User')
            ON CONFLICT (email) DO NOTHING
        """), {"e": email})
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id FROM usuarios WHERE email=:e"), {"e": email}
        ).fetchone()
    return row[0]


def cleanup_test_user(user_id: int):
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


# ── Test suites ────────────────────────────────────────────────────────────

def test_db_connection():
    print("\n[Suite 1] Database connectivity")
    try:
        check_connection()
        check("DB reachable", True)
    except Exception as e:
        check("DB reachable", False, str(e))


def test_onboarding(user_id: int):
    print("\n[Suite 2] Onboarding quiz")

    # Status before
    status_before = tsg.get_onboarding_status(user_id)
    check("Onboarding not yet complete",
          not status_before["onboarding_completado"])

    # Run onboarding
    answers = {
        "q1": "C", "q2": "A", "q3": "A", "q4": "C",
        "q5": "A", "q6": "A", "q7": "C", "q8": "A",
        "q9": "A", "q10": "C", "q11": "A", "q12": "A",
        "q13": "A", "q14": "A", "q15": "A",
    }
    result = tsg.initialize_user(user_id, answers)

    check("Skills initialized > 0",
          result["skills_initialized"] > 0,
          str(result["skills_initialized"]))
    check("At least 10 skills found",
          result["skills_initialized"] >= 10,
          str(result["skills_initialized"]))
    check("Response time < 2s",
          result["elapsed_ms"] < 2000,
          f"{result['elapsed_ms']}ms")

    # Status after
    status_after = tsg.get_onboarding_status(user_id)
    check("Onboarding marked complete",
          status_after["onboarding_completado"])
    check("Ready for recommender",
          status_after["ready_for_recommender"])

    return result


def test_skill_vector(user_id: int):
    print("\n[Suite 3] Wide&Deep skill vector")

    vector = tsg.get_skill_vector(user_id)

    check("Vector has exactly 200 skills", len(vector) == 200, str(len(vector)))
    check("All values are floats",
          all(isinstance(v, float) for v in vector.values()))
    check("All values in [0, 100]",
          all(0.0 <= v <= 100.0 for v in vector.values()))

    non_zero = {k: v for k, v in vector.items() if v > 0}
    check("At least 5 non-zero skills",
          len(non_zero) >= 5, str(len(non_zero)))

    return vector


def test_enriched_skills(user_id: int):
    print("\n[Suite 4] Enriched skills (Learning Path)")

    enriched = tsg.get_enriched_skills(user_id)
    check("Has enriched skills", len(enriched) > 0, str(len(enriched)))

    if enriched:
        sample = next(iter(enriched.values()))
        check("Has mastery field",       "mastery"    in sample)
        check("Has confidence field",    "confidence" in sample)
        check("Has velocity field",      "velocity"   in sample)
        check("Has trend field",         "trend"      in sample)
        check("Trend is valid string",
              sample["trend"] in ("mejorando", "estable", "declinando", "unknown"))

    return enriched


def test_task_processing(user_id: int):
    print("\n[Suite 5] Task submission processing")

    # Python/data task
    python_task = (
        "Desarrollé un script de análisis de datos con Python y pandas. "
        "Limpié el dataset, calculé estadísticas descriptivas y generé "
        "visualizaciones con matplotlib para presentar los hallazgos."
    )
    t0 = time.time()
    result = tsg.process_task(user_id, tarea_id=1,
                               submission_text=python_task,
                               time_spent_s=1800)
    elapsed = time.time() - t0

    check("Task processed without error", result["skills_updated"] >= 0)
    check("Skills updated > 0",
          result["skills_updated"] > 0, str(result["skills_updated"]))
    check("End-to-end latency < 5s",
          elapsed < 5.0, f"{elapsed:.2f}s")

    # Design task
    design_task = (
        "Diseñé wireframes y prototipos de alta fidelidad en Figma para "
        "una app de delivery. Conduje pruebas de usabilidad con 5 usuarios "
        "y refiné el diseño basándome en el feedback."
    )
    result2 = tsg.process_task(user_id, tarea_id=2,
                                submission_text=design_task,
                                time_spent_s=2400)
    check("Design task processed",
          result2["skills_updated"] > 0, str(result2["skills_updated"]))

    return result, result2


def test_skill_accumulation(user_id: int):
    print("\n[Suite 6] Skill accumulation over multiple tasks")

    vector_before = tsg.get_skill_vector(user_id)
    python_before = vector_before.get("python", 0.0)

    # Submit another Python task
    tsg.process_task(user_id, tarea_id=3,
                     submission_text=(
                         "Implementé una API REST con FastAPI y Python. "
                         "Usé SQLAlchemy para el ORM, pydantic para validación "
                         "y pytest para los tests. Documenté con Swagger."
                     ))

    vector_after = tsg.get_skill_vector(user_id)
    python_after = vector_after.get("python", 0.0)

    check("Python mastery increased after second task",
          python_after >= python_before,
          f"{python_before:.1f} → {python_after:.1f}")

    enriched = tsg.get_enriched_skills(user_id)
    if "python" in enriched:
        check("Python confidence > 0.1",
              enriched["python"]["confidence"] > 0.1,
              f"{enriched['python']['confidence']:.3f}")


def test_skill_gaps(user_id: int):
    print("\n[Suite 7] Skill gap analysis")

    gaps = tsg.get_skill_gaps(user_id,
                               ["python", "machine_learning", "liderazgo",
                                "diseno_ux", "estadistica"])
    check("Returns 5 gap entries",  len(gaps) == 5)
    check("Gaps sorted descending",
          all(gaps[i]["gap"] >= gaps[i+1]["gap"] for i in range(len(gaps)-1)))
    check("All gaps in [0, 100]",
          all(0.0 <= g["gap"] <= 100.0 for g in gaps))


def test_persistence(user_id: int):
    print("\n[Suite 8] Data persistence")

    # Reload profile fresh from DB
    from db.repositories import get_user_profile
    profile = get_user_profile(user_id)

    check("Profile loaded from DB",     profile is not None)
    check("User ID matches",            profile.usuario_id == user_id)
    check("Skills dict not empty",      len(profile.skills) > 0)
    check("Onboarding flag persisted",  profile.onboarding_completado is True)

    # Check inference log was written
    with engine.connect() as conn:
        count = conn.execute(text(
            "SELECT COUNT(*) FROM inferencias_habilidades WHERE usuario_id=:uid"
        ), {"uid": user_id}).scalar()
    check("Inference log has entries",  count > 0, f"{count} entries")


def test_cold_start_accuracy(user_id: int):
    """
    Soft accuracy check: after onboarding + 2 tasks, the top skills
    should include at least one of the expected analytical/python skills.
    """
    print("\n[Suite 9] Cold-start accuracy (soft check)")

    top = tsg.get_top_skills(user_id, n=10)
    top_slugs = {s["slug"] for s in top}

    expected_analytical = {"python", "analisis_datos", "pensamiento_analitico",
                            "pandas", "estadistica", "machine_learning",
                            "resolucion_problemas", "razonamiento_logico"}

    overlap = top_slugs & expected_analytical
    accuracy_ok = len(overlap) >= 2

    check("Top-10 contains ≥2 expected analytical skills",
          accuracy_ok,
          f"found: {overlap}")
    check("Cold-start threshold met (≥20% hit rate)",
          len(overlap) / len(expected_analytical) >= 0.20,
          f"{len(overlap)}/{len(expected_analytical)}")


# ── Runner ─────────────────────────────────────────────────────────────────

def run_all():
    print("=" * 58)
    print("  Temporal Skill Graph — End-to-End Test Suite")
    print("=" * 58)

    t_start = time.time()

    # Setup
    test_db_connection()
    user_id = get_or_create_test_user()
    cleanup_test_user(user_id)
    print(f"\n  Test user: id={user_id} (cleaned)")

    # Suites
    test_onboarding(user_id)
    test_skill_vector(user_id)
    test_enriched_skills(user_id)
    test_task_processing(user_id)
    test_skill_accumulation(user_id)
    test_skill_gaps(user_id)
    test_persistence(user_id)
    test_cold_start_accuracy(user_id)

    # Summary
    total   = len(results)
    passed  = sum(1 for _, ok, _ in results if ok)
    failed  = total - passed
    elapsed = time.time() - t_start

    print("\n" + "=" * 58)
    print(f"  Results: {passed}/{total} passed  |  {elapsed:.1f}s total")
    if failed:
        print(f"\n  Failed tests:")
        for name, ok, detail in results:
            if not ok:
                print(f"    {FAIL} {name}" + (f" — {detail}" if detail else ""))
    else:
        print("  ✓ ALL TESTS PASSED")
    print("=" * 58)

    return failed == 0


if __name__ == "__main__":
    ok = run_all()
    sys.exit(0 if ok else 1)
