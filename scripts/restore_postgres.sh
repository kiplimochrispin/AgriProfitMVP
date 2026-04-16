#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <dump-file> [database-url]" >&2
  exit 1
fi

DUMP_FILE="$1"
DATABASE_URL="${2:-${DATABASE_URL:-postgresql://agriprofit:agriprofit@localhost:5432/agriprofit}}"

if [[ ! -f "$DUMP_FILE" ]]; then
  echo "Dump file not found: $DUMP_FILE" >&2
  exit 1
fi

case "$DUMP_FILE" in
  *.sql)
    psql "$DATABASE_URL" -f "$DUMP_FILE"
    ;;
  *)
    pg_restore --clean --if-exists --no-owner --dbname="$DATABASE_URL" "$DUMP_FILE"
    ;;
esac
