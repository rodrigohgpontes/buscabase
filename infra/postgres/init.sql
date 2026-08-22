CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Portuguese FTS helper used by ingest and search.
DO $$
BEGIN
  PERFORM 1 FROM pg_ts_config WHERE cfgname = 'portuguese';
  IF NOT FOUND THEN
    RAISE NOTICE 'portuguese text search config missing';
  END IF;
END$$;
