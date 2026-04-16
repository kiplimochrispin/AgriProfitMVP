#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
DATABASE_URL="${1:-${DATABASE_URL:-postgresql://agriprofit:agriprofit@localhost:5432/agriprofit}}"

mkdir -p "$BACKUP_DIR"
OUTPUT_FILE="$BACKUP_DIR/agriprofit_${TIMESTAMP}.dump"

pg_dump --format=custom --no-owner --file="$OUTPUT_FILE" "$DATABASE_URL"
echo "Backup written to $OUTPUT_FILE"
