from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
from ..config import Settings
from ..db import make_engine, list_runs, get_run
from sqlalchemy.engine import Engine

router = APIRouter(tags=["opslog"])
_settings: Settings | None = None
_ops_engine: Engine | None = None

def init(settings: Settings) -> None:
    global _settings, _ops_engine
    _settings = settings
    _ops_engine = make_engine(settings.opslog_db_url)

@router.get("", summary="List runs")
def list_runs_endpoint(
    status: Optional[str] = Query(default=None),
    component: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0)
) -> List[Dict[str, Any]]:
    assert _ops_engine is not None
    return list_runs(_ops_engine, status=status, component=component, limit=limit, offset=offset)

@router.get("/{run_id}", summary="Get a run by run_id")
def get_run_endpoint(run_id: str) -> Dict[str, Any]:
    assert _ops_engine is not None
    row = get_run(_ops_engine, run_id=run_id)
    if not row:
        return {"found": False}
    return {"found": True, "run": row}
