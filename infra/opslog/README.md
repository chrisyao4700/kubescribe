# OpsLog

OpsLog is a small PostgreSQL database that stores execution records for your core job.
It is separate from the **production database** (Database A) and the **report database** (Database B).

## What it stores

Each run of the core job writes:
- **status**: `STARTED` → `SUCCESS` | `ERROR` | `CANCELLED` | `TIMEOUT`
- **timestamps**: `started_at`, `finished_at`, and a derived `duration_ms`
- **context**: `component`, `trigger` (cron/api/manual), `source` (k8s/local/ci)
- **error details**: `error_code`, `error_message`, `error_stack`
- **meta**: arbitrary JSON (counts, ids, batch sizes, etc.)

## Quickstart (Docker)

```bash
# 1) Place the folder anywhere (e.g., infra/opslog) and cd into it
cp .env.example .env          # then edit password and ports as needed

# 2) Launch Postgres with schema initialization
docker compose up -d

# 3) Check logs and health
docker compose ps
docker compose logs -f opslog-db
```

This spins up Postgres 16 with volumes and runs all SQL files in `./init` once at first start.

## Connect

- Connection URL (local):  
  `postgresql://OPSLOG_USER:OPSLOG_PASSWORD@localhost:OPSLOG_PORT/OPSLOG_DB`

With defaults:
`postgresql://opslog:change-me@localhost:5432/opslog`

### psql example

```bash
psql "postgresql://opslog:change-me@localhost:5432/opslog" -c "\dt"
psql "postgresql://opslog:change-me@localhost:5432/opslog" -c "SELECT * FROM run_log LIMIT 5;"
```

## Schema

Key objects:
- **Type**: `run_status` (enum: STARTED, SUCCESS, ERROR, CANCELLED, TIMEOUT)
- **Table**: `run_log`
- **View**: `v_latest_runs` (latest run per component)

See `init/02_schema.sql` for the canonical DDL.

## Suggested write patterns

- On job start: insert `STARTED` with a `run_id` (generated if not provided).
- On success: update the same `run_id` row to `SUCCESS`, set `finished_at` and optionally `meta`.
- On error: update to `ERROR`, set `finished_at`, fill `error_*` fields.

Example insert/update (psql):

```sql
-- Start a run
INSERT INTO run_log(run_id, status, component, trigger, source, meta)
VALUES (gen_random_uuid(), 'STARTED', 'core-runner', 'cron', 'k8s', '{"batch": 42}')
RETURNING run_id;

-- Later: mark success (supply the returned run_id)
UPDATE run_log
SET status='SUCCESS', finished_at=now(), meta = jsonb_set(COALESCE(meta,'{}'::jsonb), '{processed}', '123'::jsonb, true)
WHERE run_id = '<the-returned-uuid>';
```

## Retention & maintenance

- Start with 90–180 days retention (manual delete job or a DB cron in your platform).
- Indexes provided support typical list/detail queries.
- Consider partitioning only if the table grows into tens of millions of rows.

## Optional: pgAdmin

Uncomment the `pgadmin` service in `docker-compose.yml`, set `PGADMIN_*` in `.env`, then:

```bash
docker compose up -d pgadmin
# open http://localhost:8081 and register the server pointing to opslog-db:5432
```

## Next steps (Kubernetes)

- Replace local `.env` with **Kubernetes Secrets**.
- Mount the same init scripts via a **ConfigMap** or bake schema through migrations.
- Expose OpsLog via a **ClusterIP** Service, restricted by NetworkPolicy.
- Grant read-only vs read-write credentials as separate DB users.

---
Licensed under MIT (or your org’s standard).
