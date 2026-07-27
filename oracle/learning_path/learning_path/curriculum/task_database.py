"""
task_database.py — Micro-task library for the LPO.

120+ hand-curated tasks covering all 12 careers.
Each task: 20–60 min, targets a specific skill, has a difficulty level
and an expected mastery gain.

Run:
    python learning_path/task_database.py            # show stats
    python learning_path/task_database.py --db       # seed to PostgreSQL
"""

import sys
import os
import argparse
import logging
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
logger = logging.getLogger("lpo.task_database")

# ─────────────────────────────────────────────────────────────────────────────
#  Task format:
#  (skill_id, title, type, difficulty, duration_min, skill_gain, resource_url)
#  type: lectura | practica | quiz | proyecto | video | ejercicio
# ─────────────────────────────────────────────────────────────────────────────

TASKS = [

    # ── UX Research (skill 74) ───────────────────────────────────────────────
    (74, "What is User Research? Core Methods Overview",
     "lectura", 0.20, 25, 5.0, "https://www.nngroup.com/articles/which-ux-research-methods/"),
    (74, "Write 5 User Interview Questions for a Mobile App",
     "practica", 0.35, 35, 8.0, None),
    (74, "Conduct a 15-Minute Guerrilla Usability Test",
     "practica", 0.45, 45, 10.0, None),
    (74, "Build a User Persona from Interview Notes",
     "practica", 0.50, 40, 9.0, None),
    (74, "Analyze Survey Results: Affinity Mapping Exercise",
     "practica", 0.60, 50, 10.0, None),
    (74, "User Research Methods Quiz",
     "quiz", 0.40, 20, 6.0, None),
    (74, "Write a Research Brief for a Feature Launch",
     "proyecto", 0.65, 60, 12.0, None),

    # ── UX Design (skill 73) ─────────────────────────────────────────────────
    (73, "UX Design Fundamentals: The 5 Stages of Design Thinking",
     "lectura", 0.20, 25, 5.0, "https://www.interaction-design.org/literature/topics/design-thinking"),
    (73, "Map a User Journey for an E-commerce Checkout Flow",
     "practica", 0.40, 40, 8.0, None),
    (73, "Redesign a Confusing UI: Before & After Analysis",
     "practica", 0.55, 50, 10.0, None),
    (73, "Define Information Architecture for a 10-Page App",
     "practica", 0.60, 45, 9.0, None),
    (73, "UX Heuristics Audit: Evaluate an Existing Product",
     "practica", 0.65, 55, 11.0, None),
    (73, "UX Design Principles Quiz",
     "quiz", 0.35, 20, 5.0, None),
    (73, "End-to-End UX Case Study: Problem → Prototype",
     "proyecto", 0.75, 60, 13.0, None),

    # ── Prototyping (skill 75) ────────────────────────────────────────────────
    (75, "Intro to Figma: Frames, Components, and Auto Layout",
     "video", 0.25, 30, 6.0, "https://www.figma.com/resources/learn-design/"),
    (75, "Build a 3-Screen Low-Fidelity Wireframe in Figma",
     "practica", 0.35, 40, 8.0, None),
    (75, "Add Interactions: Create a Clickable Prototype",
     "practica", 0.50, 45, 9.0, None),
    (75, "High-Fidelity Prototype: Login + Dashboard Flow",
     "proyecto", 0.70, 60, 12.0, None),

    # ── UI Design (skill 72) ──────────────────────────────────────────────────
    (72, "Typography in UI: Choosing Fonts & Hierarchy",
     "lectura", 0.25, 25, 5.0, "https://material.io/design/typography/"),
    (72, "Color Theory for Digital Interfaces",
     "lectura", 0.30, 30, 6.0, None),
    (72, "Build a UI Component Library in Figma",
     "practica", 0.55, 50, 10.0, None),
    (72, "Dark Mode & Accessibility: Redesign a Dashboard",
     "practica", 0.65, 55, 11.0, None),
    (72, "UI Design Quiz: Spacing, Grids, and Patterns",
     "quiz", 0.40, 20, 5.0, None),

    # ── Python (skill 31) ─────────────────────────────────────────────────────
    (31, "Python Basics: Variables, Types, and Control Flow",
     "ejercicio", 0.20, 30, 7.0, "https://docs.python.org/3/tutorial/"),
    (31, "Functions and Modules in Python",
     "ejercicio", 0.30, 35, 7.0, None),
    (31, "Object-Oriented Python: Classes and Inheritance",
     "ejercicio", 0.50, 45, 8.0, None),
    (31, "File I/O and Exception Handling",
     "ejercicio", 0.45, 35, 7.0, None),
    (31, "Build a Command-Line To-Do App in Python",
     "proyecto", 0.55, 60, 12.0, None),
    (31, "Python Fundamentals Quiz",
     "quiz", 0.35, 20, 5.0, None),

    # ── Statistics (skill 36) ─────────────────────────────────────────────────
    (36, "Descriptive Statistics: Mean, Median, Variance",
     "ejercicio", 0.25, 30, 7.0, "https://www.khanacademy.org/math/statistics-probability"),
    (36, "Probability Distributions: Normal, Binomial, Poisson",
     "lectura", 0.55, 40, 8.0, None),
    (36, "Hypothesis Testing: t-test and p-values",
     "ejercicio", 0.65, 45, 9.0, None),
    (36, "Correlation vs Causation: 5 Real Dataset Examples",
     "practica", 0.50, 35, 7.0, None),
    (36, "Statistics Quiz: Inference and Confidence Intervals",
     "quiz", 0.60, 25, 6.0, None),
    (36, "A/B Test Analysis: Calculate Statistical Significance",
     "proyecto", 0.70, 55, 11.0, None),

    # ── SQL (skill 33) ────────────────────────────────────────────────────────
    (33, "SQL Basics: SELECT, WHERE, ORDER BY",
     "ejercicio", 0.20, 25, 6.0, "https://sqlzoo.net/"),
    (33, "JOINs Explained: INNER, LEFT, RIGHT, FULL",
     "ejercicio", 0.40, 35, 8.0, None),
    (33, "Aggregate Functions: GROUP BY, HAVING, COUNT, SUM",
     "ejercicio", 0.45, 35, 8.0, None),
    (33, "Subqueries and CTEs (WITH clauses)",
     "ejercicio", 0.60, 40, 9.0, None),
    (33, "Window Functions: ROW_NUMBER, RANK, LAG",
     "ejercicio", 0.70, 45, 9.0, None),
    (33, "SQL Query Optimization: EXPLAIN and Indexes",
     "lectura", 0.75, 40, 8.0, None),

    # ── Data Analysis (skill 39) ──────────────────────────────────────────────
    (39, "Exploratory Data Analysis with Pandas: Dataset Audit",
     "ejercicio", 0.35, 35, 8.0, None),
    (39, "Data Cleaning: Handle Missing Values and Outliers",
     "ejercicio", 0.45, 40, 8.0, None),
    (39, "Pivot Tables and Group Analysis in Python",
     "ejercicio", 0.50, 35, 7.0, None),
    (39, "Build a Sales Performance Dashboard (Jupyter)",
     "proyecto", 0.65, 60, 12.0, None),
    (39, "Data Analysis Quiz: Pandas and NumPy Patterns",
     "quiz", 0.50, 25, 6.0, None),

    # ── Data Visualization (skill 40) ─────────────────────────────────────────
    (40, "Chart Types and When to Use Them",
     "lectura", 0.20, 25, 5.0, "https://www.data-to-viz.com/"),
    (40, "Matplotlib: Line, Bar, Scatter, and Histogram",
     "ejercicio", 0.35, 35, 7.0, None),
    (40, "Seaborn: Statistical Visualization in 30 Minutes",
     "ejercicio", 0.45, 35, 7.0, None),
    (40, "Build an Interactive Dashboard with Plotly",
     "proyecto", 0.65, 55, 11.0, None),

    # ── Machine Learning (skill 46) ───────────────────────────────────────────
    (46, "ML Concepts: Supervised vs Unsupervised Learning",
     "lectura", 0.40, 30, 6.0, "https://scikit-learn.org/stable/tutorial/"),
    (46, "Linear Regression: Predict House Prices",
     "ejercicio", 0.50, 45, 9.0, None),
    (46, "Classification with Logistic Regression",
     "ejercicio", 0.60, 45, 9.0, None),
    (46, "Decision Trees and Random Forests",
     "ejercicio", 0.65, 50, 10.0, None),
    (46, "Model Evaluation: Accuracy, Precision, Recall, F1",
     "ejercicio", 0.65, 40, 8.0, None),
    (46, "End-to-End ML Project: Churn Prediction",
     "proyecto", 0.80, 60, 14.0, None),

    # ── JavaScript (skill 32) ─────────────────────────────────────────────────
    (32, "JavaScript Fundamentals: Variables, Functions, Scope",
     "ejercicio", 0.20, 30, 7.0, "https://javascript.info/"),
    (32, "Arrays and Objects: Map, Filter, Reduce",
     "ejercicio", 0.35, 35, 7.0, None),
    (32, "Async JavaScript: Promises and Async/Await",
     "ejercicio", 0.55, 40, 8.0, None),
    (32, "DOM Manipulation: Build a Dynamic To-Do List",
     "practica", 0.50, 45, 9.0, None),
    (32, "Fetch API: Call a REST Endpoint and Render Data",
     "practica", 0.60, 40, 8.0, None),

    # ── React (skill 52) ──────────────────────────────────────────────────────
    (52, "React Core Concepts: Components, Props, State",
     "video", 0.35, 35, 7.0, "https://react.dev/learn"),
    (52, "React Hooks: useState, useEffect, useContext",
     "ejercicio", 0.55, 45, 9.0, None),
    (52, "Build a Product Listing Page with Filter & Sort",
     "practica", 0.65, 55, 11.0, None),
    (52, "State Management: Intro to React Query",
     "ejercicio", 0.70, 45, 9.0, None),
    (52, "Full Feature: User Auth Flow in React",
     "proyecto", 0.80, 60, 13.0, None),

    # ── REST API Design (skill 54) ────────────────────────────────────────────
    (54, "REST Principles: Resources, Verbs, Status Codes",
     "lectura", 0.30, 25, 6.0, "https://restfulapi.net/"),
    (54, "Design a REST API for a Blog Platform",
     "practica", 0.50, 40, 9.0, None),
    (54, "API Security: JWT Authentication and Rate Limiting",
     "lectura", 0.65, 35, 7.0, None),
    (54, "OpenAPI/Swagger: Document Your API",
     "practica", 0.60, 40, 8.0, None),

    # ── Project Management (skill 87) ─────────────────────────────────────────
    (87, "PM Fundamentals: Scope, Schedule, Budget Triangle",
     "lectura", 0.25, 25, 5.0, None),
    (87, "Write a Project Charter for a Mobile App Launch",
     "practica", 0.45, 40, 8.0, None),
    (87, "Build a Gantt Chart: 3-Month Roadmap",
     "practica", 0.55, 45, 9.0, None),
    (87, "Risk Register: Identify and Mitigate 10 Project Risks",
     "practica", 0.60, 40, 8.0, None),
    (87, "PM Quiz: Critical Path, Float, and Milestones",
     "quiz", 0.50, 20, 5.0, None),

    # ── Agile/Scrum (skill 88) ────────────────────────────────────────────────
    (88, "Scrum Framework: Roles, Events, and Artifacts",
     "lectura", 0.20, 25, 6.0, "https://scrumguides.org/"),
    (88, "Write 10 User Stories with Acceptance Criteria",
     "practica", 0.40, 35, 8.0, None),
    (88, "Run a Sprint Planning Session: Backlog Refinement",
     "practica", 0.55, 45, 9.0, None),
    (88, "Agile Retrospective: 3 Formats Compared",
     "lectura", 0.40, 25, 5.0, None),
    (88, "Agile Quiz: Velocity, Burndown, and Kanban",
     "quiz", 0.45, 20, 5.0, None),

    # ── Leadership (skill 86) ─────────────────────────────────────────────────
    (86, "Leadership Styles: Situational Leadership Model",
     "lectura", 0.30, 25, 5.0, None),
    (86, "Give Structured Feedback Using the SBI Model",
     "practica", 0.45, 35, 7.0, None),
    (86, "Lead a Team Meeting: Facilitation Techniques",
     "practica", 0.55, 40, 8.0, None),
    (86, "Delegation: Assign Work and Track Accountability",
     "practica", 0.60, 40, 8.0, None),

    # ── Marketing (skill 93) ──────────────────────────────────────────────────
    (93, "Marketing Fundamentals: 4Ps and Customer Journey",
     "lectura", 0.20, 25, 5.0, None),
    (93, "Define a Target Audience: ICP Template",
     "practica", 0.35, 35, 7.0, None),
    (93, "SEO Basics: On-Page Optimization Checklist",
     "practica", 0.45, 40, 8.0, None),
    (93, "Build a Content Calendar for 1 Month",
     "practica", 0.55, 45, 9.0, None),
    (93, "Email Campaign: Write 3 Subject Line Variants",
     "practica", 0.50, 35, 7.0, None),

    # ── Copywriting (skill 77) ────────────────────────────────────────────────
    (77, "Copywriting Fundamentals: AIDA and PAS Frameworks",
     "lectura", 0.20, 25, 6.0, None),
    (77, "Write 3 Product Description Variants",
     "practica", 0.35, 30, 7.0, None),
    (77, "Landing Page Copy: Above-the-Fold in 50 Words",
     "practica", 0.50, 35, 8.0, None),
    (77, "Write a 300-Word Blog Intro That Hooks Readers",
     "practica", 0.55, 40, 8.0, None),
    (77, "Copywriting Quiz: Headlines and CTAs",
     "quiz", 0.40, 20, 5.0, None),

    # ── Content Strategy (skill 78) ───────────────────────────────────────────
    (78, "Content Strategy Canvas: Audience, Goals, Channels",
     "practica", 0.40, 40, 8.0, None),
    (78, "Content Audit: Evaluate 10 Existing Pieces",
     "practica", 0.55, 45, 9.0, None),
    (78, "Build a 90-Day Content Roadmap",
     "proyecto", 0.70, 60, 12.0, None),

    # ── Communication (skill 3) ───────────────────────────────────────────────
    (3, "Structured Communication: Pyramid Principle",
     "lectura", 0.20, 25, 5.0, None),
    (3, "Write a Clear Project Status Update (3-paragraph format)",
     "practica", 0.30, 30, 6.0, None),
    (3, "Presentation Skills: Structure a 5-Minute Pitch",
     "practica", 0.45, 40, 8.0, None),

    # ── Docker (skill 59) ─────────────────────────────────────────────────────
    (59, "Docker Concepts: Images, Containers, Volumes",
     "lectura", 0.30, 30, 6.0, "https://docs.docker.com/get-started/"),
    (59, "Dockerize a Python Flask App",
     "ejercicio", 0.55, 45, 10.0, None),
    (59, "Docker Compose: Multi-Container Dev Environment",
     "ejercicio", 0.70, 50, 10.0, None),

    # ── Git (skill 34) ────────────────────────────────────────────────────────
    (34, "Git Basics: Commit, Branch, Merge",
     "ejercicio", 0.20, 25, 6.0, "https://learngitbranching.js.org/"),
    (34, "Git Workflow: Feature Branches and Pull Requests",
     "ejercicio", 0.40, 35, 7.0, None),
    (34, "Resolving Merge Conflicts: 3 Scenarios",
     "ejercicio", 0.55, 35, 7.0, None),
]


