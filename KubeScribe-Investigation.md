# Investigation: Why Adopt KubeScribe vs. Current Kubeflow CronJob Approach

## 1. Current Setup (Baseline)
- We maintain a single `script.py` inside a Kubeflow workspace.  
- The script is triggered on a **Kubeflow CronJob**, configured manually in the Kubeflow UI.  
- Logs and execution history are tied to the Kubeflow job history (short retention).  
- Errors require manual inspection of Kubeflow logs or external monitoring.  
- No structured way to trigger ad-hoc/manual runs beyond editing schedules.

## 2. Proposed Framework (KubeScribe)

KubeScribe introduces three components:  
1. **core-runner (Python)** – encapsulates the processing pipeline as a reusable Docker image.  
2. **RunLog (PostgreSQL)** – permanent, queryable run history (start, finish, errors, metrics).  
3. **API (FastAPI)** – programmatic/manual trigger of runs, and query endpoints for execution state.

It runs entirely on standard **Kubernetes CronJob/Job**, without being tied to Kubeflow UI or workspaces.

---

## 3. Key Advantages

| Dimension            | Current Kubeflow CronJob                     | KubeScribe Framework                                                        |
|----------------------|----------------------------------------------|-----------------------------------------------------------------------------|
| **Observability**    | Logs live only in Kubeflow; retention short  | Structured **RunLog DB**: durable run history, queryable (dashboards, audits) |
| **Ad-hoc runs**      | Must manually change CronJob or run locally  | `POST /runs/trigger` endpoint → one-off **Job** with generated `run_id`     |
| **Error handling**   | Requires manual log inspection               | Error states logged to RunLog + **email/Slack notifications** out-of-box    |
| **Audit/compliance** | No centralized DB for run status             | Full record of `run_id`, inputs, outputs, metrics in RunLog                  |
| **Portability**      | Tied to Kubeflow cluster/workspace            | Works on any Kubernetes cluster (EKS/GKE/AKS/on-prem)                        |
| **Extensibility**    | Harder to evolve into admin UI or API         | **API-first**: already exposes endpoints → can plug in dashboards/admin UI   |
| **Configuration**    | Manual YAML/GUI editing per CronJob          | Standardized manifests + **Secrets** (DB URLs, SMTP, etc.)                    |
| **Decoupling**       | Code + schedule embedded in Kubeflow workspace| `core-runner` image versioned & independent of scheduling                     |

---

## 4. Strategic Value

- **Decouple execution from platform UI** – no lock-in to Kubeflow; jobs can be managed via GitOps, CI/CD, or API calls.  
- **Permanent run history** – enables analytics, compliance, and SLA tracking.  
- **Admin automation** – easier to add web UI for retry, cancel, or parameterized runs.  
- **Standard Kubernetes primitives** – fewer custom concepts for new engineers, easier to integrate into existing infra.  

---

## 5. Conclusion

KubeScribe turns one-off scripts + ad-hoc schedules into a **repeatable, observable, and auditable framework**.  
It sets the foundation for:
- Multi-tenant scheduling
- Workflow chaining (orchestration)
- Centralized reporting and alerting

**Recommendation:** Migrate the existing `script.py` CronJob into a `core-runner` container and adopt KubeScribe for new and existing batch jobs.
