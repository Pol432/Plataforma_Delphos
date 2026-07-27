"""
inference/api.py
----------------
Unified Temporal Skill Graph API.
This is the single entry point for all other DELPHOS systems.

Consumers:
    Wide&Deep Recommender   → get_skill_vector(user_id)
    Learning Path Optimizer → get_enriched_skills(user_id)
    Onboarding flow         → initialize_user(user_id, quiz_answers)
    Task completion hook    → process_task(user_id, tarea_id, text, time_s)
    Transcript import       → process_transcript(user_id, text)

Usage:
    from inference.api import tsg
    vector   = tsg.get_skill_vector(user_id)
    enriched = tsg.get_enriched_skills(user_id)
"""

from __future__ import annotations

import time
from typing import Optional

from db.repositories  import get_user_profile, load_skill_catalog
from inference.skill_updater import (
    update_from_task,
    update_from_quiz,
    update_from_transcript,
)
from skill_taxonomy import SKILL_NAMES, NUM_SKILLS, SKILL_DB_ID


# ── TemporalSkillGraph API class ───────────────────────────────────────────

class TemporalSkillGraph:
    """
    Main API object. Instantiate once and reuse (singleton via module-level `tsg`).
    All methods are safe to call from multiple threads.
    """

    # ── Reads ──────────────────────────────────────────────────────────────

    def get_skill_vector(self, user_id: int) -> dict[str, float]:
        """
        Returns a flat {slug: mastery_0_to_100} dict for all 200 skills.
        Skills the user has no evidence for are returned as 0.0.

        Designed for Wide&Deep Recommender input.
        Mastery is derived from xp_total / 10.
        """
        profile = get_user_profile(user_id)

        # Start with all 200 skills at 0
        vector: dict[str, float] = {slug: 0.0 for slug in SKILL_NAMES}

        for slug, skill in profile.skills.items():
            mastery = skill.xp_total / 10.0
            vector[slug] = round(min(mastery, 100.0), 2)

        return vector

    def get_enriched_skills(self, user_id: int) -> dict[str, dict]:
        """
        Returns full skill data for each skill with evidence.
        Includes mastery, confidence, velocity, trend, and predicted aptitude.

        Designed for Learning Path Optimizer input.
        Only returns skills with xp_total > 0 or a predicted aptitude.
        """
        profile = get_user_profile(user_id)
        enriched: dict[str, dict] = {}

        for slug, skill in profile.skills.items():
            mastery = skill.xp_total / 10.0
            if mastery <= 0 and skill.aptitud_predicha is None:
                continue

            enriched[slug] = {
                "mastery":           round(mastery, 2),
                "confidence":        round(skill.confianza, 4),
                "velocity":          round(skill.velocidad, 4),
                "trend":             skill.tendencia_ia,
                "predicted_aptitude": round(skill.aptitud_predicha, 2)
                                      if skill.aptitud_predicha else None,
                "evidence_count":    len(skill.fuentes_evidencia),
                "last_updated":      skill.ultimo_inferido_en.isoformat()
                                     if skill.ultimo_inferido_en else None,
            }

        return enriched

    def get_top_skills(
        self,
        user_id: int,
        n: int = 10,
        min_confidence: float = 0.0,
    ) -> list[dict]:
        """
        Returns the top-N skills by mastery, with optional confidence filter.
        Useful for profile cards and dashboards.
        """
        enriched = self.get_enriched_skills(user_id)
        filtered = [
            {"slug": slug, **data}
            for slug, data in enriched.items()
            if data["confidence"] >= min_confidence
        ]
        return sorted(filtered, key=lambda x: -x["mastery"])[:n]

    def get_skill_gaps(
        self,
        user_id: int,
        target_slugs: list[str],
    ) -> list[dict]:
        """
        For a list of target skills, returns the gap between
        current mastery and 100. Used by Learning Path Optimizer
        to prioritise which skills to develop next.
        """
        vector = self.get_skill_vector(user_id)
        gaps = []
        for slug in target_slugs:
            mastery = vector.get(slug, 0.0)
            gaps.append({
                "slug":    slug,
                "mastery": mastery,
                "gap":     round(100.0 - mastery, 2),
            })
        return sorted(gaps, key=lambda x: -x["gap"])

    def get_onboarding_status(self, user_id: int) -> dict:
        """Returns whether the user has completed onboarding."""
        profile = get_user_profile(user_id)
        skill_count = sum(
            1 for s in profile.skills.values() if s.xp_total > 0
        )
        return {
            "onboarding_completado": profile.onboarding_completado,
            "skills_with_evidence":  skill_count,
            "ready_for_recommender": skill_count >= 5,
        }

    # ── Writes ─────────────────────────────────────────────────────────────

    def initialize_user(
        self,
        user_id:      int,
        quiz_answers: dict[str, str],
    ) -> dict:
        """
        Process onboarding quiz and initialise the user's skill profile.
        Call once after the user completes the onboarding flow.

        Args:
            user_id:      DELPHOS usuarios.id
            quiz_answers: {"q1": "A", "q2": "C", ...}

        Returns:
            {"skills_initialized": N, "top_skills": [...], "elapsed_ms": N}
        """
        t0 = time.time()
        updated = update_from_quiz(user_id, quiz_answers)
        elapsed = int((time.time() - t0) * 1000)

        top = sorted(updated.items(), key=lambda x: -x[1])[:5]
        return {
            "skills_initialized": len(updated),
            "top_skills": [{"slug": s, "mastery": round(sc, 1)} for s, sc in top],
            "elapsed_ms": elapsed,
        }

    def process_task(
        self,
        user_id:         int,
        tarea_id:        int,
        submission_text: str,
        time_spent_s:    int = 0,
    ) -> dict:
        """
        Process a completed task submission and update skill profile.
        Call from the task completion webhook.

        Args:
            user_id:         DELPHOS usuarios.id
            tarea_id:        tareas_modulo.id
            submission_text: user's text answer / description
            time_spent_s:    seconds spent on the task

        Returns:
            {"skills_updated": N, "top_skills": [...], "elapsed_ms": N}
        """
        t0 = time.time()
        updated = update_from_task(user_id, tarea_id, submission_text, time_spent_s)
        elapsed = int((time.time() - t0) * 1000)

        top = sorted(updated.items(), key=lambda x: -x[1])[:5]
        return {
            "skills_updated": len(updated),
            "top_skills": [{"slug": s, "mastery": round(sc, 1)} for s, sc in top],
            "elapsed_ms": elapsed,
        }

    def process_transcript(
        self,
        user_id:         int,
        transcript_text: str,
    ) -> dict:
        """
        Extract skills from an academic transcript or CV text.

        Returns:
            {"skills_updated": N, "elapsed_ms": N}
        """
        t0 = time.time()
        updated = update_from_transcript(user_id, transcript_text)
        elapsed = int((time.time() - t0) * 1000)
        return {
            "skills_updated": len(updated),
            "elapsed_ms": elapsed,
        }


