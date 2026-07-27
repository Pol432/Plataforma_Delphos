"""
db.py — PostgreSQL connection manager for the LPO.

Usage:
    from db import get_connection, get_cursor

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute("SELECT 1")
"""

import logging
from contextlib import contextmanager
from config import DB_CONFIG

logger = logging.getLogger("lpo.db")

# ── Try to import psycopg2 ───────────────────────────────────────────────────
try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logger.warning(
        "psycopg2 not installed. DB operations will be unavailable. "
        "Install with: pip install psycopg2-binary"
    )


def get_connection():
    """
    Return a live psycopg2 connection using DB_CONFIG.
    Raises RuntimeError if psycopg2 is not installed.
    """
    if not PSYCOPG2_AVAILABLE:
        raise RuntimeError(
            "psycopg2 is required for database operations. "
            "Run: pip install psycopg2-binary"
        )
    conn = psycopg2.connect(**DB_CONFIG)
    logger.debug("DB connection opened → %s/%s", DB_CONFIG["host"], DB_CONFIG["dbname"])
    return conn


@contextmanager
def managed_connection():
    """
    Context manager that opens a connection, commits on success, rolls back on error.

    Example:
        with managed_connection() as conn:
            cur = conn.cursor()
            cur.execute(...)
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
        logger.debug("Transaction committed.")
    except Exception as exc:
        conn.rollback()
        logger.error("Transaction rolled back due to: %s", exc)
        raise
    finally:
        conn.close()
        logger.debug("DB connection closed.")


@contextmanager
def get_cursor(conn, dict_cursor: bool = True):
    """
    Context manager that yields a cursor.
    Uses RealDictCursor by default so rows behave like dicts.

    Example:
        with get_cursor(conn) as cur:
            cur.execute("SELECT id, nombre FROM habilidades_catalogo")
            rows = cur.fetchall()
            print(rows[0]["nombre"])
    """
    cursor_factory = psycopg2.extras.RealDictCursor if dict_cursor else None
    cur = conn.cursor(cursor_factory=cursor_factory) if cursor_factory else conn.cursor()
    try:
        yield cur
    finally:
        cur.close()


def test_connection() -> bool:
    """Quick health-check. Returns True if DB is reachable."""
    try:
        with managed_connection() as conn:
            with get_cursor(conn) as cur:
                cur.execute("SELECT 1 AS ok")
                row = cur.fetchone()
                return row["ok"] == 1
    except Exception as exc:
        logger.error("DB connection test failed: %s", exc)
        return False
