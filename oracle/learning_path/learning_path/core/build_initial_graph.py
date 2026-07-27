"""
build_initial_graph.py — Builds the starter 100-skill dependency graph.

Run directly:
    python learning_path/build_initial_graph.py

This script:
  1. Defines 100 core skills across 4 categories
  2. Defines prerequisite relationships between them
  3. Saves to data/skill_graph_v1.json  (dev cache)
  4. Optionally seeds the graph to PostgreSQL (pass --db flag)
"""

import sys
import os
import argparse
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from learning_path.core.graph_schema import SkillNode, SkillEdge, SkillGraph
from config import SKILL_GRAPH_PATH

logger = logging.getLogger("lpo.build_graph")


# ─────────────────────────────────────────────────────────────────────────────
#  Skill Definitions
# ─────────────────────────────────────────────────────────────────────────────

def _foundational() -> list:
    """IDs 1–30 — Transferable meta-skills."""
    return [
        # (id, name, hours, difficulty)
        (1,  "analytical_thinking",    15.0, 0.30),
        (2,  "problem_solving",        12.0, 0.30),
        (3,  "communication",          10.0, 0.25),
        (4,  "critical_thinking",      14.0, 0.30),
        (5,  "creativity",              8.0, 0.20),
        (6,  "time_management",         6.0, 0.20),
        (7,  "attention_to_detail",     8.0, 0.25),
        (8,  "learning_speed",          0.0, 0.10),  # meta-skill
        (9,  "teamwork",                8.0, 0.20),
        (10, "adaptability",            6.0, 0.20),
        (11, "research_skills",        10.0, 0.30),
        (12, "written_communication",  12.0, 0.25),
        (13, "presentation_skills",    10.0, 0.30),
        (14, "active_listening",        6.0, 0.20),
        (15, "empathy",                 5.0, 0.15),
        (16, "decision_making",        10.0, 0.30),
        (17, "negotiation",            12.0, 0.40),
        (18, "conflict_resolution",    10.0, 0.35),
        (19, "self_motivation",         4.0, 0.15),
        (20, "curiosity",               0.0, 0.10),  # meta-skill
        (21, "logical_reasoning",      12.0, 0.30),
        (22, "pattern_recognition",    10.0, 0.35),
        (23, "systems_thinking",       15.0, 0.40),
        (24, "storytelling",           10.0, 0.30),
        (25, "facilitation",           10.0, 0.35),
        (26, "mentoring",              12.0, 0.40),
        (27, "feedback_giving",         8.0, 0.30),
        (28, "growth_mindset",          0.0, 0.10),  # meta-skill
        (29, "networking",              8.0, 0.25),
        (30, "ethics_and_integrity",    6.0, 0.20),
    ]


