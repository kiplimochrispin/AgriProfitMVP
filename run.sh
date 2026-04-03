#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -x "./venv/bin/python" ]; then
  echo "Virtualenv Python not found at ./venv/bin/python"
  exit 1
fi

exec ./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
