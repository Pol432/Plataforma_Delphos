"""
career_database.py — Career definitions and skill requirements for the LPO.

12 careers targeting the Ecuadorian tech/creative job market.
Each career maps skill_id → (required_mastery, is_critical).

Run:
    python learning_path/career_database.py           # validate only
    python learning_path/career_database.py --db      # also seed to PostgreSQL
"""

import sys
import os
import argparse
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import SKILL_GRAPH_PATH

logger = logging.getLogger("lpo.career_database")

# ─────────────────────────────────────────────────────────────────────────────
#  Skill ID quick reference  (from build_initial_graph.py)
#  1=analytical_thinking  2=problem_solving   3=communication
#  5=creativity           7=attention_to_detail 9=teamwork
#  11=research_skills    12=written_comm      15=empathy
#  16=decision_making    24=storytelling      25=facilitation
#  27=feedback_giving    31=python            32=javascript
#  33=sql                34=git               36=statistics
#  37=probability        38=linear_algebra    39=data_analysis
#  40=data_visualization 41=pandas            42=numpy
#  44=scikit_learn       46=machine_learning  51=html_css
#  52=react              53=node_express      54=rest_api_design
#  55=typescript         56=postgresql        59=docker
#  61=excel_advanced     62=tableau           64=a_b_testing
#  65=google_analytics   68=system_design     69=algorithms_ds
#  70=software_testing   71=visual_design     72=ui_design
#  73=ux_design          74=user_research     75=prototyping
#  76=graphic_design     77=copywriting       78=content_strategy
#  81=figma              85=design_thinking   86=leadership
#  87=project_management 88=agile_scrum       89=stakeholder_management
#  90=product_management 93=marketing_fundamentals
#  97=data_driven_decisions 98=okrs_kpis
# ─────────────────────────────────────────────────────────────────────────────