def _technical() -> list:
    """IDs 31–70 — Hard technical skills."""
    return [
        # Programming
        (31, "python",              40.0, 0.40),
        (32, "javascript",          45.0, 0.40),
        (33, "sql",                 25.0, 0.35),
        (34, "git_version_control", 12.0, 0.30),
        (35, "linux_bash",          15.0, 0.35),
        # Data & Statistics
        (36, "statistics",          60.0, 0.60),
        (37, "probability",         40.0, 0.55),
        (38, "linear_algebra",      50.0, 0.65),
        (39, "data_analysis",       35.0, 0.50),
        (40, "data_visualization",  30.0, 0.45),
        # Python ecosystem
        (41, "pandas",              20.0, 0.45),
        (42, "numpy",               15.0, 0.40),
        (43, "matplotlib",          12.0, 0.40),
        (44, "scikit_learn",        25.0, 0.60),
        (45, "jupyter_notebooks",    8.0, 0.30),
        # ML & AI
        (46, "machine_learning",    80.0, 0.75),
        (47, "deep_learning",      100.0, 0.85),
        (48, "nlp",                 60.0, 0.80),
        (49, "computer_vision",     60.0, 0.80),
        (50, "mlops",               40.0, 0.70),
        # Web development
        (51, "html_css",            30.0, 0.30),
        (52, "react",               50.0, 0.60),
        (53, "node_express",        40.0, 0.60),
        (54, "rest_api_design",     35.0, 0.55),
        (55, "typescript",          30.0, 0.50),
        # Databases & Cloud
        (56, "postgresql",          30.0, 0.50),
        (57, "mongodb",             25.0, 0.45),
        (58, "redis",               15.0, 0.45),
        (59, "docker",              20.0, 0.55),
        (60, "cloud_fundamentals",  25.0, 0.50),
        # BI & Analytics
        (61, "excel_advanced",      20.0, 0.40),
        (62, "tableau",             18.0, 0.40),
        (63, "power_bi",            18.0, 0.40),
        (64, "a_b_testing",         20.0, 0.55),
        (65, "google_analytics",    12.0, 0.35),
        # Security & Systems
        (66, "cybersecurity_basics",20.0, 0.45),
        (67, "networking_basics",   20.0, 0.45),
        (68, "system_design",       40.0, 0.70),
        (69, "algorithms_ds",       60.0, 0.75),
        (70, "software_testing",    25.0, 0.50),
    ]


def _creative() -> list:
    """IDs 71–85 — Design & creative skills."""
    return [
        (71, "visual_design",       45.0, 0.50),
        (72, "ui_design",           50.0, 0.60),
        (73, "ux_design",           60.0, 0.65),
        (74, "user_research",       40.0, 0.55),
        (75, "prototyping",         35.0, 0.50),
        (76, "graphic_design",      50.0, 0.55),
        (77, "copywriting",         30.0, 0.40),
        (78, "content_strategy",    35.0, 0.50),
        (79, "brand_identity",      40.0, 0.55),
        (80, "motion_design",       55.0, 0.65),
        (81, "figma",               18.0, 0.35),
        (82, "adobe_xd",            20.0, 0.40),
        (83, "illustration",        50.0, 0.60),
        (84, "video_editing",       35.0, 0.50),
        (85, "design_thinking",     20.0, 0.40),
    ]


def _business() -> list:
    """IDs 86–100 — Business & leadership skills."""
    return [
        (86,  "leadership",              50.0, 0.60),
        (87,  "project_management",      45.0, 0.60),
        (88,  "agile_scrum",             20.0, 0.40),
        (89,  "stakeholder_management",  35.0, 0.55),
        (90,  "product_management",      55.0, 0.65),
        (91,  "business_strategy",       50.0, 0.65),
        (92,  "financial_literacy",      35.0, 0.55),
        (93,  "marketing_fundamentals",  30.0, 0.45),
        (94,  "sales_fundamentals",      25.0, 0.40),
        (95,  "customer_success",        20.0, 0.40),
        (96,  "operations_management",   40.0, 0.60),
        (97,  "data_driven_decisions",   25.0, 0.50),
        (98,  "okrs_kpis",               15.0, 0.40),
        (99,  "change_management",       35.0, 0.60),
        (100, "entrepreneurship",        45.0, 0.65),
    ]


# ─────────────────────────────────────────────────────────────────────────────
#  Edge Definitions
# ─────────────────────────────────────────────────────────────────────────────

