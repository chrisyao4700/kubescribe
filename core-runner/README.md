# core-runner

The **core-runner** pulls data from the **production database** (A), processes it (~5 minutes),
writes the results into the **report database** (B), and records run lifecycle in **OpsLog** (C).

It runs as a one-shot process, suitable for **Kubernetes Jobs** and **CronJobs**.

## TL;DR

```bash
# local (requires DB URLs)
cp .env.example .env && edit .env
python -m venv .venv && source .venv/bin/activate
pip install -U pip && pip install -e .
kubescribe-core-runner
```

## Configuration (env vars)

| Variable              | Required | Default | Description |
|-----------------------|----------|---------|-------------|
| `PROD_DB_URL`         | yes      |         | SQLAlchemy URL for the **production database** (A). |
| `REPORT_DB_URL`       | yes      |         | SQLAlchemy URL for the **report database** (B). |
| `OPSLOG_DB_URL`       | yes      |         | PostgreSQL URL for **OpsLog** (C). |
| `RUN_ID`              | no       | auto    | UUID for this run; generated if missing. |
| `RUN_TRIGGER`         | no       | `cron`  | `cron` \| `api` \| `manual` \| `retry`. |
| `RUN_SOURCE`          | no       | `k8s`   | `k8s` \| `local` \| `ci` \| `other`. |
| `NOTIFY_EMAIL_TO`     | no       |         | Comma-separated recipients. Enables email on ERROR if set. |
| `NOTIFY_EMAIL_FROM`   | no       |         | Sender address. |
| `SMTP_HOST`           | no       |         | SMTP host (required if notifying). |
| `SMTP_PORT`           | no       | `587`   | SMTP port. |
| `SMTP_USER`           | no       |         | SMTP user. |
| `SMTP_PASSWORD`       | no       |         | SMTP password. |
| `SMTP_USE_TLS`        | no       | `true`  | Use STARTTLS. |

### URL examples

- Postgres: `postgresql+psycopg://user:pass@host:5432/dbname`
- MySQL (PyMySQL): `mysql+pymysql://user:pass@host:3306/dbname`
- SQLite (for quick tests): `sqlite:///./local.sqlite`

## Docker

```bash
docker build -t kubescribe/core-runner:0.1.0 .
docker run --rm --env-file .env kubescribe/core-runner:0.1.0
```

## Kubernetes

Manifests are under `infra/k8s/core-runner/`:

- `cronjob.yaml` — schedule periodic runs.
- `job-template.yaml` — a template for on-demand runs (e.g., created by your API).
- `secret.example.yaml` — example Secret for injecting connection strings.

## How it works

1. **STARTED** row is inserted into OpsLog with a `run_id`.
2. Data is fetched from the production DB, transformed, and written to the report DB.
3. On success, the OpsLog row is updated to **SUCCESS** with `finished_at` and metrics.
4. On exceptions, the row is updated to **ERROR** with error details, and (optionally) email is sent.

## Customizing the pipeline

Edit `pipeline.py` — implement:
- `fetch_from_production()`
- `transform_data()`
- `write_to_report()`

Keep functions idempotent if possible.

## License

MIT (or your org’s standard).
