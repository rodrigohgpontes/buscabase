#!/usr/bin/env bash
set -euo pipefail

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
DEST="${BACKUP_DIR:-/data/backups}"
KEEP="${BACKUP_KEEP_DAYS:-14}"
mkdir -p "$DEST"

FILE="$DEST/buscabase-$STAMP.sql.gz"
echo "Dumping ${POSTGRES_DB} from ${POSTGRES_HOST} to $FILE"
pg_dump -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --format=plain | gzip -c > "$FILE"
ln -sfn "$(basename "$FILE")" "$DEST/latest.sql.gz"

find "$DEST" -name 'buscabase-*.sql.gz' -mtime +"$KEEP" -delete
echo "Backup ok: $FILE"