def _edges() -> list:
    """
    Prerequisite relationships as tuples:
        (source_id, target_id, weight, required_mastery, rationale)
    """
    return [
        # ── Foundational → Technical ──────────────────────────────────────
        (1,  31, 0.35, 50, "Analytical thinking essential for programming logic"),
        (2,  31, 0.30, 45, "Problem-solving is the core loop of coding"),
        (21, 31, 0.30, 45, "Logical reasoning maps directly to code structure"),
        (1,  36, 0.40, 50, "Statistics requires strong analytical foundations"),
        (21, 36, 0.35, 50, "Probability & stats demand logical reasoning"),
        (22, 36, 0.30, 40, "Pattern recognition accelerates stats intuition"),

        # ── Programming foundations ────────────────────────────────────────
        (31, 41, 0.30, 60, "Pandas is a Python library — Python is required"),
        (31, 42, 0.25, 55, "NumPy is a Python library — Python is required"),
        (31, 43, 0.25, 55, "Matplotlib is a Python library — Python is required"),
        (31, 45, 0.20, 50, "Jupyter runs Python kernels"),
        (41, 39, 0.30, 60, "Pandas is the primary tool for data analysis"),
        (42, 39, 0.25, 55, "NumPy underlies most data analysis"),
        (39, 40, 0.30, 65, "You need data analysis skills to visualize meaningfully"),
        (43, 40, 0.25, 55, "Matplotlib is the primary visualization library"),

        # ── Data Science path ──────────────────────────────────────────────
        (36, 44, 0.45, 65, "scikit-learn requires stats knowledge"),
        (42, 44, 0.40, 60, "scikit-learn is NumPy-based"),
        (39, 44, 0.35, 60, "Data analysis skills needed to interpret ML output"),
        (36, 46, 0.55, 70, "ML is applied statistics"),
        (38, 46, 0.50, 65, "Linear algebra is the math foundation of ML models"),
        (44, 46, 0.40, 70, "scikit-learn is the gateway to ML in Python"),
        (46, 47, 0.60, 75, "Deep learning extends ML with neural networks"),
        (38, 47, 0.55, 70, "Neural nets require heavy linear algebra"),
        (46, 48, 0.55, 70, "NLP is a specialization of ML"),
        (46, 49, 0.55, 70, "Computer vision is a specialization of ML"),
        (46, 50, 0.50, 70, "MLOps requires understanding of ML workflows"),
        (59, 50, 0.45, 60, "Docker is core to MLOps deployment"),

        # ── Web development path ───────────────────────────────────────────
        (51, 52, 0.40, 60, "React requires HTML/CSS foundations"),
        (32, 52, 0.35, 55, "React is a JavaScript framework"),
        (32, 53, 0.40, 60, "Node/Express is server-side JavaScript"),
        (33, 54, 0.35, 55, "REST API design requires SQL knowledge"),
        (53, 54, 0.30, 60, "Building REST APIs with Node/Express"),
        (52, 55, 0.35, 60, "TypeScript extends JavaScript/React"),
        (32, 55, 0.30, 55, "TypeScript is a typed superset of JavaScript"),

        # ── Database path ──────────────────────────────────────────────────
        (33, 56, 0.30, 55, "PostgreSQL uses SQL — SQL knowledge required"),
        (33, 57, 0.35, 50, "MongoDB builds on DB concepts from SQL"),
        (56, 58, 0.40, 60, "Redis complements relational DB understanding"),

        # ── DevOps path ────────────────────────────────────────────────────
        (35, 59, 0.35, 55, "Docker relies heavily on Linux/Bash"),
        (59, 60, 0.40, 60, "Cloud deployment uses containers"),
        (34, 35, 0.25, 45, "Git version control goes hand-in-hand with Bash"),

        # ── BI & Analytics path ────────────────────────────────────────────
        (33, 61, 0.25, 50, "Excel advanced uses SQL-like logic"),
        (39, 62, 0.30, 55, "Tableau builds on data analysis fundamentals"),
        (39, 63, 0.30, 55, "Power BI builds on data analysis fundamentals"),
        (36, 64, 0.45, 65, "A/B testing requires statistical knowledge"),
        (64, 97, 0.35, 60, "Data-driven decisions come from A/B testing skills"),

        # ── Design path ────────────────────────────────────────────────────
        (71, 72, 0.40, 60, "UI design builds on visual design principles"),
        (72, 73, 0.35, 65, "UX design extends UI with research focus"),
        (74, 73, 0.40, 60, "User research is foundational to UX"),
        (73, 75, 0.35, 65, "Prototyping is a core UX deliverable"),
        (81, 72, 0.30, 55, "Figma is the primary UI design tool"),
        (81, 75, 0.25, 50, "Figma is used for prototyping"),
        (71, 76, 0.35, 55, "Graphic design extends visual design"),
        (5,  71, 0.30, 45, "Creativity is the foundation of visual design"),
        (85, 73, 0.35, 55, "Design thinking underpins UX methodology"),
        (15, 74, 0.30, 45, "Empathy is crucial for user research"),
        (74, 85, 0.30, 55, "User research informs design thinking"),

        # ── Business / leadership path ─────────────────────────────────────
        (3,  86, 0.40, 60, "Leadership demands strong communication"),
        (9,  86, 0.35, 55, "Teamwork experience precedes leadership"),
        (86, 87, 0.35, 65, "Leadership skills are needed for PM"),
        (88, 87, 0.30, 55, "Agile/Scrum is the standard PM methodology"),
        (87, 90, 0.40, 65, "Product management extends project management"),
        (73, 90, 0.40, 65, "UX design is core to product thinking"),
        (97, 90, 0.35, 60, "Data-driven decisions are central to product work"),
        (86, 89, 0.30, 60, "Stakeholder management requires leadership"),
        # Note: agile_scrum (88) is a methodology WITHIN project_management (87).
        # Edge direction: agile_scrum → project_management would create a cycle.
        # The correct direction is project_management → agile_scrum
        # (knowing PM basics lets you learn Agile/Scrum specifically).
        # Edge (87→88) already defined above; removed the reverse here.
        (92, 91, 0.40, 60, "Business strategy requires financial literacy"),
        (16, 91, 0.35, 55, "Decision-making is central to strategy"),

        # ── Foundational → Business ────────────────────────────────────────
        (3,  93, 0.30, 45, "Marketing requires communication skills"),
        (77, 93, 0.35, 55, "Copywriting is core to marketing"),
        (24, 77, 0.30, 50, "Storytelling translates to copywriting"),
    ]


