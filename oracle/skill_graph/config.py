import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ── Ensure temporal_graph/ is always on sys.path ──────────────────────────
_THIS_DIR = Path(__file__).resolve().parent   # .../workspace/temporal_graph
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

# ── Find .env walking up from this file ───────────────────────────────────
def _find_env() -> Path | None:
    for parent in [_THIS_DIR, *_THIS_DIR.parents]:
        candidate = parent / ".env"
        if candidate.exists():
            return candidate
    return None

_env_path = _find_env()
if _env_path:
    load_dotenv(_env_path)
    print(f"✓ Loaded .env from {_env_path}")
else:
    print("⚠ No .env file found — falling back to shell environment")

# ── Required ───────────────────────────────────────────────────────────────
try:
    DATABASE_URL = os.environ["DATABASE_URL"]
except KeyError:
    raise EnvironmentError(
        "DATABASE_URL is not set.\n"
        f"Expected a .env file somewhere above: {_THIS_DIR}\n"
        "Make sure it contains:  DATABASE_URL=postgresql://user:pass@host/db"
    )

# ── Optional with defaults ─────────────────────────────────────────────────
EMBEDDING_MODEL      = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHECKPOINT_DIR       = Path(os.getenv("CHECKPOINT_DIR",
                            str(_THIS_DIR.parents[1] / "checkpoints")))
LOG_DIR              = Path(os.getenv("LOG_DIR",
                            str(_THIS_DIR.parents[1] / "logs")))
CACHE_DIR            = Path(os.getenv("CACHE_DIR",
                            str(_THIS_DIR.parents[1] / "data" / "embedding_cache")))
MINDSPORE_DEVICE     = os.getenv("MINDSPORE_DEVICE", "CPU")
CONFIDENCE_THRESHOLD = float(os.getenv("INFERENCE_CONFIDENCE_THRESHOLD", "0.05"))

# ── Ensure directories exist ───────────────────────────────────────────────
for _dir in (CHECKPOINT_DIR, LOG_DIR, CACHE_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
