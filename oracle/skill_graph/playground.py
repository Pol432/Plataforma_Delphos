"""
playground.py — Manual TSG testing with your own data.
Run: python playground.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from inference.api import tsg
from sqlalchemy import text
from db.connection import engine

# ── Create or get your test user ──────────────────────────────────────────
EMAIL = "pol@test.dev"   # change to whatever you want

with engine.connect() as conn:
    row = conn.execute(text("SELECT id FROM usuarios WHERE email=:e"), {"e": EMAIL}).fetchone()

if not row:
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO usuarios (email, nombre_completo)
            VALUES (:e, 'Pol Test') ON CONFLICT (email) DO NOTHING
        """), {"e": EMAIL})
    with engine.connect() as conn:
        row = conn.execute(text("SELECT id FROM usuarios WHERE email=:e"), {"e": EMAIL}).fetchone()

uid = row[0]
print(f"User id: {uid}")

# ── 1. Test the quiz with your own answers ─────────────────────────────────
# Change any answer to A/B/C/D and re-run to see how the profile changes
MY_QUIZ = {
    "q1": "A",   # How do you start organizing an event?
    "q2": "A",   # New math problem approach?
    "q3": "A",   # You find an error in submitted work?
    "q4": "A",   # Explain a hard topic to a beginner?
    "q5": "A",   # Project with huge scope in 3 days?
    "q6": "A",   # Favourite free time activity?
    "q7": "A",   # Your role in team conflict?
    "q8": "A",   # Given a dataset, what do you do?
    "q9": "A",   # How do you prefer to learn?
    "q10": "A",  # Preparing a presentation?
    "q11": "A",  # Which problem satisfies you most?
    "q12": "A",  # After finishing a task?
    "q13": "A",  # Choose a project for next month?
    "q14": "A",  # How do you react to criticism?
    "q15": "A",  # Which phrase describes you best?
}

print("\n── Quiz results ──────────────────────────────────────")
result = tsg.initialize_user(uid, MY_QUIZ)
print(f"Skills initialised: {result['skills_initialized']}")
for s in result["top_skills"]:
    print(f"  {s['slug']}: {s['mastery']}")

# ── 2. Test with your own text submission ──────────────────────────────────
MY_TEXT = """
Write here anything that describes work you've done:
a project, a task, skills you've used, something you built.
The more specific the better.
"""

print("\n── Text inference ────────────────────────────────────")
result2 = tsg.process_task(uid, tarea_id=999, submission_text=MY_TEXT)
print(f"Skills updated: {result2['skills_updated']}")
for s in result2["top_skills"]:
    print(f"  {s['slug']}: {s['mastery']}")

# ── 3. See your full profile ───────────────────────────────────────────────
print("\n── Your skill profile ────────────────────────────────")
top = tsg.get_top_skills(uid, n=15)
for s in top:
    bar = "█" * int(s["mastery"] / 10)
    print(f"  {s['slug']:<35} {s['mastery']:>5.1f}  {bar}")

# ── 4. See what Wide&Deep would receive ───────────────────────────────────
vector = tsg.get_skill_vector(uid)
non_zero = [(k, v) for k, v in vector.items() if v > 0]
print(f"\n── Wide&Deep vector: {len(non_zero)} non-zero out of 200 ──")


"""
psql postgresql://pol:delphos_dev@localhost:5432/delphos \
  -c "DELETE FROM habilidades_usuario WHERE usuario_id=(SELECT id FROM usuarios WHERE email='pol@test.dev')"
"""
