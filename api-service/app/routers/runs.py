from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..config import Settings
from ..k8s import K8sJobClient

router = APIRouter(tags=["runs"])
_settings: Settings | None = None
_k8s: K8sJobClient | None = None

class TriggerRequest(BaseModel):
    run_id: str | None = None

class TriggerResponse(BaseModel):
    job_name: str
    run_id: str

def init(settings: Settings) -> None:
    global _settings, _k8s
    _settings = settings
    _k8s = K8sJobClient(namespace=settings.kube_namespace or "default")

@router.post("/trigger", response_model=TriggerResponse)
def trigger_run(payload: TriggerRequest):
    assert _settings is not None and _k8s is not None
    res = _k8s.create_core_runner_job(
        image=_settings.job_image,
        env_from_secret=_settings.job_env_from_secret,
        backoff_limit=_settings.job_backoff_limit,
        ttl_seconds=_settings.job_ttl_seconds,
        run_id=payload.run_id
    )
    return TriggerResponse(**res)
