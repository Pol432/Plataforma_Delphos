#!/usr/bin/env sh
set -e

echo "Waiting for database to be available..."

# Ensure we run from app root so Python can import the `app` package
cd /app || exit 1

# Loop until a Python check can connect using psycopg2 and DATABASE_URL
until python - <<'PY'
import os,sys
import psycopg2
url = os.environ.get('DATABASE_URL')
if not url:
    print('DATABASE_URL not set', file=sys.stderr)
    sys.exit(1)
# SQLAlchemy-style URL may include driver prefix; psycopg2 accepts postgresql://
if url.startswith('postgresql+psycopg2://'):
    url = url.replace('postgresql+psycopg2://', 'postgresql://', 1)
try:
    conn = psycopg2.connect(url)
    conn.close()
    sys.exit(0)
except Exception as e:
    # Non-zero exit indicates DB not ready
    # print(e, file=sys.stderr)
    sys.exit(1)
PY
do
  echo "Database not ready yet - sleeping 1s"
  sleep 1
done

echo "Database available. Running migrations..."
# Run Alembic migrations using the venv's Python interpreter to ensure imports
python -m alembic upgrade head

echo "Starting Uvicorn..."
# Allow overriding uvicorn args via UVICORN_ARGS env var (e.g. --reload)
if [ -z "$UVICORN_ARGS" ]; then
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
else
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 $UVICORN_ARGS
fi