CAREERS = [

    # 1. UX Designer
    {
        "name": "UX Designer",
        "slug": "ux-designer",
        "description": "Design user-centered digital experiences through research, "
                       "wireframing, and prototyping.",
        "demand": "alta",
        "salary_usd": 1200,
        "days": 75,
        "requirements": {
            73: (85, True),   # ux_design          ← critical
            74: (80, True),   # user_research       ← critical
            75: (75, True),   # prototyping         ← critical
            72: (70, False),  # ui_design
            71: (65, False),  # visual_design
            81: (70, False),  # figma
            85: (65, False),  # design_thinking
            3:  (60, False),  # communication
            1:  (55, False),  # analytical_thinking
            15: (55, False),  # empathy
        },
    },

    # 2. Data Analyst
    {
        "name": "Data Analyst",
        "slug": "data-analyst",
        "description": "Extract insights from data using SQL, Python, and BI tools "
                       "to support business decisions.",
        "demand": "alta",
        "salary_usd": 1400,
        "days": 80,
        "requirements": {
            39: (85, True),   # data_analysis       ← critical
            33: (80, True),   # sql                 ← critical
            36: (75, True),   # statistics          ← critical
            40: (75, False),  # data_visualization
            41: (70, False),  # pandas
            31: (65, False),  # python
            62: (60, False),  # tableau
            61: (60, False),  # excel_advanced
            64: (55, False),  # a_b_testing
            97: (60, False),  # data_driven_decisions
            1:  (55, False),  # analytical_thinking
        },
    },

    # 3. Frontend Developer
    {
        "name": "Frontend Developer",
        "slug": "frontend-developer",
        "description": "Build responsive, accessible web interfaces using modern "
                       "JavaScript frameworks.",
        "demand": "alta",
        "salary_usd": 1500,
        "days": 85,
        "requirements": {
            52: (85, True),   # react               ← critical
            32: (80, True),   # javascript          ← critical
            51: (80, True),   # html_css            ← critical
            55: (70, False),  # typescript
            34: (65, False),  # git
            54: (65, False),  # rest_api_design
            72: (55, False),  # ui_design
            70: (60, False),  # software_testing
            2:  (55, False),  # problem_solving
        },
    },

    # 4. Machine Learning Engineer
    {
        "name": "Machine Learning Engineer",
        "slug": "ml-engineer",
        "description": "Build and deploy ML models that power intelligent product "
                       "features at scale.",
        "demand": "alta",
        "salary_usd": 2200,
        "days": 90,
        "requirements": {
            46: (85, True),   # machine_learning    ← critical
            36: (80, True),   # statistics          ← critical
            31: (85, True),   # python              ← critical
            38: (75, True),   # linear_algebra      ← critical
            44: (75, False),  # scikit_learn
            41: (70, False),  # pandas
            42: (70, False),  # numpy
            59: (65, False),  # docker
            34: (65, False),  # git
            68: (60, False),  # system_design
            39: (65, False),  # data_analysis
        },
    },

    # 5. Product Manager
    {
        "name": "Product Manager",
        "slug": "product-manager",
        "description": "Define product vision, align teams, and ship features that "
                       "create measurable user and business value.",
        "demand": "alta",
        "salary_usd": 1800,
        "days": 80,
        "requirements": {
            90: (85, True),   # product_management  ← critical
            73: (70, True),   # ux_design           ← critical
            97: (75, True),   # data_driven_decisions ← critical
            88: (70, False),  # agile_scrum
            87: (65, False),  # project_management
            3:  (70, False),  # communication
            16: (65, False),  # decision_making
            89: (60, False),  # stakeholder_management
            64: (60, False),  # a_b_testing
            1:  (60, False),  # analytical_thinking
        },
    },

    # 6. Full-Stack Developer
    {
        "name": "Full-Stack Developer",
        "slug": "fullstack-developer",
        "description": "Design and implement end-to-end web applications, from "
                       "database to browser.",
        "demand": "alta",
        "salary_usd": 1700,
        "days": 90,
        "requirements": {
            52: (80, True),   # react               ← critical
            53: (80, True),   # node_express        ← critical
            33: (75, True),   # sql                 ← critical
            54: (75, False),  # rest_api_design
            56: (65, False),  # postgresql
            59: (60, False),  # docker
            34: (70, False),  # git
            55: (65, False),  # typescript
            70: (60, False),  # software_testing
            68: (55, False),  # system_design
        },
    },

    # 7. UI Designer
    {
        "name": "UI Designer",
        "slug": "ui-designer",
        "description": "Create visually compelling, pixel-perfect interfaces guided "
                       "by design systems and brand guidelines.",
        "demand": "media",
        "salary_usd": 1000,
        "days": 60,
        "requirements": {
            72: (85, True),   # ui_design           ← critical
            71: (75, True),   # visual_design       ← critical
            81: (80, True),   # figma               ← critical
            75: (65, False),  # prototyping
            76: (60, False),  # graphic_design
            5:  (60, False),  # creativity
            7:  (55, False),  # attention_to_detail
            74: (55, False),  # user_research
        },
    },

    # 8. Data Scientist
    {
        "name": "Data Scientist",
        "slug": "data-scientist",
        "description": "Apply statistical modeling and ML to solve complex business "
                       "problems and communicate findings clearly.",
        "demand": "alta",
        "salary_usd": 2000,
        "days": 90,
        "requirements": {
            46: (80, True),   # machine_learning    ← critical
            36: (85, True),   # statistics          ← critical
            39: (80, True),   # data_analysis       ← critical
            31: (80, False),  # python
            41: (75, False),  # pandas
            40: (75, False),  # data_visualization
            37: (70, False),  # probability
            44: (70, False),  # scikit_learn
            64: (65, False),  # a_b_testing
            12: (65, False),  # written_communication
        },
    },

    # 9. Digital Marketing Analyst
    {
        "name": "Digital Marketing Analyst",
        "slug": "digital-marketing-analyst",
        "description": "Plan, execute, and measure digital campaigns using data "
                       "to optimize ROI.",
        "demand": "media",
        "salary_usd": 900,
        "days": 60,
        "requirements": {
            93: (80, True),   # marketing_fundamentals ← critical
            97: (75, True),   # data_driven_decisions  ← critical
            77: (70, False),  # copywriting
            65: (70, False),  # google_analytics
            39: (65, False),  # data_analysis
            33: (55, False),  # sql
            64: (65, False),  # a_b_testing
            24: (60, False),  # storytelling
            3:  (65, False),  # communication
        },
    },

    # 10. Backend Developer
    {
        "name": "Backend Developer",
        "slug": "backend-developer",
        "description": "Build robust APIs, services, and databases that power "
                       "product functionality.",
        "demand": "alta",
        "salary_usd": 1600,
        "days": 85,
        "requirements": {
            31: (85, True),   # python              ← critical
            33: (80, True),   # sql                 ← critical
            54: (80, True),   # rest_api_design     ← critical
            56: (75, False),  # postgresql
            59: (65, False),  # docker
            34: (70, False),  # git
            68: (65, False),  # system_design
            69: (65, False),  # algorithms_ds
            70: (65, False),  # software_testing
            2:  (60, False),  # problem_solving
        },
    },

    # 11. Agile Project Manager
    {
        "name": "Agile Project Manager",
        "slug": "agile-project-manager",
        "description": "Lead cross-functional teams using Agile/Scrum to deliver "
                       "projects on time and within budget.",
        "demand": "media",
        "salary_usd": 1300,
        "days": 70,
        "requirements": {
            87: (85, True),   # project_management  ← critical
            88: (80, True),   # agile_scrum         ← critical
            86: (70, False),  # leadership
            3:  (70, False),  # communication
            9:  (65, False),  # teamwork
            16: (65, False),  # decision_making
            98: (60, False),  # okrs_kpis
            27: (60, False),  # feedback_giving
            25: (60, False),  # facilitation
        },
    },

    # 12. Content Strategist
    {
        "name": "Content Strategist",
        "slug": "content-strategist",
        "description": "Develop and execute content plans that grow audiences, "
                       "build brand authority, and drive conversions.",
        "demand": "media",
        "salary_usd": 950,
        "days": 55,
        "requirements": {
            78: (85, True),   # content_strategy    ← critical
            77: (80, True),   # copywriting         ← critical
            24: (75, False),  # storytelling
            93: (65, False),  # marketing_fundamentals
            97: (65, False),  # data_driven_decisions
            11: (65, False),  # research_skills
            12: (70, False),  # written_communication
            3:  (65, False),  # communication
            5:  (60, False),  # creativity
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
#  In-memory helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_career_by_slug(slug: str) -> dict:
    for c in CAREERS:
        if c["slug"] == slug:
            return c
    raise KeyError(f"Career '{slug}' not found. Available: {list_slugs()}")


def get_career_requirements(slug: str) -> dict:
    """Return {skill_id: required_mastery} — no DB needed."""
    return {sid: req for sid, (req, _) in get_career_by_slug(slug)["requirements"].items()}


def get_critical_skills(slug: str) -> list:
    """Return skill_ids that are blocking for this career."""
    return [sid for sid, (_, crit) in get_career_by_slug(slug)["requirements"].items() if crit]


def list_slugs() -> list:
    return [c["slug"] for c in CAREERS]


# ─────────────────────────────────────────────────────────────────────────────
#  DB seeder
# ─────────────────────────────────────────────────────────────────────────────

def seed_careers_to_db(conn):
    """Upsert all careers + skill requirements to PostgreSQL. Safe to re-run."""
    from db import get_cursor
    with get_cursor(conn, dict_cursor=False) as cur:
        for career in CAREERS:
            cur.execute("""
                INSERT INTO carreras_catalogo
                    (nombre, slug, descripcion, demanda_mercado,
                     salario_promedio_usd, tiempo_estimado_dias, esta_activo)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE)
                ON CONFLICT (slug) DO UPDATE
                    SET nombre               = EXCLUDED.nombre,
                        descripcion          = EXCLUDED.descripcion,
                        demanda_mercado      = EXCLUDED.demanda_mercado,
                        salario_promedio_usd = EXCLUDED.salario_promedio_usd,
                        tiempo_estimado_dias = EXCLUDED.tiempo_estimado_dias
                RETURNING id
            """, (career["name"], career["slug"], career["description"],
                  career["demand"], career["salary_usd"], career["days"]))
            row = cur.fetchone()
            if row is None:
                cur.execute("SELECT id FROM carreras_catalogo WHERE slug = %s",
                            (career["slug"],))
                row = cur.fetchone()
            career_db_id = row[0]

            for skill_id, (req_mastery, is_crit) in career["requirements"].items():
                cur.execute("""
                    INSERT INTO habilidades_carrera
                        (carrera_id, habilidad_id, maestria_requerida, es_critica)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (carrera_id, habilidad_id) DO UPDATE
                        SET maestria_requerida = EXCLUDED.maestria_requerida,
                            es_critica         = EXCLUDED.es_critica
                """, (career_db_id, skill_id, req_mastery, is_crit))

    logger.info("Seeded %d careers to DB", len(CAREERS))
    print(f"✓ {len(CAREERS)} careers seeded to PostgreSQL")


# ─────────────────────────────────────────────────────────────────────────────
#  Self-test + entry point
# ─────────────────────────────────────────────────────────────────────────────

def _self_test() -> bool:
    from learning_path.core.graph_schema import SkillGraph
    graph = SkillGraph.load(SKILL_GRAPH_PATH)
    valid_ids = set(graph.nodes.keys())
    errors = [
        f"  '{c['slug']}': skill_id {sid} not in graph"
        for c in CAREERS for sid in c["requirements"] if sid not in valid_ids
    ]
    if errors:
        print("⚠  Validation errors:\n" + "\n".join(errors))
        return False
    print(f"✓  All {len(CAREERS)} careers validated against skill graph\n")
    header = f"  {'Career':<34} {'Skills':>6} {'Critical':>8} {'Days':>5} {'$/mo':>7}"
    print(header)
    print("  " + "─" * 64)
    for c in CAREERS:
        n_skills   = len(c["requirements"])
        n_critical = sum(1 for _, crit in c["requirements"].values() if crit)
        print(f"  {c['name']:<34} {n_skills:>6} {n_critical:>8} "
              f"{c['days']:>5} {c['salary_usd']:>7}")
    print()
    return True


def main():
    parser = argparse.ArgumentParser(description="DELPHOS LPO — Career Database")
    parser.add_argument("--db", action="store_true", help="Seed to PostgreSQL")
    args = parser.parse_args()
    print("\nDELPHOS LPO — Career Database\n")
    if not _self_test():
        sys.exit(1)
    if args.db:
        from db import managed_connection
        with managed_connection() as conn:
            seed_careers_to_db(conn)


if __name__ == "__main__":
    main()
