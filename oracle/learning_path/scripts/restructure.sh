#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  restructure.sh  —  Reorganise delphos_lpo into a layered package structure.
#  Run once from the project root:
#      bash scripts/restructure.sh
#
#  Before:   learning_path/  (15 files, all flat)
#  After:    learning_path/
#               core/        graph layer
#               careers/     career definitions
#               engine/      AI scoring pipeline
#               curriculum/  tasks + path generation + adaptive
#            scripts/demo.py (moved out of the package)
# ─────────────────────────────────────────────────────────────────────────────
set -e
cd "$(dirname "$0")/.."   # always run from project root

GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RESET='\033[0m'
ok()   { echo -e "  ${GREEN}✓${RESET}  $1"; }
warn() { echo -e "  ${YELLOW}⚠${RESET}  $1"; }

echo ""
echo "DELPHOS LPO — Restructure"
echo ""

# ── 1. Guard: don't run twice ─────────────────────────────────────────────────
if [ -d "learning_path/core" ]; then
    warn "learning_path/core/ already exists — restructure already applied."
    exit 0
fi

# ── 2. Create subpackage directories ──────────────────────────────────────────
mkdir -p learning_path/{core,careers,engine,curriculum}
ok "Directories created"

# ── 3. Move files into their new homes ────────────────────────────────────────
mv learning_path/graph_schema.py          learning_path/core/
mv learning_path/graph_converter.py       learning_path/core/
mv learning_path/build_initial_graph.py   learning_path/core/

mv learning_path/career_database.py       learning_path/careers/

mv learning_path/gap_analyzer.py          learning_path/engine/
mv learning_path/urgency_calculator.py    learning_path/engine/
mv learning_path/efficiency_ranker.py     learning_path/engine/
mv learning_path/priority_scorer.py       learning_path/engine/

mv learning_path/task_schema.py           learning_path/curriculum/
mv learning_path/task_database.py         learning_path/curriculum/
mv learning_path/curriculum_generator.py  learning_path/curriculum/
mv learning_path/adaptive_engine.py       learning_path/curriculum/

mv learning_path/demo.py                  scripts/
ok "Files moved"

# ── 4. Run the Python import-fixer ────────────────────────────────────────────
python3 - << 'PYEOF'
import os, re
from pathlib import Path

ROOT = Path(".")

# ── Mapping: old flat import → new layered import ─────────────────────────────
IMPORT_MAP = {
    "learning_path.graph_schema":        "learning_path.core.graph_schema",
    "learning_path.graph_converter":     "learning_path.core.graph_converter",
    "learning_path.build_initial_graph": "learning_path.core.build_initial_graph",
    "learning_path.career_database":     "learning_path.careers.career_database",
    "learning_path.gap_analyzer":        "learning_path.engine.gap_analyzer",
    "learning_path.urgency_calculator":  "learning_path.engine.urgency_calculator",
    "learning_path.efficiency_ranker":   "learning_path.engine.efficiency_ranker",
    "learning_path.priority_scorer":     "learning_path.engine.priority_scorer",
    "learning_path.task_schema":         "learning_path.curriculum.task_schema",
    "learning_path.task_database":       "learning_path.curriculum.task_database",
    "learning_path.curriculum_generator":"learning_path.curriculum.curriculum_generator",
    "learning_path.adaptive_engine":     "learning_path.curriculum.adaptive_engine",
}

# Files one level deeper than before → need one extra dirname() call
DEEP_DIRS = {"core", "careers", "engine", "curriculum"}

OLD_SYSPATH = "os.path.dirname(os.path.dirname(os.path.abspath(__file__)))"
NEW_SYSPATH = "os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"

updated = []
for py in ROOT.rglob("*.py"):
    if any(skip in str(py) for skip in [".venv", "__pycache__", "restructure"]):
        continue

    text = py.read_text(encoding="utf-8")
    original = text

    # Fix sys.path depth for files that moved one folder deeper
    if py.parent.name in DEEP_DIRS and py.parent.parent.name == "learning_path":
        text = text.replace(OLD_SYSPATH, NEW_SYSPATH)

    # Fix import statements
    for old, new in IMPORT_MAP.items():
        # Handles both: "from X import" and (rare) "import X"
        text = text.replace(f"from {old} import", f"from {new} import")
        text = text.replace(f"import {old}\n",     f"import {new}\n")

    if text != original:
        py.write_text(text, encoding="utf-8")
        updated.append(str(py))

