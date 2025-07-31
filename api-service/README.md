# kubescribe-api

FastAPI service that:
- Triggers **core-runner** as a **Kubernetes Job** (`POST /runs/trigger`)
- Reads **OpsLog** for run history/status (`GET /runs`, `GET /runs/{run_id}`)
- (Optional) exposes convenience reads for the **report database**

## Run locally

```bash
cp .env.example .env   # set OPSLOG_DB_URL and (optionally) REPORT_DB_URL
python -m venv .venv && source .venv/bin/activate
pip install -U pip && pip install -e .
uvicorn app.main:app --reload --port 8080
```

## Configuration (env)

| Var                      | Required | Default              | Notes |
|--------------------------|----------|----------------------|-------|
| `OPSLOG_DB_URL`         | yes      |                      | PostgreSQL URL for **OpsLog** |
| `REPORT_DB_URL`         | no       |                      | Optional: URL for **report database** |
| `API_KEY`               | no       |                      | If set, required via `x-api-key` header |
| `KUBE_NAMESPACE`        | no       | Pod namespace        | Namespace to create Jobs in (inside cluster uses downward API) |
| `JOB_IMAGE`             | yes      |                      | Container image for **core-runner** (e.g., `your-registry/kubescribe/core-runner:0.1.0`) |
| `JOB_ENV_FROM_SECRET`   | no       | `core-runner-secrets`| Secret name to mount as env for the core-runner container |
| `JOB_BACKOFF_LIMIT`     | no       | `0`                  | K8s Job backoffLimit |
| `JOB_TTL_SECONDS`       | no       | `600`                | Clean up Jobs after finish |

## Kubernetes deploy

Manifests under `infra/api/`:
- `rbac.yaml` (ServiceAccount + Role + RoleBinding to manage Jobs)
- `deployment.yaml` (FastAPI service with in-cluster k8s credentials)
- `service.yaml` (ClusterIP Service)

Update images, then:

```bash
kubectl apply -f infra/api/rbac.yaml
kubectl apply -f infra/api/deployment.yaml
kubectl apply -f infra/api/service.yaml
```

The API discovers cluster config automatically when running in Kubernetes.

## Endpoints

- `GET /healthz` — health check
- `POST /runs/trigger` — create a Job to run core-runner immediately
- `GET /runs` — list OpsLog entries (filters: status, component, limit/offset)
- `GET /runs/{run_id}` — get a single run by run_id
- `GET /report/sample` — (optional) read demo table from report DB

Auth: if `API_KEY` is set, include `x-api-key: <value>` header.

## Notes

- The Job sets env: `RUN_TRIGGER=api`, `RUN_SOURCE=k8s`, and a unique `RUN_ID` (unless provided).
- OpsLog writes are handled inside core-runner.
