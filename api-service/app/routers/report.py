from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from ..config import Settings
from ..db import make_engine, read_report_sample
from sqlalchemy.engine import Engine

router = APIRouter(tags=["report"])
_settings: Settings | None = None
_report_engine: Engine | None = None

def init(settings: Settings) -> None:
    global _settings, _report_engine
    _settings = settings
    if settings.report_db_url:
        _report_engine = make_engine(settings.report_db_url)

@router.get("/sample", summary="Read sample table from report DB")
def read_sample(limit: int = Query(default=20, ge=1, le=1000)) -> List[Dict[str, Any]]:
    if _report_engine is None:
        raise HTTPException(status_code=404, detail="REPORT_DB_URL not configured")
    return read_report_sample(_report_engine, limit=limit)
