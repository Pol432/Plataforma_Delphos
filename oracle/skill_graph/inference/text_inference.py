"""
inference/text_inference.py
---------------------------
Extracts skill signals from free-form text using keyword matching.
Used as a fast, lightweight layer before the MindSpore model runs.

Two entry points:
    extract_skills_from_text(text)         → raw keyword hits
    infer_from_submission(text, task_slugs) → weighted by task context
"""

import re
from typing import Optional

# ── Keyword dictionary ─────────────────────────────────────────────────────
# Each entry: skill_slug → {keywords, weight, min_score, max_score}
# weight:     multiplier applied to hit count before scoring
# min_score:  floor if at least 1 keyword matched
# max_score:  ceiling for this source (keyword matching is weak evidence)

SKILL_KEYWORDS: dict[str, dict] = {

    # ── Técnicas: Lenguajes ────────────────────────────────────────────────
    "python": {
        "keywords": ["python", "django", "flask", "fastapi", "pandas", "numpy",
                     "pyplot", "jupyter", "pip", "virtualenv", "pep8"],
        "weight": 1.0, "min_score": 30, "max_score": 75,
    },
    "javascript": {
        "keywords": ["javascript", "js", "es6", "es2015", "node", "nodejs",
                     "npm", "webpack", "babel", "jquery"],
        "weight": 1.0, "min_score": 30, "max_score": 75,
    },
    "typescript": {
        "keywords": ["typescript", "ts", "tsx", "type-safe", "interfaces typescript"],
        "weight": 1.0, "min_score": 30, "max_score": 75,
    },
    "java": {
        "keywords": ["java", "spring", "springboot", "maven", "gradle", "jvm", "junit"],
        "weight": 1.0, "min_score": 30, "max_score": 75,
    },
    "cpp": {
        "keywords": ["c++", "cpp", "stl", "boost", "cmake", "g++", "clang"],
        "weight": 1.0, "min_score": 30, "max_score": 75,
    },
    "sql": {
        "keywords": ["sql", "query", "join", "select", "insert", "database",
                     "tabla", "consulta", "base de datos"],
        "weight": 1.0, "min_score": 25, "max_score": 70,
    },
    "r_lenguaje": {
        "keywords": ["rstudio", " r ", "tidyverse", "ggplot", "dplyr", "caret"],
        "weight": 1.0, "min_score": 30, "max_score": 75,
    },
    "go": {
        "keywords": ["golang", " go ", "goroutine", "go module"],
        "weight": 1.0, "min_score": 30, "max_score": 75,
    },
    "rust": {
        "keywords": ["rust", "cargo", "rustc", "ownership rust", "borrow checker"],
        "weight": 1.0, "min_score": 30, "max_score": 75,
    },
    "php": {
        "keywords": ["php", "laravel", "symfony", "wordpress", "composer php"],
        "weight": 0.9, "min_score": 25, "max_score": 70,
    },

    # ── Técnicas: Ciencia de Datos ─────────────────────────────────────────
    "machine_learning": {
        "keywords": ["machine learning", "aprendizaje automático", "ml", "clasificación",
                     "regresión", "modelo predictivo", "entrenamiento modelo",
                     "feature", "training data", "dataset"],
        "weight": 1.0, "min_score": 30, "max_score": 80,
    },
    "deep_learning": {
        "keywords": ["deep learning", "red neuronal", "neural network", "cnn", "rnn",
                     "lstm", "transformer", "backpropagation", "capas ocultas"],
        "weight": 1.0, "min_score": 30, "max_score": 80,
    },
    "estadistica": {
        "keywords": ["estadística", "statistics", "promedio", "desviación estándar",
                     "distribución", "correlación", "regresión", "hipótesis",
                     "p-value", "varianza", "media"],
        "weight": 0.9, "min_score": 25, "max_score": 75,
    },
    "analisis_datos": {
        "keywords": ["análisis de datos", "data analysis", "analicé", "exploré datos",
                     "insights", "procesé datos", "limpié datos", "data cleaning",
                     "exploración", "eda"],
        "weight": 1.0, "min_score": 28, "max_score": 78,
    },
    "visualizacion_datos": {
        "keywords": ["visualización", "gráfico", "dashboard", "chart", "plot",
                     "matplotlib", "seaborn", "plotly", "d3", "infografía",
                     "tableau", "power bi"],
        "weight": 1.0, "min_score": 28, "max_score": 78,
    },
    "nlp": {
        "keywords": ["nlp", "procesamiento lenguaje", "text mining", "tokenización",
                     "sentiment analysis", "análisis sentimientos", "bert",
                     "word2vec", "embeddings texto"],
        "weight": 1.0, "min_score": 30, "max_score": 80,
    },

    # ── Técnicas: Desarrollo Web ───────────────────────────────────────────
    "html_css": {
        "keywords": ["html", "css", "html5", "css3", "sass", "scss", "flexbox",
                     "grid css", "bootstrap", "tailwind"],
        "weight": 1.0, "min_score": 25, "max_score": 70,
    },
    "react": {
        "keywords": ["react", "reactjs", "jsx", "hooks", "usestate", "useeffect",
                     "redux", "next.js", "nextjs"],
        "weight": 1.0, "min_score": 30, "max_score": 75,
    },
    "vue": {
        "keywords": ["vue", "vuejs", "nuxt", "vuex", "vue router"],
        "weight": 1.0, "min_score": 30, "max_score": 75,
    },
    "rest_api": {
        "keywords": ["api rest", "rest api", "endpoint", "http", "json",
                     "get request", "post request", "fastapi", "swagger",
                     "openapi", "api design"],
        "weight": 1.0, "min_score": 28, "max_score": 72,
    },
    "django": {
        "keywords": ["django", "django rest", "drf", "django orm", "views django"],
        "weight": 1.0, "min_score": 30, "max_score": 75,
    },

    # ── Técnicas: Cloud y DevOps ───────────────────────────────────────────
    "docker": {
        "keywords": ["docker", "dockerfile", "contenedor", "container", "docker-compose",
                     "image docker", "docker hub"],
        "weight": 1.0, "min_score": 30, "max_score": 78,
    },
    "git": {
        "keywords": ["git", "github", "gitlab", "commit", "branch", "pull request",
                     "merge", "repositorio", "version control", "gitflow"],
        "weight": 0.9, "min_score": 22, "max_score": 68,
    },
    "aws": {
        "keywords": ["aws", "amazon web services", "ec2", "s3", "lambda aws",
                     "rds aws", "cloudwatch", "iam aws"],
        "weight": 1.0, "min_score": 30, "max_score": 78,
    },
    "ci_cd": {
        "keywords": ["ci/cd", "pipeline", "github actions", "jenkins", "travis",
                     "integración continua", "continuous integration",
                     "continuous deployment"],
        "weight": 1.0, "min_score": 30, "max_score": 78,
    },
    "linux": {
        "keywords": ["linux", "bash", "terminal", "shell script", "ubuntu",
                     "debian", "chmod", "ssh", "cron"],
        "weight": 0.9, "min_score": 22, "max_score": 70,
    },

    # ── Técnicas: Especializado ────────────────────────────────────────────
    "arquitectura_sistemas": {
        "keywords": ["arquitectura", "microservicios", "monolito", "system design",
                     "escalabilidad", "latencia", "arquitectura distribuida",
                     "cache", "load balancer"],
        "weight": 1.0, "min_score": 30, "max_score": 80,
    },
    "diseno_bases_datos": {
        "keywords": ["diseño base de datos", "schema", "normalización", "modelo er",
                     "entidad relación", "índices", "foreign key", "primary key",
                     "postgresql", "mysql"],
        "weight": 1.0, "min_score": 28, "max_score": 75,
    },
    "ciberseguridad": {
        "keywords": ["ciberseguridad", "seguridad web", "vulnerabilidad", "owasp",
                     "penetration testing", "cifrado", "autenticación", "jwt",
                     "oauth", "ssl", "https"],
        "weight": 1.0, "min_score": 30, "max_score": 78,
    },
    "seo": {
        "keywords": ["seo", "search engine", "posicionamiento web", "keywords",
                     "meta tags", "google search", "core web vitals",
                     "backlinks", "ranking"],
        "weight": 0.9, "min_score": 25, "max_score": 72,
    },

    # ── Herramientas ──────────────────────────────────────────────────────
    "pandas": {
        "keywords": ["pandas", "dataframe", "pd.", "groupby", "merge pandas",
                     "read_csv", "iloc", "loc pandas"],
        "weight": 1.0, "min_score": 30, "max_score": 80,
    },
    "figma": {
        "keywords": ["figma", "prototipo figma", "wireframe figma", "componentes figma",
                     "autolayout", "design system figma"],
        "weight": 1.0, "min_score": 28, "max_score": 78,
    },
    "tableau": {
        "keywords": ["tableau", "tableau desktop", "tableau public", "dashboard tableau"],
        "weight": 1.0, "min_score": 30, "max_score": 78,
    },

    # ── Creativas ─────────────────────────────────────────────────────────
    "diseno_visual": {
        "keywords": ["diseñé", "diseño visual", "composición", "diseño gráfico",
                     "visual design", "identidad visual", "assets visuales"],
        "weight": 1.0, "min_score": 28, "max_score": 78,
    },
    "diseno_ux": {
        "keywords": ["ux", "experiencia usuario", "user experience", "usabilidad",
                     "flujo usuario", "user flow", "investigación ux",
                     "pain points", "journey"],
        "weight": 1.0, "min_score": 30, "max_score": 80,
    },
    "diseno_ui": {
        "keywords": ["ui", "interfaz", "interface design", "componentes ui",
                     "design system", "botones", "tipografía ui", "spacing"],
        "weight": 1.0, "min_score": 28, "max_score": 78,
    },
    "branding": {
        "keywords": ["branding", "marca", "identidad de marca", "brand identity",
                     "manual de marca", "brand guidelines", "logo", "paleta"],
        "weight": 1.0, "min_score": 28, "max_score": 78,
    },
    "copywriting": {
        "keywords": ["copywriting", "copy", "redacción persuasiva", "call to action",
                     "cta", "headline", "copy publicitario"],
        "weight": 1.0, "min_score": 28, "max_score": 78,
    },
    "edicion_video": {
        "keywords": ["edición de video", "video editing", "premiere", "after effects",
                     "davinci", "corte video", "montaje", "motion graphics"],
        "weight": 1.0, "min_score": 28, "max_score": 78,
    },
    "prototipado": {
        "keywords": ["prototipo", "prototype", "mockup", "wireframe", "maqueta",
                     "prototipado rápido", "low fidelity", "high fidelity"],
        "weight": 1.0, "min_score": 28, "max_score": 78,
    },

    # ── Blandas (señales textuales) ───────────────────────────────────────
    "liderazgo": {
        "keywords": ["lideré", "dirigí", "coordiné", "fui líder", "team lead",
                     "liderazgo", "encabecé", "responsable del equipo", "liderar"],
        "weight": 0.9, "min_score": 25, "max_score": 72,
    },
    "gestion_equipos": {
        "keywords": ["gestión de equipo", "equipo de", "supervisé", "management",
                     "manejé equipo", "team management", "reportes directos"],
        "weight": 0.9, "min_score": 25, "max_score": 72,
    },
    "comunicacion_escrita": {
        "keywords": ["redacté", "escribí", "artículo", "blog", "informe",
                     "ensayo", "reporte", "documenté", "newsletter"],
        "weight": 0.8, "min_score": 20, "max_score": 68,
    },
    "presentaciones": {
        "keywords": ["presenté", "presentación", "expuse", "pitch", "keynote",
                     "diapositivas", "slides", "hablé ante"],
        "weight": 0.9, "min_score": 22, "max_score": 70,
    },
    "trabajo_equipo": {
        "keywords": ["trabajé en equipo", "colaboré", "junto a", "en conjunto",
                     "teamwork", "equipo multidisciplinario"],
        "weight": 0.8, "min_score": 18, "max_score": 65,
    },
    "resolucion_problemas": {
        "keywords": ["resolví", "solucioné", "identifiqué el problema", "depuré",
                     "debugging", "troubleshooting", "arreglé"],
        "weight": 0.9, "min_score": 22, "max_score": 70,
    },
    "investigacion_mercado": {
        "keywords": ["investigué el mercado", "análisis de mercado", "competencia",
                     "market research", "benchmarking", "tendencias del mercado"],
        "weight": 0.9, "min_score": 25, "max_score": 72,
    },
    "gestion_producto": {
        "keywords": ["product manager", "product owner", "roadmap", "backlog",
                     "gestión de producto", "user stories", "epics"],
        "weight": 1.0, "min_score": 28, "max_score": 78,
    },
    "marketing": {
        "keywords": ["marketing", "campaña", "conversión", "funnel", "lead",
                     "embudo", "estrategia marketing", "cpa", "roas"],
        "weight": 0.9, "min_score": 22, "max_score": 72,
    },
    "ventas": {
        "keywords": ["ventas", "venta", "cerré", "prospecto", "cliente",
                     "pipeline ventas", "cuota", "deal"],
        "weight": 0.9, "min_score": 22, "max_score": 70,
    },
}


