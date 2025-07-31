from __future__ import annotations
from typing import Any, Dict, List
from sqlalchemy.engine import Engine
from sqlalchemy import text
import time

# ---- Replace these with real logic ----

def fetch_from_production(prod_engine: Engine) -> List[Dict[str, Any]]:
    """Fetch records from the production database.
    Replace the SQL and mapping with your real queries.
    """
    # Example placeholder: select first 10 rows from a hypothetical table
    rows: List[Dict[str, Any]] = []
    try:
        with prod_engine.connect() as conn:
            res = conn.execute(text("""
                SELECT * FROM some_source_table LIMIT 10
            """))
            cols = res.keys()
            for r in res:
                rows.append(dict(zip(cols, r)))
    except Exception:
        # It's okay if table doesn't exist in your local tests.
        # We'll operate on a mocked dataset.
        rows = [{"id": i, "value": f"sample-{i}"} for i in range(10)]
    return rows

def transform_data(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform/aggregate records. Simulate ~5 minutes work with progressive sleeps for demo.
    Replace logic with your actual processing.
    """
    out: List[Dict[str, Any]] = []
    chunks = max(1, len(records) // 5)
    for i, rec in enumerate(records):
        # Example transform
        rec2 = dict(rec)
        rec2["value_len"] = len(str(rec2.get("value", "")))
        out.append(rec2)
        # Simulate work every few records (keep short for local; tweak as needed)
        if (i + 1) % chunks == 0:
            time.sleep(0.2)  # 0.2s per chunk; adjust or remove in production
    return out

def write_to_report(report_engine: Engine, processed: List[Dict[str, Any]]) -> int:
    """Write the processed data into the report database.
    Replace with your target schema and upsert logic.
    """
    # Create a demo table if not exists (works for Postgres/MySQL; adjust types as needed)
    with report_engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS report_sample (
                id BIGINT PRIMARY KEY,
                value TEXT,
                value_len INT
            )
        """))
        # Upsert/insert simplified
        inserted = 0
        for rec in processed:
            conn.execute(text("""
                INSERT INTO report_sample (id, value, value_len)
                VALUES (:id, :value, :value_len)
                ON CONFLICT (id) DO UPDATE SET value = EXCLUDED.value, value_len = EXCLUDED.value_len
            """), rec)
            inserted += 1
    return inserted
