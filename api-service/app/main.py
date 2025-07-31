from fastapi import FastAPI, Depends, Header, HTTPException, status
from .config import load_settings, Settings
from .db import make_engine
from .routers import runs, opslog, report

settings = load_settings()
app = FastAPI(title="kubescribe-api", version="0.1.0")

# Dependency: API key check
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

@app.on_event("startup")
def _startup():
    # prime engines in routers
    runs.init(settings)
    opslog.init(settings)
    report.init(settings)

@app.get("/healthz")
def healthz():
    return {"ok": True}

# Routers
app.include_router(runs.router, prefix="/runs", dependencies=[Depends(require_api_key)])
app.include_router(opslog.router, prefix="/runs", dependencies=[Depends(require_api_key)])
app.include_router(report.router, prefix="/report", dependencies=[Depends(require_api_key)])
