#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WAIT_FOR_DB_TIMEOUT="${WAIT_FOR_DB_TIMEOUT:-60}"

if [[ -n "${DATABASE_URL:-}" ]]; then
  echo "Waiting for database readiness..."
  timeout "$WAIT_FOR_DB_TIMEOUT" bash -c '
    until python - <<'"'"'PY'"'"'
from app.database import database_is_ready
raise SystemExit(0 if database_is_ready() else 1)
PY
    do
      sleep 2
    done
  '

  echo "Running migrations..."
  alembic upgrade head
fi

echo "Starting AgriProfit web service..."
exec python -m uvicorn app.main:app --host "$HOST" --port "$PORT"
