"""
Single seed script: populates habilidades_catalogo with all 200 DELPHOS skills.
Run once: python db/seed_skills.py
Safe to re-run — uses INSERT ... ON CONFLICT (slug) DO NOTHING.
Truncates first if --reset flag is passed: python db/seed_skills.py --reset
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from db.connection import engine

SKILLS = [
    # ── BLANDAS: Cognitivas (15) ──────────────────────────────────────────
    ("pensamiento_analitico",    "Pensamiento Analítico",           "blanda",      1, "alta",  "creciendo"),
    ("resolucion_problemas",     "Resolución de Problemas",         "blanda",      1, "alta",  "creciendo"),
    ("pensamiento_critico",      "Pensamiento Crítico",             "blanda",      1, "alta",  "creciendo"),
    ("razonamiento_logico",      "Razonamiento Lógico",             "blanda",      1, "media", "estable"),
    ("reconocimiento_patrones",  "Reconocimiento de Patrones",      "blanda",      1, "media", "creciendo"),
    ("atencion_al_detalle",      "Atención al Detalle",             "blanda",      1, "alta",  "estable"),
    ("memoria_retentiva",        "Memoria Retentiva",               "blanda",      1, "media", "estable"),
    ("velocidad_aprendizaje",    "Velocidad de Aprendizaje",        "blanda",      1, "alta",  "creciendo"),
    ("adaptabilidad",            "Adaptabilidad",                   "blanda",      1, "alta",  "creciendo"),
    ("pensamiento_estrategico",  "Pensamiento Estratégico",         "blanda",      1, "alta",  "creciendo"),
    ("pensamiento_sistemico",    "Pensamiento Sistémico",           "blanda",      1, "media", "creciendo"),
    ("razonamiento_abstracto",   "Razonamiento Abstracto",          "blanda",      1, "media", "estable"),
    ("toma_decisiones",          "Toma de Decisiones",              "blanda",      1, "alta",  "estable"),
    ("sintesis_informacion",     "Síntesis de Información",         "blanda",      1, "alta",  "creciendo"),
    ("comprension_conceptual",   "Comprensión Conceptual",          "blanda",      1, "media", "estable"),
    # ── BLANDAS: Comunicación (8) ─────────────────────────────────────────
    ("comunicacion_escrita",     "Comunicación Escrita",            "blanda",      1, "alta",  "estable"),
    ("comunicacion_verbal",      "Comunicación Verbal",             "blanda",      1, "alta",  "estable"),
    ("presentaciones",           "Presentaciones",                  "blanda",      1, "alta",  "estable"),
    ("escucha_activa",           "Escucha Activa",                  "blanda",      1, "alta",  "estable"),
    ("persuasion",               "Persuasión",                      "blanda",      1, "media", "estable"),
    ("negociacion",              "Negociación",                     "blanda",      1, "media", "estable"),
    ("storytelling",             "Storytelling",                    "blanda",      1, "alta",  "creciendo"),
    ("escritura_tecnica",        "Escritura Técnica",               "blanda",      1, "alta",  "creciendo"),
    # ── BLANDAS: Personales (7) ───────────────────────────────────────────
    ("gestion_tiempo",           "Gestión del Tiempo",              "blanda",      1, "alta",  "estable"),
    ("organizacion",             "Organización",                    "blanda",      1, "alta",  "estable"),
    ("autodisciplina",           "Autodisciplina",                  "blanda",      1, "alta",  "estable"),
    ("resiliencia",              "Resiliencia",                     "blanda",      1, "alta",  "creciendo"),
    ("mentalidad_crecimiento",   "Mentalidad de Crecimiento",       "blanda",      1, "alta",  "creciendo"),
    ("inteligencia_emocional",   "Inteligencia Emocional",          "blanda",      1, "alta",  "creciendo"),
    ("manejo_estres",            "Manejo del Estrés",               "blanda",      1, "alta",  "estable"),
    # ── BLANDAS: Creativas (5) ────────────────────────────────────────────
    ("creatividad",              "Creatividad",                     "blanda",      1, "alta",  "creciendo"),
    ("ideacion",                 "Ideación",                        "blanda",      1, "alta",  "creciendo"),
    ("brainstorming",            "Brainstorming",                   "blanda",      1, "media", "estable"),
    ("design_thinking",          "Design Thinking",                 "blanda",      1, "alta",  "creciendo"),
    ("innovacion",               "Innovación",                      "blanda",      1, "alta",  "creciendo"),
    # ── BLANDAS: Liderazgo (10) ───────────────────────────────────────────
    ("liderazgo",                "Liderazgo",                       "blanda",      1, "alta",  "estable"),
    ("gestion_equipos",          "Gestión de Equipos",              "blanda",      1, "alta",  "estable"),
    ("mentoring",                "Mentoring",                       "blanda",      1, "alta",  "creciendo"),
    ("resolucion_conflictos",    "Resolución de Conflictos",        "blanda",      1, "alta",  "estable"),
    ("delegacion",               "Delegación",                      "blanda",      1, "media", "estable"),
    ("motivacion",               "Motivación",                      "blanda",      1, "alta",  "estable"),
    ("coaching",                 "Coaching",                        "blanda",      1, "alta",  "creciendo"),
    ("gestion_cambio",           "Gestión del Cambio",              "blanda",      1, "alta",  "creciendo"),
    ("planificacion_estrategica","Planificación Estratégica",        "blanda",      1, "alta",  "estable"),
    ("vision",                   "Visión",                          "blanda",      1, "alta",  "estable"),
    # ── BLANDAS: Gestión de Proyectos (8) ────────────────────────────────
    ("planificacion_proyectos",  "Planificación de Proyectos",      "blanda",      1, "alta",  "estable"),
    ("asignacion_recursos",      "Asignación de Recursos",          "blanda",      1, "media", "estable"),
    ("gestion_riesgos",          "Gestión de Riesgos",              "blanda",      1, "alta",  "creciendo"),
    ("gestion_stakeholders",     "Gestión de Stakeholders",         "blanda",      1, "alta",  "estable"),
    ("gestion_presupuesto",      "Gestión de Presupuesto",          "blanda",      1, "alta",  "estable"),
    ("gestion_cronograma",       "Gestión de Cronograma",           "blanda",      1, "alta",  "estable"),
    ("aseguramiento_calidad",    "Aseguramiento de Calidad",        "blanda",      1, "alta",  "estable"),
    ("mejora_procesos",          "Mejora de Procesos",              "blanda",      1, "alta",  "creciendo"),
    # ── BLANDAS: Operaciones de Negocio (10) ─────────────────────────────
    ("investigacion_mercado",    "Investigación de Mercado",        "blanda",      1, "alta",  "estable"),
    ("analisis_competitivo",     "Análisis Competitivo",            "blanda",      1, "alta",  "estable"),
    ("servicio_cliente",         "Servicio al Cliente",             "blanda",      1, "alta",  "estable"),
    ("ventas",                   "Ventas",                          "blanda",      1, "alta",  "estable"),
    ("marketing",                "Marketing",                       "blanda",      1, "alta",  "creciendo"),
    ("analisis_financiero",      "Análisis Financiero",             "blanda",      1, "alta",  "estable"),
    ("estrategia_negocio",       "Estrategia de Negocio",           "blanda",      1, "alta",  "estable"),
    ("gestion_producto",         "Gestión de Producto",             "blanda",      1, "alta",  "creciendo"),
    ("gestion_operaciones",      "Gestión de Operaciones",          "blanda",      1, "media", "estable"),
    ("gestion_proveedores",      "Gestión de Proveedores",          "blanda",      1, "media", "estable"),
    # ── BLANDAS: Investigación (5) ────────────────────────────────────────
    ("investigacion_usuarios",   "Investigación de Usuarios",       "blanda",      1, "alta",  "creciendo"),
    ("investigacion_ux",         "Investigación UX",                "blanda",      1, "alta",  "creciendo"),
    ("investigacion_academica",  "Investigación Académica",         "blanda",      1, "media", "estable"),
    ("revision_literatura",      "Revisión de Literatura",          "blanda",      1, "media", "estable"),
    ("diseno_experimental",      "Diseño Experimental",             "blanda",      1, "media", "estable"),
    # ── BLANDAS: Interpersonal (5) ────────────────────────────────────────
    ("trabajo_equipo",           "Trabajo en Equipo",               "blanda",      1, "alta",  "estable"),
    ("empatia",                  "Empatía",                         "blanda",      1, "alta",  "creciendo"),
    ("colaboracion",             "Colaboración",                    "blanda",      1, "alta",  "estable"),
    ("networking",               "Networking",                      "blanda",      1, "alta",  "estable"),
    ("gestion_diversidad",       "Gestión de la Diversidad",        "blanda",      1, "alta",  "creciendo"),
    # ── BLANDAS: Adicionales (11) ─────────────────────────────────────────
    ("facilitacion",             "Facilitación",                    "blanda",      1, "alta",  "creciendo"),
    ("gestion_conocimiento",     "Gestión del Conocimiento",        "blanda",      1, "media", "creciendo"),
    ("pensamiento_lateral",      "Pensamiento Lateral",             "blanda",      1, "media", "creciendo"),
    ("intrapreneurship",         "Intraemprendimiento",             "blanda",      1, "alta",  "creciendo"),
    ("gestion_conflictos",       "Gestión de Conflictos",           "blanda",      1, "alta",  "estable"),
    ("toma_riesgos",             "Toma de Riesgos Calculados",      "blanda",      1, "media", "creciendo"),
    ("autoevaluacion",           "Autoevaluación",                  "blanda",      1, "alta",  "creciendo"),
    ("orientacion_resultados",   "Orientación a Resultados",        "blanda",      1, "alta",  "estable"),
    ("gestion_prioridades",      "Gestión de Prioridades",          "blanda",      1, "alta",  "creciendo"),
    ("pruebas_usuario",          "Pruebas de Usuario",              "blanda",      1, "alta",  "creciendo"),
    ("pensamiento_critico_adv",  "Pensamiento Crítico Avanzado",    "blanda",      1, "alta",  "creciendo"),
    # ── TECNICA: Lenguajes (10) ───────────────────────────────────────────
    ("python",                   "Python",                          "tecnica",     2, "alta",  "creciendo"),
    ("javascript",               "JavaScript",                      "tecnica",     2, "alta",  "creciendo"),
    ("java",                     "Java",                            "tecnica",     2, "alta",  "estable"),
    ("cpp",                      "C++",                             "tecnica",     2, "media", "estable"),
    ("sql",                      "SQL",                             "tecnica",     2, "alta",  "estable"),
    ("r_lenguaje",               "R",                               "tecnica",     2, "media", "estable"),
    ("go",                       "Go",                              "tecnica",     2, "media", "creciendo"),
    ("rust",                     "Rust",                            "tecnica",     2, "media", "creciendo"),
    ("typescript",               "TypeScript",                      "tecnica",     2, "alta",  "creciendo"),
    ("php",                      "PHP",                             "tecnica",     2, "media", "declinando"),
    # ── TECNICA: Ciencia de Datos (10) ────────────────────────────────────
    ("machine_learning",         "Machine Learning",                "tecnica",     2, "alta",  "creciendo"),
    ("deep_learning",            "Deep Learning",                   "tecnica",     2, "alta",  "creciendo"),
    ("estadistica",              "Estadística",                     "tecnica",     2, "alta",  "estable"),
    ("analisis_datos",           "Análisis de Datos",               "tecnica",     2, "alta",  "creciendo"),
    ("visualizacion_datos",      "Visualización de Datos",          "tecnica",     2, "alta",  "creciendo"),
    ("nlp",                      "NLP",                             "tecnica",     2, "alta",  "creciendo"),
    ("vision_computacional",     "Visión Computacional",            "tecnica",     2, "alta",  "creciendo"),
    ("series_temporales",        "Series Temporales",               "tecnica",     2, "media", "estable"),
    ("ingenieria_features",      "Ingeniería de Features",          "tecnica",     2, "alta",  "creciendo"),
    ("evaluacion_modelos",       "Evaluación de Modelos",           "tecnica",     2, "alta",  "creciendo"),
    # ── TECNICA: Desarrollo Web (10) ──────────────────────────────────────
    ("html_css",                 "HTML/CSS",                        "tecnica",     2, "alta",  "estable"),
    ("react",                    "React",                           "tecnica",     2, "alta",  "creciendo"),
    ("vue",                      "Vue.js",                          "tecnica",     2, "media", "estable"),
    ("angular",                  "Angular",                         "tecnica",     2, "media", "estable"),
    ("nodejs",                   "Node.js",                         "tecnica",     2, "alta",  "estable"),
    ("django",                   "Django",                          "tecnica",     2, "media", "estable"),
    ("flask",                    "Flask",                           "tecnica",     2, "media", "estable"),
    ("rest_api",                 "REST API",                        "tecnica",     2, "alta",  "estable"),
    ("graphql",                  "GraphQL",                         "tecnica",     2, "media", "creciendo"),
    ("diseno_responsivo",        "Diseño Responsivo",               "tecnica",     2, "alta",  "estable"),
    # ── TECNICA: Cloud y DevOps (9) ───────────────────────────────────────
    ("aws",                      "AWS",                             "tecnica",     2, "alta",  "creciendo"),
    ("azure",                    "Azure",                           "tecnica",     2, "alta",  "creciendo"),
    ("gcp",                      "GCP",                             "tecnica",     2, "alta",  "creciendo"),
    ("docker",                   "Docker",                          "tecnica",     2, "alta",  "creciendo"),
    ("kubernetes",               "Kubernetes",                      "tecnica",     2, "alta",  "creciendo"),
    ("ci_cd",                    "CI/CD",                           "tecnica",     2, "alta",  "creciendo"),
    ("terraform",                "Terraform",                       "tecnica",     2, "media", "creciendo"),
    ("git",                      "Git",                             "tecnica",     2, "alta",  "estable"),
    ("linux",                    "Linux",                           "tecnica",     2, "alta",  "estable"),
    # ── TECNICA: Especializado (5) ────────────────────────────────────────
    ("ab_testing",               "A/B Testing",                     "tecnica",     2, "alta",  "creciendo"),
    ("optimizacion_conversion",  "Optimización de Conversión",      "tecnica",     2, "alta",  "creciendo"),
    ("seo",                      "SEO",                             "tecnica",     2, "alta",  "estable"),
    ("arquitectura_sistemas",    "Arquitectura de Sistemas",        "tecnica",     2, "alta",  "creciendo"),
    ("diseno_bases_datos",       "Diseño de Bases de Datos",        "tecnica",     2, "alta",  "estable"),
    # ── TECNICA: Emergente (10) ───────────────────────────────────────────
    ("blockchain",               "Blockchain",                      "tecnica",     2, "media", "creciendo"),
    ("criptomonedas",            "Criptomonedas",                   "tecnica",     2, "media", "creciendo"),
    ("ar_vr",                    "AR/VR",                           "tecnica",     2, "media", "creciendo"),
    ("iot",                      "IoT",                             "tecnica",     2, "media", "creciendo"),
    ("robotica",                 "Robótica",                        "tecnica",     2, "media", "creciendo"),
    ("computacion_cuantica",     "Computación Cuántica",            "tecnica",     2, "baja",  "creciendo"),
    ("edge_computing",           "Edge Computing",                  "tecnica",     2, "media", "creciendo"),
    ("ciberseguridad",           "Ciberseguridad",                  "tecnica",     2, "alta",  "creciendo"),
    ("prompt_engineering",       "Prompt Engineering",              "tecnica",     2, "alta",  "creciendo"),
    ("mlops",                    "MLOps",                           "tecnica",     2, "alta",  "creciendo"),
    # ── HERRAMIENTA: Datos (10) ───────────────────────────────────────────
    ("pandas",                   "Pandas",                          "herramienta", 3, "alta",  "estable"),
    ("numpy",                    "NumPy",                           "herramienta", 3, "alta",  "estable"),
    ("scikit_learn",             "Scikit-learn",                    "herramienta", 3, "alta",  "estable"),
    ("tensorflow",               "TensorFlow",                      "herramienta", 3, "alta",  "estable"),
    ("pytorch",                  "PyTorch",                         "herramienta", 3, "alta",  "creciendo"),
    ("keras",                    "Keras",                           "herramienta", 3, "media", "estable"),
    ("tableau",                  "Tableau",                         "herramienta", 3, "alta",  "estable"),
    ("power_bi",                 "Power BI",                        "herramienta", 3, "alta",  "creciendo"),
    ("excel_avanzado",           "Excel Avanzado",                  "herramienta", 3, "alta",  "estable"),
    ("sql_avanzado",             "SQL Avanzado",                    "herramienta", 3, "alta",  "estable"),
    # ── HERRAMIENTA: Productividad (6) ────────────────────────────────────
    ("notion",                   "Notion",                          "herramienta", 3, "alta",  "creciendo"),
    ("figma",                    "Figma",                           "herramienta", 3, "alta",  "creciendo"),
    ("jira",                     "Jira",                            "herramienta", 3, "alta",  "estable"),
    ("slack",                    "Slack",                           "herramienta", 3, "alta",  "estable"),
    ("trello",                   "Trello",                          "herramienta", 3, "media", "estable"),
    ("airtable",                 "Airtable",                        "herramienta", 3, "media", "creciendo"),
    # ── HERRAMIENTA: Marketing (5) ────────────────────────────────────────
    ("google_analytics",         "Google Analytics",                "herramienta", 2, "alta",  "estable"),
    ("hubspot",                  "HubSpot",                         "herramienta", 2, "media", "creciendo"),
    ("google_ads",               "Google Ads",                      "herramienta", 2, "alta",  "estable"),
    ("email_marketing",          "Email Marketing",                 "herramienta", 2, "alta",  "estable"),
    ("marketing_redes",          "Marketing en Redes Sociales",     "herramienta", 2, "alta",  "creciendo"),
    # ── HERRAMIENTA: Metodologías (2) ─────────────────────────────────────
    ("metodologia_agile",        "Metodología Agile",               "herramienta", 2, "alta",  "creciendo"),
    ("scrum",                    "Scrum",                           "herramienta", 2, "alta",  "creciendo"),
    # ── CREATIVA: Diseño Visual (15) ──────────────────────────────────────
    ("diseno_visual",            "Diseño Visual",                   "creativa",    1, "alta",  "creciendo"),
    ("diseno_ui",                "Diseño UI",                       "creativa",    1, "alta",  "creciendo"),
    ("diseno_ux",                "Diseño UX",                       "creativa",    1, "alta",  "creciendo"),
    ("diseno_grafico",           "Diseño Gráfico",                  "creativa",    1, "alta",  "estable"),
    ("ilustracion",              "Ilustración",                     "creativa",    1, "media", "estable"),
    ("tipografia",               "Tipografía",                      "creativa",    1, "media", "estable"),
    ("teoria_color",             "Teoría del Color",                "creativa",    1, "media", "estable"),
    ("diseno_layout",            "Diseño de Layout",                "creativa",    1, "media", "estable"),
    ("branding",                 "Branding",                        "creativa",    1, "alta",  "creciendo"),
    ("diseno_logo",              "Diseño de Logo",                  "creativa",    1, "media", "estable"),
    ("diseno_iconos",            "Diseño de Iconos",                "creativa",    1, "media", "estable"),
    ("edicion_imagen",           "Edición de Imagen",               "creativa",    1, "media", "estable"),
    ("fotografia",               "Fotografía",                      "creativa",    1, "media", "estable"),
    ("modelado_3d",              "Modelado 3D",                     "creativa",    1, "media", "creciendo"),
    ("animacion",                "Animación",                       "creativa",    1, "media", "creciendo"),
    # ── CREATIVA: Contenido (10) ──────────────────────────────────────────
    ("copywriting",              "Copywriting",                     "creativa",    1, "alta",  "creciendo"),
    ("redaccion_contenido",      "Redacción de Contenido",          "creativa",    1, "alta",  "creciendo"),
    ("escritura_creativa",       "Escritura Creativa",              "creativa",    1, "media", "estable"),
    ("edicion_video",            "Edición de Video",                "creativa",    1, "alta",  "creciendo"),
    ("edicion_audio",            "Edición de Audio",                "creativa",    1, "media", "estable"),
    ("guion",                    "Guion",                           "creativa",    1, "media", "estable"),
    ("contenido_redes",          "Contenido para Redes Sociales",   "creativa",    1, "alta",  "creciendo"),
    ("blog_writing",             "Blog Writing",                    "creativa",    1, "media", "estable"),
    ("documentacion_tecnica",    "Documentación Técnica",           "creativa",    1, "alta",  "creciendo"),
    ("seo_writing",              "SEO Writing",                     "creativa",    1, "alta",  "creciendo"),
    # ── CREATIVA: Especializado (4) ───────────────────────────────────────
    ("prototipado",              "Prototipado",                     "creativa",    1, "alta",  "creciendo"),
    ("wireframing",              "Wireframing",                     "creativa",    1, "alta",  "creciendo"),
    ("mapas_empatia",            "Mapas de Empatía",                "creativa",    1, "alta",  "creciendo"),
    ("customer_journey",         "Customer Journey Mapping",        "creativa",    1, "alta",  "creciendo"),
    # ── HERRAMIENTA: Cloud & Bases de Datos (5) ──────────────────────────
    ("mongodb",                  "MongoDB",                         "herramienta", 3, "alta",  "creciendo"),
    ("redis",                    "Redis",                           "herramienta", 3, "alta",  "creciendo"),
    ("postgresql",               "PostgreSQL",                      "herramienta", 3, "alta",  "estable"),
    ("firebase",                 "Firebase",                        "herramienta", 3, "media", "estable"),
    ("elasticsearch",            "Elasticsearch",                   "herramienta", 3, "media", "creciendo"),
    # ── TECNICA: Seguridad y Testing (5) ─────────────────────────────────
    ("pruebas_software",         "Pruebas de Software",             "tecnica",     2, "alta",  "estable"),
    ("automatizacion_qa",        "Automatización QA",               "tecnica",     2, "alta",  "creciendo"),
    ("seguridad_web",            "Seguridad Web",                   "tecnica",     2, "alta",  "creciendo"),
    ("api_design",               "Diseño de APIs",                  "tecnica",     2, "alta",  "creciendo"),
    ("microservicios",           "Microservicios",                  "tecnica",     2, "alta",  "creciendo"),
]

# ── Internal verification — fails loudly before touching the DB ────────────
_slugs   = [s[0] for s in SKILLS]
_nombres = [s[1] for s in SKILLS]
_dup_s   = [s for s in set(_slugs)   if _slugs.count(s)   > 1]
_dup_n   = [n for n in set(_nombres) if _nombres.count(n) > 1]
assert not _dup_s,          f"Duplicate slugs in SKILLS list: {_dup_s}"
assert not _dup_n,          f"Duplicate nombres in SKILLS list: {_dup_n}"
assert len(SKILLS) == 200,  f"Expected 200 skills, got {len(SKILLS)}"


def seed(reset: bool = False):
    if reset:
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE habilidades_catalogo CASCADE"))
        print("⚠ Catalog truncated (--reset flag)")

    inserted = 0
    skipped  = 0

    with engine.begin() as conn:
        for slug, nombre, categoria, nivel, demanda, tendencia in SKILLS:
            result = conn.execute(text("""
                INSERT INTO habilidades_catalogo
                  (slug, nombre, categoria, nivel_taxonomia, demanda_mercado, tendencia)
                VALUES
                  (:slug, :nombre, :cat, :nivel, :demanda, :tendencia)
                ON CONFLICT (slug) DO NOTHING
            """), {
                "slug":      slug,
                "nombre":    nombre,
                "cat":       categoria,
                "nivel":     nivel,
                "demanda":   demanda,
                "tendencia": tendencia,
            })
            if result.rowcount:
                inserted += 1
            else:
                skipped += 1

    with engine.connect() as conn:
        total = conn.execute(text(
            "SELECT COUNT(*) FROM habilidades_catalogo"
        )).scalar()

    print(f"✓ Seed complete — inserted: {inserted}, already existed: {skipped}")
    print(f"✓ Total in catalog: {total} / 200")
    if total != 200:
        print(f"⚠ WARNING: expected 200 but got {total}. Run with --reset to start clean.")


if __name__ == "__main__":
    reset_flag = "--reset" in sys.argv
    seed(reset=reset_flag)