# ── Core extraction function ───────────────────────────────────────────────

def extract_skills_from_text(text: str) -> dict[str, float]:
    """
    Scan text for skill keywords and return scored skill dict.

    Scoring per skill:
        raw = hit_count × weight × 15
        clamped to [min_score, max_score] if any hit, else 0

    Args:
        text: any free-form text (submission, bio, description)

    Returns:
        {slug: score_0_to_100}  — only skills with at least 1 hit
    """
    text_lower = text.lower()
    scores: dict[str, float] = {}

    for slug, config in SKILL_KEYWORDS.items():
        hit_count = 0
        for keyword in config["keywords"]:
            pattern = r"(?<!\w)" + re.escape(keyword.lower()) + r"(?!\w)"
            hit_count += len(re.findall(pattern, text_lower))

        if hit_count > 0:
            raw = min(hit_count * config["weight"] * 15, 100.0)
            # Apply min/max envelope
            score = max(config["min_score"], min(raw, config["max_score"]))
            scores[slug] = score

    return scores


# ── Implicit skill inference (transfer) ───────────────────────────────────

def infer_implicit_skills(explicit: dict[str, float]) -> dict[str, float]:
    """
    Infer soft/related skills from explicit keyword hits.
    These carry lower confidence than direct keyword matches.
    """
    implicit: dict[str, float] = {}

    # Programming → problem solving, logical reasoning
    prog_langs = {"python", "javascript", "java", "cpp", "typescript", "go", "rust"}
    prog_score = max((explicit.get(s, 0) for s in prog_langs), default=0)
    if prog_score > 0:
        implicit["resolucion_problemas"] = max(implicit.get("resolucion_problemas", 0),
                                               prog_score * 0.75)
        implicit["razonamiento_logico"]  = max(implicit.get("razonamiento_logico", 0),
                                               prog_score * 0.70)
        implicit["atencion_al_detalle"]  = max(implicit.get("atencion_al_detalle", 0),
                                               prog_score * 0.65)

    # Data science → analytical thinking
    ds_skills = {"machine_learning", "analisis_datos", "estadistica", "deep_learning"}
    ds_score = max((explicit.get(s, 0) for s in ds_skills), default=0)
    if ds_score > 0:
        implicit["pensamiento_analitico"] = max(implicit.get("pensamiento_analitico", 0),
                                                ds_score * 0.80)
        implicit["sintesis_informacion"]  = max(implicit.get("sintesis_informacion", 0),
                                                ds_score * 0.65)

    # Design → creativity, attention to detail
    design_skills = {"diseno_ux", "diseno_ui", "diseno_visual", "branding", "prototipado"}
    design_score = max((explicit.get(s, 0) for s in design_skills), default=0)
    if design_score > 0:
        implicit["creatividad"]          = max(implicit.get("creatividad", 0),
                                               design_score * 0.80)
        implicit["atencion_al_detalle"]  = max(implicit.get("atencion_al_detalle", 0),
                                               design_score * 0.70)

    # Leadership → communication
    if explicit.get("liderazgo", 0) > 0:
        implicit["comunicacion_verbal"]  = max(implicit.get("comunicacion_verbal", 0),
                                               explicit["liderazgo"] * 0.75)
        implicit["gestion_equipos"]      = max(implicit.get("gestion_equipos", 0),
                                               explicit["liderazgo"] * 0.70)

    # Git usage → collaborative workflow
    if explicit.get("git", 0) > 0:
        implicit["trabajo_equipo"]       = max(implicit.get("trabajo_equipo", 0),
                                               explicit["git"] * 0.60)
        implicit["colaboracion"]         = max(implicit.get("colaboracion", 0),
                                               explicit["git"] * 0.55)

    # Remove any slugs already in explicit (don't downgrade a stronger signal)
    return {k: v for k, v in implicit.items() if k not in explicit}


