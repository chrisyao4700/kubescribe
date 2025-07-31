from pydantic import BaseModel, Field
from typing import Optional
import os

class Settings(BaseModel):
    opslog_db_url: str = Field(..., alias="OPSLOG_DB_URL")
    report_db_url: Optional[str] = Field(default=None, alias="REPORT_DB_URL")
    api_key: Optional[str] = Field(default=None, alias="API_KEY")

    kube_namespace: Optional[str] = Field(default=None, alias="KUBE_NAMESPACE")
    job_image: str = Field(..., alias="JOB_IMAGE")
    job_env_from_secret: str = Field(default="core-runner-secrets", alias="JOB_ENV_FROM_SECRET")
    job_backoff_limit: int = Field(default=0, alias="JOB_BACKOFF_LIMIT")
    job_ttl_seconds: int = Field(default=600, alias="JOB_TTL_SECONDS")

    class Config:
        populate_by_name = True

def load_settings() -> Settings:
    if os.path.exists(".env"):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except Exception:
            pass
    # Default namespace from downward API if available
    ns = os.environ.get("KUBE_NAMESPACE")
    if not ns:
        try:
            with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r", encoding="utf-8") as f:
                os.environ["KUBE_NAMESPACE"] = f.read().strip()
        except Exception:
            pass
    return Settings()  # type: ignore
