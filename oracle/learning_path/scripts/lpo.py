#!/usr/bin/env python3
"""
lpo — DELPHOS Learning Path Optimizer · Developer CLI

Usage:
    python scripts/lpo.py <command> [options]

Commands:
    status          Show project structure and day completion status
    migrate         Run all pending DB migrations
    build-graph     Build and seed the 100-skill graph
    test-db         Test PostgreSQL connection
    run-day <N>     Print the checklist and run entry points for day N
    demo            Run the Maria / UX Designer demo
    validate        Validate graph integrity (no orphan edges, no cycles)
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ─── ANSI colours ──────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def ok(msg):    print(f"  {GREEN}✓{RESET}  {msg}")
def warn(msg):  print(f"  {YELLOW}⚠{RESET}  {msg}")
def err(msg):   print(f"  {RED}✗{RESET}  {msg}")
def info(msg):  print(f"  {BLUE}→{RESET}  {msg}")
def head(msg):  print(f"\n{BOLD}{msg}{RESET}")


# ─── Helpers ───────────────────────────────────────────────────────────────

def file_exists(rel_path: str) -> bool:
    return (ROOT / rel_path).exists()

def count_lines(rel_path: str) -> int:
    try:
        return len((ROOT / rel_path).read_text().splitlines())
    except Exception:
        return 0


# ─── Commands ──────────────────────────────────────────────────────────────

DAY_FILES = {
    1: [
        "learning_path/graph_schema.py",
        "learning_path/build_initial_graph.py",
        "data/skill_graph_v1.json",
        "migrations/001_extend_habilidades_catalogo.sql",
        "migrations/002_create_grafo_habilidades_aristas.sql",
    ],
    2: [
        "learning_path/graph_converter.py",
        "learning_path/career_database.py",
        "migrations/003_create_carreras_catalogo.sql",
        "migrations/004_create_habilidades_carrera.sql",
        "migrations/005_create_habilidades_usuario_maestria.sql",
    ],
    3: [
        "learning_path/gap_analyzer.py",
        "learning_path/urgency_calculator.py",
        "tests/test_day3_4.py",
    ],
    4: [
        "learning_path/efficiency_ranker.py",
        "learning_path/priority_scorer.py",
        "tests/test_day3_4.py",
    ],
    5: [
        "learning_path/task_schema.py",
        "learning_path/task_database.py",
        "learning_path/curriculum_generator.py",
        "learning_path/adaptive_engine.py",
        "migrations/006_create_rutas_aprendizaje.sql",
        "migrations/007_create_fases_ruta_aprendizaje.sql",
        "migrations/008_create_microtareas_lpo.sql",
        "migrations/009_create_progreso_microtarea_usuario.sql",
    ],
    6: [
        "learning_path/api.py",
        "learning_path/monitoring.py",
        "learning_path/demo.py",
        "tests/test_integration.py",
    ],
}

DAY_NAMES = {
    1: "Skill Graph Foundation",
    2: "Career Database + MindSpore Converter",
    3: "Gap Analysis + Urgency Calculator",
    4: "PageRank Efficiency + Priority Scorer",
    5: "Curriculum Generator + Adaptive Engine",
    6: "API + Integration + Testing",
}


def cmd_status(args):
    head("DELPHOS · Learning Path Optimizer — Sprint Status")
    print(f"  Root: {ROOT}\n")

    all_done = True
    for day in range(1, 7):
        files = DAY_FILES[day]
        done  = [f for f in files if file_exists(f)]
        pct   = int(len(done) / len(files) * 100)
        bar   = "█" * (pct // 10) + "░" * (10 - pct // 10)
        color = GREEN if pct == 100 else (YELLOW if pct > 0 else DIM)
        status = "✓ DONE" if pct == 100 else f"{pct}%"
        print(f"  Day {day}  [{color}{bar}{RESET}] {status:8}  {DAY_NAMES[day]}")
        if pct < 100:
            all_done = False
            missing = [f for f in files if not file_exists(f)]
            for f in missing[:3]:
                print(f"         {DIM}  missing: {f}{RESET}")
            if len(missing) > 3:
                print(f"         {DIM}  ... and {len(missing)-3} more{RESET}")

    print()
    if all_done:
        ok("All 6 days complete! Run: python scripts/lpo.py demo")
    else:
        info("Run 'python scripts/lpo.py run-day <N>' to build the next day")


def cmd_test_db(args):
    head("Testing PostgreSQL connection")
    try:
        from db import test_connection
        if test_connection():
            ok("Database connected successfully")
        else:
            err("Connection failed — check .env DB_* settings")
    except RuntimeError as e:
        warn(str(e))
        info("Install with: pip install psycopg2-binary")
    except Exception as e:
        err(f"Unexpected error: {e}")


def cmd_migrate(args):
    head("Running DB Migrations")
    migration_dir = ROOT / "migrations"
    sql_files = sorted(migration_dir.glob("*.sql"))

    if not sql_files:
        warn("No migration files found in migrations/")
        return

    for sql_file in sql_files:
        print(f"\n  → {sql_file.name}")
        # Print content preview
        content = sql_file.read_text()
        first_comment = next(
            (l.strip("- \n") for l in content.splitlines() if l.strip().startswith("--")),
            ""
        )
        if first_comment:
            print(f"    {DIM}{first_comment}{RESET}")

    print()
    info(f"To apply all migrations, run:")
    print(f"\n  {BOLD}for f in migrations/*.sql; do psql -d $DB_NAME -f \"$f\"; done{RESET}\n")
    info("Or apply individually:")
    for sql_file in sql_files:
        print(f"  psql -d $DB_NAME -f migrations/{sql_file.name}")


def cmd_build_graph(args):
    head("Building Skill Graph")
    script = ROOT / "learning_path" / "build_initial_graph.py"
    if not script.exists():
        err("learning_path/build_initial_graph.py not found")
        return

    cmd = [sys.executable, str(script)]
    if args.db:
        cmd.append("--db")

    info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode == 0:
        ok("Graph built successfully")
    else:
        err("Build failed — check output above")


def cmd_run_day(args):
    day = args.day
    if day not in DAY_NAMES:
        err(f"Day must be 1–6, got {day}")
        return

    head(f"Day {day}: {DAY_NAMES[day]}")
    print()

    files = DAY_FILES[day]
    print(f"  {BOLD}Files to create:{RESET}")
    for f in files:
        exists = file_exists(f)
        mark = f"{GREEN}✓{RESET}" if exists else f"{RED}✗{RESET}"
        print(f"    {mark}  {f}")

    print(f"\n  {BOLD}Suggested commands:{RESET}")
    if day == 1:
        print(f"    python learning_path/build_initial_graph.py")
        print(f"    python learning_path/build_initial_graph.py --db  (after migrations)")
    elif day == 2:
        print(f"    python learning_path/career_database.py")
        print(f"    python learning_path/graph_converter.py")
    elif day == 4:
        print(f"    python learning_path/efficiency_ranker.py")
    elif day == 6:
        print(f"    python scripts/lpo.py demo")

    print()
    info("Run 'python scripts/lpo.py validate' after Day 1 to check graph integrity")


def cmd_validate(args):
    head("Validating Skill Graph Integrity")
    from config import SKILL_GRAPH_PATH

    if not file_exists("data/skill_graph_v1.json"):
        err("data/skill_graph_v1.json not found — run build-graph first")
        return

    try:
        from learning_path.core.graph_schema import SkillGraph
        graph = SkillGraph.load(SKILL_GRAPH_PATH)

        # Check 1: No orphan edges
        orphan_edges = [
            e for e in graph.edges
            if e.source_id not in graph.nodes or e.target_id not in graph.nodes
        ]
        if orphan_edges:
            err(f"{len(orphan_edges)} orphan edges found (source/target not in nodes)")
            for e in orphan_edges[:5]:
                print(f"    {e.source_id} → {e.target_id}")
        else:
            ok(f"No orphan edges  ({len(graph.edges)} edges total)")

        # Check 2: Category distribution
        from collections import Counter
        cats = Counter(n.category for n in graph.nodes.values())
        ok(f"Category distribution: {dict(cats)}")

        # Check 3: Difficulty range
        difficulties = [n.difficulty_level for n in graph.nodes.values()]
        ok(f"Difficulty range: {min(difficulties):.2f} → {max(difficulties):.2f}")

        # Check 4: Cycle detection (basic)
        try:
            import networkx as nx
            G = nx.DiGraph()
            for e in graph.edges:
                G.add_edge(e.source_id, e.target_id)
            cycles = list(nx.simple_cycles(G))
            if cycles:
                err(f"{len(cycles)} cycles detected in graph!")
                for c in cycles[:3]:
                    names = [graph.nodes[n].skill_name for n in c if n in graph.nodes]
                    print(f"    {' → '.join(names)}")
            else:
                ok(f"No cycles detected — valid DAG  ({len(graph.nodes)} nodes)")
        except ImportError:
            warn("networkx not installed — skipping cycle detection")

        ok(f"Stats: {graph.stats()}")

    except Exception as e:
        err(f"Validation failed: {e}")
        import traceback
        traceback.print_exc()


def cmd_demo(args):
    head("Running LPO Demo")
    demo_script = ROOT / "learning_path" / "demo.py"
    if not demo_script.exists():
        err("learning_path/demo.py not found — complete Day 6 first")
        return
    result = subprocess.run([sys.executable, str(demo_script)], cwd=str(ROOT))
    if result.returncode != 0:
        err("Demo failed — check output above")


# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="lpo",
        description="DELPHOS Learning Path Optimizer · Developer CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status",      help="Show sprint progress")
    sub.add_parser("test-db",     help="Test PostgreSQL connection")
    sub.add_parser("migrate",     help="Show migration commands")
    sub.add_parser("validate",    help="Validate graph integrity")
    sub.add_parser("demo",        help="Run the Maria/UX Designer demo")

    p_graph = sub.add_parser("build-graph", help="Build and save the skill graph")
    p_graph.add_argument("--db", action="store_true", help="Also seed to PostgreSQL")

    p_day = sub.add_parser("run-day", help="Show Day N checklist")
    p_day.add_argument("day", type=int, choices=range(1, 7), metavar="N")

    args = parser.parse_args()

    dispatch = {
        "status":      cmd_status,
        "test-db":     cmd_test_db,
        "migrate":     cmd_migrate,
        "build-graph": cmd_build_graph,
        "run-day":     cmd_run_day,
        "validate":    cmd_validate,
        "demo":        cmd_demo,
    }

    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
