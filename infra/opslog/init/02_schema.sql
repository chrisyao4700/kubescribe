-- OpsLog schema: records lifecycle of each run of the core job.
-- This DB is independent from the production database (A) and the report database (B).

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'run_status') THEN
    CREATE TYPE run_status AS ENUM ('STARTED', 'SUCCESS', 'ERROR', 'CANCELLED', 'TIMEOUT');
  END IF;
END$$;

CREATE TABLE IF NOT EXISTS run_log (
  id BIGSERIAL PRIMARY KEY,
  run_id UUID NOT NULL DEFAULT gen_random_uuid(),      -- external or generated
  component TEXT NOT NULL DEFAULT 'core-runner',       -- which component reports
  status run_status NOT NULL,                          -- STARTED / SUCCESS / ERROR / ...
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at TIMESTAMPTZ,

  -- duration in milliseconds (derived); available when finished_at is present
  duration_ms BIGINT GENERATED ALWAYS AS (
    CASE
      WHEN finished_at IS NOT NULL THEN (EXTRACT(EPOCH FROM (finished_at - started_at)) * 1000)::BIGINT
      ELSE NULL
    END
  ) STORED,

  error_code TEXT,
  error_message TEXT,
  error_stack TEXT,
  meta JSONB,                                          -- e.g. counts, batch sizes, pointers
  trigger TEXT DEFAULT 'cron',                         -- cron | api | manual | retry
  source  TEXT DEFAULT 'k8s'                           -- k8s | local | ci | other
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_run_log_run_id   ON run_log(run_id);
CREATE INDEX IF NOT EXISTS idx_run_log_status   ON run_log(status);
CREATE INDEX IF NOT EXISTS idx_run_log_started  ON run_log(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_run_log_component ON run_log(component);

-- A lightweight view for latest runs per component (useful for dashboards)
CREATE OR REPLACE VIEW v_latest_runs AS
SELECT DISTINCT ON (component) *
FROM run_log
ORDER BY component, started_at DESC;

-- Retention suggestion (manual; uncomment to keep only 180 days)
-- DELETE FROM run_log WHERE started_at < now() - INTERVAL '180 days';