print(f"    Fixed imports in {len(updated)} file(s):")
for f in sorted(updated):
    print(f"      {f}")
PYEOF
ok "Imports updated"

# ── 5. Write __init__.py files for each subpackage ────────────────────────────

# core
cat > learning_path/core/__init__.py << 'EOF'
"""
learning_path.core — Skill graph foundation.

    graph_schema.py       SkillNode, SkillEdge, SkillGraph
    graph_converter.py    NetworkX DiGraph + NumPy adjacency matrix
    build_initial_graph.py  Seed the 100-skill DAG
"""
from learning_path.core.graph_schema import SkillNode, SkillEdge, SkillGraph
from learning_path.core.graph_converter import (
    to_networkx, to_adjacency_matrix, convert,
)
EOF

# careers
cat > learning_path/careers/__init__.py << 'EOF'
"""
learning_path.careers — Career definitions and requirements.

    career_database.py    12 careers, skill requirements, DB seeder
"""
from learning_path.careers.career_database import (
    CAREERS,
    get_career_by_slug,
    get_career_requirements,
    get_critical_skills,
    list_slugs,
)
EOF

# engine
cat > learning_path/engine/__init__.py << 'EOF'
"""
learning_path.engine — AI scoring pipeline.

    gap_analyzer.py        Gap = required − current mastery
    urgency_calculator.py  Urgency multipliers (critical / large / small)
    efficiency_ranker.py   PageRank gateway scoring (NumPy power iteration)
    priority_scorer.py     Gap × Efficiency × Urgency
"""
from learning_path.engine.gap_analyzer import (
    SkillGap,
    calculate_gaps,
    gaps_only,
    is_career_ready,
    career_readiness_pct,
)
from learning_path.engine.urgency_calculator import (
    calculate_urgency,
    calculate_all_urgencies,
)
from learning_path.engine.efficiency_ranker import calculate_efficiency
from learning_path.engine.priority_scorer import (
    PriorityScore,
    calculate_priorities,
    top_skills_to_learn,
)
EOF

# curriculum
cat > learning_path/curriculum/__init__.py << 'EOF'
"""
learning_path.curriculum — Task library, path generation, and adaptive engine.

    task_schema.py          TaskItem, LearningPhase, LearningPath
    task_database.py        120+ micro-tasks + DB seeder
    curriculum_generator.py Assemble phases from priority list
    adaptive_engine.py      Score-based adaptation (skip / reinforce)
"""
from learning_path.curriculum.task_schema import (
    TaskItem, LearningPhase, LearningPath,
)
from learning_path.curriculum.curriculum_generator import (
    generate_curriculum,
    unlock_next_phase,
)
from learning_path.curriculum.adaptive_engine import (
    CompletionResult,
    handle_task_completion,
)
EOF

ok "__init__.py files written"

# ── 6. Update learning_path/__init__.py docstring ─────────────────────────────
cat > learning_path/__init__.py << 'EOF'
"""
learning_path — DELPHOS Learning Path Optimizer package.

Subpackage layout:

  core/         Skill graph foundation (schema, converter, graph builder)
  careers/      Career definitions and DB seeder
  engine/       AI scoring pipeline (gap → urgency → efficiency → priority)
  curriculum/   Task library, path generator, and adaptive engine

Public API (the only surface DELPHOS needs to call):
  from learning_path.api import generate_path, get_current_task, complete_task
"""
EOF

ok "learning_path/__init__.py updated"

# ── 7. Verify structure ────────────────────────────────────────────────────────
echo ""
echo "  New structure:"
find learning_path -name "*.py" ! -path "*__pycache__*" | sort | sed 's/^/    /'
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Restructure complete."
echo "  Run tests to verify:  python tests/test_integration.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
