#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  fix_missing_files.sh
#  Run from the delphos_lpo root to create any missing config files.
#  Usage: bash scripts/fix_missing_files.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e
cd "$(dirname "$0")/.."   # always run from project root

GREEN='\033[0;32m'; RESET='\033[0m'
ok() { echo -e "  ${GREEN}✓${RESET}  $1"; }

# ── requirements.txt ─────────────────────────────────────────────────────────
cat > requirements.txt << 'REQUIREMENTS'
# ── Core graph & math ─────────────────────────────────
networkx>=3.2
numpy>=1.26

# ── Database ──────────────────────────────────────────
psycopg2-binary>=2.9

# ── Config & utilities ────────────────────────────────
python-dotenv>=1.0
rich>=13.0
click>=8.1

# ── Testing ───────────────────────────────────────────
pytest>=8.0
pytest-cov>=4.0

# ── Optional: MindSpore (manual install)
# mindspore>=2.2.0
REQUIREMENTS
ok "requirements.txt"

# ── .env.example ─────────────────────────────────────────────────────────────
cat > .env.example << 'ENVEXAMPLE'
# ─────────────────────────────────────────────────────
#  DELPHOS · Learning Path Optimizer — Config
#  cp .env.example .env  then fill in your values
# ─────────────────────────────────────────────────────

# ── Database ──────────────────────────────────────────
DB_HOST=localhost
DB_PORT=5432
DB_NAME=delphos
DB_USER=delphos_user
DB_PASSWORD=your_password_here

# ── LPO Settings ──────────────────────────────────────
LPO_SKILL_GRAPH_PATH=data/skill_graph_v1.json
LPO_DAMPING_FACTOR=0.85
LPO_PAGERANK_ITERATIONS=10
LPO_PAGERANK_TOLERANCE=1e-6
LPO_MIN_TASK_MINUTES=20
LPO_MAX_TASK_MINUTES=60
LPO_CAREER_READY_DAYS=90

# ── Adaptive Engine Thresholds ─────────────────────────
LPO_SKIP_THRESHOLD=85
LPO_REINFORCE_THRESHOLD=60

# ── MindSpore (optional) ──────────────────────────────
USE_MINDSPORE=0
MINDSPORE_DEVICE=CPU

# ── Logging ───────────────────────────────────────────
LOG_LEVEL=INFO
LOG_FILE=logs/lpo.log
ENVEXAMPLE
ok ".env.example"

# ── .env (only if it doesn't already exist) ───────────────────────────────────
if [ ! -f ".env" ]; then
    cp .env.example .env
    ok ".env  (created from .env.example — edit DB credentials)"
else
    ok ".env  (already exists, not overwritten)"
fi

# ── Ensure data/ and logs/ directories exist ─────────────────────────────────
mkdir -p data logs
ok "data/  and  logs/  directories"

echo ""
echo "All files present. Re-run setup:"
echo "  chmod +x setup.sh && ./setup.sh"
