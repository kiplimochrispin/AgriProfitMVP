#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <dump-file> [database-url-prefix]" >&2
  exit 1
fi

DUMP_FILE="$1"
DATABASE_URL_PREFIX="${2:-${DATABASE_URL_PREFIX:-postgresql://agriprofit:agriprofit@localhost:5432}}"
VERIFY_DB="agriprofit_restore_check_$(date +%s)"
VERIFY_URL="${DATABASE_URL_PREFIX}/${VERIFY_DB}"

createdb "$VERIFY_URL"
cleanup() {
  dropdb --if-exists "$VERIFY_URL" >/dev/null 2>&1 || true
}
trap cleanup EXIT

./scripts/restore_postgres.sh "$DUMP_FILE" "$VERIFY_URL"
psql "$VERIFY_URL" -c "SELECT COUNT(*) FROM alembic_version;" >/dev/null
echo "Restore verification passed for $DUMP_FILE"
