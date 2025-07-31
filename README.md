# KubeScribe

A **Kubernetes‑native framework** for scheduled data processing and reporting.

- Fetch data from the **Production Database**, process it (~5 minutes end‑to‑end), and write results to the **Report Database**.
- Run the core job on a **Kubernetes CronJob** at a configurable cadence.
- Record each run’s lifecycle and details in **RunLog** (formerly "OpsLog Database").
- Expose a lightweight **API** to manually trigger runs, read from RunLog, and (optionally) browse data in the Report Database.
- Emit **notifications** (e.g., email) on errors.

> **Note:** The **Production Database** and **Report Database** already exist. **RunLog** is a new PostgreSQL database owned by this project.

---

## Architecture

### Components

1. **core-runner** (Python)
   - Steps: fetch from the Production Database → transform/aggregate → persist to the Report Database.
   - Writes structured status & metrics to **RunLog** (start/finish time, duration, counts, error details).
   - Can be launched by **CronJob** or on‑demand (**Kubernetes Job**).

2. **api** (FastAPI)
   - `POST /runs/trigger` — create a one‑off Kubernetes Job to run core‑runner immediately.
   - `GET /runs` / `GET /runs/{run_id}` — read from **RunLog**.
   - *(Optional)* endpoints to read from the **Report Database** for convenience/admin views.

3. **RunLog** (PostgreSQL)
   - Stores reliable execution records for operations, observability, and audit.
   - Backed by a simple schema optimized for listing and drill‑down.

### Execution Flow

```
CronJob (schedule) or API-triggered Job
        │
        ▼
  core-runner container
   ├─ Read from Production Database
   ├─ Process (~5 min)
   ├─ Write results to Report Database
   └─ Write run status/metrics to RunLog + notify on ERROR
```

---

## Local Development

### Python (suggested)

```bash
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

Provide `OPSLOG_DB_URL`, `PROD_DB_URL`, and `REPORT_DB_URL` via `.env` or your shell before running.

### Run RunLog locally

You can spin up PostgreSQL with Docker for development:

```bash
docker run --name runlog -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=runlog \
  -d postgres:16

# Initialize schema
psql postgresql://postgres:postgres@localhost:5432/runlog -f infra/runlog/schema.sql
```

---

## Containerization

Each component ships its own Dockerfile. Typical runtime:

- **core-runner**: one‑shot process (exits after completion), suitable for a Kubernetes Job or CronJob.
- **api**: long‑running HTTP service behind a Kubernetes Deployment/Service.

Images should be built in CI and pushed to a container registry, then referenced in manifests under `infra/*`:

```
infra/
├── opslog/         # RunLog: PostgreSQL and init scripts
├── core-runner/    # CronJob + Job template
└── api/            # Deployment + Service + RBAC
```

---
