"""
monitoring/metrics.py
---------------------
Lightweight metrics tracker for the Temporal Skill Graph.
Reads from inferencias_habilidades and habilidades_usuario to
produce a live system health snapshot.

Run:
    python monitoring/metrics.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta, UTC
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from db.connection import engine


def get_system_metrics() -> dict:
    """
    Returns a snapshot of TSG system health:
    - Total users with skill profiles
    - Total inferences run (by source type)
    - Average skills per user
    - Average update latency
    - Most inferred skills
    - Recent activity (last 24h)
    """
    with engine.connect() as conn:

        # Users with any skill data
        total_users = conn.execute(text("""
            SELECT COUNT(DISTINCT usuario_id) FROM habilidades_usuario
        """)).scalar() or 0

        # Users with onboarding complete
        onboarded = conn.execute(text("""
            SELECT COUNT(*) FROM usuarios WHERE onboarding_completado = true
        """)).scalar() or 0

        # Average skills per user (skills with xp_total > 0)
        avg_skills = conn.execute(text("""
            SELECT COALESCE(AVG(skill_count), 0)
            FROM (
                SELECT usuario_id, COUNT(*) AS skill_count
                FROM habilidades_usuario
                WHERE xp_total > 0
                GROUP BY usuario_id
            ) sub
        """)).scalar() or 0.0

        # Total inferences by source type
        inference_counts = conn.execute(text("""
            SELECT tipo_fuente, COUNT(*) AS cnt
            FROM inferencias_habilidades
            GROUP BY tipo_fuente
            ORDER BY cnt DESC
        """)).fetchall()

        # Average latency per source
        avg_latency = conn.execute(text("""
            SELECT tipo_fuente, ROUND(AVG(tiempo_ms)) AS avg_ms
            FROM inferencias_habilidades
            WHERE tiempo_ms IS NOT NULL
            GROUP BY tipo_fuente
        """)).fetchall()

        # Most commonly updated skills (top 10)
        top_skills = conn.execute(text("""
            SELECT hc.slug, COUNT(*) AS update_count,
                   ROUND(AVG(hu.xp_total / 10.0)::numeric, 1) AS avg_mastery
            FROM habilidades_usuario hu
            JOIN habilidades_catalogo hc ON hc.id = hu.habilidad_id
            WHERE hu.xp_total > 0
            GROUP BY hc.slug
            ORDER BY update_count DESC
            LIMIT 10
        """)).fetchall()

        # Activity in last 24 hours
        since = datetime.now(UTC) - timedelta(hours=24)
        recent_inferences = conn.execute(text("""
            SELECT COUNT(*) FROM inferencias_habilidades
            WHERE creado_en > :since
        """), {"since": since}).scalar() or 0

        recent_skill_updates = conn.execute(text("""
            SELECT COUNT(*) FROM habilidades_usuario
            WHERE ultimo_inferido_en > :since
        """), {"since": since}).scalar() or 0

        # Confidence distribution
        conf_dist = conn.execute(text("""
            SELECT
              COUNT(*) FILTER (WHERE confianza < 0.3)  AS low,
              COUNT(*) FILTER (WHERE confianza >= 0.3
                                 AND confianza < 0.7)  AS medium,
              COUNT(*) FILTER (WHERE confianza >= 0.7) AS high
            FROM habilidades_usuario
            WHERE xp_total > 0
        """)).fetchone()

    return {
        "snapshot_at": datetime.now(UTC).isoformat(),
        "users": {
            "with_skill_data":       total_users,
            "onboarding_complete":   onboarded,
            "avg_skills_per_user":   round(float(avg_skills), 1),
        },
        "inferences": {
            "by_source": {r.tipo_fuente: r.cnt for r in inference_counts},
            "total":     sum(r.cnt for r in inference_counts),
        },
        "latency_ms": {
            r.tipo_fuente: int(r.avg_ms) for r in avg_latency
        },
        "top_skills": [
            {"slug": r.slug, "updates": r.update_count,
             "avg_mastery": float(r.avg_mastery)}
            for r in top_skills
        ],
        "last_24h": {
            "inferences":    recent_inferences,
            "skill_updates": recent_skill_updates,
        },
        "confidence_distribution": {
            "low_under_30":    conf_dist.low    if conf_dist else 0,
            "medium_30_to_70": conf_dist.medium if conf_dist else 0,
            "high_over_70":    conf_dist.high   if conf_dist else 0,
        },
    }


def print_metrics(metrics: dict):
    print("=" * 55)
    print("  Temporal Skill Graph — System Metrics")
    print(f"  {metrics['snapshot_at']}")
    print("=" * 55)

    u = metrics["users"]
    print(f"\n  Users")
    print(f"    With skill data      : {u['with_skill_data']}")
    print(f"    Onboarding complete  : {u['onboarding_complete']}")
    print(f"    Avg skills per user  : {u['avg_skills_per_user']}")

    inf = metrics["inferences"]
    print(f"\n  Inferences (total: {inf['total']})")
    for source, count in inf["by_source"].items():
        lat = metrics["latency_ms"].get(source, "—")
        print(f"    {source:<15}: {count:>4}  (avg {lat}ms)")

    print(f"\n  Last 24 hours")
    print(f"    Inferences run       : {metrics['last_24h']['inferences']}")
    print(f"    Skill updates        : {metrics['last_24h']['skill_updates']}")

    cd = metrics["confidence_distribution"]
    total_conf = sum(cd.values()) or 1
    print(f"\n  Confidence distribution")
    print(f"    Low   (<0.30) : {cd['low_under_30']:>4}  "
          f"({cd['low_under_30']/total_conf*100:.0f}%)")
    print(f"    Medium (0.3–0.7): {cd['medium_30_to_70']:>3}  "
          f"({cd['medium_30_to_70']/total_conf*100:.0f}%)")
    print(f"    High  (>0.70) : {cd['high_over_70']:>4}  "
          f"({cd['high_over_70']/total_conf*100:.0f}%)")

    print(f"\n  Top 10 most-developed skills")
    for s in metrics["top_skills"]:
        bar = "█" * int(s["avg_mastery"] / 10)
        print(f"    {s['slug']:<35} {s['avg_mastery']:>5.1f}  {bar}")

    print()


if __name__ == "__main__":
    metrics = get_system_metrics()
    print_metrics(metrics)
    # Also save as JSON for external consumption
    out_path = Path(__file__).resolve().parents[1] / "logs" / "metrics.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(metrics, indent=2))
    print(f"  Saved to: {out_path}")
