#!/usr/bin/env bash
set -euo pipefail
FILE="${1:-${BACKUP_DIR:-/data/backups}/latest.sql.gz}"
echo "Restaurando $FILE em ${POSTGRES_DB} @ ${POSTGRES_HOST}"
gunzip -c "$FILE" | psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB"
echo "Restore ok"
