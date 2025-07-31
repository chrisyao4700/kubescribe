# KubeScribe
A Kubernetes‑native framework for scheduled data processing and reporting:

Fetch data from `Production Database`, process it (~5 minutes end‑to‑end), and write results to `Report Database`.

Run the core job on a Kubernetes CronJob at a configurable cadence.

Record each run’s lifecycle and details in RunLog (formerly `OpsLog Database`).

Expose a lightweight API to manually trigger runs, read OpsLog, and (optionally) browse data in `report` database.

Emit notifications (e.g., email) on errors.

Note: `Production Database` and `Report Database` already exist. RunLog is new and owned by this project.

## Architecture
### Components

1. core-runner (Python)

Steps: fetch from `Production Database` → transform/aggregate → persist to `Report Database`

Writes structured status & metrics to `OpsLog Database` (start/finish time, duration, counts, error details)

Can be launched by CronJob or on-demand (K8s Job)

2. api (FastAPI)

 - `POST /runs/trigger` — create a one‑off K8s Job to run core-runner immediately

 - `GET /runs` / `GET /runs/{run_id}` — read RunLog

(Optional) endpoints to read from `Report Database` for convenience/admin views

 - OpsLog (PostgreSQL)

   - Stores reliable execution records for operations, observability, and audit

   - Backed by a simple schema optimized for listing and drill‑down


### Execution flow
```
CronJob (schedule) or API-triggered Job
        │
        ▼
  core-runner container
   ├─ Read from `Production Database`
   ├─ Process (~5 min)
   ├─ Write results to B
   └─ Write run status/metrics to OpsLog + notify on ERROR

```

### Local Development
Python (suggested)
```
# Core runner
cd core-runner
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .

# API
cd ../api
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
```

Provide `OPSLOG_DB_URL`, `PROD_DB_URL`, and `REPORT_DB_URL` via .env or your shell before running.

Run RunLog locally

You can spin up PostgreSQL with Docker for development:
```
docker run --name runlog -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=runlog -d postgres:16
# Initialize schema
psql postgresql://postgres:postgres@localhost:5432/runlog -f infra/runlog/schema.sql
```


### Containerization
Each component ships its own Dockerfile (to be added). Typical runtime:

- `core-runner`: one‑shot process (exits after completion), suitable for K8s Job/CronJob.

- `api`: long‑running HTTP service behind a K8s Deployment/Service.

Images should be built in CI and pushed to a registry, then referenced in manifests under infra/k8s/*.