# ─────────────────────────────────────────────────────────────────────────────
#  In-memory helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_tasks_for_skill(
    skill_id:      int,
    user_mastery:  float,    # 0–100
    limit:         int = 7,
) -> list:
    """
    Return up to `limit` tasks for a skill, ordered by difficulty.
    Difficulty window: [user_mastery/100 - 0.15, user_mastery/100 + 0.25]
    Clamped to [0.0, 1.0].
    """
    target_diff = user_mastery / 100.0
    lower = max(0.0, target_diff - 0.15)
    upper = min(1.0, target_diff + 0.25)

    matching = [
        t for t in TASKS
        if t[0] == skill_id and lower <= t[3] <= upper
    ]
    # Fall back to all tasks for that skill if window is too narrow
    if len(matching) < 2:
        matching = [t for t in TASKS if t[0] == skill_id]

    matching.sort(key=lambda t: t[3])   # sort by difficulty ascending
    return matching[:limit]


def get_tasks_dict() -> Dict[int, list]:
    """Return all tasks grouped by skill_id."""
    result: Dict[int, list] = {}
    for task in TASKS:
        result.setdefault(task[0], []).append(task)
    return result


def covered_skills() -> list:
    """Return sorted list of skill_ids that have at least one task."""
    return sorted({t[0] for t in TASKS})