# ─────────────────────────────────────────────────────────────────────────────
#  Graph Builder
# ─────────────────────────────────────────────────────────────────────────────

def create_foundational_graph() -> SkillGraph:
    """Instantiate the full 100-skill graph in memory."""
    nodes: Dict[int, SkillNode] = {}

    for category_name, skill_list in [
        ("foundational", _foundational()),
        ("technical",    _technical()),
        ("creative",     _creative()),
        ("business",     _business()),
    ]:
        for entry in skill_list:
            sid, name, hours, difficulty = entry
            nodes[sid] = SkillNode(
                skill_id=sid,
                skill_name=name,
                category=category_name,
                difficulty_level=difficulty,
                estimated_learning_hours=hours,
            )

    edges = [
        SkillEdge(
            source_id=src, target_id=tgt,
            weight=w, required_mastery=rm, rationale=reason,
        )
        for src, tgt, w, rm, reason in _edges()
    ]

    graph = SkillGraph(nodes=nodes, edges=edges)
    logger.info("Graph created — %s", graph.stats())
    return graph


# ─────────────────────────────────────────────────────────────────────────────
#  Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Build the initial LPO skill graph")
    parser.add_argument("--db", action="store_true", help="Also seed to PostgreSQL")
    parser.add_argument("--out", default=SKILL_GRAPH_PATH, help="JSON output path")
    args = parser.parse_args()

    graph = create_foundational_graph()

    # Always save JSON cache
    graph.save(args.out)
    print(f"✓ Graph saved → {args.out}")
    print(f"  Skills : {len(graph.nodes)}")
    print(f"  Edges  : {len(graph.edges)}")

    # Optionally seed to DB
    if args.db:
        from db import managed_connection
        with managed_connection() as conn:
            graph.save_to_db(conn)
        print("✓ Graph seeded to PostgreSQL")


if __name__ == "__main__":
    from typing import Dict
    main()
