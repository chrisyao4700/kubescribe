from pydantic import BaseModel, Field
from typing import Optional
import os

class Settings(BaseModel):
    prod_db_url: str = Field(..., alias="PROD_DB_URL")
    report_db_url: str = Field(..., alias="REPORT_DB_URL")
    opslog_db_url: str = Field(..., alias="OPSLOG_DB_URL")

    run_id: Optional[str] = Field(default=None, alias="RUN_ID")
    run_trigger: str = Field(default="cron", alias="RUN_TRIGGER")
    run_source: str = Field(default="k8s", alias="RUN_SOURCE")

    notify_email_to: Optional[str] = Field(default=None, alias="NOTIFY_EMAIL_TO")
    notify_email_from: Optional[str] = Field(default=None, alias="NOTIFY_EMAIL_FROM")
    smtp_host: Optional[str] = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, alias="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")

    class Config:
        populate_by_name = True

def load_settings() -> Settings:
    # Lightweight .env support for local runs
    if os.path.exists(".env"):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except Exception:
            pass
    return Settings()  # type: ignore
