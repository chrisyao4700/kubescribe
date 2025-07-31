-- Optional: sample row to verify schema (remove in production)
INSERT INTO run_log (status, component, trigger, source, meta)
VALUES ('STARTED', 'core-runner', 'manual', 'local', '{"example": true}');
