"""
config.py — Centralized settings for the Learning Path Optimizer.
Reads from environment variables (or .env file if python-dotenv is installed).
"""

import os
import logging

# ── Try to load .env file (optional dependency) ────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env not loaded; rely on real environment variables


# ── Database ────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "dbname":   os.getenv("DB_NAME", "delphos"),
    "user":     os.getenv("DB_USER", "delphos_user"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# ── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR              = os.path.dirname(os.path.abspath(__file__))
SKILL_GRAPH_PATH      = os.path.join(BASE_DIR, os.getenv("LPO_SKILL_GRAPH_PATH", "data/skill_graph_v1.json"))
LOG_FILE              = os.path.join(BASE_DIR, os.getenv("LOG_FILE", "logs/lpo.log"))

# ── PageRank ─────────────────────────────────────────────────────────────────
DAMPING_FACTOR        = float(os.getenv("LPO_DAMPING_FACTOR", 0.85))
PAGERANK_ITERATIONS   = int(os.getenv("LPO_PAGERANK_ITERATIONS", 100))
PAGERANK_TOLERANCE    = float(os.getenv("LPO_PAGERANK_TOLERANCE", 1e-6))

# ── Task sizing ─────────────────────────────────────────────────────────────
MIN_TASK_MINUTES      = int(os.getenv("LPO_MIN_TASK_MINUTES", 20))
MAX_TASK_MINUTES      = int(os.getenv("LPO_MAX_TASK_MINUTES", 60))
CAREER_READY_DAYS     = int(os.getenv("LPO_CAREER_READY_DAYS", 90))

# ── Adaptive engine ─────────────────────────────────────────────────────────
SKIP_THRESHOLD        = int(os.getenv("LPO_SKIP_THRESHOLD", 85))
REINFORCE_THRESHOLD   = int(os.getenv("LPO_REINFORCE_THRESHOLD", 60))

# ── Logging ─────────────────────────────────────────────────────────────────
LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)

logger = logging.getLogger("lpo.config")
logger.debug("Config loaded. DB=%s@%s/%s", DB_CONFIG["user"], DB_CONFIG["host"], DB_CONFIG["dbname"])
