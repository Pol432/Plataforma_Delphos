#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  DELPHOS · Learning Path Optimizer — One-Shot Setup
#
#  Usage:
#    chmod +x setup.sh && ./setup.sh
#
#  What it does:
#    1. Checks Python version
#    2. Creates a virtual environment (.venv)
#    3. Installs dependencies
#    4. Copies .env.example → .env  (if .env doesn't exist)
#    5. Creates required directories
#    6. Runs the Day 1 graph builder
#    7. Prints next steps
# ─────────────────────────────────────────────────────────────────────────────

set -e  # Exit immediately on any error

# ── Colours ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'
BOLD='\033[1m'; RESET='\033[0m'

ok()   { echo -e "  ${GREEN}✓${RESET}  $1"; }
warn() { echo -e "  ${YELLOW}⚠${RESET}  $1"; }
err()  { echo -e "  ${RED}✗${RESET}  $1"; exit 1; }
info() { echo -e "  ${BLUE}→${RESET}  $1"; }
head() { echo -e "\n${BOLD}$1${RESET}"; }

# ─────────────────────────────────────────────────────────────────────────────
head "DELPHOS · Learning Path Optimizer — Setup"
echo -e "  Root: $(pwd)\n"

# ── 1. Python version check ───────────────────────────────────────────────────
head "1/7  Checking Python"
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    err "Python 3 not found. Install Python 3.10+ from https://python.org"
fi
PY_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
PY_MAJOR=$(echo $PY_VERSION | cut -d. -f1)
PY_MINOR=$(echo $PY_VERSION | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]); then
    err "Python 3.10+ required. Found $PY_VERSION"
fi
ok "Python $PY_VERSION"

# ── 2. Virtual environment ────────────────────────────────────────────────────
head "2/7  Virtual Environment"
if [ ! -d ".venv" ]; then
    $PYTHON -m venv .venv
    ok "Created .venv"
else
    ok ".venv already exists"
fi

# Activate
source .venv/bin/activate
ok "Activated .venv"

# ── 3. Install dependencies ───────────────────────────────────────────────────
head "3/7  Installing Dependencies"
pip install --upgrade pip -q
pip install -r requirements.txt -q
ok "All dependencies installed"
warn "MindSpore NOT installed (optional). See: https://www.mindspore.cn/install"
info "NetworkX PageRank fallback will be used until MindSpore is configured"

# ── 4. Environment config ─────────────────────────────────────────────────────
head "4/7  Environment Config"
if [ ! -f ".env" ]; then
    cp .env.example .env
    ok ".env created from .env.example"
    warn "Edit .env with your PostgreSQL credentials before running --db commands"
else
    ok ".env already exists"
fi

# ── 5. Directory structure ────────────────────────────────────────────────────
head "5/7  Directory Structure"
mkdir -p data logs
ok "data/  and  logs/  ready"

# ── 6. Build initial graph ────────────────────────────────────────────────────
head "6/7  Building Skill Graph (Day 1)"
python learning_path/build_initial_graph.py
ok "Skill graph saved → data/skill_graph_v1.json"

# ── 7. Validate ───────────────────────────────────────────────────────────────
head "7/7  Validating Graph"
python scripts/lpo.py validate

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  Setup complete!${RESET}"
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "  ${BOLD}Next steps:${RESET}"
echo ""
echo -e "  1. Edit .env with your PostgreSQL credentials"
echo -e "  2. Apply DB migrations:"
echo -e "     ${BOLD}for f in migrations/*.sql; do psql -d \$DB_NAME -f \"\$f\"; done${RESET}"
echo -e "  3. Seed graph to DB:"
echo -e "     ${BOLD}python learning_path/build_initial_graph.py --db${RESET}"
echo -e "  4. Check sprint progress:"
echo -e "     ${BOLD}python scripts/lpo.py status${RESET}"
echo -e "  5. Start Day 2:"
echo -e "     ${BOLD}python scripts/lpo.py run-day 2${RESET}"
echo ""
echo -e "  ${BLUE}CLI reference:${RESET}  python scripts/lpo.py --help"
echo ""
