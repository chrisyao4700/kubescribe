from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Optional, List, Dict, Any

def make_engine(url: str) -> Engine:
    return create_engine(url, pool_pre_ping=True, future=True)

def list_runs(engine: Engine, *, status: Optional[str]=None, component: Optional[str]=None,
              limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    sql = """
    SELECT id, run_id, component, status, started_at, finished_at, duration_ms, error_code, error_message, meta
      FROM run_log
     WHERE 1=1
    """
    params = {}
    if status:
        sql += " AND status = :status"
        params["status"] = status
    if component:
        sql += " AND component = :component"
        params["component"] = component
    sql += " ORDER BY started_at DESC LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset
    rows: List[Dict[str, Any]] = []
    with engine.connect() as conn:
        res = conn.execute(text(sql), params)
        cols = res.keys()
        for r in res:
            rows.append(dict(zip(cols, r)))
    return rows

def get_run(engine: Engine, run_id: str) -> Optional[Dict[str, Any]]:
    with engine.connect() as conn:
        res = conn.execute(text("""
            SELECT id, run_id, component, status, started_at, finished_at, duration_ms,
                   error_code, error_message, error_stack, meta
              FROM run_log
             WHERE run_id = :run_id
             LIMIT 1
        """), {"run_id": run_id}).mappings().first()
        return dict(res) if res else None

def read_report_sample(engine: Engine, limit: int = 20) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with engine.connect() as conn:
        res = conn.execute(text("SELECT id, value, value_len FROM report_sample ORDER BY id LIMIT :limit"), {"limit": limit})
        for row in res.mappings():
            rows.append(dict(row))
    return rows