# ── Task-context weighted inference ───────────────────────────────────────

def infer_from_submission(
    text: str,
    task_skill_slugs: Optional[list[str]] = None,
) -> dict[str, float]:
    """
    Full inference pipeline for a task submission.

    1. Keyword extraction
    2. Implicit transfer inference
    3. Optional boost for skills already attached to the task
       (task_skill_slugs come from habilidades_tarea)

    Returns merged {slug: score} dict.
    """
    explicit  = extract_skills_from_text(text)
    implicit  = infer_implicit_skills(explicit)

    merged = {**implicit, **explicit}   # explicit wins on conflict

    # Boost skills that the task is designed to measure
    if task_skill_slugs:
        for slug in task_skill_slugs:
            if slug in merged:
                merged[slug] = min(merged[slug] * 1.20, 100.0)   # +20% boost
            else:
                # Task skill not detected by keywords → small base signal
                merged[slug] = 20.0

    return merged


if __name__ == "__main__":
    sample = """
    Desarrollé un script en Python para analizar datos de ventas usando pandas y
    matplotlib. El script limpia los datos, genera gráficos de tendencias y exporta
    un reporte en PDF. También usé git para versionar el proyecto y lo desplegué
    en AWS usando docker.
    """
    explicit = extract_skills_from_text(sample)
    full     = infer_from_submission(sample, task_skill_slugs=["analisis_datos", "python"])

    print(f"✓ Explicit skills found: {len(explicit)}")
    for s, sc in sorted(explicit.items(), key=lambda x: -x[1]):
        print(f"    {s}: {sc:.1f}")

    print(f"\n✓ Full inference (with implicit + task boost): {len(full)} skills")
    for s, sc in sorted(full.items(), key=lambda x: -x[1])[:8]:
        print(f"    {s}: {sc:.1f}")