# ─────────────────────────────────────────────────────────────────────────────
#  DB seeder
# ─────────────────────────────────────────────────────────────────────────────

def seed_tasks_to_db(conn):
    """Upsert all tasks to microtareas_lpo. Safe to re-run."""
    from db import get_cursor
    with get_cursor(conn, dict_cursor=False) as cur:
        for t in TASKS:
            skill_id, title, tipo, diff, mins, gain, url = t
            cur.execute("""
                INSERT INTO microtareas_lpo
                    (habilidad_id, titulo, descripcion, tipo_tarea,
                     nivel_dificultad, duracion_minutos, ganancia_maestria,
                     url_recurso, esta_activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                ON CONFLICT DO NOTHING
            """, (skill_id, title, title, tipo, diff, mins, gain, url))
    logger.info("Seeded %d tasks to DB", len(TASKS))
    print(f"✓ {len(TASKS)} tasks seeded to microtareas_lpo")


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    from collections import Counter
    parser = argparse.ArgumentParser(description="DELPHOS LPO — Task Database")
    parser.add_argument("--db", action="store_true", help="Seed to PostgreSQL")
    args = parser.parse_args()

    print(f"\nDELPHOS LPO — Task Database\n")
    print(f"  Total tasks : {len(TASKS)}")
    print(f"  Skills covered: {len(covered_skills())}")

    by_type = Counter(t[2] for t in TASKS)
    print(f"\n  By type:")
    for tipo, count in sorted(by_type.items()):
        print(f"    {tipo:<12} {count:>4}")

    print(f"\n  Sample — UX Research (skill 74), mastery=45:")
    for t in get_tasks_for_skill(74, 45.0, limit=4):
        print(f"    [{t[3]:.2f}] {t[1][:50]}  ({t[4]}min, +{t[5]}pts)")
    print()

    if args.db:
        from db import managed_connection
        with managed_connection() as conn:
            seed_tasks_to_db(conn)


if __name__ == "__main__":
    main()
