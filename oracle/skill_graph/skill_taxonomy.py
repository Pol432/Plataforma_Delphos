"""
skill_taxonomy.py
-----------------
Single source of truth for skill ordering and grouping.

Loads from habilidades_catalogo at startup so the taxonomy
always reflects whatever is in the DB — no manual sync needed.

Usage:
    from skill_taxonomy import SKILL_INDEX, SKILL_NAMES, TAXONOMY

    idx = SKILL_INDEX["python"]       # → int (position in 200-dim vector)
    name = SKILL_NAMES[idx]           # → "python"
    group = TAXONOMY["tecnica"]       # → [slug, slug, ...]
"""

from db.repositories import load_skill_catalog

# ── Load once at import time ───────────────────────────────────────────────
_catalog = load_skill_catalog()   # [{"id", "slug", "nombre", "categoria"}, ...]

# Ordered list of slugs (position = vector index)
SKILL_NAMES: list[str] = [row["slug"] for row in _catalog]

# slug → vector index
SKILL_INDEX: dict[str, int] = {slug: i for i, slug in enumerate(SKILL_NAMES)}

# slug → DB id
SKILL_DB_ID: dict[str, int] = {row["slug"]: row["id"] for row in _catalog}

# DB id → slug
SKILL_SLUG_BY_ID: dict[int, str] = {row["id"]: row["slug"] for row in _catalog}

# categoria → [slugs]  (for grouping and transfer learning)
TAXONOMY: dict[str, list[str]] = {}
for row in _catalog:
    TAXONOMY.setdefault(row["categoria"], []).append(row["slug"])

# Total skill count — used as model output dimension
NUM_SKILLS: int = len(SKILL_NAMES)


# ── Transfer learning groups ───────────────────────────────────────────────
# Maps a foundational skill to the technical/creative skills it predicts.
# Used by aptitude_predictor.py.

APTITUDE_TRANSFER: dict[str, dict[str, float]] = {
    # If strong in analytical thinking → predict these technical skills
    "pensamiento_analitico": {
        "python": 0.80, "machine_learning": 0.75, "estadistica": 0.78,
        "analisis_datos": 0.82, "sql": 0.72, "deep_learning": 0.70,
        "evaluacion_modelos": 0.73, "series_temporales": 0.68,
    },
    "razonamiento_logico": {
        "python": 0.75, "java": 0.70, "cpp": 0.68, "sql": 0.72,
        "arquitectura_sistemas": 0.70, "diseno_bases_datos": 0.72,
    },
    "resolucion_problemas": {
        "python": 0.72, "rest_api": 0.65, "docker": 0.60,
        "ci_cd": 0.58, "pruebas_software": 0.68,
    },
    # If strong in creativity → predict these creative/design skills
    "creatividad": {
        "diseno_visual": 0.85, "diseno_ui": 0.80, "diseno_ux": 0.78,
        "diseno_grafico": 0.82, "ilustracion": 0.75, "branding": 0.73,
        "copywriting": 0.70, "redaccion_contenido": 0.68,
    },
    "design_thinking": {
        "diseno_ux": 0.88, "prototipado": 0.85, "wireframing": 0.83,
        "mapas_empatia": 0.82, "customer_journey": 0.80,
        "investigacion_usuarios": 0.78, "pruebas_usuario": 0.75,
    },
    # If strong in communication → predict content/presentation skills
    "comunicacion_escrita": {
        "copywriting": 0.82, "redaccion_contenido": 0.85,
        "blog_writing": 0.80, "seo_writing": 0.72,
        "documentacion_tecnica": 0.75, "escritura_creativa": 0.70,
    },
    "comunicacion_verbal": {
        "presentaciones": 0.85, "storytelling": 0.80,
        "ventas": 0.72, "coaching": 0.68, "facilitacion": 0.75,
    },
    # If strong in leadership → predict management/business skills
    "liderazgo": {
        "gestion_equipos": 0.88, "coaching": 0.80, "mentoring": 0.82,
        "gestion_cambio": 0.75, "planificacion_estrategica": 0.72,
        "gestion_stakeholders": 0.70,
    },
    # If strong in analytical + creativity → predict data viz & UX
    "atencion_al_detalle": {
        "aseguramiento_calidad": 0.80, "pruebas_software": 0.75,
        "automatizacion_qa": 0.70, "diseno_bases_datos": 0.65,
        "evaluacion_modelos": 0.68,
    },
}


# ── Helper functions ───────────────────────────────────────────────────────

def slug_to_index(slug: str) -> int | None:
    """Returns vector position for a slug, or None if not found."""
    return SKILL_INDEX.get(slug)


def index_to_slug(idx: int) -> str | None:
    """Returns slug for a vector position, or None if out of range."""
    if 0 <= idx < len(SKILL_NAMES):
        return SKILL_NAMES[idx]
    return None


def slugs_in_category(categoria: str) -> list[str]:
    """Returns all slugs belonging to a category."""
    return TAXONOMY.get(categoria, [])


def get_transfer_targets(slug: str) -> dict[str, float]:
    """
    Returns skills this slug can predict aptitude for,
    with transfer weights (0–1).
    """
    return APTITUDE_TRANSFER.get(slug, {})


def scores_to_vector(scores: dict[str, float]) -> list[float]:
    """
    Converts {slug: score} dict to ordered 200-dim list.
    Missing skills default to 0.0.
    """
    vec = [0.0] * NUM_SKILLS
    for slug, score in scores.items():
        idx = SKILL_INDEX.get(slug)
        if idx is not None:
            vec[idx] = float(score)
    return vec


def vector_to_scores(vec: list[float], threshold: float = 0.0) -> dict[str, float]:
    """
    Converts ordered 200-dim list back to {slug: score} dict.
    Filters out scores at or below threshold.
    """
    return {
        SKILL_NAMES[i]: vec[i]
        for i in range(len(vec))
        if vec[i] > threshold
    }


if __name__ == "__main__":
    print(f"✓ Loaded taxonomy: {NUM_SKILLS} skills")
    print(f"  Categories: {list(TAXONOMY.keys())}")
    for cat, slugs in TAXONOMY.items():
        print(f"  [{cat}]: {len(slugs)} skills")
    print(f"\n  Sample SKILL_INDEX: python={SKILL_INDEX.get('python')}, "
          f"liderazgo={SKILL_INDEX.get('liderazgo')}")
    print(f"\n  Transfer targets for 'creatividad':")
    for s, w in get_transfer_targets("creatividad").items():
        print(f"    {s}: {w}")
