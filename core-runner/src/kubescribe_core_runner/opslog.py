from __future__ import annotations
from sqlalchemy.engine import Engine
from sqlalchemy import text
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

def start_run(engine: Engine, *, run_id: Optional[str]=None, component: str="core-runner",
              trigger: str="cron", source: str="k8s", meta: Optional[Dict[str, Any]]=None) -> str:
    rid = str(run_id or uuid4())
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO run_log (run_id, status, component, started_at, trigger, source, meta)
            VALUES (:run_id, 'STARTED', :component, now(), :trigger, :source, COALESCE(:meta, '{}'::jsonb))
        """), {"run_id": rid, "component": component, "trigger": trigger, "source": source, "meta": meta})
    return rid

def mark_success(engine: Engine, *, run_id: str, meta: Optional[Dict[str, Any]]=None) -> None:
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE run_log
               SET status='SUCCESS',
                   finished_at=now(),
                   meta = COALESCE(meta, '{}'::jsonb) || COALESCE(:meta, '{}'::jsonb)
             WHERE run_id = :run_id
        """), {"run_id": run_id, "meta": meta})

def mark_error(engine: Engine, *, run_id: str, error_code: Optional[str]=None,
               error_message: Optional[str]=None, error_stack: Optional[str]=None,
               meta: Optional[Dict[str, Any]]=None) -> None:
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE run_log
               SET status='ERROR',
                   finished_at=now(),
                   error_code = :error_code,
                   error_message = :error_message,
                   error_stack = :error_stack,
                   meta = COALESCE(meta, '{}'::jsonb) || COALESCE(:meta, '{}'::jsonb)
             WHERE run_id = :run_id
        """), {
            "run_id": run_id,
            "error_code": error_code,
            "error_message": error_message,
            "error_stack": error_stack,
            "meta": meta
        })