# ── Module-level singleton ─────────────────────────────────────────────────

tsg = TemporalSkillGraph()


# ── Smoke test ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from sqlalchemy import text
    from db.connection import engine

    # Get or create test user
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id FROM usuarios WHERE email='test@tsg.dev'")
        ).fetchone()

    if row is None:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO usuarios (email, nombre_completo)
                VALUES ('test@tsg.dev', 'Test TSG User')
                ON CONFLICT (email) DO NOTHING
            """))
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT id FROM usuarios WHERE email='test@tsg.dev'")
            ).fetchone()

    uid = row[0]
    print(f"✓ Using user_id={uid}\n")

    # ── Test 1: Onboarding status ──────────────────────────────────────────
    print("── Test 1: Onboarding status ─────────────────────")
    status = tsg.get_onboarding_status(uid)
    print(f"  {status}")

    # ── Test 2: Skill vector (Wide&Deep format) ────────────────────────────
    print("\n── Test 2: Skill vector (Wide&Deep) ──────────────")
    vector = tsg.get_skill_vector(uid)
    non_zero = {k: v for k, v in vector.items() if v > 0}
    print(f"  Total skills: {len(vector)}")
    print(f"  Skills with evidence: {len(non_zero)}")
    top3 = sorted(non_zero.items(), key=lambda x: -x[1])[:3]
    for slug, score in top3:
        print(f"    {slug}: {score}")

    # ── Test 3: Enriched skills (Learning Path format) ─────────────────────
    print("\n── Test 3: Enriched skills (Learning Path) ───────")
    enriched = tsg.get_enriched_skills(uid)
    print(f"  Skills with data: {len(enriched)}")
    if enriched:
        sample_slug = next(iter(enriched))
        print(f"  Sample ({sample_slug}):")
        for k, v in enriched[sample_slug].items():
            print(f"    {k}: {v}")

    # ── Test 4: Top skills ─────────────────────────────────────────────────
    print("\n── Test 4: Top 5 skills ──────────────────────────")
    top = tsg.get_top_skills(uid, n=5)
    for s in top:
        print(f"  {s['slug']}: mastery={s['mastery']} conf={s['confidence']}")

    # ── Test 5: Skill gaps ─────────────────────────────────────────────────
    print("\n── Test 5: Skill gaps ────────────────────────────")
    gaps = tsg.get_skill_gaps(uid, ["python", "machine_learning", "liderazgo"])
    for g in gaps:
        print(f"  {g['slug']}: mastery={g['mastery']} gap={g['gap']}")

    # ── Test 6: Process task ───────────────────────────────────────────────
    print("\n── Test 6: Process task ──────────────────────────")
    result = tsg.process_task(
        uid, tarea_id=1,
        submission_text=(
            "Construí un dashboard interactivo con React y Python FastAPI. "
            "El backend consume datos de PostgreSQL y los expone via REST API. "
            "Usé pandas para transformar los datos y Chart.js para visualizarlos."
        ),
        time_spent_s=1800,
    )
    print(f"  skills_updated: {result['skills_updated']}")
    print(f"  elapsed_ms: {result['elapsed_ms']}")
    print(f"  top_skills: {result['top_skills'][:3]}")

    print("\n✓ All API tests passed")
    print("\n── Integration summary ───────────────────────────")
    print("  Wide&Deep input  : tsg.get_skill_vector(user_id)  → 200-dim dict")
    print("  LPath input      : tsg.get_enriched_skills(user_id) → full metadata")
    print("  Onboarding hook  : tsg.initialize_user(user_id, answers)")
    print("  Task hook        : tsg.process_task(user_id, tarea_id, text)")
    print("  Transcript hook  : tsg.process_transcript(user_id, text)")
